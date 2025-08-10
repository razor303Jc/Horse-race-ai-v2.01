-- Database Schema Upgrade for Large ID Values
-- This script updates integer columns to bigint where needed for large ID values

-- Update race_results table to handle large IDs
ALTER TABLE race_results 
ADD COLUMN IF NOT EXISTS race_result_id BIGINT,
ADD COLUMN IF NOT EXISTS horse_id BIGINT,
ADD COLUMN IF NOT EXISTS jockey_id BIGINT,
ADD COLUMN IF NOT EXISTS trainer_id BIGINT;

-- Update horses table to handle large IDs  
ALTER TABLE horses 
ADD COLUMN IF NOT EXISTS horse_id_numeric BIGINT;

-- Update racecard_details table to handle large IDs
ALTER TABLE racecard_details 
ADD COLUMN IF NOT EXISTS racecard_id BIGINT,
ADD COLUMN IF NOT EXISTS horse_id BIGINT,
ADD COLUMN IF NOT EXISTS jockey_id BIGINT,
ADD COLUMN IF NOT EXISTS trainer_id BIGINT;

-- Update jockey_stats table to handle large IDs
ALTER TABLE jockey_stats 
ADD COLUMN IF NOT EXISTS jockey_id BIGINT;

-- Update trainer_stats table to handle large IDs  
ALTER TABLE trainer_stats 
ADD COLUMN IF NOT EXISTS trainer_id BIGINT;

-- Create indexes for the new bigint columns
CREATE INDEX IF NOT EXISTS idx_race_results_race_result_id ON race_results(race_result_id);
CREATE INDEX IF NOT EXISTS idx_race_results_horse_id ON race_results(horse_id);
CREATE INDEX IF NOT EXISTS idx_race_results_jockey_id ON race_results(jockey_id);
CREATE INDEX IF NOT EXISTS idx_race_results_trainer_id ON race_results(trainer_id);

CREATE INDEX IF NOT EXISTS idx_horses_horse_id_numeric ON horses(horse_id_numeric);

CREATE INDEX IF NOT EXISTS idx_racecard_details_racecard_id ON racecard_details(racecard_id);
CREATE INDEX IF NOT EXISTS idx_racecard_details_horse_id ON racecard_details(horse_id);
CREATE INDEX IF NOT EXISTS idx_racecard_details_jockey_id ON racecard_details(jockey_id);
CREATE INDEX IF NOT EXISTS idx_racecard_details_trainer_id ON racecard_details(trainer_id);

CREATE INDEX IF NOT EXISTS idx_jockey_stats_jockey_id ON jockey_stats(jockey_id);
CREATE INDEX IF NOT EXISTS idx_trainer_stats_trainer_id ON trainer_stats(trainer_id);

SELECT 'Schema upgrade completed successfully - added bigint columns for large IDs' as status;
