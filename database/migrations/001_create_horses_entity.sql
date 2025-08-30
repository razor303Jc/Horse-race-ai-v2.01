-- 001: Create Horses Entity Table
-- Purpose: Store unique horse entities with auto-increment keys
-- Date: August 30, 2025

-- Create horses entity table
CREATE TABLE IF NOT EXISTS horses_entity (
    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_id INTEGER NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(10),
    age INTEGER,
    color VARCHAR(50),
    owner VARCHAR(255),
    sire VARCHAR(255),
    dam VARCHAR(255),
    dam_sire VARCHAR(255),
    sex VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_horses_original_id ON horses_entity(original_id);
CREATE INDEX IF NOT EXISTS idx_horses_name ON horses_entity(name);
CREATE INDEX IF NOT EXISTS idx_horses_owner ON horses_entity(owner);
CREATE INDEX IF NOT EXISTS idx_horses_sire ON horses_entity(sire);
CREATE INDEX IF NOT EXISTS idx_horses_country ON horses_entity(country);

-- Create trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS horses_entity_updated_at 
    AFTER UPDATE ON horses_entity
    FOR EACH ROW 
BEGIN
    UPDATE horses_entity SET updated_at = CURRENT_TIMESTAMP WHERE entity_id = NEW.entity_id;
END;
