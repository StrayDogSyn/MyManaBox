"""
Scryfall Enrichment Service
============================

Enriches collection with Scryfall data (pricing, images, metadata).
Handles batch processing with rate limiting and error recovery.
"""

import asyncio
import logging
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from src.database.models import Card
from src.integrations.scryfall_client import ScryfallClient
from src.importers.csv_importer import CardImport

logger = logging.getLogger(__name__)


class EnrichmentService:
    """Service for enriching card data with Scryfall information."""
    
    def __init__(self, session: Optional[Session] = None):
        """
        Initialize enrichment service.
        
        Args:
            session: Optional SQLAlchemy session (used for enrich_cards only)
        """
        self.session = session
        self.stats = {
            "total": 0,
            "found": 0,
            "updated": 0,
            "not_found": 0,
            "errors": 0,
        }
    
    async def enrich_cards(
        self,
        cards: List[Card],
        batch_size: int = 100,
    ) -> dict:
        """
        Enrich cards with Scryfall data asynchronously.
        
        Args:
            cards: List of Card objects to enrich
            batch_size: Number of cards to process before commit
        
        Returns:
            Statistics dict
        """
        self.stats = {
            "total": len(cards),
            "found": 0,
            "updated": 0,
            "not_found": 0,
            "errors": 0,
        }
        
        async with ScryfallClient(cache_enabled=True) as client:
            for i, card in enumerate(cards, 1):
                try:
                    # Skip if already enriched
                    if card.price_usd is not None:
                        logger.debug(f"Card {card.name} already enriched, skipping")
                        continue
                    
                    # Search Scryfall
                    scryfall_card = await client.search_card(
                        card.name,
                        card.set_code,
                    )
                    
                    if scryfall_card:
                        # Update card data
                        card.scryfall_id = scryfall_card.scryfall_id
                        card.oracle_id = scryfall_card.oracle_id
                        card.mana_cost = scryfall_card.mana_cost
                        card.cmc = scryfall_card.cmc
                        card.type_line = scryfall_card.type_line
                        card.oracle_text = scryfall_card.oracle_text
                        card.colors = scryfall_card.colors
                        card.color_identity = scryfall_card.color_identity
                        card.power = scryfall_card.power
                        card.toughness = scryfall_card.toughness
                        card.loyalty = scryfall_card.loyalty
                        card.rarity = scryfall_card.rarity
                        card.is_foil_available = scryfall_card.is_foil_available
                        card.is_reserved_list = scryfall_card.is_reserved_list
                        card.is_commander = scryfall_card.is_commander
                        card.legalities = scryfall_card.legalities
                        card.price_usd = scryfall_card.price_usd
                        card.price_usd_foil = scryfall_card.price_usd_foil
                        card.price_eur = scryfall_card.price_eur
                        card.price_tix = scryfall_card.price_tix
                        card.image_uri = scryfall_card.image_uri
                        card.image_uri_small = scryfall_card.image_uri_small
                        
                        self.stats["found"] += 1
                        self.stats["updated"] += 1
                        logger.debug(f"Enriched {card.name} - ${card.price_usd}")
                    else:
                        self.stats["not_found"] += 1
                        logger.warning(f"Card not found in Scryfall: {card.name} ({card.set_code})")
                
                except Exception as e:
                    self.stats["errors"] += 1
                    logger.error(f"Error enriching {card.name}: {e}")
                
                # Commit in batches
                if i % batch_size == 0:
                    self.session.commit()
                    logger.info(f"Processed {i}/{len(cards)} cards")
        
        # Final commit
        self.session.commit()
        
        logger.info(f"Enrichment complete: {self.stats}")
        return self.stats
    
    async def enrich_imports(
        self,
        imports: List[CardImport],
    ) -> Tuple[dict, dict]:
        """
        Enrich CardImport objects with Scryfall data.
        
        Args:
            imports: List of CardImport objects
        
        Returns:
            (scryfall_map, stats) tuple
            scryfall_map: {(name, set_code): scryfall_id}
        """
        scryfall_map = {}
        stats = {
            "total": len(imports),
            "found": 0,
            "not_found": 0,
            "errors": 0,
        }
        
        # Deduplicate imports for enrichment
        unique_imports = {}
        for imp in imports:
            key = (imp.name, imp.set_code)
            if key not in unique_imports:
                unique_imports[key] = imp
        
        async with ScryfallClient(cache_enabled=True) as client:
            for i, (key, imp) in enumerate(unique_imports.items(), 1):
                name, set_code = key
                
                try:
                    scryfall_card = await client.search_card(name, set_code)
                    
                    if scryfall_card:
                        scryfall_map[key] = scryfall_card.scryfall_id
                        stats["found"] += 1
                        logger.debug(f"Found {name} in Scryfall")
                    else:
                        stats["not_found"] += 1
                        logger.warning(f"Card not found: {name} ({set_code})")
                
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error looking up {name}: {e}")
                
                if i % 50 == 0:
                    logger.info(f"Enriched {i}/{len(unique_imports)} unique imports")
        
        logger.info(f"Import enrichment complete: {stats}")
        return scryfall_map, stats
    
    def get_enrichment_stats(self) -> dict:
        """Get statistics from last enrichment operation."""
        return self.stats.copy()
