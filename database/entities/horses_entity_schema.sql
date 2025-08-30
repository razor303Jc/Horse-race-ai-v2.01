-- Horses Entity Table Schema
-- ===========================
-- Creates entity table for unique horses across all databases
-- PostgreSQL compatible schema

-- For Results Database
-- ====================

-- Table: horses
-- Purpose: Centralized horse entity with unique CSV horse_id mapping
-- Usage: Referenced by race results, performance tracking, etc.

CREATE TABLE IF NOT EXISTS horses (
    -- Primary key (auto-increment)
    id SERIAL PRIMARY KEY,
    
    -- CSV data mapping
    horse_id INTEGER UNIQUE NOT NULL,        -- Original CSV horse_id
    name VARCHAR(255) NOT NULL,              -- Horse name from CSV
    
    -- Physical attributes
    age INTEGER,                             -- Horse age
    weight_carried VARCHAR(20),              -- Weight carried in races
    color VARCHAR(50),                       -- Horse color/markings
    sex VARCHAR(10),                         -- Horse sex (G/C/F/etc.)
    
    -- Racing attributes  
    draw_position INTEGER,                   -- Typical draw position
    last_ran DATE,                          -- Date of last race
    
    -- Relationships (will be foreign keys)
    jockey_id INTEGER,                       -- Links to jockeys table
    trainer_id INTEGER,                      -- Links to trainers table
    
    -- Performance data
    total_runs INTEGER DEFAULT 0,           -- Total career runs
    total_wins INTEGER DEFAULT 0,           -- Total career wins
    total_places INTEGER DEFAULT 0,         -- Total career places
    win_percentage DECIMAL(5,2) DEFAULT 0.00, -- Career win percentage
    prize_money_total DECIMAL(15,2) DEFAULT 0.00, -- Total prize money
    
    -- Current form
    recent_form VARCHAR(20),                 -- Recent form (e.g., "112F3")
    current_rating INTEGER,                  -- Current official rating
    best_rating INTEGER,                     -- Best official rating
    
    -- Betting data
    last_odds VARCHAR(50),                   -- Last recorded odds
    average_odds DECIMAL(8,2),              -- Average career odds
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_race_update TIMESTAMP,             -- Last time race data was updated
    
    -- Data source tracking
    source_file VARCHAR(255),               -- Original CSV file
    import_batch_id VARCHAR(100)            -- Batch ID for tracking imports
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_horses_horse_id ON horses(horse_id);
CREATE INDEX IF NOT EXISTS idx_horses_name ON horses(name);
CREATE INDEX IF NOT EXISTS idx_horses_jockey_id ON horses(jockey_id);
CREATE INDEX IF NOT EXISTS idx_horses_trainer_id ON horses(trainer_id);
CREATE INDEX IF NOT EXISTS idx_horses_last_ran ON horses(last_ran);
CREATE INDEX IF NOT EXISTS idx_horses_win_percentage ON horses(win_percentage);
CREATE INDEX IF NOT EXISTS idx_horses_current_rating ON horses(current_rating);
CREATE INDEX IF NOT EXISTS idx_horses_updated_at ON horses(updated_at);

-- Constraints
ALTER TABLE horses ADD CONSTRAINT chk_horses_age CHECK (age >= 2 AND age <= 20);
ALTER TABLE horses ADD CONSTRAINT chk_horses_win_percentage CHECK (win_percentage >= 0 AND win_percentage <= 100);
ALTER TABLE horses ADD CONSTRAINT chk_horses_ratings CHECK (current_rating >= 0 AND best_rating >= 0);
ALTER TABLE horses ADD CONSTRAINT chk_horses_counts CHECK (total_runs >= 0 AND total_wins >= 0 AND total_places >= 0);
ALTER TABLE horses ADD CONSTRAINT chk_horses_wins_vs_runs CHECK (total_wins <= total_runs);
ALTER TABLE horses ADD CONSTRAINT chk_horses_places_vs_runs CHECK (total_places <= total_runs);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_horses_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_horses_updated_at
    BEFORE UPDATE ON horses
    FOR EACH ROW
    EXECUTE FUNCTION update_horses_updated_at();

-- Comments for documentation
COMMENT ON TABLE horses IS 'Central entity table for unique horses with CSV ID mapping';
COMMENT ON COLUMN horses.id IS 'Auto-increment primary key for internal references';
COMMENT ON COLUMN horses.horse_id IS 'Unique horse ID from CSV files - used for data mapping';
COMMENT ON COLUMN horses.name IS 'Horse name as it appears in racing data';
COMMENT ON COLUMN horses.jockey_id IS 'Most recent or primary jockey (foreign key to jockeys table)';
COMMENT ON COLUMN horses.trainer_id IS 'Current trainer (foreign key to trainers table)';
COMMENT ON COLUMN horses.win_percentage IS 'Career win percentage calculated from total_wins/total_runs';
COMMENT ON COLUMN horses.recent_form IS 'Recent race form string (e.g., "112F3" for recent placements)';
COMMENT ON COLUMN horses.import_batch_id IS 'Tracking ID for data import batch for audit purposes';

-- Example usage queries:
/*
-- Find horse by CSV horse_id
SELECT * FROM horses WHERE horse_id = 1234567;

-- Get horse with trainer and jockey info (once FK relationships are added)
SELECT h.name, h.horse_id, h.age, h.win_percentage 
FROM horses h 
WHERE h.horse_id = 1234567;

-- Find horses by trainer
SELECT * FROM horses WHERE trainer_id = 1234;

-- Find horses by win percentage
SELECT name, horse_id, win_percentage, total_runs 
FROM horses 
WHERE win_percentage > 20.00 
ORDER BY win_percentage DESC;

-- Recent form analysis
SELECT name, horse_id, recent_form, last_ran, current_rating
FROM horses 
WHERE last_ran >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY last_ran DESC;
*/
