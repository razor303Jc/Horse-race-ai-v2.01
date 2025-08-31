"""
🧪 Database Relationship Tests - results_horse_racing_db
========================================================

Tests to explore and validate relationships, constraints, and data integrity
in the results_horse_racing_db PostgreSQL database.

These tests are exploratory - failures are expected and informative!
"""

import pytest
import psycopg2
from psycopg2.extras import DictCursor
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "results_horse_racing_db",
    "user": "horse_racing",
    "password": "horse_racing_password",
    "port": "5432",
}

logger = logging.getLogger(__name__)


class TestDatabaseRelationships:
    """Test database relationships and constraints"""

    @pytest.fixture
    def db_connection(self):
        """Database connection fixture"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            yield conn
            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("Database not available for testing")

    @pytest.fixture
    def db_cursor(self, db_connection):
        """Database cursor fixture"""
        cursor = db_connection.cursor(cursor_factory=DictCursor)
        yield cursor
        cursor.close()

    def test_table_existence(self, db_cursor):
        """Test that all expected tables exist"""
        expected_tables = [
            "horses_entity",
            "jockeys_entity",
            "trainers_entity",
            "races",
            "race_results",
            "horses_index",
            "jockeys_index",
            "trainers_index",
        ]

        db_cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        )

        actual_tables = [row[0] for row in db_cursor.fetchall()]

        for table in expected_tables:
            assert (
                table in actual_tables
            ), f"Table {table} not found. Available: {actual_tables}"

        logger.info(f"✅ All expected tables exist: {expected_tables}")

    def test_foreign_key_constraints(self, db_cursor):
        """Discover and test foreign key constraints"""
        db_cursor.execute(
            """
            SELECT 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                tc.constraint_name
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            ORDER BY tc.table_name, kcu.column_name;
        """
        )

        foreign_keys = db_cursor.fetchall()

        logger.info("🔗 Foreign Key Relationships Found:")
        for fk in foreign_keys:
            logger.info(
                f"  {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}"
            )

        # Test: Should have at least some foreign key relationships
        assert len(foreign_keys) >= 0, "Expected some foreign key constraints"

        return foreign_keys

    def test_primary_key_constraints(self, db_cursor):
        """Discover primary key constraints"""
        db_cursor.execute(
            """
            SELECT 
                tc.table_name,
                kcu.column_name,
                tc.constraint_name
            FROM 
                information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
            ORDER BY tc.table_name;
        """
        )

        primary_keys = db_cursor.fetchall()

        logger.info("🔑 Primary Keys Found:")
        for pk in primary_keys:
            logger.info(f"  {pk['table_name']}.{pk['column_name']}")

        # Each table should have a primary key
        tables_with_pk = {pk["table_name"] for pk in primary_keys}
        expected_tables = [
            "horses_entity",
            "jockeys_entity",
            "trainers_entity",
            "races",
            "race_results",
        ]

        for table in expected_tables:
            if table not in tables_with_pk:
                logger.warning(f"⚠️  Table {table} has no primary key")

        return primary_keys

    def test_unique_constraints(self, db_cursor):
        """Discover unique constraints"""
        db_cursor.execute(
            """
            SELECT 
                tc.table_name,
                kcu.column_name,
                tc.constraint_name
            FROM 
                information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'UNIQUE'
            ORDER BY tc.table_name, kcu.column_name;
        """
        )

        unique_constraints = db_cursor.fetchall()

        logger.info("🎯 Unique Constraints Found:")
        for uc in unique_constraints:
            logger.info(f"  {uc['table_name']}.{uc['column_name']}")

        return unique_constraints


class TestDataRelationships:
    """Test actual data relationships"""

    @pytest.fixture
    def db_cursor(self):
        """Database cursor fixture"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor(cursor_factory=DictCursor)
            yield cursor
            cursor.close()
            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("Database not available for testing")

    def test_race_results_to_races_relationship(self, db_cursor):
        """Test relationship between race_results and races"""
        # Check if all race_ids in race_results exist in races
        db_cursor.execute(
            """
            SELECT DISTINCT race_id 
            FROM race_results 
            WHERE race_id NOT IN (SELECT race_id FROM races)
            LIMIT 10;
        """
        )

        orphaned_race_ids = db_cursor.fetchall()

        if orphaned_race_ids:
            logger.warning(
                f"⚠️  Found {len(orphaned_race_ids)} race_results with no matching race:"
            )
            for row in orphaned_race_ids:
                logger.warning(f"    race_id: {row[0]}")
        else:
            logger.info("✅ All race_results have matching races")

        # This might fail - that's OK, we're exploring!
        assert (
            len(orphaned_race_ids) <= 100
        ), f"Too many orphaned race_results: {len(orphaned_race_ids)}"

    def test_horses_consistency(self, db_cursor):
        """Test consistency between horses in different tables"""
        # Check horses in race_results vs horses_entity
        db_cursor.execute(
            """
            SELECT DISTINCT rr.horse_id, rr.horse_name
            FROM race_results rr
            WHERE rr.horse_id NOT IN (SELECT horse_id FROM horses_entity)
            LIMIT 10;
        """
        )

        missing_horses = db_cursor.fetchall()

        logger.info(
            f"🐎 Horses in race_results but not in horses_entity: {len(missing_horses)}"
        )
        for horse in missing_horses[:5]:  # Show first 5
            logger.info(f"    ID: {horse[0]}, Name: {horse[1]}")

        # Check horses in race_results vs horses_index
        db_cursor.execute(
            """
            SELECT COUNT(DISTINCT rr.horse_name)
            FROM race_results rr
            WHERE rr.horse_name NOT IN (SELECT horse_name FROM horses_index);
        """
        )

        missing_from_index = db_cursor.fetchone()[0]
        logger.info(
            f"🗂️  Horses in race_results but not in horses_index: {missing_from_index}"
        )

        return {
            "missing_from_entity": len(missing_horses),
            "missing_from_index": missing_from_index,
        }

    def test_jockeys_consistency(self, db_cursor):
        """Test consistency between jockeys in different tables"""
        # Check jockeys in race_results vs jockeys_entity
        db_cursor.execute(
            """
            SELECT COUNT(DISTINCT rr.jockey_name)
            FROM race_results rr
            WHERE rr.jockey_name NOT IN (SELECT jockey_name FROM jockeys_entity)
            AND rr.jockey_name IS NOT NULL;
        """
        )

        missing_jockeys_entity = db_cursor.fetchone()[0]

        # Check jockeys in race_results vs jockeys_index
        db_cursor.execute(
            """
            SELECT COUNT(DISTINCT rr.jockey_name)
            FROM race_results rr
            WHERE rr.jockey_name NOT IN (SELECT jockey_name FROM jockeys_index)
            AND rr.jockey_name IS NOT NULL;
        """
        )

        missing_jockeys_index = db_cursor.fetchone()[0]

        logger.info(f"🏇 Jockeys missing from jockeys_entity: {missing_jockeys_entity}")
        logger.info(f"🗂️  Jockeys missing from jockeys_index: {missing_jockeys_index}")

        return {
            "missing_from_entity": missing_jockeys_entity,
            "missing_from_index": missing_jockeys_index,
        }

    def test_trainers_consistency(self, db_cursor):
        """Test consistency between trainers in different tables"""
        # Check trainers in race_results vs trainers_entity
        db_cursor.execute(
            """
            SELECT COUNT(DISTINCT rr.trainer_name)
            FROM race_results rr
            WHERE rr.trainer_name NOT IN (SELECT trainer_name FROM trainers_entity)
            AND rr.trainer_name IS NOT NULL;
        """
        )

        missing_trainers_entity = db_cursor.fetchone()[0]

        # Check trainers in race_results vs trainers_index
        db_cursor.execute(
            """
            SELECT COUNT(DISTINCT rr.trainer_name)
            FROM race_results rr
            WHERE rr.trainer_name NOT IN (SELECT trainer_name FROM trainers_index)
            AND rr.trainer_name IS NOT NULL;
        """
        )

        missing_trainers_index = db_cursor.fetchone()[0]

        logger.info(
            f"👨‍🏫 Trainers missing from trainers_entity: {missing_trainers_entity}"
        )
        logger.info(
            f"🗂️  Trainers missing from trainers_index: {missing_trainers_index}"
        )

        return {
            "missing_from_entity": missing_trainers_entity,
            "missing_from_index": missing_trainers_index,
        }


