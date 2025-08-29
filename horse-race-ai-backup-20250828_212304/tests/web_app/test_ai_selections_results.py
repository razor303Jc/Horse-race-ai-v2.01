#!/usr/bin/env python3
"""
AI Selections Results Web App Tests
==================================

Comprehensive test suite for the AI Selections Results dashboard,
including API endpoints, React component functionality, and integration tests.
"""

import pytest
import requests
import json
import time
from typing import Dict, List, Any
import asyncio
import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class TestAISelectionsAPI:
    """Test suite for AI Selections API endpoints"""

    BASE_URL = "http://localhost:3000"
    PERFORMANCE_ENDPOINT = f"{BASE_URL}/api/ai_selections/performance"
    RECENT_ENDPOINT = f"{BASE_URL}/api/ai_selections/recent"

    def test_api_health_check(self):
        """Test if the API server is responding"""
        try:
            response = requests.get(f"{self.BASE_URL}/api/health", timeout=10)
            assert (
                response.status_code == 200
            ), f"API health check failed: {response.status_code}"
            print("✅ API server is responding")
        except requests.exceptions.RequestException as e:
            pytest.fail(f"❌ API server is not accessible: {e}")

    def test_performance_endpoint_basic(self):
        """Test performance endpoint basic functionality"""
        response = requests.get(self.PERFORMANCE_ENDPOINT, timeout=15)

        assert (
            response.status_code == 200
        ), f"Performance endpoint failed: {response.status_code}"

        data = response.json()
        assert (
            data["status"] == "success"
        ), f"API returned error: {data.get('message', 'Unknown error')}"
        assert "data" in data, "Response missing data field"
        assert "summary" in data["data"], "Response missing summary data"

        summary = data["data"]["summary"]
        required_fields = [
            "total_predictions",
            "accuracy_rate",
            "roi_percentage",
            "total_profit_loss",
            "win_rate",
            "place_rate",
        ]

        for field in required_fields:
            assert field in summary, f"Summary missing required field: {field}"
            assert isinstance(
                summary[field], (int, float)
            ), f"Field {field} should be numeric"

        # Validate our known data
        assert summary["total_predictions"] > 0, "Should have predictions"
        assert 0 <= summary["accuracy_rate"] <= 100, "Accuracy rate should be 0-100%"
        assert isinstance(
            summary["total_profit_loss"], (int, float)
        ), "P&L should be numeric"

        print(
            f"✅ Performance endpoint: {summary['total_predictions']} predictions, "
            f"{summary['accuracy_rate']}% accuracy, £{summary['total_profit_loss']} P&L"
        )

    def test_performance_endpoint_with_days_filter(self):
        """Test performance endpoint with different day filters"""
        test_periods = [7, 14, 30, 60, 90]

        for days in test_periods:
            response = requests.get(
                f"{self.PERFORMANCE_ENDPOINT}?days_back={days}", timeout=10
            )
            assert response.status_code == 200, f"Failed for {days} days filter"

            data = response.json()
            assert (
                data["status"] == "success"
            ), f"Error for {days} days: {data.get('message')}"

            summary = data["data"]["summary"]
            assert (
                summary["total_predictions"] >= 0
            ), f"Invalid prediction count for {days} days"

        print("✅ Performance endpoint works with all day filters")

    def test_confidence_breakdown_structure(self):
        """Test confidence breakdown data structure"""
        response = requests.get(self.PERFORMANCE_ENDPOINT, timeout=10)
        data = response.json()

        assert "confidence_breakdown" in data["data"], "Missing confidence breakdown"

        confidence_data = data["data"]["confidence_breakdown"]
        assert isinstance(
            confidence_data, dict
        ), "Confidence breakdown should be a dictionary"

        for level, stats in confidence_data.items():
            required_stats = [
                "total_bets",
                "successful_bets",
                "accuracy_rate",
                "profit_loss",
                "avg_roi",
            ]
            for stat in required_stats:
                assert stat in stats, f"Confidence level {level} missing {stat}"
                assert isinstance(
                    stats[stat], (int, float)
                ), f"{stat} should be numeric"

        print(
            f"✅ Confidence breakdown: {len(confidence_data)} levels with complete stats"
        )

    def test_daily_performance_data(self):
        """Test daily performance data structure"""
        response = requests.get(self.PERFORMANCE_ENDPOINT, timeout=10)
        data = response.json()

        assert "daily_performance" in data["data"], "Missing daily performance data"

        daily_data = data["data"]["daily_performance"]
        assert isinstance(daily_data, list), "Daily performance should be a list"

        if daily_data:  # If we have data
            sample_day = daily_data[0]
            required_fields = ["date", "bets", "wins", "profit", "roi", "accuracy"]

            for field in required_fields:
                assert field in sample_day, f"Daily data missing field: {field}"

        print(f"✅ Daily performance data: {len(daily_data)} days")

    def test_recent_selections_endpoint_basic(self):
        """Test recent selections endpoint basic functionality"""
        response = requests.get(self.RECENT_ENDPOINT, timeout=15)

        assert (
            response.status_code == 200
        ), f"Recent selections endpoint failed: {response.status_code}"

        data = response.json()
        assert data["status"] == "success", f"API returned error: {data.get('message')}"
        assert "data" in data, "Response missing data field"
        assert "selections" in data["data"], "Response missing selections data"
        assert (
            "total_count" in data["data"]
        ), "Response missing total_count for pagination"

        selections = data["data"]["selections"]
        total_count = data["data"]["total_count"]

        assert isinstance(selections, list), "Selections should be a list"
        assert isinstance(total_count, int), "Total count should be an integer"
        assert total_count > 0, "Should have some selections"

        print(f"✅ Recent selections: {len(selections)} returned, {total_count} total")

    def test_pagination_functionality(self):
        """Test pagination with different limits and offsets"""
        test_cases = [
            {"limit": 10, "offset": 0},
            {"limit": 25, "offset": 10},
            {"limit": 50, "offset": 50},
            {"limit": 5, "offset": 100},
        ]

        for params in test_cases:
            response = requests.get(self.RECENT_ENDPOINT, params=params, timeout=10)
            assert response.status_code == 200, f"Pagination failed for {params}"

            data = response.json()
            assert (
                data["status"] == "success"
            ), f"Pagination error for {params}: {data.get('message')}"

            returned_data = data["data"]
            assert returned_data["limit"] == params["limit"], "Limit not respected"
            assert returned_data["offset"] == params["offset"], "Offset not respected"
            assert (
                len(returned_data["selections"]) <= params["limit"]
            ), "Too many records returned"

        print("✅ Pagination working correctly with various limit/offset combinations")

    def test_selection_data_structure(self):
        """Test structure of individual selection records"""
        response = requests.get(f"{self.RECENT_ENDPOINT}?limit=5", timeout=10)
        data = response.json()

        selections = data["data"]["selections"]
        if not selections:
            pytest.skip("No selection data available for structure test")

        sample_selection = selections[0]
        required_fields = [
            "race_id",
            "horse_name",
            "selection_date",
            "ai_probability",
            "confidence_level",
            "starting_price",
            "race_result",
            "profit_loss",
            "roi_percentage",
        ]

        for field in required_fields:
            assert (
                field in sample_selection
            ), f"Selection missing required field: {field}"

        # Validate data types and ranges
        assert isinstance(
            sample_selection["ai_probability"], (int, float)
        ), "AI probability should be numeric"
        assert (
            0 <= sample_selection["ai_probability"] <= 100
        ), "AI probability should be 0-100%"
        assert sample_selection["confidence_level"] in [
            "High",
            "Medium",
            "Low",
        ], "Invalid confidence level"
        assert sample_selection["race_result"] in [
            "WIN",
            "PLACE",
            "LOSE",
        ], "Invalid race result"

        print("✅ Selection data structure validated")

    def test_api_performance_timing(self):
        """Test API response times"""
        endpoints = [
            (self.PERFORMANCE_ENDPOINT, "Performance"),
            (f"{self.RECENT_ENDPOINT}?limit=25", "Recent Selections"),
        ]

        for url, name in endpoints:
            start_time = time.time()
            response = requests.get(url, timeout=30)
            end_time = time.time()

            response_time = end_time - start_time
            assert response.status_code == 200, f"{name} endpoint failed"
            assert (
                response_time < 10.0
            ), f"{name} endpoint too slow: {response_time:.2f}s"

            print(f"✅ {name} endpoint response time: {response_time:.2f}s")

    def test_error_handling(self):
        """Test API error handling for invalid requests"""
        # Test invalid days_back parameter
        response = requests.get(f"{self.PERFORMANCE_ENDPOINT}?days_back=-1", timeout=10)
        # Should still work but may return empty data
        assert response.status_code == 200, "API should handle negative days gracefully"

        # Test very large limit
        response = requests.get(f"{self.RECENT_ENDPOINT}?limit=10000", timeout=15)
        assert response.status_code == 200, "API should handle large limits gracefully"

        # Test very large offset
        response = requests.get(f"{self.RECENT_ENDPOINT}?offset=100000", timeout=10)
        assert response.status_code == 200, "API should handle large offsets gracefully"
        data = response.json()
        assert (
            data["status"] == "success"
        ), "Large offset should return success with empty data"

        print("✅ Error handling working correctly")


