"""
🧪 Index Table Updater Tests - v2.05
====================================

Tests for the standalone index table updater script that maintains
lookup tables for horses, jockeys, and trainers.
"""

import pytest
import psycopg2
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.update_index_tables import (
    get_db_connection,
    update_horses_index,
    update_jockeys_index,
    update_trainers_index,
    get_index_stats,
    main,
)


class TestDatabaseConnection:
    """Test database connection functionality"""

    @patch("psycopg2.connect")
    def test_get_db_connection_success(self, mock_connect):
        """Test successful database connection"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        conn = get_db_connection()

        assert conn == mock_conn
        mock_connect.assert_called_once()

    @patch("psycopg2.connect")
    def test_get_db_connection_failure(self, mock_connect):
        """Test database connection failure"""
        mock_connect.side_effect = psycopg2.OperationalError("Connection failed")

        with pytest.raises(psycopg2.OperationalError):
            get_db_connection()


class TestIndexUpdates:
    """Test individual index table update functions"""

    @pytest.fixture
    def mock_cursor(self):
        """Mock database cursor"""
        cursor = Mock()
        cursor.rowcount = 5  # Simulate 5 new records
        return cursor

    def test_update_horses_index(self, mock_cursor):
        """Test horses index update"""
        result = update_horses_index(mock_cursor)

        assert result == 5
        mock_cursor.execute.assert_called_once()

        # Verify the SQL contains the expected logic
        sql_call = mock_cursor.execute.call_args[0][0]
        assert "INSERT INTO horses_index" in sql_call
        assert "horse_name" in sql_call
        assert "horse_id" in sql_call
        assert "NOT EXISTS" in sql_call

    def test_update_jockeys_index(self, mock_cursor):
        """Test jockeys index update"""
        result = update_jockeys_index(mock_cursor)

        assert result == 5
        mock_cursor.execute.assert_called_once()

        sql_call = mock_cursor.execute.call_args[0][0]
        assert "INSERT INTO jockeys_index" in sql_call
        assert "jockey_name" in sql_call
        assert "ROW_NUMBER()" in sql_call

    def test_update_trainers_index(self, mock_cursor):
        """Test trainers index update"""
        result = update_trainers_index(mock_cursor)

        assert result == 5
        mock_cursor.execute.assert_called_once()

        sql_call = mock_cursor.execute.call_args[0][0]
        assert "INSERT INTO trainers_index" in sql_call
        assert "trainer_name" in sql_call
        assert "ROW_NUMBER()" in sql_call

    def test_update_no_new_records(self, mock_cursor):
        """Test update when no new records exist"""
        mock_cursor.rowcount = 0

        result = update_horses_index(mock_cursor)

        assert result == 0
        mock_cursor.execute.assert_called_once()


class TestIndexStats:
    """Test index statistics functionality"""

    @pytest.fixture
    def mock_cursor_with_stats(self):
        """Mock cursor that returns statistics"""
        cursor = Mock()
        # Mock the fetchone() calls for different table counts
        cursor.fetchone.side_effect = [
            (391,),  # horses_index count
            (192,),  # jockeys_index count
            (223,),  # trainers_index count
            (782,),  # race_results count
        ]
        return cursor

    def test_get_index_stats(self, mock_cursor_with_stats):
        """Test getting index statistics"""
        stats = get_index_stats(mock_cursor_with_stats)

        expected_stats = {
            "horses": 391,
            "jockeys": 192,
            "trainers": 223,
            "race_results": 782,
        }

        assert stats == expected_stats
        assert mock_cursor_with_stats.execute.call_count == 4


class TestMainFunction:
    """Test the main execution function"""

    @patch("scripts.update_index_tables.get_db_connection")
    @patch("scripts.update_index_tables.get_index_stats")
    @patch("scripts.update_index_tables.update_horses_index")
    @patch("scripts.update_index_tables.update_jockeys_index")
    @patch("scripts.update_index_tables.update_trainers_index")
    def test_main_success_with_updates(
        self,
        mock_update_trainers,
        mock_update_jockeys,
        mock_update_horses,
        mock_get_stats,
        mock_get_conn,
    ):
        """Test main function with successful updates"""
        # Setup mocks
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # Mock statistics
        mock_get_stats.side_effect = [
            {"horses": 390, "jockeys": 190, "trainers": 220, "race_results": 782},
            {"horses": 391, "jockeys": 192, "trainers": 223, "race_results": 782},
        ]

        # Mock updates returning new records
        mock_update_horses.return_value = 1
        mock_update_jockeys.return_value = 2
        mock_update_trainers.return_value = 3

        # Run main function
        main()

        # Verify all functions were called
        mock_get_conn.assert_called_once()
        mock_update_horses.assert_called_once_with(mock_cursor)
        mock_update_jockeys.assert_called_once_with(mock_cursor)
        mock_update_trainers.assert_called_once_with(mock_cursor)
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("scripts.update_index_tables.get_db_connection")
    @patch("scripts.update_index_tables.get_index_stats")
    @patch("scripts.update_index_tables.update_horses_index")
    @patch("scripts.update_index_tables.update_jockeys_index")
    @patch("scripts.update_index_tables.update_trainers_index")
    def test_main_no_updates_needed(
        self,
        mock_update_trainers,
        mock_update_jockeys,
        mock_update_horses,
        mock_get_stats,
        mock_get_conn,
    ):
        """Test main function when no updates are needed"""
        # Setup mocks
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # Mock statistics (same before and after)
        mock_get_stats.side_effect = [
            {"horses": 391, "jockeys": 192, "trainers": 223, "race_results": 782},
            {"horses": 391, "jockeys": 192, "trainers": 223, "race_results": 782},
        ]

        # Mock updates returning no new records
        mock_update_horses.return_value = 0
        mock_update_jockeys.return_value = 0
        mock_update_trainers.return_value = 0

        # Run main function
        main()

        # Verify commit still called even with no updates
        mock_conn.commit.assert_called_once()

    @patch("scripts.update_index_tables.get_db_connection")
    def test_main_database_error(self, mock_get_conn):
        """Test main function with database error"""
        mock_get_conn.side_effect = psycopg2.OperationalError("Connection failed")

        # Should not raise exception, should handle gracefully
        try:
            main()
        except Exception as e:
            pytest.fail(
                f"main() should handle database errors gracefully, but raised: {e}"
            )


class TestIndexTableStructure:
    """Test index table structure and constraints"""

    def test_horses_index_structure(self):
        """Test horses_index table structure"""
        # This would test the actual table structure
        # if we had a test database
        pass

    def test_unique_constraints(self):
        """Test unique constraints on index tables"""
        # Test that duplicate entries are handled properly
        pass

    def test_foreign_key_relationships(self):
        """Test relationships between index and main tables"""
        pass


class TestLogging:
    """Test logging functionality"""

    @patch("scripts.update_index_tables.logging")
    @patch("scripts.update_index_tables.get_db_connection")
    def test_logging_setup(self, mock_get_conn, mock_logging):
        """Test that logging is properly set up"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        main()

        # Verify logging calls were made
        assert mock_logging.info.call_count > 0


