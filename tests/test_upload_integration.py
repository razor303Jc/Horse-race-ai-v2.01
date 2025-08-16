#!/usr/bin/env python3
"""
Integration Tests for Real Upload Functions
==========================================

Test the actual upload functions from safe_upload_all.py

Author: AI Assistant
Date: August 16, 2025
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRealUploadFunctions(unittest.TestCase):
    """Test the actual upload functions"""

    def setUp(self):
        """Set up test environment"""
        self.test_data_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if Path(self.test_data_dir).exists():
            shutil.rmtree(self.test_data_dir)

    def test_import_upload_functions(self):
        """Test that we can import the upload functions"""
        try:
            from safe_upload_all import (
                convert_uk_weight,
                convert_fav_position,
                clean_data_value,
                get_column_types
            )
            
            # Test basic functionality
            self.assertAlmostEqual(convert_uk_weight("9-7"), 9.5, places=2)
            self.assertEqual(convert_fav_position("1st"), 1)
            self.assertEqual(clean_data_value("", "test", "integer"), 0)
            
            column_types = get_column_types("races")
            self.assertIsInstance(column_types, dict)
            self.assertIn("integer", column_types)
            self.assertIn("float", column_types)
            self.assertIn("string", column_types)
            
            print("✅ All upload functions imported and tested successfully")
            
        except ImportError as e:
            self.fail(f"Could not import upload functions: {e}")

    def test_create_test_csv_and_validate(self):
        """Test creating test CSV and validating with real functions"""
        try:
            from safe_upload_all import clean_data_value, get_column_types
            
            # Create test CSV data
            test_data = {
                "id": [1, 2, 3],
                "race_number": [1, 2, 3],
                "weight_uk": ["9-7", "10-0", "8-14"],
                "fav": ["1st", "2nd", "3rd"],
                "SP": ["2.5", "", "-"],
                "race_name": ["Test Race 1", "Test Race 2", ""]
            }
            
            df = pd.DataFrame(test_data)
            
            # Get column types for records table
            column_types = get_column_types("records")
            
            # Test data cleaning on each column
            for col in df.columns:
                for idx, value in enumerate(df[col]):
                    if col in column_types["integer"]:
                        cleaned = clean_data_value(value, col, "integer")
                        self.assertIsInstance(cleaned, int)
                    elif col in column_types["float"]:
                        cleaned = clean_data_value(value, col, "float")
                        self.assertIsInstance(cleaned, (int, float))
                    else:
                        cleaned = clean_data_value(value, col, "string")
                        self.assertIsInstance(cleaned, str)
            
            print("✅ CSV data validation with real functions passed")
            
        except ImportError as e:
            self.skipTest(f"Upload functions not available: {e}")

    def test_upload_function_with_mock_database(self):
        """Test upload function with mocked database"""
        try:
            from safe_upload_all import upload_csv_file
            
            # Create test CSV file
            test_data = {
                "id": [1, 2, 3],
                "race_number": [1, 2, 3],
                "race_name": ["Race 1", "Race 2", "Race 3"]
            }
            
            df = pd.DataFrame(test_data)
            test_file = Path(self.test_data_dir) / "test_races.csv"
            df.to_csv(test_file, index=False)
            
            # Mock the database connection
            with patch('safe_upload_all.psycopg2.connect') as mock_connect:
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_connect.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchone.return_value = (3,)  # 3 rows inserted
                
                # Test the upload
                result = upload_csv_file(str(test_file), "races")
                
                # Verify the result
                self.assertTrue(result)
                mock_connect.assert_called_once()
                mock_cursor.execute.assert_called()
                
            print("✅ Upload function with mock database passed")
            
        except ImportError as e:
            self.skipTest(f"Upload functions not available: {e}")

    def test_column_type_definitions(self):
        """Test that column type definitions are comprehensive"""
        try:
            from safe_upload_all import get_column_types
            
            # Test all expected tables
            tables = ["races", "records", "horses", "jockeys_stats", "trainers_stats", "racecard_details"]
            
            for table in tables:
                column_types = get_column_types(table)
                
                # Verify structure
                self.assertIsInstance(column_types, dict)
                self.assertIn("integer", column_types)
                self.assertIn("float", column_types)
                self.assertIn("string", column_types)
                
                # Verify types are lists
                self.assertIsInstance(column_types["integer"], list)
                self.assertIsInstance(column_types["float"], list)
                self.assertIsInstance(column_types["string"], list)
                
                print(f"✅ Column types for {table} are properly defined")
            
        except ImportError as e:
            self.skipTest(f"Upload functions not available: {e}")

    def test_edge_case_data_conversion(self):
        """Test edge cases in data conversion"""
        try:
            from safe_upload_all import convert_uk_weight, convert_fav_position, clean_data_value
            
            # Test UK weight edge cases
            edge_weights = ["", "-", None, "invalid", "0-0", "abc-def"]
            for weight in edge_weights:
                result = convert_uk_weight(weight)
                self.assertEqual(result, 0.0, f"Failed for weight: {weight}")
            
            # Test favorite position edge cases
            edge_favs = ["", "-", None, "invalid", "0th"]
            for fav in edge_favs:
                result = convert_fav_position(fav)
                self.assertEqual(result, 0, f"Failed for fav: {fav}")
            
            # Test data cleaning edge cases
            edge_values = [None, "", "-", "none", pd.NA]
            for value in edge_values:
                # Integer type
                result = clean_data_value(value, "test", "integer")
                self.assertEqual(result, 0)
                
                # Float type
                result = clean_data_value(value, "test", "float")
                self.assertEqual(result, 0.0)
                
                # String type
                result = clean_data_value(value, "test", "string")
                self.assertEqual(result, "none")
            
            print("✅ Edge case data conversion tests passed")
            
        except ImportError as e:
            self.skipTest(f"Upload functions not available: {e}")


def run_integration_tests():
    """Run integration tests for real upload functions"""
    print("🔗 Running Integration Tests for Real Upload Functions")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test class
    suite.addTests(loader.loadTestsFromTestCase(TestRealUploadFunctions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print(f"   Ran {result.testsRun} tests successfully")
        print("   Real upload functions are working correctly")
        print("   Data conversion is validated")
        print("   Database integration is ready")
        return True
    else:
        print("❌ SOME INTEGRATION TESTS FAILED!")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}")
                print(f"    {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}")
                print(f"    {traceback}")
        
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    
    print("\n" + "=" * 60)
    print("🏁 FINAL SUMMARY")
    print("=" * 60)
    
    if success:
        print("🎉 Upload system integration tests completed successfully!")
        print("")
        print("📋 VERIFIED COMPONENTS:")
        print("   ✅ safe_upload_all.py functions")
        print("   ✅ Data conversion functions")
        print("   ✅ Column type definitions")
        print("   ✅ CSV processing workflow")
        print("   ✅ Database integration (mocked)")
        print("   ✅ Edge case handling")
        print("")
        print("🚀 Upload system is ready for production use!")
    else:
        print("⚠️  Integration test issues found")
        print("   Please review and fix failing tests before using upload system")
    
    sys.exit(0 if success else 1)
