"""Analytics service for collection insights."""

from typing import Dict, List, Tuple, Any
from decimal import Decimal
from collections import Counter
from ..models import Collection, Card


class AnalyticsService:
    """Service for analyzing collection data and providing insights."""
    
    def get_collection_summary(self, collection: Collection) -> Dict[str, Any]:
        """Get comprehensive collection summary."""
        return {
            'total_cards': collection.total_cards,
            'unique_cards': collection.unique_cards,
            'total_value': collection.total_value,
            'average_card_value': self.get_average_card_value(collection),
            'most_valuable_cards': collection.get_most_valuable_cards(10),
            'condition_distribution': collection.get_condition_stats(),
            'set_distribution': collection.get_set_stats(),
            'foil_distribution': collection.get_foil_stats(),
        }
    
    def get_average_card_value(self, collection: Collection) -> Decimal:
        """Calculate average value per card."""
        cards_with_prices = [card for card in collection.cards if card.purchase_price is not None]
        if not cards_with_prices:
            return Decimal('0')
        
        total_value = sum(card.total_value for card in cards_with_prices)
        total_count = sum(card.count for card in cards_with_prices)
        
        return Decimal(str(total_value / total_count)) if total_count > 0 else Decimal('0')
    
    def get_set_analysis(self, collection: Collection) -> Dict[str, Any]:
        """Analyze collection by sets."""
        set_stats = collection.get_set_stats()
        set_values = {}
        
        for card in collection.cards:
            if card.edition not in set_values:
                set_values[card.edition] = Decimal('0')
            set_values[card.edition] += card.total_value
        
        # Top 10 sets by count and value
        top_sets_by_count = sorted(set_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        top_sets_by_value = sorted(set_values.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_sets': len(set_stats),
            'top_sets_by_count': top_sets_by_count,
            'top_sets_by_value': top_sets_by_value,
            'set_values': set_values
        }
    
    def get_color_analysis(self, collection: Collection) -> Dict[str, Any]:
        """Analyze collection by color distribution."""
        color_groups = collection.get_cards_by_color()
        color_stats = {}
        color_values = {}
        
        for color, cards in color_groups.items():
            color_stats[color] = sum(card.count for card in cards)
            color_values[color] = sum(card.total_value for card in cards)
        
        return {
            'color_distribution': color_stats,
            'color_values': color_values,
            'most_common_color': max(color_stats.items(), key=lambda x: x[1]) if color_stats else None,
            'most_valuable_color': max(color_values.items(), key=lambda x: x[1]) if color_values else None
        }
    
    def get_rarity_analysis(self, collection: Collection) -> Dict[str, Any]:
        """Analyze collection by rarity distribution."""
        rarity_groups = collection.get_cards_by_rarity()
        rarity_stats = {}
        rarity_values = {}
        
        for rarity, cards in rarity_groups.items():
            rarity_stats[rarity] = sum(card.count for card in cards)
            rarity_values[rarity] = sum(card.total_value for card in cards)
        
        return {
            'rarity_distribution': rarity_stats,
            'rarity_values': rarity_values,
            'rarest_cards': self._get_rarest_cards(collection)
        }
    
    def get_duplicate_analysis(self, collection: Collection) -> Dict[str, Any]:
        """Analyze duplicate cards in collection."""
        duplicates = collection.find_duplicates()
        
        duplicate_value = sum(card.total_value for card in duplicates)
        duplicate_count = sum(card.count for card in duplicates)
        
        # Cards with highest duplicate count
        highest_duplicates = sorted(duplicates, key=lambda c: c.count, reverse=True)[:10]
        
        return {
            'total_duplicates': len(duplicates),
            'duplicate_card_count': duplicate_count,
            'duplicate_value': duplicate_value,
            'highest_duplicate_counts': highest_duplicates,
            'duplicate_percentage': (len(duplicates) / collection.unique_cards * 100) if collection.unique_cards > 0 else 0
        }
    
    def get_price_analysis(self, collection: Collection) -> Dict[str, Any]:
        """Analyze price distribution in collection."""
        cards_with_prices = [card for card in collection.cards if card.purchase_price is not None]
        
        if not cards_with_prices:
            return {
                'price_ranges': {},
                'average_price': Decimal('0'),
                'median_price': Decimal('0'),
                'price_distribution': {}
            }
        
        prices = [float(card.purchase_price) for card in cards_with_prices if card.purchase_price is not None]
        prices.sort()
        
        # Price ranges
        price_ranges = {
            '$0.00 - $0.99': 0,
            '$1.00 - $4.99': 0,
            '$5.00 - $9.99': 0,
            '$10.00 - $24.99': 0,
            '$25.00 - $49.99': 0,
            '$50.00+': 0
        }
        
        for price in prices:
            if price < 1.0:
                price_ranges['$0.00 - $0.99'] += 1
            elif price < 5.0:
                price_ranges['$1.00 - $4.99'] += 1
            elif price < 10.0:
                price_ranges['$5.00 - $9.99'] += 1
            elif price < 25.0:
                price_ranges['$10.00 - $24.99'] += 1
            elif price < 50.0:
                price_ranges['$25.00 - $49.99'] += 1
            else:
                price_ranges['$50.00+'] += 1
        
        # Calculate median
        n = len(prices)
        median_price = Decimal(str(prices[n // 2] if n % 2 == 1 else (prices[n // 2 - 1] + prices[n // 2]) / 2))
        
        return {
            'price_ranges': price_ranges,
            'average_price': self.get_average_card_value(collection),
            'median_price': median_price,
            'min_price': Decimal(str(min(prices))),
            'max_price': Decimal(str(max(prices))),
            'cards_with_prices': len(cards_with_prices),
            'cards_without_prices': collection.unique_cards - len(cards_with_prices)
        }
    
    def get_collection_growth_potential(self, collection: Collection) -> Dict[str, Any]:
        """Analyze potential areas for collection growth."""
        set_analysis = self.get_set_analysis(collection)
        color_analysis = self.get_color_analysis(collection)
        
        # Find underrepresented colors
        color_counts = color_analysis['color_distribution']
        avg_color_count = sum(color_counts.values()) / len(color_counts) if color_counts else 0
        underrepresented_colors = [color for color, count in color_counts.items() 
                                 if count < avg_color_count * 0.5]
        
        # Find sets with few cards (potential for completion)
        incomplete_sets = [(set_name, count) for set_name, count in set_analysis['top_sets_by_count'] 
                          if count < 10]  # Arbitrary threshold
        
        return {
            'underrepresented_colors': underrepresented_colors,
            'incomplete_sets': incomplete_sets[:10],
            'average_cards_per_color': avg_color_count,
            'total_unique_sets': set_analysis['total_sets']
        }
    
    def _get_rarest_cards(self, collection: Collection) -> List[Card]:
        """Get rarest cards based on available rarity data."""
        mythic_cards = []
        rare_cards = []
        
        for card in collection.cards:
            if card.rarity and card.rarity.value == 'mythic':
                mythic_cards.append(card)
            elif card.rarity and card.rarity.value == 'rare':
                rare_cards.append(card)
        
        # Sort by price as secondary indicator of rarity
        mythic_cards.sort(key=lambda c: c.purchase_price or Decimal('0'), reverse=True)
        rare_cards.sort(key=lambda c: c.purchase_price or Decimal('0'), reverse=True)
        
        return mythic_cards[:5] + rare_cards[:5]
