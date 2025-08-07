#!/usr/bin/env python3
"""
Test Data Validation Script for Horse Racing AI v2.0

Validates the generated test data and provides comprehensive statistics
"""

import sys
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestDataValidator:
    """Validates the generated test database"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection = None

    def connect(self):
        """Connect to test database"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            logger.info("✅ Connected to test database")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    def execute_query(self, query: str):
        """Execute query and return results"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def execute_single(self, query: str):
        """Execute query and return single result"""
        results = self.execute_query(query)
        return results[0] if results else None

    def validate_database_structure(self):
        """Validate all required tables exist"""
        logger.info("🏗️ Validating database structure...")

        required_tables = [
            "races_cards",
            "races_results",
            "horses_cards",
            "horses_results",
            "jockeys_stats",
            "trainers_stats",
            "racecard_details",
            "records",
        ]

        existing_tables = self.execute_query(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """
        )

        existing_table_names = [t["table_name"] for t in existing_tables]

        missing_tables = [t for t in required_tables if t not in existing_table_names]

        if missing_tables:
            logger.error(f"❌ Missing tables: {missing_tables}")
            return False

        logger.info(f"✅ All {len(required_tables)} required tables found")
        return True

    def get_table_statistics(self):
        """Get comprehensive statistics for all tables"""
        logger.info("📊 Gathering table statistics...")

        stats = {}
        tables = [
            "races_cards",
            "races_results",
            "horses_cards",
            "horses_results",
            "jockeys_stats",
            "trainers_stats",
            "racecard_details",
            "records",
        ]

        for table in tables:
            try:
                count = self.execute_single(f"SELECT COUNT(*) as count FROM {table}")
                stats[table] = count["count"]
                logger.info(f"   📋 {table}: {count['count']:,} records")
            except Exception as e:
                logger.error(f"❌ Failed to count {table}: {e}")
                stats[table] = 0

        return stats

    def validate_data_integrity(self):
        """Validate data relationships and integrity"""
        logger.info("🔍 Validating data integrity...")

        integrity_checks = []

        # Check race participants have valid race references
        orphaned_participants = self.execute_single(
            """
            SELECT COUNT(*) as count 
            FROM racecard_details rd 
            WHERE NOT EXISTS (
                SELECT 1 FROM races_cards rc WHERE rc.race_id = rd.race_id
            )
        """
        )
        integrity_checks.append(
            ("Orphaned race participants", orphaned_participants["count"])
        )

        # Check race results have valid race references
        orphaned_results = self.execute_single(
            """
            SELECT COUNT(*) as count 
            FROM records r 
            WHERE NOT EXISTS (
                SELECT 1 FROM races_cards rc WHERE rc.race_id = r.race_id
            )
        """
        )
        integrity_checks.append(("Orphaned race results", orphaned_results["count"]))

        # Check for races without participants
        empty_races = self.execute_single(
            """
            SELECT COUNT(*) as count 
            FROM races_cards rc 
            WHERE NOT EXISTS (
                SELECT 1 FROM racecard_details rd WHERE rd.race_id = rc.race_id
            )
        """
        )
        integrity_checks.append(("Races without participants", empty_races["count"]))

        # Check for horses with invalid statistics
        invalid_horse_stats = self.execute_single(
            """
            SELECT COUNT(*) as count 
            FROM horses_cards 
            WHERE percentage_wins > 100 OR percentage_placed > 100
        """
        )
        integrity_checks.append(
            ("Horses with invalid stats", invalid_horse_stats["count"])
        )

        all_good = True
        for check_name, count in integrity_checks:
            if count > 0:
                logger.warning(f"⚠️ {check_name}: {count}")
                all_good = False
            else:
                logger.info(f"✅ {check_name}: 0 (good)")

        return all_good

    def validate_data_distribution(self):
        """Validate data has good distribution and variety"""
        logger.info("📈 Validating data distribution...")

        # Check date range
        date_range = self.execute_single(
            """
            SELECT 
                MIN(date) as earliest,
                MAX(date) as latest,
                COUNT(DISTINCT date) as unique_dates
            FROM races_cards
        """
        )

        logger.info(
            f"📅 Date range: {date_range['earliest']} to {date_range['latest']}"
        )
        logger.info(f"📅 Unique race dates: {date_range['unique_dates']:,}")

        # Check course variety
        course_stats = self.execute_single(
            """
            SELECT COUNT(DISTINCT course) as course_count
            FROM races_cards
        """
        )
        logger.info(f"🏟️ Unique courses: {course_stats['course_count']}")

        # Check horse name uniqueness
        horse_uniqueness = self.execute_single(
            """
            SELECT 
                COUNT(*) as total_horses,
                COUNT(DISTINCT name) as unique_names
            FROM horses_cards
        """
        )

        uniqueness_rate = (
            horse_uniqueness["unique_names"] / horse_uniqueness["total_horses"]
        ) * 100
        logger.info(f"🐎 Horse name uniqueness: {uniqueness_rate:.1f}%")

        # Check jockey/trainer distribution
        jockey_stats = self.execute_single(
            """
            SELECT 
                COUNT(DISTINCT jockey) as unique_jockeys
            FROM racecard_details
        """
        )

        trainer_stats = self.execute_single(
            """
            SELECT 
                COUNT(DISTINCT trainer) as unique_trainers
            FROM racecard_details
        """
        )

        logger.info(f"🏇 Active jockeys: {jockey_stats['unique_jockeys']}")
        logger.info(f"👨‍🏫 Active trainers: {trainer_stats['unique_trainers']}")

        return True

    def performance_benchmark(self):
        """Run performance benchmarks on the test data"""
        logger.info("⚡ Running performance benchmarks...")

        benchmarks = [
            (
                "Select recent races",
                """
                SELECT * FROM races_cards 
                WHERE date >= '2024-01-01' 
                ORDER BY date DESC 
                LIMIT 100
            """,
            ),
            (
                "Complex horse lookup",
                """
                SELECT h.*, COUNT(rd.race_id) as race_count
                FROM horses_cards h
                LEFT JOIN racecard_details rd ON h.name = rd.name
                WHERE h.total_races > 10
                GROUP BY h.horse_id, h.name
                ORDER BY race_count DESC
                LIMIT 50
            """,
            ),
            (
                "Race results aggregation",
                """
                SELECT 
                    course,
                    COUNT(*) as total_races,
                    AVG(runners) as avg_runners
                FROM races_cards
                WHERE date >= '2023-01-01'
                GROUP BY course
                ORDER BY total_races DESC
                LIMIT 20
            """,
            ),
            (
                "Jockey performance stats",
                """
                SELECT 
                    j.name,
                    j.total_races,
                    j.wins,
                    j.percentage_wins,
                    COUNT(rd.race_id) as active_races
                FROM jockeys_stats j
                LEFT JOIN racecard_details rd ON j.name = rd.jockey
                GROUP BY j.jockey_id, j.name, j.total_races, j.wins, j.percentage_wins
                ORDER BY j.percentage_wins DESC
                LIMIT 25
            """,
            ),
        ]

        for benchmark_name, query in benchmarks:
            start_time = datetime.now()
            try:
                results = self.execute_query(query)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.info(
                    f"✅ {benchmark_name}: {duration:.3f}s ({len(results)} rows)"
                )
            except Exception as e:
                logger.error(f"❌ {benchmark_name} failed: {e}")

    def generate_sample_queries(self):
        """Generate sample queries to demonstrate the test data"""
        logger.info("🧪 Running sample data queries...")

        # Sample race
        sample_race = self.execute_single(
            """
            SELECT * FROM races_cards 
            ORDER BY date DESC 
            LIMIT 1
        """
        )

        if sample_race:
            logger.info(
                f"📋 Sample race: {sample_race['race_name']} at {sample_race['course']}"
            )
            logger.info(
                f"   📅 Date: {sample_race['date']}, Runners: {sample_race['runners']}"
            )

            # Get participants for this race
            participants = self.execute_query(
                f"""
                SELECT name, jockey, trainer, odds
                FROM racecard_details
                WHERE race_id = {sample_race['race_id']}
                ORDER BY horse_number::int
                LIMIT 5
            """
            )

            logger.info("   🏇 Sample participants:")
            for p in participants:
                logger.info(f"      {p['name']} ({p['jockey']}) - {p['odds']}")

        # Top performing horses
        top_horses = self.execute_query(
            """
            SELECT name, total_races, wins, percentage_wins
            FROM horses_cards
            WHERE total_races >= 5
            ORDER BY percentage_wins DESC, wins DESC
            LIMIT 5
        """
        )

        logger.info("🏆 Top performing horses:")
        for horse in top_horses:
            logger.info(
                f"   {horse['name']}: {horse['wins']}/{horse['total_races']} ({horse['percentage_wins']:.1f}%)"
            )

    def full_validation(self):
        """Run complete validation suite"""
        logger.info("🚀 Starting comprehensive test data validation...")
        logger.info("=" * 60)

        start_time = datetime.now()

        try:
            self.connect()

            # Structure validation
            if not self.validate_database_structure():
                logger.error("❌ Database structure validation failed")
                return False

            # Get statistics
            stats = self.get_table_statistics()

            # Data integrity
            integrity_ok = self.validate_data_integrity()

            # Data distribution
            self.validate_data_distribution()

            # Performance benchmarks
            self.performance_benchmark()

            # Sample queries
            self.generate_sample_queries()

            # Final summary
            end_time = datetime.now()
            duration = end_time - start_time

            logger.info("=" * 60)
            logger.info("🎉 TEST DATA VALIDATION COMPLETE!")
            logger.info("=" * 60)
            logger.info("📊 Summary Statistics:")
            total_records = sum(stats.values())
            logger.info(f"   📝 Total records: {total_records:,}")

            for table, count in stats.items():
                logger.info(f"   📋 {table}: {count:,}")

            logger.info(f"⏱️ Validation time: {duration}")
            logger.info(
                f"🎯 Data integrity: {'✅ PASSED' if integrity_ok else '❌ ISSUES FOUND'}"
            )
            logger.info("🎉 TEST DATABASE READY FOR COMPREHENSIVE TESTING!")

            return True

        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False
        finally:
            if self.connection:
                self.connection.close()


def main():
    """Main validation function"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate test database")
    parser.add_argument(
        "--database-url",
        type=str,
        default="postgresql://horse_racing_test:test_password_123@localhost:5434/horse_racing_test_db",
        help="Test database URL",
    )

    args = parser.parse_args()

    validator = TestDataValidator(args.database_url)
    success = validator.full_validation()

    if success:
        print("\n🎉 Validation completed successfully!")
        print("🚀 Test database is ready for comprehensive testing")
    else:
        print("\n❌ Validation failed - check logs for details")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
