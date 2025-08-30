-- =====================================================
-- Entity Table: jockeys_entity
-- Database: results
-- Purpose: Indexed entity table for jockeys with auto-increment primary key
-- PostgreSQL Schema for Horse Racing AI v2.05
-- =====================================================

CREATE TABLE IF NOT EXISTS jockeys_entity (
    -- Primary key - auto-incrementing
    id SERIAL PRIMARY KEY,
    
    -- Original jockey ID from CSV data (unique constraint)
    jockey_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Jockey identification
    jockey_name VARCHAR(255) NOT NULL,
    allowance_claimed VARCHAR(10), -- e.g., '3lb', '5lb', '7lb'
    
    -- Performance metrics (will be updated from stats)
    total_races INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    win_percentage DECIMAL(5,2) DEFAULT 0.00,
    total_placed INTEGER DEFAULT 0,
    place_percentage DECIMAL(5,2) DEFAULT 0.00,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    CONSTRAINT chk_jockey_win_percentage CHECK (win_percentage >= 0 AND win_percentage <= 100),
    CONSTRAINT chk_jockey_place_percentage CHECK (place_percentage >= 0 AND place_percentage <= 100),
    CONSTRAINT chk_jockey_races_positive CHECK (total_races >= 0),
    CONSTRAINT chk_jockey_wins_valid CHECK (total_wins >= 0 AND total_wins <= total_races),
    CONSTRAINT chk_jockey_placed_valid CHECK (total_placed >= 0 AND total_placed <= total_races)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_jockeys_entity_jockey_id ON jockeys_entity(jockey_id);
CREATE INDEX IF NOT EXISTS idx_jockeys_entity_name ON jockeys_entity(jockey_name);
CREATE INDEX IF NOT EXISTS idx_jockeys_entity_allowance ON jockeys_entity(allowance_claimed);
CREATE INDEX IF NOT EXISTS idx_jockeys_entity_win_pct ON jockeys_entity(win_percentage);
CREATE INDEX IF NOT EXISTS idx_jockeys_entity_active ON jockeys_entity(is_active);

-- Create trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_jockeys_entity_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_jockeys_entity_updated_at
    BEFORE UPDATE ON jockeys_entity
    FOR EACH ROW
    EXECUTE FUNCTION update_jockeys_entity_updated_at();
