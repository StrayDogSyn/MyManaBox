-- ============================================================================
-- CARDFORGE DATABASE SCHEMA v2.0
-- Magic: The Gathering Collection Management System
-- ============================================================================
-- SQLite with FTS5 full-text search
-- ============================================================================

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- ============================================================================
-- REFERENCE DATA: Sets
-- ============================================================================

CREATE TABLE IF NOT EXISTS sets (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    release_date DATE,
    set_type TEXT,  -- 'expansion', 'commander', 'core', 'masters', etc.
    card_count INTEGER,
    icon_svg_uri TEXT,
    scryfall_uri TEXT,
    is_digital BOOLEAN DEFAULT FALSE,
    is_foil_only BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sets_release ON sets(release_date);
CREATE INDEX IF NOT EXISTS idx_sets_type ON sets(set_type);

-- ============================================================================
-- CARD DATA (Scryfall normalized)
-- ============================================================================

CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scryfall_id TEXT UNIQUE NOT NULL,
    oracle_id TEXT,
    name TEXT NOT NULL,
    set_code TEXT REFERENCES sets(code),
    collector_number TEXT,
    rarity TEXT,  -- 'common', 'uncommon', 'rare', 'mythic', 'special', 'bonus'
    
    -- Colors & Identity (stored as JSON arrays)
    colors TEXT,           -- '["W", "U"]' or '[]'
    color_identity TEXT,   -- '["W", "U", "B"]'
    
    -- Mana & CMC
    mana_cost TEXT,        -- '{2}{W}{U}'
    cmc REAL,              -- Converted mana cost
    
    -- Type information
    type_line TEXT,        -- 'Legendary Creature — Human Wizard'
    oracle_text TEXT,
    
    -- Stats (nullable for non-creatures)
    power TEXT,
    toughness TEXT,
    loyalty TEXT,
    defense TEXT,
    
    -- Card structure
    layout TEXT,           -- 'normal', 'split', 'flip', 'transform', 'mdfc', etc.
    
    -- URIs & Images (JSON)
    image_uris TEXT,       -- JSON object with 'small', 'normal', 'large', etc.
    
    -- Pricing (JSON, updated regularly)
    prices_json TEXT,      -- Current Scryfall prices
    
    -- Legalities (JSON)
    legalities_json TEXT,  -- {'standard': 'legal', 'commander': 'legal', ...}
    
    -- Keywords & Mechanics
    keywords TEXT,         -- JSON array: '["Flying", "Vigilance"]'
    produced_mana TEXT,    -- JSON array for mana dorks/lands
    
    -- Rankings
    edhrec_rank INTEGER,
    penny_rank INTEGER,
    
    -- Metadata
    reserved BOOLEAN DEFAULT FALSE,
    reprint BOOLEAN DEFAULT FALSE,
    digital BOOLEAN DEFAULT FALSE,
    promo BOOLEAN DEFAULT FALSE,
    full_art BOOLEAN DEFAULT FALSE,
    textless BOOLEAN DEFAULT FALSE,
    
    -- External IDs
    tcgplayer_id INTEGER,
    cardmarket_id INTEGER,
    mtgo_id INTEGER,
    arena_id INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name);
CREATE INDEX IF NOT EXISTS idx_cards_set ON cards(set_code);
CREATE INDEX IF NOT EXISTS idx_cards_oracle ON cards(oracle_id);
CREATE INDEX IF NOT EXISTS idx_cards_cmc ON cards(cmc);
CREATE INDEX IF NOT EXISTS idx_cards_rarity ON cards(rarity);
CREATE INDEX IF NOT EXISTS idx_cards_edhrec ON cards(edhrec_rank);
CREATE INDEX IF NOT EXISTS idx_cards_type ON cards(type_line);
CREATE INDEX IF NOT EXISTS idx_cards_tcgplayer ON cards(tcgplayer_id);

-- ============================================================================
-- FULL-TEXT SEARCH (FTS5)
-- ============================================================================

