"""Constants for MyManaBox."""

from typing import Dict, List, Any


class Constants:
    """Application constants."""
    
    # File paths
    DEFAULT_CSV_FILE = "moxfield_export.csv"
    DEFAULT_CACHE_FILE = "card_cache.json"
    DEFAULT_OUTPUT_DIR = "sorted_output"
    DEFAULT_BACKUP_DIR = "backups"
    
    # API settings
    SCRYFALL_BASE_URL = "https://api.scryfall.com"
    MOXFIELD_BASE_URL = "https://api.moxfield.com"
    API_RATE_LIMIT_DELAY = 0.05  # seconds
    
    # Color mappings
    COLOR_NAMES: Dict[str, str] = {
        'W': 'White',
        'U': 'Blue', 
        'B': 'Black',
        'R': 'Red',
        'G': 'Green',
        'C': 'Colorless'
    }
    
    COLOR_KEYWORDS: Dict[str, List[str]] = {
        'White': ['plains', 'white', 'angel', 'heal', 'life', 'cleanse'],
        'Blue': ['island', 'blue', 'water', 'counter', 'draw', 'flying'],
        'Black': ['swamp', 'black', 'dark', 'death', 'shadow', 'destroy'],
        'Red': ['mountain', 'red', 'fire', 'lightning', 'burn', 'haste'],
        'Green': ['forest', 'green', 'elf', 'growth', 'nature', 'creature'],
        'Colorless': ['artifact', 'colorless', 'wastes', 'equipment']
    }
    
    # Type keywords for heuristic sorting
    TYPE_KEYWORDS: Dict[str, List[str]] = {
        'Lands': ['swamp', 'island', 'plains', 'mountain', 'forest', 'hub', 'wastes', 'gate'],
        'Creatures': ['angel', 'demon', 'dragon', 'elf', 'knight', 'beast', 'warrior', 'wizard'],
        'Artifacts': ['artifact', 'equipment', 'vehicle', 'mana', 'mind', 'soul'],
        'Instants': ['instant', 'counter', 'response', 'quick'],
        'Sorceries': ['sorcery', 'ritual', 'spell'],
        'Enchantments': ['enchantment', 'aura', 'curse', 'saga'],
        'Planeswalkers': ['planeswalker', 'walker']
    }
    
    # Price ranges for classification
    PRICE_RANGES: List[Dict[str, Any]] = [
        {'name': '$0.00 - $0.99', 'min': 0.0, 'max': 0.99},
        {'name': '$1.00 - $4.99', 'min': 1.0, 'max': 4.99},
        {'name': '$5.00 - $9.99', 'min': 5.0, 'max': 9.99},
        {'name': '$10.00 - $24.99', 'min': 10.0, 'max': 24.99},
        {'name': '$25.00 - $49.99', 'min': 25.0, 'max': 49.99},
        {'name': '$50.00+', 'min': 50.0, 'max': float('inf')}
    ]
    
    # Output formats
    OUTPUT_FORMATS = ['table', 'csv', 'json']
    
    # Table formatting
    DEFAULT_TABLE_FORMAT = 'grid'
    DEFAULT_LIMIT = 20
    
    # Backup settings
    MAX_BACKUPS_TO_KEEP = 10
