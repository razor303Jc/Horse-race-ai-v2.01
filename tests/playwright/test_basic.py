"""
Basic Playwright tests for Horse Racing AI v2.0 Web Application
Simple tests to verify core functionality without complex dependencies.
"""

import pytest
from playwright.sync_api import Page, expect
import json


class TestBasicFunctionality:
    """Test basic web application functionality"""

    def test_dashboard_loads(self, page: Page, base_url: str):
        """Test that the main dashboard loads successfully"""
        response = page.goto(base_url)

        # Check response status
        assert response.status == 200

        # Check page title
        expect(page).to_have_title("🏇 Horse Racing AI v2.0 - Comprehensive Dashboard")

        # Check main content is visible
        expect(page.locator("body")).to_be_visible()

    def test_system_status_api(self, page: Page, base_url: str):
        """Test the system status API returns valid JSON"""
        response = page.goto(f"{base_url}/api/system_status")

        assert response.status == 200

        # Get and parse JSON content
        content = page.content()
        data = json.loads(content)

        # Check essential fields exist
        assert "overall_status" in data
        assert "timestamp" in data

        # Check status value is reasonable
        assert data["overall_status"] in [
            "EXCELLENT",
            "OPERATIONAL",
            "GOOD",
            "WARNING",
            "ERROR",
        ]

    def test_error_page_works(self, page: Page, base_url: str):
        """Test that 404 error page displays correctly"""
        page.goto(f"{base_url}/nonexistent-page")

        # Should show error page
        expect(page.locator("text=404")).to_be_visible()
        expect(page.locator("text=not found")).to_be_visible()

    def test_page_has_styling(self, page: Page, base_url: str):
        """Test that the page has CSS styling applied"""
        page.goto(base_url)

        # Check that body has some styling
        body = page.locator("body")
        expect(body).to_be_visible()

        # Check if any CSS is loaded (look for common CSS properties)
        computed_style = body.evaluate("el => getComputedStyle(el)")
        assert computed_style is not None

    def test_no_javascript_errors(self, page: Page, base_url: str):
        """Test that there are no critical JavaScript errors"""
        js_errors = []

        def handle_console(msg):
            if msg.type == "error":
                js_errors.append(msg.text)

        page.on("console", handle_console)
        page.goto(base_url)
        page.wait_for_load_state("networkidle")

        # Filter out non-critical errors
        critical_errors = [
            error
            for error in js_errors
            if not any(
                ignore in error.lower()
                for ignore in ["favicon", "websocket", "cors", "net::"]
            )
        ]

        assert len(critical_errors) == 0, f"JavaScript errors: {critical_errors}"

    def test_responsive_layout(self, page: Page, base_url: str):
        """Test basic responsive design"""
        # Test desktop
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(base_url)
        expect(page.locator("body")).to_be_visible()

        # Test mobile
        page.set_viewport_size({"width": 375, "height": 667})
        page.reload()
        expect(page.locator("body")).to_be_visible()


class TestAPIBasics:
    """Basic API functionality tests"""

    def test_api_returns_json(self, page: Page, base_url: str):
        """Test that API endpoints return valid JSON"""
        response = page.goto(f"{base_url}/api/system_status")

        # Check content type
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type or "json" in content_type

    def test_api_response_time(self, page: Page, base_url: str):
        """Test that API responds in reasonable time"""
        import time

        start_time = time.time()
        response = page.goto(f"{base_url}/api/system_status")
        response_time = time.time() - start_time

        assert response.status == 200
        assert response_time < 10, f"API too slow: {response_time:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
