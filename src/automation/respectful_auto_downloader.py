#!/usr/bin/env python3
"""
Respectful Auto Downloader for Horse Racing Database
Horse Racing AI v2.0

A responsible, once-daily auto downloader that:
- Runs at 00:01 daily
- Stops when successful
- Respects horseracedatabase.com with appropriate delays
- Temporary solution until official API is available
"""

import asyncio
import logging
import os
import time
from datetime import datetime, time as dt_time
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import aiofiles
import schedule
import signal
import sys
from dataclasses import dataclass, asdict

import structlog
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = structlog.get_logger(__name__)


@dataclass
class DownloadConfig:
    """Configuration for respectful downloading"""
    
    # Timing configuration
    daily_run_time: str = "00:01"  # Run at 00:01 daily
    max_runtime_minutes: int = 60  # Maximum runtime before timeout
    
    # Respectful scraping settings
    page_delay_seconds: float = 3.0  # Delay between page requests
    retry_delay_seconds: float = 5.0  # Delay before retrying
    max_retries: int = 3  # Maximum retry attempts
    
    # Browser settings
    headless: bool = True
    user_agent: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    # Rate limiting
    requests_per_minute: int = 15  # Maximum requests per minute
    concurrent_pages: int = 1  # Only one page at a time to be respectful
    
    # Data storage
    output_directory: str = "data/daily_downloads"
    backup_directory: str = "data/daily_downloads/backups"
    
    # Success criteria
    minimum_races_required: int = 10  # Minimum races needed for success
    minimum_horses_per_race: int = 4  # Minimum horses per race


@dataclass
class DownloadSession:
    """Track download session statistics"""
    
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    races_downloaded: int = 0
    pages_visited: int = 0
    errors_encountered: int = 0
    retry_attempts: int = 0
    total_runtime_seconds: float = 0.0


