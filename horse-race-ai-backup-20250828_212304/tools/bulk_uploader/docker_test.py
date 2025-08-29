#!/usr/bin/env python3
"""
Docker Volume Test Script for Enhanced Bulk Uploader
Tests the bulk uploader with processed directory structure
"""

import os
import sys
from pathlib import Path

# Add the bulk uploader to Python path
sys.path.insert(0, "/app/tools/bulk_uploader")

try:
    from enhanced_bulk_uploader import BulkUploader
except ImportError:
    print("❌ Could not import enhanced_bulk_uploader")
    sys.exit(1)


def test_docker_connection():
    """Test database connection from Docker container"""
    print("🐳 Testing Docker database connection...")

    uploader = BulkUploader()

    if uploader.db_manager.test_connection():
        print("✅ Database connection successful")
        return True
    else:
        print("❌ Database connection failed")
        return False


def discover_processed_files():
    """Discover files in processed directory"""
    print("🔍 Discovering files in processed directory...")

    processed_dir = Path("/app/data/daily_downloads/processed")

    if not processed_dir.exists():
        print(f"❌ Processed directory not found: {processed_dir}")
        return []

    uploader = BulkUploader()

    # Discover files excluding non_target
    job_ids = uploader.discover_and_queue_files(
        processed_dir, recursive=True, exclude_dirs=["non_target"]
    )

    print(f"📋 Found {len(job_ids)} files to process:")
    for job_id in job_ids:
        job = uploader.jobs[job_id]
        print(f"   • {job.file_path.name} → {job.table_name}")

    return job_ids, uploader


def test_single_file_processing():
    """Test processing a single file"""
    print("\n🧪 Testing single file processing...")

    # Look for a specific file to test
    test_files = [
        "/app/data/daily_downloads/processed/2025-08-20/complete_mapped_horses.csv",
        "/app/data/daily_downloads/processed/2025-08-21/complete_mapped_horses.csv",
    ]

    for test_file_path in test_files:
        test_file = Path(test_file_path)
        if test_file.exists():
            print(f"📄 Testing with: {test_file}")

            uploader = BulkUploader()

            # Classify file
            table_name = uploader.discovery_engine.classify_file(test_file)
            print(f"   Classified as: {table_name}")

            # Test validation
            validation_results = uploader.validation_engine.validate_file_structure(
                test_file, table_name
            )
            print(
                f"   Validation: {'✅ PASSED' if validation_results['valid'] else '❌ FAILED'}"
            )

            if validation_results["fixes"]:
                print("   Fixes available:")
                for fix in validation_results["fixes"][:3]:  # Show first 3
                    print(f"     - {fix}")

            if validation_results["issues"]:
                print("   Issues found:")
                for issue in validation_results["issues"][:3]:  # Show first 3
                    print(f"     - {issue}")

            return True

    print("❌ No test files found")
    return False


def run_bulk_upload_test():
    """Run full bulk upload test"""
    print("\n🚀 Running bulk upload test...")

    job_ids, uploader = discover_processed_files()

    if not job_ids:
        print("❌ No files to process")
        return False

    # Limit to first 2 files for testing
    test_job_ids = job_ids[:2]
    print(f"🧪 Testing with {len(test_job_ids)} files")

    # Create a subset of jobs for testing
    test_uploader = BulkUploader()
    for job_id in test_job_ids:
        test_uploader.jobs[job_id] = uploader.jobs[job_id]

    try:
        # Process test jobs
        results = test_uploader.process_all_jobs()

        print("\n📊 TEST RESULTS:")
        print(f"   Total jobs: {results['total_jobs']}")
        print(f"   Successful: {results['successful']}")
        print(f"   Failed: {results['failed']}")

        # Show detailed results
        for job_id, result in results["job_results"].items():
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['table']} - {result['records']} records")
            if result["error"]:
                print(f"      Error: {result['error']}")

        return results["failed"] == 0

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Enhanced Bulk Uploader Docker Test")
    print("=" * 50)

    # Test 1: Database connection
    if not test_docker_connection():
        return 1

    # Test 2: File discovery
    job_ids, uploader = discover_processed_files()
    if not job_ids:
        print("❌ No files discovered for testing")
        return 1

    # Test 3: Single file processing
    if not test_single_file_processing():
        print("⚠️ Single file test failed")

    # Test 4: Small bulk upload test
    print("\n🤔 Proceed with bulk upload test? (y/N):")
    try:
        response = input().strip().lower()
        if response == "y":
            if run_bulk_upload_test():
                print("\n🎉 All tests passed!")
                return 0
            else:
                print("\n❌ Bulk upload test failed")
                return 1
        else:
            print("\n⏹️ Bulk upload test skipped")
            return 0
    except (EOFError, KeyboardInterrupt):
        print("\n⏹️ Test cancelled")
        return 0


if __name__ == "__main__":
    sys.exit(main())
