-- Advanced Racing Metrics Database Schema
-- Horse Racing AI v2.03 - Enhanced Analytics Integration
-- Created: 2025-08-20

-- ===============================================
-- 1. HORSE SPEED RATINGS TABLE
-- ===============================================
-- Stores speed figures, pace ratings, and sectional analysis
CREATE TABLE IF NOT EXISTS horse_speed_ratings (
    id SERIAL PRIMARY KEY,
    horse_id BIGINT NOT NULL,
    race_id BIGINT,
    horse_name VARCHAR(255) NOT NULL,
    race_date DATE NOT NULL,
    
    -- Core Speed Metrics
    speed_figure DECIMAL(5,2) NOT NULL,           -- 0-120 scale speed figure
    pace_rating DECIMAL(5,2),                     -- Pace-adjusted rating
    time_seconds DECIMAL(8,3),                    -- Actual race time
    distance_furlongs DECIMAL(4,2),               -- Race distance
    
    -- Sectional Analysis
    sectional_times JSONB,                        -- Array of sectional splits
    pace_classification VARCHAR(20),              -- 'front_runner', 'mid_pack', 'closer'
    speed_map_position INTEGER,                   -- Position in speed map (1-20)
    
    -- Track & Conditions
    track_condition VARCHAR(20),                  -- 'firm', 'good', 'soft', etc.
    track_variant DECIMAL(4,2) DEFAULT 0.00,     -- Track speed adjustment
    weather_impact DECIMAL(3,2) DEFAULT 1.00,    -- Weather adjustment factor
    
    -- Performance Context
    class_rating VARCHAR(20),                     -- 'class_1', 'class_2', etc.
    weight_carried DECIMAL(5,1),                  -- Weight in kg
    jockey_allowance DECIMAL(3,1) DEFAULT 0.0,   -- Apprentice allowance
    
    -- Calculation Metadata
    calculation_method VARCHAR(50) DEFAULT 'standard',
    confidence_score DECIMAL(3,2) DEFAULT 0.85,  -- Rating confidence (0-1)
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for Performance
    CONSTRAINT fk_speed_horse FOREIGN KEY (horse_id) REFERENCES horses(id),
    CONSTRAINT fk_speed_race FOREIGN KEY (race_id) REFERENCES races(id)
);

-- Speed Ratings Indexes
CREATE INDEX IF NOT EXISTS idx_speed_ratings_horse_date ON horse_speed_ratings(horse_id, race_date DESC);
CREATE INDEX IF NOT EXISTS idx_speed_ratings_figure ON horse_speed_ratings(speed_figure DESC);
CREATE INDEX IF NOT EXISTS idx_speed_ratings_pace ON horse_speed_ratings(pace_classification);
CREATE INDEX IF NOT EXISTS idx_speed_ratings_class ON horse_speed_ratings(class_rating);

-- ===============================================
-- 2. HORSE POWER RATINGS TABLE  
-- ===============================================
-- Class-par based power ratings with adjustments
CREATE TABLE IF NOT EXISTS horse_power_ratings (
    id SERIAL PRIMARY KEY,
    horse_id BIGINT NOT NULL,
    race_id BIGINT,
    horse_name VARCHAR(255) NOT NULL,
    race_date DATE NOT NULL,
    
    -- Core Power Rating
    power_rating DECIMAL(5,2) NOT NULL,           -- 0-140 scale power rating
    base_rating DECIMAL(5,2) NOT NULL,            -- Class-par base rating
    
    -- Adjustment Factors
    class_adjustment DECIMAL(4,2) DEFAULT 0.00,   -- Class level adjustment
    distance_adjustment DECIMAL(4,2) DEFAULT 0.00, -- Distance suitability
    surface_adjustment DECIMAL(4,2) DEFAULT 0.00,  -- Turf/AW preference  
    going_adjustment DECIMAL(4,2) DEFAULT 0.00,    -- Going preference
    weight_adjustment DECIMAL(4,2) DEFAULT 0.00,   -- Weight impact
    draw_adjustment DECIMAL(4,2) DEFAULT 0.00,     -- Draw bias adjustment
    
    -- Performance Context
    race_class VARCHAR(20),                       -- Race classification
    surface_type VARCHAR(10),                     -- 'turf', 'aw', 'dirt'
    going_description VARCHAR(30),                -- Going conditions
    distance_furlongs DECIMAL(4,2),               -- Race distance
    
    -- Recent Form Integration
    last_3_avg DECIMAL(5,2),                      -- Average of last 3 ratings
    form_trend VARCHAR(20),                       -- 'improving', 'declining', 'stable'
    consistency_rating DECIMAL(3,2),              -- Performance consistency (0-1)
    
    -- Calculation Metadata
    rating_confidence DECIMAL(3,2) DEFAULT 0.80,  -- Rating reliability (0-1)
    sample_size INTEGER DEFAULT 1,                -- Number of races in calculation
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_power_horse FOREIGN KEY (horse_id) REFERENCES horses(id),
    CONSTRAINT fk_power_race FOREIGN KEY (race_id) REFERENCES races(id),
    CONSTRAINT chk_power_rating CHECK (power_rating >= 0 AND power_rating <= 140)
);

