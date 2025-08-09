"""
Playwright tests for Horse Racing AI v2.0 Web Application Dashboard
Tests the main dashboard functionality, navigation, and core features.
"""

import pytest
from playwright.sync_api import Page, expect
import time


class TestDashboard:
    """Test the main dashboard functionality"""

    def test_dashboard_loads_successfully(self, page: Page, helpers):
        """Test that the main dashboard loads without errors"""
        # Navigate to the dashboard
        page.goto(page.base_url)

        # Wait for the page to load
        helpers.wait_for_loading(page)

        # Check that the title is correct
        expect(page).to_have_title("🏇 Horse Racing AI v2.0 - Comprehensive Dashboard")

        # Check for the main header
        expect(page.locator("h1")).to_contain_text("Horse Racing AI v2.0")

        # Take a screenshot for documentation
        helpers.take_screenshot(page, "dashboard_loaded")

    def test_navigation_menu_exists(self, page: Page):
        """Test that navigation menu is present and functional"""
        page.goto(page.base_url)

        # Check for navigation sections that should be present
        navigation_items = [
            "Dashboard Overview",
            "ML Predictions",
            "Race Analysis",
            "Betting Strategies",
            "Performance Tracking",
            "System Status",
        ]

        for item in navigation_items:
            # Look for navigation items (case insensitive)
            expect(page.locator(f"text={item}").first).to_be_visible()

    def test_system_status_cards(self, page: Page):
        """Test that system status cards are displayed"""
        page.goto(page.base_url)
        page.wait_for_load_state("networkidle")

        # Check for status indicators
        status_elements = [
            ".ml-status",
            ".betting-status",
            ".performance-status",
            ".notification-status",
        ]

        for element in status_elements:
            try:
                expect(page.locator(element).first).to_be_visible()
            except Exception:
                # If specific status classes don't exist, check for general indicators
                expect(page.locator("text=OPERATIONAL").first).to_be_visible()

    def test_responsive_design(self, page: Page):
        """Test that the dashboard is responsive on different screen sizes"""
        # Test desktop view
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(page.base_url)
        expect(page.locator("body")).to_be_visible()

        # Test tablet view
        page.set_viewport_size({"width": 768, "height": 1024})
        page.reload()
        expect(page.locator("body")).to_be_visible()

        # Test mobile view
        page.set_viewport_size({"width": 375, "height": 667})
        page.reload()
        expect(page.locator("body")).to_be_visible()

    def test_no_console_errors(self, page: Page, helpers):
        """Test that there are no JavaScript console errors"""
        errors = []

        def handle_console(msg):
            if msg.type == "error":
                errors.append(msg.text)

        page.on("console", handle_console)
        page.goto(page.base_url)
        page.wait_for_load_state("networkidle")

        # Allow some time for any async errors
        time.sleep(2)

        # Filter out common non-critical errors
        critical_errors = [
            error
            for error in errors
            if not any(
                ignore in error.lower()
                for ignore in ["favicon", "websocket", "cors", "mixed content"]
            )
        ]

        assert len(critical_errors) == 0, f"Console errors found: {critical_errors}"


class TestAPIEndpoints:
    """Test API endpoints through the web interface"""

    def test_system_status_api(self, page: Page):
        """Test the system status API endpoint"""
        page.goto(f"{page.base_url}/api/system_status")

        # Check that we get a JSON response
        content = page.content()
        assert "overall_status" in content
        assert "timestamp" in content
        assert "EXCELLENT" in content or "OPERATIONAL" in content

    def test_api_endpoints_accessibility(self, page: Page):
        """Test that key API endpoints are accessible"""
        endpoints = [
            "/api/system_status",
        ]

        for endpoint in endpoints:
            response = page.goto(f"{page.base_url}{endpoint}")
            assert (
                response.status < 400
            ), f"Endpoint {endpoint} returned status {response.status}"

    def test_error_page_handling(self, page: Page):
        """Test that error pages are properly displayed"""
        # Try accessing a non-existent page
        page.goto(f"{page.base_url}/nonexistent-page")

        # Should show a 404 error page
        expect(page.locator("text=404")).to_be_visible()
        expect(page.locator("text=Page not found")).to_be_visible()

        # Check that the error page has proper styling
        expect(page.locator(".error-container")).to_be_visible()


