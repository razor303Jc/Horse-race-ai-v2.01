-- Results Database Schema
-- ========================
-- Database for results data (after races happen)

-- Create the results database
CREATE DATABASE results_horse_racing_db;

-- Connect to results database
\c results_horse_racing_db;

-- Create tables for results data
CREATE TABLE IF NOT EXISTS result_races (
    race_id INTEGER PRIMARY KEY,
    race_number INTEGER,
    race_time TIME,
    course_id INTEGER,
    course VARCHAR(100),
    race_type VARCHAR(50),
    date DATE,
    race_name VARCHAR(200),
    class VARCHAR(20),
    years VARCHAR(50),
    distance VARCHAR(20),
    surface VARCHAR(100),
    prize VARCHAR(20),
    runners INTEGER,
    going VARCHAR(50),
    winner VARCHAR(100),
    winning_time VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS result_horses (
    horse_id SERIAL PRIMARY KEY,
    horse_name VARCHAR(100) NOT NULL,
    age INTEGER,
    sex VARCHAR(10),
    color VARCHAR(50),
    sire VARCHAR(100),
    dam VARCHAR(100),
    owner VARCHAR(100),
    breeder VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS result_jockeys (
    jockey_id SERIAL PRIMARY KEY,
    jockey_name VARCHAR(100) NOT NULL,
    wins INTEGER DEFAULT 0,
    runs INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0.00,
    prize_money DECIMAL(12,2) DEFAULT 0.00,
    last_14_days_wins INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS result_trainers (
    trainer_id SERIAL PRIMARY KEY,
    trainer_name VARCHAR(100) NOT NULL,
    wins INTEGER DEFAULT 0,
    runs INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0.00,
    prize_money DECIMAL(12,2) DEFAULT 0.00,
    last_14_days_wins INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS result_records (
    record_id SERIAL PRIMARY KEY,
    race_id INTEGER NOT NULL,
    horse_name VARCHAR(100),
    jockey VARCHAR(100),
    trainer VARCHAR(100),
    position INTEGER,
    finishing_position INTEGER,
    starting_price DECIMAL(8,2),
    weight VARCHAR(20),
    age INTEGER,
    form VARCHAR(20),
    time_behind VARCHAR(20),
    prize_won DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (race_id) REFERENCES result_races(race_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_result_records_race_id ON result_records(race_id);
CREATE INDEX IF NOT EXISTS idx_result_records_horse_name ON result_records(horse_name);
CREATE INDEX IF NOT EXISTS idx_result_records_position ON result_records(position);
CREATE INDEX IF NOT EXISTS idx_result_races_date ON result_races(date);
CREATE INDEX IF NOT EXISTS idx_result_races_course ON result_races(course);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE results_horse_racing_db TO horse_racing;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO horse_racing;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO horse_racing;
