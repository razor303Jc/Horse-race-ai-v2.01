#!/usr/bin/env python3
"""
Racing News Scheduler
Automated scheduling system for daily news analysis
"""

import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("news_scheduler.log"), logging.StreamHandler()],
)


class NewsScheduler:
    def __init__(self):
        self.script_path = Path(__file__).parent / "daily_news_analyzer.py"
        self.reports_dir = Path("reports/daily_news")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run_news_analysis(self):
        """Execute the daily news analysis"""
        try:
            logging.info("🕒 Starting scheduled news analysis...")

            # Run the news analyzer
            result = subprocess.run(
                ["python3", str(self.script_path)],
                capture_output=True,
                text=True,
                timeout=1800,
            )  # 30 min timeout

            if result.returncode == 0:
                logging.info("✅ News analysis completed successfully")
                logging.info(f"Output: {result.stdout}")
            else:
                logging.error(f"❌ News analysis failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            logging.error("❌ News analysis timed out after 30 minutes")
        except Exception as e:
            logging.error(f"❌ Failed to run news analysis: {e}")

    def check_ollama_service(self):
        """Check if Ollama service is running"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "ollama"], capture_output=True, text=True
            )

            if result.returncode == 0:
                logging.info("✅ Ollama service is running")
                return True
            else:
                logging.warning("⚠️ Ollama service not detected, attempting to start...")
                self.start_ollama()
                return False
        except Exception as e:
            logging.error(f"Failed to check Ollama service: {e}")
            return False

    def start_ollama(self):
        """Start Ollama service"""
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(10)  # Wait for service to start
            logging.info("🚀 Started Ollama service")
        except Exception as e:
            logging.error(f"Failed to start Ollama: {e}")

    def setup_schedules(self):
        """Setup the scheduled tasks"""
        # Daily analysis at 8:00 AM
        schedule.every().day.at("08:00").do(self.run_news_analysis)

        # Additional analysis at 2:00 PM for afternoon news
        schedule.every().day.at("14:00").do(self.run_news_analysis)

        # Evening summary at 8:00 PM
        schedule.every().day.at("20:00").do(self.run_news_analysis)

        # Check Ollama service every hour
        schedule.every().hour.do(self.check_ollama_service)

        logging.info("📅 Scheduled tasks configured:")
        logging.info("  - Daily analysis: 08:00, 14:00, 20:00")
        logging.info("  - Ollama health check: Every hour")

    def run_scheduler(self):
        """Run the main scheduler loop"""
        logging.info("🏇 Starting Racing News Scheduler")

        # Initial setup
        self.check_ollama_service()
        self.setup_schedules()

        # Run scheduler
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logging.info("⏹️ Scheduler stopped by user")
        except Exception as e:
            logging.error(f"❌ Scheduler error: {e}")


if __name__ == "__main__":
    scheduler = NewsScheduler()
    scheduler.run_scheduler()
