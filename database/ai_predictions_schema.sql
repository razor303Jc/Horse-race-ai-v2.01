-- AI Predictions Database Schema
-- Enhanced tables for storing AI racing predictions and model performance tracking

-- 1. Enhanced AI Predictions Table
CREATE TABLE IF NOT EXISTS ai_predictions (
    id SERIAL PRIMARY KEY,
    prediction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    race_id BIGINT NOT NULL,
    horse_name VARCHAR(255) NOT NULL,
    jockey VARCHAR(255),
    trainer VARCHAR(255),
    course VARCHAR(100),
    race_number INTEGER,
    race_time TIME,
    
    -- AI Model Predictions (Individual Models)
    random_forest_probability REAL,
    gradient_boosting_probability REAL,
    logistic_regression_probability REAL,
    neural_network_probability REAL,
    
    -- Ensemble Prediction
    ensemble_probability REAL NOT NULL,
    confidence_level VARCHAR(20), -- 'High', 'Medium', 'Low'
    confidence_score REAL,
    
    -- Market Data
    odds_decimal REAL,
    odds_fractional VARCHAR(20),
    market_rank INTEGER, -- 1=favorite, 2=second favorite, etc.
    implied_probability REAL,
    
    -- Feature Engineering Values (Key Features)
    log_odds REAL,
    jockey_win_pct REAL,
    trainer_win_pct REAL,
    field_size INTEGER,
    
    -- Prediction Metadata
    model_version VARCHAR(50),
    feature_count INTEGER DEFAULT 17,
    prediction_rank INTEGER, -- AI ranking within race
    
    -- Result Tracking (Updated after race)
    actual_position INTEGER, -- Final position (1, 2, 3, etc.)
    actual_result VARCHAR(20), -- 'WIN', 'PLACE', 'SHOW', 'UNPLACED'
    was_correct BOOLEAN, -- True if prediction was correct
    
    -- Performance Metrics
    prediction_accuracy REAL, -- How close was the probability to actual
    profit_loss REAL, -- If betting strategy applied
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. AI Model Performance Tracking
CREATE TABLE IF NOT EXISTS ai_model_performance (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    model_name VARCHAR(50) NOT NULL, -- 'random_forest', 'ensemble', etc.
    
    -- Daily Performance Metrics
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    accuracy_percentage REAL DEFAULT 0.0,
    
    -- Betting Performance (if strategy applied)
    total_bets INTEGER DEFAULT 0,
    winning_bets INTEGER DEFAULT 0,
    total_stake REAL DEFAULT 0.0,
    total_return REAL DEFAULT 0.0,
    profit_loss REAL DEFAULT 0.0,
    roi_percentage REAL DEFAULT 0.0,
    
    -- Confidence Analysis
    high_confidence_predictions INTEGER DEFAULT 0,
    high_confidence_correct INTEGER DEFAULT 0,
    high_confidence_accuracy REAL DEFAULT 0.0,
    
    -- Market Analysis
    favorites_predicted INTEGER DEFAULT 0,
    favorites_correct INTEGER DEFAULT 0,
    outsiders_predicted INTEGER DEFAULT 0,
    outsiders_correct INTEGER DEFAULT 0,
    
    -- Model Specific Metrics
    avg_confidence_score REAL DEFAULT 0.0,
    avg_prediction_probability REAL DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Race Results Table (for comparing with predictions)
CREATE TABLE IF NOT EXISTS race_results (
    id SERIAL PRIMARY KEY,
    race_id BIGINT NOT NULL,
    race_date DATE NOT NULL,
    course VARCHAR(100),
    race_number INTEGER,
    horse_name VARCHAR(255) NOT NULL,
    final_position INTEGER,
    jockey VARCHAR(255),
    trainer VARCHAR(255),
    starting_price_decimal REAL,
    margin VARCHAR(50), -- winning margin or distance behind
    race_time_seconds REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(race_id, horse_name) -- Prevent duplicates
);

-- 4. AI Prediction Sessions (Track each prediction run)
CREATE TABLE IF NOT EXISTS ai_prediction_sessions (
    id SERIAL PRIMARY KEY,
    session_date DATE NOT NULL DEFAULT CURRENT_DATE,
    session_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Session Metadata
    total_races INTEGER DEFAULT 0,
    total_runners INTEGER DEFAULT 0,
    courses_covered TEXT[], -- Array of course names
    
    -- Model Information
    models_used TEXT[], -- Array of model names
    feature_count INTEGER DEFAULT 17,
    model_version VARCHAR(50),
    
    -- Data Quality
    data_quality_score REAL, -- 0-100 quality score
    missing_odds_count INTEGER DEFAULT 0,
    missing_stats_count INTEGER DEFAULT 0,
    
    -- Processing Performance
    processing_time_seconds REAL,
    memory_usage_mb REAL,
    
    -- Output Files
    output_file_path TEXT,
    output_file_size_kb INTEGER,
    
    status VARCHAR(20) DEFAULT 'COMPLETED', -- 'RUNNING', 'COMPLETED', 'FAILED'
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_ai_predictions_date ON ai_predictions(prediction_date);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_race_id ON ai_predictions(race_id);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_course ON ai_predictions(course);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_confidence ON ai_predictions(confidence_level);
CREATE INDEX IF NOT EXISTS idx_ai_model_performance_date ON ai_model_performance(date);
CREATE INDEX IF NOT EXISTS idx_ai_model_performance_model ON ai_model_performance(model_name);
CREATE INDEX IF NOT EXISTS idx_race_results_date ON race_results(race_date);
CREATE INDEX IF NOT EXISTS idx_race_results_race_id ON race_results(race_id);

-- Views for Easy Querying
CREATE OR REPLACE VIEW daily_ai_summary AS
SELECT 
    prediction_date,
    COUNT(*) as total_predictions,
    COUNT(DISTINCT race_id) as total_races,
    COUNT(DISTINCT course) as courses_covered,
    AVG(ensemble_probability) as avg_probability,
    AVG(confidence_score) as avg_confidence,
    COUNT(CASE WHEN confidence_level = 'High' THEN 1 END) as high_confidence_count,
    COUNT(CASE WHEN was_correct = true THEN 1 END) as correct_predictions,
    ROUND(
        COUNT(CASE WHEN was_correct = true THEN 1 END)::REAL / 
        NULLIF(COUNT(CASE WHEN actual_result IS NOT NULL THEN 1 END), 0) * 100, 2
    ) as accuracy_percentage
FROM ai_predictions 
GROUP BY prediction_date
ORDER BY prediction_date DESC;

CREATE OR REPLACE VIEW model_comparison AS
SELECT 
    prediction_date,
    COUNT(*) as total_predictions,
    AVG(random_forest_probability) as avg_rf_prob,
    AVG(gradient_boosting_probability) as avg_gb_prob,
    AVG(logistic_regression_probability) as avg_lr_prob,
    AVG(neural_network_probability) as avg_nn_prob,
    AVG(ensemble_probability) as avg_ensemble_prob,
    STDDEV(ensemble_probability) as ensemble_std_dev
FROM ai_predictions
WHERE prediction_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY prediction_date
ORDER BY prediction_date DESC;

-- Comments
COMMENT ON TABLE ai_predictions IS 'Stores individual AI predictions for each horse in each race';
COMMENT ON TABLE ai_model_performance IS 'Tracks daily performance metrics for each AI model';
COMMENT ON TABLE race_results IS 'Stores actual race results for comparison with predictions';
COMMENT ON TABLE ai_prediction_sessions IS 'Tracks each AI prediction generation session';
COMMENT ON VIEW daily_ai_summary IS 'Daily summary of AI prediction performance';
COMMENT ON VIEW model_comparison IS 'Comparison of different AI models performance';
