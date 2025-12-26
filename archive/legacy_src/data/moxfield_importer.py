"""Moxfield collection import functionality."""

import requests
from pathlib import Path
from typing import Optional
import shutil
import pandas as pd
from datetime import datetime


class MoxfieldImporter:
    """Handles importing collections from Moxfield."""
    
    def __init__(self):
        """Initialize the Moxfield importer."""
        self.base_url = "https://api.moxfield.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/csv,text/plain,*/*'
        })
    
    def extract_collection_id(self, url: str) -> Optional[str]:
        """Extract collection ID from Moxfield URL."""
        if "/collection/" in url:
            return url.split("/collection/")[1].split("/")[0].split("?")[0]
        return None
    
    def import_from_url(self, url: str, output_file: str = "moxfield_export.csv", 
                       backup_existing: bool = True) -> bool:
        """Import collection from Moxfield URL."""
        collection_id = self.extract_collection_id(url)
        if not collection_id:
            return False
        
        # Backup existing file if requested
        if backup_existing and Path(output_file).exists():
            self._create_backup(output_file)
        
        # Try different API endpoints
        endpoints = [
            f"{self.base_url}/v2/collections/{collection_id}/export/csv",
            f"{self.base_url}/v3/collections/{collection_id}/export/csv",
            f"https://moxfield.com/collections/{collection_id}/export/csv"
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(endpoint, timeout=30)
                
                if response.status_code == 200:
                    content = response.text
                    if content and ('Count' in content or 'Name' in content):
                        # Save the CSV content
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        return True
                        
            except requests.RequestException:
                continue
        
        return False
    
    def import_from_file(self, source_file: str, output_file: str = "moxfield_export.csv", 
                        backup_existing: bool = True) -> bool:
        """Import collection from a local CSV file."""
        try:
            if not Path(source_file).exists():
                return False
            
            # Backup existing file if requested
            if backup_existing and Path(output_file).exists():
                self._create_backup(output_file)
            
            # Copy the file
            shutil.copy2(source_file, output_file)
            return True
            
        except Exception:
            return False
    
    def _create_backup(self, file_path: str) -> str:
        """Create a backup of the existing file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{file_path}.backup_{timestamp}"
        try:
            Path(file_path).rename(backup_file)
            return backup_file
        except Exception:
            return ""
