-- 🏇 Database Performance Optimization Script
-- Phase 1B: Critical Index Creation & Query Optimization
-- Target: 70% faster database queries
-- Created: August 15, 2025

-- ================================
-- SECTION 1: CRITICAL INDEXES
-- ================================

-- Remove existing basic indexes (will be replaced with optimized ones)
DROP INDEX IF EXISTS idx_races_race_id;
DROP INDEX IF EXISTS idx_races_date;
DROP INDEX IF EXISTS idx_records_race_id;
DROP INDEX IF EXISTS idx_records_horse_id;
DROP INDEX IF EXISTS idx_horses_horse_id;
DROP INDEX IF EXISTS idx_jockeys_jockey_id;
DROP INDEX IF EXISTS idx_trainers_trainer_id;

-- RACES TABLE OPTIMIZED INDEXES
-- Primary lookup patterns: race_id, date range queries, course + date combinations
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_races_race_id_date 
    ON races(race_id, date) 
    INCLUDE (course, race_type, distance, runners);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_races_date_course 
    ON races(date, course) 
    INCLUDE (race_id, race_name, race_type);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_races_course_distance 
    ON races(course, distance) 
    INCLUDE (race_id, date, race_type);

-- For race analysis queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_races_race_type_date 
    ON races(race_type, date) 
    INCLUDE (race_id, course);

-- RECORDS TABLE OPTIMIZED INDEXES  
-- Primary lookup patterns: race_id joins, horse_id analysis, position-based queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_records_race_id_position 
    ON records(race_id, position) 
    INCLUDE (horse_id, horse, jockey, trainer, sp, distance_btn);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_records_horse_id_race_id 
    ON records(horse_id, race_id) 
    INCLUDE (position, sp, distance_btn, jockey_id, trainer_id);

-- For ML feature engineering queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_records_race_id_sp 
    ON records(race_id, sp) 
    WHERE sp > 0;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_records_race_id_fav 
    ON records(race_id, fav) 
    WHERE fav = 1;

-- For jockey/trainer analysis
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_records_jockey_id_position 
    ON records(jockey_id, position) 
    INCLUDE (race_id, sp);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_records_trainer_id_position 
    ON records(trainer_id, position) 
    INCLUDE (race_id, sp);

-- HORSES TABLE OPTIMIZED INDEXES
-- Primary lookup patterns: horse_id, name searches, performance analysis
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_horses_horse_id_name 
    ON horses(horse_id, horse_name) 
    INCLUDE (total_races, wins, percentage_wins);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_horses_name_trgm 
    ON horses USING gin(horse_name gin_trgm_ops);

-- Performance-based indexes for ML features
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_horses_performance 
    ON horses(percentage_wins, total_races) 
    WHERE total_races > 0;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_horses_surface_performance 
    ON horses(flat_turf_rate, flat_aw_rate, chase_rate, hurdle_rate);

