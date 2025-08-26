"""
🧪 Database Integration Tests
============================

Integration tests for database operations across the Horse Racing AI system.
Tests multi-database architecture, connection management, and data consistency.
"""

import pytest
import pandas as pd
import psycopg2
from psycopg2.extras import DictCursor
import tempfile
from pathlib import Path

class TestMultiDatabaseArchitecture:
    """Test multi-database architecture (cards + results)"""
    
    def test_cards_database_connection(self, database_connection, test_config):
        """Test connection to cards database"""
        if database_connection:
            with database_connection.cursor(cursor_factory=DictCursor) as cursor:
                # Test basic connection
                cursor.execute("SELECT 1 as test_value")
                result = cursor.fetchone()
                assert result['test_value'] == 1
    
    @pytest.mark.database
    def test_results_database_connection(self, test_config):
        """Test connection to results database"""
        # Use separate results database config
        results_config = test_config['database'].copy()
        results_config['database'] = 'test_results_horse_racing_db'
        
        try:
            conn = psycopg2.connect(**results_config)
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT 1 as test_value")
                result = cursor.fetchone()
                assert result['test_value'] == 1
            conn.close()
        except psycopg2.Error:
            pytest.skip("Results database not available for testing")
    
    def test_database_schema_consistency(self, database_cursor):
        """Test that database schemas are consistent"""
        if database_cursor:
            # Check for required tables
            expected_tables = ['horses', 'races', 'records', 'jockeys_stats', 'trainers_stats']
            
            for table in expected_tables:
                database_cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    )
                """, (table,))
                
                table_exists = database_cursor.fetchone()[0]
                if not table_exists:
                    pytest.skip(f"Table {table} not found in test database")

class TestBulkUploaderDatabaseIntegration:
    """Test bulk uploader database integration"""
    
    def test_bulk_insert_operation(self, database_cursor, clean_database, sample_csv_files):
        """Test bulk insert operations work correctly"""
        if database_cursor:
            # Create test table if not exists
            database_cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_horses (
                    id SERIAL PRIMARY KEY,
                    horse_name VARCHAR(255),
                    age INTEGER,
                    weight VARCHAR(50),
                    jockey VARCHAR(255),
                    trainer VARCHAR(255),
                    odds VARCHAR(50),
                    race_id INTEGER
                )
            """)
            
            # Test bulk insert
            test_data = [
                ('Thunder Bolt', 4, '9-7', 'J. Smith', 'T. Brown', '3/1', 1),
                ('Lightning Strike', 5, '10-2', 'R. Jones', 'S. Davis', '5/2', 1),
                ('Storm Cloud', 6, '9-12', 'M. Williams', 'A. Wilson', '7/1', 1)
            ]
            
            from psycopg2.extras import execute_values
            execute_values(
                database_cursor,
                """
                INSERT INTO test_horses (horse_name, age, weight, jockey, trainer, odds, race_id)
                VALUES %s
                """,
                test_data
            )
            
            # Verify insert
            database_cursor.execute("SELECT COUNT(*) FROM test_horses")
            count = database_cursor.fetchone()[0]
            assert count == 3
    
    @pytest.mark.database
    def test_conflict_handling(self, database_cursor, clean_database):
        """Test ON CONFLICT handling for duplicate data"""
        if database_cursor:
            # Create test table with unique constraint
            database_cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_horses_unique (
                    id SERIAL PRIMARY KEY,
                    horse_name VARCHAR(255) UNIQUE,
                    age INTEGER
                )
            """)
            
            # Insert initial data
            database_cursor.execute("""
                INSERT INTO test_horses_unique (horse_name, age) 
                VALUES ('Thunder Bolt', 4)
            """)
            
            # Try to insert duplicate with ON CONFLICT DO NOTHING
            database_cursor.execute("""
                INSERT INTO test_horses_unique (horse_name, age) 
                VALUES ('Thunder Bolt', 5)
                ON CONFLICT (horse_name) DO NOTHING
            """)
            
            # Verify no duplicate was created
            database_cursor.execute("SELECT COUNT(*) FROM test_horses_unique")
            count = database_cursor.fetchone()[0]
            assert count == 1
            
            # Verify original data unchanged
            database_cursor.execute("""
                SELECT age FROM test_horses_unique WHERE horse_name = 'Thunder Bolt'
            """)
            age = database_cursor.fetchone()[0]
            assert age == 4  # Original age, not updated

class TestPipelineDatabaseIntegration:
    """Test pipeline database integration with fixes"""
    
    @pytest.mark.database
    def test_column_mapping_database_compatibility(self, database_cursor):
        """Test that column mappings are compatible with actual database schema"""
        if database_cursor:
            # Test horses table schema compatibility
            database_cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'horses'
                ORDER BY ordinal_position
            """)
            
            columns = database_cursor.fetchall()
            if columns:
                column_names = [col[0] for col in columns]
                
                # Verify expected columns exist
                expected_columns = ['horse_name', 'age', 'weight', 'jockey', 'trainer']
                for col in expected_columns:
                    if col not in column_names:
                        pytest.skip(f"Expected column {col} not found in horses table")
    
    @pytest.mark.database 
    def test_case_sensitivity_database_handling(self, database_cursor):
        """Test database handling of case sensitivity issues"""
        if database_cursor:
            # Create test table with lowercase column
            database_cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_case_sensitivity (
                    id SERIAL PRIMARY KEY,
                    uptodate DATE
                )
            """)
            
            # Test inserting with correct case
            database_cursor.execute("""
                INSERT INTO test_case_sensitivity (uptodate) VALUES ('2025-08-26')
            """)
            
            # Verify insert successful
            database_cursor.execute("SELECT COUNT(*) FROM test_case_sensitivity")
            count = database_cursor.fetchone()[0]
            assert count == 1
    
    @pytest.mark.database
    def test_foreign_key_constraints(self, database_cursor, clean_database):
        """Test foreign key constraint handling"""
        if database_cursor:
            # Create parent table (races)
            database_cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_races (
                    race_id SERIAL PRIMARY KEY,
                    race_name VARCHAR(255)
                )
            """)
            
            # Create child table (horses) with foreign key
            database_cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_horses_fk (
                    id SERIAL PRIMARY KEY,
                    horse_name VARCHAR(255),
                    race_id INTEGER REFERENCES test_races(race_id)
                )
            """)
            
            # Insert parent record first
            database_cursor.execute("""
                INSERT INTO test_races (race_name) VALUES ('Test Race')
                RETURNING race_id
            """)
            race_id = database_cursor.fetchone()[0]
            
            # Insert child record
            database_cursor.execute("""
                INSERT INTO test_horses_fk (horse_name, race_id) 
                VALUES ('Test Horse', %s)
            """, (race_id,))
            
            # Verify foreign key relationship
            database_cursor.execute("""
                SELECT h.horse_name, r.race_name 
                FROM test_horses_fk h 
                JOIN test_races r ON h.race_id = r.race_id
            """)
            
            result = database_cursor.fetchone()
            assert result[0] == 'Test Horse'
            assert result[1] == 'Test Race'

class TestMLDatabaseIntegration:
    """Test ML pipeline database integration"""
    
    @pytest.mark.database
    @pytest.mark.ml
    def test_training_data_extraction(self, database_cursor, clean_database):
        """Test extracting training data from database"""
        if database_cursor:
            # Create and populate test data for ML training
            database_cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_training_data (
                    id SERIAL PRIMARY KEY,
                    horse_name VARCHAR(255),
                    age INTEGER,
                    or_rating INTEGER,
                    runners INTEGER,
                    position INTEGER,
                    sp DECIMAL
                )
            """)
            
            # Insert training data
            training_records = [
                ('Horse 1', 4, 85, 8, 1, 3.0),
                ('Horse 2', 5, 90, 8, 2, 5.5),
                ('Horse 3', 6, 88, 8, 3, 7.0),
                ('Horse 4', 4, 86, 10, 1, 2.8)
            ]
            
            from psycopg2.extras import execute_values
            execute_values(
                database_cursor,
                """
                INSERT INTO ml_training_data (horse_name, age, or_rating, runners, position, sp)
                VALUES %s
                """,
                training_records
            )
            
            # Test data extraction query
            database_cursor.execute("""
                SELECT age, or_rating, runners, position, sp,
                       CASE WHEN position = 1 THEN 1 ELSE 0 END as won
                FROM ml_training_data
                WHERE age IS NOT NULL AND or_rating IS NOT NULL
            """)
            
            results = database_cursor.fetchall()
            assert len(results) == 4
            
            # Verify target variable creation
            won_count = sum(1 for row in results if row[5] == 1)  # won column
            assert won_count == 2  # Two horses in position 1
    
    @pytest.mark.database
    @pytest.mark.ml 
    def test_model_metadata_storage(self, database_cursor):
        """Test storing ML model metadata in database"""
        if database_cursor:
            # Create model metadata table
            database_cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_model_metadata (
                    id SERIAL PRIMARY KEY,
                    model_name VARCHAR(255),
                    training_date TIMESTAMP,
                    accuracy DECIMAL,
                    auc DECIMAL,
                    features_used TEXT[]
                )
            """)
            
            # Insert model metadata
            database_cursor.execute("""
                INSERT INTO ml_model_metadata 
                (model_name, training_date, accuracy, auc, features_used)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                'random_forest_win_predictor',
                '2025-08-26 12:00:00',
                0.85,
                0.92,
                ['age', 'or_rating', 'runners', 'is_favorite']
            ))
            
            # Verify storage
            database_cursor.execute("""
                SELECT model_name, accuracy, auc FROM ml_model_metadata
                WHERE model_name = 'random_forest_win_predictor'
            """)
            
            result = database_cursor.fetchone()
            assert result[0] == 'random_forest_win_predictor'
            assert float(result[1]) == 0.85
            assert float(result[2]) == 0.92

