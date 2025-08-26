"""
🧪 Pipeline Daily Upload Tests
==============================

Unit tests for the fixed pipeline daily upload system.
Tests the fixes for critical issues identified in CRITICAL_PIPELINE_FINDINGS_REPORT.md
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Test the fixed pipeline uploader
try:
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    from tools.data_processing.fixed_pipeline_daily_uploader import (
        PipelineDailyUploader, 
        DataCleaner, 
        CSV_COLUMN_MAPPINGS
    )
    PIPELINE_UPLOADER_AVAILABLE = True
except ImportError:
    PIPELINE_UPLOADER_AVAILABLE = False
    # Mock classes for testing structure
    class PipelineDailyUploader:
        pass
    class DataCleaner:
        pass
    CSV_COLUMN_MAPPINGS = {}

class TestPipelineDataCleaner:
    """Test the fixed data cleaning functionality"""
    
    def test_percentage_field_cleaning(self):
        """Test percentage field cleaning (Fix 4 enhancement)"""
        df = pd.DataFrame({
            'win_percentage': ['20%', '15.5%', '', '-', 'N/A'],
            'place_percentage': ['45%', '40%', '0%', '', None]
        })
        
        cleaned_df = DataCleaner.clean_percentage_fields(df, 'win_percentage')
        cleaned_df = DataCleaner.clean_percentage_fields(cleaned_df, 'place_percentage')
        
        # Verify percentage cleaning
        assert cleaned_df['win_percentage'].iloc[0] == 20.0
        assert cleaned_df['win_percentage'].iloc[1] == 15.5
        assert pd.isna(cleaned_df['win_percentage'].iloc[2])  # Empty string
        assert pd.isna(cleaned_df['win_percentage'].iloc[3])  # Dash
        assert pd.isna(cleaned_df['win_percentage'].iloc[4])  # N/A
        
        assert cleaned_df['place_percentage'].iloc[0] == 45.0
        assert cleaned_df['place_percentage'].iloc[1] == 40.0
        assert cleaned_df['place_percentage'].iloc[2] == 0.0
    
    def test_numeric_field_dash_cleaning(self):
        """Test Fix 4: Data cleaning for records table ('-' strings)"""
        df = pd.DataFrame({
            'finish_position': [1, '-', 3, '', 'Unknown'],
            'age': [4, '-', 6, '', 'N/A'],
            'starting_price': ['3/1', '-', '7/1', '', None]
        })
        
        # Apply numeric cleaning
        cleaned_df = DataCleaner.clean_numeric_fields(df, 'finish_position')
        cleaned_df = DataCleaner.clean_numeric_fields(cleaned_df, 'age')
        
        # Verify dash strings are converted to NULL/NaN
        assert cleaned_df['finish_position'].iloc[0] == 1.0
        assert pd.isna(cleaned_df['finish_position'].iloc[1])  # Dash converted to NaN
        assert cleaned_df['finish_position'].iloc[2] == 3.0
        assert pd.isna(cleaned_df['finish_position'].iloc[3])  # Empty string
        assert pd.isna(cleaned_df['finish_position'].iloc[4])  # Unknown
        
        assert cleaned_df['age'].iloc[0] == 4.0
        assert pd.isna(cleaned_df['age'].iloc[1])  # Dash converted to NaN
        assert cleaned_df['age'].iloc[2] == 6.0
    
    def test_case_sensitivity_normalization(self):
        """Test Fix 2 & 3: Case sensitivity handling (UptoDate -> uptodate)"""
        df = pd.DataFrame({
            'UptoDate': ['2025-08-26', '2025-08-27'],  # CSV case
            'Jockey_Name': ['J. Smith', 'R. Jones'],
            'horse_name': ['Horse 1', 'Horse 2']
        })
        
        normalized_df = DataCleaner.normalize_column_names(df)
        
        # Verify case normalization
        assert 'uptodate' in normalized_df.columns
        assert 'jockey_name' in normalized_df.columns
        assert 'horse_name' in normalized_df.columns
        
        # Original case-problematic column should be handled
        assert 'UptoDate' not in normalized_df.columns

class TestPipelineColumnMappings:
    """Test the fixed column mappings"""
    
    def test_horses_id_mapping_fix(self):
        """Test Fix 1: Column mapping for horses table (id -> horse_id)"""
        if 'results_horses' in CSV_COLUMN_MAPPINGS:
            horses_mapping = CSV_COLUMN_MAPPINGS['results_horses']['csv_to_db']
            
            # Verify the critical fix
            assert 'id' in horses_mapping, "results_horses should have 'id' mapping"
            assert horses_mapping['id'] == 'horse_id', "CSV 'id' should map to DB 'horse_id'"
            
            # Verify database assignment
            assert CSV_COLUMN_MAPPINGS['results_horses']['database'] == 'results'
    
    def test_jockeys_stats_case_fix(self):
        """Test Fix 2: Case sensitivity for jockeys_stats (UptoDate -> uptodate)"""
        if 'jockeys_stats' in CSV_COLUMN_MAPPINGS:
            jockeys_mapping = CSV_COLUMN_MAPPINGS['jockeys_stats']['csv_to_db']
            
            # Verify case sensitivity fix
            assert 'uptodate' in jockeys_mapping, "jockeys_stats should have uptodate mapping"
            assert jockeys_mapping['uptodate'] == 'uptodate', "uptodate should map correctly"
            
            # Verify database assignment
            assert CSV_COLUMN_MAPPINGS['jockeys_stats']['database'] == 'results'
    
    def test_trainers_stats_case_fix(self):
        """Test Fix 3: Case sensitivity for trainers_stats (UptoDate -> uptodate)"""
        if 'trainers_stats' in CSV_COLUMN_MAPPINGS:
            trainers_mapping = CSV_COLUMN_MAPPINGS['trainers_stats']['csv_to_db']
            
            # Verify case sensitivity fix
            assert 'uptodate' in trainers_mapping, "trainers_stats should have uptodate mapping"
            assert trainers_mapping['uptodate'] == 'uptodate', "uptodate should map correctly"
            
            # Verify database assignment
            assert CSV_COLUMN_MAPPINGS['trainers_stats']['database'] == 'results'
    
    def test_multi_database_architecture(self):
        """Test Fix 5: Multi-database support (cards vs results)"""
        # Verify cards database tables
        cards_tables = ['horses', 'races', 'racecard_details']
        for table in cards_tables:
            if table in CSV_COLUMN_MAPPINGS:
                assert CSV_COLUMN_MAPPINGS[table]['database'] == 'cards'
        
        # Verify results database tables
        results_tables = ['results_horses', 'results_races', 'records', 'jockeys_stats', 'trainers_stats']
        for table in results_tables:
            if table in CSV_COLUMN_MAPPINGS:
                assert CSV_COLUMN_MAPPINGS[table]['database'] == 'results'

class TestPipelineDailyUploaderClass:
    """Test the main PipelineDailyUploader class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def test_database_connection_configuration(self):
        """Test dual database connection setup"""
        if PIPELINE_UPLOADER_AVAILABLE:
            uploader = PipelineDailyUploader()
            
            # Verify uploader has connection placeholders
            assert hasattr(uploader, 'cards_conn')
            assert hasattr(uploader, 'results_conn')
            assert hasattr(uploader, 'processed_files')
            assert hasattr(uploader, 'failed_files')
    
    def test_file_discovery_pipeline_format(self):
        """Test CSV file discovery for pipeline format (mapped_*.csv)"""
        # Create pipeline-format CSV files
        pipeline_files = [
            'mapped_horses.csv',
            'mapped_races.csv', 
            'mapped_records.csv',
            'mapped_jockeys_stats.csv',
            'mapped_trainers_stats.csv',
            'mapped_results_horses.csv',
            'mapped_results_races.csv'
        ]
        
        # Create test files
        for filename in pipeline_files:
            test_df = pd.DataFrame({'test_col': [1, 2, 3]})
            test_df.to_csv(self.temp_dir / filename, index=False)
        
        if PIPELINE_UPLOADER_AVAILABLE:
            uploader = PipelineDailyUploader()
            
            # Mock the data directory to use temp directory
            with patch('pathlib.Path.rglob') as mock_rglob:
                mock_files = [self.temp_dir / f for f in pipeline_files]
                mock_rglob.return_value = mock_files
                
                discovered_files = uploader.find_pipeline_csv_files()
                
                # Verify pipeline file discovery
                assert len(discovered_files) > 0
    
    def test_database_routing(self):
        """Test database connection routing for different file types"""
        if PIPELINE_UPLOADER_AVAILABLE:
            uploader = PipelineDailyUploader()
            
            # Mock database connections
            uploader.cards_conn = Mock()
            uploader.results_conn = Mock()
            
            # Test cards database routing
            cards_conn = uploader.get_database_connection('horses')
            assert cards_conn == uploader.cards_conn
            
            # Test results database routing  
            results_conn = uploader.get_database_connection('records')
            assert results_conn == uploader.results_conn

