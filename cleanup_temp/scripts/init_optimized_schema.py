#!/usr/bin/env python3
"""
Updated Schema Initialization for PostgreSQL Test Database
Creates the required tables for the optimized massive dataset generator
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_optimized_schema():
    """Create database schema for the optimized massive generator"""

    # Test database configuration (port 5434)
    db_config = {
        "host": "localhost",
        "port": 5434,
        "database": "horse_racing_test_db",
        "user": "horse_racing_test",
        "password": "test_password_123",
    }

    connection = None
    cursor = None

    try:
        logger.info("🔗 Connecting to PostgreSQL test database...")
        connection = psycopg2.connect(**db_config)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        logger.info("✅ Successfully connected to test database")

        logger.info("🗑️ Dropping existing tables if they exist...")
        # Drop tables in reverse dependency order
        cursor.execute("DROP TABLE IF EXISTS race_participants CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS races CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS horses CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS jockeys_stats CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS trainers_stats CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS racecard_details CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS records CASCADE;")
        logger.info("✅ Existing tables dropped")

        logger.info("🏗️ Creating optimized database schema...")

        # Create races table (matches generator expectations)
        cursor.execute(
            """
            CREATE TABLE races (
                race_id SERIAL PRIMARY KEY,
                race_number TEXT,
                race_time TEXT,
                course TEXT,
                race_type TEXT,
                date DATE,
                race_name TEXT,
                class_level TEXT,
                years TEXT,
                distance TEXT,
                surface TEXT,
                field_size INTEGER,
                prize_money INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        logger.info("✅ Created races table")

        # Create race_participants table (matches generator expectations)
        cursor.execute(
            """
            CREATE TABLE race_participants (
                id SERIAL PRIMARY KEY,
                race_id INTEGER REFERENCES races(race_id),
                horse_name TEXT,
                jockey_name TEXT,
                trainer_name TEXT,
                horse_weight_kg REAL,
                horse_age INTEGER,
                draw INTEGER,
                handicap_weight REAL,
                win_odds REAL,
                place_odds REAL,
                barrier INTEGER,
                finished_position INTEGER,
                margin REAL,
                time_seconds REAL,
                prize_money INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        logger.info("✅ Created race_participants table")

        # Create horses table (for compatibility)
        cursor.execute(
            """
            CREATE TABLE horses (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE,
                country TEXT DEFAULT 'AU',
                age INTEGER,
                color TEXT,
                owner TEXT,
                sire TEXT,
                dam TEXT,
                dam_sire TEXT,
                sex TEXT,
                total_races INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                percentage_wins REAL DEFAULT 0.0,
                placed INTEGER DEFAULT 0,
                percentage_placed REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        logger.info("✅ Created horses table")

        # Create jockeys_stats table
        cursor.execute(
            """
            CREATE TABLE jockeys_stats (
                id SERIAL PRIMARY KEY,
                jockey_name TEXT UNIQUE,
                total_rides INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                win_percentage REAL DEFAULT 0.0,
                places INTEGER DEFAULT 0,
                place_percentage REAL DEFAULT 0.0,
                total_earnings INTEGER DEFAULT 0,
                avg_earnings_per_ride REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        logger.info("✅ Created jockeys_stats table")

        # Create trainers_stats table
        cursor.execute(
            """
            CREATE TABLE trainers_stats (
                id SERIAL PRIMARY KEY,
                trainer_name TEXT UNIQUE,
                total_runners INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                win_percentage REAL DEFAULT 0.0,
                places INTEGER DEFAULT 0,
                place_percentage REAL DEFAULT 0.0,
                total_earnings INTEGER DEFAULT 0,
                avg_earnings_per_runner REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        logger.info("✅ Created trainers_stats table")

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_races_date ON races(date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_races_course ON races(course);")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_races_race_type ON races(race_type);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_participants_race_id ON race_participants(race_id);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_participants_horse ON race_participants(horse_name);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_participants_jockey ON race_participants(jockey_name);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_participants_trainer ON race_participants(trainer_name);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_participants_position ON race_participants(finished_position);"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_horses_name ON horses(name);")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_jockeys_name ON jockeys_stats(jockey_name);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_trainers_name ON trainers_stats(trainer_name);"
        )
        logger.info("✅ Created database indexes")

        logger.info("🎉 Optimized database schema created successfully!")

        # Verify tables were created
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """
        )
        tables = cursor.fetchall()
        logger.info(f"📊 Created tables: {[table[0] for table in tables]}")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to create schema: {e}")
        return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        logger.info("🔌 Database connection closed")


if __name__ == "__main__":
    logger.info("🚀 Starting PostgreSQL optimized schema initialization...")
    success = create_optimized_schema()
    if success:
        logger.info("✅ Optimized schema initialization completed successfully!")
    else:
        logger.error("❌ Schema initialization failed!")
        exit(1)
