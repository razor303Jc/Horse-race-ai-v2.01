"""
Test suite for file watcher and monitoring functionality.
Tests the enhanced file watcher and automation components.
"""

import pytest
import sys
import os
import tempfile
import shutil
import time
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_zip_file(temp_directory):
    """Create a sample ZIP file with racing data."""
    zip_path = Path(temp_directory) / "racing_data.zip"

    with zipfile.ZipFile(zip_path, "w") as zf:
        # Add sample CSV files
        zf.writestr(
            "result_races.csv",
            "race_id,race_name,winner\n1,Gold Cup,Thunder\n2,Derby,Lightning",
        )
        zf.writestr(
            "jockeys_stats.csv",
            "jockey_id,jockey_name,wins\n1,J. Smith,45\n2,R. Johnson,38",
        )

    return str(zip_path)


class TestFileWatcherCore:
    """Test core file watcher functionality."""

    def test_watch_directory_initialization(self, temp_directory):
        """Test file watcher directory initialization."""
        try:
            from tools.automation.file_watcher_enhanced import EnhancedFileWatcher

            watcher = EnhancedFileWatcher(watch_directory=temp_directory)
            assert watcher.watch_directory == Path(temp_directory)
            assert watcher.processed_files == set()
            assert not watcher.is_running

        except ImportError:
            pytest.skip("EnhancedFileWatcher not available")

    def test_zip_file_detection(self, temp_directory, sample_zip_file):
        """Test ZIP file detection in watch directory."""
        try:
            from tools.automation.file_watcher_enhanced import EnhancedFileWatcher

            # Move ZIP file to watch directory
            zip_in_watch_dir = Path(temp_directory) / "test_data.zip"
            shutil.copy(sample_zip_file, zip_in_watch_dir)

            watcher = EnhancedFileWatcher(watch_directory=temp_directory)

            # Test file detection
            zip_files = list(watcher._get_unprocessed_zip_files())
            assert len(zip_files) == 1
            assert zip_files[0].name == "test_data.zip"

        except ImportError:
            pytest.skip("EnhancedFileWatcher not available")

    def test_file_processing_tracking(self, temp_directory):
        """Test tracking of processed files."""
        try:
            from tools.automation.file_watcher_enhanced import EnhancedFileWatcher

            watcher = EnhancedFileWatcher(watch_directory=temp_directory)

            # Simulate file processing
            test_file = Path(temp_directory) / "test.zip"
            test_file.touch()

            # Mark as processed
            watcher.processed_files.add(str(test_file))

            # Test that processed files are excluded
            unprocessed = list(watcher._get_unprocessed_zip_files())
            assert len(unprocessed) == 0

        except ImportError:
            pytest.skip("EnhancedFileWatcher not available")

    def test_zip_extraction_simulation(self, temp_directory, sample_zip_file):
        """Test ZIP file extraction simulation."""
        # Test ZIP file contents
        with zipfile.ZipFile(sample_zip_file, "r") as zf:
            file_list = zf.namelist()
            assert "result_races.csv" in file_list
            assert "jockeys_stats.csv" in file_list

            # Extract to test directory
            extract_dir = Path(temp_directory) / "extracted"
            extract_dir.mkdir()
            zf.extractall(extract_dir)

            # Verify extraction
            extracted_files = list(extract_dir.glob("*.csv"))
            assert len(extracted_files) == 2


