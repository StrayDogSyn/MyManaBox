"""
CardForge Card Model
Represents MTG cards with full Scryfall data
"""

from typing import Optional, List, Dict, Any, Set
from datetime import datetime
from decimal import Decimal
from pydantic import Field, computed_field

from .base import BaseModel, TimestampMixin
from .enums import (
    CardColor, Rarity, CardLayout, CardType, 
    Legality, FoilType, Condition
)


class CardFace(BaseModel):
    """Represents one face of a multi-faced card."""
    
    id: Optional[int] = None
    card_id: Optional[int] = None
    face_index: int = 0
    name: str
    mana_cost: Optional[str] = None
    type_line: Optional[str] = None
    oracle_text: Optional[str] = None
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None
    defense: Optional[str] = None
    colors: Optional[List[str]] = None
    image_uri: Optional[str] = None


class CardPrices(BaseModel):
    """Card pricing data from various sources."""
    
    usd: Optional[Decimal] = None
    usd_foil: Optional[Decimal] = None
    usd_etched: Optional[Decimal] = None
    eur: Optional[Decimal] = None
    eur_foil: Optional[Decimal] = None
    tix: Optional[Decimal] = None  # MTGO tickets
    
    def get_price(self, foil_type: FoilType = FoilType.NORMAL) -> Optional[Decimal]:
        """Get price for specific foil type."""
        if foil_type == FoilType.FOIL:
            return self.usd_foil
        if foil_type == FoilType.ETCHED:
            return self.usd_etched
        return self.usd


