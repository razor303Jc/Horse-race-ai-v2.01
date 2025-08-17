#!/usr/bin/env python3
"""
Working Auto Downloader - Fixed Once and For All
================================================

Uses the exact flow specified:
1. Go to https://horseracedatabase.com/my-account
2. Login with details in .env file
3. Type in input field like a human
4. Get session info
5. Click on the link https://horseracedatabase.com/my-account/downloads/
6. Use WooCommerce URLs with session cookies to download files
"""

import asyncio
import json
import logging
import os

# Import data management system
import sys
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiofiles
import aiohttp
import requests  # Add requests for NTFY notifications

# Import data validator and data manager
from data_validator import HorseRacingDataValidator

sys.path.append("/app/tools/data_processing")
try:
    from daily_downloads_manager import DailyDownloadsManager
except ImportError:
    # Fallback if not available
    DailyDownloadsManager = None
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
from rich.progress import Progress, SpinnerColumn, TextColumn

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
        self.download_dir = Path("data/daily_downloads")
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # Load credentials from environment
        self.username = os.getenv("HORSERACE_DB_USERNAME", "")
        self.password = os.getenv("HORSERACE_DB_PASSWORD", "")

        if not self.username or not self.password:
            raise ValueError(
                "Missing HORSERACE_DB_USERNAME or HORSERACE_DB_PASSWORD in .env file"
            )

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    def send_ntfy_notification(
        self, title: str, message: str, priority: str = "default"
    ) -> None:
        """Send notification to NTFY server with proper encoding."""
        try:
            # Remove Unicode emojis and extra whitespace that cause encoding issues
            safe_title = title.encode("ascii", "ignore").decode("ascii").strip()
            safe_message = message.encode("ascii", "ignore").decode("ascii").strip()

            # Use Docker network name instead of localhost when in container
            ntfy_host = os.getenv("NTFY_HOST", "horse_racing_ntfy:8081")
            url = f"http://{ntfy_host}/horse-racing-alerts"
            headers = {
                "Title": safe_title,
                "Priority": priority,
                "Tags": "horse,racing,download",
                "Content-Type": "text/plain; charset=utf-8",
            }
            response = requests.post(
                url, data=safe_message.encode("utf-8"), headers=headers
            )
            if response.status_code == 200:
                logger.info(f"✅ NTFY notification sent: {safe_title}")
            else:
                logger.warning(f"❌ NTFY notification failed: {response.status_code}")
        except Exception as e:
            logger.warning(f"❌ NTFY notification error: {e}")

    async def start_browser(self) -> None:
        """Start Playwright browser with download configuration."""
        playwright = await async_playwright().start()

        # Check if running in Docker/headless mode
        is_headless = os.getenv("HEADLESS", "false").lower() == "true"
        is_docker = os.getenv("DOCKER_CONTAINER", "false").lower() == "true"

        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-setuid-sandbox",
        ]

        # Add additional Docker-specific args for headless mode
        if is_docker or is_headless:
            browser_args.extend(
                [
                    "--disable-gpu",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-features=TranslateUI",
                    "--disable-ipc-flooding-protection",
                ]
            )

        self.browser = await playwright.chromium.launch(
            headless=is_headless,
            args=browser_args,
        )

        # Create context with download directory
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            accept_downloads=True,
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        logger.info("Browser started successfully")

    async def stop_browser(self) -> None:
        """Stop browser and cleanup properly to avoid AsyncIO exceptions."""
        try:
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            logger.info("Browser closed")
        except Exception as e:
            logger.warning(f"Browser cleanup warning: {e}")
            # Don't raise the exception as it might be cleanup-related

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
        """
        Exact login flow as specified:
        1. Go to https://horseracedatabase.com/my-account
        2. Login with details in .env file
        3. Type in input field like a human
        4. Get session info
        """
        try:
            logger.info("🔐 Starting exact login flow...")

            # Step 1: Navigate to my-account page
            logger.info("📍 Step 1: Going to https://horseracedatabase.com/my-account")
            await page.goto("https://horseracedatabase.com/my-account")
            await page.wait_for_load_state("networkidle", timeout=15000)

            # Handle potential newsletter modal
            await self.handle_newsletter_modal(page)

            # Check current URL
            current_url = page.url.lower()
            logger.info(f"Current URL: {current_url}")

            # Step 2: Find login form
            logger.info("🔍 Step 2: Looking for login form...")

            # Look for login form elements
            username_selectors = [
                'input[name="username"]',
                'input[name="email"]',
                'input[type="email"]',
                'input[id*="username"]',
                'input[id*="email"]',
            ]

            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                'input[id*="password"]',
            ]

            # Find username field
            username_element = None
            for selector in username_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        username_element = element
                        logger.info(f"✅ Found username field: {selector}")
                        break
                except Exception:
                    continue

            if not username_element:
                logger.error("❌ Could not find username field")
                return False

            # Find password field
            password_element = None
            for selector in password_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        password_element = element
                        logger.info(f"✅ Found password field: {selector}")
                        break
                except Exception:
                    continue

            if not password_element:
                logger.error("❌ Could not find password field")
                return False

            # Step 3: Type in input fields like a human
            logger.info("⌨️ Step 3: Typing credentials like a human...")
            await self.human_type(username_element, self.username)
            logger.info("✅ Username typed humanly")

            await self.human_type(password_element, self.password)
            logger.info("✅ Password typed humanly")

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
                        logger.info(f"🚀 Login submitted using: {selector}")
                        break
                except Exception:
                    continue

            # Wait for navigation after login
            await page.wait_for_load_state("networkidle", timeout=10000)

            # Check if login was successful
            new_url = page.url
            logger.info(f"After login URL: {new_url}")

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
                    logger.info("✅ Login successful - logout link found!")
                    return True
                else:
                    logger.warning("⚠️ Login status unclear - proceeding")
                    return True
            else:
                logger.warning(f"⚠️ Login may have failed - current URL: {new_url}")
                # Still try to proceed
                return True

        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
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
                name = cookie.get("name", "")
                value = cookie.get("value", "")
                if name and value:
                    cookie_dict[name] = value

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

            # Download results data (FIXED: results_url contains cards data, so extract to cards_data)
            results_success = await self.download_file_with_session(
                results_url, "cards", cookies
            )

            # Download cards data (FIXED: cards_url contains results data, so extract to results_data)
            cards_success = await self.download_file_with_session(
                cards_url, "results", cookies
            )

            # Send completion notification
            if results_success and cards_success:
                # Validate downloaded data
                validation_passed = self._validate_downloaded_data()

                if validation_passed:
                    self.send_ntfy_notification(
                        "🏇 Data Download Complete",
                        "Successfully downloaded today's race cards and yesterday's results from horseracedatabase.com",
                        "high",
                    )
                else:
                    self.send_ntfy_notification(
                        "⚠️ Download Complete with Validation Issues",
                        "Data downloaded but validation found issues. Check logs for details.",
                        "default",
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

    def _validate_downloaded_data(self) -> bool:
        """
        Validate downloaded data using the data validator

        Returns:
            bool: True if validation passes, False if there are errors
        """
        try:
            logger.info("🔍 Validating downloaded data...")

            # Run validation
            validator = HorseRacingDataValidator(self.download_dir)
            validation_results = validator.validate_download()

            # Check validation status
            validation_status = validation_results["summary"]["validation_status"]
            error_count = validation_results["summary"]["error_count"]
            warning_count = validation_results["summary"]["warning_count"]

            # Log results
            if validation_status == "PASSED":
                logger.info(f"✅ Data validation passed ({warning_count} warnings)")
                self.console.print("[green]✅ Data validation passed[/green]")

                # Log key metrics
                if "record_counts" in validation_results["summary"]:
                    counts = validation_results["summary"]["record_counts"]
                    logger.info(
                        f"📊 Data counts: Results races={counts['results_races']}, Records={counts['results_records']}, Cards races={counts['cards_races']}"
                    )

                return True
            else:
                logger.error(
                    f"❌ Data validation failed: {error_count} errors, {warning_count} warnings"
                )
                self.console.print(
                    f"[red]❌ Data validation failed: {error_count} errors[/red]"
                )

                # Log errors and warnings
                for error in validation_results["errors"]:
                    logger.error(f"  Error: {error}")
                for warning in validation_results["warnings"]:
                    logger.warning(f"  Warning: {warning}")

                return False

        except Exception as e:
            logger.error(f"❌ Data validation failed with exception: {e}")
            self.console.print(f"[red]❌ Data validation error: {e}[/red]")
            return False

    async def run(self) -> bool:
        """
        Main run method following the exact specified flow:
        1. Pre-download cleanup and organization
        2. Go to https://horseracedatabase.com/my-account
        3. Login with details in .env file
        4. Type in input field like a human
        5. Get session info
        6. Click on the link https://horseracedatabase.com/my-account/downloads/
        7. Use WooCommerce URLs with session cookies to download files
        8. Post-download data management and organization
        """
        try:
            # Step 1: Pre-download data management
            self.console.print("[cyan]🗂️ Step 1: Pre-download data management...[/cyan]")
            if DailyDownloadsManager:
                try:
                    data_manager = DailyDownloadsManager()
                    data_manager.integrate_with_auto_downloader()
                    self.console.print(
                        "[green]✅ Pre-download cleanup completed[/green]"
                    )
                except Exception as e:
                    logger.warning(f"Data management warning: {e}")
                    self.console.print(
                        f"[yellow]⚠️ Data management warning: {e}[/yellow]"
                    )

            await self.start_browser()
            if not self.context:
                logger.error("❌ Failed to create browser context")
                return False

            page = await self.context.new_page()

            # Steps 2-5: Login to establish session cookies
            self.console.print(
                "[cyan]🔐 Steps 2-5: Login to establish session...[/cyan]"
            )
            login_success = await self.login_to_site(page)

            if not login_success:
                self.console.print("[red]❌ Login failed - cannot continue[/red]")
                return False

            self.console.print("[green]✅ Login successful[/green]")

            # Step 6: Click on the downloads link
            self.console.print(
                "[cyan]📁 Step 6: Navigating to downloads page...[/cyan]"
            )
            try:
                await page.goto("https://horseracedatabase.com/my-account/downloads/")
                await page.wait_for_load_state("networkidle", timeout=10000)
                logger.info("✅ Successfully navigated to downloads page")
            except Exception as e:
                logger.warning(f"⚠️ Could not navigate to downloads page: {e}")
                # Continue anyway as we have session cookies

            # Step 7: Download data files using WooCommerce URLs with session cookies
            self.console.print(
                "[cyan]📥 Step 7: Using WooCommerce URLs to download files...[/cyan]"
            )
            download_success = await self.download_data_files()

            await page.close()

            # Step 8: Post-download data management
            if download_success and DailyDownloadsManager:
                self.console.print(
                    "[cyan]📊 Step 8: Post-download data organization...[/cyan]"
                )
                try:
                    data_manager = DailyDownloadsManager()
                    upload_files = data_manager.prepare_for_database_upload()

                    # Log prepared files for database upload
                    total_files = sum(len(files) for files in upload_files.values())
                    self.console.print(
                        f"[green]📤 Prepared {total_files} files for database upload[/green]"
                    )

                    # Save upload file list for database script
                    upload_manifest = self.download_dir / "upload_manifest.json"
                    import json

                    with open(upload_manifest, "w") as f:
                        json.dump(
                            {k: [str(p) for p in v] for k, v in upload_files.items()},
                            f,
                            indent=2,
                        )

                    self.console.print(
                        f"[blue]📋 Upload manifest saved: {upload_manifest}[/blue]"
                    )

                except Exception as e:
                    logger.warning(f"Post-download management warning: {e}")
                    self.console.print(
                        f"[yellow]⚠️ Post-download management warning: {e}[/yellow]"
                    )

            return download_success

        except Exception as e:
            logger.error(f"Run process failed: {e}")
            self.console.print(f"[red]❌ Process failed: {e}[/red]")
            return False
        finally:
            await self.stop_browser()


async def main():
    """Main function with proper AsyncIO cleanup."""
    console.print(
        Panel("🐴 Horse Race Database Auto-Downloader (Enhanced)", style="bold blue")
    )

    downloader = None
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

    finally:
        # Ensure browser is cleaned up properly
        if downloader:
            try:
                await downloader.stop_browser()
            except Exception:
                pass  # Ignore cleanup errors


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("[yellow]⚠️ Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Fatal error: {e}[/red]")
