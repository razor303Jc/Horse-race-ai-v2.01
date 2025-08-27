-- =====================================================================
-- GET UNIQUE HORSES LIST FROM RESULTS DATABASE
-- =====================================================================

-- Connect to results database
\c results_horse_racing_db;

-- Query to get unique horses with their details
SELECT 
    ROW_NUMBER() OVER (ORDER BY horse_name) as unique_horse_id,
    horse_name,
    COUNT(*) as total_appearances,
    MIN(created_at::DATE) as first_seen_date,
    MAX(created_at::DATE) as last_seen_date
FROM (
    -- Get horses from result_horses table
    SELECT horse_name, created_at 
    FROM result_horses 
    WHERE horse_name IS NOT NULL AND trim(horse_name) != ''
    
    UNION ALL
    
    -- Get horses from result_records table
    SELECT horse_name, created_at 
    FROM result_records 
    WHERE horse_name IS NOT NULL AND trim(horse_name) != ''
) combined_horses
GROUP BY horse_name
ORDER BY total_appearances DESC, horse_name;

-- Summary count
SELECT 
    'TOTAL UNIQUE HORSES' as metric,
    COUNT(DISTINCT horse_name) as count
FROM (
    SELECT horse_name FROM result_horses WHERE horse_name IS NOT NULL AND trim(horse_name) != ''
    UNION
    SELECT horse_name FROM result_records WHERE horse_name IS NOT NULL AND trim(horse_name) != ''
) all_horses;
