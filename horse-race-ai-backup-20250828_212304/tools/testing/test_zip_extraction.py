#!/usr/bin/env python3
"""
Test ZIP Extraction Functionality
=================================

Test the new ZIP extraction functionality we added to the auto downloader.
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


async def test_zip_extraction():
    """Test ZIP extraction functionality"""
    print("🧪 Testing ZIP Extraction Functionality")
    print("=" * 50)

    try:
        # Set Docker environment for headless mode
        os.environ["DOCKER_CONTAINER"] = "true"

        from src.automation.respectful_auto_downloader import RespectfulAutoDownloader

        # Initialize downloader
        downloader = RespectfulAutoDownloader()
        print("✅ Auto downloader initialized")

        # Check for existing ZIP files in the output directory
        output_dir = Path(downloader.config.output_directory)
        zip_files = list(output_dir.glob("*.zip"))

        if not zip_files:
            print("❌ No ZIP files found to test extraction")
            print(f"   Looking in: {output_dir}")
            print("   Please download some files first!")
            return False

        print(f"📦 Found {len(zip_files)} ZIP files:")
        for zip_file in zip_files:
            file_size = zip_file.stat().st_size
            print(f"   📁 {zip_file.name} ({file_size:,} bytes)")

        # Test extraction
        print("\n🗂️  Starting extraction test...")
        success = await downloader.extract_downloaded_files()

        if success:
            print("✅ ZIP extraction completed successfully!")

            # Check what was extracted
            extract_dirs = list(output_dir.glob("*_data_*"))
            print(f"\n📁 Created {len(extract_dirs)} extraction directories:")

            for extract_dir in extract_dirs:
                print(f"   📂 {extract_dir.name}")

                # Count files in each directory
                files = list(extract_dir.rglob("*"))
                file_count = len([f for f in files if f.is_file()])
                print(f"      📄 Contains {file_count} files")

                # Show first few files
                csv_files = list(extract_dir.glob("*.csv"))
                if csv_files:
                    print(f"      🗃️  CSV files found: {len(csv_files)}")
                    for csv_file in csv_files[:3]:
                        print(f"         📊 {csv_file.name}")
                    if len(csv_files) > 3:
                        print(
                            f"         📊 ... and {len(csv_files) - 3} more CSV files"
                        )

                # Check metadata
                metadata_file = extract_dir / "extraction_metadata.json"
                if metadata_file.exists():
                    print("      ✅ Extraction metadata saved")

            return True
        else:
            print("❌ ZIP extraction failed!")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Full error details:")
        return False


async def main():
    """Run extraction test"""
    print("🔧 ZIP Extraction Test")
    print("=" * 60)

    # Test extraction
    test_success = await test_zip_extraction()

    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"🗂️  ZIP extraction: {'PASS' if test_success else 'FAIL'}")

    if test_success:
        print("\n🎉 ZIP extraction is working perfectly!")
        print("✅ Files extracted to timestamped directories")
        print("✅ Metadata saved for processing")
        print("🔄 Ready for Step 2: CSV Processing")
    else:
        print("\n❌ ZIP extraction test failed.")

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
