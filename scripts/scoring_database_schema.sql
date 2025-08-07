-- Horse Form Scoring Database Schema
-- This creates tables to store detailed form analysis, power ratings, and speed/pace data

-- Form Analysis Results Table
CREATE TABLE IF NOT EXISTS form_analysis (
    id SERIAL PRIMARY KEY,
    horse_name VARCHAR(255) NOT NULL,
    race_id VARCHAR(100),
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Recent form scores (0.0-1.0)
    last_run_score DECIMAL(5,3),
    recent_form_score DECIMAL(5,3),
    seasonal_form_score DECIMAL(5,3),
    
    -- Speed metrics (0-120)
    speed_rating DECIMAL(6,2),
    pace_rating DECIMAL(6,2),
    finishing_speed_index DECIMAL(6,2),
    
    -- Consistency metrics (0.0-1.0)
    consistency_index DECIMAL(5,3),
    reliability_score DECIMAL(5,3),
    
    -- Class and competition (0-100)
    class_rating DECIMAL(6,2),
    competition_strength DECIMAL(6,2),
    
    -- Track and conditions (0.0-1.0)
    track_bias_adjustment DECIMAL(5,3),
    condition_suitability DECIMAL(5,3),
    
    -- Distance and trip (0.0-1.0)
    distance_suitability DECIMAL(5,3),
    trip_efficiency DECIMAL(5,3),
    
    -- Jockey/Trainer combination (0.0-1.0)
    jockey_form DECIMAL(5,3),
    trainer_form DECIMAL(5,3),
    combo_efficiency DECIMAL(5,3),
    
    -- Overall composite scores
    form_composite DECIMAL(6,2),
    power_rating DECIMAL(6,2),
    confidence_level DECIMAL(5,3),
    
    -- Metadata
    target_race_conditions JSONB,
    factors_breakdown JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(horse_name, race_id, analysis_date)
);

-- Power Ratings Table  
CREATE TABLE IF NOT EXISTS power_ratings (
    id SERIAL PRIMARY KEY,
    horse_name VARCHAR(255) NOT NULL,
    race_id VARCHAR(100),
    rating_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Core power rating values (0-150)
    base_rating DECIMAL(6,2) NOT NULL,
    adjusted_rating DECIMAL(6,2) NOT NULL,
    
    -- Component breakdowns (0-150)
    speed_component DECIMAL(6,2),
    class_component DECIMAL(6,2),
    form_component DECIMAL(6,2),
    consistency_component DECIMAL(6,2),
    
    -- Adjustments
    conditions_adjustment DECIMAL(6,2),
    track_bias_adj DECIMAL(6,2),
    distance_specialization_adj DECIMAL(6,2),
    surface_suitability_adj DECIMAL(6,2),
    jockey_trainer_adj DECIMAL(6,2),
    equipment_change_adj DECIMAL(6,2),
    layoff_adj DECIMAL(6,2),
    class_movement_adj DECIMAL(6,2),
    weight_allowance_adj DECIMAL(6,2),
    
    -- Metadata
    confidence_level DECIMAL(5,3),
    target_race_conditions JSONB,
    adjustment_factors JSONB,
    factors_breakdown JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(horse_name, race_id, rating_date)
);

-- Composite Scoring Results Table
CREATE TABLE IF NOT EXISTS composite_scores (
    id SERIAL PRIMARY KEY,
    horse_name VARCHAR(255) NOT NULL,
    race_id VARCHAR(100),
    scoring_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Core scores (0-100)
    form_score DECIMAL(6,2),
    power_rating DECIMAL(6,2),
    composite_score DECIMAL(6,2),
    
    -- Component breakdowns (0-100)
    speed_score DECIMAL(6,2),
    class_score DECIMAL(6,2),
    consistency_score DECIMAL(6,2),
    form_trend_score DECIMAL(6,2),
    conditions_score DECIMAL(6,2),
    
    -- Probability assessments (0.0-1.0)
    win_probability DECIMAL(5,3),
    place_probability DECIMAL(5,3),
    show_probability DECIMAL(5,3),
    confidence_level DECIMAL(5,3),
    
    -- Rankings
    composite_rank INTEGER,
    power_rating_rank INTEGER,
    form_rank INTEGER,
    
    -- Betting analysis
    betting_odds DECIMAL(8,2),
    betting_value DECIMAL(6,3), -- Can be negative
    
    -- Analysis insights
    key_factors TEXT[],
    concerns TEXT[],
    factors_breakdown JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(horse_name, race_id, scoring_date)
);