CREATE VIRTUAL TABLE IF NOT EXISTS cards_fts USING fts5(
    name,
    type_line,
    oracle_text,
    keywords,
    content='cards',
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS cards_fts_insert AFTER INSERT ON cards BEGIN
    INSERT INTO cards_fts(rowid, name, type_line, oracle_text, keywords) 
    VALUES (new.id, new.name, new.type_line, new.oracle_text, new.keywords);
END;

CREATE TRIGGER IF NOT EXISTS cards_fts_delete AFTER DELETE ON cards BEGIN
    INSERT INTO cards_fts(cards_fts, rowid, name, type_line, oracle_text, keywords) 
    VALUES ('delete', old.id, old.name, old.type_line, old.oracle_text, old.keywords);
END;

CREATE TRIGGER IF NOT EXISTS cards_fts_update AFTER UPDATE ON cards BEGIN
    INSERT INTO cards_fts(cards_fts, rowid, name, type_line, oracle_text, keywords) 
    VALUES ('delete', old.id, old.name, old.type_line, old.oracle_text, old.keywords);
    INSERT INTO cards_fts(rowid, name, type_line, oracle_text, keywords) 
    VALUES (new.id, new.name, new.type_line, new.oracle_text, new.keywords);
END;

-- ============================================================================
-- MULTI-FACE CARDS (Transform, MDFC, Split, etc.)
-- ============================================================================

CREATE TABLE IF NOT EXISTS card_faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER REFERENCES cards(id) ON DELETE CASCADE,
    face_index INTEGER NOT NULL,  -- 0 = front, 1 = back
    name TEXT NOT NULL,
    mana_cost TEXT,
    type_line TEXT,
    oracle_text TEXT,
    power TEXT,
    toughness TEXT,
    loyalty TEXT,
    defense TEXT,
    colors TEXT,
    image_uri TEXT,
    UNIQUE(card_id, face_index)
);

CREATE INDEX IF NOT EXISTS idx_card_faces_card ON card_faces(card_id);