-- Power Ratings Indexes
CREATE INDEX IF NOT EXISTS idx_power_ratings_horse_date ON horse_power_ratings(horse_id, race_date DESC);
CREATE INDEX IF NOT EXISTS idx_power_ratings_rating ON horse_power_ratings(power_rating DESC);
CREATE INDEX IF NOT EXISTS idx_power_ratings_class ON horse_power_ratings(race_class);
CREATE INDEX IF NOT EXISTS idx_power_ratings_surface ON horse_power_ratings(surface_type);

-- ===============================================
-- 3. ENHANCED FORM SCORES TABLE
-- ===============================================
-- Multi-factor form scoring system
CREATE TABLE IF NOT EXISTS horse_form_scores (
    id SERIAL PRIMARY KEY,
    horse_id BIGINT NOT NULL,
    race_id BIGINT,
    horse_name VARCHAR(255) NOT NULL,
    race_date DATE NOT NULL,
    
    -- Overall Form Score (0-100)
    form_score DECIMAL(5,2) NOT NULL,
    
    -- Component Scores (0-100 each)
    recent_form_score DECIMAL(5,2),               -- Last 5 runs performance
    class_form_score DECIMAL(5,2),                -- Performance at class level
    distance_form_score DECIMAL(5,2),             -- Performance at distance
    surface_form_score DECIMAL(5,2),              -- Surface specialization
    going_form_score DECIMAL(5,2),                -- Going conditions form
    course_form_score DECIMAL(5,2),               -- Course specialization
    
    -- Trend Analysis
    form_trend VARCHAR(20),                       -- 'improving', 'declining', 'peak', 'inconsistent'
    trend_strength DECIMAL(3,2),                  -- Trend confidence (0-1)
    peak_performance_rating DECIMAL(5,2),         -- Best recent rating
    consistency_rating DECIMAL(3,2),              -- Performance reliability
    
    -- Contextual Factors
    days_since_last_run INTEGER,                  -- Fitness/freshness factor
    trainer_form_rating DECIMAL(3,2),             -- Trainer recent form (0-1)
    jockey_form_rating DECIMAL(3,2),              -- Jockey recent form (0-1)
    stable_confidence DECIMAL(3,2),               -- Betting market confidence
    
    -- Performance Indicators
    improvement_indicator DECIMAL(4,2),           -- Expected improvement (+/-)
    class_progression VARCHAR(20),                -- 'rising', 'dropping', 'stable'
    fitness_rating DECIMAL(3,2),                  -- Fitness assessment (0-1)
    
    -- Calculation Metadata
    races_analyzed INTEGER DEFAULT 5,             -- Number of races in analysis
    confidence_level DECIMAL(3,2) DEFAULT 0.75,   -- Score reliability
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_form_horse FOREIGN KEY (horse_id) REFERENCES horses(id),
    CONSTRAINT fk_form_race FOREIGN KEY (race_id) REFERENCES races(id),
    CONSTRAINT chk_form_score CHECK (form_score >= 0 AND form_score <= 100)
);

