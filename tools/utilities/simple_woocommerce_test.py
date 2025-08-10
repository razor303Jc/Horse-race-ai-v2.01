#!/usr/bin/env python3
"""
Simple WooCommerce Test
======================

Direct test of WooCommerce download functionality
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


async def simple_woocommerce_test():
    """Simple test of WooCommerce downloader"""
    print("🛒 Simple WooCommerce Test")
    print("=" * 40)

    try:
        from demos.woocommerce_downloader import WooCommerceDownloader

        # Check credentials
        username = os.getenv("HORSERACE_DB_USERNAME")
        password = os.getenv("HORSERACE_DB_PASSWORD")
        results_url = os.getenv("HORSERACE_DB_RESULTS_URL")
        cards_url = os.getenv("HORSERACE_DB_CARDS_URL")

        print(f"👤 Username: {username}")
        print(f"🔒 Password: {'*' * len(password) if password else 'None'}")
        print(f"📥 Results URL: {results_url[:60]}..." if results_url else "❌ Missing")
        print(f"📥 Cards URL: {cards_url[:60]}..." if cards_url else "❌ Missing")

        if not all([username, password, results_url, cards_url]):
            print("❌ Missing required configuration")
            return False

        # Initialize downloader
        downloader = WooCommerceDownloader()
        print("✅ Downloader initialized")

        # Test with headless=False so we can see what's happening
        print("\n🚀 Starting browser (visible mode for debugging)...")
        if not await downloader.start_browser(headless=False):
            print("❌ Failed to start browser")
            return False

        print("✅ Browser started")

        # Create a page and try manual login
        page = await downloader.context.new_page()
        print("✅ Page created")

        # Navigate to login page and try to login
        print("\n🔐 Testing login process...")
        login_success = await downloader.login(page)

        if login_success:
            print("✅ Login successful!")

            # Wait a bit for user to see the logged-in state
            print("⏱️  Logged in successfully. You can see the browser window.")
            print("   Press Enter to continue with download test...")
            input()

            # Try downloading directly using the URLs
            print("\n📥 Testing direct download...")

            # Test results URL
            print(f"📊 Navigating to results URL...")
            await page.goto(results_url)
            await asyncio.sleep(3)
            print("✅ Navigated to results URL")

            # Test cards URL
            print(f"📊 Navigating to cards URL...")
            await page.goto(cards_url)
            await asyncio.sleep(3)
            print("✅ Navigated to cards URL")

            print("\n💡 Check your Downloads folder for any downloaded files")
            print("   The downloads should happen automatically when visiting the URLs")

        else:
            print("❌ Login failed")

        # Keep browser open for inspection
        print("\n🔍 Browser will stay open for 30 seconds for inspection...")
        await asyncio.sleep(30)

        await downloader.close()
        print("✅ Browser closed")

        return login_success

    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Full error details:")
        return False


async def check_downloads_folder():
    """Check Downloads folder for recent files"""
    print("\n📁 Checking Downloads folder...")

    downloads_dir = Path.home() / "Downloads"
    if not downloads_dir.exists():
        print(f"❌ Downloads folder not found: {downloads_dir}")
        return False

    # Look for recent zip files
    recent_files = []
    for file in downloads_dir.glob("*.zip"):
        # Check if modified in last 10 minutes
        import time

        if time.time() - file.stat().st_mtime < 600:  # 10 minutes
            recent_files.append(file)

    if recent_files:
        print(f"✅ Found {len(recent_files)} recent zip files:")
        for file in recent_files:
            print(f"   📄 {file.name} ({file.stat().st_size:,} bytes)")

            # Try to examine zip contents
            try:
                import zipfile

                with zipfile.ZipFile(file, "r") as zf:
                    files_in_zip = zf.namelist()
                    print(f"      Contains {len(files_in_zip)} files")
                    if files_in_zip:
                        print(f"      Sample: {files_in_zip[0]}")
            except Exception as e:
                print(f"      ❌ Could not read zip: {e}")
        return True
    else:
        print("❌ No recent zip files found in Downloads")
        return False


async def main():
    """Run the simple test"""
    success = await simple_woocommerce_test()

    # Check for downloaded files
    files_found = await check_downloads_folder()

    print("\n" + "=" * 40)
    if success or files_found:
        print("🎉 Test completed! Check results above.")
    else:
        print("❌ Test failed. Check error messages above.")

    return success or files_found


if __name__ == "__main__":
    asyncio.run(main())
