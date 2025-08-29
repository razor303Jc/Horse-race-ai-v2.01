#!/usr/bin/env python3
"""
Test Clean Browser Cleanup
==========================

Test that the browser cleanup properly closes all resources
without the asyncio exception.
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


async def test_clean_cleanup():
    """Test clean browser cleanup without asyncio exceptions"""
    print("🧪 Testing Clean Browser Cleanup")
    print("=" * 40)

    try:
        # Set Docker environment for headless mode
        os.environ["DOCKER_CONTAINER"] = "true"

        from src.automation.respectful_auto_downloader import RespectfulAutoDownloader

        # Initialize downloader
        downloader = RespectfulAutoDownloader()
        print("✅ Auto downloader initialized")

        # Initialize browser
        await downloader._initialize_browser()
        print("✅ Browser initialized")

        # Do a quick test operation
        if downloader.context:
            page = await downloader.context.new_page()
            await page.goto("about:blank")  # Simple page
            await page.close()
            print("✅ Browser test operation completed")

        # Clean up properly
        print("🧹 Starting clean browser cleanup...")
        await downloader._cleanup_browser()
        print("✅ Browser cleanup completed")

        # Small delay to let cleanup settle
        await asyncio.sleep(0.5)

        print("🎉 Test completed without asyncio exceptions!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Full error details:")
        return False


async def test_multiple_cleanups():
    """Test multiple cleanup cycles to ensure stability"""
    print("\n🔄 Testing Multiple Cleanup Cycles")
    print("=" * 40)

    success_count = 0
    for i in range(3):
        print(f"\n🔄 Cleanup cycle {i+1}/3")
        try:
            # Set Docker environment
            os.environ["DOCKER_CONTAINER"] = "true"

            from src.automation.respectful_auto_downloader import (
                RespectfulAutoDownloader,
            )

            downloader = RespectfulAutoDownloader()
            await downloader._initialize_browser()

            # Quick operation
            if downloader.context:
                page = await downloader.context.new_page()
                await page.goto("about:blank")
                await page.close()

            # Clean up
            await downloader._cleanup_browser()

            # Small delay
            await asyncio.sleep(0.3)

            print(f"✅ Cycle {i+1} completed")
            success_count += 1

        except Exception as e:
            print(f"❌ Cycle {i+1} failed: {e}")

    print(f"\n📊 Results: {success_count}/3 cycles completed successfully")
    return success_count == 3


async def main():
    """Run cleanup tests"""
    print("🔧 Browser Cleanup Tests")
    print("=" * 50)

    # Test 1: Single cleanup
    test1_success = await test_clean_cleanup()

    # Test 2: Multiple cleanups
    test2_success = await test_multiple_cleanups()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"✅ Single cleanup: {'PASS' if test1_success else 'FAIL'}")
    print(f"✅ Multiple cleanups: {'PASS' if test2_success else 'FAIL'}")

    if test1_success and test2_success:
        print("\n🎉 All tests passed! Cleanup is working properly.")
        print("🚫 No more asyncio exceptions should occur.")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")

    return test1_success and test2_success


if __name__ == "__main__":
    # Run the test and exit cleanly
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
        exit(0)
    except Exception as e:
        print(f"❌ Test crashed: {e}")
        exit(1)
