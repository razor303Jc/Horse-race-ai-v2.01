-- 003: Create Trainers Entity Table
-- Purpose: Store unique trainer entities with auto-increment keys
-- Date: August 30, 2025

-- Create trainers entity table
CREATE TABLE IF NOT EXISTS trainers_entity (
    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_id INTEGER NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_trainers_original_id ON trainers_entity(original_id);
CREATE INDEX IF NOT EXISTS idx_trainers_name ON trainers_entity(name);

-- Create trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS trainers_entity_updated_at 
    AFTER UPDATE ON trainers_entity
    FOR EACH ROW 
BEGIN
    UPDATE trainers_entity SET updated_at = CURRENT_TIMESTAMP WHERE entity_id = NEW.entity_id;
END;
