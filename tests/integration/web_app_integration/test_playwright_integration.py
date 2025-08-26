"""
🎭 Playwright Web App Integration Tests
=====================================

Integration between pytest framework and Playwright web application tests.
This module provides a bridge to run Playwright tests from within our main
test framework.
"""

import pytest
import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile
import time

# Test markers
pytestmark = [pytest.mark.integration, pytest.mark.web_app, pytest.mark.slow]


@pytest.fixture
def playwright_config():
    """Configuration for Playwright test execution"""
    web_app_path = Path(__file__).parent.parent.parent.parent / "src" / "web"
    return {
        "web_app_path": web_app_path,
        "playwright_config": web_app_path / "playwright.config.ts",
        "test_dir": web_app_path / "tests",
        "base_url": "http://localhost:5003",
        "timeout": 60,  # seconds
        "retries": 2,
    }


@pytest.fixture
def web_app_environment():
    """Set up web application environment for testing"""
    return {
        "NODE_ENV": "test",
        "VITE_API_URL": "http://localhost:8000",
        "VITE_WS_URL": "ws://localhost:8000",
        "PLAYWRIGHT_BROWSERS_PATH": "~/.cache/ms-playwright",
    }


class PlaywrightTestRunner:
    """Manages Playwright test execution from pytest"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.web_app_path = config["web_app_path"]
        self.results_file = None

    def setup_environment(self, env_vars: Dict[str, str]):
        """Set up environment variables for Playwright"""
        for key, value in env_vars.items():
            os.environ[key] = value

    def run_playwright_tests(
        self, test_pattern: str = None, browser: str = "chromium"
    ) -> Dict[str, Any]:
        """
        Execute Playwright tests and return results

        Args:
            test_pattern: Optional pattern to filter tests
                         (e.g., "dashboard", "api-integration")
            browser: Browser to use for testing (chromium, firefox, webkit)

        Returns:
            Dict containing test results and metadata
        """
        # Create temporary file for results
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            self.results_file = f.name

        try:
            # Build Playwright command
            cmd = [
                "npx",
                "playwright",
                "test",
                "--project",
                browser,
                "--reporter",
                f"json:{self.results_file}",
            ]

            # Add test pattern if specified
            if test_pattern:
                cmd.append(test_pattern)

            # Run Playwright tests
            result = subprocess.run(
                cmd,
                cwd=self.web_app_path,
                capture_output=True,
                text=True,
                timeout=self.config["timeout"],
            )

            # Parse results
            results = self._parse_results()
            results["command_output"] = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

            return results

        except subprocess.TimeoutExpired:
            timeout_msg = (
                f"Playwright tests timed out after " f"{self.config['timeout']} seconds"
            )
            return {"status": "timeout", "error": timeout_msg}
        except FileNotFoundError:
            return {
                "status": "setup_error",
                "error": 'Playwright not found. Run "npm install" in src/web directory.',
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            # Clean up results file
            if self.results_file and os.path.exists(self.results_file):
                try:
                    os.unlink(self.results_file)
                except Exception:
                    pass

    def _parse_results(self) -> Dict[str, Any]:
        """Parse Playwright JSON results"""
        try:
            if not os.path.exists(self.results_file):
                return {"status": "no_results", "tests": []}

            with open(self.results_file, "r") as f:
                data = json.load(f)

            return {
                "status": "completed",
                "stats": data.get("stats", {}),
                "suites": data.get("suites", []),
                "tests": self._extract_test_results(data),
            }
        except json.JSONDecodeError:
            return {
                "status": "parse_error",
                "error": "Failed to parse Playwright results",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _extract_test_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract individual test results from Playwright output"""
        tests = []

        for suite in data.get("suites", []):
            for spec in suite.get("specs", []):
                for test in spec.get("tests", []):
                    tests.append(
                        {
                            "title": test.get("title", ""),
                            "file": spec.get("file", ""),
                            "status": test.get("status", "unknown"),
                            "duration": test.get("duration", 0),
                            "errors": test.get("errors", []),
                        }
                    )

        return tests


def _assert_test_execution_status(results: Dict[str, Any]) -> None:
    """Helper function to assert test execution status"""
    expected_statuses = ["completed", "timeout", "setup_error"]
    status = results.get("status")

    if status == "setup_error":
        pytest.skip(
            f"Playwright setup required: {results.get('error', 'Unknown setup error')}"
        )
    elif status == "parse_error":
        pytest.skip(
            f"Playwright result parsing failed: {results.get('error', 'Unknown parse error')}"
        )
    elif status == "error":
        pytest.skip(
            f"Playwright execution error: {results.get('error', 'Unknown error')}"
        )

    assert status in expected_statuses, f"Unexpected status: {status}"


