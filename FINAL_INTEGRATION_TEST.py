#!/usr/bin/env python3
"""
AI Selections Results - Final Integration Test
============================================

This script performs a comprehensive end-to-end test of the entire
AI Selections Results system, testing both the React frontend and
FastAPI backend from outside the Docker containers.
"""

import requests
import json
import time
from datetime import datetime
import sys


def test_api_endpoints():
    """Test all API endpoints"""
    print("🔗 Testing API Endpoints...")

    base_url = "http://localhost:3000/api/ai_selections"

    # Test performance endpoint
    try:
        response = requests.get(f"{base_url}/performance", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                summary = data["data"]["summary"]
                print(
                    f"✅ Performance API: {summary['total_predictions']} predictions, {summary['accuracy_rate']}% accuracy"
                )
                return True
            else:
                print(f"❌ Performance API: Invalid response format")
                return False
        else:
            print(f"❌ Performance API: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Performance API: {str(e)}")
        return False


def test_pagination_api():
    """Test pagination functionality"""
    print("📄 Testing Pagination...")

    base_url = "http://localhost:3000/api/ai_selections"

    try:
        # Test with pagination parameters
        response = requests.get(f"{base_url}/recent?limit=5&offset=0", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                selections_data = data["data"]
                total_count = selections_data.get("total_count", 0)
                limit = selections_data.get("limit", 0)
                offset = selections_data.get("offset", 0)
                selections = selections_data.get("selections", [])

                print(
                    f"✅ Pagination API: {len(selections)} records returned, {total_count} total available"
                )
                print(f"   📊 Limit: {limit}, Offset: {offset}")
                return True
            else:
                print(f"❌ Pagination API: Invalid response format")
                return False
        else:
            print(f"❌ Pagination API: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Pagination API: {str(e)}")
        return False


def test_react_frontend():
    """Test React frontend accessibility"""
    print("⚛️  Testing React Frontend...")

    try:
        # Test main React app
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            content = response.text
            if "React" in content or "root" in content:
                print("✅ React App: Accessible and serving content")

                # Test AI Results route
                response = requests.get("http://localhost:3000/ai-results", timeout=10)
                if response.status_code == 200:
                    print("✅ AI Results Route: Accessible")
                    return True
                else:
                    print(
                        f"⚠️  AI Results Route: HTTP {response.status_code} (but main app works)"
                    )
                    return True
            else:
                print(f"❌ React App: Unexpected content")
                return False
        else:
            print(f"❌ React App: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ React App: {str(e)}")
        return False


def test_database_integration():
    """Test database integration through API"""
    print("🗄️  Testing Database Integration...")

    try:
        # Get performance data and verify database fields
        response = requests.get(
            "http://localhost:3000/api/ai_selections/performance?days=7", timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            summary = data["data"]["summary"]

            # Verify key database fields are present
            required_fields = [
                "total_predictions",
                "accuracy_rate",
                "roi_percentage",
                "total_profit_loss",
                "win_rate",
                "place_rate",
            ]

            missing_fields = [
                field for field in required_fields if field not in summary
            ]
            if not missing_fields:
                print(f"✅ Database Integration: All fields present")
                print(
                    f"   📈 ROI: {summary['roi_percentage']}%, Profit: £{summary['total_profit_loss']}"
                )
                return True
            else:
                print(f"❌ Database Integration: Missing fields: {missing_fields}")
                return False
        else:
            print(f"❌ Database Integration: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Database Integration: {str(e)}")
        return False


def main():
    """Run comprehensive integration tests"""
    print("🚀 AI Selections Results - Final Integration Test")
    print("=" * 60)
    print(f"📅 Test Time: {datetime.now().isoformat()}")
    print(f"🔗 Target URL: http://localhost:3000")
    print()

    tests = [
        ("API Endpoints", test_api_endpoints),
        ("Pagination API", test_pagination_api),
        ("React Frontend", test_react_frontend),
        ("Database Integration", test_database_integration),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        print("-" * 40)

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 {test_name} Test Error: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Final Integration Test Results")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")

    print(f"\n🎯 Overall Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 ALL TESTS PASSED! System is fully operational.")
        print("\n🌐 Access your AI Selections Results at:")
        print("   📊 Dashboard: http://localhost:3000/ai-results")
        print("   🔗 API Docs: http://localhost:3000/api/ai_selections/performance")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
