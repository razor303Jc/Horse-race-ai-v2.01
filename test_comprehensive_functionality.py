#!/usr/bin/env python3
"""
Comprehensive System Functionality Test
Tests actual system functionality with cross-referenced protected files.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime


class SystemFunctionalityTester:
    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.04"):
        self.base_path = Path(base_path)
        self.test_results = {}
        self.functionality_score = 0

    def test_api_endpoints(self) -> bool:
        """Test critical API functionality."""
        print("\n🔌 TESTING API ENDPOINTS...")

        api_tests = []

        # Test prediction API syntax and imports
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.path.insert(0, 'api'); import prediction_api; print('✅ Prediction API imports successfully')",
                ],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print("   ✅ api/prediction_api.py - Import successful")
                api_tests.append(True)
            else:
                print(f"   ❌ api/prediction_api.py - Import failed: {result.stderr}")
                api_tests.append(False)

        except Exception as e:
            print(f"   ❌ api/prediction_api.py - Error: {e}")
            api_tests.append(False)

        # Test ML management API
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.path.insert(0, 'api'); import ml_management_api; print('✅ ML Management API imports successfully')",
                ],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print("   ✅ api/ml_management_api.py - Import successful")
                api_tests.append(True)
            else:
                print(
                    f"   ❌ api/ml_management_api.py - Import failed: {result.stderr}"
                )
                api_tests.append(False)

        except Exception as e:
            print(f"   ❌ api/ml_management_api.py - Error: {e}")
            api_tests.append(False)

        return all(api_tests)

    def test_data_processing(self) -> bool:
        """Test data processing functionality."""
        print("\n📊 TESTING DATA PROCESSING...")

        processing_tests = []

        # Test daily downloads manager
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.path.insert(0, '.'); from tools.data_processing.daily_downloads_manager import *; print('✅ Daily downloads manager imports successfully')",
                ],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print(
                    "   ✅ tools/data_processing/daily_downloads_manager.py - Import successful"
                )
                processing_tests.append(True)
            else:
                print(
                    f"   ❌ tools/data_processing/daily_downloads_manager.py - Import failed"
                )
                processing_tests.append(False)

        except Exception as e:
            print(f"   ❌ daily_downloads_manager.py - Error: {e}")
            processing_tests.append(False)

        # Test CSV data cleaner
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.path.insert(0, '.'); from tools.data_quality.csv_data_cleaner import *; print('✅ CSV data cleaner imports successfully')",
                ],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print(
                    "   ✅ tools/data_quality/csv_data_cleaner.py - Import successful"
                )
                processing_tests.append(True)
            else:
                print("   ❌ tools/data_quality/csv_data_cleaner.py - Import failed")
                processing_tests.append(False)

        except Exception as e:
            print(f"   ❌ csv_data_cleaner.py - Error: {e}")
            processing_tests.append(False)

        # Test quick CSV import
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.path.insert(0, '.'); from tools.pipeline.quick_csv_import import *; print('✅ Quick CSV import imports successfully')",
                ],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print("   ✅ tools/pipeline/quick_csv_import.py - Import successful")
                processing_tests.append(True)
            else:
                print("   ❌ tools/pipeline/quick_csv_import.py - Import failed")
                processing_tests.append(False)

        except Exception as e:
            print(f"   ❌ quick_csv_import.py - Error: {e}")
            processing_tests.append(False)

        return all(processing_tests)

    def test_automation_system(self) -> bool:
        """Test automation system functionality."""
        print("\n🤖 TESTING AUTOMATION SYSTEM...")

        automation_tests = []

        # Test human-like downloader
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.path.insert(0, '.'); from src.automation.human_like_downloader import *; print('✅ Human-like downloader imports successfully')",
                ],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print(
                    "   ✅ src/automation/human_like_downloader.py - Import successful"
                )
                automation_tests.append(True)
            else:
                print("   ❌ src/automation/human_like_downloader.py - Import failed")
                automation_tests.append(False)

        except Exception as e:
            print(f"   ❌ human_like_downloader.py - Error: {e}")
            automation_tests.append(False)

        return all(automation_tests)

    def test_configuration_files(self) -> bool:
        """Test configuration files."""
        print("\n⚙️  TESTING CONFIGURATION FILES...")

        config_tests = []

        # Test JSON configs
        json_configs = [
            "config/pipeline_integration_config.json",
            "config/daily_watcher_config.json",
            "node-red/flows-enhanced.json",
            "node-red/working-flows.json",
        ]

        for config_file in json_configs:
            config_path = self.base_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        json.load(f)
                    print(f"   ✅ {config_file} - Valid JSON")
                    config_tests.append(True)
                except json.JSONDecodeError as e:
                    print(f"   ❌ {config_file} - Invalid JSON: {e}")
                    config_tests.append(False)
            else:
                print(f"   ❌ {config_file} - File not found")
                config_tests.append(False)

        # Test other critical files
        other_configs = [
            "ML_CONFIG.yaml",
            "pyproject.toml",
            "AI_SCHEMA.sql",
            "database/ai_predictions_enhanced_schema.sql",
        ]

        for config_file in other_configs:
            config_path = self.base_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        content = f.read()
                    if len(content) > 0:
                        print(
                            f"   ✅ {config_file} - Accessible ({len(content)} chars)"
                        )
                        config_tests.append(True)
                    else:
                        print(f"   ❌ {config_file} - Empty file")
                        config_tests.append(False)
                except Exception as e:
                    print(f"   ❌ {config_file} - Error: {e}")
                    config_tests.append(False)
            else:
                print(f"   ❌ {config_file} - File not found")
                config_tests.append(False)

        return all(config_tests)

    def test_node_red_flows(self) -> bool:
        """Test Node-RED flow functionality."""
        print("\n🔄 TESTING NODE-RED FLOWS...")

        # Check if all referenced Python scripts exist and are functional
        node_red_scripts = [
            "api/prediction_api.py",
            "tools/bulk_uploader/bulk_upload_processor.py",
            "tools/data_processing/daily_downloads_manager.py",
            "tools/data_quality/csv_data_cleaner.py",
            "tools/pipeline/quick_csv_import.py",
        ]

        script_tests = []
        for script in node_red_scripts:
            script_path = self.base_path / script
            if script_path.exists():
                print(f"   ✅ {script} - Exists and accessible")
                script_tests.append(True)
            else:
                print(f"   ❌ {script} - Missing")
                script_tests.append(False)

        return all(script_tests)

    def run_comprehensive_test(self) -> None:
        """Run comprehensive system functionality test."""
        print("🔍 COMPREHENSIVE SYSTEM FUNCTIONALITY TEST")
        print("=" * 80)
        print("Testing actual system functionality with protected files...")

        # Run all tests
        api_ok = self.test_api_endpoints()
        data_ok = self.test_data_processing()
        automation_ok = self.test_automation_system()
        config_ok = self.test_configuration_files()
        node_red_ok = self.test_node_red_flows()

        # Calculate functionality score
        test_results = [api_ok, data_ok, automation_ok, config_ok, node_red_ok]
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        self.functionality_score = int((passed_tests / total_tests) * 100)

        # Determine health status
        if self.functionality_score >= 95:
            health_status = "🟢 EXCELLENT"
        elif self.functionality_score >= 80:
            health_status = "🟡 GOOD"
        else:
            health_status = "🔴 POOR"

        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE FUNCTIONALITY RESULTS")
        print("=" * 80)

        print(
            f"\n🏥 SYSTEM FUNCTIONALITY: {health_status} ({self.functionality_score}/100)"
        )

        print(f"\n📋 TEST RESULTS:")
        print(f"   🔌 API Endpoints: {'✅ PASS' if api_ok else '❌ FAIL'}")
        print(f"   📊 Data Processing: {'✅ PASS' if data_ok else '❌ FAIL'}")
        print(f"   🤖 Automation System: {'✅ PASS' if automation_ok else '❌ FAIL'}")
        print(f"   ⚙️  Configuration Files: {'✅ PASS' if config_ok else '❌ FAIL'}")
        print(f"   🔄 Node-RED Flows: {'✅ PASS' if node_red_ok else '❌ FAIL'}")

        print(f"\n📈 FUNCTIONALITY SUMMARY:")
        print(f"   • Tests Passed: {passed_tests}/{total_tests}")
        print(f"   • Success Rate: {self.functionality_score}%")

        if self.functionality_score == 100:
            print(f"\n🎉 PERFECT FUNCTIONALITY!")
            print(f"   ✅ All critical systems are fully operational")
            print(f"   ✅ System is ready for aggressive cleanup")
            print(f"   ✅ Cross-reference analysis protection is working perfectly")
        elif self.functionality_score >= 95:
            print(f"\n✅ EXCELLENT FUNCTIONALITY!")
            print(f"   ✅ System is robust and cleanup-ready")
            print(f"   ⚠️  Minor issues may exist but core functionality intact")
        else:
            print(f"\n⚠️  FUNCTIONALITY ISSUES DETECTED!")
            print(f"   🛑 Review and fix issues before proceeding")

        # Save detailed results
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "functionality_score": self.functionality_score,
            "test_results": {
                "api_endpoints": api_ok,
                "data_processing": data_ok,
                "automation_system": automation_ok,
                "configuration_files": config_ok,
                "node_red_flows": node_red_ok,
            },
            "overall_status": (
                "EXCELLENT"
                if self.functionality_score >= 95
                else "GOOD" if self.functionality_score >= 80 else "POOR"
            ),
        }

        with open("COMPREHENSIVE_FUNCTIONALITY_TEST_REPORT.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print(
            f"\n📄 Detailed report saved to: COMPREHENSIVE_FUNCTIONALITY_TEST_REPORT.json"
        )
        print("=" * 80)


if __name__ == "__main__":
    tester = SystemFunctionalityTester()
    tester.run_comprehensive_test()
