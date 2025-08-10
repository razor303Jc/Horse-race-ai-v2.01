#!/usr/bin/env python3
"""
Qwen2.5 Rebuilt Auto Downloader
===============================

Complete Python script using Playwright for browser automation and
aiohttp for downloading files. Based on Qwen2.5's recommendations
with fixes for Docker integration.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List

import aiofiles
import aiohttp
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def login_and_extract_cookies(playwright):
    """Login to horseracedatabase.com and extract session cookies"""
    # Use headless mode for Docker
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    browser = await playwright.chromium.launch(headless=headless)
    context = await browser.new_context()
    page = await context.new_page()

    try:
        # Navigate to the login page
        logger.info("Navigating to login page...")
        await page.goto("https://horseracedatabase.com/my-account/")

        # Wait for page to fully load
        await page.wait_for_load_state("networkidle", timeout=15000)

        # Take a screenshot for debugging (if not headless)
        if not headless:
            await page.screenshot(path="debug_login_page.png")

        # Handle newsletter modal if present
        try:
            # Try multiple selectors for newsletter modal
            selectors = [
                '[aria-label="Close"]',
                'button[data-modal-id="newsletterModal"]',
                ".modal-close",
                ".newsletter-close",
                'button[data-dismiss="modal"]',
            ]

            for selector in selectors:
                try:
                    await page.wait_for_selector(selector, timeout=3000)
                    await page.click(selector)
                    logger.info(f"Closed newsletter modal using: {selector}")
                    await page.wait_for_timeout(2000)  # Wait for modal to close
                    break
                except Exception:
                    continue

        except Exception:
            logger.info("No newsletter modal found")

        # Debug: Check what's actually on the page
        logger.info(f"Current URL: {page.url}")
        logger.info(f"Page title: {await page.title()}")

        # Check if we can find any form elements
        form_elements = await page.query_selector_all("input")
        logger.info(f"Found {len(form_elements)} input elements on page")

        # Login with credentials from .env file
        username = os.getenv("HORSERACE_DB_USERNAME")
        password = os.getenv("HORSERACE_DB_PASSWORD")

        if not username or not password:
            raise ValueError("Missing username or password in .env file")

        logger.info("Filling login form...")

        # Fill username/email with multiple selector fallbacks
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
                await page.wait_for_selector(selector, timeout=5000)
                await page.fill(selector, username)
                username_filled = True
                logger.info(f"Username filled using selector: {selector}")
                break
            except Exception:
                continue

        if not username_filled:
            raise ValueError("Could not find username field")

        # Fill password with multiple selector fallbacks
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
                await page.wait_for_selector(selector, timeout=5000)
                await page.fill(selector, password)
                password_filled = True
                logger.info(f"Password filled using selector: {selector}")
                break
            except Exception:
                continue

        if not password_filled:
            raise ValueError("Could not find password field")

        # Submit login with multiple selector fallbacks
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
                await page.wait_for_selector(selector, timeout=5000)
                await page.click(selector)
                logger.info(f"Login submitted using: {selector}")
                break
            except Exception:
                continue

        # Wait for the navigation to complete
        logger.info("Waiting for login completion...")
        await page.wait_for_load_state("networkidle", timeout=10000)

        # Extract cookies
        cookies = await context.cookies()
        logger.info(f"Extracted {len(cookies)} session cookies")

        return cookies

    finally:
        await browser.close()


async def download_file(session, url, file_name):
    """Download a single file using authenticated session"""
    try:
        logger.info(f"Downloading {file_name}...")
        async with session.get(url) as response:
            if response.status == 200:
                # Create downloads directory
                download_dir = Path("data/downloads")
                download_dir.mkdir(parents=True, exist_ok=True)

                file_path = download_dir / f"{file_name}.zip"

                async with aiofiles.open(file_path, mode="wb") as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)

                logger.info(f"Successfully downloaded {file_name}.zip")
                return True
            else:
                logger.error(f"Failed to download {file_name}: HTTP {response.status}")
                return False

    except Exception as e:
        logger.error(f"Error downloading {file_name}: {e}")
        return False


async def download_files(cookies):
    """Download files using session cookies"""
    results_url = os.getenv("HORSERACE_DB_RESULTS_URL")
    cards_url = os.getenv("HORSERACE_DB_CARDS_URL")

    if not results_url or not cards_url:
        raise ValueError("Missing download URLs in .env file")

    # Convert Playwright cookies to aiohttp format
    cookie_jar = aiohttp.CookieJar()
    for cookie in cookies:
        cookie_jar.update_cookies({cookie["name"]: cookie["value"]})

    async with aiohttp.ClientSession(cookie_jar=cookie_jar) as session:
        tasks = [
            asyncio.create_task(download_file(session, results_url, "results")),
            asyncio.create_task(download_file(session, cards_url, "cards")),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successful downloads
        success_count = sum(1 for result in results if result is True)
        logger.info(f"Download completed: {success_count}/2 files successful")

        return success_count == 2


async def main():
    """Main entry point"""
    try:
        logger.info("Starting Qwen2.5 rebuilt auto downloader...")

        async with async_playwright() as playwright:
            # Step 1: Login and extract cookies
            cookies = await login_and_extract_cookies(playwright)

            if not cookies:
                logger.error("Failed to extract cookies")
                return False

            # Step 2: Download files
            success = await download_files(cookies)

            if success:
                logger.info("✅ Auto download completed successfully!")
                return True
            else:
                logger.error("❌ Auto download failed")
                return False

    except Exception as e:
        logger.error(f"Auto download error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
