-- Advanced Racing Metrics Database Schema (Corrected)
-- Horse Racing AI v2.03 - Enhanced Analytics Integration  
-- Created: 2025-08-20

-- Drop existing tables if they exist (for clean creation)
DROP TABLE IF EXISTS horse_advanced_metrics CASCADE;
DROP TABLE IF EXISTS monte_carlo_simulations CASCADE;
DROP TABLE IF EXISTS horse_form_scores CASCADE;
DROP TABLE IF EXISTS horse_power_ratings CASCADE;
DROP TABLE IF EXISTS horse_speed_ratings CASCADE;

-- ===============================================
-- 1. HORSE SPEED RATINGS TABLE
-- ===============================================
CREATE TABLE horse_speed_ratings (
    id SERIAL PRIMARY KEY,
    horse_id BIGINT NOT NULL,
    race_id INTEGER,
    horse_name VARCHAR(255) NOT NULL,
    race_date DATE NOT NULL,
    
    -- Core Speed Metrics
    speed_figure DECIMAL(5,2) NOT NULL,           
    pace_rating DECIMAL(5,2),                     
    time_seconds DECIMAL(8,3),                    
    distance_furlongs DECIMAL(4,2),               
    
    -- Sectional Analysis
    sectional_times JSONB,                        
    pace_classification VARCHAR(20),              
    speed_map_position INTEGER,                   
    
    -- Track & Conditions
    track_condition VARCHAR(20),                  
    track_variant DECIMAL(4,2) DEFAULT 0.00,     
    weather_impact DECIMAL(3,2) DEFAULT 1.00,    
    
    -- Performance Context
    class_rating VARCHAR(20),                     
    weight_carried DECIMAL(5,1),                  
    jockey_allowance DECIMAL(3,1) DEFAULT 0.0,   
    
    -- Calculation Metadata
    calculation_method VARCHAR(50) DEFAULT 'standard',
    confidence_score DECIMAL(3,2) DEFAULT 0.85,  
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys (corrected references)
    CONSTRAINT fk_speed_horse FOREIGN KEY (horse_id) REFERENCES horses(horse_id),
    CONSTRAINT fk_speed_race FOREIGN KEY (race_id) REFERENCES races(id)
);

-- ===============================================
-- 2. HORSE POWER RATINGS TABLE  
-- ===============================================
CREATE TABLE horse_power_ratings (
    id SERIAL PRIMARY KEY,
    horse_id BIGINT NOT NULL,
    race_id INTEGER,
    horse_name VARCHAR(255) NOT NULL,
    race_date DATE NOT NULL,
    
    -- Core Power Rating
    power_rating DECIMAL(5,2) NOT NULL,           
    base_rating DECIMAL(5,2) NOT NULL,            
    
    -- Adjustment Factors
    class_adjustment DECIMAL(4,2) DEFAULT 0.00,   
    distance_adjustment DECIMAL(4,2) DEFAULT 0.00, 
    surface_adjustment DECIMAL(4,2) DEFAULT 0.00,  
    going_adjustment DECIMAL(4,2) DEFAULT 0.00,    
    weight_adjustment DECIMAL(4,2) DEFAULT 0.00,   
    draw_adjustment DECIMAL(4,2) DEFAULT 0.00,     
    
    -- Performance Context
    race_class VARCHAR(20),                       
    surface_type VARCHAR(10),                     
    going_description VARCHAR(30),                
    distance_furlongs DECIMAL(4,2),               
    
    -- Recent Form Integration
    last_3_avg DECIMAL(5,2),                      
    form_trend VARCHAR(20),                       
    consistency_rating DECIMAL(3,2),              
    
    -- Calculation Metadata
    rating_confidence DECIMAL(3,2) DEFAULT 0.80,  
    sample_size INTEGER DEFAULT 1,                
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_power_horse FOREIGN KEY (horse_id) REFERENCES horses(horse_id),
    CONSTRAINT fk_power_race FOREIGN KEY (race_id) REFERENCES races(id),
    CONSTRAINT chk_power_rating CHECK (power_rating >= 0 AND power_rating <= 140)
);

