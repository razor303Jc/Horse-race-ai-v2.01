#!/usr/bin/env python3
"""
Docker Auto Downloader Runner
============================

Runs the respectful auto downloader optimized for Docker containers.
This script ensures proper Docker environment setup and configuration.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Set up Docker environment variables
os.environ["DOCKER_CONTAINER"] = "true"
os.environ["HEADLESS"] = "true"
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/app/.playwright"

# Ensure we're in the right directory
sys.path.insert(0, "/app")

from src.automation.docker_config import (
    get_docker_environment_config,
    validate_docker_setup,
)
from src.automation.respectful_auto_downloader import RespectfulAutoDownloader


async def run_docker_auto_downloader():
    """Run the auto downloader in Docker environment"""

    print("🐳 Starting Horse Racing Auto Downloader in Docker")

    # Validate Docker setup
    if not validate_docker_setup():
        print("❌ Docker environment validation failed")
        return False

    # Set up environment
    env_config = get_docker_environment_config()
    for key, value in env_config.items():
        os.environ[key] = str(value)

    print("✅ Docker environment validated and configured")

    try:
        # Initialize the auto downloader
        downloader = RespectfulAutoDownloader()

        print("🚀 Starting daily download process...")

        # Run the daily download
        success = await downloader._run_daily_download()

        if success:
            print("✅ Daily download completed successfully!")
            return True
        else:
            print("❌ Daily download failed")
            return False

    except Exception as e:
        print(f"❌ Error running auto downloader: {e}")
        logging.exception("Full error details:")
        return False


def run_once():
    """Run the auto downloader once (for testing or manual runs)"""
    return asyncio.run(run_docker_auto_downloader())


def run_scheduled():
    """Run the auto downloader on schedule (for production)"""
    import time

    import schedule

    # Schedule for 09:01 daily (test time)
    schedule.every().day.at("09:01").do(run_once)

    print("📅 Scheduled auto downloader for 09:01 daily")
    print("🔄 Waiting for scheduled time...")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Docker Auto Downloader Runner")
    parser.add_argument(
        "--mode",
        choices=["once", "scheduled"],
        default="once",
        help="Run mode: 'once' for immediate run, 'scheduled' for daily schedule",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    # Set up logging with error handling for file permissions
    log_handlers = [logging.StreamHandler()]

    # Try to add file handler if directory is writable
    try:
        import os

        os.makedirs("/app/logs", mode=0o775, exist_ok=True)
        log_handlers.append(logging.FileHandler("/app/logs/auto_downloader.log"))
        print("✅ Logging to file: /app/logs/auto_downloader.log")
    except (PermissionError, OSError) as e:
        print(f"⚠️  Cannot write to log file: {e}")
        print("📝 Logging to console only")

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=log_handlers,
    )

    print(f"🎯 Running in {args.mode} mode with {args.log_level} logging")

    try:
        if args.mode == "once":
            success = run_once()
            sys.exit(0 if success else 1)
        else:
            run_scheduled()
    except KeyboardInterrupt:
        print("\n🛑 Auto downloader stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
