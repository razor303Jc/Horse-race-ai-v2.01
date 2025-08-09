"""
Pytest configuration and fixtures for Playwright tests
"""

import pytest
from playwright.sync_api import Playwright, Browser, BrowserContext, Page
import time
import requests
from typing import Generator


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context arguments"""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "record_video_dir": "tests/playwright/videos/",
        "record_video_size": {"width": 1920, "height": 1080},
    }


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the Horse Racing AI application"""
    return "http://localhost:5002"


@pytest.fixture(scope="session", autouse=True)
def wait_for_app(base_url):
    """Wait for the application to be ready before running tests"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/api/system_status", timeout=5)
            if response.status_code == 200:
                print(f"✅ Application is ready at {base_url}")
                return
        except requests.RequestException:
            pass

        print(f"⏳ Waiting for application... (attempt {attempt + 1}/{max_attempts})")
        time.sleep(2)

    raise RuntimeError(
        f"❌ Application not ready at {base_url} after {max_attempts} attempts"
    )


@pytest.fixture
def page(browser: Browser, base_url: str) -> Generator[Page, None, None]:
    """Create a new page for each test with proper setup"""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True,
    )
    page = context.new_page()

    # Add console logging for debugging
    page.on("console", lambda msg: print(f"🖥️  Console [{msg.type}]: {msg.text}"))
    page.on("pageerror", lambda error: print(f"❌ Page Error: {error}"))

    # Set base URL as property for easy access
    page.base_url = base_url

    yield page

    # Cleanup
    context.close()


@pytest.fixture
def authenticated_page(page: Page) -> Page:
    """Page fixture with authentication if needed"""
    # If we add authentication later, handle it here
    return page


class PageHelpers:
    """Helper methods for common page interactions"""

    @staticmethod
    def wait_for_loading(page: Page, timeout: int = 30000):
        """Wait for page loading indicators to disappear"""
        try:
            # Wait for any loading spinners or indicators
            page.wait_for_selector(".loading", state="hidden", timeout=timeout)
        except:
            pass  # No loading indicators found

    @staticmethod
    def take_screenshot(page: Page, name: str):
        """Take a screenshot with timestamp"""
        timestamp = int(time.time())
        screenshot_path = f"tests/playwright/screenshots/{name}_{timestamp}.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"📸 Screenshot saved: {screenshot_path}")
        return screenshot_path

    @staticmethod
    def check_console_errors(page: Page):
        """Check for JavaScript console errors"""
        errors = []

        def handle_console(msg):
            if msg.type in ["error", "warning"]:
                errors.append(f"{msg.type.upper()}: {msg.text}")

        page.on("console", handle_console)
        return errors

    @staticmethod
    def wait_for_api_response(page: Page, api_endpoint: str, timeout: int = 10000):
        """Wait for specific API endpoint to respond"""

        def check_response(response):
            return api_endpoint in response.url and response.status < 400

        with page.expect_response(check_response, timeout=timeout) as response_info:
            return response_info.value


@pytest.fixture
def helpers():
    """Provide helper methods to tests"""
    return PageHelpers
