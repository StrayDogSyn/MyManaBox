-- CardForge Database Schema - Hardened Production Version
-- SQLite database schema with:
-- - Proper constraints (UNIQUE, CHECK, FOREIGN KEY)
-- - Indexes for performance
-- - Full-text search support
-- - Audit timestamps
-- - Foreign key enforcement

-- Enable foreign key support (must be done before creating tables)
PRAGMA foreign_keys = ON;

-- ============================================================================
-- CARDS TABLE - Core card data from Scryfall
-- ============================================================================

CREATE TABLE IF NOT EXISTS cards (
    -- Primary key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Scryfall identifiers
    scryfall_id TEXT NOT NULL UNIQUE CHECK (length(scryfall_id) > 0),
    oracle_id TEXT CHECK (length(oracle_id) > 0),  -- Same across printings
    
    -- Card identity
    name TEXT NOT NULL CHECK (length(name) > 0),
    set_code TEXT NOT NULL CHECK (length(set_code) = 3 OR length(set_code) = 4),
    collector_number TEXT NOT NULL CHECK (length(collector_number) > 0),
    
    -- Card details
    type_line TEXT NOT NULL CHECK (length(type_line) > 0),
    oracle_text TEXT,
    mana_cost TEXT,
    cmc REAL NOT NULL CHECK (cmc >= 0),
    rarity TEXT NOT NULL CHECK (rarity IN ('common', 'uncommon', 'rare', 'mythic', 'special', 'bonus')),
    
    -- Physical properties
    colors TEXT CHECK (length(colors) <= 5),  -- WUBRG only
    color_identity TEXT CHECK (length(color_identity) <= 5),
    power TEXT,
    toughness TEXT,
    loyalty TEXT,
    
    -- Release info
    released_at DATE NOT NULL,
    
    -- Scryfall metadata
    image_uris_small TEXT,
    image_uris_normal TEXT,
    image_uris_large TEXT,
    
    -- Pricing (cached from Scryfall)
    price_usd DECIMAL(10, 2),
    price_usd_foil DECIMAL(10, 2),
    price_eur DECIMAL(10, 2),
    price_tix DECIMAL(10, 2),
    price_updated_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure unique card per set
    UNIQUE(set_code, collector_number),
    CHECK (price_usd IS NULL OR price_usd >= 0),
    CHECK (price_usd_foil IS NULL OR price_usd_foil >= 0),
    CHECK (price_eur IS NULL OR price_eur >= 0),
    CHECK (price_tix IS NULL OR price_tix >= 0)
);

-- Performance indexes for common queries
CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name);
CREATE INDEX IF NOT EXISTS idx_cards_set ON cards(set_code);
CREATE INDEX IF NOT EXISTS idx_cards_rarity ON cards(rarity);
CREATE INDEX IF NOT EXISTS idx_cards_cmc ON cards(cmc);
CREATE INDEX IF NOT EXISTS idx_cards_type ON cards(type_line);
CREATE INDEX IF NOT EXISTS idx_cards_oracle_id ON cards(oracle_id) WHERE oracle_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cards_released_at ON cards(released_at);

-- Full-text search index
CREATE VIRTUAL TABLE IF NOT EXISTS cards_fts USING fts5(
    name,
    type_line,
    oracle_text,
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS cards_ai AFTER INSERT ON cards BEGIN
    INSERT INTO cards_fts(rowid, name, type_line, oracle_text)
    VALUES (new.id, new.name, new.type_line, COALESCE(new.oracle_text, ''));
END;

CREATE TRIGGER IF NOT EXISTS cards_ad AFTER DELETE ON cards BEGIN
    INSERT INTO cards_fts(cards_fts, rowid, name, type_line, oracle_text)
    VALUES ('delete', old.id, old.name, old.type_line, COALESCE(old.oracle_text, ''));
END;

CREATE TRIGGER IF NOT EXISTS cards_au AFTER UPDATE ON cards BEGIN
    INSERT INTO cards_fts(cards_fts, rowid, name, type_line, oracle_text)
    VALUES ('delete', old.id, old.name, old.type_line, COALESCE(old.oracle_text, ''));
    INSERT INTO cards_fts(rowid, name, type_line, oracle_text)
    VALUES (new.id, new.name, new.type_line, COALESCE(new.oracle_text, ''));
END;


-- ============================================================================
-- COLLECTIONS TABLE - Collection groups
-- ============================================================================

CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK (length(name) > 0),
    description TEXT,
    is_default BOOLEAN NOT NULL DEFAULT FALSE CHECK (is_default IN (0, 1)),
    is_active BOOLEAN NOT NULL DEFAULT TRUE CHECK (is_active IN (0, 1)),
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Only one default collection allowed
    UNIQUE(is_default) WHERE is_default = TRUE
);

-- Create default collection on first run
INSERT OR IGNORE INTO collections (id, name, description, is_default, is_active)
VALUES (1, 'Main Collection', 'Primary card collection', TRUE, TRUE);

CREATE INDEX IF NOT EXISTS idx_collections_is_default ON collections(is_default);
CREATE INDEX IF NOT EXISTS idx_collections_is_active ON collections(is_active);