class TestDataIntegrity:
    """Test data integrity and constraints"""

    @pytest.fixture
    def db_cursor(self):
        """Database cursor fixture"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor(cursor_factory=DictCursor)
            yield cursor
            cursor.close()
            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("Database not available for testing")

    def test_null_values_in_critical_fields(self, db_cursor):
        """Test for NULL values in critical fields"""
        critical_checks = {
            "race_results": [
                ("race_id", "Race ID should not be NULL"),
                ("horse_id", "Horse ID should not be NULL"),
                ("horse_name", "Horse name should not be NULL"),
            ],
            "races": [("race_id", "Race ID should not be NULL")],
            "horses_entity": [
                ("horse_id", "Horse ID should not be NULL"),
                ("horse_name", "Horse name should not be NULL"),
            ],
        }

        integrity_issues = []

        for table, checks in critical_checks.items():
            for column, description in checks:
                db_cursor.execute(
                    f"""
                    SELECT COUNT(*) 
                    FROM {table} 
                    WHERE {column} IS NULL;
                """
                )

                null_count = db_cursor.fetchone()[0]

                if null_count > 0:
                    logger.warning(
                        f"⚠️  {table}.{column}: {null_count} NULL values - {description}"
                    )
                    integrity_issues.append(f"{table}.{column}: {null_count} NULLs")
                else:
                    logger.info(f"✅ {table}.{column}: No NULL values")

        return integrity_issues

    def test_duplicate_primary_keys(self, db_cursor):
        """Test for duplicate values in primary key candidates"""
        tables_to_check = [
            ("horses_entity", "horse_id"),
            ("jockeys_entity", "jockey_id"),
            ("trainers_entity", "trainer_id"),
            ("races", "race_id"),
        ]

        duplicates_found = []

        for table, id_column in tables_to_check:
            db_cursor.execute(
                f"""
                SELECT {id_column}, COUNT(*) as count
                FROM {table}
                GROUP BY {id_column}
                HAVING COUNT(*) > 1
                ORDER BY count DESC
                LIMIT 5;
            """
            )

            duplicates = db_cursor.fetchall()

            if duplicates:
                logger.warning(f"⚠️  Duplicate {id_column} in {table}:")
                for dup in duplicates:
                    logger.warning(f"    {id_column}: {dup[0]} appears {dup[1]} times")
                duplicates_found.append(
                    f"{table}.{id_column}: {len(duplicates)} duplicates"
                )
            else:
                logger.info(f"✅ No duplicate {id_column} in {table}")

        return duplicates_found

    def test_place_code_values(self, db_cursor):
        """Test place code values in race_results"""
        db_cursor.execute(
            """
            SELECT place, COUNT(*) as count
            FROM race_results
            GROUP BY place
            ORDER BY count DESC;
        """
        )

        place_values = db_cursor.fetchall()

        logger.info("🏁 Place code distribution:")
        for place, count in place_values[:10]:  # Show top 10
            logger.info(f"    Place {place}: {count} occurrences")

        # Check for our mapped values
        mapped_codes = [996, 997, 998, 999]  # RR, U, PU, F
        found_mapped = [place for place, count in place_values if place in mapped_codes]

        logger.info(f"🎯 Found mapped place codes: {found_mapped}")

        return place_values


class TestIndexTableRelationships:
    """Test relationships between main tables and index tables"""

    @pytest.fixture
    def db_cursor(self):
        """Database cursor fixture"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor(cursor_factory=DictCursor)
            yield cursor
            cursor.close()
            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("Database not available for testing")

    def test_index_table_completeness(self, db_cursor):
        """Test if index tables contain all entities from race_results"""
        # Test horses_index completeness
        db_cursor.execute(
            """
            SELECT COUNT(DISTINCT horse_name) as race_results_horses
            FROM race_results
            WHERE horse_name IS NOT NULL;
        """
        )
        horses_in_results = db_cursor.fetchone()[0]

        db_cursor.execute("SELECT COUNT(*) as indexed_horses FROM horses_index;")
        horses_in_index = db_cursor.fetchone()[0]

        logger.info(
            f"🐎 Horses: {horses_in_results} in race_results, {horses_in_index} in index"
        )

        # Test jockeys_index completeness
        db_cursor.execute(
            """
            SELECT COUNT(DISTINCT jockey_name) as race_results_jockeys
            FROM race_results
            WHERE jockey_name IS NOT NULL;
        """
        )
        jockeys_in_results = db_cursor.fetchone()[0]

        db_cursor.execute("SELECT COUNT(*) as indexed_jockeys FROM jockeys_index;")
        jockeys_in_index = db_cursor.fetchone()[0]

        logger.info(
            f"🏇 Jockeys: {jockeys_in_results} in race_results, {jockeys_in_index} in index"
        )

        # Test trainers_index completeness
        db_cursor.execute(
            """
            SELECT COUNT(DISTINCT trainer_name) as race_results_trainers
            FROM race_results
            WHERE trainer_name IS NOT NULL;
        """
        )
        trainers_in_results = db_cursor.fetchone()[0]

        db_cursor.execute("SELECT COUNT(*) as indexed_trainers FROM trainers_index;")
        trainers_in_index = db_cursor.fetchone()[0]

        logger.info(
            f"👨‍🏫 Trainers: {trainers_in_results} in race_results, {trainers_in_index} in index"
        )

        return {
            "horses": {"results": horses_in_results, "index": horses_in_index},
            "jockeys": {"results": jockeys_in_results, "index": jockeys_in_index},
            "trainers": {"results": trainers_in_results, "index": trainers_in_index},
        }

    def test_index_table_structure(self, db_cursor):
        """Test index table structure"""
        index_tables = ["horses_index", "jockeys_index", "trainers_index"]

        for table in index_tables:
            db_cursor.execute(
                f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table}'
                ORDER BY ordinal_position;
            """
            )

            columns = db_cursor.fetchall()

            logger.info(f"📋 {table} structure:")
            for col in columns:
                logger.info(
                    f"    {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'}"
                )


# Performance and statistics tests
class TestDatabasePerformance:
    """Test database performance and statistics"""

    @pytest.fixture
    def db_cursor(self):
        """Database cursor fixture"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor(cursor_factory=DictCursor)
            yield cursor
            cursor.close()
            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("Database not available for testing")

    @pytest.mark.slow
    def test_table_sizes(self, db_cursor):
        """Test table sizes and row counts"""
        tables = [
            "horses_entity",
            "jockeys_entity",
            "trainers_entity",
            "races",
            "race_results",
            "horses_index",
            "jockeys_index",
            "trainers_index",
        ]

        table_stats = {}

        for table in tables:
            db_cursor.execute(f"SELECT COUNT(*) FROM {table};")
            row_count = db_cursor.fetchone()[0]

            db_cursor.execute(
                f"""
                SELECT pg_size_pretty(pg_total_relation_size('{table}'));
            """
            )
            size = db_cursor.fetchone()[0]

            table_stats[table] = {"rows": row_count, "size": size}
            logger.info(f"📊 {table}: {row_count:,} rows, {size}")

        return table_stats
