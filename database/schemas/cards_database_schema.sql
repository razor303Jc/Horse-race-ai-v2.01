-- Cards Database Schema
-- =====================
-- Database for race card data (before races happen)

-- Create the cards database
CREATE DATABASE cards_horse_racing_db;

-- Connect to cards database
\c cards_horse_racing_db;

-- Create tables for race card data
CREATE TABLE IF NOT EXISTS card_races (
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
    runners_racecard INTEGER,
    runners INTEGER,
    draw INTEGER,
    ew_racecard INTEGER,
    ew INTEGER,
    places_ew_racecard INTEGER,
    places_ew INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS card_horses (
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

CREATE TABLE IF NOT EXISTS card_jockeys (
    jockey_id SERIAL PRIMARY KEY,
    jockey_name VARCHAR(100) NOT NULL,
    wins INTEGER DEFAULT 0,
    runs INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0.00,
    prize_money DECIMAL(12,2) DEFAULT 0.00,
    last_14_days_wins INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS card_trainers (
    trainer_id SERIAL PRIMARY KEY,
    trainer_name VARCHAR(100) NOT NULL,
    wins INTEGER DEFAULT 0,
    runs INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0.00,
    prize_money DECIMAL(12,2) DEFAULT 0.00,
    last_14_days_wins INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS card_records (
    record_id INTEGER PRIMARY KEY,
    race_id INTEGER NOT NULL,
    horse_name VARCHAR(100),
    jockey VARCHAR(100),
    trainer VARCHAR(100),
    position INTEGER,
    starting_price DECIMAL(8,2),
    weight VARCHAR(20),
    age INTEGER,
    form VARCHAR(20),
    extra TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (race_id) REFERENCES card_races(race_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_card_records_race_id ON card_records(race_id);
CREATE INDEX IF NOT EXISTS idx_card_records_horse_name ON card_records(horse_name);
CREATE INDEX IF NOT EXISTS idx_card_races_date ON card_races(date);
CREATE INDEX IF NOT EXISTS idx_card_races_course ON card_races(course);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE cards_horse_racing_db TO horse_racing;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO horse_racing;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO horse_racing;