-- ============================================================================
-- COLLECTION_CARDS TABLE - Card instances owned by player
-- ============================================================================

CREATE TABLE IF NOT EXISTS collection_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign keys
    collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    
    -- Card instance properties
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    condition TEXT NOT NULL DEFAULT 'lightly_played' CHECK (
        condition IN ('mint', 'near_mint', 'lightly_played', 'moderately_played', 'heavily_played', 'damaged')
    ),
    foil TEXT NOT NULL DEFAULT 'non_foil' CHECK (foil IN ('non_foil', 'foil', 'etched')),
    language TEXT NOT NULL DEFAULT 'english' CHECK (length(language) > 0),
    
    -- Ownership tracking
    acquisition_date DATE,
    acquisition_price DECIMAL(10, 2),
    notes TEXT,
    
    -- External references
    manabox_id TEXT,  -- Reference to ManaBox export
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure uniqueness per collection + card + condition combination
    UNIQUE(collection_id, card_id, foil, condition, language),
    CHECK (acquisition_price IS NULL OR acquisition_price >= 0)
);

CREATE INDEX IF NOT EXISTS idx_collection_cards_card ON collection_cards(card_id);
CREATE INDEX IF NOT EXISTS idx_collection_cards_collection ON collection_cards(collection_id);
CREATE INDEX IF NOT EXISTS idx_collection_cards_manabox ON collection_cards(manabox_id) 
    WHERE manabox_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_collection_cards_condition ON collection_cards(condition);
CREATE INDEX IF NOT EXISTS idx_collection_cards_foil ON collection_cards(foil);


-- ============================================================================
-- DECKS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS decks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Deck identity
    name TEXT NOT NULL CHECK (length(name) > 0),
    format TEXT NOT NULL DEFAULT 'commander' CHECK (
        format IN ('standard', 'pioneer', 'modern', 'commander', 'canlander', 'vintage', 'legacy', 'casual', 'cube')
    ),
    
    -- Commander info (for commander format)
    commander_id INTEGER REFERENCES cards(id) ON DELETE SET NULL,
    partner_id INTEGER REFERENCES cards(id) ON DELETE SET NULL,
    
    -- Deck metadata
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE CHECK (is_active IN (0, 1)),
    is_public BOOLEAN NOT NULL DEFAULT FALSE CHECK (is_public IN (0, 1)),
    
    -- Collection reference
    collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK (format != 'commander' OR commander_id IS NOT NULL),  -- Commander format needs commander
    UNIQUE(collection_id, name)
);

CREATE INDEX IF NOT EXISTS idx_decks_format ON decks(format);
CREATE INDEX IF NOT EXISTS idx_decks_active ON decks(is_active);
CREATE INDEX IF NOT EXISTS idx_decks_collection ON decks(collection_id);
CREATE INDEX IF NOT EXISTS idx_decks_commander ON decks(commander_id);


-- ============================================================================
-- DECK_CARDS TABLE - Cards in a deck
-- ============================================================================

CREATE TABLE IF NOT EXISTS deck_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign keys
    deck_id INTEGER NOT NULL REFERENCES decks(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    
    -- Card quantity
    quantity INTEGER NOT NULL CHECK (quantity > 0 AND quantity <= 7),  -- Max 7 for 60-card deck
    
    -- Categorization
    category TEXT CHECK (category IN ('creatures', 'spells', 'lands', 'instants', 'sorceries', 'artifacts', 'enchantments', 'other')),
    is_sideboard BOOLEAN NOT NULL DEFAULT FALSE CHECK (is_sideboard IN (0, 1)),
    is_maybeboard BOOLEAN NOT NULL DEFAULT FALSE CHECK (is_maybeboard IN (0, 1)),
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure uniqueness per deck + card + category
    UNIQUE(deck_id, card_id, is_sideboard, is_maybeboard)
);

CREATE INDEX IF NOT EXISTS idx_deck_cards_deck ON deck_cards(deck_id);
CREATE INDEX IF NOT EXISTS idx_deck_cards_card ON deck_cards(card_id);
CREATE INDEX IF NOT EXISTS idx_deck_cards_category ON deck_cards(category) 
    WHERE category IS NOT NULL;


-- ============================================================================
-- AUTO-UPDATE TRIGGERS FOR TIMESTAMPS
-- ============================================================================

CREATE TRIGGER IF NOT EXISTS update_cards_timestamp 
    AFTER UPDATE ON cards
    FOR EACH ROW
BEGIN
    UPDATE cards SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_collections_timestamp 
    AFTER UPDATE ON collections
    FOR EACH ROW
BEGIN
    UPDATE collections SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_collection_cards_timestamp 
    AFTER UPDATE ON collection_cards
    FOR EACH ROW
BEGIN
    UPDATE collection_cards SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_decks_timestamp 
    AFTER UPDATE ON decks
    FOR EACH ROW
BEGIN
    UPDATE decks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_deck_cards_timestamp 
    AFTER UPDATE ON deck_cards
    FOR EACH ROW
BEGIN
    UPDATE deck_cards SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
