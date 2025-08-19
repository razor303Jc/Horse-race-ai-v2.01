#!/usr/bin/env python3
"""
Quick test to verify the web application and API are ready for comprehensive testing
"""

import requests
import time
import subprocess
import sys
from pathlib import Path


def check_api_health():
    """Check if the API server is running and healthy"""
    try:
        response = requests.get("http://localhost:8000/api/system_status", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def check_web_app():
    """Check if the web application is accessible"""
    try:
        response = requests.get("http://localhost:5002", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def run_typescript_check():
    """Run TypeScript type checking"""
    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"], cwd="src/web", capture_output=True, text=True
        )
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)


def main():
    """Main health check function"""
    print("🏇 Horse Racing AI v2.03 - Pre-Test Health Check")
    print("=" * 50)

    # Change to project root
    project_root = Path("/home/jc/Documents/Horse-race-ai-v2.03")
    if not project_root.exists():
        print(f"❌ Project root not found: {project_root}")
        return False

    # Check TypeScript compilation
    print("🔍 Checking TypeScript compilation...")
    ts_ok, ts_error = run_typescript_check()
    if ts_ok:
        print("✅ TypeScript compilation successful")
    else:
        print("⚠️  TypeScript compilation issues:")
        print(ts_error)

    # Check API health
    print("\n🔍 Checking API server health...")
    if check_api_health():
        print("✅ API server is running and healthy")
    else:
        print("⚠️  API server not responding - some tests may be skipped")

    # Check web application
    print("\n🔍 Checking web application...")
    if check_web_app():
        print("✅ Web application is accessible")
    else:
        print("⚠️  Web application not responding - Playwright tests may fail")

    # Check test files exist
    print("\n🔍 Checking test files...")
    test_files = [
        "tests/playwright/test_csp_configuration.py",
        "tests/playwright/test_live_race_tracking.py",
        "tests/unit/test_csp_live_race_units.py",
    ]

    all_tests_exist = True
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"✅ {test_file}")
        else:
            print(f"❌ {test_file} - missing")
            all_tests_exist = False

    # Summary
    print(f"\n📊 Health Check Summary")
    print("-" * 30)

    ready_for_testing = ts_ok and all_tests_exist

    if ready_for_testing:
        print("🎉 System is ready for comprehensive testing!")
        print("\nNext steps:")
        print("1. Ensure web application is running: http://localhost:5002")
        print("2. Run unit tests: python tests/unit/test_csp_live_race_units.py")
        print("3. Run Playwright tests: python tests/run_csp_live_race_tests.py")
        return True
    else:
        print("⚠️  Some issues detected - review and fix before testing")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
