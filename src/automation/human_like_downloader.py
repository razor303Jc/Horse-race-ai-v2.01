#!/usr/bin/env python3
"""
Horse Race Database Auto-Download System
===================================

Uses Playwright to automate downloading ZIP files from horseracedatabase.com:
1. Navigate to https://horseracedatabase.com/my-account/downloads/
2. Login with credentials from .env file
3. Use session cookies to download ZIP files via HTTP requests
4. Extract and organize the data
"""

import asyncio
import json
import logging
import os
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiofiles
import aiohttp
import requests  # Add requests for NTFY notifications
from dotenv import load_dotenv
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# Load environment variables
load_dotenv()

console = Console()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HorseRaceDatabaseDownloader:
    """Automated ZIP file downloader for horseracedatabase.com"""

    def __init__(self):
        self.console = console
        self.download_dir = Path("data/horseracedatabase")
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # Load credentials from environment
        self.username = os.getenv("HORSERACE_DB_USERNAME")
        self.password = os.getenv("HORSERACE_DB_PASSWORD")

        if not self.username or not self.password:
            raise ValueError(
                "Missing HORSERACE_DB_USERNAME or HORSERACE_DB_PASSWORD in .env file"
            )

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    def send_ntfy_notification(
        self, title: str, message: str, priority: str = "default"
    ) -> None:
        """Send notification to NTFY server."""
        try:
            url = "http://localhost:8081/horse-racing-alerts"
            headers = {
                "Title": title,
                "Priority": priority,
                "Tags": "horse,racing,download",
            }
            response = requests.post(url, data=message, headers=headers)
            if response.status_code == 200:
                logger.info(f"✅ NTFY notification sent: {title}")
            else:
                logger.warning(f"❌ NTFY notification failed: {response.status_code}")
        except Exception as e:
            logger.warning(f"❌ NTFY notification error: {e}")

    async def start_browser(self) -> None:
        """Start Playwright browser with download configuration."""
        playwright = await async_playwright().start()

        self.browser = await playwright.chromium.launch(
            headless=False,  # Keep visible for debugging
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )

        # Create context with download directory
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            accept_downloads=True,
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        logger.info("Browser started successfully")

    async def stop_browser(self) -> None:
        """Stop browser and cleanup."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Browser closed")

    async def human_type(self, element, text: str, delay_range: tuple = (50, 150)):
        """Type text character by character with human-like delays."""
        import random

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

    async def handle_newsletter_modal(self, page: Page) -> None:
        """Handle newsletter popup modals that may appear on the site."""
        try:
            # Wait a moment for any modals to appear
            await asyncio.sleep(2)

            # Common modal close selectors
            modal_close_selectors = [
                '[data-dismiss="modal"]',
                ".modal-close",
                ".close",
                'button:has-text("Close")',
                'button:has-text("×")',
                ".newsletter-close",
                '[aria-label="Close"]',
                ".popup-close",
                ".newsletter-popup .close",
                "#newsletter-modal .close",
            ]

            for selector in modal_close_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.locator(selector).first.click()
                        logger.info(f"Closed modal using selector: {selector}")
                        await asyncio.sleep(1)
                        break
                except Exception:
                    continue

            # Also try pressing Escape key
            try:
                await page.keyboard.press("Escape")
                await asyncio.sleep(0.5)
            except Exception:
                pass

        except Exception as e:
            logger.debug(f"Newsletter modal handling error (non-critical): {e}")

    async def login_to_site(self, page: Page) -> bool:
        """Login to horseracedatabase.com with credentials from .env"""
        try:
            logger.info("Navigating to horseracedatabase.com login...")

            # Try multiple login entry points
            login_urls = [
                "https://horseracedatabase.com/my-account/",
                "https://horseracedatabase.com/wp-login.php",
                "https://horseracedatabase.com/login/",
                "https://horseracedatabase.com/my-account/downloads/",
            ]

            login_form_found = False

            for login_url in login_urls:
                try:
                    logger.info(f"Trying login URL: {login_url}")
                    await page.goto(login_url)
                    await page.wait_for_load_state("networkidle", timeout=15000)

                    # Handle potential newsletter modal
                    await self.handle_newsletter_modal(page)

                    # Check current URL
                    current_url = page.url.lower()
                    logger.info(f"Current URL: {current_url}")

                    # Look for login form elements
                    has_username = (
                        await page.locator(
                            'input[name="username"], input[name="email"], input[type="email"]'
                        ).count()
                        > 0
                    )
                    has_password = (
                        await page.locator(
                            'input[name="password"], input[type="password"]'
                        ).count()
                        > 0
                    )

                    logger.info(
                        f"Username field found: {has_username}, Password field found: {has_password}"
                    )

                    if has_username and has_password:
                        logger.info("Found login form - proceeding with login...")
                        login_form_found = True
                        break

                except Exception as e:
                    logger.warning(f"Failed to load {login_url}: {e}")
                    continue

            if not login_form_found:
                logger.error("Could not find a working login page with form")
                return False

            # Check if we need to login
            current_url = page.url.lower()
            if (
                "login" in current_url
                or "signin" in current_url
                or "my-account" in current_url
                or login_form_found
            ):
                logger.info("Filling login credentials...")

                # Find and fill username/email field
                username_selectors = [
                    'input[name="username"]',
                    'input[name="email"]',
                    'input[type="email"]',
                    'input[id*="username"]',
                    'input[id*="email"]',
                ]

                username_filled = False
                for selector in username_selectors:
                    try:
                        element = page.locator(selector).first
                        if await element.count() > 0:
                            # Use human-like typing instead of instant fill
                            await self.human_type(element, self.username)
                            username_filled = True
                            logger.info(
                                f"Username typed humanly using selector: {selector}"
                            )
                            break
                    except:
                        continue

                if not username_filled:
                    logger.error("Could not find username field")
                    return False

                # Find and fill password field
                password_selectors = [
                    'input[name="password"]',
                    'input[type="password"]',
                    'input[id*="password"]',
                ]

                password_filled = False
                for selector in password_selectors:
                    try:
                        element = page.locator(selector).first
                        if await element.count() > 0:
                            # Use human-like typing instead of instant fill
                            await self.human_type(element, self.password)
                            password_filled = True
                            logger.info(
                                f"Password typed humanly using selector: {selector}"
                            )
                            break
                    except:
                        continue

                if not password_filled:
                    logger.error("Could not find password field")
                    return False

                # Submit login form with human-like pause
                await asyncio.sleep(0.5)  # Brief pause like a human would do

                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Login")',
                    'button:has-text("Sign In")',
                    'input[value*="Login"]',
                    'input[value*="Log in"]',
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

                # Wait for navigation after login
                await page.wait_for_load_state("networkidle", timeout=10000)

                # Check if login was successful
                new_url = page.url
                if "downloads" in new_url or "my-account" in new_url:
                    # Check for logout link or user menu to confirm login
                    logout_selectors = [
                        'a:has-text("Logout")',
                        'a:has-text("Sign out")',
                        ".logout",
                        '[href*="logout"]',
                    ]
                    logged_in = False
                    for logout_selector in logout_selectors:
                        if await page.locator(logout_selector).count() > 0:
                            logged_in = True
                            break

                    if logged_in:
                        logger.info("✅ Login successful!")
                        return True
                    else:
                        logger.warning("Login status unclear - proceeding")
                        return True
                else:
                    logger.warning(f"Login may have failed - current URL: {new_url}")
                    return False
            else:
                logger.info("Already logged in!")
                return True

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    async def get_session_cookies(self) -> Dict[str, str]:
        """
        Extract session cookies from current Playwright browser session.

        Returns:
            Dict with cookie names and values
        """
        try:
            if not self.context:
                logger.error("No browser context available")
                return {}

            # Get cookies from current context
            cookies = await self.context.cookies()

            # Convert to dict format for requests
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie["name"]] = cookie["value"]

            logger.info(f"Extracted {len(cookie_dict)} cookies from session")
            return cookie_dict

        except Exception as e:
            logger.error(f"Failed to extract cookies: {e}")
            return {}

    async def download_file_with_session(
        self, url: str, file_type: str, cookies: Dict[str, str]
    ) -> bool:
        """
        Download a file using session cookies from Playwright login.

        Args:
            url: Download URL
            file_type: Type of file (results/cards) for naming
            cookies: Session cookies from Playwright

        Returns:
            bool: True if download successful
        """
        try:
            # Create aiohttp session with cookies
            jar = aiohttp.CookieJar()
            for name, value in cookies.items():
                jar.update_cookies({name: value})

            async with aiohttp.ClientSession(
                cookie_jar=jar,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                },
            ) as session:

                self.console.print(f"[cyan]📥 Downloading {file_type} data...[/cyan]")

                async with session.get(url) as response:
                    status = response.status
                    content_type = response.headers.get("content-type", "").lower()

                    self.console.print(f"[blue]Status: {status}[/blue]")
                    self.console.print(f"[blue]Content-Type: {content_type}[/blue]")

                    if status == 200:
                        if "zip" in content_type or "octet-stream" in content_type:
                            # It's a ZIP file - download it
                            filename = f"horserace_{file_type}_data.zip"
                            filepath = self.download_dir / filename

                            with open(filepath, "wb") as f:
                                async for chunk in response.content.iter_chunked(8192):
                                    f.write(chunk)

                            file_size = filepath.stat().st_size
                            self.console.print(
                                f"[green]✅ Downloaded {filename} ({file_size:,} bytes)[/green]"
                            )

                            # Extract ZIP file
                            await self.extract_zip_file(filepath, file_type)
                            return True

                        else:
                            # Still getting HTML - session might not be valid
                            content = await response.text()

                            # Save debug response
                            debug_file = (
                                self.download_dir
                                / f"debug_{file_type}_with_cookies.html"
                            )
                            with open(debug_file, "w") as f:
                                f.write(content[:2000])  # Save first 2KB

                            self.console.print(
                                f"[yellow]⚠️ Got HTML response instead of ZIP file[/yellow]"
                            )
                            self.console.print(
                                f"[yellow]Debug response saved to: {debug_file}[/yellow]"
                            )

                            # Check if it's a login page
                            if any(
                                keyword in content.lower()
                                for keyword in ["login", "password", "sign in"]
                            ):
                                self.console.print(
                                    "[red]❌ Session expired or login required[/red]"
                                )

                            return False
                    else:
                        self.console.print(f"[red]❌ HTTP error: {status}[/red]")
                        return False

        except Exception as e:
            logger.error(f"Download error for {file_type}: {e}")
            self.console.print(f"[red]❌ Download error: {e}[/red]")
            return False

    async def extract_zip_file(self, zip_path: Path, file_type: str) -> bool:
        """
        Extract ZIP file and organize contents.

        Args:
            zip_path: Path to ZIP file
            file_type: Type of data (results/cards)

        Returns:
            bool: True if extraction successful
        """
        try:
            # Create extraction directory
            extract_dir = self.download_dir / f"{file_type}_data"
            extract_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                files = zip_ref.namelist()
                self.console.print(f"[cyan]📦 Extracting {len(files)} files...[/cyan]")
                zip_ref.extractall(extract_dir)

            # Show some extracted files
            for i, filename in enumerate(files[:5]):
                self.console.print(f"[green]   - {filename}[/green]")
            if len(files) > 5:
                self.console.print(
                    f"[green]   ... and {len(files) - 5} more files[/green]"
                )

            # Remove ZIP file after extraction
            zip_path.unlink()
            self.console.print(f"[blue]🗑️ Removed ZIP file[/blue]")

            return True

        except Exception as e:
            logger.error(f"Extraction error for {file_type}: {e}")
            self.console.print(f"[red]❌ Extraction error: {e}[/red]")
            return False

    async def download_data_files(self) -> bool:
        """
        Download data files from the website using session cookies.

        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            results_url = os.getenv("HORSERACE_DB_RESULTS_URL")
            cards_url = os.getenv("HORSERACE_DB_CARDS_URL")

            if not results_url or not cards_url:
                self.console.print(
                    "[red]❌ Download URLs not configured in .env file[/red]"
                )
                return False

            self.console.print("[cyan]📥 Starting file downloads...[/cyan]")

            # Get session cookies from Playwright browser
            cookies = await self.get_session_cookies()
            if not cookies:
                self.console.print("[red]❌ Failed to get session cookies[/red]")
                return False

            # Download results data
            results_success = await self.download_file_with_session(
                results_url, "results", cookies
            )

            # Download cards data
            cards_success = await self.download_file_with_session(
                cards_url, "cards", cookies
            )

            # Send completion notification
            if results_success and cards_success:
                self.send_ntfy_notification(
                    "🏇 Data Download Complete",
                    "Successfully downloaded today's race cards and yesterday's results from horseracedatabase.com",
                    "high",
                )
            elif results_success or cards_success:
                self.send_ntfy_notification(
                    "⚠️ Partial Download",
                    f"Only {'results' if results_success else 'cards'} data was downloaded successfully",
                    "default",
                )
            else:
                self.send_ntfy_notification(
                    "❌ Download Failed",
                    "Failed to download race data from horseracedatabase.com",
                    "high",
                )

            return results_success and cards_success

        except Exception as e:
            self.console.print(f"[red]❌ Error downloading files: {e}[/red]")
            return False

    async def run(self) -> bool:
        """
        Main run method with enhanced session-based downloads.

        Returns:
            bool: True if downloads successful
        """
        try:
            await self.start_browser()
            page = await self.context.new_page()

            # Step 1: Login to establish session cookies
            self.console.print("[cyan]🔐 Logging in to establish session...[/cyan]")
            login_success = await self.login_to_site(page)

            if not login_success:
                self.console.print("[red]❌ Login failed - cannot continue[/red]")
                return False

            self.console.print("[green]✅ Login successful[/green]")
            self.send_ntfy_notification(
                "🔐 Login Success",
                "Successfully logged into horseracedatabase.com",
                "default",
            )

            # Step 2: Download data files using session cookies
            download_success = await self.download_data_files()

            await page.close()
            return download_success

        except Exception as e:
            logger.error(f"Run process failed: {e}")
            self.console.print(f"[red]❌ Process failed: {e}[/red]")
            return False
        finally:
            await self.stop_browser()


async def main():
    """Main function."""
    console.print(
        Panel("🐴 Horse Race Database Auto-Downloader (Enhanced)", style="bold blue")
    )

    try:
        downloader = HorseRaceDatabaseDownloader()

        # Run the enhanced download process
        success = await downloader.run()

        if success:
            console.print("[green]🎉 All downloads completed successfully![/green]")
        else:
            console.print("[red]❌ Download process failed[/red]")

    except Exception as e:
        logger.error(f"Main process failed: {e}")
        console.print(f"[red]❌ Fatal error: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(main())
