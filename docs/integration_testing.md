# Integration Testing: Card Database & Collection System

This document details the integration between the read-only Card Database and the mutable User Collection system, focusing on data integrity, security, and performance.

## Architecture

The integration is managed by `CollectionIntegrationService`, which acts as the secure bridge between:
1.  **CardRepository**: Access to the master card database (Scryfall data).
2.  **CollectionRepository**: Access to user-owned collections.

### Key Components

*   **Secure Connection**: Uses `DatabaseConnection` with explicit transaction management to ensure atomic operations.
*   **Data Validation**: Enforces strict integrity checks (no orphaned collection items).
*   **Performance Monitoring**: Tracks operation latency and success rates via `PerformanceMonitor`.

## Testing Procedures

### 1. Basic Lookup & Add
Verifies that cards can be securely looked up in the master DB and added to a collection with correct metadata mapping.

*   **Test**: `test_secure_card_lookup_and_add`
*   **Validation**: Checks that `CollectionCard` entries inherit correct attributes (name, set) from `Card`.

### 2. Analysis Preparation
Verifies that collection data can be correctly formatted for the AI Deck Advisor.

*   **Test**: `test_collection_analysis_preparation`
*   **Validation**: Ensures JSON output contains all required fields for `DeckOptimizerAgent`.

### 3. Data Integrity
Verifies the system detects and handles data inconsistencies.

*   **Test**: `test_validation_checks`
*   **Validation**: Simulates corrupted data (orphans) and ensures the validator reports them.

### 4. Performance
Stress tests the system under load.

*   **Test**: `test_performance_load`
*   **Validation**: Bulk add 100+ cards and ensure response time stays within budget (<5s).

## Running Tests

Execute the integration test suite:

```bash
pytest tests/integration/test_collection_integration.py -v
```

## Monitoring

System metrics are logged automatically:
*   `[MONITOR] operation_name: SUCCESS/FAILURE in Xms`

To view aggregate stats programmatically:
```python
from cardforge.utils.monitoring import PerformanceMonitor
print(PerformanceMonitor.get_stats())
```
