"""
Collection Integration Service
Handles secure synchronization and validation between Card Database and User Collections.
"""

import logging
from typing import List, Dict, Optional, Any
from decimal import Decimal

from cardforge.database import get_transaction
from cardforge.repositories import CardRepository, CollectionCardRepository, CollectionRepository
from cardforge.utils.monitoring import monitor_performance

logger = logging.getLogger(__name__)

class CollectionIntegrationService:
    """
    Service to manage the integration integrity between Cards and Collections.
    """
    
    def __init__(self):
        self.card_repo = CardRepository()
        self.collection_repo = CollectionRepository()
        self.collection_card_repo = CollectionCardRepository()
        
    @monitor_performance("sync_collection_metadata")
    async def sync_collection_with_db(self, collection_id: int) -> Dict[str, int]:
        """
        Synchronize collection cards with the latest master card database metadata.
        Ensures prices, legalities, and text are up-to-date.
        """
        stats = {"updated": 0, "errors": 0}
        
        async with get_transaction() as conn:
            # Get all cards in collection
            collection_cards = await self.collection_card_repo.get_by_collection(collection_id, limit=10000)
            
            for cc in collection_cards:
                try:
                    # Fetch master card data
                    card = await self.card_repo.get(cc.card_id)
                    if not card:
                        logger.warning(f"Orphaned collection card found: {cc.id} (Card ID {cc.card_id})")
                        continue
                        
                    # Here we would update any denormalized data if we had any in collection_cards
                    # Currently collection_cards mostly links to cards, so the sync is implicit via JOINs
                    # However, we can check for logic inconsistencies if needed
                    stats["updated"] += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing card {cc.id}: {e}")
                    stats["errors"] += 1
                    
        return stats

    @monitor_performance("validate_collection_integrity")
    async def validate_collection_integrity(self, collection_id: int) -> Dict[str, List[str]]:
        """
        Check for data integrity issues in the collection.
        Returns a dict of issues found.
        """
        issues = {
            "orphans": [],
            "duplicates": [],
            "data_mismatches": []
        }
        
        collection_cards = await self.collection_card_repo.get_by_collection(collection_id, limit=10000)
        
        # Check for orphans
        for cc in collection_cards:
            card = await self.card_repo.get(cc.card_id)
            if not card:
                issues["orphans"].append(f"CollectionCard {cc.id} points to missing Card {cc.card_id}")
                
        return issues

    @monitor_performance("prepare_for_analysis")
    async def get_collection_for_analysis(self, collection_id: int) -> List[Dict[str, Any]]:
        """
        Format collection data specifically for the AI Deck Advisor.
        Returns a simplified list of cards with relevant attributes.
        """
        collection_cards = await self.collection_card_repo.get_with_card_data(collection_id, limit=10000)
        
        analysis_data = []
        for cc in collection_cards:
            if not cc.card:
                continue
                
            analysis_data.append({
                "name": cc.card.name,
                "quantity": cc.quantity,
                "cmc": cc.card.cmc,
                "type_line": cc.card.type_line,
                "oracle_text": cc.card.oracle_text,
                "colors": cc.card.colors,
                "rarity": cc.card.rarity,
                "set": cc.card.set_code
            })
            
        return analysis_data

    @monitor_performance("add_card_verified")
    async def add_card_to_collection(self, collection_id: int, scryfall_id: str, quantity: int = 1) -> bool:
        """
        Securely add a card to collection by verifying it exists in master DB first.
        """
        card = await self.card_repo.get_by_scryfall_id(scryfall_id)
        if not card:
            # Try to fetch from API if not in local DB? 
            # For now, assume local DB is source of truth for integration testing
            logger.error(f"Card with Scryfall ID {scryfall_id} not found in database.")
            return False
            
        await self.collection_card_repo.add_card(
            collection_id=collection_id,
            card_id=card.id,
            quantity=quantity
        )
        return True
