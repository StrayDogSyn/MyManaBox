"""Tests for database migration system."""

import pytest
import sqlite3
from pathlib import Path
from cardforge.database.migrations import (
    Migration,
    compute_checksum,
    init_migrations_table,
    get_applied_migrations,
    verify_migration_checksum,
    apply_migration,
    run_migrations,
    get_default_migrations,
)


class TestChecksumComputation:
    """Tests for migration checksum computation."""

    def test_compute_checksum_deterministic(self):
        """Checksum is deterministic."""
        sql = "CREATE TABLE test (id INTEGER PRIMARY KEY)"
        checksum1 = compute_checksum(sql)
        checksum2 = compute_checksum(sql)
        assert checksum1 == checksum2

    def test_compute_checksum_different_for_different_sql(self):
        """Different SQL produces different checksums."""
        sql1 = "CREATE TABLE test1 (id INTEGER)"
        sql2 = "CREATE TABLE test2 (id INTEGER)"
        assert compute_checksum(sql1) != compute_checksum(sql2)

    def test_checksum_length(self):
        """Checksum is 16 characters (first 16 of SHA256)."""
        checksum = compute_checksum("test sql")
        assert len(checksum) == 16
        assert checksum.isalnum()


class TestMigrationsTable:
    """Tests for migrations tracking table."""

    def test_init_migrations_table(self, temp_db_path):
        """Migrations table is created."""
        conn = sqlite3.connect(str(temp_db_path))
        init_migrations_table(conn)

        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='_migrations'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    def test_init_migrations_table_idempotent(self, temp_db_path):
        """Calling init multiple times is safe."""
        conn = sqlite3.connect(str(temp_db_path))
        init_migrations_table(conn)
        init_migrations_table(conn)  # Should not raise
        conn.close()

    def test_get_applied_migrations_empty(self, temp_db_path):
        """Empty database returns no migrations."""
        conn = sqlite3.connect(str(temp_db_path))
        init_migrations_table(conn)

        applied = get_applied_migrations(conn)
        assert applied == {}
        conn.close()


class TestMigrationApplication:
    """Tests for applying migrations."""

    def test_apply_simple_migration(self, temp_db_path):
        """Simple migration can be applied."""
        conn = sqlite3.connect(str(temp_db_path))
        init_migrations_table(conn)

        migration = Migration(
            version="001",
            name="test_migration",
            sql="CREATE TABLE test (id INTEGER PRIMARY KEY)",
        )

        apply_migration(conn, migration)

        # Verify migration was recorded
        applied = get_applied_migrations(conn)
        assert "001" in applied
        assert applied["001"].name == "test_migration"

        # Verify table was created
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='test'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    def test_apply_migration_twice_idempotent(self, temp_db_path):
        """Applying same migration twice is safe."""
        conn = sqlite3.connect(str(temp_db_path))
        init_migrations_table(conn)

        migration = Migration(
            version="001",
            name="test",
            sql="CREATE TABLE test (id INTEGER PRIMARY KEY)",
        )

        apply_migration(conn, migration)
        apply_migration(conn, migration)  # Should not raise

        # Only one record
        cursor = conn.execute("SELECT COUNT(*) FROM _migrations WHERE version='001'")
        assert cursor.fetchone()[0] == 1
        conn.close()

    def test_verify_checksum_mismatch_detected(self, temp_db_path):
        """Corrupted migration detected."""
        conn = sqlite3.connect(str(temp_db_path))
        init_migrations_table(conn)

        migration = Migration(
            version="001",
            name="test",
            sql="CREATE TABLE test (id INTEGER PRIMARY KEY)",
        )

        apply_migration(conn, migration)

        # Simulate corruption by modifying the SQL
        corrupted_migration = Migration(
            version="001",
            name="test",
            sql="CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)",
        )

        is_valid, error = verify_migration_checksum(conn, corrupted_migration)
        assert is_valid is False
        assert "checksum mismatch" in error.lower()
        conn.close()


class TestRunMigrations:
    """Tests for run_migrations() workflow."""

    def test_run_migrations_applies_pending(self, temp_db_path):
        """run_migrations applies pending migrations."""
        migrations = [
            Migration(
                version="001",
                name="initial",
                sql="CREATE TABLE cards (id INTEGER PRIMARY KEY, name TEXT)",
            ),
            Migration(
                version="002",
                name="add_prices",
                sql="ALTER TABLE cards ADD COLUMN price REAL",
            ),
        ]

        success, messages = run_migrations(temp_db_path, migrations)
        assert success is True
        assert any("All migrations applied" in m for m in messages)

        # Verify migrations applied
        conn = sqlite3.connect(str(temp_db_path))
        applied = get_applied_migrations(conn)
        assert "001" in applied
        assert "002" in applied
        conn.close()

    def test_run_migrations_skips_applied(self, temp_db_path):
        """run_migrations skips already-applied migrations."""
        migrations = [
            Migration(version="001", name="initial", sql="CREATE TABLE test (id INTEGER)"),
        ]

        # First run
        run_migrations(temp_db_path, migrations)

        # Second run
        success, messages = run_messages = run_migrations(temp_db_path, migrations)
        assert success is True
        assert any("already applied" in m.lower() for m in messages)

    def test_run_migrations_dry_run(self, temp_db_path):
        """dry_run=True validates without applying."""
        migrations = [
            Migration(version="001", name="test", sql="CREATE TABLE test (id INTEGER)"),
        ]

        success, messages = run_migrations(temp_db_path, migrations, dry_run=True)
        assert success is True
        assert any("Dry run" in m for m in messages)

        # Database should be empty (no tables created)
        conn = sqlite3.connect(str(temp_db_path))
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='test'"
        )
        assert cursor.fetchone() is None
        conn.close()

    def test_default_migrations_include_schema(self):
        """Default migrations include initial schema."""
        migrations = get_default_migrations()
        assert len(migrations) > 0
        assert migrations[0].version == "001"


class TestMigrationIntegration:
    """Integration tests for migrations."""

    def test_default_schema_migration_complete(self, temp_db_path):
        """Default schema migration creates all required tables."""
        success, messages = run_migrations(temp_db_path, get_default_migrations())
        assert success is True

        conn = sqlite3.connect(str(temp_db_path))
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '_%'"
        )
        tables = {row[0] for row in cursor.fetchall()}

        required_tables = {"cards", "collections", "collection_cards", "decks", "deck_cards"}
        assert required_tables.issubset(tables)

        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
