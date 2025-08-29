-- Advanced Racing Metrics Database Schema
-- Created: August 24, 2025
-- Purpose: Store advanced AI ratings, speed analysis, Monte Carlo simulations, and performance tracking

-- 🔥 Power Ratings Table
CREATE TABLE horse_power_ratings (
    id SERIAL PRIMARY KEY,
    horse_id BIGINT NOT NULL,
    horse_name VARCHAR(255) NOT NULL,
    jockey_id BIGINT,
    jockey_name VARCHAR(255),
    trainer_id BIGINT,
    trainer_name VARCHAR(255),
    race_id BIGINT NOT NULL,
    calculation_date DATE DEFAULT CURRENT_DATE,

    -- Power Rating Components (0-150 scale)
    base_power_rating REAL NOT NULL,
    speed_component REAL,
    form_component REAL,
    class_component REAL,
    consistency_component REAL,

    -- Adjustments
    age_adjustment REAL,
    weight_adjustment REAL,
    track_condition_adjustment REAL,
    distance_adjustment REAL,

    -- Final Rating
    final_power_rating REAL NOT NULL,
    rating_confidence REAL, -- 0-1 confidence score

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ⚡ Speed & Pace Ratings Table
CREATE TABLE horse_speed_pace_ratings (
    id SERIAL PRIMARY KEY,
    horse_id BIGINT NOT NULL,
    horse_name VARCHAR(255) NOT NULL,
    race_id BIGINT NOT NULL,
    calculation_date DATE DEFAULT CURRENT_DATE,

    -- Speed Metrics (0-120 scale)
    speed_rating REAL NOT NULL,
    pace_rating REAL NOT NULL,
    finishing_speed_index REAL,

    -- Pace Classification
    pace_style VARCHAR(50), -- 'front_runner', 'mid_pack', 'closer'
    early_pace_rating REAL,
    middle_pace_rating REAL,
    late_pace_rating REAL,

    -- Sectional Analysis
    sectional_times JSON, -- Store sectional breakdowns
    pace_versatility_score REAL, -- Ability to adapt pace

    -- Track Specific
    track_bias_factor REAL,
    going_suitability REAL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🎲 Monte Carlo Results Table
CREATE TABLE monte_carlo_simulations (
    id SERIAL PRIMARY KEY,
    simulation_session_id UUID NOT NULL,
    race_id BIGINT NOT NULL,
    horse_id BIGINT NOT NULL,
    horse_name VARCHAR(255) NOT NULL,
    simulation_date DATE DEFAULT CURRENT_DATE,

    -- Simulation Parameters
    simulations_run INTEGER DEFAULT 10000,
    baseline_variance REAL,
    form_impact REAL,
    consistency_impact REAL,

    -- Performance Profile
    mean_rating REAL NOT NULL,
    std_deviation REAL,
    z_score REAL,
    consistency_factor REAL,
    form_trend REAL, -- -1 to 1

    -- Probability Results
    win_probability REAL,
    place_probability REAL, -- Top 3
    show_probability REAL,  -- Top 4
    average_position REAL,

    -- Confidence Intervals
    performance_ci_lower REAL, -- 2.5th percentile
    performance_ci_upper REAL, -- 97.5th percentile

    -- Simulation Quality
    simulation_reliability REAL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🏇 Enhanced Jockey Performance Tracking
CREATE TABLE jockey_performance_metrics (
    id SERIAL PRIMARY KEY,
    jockey_id BIGINT UNIQUE NOT NULL,
    jockey_name VARCHAR(255) NOT NULL,

    -- Career Statistics
    total_rides INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    win_percentage REAL DEFAULT 0.0,

    -- Seasonal Performance
    season_rides INTEGER DEFAULT 0,
    season_wins INTEGER DEFAULT 0,
    season_win_percentage REAL DEFAULT 0.0,

    -- Recent Form (Last 30 days)
    recent_rides INTEGER DEFAULT 0,
    recent_wins INTEGER DEFAULT 0,
    recent_win_percentage REAL DEFAULT 0.0,

    -- Specialty Metrics
    class_1_win_rate REAL DEFAULT 0.0,
    handicap_win_rate REAL DEFAULT 0.0,
    heavy_going_win_rate REAL DEFAULT 0.0,

    -- Financial Performance
    total_prize_money DECIMAL(15,2),
    average_prize_per_ride DECIMAL(15,2),

    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 👨‍🏫 Enhanced Trainer Performance Tracking
CREATE TABLE trainer_performance_metrics (
    id SERIAL PRIMARY KEY,
    trainer_id BIGINT UNIQUE NOT NULL,
    trainer_name VARCHAR(255) NOT NULL,

    -- Career Statistics
    total_runners INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    win_percentage REAL DEFAULT 0.0,

    -- Seasonal Performance
    season_runners INTEGER DEFAULT 0,
    season_wins INTEGER DEFAULT 0,
    season_win_percentage REAL DEFAULT 0.0,

    -- Strike Rate Analysis
    strike_rate_last_14_days REAL DEFAULT 0.0,
    strike_rate_last_30_days REAL DEFAULT 0.0,
    strike_rate_last_90_days REAL DEFAULT 0.0,

    -- Specialty Success Rates
    first_time_out_success_rate REAL DEFAULT 0.0,
    handicap_success_rate REAL DEFAULT 0.0,
    class_1_success_rate REAL DEFAULT 0.0,

    -- Financial Performance
    total_prize_money DECIMAL(15,2),
    roi_to_stakeholders REAL,

    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 💰 Performance Tracking & ROI Table
CREATE TABLE betting_performance_tracker (
    id SERIAL PRIMARY KEY,
    selection_date DATE NOT NULL,
    race_id BIGINT NOT NULL,
    horse_name VARCHAR(255) NOT NULL,

    -- Selection Details
    ai_prediction_probability REAL,
    confidence_level VARCHAR(20),
    recommended_stake DECIMAL(10,2),
    value_rating REAL, -- AI calculated value

    -- Market Information
    starting_price_decimal REAL,
    starting_price_fractional VARCHAR(20),
    market_rank INTEGER,

    -- Betting Strategy Applied
    strategy_used VARCHAR(100), -- 'value_betting', 'level_stakes', 'kelly_criterion'
    actual_stake_placed DECIMAL(10,2),

    -- Results
    finishing_position INTEGER,
    race_result VARCHAR(20), -- 'WIN', 'PLACE', 'SHOW', 'UNPLACED'
    payout_decimal REAL,

    -- Financial Outcome
    gross_return DECIMAL(10,2),
    net_profit_loss DECIMAL(10,2),
    roi_percentage REAL,

    -- Cumulative Tracking
    running_total_stakes DECIMAL(15,2),
    running_total_returns DECIMAL(15,2),
    running_profit_loss DECIMAL(15,2),
    running_roi REAL,

    -- Performance Metrics
    hit_rate_contribution BOOLEAN, -- Did this contribute to hit rate?
    value_accuracy REAL, -- How accurate was our value assessment?

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance optimization
CREATE INDEX idx_power_ratings_horse_id ON horse_power_ratings(horse_id);
CREATE INDEX idx_power_ratings_race_id ON horse_power_ratings(race_id);
CREATE INDEX idx_power_ratings_date ON horse_power_ratings(calculation_date);
CREATE INDEX idx_power_ratings_final_rating ON horse_power_ratings(final_power_rating DESC);

CREATE INDEX idx_speed_pace_horse_id ON horse_speed_pace_ratings(horse_id);
CREATE INDEX idx_speed_pace_race_id ON horse_speed_pace_ratings(race_id);
CREATE INDEX idx_speed_pace_date ON horse_speed_pace_ratings(calculation_date);
CREATE INDEX idx_speed_pace_rating ON horse_speed_pace_ratings(speed_rating DESC);

CREATE INDEX idx_monte_carlo_session ON monte_carlo_simulations(simulation_session_id);
CREATE INDEX idx_monte_carlo_race_id ON monte_carlo_simulations(race_id);
CREATE INDEX idx_monte_carlo_horse_id ON monte_carlo_simulations(horse_id);
CREATE INDEX idx_monte_carlo_win_prob ON monte_carlo_simulations(win_probability DESC);

CREATE INDEX idx_jockey_metrics_id ON jockey_performance_metrics(jockey_id);
CREATE INDEX idx_jockey_metrics_win_rate ON jockey_performance_metrics(win_percentage DESC);

CREATE INDEX idx_trainer_metrics_id ON trainer_performance_metrics(trainer_id);
CREATE INDEX idx_trainer_metrics_win_rate ON trainer_performance_metrics(win_percentage DESC);

CREATE INDEX idx_betting_performance_date ON betting_performance_tracker(selection_date);
CREATE INDEX idx_betting_performance_race ON betting_performance_tracker(race_id);
CREATE INDEX idx_betting_performance_roi ON betting_performance_tracker(roi_percentage DESC);

-- Create views for common reporting queries
CREATE VIEW v_latest_power_ratings AS
SELECT DISTINCT ON (horse_id, race_id) *
FROM horse_power_ratings
ORDER BY horse_id, race_id, created_at DESC;

CREATE VIEW v_latest_speed_ratings AS
SELECT DISTINCT ON (horse_id, race_id) *
FROM horse_speed_pace_ratings
ORDER BY horse_id, race_id, created_at DESC;

CREATE VIEW v_top_jockeys AS
SELECT jockey_name, win_percentage, recent_win_percentage, total_rides, total_wins
FROM jockey_performance_metrics
WHERE total_rides >= 10
ORDER BY win_percentage DESC;

CREATE VIEW v_top_trainers AS
SELECT trainer_name, win_percentage, season_win_percentage, total_runners, total_wins
FROM trainer_performance_metrics
WHERE total_runners >= 10
ORDER BY win_percentage DESC;

-- Performance summary view
CREATE VIEW v_betting_performance_summary AS
SELECT 
    COUNT(*) as total_selections,
    AVG(roi_percentage) as average_roi,
    SUM(CASE WHEN race_result = 'WIN' THEN 1 ELSE 0 END) as total_wins,
    ROUND(100.0 * SUM(CASE WHEN race_result = 'WIN' THEN 1 ELSE 0 END) / COUNT(*), 2) as hit_rate,
    SUM(net_profit_loss) as total_profit_loss,
    MAX(selection_date) as last_selection_date
FROM betting_performance_tracker;

COMMENT ON DATABASE advanced_racing_metrics_db IS 'Advanced AI horse racing metrics and performance tracking database';
COMMENT ON TABLE horse_power_ratings IS 'Comprehensive power ratings with component breakdown and adjustments';
COMMENT ON TABLE horse_speed_pace_ratings IS 'Speed and pace analysis with sectional breakdowns';
COMMENT ON TABLE monte_carlo_simulations IS 'Monte Carlo simulation results with probability distributions';
COMMENT ON TABLE jockey_performance_metrics IS 'Enhanced jockey performance tracking and statistics';
COMMENT ON TABLE trainer_performance_metrics IS 'Enhanced trainer performance tracking and statistics';
COMMENT ON TABLE betting_performance_tracker IS 'Complete betting performance and ROI tracking';
