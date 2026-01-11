"""
CSV Importers for CardForge
============================

Handles parsing and importing of CSV files in various MTG collection formats.
Supports: ManaBox mobile export, standard CSV, Archidekt, Moxfield formats.
"""

import csv
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class CardImport:
    """Represents a card to be imported."""
    name: str
    set_code: str
    collector_number: Optional[str] = None
    quantity: int = 1
    is_foil: bool = False
    condition: str = "near_mint"
    language: str = "en"
    location: Optional[str] = None
    notes: Optional[str] = None
    scryfall_id: Optional[str] = None
    
    def __hash__(self):
        """Hash based on card identity (for deduplication)."""
        return hash((self.name, self.set_code, self.quantity, self.is_foil))


class CSVImporter(ABC):
    """Abstract base class for CSV importers."""
    
    def __init__(self, file_path: Path):
        """
        Initialize importer.
        
        Args:
            file_path: Path to CSV file
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.cards: List[CardImport] = []
        self.errors: List[Tuple[int, str]] = []  # (line_number, error)
    
    @abstractmethod
    def parse(self) -> List[CardImport]:
        """Parse CSV and return list of cards."""
        pass
    
    def import_file(self) -> Tuple[List[CardImport], List[Tuple[int, str]]]:
        """
        Import CSV file and return cards and errors.
        
        Returns:
            (cards, errors) tuple
        """
        try:
            self.cards = self.parse()
            logger.info(f"Successfully imported {len(self.cards)} cards from {self.file_path.name}")
        except Exception as e:
            logger.error(f"Error importing file: {e}")
            raise
        
        return self.cards, self.errors


class ManaBoxImporter(CSVImporter):
    """
    Importer for ManaBox mobile export format.
    
    Expected columns:
    - Name: Card name
    - Set Code: MTG set code (e.g., "cmr")
    - Collector #: Card number in set
    - Quantity: Number of copies
    - Foil?: Yes/No or true/false
    - Condition: near_mint, lightly_played, moderately_played, heavily_played, damaged
    - Language: Card language (default: English)
    """
    
    def parse(self) -> List[CardImport]:
        """Parse ManaBox CSV format."""
        cards = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Normalize header names
                fieldnames = {name.lower().strip(): name for name in reader.fieldnames or []}
                
                for line_num, row in enumerate(reader, start=2):
                    try:
                        # Normalize row keys
                        normalized_row = {
                            k.lower().strip(): v for k, v in row.items()
                        }
                        
                        name = self._get_field(normalized_row, ['name', 'card name', 'card'])
                        set_code = self._get_field(normalized_row, ['set code', 'set', 'edition'])
                        collector_number = self._get_field(normalized_row, ['collector #', 'collector number', 'number'])
                        
                        if not name or not set_code:
                            self.errors.append((line_num, f"Missing name or set code"))
                            continue
                        
                        quantity_str = self._get_field(normalized_row, ['quantity', 'qty', 'count']) or "1"
                        try:
                            quantity = int(quantity_str)
                        except ValueError:
                            quantity = 1
                        
                        foil_str = self._get_field(normalized_row, ['foil?', 'foil', 'is_foil']) or "no"
                        is_foil = foil_str.lower() in ['yes', 'true', '1', 'y']
                        
                        condition = self._get_field(
                            normalized_row, 
                            ['condition', 'quality']
                        ) or "near_mint"
                        
                        language = self._get_field(normalized_row, ['language', 'lang']) or "en"
                        location = self._get_field(normalized_row, ['location', 'box', 'binder'])
                        notes = self._get_field(normalized_row, ['notes', 'comments', 'notes'])
                        
                        card = CardImport(
                            name=name.strip(),
                            set_code=set_code.lower().strip(),
                            collector_number=collector_number.strip() if collector_number else None,
                            quantity=max(1, quantity),
                            is_foil=is_foil,
                            condition=condition.lower(),
                            language=language.lower(),
                            location=location.strip() if location else None,
                            notes=notes.strip() if notes else None,
                        )
                        
                        cards.append(card)
                    
                    except Exception as e:
                        self.errors.append((line_num, str(e)))
                        continue
        
        except Exception as e:
            logger.error(f"Error parsing ManaBox CSV: {e}")
            raise
        
        return cards
    
    @staticmethod
    def _get_field(row: Dict[str, str], field_names: List[str]) -> Optional[str]:
        """Get field value from row, trying multiple possible names."""
        for field in field_names:
            if field.lower() in row:
                return row[field.lower()]
        return None


class StandardCSVImporter(CSVImporter):
    """
    Importer for standard CSV format.
    
    Expected columns:
    - name
    - set
    - quantity (optional, default 1)
    - foil (optional, default false)
    """
    
    def parse(self) -> List[CardImport]:
        """Parse standard CSV format."""
        cards = []
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for line_num, row in enumerate(reader, start=2):
                try:
                    name = row.get('name', '').strip()
                    set_code = row.get('set', '').strip()
                    
                    if not name or not set_code:
                        self.errors.append((line_num, "Missing name or set"))
                        continue
                    
                    quantity = int(row.get('quantity', 1))
                    is_foil = row.get('foil', 'false').lower() in ['yes', 'true', '1']
                    
                    card = CardImport(
                        name=name,
                        set_code=set_code.lower(),
                        quantity=quantity,
                        is_foil=is_foil,
                    )
                    cards.append(card)
                
                except Exception as e:
                    self.errors.append((line_num, str(e)))
        
        return cards


class ArchidektImporter(CSVImporter):
    """
    Importer for Archidekt deck export format.
    
    Expected columns:
    - Quantity
    - Name
    - Edition
    - Collector Number (optional)
    - Foil (optional)
    """
    
    def parse(self) -> List[CardImport]:
        """Parse Archidekt CSV format."""
        cards = []
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for line_num, row in enumerate(reader, start=2):
                try:
                    quantity = int(row.get('Quantity', 1))
                    name = row.get('Name', '').strip()
                    set_code = row.get('Edition', '').strip()
                    collector_number = row.get('Collector Number', '').strip()
                    
                    if not name or not set_code:
                        self.errors.append((line_num, "Missing name or edition"))
                        continue
                    
                    is_foil = row.get('Foil', '').lower() in ['yes', 'true', '1']
                    
                    card = CardImport(
                        name=name,
                        set_code=set_code.lower(),
                        collector_number=collector_number or None,
                        quantity=quantity,
                        is_foil=is_foil,
                    )
                    cards.append(card)
                
                except Exception as e:
                    self.errors.append((line_num, str(e)))
        
        return cards


class MoxfieldImporter(CSVImporter):
    """
    Importer for Moxfield collection export format.
    
    Expected columns:
    - Name
    - Set
    - Quantity
    - Foil
    - Finish
    """
    
    def parse(self) -> List[CardImport]:
        """Parse Moxfield CSV format."""
        cards = []
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for line_num, row in enumerate(reader, start=2):
                try:
                    name = row.get('Name', '').strip()
                    set_code = row.get('Set', '').strip()
                    quantity = int(row.get('Quantity', 1))
                    
                    if not name or not set_code:
                        self.errors.append((line_num, "Missing name or set"))
                        continue
                    
                    # Moxfield uses "Foil" column with finish info
                    is_foil = row.get('Foil', '').lower() in ['foil', 'yes', 'true', '1']
                    finish = row.get('Finish', '').lower()
                    
                    if finish in ['foil', 'etched']:
                        is_foil = True
                    
                    card = CardImport(
                        name=name,
                        set_code=set_code.lower(),
                        quantity=quantity,
                        is_foil=is_foil,
                    )
                    cards.append(card)
                
                except Exception as e:
                    self.errors.append((line_num, str(e)))
        
        return cards


def detect_format(file_path: Path) -> type:
    """
    Auto-detect CSV format based on headers.
    
    Returns:
        Importer class to use
    """
    file_path = Path(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            headers_lower = [h.lower() for h in headers]
    except:
        return ManaBoxImporter  # Default
    
    # Check for specific formats
    if 'edition' in headers_lower and 'collector number' in headers_lower:
        return ArchidektImporter
    elif 'finish' in headers_lower or 'moxfield' in str(file_path).lower():
        return MoxfieldImporter
    elif 'foil?' in headers_lower or 'condition' in headers_lower:
        return ManaBoxImporter
    else:
        return StandardCSVImporter  # Fallback to standard


def import_csv(file_path: Path, format: Optional[str] = None) -> Tuple[List[CardImport], List[Tuple[int, str]]]:
    """
    Import a CSV file with auto-detection.
    
    Args:
        file_path: Path to CSV file
        format: Optional format specification ('manabox', 'archidekt', 'moxfield', 'standard')
    
    Returns:
        (cards, errors) tuple
    """
    if format:
        format_map = {
            'manabox': ManaBoxImporter,
            'archidekt': ArchidektImporter,
            'moxfield': MoxfieldImporter,
            'standard': StandardCSVImporter,
        }
        importer_class = format_map.get(format.lower(), ManaBoxImporter)
    else:
        importer_class = detect_format(file_path)
    
    logger.info(f"Using {importer_class.__name__} for {Path(file_path).name}")
    
    importer = importer_class(file_path)
    cards, errors = importer.import_file()
    
    if errors:
        logger.warning(f"Import completed with {len(errors)} errors:")
        for line, error in errors[:10]:  # Show first 10 errors
            logger.warning(f"  Line {line}: {error}")
    
    return cards, errors
