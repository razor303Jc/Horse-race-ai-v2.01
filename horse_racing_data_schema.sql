-- Horse Racing Data Pipeline Schema
-- Creates tables that match the expected CSV data structure

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Races Cards table (for races.csv from both results and cards data)
CREATE TABLE IF NOT EXISTS races_cards (
    id SERIAL PRIMARY KEY,
    race_number INTEGER,
    race_time VARCHAR(10),
    course VARCHAR(255),
    race_type VARCHAR(255),
    date DATE,
    race_name VARCHAR(255),
    class_level VARCHAR(50),
    years VARCHAR(20),
    distance VARCHAR(20),
    surface VARCHAR(50),
    field_size INTEGER,
    prize_money INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Horses table (for horses.csv)
CREATE TABLE IF NOT EXISTS horses (
    id SERIAL PRIMARY KEY,
    horse_name VARCHAR(255),
    horse_id VARCHAR(100),
    sire VARCHAR(255),
    dam VARCHAR(255),
    damsire VARCHAR(255),
    owner VARCHAR(255),
    breeder VARCHAR(255),
    country VARCHAR(50),
    foaled DATE,
    sex VARCHAR(10),
    color VARCHAR(50),
    trainer VARCHAR(255),
    jockey VARCHAR(255),
    uptodate DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Race Results table (for records.csv)
CREATE TABLE IF NOT EXISTS race_results (
    id SERIAL PRIMARY KEY,
    race_id VARCHAR(100),
    horse_name VARCHAR(255),
    jockey_name VARCHAR(255),
    trainer_name VARCHAR(255),
    horse_weight_kg DECIMAL(5,1),
    horse_age INTEGER,
    draw INTEGER,
    handicap_weight DECIMAL(4,1),
    win_odds DECIMAL(8,2),
    place_odds DECIMAL(8,2),
    barrier INTEGER,
    finished_position INTEGER,
    margin DECIMAL(6,2),
    time_seconds DECIMAL(8,2),
    prize_money INTEGER DEFAULT 0,
    race_date DATE,
    course VARCHAR(255),
    race_name VARCHAR(255),
    distance VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Jockey Stats table (for jockeys_stats.csv)
CREATE TABLE IF NOT EXISTS jockey_stats (
    id SERIAL PRIMARY KEY,
    jockey_name VARCHAR(255),
    wins INTEGER DEFAULT 0,
    runs INTEGER DEFAULT 0,
    places INTEGER DEFAULT 0,
    win_percentage DECIMAL(5,2),
    place_percentage DECIMAL(5,2),
    earnings DECIMAL(15,2),
    country VARCHAR(50),
    uptodate DATE,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Trainer Stats table (for trainers_stats.csv)
CREATE TABLE IF NOT EXISTS trainer_stats (
    id SERIAL PRIMARY KEY,
    trainer_name VARCHAR(255),
    wins INTEGER DEFAULT 0,
    runs INTEGER DEFAULT 0,
    places INTEGER DEFAULT 0,
    win_percentage DECIMAL(5,2),
    place_percentage DECIMAL(5,2),
    earnings DECIMAL(15,2),
    country VARCHAR(50),
    uptodate DATE,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Racecard Details table (for racecard_details.csv)
CREATE TABLE IF NOT EXISTS racecard_details (
    id SERIAL PRIMARY KEY,
    race_id VARCHAR(100),
    horse_name VARCHAR(255),
    jockey_name VARCHAR(255),
    trainer_name VARCHAR(255),
    horse_age INTEGER,
    horse_weight_kg DECIMAL(5,1),
    handicap_weight DECIMAL(4,1),
    draw INTEGER,
    barrier INTEGER,
    form VARCHAR(50),
    win_odds DECIMAL(8,2),
    place_odds DECIMAL(8,2),
    last_run_days INTEGER,
    career_wins INTEGER,
    career_runs INTEGER,
    distance_record VARCHAR(100),
    track_record VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_races_cards_date ON races_cards(date);
CREATE INDEX IF NOT EXISTS idx_races_cards_course ON races_cards(course);
CREATE INDEX IF NOT EXISTS idx_horses_name ON horses(horse_name);
CREATE INDEX IF NOT EXISTS idx_horses_trainer ON horses(trainer);
CREATE INDEX IF NOT EXISTS idx_race_results_horse ON race_results(horse_name);
CREATE INDEX IF NOT EXISTS idx_race_results_jockey ON race_results(jockey_name);
CREATE INDEX IF NOT EXISTS idx_race_results_trainer ON race_results(trainer_name);
CREATE INDEX IF NOT EXISTS idx_race_results_date ON race_results(race_date);
CREATE INDEX IF NOT EXISTS idx_jockey_stats_name ON jockey_stats(jockey_name);
CREATE INDEX IF NOT EXISTS idx_jockey_stats_uptodate ON jockey_stats(uptodate);
CREATE INDEX IF NOT EXISTS idx_trainer_stats_name ON trainer_stats(trainer_name);
CREATE INDEX IF NOT EXISTS idx_trainer_stats_uptodate ON trainer_stats(uptodate);
CREATE INDEX IF NOT EXISTS idx_racecard_details_race ON racecard_details(race_id);
CREATE INDEX IF NOT EXISTS idx_racecard_details_horse ON racecard_details(horse_name);

-- Add unique constraints to prevent duplicates
CREATE UNIQUE INDEX IF NOT EXISTS idx_horses_unique ON horses(horse_name, uptodate);
CREATE UNIQUE INDEX IF NOT EXISTS idx_jockey_stats_unique ON jockey_stats(jockey_name, uptodate);
CREATE UNIQUE INDEX IF NOT EXISTS idx_trainer_stats_unique ON trainer_stats(trainer_name, uptodate);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers to update timestamps
CREATE TRIGGER IF NOT EXISTS update_races_cards_updated_at 
    BEFORE UPDATE ON races_cards 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_horses_updated_at 
    BEFORE UPDATE ON horses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_race_results_updated_at 
    BEFORE UPDATE ON race_results 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_jockey_stats_updated_at 
    BEFORE UPDATE ON jockey_stats 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_trainer_stats_updated_at 
    BEFORE UPDATE ON trainer_stats 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_racecard_details_updated_at 
    BEFORE UPDATE ON racecard_details 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Verify the setup
SELECT 'Horse Racing data pipeline schema created successfully!' as status;