-- Form Scores Indexes
CREATE INDEX IF NOT EXISTS idx_form_scores_horse_date ON horse_form_scores(horse_id, race_date DESC);
CREATE INDEX IF NOT EXISTS idx_form_scores_score ON horse_form_scores(form_score DESC);
CREATE INDEX IF NOT EXISTS idx_form_scores_trend ON horse_form_scores(form_trend);
CREATE INDEX IF NOT EXISTS idx_form_scores_class ON horse_form_scores(class_progression);

-- ===============================================
-- 4. MONTE CARLO SIMULATIONS TABLE
-- ===============================================
-- Store Monte Carlo simulation results for analysis
CREATE TABLE IF NOT EXISTS monte_carlo_simulations (
    id SERIAL PRIMARY KEY,
    simulation_id VARCHAR(50) NOT NULL,           -- Unique simulation identifier
    race_id BIGINT,
    horse_id BIGINT NOT NULL,
    horse_name VARCHAR(255) NOT NULL,
    race_date DATE NOT NULL,
    
    -- Simulation Parameters
    simulation_runs INTEGER DEFAULT 10000,        -- Number of Monte Carlo runs
    simulation_method VARCHAR(30) DEFAULT 'standard',
    
    -- Probability Results
    win_probability DECIMAL(6,4) NOT NULL,        -- Win probability (0-1)
    place_probability DECIMAL(6,4),               -- Place probability (0-1)  
    show_probability DECIMAL(6,4),                -- Show probability (0-1)
    
    -- Position Analysis
    expected_position DECIMAL(4,2),               -- Average finishing position
    position_variance DECIMAL(4,2),               -- Position variability
    confidence_interval_lower DECIMAL(4,2),       -- 95% CI lower bound
    confidence_interval_upper DECIMAL(4,2),       -- 95% CI upper bound
    
    -- Value Analysis
    fair_odds DECIMAL(8,4),                       -- Calculated fair odds
    market_odds DECIMAL(8,4),                     -- Actual market odds
    value_rating VARCHAR(20),                     -- 'Strong Value', 'Some Value', 'Fair', 'Overbet'
    edge_percentage DECIMAL(5,2),                 -- Expected edge percentage
    
    -- Statistical Measures
    z_score DECIMAL(6,3),                         -- Performance z-score
    confidence_score DECIMAL(3,2),                -- Prediction confidence (0-1)
    volatility_index DECIMAL(3,2),                -- Performance volatility
    
    -- Betting Recommendations
    bet_type VARCHAR(20),                         -- 'win', 'place', 'show', 'avoid'
    stake_recommendation DECIMAL(3,2),            -- Suggested stake (0-1)
    expected_value DECIMAL(6,3),                  -- Expected value calculation
    
    -- Performance Tracking
    actual_result INTEGER,                        -- Actual finishing position (if known)
    result_accuracy VARCHAR(20),                  -- 'accurate', 'close', 'poor'
    
    -- Metadata
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_monte_horse FOREIGN KEY (horse_id) REFERENCES horses(id),
    CONSTRAINT fk_monte_race FOREIGN KEY (race_id) REFERENCES races(id),
    CONSTRAINT chk_win_prob CHECK (win_probability >= 0 AND win_probability <= 1),
    CONSTRAINT chk_place_prob CHECK (place_probability >= 0 AND place_probability <= 1)
);

-- Monte Carlo Indexes
CREATE INDEX IF NOT EXISTS idx_monte_simulation_id ON monte_carlo_simulations(simulation_id);
CREATE INDEX IF NOT EXISTS idx_monte_horse_date ON monte_carlo_simulations(horse_id, race_date DESC);
CREATE INDEX IF NOT EXISTS idx_monte_win_prob ON monte_carlo_simulations(win_probability DESC);
CREATE INDEX IF NOT EXISTS idx_monte_value ON monte_carlo_simulations(value_rating);
CREATE INDEX IF NOT EXISTS idx_monte_edge ON monte_carlo_simulations(edge_percentage DESC);

