# MyManaBox Project Structure - Clean & Organized

## 📁 Directory Structure

```text
MyManaBox/
├── 📋 Configuration Files
│   ├── .editorconfig          # Editor configuration
│   ├── .gitignore             # Git ignore rules
│   ├── pyproject.toml         # Python project configuration
│   └── requirements.txt       # Python dependencies
│
├── 📚 Documentation
│   ├── README.md              # Main project documentation
│   ├── LICENSE                # Project license
│   └── docs/                  # Detailed documentation
│       ├── COLLECTION_UPDATE_SUMMARY.md
│       ├── COMPLETION_SUMMARY.md
│       ├── IMPORT_INSTRUCTIONS.md
│       ├── README.md
│       ├── REFACTORING_SUMMARY.md
│       └── USAGE.md
│
├── 🗃️ Data & Backups
│   ├── data/                  # Main data directory
│   │   ├── backups/           # Backup files
│   │   │   └── moxfield_export_backup.csv
│   │   ├── card_cache.json    # Scryfall API cache
│   │   ├── enriched_collection.csv        # Sample enriched data
│   │   ├── enriched_collection_complete.csv # Full enriched collection
│   │   └── moxfield_export.csv # Original collection data
│   ├── backups/               # Historical backups
│   │   └── moxfield_export.csv.backup_20250704_223533
│   └── sorted_output/         # Output directory for sorted collections
│
├── 🧠 Core Application
│   ├── main.py                # Main application entry point
│   ├── dev.py                 # Development utilities
│   └── src/                   # Source code
│       ├── data/              # Data access layer
│       │   ├── csv_loader.py
│       │   ├── file_manager.py
│       │   ├── moxfield_importer.py
│       │   └── scryfall_client.py
│       ├── models/            # Data models
│       │   ├── card.py
│       │   ├── collection.py
│       │   └── enums.py
│       ├── presentation/      # User interface
│       │   ├── cli_parser.py
│       │   ├── console_interface.py
│       │   └── formatters.py
│       ├── services/          # Business logic
│       │   ├── analytics_service.py
│       │   ├── collection_service.py
│       │   ├── import_service.py
│       │   ├── search_service.py
│       │   └── sorting_service.py
│       └── utils/             # Utilities
│           ├── constants.py
│           └── helpers.py
│
├── 🔧 Tools & Scripts
│   ├── scripts/               # Utility scripts
│   │   ├── demonstrate_coverage.py
│   │   ├── enrich_collection.py
│   │   ├── field_verification.py
│   │   ├── show_fields.py
│   │   └── README.md
│   └── legacy/                # Legacy code (reference only)
│       ├── card_sorter.py
│       ├── enhanced_sorter.py
│       ├── mymanabox.py
│       └── scryfall_api.py
│
├── 🧪 Testing
│   └── tests/
│       ├── test_all.bat
│       ├── test_all.ps1
│       ├── test_comprehensive_export.py
│       ├── test_mymanabox.py
│       ├── test_refactored.py
│       └── test_value_calculation.py
│
└── 🔒 Environment
    ├── .venv/                 # Python virtual environment
    └── .vscode/               # VS Code configuration
```

## 🧹 Cleanup Actions Performed

### ✅ Removed Temporary Files

- `complete_enrichment.py` - Temporary enrichment script
- `create_enriched_csv.py` - Development script
- `create_enriched_manual.py` - Manual enrichment attempt
- `enrich_export.py` - Export helper script
- `merge_enriched.py` - Data merger script
- `quick_enrich.py` - Quick processing script
- `simple_enrich.py` - Simple enrichment test
- `run_enrichment.bat` - Temporary batch file

### ✅ Organized Data Structure

- Created `data/backups/` subdirectory
- Moved backup files to proper location
- Organized enriched collection files

### ✅ Cleaned Development Artifacts

- Removed all `__pycache__` directories
- Cleared Python bytecode files (.pyc)
- Cleaned up temporary development files

### ✅ File Organization

- Moved misplaced files to correct directories
- Maintained proper separation of concerns
- Preserved all important data and functionality

## 📊 Current Data Files

1. **`moxfield_export.csv`** - Original collection (1,834 cards)
2. **`enriched_collection_complete.csv`** - Full enriched collection (67 columns)
3. **`card_cache.json`** - Scryfall API cache (281 unique entries)
4. **Backup files** - Safely stored in backups/ directory

## 🎯 Project Status

The MyManaBox project is now **clean, organized, and fully functional** with:

- ✅ Complete MTG collection enrichment capability
- ✅ Clean, maintainable codebase structure
- ✅ Comprehensive Scryfall API integration
- ✅ Organized data and backup system
- ✅ Development artifacts removed
- ✅ Professional project organization
