-- =====================================================
-- Entity Table: horses_entity
-- Database: results
-- Purpose: Indexed entity table for horses with auto-increment primary key
-- PostgreSQL Schema for Horse Racing AI v2.05
-- =====================================================

CREATE TABLE IF NOT EXISTS horses_entity (
    -- Primary key - auto-incrementing
    id SERIAL PRIMARY KEY,
    
    -- Original horse ID from CSV data (unique constraint)
    horse_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Horse identification
    horse_name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    age INTEGER CHECK (age > 0 AND age < 50),
    colour VARCHAR(50),
    sex VARCHAR(20) CHECK (sex IN ('gelding', 'mare', 'colt', 'filly', 'stallion')),
    
    -- Connections
    owner VARCHAR(255),
    trainer VARCHAR(255),
    sire VARCHAR(255),
    dam VARCHAR(255),
    dam_sire VARCHAR(255),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_horses_entity_horse_id ON horses_entity(horse_id);
CREATE INDEX IF NOT EXISTS idx_horses_entity_name ON horses_entity(horse_name);
CREATE INDEX IF NOT EXISTS idx_horses_entity_trainer ON horses_entity(trainer);
CREATE INDEX IF NOT EXISTS idx_horses_entity_owner ON horses_entity(owner);
CREATE INDEX IF NOT EXISTS idx_horses_entity_active ON horses_entity(is_active);

-- Create trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_horses_entity_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_horses_entity_updated_at
    BEFORE UPDATE ON horses_entity
    FOR EACH ROW
    EXECUTE FUNCTION update_horses_entity_updated_at();
