"""
CardForge Deck Models
Deck building and management with category tracking
"""

from typing import Optional, List, Dict
from datetime import datetime, date
from decimal import Decimal
from pydantic import Field, computed_field

from .base import BaseModel, TimestampMixin
from .card import Card
from .enums import Format, DeckCategory


class Deck(BaseModel, TimestampMixin):
    """
    Represents a constructed deck.
    
    Maps to 'decks' table with full tracking for formats,
    commander support, and external platform sync.
    """
    
    id: Optional[int] = None
    name: str
    format: str  # 'commander', 'standard', etc.
    commander_id: Optional[int] = None
    partner_id: Optional[int] = None
    colors: Optional[List[str]] = None
    description: Optional[str] = None
    
    # External platform IDs
    moxfield_id: Optional[str] = None
    archidekt_id: Optional[str] = None
    manabox_deck_id: Optional[str] = None
    
    # Deck metadata
    is_active: bool = True
    power_level: Optional[int] = None  # 1-10 scale
    budget_target: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    
    # Performance tracking
    win_rate: Optional[float] = None
    games_played: int = 0
    games_won: int = 0
    last_played: Optional[date] = None
    
    # Tags for organization
    tags: Optional[List[str]] = None
    
    # Loaded data (not persisted)
    cards: List['DeckCard'] = Field(default_factory=list, exclude=True)
    commander: Optional[Card] = Field(default=None, exclude=True)
    partner: Optional[Card] = Field(default=None, exclude=True)
    
    @property
    def format_enum(self) -> Optional[Format]:
        """Get format as enum."""
        try:
            return Format(self.format.lower())
        except ValueError:
            return None
    
    @computed_field
    @property
    def total_cards(self) -> int:
        """Total cards in deck (excluding maybeboard)."""
        return sum(
            dc.quantity for dc in self.cards 
            if not dc.is_maybeboard
        )
    
    @computed_field
    @property
    def mainboard_count(self) -> int:
        """Cards in mainboard."""
        return sum(
            dc.quantity for dc in self.cards 
            if not dc.is_sideboard and not dc.is_maybeboard
        )
    
    @computed_field
    @property
    def sideboard_count(self) -> int:
        """Cards in sideboard."""
        return sum(
            dc.quantity for dc in self.cards 
            if dc.is_sideboard
        )
    
    @computed_field
    @property
    def completion_percentage(self) -> float:
        """Percentage of deck owned."""
        total = sum(dc.quantity for dc in self.cards if not dc.is_maybeboard)
        owned = sum(min(dc.owned_quantity, dc.quantity) for dc in self.cards if not dc.is_maybeboard)
        return (owned / total * 100) if total > 0 else 0
    
    def get_cards_by_category(self, category: DeckCategory) -> List['DeckCard']:
        """Get cards in a specific category."""
        return [dc for dc in self.cards if dc.category == category.value]
    
    def get_missing_cards(self) -> List['DeckCard']:
        """Get cards not fully owned."""
        return [
            dc for dc in self.cards 
            if not dc.is_maybeboard and dc.owned_quantity < dc.quantity
        ]


class DeckCard(BaseModel):
    """
    A card entry in a deck with quantity and categorization.
    
    Maps to 'deck_cards' table.
    """
    
    id: Optional[int] = None
    deck_id: int
    card_id: int
    quantity: int = 1
    
    # Card role
    is_commander: bool = False
    is_sideboard: bool = False
    is_maybeboard: bool = False
    
    # Categorization for deck analysis
    category: Optional[str] = None
    
    # Ownership tracking
    owned_quantity: int = 0
    
    created_at: Optional[datetime] = None
    
    # Loaded card data (not persisted)
    card: Optional[Card] = Field(default=None, exclude=True)
    
    @property
    def category_enum(self) -> Optional[DeckCategory]:
        """Get category as enum."""
        try:
            return DeckCategory(self.category) if self.category else None
        except ValueError:
            return None
    
    @computed_field
    @property
    def is_owned(self) -> bool:
        """Check if enough copies are owned."""
        return self.owned_quantity >= self.quantity
    
    @computed_field
    @property
    def missing_quantity(self) -> int:
        """How many more copies are needed."""
        return max(0, self.quantity - self.owned_quantity)
    
    @computed_field
    @property
    def value(self) -> Decimal:
        """Total value of this deck slot."""
        if not self.card:
            return Decimal('0')
        price = self.card.get_price() or Decimal('0')
        return price * self.quantity


class DeckAnalysis(BaseModel):
    """Comprehensive deck analysis results."""
    
    deck_id: int
    deck_name: str
    format: str
    commander_name: Optional[str] = None
    
    # Basic stats
    total_cards: int = 0
    total_value: Decimal = Decimal('0')
    
    # Mana curve: CMC -> count
    mana_curve: Dict[int, int] = Field(default_factory=dict)
    
    # Color distribution
    color_distribution: Dict[str, int] = Field(default_factory=dict)
    color_pips: Dict[str, int] = Field(default_factory=dict)  # Mana pips by color
    
    # Category breakdown
    category_breakdown: Dict[str, int] = Field(default_factory=dict)
    
    # Type breakdown
    creature_count: int = 0
    land_count: int = 0
    instant_count: int = 0
    sorcery_count: int = 0
    artifact_count: int = 0
    enchantment_count: int = 0
    planeswalker_count: int = 0
    
    # Ownership
    missing_cards: List[Dict] = Field(default_factory=list)
    completion_percentage: float = 0.0
    missing_value: Decimal = Decimal('0')
    
    # Computed stats
    avg_cmc: float = 0.0
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)


class MissingCard(BaseModel):
    """Card missing from a deck."""
    
    card_name: str
    scryfall_id: str
    set_code: Optional[str] = None
    quantity_needed: int = 1
    category: Optional[str] = None
    current_price: Optional[Decimal] = None
    priority: int = 3  # 1-5, lower = higher


class GameRecord(BaseModel, TimestampMixin):
    """Record of a game played with a deck."""
    
    id: Optional[int] = None
    deck_id: int
    played_at: Optional[datetime] = None
    
    # Outcome
    result: str  # 'win', 'loss', 'draw', 'scoop'
    position: Optional[int] = None  # 1st, 2nd, etc.
    total_players: int = 4
    
    # Metrics
    turn_count: Optional[int] = None
    commander_cast_count: Optional[int] = None
    elimination_turn: Optional[int] = None
    
    # Win condition
    win_condition: Optional[str] = None
    key_cards: Optional[List[str]] = None
    
    # Opponents
    opponents: Optional[List[str]] = None
    
    # Context
    notes: Optional[str] = None
    event_name: Optional[str] = None
    location: Optional[str] = None
