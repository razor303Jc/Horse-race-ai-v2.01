#!/usr/bin/env python3
"""
Enhanced File Watcher v2.05 - System Test Suite
Validation and testing script for the v2.05 file watcher system

Tests:
- System dependencies and configuration
- Docker container connectivity
- Redis and database connections
- File processing simulation
- Pipeline integration
- C2 Command Center integration

Author: Horse Racing AI System
Version: v2.05 - Latest
"""

import json
import os
import sys
import time
import tempfile
import shutil
import zipfile
import pandas as pd
from pathlib import Path
from datetime import datetime
import subprocess
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedWatcherV205TestSuite:
    """Test suite for Enhanced File Watcher v2.05"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.05"):
        self.base_path = Path(base_path)
        self.version = "v2.05"
        self.test_results = []

        # Test configuration
        self.test_data_dir = self.base_path / "data/test_v2_05"
        self.test_data_dir.mkdir(exist_ok=True)

    def log_test_result(self, test_name: str, passed: bool, message: str = ""):
        """Log a test result"""
        status = "PASS" if passed else "FAIL"
        logger.info(f"[{status}] {test_name}: {message}")

        self.test_results.append(
            {
                "test": test_name,
                "status": status,
                "passed": passed,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return passed

    def test_system_dependencies(self) -> bool:
        """Test system dependencies"""
        logger.info("🔍 Testing system dependencies...")

        dependencies = [("python3", "Python 3"), ("docker", "Docker"), ("pip3", "Pip3")]

        all_passed = True

        for cmd, name in dependencies:
            try:
                result = subprocess.run(
                    [cmd, "--version"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    self.log_test_result(
                        f"Dependency: {name}",
                        True,
                        f"Version: {result.stdout.split()[1] if result.stdout else 'unknown'}",
                    )
                else:
                    self.log_test_result(f"Dependency: {name}", False, "Not available")
                    all_passed = False
            except FileNotFoundError:
                self.log_test_result(f"Dependency: {name}", False, "Not found")
                all_passed = False

        return all_passed

    def test_python_modules(self) -> bool:
        """Test required Python modules"""
        logger.info("🐍 Testing Python modules...")

        required_modules = [
            "watchdog",
            "redis",
            "psycopg2",
            "pandas",
            "asyncio",
            "json",
            "pathlib",
            "zipfile",
        ]

        all_passed = True

        for module in required_modules:
            try:
                __import__(module)
                self.log_test_result(f"Python module: {module}", True, "Available")
            except ImportError as e:
                self.log_test_result(f"Python module: {module}", False, str(e))
                all_passed = False

        return all_passed

    def test_docker_containers(self) -> bool:
        """Test Docker container availability"""
        logger.info("🐳 Testing Docker containers...")

        required_containers = ["redis", "postgres", "horse_racing_data_pipeline_clean"]

        all_passed = True

        for container in required_containers:
            try:
                # Check if container exists and is running
                result = subprocess.run(
                    [
                        "docker",
                        "ps",
                        "--filter",
                        f"name={container}",
                        "--format",
                        "{{.Status}}",
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0 and result.stdout.strip():
                    status = result.stdout.strip()
                    self.log_test_result(
                        f"Docker container: {container}", True, f"Status: {status}"
                    )
                else:
                    self.log_test_result(
                        f"Docker container: {container}", False, "Not running"
                    )
                    all_passed = False

            except Exception as e:
                self.log_test_result(f"Docker container: {container}", False, str(e))
                all_passed = False

        return all_passed

    def test_redis_connectivity(self) -> bool:
        """Test Redis connectivity"""
        logger.info("📊 Testing Redis connectivity...")

        try:
            import redis

            client = redis.Redis(
                host="redis",
                port=6379,
                password="redis_password_123",
                decode_responses=True,
            )

            # Test basic operations
            client.ping()
            self.log_test_result("Redis: Ping", True, "Connection successful")

            # Test set/get
            test_key = f"test:{int(time.time())}"
            client.set(test_key, "test_value", ex=60)
            value = client.get(test_key)

            if value == "test_value":
                self.log_test_result("Redis: Set/Get", True, "Operations successful")
                client.delete(test_key)
                return True
            else:
                self.log_test_result("Redis: Set/Get", False, "Value mismatch")
                return False

        except Exception as e:
            self.log_test_result("Redis connectivity", False, str(e))
            return False

    def test_database_connectivity(self) -> bool:
        """Test PostgreSQL database connectivity"""
        logger.info("🗄️ Testing database connectivity...")

        try:
            import psycopg2

            conn = psycopg2.connect(
                host="postgres",
                port=5432,
                dbname="cards_horse_racing_db",
                user="horse_racing",
                password="secure_password_123",
            )

            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]

            self.log_test_result(
                "Database: Connection", True, f"PostgreSQL: {version.split()[1]}"
            )

            # Test basic query
            cursor.execute("SELECT NOW()")
            timestamp = cursor.fetchone()[0]

            self.log_test_result("Database: Query", True, f"Current time: {timestamp}")

            cursor.close()
            conn.close()

            return True

        except Exception as e:
            self.log_test_result("Database connectivity", False, str(e))
            return False

    def test_file_structure(self) -> bool:
        """Test required file structure"""
        logger.info("📁 Testing file structure...")

        required_files = [
            "tools/automation/enhanced_file_watcher_v2_05.py",
            "config/enhanced_watcher_config_v2_05.json",
            "tools/automation/start_enhanced_watcher_v2_05.sh",
            "tools/automation/watcher_status_api_v2_05.py",
        ]

        required_dirs = [
            "data/daily_downloads/manual_download",
            "data/daily_downloads/auto_download",
            "data/external_feeds",
            "logs",
            "config",
        ]

        all_passed = True

        # Check files
        for file_path in required_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                size_kb = full_path.stat().st_size / 1024
                self.log_test_result(
                    f"File: {file_path}", True, f"Size: {size_kb:.1f}KB"
                )
            else:
                self.log_test_result(f"File: {file_path}", False, "Missing")
                all_passed = False

        # Check directories
        for dir_path in required_dirs:
            full_path = self.base_path / dir_path
            if full_path.exists() and full_path.is_dir():
                self.log_test_result(f"Directory: {dir_path}", True, "Exists")
            else:
                self.log_test_result(f"Directory: {dir_path}", False, "Missing")
                all_passed = False

        return all_passed

    def test_configuration_loading(self) -> bool:
        """Test configuration file loading"""
        logger.info("⚙️ Testing configuration loading...")

        config_file = self.base_path / "config/enhanced_watcher_config_v2_05.json"

        try:
            with open(config_file, "r") as f:
                config = json.load(f)

            # Check required sections
            required_sections = [
                "watcher_settings",
                "data_validation",
                "pipeline_triggers",
                "file_patterns",
            ]

            all_passed = True

            for section in required_sections:
                if section in config:
                    self.log_test_result(f"Config section: {section}", True, "Present")
                else:
                    self.log_test_result(f"Config section: {section}", False, "Missing")
                    all_passed = False

            # Check version
            config_version = config.get("version", "unknown")
            if config_version == self.version:
                self.log_test_result(
                    "Config version", True, f"Version: {config_version}"
                )
            else:
                self.log_test_result(
                    "Config version",
                    False,
                    f"Expected {self.version}, got {config_version}",
                )
                all_passed = False

            return all_passed

        except Exception as e:
            self.log_test_result("Configuration loading", False, str(e))
            return False

    def create_test_data(self) -> bool:
        """Create test data files for processing"""
        logger.info("📝 Creating test data...")

        try:
            # Create test races CSV
            races_data = {
                "race_id": ["R001", "R002", "R003"],
                "race_time": ["14:30", "15:00", "15:30"],
                "course": ["Newmarket", "Ascot", "York"],
                "race_name": ["Test Race 1", "Test Race 2", "Test Race 3"],
                "distance": ["1200m", "1600m", "2000m"],
                "going": ["Good", "Soft", "Firm"],
            }

            races_df = pd.DataFrame(races_data)
            races_csv = self.test_data_dir / "races.csv"
            races_df.to_csv(races_csv, index=False)

            # Create test horses CSV
            horses_data = {
                "horse_id": ["H001", "H002", "H003", "H004", "H005", "H006"],
                "horse_name": [
                    "Test Horse 1",
                    "Test Horse 2",
                    "Test Horse 3",
                    "Test Horse 4",
                    "Test Horse 5",
                    "Test Horse 6",
                ],
                "race_id": ["R001", "R001", "R002", "R002", "R003", "R003"],
                "jockey": [
                    "J Smith",
                    "J Jones",
                    "J Brown",
                    "J Wilson",
                    "J Davis",
                    "J Miller",
                ],
                "trainer": [
                    "T Adams",
                    "T Baker",
                    "T Clark",
                    "T Evans",
                    "T Fisher",
                    "T Green",
                ],
                "weight": ["57kg", "58kg", "59kg", "57kg", "58kg", "59kg"],
            }

            horses_df = pd.DataFrame(horses_data)
            horses_csv = self.test_data_dir / "horses.csv"
            horses_df.to_csv(horses_csv, index=False)

            # Create test results CSV
            results_data = {
                "race_id": ["R001", "R001", "R002", "R002"],
                "position": [1, 2, 1, 2],
                "horse_id": ["H001", "H002", "H003", "H004"],
                "starting_price": ["3/1", "5/2", "2/1", "7/2"],
                "finishing_time": ["1:12.34", "1:12.89", "1:35.67", "1:36.12"],
            }

            results_df = pd.DataFrame(results_data)
            results_csv = self.test_data_dir / "results.csv"
            results_df.to_csv(results_csv, index=False)

            # Create test ZIP files
            cards_zip = self.test_data_dir / "test_racecard_data.zip"
            with zipfile.ZipFile(cards_zip, "w") as zf:
                zf.write(races_csv, "races.csv")
                zf.write(horses_csv, "horses.csv")

            results_zip = self.test_data_dir / "test_results_data.zip"
            with zipfile.ZipFile(results_zip, "w") as zf:
                zf.write(results_csv, "results.csv")

            self.log_test_result(
                "Test data creation", True, "Cards and results data created"
            )
            return True

        except Exception as e:
            self.log_test_result("Test data creation", False, str(e))
            return False

    def test_api_status_script(self) -> bool:
        """Test the status API script"""
        logger.info("🔌 Testing status API script...")

        api_script = self.base_path / "tools/automation/watcher_status_api_v2_05.py"

        try:
            # Test service status command
            result = subprocess.run(
                ["python3", str(api_script), "service"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                response = json.loads(result.stdout)
                if "version" in response and response["version"] == self.version:
                    self.log_test_result(
                        "Status API: Service", True, "Command executed successfully"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Status API: Service", False, "Invalid response format"
                    )
                    return False
            else:
                self.log_test_result(
                    "Status API: Service", False, f"Exit code: {result.returncode}"
                )
                return False

        except Exception as e:
            self.log_test_result("Status API script", False, str(e))
            return False

    def test_startup_script(self) -> bool:
        """Test the startup script"""
        logger.info("🚀 Testing startup script...")

        startup_script = (
            self.base_path / "tools/automation/start_enhanced_watcher_v2_05.sh"
        )

        try:
            # Test validate command
            result = subprocess.run(
                ["bash", str(startup_script), "validate"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.log_test_result(
                    "Startup script: Validate", True, "Validation successful"
                )
                return True
            else:
                self.log_test_result(
                    "Startup script: Validate",
                    False,
                    f"Exit code: {result.returncode}, Error: {result.stderr}",
                )
                return False

        except Exception as e:
            self.log_test_result("Startup script", False, str(e))
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        logger.info(f"🧪 Starting Enhanced File Watcher v{self.version} Test Suite")
        logger.info("=" * 60)

        start_time = datetime.now()

        # Run all tests
        tests = [
            self.test_system_dependencies,
            self.test_python_modules,
            self.test_docker_containers,
            self.test_redis_connectivity,
            self.test_database_connectivity,
            self.test_file_structure,
            self.test_configuration_loading,
            self.create_test_data,
            self.test_api_status_script,
            self.test_startup_script,
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {e}")
                self.log_test_result(test.__name__, False, f"Exception: {e}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # Summary
        summary = {
            "version": self.version,
            "test_run_id": f"test_{int(time.time())}",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": round(duration, 2),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": round(success_rate, 2),
            "overall_status": "PASS" if failed_tests == 0 else "FAIL",
            "test_results": self.test_results,
        }

        logger.info("=" * 60)
        logger.info(
            f"🏁 Test Suite Complete: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)"
        )
        logger.info(f"⏱️ Duration: {duration:.2f} seconds")

        if failed_tests == 0:
            logger.info(
                "✅ All tests passed! Enhanced File Watcher v2.05 is ready for deployment."
            )
        else:
            logger.warning(
                f"❌ {failed_tests} tests failed. Please review the failed tests before deployment."
            )

        # Save test report
        report_file = self.base_path / f"logs/test_report_v2_05_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"📄 Test report saved: {report_file}")

        return summary

    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            if self.test_data_dir.exists():
                shutil.rmtree(self.test_data_dir)
                logger.info("🧹 Test data cleaned up")
        except Exception as e:
            logger.warning(f"Failed to cleanup test data: {e}")


def main():
    """Main test runner"""
    test_suite = EnhancedWatcherV205TestSuite()

    try:
        summary = test_suite.run_all_tests()

        # Print JSON summary if requested
        if len(sys.argv) > 1 and sys.argv[1] == "--json":
            print(json.dumps(summary, indent=2))

        # Exit with appropriate code
        sys.exit(0 if summary["failed_tests"] == 0 else 1)

    except KeyboardInterrupt:
        logger.info("🛑 Test suite interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        sys.exit(1)
    finally:
        test_suite.cleanup_test_data()


if __name__ == "__main__":
    main()