-- ===============================================
-- 3. ENHANCED FORM SCORES TABLE
-- ===============================================
CREATE TABLE horse_form_scores (
    id SERIAL PRIMARY KEY,
    horse_id BIGINT NOT NULL,
    race_id INTEGER,
    horse_name VARCHAR(255) NOT NULL,
    race_date DATE NOT NULL,
    
    -- Overall Form Score (0-100)
    form_score DECIMAL(5,2) NOT NULL,
    
    -- Component Scores (0-100 each)
    recent_form_score DECIMAL(5,2),               
    class_form_score DECIMAL(5,2),                
    distance_form_score DECIMAL(5,2),             
    surface_form_score DECIMAL(5,2),              
    going_form_score DECIMAL(5,2),                
    course_form_score DECIMAL(5,2),               
    
    -- Trend Analysis
    form_trend VARCHAR(20),                       
    trend_strength DECIMAL(3,2),                  
    peak_performance_rating DECIMAL(5,2),         
    consistency_rating DECIMAL(3,2),              
    
    -- Contextual Factors
    days_since_last_run INTEGER,                  
    trainer_form_rating DECIMAL(3,2),             
    jockey_form_rating DECIMAL(3,2),              
    stable_confidence DECIMAL(3,2),               
    
    -- Performance Indicators
    improvement_indicator DECIMAL(4,2),           
    class_progression VARCHAR(20),                
    fitness_rating DECIMAL(3,2),                  
    
    -- Calculation Metadata
    races_analyzed INTEGER DEFAULT 5,             
    confidence_level DECIMAL(3,2) DEFAULT 0.75,   
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_form_horse FOREIGN KEY (horse_id) REFERENCES horses(horse_id),
    CONSTRAINT fk_form_race FOREIGN KEY (race_id) REFERENCES races(id),
    CONSTRAINT chk_form_score CHECK (form_score >= 0 AND form_score <= 100)
);

-- ===============================================
-- 4. MONTE CARLO SIMULATIONS TABLE
-- ===============================================
CREATE TABLE monte_carlo_simulations (
    id SERIAL PRIMARY KEY,
    simulation_id VARCHAR(50) NOT NULL,           
    race_id INTEGER,
    horse_id BIGINT NOT NULL,
    horse_name VARCHAR(255) NOT NULL,
    race_date DATE NOT NULL,
    
    -- Simulation Parameters
    simulation_runs INTEGER DEFAULT 10000,        
    simulation_method VARCHAR(30) DEFAULT 'standard',
    
    -- Probability Results
    win_probability DECIMAL(6,4) NOT NULL,        
    place_probability DECIMAL(6,4),               
    show_probability DECIMAL(6,4),                
    
    -- Position Analysis
    expected_position DECIMAL(4,2),               
    position_variance DECIMAL(4,2),               
    confidence_interval_lower DECIMAL(4,2),       
    confidence_interval_upper DECIMAL(4,2),       
    
    -- Value Analysis
    fair_odds DECIMAL(8,4),                       
    market_odds DECIMAL(8,4),                     
    value_rating VARCHAR(20),                     
    edge_percentage DECIMAL(5,2),                 
    
    -- Statistical Measures
    z_score DECIMAL(6,3),                         
    confidence_score DECIMAL(3,2),                
    volatility_index DECIMAL(3,2),                
    
    -- Betting Recommendations
    bet_type VARCHAR(20),                         
    stake_recommendation DECIMAL(3,2),            
    expected_value DECIMAL(6,3),                  
    
    -- Performance Tracking
    actual_result INTEGER,                        
    result_accuracy VARCHAR(20),                  
    
    -- Metadata
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_monte_horse FOREIGN KEY (horse_id) REFERENCES horses(horse_id),
    CONSTRAINT fk_monte_race FOREIGN KEY (race_id) REFERENCES races(id),
    CONSTRAINT chk_win_prob CHECK (win_probability >= 0 AND win_probability <= 1),
    CONSTRAINT chk_place_prob CHECK (place_probability >= 0 AND place_probability <= 1)
);

