-- =====================================================================
-- CREATE UNIQUE REFERENCE TABLES FOR HORSES, JOCKEYS, AND TRAINERS
-- =====================================================================
-- This script creates unique lookup tables from existing results data
-- to be used as reference when processing new CSV uploads

-- Connect to results database
\c results_horse_racing_db;

-- =====================================================================
-- 1. CREATE UNIQUE HORSES TABLE
-- =====================================================================

-- Create unique horses reference table
CREATE TABLE IF NOT EXISTS unique_horses (
    horse_id SERIAL PRIMARY KEY,
    horse_name VARCHAR(100) NOT NULL UNIQUE,
    first_seen_date DATE,
    total_races INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert unique horses from existing result_horses table
INSERT INTO unique_horses (horse_name, first_seen_date, total_races)
SELECT 
    horse_name,
    MIN(created_at::DATE) as first_seen_date,
    COUNT(*) as total_races
FROM result_horses 
WHERE horse_name IS NOT NULL 
    AND trim(horse_name) != ''
GROUP BY horse_name
ON CONFLICT (horse_name) DO NOTHING;

-- Also get horses from result_records if they're not in result_horses
INSERT INTO unique_horses (horse_name, first_seen_date, total_races)
SELECT 
    horse_name,
    MIN(created_at::DATE) as first_seen_date,
    COUNT(*) as total_races
FROM result_records 
WHERE horse_name IS NOT NULL 
    AND trim(horse_name) != ''
    AND horse_name NOT IN (SELECT horse_name FROM unique_horses)
GROUP BY horse_name
ON CONFLICT (horse_name) DO NOTHING;

-- =====================================================================
-- 2. CREATE UNIQUE JOCKEYS TABLE
-- =====================================================================

-- Create unique jockeys reference table
CREATE TABLE IF NOT EXISTS unique_jockeys (
    jockey_id SERIAL PRIMARY KEY,
    jockey_name VARCHAR(100) NOT NULL UNIQUE,
    first_seen_date DATE,
    total_rides INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert unique jockeys from existing result_jockeys table
INSERT INTO unique_jockeys (jockey_name, first_seen_date, total_rides, total_wins, win_rate)
SELECT 
    jockey_name,
    MIN(created_at::DATE) as first_seen_date,
    COALESCE(MAX(runs), 0) as total_rides,
    COALESCE(MAX(wins), 0) as total_wins,
    COALESCE(MAX(win_rate), 0.00) as win_rate
FROM result_jockeys 
WHERE jockey_name IS NOT NULL 
    AND trim(jockey_name) != ''
GROUP BY jockey_name
ON CONFLICT (jockey_name) DO NOTHING;

-- Also get jockeys from result_records if they're not in result_jockeys
INSERT INTO unique_jockeys (jockey_name, first_seen_date, total_rides)
SELECT 
    jockey,
    MIN(created_at::DATE) as first_seen_date,
    COUNT(*) as total_rides
FROM result_records 
WHERE jockey IS NOT NULL 
    AND trim(jockey) != ''
    AND jockey NOT IN (SELECT jockey_name FROM unique_jockeys)
GROUP BY jockey
ON CONFLICT (jockey_name) DO NOTHING;

-- =====================================================================
-- 3. CREATE UNIQUE TRAINERS TABLE
-- =====================================================================

-- Create unique trainers reference table
CREATE TABLE IF NOT EXISTS unique_trainers (
    trainer_id SERIAL PRIMARY KEY,
    trainer_name VARCHAR(100) NOT NULL UNIQUE,
    first_seen_date DATE,
    total_horses INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert unique trainers from existing result_trainers table
INSERT INTO unique_trainers (trainer_name, first_seen_date, total_horses, total_wins, win_rate)
SELECT 
    trainer_name,
    MIN(created_at::DATE) as first_seen_date,
    COALESCE(MAX(runs), 0) as total_horses,
    COALESCE(MAX(wins), 0) as total_wins,
    COALESCE(MAX(win_rate), 0.00) as win_rate
FROM result_trainers 
WHERE trainer_name IS NOT NULL 
    AND trim(trainer_name) != ''
GROUP BY trainer_name
ON CONFLICT (trainer_name) DO NOTHING;

-- Also get trainers from result_records if they're not in result_trainers
INSERT INTO unique_trainers (trainer_name, first_seen_date, total_horses)
SELECT 
    trainer,
    MIN(created_at::DATE) as first_seen_date,
    COUNT(*) as total_horses
FROM result_records 
WHERE trainer IS NOT NULL 
    AND trim(trainer) != ''
    AND trainer NOT IN (SELECT trainer_name FROM unique_trainers)
GROUP BY trainer
ON CONFLICT (trainer_name) DO NOTHING;

-- =====================================================================
-- 4. CREATE INDEXES FOR PERFORMANCE
-- =====================================================================

-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_unique_horses_name ON unique_horses(horse_name);
CREATE INDEX IF NOT EXISTS idx_unique_jockeys_name ON unique_jockeys(jockey_name);
CREATE INDEX IF NOT EXISTS idx_unique_trainers_name ON unique_trainers(trainer_name);

-- =====================================================================
-- 5. VERIFICATION QUERIES
-- =====================================================================

-- Display summary of unique entities
SELECT 'HORSES' as entity_type, COUNT(*) as unique_count FROM unique_horses
UNION ALL
SELECT 'JOCKEYS' as entity_type, COUNT(*) as unique_count FROM unique_jockeys
UNION ALL
SELECT 'TRAINERS' as entity_type, COUNT(*) as unique_count FROM unique_trainers;

-- Sample data from each table
SELECT 'SAMPLE HORSES:' as info;
SELECT horse_id, horse_name, first_seen_date, total_races 
FROM unique_horses 
ORDER BY total_races DESC 
LIMIT 10;

SELECT 'SAMPLE JOCKEYS:' as info;
SELECT jockey_id, jockey_name, first_seen_date, total_rides, win_rate 
FROM unique_jockeys 
ORDER BY total_rides DESC 
LIMIT 10;

SELECT 'SAMPLE TRAINERS:' as info;
SELECT trainer_id, trainer_name, first_seen_date, total_horses, win_rate 
FROM unique_trainers 
ORDER BY total_horses DESC 
LIMIT 10;

-- =====================================================================
-- 6. GRANT PERMISSIONS
-- =====================================================================

-- Grant permissions on new tables
GRANT ALL PRIVILEGES ON unique_horses TO horse_racing;
GRANT ALL PRIVILEGES ON unique_jockeys TO horse_racing;
GRANT ALL PRIVILEGES ON unique_trainers TO horse_racing;
GRANT ALL PRIVILEGES ON unique_horses_horse_id_seq TO horse_racing;
GRANT ALL PRIVILEGES ON unique_jockeys_jockey_id_seq TO horse_racing;
GRANT ALL PRIVILEGES ON unique_trainers_trainer_id_seq TO horse_racing;

-- =====================================================================
-- COMPLETION MESSAGE
-- =====================================================================

SELECT 
    'UNIQUE REFERENCE TABLES CREATED SUCCESSFULLY!' as status,
    'Tables: unique_horses, unique_jockeys, unique_trainers' as tables_created,
    'Ready for CSV processing with duplicate prevention' as next_step;
