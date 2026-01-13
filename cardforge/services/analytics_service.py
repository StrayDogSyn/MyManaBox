"""
CardForge Analytics Service
Collection-wide statistics and analysis
"""

from typing import Dict, List, Any
from decimal import Decimal
from collections import Counter

from cardforge.repositories import CollectionRepository, CollectionCardRepository
from cardforge.models import Rarity, CardColor

class AnalyticsService:
    """Service for collection analytics."""
    
    def __init__(self):
        self.collection_repo = CollectionRepository()
        self.card_entry_repo = CollectionCardRepository()
        
    async def get_collection_summary(self, collection_id: int) -> Dict[str, Any]:
        """Get high-level collection summary."""
        cards = await self.card_entry_repo.get_with_card_data(collection_id, limit=100000)
        
        if not cards:
            return {
                "total_cards": 0,
                "unique_cards": 0,
                "total_value": 0,
                "top_cards": []
            }
            
        total_qty = sum(c.quantity for c in cards)
        total_value = sum((c.purchase_price or Decimal(0)) * c.quantity for c in cards)
        
        # Sort by value
        sorted_cards = sorted(
            cards, 
            key=lambda c: (c.purchase_price or Decimal(0)) * c.quantity, 
            reverse=True
        )
        
        return {
            "total_cards": total_qty,
            "unique_cards": len(cards),
            "total_value": float(total_value),
            "top_cards": [
                {
                    "name": c.card.name,
                    "quantity": c.quantity,
                    "value": float((c.purchase_price or Decimal(0)) * c.quantity)
                }
                for c in sorted_cards[:5]
            ]
        }

    async def get_color_distribution(self, collection_id: int) -> Dict[str, int]:
        """Get distribution of cards by color."""
        cards = await self.card_entry_repo.get_with_card_data(collection_id, limit=100000)
        colors = []
        for c in cards:
            if c.card and c.card.colors:
                # Handle single colors or multicolor
                if len(c.card.colors) > 1:
                    colors.append("Multicolor")
                else:
                    colors.append(c.card.colors[0])
            else:
                colors.append("Colorless")
                
        return dict(Counter(colors))

    async def get_rarity_distribution(self, collection_id: int) -> Dict[str, int]:
        """Get distribution by rarity."""
        cards = await self.card_entry_repo.get_with_card_data(collection_id, limit=100000)
        rarities = [c.card.rarity for c in cards if c.card]
        return dict(Counter(rarities))

    async def get_set_completion(self, collection_id: int) -> List[Dict[str, Any]]:
        """Get completion status for top sets."""
        cards = await self.card_entry_repo.get_with_card_data(collection_id, limit=100000)
        
        sets = Counter(c.card.set_code for c in cards if c.card)
        
        # In a real app we'd query SetRepository for total set sizes
        # For now we just return counts
        return [
            {"set_code": code, "owned": count}
            for code, count in sets.most_common(10)
        ]
