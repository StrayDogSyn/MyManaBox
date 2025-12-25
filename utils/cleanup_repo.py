#!/usr/bin/env python3
"""
MyManaBox Repository Cleanup Script

Safely removes redundant, old, and orphaned files while preserving essential code and data.

WHAT WILL BE REMOVED:
- agent_files/ folder (incompatible architecture)
- legacy/ folder (old deprecated scripts)
- Old backup CSVs from July (keeping only current collection)
- Test files (test_export.py, test_export.csv)
- Redundant documentation files
- Old scripts that have been superseded
- Temporary/cache files

WHAT WILL BE PRESERVED:
- Current collection data (enriched_collection_complete.csv, moxfield_export.csv)
- Recent backups in data/backups/
- All src/ code
- Working scripts (auto_enrich.py, import_mobile.py, etc.)
- Essential documentation
- GUI and main application files

Usage:
    python cleanup_repo.py --dry-run    # Show what would be deleted
    python cleanup_repo.py              # Perform cleanup
    python cleanup_repo.py --aggressive # Also remove cache and pycache
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import argparse


class RepoCleanup:
    """Clean up MyManaBox repository."""
    
    def __init__(self, dry_run: bool = True, aggressive: bool = False):
        self.dry_run = dry_run
        self.aggressive = aggressive
        self.project_root = Path(__file__).parent
        self.removed_count = 0
        self.saved_space = 0
        
    def get_size(self, path: Path) -> int:
        """Get size of file or directory in bytes."""
        if path.is_file():
            return path.stat().st_size
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except PermissionError:
            pass
        return total
    
    def format_size(self, bytes: int) -> str:
        """Format bytes as human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} TB"
    
    def remove_item(self, path: Path, reason: str):
        """Remove file or directory."""
        if not path.exists():
            return
        
        size = self.get_size(path)
        size_str = self.format_size(size)
        
        if self.dry_run:
            print(f"  [DRY RUN] Would remove: {path.relative_to(self.project_root)}")
            print(f"            Reason: {reason}")
            print(f"            Size: {size_str}")
        else:
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"  ✓ Removed: {path.relative_to(self.project_root)} ({size_str})")
                self.removed_count += 1
                self.saved_space += size
            except Exception as e:
                print(f"  ✗ Error removing {path.name}: {e}")
    
    def cleanup_agent_files(self):
        """Remove agent_files folder - incompatible architecture."""
        print("\n1. Removing agent_files/ (incompatible with current architecture)")
        agent_files = self.project_root / "agent_files"
        if agent_files.exists():
            self.remove_item(agent_files, "Different project architecture, won't work with current system")
        else:
            print("  Already removed")
    
    def cleanup_legacy(self):
        """Remove legacy folder - deprecated scripts."""
        print("\n2. Removing legacy/ (deprecated old scripts)")
        legacy = self.project_root / "legacy"
        if legacy.exists():
            self.remove_item(legacy, "Old scripts superseded by current src/ structure")
        else:
            print("  Already removed")
    
    def cleanup_old_backups(self):
        """Remove old backup CSVs from data/ (July backups)."""
        print("\n3. Removing old backup CSVs from data/")
        data_dir = self.project_root / "data"
        
        # List of old backup files to remove (July 2025)
        old_backups = [
            "collection_before_final_fix_20250705_144759.csv",
            "collection_before_premiums_20250705_145405.csv",
            "collection_before_purchase_optimization_20250705_151034.csv",
            "collection_before_tcgplayer_20250705_150342.csv",
            "enriched_collection_backup_20250705_142538.csv",
            "enriched_collection_complete.backup_20250705_105302.csv",
            "enriched_collection_complete.backup_20250705_105307.csv",
            "enriched_collection_complete.backup_20250705_105331.csv",
            "enriched_collection_complete.backup_20250705_105757.csv",
            "enriched_collection_complete.backup_enhanced_20250705_141620.csv",
            "advanced_enhancement_report.txt",
            "average_pricing_analysis_20250705_152413.json"
        ]
        
        for backup_file in old_backups:
            backup_path = data_dir / backup_file
            if backup_path.exists():
                self.remove_item(backup_path, "Old backup from July 2025, no longer needed")
    
    def cleanup_test_files(self):
        """Remove test files from project root."""
        print("\n4. Removing test files")
        test_files = [
            self.project_root / "test_export.py",
            self.project_root / "test_export.csv"
        ]
        
        for test_file in test_files:
            if test_file.exists():
                self.remove_item(test_file, "Temporary test file")
    
    def cleanup_redundant_docs(self):
        """Remove redundant documentation files."""
        print("\n5. Consolidating documentation")
        
        # Keep: GET_STARTED_NOW.md (main guide), README.md (project overview)
        # Keep: ENHANCED_FEATURES.md (feature reference)
        # Remove: Redundant analysis and summary files
        
        redundant_docs = [
            "AGENT_FILES_ANALYSIS.md",  # Useful once, not needed ongoing
            "INTEGRATION_PLAN.md",      # Analysis doc, not needed ongoing
            "COMPLETE_SUMMARY.md",      # Redundant with GET_STARTED_NOW
            "ENHANCEMENT_SUMMARY.md",   # Redundant with GET_STARTED_NOW
            "START_HERE.md",            # Redundant with GET_STARTED_NOW
        ]
        
        for doc in redundant_docs:
            doc_path = self.project_root / doc
            if doc_path.exists():
                self.remove_item(doc_path, "Redundant with GET_STARTED_NOW.md")
    
    def cleanup_old_scripts(self):
        """Remove old superseded scripts from scripts/."""
        print("\n6. Removing old/superseded scripts")
        
        scripts_dir = self.project_root / "scripts"
        old_scripts = [
            "advanced_price_enhancement.py",  # Superseded by auto_enrich.py
            "average_pricing.py",             # Superseded by auto_enrich.py
            "comprehensive_price_update.py",  # Superseded by auto_enrich.py
            "price_analysis.py"               # Superseded by main.py --analytics
        ]
        
        for script in old_scripts:
            script_path = scripts_dir / script
            if script_path.exists():
                self.remove_item(script_path, "Superseded by new scripts")
        
        # Check if there's a duplicate enrich_collection.py
        old_enrich = scripts_dir / "enrich_collection.py"
        new_enrich = scripts_dir / "auto_enrich.py"
        if old_enrich.exists() and new_enrich.exists():
            self.remove_item(old_enrich, "Superseded by auto_enrich.py")
    
    def cleanup_cache(self):
        """Remove cache directories (aggressive mode only)."""
        if not self.aggressive:
            print("\n7. Skipping cache cleanup (use --aggressive to enable)")
            return
        
        print("\n7. Removing cache files (aggressive mode)")
        
        # Remove __pycache__ directories
        for pycache in self.project_root.rglob('__pycache__'):
            if pycache.is_dir():
                self.remove_item(pycache, "Python bytecode cache")
        
        # Note: card_cache.json is kept - it's valuable for avoiding API rate limits
        print("  Note: Keeping card_cache.json (Scryfall API cache)")
    
    def cleanup_misc(self):
        """Remove miscellaneous unnecessary files."""
        print("\n8. Removing miscellaneous files")
        
        misc_files = [
            self.project_root / "directory_listing.txt"  # Temporary listing file
        ]
        
        for misc_file in misc_files:
            if misc_file.exists():
                self.remove_item(misc_file, "Temporary/unnecessary file")
    
    def print_summary(self):
        """Print cleanup summary."""
        print("\n" + "=" * 60)
        print("Cleanup Summary")
        print("=" * 60)
        
        if self.dry_run:
            print(f"\n[DRY RUN MODE]")
            print(f"Would remove {self.removed_count} items")
            print(f"Would save approximately {self.format_size(self.saved_space)}")
            print("\nRun without --dry-run to actually remove files")
        else:
            print(f"\n✓ Removed {self.removed_count} items")
            print(f"✓ Freed {self.format_size(self.saved_space)}")
            print("\nYour repository is now cleaner!")
    
    def run(self):
        """Execute all cleanup operations."""
        print("=" * 60)
        print("MyManaBox Repository Cleanup")
        print("=" * 60)
        
        if self.dry_run:
            print("\nDRY RUN MODE - No files will be deleted")
        
        print(f"\nProject root: {self.project_root}")
        
        self.cleanup_agent_files()
        self.cleanup_legacy()
        self.cleanup_old_backups()
        self.cleanup_test_files()
        self.cleanup_redundant_docs()
        self.cleanup_old_scripts()
        self.cleanup_cache()
        self.cleanup_misc()
        
        self.print_summary()
        
        if self.dry_run:
            print("\n" + "=" * 60)
            print("What will be KEPT:")
            print("=" * 60)
            print("""
✓ Current collection data:
  - data/enriched_collection_complete.csv
  - data/moxfield_export.csv
  - data/backups/ (all recent backups)

✓ All source code:
  - src/ (complete codebase)
  - main.py, gui.py, run_gui.py

✓ Working scripts:
  - scripts/auto_enrich.py
  - scripts/import_mobile.py
  - scripts/export_collection.py
  - scripts/setup_automation.py
  - scripts/verify_setup.py
  - scripts/README.md

✓ Essential documentation:
  - README.md (project overview)
  - GET_STARTED_NOW.md (main user guide)
  - ENHANCED_FEATURES.md (feature reference)
  - QUICK_START.md (command reference)
  - docs/ (all detailed documentation)

✓ Configuration:
  - requirements.txt
  - pyproject.toml
  - .gitignore, .editorconfig

✓ Valuable cache:
  - card_cache.json (10 MB of Scryfall data)
            """)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clean up MyManaBox repository by removing redundant files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cleanup_repo.py --dry-run        # Preview what will be removed
  python cleanup_repo.py                  # Perform cleanup
  python cleanup_repo.py --aggressive     # Also remove cache files

This will remove:
  - agent_files/ (incompatible architecture)
  - legacy/ (old deprecated scripts)
  - Old backup CSVs from July
  - Test files
  - Redundant documentation
  - Old superseded scripts

This will keep:
  - All source code (src/)
  - Current collection data
  - Working scripts
  - Essential documentation
  - Configuration files
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be deleted without actually deleting (default)"
    )
    
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the cleanup (removes --dry-run)"
    )
    
    parser.add_argument(
        "--aggressive",
        action="store_true",
        help="Also remove cache files (__pycache__ directories)"
    )
    
    args = parser.parse_args()
    
    # If --execute is specified, turn off dry-run
    dry_run = not args.execute
    
    if not args.execute:
        print("\n⚠️  Running in DRY RUN mode. Use --execute to actually remove files.")
    
    cleanup = RepoCleanup(dry_run=dry_run, aggressive=args.aggressive)
    cleanup.run()
    
    if dry_run:
        print("\n💡 Tip: Review the list above, then run with --execute to proceed")
    else:
        print("\n✓ Cleanup complete! Run 'python scripts/verify_setup.py' to verify everything still works.")


if __name__ == "__main__":
    main()
