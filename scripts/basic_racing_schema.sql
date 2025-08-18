-- Basic Racing Database Schema for Massive Dataset Generation
-- This creates the minimum required tables for race and participant data

-- Races table
CREATE TABLE IF NOT EXISTS races (
    race_id SERIAL PRIMARY KEY,
    race_number INTEGER NOT NULL,
    race_time VARCHAR(10) NOT NULL,
    course VARCHAR(255) NOT NULL,
    race_type VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    race_name VARCHAR(255) NOT NULL,
    class_level VARCHAR(50),
    years VARCHAR(20),
    distance VARCHAR(20),
    surface VARCHAR(50),
    field_size INTEGER,
    prize_money INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Race participants table
CREATE TABLE IF NOT EXISTS race_participants (
    id SERIAL PRIMARY KEY,
    race_id INTEGER REFERENCES races(race_id) ON DELETE CASCADE,
    horse_name VARCHAR(255) NOT NULL,
    jockey_name VARCHAR(255) NOT NULL,
    trainer_name VARCHAR(255) NOT NULL,
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_races_date ON races(date);
CREATE INDEX IF NOT EXISTS idx_races_course ON races(course);
CREATE INDEX IF NOT EXISTS idx_races_race_type ON races(race_type);
CREATE INDEX IF NOT EXISTS idx_participants_race_id ON race_participants(race_id);
CREATE INDEX IF NOT EXISTS idx_participants_horse_name ON race_participants(horse_name);
CREATE INDEX IF NOT EXISTS idx_participants_jockey_name ON race_participants(jockey_name);
CREATE INDEX IF NOT EXISTS idx_participants_trainer_name ON race_participants(trainer_name);
CREATE INDEX IF NOT EXISTS idx_participants_finished_position ON race_participants(finished_position);

-- Additional useful indexes for ML training
CREATE INDEX IF NOT EXISTS idx_races_distance ON races(distance);
CREATE INDEX IF NOT EXISTS idx_races_surface ON races(surface);
CREATE INDEX IF NOT EXISTS idx_participants_win_odds ON race_participants(win_odds);
CREATE INDEX IF NOT EXISTS idx_participants_horse_age ON race_participants(horse_age);

-- View for easy querying of race results with participants
CREATE OR REPLACE VIEW race_results AS
SELECT 
    r.race_id,
    r.race_number,
    r.race_time,
    r.course,
    r.race_type,
    r.date,
    r.race_name,
    r.class_level,
    r.years,
    r.distance,
    r.surface,
    r.field_size,
    r.prize_money,
    rp.horse_name,
    rp.jockey_name,
    rp.trainer_name,
    rp.horse_weight_kg,
    rp.horse_age,
    rp.draw,
    rp.handicap_weight,
    rp.win_odds,
    rp.place_odds,
    rp.barrier,
    rp.finished_position,
    rp.margin,
    rp.time_seconds,
    rp.prize_money as participant_prize_money,
    CASE 
        WHEN rp.finished_position = 1 THEN TRUE 
        ELSE FALSE 
    END as won_race,
    CASE 
        WHEN rp.finished_position <= 3 THEN TRUE 
        ELSE FALSE 
    END as placed
FROM races r
LEFT JOIN race_participants rp ON r.race_id = rp.race_id
ORDER BY r.date DESC, r.race_time, rp.finished_position;

-- Summary statistics view
CREATE OR REPLACE VIEW race_statistics AS
SELECT 
    COUNT(*) as total_races,
    COUNT(DISTINCT course) as unique_courses,
    COUNT(DISTINCT race_type) as unique_race_types,
    MIN(date) as earliest_race,
    MAX(date) as latest_race,
    AVG(field_size) as avg_field_size,
    SUM(prize_money) as total_prize_money,
    (SELECT COUNT(*) FROM race_participants) as total_participants
FROM races;

-- Participant performance summary view
CREATE OR REPLACE VIEW participant_performance AS
SELECT 
    horse_name,
    jockey_name,
    trainer_name,
    COUNT(*) as total_starts,
    COUNT(CASE WHEN finished_position = 1 THEN 1 END) as wins,
    COUNT(CASE WHEN finished_position <= 3 THEN 1 END) as places,
    ROUND(COUNT(CASE WHEN finished_position = 1 THEN 1 END) * 100.0 / COUNT(*), 2) as win_percentage,
    ROUND(COUNT(CASE WHEN finished_position <= 3 THEN 1 END) * 100.0 / COUNT(*), 2) as place_percentage,
    ROUND(AVG(win_odds), 2) as avg_win_odds,
    SUM(prize_money) as total_prize_money
FROM race_participants
WHERE finished_position IS NOT NULL
GROUP BY horse_name, jockey_name, trainer_name
HAVING COUNT(*) >= 3  -- Only show participants with 3+ starts
ORDER BY win_percentage DESC, total_starts DESC;

COMMIT;
