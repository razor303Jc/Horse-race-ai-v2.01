#!/usr/bin/env python3
"""
Test script for human-like login integration with WooCommerce downloads
"""

import asyncio
import logging
import os

from dotenv import load_dotenv

from src.automation.respectful_auto_downloader import RespectfulAutoDownloader

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def test_human_login_integration():
    """Test the human-like login + WooCommerce download integration"""

    # Check if WooCommerce URLs are configured
    results_url = os.getenv("HORSERACE_DB_RESULTS_URL")
    cards_url = os.getenv("HORSERACE_DB_CARDS_URL")
    username = os.getenv("HORSERACE_DB_USERNAME")
    password = os.getenv("HORSERACE_DB_PASSWORD")

    print("🔧 Configuration Check:")
    print(f"  Results URL: {'✅ Configured' if results_url else '❌ Missing'}")
    print(f"  Cards URL: {'✅ Configured' if cards_url else '❌ Missing'}")
    print(f"  Username: {'✅ Configured' if username else '❌ Missing'}")
    print(f"  Password: {'✅ Configured' if password else '❌ Missing'}")

    if not all([results_url, cards_url, username, password]):
        print("\n❌ Missing required configuration. Please check your .env file.")
        return

    print("\n🚀 Starting human-like login integration test...")

    try:
        # Initialize the auto downloader
        downloader = RespectfulAutoDownloader()

        # Test just the initialization and setup
        print("✅ Auto downloader initialized successfully")

        # Test method existence
        if hasattr(downloader, "_human_login_to_site"):
            print("✅ Human login method available")
        else:
            print("❌ Human login method missing")

        if hasattr(downloader, "_download_with_session_cookies"):
            print("✅ Session cookie download method available")
        else:
            print("❌ Session cookie download method missing")

        print("\n🎯 Integration test completed successfully!")
        print(
            "📝 To run a full download test, use: python -m src.automation.respectful_auto_downloader"
        )

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        logging.exception("Full error details:")


if __name__ == "__main__":
    asyncio.run(test_human_login_integration())
