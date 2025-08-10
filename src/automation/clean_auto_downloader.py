#!/usr/bin/env python3
"""
Clean Playwright Auto Downloader
================================

Rebuilt from scratch using Qwen2.5 recommendations:
- Uses Python Playwright for browser automation
- Handles WooCommerce login flow at https://horseracedatabase.com/my-account/
- Extracts session cookies after login
- Downloads files using aiohttp with session cookies
- Production-ready for Docker containers
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles
import aiohttp
from dotenv import load_dotenv
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CleanAutoDownloader:
    """Clean Playwright-based auto downloader for horseracedatabase.com"""

    def __init__(self):
        self.download_dir = Path("data/downloads")
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # Get credentials from environment
        self.username = os.getenv("HORSERACE_DB_USERNAME", "")
        self.password = os.getenv("HORSERACE_DB_PASSWORD", "")
        self.results_url = os.getenv("HORSERACE_DB_RESULTS_URL", "")
        self.cards_url = os.getenv("HORSERACE_DB_CARDS_URL", "")

        if not all([self.username, self.password, self.results_url, self.cards_url]):
            raise ValueError("Missing required environment variables")

    async def handle_newsletter_modal(self, page: Page) -> None:
        """Handle newsletter modal if present"""
        try:
            # Try different selectors for the newsletter modal close button
            selectors = [
                '[aria-label="Close"]',
                ".modal-close",
                ".newsletter-close",
                'button[data-dismiss="modal"]',
                ".close",
            ]

            for selector in selectors:
                try:
                    await page.wait_for_selector(selector, timeout=2000)
                    await page.click(selector)
                    logger.info(f"Closed newsletter modal using selector: {selector}")
                    await asyncio.sleep(1)  # Wait for modal to close
                    break
                except Exception:
                    continue

        except Exception:
            logger.info("No newsletter modal found or already closed")

    async def login_and_extract_cookies(self) -> List[Dict[str, str]]:
        """Login to horseracedatabase.com and extract session cookies"""
        async with async_playwright() as playwright:
            # Launch browser (headless in production)
            headless = os.getenv("HEADLESS", "true").lower() == "true"
            browser = await playwright.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                logger.info("Navigating to login page...")
                await page.goto("https://horseracedatabase.com/my-account/")

                # Handle newsletter modal
                await self.handle_newsletter_modal(page)

                # Wait for login form
                await page.wait_for_selector('input[name="username"]', timeout=10000)
                logger.info("Found login form")

                # Fill login form
                await page.fill('input[name="username"]', self.username)
                await page.fill('input[name="password"]', self.password)

                # Submit login
                await page.click('button[type="submit"]')
                logger.info("Login submitted")

                # Wait for navigation (successful login)
                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                    logger.info("Login completed successfully")
                except:
                    logger.warning("Login status unclear - proceeding")

                # Extract cookies
                cookies = await context.cookies()
                logger.info(f"Extracted {len(cookies)} cookies from session")

                # Convert to dict format
                cookie_dicts = [
                    {"name": cookie.get("name", ""), "value": cookie.get("value", "")}
                    for cookie in cookies
                ]

                return cookie_dicts

            finally:
                await browser.close()

    async def download_file(
        self, session: aiohttp.ClientSession, url: str, filename: str
    ) -> bool:
        """Download a file using the authenticated session"""
        try:
            logger.info(f"Downloading {filename}...")
            async with session.get(url) as response:
                if response.status == 200:
                    file_path = self.download_dir / f"{filename}.zip"
                    async with aiofiles.open(file_path, mode="wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)

                    logger.info(f"Successfully downloaded {filename} to {file_path}")
                    return True
                else:
                    logger.error(
                        f"Failed to download {filename}: HTTP {response.status}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Error downloading {filename}: {e}")
            return False

    async def download_files_with_cookies(self, cookies: List[Dict]) -> bool:
        """Download files using session cookies"""
        # Convert Playwright cookies to aiohttp format
        cookie_jar = aiohttp.CookieJar()
        for cookie in cookies:
            cookie_jar.update_cookies({cookie["name"]: cookie["value"]})

        async with aiohttp.ClientSession(cookie_jar=cookie_jar) as session:
            tasks = [
                self.download_file(session, self.results_url, "results"),
                self.download_file(session, self.cards_url, "cards"),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check if all downloads succeeded
            success_count = sum(1 for result in results if result is True)
            total_count = len(tasks)

            logger.info(
                f"Download completed: {success_count}/{total_count} files successful"
            )
            return success_count == total_count

    async def run_download(self) -> bool:
        """Main download process"""
        try:
            logger.info("Starting clean auto downloader...")

            # Step 1: Login and extract cookies
            cookies = await self.login_and_extract_cookies()
            if not cookies:
                logger.error("Failed to extract session cookies")
                return False

            # Step 2: Download files using cookies
            success = await self.download_files_with_cookies(cookies)

            if success:
                logger.info("✅ Auto download completed successfully!")
                return True
            else:
                logger.error("❌ Auto download failed")
                return False

        except Exception as e:
            logger.error(f"Auto download error: {e}")
            return False


async def main():
    """Main entry point"""
    downloader = CleanAutoDownloader()
    success = await downloader.run_download()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
