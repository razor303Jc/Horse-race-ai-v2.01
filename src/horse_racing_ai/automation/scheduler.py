#!/usr/bin/env python3
"""
Horse Racing AI - Automation Scheduler
=====================================

Scheduler service for automated scraping and data collection.
Runs as a background service in Docker container.
"""

import asyncio
import logging
import signal
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

import schedule

from horse_racing_ai.automation.playwright_scraper import PlaywrightScraper
from horse_racing_ai.notifications.ntfy_client import NTFYClient


class SchedulerService:
    """Scheduler service for automated tasks."""

    def __init__(self):
        """Initialize the scheduler service."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.scraper: Optional[PlaywrightScraper] = None
        self.ntfy: Optional[NTFYClient] = None

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    async def initialize(self):
        """Initialize the scheduler components."""
        try:
            self.logger.info("🚀 Initializing Horse Racing AI Scheduler Service...")

            # Initialize scraper
            self.scraper = PlaywrightScraper()
            await self.scraper.start()

            # Initialize notifications
            try:
                self.ntfy = NTFYClient()
                await self.ntfy.send_message(
                    "🤖 Scheduler Service Started",
                    "Horse Racing AI automation scheduler is now running",
                    priority="normal",
                )
            except Exception as e:
                self.logger.warning(f"Could not initialize NTFY client: {e}")
                self.ntfy = None

            self.logger.info("✅ Scheduler service initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize scheduler: {e}")
            return False

    async def cleanup(self):
        """Cleanup resources."""
        try:
            self.logger.info("🧹 Cleaning up scheduler resources...")

            if self.scraper:
                await self.scraper.stop()

            if self.ntfy:
                try:
                    await self.ntfy.send_message(
                        "⏹️ Scheduler Service Stopped",
                        "Horse Racing AI automation scheduler has been stopped",
                        priority="low",
                    )
                except:
                    pass  # Don't fail cleanup if notification fails

            self.logger.info("✅ Cleanup completed")

        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")

    def schedule_jobs(self):
        """Schedule all automated jobs."""
        self.logger.info("📅 Setting up scheduled jobs...")

        # Morning scraping - get fresh race cards
        schedule.every().day.at("06:00").do(self._run_morning_scrape)
        schedule.every().day.at("06:30").do(self._run_morning_scrape)

        # Afternoon updates - update race data
        schedule.every().day.at("12:00").do(self._run_afternoon_update)
        schedule.every().day.at("15:00").do(self._run_afternoon_update)

        # Evening analysis - final updates and results
        schedule.every().day.at("18:00").do(self._run_evening_analysis)
        schedule.every().day.at("21:00").do(self._run_evening_analysis)

        # Periodic health checks
        schedule.every(30).minutes.do(self._run_health_check)

        # Weekly maintenance
        schedule.every().sunday.at("02:00").do(self._run_weekly_maintenance)

        self.logger.info("✅ Scheduled jobs configured")

    def _run_morning_scrape(self):
        """Run morning scraping job."""
        try:
            self.logger.info("🌅 Running morning scrape job...")
            if self.scraper:
                asyncio.create_task(self.scraper.scrape_race_cards())
        except Exception as e:
            self.logger.error(f"❌ Morning scrape failed: {e}")

    def _run_afternoon_update(self):
        """Run afternoon update job."""
        try:
            self.logger.info("☀️ Running afternoon update job...")
            if self.scraper:
                asyncio.create_task(self.scraper.update_race_data())
        except Exception as e:
            self.logger.error(f"❌ Afternoon update failed: {e}")

    def _run_evening_analysis(self):
        """Run evening analysis job."""
        try:
            self.logger.info("🌆 Running evening analysis job...")
            if self.scraper:
                asyncio.create_task(self.scraper.collect_results())
        except Exception as e:
            self.logger.error(f"❌ Evening analysis failed: {e}")

    def _run_health_check(self):
        """Run health check job."""
        try:
            self.logger.info("💓 Running health check...")
            # Basic health check - could be expanded
            if self.scraper and self.ntfy:
                asyncio.create_task(self._send_health_status())
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")

    def _run_weekly_maintenance(self):
        """Run weekly maintenance job."""
        try:
            self.logger.info("🔧 Running weekly maintenance...")
            # Cleanup old data, optimize database, etc.
            if self.scraper:
                asyncio.create_task(self.scraper.run_maintenance())
        except Exception as e:
            self.logger.error(f"❌ Weekly maintenance failed: {e}")

    async def _send_health_status(self):
        """Send health status notification."""
        try:
            if self.ntfy:
                await self.ntfy.send_message(
                    "💓 Scheduler Health Check",
                    f"Scheduler service is running at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    priority="low",
                )
        except Exception as e:
            self.logger.warning(f"Could not send health status: {e}")

    async def run(self):
        """Run the scheduler service."""
        if not await self.initialize():
            self.logger.error("❌ Failed to initialize, exiting...")
            return 1

        self.running = True
        self.schedule_jobs()

        self.logger.info("🚀 Horse Racing AI Scheduler Service is running...")
        self.logger.info("📋 Scheduled jobs:")
        for job in schedule.jobs:
            self.logger.info(f"  - {job}")

        try:
            while self.running:
                # Run pending scheduled jobs
                schedule.run_pending()

                # Sleep for a short interval
                await asyncio.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            self.logger.info("⏹️ Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"❌ Scheduler error: {e}")
        finally:
            await self.cleanup()

        self.logger.info("👋 Scheduler service stopped")
        return 0


async def main():
    """Main entry point for the scheduler."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("/app/logs/scheduler.log"),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info("🎯 Starting Horse Racing AI Scheduler Service...")

    try:
        scheduler = SchedulerService()
        exit_code = await scheduler.run()
        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"❌ Critical scheduler error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the scheduler
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Scheduler stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
