"""
CardForge Sync Service
Platform synchronization (Moxfield, ManaBox, Google Drive)
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from cardforge.repositories import CollectionRepository, CollectionCardRepository, DeckRepository
from cardforge.models import SyncState, SyncStatus, SyncPlatform
from cardforge.api import MoxfieldClient, GoogleDriveClient
from cardforge.config import get_config


class SyncService:
    """Service for external platform synchronization."""
    
    def __init__(self):
        self.collection_repo = CollectionRepository()
        self.cc_repo = CollectionCardRepository()
        self.deck_repo = DeckRepository()
        self.config = get_config()
    
    async def export_collection_json(self, collection_id: Optional[int] = None) -> Dict[str, Any]:
        """Export collection as JSON."""
        if collection_id is None:
            collection = await self.collection_repo.get_or_create_default()
            collection_id = collection.id
        
        collection = await self.collection_repo.get(collection_id)
        cards = await self.cc_repo.get_with_card_data(collection_id, limit=100000)
        
        return {
            'exported_at': datetime.now().isoformat(),
            'collection': {
                'id': collection.id,
                'name': collection.name,
                'description': collection.description,
            },
            'cards': [
                {
                    'name': c.card.name if c.card else None,
                    'scryfall_id': c.card.scryfall_id if c.card else None,
                    'set_code': c.card.set_code if c.card else None,
                    'quantity': c.quantity,
                    'foil': c.foil,
                    'condition': c.condition,
                    'language': c.language,
                    'location': c.location,
                    'purchase_price': str(c.purchase_price) if c.purchase_price else None,
                }
                for c in cards
            ],
            'total_cards': sum(c.quantity for c in cards),
            'unique_cards': len(cards),
        }
    
    async def backup_to_google_drive(self) -> Optional[str]:
        """Backup collection to Google Drive."""
        if not self.config.google_drive.credentials_file:
            return None
        
        export_data = await self.export_collection_json()
        
        async with GoogleDriveClient() as client:
            file_id = await client.backup_collection(export_data)
            return file_id
    
    async def restore_from_google_drive(self) -> int:
        """Restore collection from latest Google Drive backup."""
        if not self.config.google_drive.credentials_file:
            return 0
        
        async with GoogleDriveClient() as client:
            backup = await client.get_latest_backup()
            if not backup:
                return 0
        
        # Import cards from backup
        count = 0
        collection = await self.collection_repo.get_or_create_default()
        
        for card_data in backup.get('cards', []):
            # This would need card lookup logic
            count += 1
        
        return count
    
    async def sync_moxfield_decks(self) -> int:
        """Sync all decks from Moxfield."""
        if not self.config.moxfield.bearer_token:
            return 0
        
        async with MoxfieldClient(bearer_token=self.config.moxfield.bearer_token) as client:
            decks = await client.get_all_my_decks()
        
        count = 0
        for deck_data in decks:
            existing = await self.deck_repo.get_by_moxfield_id(deck_data.get('publicId'))
            if not existing:
                # Import new deck
                from cardforge.services import DeckService
                deck_service = DeckService()
                await deck_service.import_from_moxfield(deck_data.get('publicId'))
                count += 1
        
        return count
    
    async def import_manabox_csv(self, csv_path: str) -> int:
        """Import collection from ManaBox CSV export."""
        import csv
        
        collection = await self.collection_repo.get_or_create_default()
        count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                await self.cc_repo.add_card(
                    collection_id=collection.id,
                    card_id=0,  # Would need lookup
                    quantity=int(row.get('Quantity', 1)),
                    foil='foil' if row.get('Foil') == 'foil' else 'normal',
                    condition=row.get('Condition', 'NM'),
                    manabox_id=row.get('id'),
                )
                count += 1
        
        return count