class Card(BaseModel, TimestampMixin):
    """
    Represents a Magic: The Gathering card.
    
    Maps to the 'cards' table with full Scryfall data normalization.
    """
    
    # Primary identification
    id: Optional[int] = None
    scryfall_id: str
    oracle_id: Optional[str] = None
    name: str
    
    # Set information
    set_code: Optional[str] = None
    collector_number: Optional[str] = None
    rarity: Optional[str] = None
    
    # Colors
    colors: Optional[List[str]] = Field(default=None)
    color_identity: Optional[List[str]] = Field(default=None)
    
    # Mana
    mana_cost: Optional[str] = None
    cmc: Optional[float] = None
    
    # Type information
    type_line: Optional[str] = None
    oracle_text: Optional[str] = None
    
    # Stats
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None
    defense: Optional[str] = None
    
    # Card structure
    layout: Optional[str] = None
    
    # Images
    image_uris: Optional[Dict[str, str]] = None
    
    # Pricing (JSON from Scryfall)
    prices_json: Optional[Dict[str, Any]] = None
    
    # Legalities
    legalities_json: Optional[Dict[str, str]] = None
    
    # Keywords
    keywords: Optional[List[str]] = None
    produced_mana: Optional[List[str]] = None
    
    # Rankings
    edhrec_rank: Optional[int] = None
    penny_rank: Optional[int] = None
    
    # Metadata flags
    reserved: bool = False
    reprint: bool = False
    digital: bool = False
    promo: bool = False
    full_art: bool = False
    textless: bool = False
    
    # External IDs
    tcgplayer_id: Optional[int] = None
    cardmarket_id: Optional[int] = None
    mtgo_id: Optional[int] = None
    arena_id: Optional[int] = None
    
    # Multi-face cards
    card_faces: Optional[List[CardFace]] = None
    
    # Computed properties
    @computed_field
    @property
    def color_set(self) -> Set[CardColor]:
        """Get colors as CardColor enum set."""
        return CardColor.from_list(self.colors or [])
    
    @computed_field
    @property
    def color_identity_set(self) -> Set[CardColor]:
        """Get color identity as CardColor enum set."""
        return CardColor.from_list(self.color_identity or [])
    
    @computed_field
    @property
    def rarity_enum(self) -> Optional[Rarity]:
        """Get rarity as enum."""
        return Rarity.from_string(self.rarity) if self.rarity else None
    
    @computed_field
    @property
    def card_types(self) -> Set[CardType]:
        """Extract card types from type line."""
        return CardType.from_type_line(self.type_line or '')
    
    @computed_field
    @property
    def is_creature(self) -> bool:
        """Check if card is a creature."""
        return CardType.CREATURE in self.card_types
    
    @computed_field
    @property
    def is_land(self) -> bool:
        """Check if card is a land."""
        return CardType.LAND in self.card_types
    
    @computed_field
    @property
    def layout_enum(self) -> Optional[CardLayout]:
        """Get layout as enum."""
        try:
            return CardLayout(self.layout) if self.layout else None
        except ValueError:
            return None
    
    @computed_field
    @property
    def has_multiple_faces(self) -> bool:
        """Check if card has multiple faces."""
        layout = self.layout_enum
        return layout.has_multiple_faces if layout else False
    
    @property
    def prices(self) -> CardPrices:
        """Get structured prices."""
        if not self.prices_json:
            return CardPrices()
        
        return CardPrices(
            usd=Decimal(self.prices_json.get('usd')) if self.prices_json.get('usd') else None,
            usd_foil=Decimal(self.prices_json.get('usd_foil')) if self.prices_json.get('usd_foil') else None,
            usd_etched=Decimal(self.prices_json.get('usd_etched')) if self.prices_json.get('usd_etched') else None,
            eur=Decimal(self.prices_json.get('eur')) if self.prices_json.get('eur') else None,
            eur_foil=Decimal(self.prices_json.get('eur_foil')) if self.prices_json.get('eur_foil') else None,
            tix=Decimal(self.prices_json.get('tix')) if self.prices_json.get('tix') else None,
        )
    
    def get_price(self, foil_type: FoilType = FoilType.NORMAL) -> Optional[Decimal]:
        """Get price for specific foil type."""
        return self.prices.get_price(foil_type)
    
    def is_legal_in(self, format_name: str) -> bool:
        """Check if card is legal in a format."""
        if not self.legalities_json:
            return False
        
        legality = self.legalities_json.get(format_name.lower())
        return legality in ('legal', 'restricted')
    
    def get_legality(self, format_name: str) -> Legality:
        """Get legality status for a format."""
        if not self.legalities_json:
            return Legality.NOT_LEGAL
        
        legality_str = self.legalities_json.get(format_name.lower(), 'not_legal')
        try:
            return Legality(legality_str)
        except ValueError:
            return Legality.NOT_LEGAL
    
    def get_image_uri(self, size: str = 'normal') -> Optional[str]:
        """Get image URI for specified size."""
        if not self.image_uris:
            return None
        return self.image_uris.get(size)
    
    @classmethod
    def from_scryfall(cls, data: Dict[str, Any]) -> 'Card':
        """Create Card from Scryfall API response."""
        # Handle card faces for multi-faced cards
        card_faces = None
        if 'card_faces' in data and data['card_faces']:
            card_faces = [
                CardFace(
                    face_index=i,
                    name=face.get('name', ''),
                    mana_cost=face.get('mana_cost'),
                    type_line=face.get('type_line'),
                    oracle_text=face.get('oracle_text'),
                    power=face.get('power'),
                    toughness=face.get('toughness'),
                    loyalty=face.get('loyalty'),
                    defense=face.get('defense'),
                    colors=face.get('colors'),
                    image_uri=face.get('image_uris', {}).get('normal'),
                )
                for i, face in enumerate(data['card_faces'])
            ]
        
        return cls(
            scryfall_id=data['id'],
            oracle_id=data.get('oracle_id'),
            name=data['name'],
            set_code=data.get('set'),
            collector_number=data.get('collector_number'),
            rarity=data.get('rarity'),
            colors=data.get('colors'),
            color_identity=data.get('color_identity'),
            mana_cost=data.get('mana_cost'),
            cmc=data.get('cmc'),
            type_line=data.get('type_line'),
            oracle_text=data.get('oracle_text'),
            power=data.get('power'),
            toughness=data.get('toughness'),
            loyalty=data.get('loyalty'),
            defense=data.get('defense'),
            layout=data.get('layout'),
            image_uris=data.get('image_uris'),
            prices_json=data.get('prices'),
            legalities_json=data.get('legalities'),
            keywords=data.get('keywords'),
            produced_mana=data.get('produced_mana'),
            edhrec_rank=data.get('edhrec_rank'),
            penny_rank=data.get('penny_rank'),
            reserved=data.get('reserved', False),
            reprint=data.get('reprint', False),
            digital=data.get('digital', False),
            promo=data.get('promo', False),
            full_art=data.get('full_art', False),
            textless=data.get('textless', False),
            tcgplayer_id=data.get('tcgplayer_id'),
            cardmarket_id=data.get('cardmarket_id'),
            mtgo_id=data.get('mtgo_id'),
            arena_id=data.get('arena_id'),
            card_faces=card_faces,
        )


class PriceRecord(BaseModel):
    """Historical price record for a card."""
    
    id: Optional[int] = None
    card_id: int
    source: str  # 'scryfall', 'tcgplayer', etc.
    price_usd: Optional[Decimal] = None
    price_usd_foil: Optional[Decimal] = None
    price_usd_etched: Optional[Decimal] = None
    price_eur: Optional[Decimal] = None
    price_eur_foil: Optional[Decimal] = None
    price_tix: Optional[Decimal] = None
    recorded_at: Optional[datetime] = None


class PriceQuote(BaseModel):
    """Price quote from a vendor."""
    
    source: str
    price_usd: Optional[Decimal] = None
    price_foil: Optional[Decimal] = None
    url: Optional[str] = None
    updated_at: datetime
    in_stock: bool = True
    condition: Condition = Condition.NEAR_MINT


class AggregatedPrice(BaseModel):
    """Best price across all sources."""
    
    card_name: str
    scryfall_id: str
    best_price: Decimal
    best_source: str
    best_url: Optional[str] = None
    all_prices: List[PriceQuote]
    price_spread: Decimal  # max - min
    average_price: Decimal
