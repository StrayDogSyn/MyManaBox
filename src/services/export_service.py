"""
Collection Export Utilities
===========================

Exports collection data to various formats (CSV, Moxfield, Archidekt, JSON).
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from sqlalchemy.orm import Session

from src.database.models import Card, CollectionItem, Deck
from src.database.repositories.collection_repository import CollectionRepository
from src.database.repositories.card_repository import CardRepository
from src.database.connection import DatabaseManager

logger = logging.getLogger(__name__)


class CollectionExporter:
    """Exports collection to various formats."""
    
    def __init__(self, db_manager: DatabaseManager, export_dir: Path = None):
        """
        Initialize exporter.
        
        Args:
            db_manager: DatabaseManager instance
            export_dir: Directory for exports (default: data/exports)
        """
        if export_dir is None:
            export_dir = Path(__file__).parent.parent.parent / "data" / "exports"
        
        self.db_manager = db_manager
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def export_csv(
        self,
        filename: Optional[str] = None,
        include_prices: bool = True,
        filters: Optional[dict] = None,
    ) -> Path:
        """
        Export collection to CSV format.
        
        Args:
            filename: Output filename (default: collection_YYYYMMDD_HHMMSS.csv)
            include_prices: Include price columns
            filters: Optional filters (set_code, rarity, format, min_value, etc.)
        
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"collection_{self._get_timestamp()}.csv"
        
        output_path = self.export_dir / filename
        
        with self.db_manager.get_session() as session:
            collection_repo = CollectionRepository()
            items = collection_repo.get_all_items(session)
            
            # Apply filters if provided
            if filters:
                items = self._apply_filters(items, session, filters)
            
            # Prepare CSV data
            fieldnames = [
                'Name', 'Set Code', 'Quantity', 'Foil', 'Condition',
                'Language', 'Location', 'Notes'
            ]
            if include_prices:
                fieldnames.extend(['Price USD', 'Foil Price USD', 'Total Value'])
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in items:
                    row = {
                        'Name': item.card.name,
                        'Set Code': item.card.set_code,
                        'Quantity': item.quantity,
                        'Foil': 'Yes' if item.is_foil else 'No',
                        'Condition': item.condition or 'NM',
                        'Language': item.language or 'English',
                        'Location': item.location or 'Binder',
                        'Notes': item.notes or '',
                    }
                    
                    if include_prices:
                        card = item.card
                        row['Price USD'] = card.price_usd or 0.0
                        row['Foil Price USD'] = card.price_usd_foil or 0.0
                        total = (card.price_usd or 0.0) * item.quantity
                        if item.is_foil and card.price_usd_foil:
                            total = card.price_usd_foil * item.quantity
                        row['Total Value'] = round(total, 2)
                    
                    writer.writerow(row)
        
        logger.info(f"Collection exported to {output_path}")
        return output_path
    
    def export_moxfield(
        self,
        filename: Optional[str] = None,
        filters: Optional[dict] = None,
    ) -> Path:
        """
        Export collection in Moxfield format.
        
        Args:
            filename: Output filename (default: moxfield_export_YYYYMMDD_HHMMSS.csv)
            filters: Optional filters
        
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"moxfield_export_{self._get_timestamp()}.csv"
        
        output_path = self.export_dir / filename
        
        with self.db_manager.get_session() as session:
            collection_repo = CollectionRepository()
            items = collection_repo.get_all_items(session)
            
            if filters:
                items = self._apply_filters(items, session, filters)
            
            # Moxfield format: Count, Name, Edition, Foil?, Language
            fieldnames = ['Count', 'Name', 'Edition', 'Foil?', 'Language', 'Condition']
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in items:
                    row = {
                        'Count': item.quantity,
                        'Name': item.card.name,
                        'Edition': item.card.set_code.upper(),
                        'Foil?': 'foil' if item.is_foil else 'nonfoil',
                        'Language': item.language or 'en',
                        'Condition': item.condition or 'NM',
                    }
                    writer.writerow(row)
        
        logger.info(f"Collection exported to Moxfield format: {output_path}")
        return output_path
    
    def export_archidekt(
        self,
        filename: Optional[str] = None,
        filters: Optional[dict] = None,
    ) -> Path:
        """
        Export collection in Archidekt format.
        
        Args:
            filename: Output filename (default: archidekt_export_YYYYMMDD_HHMMSS.csv)
            filters: Optional filters
        
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"archidekt_export_{self._get_timestamp()}.csv"
        
        output_path = self.export_dir / filename
        
        with self.db_manager.get_session() as session:
            collection_repo = CollectionRepository()
            items = collection_repo.get_all_items(session)
            
            if filters:
                items = self._apply_filters(items, session, filters)
            
            # Archidekt format: Quantity, Card Name, Set Code
            fieldnames = ['Quantity', 'Card Name', 'Set Code', 'Foil']
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in items:
                    row = {
                        'Quantity': item.quantity,
                        'Card Name': item.card.name,
                        'Set Code': item.card.set_code,
                        'Foil': '1' if item.is_foil else '0',
                    }
                    writer.writerow(row)
        
        logger.info(f"Collection exported to Archidekt format: {output_path}")
        return output_path
    
    def export_json(
        self,
        filename: Optional[str] = None,
        include_prices: bool = True,
        filters: Optional[dict] = None,
    ) -> Path:
        """
        Export collection as JSON.
        
        Args:
            filename: Output filename (default: collection_YYYYMMDD_HHMMSS.json)
            include_prices: Include price information
            filters: Optional filters
        
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"collection_{self._get_timestamp()}.json"
        
        output_path = self.export_dir / filename
        
        with self.db_manager.get_session() as session:
            collection_repo = CollectionRepository()
            items = collection_repo.get_all_items(session)
            
            if filters:
                items = self._apply_filters(items, session, filters)
            
            # Build JSON structure
            data = {
                'export_date': datetime.now().isoformat(),
                'total_items': len(items),
                'items': []
            }
            
            total_value = 0.0
            for item in items:
                card_data = {
                    'name': item.card.name,
                    'set_code': item.card.set_code,
                    'quantity': item.quantity,
                    'is_foil': item.is_foil,
                    'condition': item.condition or 'NM',
                    'language': item.language or 'English',
                    'location': item.location or 'Binder',
                    'notes': item.notes or '',
                }
                
                if include_prices and item.card.price_usd:
                    price = item.card.price_usd_foil if item.is_foil else item.card.price_usd
                    value = (price or 0) * item.quantity
                    card_data['price_usd'] = float(item.card.price_usd or 0)
                    card_data['price_foil_usd'] = float(item.card.price_usd_foil or 0)
                    card_data['total_value'] = round(value, 2)
                    total_value += value
                
                data['items'].append(card_data)
            
            if include_prices:
                data['total_value'] = round(total_value, 2)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        
        logger.info(f"Collection exported to JSON: {output_path}")
        return output_path
    
    def _apply_filters(
        self,
        items: List[CollectionItem],
        session: Session,
        filters: dict,
    ) -> List[CollectionItem]:
        """Apply filters to collection items."""
        filtered = items
        
        # Filter by set code
        if 'set_code' in filters:
            set_code = filters['set_code'].lower()
            filtered = [i for i in filtered if i.card.set_code.lower() == set_code]
        
        # Filter by rarity
        if 'rarity' in filters:
            rarity = filters['rarity'].lower()
            filtered = [i for i in filtered if i.card.rarity.lower() == rarity]
        
        # Filter by foil status
        if 'is_foil' in filters:
            filtered = [i for i in filtered if i.is_foil == filters['is_foil']]
        
        # Filter by minimum value
        if 'min_value' in filters:
            min_value = float(filters['min_value'])
            filtered = [
                i for i in filtered
                if (i.card.price_usd or 0) >= min_value
            ]
        
        # Filter by format legality
        if 'format' in filters:
            fmt = filters['format'].lower()
            filtered = [
                i for i in filtered
                if i.card.legalities and fmt in i.card.legalities
            ]
        
        return filtered
