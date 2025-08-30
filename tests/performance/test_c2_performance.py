"""
🚀 C2 Command Center Performance Test Suite
===========================================

Performance and load testing for the C2 Command Center system.
Tests response times, throughput, memory usage, and scalability.
"""

import pytest
import requests
import time
import threading
import concurrent.futures
import psutil
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import statistics


class TestC2PerformanceBaseline:
    """Baseline performance tests for C2 components"""

    def test_dashboard_load_time_baseline(self):
        """Test dashboard initial load time"""
        url = "http://localhost:1881/c2-dashboard"
        
        # Warm up
        try:
            requests.get(url, timeout=5)
        except Exception:
            pytest.skip("C2 Dashboard not accessible")
        
        # Measure load times
        load_times = []
        for i in range(5):
            start_time = time.time()
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    load_time = time.time() - start_time
                    load_times.append(load_time)
            except Exception as e:
                pytest.skip(f"Dashboard not responding: {e}")
        
        if load_times:
            avg_load_time = statistics.mean(load_times)
            max_load_time = max(load_times)
            
            # Performance targets
            assert avg_load_time < 5.0, f"Average load time {avg_load_time:.2f}s > 5s"
            assert max_load_time < 10.0, f"Max load time {max_load_time:.2f}s > 10s"
            
            print(f"Dashboard load time - Avg: {avg_load_time:.2f}s, Max: {max_load_time:.2f}s")

    def test_api_response_time_baseline(self):
        """Test API endpoint response times"""
        endpoints = [
            "http://localhost:1881/containers/status",
            "http://localhost:1881/docker/stats",
            "http://localhost:3000/api/processing/stats"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            response_times = []
            
            # Warm up
            try:
                requests.get(endpoint, timeout=5)
            except Exception:
                continue
            
            # Measure response times
            for i in range(10):
                start_time = time.time()
                try:
                    response = requests.get(endpoint, timeout=15)
                    if response.status_code == 200:
                        response_time = time.time() - start_time
                        response_times.append(response_time)
                except Exception:
                    pass
            
            if response_times:
                avg_time = statistics.mean(response_times)
                p95_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
                
                results[endpoint] = {
                    "avg": avg_time,
                    "p95": p95_time,
                    "count": len(response_times)
                }
                
                # Performance targets
                assert avg_time < 5.0, f"{endpoint} avg response {avg_time:.2f}s > 5s"
                assert p95_time < 10.0, f"{endpoint} p95 response {p95_time:.2f}s > 10s"
        
        assert len(results) > 0, "No endpoints responded successfully"
        
        for endpoint, metrics in results.items():
            print(f"{endpoint}: Avg {metrics['avg']:.2f}s, P95 {metrics['p95']:.2f}s")

    def test_memory_usage_baseline(self):
        """Test system memory usage during operations"""
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform typical operations
        operations = [
            lambda: requests.get("http://localhost:1881/c2-dashboard", timeout=10),
            lambda: requests.get("http://localhost:1881/containers/status", timeout=10),
            lambda: requests.get("http://localhost:1881/docker/stats", timeout=10),
        ]
        
        for operation in operations:
            try:
                operation()
                time.sleep(0.5)  # Allow processing
            except Exception:
                pass
        
        # Check final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: Initial {initial_memory:.1f}MB, Final {final_memory:.1f}MB, Increase {memory_increase:.1f}MB")
        
        # Memory increase should be reasonable
        assert memory_increase < 100, f"Memory increase {memory_increase:.1f}MB too high"


class TestC2LoadTesting:
    """Load testing for C2 system components"""

    def test_concurrent_dashboard_requests(self):
        """Test concurrent dashboard access"""
        url = "http://localhost:1881/c2-dashboard"
        num_threads = 10
        requests_per_thread = 5
        
        def make_requests():
            results = []
            for i in range(requests_per_thread):
                start_time = time.time()
                try:
                    response = requests.get(url, timeout=15)
                    response_time = time.time() - start_time
                    results.append({
                        "status": response.status_code,
                        "time": response_time,
                        "success": response.status_code == 200
                    })
                except Exception as e:
                    results.append({
                        "status": 0,
                        "time": 15.0,
                        "success": False,
                        "error": str(e)
                    })
                time.sleep(0.1)  # Small delay between requests
            return results
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_requests) for _ in range(num_threads)]
            all_results = []
            for future in concurrent.futures.as_completed(futures, timeout=60):
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    pytest.skip(f"Concurrent test failed: {e}")
        
        if not all_results:
            pytest.skip("No requests completed successfully")
        
        # Analyze results
        successful_requests = [r for r in all_results if r["success"]]
        success_rate = len(successful_requests) / len(all_results)
        
        if successful_requests:
            avg_response_time = statistics.mean([r["time"] for r in successful_requests])
            max_response_time = max([r["time"] for r in successful_requests])
            
            print(f"Load test results: {success_rate:.1%} success rate, "
                  f"avg {avg_response_time:.2f}s, max {max_response_time:.2f}s")
            
            # Performance expectations under load
            assert success_rate >= 0.8, f"Success rate {success_rate:.1%} < 80%"
            assert avg_response_time < 10.0, f"Avg response time {avg_response_time:.2f}s > 10s"

    def test_api_endpoint_load(self):
        """Test API endpoint load handling"""
        endpoint = "http://localhost:1881/containers/status"
        num_workers = 8
        duration_seconds = 30
        
        stop_flag = threading.Event()
        results = []
        results_lock = threading.Lock()
        
        def worker():
            worker_results = []
            while not stop_flag.is_set():
                start_time = time.time()
                try:
                    response = requests.get(endpoint, timeout=10)
                    response_time = time.time() - start_time
                    worker_results.append({
                        "timestamp": start_time,
                        "response_time": response_time,
                        "status": response.status_code,
                        "success": response.status_code == 200
                    })
                except Exception as e:
                    worker_results.append({
                        "timestamp": start_time,
                        "response_time": 10.0,
                        "status": 0,
                        "success": False,
                        "error": str(e)
                    })
                time.sleep(0.5)  # Rate limiting
            
            with results_lock:
                results.extend(worker_results)
        
        # Start workers
        threads = []
        for i in range(num_workers):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Run for specified duration
        time.sleep(duration_seconds)
        stop_flag.set()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        if not results:
            pytest.skip("No API requests completed")
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        total_requests = len(results)
        success_rate = len(successful_requests) / total_requests
        requests_per_second = total_requests / duration_seconds
        
        if successful_requests:
            avg_response_time = statistics.mean([r["response_time"] for r in successful_requests])
            
            print(f"API load test: {requests_per_second:.1f} req/s, "
                  f"{success_rate:.1%} success, avg {avg_response_time:.2f}s")
            
            # Performance expectations
            assert success_rate >= 0.7, f"API success rate {success_rate:.1%} < 70%"
            assert avg_response_time < 8.0, f"API avg response {avg_response_time:.2f}s > 8s"

    def test_database_connection_load(self):
        """Test database connection handling under load"""
        try:
            import psycopg2
        except ImportError:
            pytest.skip("psycopg2 not available")
        
        num_connections = 5
        operations_per_connection = 10
        
        def test_connection():
            results = []
            for i in range(operations_per_connection):
                start_time = time.time()
                try:
                    # Test connection to cards database
                    conn = psycopg2.connect(
                        host="localhost",
                        port=5432,
                        database="cards_db",
                        user="postgres",
                        password="password123"
                    )
                    
                    with conn:
                        with conn.cursor() as cursor:
                            cursor.execute("SELECT 1")
                            cursor.fetchone()
                    
                    conn.close()
                    
                    response_time = time.time() - start_time
                    results.append({
                        "success": True,
                        "time": response_time
                    })
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    results.append({
                        "success": False,
                        "time": response_time,
                        "error": str(e)
                    })
                
                time.sleep(0.2)  # Small delay
            
            return results
        
        # Execute concurrent database operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_connections) as executor:
            futures = [executor.submit(test_connection) for _ in range(num_connections)]
            all_results = []
            
            for future in concurrent.futures.as_completed(futures, timeout=120):
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception:
                    pass
        
        if not all_results:
            pytest.skip("No database operations completed")
        
        # Analyze database performance
        successful_ops = [r for r in all_results if r["success"]]
        success_rate = len(successful_ops) / len(all_results)
        
        if successful_ops:
            avg_time = statistics.mean([r["time"] for r in successful_ops])
            
            print(f"Database load test: {success_rate:.1%} success, avg {avg_time:.3f}s")
            
            # Database performance expectations
            assert success_rate >= 0.8, f"DB success rate {success_rate:.1%} < 80%"
            assert avg_time < 2.0, f"DB avg time {avg_time:.3f}s > 2s"


