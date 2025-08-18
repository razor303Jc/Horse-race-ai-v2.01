-- =============================================================================
-- Race Trends & AI Performance Database Schema for Horse Racing AI v2.0
-- =============================================================================
-- Comprehensive database schema for storing race trends analysis, AI betting
-- performance, and strategy effectiveness tracking.
-- =============================================================================

-- Race Trends Analysis Tables
-- =============================================================================

-- Store individual race trend patterns
CREATE TABLE race_trends (
    id SERIAL PRIMARY KEY,
    race_id VARCHAR(255) NOT NULL,
    trend_category VARCHAR(50) NOT NULL, -- age, weight, draw, form, price, seasonal, course_form, distance_form
    trend_type VARCHAR(100) NOT NULL,    -- specific trend within category
    pattern_description TEXT,
    confidence_score DECIMAL(5,4) NOT NULL DEFAULT 0.0, -- 0.0 to 1.0
    edge_value DECIMAL(8,4) NOT NULL DEFAULT 0.0,       -- statistical edge
    sample_size INTEGER NOT NULL DEFAULT 0,
    historical_strike_rate DECIMAL(5,4) DEFAULT 0.0,
    significance_level DECIMAL(5,4) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_race_trends_race_id ON race_trends (race_id);
CREATE INDEX idx_race_trends_category ON race_trends (trend_category);
CREATE INDEX idx_race_trends_confidence ON race_trends (confidence_score);
CREATE INDEX idx_race_trends_edge ON race_trends (edge_value);

-- Store race analysis with all trend categories
CREATE TABLE race_analysis_trends (
    id SERIAL PRIMARY KEY,
    race_id VARCHAR(255) NOT NULL UNIQUE,
    track VARCHAR(100),
    race_date DATE,
    distance DECIMAL(4,1),
    surface VARCHAR(20),
    race_class VARCHAR(50),
    
    -- Trend analysis metadata
    total_trends_identified INTEGER NOT NULL DEFAULT 0,
    high_confidence_trends INTEGER NOT NULL DEFAULT 0,
    overall_edge_rating DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    trend_strength VARCHAR(20) DEFAULT 'WEAK',  -- WEAK, MODERATE, STRONG
    
    -- Age trends
    age_trends_count INTEGER DEFAULT 0,
    age_trends_edge DECIMAL(8,4) DEFAULT 0.0,
    
    -- Weight trends
    weight_trends_count INTEGER DEFAULT 0,
    weight_trends_edge DECIMAL(8,4) DEFAULT 0.0,
    
    -- Draw trends
    draw_trends_count INTEGER DEFAULT 0,
    draw_trends_edge DECIMAL(8,4) DEFAULT 0.0,
    
    -- Form trends
    form_trends_count INTEGER DEFAULT 0,
    form_trends_edge DECIMAL(8,4) DEFAULT 0.0,
    
    -- Price trends
    price_trends_count INTEGER DEFAULT 0,
    price_trends_edge DECIMAL(8,4) DEFAULT 0.0,
    
    -- Seasonal trends
    seasonal_trends_count INTEGER DEFAULT 0,
    seasonal_trends_edge DECIMAL(8,4) DEFAULT 0.0,
    
    -- Course form trends
    course_form_trends_count INTEGER DEFAULT 0,
    course_form_trends_edge DECIMAL(8,4) DEFAULT 0.0,
    
    -- Distance form trends
    distance_form_trends_count INTEGER DEFAULT 0,
    distance_form_trends_edge DECIMAL(8,4) DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_race_analysis_trends_race_id ON race_analysis_trends (race_id);
CREATE INDEX idx_race_analysis_trends_date ON race_analysis_trends (race_date);
CREATE INDEX idx_race_analysis_trends_edge ON race_analysis_trends (overall_edge_rating);
CREATE INDEX idx_race_analysis_trends_strength ON race_analysis_trends (trend_strength);

-- Store individual horse trend scores
CREATE TABLE horse_trend_scores (
    id SERIAL PRIMARY KEY,
    race_id VARCHAR(255) NOT NULL,
    horse_name VARCHAR(255) NOT NULL,
    
    -- Overall trend score
    overall_trend_score DECIMAL(6,2) NOT NULL DEFAULT 0.0,
    trend_rank INTEGER DEFAULT 0,
    trend_confidence DECIMAL(5,4) DEFAULT 0.0,
    
    -- Individual trend category scores
    age_trend_score DECIMAL(6,2) DEFAULT 0.0,
    weight_trend_score DECIMAL(6,2) DEFAULT 0.0,
    draw_trend_score DECIMAL(6,2) DEFAULT 0.0,
    form_trend_score DECIMAL(6,2) DEFAULT 0.0,
    price_trend_score DECIMAL(6,2) DEFAULT 0.0,
    seasonal_trend_score DECIMAL(6,2) DEFAULT 0.0,
    course_form_trend_score DECIMAL(6,2) DEFAULT 0.0,
    distance_form_trend_score DECIMAL(6,2) DEFAULT 0.0,
    
    -- Trend impact factors
    positive_trends_count INTEGER DEFAULT 0,
    negative_trends_count INTEGER DEFAULT 0,
    neutral_trends_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_horse_trend_scores_race_id ON horse_trend_scores (race_id);
CREATE INDEX idx_horse_trend_scores_horse ON horse_trend_scores (horse_name);
CREATE INDEX idx_horse_trend_scores_overall ON horse_trend_scores (overall_trend_score);
CREATE INDEX idx_horse_trend_scores_rank ON horse_trend_scores (trend_rank);
ALTER TABLE horse_trend_scores ADD CONSTRAINT unique_horse_race_trend UNIQUE (race_id, horse_name);

-- AI Betting Performance Tables
-- =============================================================================

-- Store AI prediction records for each race
CREATE TABLE ai_predictions (
    id SERIAL PRIMARY KEY,
    race_id VARCHAR(255) NOT NULL,
    horse_name VARCHAR(255) NOT NULL,
    prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- AI prediction methods and scores
    raw_rating DECIMAL(6,2) DEFAULT 0.0,
    monte_carlo_rating DECIMAL(6,2) DEFAULT 0.0,
    ai_ml_rating DECIMAL(6,2) DEFAULT 0.0,
    consensus_rating DECIMAL(6,2) DEFAULT 0.0,
    
    -- Probability estimates
    raw_win_probability DECIMAL(5,4) DEFAULT 0.0,
    monte_carlo_win_probability DECIMAL(5,4) DEFAULT 0.0,
    ai_ml_win_probability DECIMAL(5,4) DEFAULT 0.0,
    consensus_win_probability DECIMAL(5,4) DEFAULT 0.0,
    
    -- Confidence and agreement metrics
    prediction_confidence DECIMAL(5,4) DEFAULT 0.0,
    method_agreement_score DECIMAL(5,4) DEFAULT 0.0,
    prediction_consistency DECIMAL(5,4) DEFAULT 0.0,
    
    -- Market comparison
    betting_odds DECIMAL(8,2) DEFAULT 0.0,
    implied_probability DECIMAL(5,4) DEFAULT 0.0,
    value_rating DECIMAL(6,2) DEFAULT 0.0,
    
    -- Actual result (filled after race)
    actual_finish_position INTEGER DEFAULT NULL,
    prediction_accuracy DECIMAL(5,4) DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_predictions_race_id ON ai_predictions (race_id);
CREATE INDEX idx_ai_predictions_horse ON ai_predictions (horse_name);
CREATE INDEX idx_ai_predictions_confidence ON ai_predictions (prediction_confidence);
CREATE INDEX idx_ai_predictions_accuracy ON ai_predictions (prediction_accuracy);
CREATE INDEX idx_ai_predictions_value ON ai_predictions (value_rating);
ALTER TABLE ai_predictions ADD CONSTRAINT unique_ai_prediction UNIQUE (race_id, horse_name);

-- Store betting strategy recommendations and results
CREATE TABLE betting_strategies (
    id SERIAL PRIMARY KEY,
    race_id VARCHAR(255) NOT NULL,
    horse_name VARCHAR(255) NOT NULL,
    strategy_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Strategy details
    strategy_type VARCHAR(50) NOT NULL, -- value_bet, dutching, each_way, twenty_eighty
    bet_type VARCHAR(20) NOT NULL,      -- win, place, show, exacta, trifecta
    
    -- Recommendation details
    recommended_stake DECIMAL(10,2) DEFAULT 0.0,
    recommended_odds DECIMAL(8,2) DEFAULT 0.0,
    expected_value DECIMAL(8,4) DEFAULT 0.0,
    kelly_fraction DECIMAL(6,4) DEFAULT 0.0,
    confidence_score DECIMAL(5,4) DEFAULT 0.0,
    risk_rating VARCHAR(20) DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH
    
    -- Staking method used
    staking_method VARCHAR(20) DEFAULT 'percentage', -- kelly, percentage, fixed, value_based
    staking_multiplier DECIMAL(4,2) DEFAULT 1.0,
    
    -- Actual bet placed (if any)
    actual_stake DECIMAL(10,2) DEFAULT 0.0,
    actual_odds DECIMAL(8,2) DEFAULT 0.0,
    bet_placed BOOLEAN DEFAULT FALSE,
    
    -- Results (filled after race)
    actual_result VARCHAR(20) DEFAULT NULL, -- win, place, show, loss
    payout DECIMAL(10,2) DEFAULT 0.0,
    profit_loss DECIMAL(10,2) DEFAULT 0.0,
    roi_percentage DECIMAL(8,4) DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_betting_strategies_race_id (race_id),
    INDEX idx_betting_strategies_horse (horse_name),
    INDEX idx_betting_strategies_type (strategy_type),
    INDEX idx_betting_strategies_risk (risk_rating),
    INDEX idx_betting_strategies_roi (roi_percentage),
    INDEX idx_betting_strategies_profit (profit_loss)
);

-- Store overall performance metrics by AI method
CREATE TABLE ai_method_performance (
    id SERIAL PRIMARY KEY,
    method_name VARCHAR(50) NOT NULL,    -- raw_ratings, monte_carlo, ai_ml, consensus
    calculation_date DATE NOT NULL,
    
    -- Prediction accuracy metrics
    total_predictions INTEGER NOT NULL DEFAULT 0,
    correct_predictions INTEGER NOT NULL DEFAULT 0,
    win_accuracy DECIMAL(5,4) DEFAULT 0.0,
    place_accuracy DECIMAL(5,4) DEFAULT 0.0,
    overall_accuracy DECIMAL(5,4) DEFAULT 0.0,
    
    -- Betting performance metrics
    total_bets INTEGER DEFAULT 0,
    winning_bets INTEGER DEFAULT 0,
    total_wagered DECIMAL(12,2) DEFAULT 0.0,
    total_returned DECIMAL(12,2) DEFAULT 0.0,
    net_profit DECIMAL(12,2) DEFAULT 0.0,
    roi_percentage DECIMAL(8,4) DEFAULT 0.0,
    
    -- Risk metrics
    win_rate DECIMAL(5,4) DEFAULT 0.0,
    average_win DECIMAL(10,2) DEFAULT 0.0,
    average_loss DECIMAL(10,2) DEFAULT 0.0,
    profit_factor DECIMAL(6,2) DEFAULT 0.0,
    maximum_drawdown DECIMAL(8,4) DEFAULT 0.0,
    sharpe_ratio DECIMAL(6,4) DEFAULT 0.0,
    
    -- Confidence calibration
    confidence_calibration DECIMAL(5,4) DEFAULT 0.0,
    prediction_consistency DECIMAL(5,4) DEFAULT 0.0,
    method_agreement DECIMAL(5,4) DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_ai_method_performance_method (method_name),
    INDEX idx_ai_method_performance_date (calculation_date),
    INDEX idx_ai_method_performance_accuracy (overall_accuracy),
    INDEX idx_ai_method_performance_roi (roi_percentage),
    UNIQUE KEY unique_method_date (method_name, calculation_date)
);

-- Store strategy effectiveness analysis
CREATE TABLE strategy_performance (
    id SERIAL PRIMARY KEY,
    strategy_type VARCHAR(50) NOT NULL,
    calculation_date DATE NOT NULL,
    
    -- Usage statistics
    total_opportunities INTEGER NOT NULL DEFAULT 0,
    strategies_used INTEGER NOT NULL DEFAULT 0,
    usage_rate DECIMAL(5,4) DEFAULT 0.0,
    
    -- Performance metrics
    total_profit DECIMAL(12,2) DEFAULT 0.0,
    total_stakes DECIMAL(12,2) DEFAULT 0.0,
    roi_percentage DECIMAL(8,4) DEFAULT 0.0,
    win_rate DECIMAL(5,4) DEFAULT 0.0,
    average_odds DECIMAL(6,2) DEFAULT 0.0,
    
    -- Strategy-specific metrics
    value_capture_rate DECIMAL(5,4) DEFAULT 0.0,    -- for value betting
    dutching_efficiency DECIMAL(5,4) DEFAULT 0.0,   -- for dutching
    kelly_accuracy DECIMAL(5,4) DEFAULT 0.0,        -- for kelly criterion
    
    -- Risk analysis
    maximum_loss DECIMAL(10,2) DEFAULT 0.0,
    maximum_drawdown DECIMAL(8,4) DEFAULT 0.0,
    volatility DECIMAL(6,4) DEFAULT 0.0,
    consecutive_losses INTEGER DEFAULT 0,
    
    -- Recommendation effectiveness
    high_confidence_success DECIMAL(5,4) DEFAULT 0.0,
    medium_confidence_success DECIMAL(5,4) DEFAULT 0.0,
    low_confidence_success DECIMAL(5,4) DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_strategy_performance_type (strategy_type),
    INDEX idx_strategy_performance_date (calculation_date),
    INDEX idx_strategy_performance_roi (roi_percentage),
    INDEX idx_strategy_performance_usage (usage_rate),
    UNIQUE KEY unique_strategy_date (strategy_type, calculation_date)
);

-- Store bankroll management history
CREATE TABLE bankroll_history (
    id SERIAL PRIMARY KEY,
    record_date DATE NOT NULL,
    
    -- Bankroll status
    starting_balance DECIMAL(12,2) NOT NULL,
    current_balance DECIMAL(12,2) NOT NULL,
    peak_balance DECIMAL(12,2) NOT NULL,
    
    -- Performance metrics
    total_wagered DECIMAL(12,2) DEFAULT 0.0,
    total_returned DECIMAL(12,2) DEFAULT 0.0,
    net_profit DECIMAL(12,2) DEFAULT 0.0,
    roi_percentage DECIMAL(8,4) DEFAULT 0.0,
    
    -- Risk metrics
    drawdown_percentage DECIMAL(6,4) DEFAULT 0.0,
    risk_level VARCHAR(20) DEFAULT 'MEDIUM',
    recommended_max_bet DECIMAL(10,2) DEFAULT 0.0,
    
    -- Activity metrics
    total_bets INTEGER DEFAULT 0,
    winning_bets INTEGER DEFAULT 0,
    win_rate DECIMAL(5,4) DEFAULT 0.0,
    
    -- Kelly metrics
    kelly_fraction_average DECIMAL(6,4) DEFAULT 0.0,
    overbet_frequency DECIMAL(5,4) DEFAULT 0.0,
    underbet_frequency DECIMAL(5,4) DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_bankroll_history_date (record_date),
    INDEX idx_bankroll_history_balance (current_balance),
    INDEX idx_bankroll_history_roi (roi_percentage),
    INDEX idx_bankroll_history_risk (risk_level),
    UNIQUE KEY unique_bankroll_date (record_date)
);

-- Store AI reward signals for machine learning
CREATE TABLE ai_reward_signals (
    id SERIAL PRIMARY KEY,
    race_id VARCHAR(255) NOT NULL,
    signal_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Learning signals
    method_agreement DECIMAL(5,4) DEFAULT 0.0,
    prediction_consistency DECIMAL(5,4) DEFAULT 0.0,
    market_efficiency DECIMAL(5,4) DEFAULT 0.0,
    confidence_accuracy DECIMAL(5,4) DEFAULT 0.0,
    
    -- Reward factors
    prediction_reward DECIMAL(8,4) DEFAULT 0.0,
    profitability_reward DECIMAL(8,4) DEFAULT 0.0,
    consistency_reward DECIMAL(8,4) DEFAULT 0.0,
    risk_management_reward DECIMAL(8,4) DEFAULT 0.0,
    
    -- Penalty factors
    prediction_penalty DECIMAL(8,4) DEFAULT 0.0,
    loss_penalty DECIMAL(8,4) DEFAULT 0.0,
    inconsistency_penalty DECIMAL(8,4) DEFAULT 0.0,
    overconfidence_penalty DECIMAL(8,4) DEFAULT 0.0,
    
    -- Net reward calculation
    total_reward DECIMAL(8,4) DEFAULT 0.0,
    total_penalty DECIMAL(8,4) DEFAULT 0.0,
    net_reward DECIMAL(8,4) DEFAULT 0.0,
    
    -- Context data for learning
    race_difficulty DECIMAL(5,4) DEFAULT 0.0,
    field_size INTEGER DEFAULT 0,
    track_conditions VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_ai_reward_signals_race_id (race_id),
    INDEX idx_ai_reward_signals_timestamp (signal_timestamp),
    INDEX idx_ai_reward_signals_net_reward (net_reward),
    INDEX idx_ai_reward_signals_method_agreement (method_agreement)
);

-- Store temporal performance patterns
CREATE TABLE performance_patterns (
    id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(50) NOT NULL,   -- daily, weekly, monthly, seasonal
    period_key VARCHAR(50) NOT NULL,     -- 2024-01-15, 2024-W03, 2024-01, Q1-2024
    
    -- Performance metrics for this period
    total_races INTEGER NOT NULL DEFAULT 0,
    total_predictions INTEGER NOT NULL DEFAULT 0,
    prediction_accuracy DECIMAL(5,4) DEFAULT 0.0,
    
    -- Betting performance
    total_bets INTEGER DEFAULT 0,
    total_wagered DECIMAL(12,2) DEFAULT 0.0,
    total_returned DECIMAL(12,2) DEFAULT 0.0,
    net_profit DECIMAL(12,2) DEFAULT 0.0,
    roi_percentage DECIMAL(8,4) DEFAULT 0.0,
    win_rate DECIMAL(5,4) DEFAULT 0.0,
    
    -- Best performing elements
    best_method VARCHAR(50),
    best_strategy VARCHAR(50),
    best_track VARCHAR(100),
    best_race_class VARCHAR(50),
    
    -- Pattern insights
    trend_direction VARCHAR(20) DEFAULT 'STABLE', -- IMPROVING, DECLINING, STABLE
    consistency_score DECIMAL(5,4) DEFAULT 0.0,
    volatility DECIMAL(6,4) DEFAULT 0.0,
    
    period_start DATE,
    period_end DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_performance_patterns_type (pattern_type),
    INDEX idx_performance_patterns_period (period_key),
    INDEX idx_performance_patterns_roi (roi_percentage),
    INDEX idx_performance_patterns_accuracy (prediction_accuracy),
    UNIQUE KEY unique_pattern_period (pattern_type, period_key)
);

-- =============================================================================
-- Views for Easy Data Access
-- =============================================================================

-- Comprehensive race analysis view
CREATE VIEW v_race_performance_summary AS
SELECT 
    rat.race_id,
    rat.track,
    rat.race_date,
    rat.distance,
    rat.surface,
    rat.race_class,
    
    -- Trends analysis
    rat.total_trends_identified,
    rat.high_confidence_trends,
    rat.overall_edge_rating,
    rat.trend_strength,
    
    -- AI performance
    COUNT(ap.id) as total_ai_predictions,
    AVG(ap.prediction_confidence) as avg_ai_confidence,
    AVG(ap.prediction_accuracy) as avg_ai_accuracy,
    
    -- Betting performance
    COUNT(bs.id) as total_betting_strategies,
    SUM(bs.actual_stake) as total_stakes,
    SUM(bs.payout) as total_payouts,
    SUM(bs.profit_loss) as net_profit,
    AVG(bs.roi_percentage) as avg_roi
    
FROM race_analysis_trends rat
LEFT JOIN ai_predictions ap ON rat.race_id = ap.race_id
LEFT JOIN betting_strategies bs ON rat.race_id = bs.race_id
GROUP BY rat.race_id, rat.track, rat.race_date, rat.distance, rat.surface, 
         rat.race_class, rat.total_trends_identified, rat.high_confidence_trends,
         rat.overall_edge_rating, rat.trend_strength;

-- Method performance comparison view
CREATE VIEW v_method_performance_comparison AS
SELECT 
    method_name,
    calculation_date,
    overall_accuracy,
    roi_percentage,
    win_rate,
    profit_factor,
    maximum_drawdown,
    confidence_calibration,
    RANK() OVER (PARTITION BY calculation_date ORDER BY roi_percentage DESC) as roi_rank,
    RANK() OVER (PARTITION BY calculation_date ORDER BY overall_accuracy DESC) as accuracy_rank
FROM ai_method_performance
WHERE calculation_date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY);

-- Strategy effectiveness view
CREATE VIEW v_strategy_effectiveness AS
SELECT 
    strategy_type,
    calculation_date,
    usage_rate,
    roi_percentage,
    win_rate,
    value_capture_rate,
    maximum_drawdown,
    high_confidence_success,
    CASE 
        WHEN roi_percentage > 10 AND win_rate > 0.4 THEN 'EXCELLENT'
        WHEN roi_percentage > 5 AND win_rate > 0.3 THEN 'GOOD'
        WHEN roi_percentage > 0 AND win_rate > 0.25 THEN 'FAIR'
        ELSE 'POOR'
    END as effectiveness_rating
FROM strategy_performance
WHERE calculation_date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY);

-- =============================================================================
-- Indexes for Performance Optimization
-- =============================================================================

-- Composite indexes for common query patterns
CREATE INDEX idx_race_performance_date_track ON race_analysis_trends (race_date, track);
CREATE INDEX idx_ai_predictions_date_confidence ON ai_predictions (prediction_timestamp, prediction_confidence);
CREATE INDEX idx_betting_strategies_date_type ON betting_strategies (strategy_timestamp, strategy_type);
CREATE INDEX idx_method_performance_date_roi ON ai_method_performance (calculation_date, roi_percentage);
CREATE INDEX idx_strategy_performance_date_roi ON strategy_performance (calculation_date, roi_percentage);

-- =============================================================================
-- Comments and Documentation
-- =============================================================================

-- Add table comments for documentation
ALTER TABLE race_trends COMMENT = 'Individual race trend patterns identified by RaceTrendsAnalyzer';
ALTER TABLE race_analysis_trends COMMENT = 'Complete race analysis with all trend categories and edge ratings';
ALTER TABLE horse_trend_scores COMMENT = 'Individual horse scores against identified race trends';
ALTER TABLE ai_predictions COMMENT = 'AI prediction records for all methods with accuracy tracking';
ALTER TABLE betting_strategies COMMENT = 'Betting strategy recommendations and actual results';
ALTER TABLE ai_method_performance COMMENT = 'Performance metrics by AI prediction method';
ALTER TABLE strategy_performance COMMENT = 'Effectiveness analysis of different betting strategies';
ALTER TABLE bankroll_history COMMENT = 'Historical bankroll management and performance tracking';
ALTER TABLE ai_reward_signals COMMENT = 'Reward signals for AI machine learning and improvement';
ALTER TABLE performance_patterns COMMENT = 'Temporal performance patterns for trend analysis';
