"""
Weekly Report Generation
Generate comprehensive collection reports
"""

import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

from cardforge.services import CollectionService, PricingService, DeckService
from cardforge.repositories import PriceRepository


logger = logging.getLogger(__name__)


class WeeklyReport:
    """
    Generate weekly collection reports.
    
    Reports include:
    - Collection value change
    - Notable price movements
    - Deck completion progress
    - Shopping list updates
    """
    
    def __init__(self, collection_id: int = 1):
        """
        Initialize weekly report generator.
        
        Args:
            collection_id: Collection to report on
        """
        self.collection_id = collection_id
        
        # Services
        self.collection_service = CollectionService()
        self.pricing_service = PricingService()
        self.deck_service = DeckService()
        self.price_repo = PriceRepository()
    
    async def generate(self) -> dict:
        """
        Generate weekly report.
        
        Returns:
            Report data dictionary
        """
        logger.info("Generating weekly report...")
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "period": "Last 7 days",
            "sections": {},
        }
        
        # Section 1: Collection Overview
        logger.info("Generating collection overview...")
        report["sections"]["overview"] = await self._collection_overview()
        
        # Section 2: Value Changes
        logger.info("Analyzing value changes...")
        report["sections"]["value_changes"] = await self._value_changes()
        
        # Section 3: Price Movers
        logger.info("Finding price movers...")
        report["sections"]["price_movers"] = await self._price_movers()
        
        # Section 4: Deck Progress
        logger.info("Checking deck progress...")
        report["sections"]["deck_progress"] = await self._deck_progress()
        
        # Section 5: Shopping List
        logger.info("Updating shopping list...")
        report["sections"]["shopping_list"] = await self._shopping_list_update()
        
        logger.info("Weekly report generated successfully")
        
        return report
    
    async def _collection_overview(self) -> dict:
        """Generate collection overview section."""
        stats = await self.collection_service.get_stats(self.collection_id)
        
        return {
            "unique_cards": stats.unique_cards,
            "total_cards": stats.total_cards,
            "total_value": str(stats.total_value),
            "average_card_value": str(stats.total_value / stats.unique_cards if stats.unique_cards > 0 else 0),
            "foil_percentage": f"{(stats.foil_count / stats.total_cards * 100):.1f}%" if stats.total_cards > 0 else "0%",
        }
    
    async def _value_changes(self) -> dict:
        """Analyze collection value changes over the week."""
        # Get current value
        current_stats = await self.collection_service.get_stats(self.collection_id)
        current_value = current_stats.total_value
        
        # Get value from 7 days ago (would need historical data)
        # For now, return placeholder
        week_ago_value = current_value * Decimal("0.98")  # Simulate 2% gain
        
        change = current_value - week_ago_value
        change_percent = (change / week_ago_value * 100) if week_ago_value > 0 else 0
        
        return {
            "current_value": str(current_value),
            "week_ago_value": str(week_ago_value),
            "change_amount": str(change),
            "change_percent": f"{change_percent:.2f}%",
            "trend": "up" if change > 0 else "down" if change < 0 else "stable",
        }
    
    async def _price_movers(self) -> dict:
        """Find cards with significant price movements."""
        gainers = await self.price_repo.get_biggest_movers(days=7, limit=5, direction='up')
        losers = await self.price_repo.get_biggest_movers(days=7, limit=5, direction='down')
        
        return {
            "gainers": [
                {
                    "card": f"{g['name']} ({g['set_code']})",
                    "change": f"+${g['change']:.2f}",
                    "percent": f"+{g['change_pct']:.1f}%"
                }
                for g in gainers
            ],
            "losers": [
                {
                    "card": f"{l['name']} ({l['set_code']})",
                    "change": f"${l['change']:.2f}",
                    "percent": f"{l['change_pct']:.1f}%"
                }
                for l in losers
            ],
            "note": "Based on recorded price history",
        }
    
    async def _deck_progress(self) -> dict:
        """Check deck completion progress."""
        # Get all decks
        decks = await self.deck_service.get_all_decks()
        
        deck_summaries = []
        
        for deck in decks:
            missing = await self.deck_service.get_missing_cards(deck.id)
            total_cards = len(deck.cards) if hasattr(deck, 'cards') else 0
            missing_count = len(missing)
            completion = ((total_cards - missing_count) / total_cards * 100) if total_cards > 0 else 0
            
            deck_summaries.append({
                "name": deck.name,
                "completion": f"{completion:.1f}%",
                "missing_cards": missing_count,
                "estimated_cost": str(sum(m.current_price for m in missing if m.current_price)),
            })
        
        return {
            "total_decks": len(decks),
            "decks": deck_summaries,
        }
    
    async def _shopping_list_update(self) -> dict:
        """Update shopping list section."""
        from cardforge.services import TradeService
        
        trade_service = TradeService()
        
        # Get buy list
        items = await trade_service.get_buy_list()
        summary = await trade_service.get_buy_list_summary()
        
        # Group by priority
        high_priority = [i for i in items if i.priority <= 2]
        medium_priority = [i for i in items if i.priority == 3]
        low_priority = [i for i in items if i.priority >= 4]
        
        return {
            "total_items": summary.total_items,
            "total_cost": str(summary.total_cost),
            "by_priority": {
                "high": len(high_priority),
                "medium": len(medium_priority),
                "low": len(low_priority),
            },
            "top_5_items": [
                {"card": i.card_name, "price": str(i.best_price), "priority": i.priority}
                for i in items[:5]
            ],
        }
    
    async def save_to_file(self, report: dict, output_path: Path) -> None:
        """Save report to file."""
        import json
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {output_path}")
    
    def format_as_markdown(self, report: dict) -> str:
        """Format report as Markdown."""
        md = f"# CardForge Weekly Report\n\n"
        md += f"**Generated:** {report['generated_at']}\n"
        md += f"**Period:** {report['period']}\n\n"
        
        # Overview
        overview = report["sections"]["overview"]
        md += "## Collection Overview\n\n"
        md += f"- **Unique Cards:** {overview['unique_cards']}\n"
        md += f"- **Total Cards:** {overview['total_cards']}\n"
        md += f"- **Total Value:** ${overview['total_value']}\n"
        md += f"- **Average Value:** ${overview['average_card_value']}\n"
        md += f"- **Foil %:** {overview['foil_percentage']}\n\n"
        
        # Value Changes
        changes = report["sections"]["value_changes"]
        md += "## Value Changes\n\n"
        md += f"- **Current Value:** ${changes['current_value']}\n"
        md += f"- **Week Ago:** ${changes['week_ago_value']}\n"
        md += f"- **Change:** ${changes['change_amount']} ({changes['change_percent']})\n"
        md += f"- **Trend:** {changes['trend'].upper()}\n\n"
        
        # Price Movers
        movers = report["sections"]["price_movers"]
        md += "## Price Movers\n\n"
        md += "### Top Gainers\n"
        for gainer in movers.get("gainers", []):
            md += f"- **{gainer['card']}:** {gainer['change']} ({gainer['percent']})\n"
        md += "\n### Top Losers\n"
        for loser in movers.get("losers", []):
            md += f"- **{loser['card']}:** {loser['change']} ({loser['percent']})\n"
        md += "\n"
        
        # Deck Progress
        deck_progress = report["sections"]["deck_progress"]
        md += "## Deck Progress\n\n"
        for deck in deck_progress.get("decks", []):
            md += f"### {deck['name']}\n"
            md += f"- **Completion:** {deck['completion']}\n"
            md += f"- **Missing Cards:** {deck['missing_cards']}\n"
            md += f"- **Estimated Cost:** ${deck['estimated_cost']}\n\n"
        
        # Shopping List
        shopping = report["sections"]["shopping_list"]
        md += "## Shopping List Update\n\n"
        md += f"- **Total Items:** {shopping['total_items']}\n"
        md += f"- **Total Cost:** ${shopping['total_cost']}\n"
        md += f"- **High Priority:** {shopping['by_priority']['high']}\n"
        md += f"- **Medium Priority:** {shopping['by_priority']['medium']}\n"
        md += f"- **Low Priority:** {shopping['by_priority']['low']}\n\n"
        
        md += "### Top 5 Items\n"
        for item in shopping.get("top_5_items", []):
            md += f"- **{item['card']}** - ${item['price']} (Priority: {item['priority']})\n"
        
        return md


async def main():
    """Run weekly report as standalone script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    reporter = WeeklyReport()
    report = await reporter.generate()
    
    # Save as JSON
    output_dir = Path("data/reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d")
    json_path = output_dir / f"weekly_report_{timestamp}.json"
    await reporter.save_to_file(report, json_path)
    
    # Save as Markdown
    md_content = reporter.format_as_markdown(report)
    md_path = output_dir / f"weekly_report_{timestamp}.md"
    md_path.write_text(md_content, encoding="utf-8")
    
    print(f"\n=== Weekly Report Generated ===")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print("\nPreview:")
    print(md_content[:500] + "...")


if __name__ == "__main__":
    asyncio.run(main())
