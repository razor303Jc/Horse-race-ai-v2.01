#!/usr/bin/env python3
"""
🔧 Horse Racing AI - Project Cleanup Validator
Validates system functionality after file cleanup operations

This tool:
1. Runs comprehensive system health checks
2. Validates Docker services and dependencies
3. Tests API endpoints and pipeline functionality
4. Ensures no critical functionality is broken
5. Provides rollback recommendations if issues detected

Author: AI Assistant
Date: August 26, 2025
Version: 1.0.0
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CleanupValidator:
    """Validates system functionality after cleanup operations"""

    def __init__(self, project_root: Optional[str] = None):
        default_root = "/home/jc/Documents/Horse-race-ai-v2.04"
        self.project_root = Path(project_root or default_root)

        # Test results
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": [],
            "passed_tests": [],
            "failed_tests": [],
            "warnings": [],
            "critical_failures": [],
            "overall_status": "unknown",
        }

        # Output paths
        self.output_dir = self.project_root / "data" / "validation"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Known critical components
        self.critical_files = [
            "src/web/api_server_enhanced.py",
            "tools/pipeline_coordinator.py",
            "docker-compose.clean.yml",
            ".env",
        ]

        self.critical_services = ["postgres", "redis", "web_app", "data_pipeline"]

    def log_test_result(
        self, test_name: str, status: str, details: str = "", is_critical: bool = False
    ):
        """Log a test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "critical": is_critical,
        }

        self.test_results["tests_run"].append(result)

        if status == "PASS":
            self.test_results["passed_tests"].append(test_name)
            logger.info(f"✅ {test_name}: PASSED")
        elif status == "FAIL":
            self.test_results["failed_tests"].append(test_name)
            if is_critical:
                self.test_results["critical_failures"].append(test_name)
            logger.error(f"❌ {test_name}: FAILED - {details}")
        elif status == "WARN":
            self.test_results["warnings"].append(test_name)
            logger.warning(f"⚠️ {test_name}: WARNING - {details}")

    def test_critical_files_exist(self) -> bool:
        """Test that critical files still exist"""
        logger.info("🧪 Testing critical file existence...")

        all_exist = True
        for file_path in self.critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.log_test_result(f"Critical file exists: {file_path}", "PASS")
            else:
                self.log_test_result(
                    f"Critical file missing: {file_path}",
                    "FAIL",
                    f"File not found: {full_path}",
                    is_critical=True,
                )
                all_exist = False

        return all_exist

    def test_docker_services(self) -> bool:
        """Test Docker services are running"""
        logger.info("🐳 Testing Docker services...")

        try:
            # Check if docker is available
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, timeout=10
            )
            if result.returncode != 0:
                self.log_test_result(
                    "Docker availability",
                    "FAIL",
                    "Docker not available",
                    is_critical=True,
                )
                return False

            self.log_test_result("Docker availability", "PASS")

            # Check running containers
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode != 0:
                self.log_test_result(
                    "Docker ps command", "FAIL", result.stderr, is_critical=True
                )
                return False

            running_containers = result.stdout.strip().split("\n")
            running_containers = [c for c in running_containers if c]

            services_status = {}
            for service in self.critical_services:
                # Check if any container name contains the service name
                service_running = any(
                    service in container.lower() for container in running_containers
                )
                services_status[service] = service_running

                if service_running:
                    self.log_test_result(f"Docker service: {service}", "PASS")
                else:
                    self.log_test_result(
                        f"Docker service: {service}",
                        "FAIL",
                        f"Service not running",
                        is_critical=True,
                    )

            return all(services_status.values())

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            self.log_test_result(
                "Docker services check", "FAIL", str(e), is_critical=True
            )
            return False
        except FileNotFoundError:
            self.log_test_result(
                "Docker services check",
                "FAIL",
                "Docker not installed",
                is_critical=True,
            )
            return False

    def test_database_connectivity(self) -> bool:
        """Test database connectivity"""
        logger.info("🗄️ Testing database connectivity...")

        try:
            # Test PostgreSQL connectivity via Docker
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_postgres_clean",
                    "psql",
                    "-U",
                    "horse_racing",
                    "-d",
                    "postgres",
                    "-c",
                    "SELECT 1;",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                self.log_test_result("PostgreSQL connectivity", "PASS")

                # Test specific databases
                databases = [
                    "cards_horse_racing_db",
                    "results_horse_racing_db",
                    "advanced_racing_metrics_db",
                ]

                all_db_ok = True
                for db in databases:
                    db_result = subprocess.run(
                        [
                            "docker",
                            "exec",
                            "horse_racing_postgres_clean",
                            "psql",
                            "-U",
                            "horse_racing",
                            "-d",
                            db,
                            "-c",
                            "SELECT COUNT(*) FROM information_schema.tables;",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )

                    if db_result.returncode == 0:
                        self.log_test_result(f"Database access: {db}", "PASS")
                    else:
                        self.log_test_result(
                            f"Database access: {db}",
                            "FAIL",
                            db_result.stderr,
                            is_critical=True,
                        )
                        all_db_ok = False

                return all_db_ok
            else:
                self.log_test_result(
                    "PostgreSQL connectivity", "FAIL", result.stderr, is_critical=True
                )
                return False

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            self.log_test_result(
                "Database connectivity", "FAIL", str(e), is_critical=True
            )
            return False

    def test_redis_connectivity(self) -> bool:
        """Test Redis connectivity"""
        logger.info("🔄 Testing Redis connectivity...")

        try:
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_redis_clean",
                    "redis-cli",
                    "-a",
                    "redis_password_123",
                    "ping",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and "PONG" in result.stdout:
                self.log_test_result("Redis connectivity", "PASS")
                return True
            else:
                self.log_test_result(
                    "Redis connectivity", "FAIL", result.stderr, is_critical=True
                )
                return False

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            self.log_test_result("Redis connectivity", "FAIL", str(e), is_critical=True)
            return False

    def test_api_endpoints(self) -> bool:
        """Test API endpoints are responding"""
        logger.info("🌐 Testing API endpoints...")

        base_url = "http://localhost:3000"

        # Wait for API to be available
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{base_url}/api/system_status", timeout=10)
                break
            except requests.RequestException:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    self.log_test_result(
                        "API availability",
                        "FAIL",
                        "API not responding",
                        is_critical=True,
                    )
                    return False

        # Test key endpoints
        endpoints = [
            "/api/system_status",
            "/api/races_by_date/2025-08-24",
            "/api/health",
        ]

        all_endpoints_ok = True
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    self.log_test_result(f"API endpoint: {endpoint}", "PASS")
                else:
                    self.log_test_result(
                        f"API endpoint: {endpoint}",
                        "FAIL",
                        f"Status: {response.status_code}",
                        is_critical=True,
                    )
                    all_endpoints_ok = False
            except requests.RequestException as e:
                self.log_test_result(
                    f"API endpoint: {endpoint}", "FAIL", str(e), is_critical=True
                )
                all_endpoints_ok = False

        return all_endpoints_ok

    def test_python_imports(self) -> bool:
        """Test that critical Python modules can be imported"""
        logger.info("🐍 Testing Python imports...")

        critical_modules = [
            "src.web.api_server_enhanced",
            "tools.pipeline_coordinator",
            "src.database.database_manager",
        ]

        all_imports_ok = True
        for module in critical_modules:
            try:
                # Test import via subprocess to avoid affecting current process
                result = subprocess.run(
                    [sys.executable, "-c", f'import {module}; print("OK")'],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd=self.project_root,
                    env={**os.environ, "PYTHONPATH": str(self.project_root)},
                )

                if result.returncode == 0 and "OK" in result.stdout:
                    self.log_test_result(f"Python import: {module}", "PASS")
                else:
                    self.log_test_result(
                        f"Python import: {module}",
                        "FAIL",
                        result.stderr,
                        is_critical=True,
                    )
                    all_imports_ok = False

            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                self.log_test_result(
                    f"Python import: {module}", "FAIL", str(e), is_critical=True
                )
                all_imports_ok = False

        return all_imports_ok

    def test_file_permissions(self) -> bool:
        """Test file permissions for critical files"""
        logger.info("🔐 Testing file permissions...")

        executable_files = [
            "start_daily_watcher.sh",
            "start_pipeline_integration.sh",
            "process_manual_data.py",
            "upload_race_data.py",
        ]

        all_permissions_ok = True
        for file_name in executable_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                if os.access(file_path, os.X_OK):
                    self.log_test_result(f"File executable: {file_name}", "PASS")
                else:
                    self.log_test_result(
                        f"File executable: {file_name}", "WARN", "File not executable"
                    )
                    all_permissions_ok = False
            else:
                self.log_test_result(
                    f"File exists: {file_name}", "WARN", "File not found"
                )

        return all_permissions_ok

    def test_data_integrity(self) -> bool:
        """Test data integrity and basic database queries"""
        logger.info("📊 Testing data integrity...")

        try:
            # Test basic data queries
            queries = [
                ("cards_horse_racing_db", "SELECT COUNT(*) FROM races LIMIT 1;"),
                ("results_horse_racing_db", "SELECT COUNT(*) FROM results LIMIT 1;"),
                (
                    "advanced_racing_metrics_db",
                    "SELECT COUNT(*) FROM form_metrics LIMIT 1;",
                ),
            ]

            all_queries_ok = True
            for db, query in queries:
                try:
                    result = subprocess.run(
                        [
                            "docker",
                            "exec",
                            "horse_racing_postgres_clean",
                            "psql",
                            "-U",
                            "horse_racing",
                            "-d",
                            db,
                            "-c",
                            query,
                        ],
                        capture_output=True,
                        text=True,
                        timeout=15,
                    )

                    if result.returncode == 0:
                        self.log_test_result(f"Data query: {db}", "PASS")
                    else:
                        self.log_test_result(
                            f"Data query: {db}",
                            "WARN",
                            "Query failed - table may not exist",
                        )

                except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                    self.log_test_result(f"Data query: {db}", "WARN", str(e))
                    all_queries_ok = False

            return all_queries_ok

        except Exception as e:
            self.log_test_result("Data integrity check", "WARN", str(e))
            return False

    def test_log_file_access(self) -> bool:
        """Test that log files can be written"""
        logger.info("📝 Testing log file access...")

        log_dirs = ["logs", "data/audit", "data/versions", "data/usage_tracking"]

        all_logs_ok = True
        for log_dir in log_dirs:
            dir_path = self.project_root / log_dir
            try:
                dir_path.mkdir(parents=True, exist_ok=True)

                # Test write access
                test_file = dir_path / "test_write.tmp"
                with open(test_file, "w") as f:
                    f.write("test")
                test_file.unlink()  # Clean up

                self.log_test_result(f"Log directory writable: {log_dir}", "PASS")

            except Exception as e:
                self.log_test_result(
                    f"Log directory writable: {log_dir}", "WARN", str(e)
                )
                all_logs_ok = False

        return all_logs_ok

    def run_comprehensive_validation(self) -> Dict:
        """Run all validation tests"""
        logger.info("🚀 Starting comprehensive system validation...")

        # Run all tests
        test_functions = [
            ("Critical Files", self.test_critical_files_exist),
            ("Docker Services", self.test_docker_services),
            ("Database Connectivity", self.test_database_connectivity),
            ("Redis Connectivity", self.test_redis_connectivity),
            ("API Endpoints", self.test_api_endpoints),
            ("Python Imports", self.test_python_imports),
            ("File Permissions", self.test_file_permissions),
            ("Data Integrity", self.test_data_integrity),
            ("Log File Access", self.test_log_file_access),
        ]

        for test_name, test_function in test_functions:
            try:
                logger.info(f"🧪 Running: {test_name}")
                test_function()
            except Exception as e:
                self.log_test_result(
                    test_name, "FAIL", f"Test crashed: {e}", is_critical=True
                )

        # Determine overall status
        if self.test_results["critical_failures"]:
            self.test_results["overall_status"] = "CRITICAL_FAILURE"
        elif self.test_results["failed_tests"]:
            self.test_results["overall_status"] = "FAILURE"
        elif self.test_results["warnings"]:
            self.test_results["overall_status"] = "WARNING"
        else:
            self.test_results["overall_status"] = "SUCCESS"

        # Generate summary
        summary = {
            "overall_status": self.test_results["overall_status"],
            "tests_total": len(self.test_results["tests_run"]),
            "tests_passed": len(self.test_results["passed_tests"]),
            "tests_failed": len(self.test_results["failed_tests"]),
            "warnings": len(self.test_results["warnings"]),
            "critical_failures": len(self.test_results["critical_failures"]),
            "recommendation": self.generate_recommendation(),
        }

        self.test_results["summary"] = summary

        # Save results
        self.save_validation_results()

        return self.test_results

    def generate_recommendation(self) -> str:
        """Generate recommendation based on test results"""
        if self.test_results["critical_failures"]:
            return (
                "ROLLBACK RECOMMENDED: Critical system failures detected. "
                "Restore from backup immediately."
            )
        elif len(self.test_results["failed_tests"]) > 5:
            return (
                "ROLLBACK RECOMMENDED: Multiple system failures detected. "
                "Consider restoring from backup."
            )
        elif self.test_results["failed_tests"]:
            return (
                "INVESTIGATE REQUIRED: Some tests failed. "
                "Review failures and fix issues before proceeding."
            )
        elif self.test_results["warnings"]:
            return (
                "MONITORING RECOMMENDED: System operational but some warnings. "
                "Monitor system closely for any issues."
            )
        else:
            return (
                "CLEANUP SUCCESSFUL: All tests passed. " "System is fully operational."
            )

    def save_validation_results(self):
        """Save validation results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.output_dir / f"validation_results_{timestamp}.json"

        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)

        # Also save human-readable summary
        summary_file = self.output_dir / f"validation_summary_{timestamp}.md"
        self.generate_summary_report(summary_file)

        logger.info(f"💾 Validation results saved to: {results_file}")

    def generate_summary_report(self, output_file: Path):
        """Generate human-readable summary report"""
        status_icons = {
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "FAILURE": "❌",
            "CRITICAL_FAILURE": "🚨",
        }

        status = self.test_results["overall_status"]
        icon = status_icons.get(status, "❓")

        summary = f"""# 🔧 System Validation Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## {icon} Overall Status: {status}

## 📊 Test Summary
- **Total Tests**: {self.test_results['summary']['tests_total']}
- **Passed**: {self.test_results['summary']['tests_passed']} ✅
- **Failed**: {self.test_results['summary']['tests_failed']} ❌
- **Warnings**: {self.test_results['summary']['warnings']} ⚠️
- **Critical Failures**: {self.test_results['summary']['critical_failures']} 🚨

## 💡 Recommendation
{self.test_results['summary']['recommendation']}

## 📋 Test Details

### ✅ Passed Tests
"""

        for test in self.test_results["passed_tests"]:
            summary += f"- {test}\n"

        if self.test_results["failed_tests"]:
            summary += "\n### ❌ Failed Tests\n"
            for test in self.test_results["failed_tests"]:
                summary += f"- {test}\n"

        if self.test_results["warnings"]:
            summary += "\n### ⚠️ Warnings\n"
            for test in self.test_results["warnings"]:
                summary += f"- {test}\n"

        if self.test_results["critical_failures"]:
            summary += "\n### 🚨 Critical Failures\n"
            for test in self.test_results["critical_failures"]:
                summary += f"- {test}\n"

        summary += "\n## 🔧 Detailed Results\n"
        for test_result in self.test_results["tests_run"]:
            status_symbol = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(
                test_result["status"], "❓"
            )
            summary += f"\n### {status_symbol} {test_result['test']}\n"
            summary += f"- **Status**: {test_result['status']}\n"
            summary += f"- **Time**: {test_result['timestamp']}\n"
            if test_result["details"]:
                summary += f"- **Details**: {test_result['details']}\n"
            if test_result["critical"]:
                summary += f"- **Critical**: Yes 🚨\n"

        with open(output_file, "w") as f:
            f.write(summary)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate system after cleanup")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick validation (skip data integrity)",
    )
    parser.add_argument(
        "--critical-only", action="store_true", help="Run only critical tests"
    )

    args = parser.parse_args()

    try:
        validator = CleanupValidator(args.project_root)

        print("🔧 Starting system validation...")
        results = validator.run_comprehensive_validation()

        # Print summary
        summary = results["summary"]
        status_icons = {
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "FAILURE": "❌",
            "CRITICAL_FAILURE": "🚨",
        }

        icon = status_icons.get(summary["overall_status"], "❓")
        print(f"\n{icon} Overall Status: {summary['overall_status']}")
        print(f"📊 Tests: {summary['tests_passed']}/{summary['tests_total']} passed")

        if summary["warnings"]:
            print(f"⚠️ Warnings: {summary['warnings']}")
        if summary["tests_failed"]:
            print(f"❌ Failures: {summary['tests_failed']}")
        if summary["critical_failures"]:
            print(f"🚨 Critical Failures: {summary['critical_failures']}")

        print(f"\n💡 {summary['recommendation']}")

        # Exit code based on results
        if summary["critical_failures"] > 0:
            return 2  # Critical failure
        elif summary["tests_failed"] > 0:
            return 1  # Some failures
        else:
            return 0  # Success

    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
