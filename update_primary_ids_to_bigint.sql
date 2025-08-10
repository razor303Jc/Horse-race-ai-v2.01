-- Update primary ID columns to BIGINT for safety
-- This ensures all ID columns can handle large values

-- Update race_results table primary key to bigint
ALTER TABLE race_results ALTER COLUMN id TYPE BIGINT;

-- Update racecard_details table primary key to bigint  
ALTER TABLE racecard_details ALTER COLUMN id TYPE BIGINT;

-- Update horses table primary key to bigint
ALTER TABLE horses ALTER COLUMN id TYPE BIGINT;

-- Update races_cards table primary key to bigint
ALTER TABLE races_cards ALTER COLUMN id TYPE BIGINT;

-- Update jockey_stats table primary key to bigint
ALTER TABLE jockey_stats ALTER COLUMN id TYPE BIGINT;

-- Update trainer_stats table primary key to bigint
ALTER TABLE trainer_stats ALTER COLUMN id TYPE BIGINT;

SELECT 'Primary ID columns updated to BIGINT successfully' as status;