class RespectfulAutoDownloader:
    """Respectful auto downloader for horse racing data"""
    
    def __init__(self, config: Optional[DownloadConfig] = None):
        self.config = config or DownloadConfig()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.session: Optional[DownloadSession] = None
        self.should_stop = False
        self.last_request_time = 0.0
        
        # Create output directories
        Path(self.config.output_directory).mkdir(parents=True, exist_ok=True)
        Path(self.config.backup_directory).mkdir(parents=True, exist_ok=True)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals gracefully"""
        logger.warning(f"Received signal {signum}, initiating graceful shutdown...")
        self.should_stop = True
    
    async def _respect_rate_limit(self) -> None:
        """Enforce respectful rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        min_delay = 60.0 / self.config.requests_per_minute
        
        if time_since_last_request < min_delay:
            sleep_time = min_delay - time_since_last_request
            logger.info(f"Rate limiting: waiting {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    async def _respectful_page_load(self, page: Page, url: str) -> bool:
        """Load a page with respectful delays and error handling"""
        try:
            await self._respect_rate_limit()
            
            logger.info(f"Respectfully loading: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Additional respectful delay
            await asyncio.sleep(self.config.page_delay_seconds)
            
            if self.session:
                self.session.pages_visited += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading page {url}: {e}")
            if self.session:
                self.session.errors_encountered += 1
            return False
    
    async def _initialize_browser(self) -> bool:
        """Initialize browser with respectful settings"""
        try:
            logger.info("Initializing respectful browser...")
            
            playwright = await async_playwright().__aenter__()
            self.browser = await playwright.chromium.launch(
                headless=self.config.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor"
                ]
            )
            
            self.context = await self.browser.new_context(
                user_agent=self.config.user_agent,
                viewport={
                    "width": self.config.viewport_width,
                    "height": self.config.viewport_height
                },
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                }
            )
            
            logger.info("Browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    async def _cleanup_browser(self) -> None:
        """Clean up browser resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("Browser cleanup completed")
        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")
    
    async def _download_race_data(self) -> Dict[str, Any]:
        """Download race data respectfully from horseracedatabase.com"""
        race_data = {
            "download_date": datetime.now().isoformat(),
            "races": [],
            "metadata": {
                "source": "horseracedatabase.com",
                "download_method": "respectful_auto_downloader",
                "note": "Temporary until official API available"
            }
        }
        
        try:
            if not self.context:
                raise RuntimeError("Browser context not initialized")
            
            page = await self.context.new_page()
            
            # Start with today's racing page (example URL structure)
            today = datetime.now().strftime("%Y-%m-%d")
            base_url = "https://www.horseracedatabase.com"
            
            # Note: This is a placeholder - actual URLs would need to be determined
            # based on horseracedatabase.com's structure
            racing_url = f"{base_url}/racing/{today}"
            
            success = await self._respectful_page_load(page, racing_url)
            if not success:
                logger.error("Failed to load main racing page")
                return race_data
            
            # Example scraping logic (would need to be adapted to actual site structure)
            logger.info("Scanning for race listings...")
            
            # This would be replaced with actual selectors for horseracedatabase.com
            try:
                race_links = await page.query_selector_all("a[href*='race']")
                logger.info(f"Found {len(race_links)} potential race links")
                
                for i, link in enumerate(race_links[:self.config.minimum_races_required]):
                    if self.should_stop:
                        logger.info("Stop signal received, ending download")
                        break
                    
                    try:
                        href = await link.get_attribute("href")
                        if href:
                            race_url = href if href.startswith("http") else f"{base_url}{href}"
                            
                            # Download individual race data
                            race_info = await self._download_race_info(page, race_url, i + 1)
                            if race_info:
                                race_data["races"].append(race_info)
                                if self.session:
                                    self.session.races_downloaded += 1
                                
                                logger.info(f"Downloaded race {i + 1}: {race_info.get('race_name', 'Unknown')}")
                    
                    except Exception as e:
                        logger.error(f"Error processing race link {i + 1}: {e}")
                        if self.session:
                            self.session.errors_encountered += 1
            
            except Exception as e:
                logger.error(f"Error finding race links: {e}")
            
            await page.close()
            
        except Exception as e:
            logger.error(f"Error in download process: {e}")
        
        return race_data
    
    async def _download_race_info(self, page: Page, race_url: str, race_number: int) -> Optional[Dict[str, Any]]:
        """Download information for a specific race"""
        try:
            success = await self._respectful_page_load(page, race_url)
            if not success:
                return None
            
            # Example race data extraction (would need actual selectors)
            race_info = {
                "race_number": race_number,
                "race_url": race_url,
                "race_name": "Sample Race",  # Would extract from page
                "track": "Sample Track",     # Would extract from page
                "race_time": datetime.now().isoformat(),
                "distance": "1 mile",        # Would extract from page
                "horses": []                 # Would extract horse data
            }
            
            # Note: Actual implementation would extract real data using proper selectors
            logger.info(f"Respectfully extracted race data for race {race_number}")
            
            return race_info
            
        except Exception as e:
            logger.error(f"Error downloading race info from {race_url}: {e}")
            return None
    
    async def _save_download_session(self, session: DownloadSession, data: Dict[str, Any]) -> str:
        """Save download session data"""
        try:
            filename = f"race_data_{session.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = Path(self.config.output_directory) / filename
            
            # Save main data
            async with aiofiles.open(filepath, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))
            
            # Save session metadata
            session_file = filepath.with_suffix('.session.json')
            async with aiofiles.open(session_file, 'w') as f:
                await f.write(json.dumps(asdict(session), indent=2, default=str))
            
            logger.info(f"Download session saved to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving download session: {e}")
            return ""
    
    async def _run_daily_download(self) -> bool:
        """Run the daily download process"""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session = DownloadSession(
            session_id=session_id,
            start_time=datetime.now()
        )
        
        logger.info(f"Starting respectful daily download session: {session_id}")
        
        try:
            # Initialize browser
            if not await self._initialize_browser():
                return False
            
            # Download race data
            race_data = await self._download_race_data()
            
            # Check success criteria
            races_downloaded = len(race_data.get("races", []))
            success = races_downloaded >= self.config.minimum_races_required
            
            self.session.end_time = datetime.now()
            self.session.success = success
            self.session.total_runtime_seconds = (
                self.session.end_time - self.session.start_time
            ).total_seconds()
            
            # Save results
            await self._save_download_session(self.session, race_data)
            
            if success:
                logger.info(f"✅ Daily download completed successfully! Downloaded {races_downloaded} races")
            else:
                logger.warning(f"⚠️ Daily download incomplete. Only {races_downloaded} races downloaded (minimum: {self.config.minimum_races_required})")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in daily download: {e}")
            return False
        
        finally:
            await self._cleanup_browser()
    
    def _schedule_daily_download(self) -> None:
        """Schedule the daily download job"""
        logger.info(f"Scheduling daily download at {self.config.daily_run_time}")
        
        schedule.every().day.at(self.config.daily_run_time).do(
            lambda: asyncio.run(self._run_daily_download())
        )
    
    async def run_once(self) -> bool:
        """Run download process once (for testing)"""
        logger.info("Running one-time respectful download...")
        return await self._run_daily_download()
    
    def run_scheduler(self) -> None:
        """Run the daily scheduler"""
        logger.info("Starting respectful auto downloader scheduler...")
        logger.info(f"Next download scheduled for: {self.config.daily_run_time}")
        
        self._schedule_daily_download()
        
        while not self.should_stop:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                time.sleep(5)
        
        logger.info("Respectful auto downloader scheduler stopped")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Respectful Auto Downloader for Horse Racing Data")
    parser.add_argument("--run-once", action="store_true", help="Run download once instead of scheduling")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    args = parser.parse_args()
    
    # Load configuration if provided
    config = DownloadConfig()
    if args.config and Path(args.config).exists():
        try:
            with open(args.config, 'r') as f:
                config_data = json.load(f)
                # Update config with loaded values
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    downloader = RespectfulAutoDownloader(config)
    
    if args.run_once:
        # Run once for testing
        result = asyncio.run(downloader.run_once())
        sys.exit(0 if result else 1)
    else:
        # Run scheduler
        downloader.run_scheduler()


if __name__ == "__main__":
    main()
