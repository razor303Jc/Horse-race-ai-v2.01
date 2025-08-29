-- Race Card Database Schema
-- Creates dedicated tables for race card data for ML training

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS race_entries CASCADE;
DROP TABLE IF EXISTS horses CASCADE;  
DROP TABLE IF EXISTS race_cards CASCADE;
DROP TABLE IF EXISTS data_quality_log CASCADE;

-- Create race_cards table (main race information)
CREATE TABLE race_cards (
    race_id BIGINT PRIMARY KEY,
    race_number INTEGER,
    race_time TIMESTAMP,
    course_id INTEGER,
    course VARCHAR(100),
    race_type VARCHAR(50),
    race_date DATE,
    race_name VARCHAR(200),
    class VARCHAR(20),
    age_restriction VARCHAR(20),
    distance VARCHAR(50),
    surface VARCHAR(50),
    prize VARCHAR(50),
    runners_racecard INTEGER,
    runners INTEGER,
    draw_info VARCHAR(20),
    ew_racecard INTEGER,
    ew INTEGER,
    places_ew_racecard INTEGER,
    places_ew INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create horses table (horse information and performance stats)
CREATE TABLE horses (
    horse_id BIGINT PRIMARY KEY,
    uptodate DATE,
    state VARCHAR(20),
    race_id_last_race BIGINT,
    date_last_race DATE,
    name VARCHAR(100),
    country VARCHAR(10),
    age INTEGER,
    color VARCHAR(30),
    owner VARCHAR(200),
    sire VARCHAR(100),
    dam VARCHAR(100),
    dam_sire VARCHAR(100),
    sex VARCHAR(20),
    total_races FLOAT,
    wins FLOAT,
    percentage_wins VARCHAR(10),
    placed FLOAT,
    percentage_placed VARCHAR(10),
    flat_aw_races FLOAT,
    flat_aw_wins FLOAT,
    flat_aw_rate VARCHAR(10),
    flat_aw_placed FLOAT,
    flat_aw_placed_rate VARCHAR(10),
    flat_turf_races FLOAT,
    flat_turf_wins FLOAT,
    flat_turf_rate VARCHAR(10),
    flat_turf_placed FLOAT,
    flat_turf_placed_rate VARCHAR(10),
    chase_races FLOAT,
    chase_wins FLOAT,
    chase_rate VARCHAR(10),
    chase_placed FLOAT,
    chase_placed_rate VARCHAR(10),
    hurdle_races FLOAT,
    hurdle_wins FLOAT,
    hurdle_rate VARCHAR(10),
    hurdle_placed FLOAT,
    hurdle_placed_rate VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create race_entries table (race-specific horse entries with odds, jockey, etc.)
CREATE TABLE race_entries (
    entry_id BIGSERIAL PRIMARY KEY,
    race_id BIGINT REFERENCES race_cards(race_id),
    horse_id BIGINT REFERENCES horses(horse_id),
    horse_number INTEGER,
    draw INTEGER,
    country VARCHAR(10),
    horse_name VARCHAR(100),
    age INTEGER,
    weight_uk VARCHAR(10),
    weight_kg FLOAT,
    gears VARCHAR(20),
    horse_rate INTEGER,
    jockey_id INTEGER,
    jockey VARCHAR(100),
    trainer_id INTEGER,
    trainer VARCHAR(100),
    favourite_position VARCHAR(10),
    odds VARCHAR(20),
    odds_decimal FLOAT,
    timeform_comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(race_id, horse_id)
);

-- Create data quality log table
CREATE TABLE data_quality_log (
    log_id BIGSERIAL PRIMARY KEY,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    table_name VARCHAR(50),
    records_processed INTEGER,
    records_inserted INTEGER,
    records_updated INTEGER,
    records_failed INTEGER,
    processing_time_ms INTEGER,
    data_source VARCHAR(100),
    status VARCHAR(20),
    error_details TEXT
);

-- Create indexes for performance
CREATE INDEX idx_race_cards_date ON race_cards(race_date);
CREATE INDEX idx_race_cards_course ON race_cards(course);
CREATE INDEX idx_race_cards_time ON race_cards(race_time);

CREATE INDEX idx_horses_name ON horses(name);
CREATE INDEX idx_horses_performance ON horses(total_races, wins);

CREATE INDEX idx_race_entries_race ON race_entries(race_id);
CREATE INDEX idx_race_entries_horse ON race_entries(horse_id);
CREATE INDEX idx_race_entries_odds ON race_entries(odds_decimal);

-- Create views for ML training data
CREATE VIEW ml_training_view AS
SELECT 
    rc.race_id,
    rc.race_time,
    rc.course,
    rc.race_type,
    rc.distance,
    rc.surface,
    rc.runners,
    re.horse_id,
    re.horse_name,
    re.age,
    re.weight_kg,
    re.draw,
    re.odds_decimal,
    re.jockey,
    re.trainer,
    h.total_races,
    h.wins,
    h.percentage_wins,
    h.flat_turf_wins,
    h.flat_aw_wins,
    h.chase_wins,
    h.hurdle_wins
FROM race_cards rc
JOIN race_entries re ON rc.race_id = re.race_id
JOIN horses h ON re.horse_id = h.horse_id;

-- Create view for today's races
CREATE VIEW todays_races AS
SELECT 
    rc.*,
    COUNT(re.entry_id) as actual_runners
FROM race_cards rc
LEFT JOIN race_entries re ON rc.race_id = re.race_id
WHERE rc.race_date = CURRENT_DATE
GROUP BY rc.race_id
ORDER BY rc.race_time;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO horserace_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO horserace_user;

-- Add comments for documentation
COMMENT ON TABLE race_cards IS 'Main race information including timing, course, and race details';
COMMENT ON TABLE horses IS 'Horse profiles with comprehensive performance statistics';
COMMENT ON TABLE race_entries IS 'Race-specific entries linking horses to races with odds and participant details';
COMMENT ON TABLE data_quality_log IS 'Data quality tracking for upload monitoring';

COMMENT ON VIEW ml_training_view IS 'Denormalized view optimized for ML model training';
COMMENT ON VIEW todays_races IS 'Current day races with runner counts for quick reference';
