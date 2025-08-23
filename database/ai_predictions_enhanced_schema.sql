-- AI Predictions Database Schema Update
-- =====================================
-- 
-- This schema extends the existing ai_predictions table with additional fields
-- and creates supporting tables for comprehensive AI race predictions storage.

-- Ensure ai_predictions table exists with all required columns
CREATE TABLE IF NOT EXISTS ai_predictions (
    id SERIAL PRIMARY KEY,
    race_id INTEGER NOT NULL,
    horse_name VARCHAR(255) NOT NULL,
    jockey VARCHAR(255),
    trainer VARCHAR(255),
    course VARCHAR(255),
    race_number INTEGER,
    
    -- Individual model predictions
    random_forest_probability DECIMAL(10,6),
    gradient_boosting_probability DECIMAL(10,6),
    logistic_regression_probability DECIMAL(10,6),
    neural_network_probability DECIMAL(10,6),
    
    -- Ensemble prediction
    ensemble_probability DECIMAL(10,6) NOT NULL,
    confidence_level VARCHAR(20),
    confidence_score DECIMAL(10,6),
    
    -- Market data
    odds_decimal DECIMAL(10,2),
    market_rank INTEGER,
    implied_probability DECIMAL(10,6),
    
    -- Feature values
    log_odds DECIMAL(10,6),
    jockey_win_pct DECIMAL(10,6),
    trainer_win_pct DECIMAL(10,6),
    field_size INTEGER,
    
    -- Model metadata
    model_version VARCHAR(50),
    feature_count INTEGER,
    prediction_rank INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add missing columns to existing table if they don't exist
DO $$ 
BEGIN 
    -- Check and add confidence_level column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='ai_predictions' AND column_name='confidence_level') THEN
        ALTER TABLE ai_predictions ADD COLUMN confidence_level VARCHAR(20);
    END IF;
    
    -- Check and add confidence_score column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='ai_predictions' AND column_name='confidence_score') THEN
        ALTER TABLE ai_predictions ADD COLUMN confidence_score DECIMAL(10,6);
    END IF;
    
    -- Check and add market_rank column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='ai_predictions' AND column_name='market_rank') THEN
        ALTER TABLE ai_predictions ADD COLUMN market_rank INTEGER;
    END IF;
    
    -- Check and add prediction_rank column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='ai_predictions' AND column_name='prediction_rank') THEN
        ALTER TABLE ai_predictions ADD COLUMN prediction_rank INTEGER;
    END IF;
    
    -- Check and add model_version column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='ai_predictions' AND column_name='model_version') THEN
        ALTER TABLE ai_predictions ADD COLUMN model_version VARCHAR(50);
    END IF;
    
    -- Check and add feature_count column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='ai_predictions' AND column_name='feature_count') THEN
        ALTER TABLE ai_predictions ADD COLUMN feature_count INTEGER;
    END IF;
    
    -- Check and add updated_at column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='ai_predictions' AND column_name='updated_at') THEN
        ALTER TABLE ai_predictions ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
    
END $$;