class TestErrorHandling:
    """Test error handling scenarios"""

    @patch("scripts.update_index_tables.get_db_connection")
    def test_cursor_error_handling(self, mock_get_conn):
        """Test handling of cursor-related errors"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = psycopg2.Error("SQL Error")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # Should handle the error gracefully
        try:
            main()
        except Exception as e:
            pytest.fail(f"Should handle SQL errors gracefully, but raised: {e}")

    @patch("scripts.update_index_tables.get_db_connection")
    def test_connection_cleanup(self, mock_get_conn):
        """Test that connections are properly cleaned up"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # Simulate an error during execution
        mock_cursor.execute.side_effect = Exception("Test error")

        try:
            main()
        except:
            pass

        # Verify cleanup still happens
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


# Integration test fixtures
@pytest.fixture
def test_database_config():
    """Test database configuration"""
    return {
        "host": "localhost",
        "database": "results_horse_racing_db",
        "user": "horse_racing",
        "password": "horse_racing_password",
        "port": "5432",
    }


@pytest.fixture
def sample_race_results_data():
    """Sample race results data for testing index updates"""
    return [
        (
            1,
            1,
            1,
            1,
            101,
            "New Horse A",
            "GB",
            4,
            135,
            5.0,
            "New Jockey A",
            "New Trainer A",
            "F",
            0,
        ),
        (
            2,
            2,
            2,
            2,
            102,
            "New Horse B",
            "IRE",
            5,
            140,
            10.0,
            "New Jockey B",
            "New Trainer B",
            "2",
            1.5,
        ),
        (
            3,
            3,
            999,
            3,
            103,
            "New Horse C",
            "FR",
            3,
            132,
            15.0,
            "New Jockey C",
            "New Trainer C",
            "3",
            999,
        ),
    ]
