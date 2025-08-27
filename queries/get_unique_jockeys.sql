-- =====================================================================
-- GET UNIQUE JOCKEYS LIST FROM RESULTS DATABASE
-- =====================================================================

-- Query to get unique jockeys with their details
SELECT 
    ROW_NUMBER() OVER (ORDER BY jockey_name) as unique_jockey_id,
    jockey_name,
    COUNT(*) as total_rides,
    MIN(created_at::DATE) as first_seen_date,
    MAX(created_at::DATE) as last_seen_date,
    -- Try to get win statistics if available
    COALESCE(MAX(wins), 0) as total_wins,
    COALESCE(MAX(win_rate), 0.00) as best_win_rate
FROM (
    -- Get jockeys from result_jockeys table
    SELECT jockey_name, created_at, wins, win_rate 
    FROM result_jockeys 
    WHERE jockey_name IS NOT NULL AND trim(jockey_name) != ''
    
    UNION ALL
    
    -- Get jockeys from result_records table
    SELECT jockey as jockey_name, created_at, NULL as wins, NULL as win_rate 
    FROM result_records 
    WHERE jockey IS NOT NULL AND trim(jockey) != ''
) combined_jockeys
GROUP BY jockey_name
ORDER BY total_rides DESC, jockey_name;

-- Summary count
SELECT 
    'TOTAL UNIQUE JOCKEYS' as metric,
    COUNT(DISTINCT jockey_name) as count
FROM (
    SELECT jockey_name FROM result_jockeys WHERE jockey_name IS NOT NULL AND trim(jockey_name) != ''
    UNION
    SELECT jockey FROM result_records WHERE jockey IS NOT NULL AND trim(jockey) != ''
) all_jockeys;
