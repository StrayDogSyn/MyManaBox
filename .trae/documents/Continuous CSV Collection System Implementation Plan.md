# Implementation Plan: Continuous CSV Collection System

This plan delivers a robust, production-ready system to manage the specified Moxfield CSV collection file (`data/moxfield_collection_2026-01-12-0154Z.csv`) with continuous synchronization, file locking, and version control.

## 1. Core Architecture: `CsvCollectionManager`
Create a new service `cardforge/services/csv_collection_manager.py` that acts as the authoritative interface for this collection.

*   **Hybrid Storage Model**:
    *   **Reads**: Served from SQLite (via `CollectionRepository`) for millisecond-latency querying and filtering.
    *   **Writes**: Transactionally applied to SQLite first, then immediately synchronized to the CSV file to ensure the file remains the "source of truth".
    *   **Synchronization**: Automatic `sync_from_csv` on startup to ingest external changes, and `sync_to_csv` on writes.

## 2. Robust File Handling
Implement a custom `FileLock` mechanism to ensure safe concurrent access.

*   **Locking Strategy**: Use a distinct `.lock` file containing the process ID and timestamp.
    *   Acquire lock before any CSV write.
    *   Wait/Retry mechanism for concurrent access attempts.
    *   Automatic stale lock cleanup (timeout-based).
*   **Atomic Writes**: Write to a temporary file first (`.tmp`), then perform an atomic rename to the target CSV path to prevent data corruption during write failures.

## 3. Version Control & History
Implement automatic versioning to preserve data integrity.

*   **History Directory**: Create a `data/history/` directory.
*   **Versioning Logic**: Before any write operation, copy the current CSV to `data/history/{filename}_{timestamp}.csv`.
*   **Retention Policy**: Keep the last 10 versions to manage disk space (configurable).

## 4. Collection Interface
The `CsvCollectionManager` will provide a high-level API:

*   `initialize()`: Sets up file paths, acquires lock, performs initial sync (CSV -> DB).
*   `query(filters)`: Proxies to `CollectionRepository` for fast filtering.
*   `add_card(card_data)`, `update_card(card_id, data)`, `remove_card(card_id)`:
    1.  Acquire CSV lock.
    2.  Create backup version.
    3.  Update SQLite DB.
    4.  Regenerate full CSV from DB.
    5.  Atomic write to CSV.
    6.  Release lock.
*   `bulk_import(csv_path)`: Optimized batch operation.

## 5. Testing & Verification
Create `tests/integration/test_csv_manager.py` to verify:

*   **Concurrency**: Simulate multiple "processes" trying to write simultaneously.
*   **Persistence**: Verify data survives service restarts.
*   **Integrity**: Ensure CSV content matches DB content exactly.
*   **Performance**: Measure latency of read/write operations with large datasets (10k+ cards).

## Execution Steps
1.  Create `cardforge/utils/file_locking.py` (Locking mechanism).
2.  Create `cardforge/services/csv_collection_manager.py` (Core logic).
3.  Create `tests/integration/test_csv_manager.py` (Test suite).
4.  Run tests and verify against the specific file path.
