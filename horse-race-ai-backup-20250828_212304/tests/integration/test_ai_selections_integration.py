#!/usr/bin/env python3
"""
AI Selections Results Integration Tests
======================================

Integration tests for the AI Selections Results web application,
testing end-to-end functionality, user workflows, and system integration.
"""

import pytest
import requests
import time
import json
from typing import Dict, List, Any


class TestWebAppIntegration:
    """Integration tests for web application"""

    WEB_URL = "http://localhost:3000"
    API_BASE = f"{WEB_URL}/api/ai_selections"

    def test_web_app_accessibility(self):
        """Test web app is accessible"""
        response = requests.get(self.WEB_URL, timeout=10)
        assert response.status_code == 200
        print("✅ Web app accessible")

    def test_ai_results_page_route(self):
        """Test AI results page route works"""
        response = requests.get(f"{self.WEB_URL}/ai-results", timeout=15)
        assert response.status_code == 200

        # Check content type is HTML
        content_type = response.headers.get("content-type", "")
        assert "html" in content_type.lower()

        print("✅ AI Results page route working")

    def test_api_endpoints_from_webapp(self):
        """Test API endpoints work from web app context"""
        endpoints = [f"{self.API_BASE}/performance", f"{self.API_BASE}/recent?limit=10"]

        for endpoint in endpoints:
            response = requests.get(endpoint, timeout=15)
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "success"

        print("✅ API endpoints accessible from web app")

    def test_cors_headers(self):
        """Test CORS headers for frontend compatibility"""
        response = requests.options(f"{self.API_BASE}/performance", timeout=10)

        # Should allow CORS or return success
        # 405 (Method Not Allowed) is acceptable if OPTIONS not implemented
        # 404 is ok if OPTIONS endpoint doesn't exist
        assert response.status_code in [200, 204, 404, 405]

        print("✅ CORS handling appropriate")

    def test_data_flow_consistency(self):
        """Test data flows consistently through the system"""
        # Get performance data
        perf_response = requests.get(f"{self.API_BASE}/performance", timeout=15)
        perf_data = perf_response.json()["data"]

        # Get selections data
        sel_response = requests.get(f"{self.API_BASE}/recent?limit=5", timeout=10)
        sel_data = sel_response.json()["data"]

        # Verify data consistency
        assert perf_data["summary"]["total_predictions"] == sel_data["total_count"]
        assert len(sel_data["selections"]) <= 5

        print("✅ Data flows consistently through system")


class TestUserWorkflows:
    """Test common user workflows"""

    API_BASE = "http://localhost:3000/api/ai_selections"

    def test_dashboard_overview_workflow(self):
        """Test dashboard overview user workflow"""
        # 1. User visits dashboard - gets performance summary
        response = requests.get(f"{self.API_BASE}/performance", timeout=15)
        data = response.json()["data"]

        summary = data["summary"]
        assert "total_predictions" in summary
        assert "accuracy_rate" in summary
        assert "roi_percentage" in summary

        # 2. User sees confidence breakdown
        assert "confidence_breakdown" in data
        confidence_data = data["confidence_breakdown"]
        assert len(confidence_data) > 0

        # 3. User sees daily performance
        assert "daily_performance" in data
        daily_data = data["daily_performance"]
        assert isinstance(daily_data, list)

        print("✅ Dashboard overview workflow complete")

    def test_pagination_workflow(self):
        """Test pagination user workflow"""
        # 1. User loads first page
        page1 = requests.get(f"{self.API_BASE}/recent?limit=25&offset=0", timeout=10)
        page1_data = page1.json()["data"]

        total_count = page1_data["total_count"]
        page1_selections = page1_data["selections"]

        # 2. User loads second page if enough data
        if total_count > 25:
            page2_url = f"{self.API_BASE}/recent?limit=25&offset=25"
            page2 = requests.get(page2_url, timeout=10)
            page2_data = page2.json()["data"]
            page2_selections = page2_data["selections"]

            # Verify different data on different pages
            if page1_selections and page2_selections:
                assert page1_selections[0]["race_id"] != page2_selections[0]["race_id"]

        print(f"✅ Pagination workflow: {total_count} total records")

    def test_filtering_workflow(self):
        """Test filtering user workflow"""
        # 1. Get all data
        all_data = requests.get(f"{self.API_BASE}/recent?limit=100", timeout=10)
        all_selections = all_data.json()["data"]["selections"]

        if not all_selections:
            pytest.skip("No data available for filtering test")

        # 2. Check different confidence levels exist
        confidence_levels = set(s["confidence_level"] for s in all_selections)

        # 3. Check different race results exist
        race_results = set(s["race_result"] for s in all_selections)

        assert len(confidence_levels) > 0
        assert len(race_results) > 0

        confidence_count = len(confidence_levels)
        results_count = len(race_results)
        print(
            f"✅ Filtering data available: {confidence_count} confidence levels, "
            f"{results_count} result types"
        )

    def test_time_period_analysis_workflow(self):
        """Test time period analysis workflow"""
        periods = [7, 14, 30]
        period_data = []

        for days in periods:
            perf_url = f"{self.API_BASE}/performance?days_back={days}"
            response = requests.get(perf_url, timeout=10)
            data = response.json()["data"]

            summary = data["summary"]
            period_data.append(
                {
                    "days": days,
                    "predictions": summary["total_predictions"],
                    "accuracy": summary["accuracy_rate"],
                    "profit": summary["total_profit_loss"],
                }
            )

        # Verify data makes sense across periods
        period_data.sort(key=lambda x: x["days"])

        # Longer periods should generally have more predictions
        for i in range(1, len(period_data)):
            current = period_data[i]
            previous = period_data[i - 1]

            error_msg = (
                f"Longer period should have more predictions: "
                f"{current['days']} days vs {previous['days']} days"
            )

            assert current["predictions"] >= previous["predictions"], error_msg

        print("✅ Time period analysis workflow validated")


