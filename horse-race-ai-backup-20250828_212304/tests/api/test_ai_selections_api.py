#!/usr/bin/env python3
"""
AI Selections API Tests
======================

Focused test suite for the AI Selections API endpoints,
including performance, pagination, and data validation tests.
"""

import pytest
import requests
import json
import time
from typing import Dict, List, Any


class TestAISelectionsPerformanceAPI:
    """Test suite for AI Selections Performance API"""

    BASE_URL = "http://localhost:3000"
    ENDPOINT = f"{BASE_URL}/api/ai_selections/performance"

    def test_performance_endpoint_success(self):
        """Test performance endpoint returns success"""
        response = requests.get(self.ENDPOINT, timeout=10)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        print("✅ Performance API endpoint working")

    def test_performance_summary_structure(self):
        """Test performance summary data structure"""
        response = requests.get(self.ENDPOINT, timeout=10)
        data = response.json()

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
            assert field in summary
            assert isinstance(summary[field], (int, float))

        # Validate ranges
        assert 0 <= summary["accuracy_rate"] <= 100
        assert 0 <= summary["win_rate"] <= 100
        assert 0 <= summary["place_rate"] <= 100

        print(
            f"✅ Performance summary: {summary['total_predictions']} "
            f"predictions, {summary['accuracy_rate']}% accuracy"
        )

    def test_confidence_breakdown(self):
        """Test confidence breakdown data"""
        response = requests.get(self.ENDPOINT, timeout=10)
        data = response.json()

        confidence_data = data["data"]["confidence_breakdown"]
        assert isinstance(confidence_data, dict)

        for level, stats in confidence_data.items():
            assert level in ["High", "Medium", "Low"]
            assert "total_bets" in stats
            assert "accuracy_rate" in stats
            assert stats["total_bets"] >= 0
            assert 0 <= stats["accuracy_rate"] <= 100

        print(f"✅ Confidence breakdown: {len(confidence_data)} levels")

    def test_daily_performance(self):
        """Test daily performance data"""
        response = requests.get(self.ENDPOINT, timeout=10)
        data = response.json()

        daily_data = data["data"]["daily_performance"]
        assert isinstance(daily_data, list)

        if daily_data:
            sample = daily_data[0]
            required_fields = ["date", "bets", "wins", "profit", "roi"]
            for field in required_fields:
                assert field in sample

        print(f"✅ Daily performance: {len(daily_data)} days")

    def test_best_worst_performers(self):
        """Test best and worst performers data"""
        response = requests.get(self.ENDPOINT, timeout=10)
        data = response.json()

        best = data["data"]["best_performers"]
        worst = data["data"]["worst_performers"]

        assert isinstance(best, list)
        assert isinstance(worst, list)

        if best:
            assert "horse_name" in best[0]
            assert "profit_loss" in best[0]
            assert "race_result" in best[0]

        print(f"✅ Performers: {len(best)} best, {len(worst)} worst")

    def test_days_back_parameter(self):
        """Test days_back parameter functionality"""
        test_periods = [7, 14, 30, 60]

        for days in test_periods:
            response = requests.get(f"{self.ENDPOINT}?days_back={days}", timeout=10)
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "success"

        print("✅ Days back parameter working")


class TestAISelectionsRecentAPI:
    """Test suite for AI Selections Recent API"""

    BASE_URL = "http://localhost:3000"
    ENDPOINT = f"{BASE_URL}/api/ai_selections/recent"

    def test_recent_endpoint_success(self):
        """Test recent selections endpoint returns success"""
        response = requests.get(self.ENDPOINT, timeout=10)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        print("✅ Recent selections API endpoint working")

    def test_pagination_structure(self):
        """Test pagination data structure"""
        response = requests.get(self.ENDPOINT, timeout=10)
        data = response.json()

        result = data["data"]
        required_fields = ["selections", "total_count", "limit", "offset"]

        for field in required_fields:
            assert field in result

        assert isinstance(result["selections"], list)
        assert isinstance(result["total_count"], int)
        assert result["total_count"] > 0

        print(f"✅ Pagination: {result['total_count']} total records")

    def test_selection_record_structure(self):
        """Test individual selection record structure"""
        response = requests.get(f"{self.ENDPOINT}?limit=5", timeout=10)
        data = response.json()

        selections = data["data"]["selections"]
        if not selections:
            pytest.skip("No selection data available")

        sample = selections[0]
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
            assert field in sample

        # Validate data types and values
        assert isinstance(sample["ai_probability"], (int, float))
        assert 0 <= sample["ai_probability"] <= 100
        assert sample["confidence_level"] in ["High", "Medium", "Low"]
        assert sample["race_result"] in ["WIN", "PLACE", "LOSE"]

        print("✅ Selection record structure validated")

    def test_pagination_limits(self):
        """Test pagination with different limits"""
        test_limits = [5, 10, 25, 50, 100]

        for limit in test_limits:
            response = requests.get(f"{self.ENDPOINT}?limit={limit}", timeout=10)
            assert response.status_code == 200

            data = response.json()
            result = data["data"]

            assert result["limit"] == limit
            assert len(result["selections"]) <= limit

        print("✅ Pagination limits working correctly")

    def test_pagination_offsets(self):
        """Test pagination with different offsets"""
        offsets = [0, 10, 25, 50]

        for offset in offsets:
            response = requests.get(
                f"{self.ENDPOINT}?limit=10&offset={offset}", timeout=10
            )
            assert response.status_code == 200

            data = response.json()
            result = data["data"]

            assert result["offset"] == offset
            assert result["limit"] == 10

        print("✅ Pagination offsets working correctly")

    def test_large_offset_handling(self):
        """Test handling of large offsets"""
        response = requests.get(f"{self.ENDPOINT}?offset=10000&limit=10", timeout=10)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"

        # Should return empty selections for large offset
        result = data["data"]
        assert len(result["selections"]) == 0

        print("✅ Large offset handling working")