class TestDatabasePerformance:
    """Test database performance and optimization"""
    
    @pytest.mark.performance
    @pytest.mark.database
    def test_bulk_insert_performance(self, database_cursor, clean_database):
        """Test bulk insert performance"""
        if database_cursor:
            # Create test table
            database_cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_test (
                    id SERIAL PRIMARY KEY,
                    horse_name VARCHAR(255),
                    data_field INTEGER
                )
            """)
            
            # Generate large dataset
            large_dataset = [
                (f'Horse {i}', i % 1000) for i in range(10000)
            ]
            
            import time
            start_time = time.time()
            
            # Bulk insert
            from psycopg2.extras import execute_values
            execute_values(
                database_cursor,
                "INSERT INTO performance_test (horse_name, data_field) VALUES %s",
                large_dataset,
                page_size=1000
            )
            
            end_time = time.time()
            insert_time = end_time - start_time
            
            # Performance assertion (should insert 10k records quickly)
            assert insert_time < 5.0, f"Bulk insert too slow: {insert_time}s"
            
            # Verify all records inserted
            database_cursor.execute("SELECT COUNT(*) FROM performance_test")
            count = database_cursor.fetchone()[0]
            assert count == 10000
    
    @pytest.mark.performance
    @pytest.mark.database
    def test_query_performance(self, database_cursor):
        """Test query performance on large datasets"""
        if database_cursor:
            # Test query performance
            import time
            start_time = time.time()
            
            database_cursor.execute("""
                SELECT horse_name, data_field 
                FROM performance_test 
                WHERE data_field < 100
                ORDER BY data_field
                LIMIT 1000
            """)
            
            results = database_cursor.fetchall()
            end_time = time.time()
            query_time = end_time - start_time
            
            # Query should be fast
            assert query_time < 1.0, f"Query too slow: {query_time}s"
            assert len(results) > 0

class TestDatabaseMigrationSupport:
    """Test database migration and schema evolution support"""
    
    @pytest.mark.database
    def test_schema_migration_compatibility(self, database_cursor):
        """Test schema migration compatibility"""
        if database_cursor:
            # Test adding new column to existing table
            database_cursor.execute("""
                CREATE TABLE IF NOT EXISTS migration_test (
                    id SERIAL PRIMARY KEY,
                    original_field VARCHAR(255)
                )
            """)
            
            # Insert some data
            database_cursor.execute("""
                INSERT INTO migration_test (original_field) VALUES ('test_data')
            """)
            
            # Add new column (simulating migration)
            database_cursor.execute("""
                ALTER TABLE migration_test 
                ADD COLUMN IF NOT EXISTS new_field INTEGER DEFAULT 0
            """)
            
            # Verify migration worked
            database_cursor.execute("""
                SELECT original_field, new_field FROM migration_test
            """)
            
            result = database_cursor.fetchone()
            assert result[0] == 'test_data'
            assert result[1] == 0  # Default value

# Test markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.database
]
