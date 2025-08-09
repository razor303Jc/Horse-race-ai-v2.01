#!/usr/bin/env python3
"""
Daily Scheduler for Respectful Auto Downloader
Horse Racing AI v2.0

Runs the respectful auto downloader at 00:01 daily and stops when successful.
"""

import asyncio
import logging
import os
import sys
import time
from datetime import datetime, time as dt_time
from pathlib import Path
from typing import Optional
import json
import schedule
import signal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from automation.respectful_auto_downloader import RespectfulAutoDownloader, DownloadConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/auto_downloader_scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoDownloaderScheduler:
    """Daily scheduler for the respectful auto downloader"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/respectful_downloader_config.json"
        self.downloader: Optional[RespectfulAutoDownloader] = None
        self.should_stop = False
        self.last_run_date: Optional[str] = None
        self.last_run_success = False
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Auto Downloader Scheduler initialized")
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully"""
        logger.warning(f"Received signal {signum}, shutting down scheduler...")
        self.should_stop = True
    
    def _load_config(self) -> DownloadConfig:
        """Load configuration from file"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                config = DownloadConfig()
                # Update config with loaded values
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
            else:
                logger.warning(f"Config file not found: {self.config_path}, using defaults")
                return DownloadConfig()
                
        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults")
            return DownloadConfig()
    
    async def _run_daily_download(self) -> bool:
        """Run the daily download job"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Check if we already ran successfully today
        if self.last_run_date == today and self.last_run_success:
            logger.info(f"Download already completed successfully today ({today})")
            return True
        
        logger.info(f"Starting daily download for {today}")
        
        try:
            # Load fresh config
            config = self._load_config()
            
            # Create new downloader instance
            self.downloader = RespectfulAutoDownloader(config)
            
            # Run the download
            success = await self.downloader.run_once()
            
            # Update tracking
            self.last_run_date = today
            self.last_run_success = success
            
            if success:
                logger.info(f"✅ Daily download completed successfully for {today}")
                self._log_success_status(today)
            else:
                logger.warning(f"⚠️ Daily download failed for {today}")
                self._log_failure_status(today)
            
            return success
            
        except Exception as e:
            logger.error(f"Error in daily download: {e}")
            self.last_run_success = False
            return False
    
    def _log_success_status(self, date: str) -> None:
        """Log successful download to status file"""
        try:
            status_file = Path("data/daily_downloads/last_success.json")
            status_file.parent.mkdir(parents=True, exist_ok=True)
            
            status = {
                "last_success_date": date,
                "last_success_time": datetime.now().isoformat(),
                "status": "success",
                "message": "Daily download completed successfully"
            }
            
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error logging success status: {e}")
    
    def _log_failure_status(self, date: str) -> None:
        """Log failed download to status file"""
        try:
            status_file = Path("data/daily_downloads/last_failure.json")
            status_file.parent.mkdir(parents=True, exist_ok=True)
            
            status = {
                "last_failure_date": date,
                "last_failure_time": datetime.now().isoformat(),
                "status": "failure",
                "message": "Daily download failed or incomplete"
            }
            
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error logging failure status: {e}")
    
    def _schedule_job(self) -> None:
        """Schedule the daily download job"""
        config = self._load_config()
        run_time = config.daily_run_time
        
        logger.info(f"Scheduling daily download at {run_time}")
        
        schedule.every().day.at(run_time).do(
            lambda: asyncio.run(self._run_daily_download())
        )
        
        # Log next scheduled run
        next_run = schedule.next_run()
        logger.info(f"Next download scheduled for: {next_run}")
    
    def get_status(self) -> dict:
        """Get current scheduler status"""
        return {
            "scheduler_running": not self.should_stop,
            "last_run_date": self.last_run_date,
            "last_run_success": self.last_run_success,
            "next_run": str(schedule.next_run()) if schedule.jobs else None,
            "config_path": self.config_path
        }
    
    def run(self) -> None:
        """Run the scheduler"""
        logger.info("Starting Auto Downloader Scheduler")
        logger.info("This will run the respectful auto downloader at 00:01 daily")
        logger.info("The downloader will stop when successful or after maximum runtime")
        
        # Schedule the job
        self._schedule_job()
        
        # Main scheduler loop
        while not self.should_stop:
            try:
                schedule.run_pending()
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(5)
        
        logger.info("Auto Downloader Scheduler stopped")
    
    async def run_now(self) -> bool:
        """Run download immediately (for testing)"""
        logger.info("Running download immediately...")
        return await self._run_daily_download()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily Scheduler for Respectful Auto Downloader")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--run-now", action="store_true", help="Run download immediately instead of scheduling")
    parser.add_argument("--status", action="store_true", help="Show scheduler status")
    args = parser.parse_args()
    
    scheduler = AutoDownloaderScheduler(args.config)
    
    if args.status:
        status = scheduler.get_status()
        print("Auto Downloader Scheduler Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        return
    
    if args.run_now:
        # Run immediately for testing
        result = asyncio.run(scheduler.run_now())
        sys.exit(0 if result else 1)
    else:
        # Run scheduler
        scheduler.run()


if __name__ == "__main__":
    main()