-- Speed and Pace Analysis Table
CREATE TABLE IF NOT EXISTS speed_pace_analysis (
    id SERIAL PRIMARY KEY,
    horse_name VARCHAR(255) NOT NULL,
    race_id VARCHAR(100),
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Speed figures and ratings
    base_speed_rating DECIMAL(6,2),
    adjusted_speed_rating DECIMAL(6,2),
    speed_figure DECIMAL(6,2),
    
    -- Pace analysis
    early_pace_rating DECIMAL(6,2),
    middle_pace_rating DECIMAL(6,2),
    late_pace_rating DECIMAL(6,2),
    finishing_kick_rating DECIMAL(6,2),
    
    -- Pace scenario suitability
    pace_scenario VARCHAR(50), -- 'fast', 'moderate', 'slow'
    pace_suitability_score DECIMAL(6,2),
    
    -- Speed trends and patterns
    speed_trend_direction VARCHAR(20), -- 'improving', 'declining', 'stable'
    speed_trend_score DECIMAL(6,3), -- -1.0 to 1.0
    speed_consistency DECIMAL(5,3),
    
    -- Distance and surface speed specialization
    distance_speed_rating DECIMAL(6,2),
    surface_speed_rating DECIMAL(6,2),
    
    -- Comparative speed metrics
    class_par_speed DECIMAL(6,2),
    speed_vs_class DECIMAL(6,3), -- How speed compares to class average
    
    -- Trip and efficiency analysis
    trip_rating DECIMAL(6,2),
    trouble_encountered BOOLEAN DEFAULT FALSE,
    wide_trip BOOLEAN DEFAULT FALSE,
    traffic_issues BOOLEAN DEFAULT FALSE,
    
    -- Environmental factors
    track_variant DECIMAL(6,2),
    track_condition VARCHAR(20),
    wind_factor DECIMAL(5,2),
    
    -- Sectional times (if available)
    sectional_times JSONB,
    fractional_times JSONB,
    
    -- Metadata
    analysis_confidence DECIMAL(5,3),
    data_quality_score DECIMAL(5,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(horse_name, race_id, analysis_date)
);

-- Race Analysis Summary Table
CREATE TABLE IF NOT EXISTS race_analysis (
    id SERIAL PRIMARY KEY,
    race_id VARCHAR(100) NOT NULL,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Race context
    race_conditions JSONB,
    field_size INTEGER,
    race_type VARCHAR(50),
    distance DECIMAL(4,1),
    surface VARCHAR(20),
    track_condition VARCHAR(20),
    
    -- Pace scenario analysis
    predicted_pace_scenario VARCHAR(50),
    pace_competitiveness DECIMAL(5,3),
    early_speed_horses INTEGER,
    closers_count INTEGER,
    
    -- Track bias and conditions
    track_bias VARCHAR(50), -- 'inside', 'outside', 'neutral'
    bias_strength DECIMAL(5,3),
    weather_impact DECIMAL(5,3),
    
    -- Field analysis
    field_strength_rating DECIMAL(6,2),
    class_homogeneity DECIMAL(5,3), -- How similar the class levels are
    form_spread DECIMAL(5,3), -- Range of form ratings
    
    -- Key insights and angles
    key_angles TEXT[],
    betting_angles TEXT[],
    value_opportunities TEXT[],
    potential_overlays TEXT[],
    
    -- Race competitiveness
    competitiveness_rating DECIMAL(5,3),
    expected_margin DECIMAL(4,1),
    confidence_in_analysis DECIMAL(5,3),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(race_id, analysis_date)
);

-- Horse Performance Trends Table
CREATE TABLE IF NOT EXISTS horse_performance_trends (
    id SERIAL PRIMARY KEY,
    horse_name VARCHAR(255) NOT NULL,
    trend_period VARCHAR(20), -- '30_days', '90_days', '365_days'
    trend_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Form trends
    form_trend_direction VARCHAR(20), -- 'improving', 'declining', 'stable'
    form_trend_strength DECIMAL(5,3), -- -1.0 to 1.0
    consistency_trend DECIMAL(5,3),
    
    -- Class trends
    class_progression DECIMAL(6,3),
    purse_trend DECIMAL(8,2),
    competition_level_trend DECIMAL(5,3),
    
    -- Speed trends
    speed_progression DECIMAL(6,3),
    pace_adaptation DECIMAL(5,3),
    finishing_ability_trend DECIMAL(5,3),
    
    -- Condition-specific trends
    distance_performance_trend JSONB, -- By distance
    surface_performance_trend JSONB,  -- By surface
    track_performance_trend JSONB,    -- By track
    
    -- Jockey/Trainer trends
    jockey_combo_trend DECIMAL(5,3),
    trainer_form_trend DECIMAL(5,3),
    stable_confidence DECIMAL(5,3),
    
    -- Statistical measures
    sample_size INTEGER,
    trend_confidence DECIMAL(5,3),
    data_quality DECIMAL(5,3),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(horse_name, trend_period, trend_date)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_form_analysis_horse_date ON form_analysis(horse_name, analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_form_analysis_race ON form_analysis(race_id);
CREATE INDEX IF NOT EXISTS idx_power_ratings_horse_date ON power_ratings(horse_name, rating_date DESC);
CREATE INDEX IF NOT EXISTS idx_power_ratings_race ON power_ratings(race_id);
CREATE INDEX IF NOT EXISTS idx_composite_scores_horse_date ON composite_scores(horse_name, scoring_date DESC);
CREATE INDEX IF NOT EXISTS idx_composite_scores_race ON composite_scores(race_id);
CREATE INDEX IF NOT EXISTS idx_speed_pace_horse_date ON speed_pace_analysis(horse_name, analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_speed_pace_race ON speed_pace_analysis(race_id);
CREATE INDEX IF NOT EXISTS idx_race_analysis_race ON race_analysis(race_id);
CREATE INDEX IF NOT EXISTS idx_horse_trends_horse_period ON horse_performance_trends(horse_name, trend_period);

-- Create a view for complete horse analysis
CREATE OR REPLACE VIEW horse_complete_analysis AS
SELECT 
    fa.horse_name,
    fa.race_id,
    fa.analysis_date,
    
    -- Form metrics
    fa.recent_form_score,
    fa.speed_rating,
    fa.consistency_index,
    fa.class_rating,
    fa.confidence_level as form_confidence,
    
    -- Power rating
    pr.adjusted_rating as power_rating,
    pr.speed_component,
    pr.class_component,
    pr.form_component,
    pr.conditions_adjustment,
    
    -- Composite score
    cs.composite_score,
    cs.win_probability,
    cs.place_probability,
    cs.composite_rank,
    cs.betting_value,
    
    -- Speed/Pace analysis
    spa.base_speed_rating,
    spa.pace_scenario,
    spa.speed_trend_direction,
    spa.trip_rating,
    
    -- Analysis metadata
    GREATEST(fa.analysis_date, pr.rating_date, cs.scoring_date, spa.analysis_date) as latest_analysis
    
FROM form_analysis fa
LEFT JOIN power_ratings pr ON fa.horse_name = pr.horse_name AND fa.race_id = pr.race_id
LEFT JOIN composite_scores cs ON fa.horse_name = cs.horse_name AND fa.race_id = cs.race_id  
LEFT JOIN speed_pace_analysis spa ON fa.horse_name = spa.horse_name AND fa.race_id = spa.race_id;

-- Comments on tables
COMMENT ON TABLE form_analysis IS 'Detailed form analysis results for horses including speed, class, consistency metrics';
COMMENT ON TABLE power_ratings IS 'Power rating calculations with component breakdowns and adjustments';
COMMENT ON TABLE composite_scores IS 'Composite scoring results combining form analysis and power ratings';
COMMENT ON TABLE speed_pace_analysis IS 'Detailed speed and pace analysis including sectionals and trip notes';
COMMENT ON TABLE race_analysis IS 'Race-level analysis including pace scenarios and field dynamics';
COMMENT ON TABLE horse_performance_trends IS 'Performance trend analysis over different time periods';
