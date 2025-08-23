-- ===================================================================
-- AI SELECTIONS DATABASE SCHEMA
-- ===================================================================
-- Purpose: Store AI-generated horse race predictions and selections
-- Author: Horse Racing AI System
-- Created: 2025-08-23
-- ===================================================================

-- Main AI Selections Table
-- Stores the primary AI predictions for each horse in each race
CREATE TABLE IF NOT EXISTS ai_selections (
    selection_id SERIAL PRIMARY KEY,
    race_id INTEGER NOT NULL,
    detail_id INTEGER NOT NULL,
    horse_name VARCHAR(100) NOT NULL,
    
    -- AI Prediction Scores
    win_probability DECIMAL(5,4) NOT NULL,  -- 0.0000 to 1.0000
    place_probability DECIMAL(5,4),
    confidence_score DECIMAL(5,4) NOT NULL, -- Overall prediction confidence
    
    -- Model Information
    model_name VARCHAR(50) NOT NULL,        -- RandomForest, GradientBoosting, etc.
    model_version VARCHAR(20) NOT NULL,     -- Training session/version
    auc_score DECIMAL(5,4),                 -- Model's AUC performance
    
    -- Selection Categories
    ai_selection_type VARCHAR(20) NOT NULL, -- 'win', 'place', 'each_way'
    recommended_stake DECIMAL(5,2),         -- Suggested bet amount
    expected_value DECIMAL(8,4),            -- Expected return calculation
    
    -- Race Context
    race_date DATE NOT NULL,
    course VARCHAR(100) NOT NULL,
    race_number INTEGER NOT NULL,
    
    -- Prediction Metadata
    features_used TEXT,                     -- JSON of features used in prediction
    prediction_factors TEXT,                -- Key factors influencing prediction
    
    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_ai_selections_race_id FOREIGN KEY (race_id) REFERENCES races(race_id),
    CONSTRAINT fk_ai_selections_detail_id FOREIGN KEY (detail_id) REFERENCES racecard_details(detail_id),
    
    -- Ensure probabilities are valid
    CONSTRAINT chk_win_probability CHECK (win_probability >= 0 AND win_probability <= 1),
    CONSTRAINT chk_place_probability CHECK (place_probability IS NULL OR (place_probability >= 0 AND place_probability <= 1)),
    CONSTRAINT chk_confidence_score CHECK (confidence_score >= 0 AND confidence_score <= 1),
    CONSTRAINT chk_auc_score CHECK (auc_score IS NULL OR (auc_score >= 0 AND auc_score <= 1))
);

-- AI Selection Summary Table
-- Stores aggregated predictions per race
CREATE TABLE IF NOT EXISTS ai_race_summary (
    summary_id SERIAL PRIMARY KEY,
    race_id INTEGER NOT NULL,
    
    -- Top Selections
    top_win_selection VARCHAR(100),          -- Horse name
    top_win_probability DECIMAL(5,4),
    top_place_selection VARCHAR(100),
    top_place_probability DECIMAL(5,4),
    
    -- Race Analysis
    race_competitiveness DECIMAL(5,4),      -- How close the race is predicted to be
    prediction_certainty DECIMAL(5,4),      -- Overall confidence in race predictions
    total_horses_analyzed INTEGER,
    
    -- Model Performance Context
    avg_model_auc DECIMAL(5,4),             -- Average AUC of models used
    model_consensus VARCHAR(50),             -- Agreement between models
    
    -- Recommendations
    betting_strategy TEXT,                   -- Suggested betting approach
    risk_assessment VARCHAR(20),            -- 'low', 'medium', 'high'
    
    -- Race Information
    race_date DATE NOT NULL,
    course VARCHAR(100) NOT NULL,
    race_number INTEGER NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_ai_race_summary_race_id FOREIGN KEY (race_id) REFERENCES races(race_id)
);

