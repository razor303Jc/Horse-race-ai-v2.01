-- Jockeys Entity Table Schema
-- ============================
-- Creates entity table for unique jockeys across all databases
-- PostgreSQL compatible schema

-- For Results Database
-- ====================

-- Table: jockeys
-- Purpose: Centralized jockey entity with unique CSV jockey_id mapping
-- Usage: Referenced by horses, race results, performance tracking, etc.

CREATE TABLE IF NOT EXISTS jockeys (
    -- Primary key (auto-increment)
    id SERIAL PRIMARY KEY,
    
    -- CSV data mapping
    jockey_id INTEGER UNIQUE NOT NULL,       -- Original CSV jockey_id
    name VARCHAR(255) NOT NULL,              -- Jockey name from CSV
    
    -- Personal attributes
    age INTEGER,                             -- Jockey age
    weight_allowance DECIMAL(4,1),          -- Weight allowance (e.g., 7.0 lbs)
    claim_allowance VARCHAR(20),            -- Claiming allowance description
    apprentice BOOLEAN DEFAULT FALSE,        -- Is apprentice jockey
    
    -- Career statistics
    total_runs INTEGER DEFAULT 0,           -- Total career runs
    total_wins INTEGER DEFAULT 0,           -- Total career wins
    total_places INTEGER DEFAULT 0,         -- Total career places (2nd/3rd)
    total_shows INTEGER DEFAULT 0,          -- Total career shows (1st/2nd/3rd)
    
    -- Performance metrics
    win_percentage DECIMAL(5,2) DEFAULT 0.00,    -- Career win percentage
    place_percentage DECIMAL(5,2) DEFAULT 0.00,  -- Career place percentage
    show_percentage DECIMAL(5,2) DEFAULT 0.00,   -- Career show percentage
    
    -- Financial data
    prize_money_total DECIMAL(15,2) DEFAULT 0.00, -- Total career prize money
    prize_money_year DECIMAL(15,2) DEFAULT 0.00,  -- Current year prize money
    
    -- Current form and ratings
    current_form VARCHAR(20),               -- Recent form string
    current_rating INTEGER,                 -- Current performance rating
    best_rating INTEGER,                    -- Best career rating
    strike_rate DECIMAL(5,2),              -- Recent strike rate
    
    -- Specializations
    preferred_distance VARCHAR(50),         -- Preferred race distance
    preferred_surface VARCHAR(50),          -- Preferred track surface
    preferred_class VARCHAR(50),            -- Preferred race class
    
    -- Activity tracking
    races_this_year INTEGER DEFAULT 0,      -- Races ridden this year
    wins_this_year INTEGER DEFAULT 0,       -- Wins this year
    last_race_date DATE,                    -- Date of last race
    last_win_date DATE,                     -- Date of last win
    
    -- Geographic data
    based_location VARCHAR(255),            -- Primary location/stable
    license_type VARCHAR(50),               -- License type/category
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_race_update TIMESTAMP,             -- Last time race data was updated
    
    -- Data source tracking
    source_file VARCHAR(255),               -- Original CSV file
    import_batch_id VARCHAR(100),           -- Batch ID for tracking imports
    
    -- Status
    active BOOLEAN DEFAULT TRUE,            -- Currently active jockey
    retired_date DATE                       -- Retirement date if applicable
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_jockeys_jockey_id ON jockeys(jockey_id);
CREATE INDEX IF NOT EXISTS idx_jockeys_name ON jockeys(name);
CREATE INDEX IF NOT EXISTS idx_jockeys_win_percentage ON jockeys(win_percentage);
CREATE INDEX IF NOT EXISTS idx_jockeys_prize_money ON jockeys(prize_money_total);
CREATE INDEX IF NOT EXISTS idx_jockeys_last_race_date ON jockeys(last_race_date);
CREATE INDEX IF NOT EXISTS idx_jockeys_based_location ON jockeys(based_location);
CREATE INDEX IF NOT EXISTS idx_jockeys_active ON jockeys(active);
CREATE INDEX IF NOT EXISTS idx_jockeys_current_rating ON jockeys(current_rating);
CREATE INDEX IF NOT EXISTS idx_jockeys_updated_at ON jockeys(updated_at);

-- Constraints
ALTER TABLE jockeys ADD CONSTRAINT chk_jockeys_age CHECK (age >= 16 AND age <= 80);
ALTER TABLE jockeys ADD CONSTRAINT chk_jockeys_percentages CHECK (
    win_percentage >= 0 AND win_percentage <= 100 AND
    place_percentage >= 0 AND place_percentage <= 100 AND
    show_percentage >= 0 AND show_percentage <= 100
);
ALTER TABLE jockeys ADD CONSTRAINT chk_jockeys_ratings CHECK (current_rating >= 0 AND best_rating >= 0);
ALTER TABLE jockeys ADD CONSTRAINT chk_jockeys_counts CHECK (
    total_runs >= 0 AND total_wins >= 0 AND total_places >= 0 AND total_shows >= 0
);
ALTER TABLE jockeys ADD CONSTRAINT chk_jockeys_wins_vs_runs CHECK (total_wins <= total_runs);
ALTER TABLE jockeys ADD CONSTRAINT chk_jockeys_places_vs_runs CHECK (total_places <= total_runs);
ALTER TABLE jockeys ADD CONSTRAINT chk_jockeys_shows_vs_runs CHECK (total_shows <= total_runs);
ALTER TABLE jockeys ADD CONSTRAINT chk_jockeys_year_counts CHECK (
    races_this_year >= 0 AND wins_this_year >= 0 AND wins_this_year <= races_this_year
);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_jockeys_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_jockeys_updated_at
    BEFORE UPDATE ON jockeys
    FOR EACH ROW
    EXECUTE FUNCTION update_jockeys_updated_at();

-- Trigger to calculate percentages automatically
CREATE OR REPLACE FUNCTION calculate_jockey_percentages()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate win percentage
    IF NEW.total_runs > 0 THEN
        NEW.win_percentage = ROUND((NEW.total_wins::DECIMAL / NEW.total_runs::DECIMAL) * 100, 2);
        NEW.place_percentage = ROUND((NEW.total_places::DECIMAL / NEW.total_runs::DECIMAL) * 100, 2);
        NEW.show_percentage = ROUND((NEW.total_shows::DECIMAL / NEW.total_runs::DECIMAL) * 100, 2);
    ELSE
        NEW.win_percentage = 0;
        NEW.place_percentage = 0;
        NEW.show_percentage = 0;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_jockeys_calculate_percentages
    BEFORE INSERT OR UPDATE OF total_runs, total_wins, total_places, total_shows ON jockeys
    FOR EACH ROW
    EXECUTE FUNCTION calculate_jockey_percentages();

-- Comments for documentation
COMMENT ON TABLE jockeys IS 'Central entity table for unique jockeys with CSV ID mapping';
COMMENT ON COLUMN jockeys.id IS 'Auto-increment primary key for internal references';
COMMENT ON COLUMN jockeys.jockey_id IS 'Unique jockey ID from CSV files - used for data mapping';
COMMENT ON COLUMN jockeys.name IS 'Jockey name as it appears in racing data';
COMMENT ON COLUMN jockeys.claim_allowance IS 'Weight allowance description from CSV';
COMMENT ON COLUMN jockeys.win_percentage IS 'Career win percentage (auto-calculated)';
COMMENT ON COLUMN jockeys.strike_rate IS 'Recent performance strike rate';
COMMENT ON COLUMN jockeys.preferred_distance IS 'Distance category where jockey performs best';
COMMENT ON COLUMN jockeys.import_batch_id IS 'Tracking ID for data import batch for audit purposes';

-- Example usage queries:
/*
-- Find jockey by CSV jockey_id
SELECT * FROM jockeys WHERE jockey_id = 12345;

-- Top performing jockeys by win percentage
SELECT name, jockey_id, win_percentage, total_wins, total_runs, prize_money_total
FROM jockeys 
WHERE total_runs >= 50  -- Only jockeys with significant experience
ORDER BY win_percentage DESC
LIMIT 20;

-- Jockeys with recent activity
SELECT name, jockey_id, last_race_date, races_this_year, wins_this_year,
       ROUND((wins_this_year::DECIMAL / NULLIF(races_this_year, 0)::DECIMAL) * 100, 2) as year_win_pct
FROM jockeys 
WHERE last_race_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY last_race_date DESC;

-- Prize money leaders
SELECT name, jockey_id, prize_money_total, prize_money_year, win_percentage
FROM jockeys 
ORDER BY prize_money_total DESC
LIMIT 20;

-- Find apprentice jockeys
SELECT name, jockey_id, age, claim_allowance, apprentice, win_percentage
FROM jockeys 
WHERE apprentice = TRUE OR claim_allowance IS NOT NULL
ORDER BY win_percentage DESC;

-- Jockeys by location
SELECT based_location, COUNT(*) as jockey_count, 
       AVG(win_percentage) as avg_win_pct,
       SUM(prize_money_total) as total_prize_money
FROM jockeys 
WHERE active = TRUE
GROUP BY based_location
ORDER BY jockey_count DESC;
*/
