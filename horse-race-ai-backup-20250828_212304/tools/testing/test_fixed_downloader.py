#!/usr/bin/env python3
"""
Quick Test of Fixed Auto Downloader
===================================

Test the fixed approach using aiohttp like the disabled downloader
"""

import asyncio
import logging
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_fixed_approach():
    """Test the fixed auto downloader approach"""
    print("🧪 Testing Fixed Auto Downloader Approach")
    print("=" * 50)

    try:
        # Set Docker environment for headless mode
        os.environ["DOCKER_CONTAINER"] = "true"

        from src.automation.respectful_auto_downloader import RespectfulAutoDownloader

        # Initialize downloader
        downloader = RespectfulAutoDownloader()
        print("✅ Auto downloader initialized")

        # Initialize browser context
        await downloader._initialize_browser()
        print("✅ Browser initialized (headless mode)")

        # Test the WooCommerce download method
        print("\n🚀 Testing WooCommerce download with aiohttp approach...")
        success = await downloader._try_woocommerce_download()

        # Clean up
        await downloader._cleanup_browser()

        if success:
            print("🎉 Download test successful!")
            print("📁 Check project_root / 'data' / daily_downloads for downloaded files")
            return True
        else:
            print("❌ Download test failed")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Full error details:")
        return False


async def check_downloads():
    """Check if any files were downloaded"""
    import time
    from pathlib import Path

    print("\n📁 Checking for downloaded files...")

    # Check default download location
    download_dir = Path("project_root / 'data' / daily_downloads")
    if download_dir.exists():
        # Look for recent files (last 10 minutes)
        recent_files = []
        current_time = time.time()

        for file in download_dir.glob("*.zip"):
            if current_time - file.stat().st_mtime < 600:  # 10 minutes
                recent_files.append(file)

        if recent_files:
            print(f"✅ Found {len(recent_files)} recent downloads:")
            for file in recent_files:
                size = file.stat().st_size
                print(f"   📄 {file.name} ({size:,} bytes)")

                # Quick peek at zip contents
                try:
                    import zipfile

                    with zipfile.ZipFile(file, "r") as zf:
                        file_count = len(zf.namelist())
                        print(f"      Contains {file_count} files")
                except Exception as e:
                    print(f"      ⚠️ Could not read zip: {e}")
            return True
        else:
            print("❌ No recent downloads found")
    else:
        print(f"❌ Download directory doesn't exist: {download_dir}")

    return False


async def main():
    """Run the test"""
    success = await test_fixed_approach()
    files_found = await check_downloads()

    print("\n" + "=" * 50)
    if success or files_found:
        print("🎯 Test completed successfully!")
    else:
        print("❌ Test failed - check error messages above")


if __name__ == "__main__":
    asyncio.run(main())
