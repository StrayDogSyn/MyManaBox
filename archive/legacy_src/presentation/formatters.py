"""Formatters for displaying collection data."""

from typing import List, Dict, Any
from decimal import Decimal
from tabulate import tabulate
import json
import csv
from io import StringIO
from ..models import Collection, Card


class TableFormatter:
    """Formats data for tabular display."""
    
    @staticmethod
    def format_cards_table(cards: List[Card], limit: int = 20) -> str:
        """Format cards as a table."""
        if not cards:
            return "No cards found."
        
        # Limit results
        display_cards = cards[:limit]
        
        # Prepare data for tabulation
        headers = ['Name', 'Edition', 'Count', 'Price', 'Condition']
        rows = []
        
        for card in display_cards:
            price_str = f"${card.purchase_price}" if card.purchase_price else ""
            rows.append([
                card.name,
                card.edition,
                card.count,
                price_str,
                card.condition.value
            ])
        
        table = tabulate(rows, headers=headers, tablefmt='grid')
        
        if len(cards) > limit:
            table += f"\n\n... and {len(cards) - limit} more cards"
        
        return table
    
    @staticmethod
    def format_summary_table(summary_data: Dict[str, Any]) -> str:
        """Format collection summary as a table."""
        rows = [
            ['Total Cards', summary_data.get('total_cards', 0)],
            ['Unique Cards', summary_data.get('unique_cards', 0)],
            ['Total Value', f"${summary_data.get('total_value', 0):.2f}"],
            ['Average Value', f"${summary_data.get('average_card_value', 0):.2f}"]
        ]
        
        return tabulate(rows, headers=['Metric', 'Value'], tablefmt='grid')
    
    @staticmethod
    def format_stats_table(stats_data: Dict[str, Any]) -> str:
        """Format detailed statistics as tables."""
        output = []
        
        # Condition stats
        if 'condition_stats' in stats_data:
            condition_data = stats_data['condition_stats']
            if condition_data:
                rows = [[condition, count] for condition, count in condition_data.items()]
                output.append("Cards by Condition:")
                output.append(tabulate(rows, headers=['Condition', 'Count'], tablefmt='grid'))
                output.append("")
        
        # Set stats (top 10)
        if 'set_stats' in stats_data:
            set_data = stats_data['set_stats']
            if set_data:
                top_sets = sorted(set_data.items(), key=lambda x: x[1], reverse=True)[:10]
                rows = [[set_name, count] for set_name, count in top_sets]
                output.append("Top 10 Sets by Card Count:")
                output.append(tabulate(rows, headers=['Set', 'Count'], tablefmt='grid'))
                output.append("")
        
        # Foil stats
        if 'foil_stats' in stats_data:
            foil_data = stats_data['foil_stats']
            if foil_data:
                rows = [[status, count] for status, count in foil_data.items()]
                output.append("Foil Status:")
                output.append(tabulate(rows, headers=['Status', 'Count'], tablefmt='grid'))
        
        return "\n".join(output)
    
    @staticmethod
    def format_grouped_cards(grouped_cards: Dict[str, List[Card]], limit_per_group: int = 10) -> str:
        """Format grouped cards display."""
        output = []
        
        for group_name, cards in grouped_cards.items():
            if cards:
                output.append(f"\n=== {group_name} ({len(cards)} cards) ===")
                display_cards = cards[:limit_per_group]
                
                rows = []
                for card in display_cards:
                    price_str = f"${card.purchase_price}" if card.purchase_price else ""
                    rows.append([card.name, card.edition, card.count, price_str])
                
                if rows:
                    output.append(tabulate(rows, headers=['Name', 'Edition', 'Count', 'Price'], tablefmt='grid'))
                
                if len(cards) > limit_per_group:
                    output.append(f"... and {len(cards) - limit_per_group} more cards in this group")
        
        return "\n".join(output)


