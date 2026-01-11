-- Migration 002: FTS5 Full-Text Search
-- Adds FTS5 virtual table and triggers for full-text search
-- Author: CardForge Team
-- Date: 2026-01-11

-- ============================================================================
-- FTS5 VIRTUAL TABLE
-- ============================================================================
-- Create FTS5 virtual table for full-text search on cards
-- Searches across name, type_line, and oracle_text
CREATE VIRTUAL TABLE IF NOT EXISTS cards_fts USING fts5(
    card_id UNINDEXED,
    name,
    type_line,
    oracle_text,
    content='cards',
    content_rowid='id'
);

-- ============================================================================
-- FTS5 SYNC TRIGGERS
-- ============================================================================
-- Keep FTS5 table in sync with cards table

-- Insert trigger
CREATE TRIGGER IF NOT EXISTS cards_fts_insert 
AFTER INSERT ON cards
BEGIN
    INSERT INTO cards_fts(card_id, name, type_line, oracle_text)
    VALUES (new.id, new.name, new.type_line, new.oracle_text);
END;

-- Update trigger
CREATE TRIGGER IF NOT EXISTS cards_fts_update 
AFTER UPDATE ON cards
BEGIN
    UPDATE cards_fts
    SET name = new.name,
        type_line = new.type_line,
        oracle_text = new.oracle_text
    WHERE card_id = new.id;
END;

-- Delete trigger
CREATE TRIGGER IF NOT EXISTS cards_fts_delete 
AFTER DELETE ON cards
BEGIN
    DELETE FROM cards_fts WHERE card_id = old.id;
END;
