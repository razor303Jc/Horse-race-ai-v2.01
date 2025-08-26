"""
🧪 Rebuilded Test Framework Configuration
=======================================

Global test configuration and fixtures for the Horse Racing AI v2.04 test framework.
Provides comprehensive setup for unit, integration, system, and performance testing.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Dict, Generator, Any
import pytest
import pandas as pd
import psycopg2
from psycopg2.extras import DictCursor
from unittest.mock import Mock, MagicMock
import logging

# Setup test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test project root
TEST_ROOT = Path(__file__).parent
PROJECT_ROOT = TEST_ROOT.parent

# Test data directories
FIXTURES_DIR = TEST_ROOT / "fixtures"
SAMPLE_DATA_DIR = FIXTURES_DIR / "sample_csv_data"
REPORTS_DIR = TEST_ROOT / "reports"

# Ensure directories exist
FIXTURES_DIR.mkdir(exist_ok=True)
SAMPLE_DATA_DIR.mkdir(exist_ok=True) 
REPORTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Create reports directory
    REPORTS_DIR.mkdir(exist_ok=True)
    
    # Setup test environment variables
    os.environ["TESTING"] = "true"
    os.environ["TEST_DATABASE_URL"] = "postgresql://horse_racing:test_password@localhost:5433/test_horse_racing_db"
    
    logger.info("🧪 Test framework configured")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on file location
        if "unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "system/" in str(item.fspath):
            item.add_marker(pytest.mark.system)
        elif "performance/" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            
        # Add component-specific markers
        if "bulk_uploader/" in str(item.fspath):
            item.add_marker(pytest.mark.bulk_uploader)
        elif "pipeline/" in str(item.fspath):
            item.add_marker(pytest.mark.pipeline)
        elif "ml_training/" in str(item.fspath):
            item.add_marker(pytest.mark.ml)
        elif "api/" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "database/" in str(item.fspath):
            item.add_marker(pytest.mark.database)

# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_database_config():
    """Test database configuration"""
    return {
        "host": "localhost",
        "port": 5433,  # Test database port
        "database": "test_horse_racing_db",
        "user": "horse_racing",
        "password": "test_password",
    }

@pytest.fixture(scope="session")
def database_connection(test_database_config):
    """Create test database connection"""
    try:
        conn = psycopg2.connect(**test_database_config)
        conn.autocommit = True
        yield conn
        conn.close()
    except psycopg2.Error as e:
        logger.warning(f"Test database not available: {e}")
        yield None

@pytest.fixture
def database_cursor(database_connection):
    """Create database cursor for tests"""
    if database_connection:
        with database_connection.cursor(cursor_factory=DictCursor) as cursor:
            yield cursor
    else:
        yield None

@pytest.fixture
def clean_database(database_connection):
    """Clean database before each test"""
    if database_connection:
        with database_connection.cursor() as cursor:
            # Clean test tables
            tables = ['records', 'horses', 'races', 'jockeys_stats', 'trainers_stats']
            for table in tables:
                try:
                    cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
                except psycopg2.Error:
                    pass  # Table might not exist
    yield
    # Cleanup after test if needed

# ============================================================================
# FILE SYSTEM FIXTURES  
# ============================================================================

@pytest.fixture
def temp_directory():
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def sample_csv_files(temp_directory):
    """Create sample CSV files for testing"""
    files = {}
    
    # Sample horses.csv
    horses_data = {
        'horse_name': ['Thunder Bolt', 'Lightning Strike', 'Storm Cloud'],
        'age': [4, 5, 6],
        'weight': ['9-7', '10-2', '9-12'],
        'jockey': ['J. Smith', 'R. Jones', 'M. Williams'],
        'trainer': ['T. Brown', 'S. Davis', 'A. Wilson'],
        'odds': ['3/1', '5/2', '7/1'],
        'race_id': [1, 1, 1]
    }
    horses_file = temp_directory / "horses.csv"
    pd.DataFrame(horses_data).to_csv(horses_file, index=False)
    files['horses'] = horses_file
    
    # Sample races.csv
    races_data = {
        'race_id': [1, 2, 3],
        'race_time': ['14:30', '15:05', '15:40'],
        'race_name': ['Maiden Stakes', 'Handicap', 'Novice Hurdle'],
        'distance': ['1m 2f', '1m 4f', '2m'],
        'going': ['Good', 'Good to Firm', 'Soft'],
        'race_class': ['Class 4', 'Class 3', 'Class 2']
    }
    races_file = temp_directory / "races.csv"
    pd.DataFrame(races_data).to_csv(races_file, index=False)
    files['races'] = races_file
    
    # Sample records.csv
    records_data = {
        'horse_name': ['Thunder Bolt', 'Lightning Strike', 'Storm Cloud'],
        'finish_position': [1, 2, 3],
        'starting_price': ['3/1', '5/2', '7/1'],
        'jockey': ['J. Smith', 'R. Jones', 'M. Williams'],
        'race_id': [1, 1, 1]
    }
    records_file = temp_directory / "records.csv"
    pd.DataFrame(records_data).to_csv(records_file, index=False)
    files['records'] = records_file
    
    return files

@pytest.fixture
def problematic_csv_files(temp_directory):
    """Create CSV files with data quality issues for testing"""
    files = {}
    
    # CSV with missing values and bad data types
    problematic_data = {
        'horse_name': ['Good Horse', '', None, 'Bad Horse'],
        'age': [4, '-', '', 'Unknown'],
        'weight': ['9-7', '', None, 'Heavy'],
        'finish_position': [1, '-', '', 'Last'],
        'win_percentage': ['20%', '', None, 'Good'],
        'UptoDate': ['2025-08-26', '2025-08-26', '', None]  # Case sensitivity issue
    }
    problematic_file = temp_directory / "problematic.csv"
    pd.DataFrame(problematic_data).to_csv(problematic_file, index=False)
    files['problematic'] = problematic_file
    
    return files

# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_database_connection():
    """Mock database connection for testing without real database"""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__exit__.return_value = None
    return mock_conn

@pytest.fixture
def mock_bulk_uploader():
    """Mock bulk uploader for testing"""
    mock_uploader = Mock()
    mock_uploader.process_files.return_value = (8, 0)  # 8 successful, 0 failed
    mock_uploader.get_upload_summary.return_value = {
        'total_files': 8,
        'successful': 8,
        'failed': 0,
        'total_records': 12591
    }
    return mock_uploader

@pytest.fixture
def mock_ml_pipeline():
    """Mock ML training pipeline for testing"""
    mock_pipeline = Mock()
    mock_pipeline.train_models.return_value = True
    mock_pipeline.get_model_performance.return_value = {
        'accuracy': 0.85,
        'auc': 0.92,
        'models_trained': 2
    }
    return mock_pipeline

# ============================================================================
# CONFIGURATION FIXTURES
# ============================================================================

@pytest.fixture
def test_config():
    """Test configuration dictionary"""
    return {
        'database': {
            'host': 'localhost',
            'port': 5433,
            'database': 'test_horse_racing_db',
            'user': 'horse_racing',
            'password': 'test_password'
        },
        'bulk_uploader': {
            'batch_size': 100,
            'max_workers': 2,
            'timeout': 30
        },
        'ml_training': {
            'test_size': 0.2,
            'random_state': 42,
            'max_iter': 100
        }
    }

@pytest.fixture
def column_mappings():
    """Column mappings for testing data transformations"""
    return {
        'horses': {
            'csv_to_db': {
                'horse_name': 'horse_name',
                'age': 'age',
                'weight': 'weight',
                'jockey': 'jockey',
                'trainer': 'trainer',
                'odds': 'odds',
                'race_id': 'race_id'
            }
        },
        'races': {
            'csv_to_db': {
                'race_time': 'race_time',
                'race_name': 'race_name',
                'distance': 'distance',
                'going': 'going',
                'race_class': 'race_class',
                'race_id': 'race_id'
            }
        }
    }

# ============================================================================
# ASYNC FIXTURES
# ============================================================================

@pytest.fixture(scope="session") 
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_database_connection():
    """Async database connection for testing"""
    # This would use asyncpg in a real implementation
    mock_conn = Mock()
    yield mock_conn

# ============================================================================
# PERFORMANCE FIXTURES
# ============================================================================

@pytest.fixture
def performance_baseline():
    """Performance baselines for testing"""
    return {
        'bulk_upload_rate': 10000,  # records per minute
        'api_response_time': 200,   # milliseconds
        'ml_training_time': 300,    # seconds
        'memory_usage': 500         # MB
    }

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_test_data(rows: int = 100) -> pd.DataFrame:
    """Create test dataframe with specified number of rows"""
    import random
    
    horses = [f"Test Horse {i}" for i in range(1, rows + 1)]
    ages = [random.randint(3, 8) for _ in range(rows)]
    weights = [f"{random.randint(8, 11)}-{random.randint(0, 13)}" for _ in range(rows)]
    
    return pd.DataFrame({
        'horse_name': horses,
        'age': ages,
        'weight': weights,
        'race_id': [random.randint(1, 10) for _ in range(rows)]
    })

def assert_database_state(cursor, table: str, expected_count: int):
    """Assert database table has expected number of records"""
    if cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        actual_count = cursor.fetchone()[0]
        assert actual_count == expected_count, f"Expected {expected_count} records in {table}, got {actual_count}"

def assert_file_processed(file_path: Path, expected_records: int):
    """Assert file was processed correctly"""
    assert file_path.exists(), f"File {file_path} should exist"
    df = pd.read_csv(file_path)
    assert len(df) == expected_records, f"Expected {expected_records} records, got {len(df)}"

# ============================================================================
# TEST MARKERS AND CATEGORIES
# ============================================================================

# Fast tests that should run in CI
pytest.mark.fast = pytest.mark.unit

# Slow tests that may be skipped in quick runs  
pytest.mark.slow = pytest.mark.system

# Tests requiring external dependencies
pytest.mark.external = pytest.mark.database

# Critical tests that must always pass
pytest.mark.critical = pytest.mark.smoke
