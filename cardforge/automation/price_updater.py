"""
Price Updater Automation
Automated price updates from multiple sources
"""

import asyncio
import logging
from datetime import datetime
from decimal import Decimal

from cardforge.services import PricingService, CollectionService
from cardforge.repositories import CardRepository, PriceRepository


logger = logging.getLogger(__name__)


class PriceUpdater:
    """
    Automated price update system.
    
    Updates prices from:
    - Scryfall (primary)
    - TCGPlayer (if API key available)
    - CardKingdom (scraping fallback)
    """
    
    def __init__(self, collection_id: int = 1):
        """
        Initialize price updater.
        
        Args:
            collection_id: Collection to update prices for
        """
        self.collection_id = collection_id
        
        # Services
        self.pricing_service = PricingService()
        self.collection_service = CollectionService()
        self.card_repo = CardRepository()
        self.price_repo = PriceRepository()
    
    async def run(self, full_update: bool = False) -> dict:
        """
        Run price update.
        
        Args:
            full_update: If True, update all cards; if False, only recent
            
        Returns:
            Update statistics
        """
        logger.info("Starting price update...")
        start_time = datetime.now()
        
        stats = {
            "started_at": start_time.isoformat(),
            "mode": "full" if full_update else "incremental",
            "cards_processed": 0,
            "cards_updated": 0,
            "errors": 0,
            "sources": {},
        }
        
        try:
            # Get cards to update
            if full_update:
                cards = await self.card_repo.get_all()
            else:
                # Only update cards in collection
                collection_cards = await self.collection_service.get_all_cards(
                    self.collection_id
                )
                card_ids = [cc.card_id for cc in collection_cards]
                cards = await self.card_repo.get_by_ids(card_ids)
            
            stats["cards_processed"] = len(cards)
            logger.info(f"Updating prices for {len(cards)} cards...")
            
            # Update prices with rate limiting
            for i, card in enumerate(cards):
                try:
                    # Update from Scryfall
                    price_data = await self.pricing_service.get_current_price(card.id)
                    
                    if price_data:
                        await self.price_repo.record_price(
                            card_id=card.id,
                            source="scryfall",
                            price_usd=price_data.get("usd"),
                            price_usd_foil=price_data.get("usd_foil"),
                        )
                        stats["cards_updated"] += 1
                    
                    # Rate limiting (10 req/sec for Scryfall)
                    if (i + 1) % 10 == 0:
                        await asyncio.sleep(1)
                    
                    # Progress logging
                    if (i + 1) % 100 == 0:
                        logger.info(f"Progress: {i + 1}/{len(cards)} cards")
                
                except Exception as e:
                    logger.error(f"Failed to update price for {card.name}: {e}")
                    stats["errors"] += 1
            
            # Calculate statistics
            duration = (datetime.now() - start_time).total_seconds()
            stats["completed_at"] = datetime.now().isoformat()
            stats["duration_seconds"] = duration
            stats["cards_per_second"] = stats["cards_processed"] / duration if duration > 0 else 0
            
            logger.info(
                f"Price update complete: {stats['cards_updated']} cards updated "
                f"in {duration:.2f}s ({stats['cards_per_second']:.2f} cards/sec)"
            )
            
        except Exception as e:
            logger.error(f"Price update failed: {e}", exc_info=True)
            stats["status"] = "failed"
            stats["error"] = str(e)
        
        return stats
    
    async def update_single_card(self, card_name: str) -> dict:
        """
        Update price for a single card.
        
        Args:
            card_name: Card name to update
            
        Returns:
            Update result
        """
        card = await self.card_repo.get_by_name(card_name)
        
        if not card:
            return {"success": False, "error": "Card not found"}
        
        try:
            price_data = await self.pricing_service.get_current_price(card.id)
            
            if price_data:
                await self.price_repo.record_price(
                    card_id=card.id,
                    source="scryfall",
                    price_usd=price_data.get("usd"),
                    price_usd_foil=price_data.get("usd_foil"),
                )
                
                return {
                    "success": True,
                    "card": card.name,
                    "price_usd": str(price_data.get("usd", "N/A")),
                    "price_usd_foil": str(price_data.get("usd_foil", "N/A")),
                }
            
            return {"success": False, "error": "No price data available"}
            
        except Exception as e:
            logger.error(f"Failed to update price for {card_name}: {e}")
            return {"success": False, "error": str(e)}


async def main():
    """Run price updater as standalone script."""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    parser = argparse.ArgumentParser(description="Update card prices")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full update (all cards) instead of incremental",
    )
    parser.add_argument(
        "--card",
        type=str,
        help="Update single card by name",
    )
    
    args = parser.parse_args()
    
    updater = PriceUpdater()
    
    if args.card:
        # Single card update
        result = await updater.update_single_card(args.card)
        print(f"\n=== Single Card Update ===")
        print(f"Card: {result.get('card', args.card)}")
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Price (USD): ${result['price_usd']}")
            print(f"Price (Foil): ${result['price_usd_foil']}")
        else:
            print(f"Error: {result.get('error')}")
    else:
        # Batch update
        stats = await updater.run(full_update=args.full)
        print(f"\n=== Price Update Results ===")
        print(f"Mode: {stats['mode']}")
        print(f"Cards processed: {stats['cards_processed']}")
        print(f"Cards updated: {stats['cards_updated']}")
        print(f"Errors: {stats['errors']}")
        print(f"Duration: {stats.get('duration_seconds', 0):.2f}s")
        print(f"Rate: {stats.get('cards_per_second', 0):.2f} cards/sec")


if __name__ == "__main__":
    asyncio.run(main())