-- Create AI prediction daily summaries table
CREATE TABLE IF NOT EXISTS ai_prediction_daily_summaries (
    id SERIAL PRIMARY KEY,
    prediction_date DATE NOT NULL UNIQUE,
    total_races INTEGER DEFAULT 0,
    total_runners INTEGER DEFAULT 0,
    predictions_generated INTEGER DEFAULT 0,
    predictions_stored INTEGER DEFAULT 0,
    avg_confidence_score DECIMAL(10,6),
    high_confidence_count INTEGER DEFAULT 0,
    medium_confidence_count INTEGER DEFAULT 0,
    low_confidence_count INTEGER DEFAULT 0,
    recommended_bets_count INTEGER DEFAULT 0,
    top_prediction_horse VARCHAR(255),
    top_prediction_probability DECIMAL(10,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create AI model performance tracking table
CREATE TABLE IF NOT EXISTS ai_model_performance (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    evaluation_date DATE NOT NULL,
    
    -- Performance metrics
    accuracy DECIMAL(10,6),
    precision_score DECIMAL(10,6),
    recall_score DECIMAL(10,6),
    f1_score DECIMAL(10,6),
    auc_roc DECIMAL(10,6),
    log_loss DECIMAL(10,6),
    
    -- Race-specific metrics
    win_prediction_accuracy DECIMAL(10,6),
    place_prediction_accuracy DECIMAL(10,6),
    show_prediction_accuracy DECIMAL(10,6),
    
    -- Betting performance
    roi_percent DECIMAL(10,4),
    profit_loss DECIMAL(12,2),
    total_bets INTEGER,
    winning_bets INTEGER,
    
    -- Model characteristics
    training_samples INTEGER,
    feature_count INTEGER,
    training_duration_minutes INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create AI prediction results tracking (for validation against actual results)
CREATE TABLE IF NOT EXISTS ai_prediction_results (
    id SERIAL PRIMARY KEY,
    race_id INTEGER NOT NULL,
    horse_name VARCHAR(255) NOT NULL,
    predicted_probability DECIMAL(10,6),
    predicted_rank INTEGER,
    actual_finish_position INTEGER,
    was_winner BOOLEAN DEFAULT FALSE,
    was_placed BOOLEAN DEFAULT FALSE,
    odds_decimal DECIMAL(10,2),
    
    -- Performance metrics for this prediction
    prediction_accuracy_score DECIMAL(10,6),
    rank_accuracy_score DECIMAL(10,6),
    value_score DECIMAL(10,6),
    
    race_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(race_id, horse_name)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_ai_predictions_race_id ON ai_predictions(race_id);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_created_at ON ai_predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_ensemble_prob ON ai_predictions(ensemble_probability DESC);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_confidence ON ai_predictions(confidence_level, confidence_score);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_course_date ON ai_predictions(course, created_at);

CREATE INDEX IF NOT EXISTS idx_ai_daily_summaries_date ON ai_prediction_daily_summaries(prediction_date);
CREATE INDEX IF NOT EXISTS idx_ai_model_performance_date ON ai_model_performance(evaluation_date);
CREATE INDEX IF NOT EXISTS idx_ai_model_performance_name ON ai_model_performance(model_name, model_version);

CREATE INDEX IF NOT EXISTS idx_ai_prediction_results_race ON ai_prediction_results(race_id);
CREATE INDEX IF NOT EXISTS idx_ai_prediction_results_date ON ai_prediction_results(race_date);
CREATE INDEX IF NOT EXISTS idx_ai_prediction_results_horse ON ai_prediction_results(horse_name);

-- Create view for daily prediction summaries
CREATE OR REPLACE VIEW ai_predictions_daily_view AS
SELECT 
    DATE(created_at) as prediction_date,
    COUNT(*) as total_predictions,
    COUNT(DISTINCT race_id) as total_races,
    COUNT(DISTINCT course) as total_courses,
    AVG(ensemble_probability) as avg_ensemble_probability,
    AVG(confidence_score) as avg_confidence_score,
    COUNT(CASE WHEN confidence_level = 'High' THEN 1 END) as high_confidence_count,
    COUNT(CASE WHEN confidence_level = 'Medium' THEN 1 END) as medium_confidence_count,
    COUNT(CASE WHEN confidence_level = 'Low' THEN 1 END) as low_confidence_count,
    MAX(ensemble_probability) as max_probability,
    MIN(ensemble_probability) as min_probability
FROM ai_predictions 
GROUP BY DATE(created_at)
ORDER BY prediction_date DESC;

-- Create view for top daily predictions
CREATE OR REPLACE VIEW ai_top_predictions_daily AS
SELECT 
    DATE(ap.created_at) as prediction_date,
    ap.race_id,
    ap.course,
    ap.race_number,
    ap.horse_name,
    ap.jockey,
    ap.trainer,
    ap.ensemble_probability,
    ap.confidence_score,
    ap.confidence_level,
    ap.prediction_rank,
    ROW_NUMBER() OVER (PARTITION BY DATE(ap.created_at) ORDER BY ap.ensemble_probability DESC) as daily_rank
FROM ai_predictions ap
ORDER BY prediction_date DESC, daily_rank;

-- Create function to update daily summaries
CREATE OR REPLACE FUNCTION update_daily_prediction_summary(summary_date DATE)
RETURNS VOID AS $$
BEGIN
    INSERT INTO ai_prediction_daily_summaries (
        prediction_date,
        total_races,
        total_runners,
        predictions_generated,
        predictions_stored,
        avg_confidence_score,
        high_confidence_count,
        medium_confidence_count,
        low_confidence_count,
        top_prediction_horse,
        top_prediction_probability
    )
    SELECT 
        summary_date,
        COUNT(DISTINCT race_id),
        COUNT(*),
        COUNT(*),
        COUNT(*),
        AVG(confidence_score),
        COUNT(CASE WHEN confidence_level = 'High' THEN 1 END),
        COUNT(CASE WHEN confidence_level = 'Medium' THEN 1 END),
        COUNT(CASE WHEN confidence_level = 'Low' THEN 1 END),
        (SELECT horse_name FROM ai_predictions 
         WHERE DATE(created_at) = summary_date 
         ORDER BY ensemble_probability DESC LIMIT 1),
        MAX(ensemble_probability)
    FROM ai_predictions 
    WHERE DATE(created_at) = summary_date
    ON CONFLICT (prediction_date) DO UPDATE SET
        total_races = EXCLUDED.total_races,
        total_runners = EXCLUDED.total_runners,
        predictions_generated = EXCLUDED.predictions_generated,
        predictions_stored = EXCLUDED.predictions_stored,
        avg_confidence_score = EXCLUDED.avg_confidence_score,
        high_confidence_count = EXCLUDED.high_confidence_count,
        medium_confidence_count = EXCLUDED.medium_confidence_count,
        low_confidence_count = EXCLUDED.low_confidence_count,
        top_prediction_horse = EXCLUDED.top_prediction_horse,
        top_prediction_probability = EXCLUDED.top_prediction_probability,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to ai_predictions table
DROP TRIGGER IF EXISTS update_ai_predictions_updated_at ON ai_predictions;
CREATE TRIGGER update_ai_predictions_updated_at
    BEFORE UPDATE ON ai_predictions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to ai_prediction_daily_summaries table
DROP TRIGGER IF EXISTS update_ai_daily_summaries_updated_at ON ai_prediction_daily_summaries;
CREATE TRIGGER update_ai_daily_summaries_updated_at
    BEFORE UPDATE ON ai_prediction_daily_summaries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed for your user)
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_predictions TO horse_racing;
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_prediction_daily_summaries TO horse_racing;
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_model_performance TO horse_racing;
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_prediction_results TO horse_racing;

GRANT USAGE, SELECT ON SEQUENCE ai_predictions_id_seq TO horse_racing;
GRANT USAGE, SELECT ON SEQUENCE ai_prediction_daily_summaries_id_seq TO horse_racing;
GRANT USAGE, SELECT ON SEQUENCE ai_model_performance_id_seq TO horse_racing;
GRANT USAGE, SELECT ON SEQUENCE ai_prediction_results_id_seq TO horse_racing;

GRANT SELECT ON ai_predictions_daily_view TO horse_racing;
GRANT SELECT ON ai_top_predictions_daily TO horse_racing;

-- Insert sample data to verify schema
INSERT INTO ai_model_performance (
    model_name, model_version, evaluation_date,
    accuracy, precision_score, recall_score, f1_score,
    win_prediction_accuracy, training_samples, feature_count
) VALUES (
    'V201EnsemblePredictor', 'v2.04', CURRENT_DATE,
    0.758, 0.234, 0.301, 0.264,
    0.234, 50000, 17
) ON CONFLICT DO NOTHING;

-- Create notification for successful schema update
DO $$
BEGIN
    RAISE NOTICE 'AI Predictions schema update completed successfully!';
    RAISE NOTICE 'Tables created/updated: ai_predictions, ai_prediction_daily_summaries, ai_model_performance, ai_prediction_results';
    RAISE NOTICE 'Views created: ai_predictions_daily_view, ai_top_predictions_daily';
    RAISE NOTICE 'Functions created: update_daily_prediction_summary, update_updated_at_column';
    RAISE NOTICE 'Indexes and triggers applied for performance optimization';
END $$;
