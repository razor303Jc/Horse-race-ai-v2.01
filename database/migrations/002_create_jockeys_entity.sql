-- 002: Create Jockeys Entity Table
-- Purpose: Store unique jockey entities with auto-increment keys
-- Date: August 30, 2025

-- Create jockeys entity table
CREATE TABLE IF NOT EXISTS jockeys_entity (
    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_id INTEGER NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_jockeys_original_id ON jockeys_entity(original_id);
CREATE INDEX IF NOT EXISTS idx_jockeys_name ON jockeys_entity(name);

-- Create trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS jockeys_entity_updated_at 
    AFTER UPDATE ON jockeys_entity
    FOR EACH ROW 
BEGIN
    UPDATE jockeys_entity SET updated_at = CURRENT_TIMESTAMP WHERE entity_id = NEW.entity_id;
END;
