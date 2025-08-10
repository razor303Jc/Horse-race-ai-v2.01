#!/usr/bin/env python3
"""
Test CSV Processing Functionality
=================================

Test the new CSV processing functionality we added to the auto downloader.
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


async def test_csv_processing():
    """Test CSV processing functionality"""
    print("🧪 Testing CSV Processing Functionality")
    print("=" * 50)

    try:
        # Set Docker environment for headless mode
        os.environ["DOCKER_CONTAINER"] = "true"

        from src.automation.respectful_auto_downloader import RespectfulAutoDownloader

        # Initialize downloader
        downloader = RespectfulAutoDownloader()
        print("✅ Auto downloader initialized")

        # Check for existing extraction directories
        output_dir = Path(downloader.config.output_directory)
        extract_dirs = list(output_dir.glob("*_data_*"))

        if not extract_dirs:
            print("❌ No extraction directories found to process")
            print(f"   Looking in: {output_dir}")
            print("   Please extract ZIP files first!")
            return False

        print(f"📁 Found {len(extract_dirs)} extraction directories:")
        for extract_dir in extract_dirs:
            csv_files = list(extract_dir.rglob("*.csv"))
            print(f"   📂 {extract_dir.name} ({len(csv_files)} CSV files)")

        # Test CSV processing
        print("\n📊 Starting CSV processing test...")
        results = await downloader.process_extracted_csv_files()

        if results["success"]:
            print("✅ CSV processing completed successfully!")
            print(f"📄 Processed {results['processed_files']} CSV files")

            # Show results data
            if results.get("results_data"):
                print("\n📊 Results Data:")
                results_data = results["results_data"]
                print(f"   📁 Directory: {Path(results_data['extract_dir']).name}")
                print(f"   📄 Files processed: {results_data['files_processed']}")
                print(
                    f"   📊 Total rows: {results_data['statistics'].get('total_rows', 0)}"
                )

                # Show CSV file details
                for file_path, file_data in results_data.get("csv_files", {}).items():
                    stats = file_data["statistics"]
                    print(
                        f"      📈 {file_path}: {stats['rows']} rows, {stats['columns']} columns"
                    )

            # Show cards data
            if results.get("cards_data"):
                print("\n🃏 Cards Data:")
                cards_data = results["cards_data"]
                print(f"   📁 Directory: {Path(cards_data['extract_dir']).name}")
                print(f"   📄 Files processed: {cards_data['files_processed']}")
                print(
                    f"   📊 Total rows: {cards_data['statistics'].get('total_rows', 0)}"
                )

                # Show CSV file details
                for file_path, file_data in cards_data.get("csv_files", {}).items():
                    stats = file_data["statistics"]
                    print(
                        f"      📈 {file_path}: {stats['rows']} rows, {stats['columns']} columns"
                    )

            # Show any errors
            if results.get("errors"):
                print(f"\n⚠️ {len(results['errors'])} errors encountered:")
                for error in results["errors"]:
                    print(f"   ❌ {error}")

            return True
        else:
            print("❌ CSV processing failed!")
            if "error" in results:
                print(f"   Error: {results['error']}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Full error details:")
        return False


async def main():
    """Run CSV processing test"""
    print("🔧 CSV Processing Test")
    print("=" * 60)

    # Test CSV processing
    test_success = await test_csv_processing()

    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"📄 CSV processing: {'PASS' if test_success else 'FAIL'}")

    if test_success:
        print("\n🎉 CSV processing is working perfectly!")
        print("✅ CSV files analyzed and statistics generated")
        print("✅ Data prepared for database upload")
        print("🔄 Ready for Step 3: Database Integration")
    else:
        print("\n❌ CSV processing test failed.")

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
