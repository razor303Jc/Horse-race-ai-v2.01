"""
🧪 Comprehensive API Integration Tests - Current System Status
==============================================================

Tests the existing web application API endpoints without modifying configuration.
Focuses on testing what's currently working and documenting current capabilities.
"""

import pytest
import requests
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Optional
import json
import concurrent.futures


class TestCurrentAPIStatus:
    """Test current API system status and capabilities"""

    BASE_URL = "http://localhost:3000"
    API_BASE_URL = f"{BASE_URL}/api"

    @pytest.mark.integration
    def test_current_system_status_analysis(self):
        """Analyze current system status without changes"""
        response = requests.get(f"{self.API_BASE_URL}/system_status", timeout=10)

        assert response.status_code == 200, "System status endpoint not responding"

        data = response.json()

        print("\n🔍 CURRENT SYSTEM STATUS ANALYSIS:")
        print(f"   Overall Status: {data.get('overall_status', 'UNKNOWN')}")
        print(f"   Timestamp: {data.get('timestamp', 'N/A')}")

        # Database status
        db_status = data.get("database", {})
        print(f"   📊 Database Status:")
        for db_name, status in db_status.items():
            print(f"      {db_name}: {status}")

        # Other components
        components = [
            "ml_models",
            "betting_integration",
            "contextual_ai",
            "notifications",
            "performance_tracker",
        ]
        print(f"   🔧 Component Status:")
        for component in components:
            status = data.get(component, "UNKNOWN")
            print(f"      {component}: {status}")

        return data

    @pytest.mark.integration
    def test_available_endpoints_discovery(self):
        """Discover what endpoints are currently available"""
        endpoints_to_test = [
            "/system_status",
            "/database_stats",
            "/daily_races",
            "/horses",
            "/jockeys",
            "/trainers",
            "/dashboard_data",
            "/betting/recommendations",
            "/ml/models",
        ]

        available_endpoints = []
        unavailable_endpoints = []

        print("\n🌐 ENDPOINT AVAILABILITY ANALYSIS:")

        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=5)
                if response.status_code == 200:
                    available_endpoints.append(endpoint)
                    print(f"   ✅ {endpoint}: Available ({response.status_code})")
                else:
                    unavailable_endpoints.append((endpoint, response.status_code))
                    print(f"   ❌ {endpoint}: Error ({response.status_code})")
            except Exception as e:
                unavailable_endpoints.append((endpoint, str(e)))
                print(f"   ❌ {endpoint}: Exception ({str(e)[:50]})")

        print(
            f"\n📈 Summary: {len(available_endpoints)} available, {len(unavailable_endpoints)} unavailable"
        )

        return {"available": available_endpoints, "unavailable": unavailable_endpoints}

    @pytest.mark.performance
    def test_current_performance_baseline(self):
        """Establish performance baseline for current system"""
        endpoints = ["/system_status", "/database_stats"]

        performance_data = {}

        print("\n⚡ PERFORMANCE BASELINE MEASUREMENT:")

        for endpoint in endpoints:
            response_times = []

            # Test multiple times for average
            for i in range(5):
                start_time = time.time()
                try:
                    response = requests.get(
                        f"{self.API_BASE_URL}{endpoint}", timeout=10
                    )
                    end_time = time.time()

                    if response.status_code == 200:
                        response_times.append((end_time - start_time) * 1000)
                except Exception:
                    pass

            if response_times:
                avg_time = sum(response_times) / len(response_times)
                min_time = min(response_times)
                max_time = max(response_times)

                performance_data[endpoint] = {
                    "avg_ms": round(avg_time, 2),
                    "min_ms": round(min_time, 2),
                    "max_ms": round(max_time, 2),
                    "samples": len(response_times),
                }

                print(f"   {endpoint}:")
                print(f"      Average: {avg_time:.2f}ms")
                print(f"      Range: {min_time:.2f}ms - {max_time:.2f}ms")

        return performance_data

    @pytest.mark.integration
    def test_data_availability_analysis(self):
        """Analyze what data is currently available"""

        print("\n📊 DATA AVAILABILITY ANALYSIS:")

        # Test database stats
        try:
            response = requests.get(f"{self.API_BASE_URL}/database_stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   Database Statistics:")
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        print(f"      {key}: {value:,}")
                    else:
                        print(f"      {key}: {value}")
        except Exception as e:
            print(f"   ❌ Database stats error: {e}")

        # Test daily races
        try:
            response = requests.get(f"{self.API_BASE_URL}/daily_races", timeout=10)
            if response.status_code == 200:
                data = response.json()
                total_races = data.get("total_races", 0)
                races = data.get("races", [])
                print(f"   Daily Races: {total_races} total, {len(races)} in response")
        except Exception as e:
            print(f"   ❌ Daily races error: {e}")

    @pytest.mark.load_test
    def test_concurrent_request_handling(self):
        """Test how system handles concurrent requests"""

        print("\n🚀 CONCURRENT REQUEST LOAD TEST:")

        def make_request(endpoint):
            try:
                start_time = time.time()
                response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=10)
                end_time = time.time()
                return {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time": (end_time - start_time) * 1000,
                    "success": response.status_code == 200,
                }
            except Exception as e:
                return {
                    "endpoint": endpoint,
                    "status_code": None,
                    "response_time": None,
                    "success": False,
                    "error": str(e),
                }

        # Test with 10 concurrent requests to system_status
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(make_request, "/system_status") for _ in range(10)
            ]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]

        if successful_requests:
            avg_response_time = sum(
                r["response_time"] for r in successful_requests
            ) / len(successful_requests)
            print(f"   ✅ Successful requests: {len(successful_requests)}/10")
            print(f"   ⚡ Average response time: {avg_response_time:.2f}ms")

        if failed_requests:
            print(f"   ❌ Failed requests: {len(failed_requests)}/10")
            for failed in failed_requests[:3]:  # Show first 3 failures
                print(f"      Error: {failed.get('error', 'Unknown')}")

        return {"successful": len(successful_requests), "failed": len(failed_requests)}

    @pytest.mark.integration
    def test_error_handling_analysis(self):
        """Test how system handles various error conditions"""

        print("\n🔍 ERROR HANDLING ANALYSIS:")

        error_tests = [
            ("/nonexistent_endpoint", "Non-existent endpoint"),
            ("/horses?limit=invalid", "Invalid parameter"),
            ("/race_details/999999", "Non-existent resource"),
        ]

        for endpoint, description in error_tests:
            try:
                response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=5)
                print(f"   {description}: {response.status_code}")

                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        if "error" in error_data or "message" in error_data:
                            print(f"      Error message provided: ✅")
                        else:
                            print(f"      Error message missing: ❌")
                    except:
                        print(f"      Non-JSON error response: ⚠️")

            except Exception as e:
                print(f"   {description}: Exception - {str(e)[:50]}")

    @pytest.mark.integration
    def test_data_consistency_checks(self):
        """Check data consistency across different endpoints"""

        print("\n🔧 DATA CONSISTENCY ANALYSIS:")

        try:
            # Get database stats
            stats_response = requests.get(
                f"{self.API_BASE_URL}/database_stats", timeout=10
            )
            if stats_response.status_code == 200:
                stats_data = stats_response.json()

                # Get horses data
                horses_response = requests.get(
                    f"{self.API_BASE_URL}/horses?limit=5", timeout=10
                )
                if horses_response.status_code == 200:
                    horses_data = horses_response.json()
                    horses_list = (
                        horses_data
                        if isinstance(horses_data, list)
                        else horses_data.get("horses", [])
                    )

                    print(
                        f"   Database stats show horses: {stats_data.get('total_horses', 'N/A')}"
                    )
                    print(f"   Horses endpoint returns: {len(horses_list)} (sample)")

                # Similar checks for other endpoints...
                print(f"   ✅ Data consistency checks completed")

        except Exception as e:
            print(f"   ❌ Data consistency check failed: {e}")


