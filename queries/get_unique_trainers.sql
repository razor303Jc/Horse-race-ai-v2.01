-- =====================================================================
-- GET UNIQUE TRAINERS LIST FROM RESULTS DATABASE
-- =====================================================================

-- Query to get unique trainers with their details
SELECT 
    ROW_NUMBER() OVER (ORDER BY trainer_name) as unique_trainer_id,
    trainer_name,
    COUNT(*) as total_horses_trained,
    MIN(created_at::DATE) as first_seen_date,
    MAX(created_at::DATE) as last_seen_date,
    -- Try to get win statistics if available
    COALESCE(MAX(wins), 0) as total_wins,
    COALESCE(MAX(win_rate), 0.00) as best_win_rate
FROM (
    -- Get trainers from result_trainers table
    SELECT trainer_name, created_at, wins, win_rate 
    FROM result_trainers 
    WHERE trainer_name IS NOT NULL AND trim(trainer_name) != ''
    
    UNION ALL
    
    -- Get trainers from result_records table
    SELECT trainer as trainer_name, created_at, NULL as wins, NULL as win_rate 
    FROM result_records 
    WHERE trainer IS NOT NULL AND trim(trainer) != ''
) combined_trainers
GROUP BY trainer_name
ORDER BY total_horses_trained DESC, trainer_name;

-- Summary count
SELECT 
    'TOTAL UNIQUE TRAINERS' as metric,
    COUNT(DISTINCT trainer_name) as count
FROM (
    SELECT trainer_name FROM result_trainers WHERE trainer_name IS NOT NULL AND trim(trainer_name) != ''
    UNION
    SELECT trainer FROM result_records WHERE trainer IS NOT NULL AND trim(trainer) != ''
) all_trainers;
