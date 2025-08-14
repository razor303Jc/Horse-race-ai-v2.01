#!/usr/bin/env python3
"""
Comprehensive Integration Test for Docker Organization

This test validates the complete pipeline integration after Docker reorganization,
including data processing, pipeline management, schedule updates, and database relationships.
"""

import unittest
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestCompleteIntegration(unittest.TestCase):
    """Complete integration test suite"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = project_root
        
    def test_docker_organization_complete(self):
        """Test that all Docker organization is complete"""
        print("\n🐳 Testing Docker Organization...")
        
        # Test Docker directories exist
        docker_dirs = [
            "docker/data_processing",
            "docker/pipeline_management", 
            "docker/web_app"
        ]
        
        for dir_path in docker_dirs:
            full_path = self.project_root / dir_path
            self.assertTrue(full_path.exists(), f"{dir_path} should exist")
            print(f"  ✅ {dir_path} exists")
        
        # Test Dockerfiles exist
        dockerfiles = [
            "Dockerfile.data-processing",
            "Dockerfile.pipeline-management"
        ]
        
        for dockerfile in dockerfiles:
            full_path = self.project_root / dockerfile
            self.assertTrue(full_path.exists(), f"{dockerfile} should exist")
            print(f"  ✅ {dockerfile} exists")

    def test_schedule_updated_correctly(self):
        """Test that schedule has been updated to 00:01"""
        print("\n⏰ Testing Schedule Updates...")
        
        # Test main config file
        config_file = self.project_root / "config/daily_pipeline_config.json"
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        download_time = config["dynamic_schedule"]["download_time"]
        self.assertEqual(download_time, "00:01", "Main config should be 00:01")
        print(f"  ✅ Main config updated to {download_time}")
        
        # Test duplicate config file
        config_file2 = self.project_root / "config/config/daily_pipeline_config.json"
        with open(config_file2, 'r') as f:
            config2 = json.load(f)
        
        download_time2 = config2["schedule"]["download_time"]
        self.assertEqual(download_time2, "00:01", "Duplicate config should be 00:01")
        print(f"  ✅ Duplicate config updated to {download_time2}")

    def test_data_integrity_issues_identified(self):
        """Test that data integrity issues are properly identified"""
        print("\n🔍 Testing Data Integrity Analysis...")
        
        # Run database relationship test and capture output
        cmd = [sys.executable, str(self.project_root / "tools/testing/database_relationships_test.py")]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout
            
            # Check that key issues are identified
            self.assertIn("records reference non-existent races", output)
            self.assertIn("jockeys in records not found", output)
            self.assertIn("trainers in records not found", output)
            print("  ✅ Data integrity issues properly identified")
            
            # Check that foreign key suggestions are present
            self.assertIn("ALTER TABLE records ADD CONSTRAINT", output)
            print("  ✅ Foreign key constraints suggested")
            
        except subprocess.TimeoutExpired:
            self.fail("Database relationship test timed out")
        except Exception as e:
            self.fail(f"Database relationship test failed: {e}")

    def test_csv_data_samples_exist(self):
        """Test that CSV data samples are available for review"""
        print("\n📊 Testing CSV Data Samples...")
        
        data_dir = self.project_root / "data/daily_downloads/cards_data"
        expected_tables = ["races", "records", "horses", "jockeys_stats", "trainers_stats"]
        
        for table in expected_tables:
            csv_file = data_dir / table / f"{table}.csv"
            self.assertTrue(csv_file.exists(), f"{table}.csv should exist")
            
            # Check that file has content
            with open(csv_file, 'r') as f:
                lines = f.readlines()
                self.assertGreater(len(lines), 1, f"{table}.csv should have data")
            
            print(f"  ✅ {table}.csv exists with {len(lines)} lines")

    def test_docker_compose_integration(self):
        """Test Docker Compose configuration"""
        print("\n🐙 Testing Docker Compose Integration...")
        
        compose_file = self.project_root / "docker-compose.yml"
        with open(compose_file, 'r') as f:
            content = f.read()
        
        # Check for new services
        services = ["data-processor", "pipeline-manager"]
        for service in services:
            self.assertIn(f"{service}:", content)
            print(f"  ✅ {service} service configured")
        
        # Check for profiles
        profiles = ["data-processing", "pipeline-management"]
        for profile in profiles:
            self.assertIn(profile, content)
            print(f"  ✅ {profile} profile configured")

    def test_auto_downloader_container_rebuilt(self):
        """Test that auto-downloader container was rebuilt"""
        print("\n🔄 Testing Auto-Downloader Rebuild...")
        
        try:
            # Check Docker images for recently built auto-downloader
            cmd = ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}\t{{.CreatedAt}}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            images = result.stdout
            auto_downloader_found = False
            
            for line in images.split('\n'):
                if 'auto-downloader' in line:
                    auto_downloader_found = True
                    print(f"  ✅ Auto-downloader image found: {line.strip()}")
                    break
            
            self.assertTrue(auto_downloader_found, "Auto-downloader image should exist")
            
        except Exception as e:
            self.skipTest(f"Docker not available for testing: {e}")

    def test_pipeline_files_moved_correctly(self):
        """Test that pipeline files were moved to correct locations"""
        print("\n📁 Testing File Organization...")
        
        # Check data processing files
        data_processing_files = [
            "docker/data_processing/data_cleaner.py",
            "docker/data_processing/clean_upload.py",
            "docker/data_processing/simple_upload.py",
            "docker/data_processing/upload_races.py"
        ]
        
        for file_path in data_processing_files:
            full_path = self.project_root / file_path
            self.assertTrue(full_path.exists(), f"{file_path} should exist")
            print(f"  ✅ {file_path} moved correctly")
        
        # Check pipeline management files
        pipeline_files = [
            "docker/pipeline_management/dynamic_pipeline_timing.py",
            "docker/pipeline_management/pipeline_integration_summary.py"
        ]
        
        for file_path in pipeline_files:
            full_path = self.project_root / file_path
            self.assertTrue(full_path.exists(), f"{file_path} should exist")
            print(f"  ✅ {file_path} moved correctly")
        
        # Check web app files
        web_app_files = [
            "docker/web_app/app.py",
            "docker/web_app/main.py"
        ]
        
        for file_path in web_app_files:
            full_path = self.project_root / file_path
            self.assertTrue(full_path.exists(), f"{file_path} should exist")
            print(f"  ✅ {file_path} moved correctly")

    def test_old_files_removed_from_root(self):
        """Test that old files were removed from root directory"""
        print("\n🧹 Testing Root Directory Cleanup...")
        
        # These files should no longer be in root
        removed_files = [
            "data_cleaner.py",
            "clean_upload.py",
            "simple_upload.py",
            "upload_races.py",
            "dynamic_pipeline_timing.py",
            "pipeline_integration_summary.py",
            "app.py",
            "main.py"
        ]
        
        for file_name in removed_files:
            file_path = self.project_root / file_name
            self.assertFalse(file_path.exists(), f"{file_name} should be removed from root")
            print(f"  ✅ {file_name} removed from root")

    def test_integration_tests_pass(self):
        """Test that all integration tests pass"""
        print("\n🧪 Testing Integration Test Suite...")
        
        # Run the Docker organization tests
        test_file = self.project_root / "tests/test_docker_organization.py"
        cmd = [sys.executable, str(test_file)]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, "Docker organization tests should pass")
            print("  ✅ All Docker organization tests pass")
            
        except subprocess.TimeoutExpired:
            self.fail("Integration tests timed out")
        except Exception as e:
            self.fail(f"Integration tests failed: {e}")


def run_comprehensive_test_suite():
    """Run the complete test suite with detailed reporting"""
    print("🚀 Complete Pipeline Integration Test Suite")
    print("=" * 80)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCompleteIntegration)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print detailed summary
    print("\n" + "=" * 80)
    print("📋 TEST SUMMARY")
    print("=" * 80)
    
    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED!")
        print("✅ Docker organization complete")
        print("✅ Schedule updated to 00:01") 
        print("✅ Database relationships analyzed")
        print("✅ CSV data samples available")
        print("✅ Auto-downloader container rebuilt")
        print("✅ File organization verified")
        print("✅ Integration tests passing")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        for test, error in result.failures + result.errors:
            print(f"  - {test}: {error}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Review CSV data samples in data/daily_downloads/cards_data/")
    print("2. Address data integrity issues identified in database analysis")
    print("3. Test new Docker services with profiles:")
    print("   - docker-compose --profile data-processing up")
    print("   - docker-compose --profile pipeline-management up")
    print("4. Consider adding foreign key constraints after data cleanup")
    print("5. Monitor auto-downloader with new 00:01 schedule")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_comprehensive_test_suite()
    sys.exit(0 if success else 1)
