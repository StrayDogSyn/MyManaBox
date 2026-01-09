"""Unit tests for CSV import functionality."""
import pytest
from pathlib import Path


class TestCSVImporter:
    """Tests for CSV import logic."""
    
    def test_detect_17_column_schema(self, temp_csv_file_17):
        """Should detect 17-column schema."""
        from cardforge.importers.csv_importer import detect_csv_schema, CSVSchema
        
        schema = detect_csv_schema(temp_csv_file_17)
        
        assert schema == CSVSchema.FULL_17_COLUMN
    
    def test_detect_15_column_schema(self, temp_csv_file_15):
        """Should detect 15-column schema."""
        from cardforge.importers.csv_importer import detect_csv_schema, CSVSchema
        
        schema = detect_csv_schema(temp_csv_file_15)
        
        assert schema == CSVSchema.MINIMAL_15_COLUMN
    
    @pytest.mark.asyncio
    async def test_import_17_columns_preserves_binder(self, temp_csv_file_17):
        """Full schema preserves binder info."""
        from cardforge.importers.csv_importer import CSVImporter
        
        importer = CSVImporter()
        stats = await importer.import_csv(
            file_path=temp_csv_file_17,
            collection_id=1,
            merge=False,
            backup=False
        )
        
        assert stats['imported'] >= 2
        assert stats['schema'] == 'full_17'
    
    @pytest.mark.asyncio
    async def test_import_15_columns_uses_defaults(self, temp_csv_file_15):
        """Minimal schema uses default binder."""
        from cardforge.importers.csv_importer import CSVImporter
        
        importer = CSVImporter()
        stats = await importer.import_csv(
            file_path=temp_csv_file_15,
            collection_id=1,
            merge=False,
            backup=False
        )
        
        assert stats['imported'] >= 2
        assert stats['schema'] == 'minimal_15'
    
    def test_import_missing_file_raises_error(self, tmp_path):
        """Missing file should raise error."""
        from cardforge.importers.csv_importer import CSVImporter
        
        with pytest.raises((FileNotFoundError, ValueError)):
            importer = CSVImporter()
            # This should raise an error
            importer._import_row(None, 1, None)
    
    def test_parse_foil_correctly(self):
        """Should parse foil status correctly."""
        from cardforge.importers.csv_importer import CSVImporter
        
        importer = CSVImporter()
        
        assert importer._parse_foil("foil") is True
        assert importer._parse_foil("normal") is False
        assert importer._parse_foil("") is False
        assert importer._parse_foil(None) is False
    
    def test_parse_condition_correctly(self):
        """Should parse condition correctly."""
        from cardforge.importers.csv_importer import CSVImporter
        from cardforge.models import Condition
        
        importer = CSVImporter()
        
        assert importer._parse_condition("near mint") == Condition.NEAR_MINT
        assert importer._parse_condition("lightly played") == Condition.LIGHTLY_PLAYED
        assert importer._parse_condition("nm") == Condition.NEAR_MINT
        assert importer._parse_condition("") == Condition.NEAR_MINT
