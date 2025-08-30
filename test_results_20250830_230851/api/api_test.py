#!/usr/bin/env python3
import requests
import time
import json
import sys
import concurrent.futures
from datetime import datetime

def test_api_endpoint(url, endpoint, expected_status=200):
    """Test a single API endpoint"""
    start_time = time.perf_counter()
    try:
        response = requests.get(f"{url}{endpoint}", timeout=10)
        response_time = (time.perf_counter() - start_time) * 1000
        
        return {
            "endpoint": endpoint,
            "status_code": response.status_code,
            "response_time_ms": round(response_time, 2),
            "content_length": len(response.content),
            "success": response.status_code == expected_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        response_time = (time.perf_counter() - start_time) * 1000
        return {
            "endpoint": endpoint,
            "error": str(e),
            "response_time_ms": round(response_time, 2),
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

def load_test_endpoint(url, endpoint, concurrent_users=10, requests_per_user=5):
    """Load test a single endpoint with concurrent users"""
    
    def user_session():
        results = []
        for _ in range(requests_per_user):
            result = test_api_endpoint(url, endpoint)
            results.append(result)
            time.sleep(0.1)  # Small delay between requests
        return results
    
    all_results = []
    start_time = time.perf_counter()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(user_session) for _ in range(concurrent_users)]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                user_results = future.result()
                all_results.extend(user_results)
            except Exception as e:
                print(f"User session failed: {e}")
    
    total_time = time.perf_counter() - start_time
    
    # Calculate statistics
    successful_requests = [r for r in all_results if r.get('success', False)]
    failed_requests = [r for r in all_results if not r.get('success', False)]
    
    if successful_requests:
        response_times = [r['response_time_ms'] for r in successful_requests]
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
    else:
        avg_response_time = min_response_time = max_response_time = p95_response_time = 0
    
    return {
        "endpoint": endpoint,
        "concurrent_users": concurrent_users,
        "requests_per_user": requests_per_user,
        "total_requests": len(all_results),
        "successful_requests": len(successful_requests),
        "failed_requests": len(failed_requests),
        "success_rate": round((len(successful_requests) / len(all_results)) * 100, 2) if all_results else 0,
        "total_time_seconds": round(total_time, 2),
        "requests_per_second": round(len(all_results) / total_time, 2) if total_time > 0 else 0,
        "avg_response_time_ms": round(avg_response_time, 2),
        "min_response_time_ms": round(min_response_time, 2),
        "max_response_time_ms": round(max_response_time, 2),
        "p95_response_time_ms": round(p95_response_time, 2),
        "timestamp": datetime.now().isoformat()
    }

def test_api_performance(base_url, results_file, concurrent_users=10):
    """Run comprehensive API performance tests"""
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "base_url": base_url,
        "concurrent_users": concurrent_users,
        "tests": {}
    }
    
    # Define test endpoints
    endpoints = [
        "/health",
        "/api/races",
        "/api/horses",
        "/api/jockeys",
        "/api/trainers",
        "/api/predictions/latest"
    ]
    
    print(f"Testing API performance with {concurrent_users} concurrent users...")
    
    for endpoint in endpoints:
        print(f"Testing endpoint: {endpoint}")
        
        # Single request test
        single_result = test_api_endpoint(base_url, endpoint)
        
        # Load test
        load_result = load_test_endpoint(base_url, endpoint, concurrent_users, 3)
        
        results["tests"][endpoint] = {
            "single_request": single_result,
            "load_test": load_result
        }
    
    # Calculate overall statistics
    all_load_tests = [test["load_test"] for test in results["tests"].values()]
    
    if all_load_tests:
        overall_success_rate = sum(test["success_rate"] for test in all_load_tests) / len(all_load_tests)
        overall_avg_response = sum(test["avg_response_time_ms"] for test in all_load_tests) / len(all_load_tests)
        overall_requests_per_sec = sum(test["requests_per_second"] for test in all_load_tests)
        
        results["summary"] = {
            "overall_success_rate": round(overall_success_rate, 2),
            "overall_avg_response_ms": round(overall_avg_response, 2),
            "total_requests_per_second": round(overall_requests_per_sec, 2),
            "endpoints_tested": len(endpoints),
            "status": "pass" if overall_success_rate >= 95 and overall_avg_response < 500 else "warning"
        }
    
    # Save results
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    results_file = sys.argv[2] if len(sys.argv) > 2 else "api_performance.json"
    concurrent_users = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    results = test_api_performance(base_url, results_file, concurrent_users)
    
    summary = results.get('summary', {})
    print(f"API Performance Test Results:")
    print(f"Success Rate: {summary.get('overall_success_rate', 0)}%")
    print(f"Average Response Time: {summary.get('overall_avg_response_ms', 0)}ms")
    print(f"Requests/Second: {summary.get('total_requests_per_second', 0)}")
    
    if summary.get('status') == 'pass':
        sys.exit(0)
    else:
        sys.exit(1)
