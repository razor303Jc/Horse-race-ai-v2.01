#!/usr/bin/env python3
"""
Bulk Uploader Test Suite
Comprehensive tests for the bulk uploader system
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path
import os
import sys

# Add the bulk uploader to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bulk_uploader import (
    BulkUploadConfig,
    DatabaseConnectionManager,
    DataDiscoveryEngine,
    ValidationEngine,
    BulkProcessingEngine,
    BulkUploader,
)


class TestBulkUploadConfig:
    """Test configuration management"""

    def test_default_config(self):
        config = BulkUploadConfig()
        assert config.batch_size == 1000
        assert config.max_workers == 4
        assert config.validation_level == "strict"

    def test_custom_config(self):
        config = BulkUploadConfig(batch_size=500, validation_level="lenient")
        assert config.batch_size == 500
        assert config.validation_level == "lenient"


class TestDatabaseConnectionManager:
    """Test database connection management"""

    def test_environment_detection_container(self):
        # Mock container environment
        os.environ["DOCKER_CONTAINER"] = "true"
        manager = DatabaseConnectionManager()

        assert manager.config["host"] == "postgres"
        assert manager.config["port"] == "5432"

        # Cleanup
        if "DOCKER_CONTAINER" in os.environ:
            del os.environ["DOCKER_CONTAINER"]

    def test_environment_detection_local(self):
        # Ensure no container markers
        if "DOCKER_CONTAINER" in os.environ:
            del os.environ["DOCKER_CONTAINER"]

        manager = DatabaseConnectionManager()

        # Should default to localhost
        assert (
            "localhost" in manager.config["host"]
            or os.environ.get("DB_HOST") == manager.config["host"]
        )


class TestDataDiscoveryEngine:
    """Test data discovery functionality"""

    def setup_method(self):
        self.config = BulkUploadConfig()
        self.engine = DataDiscoveryEngine(self.config)
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_supported_formats(self):
        assert ".csv" in self.engine.supported_formats
        assert ".json" in self.engine.supported_formats
        assert ".xlsx" in self.engine.supported_formats

    def test_file_discovery(self):
        # Create test files
        (self.temp_path / "test.csv").touch()
        (self.temp_path / "test.json").touch()
        (self.temp_path / "test.txt").touch()  # Not supported

        files = self.engine.discover_files(self.temp_path)

        assert len(files) == 2
        assert any("test.csv" in str(f) for f in files)
        assert any("test.json" in str(f) for f in files)
        assert not any("test.txt" in str(f) for f in files)

    def test_file_classification(self):
        # Test classification rules
        assert self.engine.classify_file(Path("mapped_horses.csv")) == "horses"
        assert self.engine.classify_file(Path("mapped_races.csv")) == "races"
        assert self.engine.classify_file(Path("mapped_records.csv")) == "records"
        assert self.engine.classify_file(Path("unknown_file.csv")) is None

    def test_metadata_extraction(self):
        # Create test CSV file
        test_file = self.temp_path / "test.csv"
        test_data = pd.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})
        test_data.to_csv(test_file, index=False)

        metadata = self.engine.extract_metadata(test_file)

        assert "file_path" in metadata
        assert "file_size" in metadata
        assert "columns" in metadata
        assert metadata["columns"] == ["id", "name"]
        assert metadata["estimated_rows"] == 3


class TestValidationEngine:
    """Test validation functionality"""

    def setup_method(self):
        self.config = BulkUploadConfig()
        # Note: These tests would need a test database for full validation
        # For now, we'll test the logic without actual DB connections

    def test_column_mappings(self):
        config = BulkUploadConfig()

        # Create a mock DB manager for testing
        class MockDBManager:
            def get_connection(self):
                return None

        engine = ValidationEngine(MockDBManager(), config)

        # Test mapping retrieval
        horses_mappings = engine.column_mappings.get("horses", {})
        assert horses_mappings.get("id") == "horse_id"
        assert horses_mappings.get("name") == "horse_name"


class TestBulkProcessingEngine:
    """Test data processing functionality"""

    def setup_method(self):
        self.config = BulkUploadConfig()

        # Create mock validator
        class MockValidator:
            def get_table_schema(self, table_name):
                return {
                    "horse_id": {"type": "integer", "nullable": False},
                    "horse_name": {"type": "text", "nullable": False},
                }

            def validate_data_integrity(self, df, table_name):
                return {"valid": True, "warnings": [], "errors": []}

        self.engine = BulkProcessingEngine(MockValidator(), self.config)
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_data_type_conversion(self):
        # Create test DataFrame
        df = pd.DataFrame(
            {
                "horse_id": ["1", "2", "3"],  # String that should become int
                "horse_name": ["Horse A", "Horse B", "Horse C"],
            }
        )

        table_schema = {
            "horse_id": {"type": "integer", "nullable": False},
            "horse_name": {"type": "text", "nullable": False},
        }

        self.engine._convert_data_types(df, table_schema)

        # Check that horse_id was converted to int
        assert pd.api.types.is_integer_dtype(df["horse_id"])

    def test_file_processing(self):
        # Create test CSV file
        test_file = self.temp_path / "test_horses.csv"
        test_data = pd.DataFrame(
            {"id": [1, 2, 3], "name": ["Horse A", "Horse B", "Horse C"]}
        )
        test_data.to_csv(test_file, index=False)

        validation_results = {
            "valid": True,
            "column_mapping": {"id": "horse_id", "name": "horse_name"},
        }

        success, df, error = self.engine.process_file(
            test_file, "horses", validation_results
        )

        assert success
        assert len(df) == 3
        assert "horse_id" in df.columns
        assert "horse_name" in df.columns


class TestBulkUploader:
    """Test main uploader functionality"""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create test data files
        self.create_test_files()

    def teardown_method(self):
        import shutil

        shutil.rmtree(self.temp_dir)

    def create_test_files(self):
        """Create test data files"""
        # Horses file
        horses_data = pd.DataFrame(
            {"horse_id": [1, 2, 3], "horse_name": ["Thunder", "Lightning", "Storm"]}
        )
        horses_data.to_csv(self.temp_path / "mapped_horses.csv", index=False)

        # Races file
        races_data = pd.DataFrame(
            {"race_id": [101, 102, 103], "race_name": ["Derby", "Stakes", "Classic"]}
        )
        races_data.to_csv(self.temp_path / "mapped_races.csv", index=False)

        # Non-matching file (should be ignored)
        other_data = pd.DataFrame({"col1": [1, 2, 3]})
        other_data.to_csv(self.temp_path / "other_data.csv", index=False)

    def test_job_id_generation(self):
        uploader = BulkUploader()

        test_path = Path("test_file.csv")
        job_id1 = uploader._generate_job_id(test_path)
        job_id2 = uploader._generate_job_id(test_path)

        # Job IDs should be different (due to timestamp)
        assert job_id1 != job_id2
        assert job_id1.startswith("job_")

    def test_file_discovery_and_queuing(self):
        uploader = BulkUploader()

        job_ids = uploader.discover_and_queue_files(self.temp_path)

        # Should find horses and races files, but not other_data
        assert len(job_ids) == 2

        # Check that jobs were created properly
        for job_id in job_ids:
            assert job_id in uploader.jobs
            job = uploader.jobs[job_id]
            assert job.table_name in ["horses", "races"]
            assert job.status == "pending"

    def test_job_status_tracking(self):
        uploader = BulkUploader()

        job_ids = uploader.discover_and_queue_files(self.temp_path)

        # Test status retrieval
        for job_id in job_ids:
            status = uploader.get_job_status(job_id)

            assert status is not None
            assert status["job_id"] == job_id
            assert status["status"] == "pending"
            assert "file_path" in status
            assert "table_name" in status

        # Test all jobs status
        all_status = uploader.get_all_jobs_status()
        assert len(all_status) == len(job_ids)


def run_tests():
    """Run the test suite"""
    print("🧪 Running Bulk Uploader Test Suite")
    print("=" * 50)

    # Run tests with pytest
    exit_code = pytest.main([__file__, "-v", "--tb=short", "--no-header"])

    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")

    return exit_code


if __name__ == "__main__":
    import sys

    sys.exit(run_tests())