-- ===============================================
-- 5. ADVANCED METRICS SUMMARY TABLE
-- ===============================================
-- Consolidated view of all advanced metrics per horse/race
CREATE TABLE IF NOT EXISTS horse_advanced_metrics (
    id SERIAL PRIMARY KEY,
    horse_id BIGINT NOT NULL,
    race_id BIGINT,
    horse_name VARCHAR(255) NOT NULL,
    race_date DATE NOT NULL,
    
    -- Linked Metric IDs
    speed_rating_id INTEGER,
    power_rating_id INTEGER,
    form_score_id INTEGER,
    monte_carlo_id INTEGER,
    
    -- Quick Access Summary
    overall_rating DECIMAL(5,2),                  -- Combined rating (0-100)
    confidence_level DECIMAL(3,2),                -- Overall confidence
    recommendation VARCHAR(30),                   -- 'Strong Pick', 'Value Bet', 'Avoid', etc.
    
    -- Key Metrics Summary
    speed_figure_summary DECIMAL(5,2),
    power_rating_summary DECIMAL(5,2),
    form_score_summary DECIMAL(5,2),
    win_probability_summary DECIMAL(6,4),
    
    -- Last Updated
    metrics_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_advanced_horse FOREIGN KEY (horse_id) REFERENCES horses(id),
    CONSTRAINT fk_advanced_race FOREIGN KEY (race_id) REFERENCES races(id),
    CONSTRAINT fk_speed_ref FOREIGN KEY (speed_rating_id) REFERENCES horse_speed_ratings(id),
    CONSTRAINT fk_power_ref FOREIGN KEY (power_rating_id) REFERENCES horse_power_ratings(id),
    CONSTRAINT fk_form_ref FOREIGN KEY (form_score_id) REFERENCES horse_form_scores(id),
    CONSTRAINT fk_monte_ref FOREIGN KEY (monte_carlo_id) REFERENCES monte_carlo_simulations(id),
    UNIQUE(horse_id, race_id)
);

-- Advanced Metrics Summary Indexes
CREATE INDEX IF NOT EXISTS idx_advanced_horse_date ON horse_advanced_metrics(horse_id, race_date DESC);
CREATE INDEX IF NOT EXISTS idx_advanced_overall ON horse_advanced_metrics(overall_rating DESC);
CREATE INDEX IF NOT EXISTS idx_advanced_recommendation ON horse_advanced_metrics(recommendation);

-- ===============================================
-- 6. PERFORMANCE TRACKING VIEW
-- ===============================================
-- View for tracking prediction accuracy over time
CREATE OR REPLACE VIEW advanced_metrics_performance AS
SELECT 
    m.horse_name,
    m.race_date,
    m.win_probability,
    m.expected_position,
    m.value_rating,
    m.actual_result,
    CASE 
        WHEN m.actual_result = 1 AND m.win_probability > 0.3 THEN 'WIN_PREDICTED'
        WHEN m.actual_result <= 3 AND m.place_probability > 0.5 THEN 'PLACE_PREDICTED'
        WHEN m.actual_result IS NOT NULL THEN 'MISS'
        ELSE 'PENDING'
    END AS prediction_outcome,
    s.speed_figure,
    p.power_rating,
    f.form_score
FROM monte_carlo_simulations m
LEFT JOIN horse_speed_ratings s ON m.horse_id = s.horse_id AND m.race_date = s.race_date
LEFT JOIN horse_power_ratings p ON m.horse_id = p.horse_id AND m.race_date = p.race_date  
LEFT JOIN horse_form_scores f ON m.horse_id = f.horse_id AND m.race_date = f.race_date
ORDER BY m.race_date DESC, m.win_probability DESC;

-- ===============================================
-- COMMENTS AND DOCUMENTATION
-- ===============================================

COMMENT ON TABLE horse_speed_ratings IS 'Speed figures and pace analysis for each horse performance';
COMMENT ON TABLE horse_power_ratings IS 'Class-par based power ratings with contextual adjustments';
COMMENT ON TABLE horse_form_scores IS 'Multi-factor form analysis and trend scoring';
COMMENT ON TABLE monte_carlo_simulations IS 'Monte Carlo simulation results and betting analysis';
COMMENT ON TABLE horse_advanced_metrics IS 'Consolidated summary of all advanced racing metrics';

-- Schema creation completed
SELECT 'Advanced Racing Metrics Schema Created Successfully!' as status;
