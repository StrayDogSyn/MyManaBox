"""Import service for managing collection imports."""

from typing import Optional
from ..models import Collection
from ..data import MoxfieldImporter, CSVLoader, FileManager


class ImportService:
    """Service for importing collections from various sources."""
    
    def __init__(self, csv_loader: CSVLoader, file_manager: FileManager):
        """Initialize import service."""
        self.csv_loader = csv_loader
        self.file_manager = file_manager
        self.moxfield_importer = MoxfieldImporter()
    
    def import_from_moxfield_url(self, url: str, output_file: str = "moxfield_export.csv",
                                backup_existing: bool = True) -> tuple[bool, Optional[str]]:
        """Import collection from Moxfield URL."""
        # Create backup if requested
        backup_file = None
        if backup_existing:
            backup_file = self.file_manager.create_backup(output_file)
        
        # Attempt import
        success = self.moxfield_importer.import_from_url(url, output_file, backup_existing=False)
        
        if success:
            return True, backup_file
        else:
            # Restore backup if import failed and backup was created
            if backup_file:
                self.file_manager.restore_backup(backup_file, output_file)
            return False, None
    
    def import_from_file(self, source_file: str, output_file: str = "moxfield_export.csv",
                        backup_existing: bool = True) -> tuple[bool, Optional[str]]:
        """Import collection from local file."""
        # Create backup if requested
        backup_file = None
        if backup_existing:
            backup_file = self.file_manager.create_backup(output_file)
        
        # Attempt import
        success = self.moxfield_importer.import_from_file(source_file, output_file, backup_existing=False)
        
        if success:
            return True, backup_file
        else:
            # Restore backup if import failed and backup was created
            if backup_file:
                self.file_manager.restore_backup(backup_file, output_file)
            return False, None
    
    def validate_import_file(self, file_path: str) -> tuple[bool, str]:
        """Validate that an import file is in correct format."""
        try:
            # Try to load the file as a collection
            temp_loader = CSVLoader(file_path)
            collection = temp_loader.load_collection("Validation")
            
            if collection is None:
                return False, "Could not load file as CSV"
            
            if collection.unique_cards == 0:
                return False, "File contains no valid cards"
            
            # Check for required columns (basic validation)
            if not any(card.name for card in collection.cards):
                return False, "File missing card names"
            
            return True, f"Valid file with {collection.unique_cards} unique cards"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def get_import_instructions(self, url: str) -> dict:
        """Get manual import instructions for a URL."""
        collection_id = self.moxfield_importer.extract_collection_id(url)
        
        return {
            'url': url,
            'collection_id': collection_id,
            'steps': [
                f"1. Go to: {url}",
                "2. Make sure you're logged into Moxfield",
                "3. Ensure the collection is set to 'Public' if you want to share it",
                "4. Look for an 'Export' or 'Download' button on the collection page",
                "5. Select 'CSV' format",
                "6. Download the file",
                "7. Use the --import-file option to import the downloaded CSV"
            ],
            'alternative_command': f"python main.py --import-file 'your_downloaded_file.csv'"
        }
    
    def list_available_backups(self, file_path: str = "moxfield_export.csv") -> list[str]:
        """List available backup files."""
        return self.file_manager.list_backups(file_path)
    
    def restore_from_backup(self, backup_file: str, target_file: str = "moxfield_export.csv") -> bool:
        """Restore collection from backup."""
        return self.file_manager.restore_backup(backup_file, target_file)
