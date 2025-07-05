# MyManaBox - Refactored with Separation of Concerns

## 🎯 Project Overview

MyManaBox has been completely refactored using **separation of concerns** principles, transforming a monolithic script into a well-organized, maintainable application architecture.

## 📁 New Project Structure

```
MyManaBox/
├── main.py                     # 🚀 Main entry point
├── src/                        # 📦 Source code organized by responsibility
│   ├── models/                 # 📊 Data Models
│   │   ├── __init__.py
│   │   ├── card.py            # Card data structure
│   │   ├── collection.py      # Collection management
│   │   └── enums.py           # Color, Rarity, Type enums
│   ├── data/                   # 💾 Data Access Layer
│   │   ├── __init__.py
│   │   ├── csv_loader.py      # CSV file operations
│   │   ├── moxfield_importer.py # Moxfield import logic
│   │   ├── scryfall_client.py  # Scryfall API client
│   │   └── file_manager.py     # File management utilities
│   ├── services/               # 🔧 Business Logic Layer
│   │   ├── __init__.py
│   │   ├── collection_service.py # Collection management
│   │   ├── sorting_service.py    # Card sorting logic
│   │   ├── search_service.py     # Search and filtering
│   │   ├── analytics_service.py  # Statistics and insights
│   │   └── import_service.py     # Import coordination
│   ├── presentation/           # 🖥️ Presentation Layer
│   │   ├── __init__.py
│   │   ├── console_interface.py  # CLI interface
│   │   ├── formatters.py         # Output formatting
│   │   └── cli_parser.py         # Command line parsing
│   └── utils/                  # 🛠️ Utilities
│       ├── __init__.py
│       ├── constants.py        # Application constants
│       └── helpers.py          # Helper functions
├── test_refactored.py          # ✅ Testing script
└── [existing files...]         # Legacy files preserved
```

## 🏗️ Architecture Principles

### 1. **Separation of Concerns**
Each layer has a single, well-defined responsibility:

- **Models**: Pure data structures with no external dependencies
- **Data Access**: File I/O, API calls, data persistence
- **Services**: Business logic, card operations, analytics
- **Presentation**: User interface, formatting, CLI handling
- **Utils**: Common utilities, constants, helpers

### 2. **Dependency Injection**
Services are created and injected at the application level, making testing and modularity easier.

### 3. **Type Safety**
Comprehensive type hints throughout the codebase for better IDE support and error prevention.

### 4. **Clean Interfaces**
Each layer exposes clean, minimal interfaces to other layers.

## 🔧 Key Components

### Data Models (`src/models/`)

**Card Model**:
```python
@dataclass
class Card:
    name: str
    edition: str
    count: int = 1
    purchase_price: Optional[Decimal] = None
    condition: Condition = Condition.NEAR_MINT
    foil: bool = False
    # API-enriched fields
    colors: Optional[Set[CardColor]] = None
    rarity: Optional[CardRarity] = None
    types: Optional[Set[CardType]] = None
```

**Collection Model**:
- Manages lists of cards
- Provides aggregation methods (total value, card counts)
- Handles duplicate detection
- Supports grouping and filtering operations

### Data Access Layer (`src/data/`)

**CSVLoader**: Handles CSV file operations
**MoxfieldImporter**: Manages Moxfield collection imports  
**ScryfallClient**: API integration for card data enrichment
**FileManager**: File operations, backups, cleanup

### Business Logic (`src/services/`)

**CollectionService**: Core collection management
**SortingService**: Card organization and export
**SearchService**: Card search and filtering
**AnalyticsService**: Collection insights and statistics
**ImportService**: Import coordination and validation

### Presentation Layer (`src/presentation/`)

**ConsoleInterface**: Main CLI application
**Formatters**: Output formatting (table, CSV, JSON)
**CLIParser**: Command line argument parsing

## ✅ Benefits of Refactoring

### 1. **Maintainability**
- Clear separation makes code easier to understand and modify
- Changes in one layer don't cascade to others
- New features can be added with minimal impact

### 2. **Testability**
- Each component can be unit tested in isolation
- Mock dependencies easily for testing
- Business logic separated from I/O operations

### 3. **Extensibility**
- New data sources (APIs, databases) can be added without changing business logic
- New output formats easily supported
- Additional services can be plugged in

### 4. **Reusability**
- Services can be reused in different contexts
- Models are framework-agnostic
- Data access layer can support multiple clients

### 5. **Type Safety**
- Comprehensive type hints prevent runtime errors
- Better IDE support and autocomplete
- Easier refactoring with confidence

## 🚀 Usage

The refactored application maintains all original functionality while providing a cleaner architecture:

```bash
# Run with new architecture
python main.py

# All original commands still work
python card_sorter.py --summary
python card_sorter.py --sort color
python card_sorter.py --duplicates
```

## 🔄 Migration Path

The refactoring preserves all existing functionality:

- ✅ **Backward Compatibility**: All original commands work
- ✅ **Data Compatibility**: Uses existing CSV files
- ✅ **Feature Parity**: All features preserved and enhanced
- ✅ **Performance**: Improved through better organization

## 🎉 Results

**Before Refactoring**:
- Single 536-line monolithic file
- Mixed responsibilities (UI, business logic, data access)
- Difficult to test and extend
- Tight coupling between components

**After Refactoring**:
- 15+ focused modules with clear responsibilities
- Separation of concerns with clean interfaces
- Easy to test, extend, and maintain
- Loose coupling with dependency injection
- Type-safe throughout
- Ready for future enhancements

The project is now a well-architected, professional-grade application that follows software engineering best practices while maintaining all the functionality you love!