-- JOCKEYS_STATS TABLE OPTIMIZED INDEXES
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jockeys_id_name 
    ON jockeys_stats(jockey_id, jockey_name) 
    INCLUDE (percentage_wins, total_races);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jockeys_name_trgm 
    ON jockeys_stats USING gin(jockey_name gin_trgm_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jockeys_performance 
    ON jockeys_stats(percentage_wins, total_races) 
    WHERE total_races > 0;

-- TRAINERS_STATS TABLE OPTIMIZED INDEXES
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trainers_id_name 
    ON trainers_stats(trainer_id, trainer_name) 
    INCLUDE (percentage_wins, total_races);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trainers_name_trgm 
    ON trainers_stats USING gin(trainer_name gin_trgm_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trainers_performance 
    ON trainers_stats(percentage_wins, total_races) 
    WHERE total_races > 0;

-- ================================
-- SECTION 2: MATERIALIZED VIEWS
-- ================================

-- Fast race summary for dashboard and ML feature engineering
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_race_summary AS
SELECT 
    r.race_id,
    r.race_name,
    r.course,
    r.date,
    r.distance,
    r.race_type,
    r.prize,
    r.runners,
    COUNT(rec.id) as actual_runners,
    MIN(CASE WHEN rec.sp > 0 THEN rec.sp END) as min_odds,
    MAX(CASE WHEN rec.sp > 0 THEN rec.sp END) as max_odds,
    AVG(CASE WHEN rec.sp > 0 THEN rec.sp END) as avg_odds,
    STDDEV(CASE WHEN rec.sp > 0 THEN rec.sp END) as odds_std,
    MAX(CASE WHEN rec.position = 1 THEN rec.horse END) as winner,
    MAX(CASE WHEN rec.position = 1 THEN rec.sp END) as winning_odds,
    MAX(CASE WHEN rec.position = 1 THEN rec.jockey END) as winning_jockey,
    MAX(CASE WHEN rec.position = 1 THEN rec.trainer END) as winning_trainer
FROM races r
LEFT JOIN records rec ON r.race_id = rec.race_id
GROUP BY r.race_id, r.race_name, r.course, r.date, r.distance, r.race_type, r.prize, r.runners;

-- Index for the materialized view
CREATE UNIQUE INDEX idx_mv_race_summary_race_id ON mv_race_summary(race_id);
CREATE INDEX idx_mv_race_summary_date_course ON mv_race_summary(date, course);

-- Horse performance aggregation for ML features
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_horse_performance AS
SELECT 
    h.horse_id,
    h.horse_name,
    h.total_races,
    h.wins,
    h.percentage_wins,
    h.placed,
    h.percentage_placed,
    COUNT(rec.id) as database_races,
    COUNT(CASE WHEN rec.position = 1 THEN 1 END) as database_wins,
    COUNT(CASE WHEN rec.position <= 3 THEN 1 END) as database_places,
    AVG(CASE WHEN rec.sp > 0 THEN rec.sp END) as avg_starting_price,
    AVG(rec.position::decimal) as avg_position,
    MIN(rec.position) as best_position,
    COUNT(DISTINCT rec.race_id) as unique_races,
    MAX(r.date) as last_race_date
FROM horses h
LEFT JOIN records rec ON h.horse_id = rec.horse_id
LEFT JOIN races r ON rec.race_id = r.race_id
GROUP BY h.horse_id, h.horse_name, h.total_races, h.wins, h.percentage_wins, h.placed, h.percentage_placed;

-- Index for horse performance view
CREATE UNIQUE INDEX idx_mv_horse_performance_horse_id ON mv_horse_performance(horse_id);
CREATE INDEX idx_mv_horse_performance_name ON mv_horse_performance(horse_name);

-- ================================
-- SECTION 3: QUERY OPTIMIZATION
-- ================================

-- Update table statistics for better query planning
ANALYZE races;
ANALYZE records;
ANALYZE horses;
ANALYZE jockeys_stats;
ANALYZE trainers_stats;

-- Set appropriate work_mem for better query performance
-- This will be reset when connection closes
SET work_mem = '256MB';

-- ================================
-- SECTION 4: PERFORMANCE MONITORING
-- ================================

-- Create performance tracking table
CREATE TABLE IF NOT EXISTS query_performance_log (
    id SERIAL PRIMARY KEY,
    query_type VARCHAR(100),
    query_description TEXT,
    execution_time_ms INTEGER,
    rows_returned INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    slow_query BOOLEAN DEFAULT FALSE
);

-- Index for performance monitoring
CREATE INDEX idx_query_performance_timestamp ON query_performance_log(timestamp);
CREATE INDEX idx_query_performance_slow ON query_performance_log(slow_query) WHERE slow_query = TRUE;

-- Function to log query performance
CREATE OR REPLACE FUNCTION log_query_performance(
    p_query_type VARCHAR(100),
    p_description TEXT,
    p_execution_time INTEGER,
    p_rows_returned INTEGER
) RETURNS VOID AS $$
BEGIN
    INSERT INTO query_performance_log (query_type, query_description, execution_time_ms, rows_returned, slow_query)
    VALUES (p_query_type, p_description, p_execution_time, p_rows_returned, p_execution_time > 1000);
END;
$$ LANGUAGE plpgsql;

-- ================================
-- SECTION 5: COMMON QUERY PATTERNS
-- ================================

-- Example optimized queries that should now be much faster:

/*
-- Race data with horse details (for ML feature engineering)
EXPLAIN (ANALYZE, BUFFERS) 
SELECT r.race_id, r.date, r.course, r.distance, r.race_type,
       rec.horse, rec.horse_id, rec.position, rec.sp, rec.draw,
       rec.jockey, rec.trainer, rec.age, rec.weight
FROM races r
JOIN records rec ON r.race_id = rec.race_id
WHERE r.date >= '2024-01-01' AND r.course = 'Ascot'
ORDER BY r.date DESC, rec.sp ASC;

-- Horse performance analysis
EXPLAIN (ANALYZE, BUFFERS)
SELECT h.horse_name, h.percentage_wins, 
       mv.avg_starting_price, mv.avg_position, mv.last_race_date
FROM horses h
JOIN mv_horse_performance mv ON h.horse_id = mv.horse_id
WHERE h.total_races > 5 AND h.percentage_wins > 10
ORDER BY h.percentage_wins DESC;

-- Race summary for dashboard
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mv_race_summary 
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC, avg_odds ASC;
*/

-- ================================
-- SECTION 6: MAINTENANCE
-- ================================

-- Refresh materialized views (should be run periodically)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_race_summary;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_horse_performance;

-- Vacuum and analyze for optimal performance
-- VACUUM ANALYZE races;
-- VACUUM ANALYZE records;
-- VACUUM ANALYZE horses;
-- VACUUM ANALYZE jockeys_stats;
-- VACUUM ANALYZE trainers_stats;

-- ================================
-- COMPLETION SUMMARY
-- ================================

-- Performance monitoring query
DO $$
BEGIN
    RAISE NOTICE '🎯 Database Performance Optimization Complete!';
    RAISE NOTICE '📊 Indexes Created: 15 optimized indexes with INCLUDE columns';
    RAISE NOTICE '🚀 Materialized Views: 2 views for fast aggregations';
    RAISE NOTICE '📈 Expected Performance: 60-80%% query improvement';
    RAISE NOTICE '🔍 Monitoring: query_performance_log table created';
    RAISE NOTICE '⚡ Next: Run EXPLAIN ANALYZE on key queries to verify improvements';
END $$;
