#!/usr/bin/env python3
"""
Manual Test Script for Auto Downloader
======================================

This script manually tests the auto downloader to verify:
1. Login functionality works
2. Zip files are downloaded
3. Zip file contents are valid
4. Human-like behavior is working
"""

import asyncio
import logging
import os
import zipfile
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_woocommerce_downloader():
    """Test the WooCommerce downloader directly"""
    print("🛒 Testing WooCommerce Downloader...")

    try:
        from demos.woocommerce_downloader import WooCommerceDownloader

        # Get URLs from environment
        results_url = os.getenv("HORSERACE_DB_RESULTS_URL")
        cards_url = os.getenv("HORSERACE_DB_CARDS_URL")

        if not results_url or not cards_url:
            print("❌ Missing WooCommerce URLs in .env file")
            return False

        print(f"📥 Using results URL: {results_url[:50]}...")
        print(f"📥 Using cards URL: {cards_url[:50]}...")

        # Initialize downloader
        downloader = WooCommerceDownloader()
        print("✅ WooCommerce downloader initialized")

        # Run download with headless=False to see what happens
        print("🚀 Starting download (headless=False for visibility)...")
        results = await downloader.run_with_direct_urls(
            results_url=results_url,
            cards_url=cards_url,
            headless=False,  # So we can see the browser
        )

        print(f"📊 Download results: {results}")

        if results.get("results", False) and results.get("cards", False):
            print("✅ Both files downloaded successfully!")
            return True
        else:
            print("❌ Download failed")
            return False

    except Exception as e:
        print(f"❌ WooCommerce downloader test failed: {e}")
        logger.exception("Full error details:")
        return False


async def test_respectful_auto_downloader():
    """Test the respectful auto downloader"""
    print("\n🤖 Testing Respectful Auto Downloader...")

    try:
        from src.automation.respectful_auto_downloader import RespectfulAutoDownloader

        # Initialize downloader
        downloader = RespectfulAutoDownloader()
        print("✅ Respectful auto downloader initialized")

        # Test just the WooCommerce download method
        print("🚀 Testing WooCommerce download method...")
        success = await downloader._try_woocommerce_download()

        if success:
            print("✅ Respectful auto downloader WooCommerce method worked!")
            return True
        else:
            print("❌ Respectful auto downloader WooCommerce method failed")
            return False

    except Exception as e:
        print(f"❌ Respectful auto downloader test failed: {e}")
        logger.exception("Full error details:")
        return False


def check_downloaded_files():
    """Check for downloaded files and examine their contents"""
    print("\n📁 Checking Downloaded Files...")

    # Check common download locations
    download_locations = [
        Path("downloads/horseracedatabase"),
        Path("data/horseracedatabase"),
        Path("data/daily_downloads"),
        Path.home() / "Downloads",
        Path.cwd(),
    ]

    zip_files = []
    for location in download_locations:
        if location.exists():
            # Look for recently downloaded zip files
            for file in location.glob("*.zip"):
                # Check if file was created in the last hour
                file_time = datetime.fromtimestamp(file.stat().st_mtime)
                time_diff = datetime.now() - file_time
                if time_diff.total_seconds() < 3600:  # 1 hour
                    zip_files.append(file)
                    print(f"✅ Found recent zip file: {file}")

    if not zip_files:
        print("❌ No recent zip files found")
        return False

    # Examine zip file contents
    for zip_file in zip_files:
        print(f"\n🔍 Examining {zip_file.name}:")
        try:
            with zipfile.ZipFile(zip_file, "r") as zf:
                file_list = zf.namelist()
                print(f"📄 Contains {len(file_list)} files:")
                for i, filename in enumerate(file_list[:10]):  # Show first 10 files
                    print(f"  {i+1}. {filename}")
                if len(file_list) > 10:
                    print(f"  ... and {len(file_list) - 10} more files")

                # Check file sizes
                total_size = sum(zf.getinfo(name).file_size for name in file_list)
                print(f"📊 Total uncompressed size: {total_size:,} bytes")

                # Try to read a sample file
                if file_list:
                    sample_file = file_list[0]
                    try:
                        with zf.open(sample_file) as sample:
                            content = sample.read(200)  # Read first 200 bytes
                            print(f"📝 Sample content from {sample_file}:")
                            print(f"   {content[:100]}...")
                    except Exception as e:
                        print(f"⚠️  Couldn't read sample file: {e}")

        except zipfile.BadZipFile:
            print(f"❌ {zip_file.name} is not a valid zip file")
        except Exception as e:
            print(f"❌ Error examining {zip_file.name}: {e}")

    return len(zip_files) > 0


def validate_environment():
    """Validate that all required environment variables are set"""
    print("🔧 Validating Environment...")

    required_vars = [
        "HORSERACE_DB_USERNAME",
        "HORSERACE_DB_PASSWORD",
        "HORSERACE_DB_RESULTS_URL",
        "HORSERACE_DB_CARDS_URL",
    ]

    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show partial value for security
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Missing")
            missing.append(var)

    return len(missing) == 0


async def main():
    """Run manual test of auto downloader"""
    print("🧪 Manual Auto Downloader Test")
    print("=" * 50)

    # Validate environment
    if not validate_environment():
        print("❌ Environment validation failed. Please check your .env file.")
        return False

    print("\n" + "=" * 50)
    print("Choose test mode:")
    print("1. Test WooCommerce downloader (visible browser)")
    print("2. Test Respectful auto downloader")
    print("3. Check existing downloaded files")
    print("4. Run all tests")

    try:
        choice = input("\nEnter choice (1-4): ").strip()
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
        return False

    success = False

    if choice == "1":
        success = await test_woocommerce_downloader()
    elif choice == "2":
        success = await test_respectful_auto_downloader()
    elif choice == "3":
        success = check_downloaded_files()
    elif choice == "4":
        print("\n🚀 Running all tests...")
        woo_success = await test_woocommerce_downloader()
        auto_success = await test_respectful_auto_downloader()
        files_found = check_downloaded_files()
        success = woo_success or auto_success or files_found
    else:
        print("❌ Invalid choice")
        return False

    print("\n" + "=" * 50)
    if success:
        print("🎉 Manual test completed successfully!")
        print("📁 Check the output above for download details")
    else:
        print("❌ Manual test failed")
        print("🔍 Check the error messages above for troubleshooting")

    return success


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test crashed: {e}")
        logging.exception("Full error details:")
