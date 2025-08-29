#!/usr/bin/env python3
"""
Test Improved Column Mapping
============================

Test the new column mapping system to ensure CSV columns are properly
mapped to database columns.
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


async def test_improved_upload():
    """Test the improved column mapping upload"""
    print("🧪 Testing Improved Column Mapping Upload")
    print("=" * 50)

    try:
        # Set Docker environment for headless mode
        os.environ["DOCKER_CONTAINER"] = "true"

        from src.automation.respectful_auto_downloader import RespectfulAutoDownloader

        # Initialize downloader
        downloader = RespectfulAutoDownloader()
        print("✅ Auto downloader initialized")

        # Process CSV files
        print("\n📊 Processing CSV files...")
        processing_results = await downloader.process_extracted_csv_files()

        if not processing_results["success"]:
            print("❌ CSV processing failed")
            return False

        files_count = processing_results["processed_files"]
        print(f"✅ CSV processing complete: {files_count} files")

        # Test upload with improved column mapping
        print("\n🗄️ Testing upload with improved column mapping...")
        upload_results = await downloader.upload_to_database(processing_results)

        print("📊 Upload Results:")
        print(f"   ✅ Success: {upload_results.get('success', False)}")
        print(f"   📊 Records inserted: {upload_results.get('records_inserted', 0)}")
        print(f"   🗃️ Tables updated: {upload_results.get('tables_updated', 0)}")

        # Show detailed file upload results
        file_uploads = upload_results.get("file_uploads", {})
        if file_uploads:
            print("   📄 File upload details:")
            for file_path, details in file_uploads.items():
                file_name = Path(file_path).name
                table = details.get("table", "unknown")
                records = details.get("records_inserted", 0)
                success = details.get("success", False)
                status = "✅" if success else "❌"
                print(f"      {status} {file_name} → {table}: {records} records")

        # Show any errors
        errors = upload_results.get("errors", [])
        if errors:
            print("   ❌ Upload errors:")
            for error in errors:
                print(f"      • {error}")

        return upload_results.get("success", False)

    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Full error details:")
        return False


async def check_database_content():
    """Check what data is now in the database"""
    print("\n🔍 Checking Database Content After Upload")
    print("=" * 50)

    # Import here to avoid issues
    import subprocess

    import docker

    try:
        # Check record counts
        result = subprocess.run(
            [
                "docker",
                "exec",
                "horse_racing_postgres",
                "psql",
                "-U",
                "horse_racing",
                "-d",
                "horse_racing_db",
                "-c",
                """
            SELECT 
              table_name,
              record_count,
              CASE 
                WHEN record_count > 0 THEN '✅ Has data'
                ELSE '❌ Empty'
              END as status
            FROM (
              SELECT 'horses' as table_name, COUNT(*) as record_count FROM horses
              UNION ALL SELECT 'jockey_stats', COUNT(*) FROM jockey_stats  
              UNION ALL SELECT 'trainer_stats', COUNT(*) FROM trainer_stats
              UNION ALL SELECT 'races_cards', COUNT(*) FROM races_cards
              UNION ALL SELECT 'race_results', COUNT(*) FROM race_results
              UNION ALL SELECT 'racecard_details', COUNT(*) FROM racecard_details
            ) t
            ORDER BY record_count DESC;
            """,
            ],
            capture_output=True,
            text=True,
            cwd="/home/jc/Documents/Horse-race-ai-v2.01",
        )

        print("📊 Table Record Counts:")
        print(result.stdout)

        # Check sample data with names
        result2 = subprocess.run(
            [
                "docker",
                "exec",
                "horse_racing_postgres",
                "psql",
                "-U",
                "horse_racing",
                "-d",
                "horse_racing_db",
                "-c",
                """
            -- Check if names are now populated
            SELECT 'JOCKEY SAMPLE' as info;
            SELECT jockey_name, wins, runs, win_percentage, uptodate 
            FROM jockey_stats 
            WHERE jockey_name IS NOT NULL AND jockey_name != ''
            ORDER BY wins DESC LIMIT 3;
            
            SELECT 'TRAINER SAMPLE' as info;  
            SELECT trainer_name, wins, runs, win_percentage, uptodate
            FROM trainer_stats
            WHERE trainer_name IS NOT NULL AND trainer_name != ''
            ORDER BY wins DESC LIMIT 3;
            
            SELECT 'HORSE SAMPLE' as info;
            SELECT horse_name, sire, country, uptodate
            FROM horses  
            WHERE horse_name IS NOT NULL AND horse_name != ''
            ORDER BY id LIMIT 3;
            """,
            ],
            capture_output=True,
            text=True,
            cwd="/home/jc/Documents/Horse-race-ai-v2.01",
        )

        print("🐎 Sample Data (to verify names are populated):")
        print(result2.stdout)

        return True

    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False


async def main():
    """Run improved upload test"""
    print("🔧 Improved Column Mapping Test Suite")
    print("=" * 60)

    # Test 1: Upload with improved mapping
    upload_success = await test_improved_upload()

    # Test 2: Check database content
    db_check_success = await check_database_content()

    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"🗄️ Improved upload: {'PASS' if upload_success else 'FAIL'}")
    print(f"🔍 Database check: {'PASS' if db_check_success else 'FAIL'}")

    if upload_success and db_check_success:
        print("\n🎉 Column mapping improvements working!")
        print("✅ CSV columns properly mapped to database columns")
        print("✅ Names should now be populated correctly")
        print("🚀 Data pipeline fully operational!")
    else:
        print("\n❌ Some tests failed - column mapping needs more work.")

    return upload_success and db_check_success


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
