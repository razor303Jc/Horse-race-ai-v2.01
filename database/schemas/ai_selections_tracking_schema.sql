-- AI Horse Selections Tracking Database Schema
-- Horse Racing AI v2.03 - Enhanced Selection Analytics
-- Created: 2025-08-20

-- ===============================================
-- 1. AI HORSE SELECTIONS TABLE
-- ===============================================
CREATE TABLE IF NOT EXISTS ai_horse_selections (
    id SERIAL PRIMARY KEY,
    selection_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Race Information
    race_id VARCHAR(50) NOT NULL,
    race_date TIMESTAMP NOT NULL,
    course VARCHAR(100) NOT NULL,
    race_number INTEGER NOT NULL,
    race_time VARCHAR(20),
    race_distance DECIMAL(4,2),
    race_class VARCHAR(50),
    
    -- Horse Information
    horse_name VARCHAR(255) NOT NULL,
    horse_id VARCHAR(50),
    jockey VARCHAR(255),
    trainer VARCHAR(255),
    weight DECIMAL(5,1),
    draw INTEGER,
    
    -- AI Prediction Details
    ai_model_version VARCHAR(50) NOT NULL,
    prediction_method VARCHAR(50) NOT NULL, -- 'raw_ratings', 'monte_carlo', 'ai_ml', 'consensus'
    win_probability DECIMAL(5,4) NOT NULL,
    place_probability DECIMAL(5,4),
    show_probability DECIMAL(5,4),
    confidence_score DECIMAL(5,4) NOT NULL,
    confidence_level VARCHAR(20), -- 'HIGH', 'MEDIUM', 'LOW'
    
    -- Market Data
    odds_decimal DECIMAL(8,2),
    odds_fractional VARCHAR(20),
    market_rank INTEGER,
    implied_probability DECIMAL(5,4),
    
    -- Selection Strategy
    selection_type VARCHAR(50) NOT NULL, -- 'WIN', 'PLACE', 'SHOW', 'EACH_WAY'
    betting_strategy VARCHAR(50), -- '80_20', 'dutching', 'value_bet', 'conservative'
    stake_amount DECIMAL(10,2),
    recommended_stake DECIMAL(10,2),
    
    -- Actual Results
    actual_position INTEGER,
    actual_result VARCHAR(20), -- 'WIN', 'PLACE', 'SHOW', 'UNPLACED'
    was_correct BOOLEAN DEFAULT FALSE,
    result_updated_at TIMESTAMP,
    
    -- Financial Tracking
    stake_placed DECIMAL(10,2) DEFAULT 0.00,
    payout_received DECIMAL(10,2) DEFAULT 0.00,
    profit_loss DECIMAL(10,2) DEFAULT 0.00,
    roi_percentage DECIMAL(8,4) DEFAULT 0.00,
    
    -- Performance Metrics
    prediction_accuracy DECIMAL(5,4),
    value_assessment VARCHAR(20), -- 'OVERLAY', 'UNDERLAY', 'FAIR'
    edge_percentage DECIMAL(8,4),
    
    -- Contextual Data
    field_size INTEGER,
    weather_conditions VARCHAR(100),
    track_condition VARCHAR(50),
    pace_scenario VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Selections Indexes
CREATE INDEX IF NOT EXISTS idx_ai_selections_race_date ON ai_horse_selections(race_date DESC);
CREATE INDEX IF NOT EXISTS idx_ai_selections_race_id ON ai_horse_selections(race_id);
CREATE INDEX IF NOT EXISTS idx_ai_selections_horse ON ai_horse_selections(horse_name);
CREATE INDEX IF NOT EXISTS idx_ai_selections_method ON ai_horse_selections(prediction_method);
CREATE INDEX IF NOT EXISTS idx_ai_selections_strategy ON ai_horse_selections(betting_strategy);
CREATE INDEX IF NOT EXISTS idx_ai_selections_confidence ON ai_horse_selections(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_ai_selections_roi ON ai_horse_selections(roi_percentage DESC);
CREATE INDEX IF NOT EXISTS idx_ai_selections_course ON ai_horse_selections(course);

-- ===============================================
-- 2. AI SELECTION PERFORMANCE AGGREGATES TABLE
-- ===============================================
CREATE TABLE IF NOT EXISTS ai_selection_performance (
    id SERIAL PRIMARY KEY,
    
    -- Analysis Period
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    period_type VARCHAR(20) NOT NULL, -- 'DAILY', 'WEEKLY', 'MONTHLY'
    
    -- Selection Metrics
    total_selections INTEGER DEFAULT 0,
    win_selections INTEGER DEFAULT 0,
    place_selections INTEGER DEFAULT 0,
    show_selections INTEGER DEFAULT 0,
    unplaced_selections INTEGER DEFAULT 0,
    
    -- Accuracy Metrics
    win_accuracy DECIMAL(5,4) DEFAULT 0.0000,
    place_accuracy DECIMAL(5,4) DEFAULT 0.0000,
    overall_accuracy DECIMAL(5,4) DEFAULT 0.0000,
    confidence_calibration DECIMAL(5,4) DEFAULT 0.0000,
    
    -- Financial Performance
    total_stakes DECIMAL(12,2) DEFAULT 0.00,
    total_payouts DECIMAL(12,2) DEFAULT 0.00,
    net_profit DECIMAL(12,2) DEFAULT 0.00,
    roi_percentage DECIMAL(8,4) DEFAULT 0.0000,
    profit_factor DECIMAL(8,4) DEFAULT 0.0000,
    
    -- Risk Metrics
    max_drawdown DECIMAL(10,2) DEFAULT 0.00,
    consecutive_losses INTEGER DEFAULT 0,
    win_loss_ratio DECIMAL(8,4) DEFAULT 0.0000,
    volatility DECIMAL(8,4) DEFAULT 0.0000,
    
    -- Strategy Performance (JSON)
    strategy_breakdown TEXT, -- JSON of strategy-specific performance
    method_breakdown TEXT, -- JSON of method-specific performance
    
    -- Market Analysis
    average_odds DECIMAL(8,2) DEFAULT 0.00,
    overlay_percentage DECIMAL(5,2) DEFAULT 0.00,
    value_capture_rate DECIMAL(5,2) DEFAULT 0.00,
    
    -- Contextual Factors (JSON)
    weather_impact TEXT, -- JSON of weather performance breakdown
    class_impact TEXT, -- JSON of class performance breakdown
    distance_impact TEXT, -- JSON of distance performance breakdown
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_perf_period ON ai_selection_performance(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_perf_type ON ai_selection_performance(period_type);
CREATE INDEX IF NOT EXISTS idx_perf_roi ON ai_selection_performance(roi_percentage DESC);

-- ===============================================
-- 3. AI SELECTION RESULTS RELATIONSHIPS TABLE
-- ===============================================
CREATE TABLE IF NOT EXISTS ai_selection_race_relationships (
    id SERIAL PRIMARY KEY,
    
    -- Primary Keys
    selection_id VARCHAR(100) NOT NULL,
    race_id VARCHAR(50) NOT NULL,
    
    -- Race Result Data
    race_winner VARCHAR(255),
    race_second VARCHAR(255),
    race_third VARCHAR(255),
    winning_margin DECIMAL(4,2),
    race_time_seconds DECIMAL(8,3),
    
    -- Selection Context in Race
    selection_finish_position INTEGER,
    selections_in_race INTEGER, -- How many AI selections in this race
    best_ai_position INTEGER, -- Best finish of AI selections
    worst_ai_position INTEGER, -- Worst finish of AI selections
    
    -- Race Dynamics
    pace_type VARCHAR(20), -- 'fast', 'moderate', 'slow'
    pace_impact VARCHAR(20), -- 'helped', 'hindered', 'neutral'
    track_bias VARCHAR(50), -- 'inside', 'outside', 'none'
    bias_impact VARCHAR(20), -- 'helped', 'hindered', 'neutral'
    
    -- Competitive Analysis
    favorite_finished INTEGER, -- Position of favorite
    longshot_winner BOOLEAN DEFAULT FALSE, -- Winner over 10/1
    form_upheld BOOLEAN, -- Did form horses finish well
    
    -- Market Analysis
    sp_accuracy DECIMAL(5,4), -- How accurate were starting prices
    market_leader_performance VARCHAR(20), -- 'won', 'placed', 'unplaced'
    overlay_performance VARCHAR(20), -- How overlays performed
    
    -- AI Performance Context
    prediction_vs_market DECIMAL(5,4), -- AI prob vs market prob difference
    value_identified BOOLEAN DEFAULT FALSE, -- Was value correctly identified
    risk_assessment_accurate BOOLEAN DEFAULT FALSE, -- Was risk correctly assessed
    
    -- Learning Signals
    surprise_result BOOLEAN DEFAULT FALSE, -- Unexpected outcome
    ai_error_type VARCHAR(50), -- Type of error if prediction wrong
    improvement_opportunity TEXT, -- What could be improved
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Relationships Indexes
CREATE INDEX IF NOT EXISTS idx_rel_selection ON ai_selection_race_relationships(selection_id);
CREATE INDEX IF NOT EXISTS idx_rel_race ON ai_selection_race_relationships(race_id);
CREATE INDEX IF NOT EXISTS idx_rel_position ON ai_selection_race_relationships(selection_finish_position);
CREATE INDEX IF NOT EXISTS idx_rel_surprise ON ai_selection_race_relationships(surprise_result);

-- ===============================================
-- 4. AI CONTEXTUAL ANALYSIS CACHE TABLE
-- ===============================================
CREATE TABLE IF NOT EXISTS ai_contextual_analysis_cache (
    id SERIAL PRIMARY KEY,
    
    -- Cache Key
    analysis_type VARCHAR(50) NOT NULL, -- 'daily', 'weekly', 'monthly', 'strategy'
    cache_key VARCHAR(255) NOT NULL UNIQUE,
    
    -- Analysis Data
    analysis_data TEXT NOT NULL, -- JSON analysis results
    
    -- Metadata
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    parameters TEXT, -- JSON of analysis parameters
    
    -- Performance Summary
    selections_analyzed INTEGER,
    accuracy_score DECIMAL(5,4),
    roi_score DECIMAL(8,4),
    confidence_score DECIMAL(5,4)
);

-- Cache Indexes
CREATE INDEX IF NOT EXISTS idx_cache_key ON ai_contextual_analysis_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_type ON ai_contextual_analysis_cache(analysis_type);
CREATE INDEX IF NOT EXISTS idx_cache_expires ON ai_contextual_analysis_cache(expires_at);

-- ===============================================
-- 5. VIEWS FOR QUICK ANALYSIS
-- ===============================================

-- Daily Performance Summary View
CREATE OR REPLACE VIEW daily_ai_performance AS
SELECT 
    DATE(race_date) as analysis_date,
    COUNT(*) as total_selections,
    COUNT(CASE WHEN was_correct THEN 1 END) as correct_selections,
    ROUND(AVG(CASE WHEN was_correct THEN 1.0 ELSE 0.0 END), 4) as accuracy,
    SUM(stake_placed) as total_stakes,
    SUM(payout_received) as total_payouts,
    SUM(profit_loss) as net_profit,
    ROUND(
        CASE 
            WHEN SUM(stake_placed) > 0 
            THEN (SUM(profit_loss) / SUM(stake_placed)) * 100 
            ELSE 0 
        END, 4
    ) as roi_percentage,
    ROUND(AVG(confidence_score), 4) as avg_confidence,
    prediction_method,
    betting_strategy
FROM ai_horse_selections 
WHERE result_updated_at IS NOT NULL
GROUP BY DATE(race_date), prediction_method, betting_strategy
ORDER BY analysis_date DESC;

-- Strategy Performance Comparison View
CREATE OR REPLACE VIEW strategy_performance_comparison AS
SELECT 
    betting_strategy,
    COUNT(*) as total_selections,
    ROUND(AVG(CASE WHEN was_correct THEN 1.0 ELSE 0.0 END), 4) as accuracy,
    SUM(profit_loss) as total_profit,
    ROUND(
        CASE 
            WHEN SUM(stake_placed) > 0 
            THEN (SUM(profit_loss) / SUM(stake_placed)) * 100 
            ELSE 0 
        END, 4
    ) as roi_percentage,
    ROUND(AVG(confidence_score), 4) as avg_confidence,
    COUNT(CASE WHEN value_assessment = 'OVERLAY' THEN 1 END) as overlay_count,
    ROUND(
        AVG(CASE WHEN value_assessment = 'OVERLAY' AND was_correct THEN 1.0 ELSE 0.0 END), 4
    ) as overlay_success_rate
FROM ai_horse_selections 
WHERE result_updated_at IS NOT NULL
  AND betting_strategy IS NOT NULL
GROUP BY betting_strategy
ORDER BY roi_percentage DESC;

-- Method Performance Analysis View
CREATE OR REPLACE VIEW method_performance_analysis AS
SELECT 
    prediction_method,
    COUNT(*) as total_predictions,
    ROUND(AVG(CASE WHEN was_correct THEN 1.0 ELSE 0.0 END), 4) as accuracy,
    ROUND(AVG(confidence_score), 4) as avg_confidence,
    ROUND(AVG(win_probability), 4) as avg_win_probability,
    SUM(profit_loss) as total_profit,
    ROUND(
        CASE 
            WHEN SUM(stake_placed) > 0 
            THEN (SUM(profit_loss) / SUM(stake_placed)) * 100 
            ELSE 0 
        END, 4
    ) as roi_percentage,
    COUNT(CASE WHEN confidence_level = 'HIGH' THEN 1 END) as high_confidence_count,
    ROUND(
        AVG(CASE WHEN confidence_level = 'HIGH' AND was_correct THEN 1.0 ELSE 0.0 END), 4
    ) as high_confidence_accuracy
FROM ai_horse_selections 
WHERE result_updated_at IS NOT NULL
GROUP BY prediction_method
ORDER BY accuracy DESC;

-- ===============================================
-- 6. STORED PROCEDURES FOR ANALYSIS
-- ===============================================

-- Function to calculate confidence calibration
CREATE OR REPLACE FUNCTION calculate_confidence_calibration(
    start_date_param TIMESTAMP DEFAULT NULL,
    end_date_param TIMESTAMP DEFAULT NULL
) RETURNS TABLE (
    confidence_bin VARCHAR(20),
    predicted_accuracy DECIMAL(5,4),
    actual_accuracy DECIMAL(5,4),
    calibration_score DECIMAL(5,4),
    sample_size INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH confidence_bins AS (
        SELECT 
            CASE 
                WHEN confidence_score < 0.6 THEN 'LOW'
                WHEN confidence_score < 0.8 THEN 'MEDIUM'
                ELSE 'HIGH'
            END as bin,
            CASE 
                WHEN confidence_score < 0.6 THEN 0.5
                WHEN confidence_score < 0.8 THEN 0.7
                ELSE 0.85
            END as expected_acc,
            CASE WHEN was_correct THEN 1.0 ELSE 0.0 END as actual_result,
            1 as count_record
        FROM ai_horse_selections
        WHERE result_updated_at IS NOT NULL
          AND (start_date_param IS NULL OR race_date >= start_date_param)
          AND (end_date_param IS NULL OR race_date <= end_date_param)
    )
    SELECT 
        bin::VARCHAR(20),
        expected_acc::DECIMAL(5,4),
        ROUND(AVG(actual_result), 4)::DECIMAL(5,4),
        ROUND(1.0 - ABS(expected_acc - AVG(actual_result)), 4)::DECIMAL(5,4),
        SUM(count_record)::INTEGER
    FROM confidence_bins
    GROUP BY bin, expected_acc
    ORDER BY bin;
END;
$$ LANGUAGE plpgsql;

-- Function to get top performing conditions
CREATE OR REPLACE FUNCTION get_top_conditions(
    condition_type VARCHAR(50), -- 'weather', 'track', 'class'
    limit_results INTEGER DEFAULT 5
) RETURNS TABLE (
    condition_value VARCHAR(100),
    selection_count INTEGER,
    accuracy DECIMAL(5,4),
    roi_percentage DECIMAL(8,4)
) AS $$
BEGIN
    IF condition_type = 'weather' THEN
        RETURN QUERY
        SELECT 
            weather_conditions::VARCHAR(100),
            COUNT(*)::INTEGER,
            ROUND(AVG(CASE WHEN was_correct THEN 1.0 ELSE 0.0 END), 4)::DECIMAL(5,4),
            ROUND(
                CASE 
                    WHEN SUM(stake_placed) > 0 
                    THEN (SUM(profit_loss) / SUM(stake_placed)) * 100 
                    ELSE 0 
                END, 4
            )::DECIMAL(8,4)
        FROM ai_horse_selections
        WHERE result_updated_at IS NOT NULL
          AND weather_conditions IS NOT NULL
        GROUP BY weather_conditions
        HAVING COUNT(*) >= 5
        ORDER BY ROUND(AVG(CASE WHEN was_correct THEN 1.0 ELSE 0.0 END), 4) DESC
        LIMIT limit_results;
        
    ELSIF condition_type = 'track' THEN
        RETURN QUERY
        SELECT 
            track_condition::VARCHAR(100),
            COUNT(*)::INTEGER,
            ROUND(AVG(CASE WHEN was_correct THEN 1.0 ELSE 0.0 END), 4)::DECIMAL(5,4),
            ROUND(
                CASE 
                    WHEN SUM(stake_placed) > 0 
                    THEN (SUM(profit_loss) / SUM(stake_placed)) * 100 
                    ELSE 0 
                END, 4
            )::DECIMAL(8,4)
        FROM ai_horse_selections
        WHERE result_updated_at IS NOT NULL
          AND track_condition IS NOT NULL
        GROUP BY track_condition
        HAVING COUNT(*) >= 5
        ORDER BY ROUND(AVG(CASE WHEN was_correct THEN 1.0 ELSE 0.0 END), 4) DESC
        LIMIT limit_results;
        
    ELSIF condition_type = 'class' THEN
        RETURN QUERY
        SELECT 
            race_class::VARCHAR(100),
            COUNT(*)::INTEGER,
            ROUND(AVG(CASE WHEN was_correct THEN 1.0 ELSE 0.0 END), 4)::DECIMAL(5,4),
            ROUND(
                CASE 
                    WHEN SUM(stake_placed) > 0 
                    THEN (SUM(profit_loss) / SUM(stake_placed)) * 100 
                    ELSE 0 
                END, 4
            )::DECIMAL(8,4)
        FROM ai_horse_selections
        WHERE result_updated_at IS NOT NULL
          AND race_class IS NOT NULL
        GROUP BY race_class
        HAVING COUNT(*) >= 5
        ORDER BY ROUND(AVG(CASE WHEN was_correct THEN 1.0 ELSE 0.0 END), 4) DESC
        LIMIT limit_results;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ===============================================
-- 7. COMMENTS AND DOCUMENTATION
-- ===============================================

COMMENT ON TABLE ai_horse_selections IS 'Comprehensive tracking of AI horse selections with profit/loss and contextual data';
COMMENT ON TABLE ai_selection_performance IS 'Aggregated performance metrics for different time periods and strategies';
COMMENT ON TABLE ai_selection_race_relationships IS 'Relationships between AI selections and race results for contextual analysis';
COMMENT ON TABLE ai_contextual_analysis_cache IS 'Cached analysis results to improve performance';

COMMENT ON COLUMN ai_horse_selections.selection_id IS 'Unique identifier for each AI selection';
COMMENT ON COLUMN ai_horse_selections.prediction_method IS 'AI method used: raw_ratings, monte_carlo, ai_ml, consensus';
COMMENT ON COLUMN ai_horse_selections.confidence_score IS 'AI confidence in prediction (0.0 to 1.0)';
COMMENT ON COLUMN ai_horse_selections.value_assessment IS 'Market value assessment: OVERLAY, UNDERLAY, FAIR';
COMMENT ON COLUMN ai_horse_selections.edge_percentage IS 'Calculated betting edge over market odds';
COMMENT ON COLUMN ai_horse_selections.roi_percentage IS 'Return on investment percentage for this selection';

-- ===============================================
-- 8. SAMPLE QUERIES FOR ANALYSIS
-- ===============================================

-- Daily performance trend
-- SELECT * FROM daily_ai_performance ORDER BY analysis_date DESC LIMIT 30;

-- Best performing strategies
-- SELECT * FROM strategy_performance_comparison WHERE total_selections >= 20;

-- Method comparison
-- SELECT * FROM method_performance_analysis;

-- Confidence calibration check
-- SELECT * FROM calculate_confidence_calibration(CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE);

-- Top weather conditions
-- SELECT * FROM get_top_conditions('weather', 10);

-- Recent high-confidence selections
-- SELECT selection_id, horse_name, course, confidence_score, was_correct, roi_percentage
-- FROM ai_horse_selections 
-- WHERE confidence_level = 'HIGH' 
--   AND race_date >= CURRENT_DATE - INTERVAL '7 days'
-- ORDER BY race_date DESC;
