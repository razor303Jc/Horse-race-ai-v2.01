#!/usr/bin/env python3
"""
Test Database Integration Functionality
=======================================

Test the new database upload functionality we added to the auto downloader.
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


async def test_database_integration():
    """Test database integration functionality"""
    print("🧪 Testing Database Integration Functionality")
    print("=" * 50)

    try:
        # Check database URL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not found in environment")
            print("   Please set DATABASE_URL in .env file")
            return False

        print(f"✅ Database URL configured")

        # Set Docker environment for headless mode
        os.environ["DOCKER_CONTAINER"] = "true"

        from src.automation.respectful_auto_downloader import RespectfulAutoDownloader

        # Initialize downloader
        downloader = RespectfulAutoDownloader()
        print("✅ Auto downloader initialized")

        # First, run CSV processing to get data ready
        print("\n📊 Processing CSV files first...")
        processing_results = await downloader.process_extracted_csv_files()

        if not processing_results["success"]:
            print("❌ CSV processing failed - cannot test database upload")
            return False

        print(
            f"✅ CSV processing complete: {processing_results['processed_files']} files"
        )

        # Test database upload
        print("\n🗄️ Starting database upload test...")
        upload_results = await downloader.upload_to_database(processing_results)

        if upload_results["success"]:
            print("✅ Database upload completed successfully!")
            print(f"📊 Records inserted: {upload_results['records_inserted']}")
            print(f"🗃️ Tables updated: {upload_results['tables_updated']}")

            # Show results upload details
            if upload_results.get("results_upload"):
                results_upload = upload_results["results_upload"]
                print(f"\n📊 Results Upload:")
                print(f"   📄 Records: {results_upload.get('records_inserted', 0)}")
                print(f"   🗃️ Tables: {results_upload.get('tables_updated', 0)}")

                for file_path, file_info in results_upload.get(
                    "file_uploads", {}
                ).items():
                    table = file_info["table"]
                    records = file_info["records_inserted"]
                    print(
                        f"      📈 {Path(file_path).name} → {table} ({records} records)"
                    )

            # Show cards upload details
            if upload_results.get("cards_upload"):
                cards_upload = upload_results["cards_upload"]
                print(f"\n🃏 Cards Upload:")
                print(f"   📄 Records: {cards_upload.get('records_inserted', 0)}")
                print(f"   🗃️ Tables: {cards_upload.get('tables_updated', 0)}")

                for file_path, file_info in cards_upload.get(
                    "file_uploads", {}
                ).items():
                    table = file_info["table"]
                    records = file_info["records_inserted"]
                    print(
                        f"      📈 {Path(file_path).name} → {table} ({records} records)"
                    )

            # Show any errors
            if upload_results.get("errors"):
                print(f"\n⚠️ {len(upload_results['errors'])} errors encountered:")
                for error in upload_results["errors"]:
                    print(f"   ❌ {error}")

            return True
        else:
            print("❌ Database upload failed!")
            if "error" in upload_results:
                print(f"   Error: {upload_results['error']}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Full error details:")
        return False


async def main():
    """Run database integration test"""
    print("🔧 Database Integration Test")
    print("=" * 60)

    # Test database integration
    test_success = await test_database_integration()

    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"🗄️ Database integration: {'PASS' if test_success else 'FAIL'}")

    if test_success:
        print("\n🎉 Database integration is working perfectly!")
        print("✅ CSV data uploaded to PostgreSQL database")
        print("✅ Tables updated with race data")
        print("🔄 Ready for Step 4: ML Pipeline Integration")
    else:
        print("\n❌ Database integration test failed.")

    return test_success


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
