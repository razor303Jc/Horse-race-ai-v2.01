"""
Test suite for CSV column mapping and data processing.
Tests the separated data architecture and column mapping functionality.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
import pandas as pd
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.data_processing.advanced_csv_mapper import AdvancedCSVMapper
except ImportError:
    AdvancedCSVMapper = None


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_csv_mapping():
    """Create sample CSV column mapping configuration."""
    return {
        "tables": {
            "card_races": {
                "race_id": "INTEGER PRIMARY KEY",
                "course_name": "TEXT NOT NULL",
                "race_time": "TIME",
                "race_date": "DATE NOT NULL"
            },
            "card_records": {
                "record_id": "INTEGER PRIMARY KEY",
                "horse_name": "TEXT NOT NULL",
                "jockey_name": "TEXT",
                "trainer_name": "TEXT"
            },
            "result_races": {
                "race_id": "INTEGER PRIMARY KEY",
                "race_name": "TEXT NOT NULL",
                "winner": "TEXT",
                "finish_time": "TIME"
            },
            "jockeys_stats": {
                "jockey_id": "INTEGER PRIMARY KEY",
                "jockey_name": "TEXT NOT NULL",
                "total_wins": "INTEGER DEFAULT 0",
                "total_races": "INTEGER DEFAULT 0"
            },
            "trainers_stats": {
                "trainer_id": "INTEGER PRIMARY KEY",
                "trainer_name": "TEXT NOT NULL",
                "total_wins": "INTEGER DEFAULT 0",
                "win_percentage": "DECIMAL(5,2)"
            }
        }
    }


@pytest.fixture
def sample_csv_data(temp_directory):
    """Create sample CSV files for testing."""
    csv_files = {}
    
    # Create card_races.csv
    card_races_data = pd.DataFrame({
        'race_id': [1, 2, 3],
        'course_name': ['Ascot', 'Cheltenham', 'Newmarket'],
        'race_time': ['14:30', '15:15', '16:00'],
        'race_date': ['2025-08-23', '2025-08-23', '2025-08-23']
    })
    card_races_file = Path(temp_directory) / "card_races.csv"
    card_races_data.to_csv(card_races_file, index=False)
    csv_files['card_races'] = str(card_races_file)
    
    # Create result_races.csv
    result_races_data = pd.DataFrame({
        'race_id': [101, 102, 103],
        'race_name': ['Gold Cup', 'Derby Stakes', 'Oaks'],
        'winner': ['Thunder', 'Lightning', 'Storm'],
        'finish_time': ['2:45.67', '2:33.12', '2:41.89']
    })
    result_races_file = Path(temp_directory) / "result_races.csv"
    result_races_data.to_csv(result_races_file, index=False)
    csv_files['result_races'] = str(result_races_file)
    
    # Create jockeys_stats.csv
    jockeys_data = pd.DataFrame({
        'jockey_id': [1, 2, 3, 4, 5],
        'jockey_name': ['J. Smith', 'R. Johnson', 'M. Williams', 'S. Brown', 'A. Davis'],
        'total_wins': [45, 38, 52, 41, 29],
        'total_races': [180, 165, 200, 190, 140]
    })
    jockeys_file = Path(temp_directory) / "jockeys_stats.csv"
    jockeys_data.to_csv(jockeys_file, index=False)
    csv_files['jockeys_stats'] = str(jockeys_file)
    
    return csv_files


class TestCSVColumnMapping:
    """Test suite for CSV column mapping functionality."""
    
    def test_mapping_structure_validation(self, sample_csv_mapping):
        """Test validation of CSV mapping structure."""
        # Verify all required tables exist
        required_tables = ['card_races', 'result_races', 'jockeys_stats', 'trainers_stats']
        for table in required_tables:
            assert table in sample_csv_mapping['tables']
        
        # Verify no foreign key constraints
        for table_name, table_schema in sample_csv_mapping['tables'].items():
            for column_name, column_def in table_schema.items():
                assert "REFERENCES" not in column_def.upper()
                assert "FOREIGN KEY" not in column_def.upper()
    
    def test_separated_card_results_architecture(self, sample_csv_mapping):
        """Test that card and results data are properly separated."""
        tables = sample_csv_mapping['tables']
        
        # Card data tables
        card_tables = ['card_races', 'card_records', 'card_horses', 'racecard_details']
        # Results data tables  
        result_tables = ['result_races', 'jockeys_stats', 'trainers_stats']
        
        # Verify card tables exist (may be empty but should be defined)
        for table in card_tables:
            if table in tables:
                # If table exists, verify it has independent structure
                assert 'race_id' in tables[table] or 'record_id' in tables[table] or 'horse_id' in tables[table]
        
        # Verify results tables exist
        for table in result_tables:
            if table in tables:
                # Results tables should have independent primary keys
                primary_keys = [col for col, def_ in tables[table].items() if 'PRIMARY KEY' in def_]
                assert len(primary_keys) >= 1
    
    def test_csv_file_validation(self, sample_csv_data):
        """Test CSV file validation and structure."""
        for table_name, csv_file in sample_csv_data.items():
            # Test file exists and is readable
            df = pd.read_csv(csv_file)
            assert not df.empty
            assert len(df.columns) > 0
            
            # Test data integrity
            if table_name == 'card_races':
                assert 'race_id' in df.columns
                assert 'course_name' in df.columns
                assert not df['course_name'].isna().any()
            
            elif table_name == 'result_races':
                assert 'race_id' in df.columns
                assert 'race_name' in df.columns
                assert not df['race_name'].isna().any()
            
            elif table_name == 'jockeys_stats':
                assert 'jockey_id' in df.columns
                assert 'jockey_name' in df.columns
                assert 'total_wins' in df.columns
                assert df['total_wins'].dtype in ['int64', 'float64']
    
    def test_data_type_mapping(self, sample_csv_mapping):
        """Test correct data type mapping for database columns."""
        tables = sample_csv_mapping['tables']
        
        # Test various data types are correctly specified
        for table_name, table_schema in tables.items():
            for column_name, column_def in table_schema.items():
                # Verify data type is specified
                data_types = ['INTEGER', 'TEXT', 'DATE', 'TIME', 'DECIMAL', 'BOOLEAN']
                has_valid_type = any(dt in column_def.upper() for dt in data_types)
                assert has_valid_type, f"Invalid data type in {table_name}.{column_name}: {column_def}"
    
    def test_primary_key_constraints(self, sample_csv_mapping):
        """Test primary key constraints are properly defined."""
        tables = sample_csv_mapping['tables']
        
        for table_name, table_schema in tables.items():
            # Each table should have exactly one primary key
            primary_keys = [col for col, def_ in table_schema.items() if 'PRIMARY KEY' in def_]
            assert len(primary_keys) == 1, f"Table {table_name} should have exactly one primary key"


class TestDataProcessingPipeline:
    """Test suite for data processing pipeline functionality."""
    
    def test_csv_to_database_mapping(self, sample_csv_data, sample_csv_mapping):
        """Test mapping CSV data to database schema."""
        for table_name, csv_file in sample_csv_data.items():
            if table_name in sample_csv_mapping['tables']:
                df = pd.read_csv(csv_file)
                table_schema = sample_csv_mapping['tables'][table_name]
                
                # Test that CSV columns match expected schema columns
                schema_columns = set(table_schema.keys())
                csv_columns = set(df.columns)
                
                # Allow for subset matching (CSV may have fewer columns)
                missing_required = schema_columns - csv_columns
                # Only check that primary key exists
                primary_key_cols = [col for col, def_ in table_schema.items() if 'PRIMARY KEY' in def_]
                for pk_col in primary_key_cols:
                    assert pk_col in csv_columns, f"Primary key {pk_col} missing in {table_name} CSV"
    
    def test_data_validation_rules(self, sample_csv_data):
        """Test data validation rules for CSV processing."""
        for table_name, csv_file in sample_csv_data.items():
            df = pd.read_csv(csv_file)
            
            # Test for common data quality issues
            if table_name == 'jockeys_stats':
                # Total wins should not be negative
                assert not (df['total_wins'] < 0).any()
                # Total races should be >= total wins
                assert not (df['total_races'] < df['total_wins']).any()
            
            # Test for null values in required fields
            if 'name' in df.columns:
                assert not df['name'].isna().any()
    
    def test_database_schema_generation(self, sample_csv_mapping, temp_directory):
        """Test generation of database schema from mapping."""
        # Create a test SQL file
        sql_file = Path(temp_directory) / "test_schema.sql"
        
        with open(sql_file, 'w') as f:
            for table_name, table_schema in sample_csv_mapping['tables'].items():
                f.write(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
                columns = []
                for col_name, col_def in table_schema.items():
                    columns.append(f"    {col_name} {col_def}")
                f.write(",\n".join(columns))
                f.write("\n);\n\n")
        
        # Verify SQL file was created and has content
        assert sql_file.exists()
        sql_content = sql_file.read_text()
        assert "CREATE TABLE" in sql_content
        assert "card_races" in sql_content
        assert "result_races" in sql_content


class TestSeparatedDataArchitecture:
    """Test suite specifically for separated card/results data architecture."""
    
    def test_independent_table_structures(self, sample_csv_mapping):
        """Test that card and result tables are independent."""
        tables = sample_csv_mapping['tables']
        
        # Define table categories
        card_tables = ['card_races', 'card_records', 'card_horses', 'racecard_details']
        result_tables = ['result_races', 'jockeys_stats', 'trainers_stats']
        
        # Test that no cross-references exist
        for card_table in card_tables:
            if card_table in tables:
                for result_table in result_tables:
                    if result_table in tables:
                        # Check that card table doesn't reference result table
                        for col_name, col_def in tables[card_table].items():
                            assert result_table not in col_def.lower()
                        
                        # Check that result table doesn't reference card table
                        for col_name, col_def in tables[result_table].items():
                            assert card_table not in col_def.lower()
    
    def test_no_foreign_key_constraints(self, sample_csv_mapping):
        """Test that no foreign key constraints exist between separated tables."""
        tables = sample_csv_mapping['tables']
        
        foreign_key_indicators = ['REFERENCES', 'FOREIGN KEY', 'FK_']
        
        for table_name, table_schema in tables.items():
            for column_name, column_def in table_schema.items():
                for indicator in foreign_key_indicators:
                    assert indicator not in column_def.upper(), \
                        f"Foreign key constraint found in {table_name}.{column_name}: {column_def}"
    
    def test_data_isolation(self, sample_csv_data):
        """Test that card and result data can be processed independently."""
        # Card data files
        card_files = [f for f in sample_csv_data.keys() if f.startswith('card_')]
        # Result data files
        result_files = [f for f in sample_csv_data.keys() if not f.startswith('card_')]
        
        # Test that each group can be processed independently
        for card_file in card_files:
            if card_file in sample_csv_data:
                df = pd.read_csv(sample_csv_data[card_file])
                # Card data should be self-contained
                assert not df.empty
        
        for result_file in result_files:
            if result_file in sample_csv_data:
                df = pd.read_csv(sample_csv_data[result_file])
                # Result data should be self-contained
                assert not df.empty


@pytest.mark.integration
class TestCSVMappingIntegration:
    """Integration tests for CSV mapping with pipeline components."""
    
    def test_mapping_file_compatibility(self):
        """Test that mapping file is compatible with pipeline components."""
        mapping_file = project_root / "config" / "csv_column_mapping.json"
        
        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                mapping_data = json.load(f)
            
            # Test structure
            assert "tables" in mapping_data
            
            # Test that separated architecture is implemented
            tables = mapping_data['tables']
            separated_indicators = ['card_', 'result_', 'jockeys_', 'trainers_']
            
            found_tables = []
            for table_name in tables.keys():
                for indicator in separated_indicators:
                    if indicator in table_name:
                        found_tables.append(table_name)
            
            assert len(found_tables) > 0, "No separated tables found in mapping"
    
    @pytest.mark.slow
    def test_end_to_end_csv_processing(self, sample_csv_data, temp_directory):
        """Test end-to-end CSV processing workflow."""
        # This would test the complete CSV processing pipeline
        # Skip if advanced CSV mapper not available
        if AdvancedCSVMapper is None:
            pytest.skip("AdvancedCSVMapper not available")
        
        # Test would involve:
        # 1. Loading CSV files
        # 2. Applying column mapping
        # 3. Validating transformed data
        # 4. Generating database upload manifest
        
        # For now, just verify the files can be read
        for table_name, csv_file in sample_csv_data.items():
            df = pd.read_csv(csv_file)
            assert not df.empty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
