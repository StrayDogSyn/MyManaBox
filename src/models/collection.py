"""Collection data model."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from decimal import Decimal
from collections import defaultdict, Counter
from .card import Card
from .enums import CardColor, CardRarity, CardType, Condition


@dataclass
class Collection:
    """Represents a collection of Magic cards."""
    
    cards: List[Card] = field(default_factory=list)
    name: str = "My Collection"
    
    def add_card(self, card: Card) -> None:
        """Add a card to the collection."""
        # Check if card already exists (same name and edition)
        for existing_card in self.cards:
            if existing_card.name == card.name and existing_card.edition == card.edition:
                existing_card.count += card.count
                return
        
        # Add as new card
        self.cards.append(card)
    
    def remove_card(self, card: Card, count: Optional[int] = None) -> bool:
        """Remove card(s) from collection. Returns True if successful."""
        for existing_card in self.cards:
            if existing_card.name == card.name and existing_card.edition == card.edition:
                remove_count = count if count is not None else existing_card.count
                
                if remove_count >= existing_card.count:
                    self.cards.remove(existing_card)
                else:
                    existing_card.count -= remove_count
                return True
        return False
    
    @property
    def total_cards(self) -> int:
        """Total number of individual cards."""
        return sum(card.count for card in self.cards)
    
    @property
    def unique_cards(self) -> int:
        """Number of unique cards (ignoring count)."""
        return len(self.cards)
    
    @property
    def total_value(self) -> Decimal:
        """Total value of all cards."""
        return sum((card.total_value for card in self.cards), Decimal('0'))
    
    def get_cards_by_color(self) -> Dict[str, List[Card]]:
        """Group cards by color identity."""
        color_groups = {
            'White': [],
            'Blue': [],
            'Black': [],
            'Red': [],
            'Green': [],
            'Colorless': [],
            'Multicolor': []
        }
        
        for card in self.cards:
            if card.is_colorless:
                color_groups['Colorless'].append(card)
            elif card.is_multicolor:
                color_groups['Multicolor'].append(card)
            elif card.color_identity:
                # Single color
                color_map = {
                    CardColor.WHITE: 'White',
                    CardColor.BLUE: 'Blue',
                    CardColor.BLACK: 'Black',
                    CardColor.RED: 'Red',
                    CardColor.GREEN: 'Green'
                }
                for color in card.color_identity:
                    if color in color_map:
                        color_groups[color_map[color]].append(card)
                        break
            else:
                # Fallback to heuristic-based sorting for cards without API data
                color_groups.update(self._heuristic_color_sort([card]))
        
        return color_groups
    
    def get_cards_by_set(self) -> Dict[str, List[Card]]:
        """Group cards by set/edition."""
        return {edition: [card for card in self.cards if card.edition == edition] 
                for edition in set(card.edition for card in self.cards)}
    
    def get_cards_by_rarity(self) -> Dict[str, List[Card]]:
        """Group cards by rarity."""
        rarity_groups = defaultdict(list)
        
        for card in self.cards:
            if card.rarity:
                rarity_groups[card.rarity.value].append(card)
            else:
                # Fallback to price-based heuristic
                if card.purchase_price is None or card.purchase_price == 0:
                    rarity_groups['common'].append(card)
                elif card.purchase_price < Decimal('0.50'):
                    rarity_groups['common'].append(card)
                elif card.purchase_price < Decimal('2.00'):
                    rarity_groups['uncommon'].append(card)
                elif card.purchase_price < Decimal('10.00'):
                    rarity_groups['rare'].append(card)
                else:
                    rarity_groups['mythic'].append(card)
        
        return dict(rarity_groups)
    
    def get_cards_by_type(self) -> Dict[str, List[Card]]:
        """Group cards by card type."""
        type_groups = defaultdict(list)
        
        for card in self.cards:
            if card.types:
                # Use API data
                primary_type = next(iter(card.types), CardType.CREATURE)
                type_groups[primary_type.value].append(card)
            else:
                # Fallback to heuristic
                type_groups.update(self._heuristic_type_sort([card]))
        
        return dict(type_groups)
    
    def find_duplicates(self) -> List[Card]:
        """Find cards that appear multiple times."""
        return [card for card in self.cards if card.count > 1]
    
    def search_by_name(self, query: str, case_sensitive: bool = False) -> List[Card]:
        """Search for cards by name."""
        if case_sensitive:
            return [card for card in self.cards if query in card.name]
        else:
            query = query.lower()
            return [card for card in self.cards if query in card.name.lower()]
    
    def get_condition_stats(self) -> Dict[str, int]:
        """Get card count by condition."""
        condition_count = Counter()
        for card in self.cards:
            condition_count[card.condition.value] += card.count
        return dict(condition_count)
    
    def get_set_stats(self) -> Dict[str, int]:
        """Get card count by set."""
        set_count = Counter()
        for card in self.cards:
            set_count[card.edition] += card.count
        return dict(set_count)
    
    def get_foil_stats(self) -> Dict[str, int]:
        """Get foil vs non-foil statistics."""
        foil_count = sum(card.count for card in self.cards if card.foil)
        non_foil_count = sum(card.count for card in self.cards if not card.foil)
        return {"Foil": foil_count, "Non-foil": non_foil_count}
    
    def get_most_valuable_cards(self, limit: int = 10) -> List[Card]:
        """Get the most valuable cards by individual price."""
        cards_with_prices = [card for card in self.cards if card.purchase_price is not None]
        return sorted(
            cards_with_prices,
            key=lambda c: c.purchase_price or Decimal('0'),
            reverse=True
        )[:limit]
    
    def _heuristic_color_sort(self, cards: List[Card]) -> Dict[str, List[Card]]:
        """Fallback color sorting based on card names."""
        color_groups = {
            'White': [],
            'Blue': [],
            'Black': [],
            'Red': [],
            'Green': [],
            'Colorless': [],
            'Multicolor': []
        }
        
        for card in cards:
            name = card.name.lower()
            
            if any(word in name for word in ['swamp', 'black', 'dark', 'death', 'shadow']):
                color_groups['Black'].append(card)
            elif any(word in name for word in ['island', 'blue', 'water', 'counter', 'draw']):
                color_groups['Blue'].append(card)
            elif any(word in name for word in ['plains', 'white', 'angel', 'heal', 'life']):
                color_groups['White'].append(card)
            elif any(word in name for word in ['mountain', 'red', 'fire', 'lightning', 'burn']):
                color_groups['Red'].append(card)
            elif any(word in name for word in ['forest', 'green', 'elf', 'growth', 'nature']):
                color_groups['Green'].append(card)
            elif any(word in name for word in ['artifact', 'colorless']):
                color_groups['Colorless'].append(card)
            else:
                color_groups['Multicolor'].append(card)
        
        return color_groups
    
    def _heuristic_type_sort(self, cards: List[Card]) -> Dict[str, List[Card]]:
        """Fallback type sorting based on card names."""
        type_groups = {
            'Creatures': [],
            'Instants': [],
            'Sorceries': [],
            'Artifacts': [],
            'Enchantments': [],
            'Planeswalkers': [],
            'Lands': [],
            'Other': []
        }
        
        for card in cards:
            name = card.name.lower()
            
            if any(word in name for word in ['swamp', 'island', 'plains', 'mountain', 'forest', 'hub', 'wastes']):
                type_groups['Lands'].append(card)
            elif any(word in name for word in ['angel', 'demon', 'dragon', 'elf', 'knight', 'beast', 'warrior']):
                type_groups['Creatures'].append(card)
            elif any(word in name for word in ['artifact', 'equipment', 'vehicle']):
                type_groups['Artifacts'].append(card)
            else:
                type_groups['Other'].append(card)
        
        return type_groups
    
    @classmethod
    def from_csv_data(cls, csv_data: List[dict], name: str = "My Collection") -> 'Collection':
        """Create Collection from CSV data."""
        cards = [Card.from_csv_row(row) for row in csv_data]
        return cls(cards=cards, name=name)
