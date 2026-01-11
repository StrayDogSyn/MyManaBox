-- Migration 001: Initial Schema
-- Creates all core tables for CardForge database
-- Author: CardForge Team
-- Date: 2026-01-11

-- ============================================================================
-- CARDS TABLE
-- ============================================================================
-- Stores MTG card data from Scryfall API
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scryfall_id VARCHAR(36) NOT NULL UNIQUE,
    oracle_id VARCHAR(36),
    name VARCHAR(255) NOT NULL,
    set_code VARCHAR(10) NOT NULL,
    collector_number VARCHAR(20) NOT NULL,
    mana_cost VARCHAR(100),
    cmc REAL DEFAULT 0.0,
    type_line VARCHAR(255) NOT NULL,
    oracle_text TEXT,
    colors VARCHAR(20),
    color_identity VARCHAR(20),
    power VARCHAR(10),
    toughness VARCHAR(10),
    loyalty VARCHAR(10),
    rarity VARCHAR(20) NOT NULL,
    is_foil_available BOOLEAN DEFAULT 0,
    is_reserved_list BOOLEAN DEFAULT 0,
    is_commander BOOLEAN DEFAULT 0,
    legalities TEXT,
    price_usd DECIMAL(10, 2),
    price_usd_foil DECIMAL(10, 2),
    price_eur DECIMAL(10, 2),
    price_tix DECIMAL(10, 2),
    image_uri VARCHAR(500),
    image_uri_small VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for cards table
CREATE INDEX IF NOT EXISTS idx_card_scryfall_id ON cards(scryfall_id);
CREATE INDEX IF NOT EXISTS idx_card_oracle_id ON cards(oracle_id);
CREATE INDEX IF NOT EXISTS idx_card_name ON cards(name);
CREATE INDEX IF NOT EXISTS idx_card_set_code ON cards(set_code);
CREATE INDEX IF NOT EXISTS idx_card_rarity ON cards(rarity);
CREATE INDEX IF NOT EXISTS idx_card_name_set ON cards(name, set_code);
CREATE INDEX IF NOT EXISTS idx_card_colors ON cards(colors);
CREATE INDEX IF NOT EXISTS idx_card_type ON cards(type_line);

-- ============================================================================
-- COLLECTION_ITEMS TABLE
-- ============================================================================
-- Stores individual card instances in user's collection
CREATE TABLE IF NOT EXISTS collection_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    is_foil BOOLEAN DEFAULT 0,
    condition VARCHAR(20) NOT NULL DEFAULT 'near_mint',
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    acquired_date TIMESTAMP,
    acquired_price DECIMAL(10, 2),
    location VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
    CHECK (quantity > 0)
);

-- Indexes for collection_items table
CREATE INDEX IF NOT EXISTS idx_collection_card_id ON collection_items(card_id);
CREATE INDEX IF NOT EXISTS idx_collection_card_foil ON collection_items(card_id, is_foil);

-- ============================================================================
-- DECKS TABLE
-- ============================================================================
-- Stores user's deck lists
CREATE TABLE IF NOT EXISTS decks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    format VARCHAR(50) NOT NULL,
    commander_id INTEGER,
    partner_commander_id INTEGER,
    description TEXT,
    archetype VARCHAR(100),
    color_identity VARCHAR(20),
    total_cards INTEGER DEFAULT 0,
    estimated_value DECIMAL(10, 2),
    is_active BOOLEAN DEFAULT 1,
    is_complete BOOLEAN DEFAULT 0,
    moxfield_url VARCHAR(500),
    archidekt_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (commander_id) REFERENCES cards(id) ON DELETE SET NULL,
    FOREIGN KEY (partner_commander_id) REFERENCES cards(id) ON DELETE SET NULL
);

-- Indexes for decks table
CREATE INDEX IF NOT EXISTS idx_deck_name ON decks(name);
CREATE INDEX IF NOT EXISTS idx_deck_format ON decks(format);
CREATE INDEX IF NOT EXISTS idx_deck_format_active ON decks(format, is_active);

-- ============================================================================
-- DECK_CARDS TABLE
-- ============================================================================
-- Many-to-many relationship between decks and cards
CREATE TABLE IF NOT EXISTS deck_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id INTEGER NOT NULL,
    card_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    category VARCHAR(50) NOT NULL DEFAULT 'mainboard',
    is_foil BOOLEAN DEFAULT 0,
    tags VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
    CHECK (quantity > 0),
    UNIQUE (deck_id, card_id, category)
);

-- Indexes for deck_cards table
CREATE INDEX IF NOT EXISTS idx_deck_card_deck_id ON deck_cards(deck_id);
CREATE INDEX IF NOT EXISTS idx_deck_card_card_id ON deck_cards(card_id);
CREATE INDEX IF NOT EXISTS idx_deck_card_category ON deck_cards(deck_id, category);

-- ============================================================================
-- PRICE_HISTORY TABLE
-- ============================================================================
-- Historical price tracking for cards
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    date TIMESTAMP NOT NULL,
    price_usd DECIMAL(10, 2),
    price_usd_foil DECIMAL(10, 2),
    price_eur DECIMAL(10, 2),
    price_tix DECIMAL(10, 2),
    source VARCHAR(50) NOT NULL DEFAULT 'scryfall',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
    UNIQUE (card_id, date, source)
);

-- Indexes for price_history table
CREATE INDEX IF NOT EXISTS idx_price_history_card_id ON price_history(card_id);
CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(date);

-- ============================================================================
-- TRADES TABLE
-- ============================================================================
-- Trade records (buying/selling/trading cards)
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_type VARCHAR(20) NOT NULL,
    partner_name VARCHAR(255),
    platform VARCHAR(100),
    total_value DECIMAL(10, 2) NOT NULL,
    shipping_cost DECIMAL(10, 2),
    cards_json TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    trade_date TIMESTAMP NOT NULL,
    completed_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for trades table
CREATE INDEX IF NOT EXISTS idx_trade_type ON trades(trade_type);
CREATE INDEX IF NOT EXISTS idx_trade_date_type ON trades(trade_date, trade_type);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update updated_at timestamp on cards table
CREATE TRIGGER IF NOT EXISTS update_cards_timestamp 
AFTER UPDATE ON cards
FOR EACH ROW
BEGIN
    UPDATE cards SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update updated_at timestamp on collection_items table
CREATE TRIGGER IF NOT EXISTS update_collection_items_timestamp 
AFTER UPDATE ON collection_items
FOR EACH ROW
BEGIN
    UPDATE collection_items SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update updated_at timestamp on decks table
CREATE TRIGGER IF NOT EXISTS update_decks_timestamp 
AFTER UPDATE ON decks
FOR EACH ROW
BEGIN
    UPDATE decks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update updated_at timestamp on trades table
CREATE TRIGGER IF NOT EXISTS update_trades_timestamp 
AFTER UPDATE ON trades
FOR EACH ROW
BEGIN
    UPDATE trades SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