class CollectionFormatter:
    """Formats collection data for various output formats."""
    
    def __init__(self, output_format: str = "table"):
        """Initialize with output format."""
        self.output_format = output_format.lower()
        self.table_formatter = TableFormatter()
    
    def format_collection_summary(self, collection: Collection) -> str:
        """Format collection summary."""
        summary_data = {
            'total_cards': collection.total_cards,
            'unique_cards': collection.unique_cards,
            'total_value': collection.total_value,
            'average_card_value': self._calculate_average_value(collection)
        }
        
        if self.output_format == "json":
            return json.dumps(summary_data, indent=2, default=str)
        elif self.output_format == "csv":
            return self._dict_to_csv(summary_data)
        else:  # table
            return self.table_formatter.format_summary_table(summary_data)
    
    def format_cards(self, cards: List[Card], limit: int = 20) -> str:
        """Format cards list."""
        if self.output_format == "json":
            return json.dumps([self._card_to_dict(card) for card in cards[:limit]], indent=2, default=str)
        elif self.output_format == "csv":
            return self._cards_to_csv(cards[:limit])
        else:  # table
            return self.table_formatter.format_cards_table(cards, limit)
    
    def format_grouped_cards(self, grouped_cards: Dict[str, List[Card]], limit_per_group: int = 10) -> str:
        """Format grouped cards."""
        if self.output_format == "json":
            formatted_groups = {}
            for group_name, cards in grouped_cards.items():
                formatted_groups[group_name] = [self._card_to_dict(card) for card in cards[:limit_per_group]]
            return json.dumps(formatted_groups, indent=2, default=str)
        elif self.output_format == "csv":
            # For CSV, concatenate all groups
            all_cards = []
            for group_name, cards in grouped_cards.items():
                for card in cards[:limit_per_group]:
                    card_dict = self._card_to_dict(card)
                    card_dict['Group'] = group_name
                    all_cards.append(card_dict)
            return self._dicts_to_csv(all_cards)
        else:  # table
            return self.table_formatter.format_grouped_cards(grouped_cards, limit_per_group)
    
    def format_analytics(self, analytics_data: Dict[str, Any]) -> str:
        """Format analytics data."""
        if self.output_format == "json":
            return json.dumps(analytics_data, indent=2, default=str)
        elif self.output_format == "csv":
            # Flatten analytics data for CSV
            flattened = self._flatten_dict(analytics_data)
            return self._dict_to_csv(flattened)
        else:  # table
            return self._format_analytics_table(analytics_data)
    
    def _calculate_average_value(self, collection: Collection) -> Decimal:
        """Calculate average card value."""
        cards_with_prices = [card for card in collection.cards if card.purchase_price is not None]
        if not cards_with_prices:
            return Decimal('0')
        
        total_value = sum(card.total_value for card in cards_with_prices)
        total_count = sum(card.count for card in cards_with_prices)
        
        return Decimal(str(total_value / total_count)) if total_count > 0 else Decimal('0')
    
    def _card_to_dict(self, card: Card) -> Dict[str, Any]:
        """Convert card to dictionary."""
        return {
            'name': card.name,
            'edition': card.edition,
            'count': card.count,
            'purchase_price': float(card.purchase_price) if card.purchase_price else None,
            'condition': card.condition.value,
            'foil': card.foil,
            'total_value': float(card.total_value)
        }
    
    def _dict_to_csv(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to CSV."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Key', 'Value'])
        
        # Write data
        for key, value in data.items():
            writer.writerow([key, value])
        
        return output.getvalue()
    
    def _dicts_to_csv(self, data_list: List[Dict[str, Any]]) -> str:
        """Convert list of dictionaries to CSV."""
        if not data_list:
            return ""
        
        output = StringIO()
        fieldnames = data_list[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in data_list:
            writer.writerow(row)
        
        return output.getvalue()
    
    def _cards_to_csv(self, cards: List[Card]) -> str:
        """Convert cards to CSV."""
        return self._dicts_to_csv([self._card_to_dict(card) for card in cards])
    
    def _flatten_dict(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested dictionary."""
        flattened = {}
        
        for key, value in data.items():
            new_key = f"{prefix}_{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(self._flatten_dict(value, new_key))
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                # Skip complex nested lists for CSV
                flattened[new_key] = f"{len(value)} items"
            else:
                flattened[new_key] = value
        
        return flattened
    
    def _format_analytics_table(self, analytics_data: Dict[str, Any]) -> str:
        """Format analytics as tables."""
        output = []
        
        # Basic stats
        if 'total_cards' in analytics_data:
            basic_stats = [
                ['Total Cards', analytics_data.get('total_cards', 0)],
                ['Unique Cards', analytics_data.get('unique_cards', 0)],
                ['Total Value', f"${analytics_data.get('total_value', 0):.2f}"],
                ['Average Value', f"${analytics_data.get('average_card_value', 0):.2f}"]
            ]
            output.append("Collection Overview:")
            output.append(tabulate(basic_stats, headers=['Metric', 'Value'], tablefmt='grid'))
            output.append("")
        
        return "\n".join(output)
