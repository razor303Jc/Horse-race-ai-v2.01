#!/usr/bin/env python3
"""
Quick API Validation Test
=========================

Fast validation of all 5 automation API endpoints
"""

import requests
import time
from datetime import datetime

NODE_RED_URL = "http://localhost:1880"


def quick_api_test():
    """Quick test of all API endpoints"""

    print("⚡ QUICK API VALIDATION TEST")
    print("=" * 40)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 {NODE_RED_URL}/api/pipeline/")
    print("")

    endpoints = [
        ("trigger", "Manual Pipeline"),
        ("data_relationships", "Data Relationships"),
        ("performance_tracker", "Performance Tracker"),
        ("ml_training", "ML Training"),
        ("ai_selections", "AI Selections"),
    ]

    results = []

    for endpoint, description in endpoints:
        url = f"{NODE_RED_URL}/api/pipeline/{endpoint}"

        try:
            print(f"🧪 Testing {description}...")
            start_time = time.time()
            response = requests.post(url, timeout=10)
            end_time = time.time()

            response_time = end_time - start_time

            if response.status_code == 200:
                print(f"✅ {endpoint}: OK ({response_time:.3f}s)")
                try:
                    json_response = response.json()
                    if json_response.get("success"):
                        print(f"   Message: {json_response.get('message', 'Success')}")
                except:
                    print(f"   Response: {response.text[:100]}...")
                results.append((endpoint, True, response_time))
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
                results.append((endpoint, False, response_time))

        except requests.exceptions.Timeout:
            print(f"⏰ {endpoint}: Timeout (>10s)")
            results.append((endpoint, False, 0))
        except Exception as e:
            print(f"❌ {endpoint}: Error - {str(e)[:50]}...")
            results.append((endpoint, False, 0))

        print("")

    # Summary
    working = sum(1 for _, success, _ in results if success)
    total = len(results)

    print("📊 SUMMARY:")
    print(f"• Working Endpoints: {working}/{total}")
    print(f"• Success Rate: {working/total*100:.1f}%")

    if working == total:
        print("• Status: ✅ ALL ENDPOINTS OPERATIONAL")
    elif working > 0:
        print("• Status: ⚠️  PARTIAL FUNCTIONALITY")
    else:
        print("• Status: ❌ ALL ENDPOINTS FAILED")

    # Response time analysis
    response_times = [rt for _, success, rt in results if success and rt > 0]
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        print(f"• Average Response Time: {avg_time:.3f}s")

        if avg_time < 1.0:
            print("• Performance: 🚀 EXCELLENT")
        elif avg_time < 3.0:
            print("• Performance: ✅ GOOD")
        else:
            print("• Performance: ⚠️  NEEDS OPTIMIZATION")

    return working == total


if __name__ == "__main__":
    success = quick_api_test()
    exit(0 if success else 1)
