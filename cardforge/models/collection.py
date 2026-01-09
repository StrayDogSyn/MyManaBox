"""
CardForge Collection Models
Collection and CollectionCard for inventory management
"""

from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import Field, computed_field

from .base import BaseModel, TimestampMixin
from .card import Card
from .enums import Condition, FoilType


class Collection(BaseModel, TimestampMixin):
    """
    Represents a card collection.
    
    Users can have multiple collections (Main, Trade Binder, etc.)
    """
    
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    is_default: bool = False
    
    # Loaded cards (not persisted)
    cards: List['CollectionCard'] = Field(default_factory=list, exclude=True)
    
    @computed_field
    @property
    def total_cards(self) -> int:
        """Total card count across all entries."""
        return sum(cc.quantity for cc in self.cards)
    
    @computed_field
    @property
    def unique_cards(self) -> int:
        """Number of unique cards."""
        return len(self.cards)
    
    @computed_field
    @property
    def total_value(self) -> Decimal:
        """Total collection value."""
        return sum(cc.total_value for cc in self.cards)


class CollectionCard(BaseModel, TimestampMixin):
    """
    A card entry in a collection with quantity and condition.
    
    Maps to 'collection_cards' table.
    """
    
    id: Optional[int] = None
    collection_id: int
    card_id: int
    quantity: int = 1
    foil: str = "normal"  # 'normal', 'foil', 'etched'
    condition: str = "NM"
    language: str = "en"
    
    # Acquisition tracking
    purchase_price: Optional[Decimal] = None
    purchase_date: Optional[date] = None
    purchase_source: Optional[str] = None
    
    # External sync IDs
    manabox_id: Optional[str] = None
    moxfield_id: Optional[str] = None
    
    # User metadata
    notes: Optional[str] = None
    location: Optional[str] = None  # Physical location: 'binder-1', 'deck-box-red'
    
    # Loaded card data (not persisted)
    card: Optional[Card] = Field(default=None, exclude=True)
    
    @property
    def foil_type(self) -> FoilType:
        """Get foil type as enum."""
        return FoilType.from_string(self.foil)
    
    @property
    def condition_enum(self) -> Condition:
        """Get condition as enum."""
        return Condition.from_string(self.condition)
    
    @computed_field
    @property
    def current_price(self) -> Decimal:
        """Get current market price for this specific printing/condition."""
        if not self.card:
            return Decimal('0')
        
        base_price = self.card.get_price(self.foil_type) or Decimal('0')
        return base_price * Decimal(str(self.condition_enum.price_modifier))
    
    @computed_field
    @property
    def total_value(self) -> Decimal:
        """Total value for this line item."""
        return self.current_price * self.quantity
    
    @computed_field
    @property
    def gain_loss(self) -> Optional[Decimal]:
        """Calculate gain/loss vs purchase price."""
        if self.purchase_price is None:
            return None
        return self.total_value - (self.purchase_price * self.quantity)


class OwnershipInfo(BaseModel):
    """Aggregated ownership information for a card."""
    
    card_name: str
    oracle_id: Optional[str] = None
    scryfall_id: Optional[str] = None
    total_quantity: int = 0
    by_condition: dict = Field(default_factory=dict)  # {'NM': 3, 'LP': 1}
    by_foil: dict = Field(default_factory=dict)  # {'normal': 2, 'foil': 2}
    by_set: dict = Field(default_factory=dict)  # {'MH2': 1, 'M21': 2}
    locations: List[str] = Field(default_factory=list)
    total_value: Decimal = Decimal('0')
    
    @property
    def is_owned(self) -> bool:
        """Check if any copies are owned."""
        return self.total_quantity > 0


class CollectionStats(BaseModel):
    """Collection-level statistics."""
    
    collection_id: int
    collection_name: str
    unique_cards: int = 0
    total_cards: int = 0
    total_value: Decimal = Decimal('0')
    avg_card_value: Decimal = Decimal('0')
    foil_count: int = 0
    unique_sets: int = 0
    
    # Rarity breakdown
    mythic_count: int = 0
    rare_count: int = 0
    uncommon_count: int = 0
    common_count: int = 0
    
    # Value tiers
    bulk_count: int = 0  # < $1
    low_value_count: int = 0  # $1-10
    mid_value_count: int = 0  # $10-50
    high_value_count: int = 0  # $50+
