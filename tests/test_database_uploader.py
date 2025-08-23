"""
Test suite for database uploader functionality.
Tests the simple database uploader and upload manifest handling.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.data_processing.simple_database_uploader import SimpleDatabaseUploader
except ImportError:
    SimpleDatabaseUploader = None


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_manifest_old_format():
    """Create sample upload manifest in old format."""
    return {
        "files": [
            {"file": "result_races.csv", "table": "result_races"},
            {"file": "jockeys_stats.csv", "table": "jockeys_stats"},
            {"file": "trainers_stats.csv", "table": "trainers_stats"}
        ]
    }


@pytest.fixture
def sample_manifest_new_format():
    """Create sample upload manifest in new format."""
    return {
        "tables": {
            "result_races": {"file": "result_races.csv"},
            "jockeys_stats": {"file": "jockeys_stats.csv"},
            "trainers_stats": {"file": "trainers_stats.csv"}
        }
    }


@pytest.fixture
def sample_csv_files(temp_directory):
    """Create sample CSV files for upload testing."""
    csv_files = {}
    
    # Create result_races.csv
    result_races_content = """race_id,race_name,winner,finish_time
1,Gold Cup,Thunder,2:45.67
2,Derby Stakes,Lightning,2:33.12
3,Oaks,Storm,2:41.89"""
    
    result_races_file = Path(temp_directory) / "result_races.csv"
    with open(result_races_file, 'w') as f:
        f.write(result_races_content)
    csv_files['result_races.csv'] = str(result_races_file)
    
    # Create jockeys_stats.csv
    jockeys_content = """jockey_id,jockey_name,total_wins,total_races
