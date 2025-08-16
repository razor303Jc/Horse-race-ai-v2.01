-- Complete Database Schema for ALL CSV Columns
-- Matches CSV structure exactly with proper NULL handling
-- Created to preserve ALL data from CSV files

-- Races table - matches all 20 CSV columns
CREATE TABLE IF NOT EXISTS races (
    id SERIAL PRIMARY KEY,
    race_id TEXT DEFAULT 'none',
    race_number INTEGER DEFAULT 0,
    race_time TEXT DEFAULT 'none',
    course_id INTEGER DEFAULT 0,
    course TEXT DEFAULT 'none',
    race_type TEXT DEFAULT 'none',
    date TEXT DEFAULT 'none',
    race_name TEXT DEFAULT 'none',
    class TEXT DEFAULT 'none',
    years TEXT DEFAULT 'none',
    distance TEXT DEFAULT 'none',
    surface TEXT DEFAULT 'none',
    prize TEXT DEFAULT 'none',
    runners_racecard INTEGER DEFAULT 0,
    runners INTEGER DEFAULT 0,
    draw INTEGER DEFAULT 0,
    ew_racecard INTEGER DEFAULT 0,
    ew INTEGER DEFAULT 0,
    places_ew_racecard INTEGER DEFAULT 0,
    places_ew INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Records table - matches all 64 CSV columns including sectional times
CREATE TABLE IF NOT EXISTS records (
    id SERIAL PRIMARY KEY,
    record_id TEXT DEFAULT 'none',
    race_id TEXT DEFAULT 'none',
    horse_number INTEGER DEFAULT 0,
    position INTEGER DEFAULT 0,
    draw INTEGER DEFAULT 0,
    horse_id INTEGER DEFAULT 0,
    country TEXT DEFAULT 'none',
    horse TEXT DEFAULT 'none',
    age INTEGER DEFAULT 0,
    weight_uk DECIMAL DEFAULT 0.0,
    weight DECIMAL DEFAULT 0.0,
    gears TEXT DEFAULT 'none',
    or_rating INTEGER DEFAULT 0,
    jockey_id INTEGER DEFAULT 0,
    jockey TEXT DEFAULT 'none',
    trainer_id INTEGER DEFAULT 0,
    trainer TEXT DEFAULT 'none',
    fav INTEGER DEFAULT 0,
    sp DECIMAL DEFAULT 0.0,
    distance_btn DECIMAL DEFAULT 0.0,
    distance_btn_total DECIMAL DEFAULT 0.0,
    distance_sec_1 DECIMAL DEFAULT 0.0,
    sectional_time_1 DECIMAL DEFAULT 0.0,
    distance_sec_2 DECIMAL DEFAULT 0.0,
    sectional_time_2 DECIMAL DEFAULT 0.0,
    distance_sec_3 DECIMAL DEFAULT 0.0,
    sectional_time_3 DECIMAL DEFAULT 0.0,
    distance_sec_4 DECIMAL DEFAULT 0.0,
    sectional_time_4 DECIMAL DEFAULT 0.0,
    distance_sec_5 DECIMAL DEFAULT 0.0,
    sectional_time_5 DECIMAL DEFAULT 0.0,
    distance_sec_6 DECIMAL DEFAULT 0.0,
    sectional_time_6 DECIMAL DEFAULT 0.0,
    distance_sec_7 DECIMAL DEFAULT 0.0,
    sectional_time_7 DECIMAL DEFAULT 0.0,
    distance_sec_8 DECIMAL DEFAULT 0.0,
    sectional_time_8 DECIMAL DEFAULT 0.0,
    distance_sec_9 DECIMAL DEFAULT 0.0,
    sectional_time_9 DECIMAL DEFAULT 0.0,
    distance_sec_10 DECIMAL DEFAULT 0.0,
    sectional_time_10 DECIMAL DEFAULT 0.0,
    distance_sec_11 DECIMAL DEFAULT 0.0,
    sectional_time_11 DECIMAL DEFAULT 0.0,
    distance_sec_12 DECIMAL DEFAULT 0.0,
    sectional_time_12 DECIMAL DEFAULT 0.0,
    distance_sec_13 DECIMAL DEFAULT 0.0,
    sectional_time_13 DECIMAL DEFAULT 0.0,
    distance_sec_14 DECIMAL DEFAULT 0.0,
    sectional_time_14 DECIMAL DEFAULT 0.0,
    distance_sec_15 DECIMAL DEFAULT 0.0,
    sectional_time_15 DECIMAL DEFAULT 0.0,
    distance_sec_16 DECIMAL DEFAULT 0.0,
    sectional_time_16 DECIMAL DEFAULT 0.0,
    distance_sec_17 DECIMAL DEFAULT 0.0,
    sectional_time_17 DECIMAL DEFAULT 0.0,
    distance_sec_18 DECIMAL DEFAULT 0.0,
    sectional_time_18 DECIMAL DEFAULT 0.0,
    finish_time DECIMAL DEFAULT 0.0,
    distance_speed_early_race DECIMAL DEFAULT 0.0,
    speed_achieved_early_race DECIMAL DEFAULT 0.0,
    distance_speed_mid_race DECIMAL DEFAULT 0.0,
    speed_achieved_mid_race DECIMAL DEFAULT 0.0,
    distance_speed_finish_race DECIMAL DEFAULT 0.0,
    speed_achieved_finish_race DECIMAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Horses table - matches all 39 CSV columns
CREATE TABLE IF NOT EXISTS horses (
    id SERIAL PRIMARY KEY,
    horse_id INTEGER DEFAULT 0,
    uptodate TEXT DEFAULT 'none',
    state TEXT DEFAULT 'none',
    race_id_last_race INTEGER DEFAULT 0,
    date_last_race TEXT DEFAULT 'none',
    horse_name TEXT DEFAULT 'none',
    country TEXT DEFAULT 'none',
    age INTEGER DEFAULT 0,
    color TEXT DEFAULT 'none',
    owner TEXT DEFAULT 'none',
    sire TEXT DEFAULT 'none',
    dam TEXT DEFAULT 'none',
    dam_sire TEXT DEFAULT 'none',
    sex TEXT DEFAULT 'none',
    total_races INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    percentage_wins DECIMAL DEFAULT 0.0,
    placed INTEGER DEFAULT 0,
    percentage_placed DECIMAL DEFAULT 0.0,
    flat_aw_races INTEGER DEFAULT 0,
    flat_aw_wins INTEGER DEFAULT 0,
    flat_aw_rate DECIMAL DEFAULT 0.0,
    flat_aw_placed INTEGER DEFAULT 0,
    flat_aw_placed_rate DECIMAL DEFAULT 0.0,
    flat_turf_races INTEGER DEFAULT 0,
    flat_turf_wins INTEGER DEFAULT 0,
    flat_turf_rate DECIMAL DEFAULT 0.0,
    flat_turf_placed INTEGER DEFAULT 0,
    flat_turf_placed_rate DECIMAL DEFAULT 0.0,
    chase_races INTEGER DEFAULT 0,
    chase_wins INTEGER DEFAULT 0,
    chase_rate DECIMAL DEFAULT 0.0,
    chase_placed INTEGER DEFAULT 0,
    chase_placed_rate DECIMAL DEFAULT 0.0,
    hurdle_races INTEGER DEFAULT 0,
    hurdle_wins INTEGER DEFAULT 0,
    hurdle_rate DECIMAL DEFAULT 0.0,
    hurdle_placed INTEGER DEFAULT 0,
    hurdle_placed_rate DECIMAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jockeys stats table - matches all 28 CSV columns
CREATE TABLE IF NOT EXISTS jockeys_stats (
    id SERIAL PRIMARY KEY,
    jockey_id TEXT DEFAULT 'none',
    uptodate TEXT DEFAULT 'none',
    jockey_name TEXT DEFAULT 'none',
    total_races INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    percentage_wins DECIMAL DEFAULT 0.0,
    placed INTEGER DEFAULT 0,
    percentage_placed DECIMAL DEFAULT 0.0,
    flat_aw_races INTEGER DEFAULT 0,
    flat_aw_wins INTEGER DEFAULT 0,
    flat_aw_rate DECIMAL DEFAULT 0.0,
    flat_aw_placed INTEGER DEFAULT 0,
    flat_aw_placed_rate DECIMAL DEFAULT 0.0,
    flat_turf_races INTEGER DEFAULT 0,
    flat_turf_wins INTEGER DEFAULT 0,
    flat_turf_rate DECIMAL DEFAULT 0.0,
    flat_turf_placed INTEGER DEFAULT 0,
    flat_turf_placed_rate DECIMAL DEFAULT 0.0,
    chase_races INTEGER DEFAULT 0,
    chase_wins INTEGER DEFAULT 0,
    chase_rate DECIMAL DEFAULT 0.0,
    chase_placed INTEGER DEFAULT 0,
    chase_placed_rate DECIMAL DEFAULT 0.0,
    hurdle_races INTEGER DEFAULT 0,
    hurdle_wins INTEGER DEFAULT 0,
    hurdle_rate DECIMAL DEFAULT 0.0,
    hurdle_placed INTEGER DEFAULT 0,
    hurdle_placed_rate DECIMAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trainers stats table - matches all 28 CSV columns
CREATE TABLE IF NOT EXISTS trainers_stats (
    id SERIAL PRIMARY KEY,
    trainer_id TEXT DEFAULT 'none',
    uptodate TEXT DEFAULT 'none',
    trainer_name TEXT DEFAULT 'none',
    total_races INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    percentage_wins DECIMAL DEFAULT 0.0,
    placed INTEGER DEFAULT 0,
    percentage_placed DECIMAL DEFAULT 0.0,
    flat_aw_races INTEGER DEFAULT 0,
    flat_aw_wins INTEGER DEFAULT 0,
    flat_aw_rate DECIMAL DEFAULT 0.0,
    flat_aw_placed INTEGER DEFAULT 0,
    flat_aw_placed_rate DECIMAL DEFAULT 0.0,
    flat_turf_races INTEGER DEFAULT 0,
    flat_turf_wins INTEGER DEFAULT 0,
    flat_turf_rate DECIMAL DEFAULT 0.0,
    flat_turf_placed INTEGER DEFAULT 0,
    flat_turf_placed_rate DECIMAL DEFAULT 0.0,
    chase_races INTEGER DEFAULT 0,
    chase_wins INTEGER DEFAULT 0,
    chase_rate DECIMAL DEFAULT 0.0,
    chase_placed INTEGER DEFAULT 0,
    chase_placed_rate DECIMAL DEFAULT 0.0,
    hurdle_races INTEGER DEFAULT 0,
    hurdle_wins INTEGER DEFAULT 0,
    hurdle_rate DECIMAL DEFAULT 0.0,
    hurdle_placed INTEGER DEFAULT 0,
    hurdle_placed_rate DECIMAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_races_race_id ON races(race_id);
CREATE INDEX IF NOT EXISTS idx_races_date ON races(date);
CREATE INDEX IF NOT EXISTS idx_records_race_id ON records(race_id);
CREATE INDEX IF NOT EXISTS idx_records_horse_id ON records(horse_id);
CREATE INDEX IF NOT EXISTS idx_horses_horse_id ON horses(horse_id);
CREATE INDEX IF NOT EXISTS idx_jockeys_jockey_id ON jockeys_stats(jockey_id);
CREATE INDEX IF NOT EXISTS idx_trainers_trainer_id ON trainers_stats(trainer_id);

-- Create comments for documentation
COMMENT ON TABLE races IS 'Complete race information with all 20 CSV columns preserved';
COMMENT ON TABLE records IS 'Complete race records with all 64 CSV columns including sectional times';
COMMENT ON TABLE horses IS 'Complete horse statistics with all 39 CSV columns';
COMMENT ON TABLE jockeys_stats IS 'Complete jockey statistics with all 28 CSV columns';
COMMENT ON TABLE trainers_stats IS 'Complete trainer statistics with all 28 CSV columns';

-- Create view for race analysis with all data
CREATE OR REPLACE VIEW race_analysis_complete AS
SELECT 
    r.race_id,
    r.race_name,
    r.course,
    r.date,
    r.distance,
    r.race_type,
    COUNT(rec.id) as total_runners,
    AVG(CASE WHEN rec.sp > 0 THEN rec.sp END) as avg_starting_price,
    MAX(CASE WHEN rec.position = 1 THEN h.horse_name END) as winner,
    MAX(CASE WHEN rec.position = 1 THEN j.jockey_name END) as winning_jockey,
    MAX(CASE WHEN rec.position = 1 THEN t.trainer_name END) as winning_trainer
FROM races r
LEFT JOIN records rec ON r.race_id = rec.race_id
LEFT JOIN horses h ON rec.horse_id = h.horse_id
LEFT JOIN jockeys_stats j ON rec.jockey_id::text = j.jockey_id
LEFT JOIN trainers_stats t ON rec.trainer_id::text = t.trainer_id
GROUP BY r.race_id, r.race_name, r.course, r.date, r.distance, r.race_type;