class TestC2ScalabilityLimits:
    """Test scalability limits and breaking points"""

    def test_max_concurrent_users(self):
        """Test maximum concurrent user simulation"""
        url = "http://localhost:1881/c2-dashboard"
        max_workers = 20
        test_duration = 15  # seconds
        
        stop_event = threading.Event()
        results = []
        results_lock = threading.Lock()
        
        def simulate_user():
            user_results = []
            while not stop_event.is_set():
                start_time = time.time()
                try:
                    response = requests.get(url, timeout=20)
                    response_time = time.time() - start_time
                    user_results.append({
                        "success": response.status_code == 200,
                        "time": response_time,
                        "status": response.status_code
                    })
                except Exception:
                    user_results.append({
                        "success": False,
                        "time": 20.0,
                        "status": 0
                    })
                
                # Simulate user think time
                time.sleep(1.0)
            
            with results_lock:
                results.extend(user_results)
        
        # Start simulated users
        threads = []
        for i in range(max_workers):
            thread = threading.Thread(target=simulate_user)
            thread.start()
            threads.append(thread)
        
        # Run test
        time.sleep(test_duration)
        stop_event.set()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=5)
        
        if not results:
            pytest.skip("No user simulation results")
        
        # Analyze scalability
        successful_requests = [r for r in results if r["success"]]
        success_rate = len(successful_requests) / len(results)
        
        if successful_requests:
            avg_response_time = statistics.mean([r["time"] for r in successful_requests])
            throughput = len(results) / test_duration
            
            print(f"Scalability test: {max_workers} users, {throughput:.1f} req/s, "
                  f"{success_rate:.1%} success, avg {avg_response_time:.2f}s")
            
            # Scalability expectations
            assert success_rate >= 0.6, f"Success rate {success_rate:.1%} < 60% with {max_workers} users"

    def test_large_payload_handling(self):
        """Test handling of increasingly large payloads"""
        url = "http://localhost:1881/send-ntfy"
        payload_sizes = [1024, 5120, 10240, 51200]  # 1KB, 5KB, 10KB, 50KB
        
        results = {}
        
        for size in payload_sizes:
            large_message = "A" * size
            payload = {
                "message": large_message,
                "priority": "3",
                "topic": "horse-racing-ai"
            }
            
            start_time = time.time()
            try:
                response = requests.post(url, json=payload, timeout=30)
                response_time = time.time() - start_time
                
                results[size] = {
                    "success": response.status_code in [200, 201],
                    "status": response.status_code,
                    "time": response_time
                }
                
            except Exception as e:
                results[size] = {
                    "success": False,
                    "status": 0,
                    "time": 30.0,
                    "error": str(e)
                }
        
        # Analyze payload handling
        for size, result in results.items():
            size_kb = size / 1024
            print(f"Payload {size_kb:.0f}KB: "
                  f"{'✓' if result['success'] else '✗'} "
                  f"({result['status']}) {result['time']:.2f}s")
        
        # Should handle reasonable payload sizes
        if 1024 in results:
            assert results[1024]["success"], "Failed to handle 1KB payload"

    def test_memory_usage_under_load(self):
        """Test memory usage during sustained load"""
        url = "http://localhost:1881/containers/status"
        
        # Get baseline memory
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate sustained load
        def generate_load():
            for i in range(50):
                try:
                    requests.get(url, timeout=5)
                except Exception:
                    pass
                time.sleep(0.1)
        
        # Monitor memory during load
        memory_samples = []
        load_thread = threading.Thread(target=generate_load)
        load_thread.start()
        
        for i in range(20):
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_samples.append(current_memory)
            time.sleep(0.5)
        
        load_thread.join()
        
        # Analyze memory usage
        if memory_samples:
            max_memory = max(memory_samples)
            avg_memory = statistics.mean(memory_samples)
            memory_increase = max_memory - baseline_memory
            
            print(f"Memory under load: Baseline {baseline_memory:.1f}MB, "
                  f"Max {max_memory:.1f}MB, Avg {avg_memory:.1f}MB, "
                  f"Increase {memory_increase:.1f}MB")
            
            # Memory usage should be stable
            assert memory_increase < 200, f"Memory increase {memory_increase:.1f}MB too high"


