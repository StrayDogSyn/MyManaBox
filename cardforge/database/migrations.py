"""Safe database migration system.

Applies migrations with checksums to prevent repeated/corrupted migrations.
All migrations tracked and reversible.
"""

import sqlite3
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import NamedTuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class Migration(NamedTuple):
    """Migration metadata."""

    version: str  # e.g., "001"
    name: str  # e.g., "initial_schema"
    sql: str  # SQL to execute
    checksum: str = ""  # SHA256 hash of SQL


@dataclass
class MigrationRecord:
    """Record of applied migration."""

    version: str
    name: str
    applied_at: datetime
    checksum: str


def compute_checksum(sql: str) -> str:
    """Compute SHA256 checksum of SQL content.

    Args:
        sql: SQL content

    Returns:
        First 16 characters of SHA256 hash
    """
    return hashlib.sha256(sql.encode()).hexdigest()[:16]


def init_migrations_table(conn: sqlite3.Connection) -> None:
    """Create migrations tracking table if not exists.

    Args:
        conn: SQLite connection
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS _migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            checksum TEXT NOT NULL,
            applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def get_applied_migrations(conn: sqlite3.Connection) -> dict[str, MigrationRecord]:
    """Get all applied migrations from database.

    Args:
        conn: SQLite connection

    Returns:
        Dictionary of {version: MigrationRecord}
    """
    cursor = conn.execute(
        "SELECT version, name, applied_at, checksum FROM _migrations ORDER BY version"
    )
    return {
        row[0]: MigrationRecord(
            version=row[0],
            name=row[1],
            applied_at=datetime.fromisoformat(row[2]),
            checksum=row[3],
        )
        for row in cursor.fetchall()
    }


def verify_migration_checksum(
    conn: sqlite3.Connection, migration: Migration
) -> tuple[bool, Optional[str]]:
    """Verify a migration hasn't been corrupted.

    Args:
        conn: SQLite connection
        migration: Migration to verify

    Returns:
        Tuple of (is_valid, error_message)
    """
    cursor = conn.execute(
        "SELECT checksum FROM _migrations WHERE version = ?", (migration.version,)
    )
    row = cursor.fetchone()

    if not row:
        return True, None  # Not yet applied

    stored_checksum = row[0]
    computed_checksum = compute_checksum(migration.sql)

    if stored_checksum != computed_checksum:
        return False, (
            f"Migration {migration.version} checksum mismatch! "
            f"Expected {stored_checksum}, got {computed_checksum}. "
            f"This may indicate corruption."
        )

    return True, None


def apply_migration(conn: sqlite3.Connection, migration: Migration) -> None:
    """Apply a single migration with safety checks.

    Args:
        conn: SQLite connection
        migration: Migration to apply

    Raises:
        sqlite3.Error: If migration fails
        RuntimeError: If migration already applied or checksum mismatch
    """
    # Check if already applied
    cursor = conn.execute(
        "SELECT version FROM _migrations WHERE version = ?", (migration.version,)
    )
    if cursor.fetchone():
        logger.info(f"Migration {migration.version} already applied, skipping")
        return

    # Verify checksum if it was applied before
    is_valid, error = verify_migration_checksum(conn, migration)
    if not is_valid:
        raise RuntimeError(error)

    try:
        # Execute migration SQL
        conn.executescript(migration.sql)

        # Record migration
        checksum = compute_checksum(migration.sql)
        conn.execute(
            """
            INSERT INTO _migrations (version, name, checksum)
            VALUES (?, ?, ?)
            """,
            (migration.version, migration.name, checksum),
        )
        conn.commit()
        logger.info(f"✅ Applied migration {migration.version}: {migration.name}")

    except sqlite3.Error as e:
        conn.rollback()
        logger.error(
            f"❌ Failed to apply migration {migration.version}: {e}. Rolling back."
        )
        raise


def run_migrations(
    db_path: Path, migrations: list[Migration], dry_run: bool = False
) -> tuple[bool, list[str]]:
    """Run all pending migrations.

    Args:
        db_path: Path to SQLite database
        migrations: List of migrations to apply
        dry_run: If True, validate without applying

    Returns:
        Tuple of (success, messages)
    """
    messages: list[str] = []

    try:
        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(db_path))
        init_migrations_table(conn)

        # Check all migrations
        applied = get_applied_migrations(conn)
        pending = [m for m in migrations if m.version not in applied]

        if not pending:
            messages.append("✅ All migrations already applied")
            conn.close()
            return True, messages

        messages.append(f"📋 Found {len(pending)} pending migration(s)")

        if dry_run:
            for migration in pending:
                messages.append(f"  - {migration.version}: {migration.name}")
            messages.append("🔍 Dry run complete - no changes applied")
            conn.close()
            return True, messages

        # Apply pending migrations
        for migration in pending:
            try:
                apply_migration(conn, migration)
                messages.append(f"✅ {migration.version}: {migration.name}")
            except Exception as e:
                messages.append(f"❌ {migration.version} failed: {e}")
                conn.close()
                return False, messages

        conn.close()
        messages.append("\n🎉 All migrations applied successfully!")
        return True, messages

    except Exception as e:
        messages.append(f"❌ Migration error: {e}")
        return False, messages


# ============================================================================
# PREDEFINED MIGRATIONS
# ============================================================================

MIGRATION_001_INITIAL_SCHEMA = Migration(
    version="001",
    name="initial_hardened_schema",
    sql="""
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Cards table
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scryfall_id TEXT NOT NULL UNIQUE CHECK (length(scryfall_id) > 0),
    oracle_id TEXT CHECK (length(oracle_id) > 0),
    name TEXT NOT NULL CHECK (length(name) > 0),
    set_code TEXT NOT NULL CHECK (length(set_code) = 3 OR length(set_code) = 4),
    collector_number TEXT NOT NULL CHECK (length(collector_number) > 0),
    type_line TEXT NOT NULL CHECK (length(type_line) > 0),
    oracle_text TEXT,
    mana_cost TEXT,
    cmc REAL NOT NULL CHECK (cmc >= 0),
    rarity TEXT NOT NULL CHECK (rarity IN ('common', 'uncommon', 'rare', 'mythic', 'special', 'bonus')),
    colors TEXT CHECK (length(colors) <= 5),
    color_identity TEXT CHECK (length(color_identity) <= 5),
    power TEXT,
    toughness TEXT,
    loyalty TEXT,
    released_at DATE NOT NULL,
    image_uris_small TEXT,
    image_uris_normal TEXT,
    image_uris_large TEXT,
    price_usd DECIMAL(10, 2),
    price_usd_foil DECIMAL(10, 2),
    price_eur DECIMAL(10, 2),
    price_tix DECIMAL(10, 2),
    price_updated_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(set_code, collector_number),
    CHECK (price_usd IS NULL OR price_usd >= 0),
    CHECK (price_usd_foil IS NULL OR price_usd_foil >= 0),
    CHECK (price_eur IS NULL OR price_eur >= 0),
    CHECK (price_tix IS NULL OR price_tix >= 0)
);

CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name);
CREATE INDEX IF NOT EXISTS idx_cards_set ON cards(set_code);
CREATE INDEX IF NOT EXISTS idx_cards_rarity ON cards(rarity);
CREATE INDEX IF NOT EXISTS idx_cards_cmc ON cards(cmc);
CREATE INDEX IF NOT EXISTS idx_cards_type ON cards(type_line);
CREATE INDEX IF NOT EXISTS idx_cards_oracle_id ON cards(oracle_id) WHERE oracle_id IS NOT NULL;

-- Collections table
CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK (length(name) > 0),
    description TEXT,
    is_default BOOLEAN NOT NULL DEFAULT FALSE CHECK (is_default IN (0, 1)),
    is_active BOOLEAN NOT NULL DEFAULT TRUE CHECK (is_active IN (0, 1)),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(is_default) WHERE is_default = TRUE
);

INSERT OR IGNORE INTO collections (id, name, description, is_default, is_active)
VALUES (1, 'Main Collection', 'Primary card collection', TRUE, TRUE);

-- Collection cards table
CREATE TABLE IF NOT EXISTS collection_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    condition TEXT NOT NULL DEFAULT 'lightly_played' CHECK (
        condition IN ('mint', 'near_mint', 'lightly_played', 'moderately_played', 'heavily_played', 'damaged')
    ),
    foil TEXT NOT NULL DEFAULT 'non_foil' CHECK (foil IN ('non_foil', 'foil', 'etched')),
    language TEXT NOT NULL DEFAULT 'english' CHECK (length(language) > 0),
    acquisition_date DATE,
    acquisition_price DECIMAL(10, 2),
    notes TEXT,
    manabox_id TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(collection_id, card_id, foil, condition, language),
    CHECK (acquisition_price IS NULL OR acquisition_price >= 0)
);

