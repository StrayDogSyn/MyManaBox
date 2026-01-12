# Integration Plan: Card Database & Collection System

This plan details the implementation of a secure, validated integration between the Card Database and User Collection to support the Deck Advisor system.

## 1. Core Integration Service (`cardforge/services/integration_service.py`)
Create a new `CollectionIntegrationService` to manage the data flow between the read-only Card Database and the mutable User Collection.

*   **Secure Connection**: Leverage the existing `DatabaseConnection` with explicit transaction management for all integration operations to ensure atomicity.
*   **Data Mapping**: Implement `sync_collection_metadata` to ensure all collection cards have up-to-date attributes (prices, oracle text, legalities) from the master card database.
*   **Validation**: Implement `validate_collection_integrity` to detect:
    *   Orphaned collection entries (referencing non-existent cards).
    *   Data mismatches (e.g., set code conflicts).
    *   Duplicate ManaBox IDs.

## 2. Performance Monitoring (`cardforge/utils/monitoring.py`)
Implement a monitoring system to track the health of the integration.

*   **`PerformanceMonitor` class**:
    *   Track operation durations (latency).
    *   Count success/failure rates.
    *   Log detailed error context for debugging.
*   **Decorators**: Add `@monitor_performance` to critical integration methods.

## 3. Comprehensive Testing Suite (`tests/integration/test_collection_integration.py`)
Develop a dedicated test suite covering the four required areas:

*   **Lookup**: Verify accurate retrieval of card data for collection items.
*   **Analysis**: Test `DeckOptimizerAgent`'s ability to read from the collection.
*   **Recommendations**: Ensure AI recommendations can be cross-referenced with owned cards.
*   **Performance**: Stress test with bulk operations (e.g., adding/syncing 1000 cards).

## 4. Documentation & Verification
*   **Documentation**: Create `docs/integration_testing.md` detailing the architecture, data flow, and testing procedures.
*   **Verification Script**: Create `verify_integration.py` to run the integration tests and report system health.

## Execution Steps
1.  Create `cardforge/utils/monitoring.py`.
2.  Create `cardforge/services/integration_service.py`.
3.  Create `tests/integration/test_collection_integration.py`.
4.  Create `docs/integration_testing.md`.
5.  Create `verify_integration.py`.
6.  Run verification to confirm all requirements are met.
