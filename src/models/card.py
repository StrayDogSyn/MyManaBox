"""Card data model."""

from dataclasses import dataclass
from typing import Optional, Set, List
from decimal import Decimal
from .enums import CardColor, CardRarity, CardType, Condition


@dataclass
class Card:
    """Represents a Magic: The Gathering card."""
    
    name: str
    edition: str
    count: int = 1
    purchase_price: Optional[Decimal] = None
    condition: Condition = Condition.NEAR_MINT
    foil: bool = False
    
    # Additional metadata (can be enriched from API)
    colors: Optional[Set[CardColor]] = None
    color_identity: Optional[Set[CardColor]] = None
    rarity: Optional[CardRarity] = None
    types: Optional[Set[CardType]] = None
    type_line: Optional[str] = None
    mana_cost: Optional[str] = None
    cmc: Optional[int] = None
    oracle_text: Optional[str] = None
    scryfall_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default collections."""
        if self.colors is None:
            self.colors = set()
        if self.color_identity is None:
            self.color_identity = set()
        if self.types is None:
            self.types = set()
    
    @property
    def is_multicolor(self) -> bool:
        """Check if card is multicolor."""
        return len(self.color_identity or set()) > 1
    
    @property
    def is_colorless(self) -> bool:
        """Check if card is colorless."""
        colors = self.color_identity or set()
        return len(colors) == 0 or CardColor.COLORLESS in colors
    
    @property
    def total_value(self) -> Decimal:
        """Calculate total value of all copies."""
        if self.purchase_price is None:
            return Decimal('0')
        return self.purchase_price * self.count
    
    @classmethod
    def from_csv_row(cls, row_data: dict) -> 'Card':
        """Create Card from CSV row data."""
        # Parse purchase price
        price_str = str(row_data.get('Purchase Price', '')).replace('$', '').strip()
        purchase_price = None
        if price_str and price_str != 'nan':
            try:
                purchase_price = Decimal(price_str)
            except (ValueError, TypeError):
                purchase_price = None
        
        # Parse condition
        condition_str = row_data.get('Condition', 'Near Mint')
        condition = Condition.NEAR_MINT
        for cond in Condition:
            if cond.value.lower() == condition_str.lower():
                condition = cond
                break
        
        # Parse foil status
        foil_str = str(row_data.get('Foil', '')).strip()
        foil = bool(foil_str and foil_str.lower() not in ['', 'false', 'no', '0'])
        
        return cls(
            name=row_data.get('Name', ''),
            edition=row_data.get('Edition', ''),
            count=int(row_data.get('Count', 1)),
            purchase_price=purchase_price,
            condition=condition,
            foil=foil
        )
    
    def to_dict(self) -> dict:
        """Convert Card to dictionary for CSV export."""
        return {
            'Name': self.name,
            'Edition': self.edition,
            'Count': self.count,
            'Purchase Price': f"${self.purchase_price}" if self.purchase_price else "",
            'Condition': self.condition.value,
            'Foil': "Yes" if self.foil else ""
        }
