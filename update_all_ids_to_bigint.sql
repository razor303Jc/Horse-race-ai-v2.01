-- Comprehensive update of all ID columns to BIGINT to handle large values
-- This script updates both primary keys and foreign keys

-- Start a transaction
BEGIN;

-- Update race_results table
ALTER TABLE race_results ALTER COLUMN id TYPE BIGINT;
-- Add foreign key ID columns to BIGINT if they exist
DO $$ 
BEGIN
    -- Update race_result_id if it exists
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'race_results' AND column_name = 'race_result_id') THEN
        ALTER TABLE race_results ALTER COLUMN race_result_id TYPE BIGINT;
    END IF;
    
    -- Update race_id if it exists  
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'race_results' AND column_name = 'race_id') THEN
        ALTER TABLE race_results ALTER COLUMN race_id TYPE BIGINT;
    END IF;
    
    -- Update horse_id if it exists
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'race_results' AND column_name = 'horse_id') THEN
        ALTER TABLE race_results ALTER COLUMN horse_id TYPE BIGINT;
    END IF;
    
    -- Update jockey_id if it exists
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'race_results' AND column_name = 'jockey_id') THEN
        ALTER TABLE race_results ALTER COLUMN jockey_id TYPE BIGINT;
    END IF;
    
    -- Update trainer_id if it exists  
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'race_results' AND column_name = 'trainer_id') THEN
        ALTER TABLE race_results ALTER COLUMN trainer_id TYPE BIGINT;
    END IF;
END
$$;

-- Update racecard_details table
ALTER TABLE racecard_details ALTER COLUMN id TYPE BIGINT;
DO $$ 
BEGIN
    -- Update racecard_id if it exists
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'racecard_details' AND column_name = 'racecard_id') THEN
        ALTER TABLE racecard_details ALTER COLUMN racecard_id TYPE BIGINT;
    END IF;
    
    -- Update race_id if it exists  
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'racecard_details' AND column_name = 'race_id') THEN
        ALTER TABLE racecard_details ALTER COLUMN race_id TYPE BIGINT;
    END IF;
    
    -- Update horse_id if it exists
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'racecard_details' AND column_name = 'horse_id') THEN
        ALTER TABLE racecard_details ALTER COLUMN horse_id TYPE BIGINT;
    END IF;
    
    -- Update jockey_id if it exists
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'racecard_details' AND column_name = 'jockey_id') THEN
        ALTER TABLE racecard_details ALTER COLUMN jockey_id TYPE BIGINT;
    END IF;
    
    -- Update trainer_id if it exists  
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'racecard_details' AND column_name = 'trainer_id') THEN
        ALTER TABLE racecard_details ALTER COLUMN trainer_id TYPE BIGINT;
    END IF;
END
$$;

-- Update horses table
ALTER TABLE horses ALTER COLUMN id TYPE BIGINT;
DO $$ 
BEGIN
    -- Update horse_id_numeric if it exists
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'horses' AND column_name = 'horse_id_numeric') THEN
        ALTER TABLE horses ALTER COLUMN horse_id_numeric TYPE BIGINT;
    END IF;
END
$$;

-- Update other tables with ID columns
ALTER TABLE races_cards ALTER COLUMN id TYPE BIGINT;
ALTER TABLE jockey_stats ALTER COLUMN id TYPE BIGINT;
ALTER TABLE trainer_stats ALTER COLUMN id TYPE BIGINT;

-- Commit the transaction
COMMIT;

SELECT 'All ID columns updated to BIGINT successfully' as status;