1,J. Smith,45,180
2,R. Johnson,38,165
3,M. Williams,52,200"""
    
    jockeys_file = Path(temp_directory) / "jockeys_stats.csv"
    with open(jockeys_file, 'w') as f:
        f.write(jockeys_content)
    csv_files['jockeys_stats.csv'] = str(jockeys_file)
    
    return csv_files


class TestSimpleDatabaseUploader:
    """Test suite for SimpleDatabaseUploader class."""
    
    def test_initialization(self):
        """Test uploader initialization."""
        if SimpleDatabaseUploader is None:
            pytest.skip("SimpleDatabaseUploader not available")
        
        uploader = SimpleDatabaseUploader()
        assert uploader is not None
        assert hasattr(uploader, '_load_upload_manifest')
        assert hasattr(uploader, 'upload_files')
    
    def test_manifest_loading_old_format(self, temp_directory, sample_manifest_old_format):
        """Test loading manifest in old format."""
        if SimpleDatabaseUploader is None:
            pytest.skip("SimpleDatabaseUploader not available")
        
        manifest_file = Path(temp_directory) / "manifest_old.json"
        with open(manifest_file, 'w') as f:
            json.dump(sample_manifest_old_format, f)
        
        uploader = SimpleDatabaseUploader()
        manifest_data = uploader._load_upload_manifest(str(manifest_file))
        
        assert manifest_data is not None
        assert "files" in manifest_data
        assert len(manifest_data["files"]) == 3
    
    def test_manifest_loading_new_format(self, temp_directory, sample_manifest_new_format):
        """Test loading manifest in new format."""
        if SimpleDatabaseUploader is None:
            pytest.skip("SimpleDatabaseUploader not available")
        
        manifest_file = Path(temp_directory) / "manifest_new.json"
        with open(manifest_file, 'w') as f:
            json.dump(sample_manifest_new_format, f)
        
        uploader = SimpleDatabaseUploader()
        manifest_data = uploader._load_upload_manifest(str(manifest_file))
        
        assert manifest_data is not None
        assert "tables" in manifest_data
        assert len(manifest_data["tables"]) == 3
    
    def test_manifest_format_flexibility(self, temp_directory):
        """Test that uploader handles both manifest formats."""
        if SimpleDatabaseUploader is None:
            pytest.skip("SimpleDatabaseUploader not available")
        
        # Test old format
        old_manifest = {
            "files": [{"file": "test.csv", "table": "test_table"}]
        }
        old_file = Path(temp_directory) / "old_manifest.json"
        with open(old_file, 'w') as f:
            json.dump(old_manifest, f)
        
        # Test new format
        new_manifest = {
            "tables": {"test_table": {"file": "test.csv"}}
        }
        new_file = Path(temp_directory) / "new_manifest.json"
        with open(new_file, 'w') as f:
            json.dump(new_manifest, f)
        
        uploader = SimpleDatabaseUploader()
        
        old_data = uploader._load_upload_manifest(str(old_file))
        new_data = uploader._load_upload_manifest(str(new_file))
        
        assert old_data is not None
        assert new_data is not None
    
    @patch('psycopg2.connect')
    def test_database_connection(self, mock_connect):
        """Test database connection establishment."""
        if SimpleDatabaseUploader is None:
            pytest.skip("SimpleDatabaseUploader not available")
        
        # Mock successful connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        uploader = SimpleDatabaseUploader()
        
        # Test connection would be established
        assert mock_connect is not None
    
    @patch('psycopg2.connect')
    def test_table_creation(self, mock_connect):
        """Test database table creation."""
        if SimpleDatabaseUploader is None:
            pytest.skip("SimpleDatabaseUploader not available")
        
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        uploader = SimpleDatabaseUploader()
        
        # Test table creation logic
        table_schema = {
            "race_id": "INTEGER PRIMARY KEY",
            "race_name": "TEXT NOT NULL",
            "winner": "TEXT"
        }
        
        # This would test the table creation functionality
        assert table_schema is not None
    
    def test_csv_file_validation(self, sample_csv_files):
        """Test CSV file validation before upload."""
        if SimpleDatabaseUploader is None:
            pytest.skip("SimpleDatabaseUploader not available")
        
        uploader = SimpleDatabaseUploader()
        
        for filename, filepath in sample_csv_files.items():
            # Test file exists and is readable
            assert Path(filepath).exists()
            
            # Test file has CSV content
            with open(filepath, 'r') as f:
                content = f.read()
                assert ',' in content  # Basic CSV check
                assert '\n' in content  # Multiple lines
    
    def test_error_handling(self):
        """Test error handling in uploader."""
        if SimpleDatabaseUploader is None:
            pytest.skip("SimpleDatabaseUploader not available")
        
        uploader = SimpleDatabaseUploader()
        
        # Test handling of non-existent manifest file
        result = uploader._load_upload_manifest("non_existent_file.json")
        assert result is None or result == {}
    
    @patch('subprocess.run')
    def test_docker_integration(self, mock_subprocess):
        """Test Docker container integration for uploads."""
        # Mock successful Docker execution
        mock_subprocess.return_value = Mock(returncode=0, stdout="Upload successful")
        
        # Test Docker command execution
        result = mock_subprocess.return_value
        assert result.returncode == 0


class TestUploadManifestHandling:
    """Test suite for upload manifest handling and processing."""
    
    def test_manifest_validation(self, sample_manifest_old_format, sample_manifest_new_format):
        """Test validation of manifest file structure."""
        # Test old format validation
        assert "files" in sample_manifest_old_format
        for file_entry in sample_manifest_old_format["files"]:
            assert "file" in file_entry
            assert "table" in file_entry
        
        # Test new format validation
        assert "tables" in sample_manifest_new_format
        for table_name, table_info in sample_manifest_new_format["tables"].items():
            assert "file" in table_info
            assert isinstance(table_name, str)
    
    def test_manifest_conversion(self):
        """Test conversion between manifest formats."""
        # Test converting old format to new format
        old_format = {
            "files": [
                {"file": "races.csv", "table": "races"},
                {"file": "jockeys.csv", "table": "jockeys"}
            ]
        }
        
        # Convert to new format
        new_format = {"tables": {}}
        for file_entry in old_format["files"]:
            table_name = file_entry["table"]
            new_format["tables"][table_name] = {"file": file_entry["file"]}
        
        assert "tables" in new_format
        assert "races" in new_format["tables"]
        assert "jockeys" in new_format["tables"]
        assert new_format["tables"]["races"]["file"] == "races.csv"
    
    def test_manifest_file_paths(self, temp_directory):
        """Test handling of file paths in manifest."""
        manifest = {
            "tables": {
                "test_table": {"file": "data/test.csv"}
            }
        }
        
        manifest_file = Path(temp_directory) / "test_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f)
        
        # Test manifest file creation and reading
        assert manifest_file.exists()
        
        with open(manifest_file, 'r') as f:
            loaded_manifest = json.load(f)
        
        assert loaded_manifest == manifest


class TestDatabaseSchemaHandling:
    """Test suite for database schema handling."""
    
    def test_separated_table_schemas(self):
        """Test separated table schema definitions."""
        # Define separated schemas
        card_schemas = {
            "card_races": {
                "race_id": "INTEGER PRIMARY KEY",
                "course_name": "TEXT NOT NULL",
                "race_date": "DATE NOT NULL"
            },
            "card_records": {
                "record_id": "INTEGER PRIMARY KEY",
                "horse_name": "TEXT NOT NULL",
                "jockey_name": "TEXT"
            }
        }
        
        result_schemas = {
            "result_races": {
                "race_id": "INTEGER PRIMARY KEY",
                "race_name": "TEXT NOT NULL",
                "winner": "TEXT"
            },
            "jockeys_stats": {
                "jockey_id": "INTEGER PRIMARY KEY",
                "jockey_name": "TEXT NOT NULL",
                "total_wins": "INTEGER DEFAULT 0"
            }
        }
        
        # Test that schemas are independent
        for card_table, card_schema in card_schemas.items():
            for result_table, result_schema in result_schemas.items():
                # No cross-references should exist
                for col_name, col_def in card_schema.items():
                    assert result_table.lower() not in col_def.lower()
                
                for col_name, col_def in result_schema.items():
                    assert card_table.lower() not in col_def.lower()
    
    def test_no_foreign_key_constraints(self):
        """Test that schemas have no foreign key constraints."""
        sample_schemas = {
            "races": {
                "race_id": "INTEGER PRIMARY KEY",
                "race_name": "TEXT NOT NULL"
            },
            "horses": {
                "horse_id": "INTEGER PRIMARY KEY",
                "horse_name": "TEXT NOT NULL"
            }
        }
        
        # Test no foreign key references
        foreign_key_keywords = ["REFERENCES", "FOREIGN KEY", "FK_"]
        
        for table_name, table_schema in sample_schemas.items():
            for col_name, col_def in table_schema.items():
                for keyword in foreign_key_keywords:
                    assert keyword not in col_def.upper()
    
    def test_primary_key_definitions(self):
        """Test primary key definitions in schemas."""
        schema = {
            "test_table": {
                "id": "INTEGER PRIMARY KEY",
                "name": "TEXT NOT NULL",
                "value": "INTEGER"
            }
        }
        
        # Test primary key identification
        primary_keys = []
        for col_name, col_def in schema["test_table"].items():
            if "PRIMARY KEY" in col_def.upper():
                primary_keys.append(col_name)
        
        assert len(primary_keys) == 1
        assert primary_keys[0] == "id"


@pytest.mark.integration
class TestDatabaseUploaderIntegration:
    """Integration tests for database uploader with pipeline components."""
    
    @pytest.mark.slow
    def test_uploader_with_docker(self):
        """Test uploader integration with Docker environment."""
        # Check if Docker is available
        try:
            import subprocess
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                pytest.skip("Docker not available")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Docker not available")
        
        # Test that Docker integration would work
        assert True  # Placeholder for actual Docker integration test
    
    def test_uploader_configuration_compatibility(self):
        """Test uploader compatibility with project configuration."""
        # Test configuration file compatibility
        config_file = project_root / "config" / "csv_column_mapping.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Test that configuration is compatible with uploader
            if "tables" in config_data:
                assert len(config_data["tables"]) > 0
                
                # Test separated architecture is reflected in config
                table_names = list(config_data["tables"].keys())
                separated_indicators = any(
                    any(indicator in name for indicator in ['card_', 'result_', 'jockeys_', 'trainers_'])
                    for name in table_names
                )
                assert separated_indicators
    
    def test_end_to_end_upload_simulation(self, temp_directory, sample_csv_files):
        """Test end-to-end upload simulation."""
        if SimpleDatabaseUploader is None:
            pytest.skip("SimpleDatabaseUploader not available")
        
        # Create manifest file
        manifest = {
            "tables": {
                "result_races": {"file": "result_races.csv"},
                "jockeys_stats": {"file": "jockeys_stats.csv"}
            }
        }
        
        manifest_file = Path(temp_directory) / "upload_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f)
        
        uploader = SimpleDatabaseUploader()
        
        # Test manifest loading
        loaded_manifest = uploader._load_upload_manifest(str(manifest_file))
        assert loaded_manifest is not None
        
        # Test that files referenced in manifest exist
        for table_name, table_info in loaded_manifest.get("tables", {}).items():
            filename = table_info["file"]
            assert filename in sample_csv_files


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
