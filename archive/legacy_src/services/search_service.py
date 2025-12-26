"""Search service for finding cards."""

from typing import List, Optional, Dict, Any
from ..models import Collection, Card, CardColor, CardRarity, CardType


class SearchService:
    """Service for searching and filtering cards."""
    
    def search_by_name(self, collection: Collection, query: str, 
                      case_sensitive: bool = False) -> List[Card]:
        """Search for cards by name."""
        return collection.search_by_name(query, case_sensitive)
    
    def search_by_text(self, collection: Collection, query: str, 
                      case_sensitive: bool = False) -> List[Card]:
        """Search for cards by oracle text."""
        if case_sensitive:
            return [card for card in collection.cards 
                   if card.oracle_text and query in card.oracle_text]
        else:
            query = query.lower()
            return [card for card in collection.cards 
                   if card.oracle_text and query in card.oracle_text.lower()]
    
    def filter_by_color(self, collection: Collection, colors: List[str]) -> List[Card]:
        """Filter cards by color identity."""
        color_set = set()
        color_map = {
            'white': CardColor.WHITE, 'w': CardColor.WHITE,
            'blue': CardColor.BLUE, 'u': CardColor.BLUE,
            'black': CardColor.BLACK, 'b': CardColor.BLACK,
            'red': CardColor.RED, 'r': CardColor.RED,
            'green': CardColor.GREEN, 'g': CardColor.GREEN,
            'colorless': CardColor.COLORLESS, 'c': CardColor.COLORLESS
        }
        
        for color in colors:
            if color.lower() in color_map:
                color_set.add(color_map[color.lower()])
        
        return [card for card in collection.cards 
                if card.color_identity and color_set.intersection(card.color_identity)]
    
    def filter_by_rarity(self, collection: Collection, rarities: List[str]) -> List[Card]:
        """Filter cards by rarity."""
        rarity_set = set()
        rarity_map = {
            'common': CardRarity.COMMON,
            'uncommon': CardRarity.UNCOMMON,
            'rare': CardRarity.RARE,
            'mythic': CardRarity.MYTHIC,
            'special': CardRarity.SPECIAL
        }
        
        for rarity in rarities:
            if rarity.lower() in rarity_map:
                rarity_set.add(rarity_map[rarity.lower()])
        
        return [card for card in collection.cards 
                if card.rarity and card.rarity in rarity_set]
    
    def filter_by_type(self, collection: Collection, types: List[str]) -> List[Card]:
        """Filter cards by type."""
        type_set = set()
        type_map = {
            'creature': CardType.CREATURE,
            'instant': CardType.INSTANT,
            'sorcery': CardType.SORCERY,
            'artifact': CardType.ARTIFACT,
            'enchantment': CardType.ENCHANTMENT,
            'planeswalker': CardType.PLANESWALKER,
            'land': CardType.LAND,
            'tribal': CardType.TRIBAL,
            'battle': CardType.BATTLE
        }
        
        for card_type in types:
            if card_type.lower() in type_map:
                type_set.add(type_map[card_type.lower()])
        
        return [card for card in collection.cards 
                if card.types and type_set.intersection(card.types)]
    
    def filter_by_set(self, collection: Collection, sets: List[str]) -> List[Card]:
        """Filter cards by set/edition."""
        set_codes = {s.lower() for s in sets}
        return [card for card in collection.cards 
                if card.edition.lower() in set_codes]
    
    def filter_by_price_range(self, collection: Collection, 
                             min_price: Optional[float] = None,
                             max_price: Optional[float] = None) -> List[Card]:
        """Filter cards by price range."""
        results = []
        for card in collection.cards:
            if card.purchase_price is None:
                continue
            
            price = float(card.purchase_price)
            
            if min_price is not None and price < min_price:
                continue
            
            if max_price is not None and price > max_price:
                continue
            
            results.append(card)
        
        return results
    
    def filter_by_condition(self, collection: Collection, conditions: List[str]) -> List[Card]:
        """Filter cards by condition."""
        condition_names = {c.lower() for c in conditions}
        return [card for card in collection.cards 
                if card.condition.value.lower() in condition_names]
    
    def filter_foils_only(self, collection: Collection) -> List[Card]:
        """Get only foil cards."""
        return [card for card in collection.cards if card.foil]
    
    def filter_non_foils_only(self, collection: Collection) -> List[Card]:
        """Get only non-foil cards."""
        return [card for card in collection.cards if not card.foil]
    
    def find_duplicates(self, collection: Collection) -> List[Card]:
        """Find duplicate cards in collection."""
        return collection.find_duplicates()
    
    def advanced_search(self, collection: Collection, criteria: Dict[str, Any]) -> List[Card]:
        """Perform advanced search with multiple criteria."""
        results = collection.cards.copy()
        
        # Apply name filter
        if 'name' in criteria:
            name_query = criteria['name']
            case_sensitive = criteria.get('case_sensitive', False)
            if case_sensitive:
                results = [card for card in results if name_query in card.name]
            else:
                name_query = name_query.lower()
                results = [card for card in results if name_query in card.name.lower()]
        
        # Apply text filter
        if 'text' in criteria:
            text_query = criteria['text']
            case_sensitive = criteria.get('case_sensitive', False)
            if case_sensitive:
                results = [card for card in results 
                          if card.oracle_text and text_query in card.oracle_text]
            else:
                text_query = text_query.lower()
                results = [card for card in results 
                          if card.oracle_text and text_query in card.oracle_text.lower()]
        
        # Apply color filter
        if 'colors' in criteria:
            temp_collection = Collection(cards=results)
            results = self.filter_by_color(temp_collection, criteria['colors'])
        
        # Apply rarity filter
        if 'rarities' in criteria:
            temp_collection = Collection(cards=results)
            results = self.filter_by_rarity(temp_collection, criteria['rarities'])
        
        # Apply type filter
        if 'types' in criteria:
            temp_collection = Collection(cards=results)
            results = self.filter_by_type(temp_collection, criteria['types'])
        
        # Apply set filter
        if 'sets' in criteria:
            temp_collection = Collection(cards=results)
            results = self.filter_by_set(temp_collection, criteria['sets'])
        
        # Apply price range filter
        if 'min_price' in criteria or 'max_price' in criteria:
            temp_collection = Collection(cards=results)
            results = self.filter_by_price_range(
                temp_collection, 
                criteria.get('min_price'),
                criteria.get('max_price')
            )
        
        # Apply condition filter
        if 'conditions' in criteria:
            temp_collection = Collection(cards=results)
            results = self.filter_by_condition(temp_collection, criteria['conditions'])
        
        # Apply foil filter
        if 'foil_only' in criteria and criteria['foil_only']:
            results = [card for card in results if card.foil]
        elif 'non_foil_only' in criteria and criteria['non_foil_only']:
            results = [card for card in results if not card.foil]
        
        return results
