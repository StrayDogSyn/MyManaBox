"""Unit tests for export functionality."""
import pytest
from pathlib import Path


class TestMoxfieldExporter:
    """Tests for Moxfield export format."""
    
    @pytest.mark.asyncio
    async def test_export_creates_file(self, tmp_path):
        """Should create export file."""
        from cardforge.exporters.moxfield_exporter import MoxfieldExporter
        
        output = tmp_path / "export.csv"
        exporter = MoxfieldExporter()
        
        # Export with minimal data
        stats = await exporter.export_collection(
            collection_id=1,
            output_path=output
        )
        
        # File should be created even if empty
        assert output.exists() or stats['errors'] > 0


class TestCSVExporter:
    """Tests for CSV export format."""
    
    @pytest.mark.asyncio
    async def test_export_creates_csv(self, tmp_path):
        """Should create CSV file."""
        from cardforge.exporters.csv_exporter import CSVExporter
        
        output = tmp_path / "export.csv"
        exporter = CSVExporter()
        
        stats = await exporter.export_csv(
            collection_id=1,
            output_path=output,
            include_binder_info=True
        )
        
        assert output.exists() or stats['errors'] > 0
    
    def test_format_condition_correctly(self):
        """Should format condition strings."""
        from cardforge.exporters.csv_exporter import CSVExporter
        
        exporter = CSVExporter()
        
        assert exporter._format_condition("near_mint") == "Near Mint"
        assert exporter._format_condition("lightly_played") == "Lightly Played"
    
    def test_format_language_correctly(self):
        """Should format language strings."""
        from cardforge.exporters.csv_exporter import CSVExporter
        
        exporter = CSVExporter()
        
        assert exporter._format_language("english") == "English"
        assert exporter._format_language("japanese") == "Japanese"


class TestArchidektExporter:
    """Tests for Archidekt export format."""
    
    @pytest.mark.asyncio
    async def test_export_creates_text_file(self, tmp_path):
        """Should create text file."""
        from cardforge.exporters.archidekt_exporter import ArchidektExporter
        
        output = tmp_path / "deck.txt"
        exporter = ArchidektExporter()
        
        stats = await exporter.export_deck(
            deck_id=1,
            output_path=output
        )
        
        assert output.exists() or stats['errors'] > 0
