#!/usr/bin/env python3
"""
Docker Auto Downloader Validation Test
=====================================

Comprehensive test to validate Docker setup for the auto downloader.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from pathlib import Path


def test_docker_configuration():
    """Test Docker-specific configuration"""
    print("🐳 Testing Docker Configuration...")

    # Set Docker environment
    os.environ["DOCKER_CONTAINER"] = "true"
    os.environ["HEADLESS"] = "true"

    try:
        from src.automation.docker_config import (
            DockerDownloadConfig,
            get_docker_browser_args,
            validate_docker_setup,
        )

        print("✅ Docker config imports successful")

        # Test configuration
        config = DockerDownloadConfig()
        print(f"✅ Docker config created (headless: {config.headless})")

        # Test browser args
        args = get_docker_browser_args()
        print(f"✅ Browser args generated ({len(args)} arguments)")

        return True
    except Exception as e:
        print(f"❌ Docker config test failed: {e}")
        return False


def test_auto_downloader_import():
    """Test auto downloader import and initialization"""
    print("\n🤖 Testing Auto Downloader...")

    try:
        from src.automation.respectful_auto_downloader import RespectfulAutoDownloader

        print("✅ Auto downloader imports successful")

        # Test initialization
        downloader = RespectfulAutoDownloader()
        print("✅ Auto downloader initializes successfully")
        print(f"📊 Configuration: headless={downloader.config.headless}")

        return True
    except Exception as e:
        print(f"❌ Auto downloader test failed: {e}")
        return False


def test_woocommerce_integration():
    """Test WooCommerce downloader integration"""
    print("\n🛒 Testing WooCommerce Integration...")

    try:
        from demos.woocommerce_downloader import WooCommerceDownloader

        print("✅ WooCommerce downloader imports successful")

        # Test initialization
        woo_downloader = WooCommerceDownloader()
        print("✅ WooCommerce downloader initializes successfully")

        return True
    except Exception as e:
        print(f"❌ WooCommerce integration test failed: {e}")
        return False


def test_environment_variables():
    """Test required environment variables"""
    print("\n🌍 Testing Environment Variables...")

    required_vars = [
        "HORSERACE_DB_USERNAME",
        "HORSERACE_DB_PASSWORD",
        "HORSERACE_DB_RESULTS_URL",
        "HORSERACE_DB_CARDS_URL",
    ]

    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: Configured")
        else:
            print(f"❌ {var}: Missing")
            missing_vars.append(var)

    return len(missing_vars) == 0


def test_playwright_availability():
    """Test Playwright availability"""
    print("\n🎭 Testing Playwright...")

    try:
        from playwright.async_api import async_playwright

        print("✅ Playwright imports successful")
        return True
    except Exception as e:
        print(f"❌ Playwright test failed: {e}")
        return False


def test_directory_structure():
    """Test directory structure for Docker"""
    print("\n📁 Testing Directory Structure...")

    # Check current directory structure
    current_dir = Path.cwd()
    required_files = [
        "src/automation/respectful_auto_downloader.py",
        "src/automation/docker_config.py",
        "demos/woocommerce_downloader.py",
        "docker-compose.auto-downloader.yml",
        "run_docker_auto_downloader.py",
        "manage_docker_auto_downloader.sh",
    ]

    missing_files = []
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}: Found")
        else:
            print(f"❌ {file_path}: Missing")
            missing_files.append(file_path)

    return len(missing_files) == 0


def main():
    """Run all validation tests"""
    print("🔍 Docker Auto Downloader Validation Test")
    print("=" * 50)

    tests = [
        ("Docker Configuration", test_docker_configuration),
        ("Auto Downloader", test_auto_downloader_import),
        ("WooCommerce Integration", test_woocommerce_integration),
        ("Environment Variables", test_environment_variables),
        ("Playwright", test_playwright_availability),
        ("Directory Structure", test_directory_structure),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)

    passed = sum(results.values())
    total = len(results)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Docker auto downloader is ready!")
        return True
    else:
        print("⚠️  Some tests failed. Check configuration before running in Docker.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
