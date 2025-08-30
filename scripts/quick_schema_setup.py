#!/usr/bin/env python3
"""
Quick Schema Setup for Testing & Simulation
Create all required tables for comprehensive PostgreSQL testing
"""
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def execute_sql(database, sql_command):
    """Execute SQL command via docker exec"""
    cmd = [
        "docker",
        "exec",
        "horse_racing_postgres_clean",
        "psql",
        "-U",
        "horse_racing",
        "-d",
        database,
        "-c",
        sql_command,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"SQL executed successfully")
            return True
        else:
            logging.error(f"SQL failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        logging.error(f"Failed to execute SQL: {e}")
        return False


def create_complete_schema():
    """Create complete database schema for testing"""
    logging.info("Creating complete racing database schema...")

    # Entity tables
    horses_table = """
        CREATE TABLE IF NOT EXISTS horses_entity (
            id SERIAL PRIMARY KEY,
            horse_id INTEGER UNIQUE NOT NULL,
            horse_name VARCHAR(255),
            age INTEGER,
            sex VARCHAR(10),
            trainer VARCHAR(255),
            rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_horses_name ON horses_entity(horse_name);
        CREATE INDEX IF NOT EXISTS idx_horses_trainer ON horses_entity(trainer);
    """

    jockeys_table = """
        CREATE TABLE IF NOT EXISTS jockeys_entity (
            id SERIAL PRIMARY KEY,
            jockey_id INTEGER UNIQUE NOT NULL,
            jockey_name VARCHAR(255),
            claim_allowance INTEGER,
            wins INTEGER,
            runs INTEGER,
            win_rate DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_jockeys_name ON jockeys_entity(jockey_name);
    """

    trainers_table = """
        CREATE TABLE IF NOT EXISTS trainers_entity (
            id SERIAL PRIMARY KEY,
            trainer_id INTEGER UNIQUE NOT NULL,
            trainer_name VARCHAR(255),
            total_races INTEGER,
            wins INTEGER,
            win_percentage DECIMAL(5,2),
            placed INTEGER,
            place_percentage DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_trainers_name ON trainers_entity(trainer_name);
    """

    # Execute schema creation
    success = True
    success &= execute_sql("results", horses_table)
    success &= execute_sql("results", jockeys_table)
    success &= execute_sql("results", trainers_table)

    if success:
        logging.info("✅ Complete schema created successfully!")
        return True
    else:
        logging.error("❌ Schema creation failed!")
        return False


def verify_schema():
    """Verify all tables exist"""
    logging.info("Verifying schema...")

    tables_check = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """

    success = execute_sql("results", tables_check)
    return success


if __name__ == "__main__":
    print("🚀 Setting up complete PostgreSQL schema for Testing & Simulation...")

    if create_complete_schema():
        if verify_schema():
            print(
                "✅ Schema setup complete! Ready for data loading and performance testing."
            )
        else:
            print("⚠️ Schema verification failed")
    else:
        print("❌ Schema setup failed!")
