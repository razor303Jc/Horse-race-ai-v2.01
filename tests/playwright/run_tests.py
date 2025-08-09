#!/usr/bin/env python3
"""
Test runner for Horse Racing AI v2.0 Playwright tests
Runs web application tests against the containerized system.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path


def check_app_health(base_url: str = "http://localhost:5002", max_attempts: int = 10):
    """Check if the web application is healthy and ready for testing"""
    print(f"🔍 Checking application health at {base_url}...")

    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/api/system_status", timeout=5)
            if response.status_code == 200:
                print("✅ Application is healthy and ready for testing!")
                return True
        except requests.RequestException as e:
            print(f"⏳ Attempt {attempt + 1}/{max_attempts}: {e}")
            time.sleep(2)

    print(f"❌ Application not ready after {max_attempts} attempts")
    return False


def run_playwright_tests():
    """Run the Playwright test suite"""
    print("🎭 Starting Playwright tests...")

    # Ensure we're in the right directory
    project_root = Path(__file__).parent.parent.parent

    # Run pytest with Playwright
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/playwright/",
        "-v",
        "--tb=short",
        "--capture=no",
        f"--rootdir={project_root}",
    ]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=project_root)

    return result.returncode == 0


def main():
    """Main test runner function"""
    print("🏇 Horse Racing AI v2.0 - Playwright Test Runner")
    print("=" * 50)

    # Check if application is ready
    if not check_app_health():
        print("❌ Application is not ready. Please start the Docker containers first:")
        print("   docker compose up -d")
        sys.exit(1)

    # Run tests
    success = run_playwright_tests()

    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
