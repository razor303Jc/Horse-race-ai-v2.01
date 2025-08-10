#!/usr/bin/env python3
"""
⏰ Data Relationships Pipeline Scheduler
Automated scheduling for regular pipeline runs

This script can be added to cron jobs or run as a daemon
to ensure data relationships are maintained automatically.

Author: AI Assistant
Date: August 10, 2025
"""

import logging
import os
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tools.data_processing.upload_integration_hook import DataUploadIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(project_root / "logs" / "pipeline_scheduler.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class PipelineScheduler:
    """Scheduler for automated pipeline runs."""

    def __init__(self, check_interval_minutes: int = 60):
        self.check_interval = check_interval_minutes * 60  # Convert to seconds
        self.integration = DataUploadIntegration()
        self.running = False

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"📋 Received signal {signum}, shutting down gracefully...")
        self.running = False

    def run_daemon(self):
        """Run as a daemon process, checking for new data periodically."""
        logger.info("🔄 Starting pipeline scheduler daemon")
        logger.info(f"⏰ Check interval: {self.check_interval // 60} minutes")

        self.running = True

        while self.running:
            try:
                logger.info("🔍 Checking for new data...")

                # Check if pipeline should run
                if self.integration.check_new_data():
                    logger.info("🚀 New data detected, running pipeline...")
                    success = self.integration.run_pipeline()

                    if success:
                        logger.info("✅ Scheduled pipeline run completed successfully")
                    else:
                        logger.error("❌ Scheduled pipeline run failed")
                else:
                    logger.info("ℹ️  No new data, waiting for next check...")

                # Wait for next check
                for _ in range(self.check_interval):
                    if not self.running:
                        break
                    time.sleep(1)

            except Exception as e:
                logger.error(f"❌ Error in scheduler loop: {e}")
                # Wait a bit before retrying
                time.sleep(60)

        logger.info("🛑 Pipeline scheduler daemon stopped")

    def run_single_check(self):
        """Run a single check and pipeline if needed."""
        logger.info("🔍 Running single pipeline check...")

        try:
            if self.integration.check_new_data():
                logger.info("🚀 New data detected, running pipeline...")
                success = self.integration.run_pipeline()
                return success
            else:
                logger.info("ℹ️  No new data, pipeline not needed")
                return True

        except Exception as e:
            logger.error(f"❌ Error in single check: {e}")
            return False


def create_cron_job():
    """Generate cron job command for user reference."""
    script_path = Path(__file__).absolute()

    # Run every 2 hours
    cron_command = f"0 */2 * * * cd {project_root} && {sys.executable} {script_path} --single-check"

    print("📋 Add this line to your crontab to run every 2 hours:")
    print(f"   {cron_command}")
    print()
    print("📝 To edit crontab:")
    print("   crontab -e")
    print()
    print("📄 To view current crontab:")
    print("   crontab -l")


def main():
    """Main function for command line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Data Relationships Pipeline Scheduler"
    )
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument(
        "--single-check", action="store_true", help="Run single check and exit"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in minutes (daemon mode)",
    )
    parser.add_argument(
        "--cron-help", action="store_true", help="Show cron job setup instructions"
    )
    args = parser.parse_args()

    if args.cron_help:
        create_cron_job()
        return True

    scheduler = PipelineScheduler(check_interval_minutes=args.interval)

    if args.daemon:
        print("🔄 Starting pipeline scheduler daemon...")
        print(f"⏰ Will check for new data every {args.interval} minutes")
        print("🛑 Press Ctrl+C to stop")
        scheduler.run_daemon()
        return True
    elif args.single_check:
        return scheduler.run_single_check()
    else:
        print("⚠️  No action specified. Use --daemon, --single-check, or --cron-help")
        parser.print_help()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
