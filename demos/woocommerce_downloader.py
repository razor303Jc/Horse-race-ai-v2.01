#!/usr/bin/env python3
"""
WooCommerce Horse Race Database Auto-Downloader
==============================================

Handles WooCommerce-specific download patterns from horseracedatabase.com:
1. Handles newsletter modals and popups
2. Uses direct download URLs with order parameters
3. Manages WooCommerce authentication and downloads
"""

import asyncio
import logging
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)
from rich.console import Console
from rich.panel import Panel

# Load environment variables
load_dotenv()

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WooCommerceDownloader:
    """WooCommerce-aware downloader for horseracedatabase.com"""

    def __init__(self):
        self.console = console
        self.download_dir = Path("downloads/horseracedatabase")
        self.data_dir = Path("data/horseracedatabase")

        # Create directories
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Get credentials from environment
        self.username = os.getenv("HORSERACE_DB_USERNAME")
        self.password = os.getenv("HORSERACE_DB_PASSWORD")

        if not self.username or not self.password:
            raise ValueError(
                "Missing HORSERACE_DB_USERNAME or HORSERACE_DB_PASSWORD in .env file"
            )

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    async def _human_type(
        self, element, text: str, delay_range: tuple = (50, 150)
    ) -> None:
        """Type text character by character with human-like delays."""
        # Clear the field first
        await element.click()
        await element.press("Control+a")
        await element.press("Delete")

        # Type each character with random delays
        for char in text:
            await element.type(char)
            # Random delay between characters (50-150ms)
            delay = random.randint(delay_range[0], delay_range[1])
            await asyncio.sleep(delay / 1000)  # Convert to seconds

        # Small pause after typing like a human would
        await asyncio.sleep(random.randint(200, 500) / 1000)

    async def _human_scroll(self, page: Page) -> None:
        """Scroll page naturally like a human would."""
        # Random scroll amount
        scroll_amount = random.randint(200, 800)

        # Scroll down with slight variations
        for _ in range(3):
            await page.mouse.wheel(0, scroll_amount + random.randint(-50, 50))
            await asyncio.sleep(random.randint(500, 1500) / 1000)

    async def _human_page_interaction(self, page: Page) -> None:
        """Add human-like page interactions."""
        # Random mouse movements
        width = 1920
        height = 1080

        # Move mouse to random positions
        for _ in range(random.randint(1, 3)):
            x = random.randint(100, width - 100)
            y = random.randint(100, height - 100)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.randint(300, 800) / 1000)

    async def start_browser(self, headless: bool = True) -> bool:
        """Start browser with anti-detection settings and Docker support."""
        try:
            playwright = await async_playwright().start()

            # Docker-optimized browser arguments
            browser_args = [
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",  # Speed up loading in container
                "--disable-javascript-harmony-shipping",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--disable-ipc-flooding-protection",
                "--memory-pressure-off",
                "--max_old_space_size=4096",
                "--single-process",  # Important for containers
            ]

            self.browser = await playwright.chromium.launch(
                headless=headless,
                args=browser_args,
            )

            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                },
            )

            logger.info(f"Browser started successfully (headless={headless})")
            return True

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False

    async def handle_newsletter_modal(self, page: Page) -> bool:
        """Handle newsletter signup modal that blocks login."""
        try:
            logger.info("Checking for newsletter modal...")

            # Wait a bit for modals to appear
            await page.wait_for_timeout(2000)

            # Common modal close selectors
            close_selectors = [
                '[aria-label="Close"]',
                ".close",
                ".modal-close",
                ".popup-close",
                'button:has-text("×")',
                'button:has-text("Close")',
                'button:has-text("No thanks")',
                '[data-dismiss="modal"]',
                ".newsletter-close",
                ".popup-overlay .close",
            ]

            for selector in close_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0 and await element.is_visible():
                        await element.click()
                        logger.info(f"Closed modal using selector: {selector}")
                        await page.wait_for_timeout(1000)
                        return True
                except:
                    continue

            # Try pressing Escape key to close modal
            try:
                await page.keyboard.press("Escape")
                logger.info("Tried closing modal with Escape key")
                await page.wait_for_timeout(1000)
            except:
                pass

            return True

        except Exception as e:
            logger.error(f"Modal handling failed: {e}")
            return False

    async def login(self, page: Page) -> bool:
        """Login to horseracedatabase.com with WooCommerce handling."""
        try:
            logger.info("Navigating to horseracedatabase.com login...")
            await page.goto("https://horseracedatabase.com/my-account/", timeout=30000)

            # Handle newsletter modal first
            await self.handle_newsletter_modal(page)

            # Check if already logged in
            if (
                "downloads" in page.url
                or await page.locator(".woocommerce-account").count() > 0
            ):
                logger.info("Already logged in!")
                return True

            # Fill username/email
            username_selectors = [
                "#username",
                'input[name="username"]',
                'input[type="email"]',
                "#user_login",
                ".username input",
            ]

            username_filled = False
            for selector in username_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        # Type safety check
                        assert self.username is not None, "Username not configured"
                        await self._human_type(element, self.username)
                        username_filled = True
                        logger.info(f"Username filled using selector: {selector}")
                        break
                except Exception:
                    continue

            if not username_filled:
                logger.error("Could not find username field")
                return False

            # Fill password
            password_selectors = [
                "#password",
                'input[name="password"]',
                'input[type="password"]',
                "#user_pass",
                ".password input",
            ]

            password_filled = False
            for selector in password_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        # Type safety check
                        assert self.password is not None, "Password not configured"
                        await self._human_type(element, self.password)
                        password_filled = True
                        logger.info(f"Password filled using selector: {selector}")
                        break
                except Exception:
                    continue

            if not password_filled:
                logger.error("Could not find password field")
                return False

            # Submit login
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Sign In")',
                'input[value*="Login"]',
                ".woocommerce-form-login button",
            ]

            for selector in submit_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        await element.click()
                        logger.info(f"Login submitted using: {selector}")
                        break
                except:
                    continue

            # Wait for navigation
            await page.wait_for_load_state("networkidle", timeout=10000)

            # Check login success
            current_url = page.url
            if (
                "downloads" in current_url
                or "my-account" in current_url
                or await page.locator(".woocommerce-account").count() > 0
            ):
                logger.info("✅ Login successful!")
                return True
            else:
                logger.warning(f"Login may have failed - current URL: {current_url}")
                return False

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    async def download_direct_url(
        self, page: Page, url: str, file_type: str
    ) -> Optional[Path]:
        """Download file from direct WooCommerce URL."""
        try:
            logger.info(f"Downloading {file_type} from: {url}")

            # Start waiting for download
            async with page.expect_download() as download_info:
                await page.goto(url)

            download = await download_info.value

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{file_type}_{timestamp}.zip"
            file_path = self.download_dir / filename

            # Save download
            await download.save_as(file_path)

            logger.info(f"✅ Downloaded {file_type} to: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Download failed for {file_type}: {e}")
            return None

    async def run_with_direct_urls(
        self, results_url: str = None, cards_url: str = None, headless: bool = True
    ) -> Dict[str, bool]:
        """Run downloader with direct WooCommerce URLs."""
        results = {"results": False, "cards": False}

        try:
            if not await self.start_browser(headless=headless):
                return results

            page = await self.context.new_page()

            # Login first
            if not await self.login(page):
                logger.error("Login failed")
                return results

            # Navigate to downloads page
            await page.goto(
                "https://horseracedatabase.com/my-account/downloads/", timeout=30000
            )
            await page.wait_for_load_state("networkidle")

            # Download results if URL provided
            if results_url:
                results_file = await self.download_direct_url(
                    page, results_url, "results"
                )
                if results_file:
                    results["results"] = True
                    logger.info(f"Results downloaded: {results_file}")

            # Download cards if URL provided
            if cards_url:
                cards_file = await self.download_direct_url(page, cards_url, "cards")
                if cards_file:
                    results["cards"] = True
                    logger.info(f"Cards downloaded: {cards_file}")

            return results

        except Exception as e:
            logger.error(f"Download process failed: {e}")
            return results

        finally:
            if self.browser:
                await self.browser.close()

    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()


async def main():
    """Main function to test the WooCommerce downloader."""
    console.print(
        Panel.fit(
            "🏇 WooCommerce Horse Race Database Auto-Downloader\n"
            "Handles newsletter modals and WooCommerce downloads",
            title="WooCommerce Downloader",
        )
    )

    try:
        downloader = WooCommerceDownloader()

        # Example URLs - replace with actual URLs from your account
        results_url = "https://horseracedatabase.com/?download_file=17605&order=wc_order_CdJf7udYlJDk3&email=justin.d.crooke%40gmail.com&key=6e9e40dd-781e-45fa-8f14-dc54734dd36f"
        cards_url = None  # Add cards URL here if you have it

        results = await downloader.run_with_direct_urls(results_url, cards_url)

        console.print("\n📊 Download Results:")
        for file_type, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            console.print(f"  • {file_type.title()}: {status}")

        if any(results.values()):
            console.print(
                "🎉 [bold green]Downloads completed successfully![/bold green]"
            )
        else:
            console.print("⚠️ [bold yellow]No files were downloaded[/bold yellow]")

    except Exception as e:
        console.print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