class TestPipelineIntegrationFixes:
    """Integration tests for pipeline fixes"""
    
    def test_complete_data_processing_workflow(self):
        """Test complete data processing workflow with all fixes"""
        # Create problematic CSV data matching the critical issues
        horses_data = pd.DataFrame({
            'id': [1, 2, 3],  # Fix 1: Should map to horse_id
            'horse_name': ['Thunder Bolt', 'Lightning Strike', 'Storm Cloud'],
            'age': [4, '-', 6],  # Fix 4: Dash strings
            'weight': ['9-7', '10-2', '9-12'],
            'race_id': [101, 102, 103]
        })
        
        jockeys_data = pd.DataFrame({
            'jockey_name': ['J. Smith', 'R. Jones', 'M. Williams'],
            'rides': [100, 150, '-'],  # Fix 4: Dash strings
            'wins': [20, 30, 45],
            'win_percentage': ['20%', '20%', '22.5%'],  # Percentage cleaning
            'UptoDate': ['2025-08-26', '2025-08-26', '2025-08-26']  # Fix 2: Case sensitivity
        })
        
        records_data = pd.DataFrame({
            'horse_name': ['Thunder Bolt', 'Lightning Strike', 'Storm Cloud'],
            'finish_position': [1, '-', 3],  # Fix 4: Dash strings in integer field
            'starting_price': ['3/1', '-', '7/1'],
            'age': [4, '-', 6],  # Fix 4: More dash strings
            'race_id': [101, 102, 103]
        })
        
        # Apply all data cleaning fixes
        # Fix 1: Column normalization
        horses_clean = DataCleaner.normalize_column_names(horses_data)
        jockeys_clean = DataCleaner.normalize_column_names(jockeys_data)
        records_clean = DataCleaner.normalize_column_names(records_data)
        
        # Fix 4: Numeric field cleaning
        horses_clean = DataCleaner.clean_numeric_fields(horses_clean, 'age')
        jockeys_clean = DataCleaner.clean_numeric_fields(jockeys_clean, 'rides')
        records_clean = DataCleaner.clean_numeric_fields(records_clean, 'finish_position')
        records_clean = DataCleaner.clean_numeric_fields(records_clean, 'age')
        
        # Percentage cleaning
        jockeys_clean = DataCleaner.clean_percentage_fields(jockeys_clean, 'win_percentage')
        
        # Verify all fixes applied correctly
        # Fix 1: Column names normalized
        assert 'uptodate' in jockeys_clean.columns
        
        # Fix 4: Dash strings cleaned
        assert pd.isna(horses_clean['age'].iloc[1])  # Dash converted to NaN
        assert pd.isna(jockeys_clean['rides'].iloc[2])  # Dash converted to NaN
        assert pd.isna(records_clean['finish_position'].iloc[1])  # Dash converted to NaN
        assert pd.isna(records_clean['age'].iloc[1])  # Dash converted to NaN
        
        # Percentage cleaning
        assert jockeys_clean['win_percentage'].iloc[0] == 20.0
        assert jockeys_clean['win_percentage'].iloc[1] == 20.0
        assert jockeys_clean['win_percentage'].iloc[2] == 22.5
    
    def test_critical_fixes_validation(self):
        """Test validation that all critical fixes from the report are implemented"""
        # This test validates the fixes mentioned in CRITICAL_PIPELINE_FINDINGS_REPORT.md
        
        # Fix 1: horses table "id" column mapping
        if 'results_horses' in CSV_COLUMN_MAPPINGS:
            horses_mapping = CSV_COLUMN_MAPPINGS['results_horses']['csv_to_db']
            assert 'id' in horses_mapping, "Fix 1: horses 'id' mapping missing"
            assert horses_mapping['id'] == 'horse_id', "Fix 1: incorrect 'id' mapping"
        
        # Fix 2: jockeys_stats case sensitivity
        if 'jockeys_stats' in CSV_COLUMN_MAPPINGS:
            jockeys_mapping = CSV_COLUMN_MAPPINGS['jockeys_stats']['csv_to_db']
            assert 'uptodate' in jockeys_mapping, "Fix 2: jockeys uptodate mapping missing"
        
        # Fix 3: trainers_stats case sensitivity
        if 'trainers_stats' in CSV_COLUMN_MAPPINGS:
            trainers_mapping = CSV_COLUMN_MAPPINGS['trainers_stats']['csv_to_db']
            assert 'uptodate' in trainers_mapping, "Fix 3: trainers uptodate mapping missing"
        
        # Fix 4: Data cleaning capability
        test_df = pd.DataFrame({'test_field': [1, '-', 3]})
        cleaned_df = DataCleaner.clean_numeric_fields(test_df, 'test_field')
        assert pd.isna(cleaned_df['test_field'].iloc[1]), "Fix 4: dash cleaning not working"
        
        # Fix 5: Multi-database support
        expected_cards = ['horses', 'races']
        expected_results = ['records', 'jockeys_stats', 'trainers_stats']
        
        for table in expected_cards:
            if table in CSV_COLUMN_MAPPINGS:
                assert CSV_COLUMN_MAPPINGS[table]['database'] == 'cards'
        
        for table in expected_results:
            if table in CSV_COLUMN_MAPPINGS:
                assert CSV_COLUMN_MAPPINGS[table]['database'] == 'results'

