"""Playwright-based web scraping for horse racing data."""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from ..core.config import config

logger = structlog.get_logger(__name__)


@dataclass
class RaceData:
    """Data structure for race information."""

    race_id: str
    track: str
    race_number: int
    race_time: datetime
    distance: str
    surface: str
    horses: List[Dict[str, Any]]
    conditions: str
    purse: Optional[float] = None


@dataclass
class HorseData:
    """Data structure for individual horse information."""

    name: str
    jockey: str
    trainer: str
    weight: int
    odds: Optional[float] = None
    post_position: int = 0
    form: Optional[str] = None
    speed_figures: Optional[Dict[str, int]] = None


class PlaywrightScraper:
    """Playwright-based web scraper for horse racing data."""

    def __init__(self) -> None:
        """Initialize the scraper."""
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.config = config.scraping

    async def __aenter__(self) -> "PlaywrightScraper":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()

    async def start(self) -> None:
        """Start the browser and create context."""
        logger.info("Starting Playwright browser")

        playwright = await async_playwright().__aenter__()
        self.browser = await playwright.chromium.launch(
            headless=self.config.headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

        self.context = await self.browser.new_context(
            user_agent=self.config.user_agent, viewport={"width": 1920, "height": 1080}
        )

        # Set default timeout
        self.context.set_default_timeout(self.config.timeout)

        logger.info("Browser started successfully")

    async def stop(self) -> None:
        """Stop the browser and clean up."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Browser stopped")

    async def create_page(self) -> Page:
        """Create a new page in the browser context."""
        if not self.context:
            raise RuntimeError("Browser context not initialized. Call start() first.")

        page = await self.context.new_page()

        # Add request interceptors for efficiency
        await page.route(
            "**/*.{png,jpg,jpeg,gif,svg,css,font,woff,woff2}",
            lambda route: route.abort(),
        )

        return page

    async def login_to_site(
        self, page: Page, url: str, username: str, password: str
    ) -> bool:
        """Generic login function for racing websites."""
        try:
            logger.info(f"Attempting to login to {url}")

            await page.goto(url)
            await page.wait_for_load_state("networkidle")

            # Look for common login form selectors
            login_selectors = [
                'input[name="username"], input[name="email"], input[type="email"]',
                'input[name="password"], input[name="password"]',
                'button[type="submit"], input[type="submit"], button:has-text("Login")',
            ]

            # Fill username
            username_field = await page.locator(login_selectors[0]).first
            await username_field.fill(username)

            # Fill password
            password_field = await page.locator(login_selectors[1]).first
            await password_field.fill(password)

            # Submit form
            submit_button = await page.locator(login_selectors[2]).first
            await submit_button.click()

            # Wait for navigation or error
            await page.wait_for_load_state("networkidle")

            # Check if login was successful
            current_url = page.url
            login_success = url not in current_url or "dashboard" in current_url.lower()

            if login_success:
                logger.info("Login successful")
            else:
                logger.warning("Login may have failed - still on login page")

            return login_success

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    async def scrape_race_data(self, page: Page, race_url: str) -> Optional[RaceData]:
        """Scrape race data from a specific race page."""
        try:
            logger.info(f"Scraping race data from {race_url}")

            await page.goto(race_url)
            await page.wait_for_load_state("networkidle")

            # Extract race metadata (this would be customized per site)
            race_title = await page.locator("h1, .race-title").first.inner_text()
            race_info = await self._extract_race_info(page)
            horses = await self._extract_horse_data(page)

            race_data = RaceData(
                race_id=f"race_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                track=race_info.get("track", "Unknown"),
                race_number=race_info.get("race_number", 1),
                race_time=race_info.get("race_time", datetime.now()),
                distance=race_info.get("distance", "Unknown"),
                surface=race_info.get("surface", "Unknown"),
                conditions=race_info.get("conditions", "Unknown"),
                horses=horses,
                purse=race_info.get("purse"),
            )

            logger.info(f"Successfully scraped data for race {race_data.race_id}")
            return race_data

        except Exception as e:
            logger.error(f"Failed to scrape race data: {e}")
            return None

    async def _extract_race_info(self, page: Page) -> Dict[str, Any]:
        """Extract race metadata from the page."""
        # This would be customized based on the specific racing website structure
        race_info = {}

        try:
            # Example selectors - would need to be adapted for specific sites
            track = await page.locator(".track-name, .venue").first.inner_text()
            race_info["track"] = track.strip()
        except Exception:
            pass

        try:
            distance = await page.locator(
                ".distance, .race-distance"
            ).first.inner_text()
            race_info["distance"] = distance.strip()
        except Exception:
            pass

        return race_info

    async def _extract_horse_data(self, page: Page) -> List[Dict[str, Any]]:
        """Extract horse data from the race page."""
        horses = []

        try:
            # Find horse entries - adapt selectors for specific sites
            horse_rows = await page.locator(".horse-entry, .runner, tbody tr").all()

            for row in horse_rows:
                try:
                    horse_data = {}

                    # Extract horse name
                    name_element = await row.locator(".horse-name, .runner-name").first
                    horse_data["name"] = await name_element.inner_text()

                    # Extract jockey
                    jockey_element = await row.locator(".jockey, .rider").first
                    horse_data["jockey"] = await jockey_element.inner_text()

                    # Extract odds if available
                    try:
                        odds_element = await row.locator(".odds, .price").first
                        odds_text = await odds_element.inner_text()
                        horse_data["odds"] = self._parse_odds(odds_text)
                    except Exception:
                        horse_data["odds"] = None

                    horses.append(horse_data)

                except Exception as e:
                    logger.warning(f"Failed to extract data for a horse: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to extract horse data: {e}")

        return horses

    def _parse_odds(self, odds_text: str) -> Optional[float]:
        """Parse odds from text format."""
        try:
            # Handle different odds formats
            odds_text = odds_text.strip()

            if "/" in odds_text:  # Fractional odds
                numerator, denominator = odds_text.split("/")
                return float(numerator) / float(denominator) + 1
            elif odds_text.replace(".", "").isdigit():  # Decimal odds
                return float(odds_text)
            else:
                return None
        except Exception:
            return None

    async def save_screenshot(self, page: Page, filename: str) -> Path:
        """Save a screenshot of the current page."""
        screenshot_dir = config.data_dir / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)

        screenshot_path = (
            screenshot_dir
            / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        await page.screenshot(path=str(screenshot_path), full_page=True)

        logger.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path

    async def scrape_race_cards(self) -> List[RaceData]:
        """Scrape race cards for today's races."""
        try:
            logger.info("Starting race card scraping")

            # Example race URLs - in production this would come from a config or API
            race_urls = [
                "https://www.example-racing-site.com/today",
                # Add more URLs as needed
            ]

            race_cards = []

            if not self.context:
                await self.start()

            for url in race_urls:
                try:
                    page = await self.create_page()
                    race_data = await self.scrape_race_data(page, url)
                    if race_data:
                        race_cards.append(race_data)
                    await page.close()
                except Exception as e:
                    logger.error(f"Failed to scrape race from {url}: {e}")
                    continue

            logger.info(f"Successfully scraped {len(race_cards)} race cards")
            return race_cards

        except Exception as e:
            logger.error(f"Race card scraping failed: {e}")
            return []

    async def update_race_data(self) -> bool:
        """Update existing race data with latest information."""
        try:
            logger.info("Updating race data")

            # In production, this would update existing race data
            # For now, we'll just scrape fresh data
            race_cards = await self.scrape_race_cards()

            logger.info(f"Updated data for {len(race_cards)} races")
            return len(race_cards) > 0

        except Exception as e:
            logger.error(f"Race data update failed: {e}")
            return False

    async def collect_results(self) -> List[Dict]:
        """Collect race results for completed races."""
        try:
            logger.info("Collecting race results")

            # Example implementation - would scrape actual results
            results = []

            if not self.context:
                await self.start()

            # In production, this would scrape actual race results
            # For now, return empty list

            logger.info(f"Collected {len(results)} race results")
            return results

        except Exception as e:
            logger.error(f"Result collection failed: {e}")
            return []

    async def run_maintenance(self) -> bool:
        """Run maintenance tasks like cleaning up old data."""
        try:
            logger.info("Running maintenance tasks")

            # Example maintenance tasks:
            # - Clean up old screenshots
            # - Clear browser cache
            # - Remove temporary files

            # Clean up old screenshots (older than 7 days)
            try:
                screenshot_dir = config.data_dir / "screenshots"
                if screenshot_dir.exists():
                    from datetime import timedelta

                    cutoff_time = datetime.now() - timedelta(days=7)

                    for screenshot_file in screenshot_dir.glob("*.png"):
                        file_time = datetime.fromtimestamp(
                            screenshot_file.stat().st_mtime
                        )
                        if file_time < cutoff_time:
                            screenshot_file.unlink()
                            logger.info(
                                f"Deleted old screenshot: {screenshot_file.name}"
                            )
            except Exception as e:
                logger.warning(f"Screenshot cleanup failed: {e}")

            logger.info("Maintenance tasks completed successfully")
            return True

        except Exception as e:
            logger.error(f"Maintenance tasks failed: {e}")
            return False