-- AI Model Performance Tracking
-- Tracks the performance of different AI models
CREATE TABLE IF NOT EXISTS ai_model_performance (
    performance_id SERIAL PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    
    -- Training Metrics
    training_date DATE NOT NULL,
    training_sessions INTEGER,
    best_auc DECIMAL(5,4),
    avg_auc DECIMAL(5,4),
    accuracy DECIMAL(5,4),
    
    -- Dataset Information
    training_records INTEGER,
    validation_records INTEGER,
    
    -- Model Status
    is_active BOOLEAN DEFAULT TRUE,
    deployment_date TIMESTAMP,
    
    -- Performance Notes
    performance_notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Selection Results Tracking
-- Tracks actual outcomes vs AI predictions for performance analysis
CREATE TABLE IF NOT EXISTS ai_selection_results (
    result_id SERIAL PRIMARY KEY,
    selection_id INTEGER NOT NULL,
    
    -- Actual Results
    actual_position INTEGER,                -- Final finishing position
    actual_win BOOLEAN DEFAULT FALSE,
    actual_place BOOLEAN DEFAULT FALSE,
    actual_odds DECIMAL(8,2),              -- Final SP odds
    
    -- Prediction Accuracy
    prediction_correct BOOLEAN,
    probability_accuracy DECIMAL(5,4),     -- How close probability was to outcome
    
    -- Financial Performance
    profit_loss DECIMAL(8,2),              -- If bet was placed
    roi DECIMAL(5,4),                      -- Return on investment
    
    -- Analysis
    prediction_analysis TEXT,              -- Why prediction was right/wrong
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_ai_selection_results_selection_id FOREIGN KEY (selection_id) REFERENCES ai_selections(selection_id)
);

-- ===================================================================
-- INDEXES FOR PERFORMANCE
-- ===================================================================

-- Primary lookup indexes
CREATE INDEX IF NOT EXISTS idx_ai_selections_race_id ON ai_selections(race_id);
CREATE INDEX IF NOT EXISTS idx_ai_selections_horse_name ON ai_selections(horse_name);
CREATE INDEX IF NOT EXISTS idx_ai_selections_race_date ON ai_selections(race_date);
CREATE INDEX IF NOT EXISTS idx_ai_selections_model_name ON ai_selections(model_name);
CREATE INDEX IF NOT EXISTS idx_ai_selections_confidence ON ai_selections(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_ai_selections_win_prob ON ai_selections(win_probability DESC);

-- Summary table indexes
CREATE INDEX IF NOT EXISTS idx_ai_race_summary_race_id ON ai_race_summary(race_id);
CREATE INDEX IF NOT EXISTS idx_ai_race_summary_date ON ai_race_summary(race_date);

-- Performance tracking indexes
CREATE INDEX IF NOT EXISTS idx_ai_model_performance_name ON ai_model_performance(model_name);
CREATE INDEX IF NOT EXISTS idx_ai_model_performance_active ON ai_model_performance(is_active);

-- Results tracking indexes
CREATE INDEX IF NOT EXISTS idx_ai_selection_results_selection_id ON ai_selection_results(selection_id);
CREATE INDEX IF NOT EXISTS idx_ai_selection_results_profit ON ai_selection_results(profit_loss);

-- ===================================================================
-- VIEWS FOR EASY DATA ACCESS
-- ===================================================================

-- View: Latest AI Selections with Race Details
CREATE OR REPLACE VIEW vw_latest_ai_selections AS
SELECT 
    s.selection_id,
    s.race_id,
    s.detail_id,
    s.horse_name,
    s.win_probability,
    s.place_probability,
    s.confidence_score,
    s.model_name,
    s.ai_selection_type,
    s.recommended_stake,
    s.expected_value,
    
    -- Race details
    r.race_name,
    r.race_number,
    r.race_time,
    r.course,
    r.race_date,
    r.distance,
    r.class,
    
    -- Horse details
    rd.jockey,
    rd.trainer,
    rd.number,
    rd.odds,
    rd.weight,
    rd.age,
    rd.form,
    
    s.created_at
FROM ai_selections s
JOIN races r ON s.race_id = r.race_id
JOIN racecard_details rd ON s.detail_id = rd.detail_id
WHERE s.race_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY s.race_date DESC, s.race_number, s.confidence_score DESC;

-- View: Top AI Selections by Race
CREATE OR REPLACE VIEW vw_top_ai_selections AS
SELECT 
    race_id,
    race_date,
    course,
    race_number,
    horse_name,
    win_probability,
    confidence_score,
    model_name,
    ROW_NUMBER() OVER (PARTITION BY race_id ORDER BY win_probability DESC) as selection_rank
FROM ai_selections
WHERE race_date >= CURRENT_DATE
ORDER BY race_date, race_number, selection_rank;

-- View: AI Model Performance Summary
CREATE OR REPLACE VIEW vw_ai_model_performance AS
SELECT 
    model_name,
    model_version,
    training_date,
    best_auc,
    avg_auc,
    accuracy,
    training_records,
    is_active,
    ROW_NUMBER() OVER (PARTITION BY model_name ORDER BY training_date DESC) as version_rank
FROM ai_model_performance
ORDER BY training_date DESC;

-- ===================================================================
-- FUNCTIONS FOR DATA MANAGEMENT
-- ===================================================================

-- Function: Update AI Selection timestamp
CREATE OR REPLACE FUNCTION update_ai_selection_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update timestamp on ai_selections
DROP TRIGGER IF EXISTS tr_ai_selections_updated_at ON ai_selections;
CREATE TRIGGER tr_ai_selections_updated_at
    BEFORE UPDATE ON ai_selections
    FOR EACH ROW
    EXECUTE FUNCTION update_ai_selection_timestamp();

-- Trigger: Auto-update timestamp on ai_race_summary
DROP TRIGGER IF EXISTS tr_ai_race_summary_updated_at ON ai_race_summary;
CREATE TRIGGER tr_ai_race_summary_updated_at
    BEFORE UPDATE ON ai_race_summary
    FOR EACH ROW
    EXECUTE FUNCTION update_ai_selection_timestamp();

-- ===================================================================
-- INITIAL DATA / EXAMPLE RECORDS
-- ===================================================================

-- Insert initial model performance record for current training
INSERT INTO ai_model_performance (
    model_name, 
    model_version, 
    training_date, 
    training_sessions, 
    best_auc, 
    avg_auc, 
    accuracy, 
    training_records, 
    validation_records, 
    is_active, 
    deployment_date,
    performance_notes
) VALUES (
    'GradientBoosting',
    'v2025.08.23',
    CURRENT_DATE,
    125,  -- Based on our current training (25 Phase 1 + 100 Phase 2)
    0.8664,
    0.8094,
    0.8945,
    2089,
    523,  -- Assuming 25% for validation
    TRUE,
    CURRENT_TIMESTAMP,
    'ML training with expanded dataset. Phase 1: 25 sessions (Best AUC: 0.8664), Phase 2: Extended training with comprehensive results data.'
) ON CONFLICT DO NOTHING;

INSERT INTO ai_model_performance (
    model_name, 
    model_version, 
    training_date, 
    training_sessions, 
    best_auc, 
    avg_auc, 
    accuracy, 
    training_records, 
    validation_records, 
    is_active, 
    deployment_date,
    performance_notes
) VALUES (
    'RandomForest',
    'v2025.08.23',
    CURRENT_DATE,
    125,
    0.8502,  -- Notable performance from Phase 2
    0.8094,
    0.8897,
    2089,
    523,
    TRUE,
    CURRENT_TIMESTAMP,
    'Consistent performer across both training phases. Strong accuracy and reliable predictions.'
) ON CONFLICT DO NOTHING;

-- ===================================================================
-- GRANTS AND PERMISSIONS
-- ===================================================================

-- Grant permissions to horse_racing user
GRANT ALL PRIVILEGES ON ai_selections TO horse_racing;
GRANT ALL PRIVILEGES ON ai_race_summary TO horse_racing;
GRANT ALL PRIVILEGES ON ai_model_performance TO horse_racing;
GRANT ALL PRIVILEGES ON ai_selection_results TO horse_racing;

-- Grant sequence permissions
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO horse_racing;

-- ===================================================================
-- SCHEMA COMPLETE
-- ===================================================================
-- This schema provides:
-- 1. Comprehensive AI selection storage
-- 2. Race-level summary and analysis
-- 3. Model performance tracking
-- 4. Results validation and analysis
-- 5. Optimized indexes for performance
-- 6. Views for easy data access
-- 7. Automated timestamp management
-- ===================================================================
