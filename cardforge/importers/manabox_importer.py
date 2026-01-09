"""
ManaBox Mobile App Importer
Specialized importer for ManaBox CSV exports with schema validation
"""

from pathlib import Path
from typing import Optional
import logging

from .csv_importer import CSVImporter, CSVSchema, detect_csv_schema


logger = logging.getLogger(__name__)


class ManaBoxImporter(CSVImporter):
    """
    Specialized importer for ManaBox mobile app CSV exports.
    
    Handles ManaBox-specific quirks and provides better error messages.
    """
    
    async def import_manabox_csv(
        self,
        file_path: Path,
        collection_id: int,
        merge: bool = True,
        backup: bool = True,
    ) -> dict:
        """
        Import from ManaBox mobile app CSV export.
        
        Args:
            file_path: Path to ManaBox CSV export
            collection_id: Target collection ID
            merge: If True, merge with existing data (recommended for ManaBox)
            backup: Create backup before import
            
        Returns:
            Import statistics with ManaBox-specific info
        """
        # Validate file exists
        if not file_path.exists():
            raise FileNotFoundError(f"ManaBox CSV not found: {file_path}")
        
        # Detect and validate schema
        schema = detect_csv_schema(file_path)
        
        if schema == CSVSchema.UNKNOWN:
            raise ValueError(
                f"Invalid ManaBox CSV format in {file_path}. "
                "Expected 15 or 17 columns. Please export from ManaBox app."
            )
        
        logger.info(f"Detected ManaBox schema: {schema.value}")
        logger.info(f"Import mode: {'MERGE' if merge else 'REPLACE'}")
        
        # Use parent CSV importer
        stats = await self.import_csv(
            file_path=file_path,
            collection_id=collection_id,
            merge=merge,
            backup=backup,
        )
        
        # Add ManaBox-specific stats
        stats["source"] = "ManaBox Mobile App"
        stats["merge_mode"] = merge
        
        # Log results
        logger.info(
            f"ManaBox import complete: {stats['imported']} cards imported, "
            f"{stats['errors']} errors, {stats['skipped']} skipped"
        )
        
        if stats["warnings"]:
            logger.warning(f"Import warnings: {len(stats['warnings'])}")
            for warning in stats["warnings"][:5]:  # Show first 5
                logger.warning(f"  - {warning}")
        
        return stats
    
    def validate_manabox_export(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """
        Validate that a CSV file is a valid ManaBox export.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path.exists():
            return False, f"File not found: {file_path}"
        
        if file_path.suffix.lower() != ".csv":
            return False, "File must be a CSV (.csv extension)"
        
        schema = detect_csv_schema(file_path)
        
        if schema == CSVSchema.UNKNOWN:
            return False, (
                "Invalid ManaBox CSV format. Expected 15 or 17 columns. "
                "Please export from ManaBox app using 'Export Collection' feature."
            )
        
        return True, None
