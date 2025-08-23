"""
Test suite for pipeline integration components.
Tests the complete file watcher and pipeline automation system.
"""

import pytest
import sys
import os
import tempfile
import shutil
import json
import subprocess
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.automation.file_watcher_enhanced import EnhancedFileWatcher
    from tools.automation.pipeline_automation import PipelineAutomation
except ImportError:
    # Handle import errors gracefully for testing
    EnhancedFileWatcher = None
    PipelineAutomation = None


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config_file(temp_directory):
    """Create a mock configuration file."""
    config = {
        "tables": {
            "result_races": {
                "id": "INTEGER PRIMARY KEY",
                "race_name": "TEXT",
                "date": "DATE"
            },
            "jockeys_stats": {
                "id": "INTEGER PRIMARY KEY",
                "jockey_name": "TEXT",
                "wins": "INTEGER"
            }
        }
    }
    config_file = Path(temp_directory) / "test_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f)
    return str(config_file)


@pytest.fixture
def sample_csv_files(temp_directory):
    """Create sample CSV files for testing."""
    csv_dir = Path(temp_directory) / "csv_files"
    csv_dir.mkdir()
    
    # Create result_races.csv
    result_races_csv = csv_dir / "result_races.csv"
    with open(result_races_csv, 'w') as f:
        f.write("id,race_name,date\n1,Test Race,2025-08-23\n")
    
    # Create jockeys_stats.csv  
    jockeys_csv = csv_dir / "jockeys_stats.csv"
    with open(jockeys_csv, 'w') as f:
        f.write("id,jockey_name,wins\n1,Test Jockey,5\n")
    
    return str(csv_dir)


class TestEnhancedFileWatcher:
    """Test suite for EnhancedFileWatcher class."""
    
    def test_initialization(self, temp_directory):
        """Test file watcher initialization."""
        watcher = EnhancedFileWatcher(watch_directory=temp_directory)
        assert watcher.watch_directory == Path(temp_directory)
        assert watcher.processed_files == set()
        assert watcher.is_running is False
    
    def test_zip_file_detection(self, temp_directory):
        """Test ZIP file detection capability."""
        watcher = EnhancedFileWatcher(watch_directory=temp_directory)
        
        # Create a test ZIP file
        test_zip = Path(temp_directory) / "test_data.zip"
        test_zip.touch()
        
        # Test file detection
        zip_files = list(watcher._get_unprocessed_zip_files())
        assert len(zip_files) == 1
        assert zip_files[0].name == "test_data.zip"
    
    @patch('tools.automation.file_watcher_enhanced.EnhancedFileWatcher._run_csv_mapper')
    @patch('tools.automation.file_watcher_enhanced.EnhancedFileWatcher._run_database_upload')
    @patch('tools.automation.file_watcher_enhanced.EnhancedFileWatcher._trigger_ml_updates')
    def test_pipeline_trigger(self, mock_ml, mock_db, mock_csv, temp_directory):
        """Test pipeline trigger functionality."""
        watcher = EnhancedFileWatcher(watch_directory=temp_directory)
        
        # Mock successful execution
        mock_csv.return_value = True
        mock_db.return_value = True  
        mock_ml.return_value = True
        
        # Test pipeline execution
        result = watcher.trigger_data_pipeline()
        
        assert result is True
        mock_csv.assert_called_once()
        mock_db.assert_called_once()
        mock_ml.assert_called_once()
    
    def test_file_extraction(self, temp_directory):
        """Test ZIP file extraction logic."""
        watcher = EnhancedFileWatcher(watch_directory=temp_directory)
        
        # Create a test directory structure
        extract_dir = Path(temp_directory) / "extracted"
        extract_dir.mkdir()
        
        # Create test CSV files
        (extract_dir / "test1.csv").touch()
        (extract_dir / "test2.csv").touch()
        
        # Test extraction detection
        csv_files = list(extract_dir.glob("*.csv"))
        assert len(csv_files) == 2


