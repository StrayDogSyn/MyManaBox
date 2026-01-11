"""
Database Batch Insertion Service
=================================

High-performance bulk insert operations for CardForge database.
Handles card lookups, upserts, and collection item insertion.
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database.models import Card, CollectionItem
from src.importers.csv_importer import CardImport

logger = logging.getLogger(__name__)


class BatchInsertService:
    """High-performance batch insert service for cards and collection items."""
    
    def __init__(self, session: Session):
        """
        Initialize batch insert service.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self.stats = {
            "total": 0,
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }
    
    def find_or_create_card(
        self,
        scryfall_id: Optional[str],
        name: str,
        set_code: str,
        **card_data,
    ) -> Tuple[Card, bool]:
        """
        Find existing card or create new one.
        
        Args:
            scryfall_id: Scryfall card ID (if known)
            name: Card name
            set_code: MTG set code
            **card_data: Additional card attributes
        
        Returns:
            (card, is_new) tuple
        """
        # Try to find by scryfall_id first
        if scryfall_id:
            card = self.session.query(Card).filter(
                Card.scryfall_id == scryfall_id
            ).first()
            
            if card:
                return card, False
        
        # Try to find by name and set
        card = self.session.query(Card).filter(
            (Card.name == name) & (Card.set_code == set_code)
        ).first()
        
        if card:
            return card, False
        
        # Create new card
        card = Card(
            name=name,
            set_code=set_code,
            scryfall_id=scryfall_id,
            type_line=card_data.get('type_line', ''),
            rarity=card_data.get('rarity', 'common'),
            **{k: v for k, v in card_data.items() if hasattr(Card, k)}
        )
        
        self.session.add(card)
        self.session.flush()  # Get ID without committing
        
        return card, True
    
    def insert_collection_items(
        self,
        cards: List[CardImport],
        scryfall_map: Optional[dict] = None,
        replace_mode: bool = False,
    ) -> dict:
        """
        Insert collection items from CardImport objects.
        
        Args:
            cards: List of CardImport objects
            scryfall_map: Optional mapping of {(name, set): scryfall_id}
            replace_mode: If True, delete existing items before insert
        
        Returns:
            Statistics dict
        """
        self.stats = {
            "total": len(cards),
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "duplicates": 0,
        }
        
        scryfall_map = scryfall_map or {}
        
        # In replace mode, clear existing collection
        if replace_mode:
            logger.info("Replace mode: clearing existing collection items")
            self.session.query(CollectionItem).delete()
            self.session.flush()
        
        # Deduplicate imports (same card, set, foil status)
        unique_cards = {}
        for card_import in cards:
            key = (card_import.name, card_import.set_code, card_import.is_foil)
            
            if key in unique_cards:
                # Accumulate quantity
                unique_cards[key].quantity += card_import.quantity
                self.stats["duplicates"] += 1
            else:
                unique_cards[key] = card_import
        
        logger.info(f"Processing {len(unique_cards)} unique cards (deduplicated {self.stats['duplicates']})")
        
        # Insert collection items
        for card_import in unique_cards.values():
            try:
                # Find or create card
                scryfall_id = scryfall_map.get((card_import.name, card_import.set_code))
                card, is_new = self.find_or_create_card(
                    scryfall_id,
                    card_import.name,
                    card_import.set_code,
                )
                
                if is_new:
                    self.stats["inserted"] += 1
                
                # Check if collection item exists
                existing_item = self.session.query(CollectionItem).filter(
                    (CollectionItem.card_id == card.id) &
                    (CollectionItem.is_foil == card_import.is_foil)
                ).first()
                
                if existing_item:
                    # Update quantity
                    existing_item.quantity += card_import.quantity
                    existing_item.updated_at = datetime.utcnow()
                    self.stats["updated"] += 1
                else:
                    # Create new collection item
                    item = CollectionItem(
                        card_id=card.id,
                        quantity=card_import.quantity,
                        is_foil=card_import.is_foil,
                        condition=card_import.condition,
                        language=card_import.language,
                        location=card_import.location,
                        notes=card_import.notes,
                        acquired_date=datetime.utcnow(),
                    )
                    self.session.add(item)
                    self.stats["inserted"] += 1
            
            except Exception as e:
                logger.error(f"Error inserting {card_import.name}: {e}")
                self.stats["errors"] += 1
        
        self.session.commit()
        
        logger.info(f"Collection insert complete: {self.stats}")
        return self.stats
    
    def get_collection_stats(self) -> dict:
        """Get current collection statistics."""
        total_items = self.session.query(
            func.count(CollectionItem.id)
        ).scalar() or 0
        
        unique_cards = self.session.query(
            func.count(func.distinct(CollectionItem.card_id))
        ).scalar() or 0
        
        total_cards = self.session.query(
            func.sum(CollectionItem.quantity)
        ).scalar() or 0
        
        foil_count = self.session.query(
            func.sum(CollectionItem.quantity)
        ).filter(CollectionItem.is_foil == True).scalar() or 0
        
        return {
            "collection_items": total_items,
            "unique_cards": unique_cards,
            "total_cards": total_cards,
            "foil_cards": foil_count,
            "non_foil_cards": total_cards - foil_count,
        }
    
    def get_insert_stats(self) -> dict:
        """Get statistics from last insert operation."""
        return self.stats.copy()