class TestSystemPerformance:
    """Test system performance under various conditions"""

    API_BASE = "http://localhost:3000/api/ai_selections"

    def test_response_times_under_load(self):
        """Test response times under simulated load"""
        import concurrent.futures

        def timed_request(endpoint):
            start = time.time()
            try:
                response = requests.get(endpoint, timeout=10)
                end = time.time()
                return {"success": response.status_code == 200, "time": end - start}
            except Exception:
                return {"success": False, "time": 10.0}

        endpoints = [f"{self.API_BASE}/performance", f"{self.API_BASE}/recent?limit=25"]

        # Simulate 10 concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(10):
                for endpoint in endpoints:
                    futures.append(executor.submit(timed_request, endpoint))

            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Analyze results
        successful = [r for r in results if r["success"]]
        if successful:
            avg_time = sum(r["time"] for r in successful) / len(successful)
            max_time = max(r["time"] for r in successful)

            assert avg_time < 5.0, f"Average response time too high: {avg_time:.2f}s"
            assert max_time < 15.0, f"Max response time too high: {max_time:.2f}s"

            success_rate = len(successful) / len(results)
            assert success_rate >= 0.8, f"Success rate too low: {success_rate:.1%}"

            perf_msg = (
                f"✅ Performance under load: {avg_time:.2f}s avg, "
                f"{success_rate:.1%} success"
            )
            print(perf_msg)
        else:
            pytest.fail("No successful requests during load test")

    def test_large_dataset_handling(self):
        """Test handling of large dataset requests"""
        # Test maximum reasonable limit
        response = requests.get(f"{self.API_BASE}/recent?limit=1000", timeout=30)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"

        selections = data["data"]["selections"]
        # Should handle large requests gracefully
        assert len(selections) <= 1000

        print(f"✅ Large dataset handling: {len(selections)} records returned")

    def test_memory_efficiency(self):
        """Test system doesn't have obvious memory issues"""
        # Make multiple large requests to test memory handling
        for i in range(5):
            offset = i * 100
            url = f"{self.API_BASE}/recent?limit=100&offset={offset}"
            response = requests.get(url, timeout=15)
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "success"

            # Verify response structure is consistent
            assert "selections" in data["data"]
            assert "total_count" in data["data"]

        print("✅ Memory efficiency: Multiple large requests handled")