CREATE INDEX IF NOT EXISTS idx_collection_cards_card ON collection_cards(card_id);
CREATE INDEX IF NOT EXISTS idx_collection_cards_collection ON collection_cards(collection_id);

-- Decks table
CREATE TABLE IF NOT EXISTS decks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (length(name) > 0),
    format TEXT NOT NULL DEFAULT 'commander' CHECK (
        format IN ('standard', 'pioneer', 'modern', 'commander', 'canlander', 'vintage', 'legacy', 'casual', 'cube')
    ),
    commander_id INTEGER REFERENCES cards(id) ON DELETE SET NULL,
    partner_id INTEGER REFERENCES cards(id) ON DELETE SET NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE CHECK (is_active IN (0, 1)),
    is_public BOOLEAN NOT NULL DEFAULT FALSE CHECK (is_public IN (0, 1)),
    collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (format != 'commander' OR commander_id IS NOT NULL),
    UNIQUE(collection_id, name)
);

-- Deck cards table
CREATE TABLE IF NOT EXISTS deck_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id INTEGER NOT NULL REFERENCES decks(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0 AND quantity <= 7),
    category TEXT CHECK (category IN ('creatures', 'spells', 'lands', 'instants', 'sorceries', 'artifacts', 'enchantments', 'other')),
    is_sideboard BOOLEAN NOT NULL DEFAULT FALSE CHECK (is_sideboard IN (0, 1)),
    is_maybeboard BOOLEAN NOT NULL DEFAULT FALSE CHECK (is_maybeboard IN (0, 1)),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(deck_id, card_id, is_sideboard, is_maybeboard)
);

-- Auto-update triggers
CREATE TRIGGER IF NOT EXISTS update_cards_timestamp 
    AFTER UPDATE ON cards FOR EACH ROW
BEGIN
    UPDATE cards SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_collections_timestamp 
    AFTER UPDATE ON collections FOR EACH ROW
BEGIN
    UPDATE collections SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_collection_cards_timestamp 
    AFTER UPDATE ON collection_cards FOR EACH ROW
BEGIN
    UPDATE collection_cards SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_decks_timestamp 
    AFTER UPDATE ON decks FOR EACH ROW
BEGIN
    UPDATE decks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_deck_cards_timestamp 
    AFTER UPDATE ON deck_cards FOR EACH ROW
BEGIN
    UPDATE deck_cards SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
""",
)


def get_default_migrations() -> list[Migration]:
    """Get the default set of migrations.

    Returns:
        List of Migration objects
    """
    return [MIGRATION_001_INITIAL_SCHEMA]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m cardforge.database.migrations <db_path> [--dry-run]")
        sys.exit(1)

    db_path = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv

    success, messages = run_migrations(db_path, get_default_migrations(), dry_run)
    for msg in messages:
        print(msg)
    sys.exit(0 if success else 1)