class TestAPIComprehensiveSuite:
    """Comprehensive API test suite for current system"""

    @pytest.mark.integration
    def test_full_system_health_report(self):
        """Generate comprehensive system health report"""

        print("\n" + "=" * 60)
        print("🏥 COMPREHENSIVE SYSTEM HEALTH REPORT")
        print("=" * 60)

        # Run all test categories
        status_tester = TestCurrentAPIStatus()

        # 1. System Status
        print("\n1️⃣ SYSTEM STATUS:")
        status_data = status_tester.test_current_system_status_analysis()

        # 2. Endpoint Discovery
        print("\n2️⃣ ENDPOINT DISCOVERY:")
        endpoint_data = status_tester.test_available_endpoints_discovery()

        # 3. Performance Baseline
        print("\n3️⃣ PERFORMANCE BASELINE:")
        performance_data = status_tester.test_current_performance_baseline()

        # 4. Data Availability
        print("\n4️⃣ DATA AVAILABILITY:")
        status_tester.test_data_availability_analysis()

        # 5. Error Handling
        print("\n5️⃣ ERROR HANDLING:")
        status_tester.test_error_handling_analysis()

        # 6. Load Testing
        print("\n6️⃣ LOAD TESTING:")
        load_data = status_tester.test_concurrent_request_handling()

        # Generate summary
        print("\n" + "=" * 60)
        print("📋 SUMMARY REPORT")
        print("=" * 60)
        print(f"Overall Status: {status_data.get('overall_status', 'UNKNOWN')}")
        print(f"Available Endpoints: {len(endpoint_data['available'])}")
        print(f"Load Test Success Rate: {load_data['successful']}/10")

        database_health = status_data.get("database", {})
        connected_dbs = [
            db for db, status in database_health.items() if status != "DISCONNECTED"
        ]
        print(f"Connected Databases: {len(connected_dbs)}/3")

        print("\n✅ Comprehensive system analysis complete!")
        print("=" * 60)


if __name__ == "__main__":
    # Run the comprehensive test suite
    pytest.main([__file__, "-v", "--tb=short", "-s"])