class TestC2PerformanceRegression:
    """Performance regression testing"""

    def test_dashboard_performance_regression(self):
        """Test for performance regression in dashboard loading"""
        url = "http://localhost:1881/c2-dashboard"
        expected_load_time = 5.0  # seconds
        
        load_times = []
        for i in range(3):
            start_time = time.time()
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    load_time = time.time() - start_time
                    load_times.append(load_time)
            except Exception:
                pytest.skip("Dashboard not accessible for regression test")
        
        if load_times:
            avg_load_time = statistics.mean(load_times)
            
            # Compare against expected performance
            performance_ratio = avg_load_time / expected_load_time
            
            print(f"Performance regression test: {avg_load_time:.2f}s "
                  f"(target: {expected_load_time:.2f}s, ratio: {performance_ratio:.2f})")
            
            # Allow some performance degradation but flag significant regression
            assert performance_ratio < 2.0, f"Performance regression: {performance_ratio:.2f}x slower than expected"

    def test_api_throughput_regression(self):
        """Test for API throughput regression"""
        endpoint = "http://localhost:1881/containers/status"
        expected_min_throughput = 2.0  # requests per second
        test_duration = 10  # seconds
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < test_duration:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    request_count += 1
            except Exception:
                pass
            time.sleep(0.1)  # Minimum delay
        
        actual_duration = time.time() - start_time
        throughput = request_count / actual_duration
        
        print(f"Throughput regression test: {throughput:.2f} req/s "
              f"(target: {expected_min_throughput:.2f} req/s)")
        
        # Check for throughput regression
        if request_count > 0:
            assert throughput >= expected_min_throughput * 0.7, f"Throughput regression: {throughput:.2f} req/s too low"


# Performance test utilities
@pytest.fixture
def performance_monitor():
    """Fixture for monitoring system performance during tests"""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.start_memory = None
            self.measurements = []
        
        def start(self):
            self.start_time = time.time()
            process = psutil.Process()
            self.start_memory = process.memory_info().rss / 1024 / 1024
        
        def measure(self, label: str):
            if self.start_time:
                elapsed = time.time() - self.start_time
                process = psutil.Process()
                current_memory = process.memory_info().rss / 1024 / 1024
                
                self.measurements.append({
                    "label": label,
                    "elapsed": elapsed,
                    "memory_mb": current_memory,
                    "memory_delta": current_memory - self.start_memory
                })
        
        def summary(self):
            return {
                "measurements": self.measurements,
                "total_time": self.measurements[-1]["elapsed"] if self.measurements else 0,
                "max_memory": max([m["memory_mb"] for m in self.measurements]) if self.measurements else 0
            }
    
    return PerformanceMonitor()


if __name__ == "__main__":
    # Run performance tests with specific markers
    pytest.main([__file__, "-v", "--tb=short", "-s", "-x"])
