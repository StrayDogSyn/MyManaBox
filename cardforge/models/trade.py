"""
CardForge Trade Models
Buy list and sell list management
"""

from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import Field, computed_field

from .base import BaseModel, TimestampMixin
from .card import Card
from .enums import (
    BuyListStatus, SellListStatus, SellReason, 
    DeckCategory, Condition, FoilType
)


class BuyListItem(BaseModel, TimestampMixin):
    """
    A card on the buy list.
    
    Maps to 'buy_list' table.
    """
    
    id: Optional[int] = None
    card_id: int
    deck_id: Optional[int] = None
    
    # Priority & targeting
    priority: int = 3  # 1=urgent, 2=high, 3=medium, 4=low, 5=someday
    quantity_needed: int = 1
    max_price: Optional[Decimal] = None
    preferred_condition: str = "NM"
    accept_foil: bool = True
    
    # Best deal tracking
    best_price: Optional[Decimal] = None
    best_source: Optional[str] = None
    best_url: Optional[str] = None
    price_last_checked: Optional[datetime] = None
    
    # Status
    status: str = "wanted"  # 'wanted', 'ordered', 'shipped', 'received', 'cancelled'
    
    # Acquisition
    purchased_price: Optional[Decimal] = None
    purchased_source: Optional[str] = None
    purchased_at: Optional[datetime] = None
    
    notes: Optional[str] = None
    
    # Loaded data (not persisted)
    card: Optional[Card] = Field(default=None, exclude=True)
    card_name: Optional[str] = Field(default=None, exclude=True)  # For display
    deck_name: Optional[str] = Field(default=None, exclude=True)
    category: Optional[str] = Field(default=None, exclude=True)
    
    @property
    def status_enum(self) -> BuyListStatus:
        """Get status as enum."""
        return BuyListStatus(self.status)
    
    @computed_field
    @property
    def total_cost(self) -> Decimal:
        """Total cost at best price."""
        if self.best_price:
            return self.best_price * self.quantity_needed
        return Decimal('0')
    
    @computed_field
    @property
    def is_within_budget(self) -> bool:
        """Check if best price is within max price budget."""
        if not self.max_price or not self.best_price:
            return True
        return self.best_price <= self.max_price
    
    @property
    def priority_label(self) -> str:
        """Human-readable priority."""
        labels = {
            1: "Urgent",
            2: "High",
            3: "Medium",
            4: "Low",
            5: "Someday"
        }
        return labels.get(self.priority, "Unknown")


class SellListItem(BaseModel, TimestampMixin):
    """
    A card on the sell list.
    
    Maps to 'sell_list' table.
    """
    
    id: Optional[int] = None
    collection_card_id: int
    
    # Selling parameters
    reason: Optional[str] = None  # 'duplicate', 'not_needed', 'upgrade', 'cash_out'
    quantity_to_sell: int = 1
    min_price: Optional[Decimal] = None
    
    # Best buylist tracking
    best_buylist_price: Optional[Decimal] = None
    best_buylist_source: Optional[str] = None
    best_tcgplayer_price: Optional[Decimal] = None
    price_last_checked: Optional[datetime] = None
    
    # Listing status
    status: str = "considering"  # 'considering', 'listed', 'sold', 'removed'
    listed_platform: Optional[str] = None
    listed_price: Optional[Decimal] = None
    listed_at: Optional[datetime] = None
    
    # Sale completion
    sold_price: Optional[Decimal] = None
    sold_to: Optional[str] = None
    sold_at: Optional[datetime] = None
    
    notes: Optional[str] = None
    
    # Loaded data (not persisted)
    card_name: Optional[str] = Field(default=None, exclude=True)
    set_code: Optional[str] = Field(default=None, exclude=True)
    current_market_price: Optional[Decimal] = Field(default=None, exclude=True)
    
    @property
    def status_enum(self) -> SellListStatus:
        """Get status as enum."""
        return SellListStatus(self.status)
    
    @property
    def reason_enum(self) -> Optional[SellReason]:
        """Get reason as enum."""
        try:
            return SellReason(self.reason) if self.reason else None
        except ValueError:
            return None
    
    @computed_field
    @property
    def potential_value(self) -> Decimal:
        """Potential value from sale."""
        price = self.best_buylist_price or self.best_tcgplayer_price or Decimal('0')
        return price * self.quantity_to_sell
    
    @computed_field
    @property
    def spread(self) -> Optional[Decimal]:
        """Spread between market and buylist price."""
        if self.best_tcgplayer_price and self.best_buylist_price:
            return self.best_tcgplayer_price - self.best_buylist_price
        return None


class BuyListSummary(BaseModel):
    """Summary of buy list."""
    
    total_items: int = 0
    total_cards: int = 0  # Sum of quantities
    total_cost: Decimal = Decimal('0')
    
    # By priority
    by_priority: dict = Field(default_factory=dict)  # {1: 5, 2: 10, ...}
    
    # By status
    by_status: dict = Field(default_factory=dict)  # {'wanted': 15, 'ordered': 3, ...}
    
    # By deck
    by_deck: dict = Field(default_factory=dict)  # {'Deck Name': 10, ...}
    
    # Budget analysis
    within_budget_count: int = 0
    over_budget_count: int = 0


class SellListSummary(BaseModel):
    """Summary of sell list."""
    
    total_items: int = 0
    total_cards: int = 0  # Sum of quantities
    potential_value: Decimal = Decimal('0')
    
    # By reason
    by_reason: dict = Field(default_factory=dict)
    
    # By status
    by_status: dict = Field(default_factory=dict)
    
    # Value tiers
    high_value_count: int = 0  # $10+
    mid_value_count: int = 0   # $1-10
    bulk_count: int = 0        # < $1


class DuplicateCard(BaseModel):
    """A duplicate card eligible for selling."""
    
    oracle_id: str
    card_name: str
    total_owned: int = 0
    needed_in_decks: int = 0
    safe_to_sell: int = 0
    
    # Breakdown by printing
    printings: List[dict] = Field(default_factory=list)
    
    # Best pricing
    highest_price: Optional[Decimal] = None
    best_printing_to_sell: Optional[str] = None
    
    # Total potential value
    potential_value: Decimal = Decimal('0')
