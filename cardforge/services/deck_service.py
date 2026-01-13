"""
CardForge Deck Service
Deck management and analysis
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal

from cardforge.repositories import DeckRepository, DeckCardRepository, CardRepository
from cardforge.models import Deck, DeckCard, MissingCard
from cardforge.api import MoxfieldClient


class DeckService:
    """Service for deck operations."""
    
    def __init__(self):
        self.deck_repo = DeckRepository()
        self.deck_card_repo = DeckCardRepository()
        self.card_repo = CardRepository()
    
    async def create_deck(
        self,
        name: str,
        format: str,
        description: Optional[str] = None,
        commander_name: Optional[str] = None,
    ) -> Deck:
        """Create a new deck."""
        deck = Deck(
            name=name,
            format=format.lower(),
            description=description,
        )
        
        if commander_name:
            commander = await self.card_repo.get_by_name(commander_name)
            if commander:
                deck.commander_id = commander.id
        
        return await self.deck_repo.create(deck)
    
    async def get_deck(self, deck_id: int) -> Optional[Deck]:
        """Get deck with cards."""
        return await self.deck_repo.get_with_cards(deck_id)
    
    async def add_card(
        self,
        deck_id: int,
        card_name: str,
        quantity: int = 1,
        is_sideboard: bool = False,
        category: Optional[str] = None,
    ) -> Optional[DeckCard]:
        """Add card to deck."""
        card = await self.card_repo.get_by_name(card_name)
        if not card:
            return None
        
        return await self.deck_card_repo.add_card(
            deck_id=deck_id,
            card_id=card.id,
            quantity=quantity,
            is_sideboard=is_sideboard,
            category=category,
        )
    
    async def get_missing_cards(self, deck_id: int) -> List[MissingCard]:
        """Get cards needed to complete deck."""
        await self.deck_card_repo.update_owned_quantities(deck_id)
        return await self.deck_card_repo.get_missing_cards(deck_id)
    
    async def import_from_moxfield(self, deck_id_or_url: str) -> Optional[Deck]:
        """Import deck from Moxfield."""
        # Extract ID from URL if needed
        moxfield_id = deck_id_or_url.split('/')[-1]
        
        async with MoxfieldClient() as client:
            deck_data = await client.import_deck(moxfield_id)
        
        deck = Deck(
            name=deck_data['name'],
            format=deck_data.get('format', 'commander'),
            description=deck_data.get('description'),
            moxfield_id=moxfield_id,
        )
        deck = await self.deck_repo.create(deck)
        
        # Add cards
        for card_data in deck_data.get('mainboard', []):
            card = await self.card_repo.get_by_scryfall_id(card_data['scryfall_id'])
            if card:
                await self.deck_card_repo.add_card(
                    deck_id=deck.id,
                    card_id=card.id,
                    quantity=card_data.get('quantity', 1),
                )
        
        for card_data in deck_data.get('commanders', []):
            card = await self.card_repo.get_by_scryfall_id(card_data['scryfall_id'])
            if card:
                deck.commander_id = card.id
                await self.deck_repo.update(deck)
        
        return deck
    
    async def calculate_value(self, deck_id: int) -> Decimal:
        """Calculate deck's total value."""
        return await self.deck_repo.update_value(deck_id)
    
    async def get_completion_status(self, deck_id: int) -> Dict:
        """Get deck completion percentage."""
        return await self.deck_repo.get_completion_status(deck_id)

    async def analyze_deck(self, deck_id: int) -> Dict[str, Any]:
        """
        Analyze deck composition.
        
        Returns:
            Dictionary containing:
            - mana_curve: Count of cards by CMC
            - color_distribution: Count of cards by color
            - type_distribution: Count of cards by primary type
            - lands_count: Total lands
            - ramp_count: Estimate of ramp sources (based on type/text)
        """
        deck = await self.get_deck(deck_id)
        if not deck:
            return {}
            
        analysis = {
            "mana_curve": {i: 0 for i in range(8)}, # 0-7+
            "color_distribution": {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0},
            "type_distribution": {},
            "lands_count": 0,
            "creature_count": 0,
            "instant_sorcery_count": 0,
        }
        
        for deck_card in deck.cards:
            card = deck_card.card
            if not card:
                continue
                
            qty = deck_card.quantity
            
            # Mana Curve (exclude lands usually, but simplistic here)
            if "Land" not in card.type_line:
                cmc = int(card.cmc) if card.cmc is not None else 0
                idx = min(cmc, 7)
                analysis["mana_curve"][idx] += qty
            
            # Colors
            if not card.colors:
                analysis["color_distribution"]["C"] += qty
            else:
                for color in card.colors:
                    if color in analysis["color_distribution"]:
                        analysis["color_distribution"][color] += qty
            
            # Types
            primary_type = card.type_line.split("—")[0].strip().split(" ")[-1] if "—" in card.type_line else card.type_line.split(" ")[0]
            # Simple fallback parsing
            if "Land" in card.type_line:
                analysis["lands_count"] += qty
                primary_type = "Land"
            elif "Creature" in card.type_line:
                analysis["creature_count"] += qty
                primary_type = "Creature"
            elif "Instant" in card.type_line or "Sorcery" in card.type_line:
                analysis["instant_sorcery_count"] += qty
            
            analysis["type_distribution"][primary_type] = analysis["type_distribution"].get(primary_type, 0) + qty
            
        return analysis