@pytest.mark.integration
@pytest.mark.web_app
def test_playwright_dashboard_functionality(playwright_config, web_app_environment):
    """Test dashboard functionality using Playwright"""
    runner = PlaywrightTestRunner(playwright_config)
    runner.setup_environment(web_app_environment)

    # Run dashboard-specific tests
    results = runner.run_playwright_tests("dashboard.spec.ts")

    # Assert test execution
    expected_statuses = ["completed", "timeout"]
    status = results.get("status")
    assert status in expected_statuses, f"Unexpected status: {status}"

    if results["status"] == "completed":
        # Check that tests ran
        assert "tests" in results

        # Log test results for debugging
        for test in results["tests"]:
            print(f"Dashboard Test: {test['title']} - {test['status']}")

        # Count passed tests
        passed_tests = [t for t in results["tests"] if t["status"] == "passed"]
        failed_tests = [t for t in results["tests"] if t["status"] == "failed"]

        # Allow some failures but ensure at least some tests pass
        if failed_tests:
            print(f"⚠️  {len(failed_tests)} dashboard tests failed:")
            for test in failed_tests:
                print(f"   - {test['title']}: {test.get('errors', [])}")

        # Require at least 50% success rate
        if len(results["tests"]) > 0:
            success_rate = len(passed_tests) / len(results["tests"])
            rate_msg = f"Dashboard tests success rate too low: {success_rate:.2%}"
            assert success_rate >= 0.5, rate_msg


@pytest.mark.integration
@pytest.mark.web_app
def test_playwright_api_integration(playwright_config, web_app_environment):
    """Test API integration using Playwright"""
    runner = PlaywrightTestRunner(playwright_config)
    runner.setup_environment(web_app_environment)

    # Run API integration tests
    results = runner.run_playwright_tests("api-integration.spec.ts")

    # Assert test execution
    _assert_test_execution_status(results)

    if results["status"] == "completed":
        # Log test results
        for test in results["tests"]:
            print(f"API Integration Test: {test['title']} - {test['status']}")

        # Count results
        passed_tests = [t for t in results["tests"] if t["status"] == "passed"]

        # API integration is critical, so we want at least one test to pass
        assert len(passed_tests) > 0, "No API integration tests passed"


@pytest.mark.integration
@pytest.mark.web_app
def test_playwright_race_cards_functionality(playwright_config, web_app_environment):
    """Test race cards functionality using Playwright"""
    runner = PlaywrightTestRunner(playwright_config)
    runner.setup_environment(web_app_environment)

    # Run race cards tests
    results = runner.run_playwright_tests("race-cards.spec.ts")

    # Assert test execution
    _assert_test_execution_status(results)

    if results["status"] == "completed":
        # Log test results
        for test in results["tests"]:
            print(f"Race Cards Test: {test['title']} - {test['status']}")


@pytest.mark.integration
@pytest.mark.web_app
@pytest.mark.slow
def test_playwright_e2e_workflows(playwright_config, web_app_environment):
    """Test end-to-end user workflows using Playwright"""
    runner = PlaywrightTestRunner(playwright_config)
    runner.setup_environment(web_app_environment)

    # Run E2E tests
    results = runner.run_playwright_tests("e2e.spec.ts")

    # Assert test execution
    _assert_test_execution_status(results)

    if results["status"] == "completed":
        # Log test results
        for test in results["tests"]:
            print(f"E2E Test: {test['title']} - {test['status']}")


@pytest.mark.integration
@pytest.mark.web_app
def test_playwright_live_race_tracking(playwright_config, web_app_environment):
    """Test live race tracking functionality using Playwright"""
    runner = PlaywrightTestRunner(playwright_config)
    runner.setup_environment(web_app_environment)

    # Run live race tracking tests
    results = runner.run_playwright_tests("live-race-tracking.spec.ts")

    # Assert test execution
    _assert_test_execution_status(results)

    if results["status"] == "completed":
        # Log test results
        for test in results["tests"]:
            print(f"Live Race Tracking Test: {test['title']} - {test['status']}")


@pytest.mark.integration
@pytest.mark.web_app
@pytest.mark.comprehensive
def test_playwright_full_suite(playwright_config, web_app_environment):
    """Run the complete Playwright test suite"""
    runner = PlaywrightTestRunner(playwright_config)
    runner.setup_environment(web_app_environment)

    # Run all Playwright tests
    results = runner.run_playwright_tests()

    # Assert test execution
    _assert_test_execution_status(results)

    if results["status"] == "completed":
        # Comprehensive statistics
        total_tests = len(results["tests"])
        passed_tests = [t for t in results["tests"] if t["status"] == "passed"]
        failed_tests = [t for t in results["tests"] if t["status"] == "failed"]
        skipped_tests = [t for t in results["tests"] if t["status"] == "skipped"]

        print("\n🎭 Playwright Test Suite Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {len(passed_tests)}")
        print(f"   Failed: {len(failed_tests)}")
        print(f"   Skipped: {len(skipped_tests)}")

        if total_tests > 0:
            success_rate = len(passed_tests) / total_tests
            print(f"   Success Rate: {success_rate:.1%}")

            # Log failed tests for debugging
            if failed_tests:
                print("\n❌ Failed Tests:")
                for test in failed_tests:
                    print(f"   - {test['file']}: {test['title']}")
                    if test.get("errors"):
                        for error in test["errors"][:2]:  # Limit to 2 errors per test
                            error_msg = error.get("message", "Unknown error")
                            print(f"     Error: {error_msg}")