-- ===============================================
-- 5. ADVANCED METRICS SUMMARY TABLE
-- ===============================================
CREATE TABLE horse_advanced_metrics (
    id SERIAL PRIMARY KEY,
    horse_id BIGINT NOT NULL,
    race_id INTEGER,
    horse_name VARCHAR(255) NOT NULL,
    race_date DATE NOT NULL,
    
    -- Linked Metric IDs
    speed_rating_id INTEGER,
    power_rating_id INTEGER,
    form_score_id INTEGER,
    monte_carlo_id INTEGER,
    
    -- Quick Access Summary
    overall_rating DECIMAL(5,2),                  
    confidence_level DECIMAL(3,2),                
    recommendation VARCHAR(30),                   
    
    -- Key Metrics Summary
    speed_figure_summary DECIMAL(5,2),
    power_rating_summary DECIMAL(5,2),
    form_score_summary DECIMAL(5,2),
    win_probability_summary DECIMAL(6,4),
    
    -- Last Updated
    metrics_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_advanced_horse FOREIGN KEY (horse_id) REFERENCES horses(horse_id),
    CONSTRAINT fk_advanced_race FOREIGN KEY (race_id) REFERENCES races(id),
    CONSTRAINT fk_speed_ref FOREIGN KEY (speed_rating_id) REFERENCES horse_speed_ratings(id),
    CONSTRAINT fk_power_ref FOREIGN KEY (power_rating_id) REFERENCES horse_power_ratings(id),
    CONSTRAINT fk_form_ref FOREIGN KEY (form_score_id) REFERENCES horse_form_scores(id),
    CONSTRAINT fk_monte_ref FOREIGN KEY (monte_carlo_id) REFERENCES monte_carlo_simulations(id),
    UNIQUE(horse_id, race_id)
);

-- ===============================================
-- CREATE INDEXES FOR PERFORMANCE
-- ===============================================

-- Speed Ratings Indexes
CREATE INDEX idx_speed_ratings_horse_date ON horse_speed_ratings(horse_id, race_date DESC);
CREATE INDEX idx_speed_ratings_figure ON horse_speed_ratings(speed_figure DESC);
CREATE INDEX idx_speed_ratings_pace ON horse_speed_ratings(pace_classification);
CREATE INDEX idx_speed_ratings_class ON horse_speed_ratings(class_rating);

-- Power Ratings Indexes
CREATE INDEX idx_power_ratings_horse_date ON horse_power_ratings(horse_id, race_date DESC);
CREATE INDEX idx_power_ratings_rating ON horse_power_ratings(power_rating DESC);
CREATE INDEX idx_power_ratings_class ON horse_power_ratings(race_class);
CREATE INDEX idx_power_ratings_surface ON horse_power_ratings(surface_type);

-- Form Scores Indexes
CREATE INDEX idx_form_scores_horse_date ON horse_form_scores(horse_id, race_date DESC);
CREATE INDEX idx_form_scores_score ON horse_form_scores(form_score DESC);
CREATE INDEX idx_form_scores_trend ON horse_form_scores(form_trend);
CREATE INDEX idx_form_scores_class ON horse_form_scores(class_progression);

-- Monte Carlo Indexes
CREATE INDEX idx_monte_simulation_id ON monte_carlo_simulations(simulation_id);
CREATE INDEX idx_monte_horse_date ON monte_carlo_simulations(horse_id, race_date DESC);
CREATE INDEX idx_monte_win_prob ON monte_carlo_simulations(win_probability DESC);
CREATE INDEX idx_monte_value ON monte_carlo_simulations(value_rating);
CREATE INDEX idx_monte_edge ON monte_carlo_simulations(edge_percentage DESC);

-- Advanced Metrics Summary Indexes
CREATE INDEX idx_advanced_horse_date ON horse_advanced_metrics(horse_id, race_date DESC);
CREATE INDEX idx_advanced_overall ON horse_advanced_metrics(overall_rating DESC);
CREATE INDEX idx_advanced_recommendation ON horse_advanced_metrics(recommendation);

-- ===============================================
-- PERFORMANCE TRACKING VIEW
-- ===============================================
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
-- TABLE COMMENTS
-- ===============================================
COMMENT ON TABLE horse_speed_ratings IS 'Speed figures and pace analysis for each horse performance';
COMMENT ON TABLE horse_power_ratings IS 'Class-par based power ratings with contextual adjustments';
COMMENT ON TABLE horse_form_scores IS 'Multi-factor form analysis and trend scoring';
COMMENT ON TABLE monte_carlo_simulations IS 'Monte Carlo simulation results and betting analysis';
COMMENT ON TABLE horse_advanced_metrics IS 'Consolidated summary of all advanced racing metrics';

-- Success message
SELECT 'Advanced Racing Metrics Schema Created Successfully!' as status,
       'Tables: horse_speed_ratings, horse_power_ratings, horse_form_scores, monte_carlo_simulations, horse_advanced_metrics' as tables_created;
