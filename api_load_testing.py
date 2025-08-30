#!/usr/bin/env python3
"""
Horse Racing AI - API Load Testing Suite
========================================

Comprehensive testing of all 5 automation API endpoints under load
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import requests

NODE_RED_URL = "http://c2.horse-racing.local"


class APILoadTester:
    """API Load Testing for Horse Racing AI Automation"""

    def __init__(self):
        self.base_url = f"{NODE_RED_URL}/api/pipeline"
        self.endpoints = [
            "trigger",  # Manual pipeline
            "data_relationships",  # Data relationships
            "performance_tracker",  # Performance tracking
            "ml_training",  # ML model training
            "ai_selections",  # AI race selections
        ]
        self.results = {}

    def test_single_endpoint(self, endpoint: str) -> dict:
        """Test a single endpoint and measure performance"""
        url = f"{self.base_url}/{endpoint}"

        try:
            start_time = time.time()
            response = requests.post(url, timeout=30)
            end_time = time.time()

            return {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200,
                "response_size": len(response.content),
                "content": response.text[:200] if response.text else "",
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "status_code": 0,
                "response_time": 0,
                "success": False,
                "error": str(e),
            }

    def concurrent_test(self, endpoint: str, num_requests: int = 5) -> list:
        """Test endpoint with concurrent requests"""
        print(f"🔄 Testing {endpoint} with {num_requests} concurrent requests...")

        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [
                executor.submit(self.test_single_endpoint, endpoint)
                for _ in range(num_requests)
            ]
            results = [future.result() for future in futures]

        return results

    def sequential_test(self, endpoint: str, num_requests: int = 3) -> list:
        """Test endpoint with sequential requests"""
        print(f"🔄 Testing {endpoint} with {num_requests} sequential requests...")

        results = []
        for i in range(num_requests):
            result = self.test_single_endpoint(endpoint)
            results.append(result)
            time.sleep(1)  # 1 second delay between requests

        return results

    def analyze_results(self, results: list, test_type: str, endpoint: str):
        """Analyze test results and generate metrics"""
        if not results:
            return

        successful_results = [r for r in results if r.get("success", False)]
        response_times = [r["response_time"] for r in successful_results]

        if not response_times:
            print(f"❌ {endpoint} ({test_type}): All requests failed")
            return

        metrics = {
            "endpoint": endpoint,
            "test_type": test_type,
            "total_requests": len(results),
            "successful_requests": len(successful_results),
            "success_rate": len(successful_results) / len(results) * 100,
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "median_response_time": statistics.median(response_times),
        }

        if len(response_times) > 1:
            metrics["std_dev"] = statistics.stdev(response_times)

        # Store results
        if endpoint not in self.results:
            self.results[endpoint] = {}
        self.results[endpoint][test_type] = metrics

        # Print results
        print(f"✅ {endpoint} ({test_type}):")
        print(f"   Success Rate: {metrics['success_rate']:.1f}%")
        print(f"   Avg Response: {metrics['avg_response_time']:.3f}s")
        print(
            f"   Min/Max: {metrics['min_response_time']:.3f}s / {metrics['max_response_time']:.3f}s"
        )
        print(f"   Median: {metrics['median_response_time']:.3f}s")
        if "std_dev" in metrics:
            print(f"   Std Dev: {metrics['std_dev']:.3f}s")
        print("")

    def run_comprehensive_test(self):
        """Run comprehensive load testing on all endpoints"""
        print("🚀 HORSE RACING AI - API LOAD TESTING")
        print("=" * 60)
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Base URL: {self.base_url}")
        print(f"📊 Testing {len(self.endpoints)} endpoints")
        print("")

        for endpoint in self.endpoints:
            print(f"🎯 TESTING ENDPOINT: {endpoint}")
            print("-" * 40)

            # Sequential test
            sequential_results = self.sequential_test(endpoint, 3)
            self.analyze_results(sequential_results, "sequential", endpoint)

            # Concurrent test
            concurrent_results = self.concurrent_test(endpoint, 3)
            self.analyze_results(concurrent_results, "concurrent", endpoint)

            time.sleep(2)  # Brief pause between endpoints

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("📊 LOAD TESTING SUMMARY REPORT")
        print("=" * 50)

        all_endpoints_working = True
        total_endpoints = len(self.endpoints)
        working_endpoints = 0

        for endpoint in self.endpoints:
            if endpoint in self.results:
                sequential = self.results[endpoint].get("sequential", {})
                concurrent = self.results[endpoint].get("concurrent", {})

                seq_success = sequential.get("success_rate", 0)
                conc_success = concurrent.get("success_rate", 0)

                if seq_success > 0 or conc_success > 0:
                    working_endpoints += 1
                    status = "✅ WORKING"
                else:
                    all_endpoints_working = False
                    status = "❌ FAILED"

                print(f"{status} {endpoint}")
                if sequential:
                    print(
                        f"    Sequential: {seq_success:.1f}% success, {sequential.get('avg_response_time', 0):.3f}s avg"
                    )
                if concurrent:
                    print(
                        f"    Concurrent: {conc_success:.1f}% success, {concurrent.get('avg_response_time', 0):.3f}s avg"
                    )
                print("")
            else:
                all_endpoints_working = False
                print(f"❌ FAILED {endpoint} (No test results)")
                print("")

        print("🎯 OVERALL RESULTS:")
        print(f"• Working Endpoints: {working_endpoints}/{total_endpoints}")
        print(f"• Success Rate: {working_endpoints/total_endpoints*100:.1f}%")

        if all_endpoints_working:
            print("• Status: ✅ ALL ENDPOINTS OPERATIONAL")
        else:
            print("• Status: ⚠️  SOME ENDPOINTS HAVE ISSUES")

        # Performance recommendations
        print("\n💡 PERFORMANCE RECOMMENDATIONS:")
        fast_endpoints = []
        slow_endpoints = []

        for endpoint, tests in self.results.items():
            sequential = tests.get("sequential", {})
            avg_time = sequential.get("avg_response_time", 0)

            if avg_time < 1.0:
                fast_endpoints.append(f"{endpoint} ({avg_time:.3f}s)")
            elif avg_time > 3.0:
                slow_endpoints.append(f"{endpoint} ({avg_time:.3f}s)")

        if fast_endpoints:
            print(f"• Fast Endpoints: {', '.join(fast_endpoints)}")
        if slow_endpoints:
            print(f"• Slow Endpoints: {', '.join(slow_endpoints)}")
            print("  Consider optimization for slow endpoints")

        return all_endpoints_working

    def save_results_to_file(self):
        """Save detailed results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_load_test_results_{timestamp}.json"

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "endpoints_tested": self.endpoints,
            "results": self.results,
        }

        with open(filename, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"📄 Detailed results saved to: {filename}")


def main():
    """Run the complete API load testing suite"""
    tester = APILoadTester()

    try:
        # Run comprehensive testing
        tester.run_comprehensive_test()

        # Generate summary
        all_working = tester.generate_summary_report()

        # Save results
        tester.save_results_to_file()

        print("\n🎉 API LOAD TESTING COMPLETE!")

        if all_working:
            print("✅ All automation endpoints are operational and performing well")
        else:
            print("⚠️  Some endpoints need attention - check the report above")

        return all_working

    except Exception as e:
        print(f"❌ Load testing failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