-- ============================================================================
-- PRICE HISTORY (Multi-source tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER REFERENCES cards(id) ON DELETE CASCADE,
    source TEXT NOT NULL,          -- 'scryfall', 'tcgplayer', 'cardkingdom', 'cardmarket'
    price_usd REAL,
    price_usd_foil REAL,
    price_usd_etched REAL,
    price_eur REAL,
    price_eur_foil REAL,
    price_tix REAL,                -- MTGO tickets
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_price_history_card ON price_history(card_id);
CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(recorded_at);
CREATE INDEX IF NOT EXISTS idx_price_history_source ON price_history(source);

-- ============================================================================
-- COLLECTIONS (User's card inventory)
-- ============================================================================

CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS collection_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER REFERENCES collections(id) ON DELETE CASCADE,
    card_id INTEGER REFERENCES cards(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    foil TEXT DEFAULT 'normal',     -- 'normal', 'foil', 'etched'
    condition TEXT DEFAULT 'NM',    -- 'NM', 'LP', 'MP', 'HP', 'DMG'
    language TEXT DEFAULT 'en',
    
    -- Acquisition tracking
    purchase_price REAL,
    purchase_date DATE,
    purchase_source TEXT,           -- 'tcgplayer', 'cardkingdom', 'lgs', 'trade', etc.
    
    -- External IDs for sync
    manabox_id TEXT,
    moxfield_id TEXT,
    
    -- User notes & location
    notes TEXT,
    location TEXT,                  -- 'binder-1', 'deck-box-red', etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(collection_id, card_id, foil, condition, language)
);

CREATE INDEX IF NOT EXISTS idx_collection_cards_collection ON collection_cards(collection_id);
CREATE INDEX IF NOT EXISTS idx_collection_cards_card ON collection_cards(card_id);
CREATE INDEX IF NOT EXISTS idx_collection_cards_foil ON collection_cards(foil);
CREATE INDEX IF NOT EXISTS idx_collection_cards_manabox ON collection_cards(manabox_id);

-- ============================================================================
-- DECKS (Deck management with format tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS decks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    format TEXT NOT NULL,           -- 'commander', 'standard', 'modern', 'legacy', etc.
    commander_id INTEGER REFERENCES cards(id),
    partner_id INTEGER REFERENCES cards(id),  -- For partner commanders
    colors TEXT,                    -- Color identity JSON array
    description TEXT,
    
    -- External platform IDs
    moxfield_id TEXT UNIQUE,
    archidekt_id TEXT,
    manabox_deck_id TEXT,
    
    -- Deck metadata
    is_active BOOLEAN DEFAULT TRUE,
    power_level INTEGER,            -- 1-10 scale
    budget_target REAL,
    current_value REAL,             -- Calculated from card prices
    
    -- Performance tracking
    win_rate REAL,
    games_played INTEGER DEFAULT 0,
    games_won INTEGER DEFAULT 0,
    last_played DATE,
    
    -- Tags for organization
    tags TEXT,                      -- JSON array: '["competitive", "voltron"]'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_decks_format ON decks(format);
CREATE INDEX IF NOT EXISTS idx_decks_commander ON decks(commander_id);
CREATE INDEX IF NOT EXISTS idx_decks_active ON decks(is_active);
CREATE INDEX IF NOT EXISTS idx_decks_moxfield ON decks(moxfield_id);

CREATE TABLE IF NOT EXISTS deck_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE,
    card_id INTEGER REFERENCES cards(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    
    -- Card role in deck
    is_commander BOOLEAN DEFAULT FALSE,
    is_sideboard BOOLEAN DEFAULT FALSE,
    is_maybeboard BOOLEAN DEFAULT FALSE,
    
    -- Categorization for deck analysis
    category TEXT,                  -- 'ramp', 'removal', 'protection', 'finisher', etc.
    
    -- Ownership tracking (links to collection)
    owned_quantity INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(deck_id, card_id, is_sideboard, is_maybeboard)
);

CREATE INDEX IF NOT EXISTS idx_deck_cards_deck ON deck_cards(deck_id);
CREATE INDEX IF NOT EXISTS idx_deck_cards_card ON deck_cards(card_id);
CREATE INDEX IF NOT EXISTS idx_deck_cards_category ON deck_cards(category);

-- ============================================================================
-- BUY LIST (Cards to acquire)
-- ============================================================================

CREATE TABLE IF NOT EXISTS buy_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER REFERENCES cards(id) ON DELETE CASCADE,
    deck_id INTEGER REFERENCES decks(id) ON DELETE SET NULL,
    
    -- Priority & targeting
    priority INTEGER DEFAULT 3,      -- 1=urgent, 2=high, 3=medium, 4=low, 5=someday
    quantity_needed INTEGER DEFAULT 1,
    max_price REAL,                  -- Won't suggest purchases above this
    preferred_condition TEXT DEFAULT 'NM',
    accept_foil BOOLEAN DEFAULT TRUE,
    
    -- Best deal tracking (updated by price service)
    best_price REAL,
    best_source TEXT,
    best_url TEXT,
    price_last_checked TIMESTAMP,
    
    -- Status tracking
    status TEXT DEFAULT 'wanted',    -- 'wanted', 'ordered', 'shipped', 'received', 'cancelled'
    
    -- Acquisition
    purchased_price REAL,
    purchased_source TEXT,
    purchased_at TIMESTAMP,
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_buy_list_priority ON buy_list(priority);
CREATE INDEX IF NOT EXISTS idx_buy_list_status ON buy_list(status);
CREATE INDEX IF NOT EXISTS idx_buy_list_deck ON buy_list(deck_id);

-- ============================================================================
-- SELL LIST (Cards to offload)
-- ============================================================================

CREATE TABLE IF NOT EXISTS sell_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_card_id INTEGER REFERENCES collection_cards(id) ON DELETE CASCADE,
    
    -- Selling parameters
    reason TEXT,                     -- 'duplicate', 'not_needed', 'upgrade', 'cash_out'
    quantity_to_sell INTEGER DEFAULT 1,
    min_price REAL,                  -- Won't sell below this
    
    -- Best buylist tracking
    best_buylist_price REAL,
    best_buylist_source TEXT,
    best_tcgplayer_price REAL,       -- TCGPlayer market for comparison
    price_last_checked TIMESTAMP,
    
    -- Listing status
    status TEXT DEFAULT 'considering', -- 'considering', 'listed', 'sold', 'removed'
    listed_platform TEXT,            -- 'tcgplayer', 'cardsphere', 'facebook', etc.
    listed_price REAL,
    listed_at TIMESTAMP,
    
    -- Sale completion
    sold_price REAL,
    sold_to TEXT,
    sold_at TIMESTAMP,
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sell_list_status ON sell_list(status);
CREATE INDEX IF NOT EXISTS idx_sell_list_reason ON sell_list(reason);

-- ============================================================================
-- GAME HISTORY (Performance tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS game_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Game outcome
    result TEXT,                     -- 'win', 'loss', 'draw', 'scoop'
    position INTEGER,                -- 1st, 2nd, 3rd, 4th in multiplayer
    total_players INTEGER DEFAULT 4,
    
    -- Game metrics
    turn_count INTEGER,
    commander_cast_count INTEGER,
    elimination_turn INTEGER,        -- Turn eliminated (if loss)
    
    -- Win condition
    win_condition TEXT,              -- 'combat', 'combo', 'commander_damage', etc.
    key_cards TEXT,                  -- JSON array of pivotal cards
    
    -- Opponent info
    opponents TEXT,                  -- JSON array of opponent deck/commander names
    
    -- Notes
    notes TEXT,
    
    -- Location/event
    event_name TEXT,
    location TEXT
);

CREATE INDEX IF NOT EXISTS idx_game_history_deck ON game_history(deck_id);
CREATE INDEX IF NOT EXISTS idx_game_history_date ON game_history(played_at);
CREATE INDEX IF NOT EXISTS idx_game_history_result ON game_history(result);

-- ============================================================================
-- SYNC STATE (External platform sync tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS sync_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,          -- 'manabox', 'moxfield', 'archidekt', 'google_drive'
    entity_type TEXT NOT NULL,       -- 'collection', 'deck', 'backup'
    entity_id INTEGER,
    external_id TEXT,
    last_sync TIMESTAMP,
    sync_hash TEXT,                  -- Hash of data for change detection
    status TEXT DEFAULT 'synced',    -- 'synced', 'pending', 'conflict', 'error'
    error_message TEXT,
    UNIQUE(platform, entity_type, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_sync_state_platform ON sync_state(platform);
CREATE INDEX IF NOT EXISTS idx_sync_state_status ON sync_state(status);

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Insert initial version
INSERT OR IGNORE INTO schema_version (version, description) 
VALUES (1, 'Initial CardForge schema v2.0');

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Collection value by card
CREATE VIEW IF NOT EXISTS v_collection_value AS
SELECT 
    cc.id,
    c.name,
    c.set_code,
    s.name as set_name,
    cc.quantity,
    cc.foil,
    cc.condition,
    cc.purchase_price,
    CASE 
        WHEN cc.foil = 'foil' THEN json_extract(c.prices_json, '$.usd_foil')
        WHEN cc.foil = 'etched' THEN json_extract(c.prices_json, '$.usd_etched')
        ELSE json_extract(c.prices_json, '$.usd')
    END as current_price,
    cc.quantity * CASE 
        WHEN cc.foil = 'foil' THEN COALESCE(json_extract(c.prices_json, '$.usd_foil'), 0)
        WHEN cc.foil = 'etched' THEN COALESCE(json_extract(c.prices_json, '$.usd_etched'), 0)
        ELSE COALESCE(json_extract(c.prices_json, '$.usd'), 0)
    END as total_value
FROM collection_cards cc
JOIN cards c ON cc.card_id = c.id
LEFT JOIN sets s ON c.set_code = s.code;

-- Duplicate cards in collection (candidates for sell list)
CREATE VIEW IF NOT EXISTS v_duplicates AS
SELECT 
    c.oracle_id,
    c.name,
    SUM(cc.quantity) as total_copies,
    GROUP_CONCAT(DISTINCT c.set_code) as printings,
    MAX(json_extract(c.prices_json, '$.usd')) as highest_price
FROM collection_cards cc
JOIN cards c ON cc.card_id = c.id
JOIN collections col ON cc.collection_id = col.id
GROUP BY c.oracle_id
HAVING SUM(cc.quantity) > 1
ORDER BY total_copies DESC;

-- Deck completion status
CREATE VIEW IF NOT EXISTS v_deck_completion AS
SELECT 
    d.id as deck_id,
    d.name as deck_name,
    d.format,
    d.commander_id,
    (SELECT name FROM cards WHERE id = d.commander_id) as commander_name,
    COUNT(dc.id) as total_unique_cards,
    SUM(dc.quantity) as total_card_slots,
    SUM(dc.owned_quantity) as owned_cards,
    SUM(dc.quantity) - SUM(dc.owned_quantity) as missing_cards,
    ROUND(100.0 * SUM(CASE WHEN dc.owned_quantity >= dc.quantity THEN dc.quantity ELSE dc.owned_quantity END) / SUM(dc.quantity), 1) as completion_pct,
    d.current_value
FROM decks d
LEFT JOIN deck_cards dc ON d.id = dc.deck_id AND dc.is_maybeboard = FALSE
GROUP BY d.id;

-- Buy list with current prices
CREATE VIEW IF NOT EXISTS v_buy_list_prices AS
SELECT 
    bl.id,
    bl.priority,
    bl.quantity_needed,
    bl.status,
    c.name as card_name,
    c.set_code,
    json_extract(c.prices_json, '$.usd') as scryfall_price,
    bl.best_price,
    bl.best_source,
    bl.best_url,
    bl.max_price,
    d.name as for_deck,
    bl.created_at
FROM buy_list bl
JOIN cards c ON bl.card_id = c.id
LEFT JOIN decks d ON bl.deck_id = d.id
WHERE bl.status = 'wanted'
ORDER BY bl.priority, bl.best_price;

-- Collection summary statistics
CREATE VIEW IF NOT EXISTS v_collection_stats AS
SELECT
    col.id as collection_id,
    col.name as collection_name,
    COUNT(DISTINCT cc.card_id) as unique_cards,
    SUM(cc.quantity) as total_cards,
    SUM(cc.quantity * COALESCE(json_extract(c.prices_json, '$.usd'), 0)) as total_value,
    AVG(COALESCE(json_extract(c.prices_json, '$.usd'), 0)) as avg_card_value,
    SUM(CASE WHEN cc.foil != 'normal' THEN cc.quantity ELSE 0 END) as foil_count,
    COUNT(DISTINCT c.set_code) as unique_sets
FROM collections col
LEFT JOIN collection_cards cc ON col.id = cc.collection_id
LEFT JOIN cards c ON cc.card_id = c.id
GROUP BY col.id;