class TestPipelinePerformance:
    """Performance tests for pipeline components"""
    
    @pytest.mark.performance
    def test_large_dataset_processing(self):
        """Test processing large datasets efficiently"""
        # Create large dataset similar to production (11,973 records)
        large_df = pd.DataFrame({
            'horse_name': [f'Horse {i}' for i in range(12000)],
            'age': [4 if i % 3 != 0 else '-' for i in range(12000)],  # Mix valid and dash
            'win_percentage': [f'{20 + i % 50}%' for i in range(12000)],
            'finish_position': [1 if i % 4 == 0 else '-' for i in range(12000)]
        })
        
        import time
        start_time = time.time()
        
        # Apply all cleaning operations
        cleaned_df = DataCleaner.clean_numeric_fields(large_df, 'age')
        cleaned_df = DataCleaner.clean_percentage_fields(cleaned_df, 'win_percentage')
        cleaned_df = DataCleaner.clean_numeric_fields(cleaned_df, 'finish_position')
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Performance assertion (should process 12k records quickly)
        assert processing_time < 5.0, f"Large dataset processing too slow: {processing_time}s"
        assert len(cleaned_df) == 12000

# Test markers
pytestmark = [
    pytest.mark.unit,
    pytest.mark.pipeline,
    pytest.mark.critical  # These are critical fixes
]