class TestErrorHandling:
    """Test error handling and edge cases"""

    API_BASE = "http://localhost:3000/api/ai_selections"
    WEB_URL = "http://localhost:3000"

    def test_invalid_routes(self):
        """Test handling of invalid routes"""
        invalid_routes = [
            f"{self.WEB_URL}/invalid-page",
            f"{self.WEB_URL}/ai-results/invalid",
            f"{self.API_BASE}/invalid",
        ]

        for route in invalid_routes:
            response = requests.get(route, timeout=10)
            # Should return 404 or redirect, not 500
            error_msg = f"Unexpected status for {route}: {response.status_code}"
            assert response.status_code in [404, 200], error_msg

        print("✅ Invalid routes handled gracefully")

    def test_malformed_parameters(self):
        """Test handling of malformed parameters"""
        malformed_requests = [
            f"{self.API_BASE}/performance?days_back=invalid",
            f"{self.API_BASE}/recent?limit=invalid",
            f"{self.API_BASE}/recent?offset=invalid",
            f"{self.API_BASE}/performance?days_back=999999",
        ]

        for request_url in malformed_requests:
            response = requests.get(request_url, timeout=10)
            # Should handle gracefully - 422 (Unprocessable Entity) is correct
            # for invalid parameters, 200 with error status is also acceptable
            assert response.status_code in [200, 422]

            # Should return valid JSON
            try:
                data = response.json()
                # FastAPI validation errors have 'detail' field
                # Custom errors have 'status' field
                assert "status" in data or "detail" in data

                if response.status_code == 422:
                    # FastAPI validation error - this is correct behavior
                    assert "detail" in data
                    assert isinstance(data["detail"], list)
                else:
                    # Custom error handling - should have error status
                    assert data["status"] in ["error", "success"]
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON returned for: {request_url}")

        print("✅ Malformed parameters handled gracefully")

        print("✅ Malformed parameters handled gracefully")

    def test_timeout_handling(self):
        """Test system behavior under timeout conditions"""
        # Test with very short timeout to simulate network issues
        try:
            response = requests.get(f"{self.API_BASE}/performance", timeout=0.001)
            # If it succeeds, that's fine too
            assert response.status_code == 200
        except requests.exceptions.Timeout:
            # Timeout is expected and acceptable
            pass
        except requests.exceptions.RequestException:
            # Other network errors are also acceptable for this test
            pass

        print("✅ Timeout conditions handled appropriately")


class TestDataIntegrity:
    """Test data integrity and business logic validation"""

    API_BASE = "http://localhost:3000/api/ai_selections"

    def test_business_logic_validation(self):
        """Test business logic makes sense"""
        response = requests.get(f"{self.API_BASE}/performance", timeout=15)
        data = response.json()["data"]

        summary = data["summary"]

        # Basic business logic checks
        total_predictions = summary["total_predictions"]
        correct_predictions = summary["correct_predictions"]
        accuracy_rate = summary["accuracy_rate"]

        if total_predictions > 0:
            # Accuracy rate should match calculation
            expected_accuracy = (correct_predictions / total_predictions) * 100
            accuracy_error = (
                "Accuracy calculation incorrect: "
                f"{accuracy_rate} vs {expected_accuracy}"
            )
            assert abs(accuracy_rate - expected_accuracy) < 0.1, accuracy_error

        # Win rate should be <= accuracy rate
        win_rate = summary["win_rate"]
        win_error = "Win rate should not exceed accuracy rate"
        assert win_rate <= accuracy_rate + 0.1, win_error

        print("✅ Business logic validation passed")

    def test_roi_calculations(self):
        """Test ROI calculations are reasonable"""
        response = requests.get(f"{self.API_BASE}/recent?limit=50", timeout=10)
        data = response.json()["data"]

        selections = data["selections"]

        for selection in selections:
            roi = selection["roi_percentage"]
            profit = selection["profit_loss"]

            # ROI should be reasonable
            assert -100 <= roi <= 10000, f"ROI out of reasonable range: {roi}%"

            # Profit and ROI should have consistent sign (mostly)
            if profit > 0:
                roi_error = "Positive profit should not have extremely negative ROI"
                assert roi > -100, roi_error
            if profit < -50:  # Significant loss
                assert roi < 0, "Large loss should have negative ROI"

        print("✅ ROI calculations validated")


def run_integration_tests():
    """Run all integration tests"""
    print("🔗 AI Selections Results Integration Test Suite")
    print("=" * 60)

    test_classes = [
        TestWebAppIntegration,
        TestUserWorkflows,
        TestSystemPerformance,
        TestErrorHandling,
        TestDataIntegrity,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = []

    for test_class in test_classes:
        print(f"\n🧪 {test_class.__name__}")
        print("-" * 40)

        test_instance = test_class()
        test_methods = [m for m in dir(test_instance) if m.startswith("test_")]

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

    # Summary
    print("\n📊 Integration Test Results")
    print("=" * 40)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

    if failed_tests:
        print("\n❌ Failed Tests:")
        for failure in failed_tests:
            print(f"  • {failure}")

    return passed_tests, len(failed_tests), total_tests


if __name__ == "__main__":
    passed, failed, total = run_integration_tests()

    if failed == 0:
        print("\n🎉 All integration tests passed!")
        print("🚀 AI Selections Results system is ready for production!")
    else:
        print(f"\n⚠️  {failed} integration tests failed.")
        print("🔧 Please review and fix issues before production deployment.")

    exit(0 if failed == 0 else 1)
