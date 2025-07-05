#!/usr/bin/env python3
"""
Enhanced MTG Card API Integration
Provides integration with Scryfall API for accurate card data.
"""

import requests
import time
import json
from typing import Dict, Optional, Any
from pathlib import Path

class ScryfallAPI:
    """Interface to Scryfall API for MTG card data."""
    
    BASE_URL = "https://api.scryfall.com"
    
    def __init__(self, cache_file: str = "card_cache.json"):
        """Initialize with optional caching."""
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Load cached card data."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def get_card_data(self, name: str, set_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get card data from Scryfall API with caching."""
        cache_key = f"{name}_{set_code or 'any'}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Rate limiting - Scryfall allows 10 requests per second
        time.sleep(0.1)
        
        # Build query
        query = f'!"{name}"'
        if set_code:
            query += f" set:{set_code}"
        
        try:
            url = f"{self.BASE_URL}/cards/search"
            params = {"q": query, "unique": "cards"}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("total_cards", 0) > 0:
                card = data["data"][0]  # Get first match
                
                # Extract useful data
                card_info = {
                    "name": card.get("name"),
                    "mana_cost": card.get("mana_cost", ""),
                    "cmc": card.get("cmc", 0),
                    "colors": card.get("colors", []),
                    "color_identity": card.get("color_identity", []),
                    "type_line": card.get("type_line", ""),
                    "rarity": card.get("rarity", ""),
                    "set": card.get("set", ""),
                    "set_name": card.get("set_name", ""),
                    "collector_number": card.get("collector_number", ""),
                    "prices": card.get("prices", {}),
                    "scryfall_uri": card.get("scryfall_uri", "")
                }
                
                # Cache the result
                self.cache[cache_key] = card_info
                self._save_cache()
                
                return card_info
                
        except requests.RequestException as e:
            print(f"API Error for {name}: {e}")
        except Exception as e:
            print(f"Unexpected error for {name}: {e}")
        
        return None
    
    def get_color_name(self, color_identity: list) -> str:
        """Convert color identity to readable name."""
        if not color_identity:
            return "Colorless"
        elif len(color_identity) == 1:
            color_map = {
                "W": "White",
                "U": "Blue", 
                "B": "Black",
                "R": "Red",
                "G": "Green"
            }
            return color_map.get(color_identity[0], "Unknown")
        else:
            return "Multicolor"
    
    def get_card_types(self, type_line: str) -> list:
        """Extract card types from type line."""
        if not type_line:
            return []
        
        # Split on '—' to separate types from subtypes
        parts = type_line.split('—')
        main_types = parts[0].strip().split()
        
        return main_types
