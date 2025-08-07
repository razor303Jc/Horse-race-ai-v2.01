#!/usr/bin/env python3
"""
Schema Initialization for PostgreSQL Test Database
Creates the required tables for the massive dataset generator
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_test_schema():
    """Create database schema for the test database"""

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

        logger.info("🏗️ Creating database schema...")

        # Create races table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS races (
                Race_ID INTEGER PRIMARY KEY,
                race_number TEXT,
                race_time TEXT,
                course_id REAL,
                Course TEXT,
                Race_type TEXT,
                Date DATE,
                Race_name TEXT,
                Class TEXT,
                Years TEXT,
                Distance TEXT,
                Surface TEXT,
                Prize TEXT,
                Runners_racecard INTEGER,
                Runners TEXT,
                Draw TEXT,
                EW_racecard INTEGER,
                EW TEXT,
                Places_EW_racecard INTEGER,
                Places_EW TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        logger.info("✅ Created races table")

        # Create horses table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS horses (
                id INTEGER PRIMARY KEY,
                uptodate DATE,
                state TEXT,
                race_id_last_race INTEGER,
                date_last_race DATE,
                name TEXT,
                country TEXT,
                age TEXT,
                color TEXT,
                owner TEXT,
                sire TEXT,
                dam TEXT,
                dam_sire TEXT,
                sex TEXT,
                Total_races REAL,
                Wins REAL,
                Percentage_wins TEXT,
                placed REAL,
                Percentage_placed TEXT,
                Flat_AW_races REAL,
                Flat_AW_wins REAL,
                Flat_AW_rate TEXT,
                Flat_AW_placed REAL,
                Flat_AW_placed_rate TEXT,
                Flat_Turf_races REAL,
                Flat_Turf_wins REAL,
                Flat_Turf_rate TEXT,
                Flat_Turf_placed REAL,
                Flat_Turf_placed_rate TEXT,
                Chase_races REAL,
                Chase_wins REAL,
                Chase_rate TEXT,
                Chase_placed REAL,
                Chase_placed_rate TEXT,
                Hurdle_races REAL,
                Hurdle_wins REAL,
                Hurdle_rate TEXT,
                Hurdle_placed REAL,
                Hurdle_placed_rate TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        logger.info("✅ Created horses table")

        # Create jockeys_stats table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS jockeys_stats (
                id SERIAL PRIMARY KEY,
                jockey_name TEXT,
                total_rides INTEGER,
                wins INTEGER,
                win_percentage REAL,
                places INTEGER,
                place_percentage REAL,
                total_earnings TEXT,
                avg_earnings_per_ride REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        logger.info("✅ Created jockeys_stats table")

        # Create trainers_stats table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trainers_stats (
                id SERIAL PRIMARY KEY,
                trainer_name TEXT,
                total_runners INTEGER,
                wins INTEGER,
                win_percentage REAL,
                places INTEGER,
                place_percentage REAL,
                total_earnings TEXT,
                avg_earnings_per_runner REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        logger.info("✅ Created trainers_stats table")

        # Create racecard_details table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS racecard_details (
                id SERIAL PRIMARY KEY,
                race_id INTEGER,
                horse_id INTEGER,
                horse_name TEXT,
                jockey TEXT,
                trainer TEXT,
                weight TEXT,
                odds TEXT,
                form TEXT,
                age TEXT,
                draw INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (race_id) REFERENCES races(Race_ID),
                FOREIGN KEY (horse_id) REFERENCES horses(id)
            );
        """
        )
        logger.info("✅ Created racecard_details table")

        # Create records table (for results data)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id SERIAL PRIMARY KEY,
                race_id INTEGER,
                position INTEGER,
                horse_name TEXT,
                jockey TEXT,
                trainer TEXT,
                sp_odds TEXT,
                margin TEXT,
                time_taken TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (race_id) REFERENCES races(Race_ID)
            );
        """
        )
        logger.info("✅ Created records table")

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_races_date ON races(Date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_races_course ON races(Course);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_horses_name ON horses(name);")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_racecard_race_id ON racecard_details(race_id);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_records_race_id ON records(race_id);"
        )
        logger.info("✅ Created database indexes")

        logger.info("🎉 Database schema created successfully!")

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
    logger.info("🚀 Starting PostgreSQL test database schema initialization...")
    success = create_test_schema()
    if success:
        logger.info("✅ Schema initialization completed successfully!")
    else:
        logger.error("❌ Schema initialization failed!")
        exit(1)