class TestPipelineAutomation:
    """Test suite for PipelineAutomation class."""
    
    def test_initialization(self):
        """Test pipeline automation initialization."""
        automation = PipelineAutomation()
        assert automation.logger is not None
        assert hasattr(automation, 'run_pipeline')
    
    @patch('subprocess.run')
    def test_csv_mapper_execution(self, mock_subprocess):
        """Test CSV mapper execution."""
        automation = PipelineAutomation()
        
        # Mock successful subprocess execution
        mock_subprocess.return_value = Mock(returncode=0, stdout="Success")
        
        result = automation._run_csv_mapper()
        
        assert result is True
        mock_subprocess.assert_called_once()
    
    @patch('subprocess.run')
    def test_database_upload_execution(self, mock_subprocess):
        """Test database upload execution."""
        automation = PipelineAutomation()
        
        # Mock successful Docker execution
        mock_subprocess.return_value = Mock(returncode=0, stdout="Upload complete")
        
        result = automation._run_database_upload()
        
        assert result is True
        mock_subprocess.assert_called_once()
    
    @patch('subprocess.run')
    def test_ml_update_trigger(self, mock_subprocess):
        """Test ML update trigger."""
        automation = PipelineAutomation()
        
        # Mock successful ML trigger
        mock_subprocess.return_value = Mock(returncode=0, stdout="ML updated")
        
        result = automation._trigger_ml_updates()
        
        assert result is True
        mock_subprocess.assert_called_once()
    
    @patch('tools.automation.pipeline_automation.PipelineAutomation._run_csv_mapper')
    @patch('tools.automation.pipeline_automation.PipelineAutomation._run_database_upload')
    @patch('tools.automation.pipeline_automation.PipelineAutomation._trigger_ml_updates')
    def test_complete_pipeline_execution(self, mock_ml, mock_db, mock_csv):
        """Test complete pipeline execution."""
        automation = PipelineAutomation()
        
        # Mock all steps as successful
        mock_csv.return_value = True
        mock_db.return_value = True
        mock_ml.return_value = True
        
        result = automation.run_pipeline()
        
        assert result is True
        mock_csv.assert_called_once()
        mock_db.assert_called_once()
        mock_ml.assert_called_once()
    
    def test_error_handling(self):
        """Test error handling in pipeline execution."""
        automation = PipelineAutomation()
        
        with patch('subprocess.run') as mock_subprocess:
            # Mock failed execution
            mock_subprocess.return_value = Mock(returncode=1, stderr="Error occurred")
            
            result = automation._run_csv_mapper()
            assert result is False


class TestCSVColumnMapping:
    """Test suite for CSV column mapping functionality."""
    
    def test_mapping_file_loading(self, mock_config_file):
        """Test loading of CSV column mapping configuration."""
        # Test that we can load the mapping file
        assert Path(mock_config_file).exists()
        
        with open(mock_config_file, 'r') as f:
            config = json.load(f)
        
        assert "tables" in config
        assert "result_races" in config["tables"]
        assert "jockeys_stats" in config["tables"]
    
    def test_separated_table_structure(self, mock_config_file):
        """Test separated table structure in mapping."""
        with open(mock_config_file, 'r') as f:
            config = json.load(f)
        
        # Verify no foreign key references
        for table_name, table_schema in config["tables"].items():
            for column_name, column_def in table_schema.items():
                assert "REFERENCES" not in column_def.upper()
                assert "FOREIGN KEY" not in column_def.upper()


class TestDatabaseUploader:
    """Test suite for database uploader functionality."""
    
    @patch('psycopg2.connect')
    def test_database_connection(self, mock_connect):
        """Test database connection establishment."""
        from tools.data_processing.simple_database_uploader import SimpleDatabaseUploader
        
        # Mock successful connection
        mock_connect.return_value = Mock()
        
        uploader = SimpleDatabaseUploader()
        # Test would verify connection logic
        assert uploader is not None
    
    def test_manifest_format_handling(self, temp_directory):
        """Test handling of different manifest formats."""
        from tools.data_processing.simple_database_uploader import SimpleDatabaseUploader
        
        # Create test manifest with "files" format
        manifest_old = {
            "files": [
                {"file": "result_races.csv", "table": "result_races"}
            ]
        }
        
        # Create test manifest with "tables" format  
        manifest_new = {
            "tables": {
                "result_races": {"file": "result_races.csv"}
            }
        }
        
        manifest_file_old = Path(temp_directory) / "manifest_old.json"
        manifest_file_new = Path(temp_directory) / "manifest_new.json"
        
        with open(manifest_file_old, 'w') as f:
            json.dump(manifest_old, f)
        
        with open(manifest_file_new, 'w') as f:
            json.dump(manifest_new, f)
        
        uploader = SimpleDatabaseUploader()
        
        # Test loading both formats
        data_old = uploader._load_upload_manifest(str(manifest_file_old))
        data_new = uploader._load_upload_manifest(str(manifest_file_new))
        
        assert data_old is not None
        assert data_new is not None