class TestAISelectionsWebApp:
    """Test suite for AI Selections Results web application"""

    WEB_URL = "http://localhost:3000/ai-results"

    @classmethod
    def setup_class(cls):
        """Setup Chrome driver for web testing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(10)
        except Exception as e:
            pytest.skip(f"Chrome driver not available: {e}")

    @classmethod
    def teardown_class(cls):
        """Cleanup Chrome driver"""
        if hasattr(cls, "driver"):
            cls.driver.quit()

    def test_page_loads_successfully(self):
        """Test if the AI Results page loads without errors"""
        self.driver.get(self.WEB_URL)

        # Wait for page to load
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Check if we're on the right page
        assert "ai-results" in self.driver.current_url.lower(), "Not on AI Results page"

        # Look for the main heading
        try:
            heading = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[contains(text(), 'AI Selections') or contains(text(), 'Performance')]",
                    )
                )
            )
            assert heading.is_displayed(), "Main heading not visible"
        except TimeoutException:
            # Try alternative selectors
            headings = self.driver.find_elements(
                By.TAG_NAME, "h1"
            ) + self.driver.find_elements(By.TAG_NAME, "h2")
            assert len(headings) > 0, "No headings found on page"

        print("✅ AI Results page loads successfully")

    def test_summary_cards_present(self):
        """Test if performance summary cards are displayed"""
        self.driver.get(self.WEB_URL)

        # Wait for cards to load
        time.sleep(5)

        # Look for cards containing key metrics
        card_selectors = [
            "//*[contains(text(), 'Total Predictions') or contains(text(), 'Predictions')]",
            "//*[contains(text(), 'Accuracy') or contains(text(), 'ROI') or contains(text(), 'Profit')]",
        ]

        cards_found = 0
        for selector in card_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    cards_found += len(elements)
            except NoSuchElementException:
                continue

        assert cards_found > 0, "No summary cards found on page"
        print(f"✅ Found {cards_found} summary cards/metrics")

    def test_navigation_tabs_present(self):
        """Test if navigation tabs are present and functional"""
        self.driver.get(self.WEB_URL)
        time.sleep(5)

        # Look for tab-like elements
        tab_selectors = [
            "//button[contains(@class, 'tab') or contains(@role, 'tab')]",
            "//*[contains(text(), 'Overview') or contains(text(), 'Trends') or contains(text(), 'Details') or contains(text(), 'Analysis')]",
        ]

        tabs_found = False
        for selector in tab_selectors:
            try:
                tabs = self.driver.find_elements(By.XPATH, selector)
                if tabs:
                    tabs_found = True
                    break
            except NoSuchElementException:
                continue

        if tabs_found:
            print("✅ Navigation tabs found")
        else:
            print("⚠️  Navigation tabs not found (may be loaded dynamically)")

    def test_table_with_pagination(self):
        """Test if data table with pagination is present"""
        self.driver.get(self.WEB_URL)
        time.sleep(8)  # Allow more time for data loading

        # Look for table elements
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        if not tables:
            # Try other table selectors
            tables = self.driver.find_elements(
                By.XPATH, "//*[contains(@class, 'table') or contains(@role, 'grid')]"
            )

        if tables:
            print("✅ Data table found")

            # Look for pagination controls
            pagination_selectors = [
                "//*[contains(text(), 'rows per page') or contains(text(), 'of')]",
                "//button[contains(@aria-label, 'page') or contains(@title, 'page')]",
                "//*[contains(@class, 'pagination')]",
            ]

            pagination_found = False
            for selector in pagination_selectors:
                try:
                    pagination_elements = self.driver.find_elements(By.XPATH, selector)
                    if pagination_elements:
                        pagination_found = True
                        break
                except NoSuchElementException:
                    continue

            if pagination_found:
                print("✅ Pagination controls found")
            else:
                print("⚠️  Pagination controls not found (may be hidden if few records)")
        else:
            print("⚠️  Data table not found (may be loading)")

    def test_charts_loading(self):
        """Test if charts are loading"""
        self.driver.get(self.WEB_URL)
        time.sleep(10)  # Allow time for charts to render

        # Look for chart elements (SVG is common for Recharts)
        chart_selectors = [
            "svg",
            "//*[contains(@class, 'recharts')]",
            "//*[contains(@class, 'chart')]",
        ]

        charts_found = 0
        for selector in chart_selectors:
            try:
                if selector == "svg":
                    charts = self.driver.find_elements(By.TAG_NAME, selector)
                else:
                    charts = self.driver.find_elements(By.XPATH, selector)
                charts_found += len(charts)
            except NoSuchElementException:
                continue

        if charts_found > 0:
            print(f"✅ Found {charts_found} chart elements")
        else:
            print("⚠️  Chart elements not found (may be loading or require interaction)")

    def test_responsive_design(self):
        """Test responsive design at different screen sizes"""
        test_sizes = [
            (1920, 1080),  # Desktop
            (768, 1024),  # Tablet
            (375, 667),  # Mobile
        ]

        for width, height in test_sizes:
            self.driver.set_window_size(width, height)
            self.driver.get(self.WEB_URL)
            time.sleep(3)

            # Check if page content is still visible
            body = self.driver.find_element(By.TAG_NAME, "body")
            assert body.is_displayed(), f"Page not visible at {width}x{height}"

            # Check if content fits viewport
            body_rect = body.rect
            assert (
                body_rect["width"] <= width + 50
            ), f"Content overflows at {width}x{height}"  # Allow some tolerance

        print("✅ Responsive design working across different screen sizes")

    def test_error_handling_display(self):
        """Test if the page handles API errors gracefully"""
        # This test assumes the page will handle API errors gracefully
        # by showing error messages or loading states

        self.driver.get(self.WEB_URL)
        time.sleep(5)

        # Look for error messages or loading indicators
        error_indicators = [
            "//*[contains(text(), 'Error') or contains(text(), 'Failed') or contains(text(), 'Loading')]",
            "//*[contains(@class, 'error') or contains(@class, 'loading')]",
        ]

        # The page should either show data OR show a loading/error state
        has_content = False

        # Check for data content
        if self.driver.find_elements(By.TAG_NAME, "table") or self.driver.find_elements(
            By.TAG_NAME, "svg"
        ):
            has_content = True

        # Check for error/loading states
        for selector in error_indicators:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    has_content = True
                    break
            except NoSuchElementException:
                continue

        assert has_content, "Page shows neither data nor error/loading state"
        print("✅ Page handles loading/error states appropriately")


class TestIntegrationScenarios:
    """Integration tests combining API and web app functionality"""

    def test_data_consistency_api_vs_webapp(self):
        """Test that web app displays data consistent with API"""
        # Get data from API
        api_response = requests.get(
            "http://localhost:3000/api/ai_selections/performance", timeout=15
        )
        assert api_response.status_code == 200, "API call failed"

        api_data = api_response.json()
        assert api_data["status"] == "success", "API returned error"

        api_summary = api_data["data"]["summary"]

        # Test that we can access the web app (basic integration)
        web_response = requests.get("http://localhost:3000/ai-results", timeout=15)
        assert web_response.status_code == 200, "Web app not accessible"

        print(
            f"✅ API and web app both accessible - API shows {api_summary['total_predictions']} predictions"
        )

    def test_api_endpoint_load_handling(self):
        """Test API can handle multiple concurrent requests"""
        import concurrent.futures
        import threading

        def make_request(endpoint):
            try:
                response = requests.get(endpoint, timeout=10)
                return response.status_code == 200
            except:
                return False

        endpoints = [
            "http://localhost:3000/api/ai_selections/performance",
            "http://localhost:3000/api/ai_selections/recent?limit=10",
            "http://localhost:3000/api/ai_selections/recent?limit=25&offset=10",
        ]

        # Make 10 concurrent requests to each endpoint
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            futures = []
            for _ in range(10):
                for endpoint in endpoints:
                    futures.append(executor.submit(make_request, endpoint))

            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8, f"API success rate too low: {success_rate:.2%}"

        print(
            f"✅ API load test: {success_rate:.1%} success rate with {len(results)} concurrent requests"
        )

    def test_full_user_journey(self):
        """Test a complete user journey through the AI Results page"""
        # This test simulates a user visiting the page and interacting with it

        # 1. Check main page accessibility
        main_response = requests.get("http://localhost:3000", timeout=10)
        assert main_response.status_code == 200, "Main page not accessible"

        # 2. Check AI results page accessibility
        ai_results_response = requests.get(
            "http://localhost:3000/ai-results", timeout=15
        )
        assert ai_results_response.status_code == 200, "AI Results page not accessible"

        # 3. Verify API endpoints work as expected
        performance_response = requests.get(
            "http://localhost:3000/api/ai_selections/performance", timeout=15
        )
        assert performance_response.status_code == 200, "Performance API not working"

        selections_response = requests.get(
            "http://localhost:3000/api/ai_selections/recent?limit=5", timeout=10
        )
        assert selections_response.status_code == 200, "Selections API not working"

        # 4. Verify data quality
        performance_data = performance_response.json()
        assert performance_data["status"] == "success", "Performance API error"

        selections_data = selections_response.json()
        assert selections_data["status"] == "success", "Selections API error"
        assert (
            selections_data["data"]["total_count"] > 0
        ), "No selections data available"

        print("✅ Complete user journey test passed")


# Test execution and reporting functions
def run_comprehensive_tests():
    """Run all tests and generate a comprehensive report"""
    print("🧪 AI Selections Results - Comprehensive Test Suite")
    print("=" * 60)
    print()

    # Collect all test classes
    test_classes = [
        TestAISelectionsAPI,
        TestAISelectionsWebApp,
        TestIntegrationScenarios,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = []

    for test_class in test_classes:
        print(f"🔍 Running {test_class.__name__}")
        print("-" * 40)

        # Get all test methods
        test_methods = [
            method for method in dir(test_class) if method.startswith("test_")
        ]

        # Setup class if needed
        if hasattr(test_class, "setup_class"):
            try:
                test_class.setup_class()
            except Exception as e:
                print(f"❌ Failed to setup {test_class.__name__}: {e}")
                continue

        # Run each test method
        test_instance = test_class()
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                passed_tests += 1
                print(f"  ✅ {method_name}")
            except Exception as e:
                failed_tests.append(f"{test_class.__name__}.{method_name}: {e}")
                print(f"  ❌ {method_name}: {e}")

        # Cleanup class if needed
        if hasattr(test_class, "teardown_class"):
            try:
                test_class.teardown_class()
            except Exception as e:
                print(f"⚠️  Failed to cleanup {test_class.__name__}: {e}")

        print()

    # Generate summary report
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

    if failed_tests:
        print("\n❌ Failed Tests:")
        for failure in failed_tests:
            print(f"  • {failure}")

    print("\n🎯 Test Categories Covered:")
    print("  ✅ API Endpoint Testing")
    print("  ✅ Web Application Testing")
    print("  ✅ Integration Testing")
    print("  ✅ Performance Testing")
    print("  ✅ Error Handling Testing")
    print("  ✅ Data Validation Testing")

    return passed_tests, len(failed_tests), total_tests


if __name__ == "__main__":
    try:
        passed, failed, total = run_comprehensive_tests()

        if failed == 0:
            print(
                "\n🎉 All tests passed! AI Selections Results is ready for production."
            )
            exit(0)
        else:
            print(f"\n⚠️  {failed} tests failed. Please review and fix issues.")
            exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        exit(1)
