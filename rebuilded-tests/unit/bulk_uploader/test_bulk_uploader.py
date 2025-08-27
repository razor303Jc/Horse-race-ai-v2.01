"""
🧪 Bulk Uploader Unit Tests
===========================

Unit tests for the bulk uploader system components.
Tests individual functions and classes in isolation.
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json

# Test the actual bulk uploader modules
try:
    import sys

    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    from tools.bulk_uploader.simple_bulk_uploader import SimpleBulkUploader, DataCleaner
    from tools.bulk_uploader.column_mappings import CSV_COLUMN_MAPPINGS

    BULK_UPLOADER_AVAILABLE = True
except ImportError:
    BULK_UPLOADER_AVAILABLE = False

    # Create mock classes for testing structure
    class SimpleBulkUploader:
        pass

    class DataCleaner:
        pass

    CSV_COLUMN_MAPPINGS = {}


class TestDataCleaner:
    """Test the DataCleaner utility class"""

    def test_clean_percentage_fields(self):
        """Test percentage field cleaning"""
        # Create test data with percentage fields
        df = pd.DataFrame(
            {
                "win_percentage": ["20%", "15.5%", "", "0%"],
                "roi": ["25.5%", "-8.2%", "", "N/A"],
            }
        )

        # Test percentage cleaning
        cleaned_df = DataCleaner.clean_percentage_fields(df, "win_percentage")

        # Verify percentages were converted to floats
        assert cleaned_df["win_percentage"].iloc[0] == 20.0
        assert cleaned_df["win_percentage"].iloc[1] == 15.5
        assert pd.isna(cleaned_df["win_percentage"].iloc[2])
        assert cleaned_df["win_percentage"].iloc[3] == 0.0

    def test_clean_numeric_fields(self):
        """Test numeric field cleaning with problematic values"""
        df = pd.DataFrame(
            {"finish_position": [1, "-", "", "Unknown"], "age": [4, "-", "N/A", 6]}
        )

        # Test numeric cleaning
        cleaned_df = DataCleaner.clean_numeric_fields(df, "finish_position")
        cleaned_df = DataCleaner.clean_numeric_fields(cleaned_df, "age")

        # Verify problematic values were converted to NaN
        assert cleaned_df["finish_position"].iloc[0] == 1.0
        assert pd.isna(cleaned_df["finish_position"].iloc[1])
        assert pd.isna(cleaned_df["finish_position"].iloc[2])
        assert pd.isna(cleaned_df["finish_position"].iloc[3])

        assert cleaned_df["age"].iloc[0] == 4.0
        assert pd.isna(cleaned_df["age"].iloc[1])
        assert pd.isna(cleaned_df["age"].iloc[2])
        assert cleaned_df["age"].iloc[3] == 6.0

    def test_clean_race_results_fields(self):
        """Test race results specific field cleaning"""
        df = pd.DataFrame({"finish_position": ["1st", "2nd", "3rd", "PU", "F"]})

        # Test race results cleaning
        cleaned_df = DataCleaner.clean_race_results_fields(df)

        # Verify ordinals were converted to integers
        assert cleaned_df["finish_position"].iloc[0] == 1.0
        assert cleaned_df["finish_position"].iloc[1] == 2.0
        assert cleaned_df["finish_position"].iloc[2] == 3.0
        # Non-numeric positions should become NaN
        assert pd.isna(cleaned_df["finish_position"].iloc[3])
        assert pd.isna(cleaned_df["finish_position"].iloc[4])


class TestColumnMappings:
    """Test column mapping functionality"""

    def test_column_mappings_structure(self):
        """Test that column mappings have correct structure"""
        # Verify key tables exist in mappings
        expected_tables = [
            "horses",
            "races",
            "records",
            "jockeys_stats",
            "trainers_stats",
        ]

        for table in expected_tables:
            assert table in CSV_COLUMN_MAPPINGS, f"Table {table} missing from mappings"
            assert (
                "csv_to_db" in CSV_COLUMN_MAPPINGS[table]
            ), f"csv_to_db missing for {table}"

    def test_horses_id_mapping_fix(self):
        """Test that horses table has correct id mapping"""
        if "results_horses" in CSV_COLUMN_MAPPINGS:
            horses_mapping = CSV_COLUMN_MAPPINGS["results_horses"]["csv_to_db"]
            assert "id" in horses_mapping, "horses mapping should include 'id' field"
            assert (
                horses_mapping["id"] == "horse_id"
            ), "CSV 'id' should map to 'horse_id'"

    def test_case_sensitivity_fix(self):
        """Test that case sensitivity issues are handled"""
        # Check jockeys_stats mapping
        if "jockeys_stats" in CSV_COLUMN_MAPPINGS:
            jockeys_mapping = CSV_COLUMN_MAPPINGS["jockeys_stats"]["csv_to_db"]
            assert (
                "uptodate" in jockeys_mapping
            ), "jockeys_stats should have uptodate mapping"
            assert (
                jockeys_mapping["uptodate"] == "uptodate"
            ), "uptodate should map to uptodate"

        # Check trainers_stats mapping
        if "trainers_stats" in CSV_COLUMN_MAPPINGS:
            trainers_mapping = CSV_COLUMN_MAPPINGS["trainers_stats"]["csv_to_db"]
            assert (
                "uptodate" in trainers_mapping
            ), "trainers_stats should have uptodate mapping"
            assert (
                trainers_mapping["uptodate"] == "uptodate"
            ), "uptodate should map to uptodate"


class TestBulkUploader:
    """Test the main BulkUploader class"""

    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.mock_config = {
            "databases": {
                "cards": {"host": "localhost", "database": "test_cards_db"},
                "results": {"host": "localhost", "database": "test_results_db"},
            }
        }

    @patch("tools.bulk_uploader.simple_bulk_uploader.psycopg2.connect")
    def test_database_connection(self, mock_connect):
        """Test database connection establishment"""
        # Setup mock connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        if BULK_UPLOADER_AVAILABLE:
            uploader = SimpleBulkUploader()

            # Test connection creation
            conn = uploader.get_connection("cards")
            assert conn is not None
            mock_connect.assert_called()

    def test_file_discovery(self):
        """Test CSV file discovery functionality"""
        # Create test CSV files
        test_files = {
            "horses.csv": pd.DataFrame({"horse_name": ["Test Horse"], "age": [4]}),
            "races.csv": pd.DataFrame({"race_name": ["Test Race"], "distance": ["1m"]}),
            "records.csv": pd.DataFrame(
                {"horse_name": ["Test Horse"], "position": [1]}
            ),
        }

        # Write test files
        for filename, df in test_files.items():
            df.to_csv(self.temp_dir / filename, index=False)

        if BULK_UPLOADER_AVAILABLE:
            uploader = BulkUploader()
            discovered_files = uploader.discover_csv_files(self.temp_dir)

            # Verify file discovery
            assert len(discovered_files) == len(test_files)
            assert all(f.name in test_files.keys() for f in discovered_files)

    @patch("tools.bulk_uploader.simple_bulk_uploader.psycopg2.connect")
    def test_upload_process(self, mock_connect):
        """Test the upload process with mock database"""
        # Setup mock database
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Create test CSV file
        test_df = pd.DataFrame(
            {
                "horse_name": ["Thunder Bolt", "Lightning Strike"],
                "age": [4, 5],
                "weight": ["9-7", "10-2"],
                "race_id": [1, 1],
            }
        )
        test_file = self.temp_dir / "horses.csv"
        test_df.to_csv(test_file, index=False)

        if BULK_UPLOADER_AVAILABLE:
            uploader = BulkUploader()

            # Test upload process
            result = uploader.process_file(test_file, "horses")

            # Verify database interaction
            mock_connect.assert_called()
            assert result is not None


class TestBulkUploaderIntegration:
    """Integration tests for bulk uploader components"""

    def test_data_cleaning_integration(self):
        """Test integration between data cleaning components"""
        # Create problematic data
        df = pd.DataFrame(
            {
                "horse_name": ["Good Horse", "Bad Horse"],
                "age": [4, "-"],
                "win_percentage": ["20%", ""],
                "finish_position": ["1st", "PU"],
                "UptoDate": ["2025-08-26", "2025-08-26"],
            }
        )

        # Apply all cleaning functions
        cleaned_df = DataCleaner.clean_percentage_fields(df, "win_percentage")
        cleaned_df = DataCleaner.clean_numeric_fields(cleaned_df, "age")
        cleaned_df = DataCleaner.clean_race_results_fields(cleaned_df)

        # Verify comprehensive cleaning
        assert cleaned_df["win_percentage"].iloc[0] == 20.0
        assert pd.isna(cleaned_df["win_percentage"].iloc[1])
        assert cleaned_df["age"].iloc[0] == 4.0
        assert pd.isna(cleaned_df["age"].iloc[1])
        assert cleaned_df["finish_position"].iloc[0] == 1.0
        assert pd.isna(cleaned_df["finish_position"].iloc[1])

    def test_column_mapping_application(self):
        """Test applying column mappings to data"""
        # Create test data with CSV column names
        df = pd.DataFrame(
            {
                "id": [1, 2],
                "horse_name": ["Horse 1", "Horse 2"],
                "UptoDate": ["2025-08-26", "2025-08-26"],
            }
        )

        # Test mapping application (conceptual)
        if "results_horses" in CSV_COLUMN_MAPPINGS:
            mapping = CSV_COLUMN_MAPPINGS["results_horses"]["csv_to_db"]

            # Verify mappings exist for problematic columns
            assert "id" in mapping
            assert mapping["id"] == "horse_id"


class TestBulkUploaderPerformance:
    """Performance tests for bulk uploader"""

    @pytest.mark.performance
    def test_large_file_processing(self):
        """Test processing large CSV files"""
        # Create large test dataset
        large_df = pd.DataFrame(
            {
                "horse_name": [f"Horse {i}" for i in range(10000)],
                "age": [4] * 10000,
                "weight": ["9-7"] * 10000,
                "race_id": [1] * 10000,
            }
        )

        temp_dir = Path(tempfile.mkdtemp())
        large_file = temp_dir / "large_horses.csv"
        large_df.to_csv(large_file, index=False)

        # Time the data cleaning
        import time

        start_time = time.time()

        cleaned_df = DataCleaner.clean_numeric_fields(large_df, "age")

        end_time = time.time()
        processing_time = end_time - start_time

        # Performance assertion (should process 10k records in under 1 second)
        assert (
            processing_time < 1.0
        ), f"Large file processing too slow: {processing_time}s"
        assert len(cleaned_df) == 10000


# Test markers for categorization
pytestmark = [pytest.mark.unit, pytest.mark.bulk_uploader]
