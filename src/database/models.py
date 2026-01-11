"""
SQLAlchemy ORM Models
=====================

Defines the database schema for CardForge using SQLAlchemy ORM.

Tables:
-------
- cards: MTG card data from Scryfall
- collection_items: User's card collection (individual card instances)
- decks: User's deck list
- deck_cards: Cards in each deck (many-to-many relationship)
- price_history: Historical price data for cards
- trades: Trade records (buying/selling/trading cards)
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    DECIMAL,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Card(Base):
    """
    MTG Card data from Scryfall API.
    
    Represents the canonical card information (not individual copies).
    """
    __tablename__ = "cards"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Scryfall identifiers
    scryfall_id: Mapped[Optional[str]] = mapped_column(String(36), unique=True, index=True)
    oracle_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    
    # Card identity
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    set_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    collector_number: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Card attributes
    mana_cost: Mapped[Optional[str]] = mapped_column(String(100))
    cmc: Mapped[float] = mapped_column(Float, default=0.0)
    type_line: Mapped[Optional[str]] = mapped_column(String(255))
    oracle_text: Mapped[Optional[str]] = mapped_column(Text)
    
    # Colors
    colors: Mapped[Optional[str]] = mapped_column(String(20))  # e.g., "W,U,B,R,G"
    color_identity: Mapped[Optional[str]] = mapped_column(String(20))  # e.g., "U,B"
    
    # Power/Toughness/Loyalty
    power: Mapped[Optional[str]] = mapped_column(String(10))
    toughness: Mapped[Optional[str]] = mapped_column(String(10))
    loyalty: Mapped[Optional[str]] = mapped_column(String(10))
    
    # Card properties
    rarity: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        index=True,
    )  # common, uncommon, rare, mythic
    
    is_foil_available: Mapped[bool] = mapped_column(Boolean, default=False)
    is_reserved_list: Mapped[bool] = mapped_column(Boolean, default=False)
    is_commander: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Legality (JSON-like string: "standard:legal,modern:banned,...")
    legalities: Mapped[Optional[str]] = mapped_column(Text)
    
    # Pricing (current/latest prices)
    price_usd: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    price_usd_foil: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    price_eur: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    price_tix: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    
    # Images
    image_uri: Mapped[Optional[str]] = mapped_column(String(500))
    image_uri_small: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relationships
    collection_items: Mapped[List["CollectionItem"]] = relationship(
        "CollectionItem",
        back_populates="card",
        cascade="all, delete-orphan",
    )
    deck_cards: Mapped[List["DeckCard"]] = relationship(
        "DeckCard",
        back_populates="card",
        cascade="all, delete-orphan",
    )
    price_history: Mapped[List["PriceHistory"]] = relationship(
        "PriceHistory",
        back_populates="card",
        cascade="all, delete-orphan",
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_card_name_set", "name", "set_code"),
        Index("idx_card_colors", "colors"),
        Index("idx_card_type", "type_line"),
    )
    
    def __repr__(self) -> str:
        return f"<Card(id={self.id}, name='{self.name}', set='{self.set_code}')>"


class CollectionItem(Base):
    """
    Individual card instance in user's collection.
    
    Represents a specific copy of a card (with condition, foil status, etc.).
    """
    __tablename__ = "collection_items"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to card
    card_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Card instance properties
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_foil: Mapped[bool] = mapped_column(Boolean, default=False)
    
    condition: Mapped[str] = mapped_column(
        String(20),
        default="near_mint",
        nullable=False,
    )  # near_mint, lightly_played, moderately_played, heavily_played, damaged
    
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    
    # Acquisition details
    acquired_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    acquired_price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    
    # Storage location
    location: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., "Binder 1 - Page 3"
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    
    # Relationships
    card: Mapped["Card"] = relationship("Card", back_populates="collection_items")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quantity_positive"),
        Index("idx_collection_card_foil", "card_id", "is_foil"),
    )
    
    def __repr__(self) -> str:
        foil_str = " (Foil)" if self.is_foil else ""
        return f"<CollectionItem(id={self.id}, card_id={self.card_id}, qty={self.quantity}{foil_str})>"


class Deck(Base):
    """
    User's deck list.
    
    Represents a collection of cards organized as a playable deck.
    """
    __tablename__ = "decks"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Deck identity
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    format: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # commander, standard, modern, legacy, vintage, etc.
    
    # Commander (for Commander format)
    commander_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("cards.id", ondelete="SET NULL"),
    )
    partner_commander_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("cards.id", ondelete="SET NULL"),
    )
    
    # Deck metadata
    description: Mapped[Optional[str]] = mapped_column(Text)
    archetype: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., "Voltron", "Storm", "Aggro"
    
    # Colors
    color_identity: Mapped[Optional[str]] = mapped_column(String(20))  # e.g., "U,B,R"
    
    # Stats
    total_cards: Mapped[int] = mapped_column(Integer, default=0)
    estimated_value: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # External references
    moxfield_url: Mapped[Optional[str]] = mapped_column(String(500))
    archidekt_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    
    # Relationships
    commander: Mapped[Optional["Card"]] = relationship(
        "Card",
        foreign_keys=[commander_id],
    )
    partner_commander: Mapped[Optional["Card"]] = relationship(
        "Card",
        foreign_keys=[partner_commander_id],
    )
    deck_cards: Mapped[List["DeckCard"]] = relationship(
        "DeckCard",
        back_populates="deck",
        cascade="all, delete-orphan",
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_deck_format_active", "format", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<Deck(id={self.id}, name='{self.name}', format='{self.format}')>"


class DeckCard(Base):
    """
    Cards in a deck (many-to-many relationship between decks and cards).
    
    Tracks which cards are in which decks, with quantity and category.
    """
    __tablename__ = "deck_cards"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    deck_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("decks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    card_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Card details in deck
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    category: Mapped[str] = mapped_column(
        String(50),
        default="mainboard",
        nullable=False,
    )  # mainboard, sideboard, maybeboard, commander
    
    is_foil: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Card role in deck (custom tags)
    tags: Mapped[Optional[str]] = mapped_column(String(255))  # e.g., "ramp,removal,wincon"
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    deck: Mapped["Deck"] = relationship("Deck", back_populates="deck_cards")
    card: Mapped["Card"] = relationship("Card", back_populates="deck_cards")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("deck_id", "card_id", "category", name="uq_deck_card_category"),
        CheckConstraint("quantity > 0", name="check_deck_card_quantity_positive"),
        Index("idx_deck_card_category", "deck_id", "category"),
    )
    
    def __repr__(self) -> str:
        return f"<DeckCard(deck_id={self.deck_id}, card_id={self.card_id}, qty={self.quantity})>"


class PriceHistory(Base):
    """
    Historical price data for cards.
    
    Tracks price changes over time for trend analysis and collection valuation.
    """
    __tablename__ = "price_history"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    card_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Price data
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    price_usd: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    price_usd_foil: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    price_eur: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    price_tix: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    
    # Source
    source: Mapped[str] = mapped_column(
        String(50),
        default="scryfall",
        nullable=False,
    )  # scryfall, tcgplayer, cardmarket, etc.
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    card: Mapped["Card"] = relationship("Card", back_populates="price_history")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("card_id", "date", "source", name="uq_price_history_card_date_source"),
        Index("idx_price_history_date", "date"),
    )
    
    def __repr__(self) -> str:
        return f"<PriceHistory(card_id={self.card_id}, date={self.date}, price=${self.price_usd})>"


class Trade(Base):
    """
    Trade records (buying/selling/trading cards).
    
    Tracks financial transactions and card movement in/out of collection.
    """
    __tablename__ = "trades"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Trade type
    trade_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )  # buy, sell, trade
    
    # Trade partner
    partner_name: Mapped[Optional[str]] = mapped_column(String(255))
    platform: Mapped[Optional[str]] = mapped_column(String(100))  # tcgplayer, ebay, local store, etc.
    
    # Financial details
    total_value: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    shipping_cost: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    
    # Trade details (JSON-like string with card IDs and quantities)
    cards_json: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )  # pending, completed, cancelled
    
    # Dates
    trade_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_trade_date_type", "trade_date", "trade_type"),
    )
    
    def __repr__(self) -> str:
        return f"<Trade(id={self.id}, type='{self.trade_type}', value=${self.total_value})>"