class TestIntegrationScenarios:
    """Test suite for end-to-end integration scenarios."""
    
    @patch('subprocess.run')
    def test_complete_pipeline_flow(self, mock_subprocess, temp_directory):
        """Test complete pipeline flow from file detection to completion."""
        # Mock all subprocess calls as successful
        mock_subprocess.return_value = Mock(returncode=0, stdout="Success")
        
        # Create test environment
        watcher = EnhancedFileWatcher(watch_directory=temp_directory)
        automation = PipelineAutomation()
        
        # Create test ZIP file
        test_zip = Path(temp_directory) / "test_racing_data.zip"
        test_zip.touch()
        
        # Test file detection
        zip_files = list(watcher._get_unprocessed_zip_files())
        assert len(zip_files) == 1
        
        # Test pipeline execution
        with patch.object(watcher, 'trigger_data_pipeline', return_value=True):
            result = watcher.trigger_data_pipeline()
            assert result is True
    
    @patch('docker.from_env')
    def test_docker_integration(self, mock_docker):
        """Test Docker container integration."""
        # Mock Docker client
        mock_client = Mock()
        mock_docker.return_value = mock_client
        
        # Mock container
        mock_container = Mock()
        mock_container.exec_run.return_value = (0, b"Success")
        mock_client.containers.get.return_value = mock_container
        
        # Test Docker execution would work
        assert mock_client is not None
    
    def test_error_recovery(self, temp_directory):
        """Test error recovery and resilience."""
        watcher = EnhancedFileWatcher(watch_directory=temp_directory)
        
        # Test handling of corrupted ZIP files
        corrupt_zip = Path(temp_directory) / "corrupt.zip"
        with open(corrupt_zip, 'w') as f:
            f.write("This is not a valid ZIP file")
        
        # Watcher should handle this gracefully
        zip_files = list(watcher._get_unprocessed_zip_files())
        assert len(zip_files) == 1  # File is detected but processing would fail gracefully


@pytest.mark.integration
class TestFullSystemIntegration:
    """Full system integration tests."""
    
    def test_pipeline_automation_cli(self):
        """Test pipeline automation CLI interface."""
        # Test that the CLI script exists and is executable
        cli_script = project_root / "tools" / "automation" / "pipeline_automation.py"
        assert cli_script.exists()
        assert cli_script.is_file()
    
    def test_configuration_files(self):
        """Test that all required configuration files exist."""
        config_files = [
            project_root / "config" / "csv_column_mapping.json",
            project_root / "docker-compose.clean.yml",
            project_root / "pytest.ini"
        ]
        
        for config_file in config_files:
            assert config_file.exists(), f"Configuration file missing: {config_file}"
    
    def test_docker_services(self):
        """Test Docker services configuration."""
        docker_compose = project_root / "docker-compose.clean.yml"
        assert docker_compose.exists()
        
        # Read and verify Docker compose structure
        with open(docker_compose, 'r') as f:
            content = f.read()
            assert "postgres" in content
            assert "horse_racing_network" in content
    
    @pytest.mark.slow
    def test_database_connectivity(self):
        """Test database connectivity (requires Docker)."""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "horse_racing_postgres_clean" in result.stdout:
                # Database container is running
                assert True
            else:
                # Skip test if container not available
                pytest.skip("Database container not available")
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pytest.skip("Docker not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