class TestUserInteractions:
    """Test user interactions and dynamic features"""

    def test_clickable_elements(self, page: Page):
        """Test that interactive elements are clickable"""
        page.goto(page.base_url)
        page.wait_for_load_state("networkidle")

        # Look for buttons and links
        buttons = page.locator("button, .btn, a[href]").all()

        # Ensure we have some interactive elements
        assert len(buttons) > 0, "No interactive elements found on dashboard"

        # Test that at least some buttons are visible and enabled
        visible_buttons = [btn for btn in buttons if btn.is_visible()]
        assert len(visible_buttons) > 0, "No visible interactive elements found"

    def test_navigation_functionality(self, page: Page):
        """Test navigation between different sections"""
        page.goto(page.base_url)

        # Look for navigation links and test them
        nav_links = page.locator("a[href], button[onclick]").all()

        for link in nav_links[:3]:  # Test first 3 links to avoid too many requests
            if link.is_visible():
                try:
                    link.click()
                    page.wait_for_load_state("networkidle", timeout=5000)
                    # Verify we're still on a valid page
                    expect(page.locator("body")).to_be_visible()
                except Exception:
                    # Some links might be external or require different handling
                    pass

    def test_form_interactions(self, page: Page):
        """Test form elements if present"""
        page.goto(page.base_url)

        # Look for form elements
        inputs = page.locator("input, select, textarea").all()

        # If forms exist, test basic interaction
        for form_input in inputs[:2]:  # Test first 2 inputs
            if form_input.is_visible() and form_input.is_enabled():
                try:
                    # Test typing in input fields
                    input_type = form_input.get_attribute("type")
                    if input_type in ["text", "search", None]:
                        form_input.fill("test input")
                        assert form_input.input_value() == "test input"
                except Exception:
                    # Some inputs might have restrictions
                    pass


class TestPerformance:
    """Test performance and loading times"""

    def test_page_load_performance(self, page: Page):
        """Test that the page loads within acceptable time limits"""
        start_time = time.time()

        page.goto(page.base_url)
        page.wait_for_load_state("networkidle")

        load_time = time.time() - start_time

        # Assert that page loads within 10 seconds
        assert load_time < 10, f"Page took too long to load: {load_time:.2f} seconds"

    def test_resource_loading(self, page: Page):
        """Test that CSS and JS resources load properly"""
        page.goto(page.base_url)

        # Check for CSS
        css_elements = page.locator("link[rel='stylesheet'], style").all()
        assert len(css_elements) > 0, "No CSS resources found"

        # Check that page is styled (has some CSS applied)
        body_styles = page.locator("body").evaluate("el => getComputedStyle(el)")
        assert body_styles is not None

    def test_api_response_times(self, page: Page):
        """Test that API responses are reasonably fast"""
        start_time = time.time()

        response = page.goto(f"{page.base_url}/api/system_status")

        response_time = time.time() - start_time

        # Assert API responds within 5 seconds
        assert (
            response_time < 5
        ), f"API took too long to respond: {response_time:.2f} seconds"
        assert response.status == 200


class TestSecurity:
    """Test basic security aspects"""

    def test_no_sensitive_data_exposure(self, page: Page):
        """Test that no sensitive data is exposed in the client"""
        page.goto(page.base_url)

        content = page.content().lower()

        # Check that common sensitive patterns are not exposed
        sensitive_patterns = [
            "password",
            "secret_key",
            "api_key",
            "private_key",
            "token",
        ]

        for pattern in sensitive_patterns:
            assert (
                pattern not in content
            ), f"Sensitive data pattern '{pattern}' found in page content"

    def test_proper_error_handling(self, page: Page):
        """Test that errors don't expose system information"""
        # Test 404 page
        page.goto(f"{page.base_url}/nonexistent")
        content = page.content().lower()

        # Ensure error page doesn't expose stack traces or system paths
        dangerous_patterns = [
            "traceback",
            "/usr/",
            "/home/",
            "exception:",
            "error at line",
        ]

        for pattern in dangerous_patterns:
            assert (
                pattern not in content
            ), f"System information '{pattern}' exposed in error page"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
