#!/usr/bin/env python3
"""
Create Unique Reference Tables
============================

This script creates unique lookup tables for horses, jockeys, and trainers
from existing data in the results_horse_racing_db database. This helps prevent
duplicates when processing new CSV files.

Usage:
    python create_unique_reference_tables.py [--dry-run] [--verbose]

Options:
    --dry-run    : Show what would be created without actually creating tables
    --verbose    : Show detailed progress information
"""

import os
import sys
import psycopg2
import psycopg2.extras
from pathlib import Path
import argparse
from datetime import datetime


class UniqueReferenceTableCreator:
    """Creates unique reference tables for horses, jockeys, and trainers"""

    def __init__(self, dry_run=False, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose

        # Database configuration
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def connect_database(self):
        """Connect to the results database"""
        try:
            if self.verbose:
                print("🔗 Connecting to results_horse_racing_db...")

            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return None

    def get_unique_horses(self, conn):
        """Get unique horses from existing data"""
        query = """
        SELECT 
            horse_name,
            COUNT(*) as total_appearances,
            MIN(created_at::DATE) as first_seen_date
        FROM horses 
        WHERE horse_name IS NOT NULL AND trim(horse_name) != ''
        GROUP BY horse_name
        ORDER BY total_appearances DESC, horse_name;
        """

        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query)
                results = cur.fetchall()

                if self.verbose:
                    print(f"📊 Found {len(results)} unique horses")

                return results
        except Exception as e:
            print(f"❌ Error getting unique horses: {e}")
            return []

    def get_unique_jockeys(self, conn):
        """Get unique jockeys from existing data"""
        query = """
        SELECT 
            jockey_name,
            COUNT(*) as total_rides,
            MIN(created_at::DATE) as first_seen_date,
            COALESCE(MAX(wins), 0) as total_wins,
            COALESCE(MAX(win_rate), 0.00) as best_win_rate
        FROM jockeys_stats 
        WHERE jockey_name IS NOT NULL AND trim(jockey_name) != ''
        GROUP BY jockey_name
        ORDER BY total_rides DESC, jockey_name;
        """

        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query)
                results = cur.fetchall()

                if self.verbose:
                    print(f"🏇 Found {len(results)} unique jockeys")

                return results
        except Exception as e:
            print(f"❌ Error getting unique jockeys: {e}")
            return []

    def get_unique_trainers(self, conn):
        """Get unique trainers from existing data"""
        query = """
        SELECT 
            trainer_name,
            COUNT(*) as total_horses_trained,
            MIN(created_at::DATE) as first_seen_date,
            COALESCE(MAX(wins), 0) as total_wins,
            COALESCE(MAX(win_rate), 0.00) as best_win_rate
        FROM trainers_stats 
        WHERE trainer_name IS NOT NULL AND trim(trainer_name) != ''
        GROUP BY trainer_name
        ORDER BY total_horses_trained DESC, trainer_name;
        """

        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query)
                results = cur.fetchall()

                if self.verbose:
                    print(f"🎓 Found {len(results)} unique trainers")

                return results
        except Exception as e:
            print(f"❌ Error getting unique trainers: {e}")
            return []

    def create_unique_tables(self, conn):
        """Create the unique reference tables"""

        # Table creation queries
        tables = {
            "unique_horses": """
                CREATE TABLE IF NOT EXISTS unique_horses (
                    horse_id SERIAL PRIMARY KEY,
                    horse_name VARCHAR(100) NOT NULL UNIQUE,
                    first_seen_date DATE,
                    total_races INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_unique_horses_name ON unique_horses(horse_name);
            """,
            "unique_jockeys": """
                CREATE TABLE IF NOT EXISTS unique_jockeys (
                    jockey_id SERIAL PRIMARY KEY,
                    jockey_name VARCHAR(100) NOT NULL UNIQUE,
                    first_seen_date DATE,
                    total_rides INTEGER DEFAULT 0,
                    total_wins INTEGER DEFAULT 0,
                    win_rate DECIMAL(5,2) DEFAULT 0.00,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_unique_jockeys_name ON unique_jockeys(jockey_name);
            """,
            "unique_trainers": """
                CREATE TABLE IF NOT EXISTS unique_trainers (
                    trainer_id SERIAL PRIMARY KEY,
                    trainer_name VARCHAR(100) NOT NULL UNIQUE,
                    first_seen_date DATE,
                    total_horses INTEGER DEFAULT 0,
                    total_wins INTEGER DEFAULT 0,
                    win_rate DECIMAL(5,2) DEFAULT 0.00,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_unique_trainers_name ON unique_trainers(trainer_name);
            """,
        }

        if self.dry_run:
            print("🔍 DRY RUN - Tables that would be created:")
            for table_name in tables.keys():
                print(f"  ✅ {table_name}")
            return True

        try:
            with conn.cursor() as cur:
                for table_name, create_sql in tables.items():
                    if self.verbose:
                        print(f"🏗️ Creating table: {table_name}")
                    cur.execute(create_sql)

                conn.commit()
                print("✅ Tables created successfully")
                return True

        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            conn.rollback()
            return False

    def populate_tables(self, conn):
        """Populate the unique reference tables with data"""

        if self.dry_run:
            print("🔍 DRY RUN - Would populate tables with unique data")
            return True

        try:
            # Get unique data
            horses = self.get_unique_horses(conn)
            jockeys = self.get_unique_jockeys(conn)
            trainers = self.get_unique_trainers(conn)

            # Insert horses
            if horses:
                with conn.cursor() as cur:
                    for horse in horses:
                        cur.execute(
                            """
                            INSERT INTO unique_horses (horse_name, first_seen_date, total_races)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (horse_name) DO NOTHING
                        """,
                            (
                                horse["horse_name"],
                                horse["first_seen_date"],
                                horse["total_appearances"],
                            ),
                        )

                    if self.verbose:
                        print(f"✅ Inserted {len(horses)} unique horses")

            # Insert jockeys
            if jockeys:
                with conn.cursor() as cur:
                    for jockey in jockeys:
                        cur.execute(
                            """
                            INSERT INTO unique_jockeys (jockey_name, first_seen_date, total_rides, total_wins, win_rate)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (jockey_name) DO NOTHING
                        """,
                            (
                                jockey["jockey_name"],
                                jockey["first_seen_date"],
                                jockey["total_rides"],
                                jockey["total_wins"],
                                jockey["best_win_rate"],
                            ),
                        )

                    if self.verbose:
                        print(f"✅ Inserted {len(jockeys)} unique jockeys")

            # Insert trainers
            if trainers:
                with conn.cursor() as cur:
                    for trainer in trainers:
                        cur.execute(
                            """
                            INSERT INTO unique_trainers (trainer_name, first_seen_date, total_horses, total_wins, win_rate)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (trainer_name) DO NOTHING
                        """,
                            (
                                trainer["trainer_name"],
                                trainer["first_seen_date"],
                                trainer["total_horses_trained"],
                                trainer["total_wins"],
                                trainer["best_win_rate"],
                            ),
                        )

                    if self.verbose:
                        print(f"✅ Inserted {len(trainers)} unique trainers")

            conn.commit()
            return True

        except Exception as e:
            print(f"❌ Error populating tables: {e}")
            conn.rollback()
            return False

    def show_summary(self, conn):
        """Show summary of created tables"""

        if self.dry_run:
            return

        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Get counts
                cur.execute("SELECT COUNT(*) as count FROM unique_horses")
                horse_count = cur.fetchone()["count"]

                cur.execute("SELECT COUNT(*) as count FROM unique_jockeys")
                jockey_count = cur.fetchone()["count"]

                cur.execute("SELECT COUNT(*) as count FROM unique_trainers")
                trainer_count = cur.fetchone()["count"]

                print("\n" + "=" * 60)
                print("📊 UNIQUE REFERENCE TABLES SUMMARY")
                print("=" * 60)
                print(f"🐎 Unique Horses:  {horse_count:,}")
                print(f"🏇 Unique Jockeys: {jockey_count:,}")
                print(f"🎓 Unique Trainers: {trainer_count:,}")
                print("=" * 60)

                # Show sample data
                if self.verbose:
                    print("\n📋 Sample Data:")

                    # Top 5 horses by race count
                    cur.execute(
                        "SELECT horse_name, total_races FROM unique_horses ORDER BY total_races DESC LIMIT 5"
                    )
                    top_horses = cur.fetchall()
                    print("\n🐎 Top Horses by Race Count:")
                    for horse in top_horses:
                        print(
                            f"  • {horse['horse_name']}: {horse['total_races']} races"
                        )

                    # Top 5 jockeys by ride count
                    cur.execute(
                        "SELECT jockey_name, total_rides FROM unique_jockeys ORDER BY total_rides DESC LIMIT 5"
                    )
                    top_jockeys = cur.fetchall()
                    print("\n🏇 Top Jockeys by Ride Count:")
                    for jockey in top_jockeys:
                        print(
                            f"  • {jockey['jockey_name']}: {jockey['total_rides']} rides"
                        )

                    # Top 5 trainers by horse count
                    cur.execute(
                        "SELECT trainer_name, total_horses FROM unique_trainers ORDER BY total_horses DESC LIMIT 5"
                    )
                    top_trainers = cur.fetchall()
                    print("\n🎓 Top Trainers by Horse Count:")
                    for trainer in top_trainers:
                        print(
                            f"  • {trainer['trainer_name']}: {trainer['total_horses']} horses"
                        )

        except Exception as e:
            print(f"❌ Error showing summary: {e}")

    def run(self):
        """Main execution method"""
        print("🚀 Creating Unique Reference Tables")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🗄️ Database: {self.db_config['database']}")

        if self.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
        print()

        # Connect to database
        conn = self.connect_database()
        if not conn:
            return False

        try:
            # Create tables
            if not self.create_unique_tables(conn):
                return False

            # Populate tables
            if not self.populate_tables(conn):
                return False

            # Show summary
            self.show_summary(conn)

            print("\n🎉 Unique reference tables created successfully!")
            print("📋 Ready for CSV processing with duplicate prevention")

            return True

        finally:
            conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Create unique reference tables for horses, jockeys, and trainers"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without making changes",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed progress information"
    )

    args = parser.parse_args()

    creator = UniqueReferenceTableCreator(dry_run=args.dry_run, verbose=args.verbose)
    success = creator.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
