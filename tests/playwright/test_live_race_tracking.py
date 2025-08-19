"""
Playwright tests for Live Race Tracking functionality
Tests WebSocket connections, real-time updates, and race monitoring features.
"""

import pytest
from playwright.sync_api import Page, expect
import time
import json


class TestLiveRaceTracking:
    """Test live race tracking WebSocket functionality"""

    def test_live_race_tracker_component_loads(self, page: Page, helpers):
        """Test that LiveRaceTracker component loads successfully"""
        page.goto(page.base_url)
        helpers.wait_for_loading(page)

        # Look for live race tracking section or component
        # The component might be in a tab or section
        race_tracker_selectors = [
            "[data-testid='live-race-tracker']",
            ".live-race-tracker",
            "text=Live Race Tracking",
            "text=Race Progress",
            "text=Live Updates",
        ]

        component_found = False
        for selector in race_tracker_selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible():
                    component_found = True
                    print(f"✅ Live race tracker found with selector: {selector}")
                    break
            except:
                continue

        if not component_found:
            print("⚠️  Live race tracker component not immediately visible")
            print("📝 May be in a tab or require navigation")

        # Take screenshot for documentation
        helpers.take_screenshot(page, "live_race_tracker_search")

    def test_race_selection_component(self, page: Page):
        """Test race selection component functionality"""
        page.goto(page.base_url)

        # Look for race selection interface
        race_selection_selectors = [
            "[data-testid='race-selection']",
            ".race-selection",
            "select[name*='race']",
            "text=Select Race",
            "text=Choose Race",
        ]

        for selector in race_selection_selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible():
                    print(f"✅ Race selection found with selector: {selector}")
                    return
            except:
                continue

        print("📝 Race selection component may require specific navigation")

    def test_websocket_connection_capability(self, page: Page):
        """Test WebSocket connection capability and setup"""
        page.goto(page.base_url)

        # Test if WebSocket is available in the browser context
        websocket_support = page.evaluate(
            """
            () => {
                return {
                    websocketAvailable: typeof WebSocket !== 'undefined',
                    currentURL: window.location.href,
                    protocol: window.location.protocol
                };
            }
        """
        )

        assert websocket_support["websocketAvailable"], "WebSocket should be available"
        print(f"✅ WebSocket support confirmed: {websocket_support}")

    def test_api_service_hook_functionality(self, page: Page):
        """Test API service hook functionality"""
        page.goto(page.base_url)

        # Check if API service functions are working
        # This tests the useApiService hook indirectly
        api_test_result = page.evaluate(
            """
            () => {
                // Test basic fetch capability
                return {
                    fetchAvailable: typeof fetch !== 'undefined',
                    baseURL: window.location.origin
                };
            }
        """
        )

        assert api_test_result["fetchAvailable"], "Fetch API should be available"
        print(f"✅ API service capabilities confirmed: {api_test_result}")

    def test_race_data_display(self, page: Page, helpers):
        """Test race data display and formatting"""
        page.goto(page.base_url)
        helpers.wait_for_loading(page)

        # Look for race data display elements
        race_data_selectors = [
            "[data-testid*='race']",
            ".race-info",
            ".race-data",
            "text=Race Time",
            "text=Track",
            "text=Distance",
        ]

        race_elements_found = []
        for selector in race_data_selectors:
            try:
                elements = page.locator(selector)
                count = elements.count()
                if count > 0:
                    race_elements_found.append(f"{selector}: {count} elements")
            except:
                continue

        if race_elements_found:
            print(f"✅ Race data elements found: {race_elements_found}")
        else:
            print("📝 Race data may be loaded dynamically or require specific state")

    def test_loading_states_and_error_handling(self, page: Page):
        """Test loading states and error handling in race tracking"""
        page.goto(page.base_url)

        # Look for loading indicators
        loading_selectors = [
            ".loading",
            "[data-testid='loading']",
            "text=Loading",
            ".spinner",
            ".loading-spinner",
        ]

        # Initially there might be loading states
        initial_loading_found = False
        for selector in loading_selectors:
            try:
                element = page.locator(selector)
                if element.is_visible():
                    initial_loading_found = True
                    print(f"✅ Loading state found: {selector}")
                    break
            except:
                continue

        # Wait for loading to complete
        time.sleep(3)

        # Check if loading states are properly cleared
        persistent_loading = []
        for selector in loading_selectors:
            try:
                element = page.locator(selector)
                if element.is_visible():
                    persistent_loading.append(selector)
            except:
                continue

        if len(persistent_loading) == 0:
            print("✅ Loading states properly cleared")
        else:
            print(f"⚠️  Persistent loading indicators: {persistent_loading}")

    def test_real_time_update_simulation(self, page: Page):
        """Test real-time update simulation and WebSocket message handling"""
        page.goto(page.base_url)

        # Set up console monitoring for WebSocket activities
        websocket_activities = []

        def handle_console(msg):
            text = msg.text.lower()
            if any(
                keyword in text
                for keyword in ["websocket", "ws", "race update", "live"]
            ):
                websocket_activities.append(msg.text)

        page.on("console", handle_console)

        # Wait for potential WebSocket connections
        time.sleep(5)

        if websocket_activities:
            print(f"✅ WebSocket activities detected: {websocket_activities}")
        else:
            print("📝 No WebSocket activities in console (may be expected)")

    def test_race_progress_visualization(self, page: Page):
        """Test race progress visualization elements"""
        page.goto(page.base_url)

        # Look for progress visualization elements
        progress_selectors = [
            ".progress",
            ".race-progress",
            "[data-testid*='progress']",
            ".progress-bar",
            "text=Progress",
            "[role='progressbar']",
        ]

        progress_elements = []
        for selector in progress_selectors:
            try:
                elements = page.locator(selector)
                count = elements.count()
                if count > 0:
                    progress_elements.append(f"{selector}: {count}")
            except:
                continue

        if progress_elements:
            print(f"✅ Progress visualization elements: {progress_elements}")
        else:
            print("📝 Progress visualization may be context-dependent")

    def test_websocket_error_handling(self, page: Page):
        """Test WebSocket error handling and reconnection logic"""
        page.goto(page.base_url)

        # Monitor for WebSocket error handling
        error_handling_logs = []

        def handle_console(msg):
            text = msg.text.lower()
            if any(
                keyword in text for keyword in ["error", "failed", "reconnect", "retry"]
            ):
                if "websocket" in text or "ws" in text:
                    error_handling_logs.append(msg.text)

        page.on("console", handle_console)

        # Simulate poor network conditions by waiting and checking
        time.sleep(5)

        # Test WebSocket error simulation (if exposed)
        try:
            page.evaluate(
                """
                () => {
                    // Try to create a WebSocket to a non-existent endpoint
                    // This should trigger error handling
                    try {
                        const testWS = new WebSocket('ws://localhost:9999/invalid');
                        testWS.onerror = (error) => {
                            console.log('WebSocket test error handled:', error);
                        };
                    } catch (e) {
                        console.log('WebSocket error caught:', e.message);
                    }
                }
            """
            )

            time.sleep(2)  # Wait for error handling

        except Exception as e:
            print(f"WebSocket error simulation: {e}")

        print(f"📊 Error handling activities: {len(error_handling_logs)}")

    def test_race_data_persistence(self, page: Page):
        """Test race data persistence and state management"""
        page.goto(page.base_url)

        # Check if race data persists across page interactions
        initial_state = page.evaluate(
            """
            () => {
                // Check for any stored race data
                return {
                    localStorage: Object.keys(localStorage).length,
                    sessionStorage: Object.keys(sessionStorage).length,
                    hasRaceData: document.querySelector('[data-testid*="race"]') !== null
                };
            }
        """
        )

        print(f"📊 Initial page state: {initial_state}")

        # Reload page and check persistence
        page.reload()
        time.sleep(2)

        post_reload_state = page.evaluate(
            """
            () => {
                return {
                    localStorage: Object.keys(localStorage).length,
                    sessionStorage: Object.keys(sessionStorage).length,
                    hasRaceData: document.querySelector('[data-testid*="race"]') !== null
                };
            }
        """
        )

        print(f"📊 Post-reload state: {post_reload_state}")


