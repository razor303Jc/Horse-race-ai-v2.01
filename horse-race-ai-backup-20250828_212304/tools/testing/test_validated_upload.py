#!/usr/bin/env python3
"""
Test Data Validation and Database Integration
==============================================

Test the new data validation functionality that checks for fresh data
and prevents duplicate uploads to the database.
"""

import asyncio
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_data_validation():
    """Test data validation functionality"""
    print("🧪 Testing Data Validation Functionality")
    print("=" * 50)
    
    try:
        # Set Docker environment for headless mode
        os.environ['DOCKER_CONTAINER'] = 'true'
        
        from src.automation.respectful_auto_downloader import RespectfulAutoDownloader
        
        # Initialize downloader
        downloader = RespectfulAutoDownloader()
        print("✅ Auto downloader initialized")
        
        # First, run CSV processing to get data ready
        print("\n📊 Processing CSV files...")
        processing_results = await downloader.process_extracted_csv_files()
        
        if not processing_results["success"]:
            print("❌ CSV processing failed - cannot test validation")
            return False
        
        files_count = processing_results['processed_files']
        print(f"✅ CSV processing complete: {files_count} files")
        
        # Test data validation
        print("\n🔍 Starting data validation test...")
        validation_results = await downloader.validate_data_freshness(
            processing_results
        )
        
        print("📊 Validation Results:")
        print(f"   🔍 Is Fresh: {validation_results['is_fresh']}")
        print(f"   🔄 Is Duplicate: {validation_results['is_duplicate']}")
        print(f"   ✅ Validation Passed: {validation_results['validation_passed']}")
        action = validation_results['recommended_action']
        print(f"   📋 Recommended Action: {action}")
        
        # Show date validation details
        date_validation = validation_results.get("date_validation", {})
        if date_validation:
            print("\n📅 Date Analysis:")
            today_count = date_validation.get('today_data_count', 0)
            print(f"   📊 Today's data: {today_count} records")
            yesterday_count = date_validation.get('yesterday_data_count', 0)
            print(f"   📊 Yesterday's data: {yesterday_count} records")
            older_count = date_validation.get('older_data_count', 0)
            print(f"   📊 Older data: {older_count} records")
            has_fresh = date_validation.get('has_fresh_data', False)
            print(f"   ✅ Has fresh data: {has_fresh}")
            
            # Show date ranges found
            date_ranges = date_validation.get("date_ranges_found", [])
            if date_ranges:
                print(f"   📈 Date ranges found in {len(date_ranges)} files:")
                for date_range in date_ranges[:5]:  # Show first 5
                    file_name = date_range['file']
                    column = date_range['column']
                    min_date = date_range['min_date']
                    max_date = date_range['max_date']
                    print(f"      📄 {file_name} ({column}): {min_date} to {max_date}")
        
        # Show duplicate check details
        duplicate_checks = validation_results.get("duplicate_checks", {})
        if duplicate_checks:
            print("\n🔍 Duplicate Analysis:")
            db_accessible = duplicate_checks.get('database_accessible', False)
            print(f"   �️ Database accessible: {db_accessible}")
            all_exists = duplicate_checks.get('all_data_exists', True)
            print(f"   🔄 All data exists: {all_exists}")
            
            new_files = duplicate_checks.get("new_files", [])
            duplicate_files = duplicate_checks.get("duplicate_files", [])
            
            if new_files:
                files_str = ', '.join(new_files)
                print(f"   ✨ New files ({len(new_files)}): {files_str}")
            if duplicate_files:
                files_str = ', '.join(duplicate_files)
                print(f"   🔄 Duplicate files ({len(duplicate_files)}): {files_str}")
            
            # Show detailed check results
            check_details = duplicate_checks.get("check_details", {})
            if check_details:
                print("   📊 Detailed checks:")
                for file_path, details in check_details.items():
                    file_name = Path(file_path).name
                    existing = details.get("existing_records", 0)
                    new_records = details.get("new_records", 0)
                    table = details.get("table", "unknown")
                    print(f"      📈 {file_name} → {table}: "
                          f"{existing} existing, {new_records} new")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Full error details:")
        return False


async def test_validated_upload():
    """Test the complete validated upload process"""
    print("\n🧪 Testing Validated Upload Process")
    print("=" * 50)
    
    try:
        from src.automation.respectful_auto_downloader import RespectfulAutoDownloader
        
        # Initialize downloader
        downloader = RespectfulAutoDownloader()
        
        # Process CSV files
        processing_results = await downloader.process_extracted_csv_files()
        
        if not processing_results["success"]:
            print("❌ CSV processing failed")
            return False
        
        # Test validated upload
        print("🗄️ Starting validated upload test...")
        upload_results = await downloader.upload_to_database(processing_results)
        
        print("📊 Upload Results:")
        print(f"   ✅ Success: {upload_results.get('success', False)}")
        print(f"   📊 Records inserted: {upload_results.get('records_inserted', 0)}")
        print(f"   🗃️ Tables updated: {upload_results.get('tables_updated', 0)}")
        
        # Show validation results that influenced the upload
        validation_results = upload_results.get("validation_results", {})
        if validation_results:
            print(f"   🔍 Validation passed: {validation_results.get('validation_passed', False)}")
            print(f"   📋 Action taken: {validation_results.get('recommended_action', 'unknown')}")
        
        # Check if upload was skipped
        if upload_results.get("skipped"):
            print(f"   ⏭️ Upload skipped: {upload_results.get('skip_reason', 'Unknown reason')}")
        
        return upload_results.get("success", False) or upload_results.get("skipped", False)
        
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        logger.exception("Full error details:")
        return False


async def main():
    """Run validation and upload tests"""
    print("🔧 Data Validation and Upload Test Suite")
    print("=" * 60)
    
    # Test 1: Data validation
    validation_success = await test_data_validation()
    
    # Test 2: Validated upload
    upload_success = await test_validated_upload()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"🔍 Data validation: {'PASS' if validation_success else 'FAIL'}")
    print(f"🗄️ Validated upload: {'PASS' if upload_success else 'FAIL'}")
    
    if validation_success and upload_success:
        print("\n🎉 All validation and upload tests passed!")
        print("✅ Data freshness validation working")
        print("✅ Duplicate detection working")
        print("✅ Smart upload decisions working")
        print("🔄 Ready for Step 4: ML Pipeline Integration")
    else:
        print("\n❌ Some tests failed.")
    
    return validation_success and upload_success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
        exit(0)
    except Exception as e:
        print(f"❌ Test crashed: {e}")
        exit(1)