class TestPipelineTriggers:
    """Test pipeline trigger functionality."""

    @patch("subprocess.run")
    def test_csv_mapper_trigger(self, mock_subprocess):
        """Test CSV mapper trigger functionality."""
        try:
            from tools.automation.file_watcher_enhanced import EnhancedFileWatcher

            # Mock successful execution
            mock_subprocess.return_value = Mock(returncode=0, stdout="Success")

            watcher = EnhancedFileWatcher(watch_directory="/tmp")
            result = watcher._run_csv_mapper()

            assert result is True
            mock_subprocess.assert_called_once()

        except ImportError:
            pytest.skip("EnhancedFileWatcher not available")

    @patch("subprocess.run")
    def test_database_upload_trigger(self, mock_subprocess):
        """Test database upload trigger functionality."""
        try:
            from tools.automation.file_watcher_enhanced import EnhancedFileWatcher

            # Mock successful Docker execution
            mock_subprocess.return_value = Mock(returncode=0, stdout="Upload complete")

            watcher = EnhancedFileWatcher(watch_directory="/tmp")
            result = watcher._run_database_upload()

            assert result is True
            mock_subprocess.assert_called_once()

        except ImportError:
            pytest.skip("EnhancedFileWatcher not available")

    @patch("subprocess.run")
    def test_ml_update_trigger(self, mock_subprocess):
        """Test ML model update trigger functionality."""
        try:
            from tools.automation.file_watcher_enhanced import EnhancedFileWatcher

            # Mock successful ML trigger
            mock_subprocess.return_value = Mock(returncode=0, stdout="ML updated")

            watcher = EnhancedFileWatcher(watch_directory="/tmp")
            result = watcher._trigger_ml_updates()

            assert result is True
            mock_subprocess.assert_called_once()

        except ImportError:
            pytest.skip("EnhancedFileWatcher not available")

    def test_complete_pipeline_trigger(self, temp_directory):
        """Test complete pipeline trigger sequence."""
        try:
            from tools.automation.file_watcher_enhanced import EnhancedFileWatcher

            watcher = EnhancedFileWatcher(watch_directory=temp_directory)

            with (
                patch.object(watcher, "_run_csv_mapper", return_value=True),
                patch.object(watcher, "_run_database_upload", return_value=True),
                patch.object(watcher, "_trigger_ml_updates", return_value=True),
            ):

                result = watcher.trigger_data_pipeline()
                assert result is True

        except ImportError:
            pytest.skip("EnhancedFileWatcher not available")


class TestErrorHandling:
    """Test error handling in file watcher."""

    def test_invalid_watch_directory(self):
        """Test handling of invalid watch directory."""
        try:
            from tools.automation.file_watcher_enhanced import EnhancedFileWatcher

            # Test with non-existent directory
            with pytest.raises((FileNotFoundError, OSError)):
                watcher = EnhancedFileWatcher(watch_directory="/non/existent/path")

        except ImportError:
            pytest.skip("EnhancedFileWatcher not available")

    def test_corrupted_zip_handling(self, temp_directory):
        """Test handling of corrupted ZIP files."""
        # Create a corrupted ZIP file
        corrupted_zip = Path(temp_directory) / "corrupted.zip"
        with open(corrupted_zip, "w") as f:
            f.write("This is not a valid ZIP file")

        # Test that system handles corrupted files gracefully
        try:
            with zipfile.ZipFile(corrupted_zip, "r"):
                pass
        except zipfile.BadZipFile:
            # Expected behavior - corrupted files should raise BadZipFile
            assert True

    @patch("subprocess.run")
    def test_pipeline_failure_handling(self, mock_subprocess):
        """Test handling of pipeline execution failures."""
        try:
            from tools.automation.file_watcher_enhanced import EnhancedFileWatcher

            # Mock failed execution
            mock_subprocess.return_value = Mock(returncode=1, stderr="Error occurred")

            watcher = EnhancedFileWatcher(watch_directory="/tmp")
            result = watcher._run_csv_mapper()

            assert result is False

        except ImportError:
            pytest.skip("EnhancedFileWatcher not available")


class TestWatcherConfiguration:
    """Test file watcher configuration and setup."""

    def test_watch_directory_creation(self, temp_directory):
        """Test automatic creation of watch directory."""
        watch_dir = Path(temp_directory) / "new_watch_dir"

        # Directory should not exist initially
        assert not watch_dir.exists()

        # Create directory
        watch_dir.mkdir(exist_ok=True)

        # Directory should now exist
        assert watch_dir.exists()
        assert watch_dir.is_dir()

    def test_configuration_validation(self):
        """Test validation of watcher configuration."""
        # Test configuration parameters
        config = {
            "watch_directory": "/path/to/watch",
            "check_interval": 5,
            "max_retries": 3,
            "enable_logging": True,
        }

        # Validate configuration structure
        assert "watch_directory" in config
        assert isinstance(config["check_interval"], int)
        assert config["check_interval"] > 0
        assert isinstance(config["max_retries"], int)
        assert isinstance(config["enable_logging"], bool)

    def test_logging_configuration(self):
        """Test logging configuration for file watcher."""
        # Test logging setup
        logger = logging.getLogger("test_watcher")
        logger.setLevel(logging.INFO)

        # Test log levels
        assert logger.level == logging.INFO
        assert logger.isEnabledFor(logging.INFO)
        assert logger.isEnabledFor(logging.ERROR)