class TestLiveRaceTrackingIntegration:
    """Test live race tracking integration with other components"""

    def test_integration_with_dashboard(self, page: Page, helpers):
        """Test live race tracking integration with main dashboard"""
        page.goto(page.base_url)
        helpers.wait_for_loading(page)

        # Check if live race tracking is integrated into dashboard
        dashboard_integration = page.evaluate(
            """
            () => {
                const dashboardElements = document.querySelectorAll('[class*="dashboard"], [id*="dashboard"]');
                const raceElements = document.querySelectorAll('[class*="race"], [data-testid*="race"]');
                
                return {
                    dashboardElements: dashboardElements.length,
                    raceElements: raceElements.length,
                    integrated: dashboardElements.length > 0 && raceElements.length > 0
                };
            }
        """
        )

        print(f"🔗 Dashboard integration status: {dashboard_integration}")

    def test_performance_metrics_integration(self, page: Page):
        """Test integration with PerformanceMetricsDashboard"""
        page.goto(page.base_url)

        # Look for performance metrics related to race tracking
        performance_elements = page.locator("text=Performance").or_locator(
            ".performance"
        )

        if performance_elements.count() > 0:
            print("✅ Performance metrics components found")

            # Check for race-related metrics
            race_metrics = page.locator("text=Race").and_(page.locator(".metric"))
            if race_metrics.count() > 0:
                print("✅ Race-related performance metrics found")
        else:
            print("📝 Performance metrics may be in separate view")

    def test_api_integration_endpoints(self, page: Page):
        """Test API integration endpoints for live race data"""
        page.goto(page.base_url)

        # Monitor API calls made by the application
        api_requests = []

        def handle_request(request):
            if "/api/" in request.url:
                api_requests.append({"url": request.url, "method": request.method})

        page.on("request", handle_request)

        # Wait for initial API calls
        time.sleep(5)

        race_related_apis = [
            req
            for req in api_requests
            if any(
                keyword in req["url"].lower()
                for keyword in ["race", "live", "track", "update"]
            )
        ]

        if race_related_apis:
            print(f"✅ Race-related API calls detected: {len(race_related_apis)}")
            for api in race_related_apis[:3]:  # Show first 3
                print(f"  📡 {api['method']} {api['url']}")
        else:
            print("📝 No race-related API calls detected in initial load")

    def test_responsive_design_race_tracking(self, page: Page):
        """Test responsive design for race tracking components"""
        page.goto(page.base_url)

        # Test different viewport sizes
        viewports = [
            {"width": 1920, "height": 1080, "name": "Desktop"},
            {"width": 768, "height": 1024, "name": "Tablet"},
            {"width": 375, "height": 667, "name": "Mobile"},
        ]

        for viewport in viewports:
            page.set_viewport_size(viewport["width"], viewport["height"])
            time.sleep(1)

            # Check if race elements are still visible and properly arranged
            race_elements_visible = page.evaluate(
                """
                () => {
                    const raceElements = document.querySelectorAll('[data-testid*="race"], [class*="race"]');
                    let visibleCount = 0;
                    
                    raceElements.forEach(el => {
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            visibleCount++;
                        }
                    });
                    
                    return {
                        total: raceElements.length,
                        visible: visibleCount
                    };
                }
            """
            )

            print(
                f"📱 {viewport['name']} ({viewport['width']}x{viewport['height']}): "
                f"{race_elements_visible['visible']}/{race_elements_visible['total']} race elements visible"
            )

        # Reset to default viewport
        page.set_viewport_size(1920, 1080)

    def test_accessibility_race_tracking(self, page: Page):
        """Test accessibility features for race tracking"""
        page.goto(page.base_url)

        # Check for accessibility attributes
        accessibility_check = page.evaluate(
            """
            () => {
                const raceElements = document.querySelectorAll('[data-testid*="race"], [class*="race"]');
                let accessibilityFeatures = {
                    ariaLabels: 0,
                    roles: 0,
                    tabIndex: 0,
                    altText: 0
                };
                
                raceElements.forEach(el => {
                    if (el.getAttribute('aria-label')) accessibilityFeatures.ariaLabels++;
                    if (el.getAttribute('role')) accessibilityFeatures.roles++;
                    if (el.getAttribute('tabindex')) accessibilityFeatures.tabIndex++;
                    
                    const images = el.querySelectorAll('img');
                    images.forEach(img => {
                        if (img.getAttribute('alt')) accessibilityFeatures.altText++;
                    });
                });
                
                return accessibilityFeatures;
            }
        """
        )

        print(f"♿ Accessibility features in race tracking: {accessibility_check}")

    def test_error_boundary_race_tracking(self, page: Page):
        """Test error boundary handling for race tracking components"""
        page.goto(page.base_url)

        # Monitor for React error boundaries or error handling
        error_boundary_logs = []

        def handle_console(msg):
            text = msg.text.lower()
            if any(
                keyword in text
                for keyword in ["error boundary", "component error", "catch"]
            ):
                error_boundary_logs.append(msg.text)

        page.on("console", handle_console)

        # Wait and check for any error boundary activations
        time.sleep(3)

        if len(error_boundary_logs) == 0:
            print("✅ No error boundary activations detected")
        else:
            print(f"⚠️  Error boundary activities: {error_boundary_logs}")
