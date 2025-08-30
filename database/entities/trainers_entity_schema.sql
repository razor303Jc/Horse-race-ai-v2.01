-- Trainers Entity Table Schema
-- =============================
-- Creates entity table for unique trainers across all databases
-- PostgreSQL compatible schema

-- For Results Database
-- ====================

-- Table: trainers
-- Purpose: Centralized trainer entity with unique CSV trainer_id mapping
-- Usage: Referenced by horses, performance tracking, stable management, etc.

CREATE TABLE IF NOT EXISTS trainers (
    -- Primary key (auto-increment)
    id SERIAL PRIMARY KEY,
    
    -- CSV data mapping
    trainer_id INTEGER UNIQUE NOT NULL,      -- Original CSV trainer_id
    name VARCHAR(255) NOT NULL,              -- Trainer name from CSV
    
    -- Personal/Business attributes
    license_number VARCHAR(50),              -- Official trainer license number
    license_type VARCHAR(50),                -- License category/type
    years_training INTEGER,                  -- Years in training business
    
    -- Stable information
    stable_name VARCHAR(255),                -- Official stable name
    stable_location VARCHAR(255),            -- Primary stable location
    stable_capacity INTEGER,                 -- Maximum horses in stable
    current_horse_count INTEGER DEFAULT 0,   -- Current number of horses
    
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
    average_purse DECIMAL(10,2),             -- Average purse per race
    
    -- Current form and ratings
    current_form VARCHAR(20),               -- Recent form string
    current_rating INTEGER,                 -- Current performance rating
    best_rating INTEGER,                    -- Best career rating
    strike_rate DECIMAL(5,2),              -- Recent strike rate
    
    -- Specializations
    preferred_distance VARCHAR(50),         -- Preferred race distance
    preferred_surface VARCHAR(50),          -- Preferred track surface  
    preferred_class VARCHAR(50),            -- Preferred race class
    specialization VARCHAR(100),            -- Training specialization
    
    -- Activity tracking
    races_this_year INTEGER DEFAULT 0,      -- Races this year
    wins_this_year INTEGER DEFAULT 0,       -- Wins this year
    horses_trained_year INTEGER DEFAULT 0,  -- Different horses trained this year
    last_race_date DATE,                    -- Date of last race
    last_win_date DATE,                     -- Date of last win
    
    -- Track performance
    home_track VARCHAR(100),                -- Primary/home track
    home_track_wins INTEGER DEFAULT 0,      -- Wins at home track
    home_track_runs INTEGER DEFAULT 0,      -- Runs at home track
    
    -- Rankings and recognition
    regional_ranking INTEGER,               -- Regional trainer ranking
    national_ranking INTEGER,               -- National trainer ranking
    awards_count INTEGER DEFAULT 0,         -- Number of training awards
    champion_horses INTEGER DEFAULT 0,      -- Number of champion horses trained
    
    -- Business metrics
    training_fees_range VARCHAR(50),        -- Typical training fee range
    success_with_young_horses DECIMAL(5,2), -- Success rate with 2-3 year olds
    success_with_veterans DECIMAL(5,2),     -- Success rate with older horses
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_race_update TIMESTAMP,             -- Last time race data was updated
    
    -- Data source tracking
    source_file VARCHAR(255),               -- Original CSV file
    import_batch_id VARCHAR(100),           -- Batch ID for tracking imports
    
    -- Status
    active BOOLEAN DEFAULT TRUE,            -- Currently active trainer
    retired_date DATE,                      -- Retirement date if applicable
    suspended BOOLEAN DEFAULT FALSE,        -- Currently suspended
    suspension_end_date DATE                -- End date of suspension
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_trainers_trainer_id ON trainers(trainer_id);
CREATE INDEX IF NOT EXISTS idx_trainers_name ON trainers(name);
CREATE INDEX IF NOT EXISTS idx_trainers_win_percentage ON trainers(win_percentage);
CREATE INDEX IF NOT EXISTS idx_trainers_prize_money ON trainers(prize_money_total);
CREATE INDEX IF NOT EXISTS idx_trainers_stable_location ON trainers(stable_location);
CREATE INDEX IF NOT EXISTS idx_trainers_last_race_date ON trainers(last_race_date);
CREATE INDEX IF NOT EXISTS idx_trainers_active ON trainers(active);
CREATE INDEX IF NOT EXISTS idx_trainers_current_rating ON trainers(current_rating);
CREATE INDEX IF NOT EXISTS idx_trainers_home_track ON trainers(home_track);
CREATE INDEX IF NOT EXISTS idx_trainers_updated_at ON trainers(updated_at);

-- Constraints
ALTER TABLE trainers ADD CONSTRAINT chk_trainers_years_training CHECK (years_training >= 0 AND years_training <= 80);
ALTER TABLE trainers ADD CONSTRAINT chk_trainers_percentages CHECK (
    win_percentage >= 0 AND win_percentage <= 100 AND
    place_percentage >= 0 AND place_percentage <= 100 AND
    show_percentage >= 0 AND show_percentage <= 100
);
ALTER TABLE trainers ADD CONSTRAINT chk_trainers_ratings CHECK (current_rating >= 0 AND best_rating >= 0);
ALTER TABLE trainers ADD CONSTRAINT chk_trainers_counts CHECK (
    total_runs >= 0 AND total_wins >= 0 AND total_places >= 0 AND total_shows >= 0
);
ALTER TABLE trainers ADD CONSTRAINT chk_trainers_wins_vs_runs CHECK (total_wins <= total_runs);
ALTER TABLE trainers ADD CONSTRAINT chk_trainers_places_vs_runs CHECK (total_places <= total_runs);
ALTER TABLE trainers ADD CONSTRAINT chk_trainers_shows_vs_runs CHECK (total_shows <= total_runs);
ALTER TABLE trainers ADD CONSTRAINT chk_trainers_year_counts CHECK (
    races_this_year >= 0 AND wins_this_year >= 0 AND wins_this_year <= races_this_year
);
ALTER TABLE trainers ADD CONSTRAINT chk_trainers_stable_capacity CHECK (
    stable_capacity >= 0 AND current_horse_count >= 0 AND current_horse_count <= stable_capacity
);
ALTER TABLE trainers ADD CONSTRAINT chk_trainers_home_track_stats CHECK (
    home_track_wins >= 0 AND home_track_runs >= 0 AND home_track_wins <= home_track_runs
);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_trainers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_trainers_updated_at
    BEFORE UPDATE ON trainers
    FOR EACH ROW
    EXECUTE FUNCTION update_trainers_updated_at();

-- Trigger to calculate percentages automatically
CREATE OR REPLACE FUNCTION calculate_trainer_percentages()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate win percentages
    IF NEW.total_runs > 0 THEN
        NEW.win_percentage = ROUND((NEW.total_wins::DECIMAL / NEW.total_runs::DECIMAL) * 100, 2);
        NEW.place_percentage = ROUND((NEW.total_places::DECIMAL / NEW.total_runs::DECIMAL) * 100, 2);
        NEW.show_percentage = ROUND((NEW.total_shows::DECIMAL / NEW.total_runs::DECIMAL) * 100, 2);
    ELSE
        NEW.win_percentage = 0;
        NEW.place_percentage = 0;
        NEW.show_percentage = 0;
    END IF;
    
    -- Calculate home track success rate
    IF NEW.home_track_runs > 0 THEN
        NEW.success_with_young_horses = COALESCE(NEW.success_with_young_horses, 
            ROUND((NEW.home_track_wins::DECIMAL / NEW.home_track_runs::DECIMAL) * 100, 2));
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_trainers_calculate_percentages
    BEFORE INSERT OR UPDATE OF total_runs, total_wins, total_places, total_shows, home_track_wins, home_track_runs ON trainers
    FOR EACH ROW
    EXECUTE FUNCTION calculate_trainer_percentages();

-- Comments for documentation
COMMENT ON TABLE trainers IS 'Central entity table for unique trainers with CSV ID mapping';
COMMENT ON COLUMN trainers.id IS 'Auto-increment primary key for internal references';
COMMENT ON COLUMN trainers.trainer_id IS 'Unique trainer ID from CSV files - used for data mapping';
COMMENT ON COLUMN trainers.name IS 'Trainer name as it appears in racing data';
COMMENT ON COLUMN trainers.stable_name IS 'Official name of training stable/operation';
COMMENT ON COLUMN trainers.win_percentage IS 'Career win percentage (auto-calculated)';
COMMENT ON COLUMN trainers.specialization IS 'Training specialty (sprinters, stayers, juveniles, etc.)';
COMMENT ON COLUMN trainers.current_horse_count IS 'Current number of horses in training';
COMMENT ON COLUMN trainers.import_batch_id IS 'Tracking ID for data import batch for audit purposes';

-- Example usage queries:
/*
-- Find trainer by CSV trainer_id
SELECT * FROM trainers WHERE trainer_id = 1234;

-- Top performing trainers by win percentage
SELECT name, trainer_id, win_percentage, total_wins, total_runs, 
       prize_money_total, stable_location
FROM trainers 
WHERE total_runs >= 100  -- Only trainers with significant experience
ORDER BY win_percentage DESC
LIMIT 20;

-- Trainers with recent activity
SELECT name, trainer_id, last_race_date, races_this_year, wins_this_year,
       current_horse_count,
       ROUND((wins_this_year::DECIMAL / NULLIF(races_this_year, 0)::DECIMAL) * 100, 2) as year_win_pct
FROM trainers 
WHERE last_race_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY last_race_date DESC;

-- Prize money leaders
SELECT name, trainer_id, prize_money_total, prize_money_year, 
       win_percentage, stable_location
FROM trainers 
ORDER BY prize_money_total DESC
LIMIT 20;

-- Trainers by location with stats
SELECT stable_location, COUNT(*) as trainer_count, 
       AVG(win_percentage) as avg_win_pct,
       SUM(prize_money_total) as total_prize_money,
       SUM(current_horse_count) as total_horses
FROM trainers 
WHERE active = TRUE
GROUP BY stable_location
ORDER BY trainer_count DESC;

-- Home track specialists
SELECT name, trainer_id, home_track, 
       home_track_wins, home_track_runs,
       ROUND((home_track_wins::DECIMAL / NULLIF(home_track_runs, 0)::DECIMAL) * 100, 2) as home_win_pct,
       win_percentage as overall_win_pct
FROM trainers 
WHERE home_track_runs >= 50
ORDER BY (home_track_wins::DECIMAL / NULLIF(home_track_runs, 0)::DECIMAL) DESC
LIMIT 20;

-- Training capacity analysis
SELECT stable_location, 
       AVG(stable_capacity) as avg_capacity,
       AVG(current_horse_count) as avg_current_horses,
       AVG((current_horse_count::DECIMAL / NULLIF(stable_capacity, 0)::DECIMAL) * 100) as avg_utilization_pct
FROM trainers 
WHERE stable_capacity > 0 AND active = TRUE
GROUP BY stable_location
ORDER BY avg_utilization_pct DESC;
*/
