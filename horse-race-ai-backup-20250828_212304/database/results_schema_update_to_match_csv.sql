-- Results Database Schema Update Script to Match CSV Structure
-- Date: 2025-08-24
-- Purpose: Align results_horse_racing_db schema with actual CSV data structure

-- ============================================================================
-- 1. RECORDS Table - Complete Restructure Required
-- ============================================================================

-- Drop existing table and recreate with correct structure matching CSV
DROP TABLE IF EXISTS records CASCADE;

CREATE TABLE records (
    id INTEGER PRIMARY KEY,                    -- Maps to CSV 'ID'
    race_id INTEGER NOT NULL,                  -- Maps to CSV 'Race_ID'
    horse_number INTEGER,                      -- Maps to CSV 'Horse_number' (cloth number)
    place INTEGER,                             -- Maps to CSV 'Place' (finishing position)
    draw INTEGER,                              -- Maps to CSV 'Draw' (starting stall)
    horse_id INTEGER,                          -- Maps to CSV 'Horse_ID'
    country VARCHAR(10),                       -- Maps to CSV 'Country'
    name VARCHAR(100),                         -- Maps to CSV 'Name' (horse name)
    age INTEGER,                               -- Maps to CSV 'Age'
    weight_uk VARCHAR(20),                     -- Maps to CSV 'weight_uk'
    weight DECIMAL(5,2),                       -- Maps to CSV 'weight'
    gears VARCHAR(20),                         -- Maps to CSV 'gears'
    horse_rate INTEGER,                        -- Maps to CSV 'Horse_rate'
    jockey_id INTEGER,                         -- Maps to CSV 'jockey_ID'
    jockey VARCHAR(100),                       -- Maps to CSV 'jockey'
    trainer_id INTEGER,                        -- Maps to CSV 'trainer_ID'
    trainer VARCHAR(100),                      -- Maps to CSV 'trainer'
    fav VARCHAR(10),                           -- Maps to CSV 'fav'
    sp DECIMAL(8,2),                          -- Maps to CSV 'SP' (Starting Price)
    distance_btn VARCHAR(20),                  -- Maps to CSV 'Distance_btn'
    distance_btn_total DECIMAL(8,2),          -- Maps to CSV 'Distance_btn_total'
    
    -- Sectional timing data (for speed analysis)
    distance_sec_1 DECIMAL(8,2),
    sectional_time_1 DECIMAL(8,3),
    distance_sec_2 DECIMAL(8,2),
    sectional_time_2 DECIMAL(8,3),
    distance_sec_3 DECIMAL(8,2),
    sectional_time_3 DECIMAL(8,3),
    distance_sec_4 DECIMAL(8,2),
    sectional_time_4 DECIMAL(8,3),
    distance_sec_5 DECIMAL(8,2),
    sectional_time_5 DECIMAL(8,3),
    distance_sec_6 DECIMAL(8,2),
    sectional_time_6 DECIMAL(8,3),
    distance_sec_7 DECIMAL(8,2),
    sectional_time_7 DECIMAL(8,3),
    distance_sec_8 DECIMAL(8,2),
    sectional_time_8 DECIMAL(8,3),
    distance_sec_9 DECIMAL(8,2),
    sectional_time_9 DECIMAL(8,3),
    distance_sec_10 DECIMAL(8,2),
    sectional_time_10 DECIMAL(8,3),
    distance_sec_11 DECIMAL(8,2),
    sectional_time_11 DECIMAL(8,3),
    distance_sec_12 DECIMAL(8,2),
    sectional_time_12 DECIMAL(8,3),
    distance_sec_13 DECIMAL(8,2),
    sectional_time_13 DECIMAL(8,3),
    distance_sec_14 DECIMAL(8,2),
    sectional_time_14 DECIMAL(8,3),
    distance_sec_15 DECIMAL(8,2),
    sectional_time_15 DECIMAL(8,3),
    distance_sec_16 DECIMAL(8,2),
    sectional_time_16 DECIMAL(8,3),
    distance_sec_17 DECIMAL(8,2),
    sectional_time_17 DECIMAL(8,3),
    distance_sec_18 DECIMAL(8,2),
    sectional_time_18 DECIMAL(8,3),
    
    -- Performance timing data
    finish_time DECIMAL(8,3),
    distance_speed_early_race DECIMAL(8,2),
    speed_achieved_early_race DECIMAL(8,2),
    distance_speed_mid_race DECIMAL(8,2),
    speed_achieved_mid_race DECIMAL(8,2),
    distance_speed_finish_race DECIMAL(8,2),
    speed_achieved_finish_race DECIMAL(8,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_records_race_id ON records(race_id);
CREATE INDEX idx_records_horse_id ON records(horse_id);
CREATE INDEX idx_records_horse_number ON records(horse_number);
CREATE INDEX idx_records_name ON records(name);
CREATE INDEX idx_records_place ON records(place);
CREATE INDEX idx_records_jockey_id ON records(jockey_id);
CREATE INDEX idx_records_trainer_id ON records(trainer_id);

-- ============================================================================
-- 2. RACES Table - Minor Cleanup (Remove Extra Fields Not in CSV)
-- ============================================================================

-- The races table mostly matches but has some extra fields not in CSV
-- We'll keep them as they might be useful for results data
-- No changes needed - the current structure is compatible

-- ============================================================================
-- 3. HORSES Table - Should Already Match from Previous Update
-- ============================================================================
-- The horses table should already have the correct structure from the cards update
-- If not, it uses the same CSV structure so no additional changes needed

-- ============================================================================
-- 4. Add Foreign Key Relationships
-- ============================================================================

-- Add foreign key constraints
ALTER TABLE records 
ADD CONSTRAINT fk_records_race_id 
FOREIGN KEY (race_id) REFERENCES races(race_id);

-- Note: Cannot add FK to horses table until we ensure referential integrity

-- ============================================================================
-- 5. Add Comments for Documentation
-- ============================================================================

COMMENT ON TABLE records IS 'Race results with complete sectional timing data matching CSV structure';
COMMENT ON COLUMN records.id IS 'Primary key from CSV ID field';
COMMENT ON COLUMN records.horse_number IS 'Cloth number worn by horse (required)';
COMMENT ON COLUMN records.place IS 'Finishing position in race';
COMMENT ON COLUMN records.draw IS 'Starting stall position (can be NULL)';
COMMENT ON COLUMN records.name IS 'Horse name';
COMMENT ON COLUMN records.sp IS 'Starting Price (final odds)';
COMMENT ON COLUMN records.distance_btn IS 'Distance beaten (lengths/margins)';
COMMENT ON COLUMN records.finish_time IS 'Total race finish time';

-- Add comments for sectional timing fields
COMMENT ON COLUMN records.distance_sec_1 IS 'Distance covered in first section';
COMMENT ON COLUMN records.sectional_time_1 IS 'Time taken for first section';
-- (Additional sectional comments would follow same pattern)

COMMENT ON COLUMN records.speed_achieved_early_race IS 'Speed achieved in early part of race';
COMMENT ON COLUMN records.speed_achieved_mid_race IS 'Speed achieved in middle part of race';
COMMENT ON COLUMN records.speed_achieved_finish_race IS 'Speed achieved in finish of race';
