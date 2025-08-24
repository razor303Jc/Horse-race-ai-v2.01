-- Schema Update Script to Match CSV Structure
-- Date: 2025-08-24
-- Purpose: Align database schema with actual CSV data structure

-- ============================================================================
-- 1. RACECARD_DETAILS Table - Complete Restructure
-- ============================================================================

-- Drop existing table and recreate with correct structure
DROP TABLE IF EXISTS racecard_details CASCADE;

CREATE TABLE racecard_details (
    id INTEGER PRIMARY KEY,
    race_id INTEGER NOT NULL,
    horse_number INTEGER,
    draw INTEGER,  -- This is the stall position (can be NULL)
    horse_id INTEGER,
    country VARCHAR(10),
    name VARCHAR(100),  -- Horse name
    age INTEGER,
    weight_uk VARCHAR(20),
    weight DECIMAL(5,2),
    gears VARCHAR(20),
    horse_rate INTEGER,
    jockey_id INTEGER,
    jockey VARCHAR(100),
    trainer_id INTEGER,
    trainer VARCHAR(100),
    fav VARCHAR(10),
    odds VARCHAR(20),
    odds_decimal DECIMAL(8,2),
    timeform_comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_racecard_details_race_id ON racecard_details(race_id);
CREATE INDEX idx_racecard_details_horse_id ON racecard_details(horse_id);
CREATE INDEX idx_racecard_details_horse_number ON racecard_details(horse_number);
CREATE INDEX idx_racecard_details_name ON racecard_details(name);

-- ============================================================================
-- 2. HORSES Table - Add Missing Fields
-- ============================================================================

-- Drop existing and recreate with full CSV structure
DROP TABLE IF EXISTS horses CASCADE;

CREATE TABLE horses (
    id INTEGER PRIMARY KEY,
    uptodate DATE,
    state VARCHAR(20),
    race_id_last_race INTEGER,
    date_last_race DATE,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(10),
    age INTEGER,
    color VARCHAR(50),
    owner VARCHAR(200),
    sire VARCHAR(100),
    dam VARCHAR(100),
    dam_sire VARCHAR(100),
    sex VARCHAR(20),
    total_races DECIMAL(8,1),
    wins DECIMAL(8,1),
    percentage_wins VARCHAR(10),
    placed DECIMAL(8,1),
    percentage_placed VARCHAR(10),
    flat_aw_races DECIMAL(8,1),
    flat_aw_wins DECIMAL(8,1),
    flat_aw_rate VARCHAR(10),
    flat_aw_placed DECIMAL(8,1),
    flat_aw_placed_rate VARCHAR(10),
    flat_turf_races DECIMAL(8,1),
    flat_turf_wins DECIMAL(8,1),
    flat_turf_rate VARCHAR(10),
    flat_turf_placed DECIMAL(8,1),
    flat_turf_placed_rate VARCHAR(10),
    chase_races DECIMAL(8,1),
    chase_wins DECIMAL(8,1),
    chase_rate VARCHAR(10),
    chase_placed DECIMAL(8,1),
    chase_placed_rate VARCHAR(10),
    hurdle_races DECIMAL(8,1),
    hurdle_wins DECIMAL(8,1),
    hurdle_rate VARCHAR(10),
    hurdle_placed DECIMAL(8,1),
    hurdle_placed_rate VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_horses_name ON horses(name);
CREATE INDEX idx_horses_country ON horses(country);
CREATE INDEX idx_horses_state ON horses(state);
CREATE INDEX idx_horses_last_race ON horses(race_id_last_race);

-- ============================================================================
-- 3. RACES Table - Already matches CSV structure, no changes needed
-- ============================================================================
-- The races table structure already matches the CSV perfectly

-- ============================================================================
-- 4. Recreate Foreign Key Relationships
-- ============================================================================

-- Add foreign key constraints
ALTER TABLE racecard_details 
ADD CONSTRAINT fk_racecard_details_race_id 
FOREIGN KEY (race_id) REFERENCES races(race_id);

-- Note: We cannot add FK to horses table from racecard_details 
-- because horse_id values might not exist in horses table yet
-- This will need to be handled during data import

COMMENT ON TABLE racecard_details IS 'Race card details matching CSV structure with draw (stall) and horse_number (cloth number) as separate fields';
COMMENT ON TABLE horses IS 'Horse information with complete racing statistics matching CSV structure';
COMMENT ON COLUMN racecard_details.draw IS 'Starting stall position (can be NULL)';
COMMENT ON COLUMN racecard_details.horse_number IS 'Cloth number worn by horse (required)';
COMMENT ON COLUMN racecard_details.name IS 'Horse name';
