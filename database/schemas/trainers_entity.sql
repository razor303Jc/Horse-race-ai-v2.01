-- =====================================================
-- Entity Table: trainers_entity
-- Database: results
-- Purpose: Indexed entity table for trainers with auto-increment primary key
-- PostgreSQL Schema for Horse Racing AI v2.05
-- =====================================================

CREATE TABLE IF NOT EXISTS trainers_entity (
    -- Primary key - auto-incrementing
    id SERIAL PRIMARY KEY,
    
    -- Original trainer ID from CSV data (unique constraint)
    trainer_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Trainer identification
    trainer_name VARCHAR(255) NOT NULL,
    
    -- Performance metrics (will be updated from stats)
    total_runners INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    win_percentage DECIMAL(5,2) DEFAULT 0.00,
    total_placed INTEGER DEFAULT 0,
    place_percentage DECIMAL(5,2) DEFAULT 0.00,
    
    -- Race type specific stats
    flat_runners INTEGER DEFAULT 0,
    flat_wins INTEGER DEFAULT 0,
    flat_win_rate DECIMAL(5,2) DEFAULT 0.00,
    jumps_runners INTEGER DEFAULT 0,
    jumps_wins INTEGER DEFAULT 0,
    jumps_win_rate DECIMAL(5,2) DEFAULT 0.00,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    CONSTRAINT chk_trainer_win_percentage CHECK (win_percentage >= 0 AND win_percentage <= 100),
    CONSTRAINT chk_trainer_place_percentage CHECK (place_percentage >= 0 AND place_percentage <= 100),
    CONSTRAINT chk_trainer_flat_win_rate CHECK (flat_win_rate >= 0 AND flat_win_rate <= 100),
    CONSTRAINT chk_trainer_jumps_win_rate CHECK (jumps_win_rate >= 0 AND jumps_win_rate <= 100),
    CONSTRAINT chk_trainer_runners_positive CHECK (total_runners >= 0),
    CONSTRAINT chk_trainer_wins_valid CHECK (total_wins >= 0 AND total_wins <= total_runners),
    CONSTRAINT chk_trainer_placed_valid CHECK (total_placed >= 0 AND total_placed <= total_runners),
    CONSTRAINT chk_trainer_flat_wins_valid CHECK (flat_wins >= 0 AND flat_wins <= flat_runners),
    CONSTRAINT chk_trainer_jumps_wins_valid CHECK (jumps_wins >= 0 AND jumps_wins <= jumps_runners)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_trainers_entity_trainer_id ON trainers_entity(trainer_id);
CREATE INDEX IF NOT EXISTS idx_trainers_entity_name ON trainers_entity(trainer_name);
CREATE INDEX IF NOT EXISTS idx_trainers_entity_win_pct ON trainers_entity(win_percentage);
CREATE INDEX IF NOT EXISTS idx_trainers_entity_flat_rate ON trainers_entity(flat_win_rate);
CREATE INDEX IF NOT EXISTS idx_trainers_entity_jumps_rate ON trainers_entity(jumps_win_rate);
CREATE INDEX IF NOT EXISTS idx_trainers_entity_active ON trainers_entity(is_active);

-- Create trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_trainers_entity_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_trainers_entity_updated_at
    BEFORE UPDATE ON trainers_entity
    FOR EACH ROW
    EXECUTE FUNCTION update_trainers_entity_updated_at();
