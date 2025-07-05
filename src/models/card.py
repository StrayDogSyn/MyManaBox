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
    market_value: Optional[Decimal] = None  # Current market price from API
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
    
    # Extended Scryfall data
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None
    defense: Optional[str] = None
    artist: Optional[str] = None
    flavor_text: Optional[str] = None
    image_uris: Optional[dict] = None
    prices: Optional[dict] = None  # Full price object from Scryfall
    set_name: Optional[str] = None
    set_type: Optional[str] = None
    released_at: Optional[str] = None
    collector_number: Optional[str] = None
    border_color: Optional[str] = None
    frame: Optional[str] = None
    security_stamp: Optional[str] = None
    layout: Optional[str] = None
    keywords: Optional[list] = None
    legalities: Optional[dict] = None
    reserved: Optional[bool] = None
    digital: Optional[bool] = None
    reprint: Optional[bool] = None
    variation: Optional[bool] = None
    promo: Optional[bool] = None
    textless: Optional[bool] = None
    full_art: Optional[bool] = None
    story_spotlight: Optional[bool] = None
    edhrec_rank: Optional[int] = None
    penny_rank: Optional[int] = None
    
    # Additional Core Card Fields
    arena_id: Optional[int] = None
    mtgo_id: Optional[int] = None
    mtgo_foil_id: Optional[int] = None
    multiverse_ids: Optional[list] = None
    tcgplayer_id: Optional[int] = None
    tcgplayer_etched_id: Optional[int] = None
    cardmarket_id: Optional[int] = None
    oracle_id: Optional[str] = None
    
    # Additional Gameplay Fields
    all_parts: Optional[list] = None
    card_faces: Optional[list] = None
    color_indicator: Optional[Set[CardColor]] = None
    game_changer: Optional[bool] = None
    hand_modifier: Optional[str] = None
    life_modifier: Optional[str] = None
    produced_mana: Optional[Set[CardColor]] = None
    
    # Additional Print Fields
    artist_ids: Optional[list] = None
    attraction_lights: Optional[list] = None
    booster: Optional[bool] = None
    card_back_id: Optional[str] = None
    content_warning: Optional[bool] = None
    finishes: Optional[list] = None
    flavor_name: Optional[str] = None
    frame_effects: Optional[list] = None
    games: Optional[list] = None
    highres_image: Optional[bool] = None
    illustration_id: Optional[str] = None
    image_status: Optional[str] = None
    oversized: Optional[bool] = None
    printed_name: Optional[str] = None
    printed_text: Optional[str] = None
    printed_type_line: Optional[str] = None
    promo_types: Optional[list] = None
    purchase_uris: Optional[dict] = None
    related_uris: Optional[dict] = None
    scryfall_set_uri: Optional[str] = None
    set_search_uri: Optional[str] = None
    set_uri: Optional[str] = None
    set_id: Optional[str] = None
    variation_of: Optional[str] = None
    watermark: Optional[str] = None
    preview: Optional[dict] = None
    
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
        """Calculate total value of all copies using market value if available, otherwise purchase price."""
        # Prefer market value (current) over purchase price (historical)
        price = self.market_value or self.purchase_price
        if price is None:
            return Decimal('0')
        return price * self.count
    
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
        
        # Parse market value from USD Price column
        market_str = str(row_data.get('USD Price', '')).replace('$', '').strip()
        market_value = None
        if market_str and market_str != 'nan':
            try:
                market_value = Decimal(market_str)
            except (ValueError, TypeError):
                market_value = None
        
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
        
        # Parse rarity
        rarity = None
        rarity_str = row_data.get('Rarity', '').strip()
        if rarity_str:
            for r in CardRarity:
                if r.value.lower() == rarity_str.lower():
                    rarity = r
                    break
        
        # Parse colors
        colors = None
        colors_str = row_data.get('Colors', '').strip()
        if colors_str:
            colors = set()
            for color_char in colors_str.split('|'):
                color_char = color_char.strip()
                if color_char == 'W':
                    colors.add(CardColor.WHITE)
                elif color_char == 'U':
                    colors.add(CardColor.BLUE)
                elif color_char == 'B':
                    colors.add(CardColor.BLACK)
                elif color_char == 'R':
                    colors.add(CardColor.RED)
                elif color_char == 'G':
                    colors.add(CardColor.GREEN)
        
        # Parse CMC
        cmc = None
        cmc_str = row_data.get('CMC', '').strip()
        if cmc_str:
            try:
                cmc = int(float(cmc_str))
            except (ValueError, TypeError):
                cmc = None
        
        return cls(
            name=row_data.get('Name', ''),
            edition=row_data.get('Edition', ''),
            count=int(row_data.get('Count', 1)),
            purchase_price=purchase_price,
            market_value=market_value,
            condition=condition,
            foil=foil,
            rarity=rarity,
            colors=colors,
            cmc=cmc,
            type_line=row_data.get('Type Line', ''),
            mana_cost=row_data.get('Mana Cost', ''),
            oracle_text=row_data.get('Oracle Text', ''),
            set_name=row_data.get('Set Name', ''),
            power=row_data.get('Power', ''),
            toughness=row_data.get('Toughness', ''),
            loyalty=row_data.get('Loyalty', ''),
            artist=row_data.get('Artist', ''),
            scryfall_id=row_data.get('Scryfall ID', ''),
            collector_number=row_data.get('Collector Number', '')
        )
    
    def to_dict(self) -> dict:
        """Convert Card to dictionary for comprehensive CSV export."""
        # Helper function to format sets and lists
        def format_set(s):
            if s is None:
                return ""
            if isinstance(s, set):
                return "|".join(str(item.value) if hasattr(item, 'value') else str(item) for item in sorted(s))
            elif isinstance(s, list):
                return "|".join(str(item) for item in s)
            return str(s)
        
        def format_dict(d):
            if d is None:
                return ""
            if isinstance(d, dict):
                return "|".join(f"{k}:{v}" for k, v in d.items() if v is not None)
            return str(d)
        
        return {
            # Basic card info
            'Name': self.name,
            'Edition': self.edition,
            'Count': self.count,
            'Purchase Price': f"${self.purchase_price}" if self.purchase_price else "",
            'Market Value': f"${self.market_value}" if self.market_value else "",
            'Total Value': f"${self.total_value}" if self.total_value else "",
            'Condition': self.condition.value,
            'Foil': "Yes" if self.foil else "",
            
            # Scryfall enriched data
            'Scryfall ID': self.scryfall_id or "",
            'Colors': format_set(self.colors),
            'Color Identity': format_set(self.color_identity),
            'Rarity': self.rarity.value if self.rarity else "",
            'Types': format_set(self.types),
            'Type Line': self.type_line or "",
            'Mana Cost': self.mana_cost or "",
            'CMC': self.cmc if self.cmc is not None else "",
            'Power': self.power or "",
            'Toughness': self.toughness or "",
            'Loyalty': self.loyalty or "",
            'Defense': self.defense or "",
            'Oracle Text': self.oracle_text or "",
            
            # Artist and flavor
            'Artist': self.artist or "",
            'Artist IDs': "|".join(self.artist_ids) if self.artist_ids else "",
            'Flavor Text': self.flavor_text or "",
            'Flavor Name': self.flavor_name or "",
            
            # Set information
            'Set Name': self.set_name or "",
            'Set Type': self.set_type or "",
            'Set ID': self.set_id or "",
            'Released At': self.released_at or "",
            'Collector Number': self.collector_number or "",
            
            # Card properties
            'Border Color': self.border_color or "",
            'Frame': self.frame or "",
            'Frame Effects': "|".join(self.frame_effects) if self.frame_effects else "",
            'Security Stamp': self.security_stamp or "",
            'Layout': self.layout or "",
            'Keywords': "|".join(self.keywords) if self.keywords else "",
            'Watermark': self.watermark or "",
            
            # IDs and External References
            'Arena ID': self.arena_id if self.arena_id else "",
            'MTGO ID': self.mtgo_id if self.mtgo_id else "",
            'MTGO Foil ID': self.mtgo_foil_id if self.mtgo_foil_id else "",
            'TCGPlayer ID': self.tcgplayer_id if self.tcgplayer_id else "",
            'TCGPlayer Etched ID': self.tcgplayer_etched_id if self.tcgplayer_etched_id else "",
            'Cardmarket ID': self.cardmarket_id if self.cardmarket_id else "",
            'Oracle ID': self.oracle_id or "",
            'Multiverse IDs': "|".join(map(str, self.multiverse_ids)) if self.multiverse_ids else "",
            
            # Additional Gameplay Fields
            'Color Indicator': format_set(self.color_indicator),
            'Produced Mana': format_set(self.produced_mana),
            'Hand Modifier': self.hand_modifier or "",
            'Life Modifier': self.life_modifier or "",
            
            # Boolean properties
            'Reserved': "Yes" if self.reserved else "",
            'Digital': "Yes" if self.digital else "",
            'Reprint': "Yes" if self.reprint else "",
            'Variation': "Yes" if self.variation else "",
            'Promo': "Yes" if self.promo else "",
            'Textless': "Yes" if self.textless else "",
            'Full Art': "Yes" if self.full_art else "",
            'Story Spotlight': "Yes" if self.story_spotlight else "",
            'Game Changer': "Yes" if self.game_changer else "",
            'Booster': "Yes" if self.booster else "",
            'Content Warning': "Yes" if self.content_warning else "",
            'Highres Image': "Yes" if self.highres_image else "",
            'Oversized': "Yes" if self.oversized else "",
            
            # Prices (detailed)
            'USD Price': self.prices.get('usd') if self.prices else "",
            'USD Foil Price': self.prices.get('usd_foil') if self.prices else "",
            'USD Etched Price': self.prices.get('usd_etched') if self.prices else "",
            'EUR Price': self.prices.get('eur') if self.prices else "",
            'EUR Foil Price': self.prices.get('eur_foil') if self.prices else "",
            'EUR Etched Price': self.prices.get('eur_etched') if self.prices else "",
            'TIX Price': self.prices.get('tix') if self.prices else "",
            
            # Print-specific fields
            'Printed Name': self.printed_name or "",
            'Printed Text': self.printed_text or "",
            'Printed Type Line': self.printed_type_line or "",
            'Finishes': "|".join(self.finishes) if self.finishes else "",
            'Games': "|".join(self.games) if self.games else "",
            'Promo Types': "|".join(self.promo_types) if self.promo_types else "",
            'Attraction Lights': "|".join(map(str, self.attraction_lights)) if self.attraction_lights else "",
            
            # Variation info
            'Variation Of': self.variation_of or "",
            'Card Back ID': self.card_back_id or "",
            'Illustration ID': self.illustration_id or "",
            'Image Status': self.image_status or "",
            
            # Rankings
            'EDHREC Rank': self.edhrec_rank if self.edhrec_rank else "",
            'Penny Rank': self.penny_rank if self.penny_rank else "",
            
            # Complex objects as formatted strings
            'Legalities': format_dict(self.legalities),
            'Purchase URIs': format_dict(self.purchase_uris),
            'Related URIs': format_dict(self.related_uris),
            'All Parts': "|".join([f"{part.get('name', '')}:{part.get('component', '')}" for part in (self.all_parts or [])]),
            'Card Faces': str(len(self.card_faces)) if self.card_faces else "",
            'Preview': format_dict(self.preview),
            
            # URI fields
            'Scryfall Set URI': self.scryfall_set_uri or "",
            'Set Search URI': self.set_search_uri or "",
            'Set URI': self.set_uri or "",
            
            # Image URLs
            'Image Small': self.image_uris.get('small') if self.image_uris else "",
            'Image Normal': self.image_uris.get('normal') if self.image_uris else "",
            'Image Large': self.image_uris.get('large') if self.image_uris else "",
            'Image PNG': self.image_uris.get('png') if self.image_uris else "",
            'Image Art Crop': self.image_uris.get('art_crop') if self.image_uris else "",
            'Image Border Crop': self.image_uris.get('border_crop') if self.image_uris else "",
        }