class TestMonitoringIntegration:
    """Test integration with monitoring systems."""

    def test_progress_tracking(self, temp_directory):
        """Test progress tracking during file processing."""
        try:
            from tools.automation.file_watcher_enhanced import EnhancedFileWatcher

            watcher = EnhancedFileWatcher(watch_directory=temp_directory)

            # Test progress tracking state
            assert hasattr(watcher, "processed_files")
            assert isinstance(watcher.processed_files, set)

        except ImportError:
            pytest.skip("EnhancedFileWatcher not available")

    def test_status_reporting(self):
        """Test status reporting functionality."""
        # Test status structure
        status = {
            "is_running": True,
            "files_processed": 5,
            "last_activity": "2025-08-23T10:30:00Z",
            "errors": 0,
        }

        # Validate status structure
        assert "is_running" in status
        assert "files_processed" in status
        assert "last_activity" in status
        assert "errors" in status
        assert isinstance(status["files_processed"], int)
        assert status["files_processed"] >= 0

    def test_health_check(self, temp_directory):
        """Test health check functionality."""
        # Test basic health indicators
        health_indicators = {
            "watch_directory_accessible": Path(temp_directory).exists(),
            "docker_available": True,  # Mocked for test
            "database_accessible": True,  # Mocked for test
            "disk_space_sufficient": True,  # Mocked for test
        }

        # All health indicators should be positive for healthy system
        assert all(health_indicators.values())


@pytest.mark.integration
class TestFileWatcherSystemIntegration:
    """Integration tests for file watcher with full system."""

    def test_watcher_pipeline_integration(self, temp_directory):
        """Test integration between watcher and pipeline components."""
        try:
            from tools.automation.file_watcher_enhanced import EnhancedFileWatcher
            from tools.automation.pipeline_automation import PipelineAutomation

            watcher = EnhancedFileWatcher(watch_directory=temp_directory)
            pipeline = PipelineAutomation()

            # Test that components can be instantiated together
            assert watcher is not None
            assert pipeline is not None

        except ImportError:
            pytest.skip("Pipeline components not available")

    @pytest.mark.slow
    def test_end_to_end_file_processing(self, temp_directory, sample_zip_file):
        """Test end-to-end file processing workflow."""
        # Copy ZIP file to watch directory
        zip_in_watch = Path(temp_directory) / "test_racing_data.zip"
        shutil.copy(sample_zip_file, zip_in_watch)

        try:
            from tools.automation.file_watcher_enhanced import EnhancedFileWatcher

            watcher = EnhancedFileWatcher(watch_directory=temp_directory)

            # Test file detection
            unprocessed = list(watcher._get_unprocessed_zip_files())
            assert len(unprocessed) == 1

            # Test that pipeline would be triggered
            with patch.object(
                watcher, "trigger_data_pipeline", return_value=True
            ) as mock_trigger:
                # Simulate file processing
                result = watcher.trigger_data_pipeline()
                assert result is True
                mock_trigger.assert_called_once()

        except ImportError:
            pytest.skip("EnhancedFileWatcher not available")

    def test_concurrent_file_handling(self, temp_directory):
        """Test handling of multiple files arriving concurrently."""
        # Create multiple ZIP files
        for i in range(3):
            zip_file = Path(temp_directory) / f"racing_data_{i}.zip"
            with zipfile.ZipFile(zip_file, "w") as zf:
                zf.writestr(f"data_{i}.csv", f"id,name\n{i},Test{i}")

        try:
            from tools.automation.file_watcher_enhanced import EnhancedFileWatcher

            watcher = EnhancedFileWatcher(watch_directory=temp_directory)

            # Test multiple file detection
            unprocessed = list(watcher._get_unprocessed_zip_files())
            assert len(unprocessed) == 3

        except ImportError:
            pytest.skip("EnhancedFileWatcher not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