class TestAPIPerformance:
    """Test suite for API performance and reliability"""

    BASE_URL = "http://localhost:3000"

    def test_response_times(self):
        """Test API response times are acceptable"""
        endpoints = [
            "/api/ai_selections/performance",
            "/api/ai_selections/recent?limit=25",
        ]

        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{self.BASE_URL}{endpoint}", timeout=15)
            end_time = time.time()

            assert response.status_code == 200

            response_time = end_time - start_time
            assert response_time < 10.0, f"Response too slow: {response_time:.2f}s"

            print(f"✅ {endpoint}: {response_time:.2f}s")

    def test_concurrent_requests(self):
        """Test API can handle concurrent requests"""
        import concurrent.futures

        def make_request():
            try:
                response = requests.get(
                    f"{self.BASE_URL}/api/ai_selections/performance", timeout=10
                )
                return response.status_code == 200
            except:
                return False

        # Make 20 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8, f"Success rate too low: {success_rate:.1%}"

        print(f"✅ Concurrent requests: {success_rate:.1%} success rate")

    def test_error_recovery(self):
        """Test API error handling and recovery"""
        # Test with invalid parameters
        invalid_requests = [
            "/api/ai_selections/performance?days_back=-1",
            "/api/ai_selections/recent?limit=-5",
            "/api/ai_selections/recent?offset=-10",
        ]

        for endpoint in invalid_requests:
            response = requests.get(f"{self.BASE_URL}{endpoint}", timeout=10)
            # Should return 200 with error handling or valid default behavior
            assert response.status_code == 200

        print("✅ Error recovery working")


class TestDataValidation:
    """Test suite for data validation and consistency"""

    BASE_URL = "http://localhost:3000"

    def test_data_consistency(self):
        """Test data consistency between endpoints"""
        # Get performance summary
        perf_response = requests.get(
            f"{self.BASE_URL}/api/ai_selections/performance", timeout=10
        )
        perf_data = perf_response.json()
        total_predictions = perf_data["data"]["summary"]["total_predictions"]

        # Get recent selections total count
        recent_response = requests.get(
            f"{self.BASE_URL}/api/ai_selections/recent?limit=1", timeout=10
        )
        recent_data = recent_response.json()
        total_count = recent_data["data"]["total_count"]

        # Should be consistent
        assert (
            total_predictions == total_count
        ), f"Inconsistent totals: {total_predictions} vs {total_count}"

        print(f"✅ Data consistency: {total_predictions} predictions")

    def test_profit_loss_calculations(self):
        """Test profit/loss calculations are valid"""
        response = requests.get(
            f"{self.BASE_URL}/api/ai_selections/recent?limit=10", timeout=10
        )
        data = response.json()

        selections = data["data"]["selections"]
        for selection in selections:
            profit = selection["profit_loss"]
            roi = selection["roi_percentage"]

            # Basic validation
            assert isinstance(profit, (int, float))
            assert isinstance(roi, (int, float))

            # ROI should be reasonable (allowing for high-odds selections)
            assert -100 <= roi <= 10000  # -100% to 10000% is reasonable range

        print("✅ Profit/loss calculations validated")

    def test_date_formats(self):
        """Test date formats are consistent"""
        response = requests.get(
            f"{self.BASE_URL}/api/ai_selections/recent?limit=5", timeout=10
        )
        data = response.json()

        selections = data["data"]["selections"]
        for selection in selections:
            selection_date = selection["selection_date"]

            # Should be valid ISO date format
            try:
                from datetime import datetime

                datetime.fromisoformat(selection_date.replace("Z", "+00:00"))
            except ValueError:
                pytest.fail(f"Invalid date format: {selection_date}")

        print("✅ Date formats validated")


def run_api_tests():
    """Run all API tests"""
    print("🧪 AI Selections API Test Suite")
    print("=" * 50)

    test_classes = [
        TestAISelectionsPerformanceAPI,
        TestAISelectionsRecentAPI,
        TestAPIPerformance,
        TestDataValidation,
    ]

    total_tests = 0
    passed_tests = 0

    for test_class in test_classes:
        print(f"\n📊 {test_class.__name__}")
        print("-" * 30)

        test_instance = test_class()
        test_methods = [m for m in dir(test_instance) if m.startswith("test_")]

        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                passed_tests += 1
            except Exception as e:
                print(f"❌ {method_name}: {e}")

    print(f"\n📈 Results: {passed_tests}/{total_tests} tests passed")
    return passed_tests, total_tests


if __name__ == "__main__":
    passed, total = run_api_tests()
    if passed == total:
        print("🎉 All API tests passed!")
    else:
        print(f"⚠️  {total - passed} tests failed")
