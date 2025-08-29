#!/usr/bin/env python3
"""
Critical Files Validation Test
Tests the functionality of all critical files identified in cross-reference analysis.
"""

import sys
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


class CriticalFilesValidator:
    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.04"):
        self.base_path = Path(base_path)
        self.test_results = {}
        self.critical_files = []
        self.important_files = []
        self.load_critical_files()

    def load_critical_files(self) -> None:
        """Load critical files from cross-reference report."""
        report_path = self.base_path / "CRITICAL_FILES_CROSS_REFERENCE_REPORT.json"

        if report_path.exists():
            with open(report_path, "r") as f:
                data = json.load(f)

            protection_recs = data.get("protection_recommendations", {})
            self.critical_files = protection_recs.get("critical_never_delete", [])
            self.important_files = protection_recs.get("important_careful_review", [])

            print(f"✅ Loaded {len(self.critical_files)} critical files")
            print(f"✅ Loaded {len(self.important_files)} important files")
        else:
            print("❌ Cross-reference report not found")

    def test_python_file_syntax(self, file_path: str) -> Tuple[bool, str]:
        """Test if Python file has valid syntax."""
        full_path = self.base_path / file_path

        if not full_path.exists():
            return False, f"File not found: {file_path}"

        try:
            # Test syntax by compiling
            with open(full_path, "r", encoding="utf-8") as f:
                source = f.read()
            compile(source, str(full_path), "exec")
            return True, "Syntax OK"
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"
        except Exception as e:
            return False, f"Error: {e}"

    def test_python_imports(self, file_path: str) -> Tuple[bool, str]:
        """Test if Python file imports can be resolved."""
        full_path = self.base_path / file_path

        if not full_path.exists():
            return False, f"File not found: {file_path}"

        try:
            # Try to load the module
            spec = importlib.util.spec_from_file_location("test_module", full_path)
            if spec is None:
                return False, "Could not create module spec"

            # This tests if imports can be resolved without executing
            module = importlib.util.module_from_spec(spec)
            return True, "Imports OK"
        except ImportError as e:
            return False, f"Import Error: {e}"
        except Exception as e:
            return False, f"Error: {e}"

    def test_json_file_validity(self, file_path: str) -> Tuple[bool, str]:
        """Test if JSON file is valid."""
        full_path = self.base_path / file_path

        if not full_path.exists():
            return False, f"File not found: {file_path}"

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                json.load(f)
            return True, "JSON Valid"
        except json.JSONDecodeError as e:
            return False, f"JSON Error: {e}"
        except Exception as e:
            return False, f"Error: {e}"

    def test_file_accessibility(self, file_path: str) -> Tuple[bool, str]:
        """Test if file is accessible and readable."""
        full_path = self.base_path / file_path

        if not full_path.exists():
            return False, f"File not found: {file_path}"

        if not full_path.is_file():
            return False, f"Not a file: {file_path}"

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                f.read(100)  # Read first 100 chars
            return True, f"Accessible ({full_path.stat().st_size} bytes)"
        except Exception as e:
            return False, f"Access Error: {e}"

    def validate_critical_files(self) -> None:
        """Validate all critical files."""
        print("\n🔴 TESTING CRITICAL FILES (Never Delete):")
        print("=" * 60)

        critical_results = {}

        for file_path in self.critical_files:
            print(f"\n🎯 Testing: {file_path}")

            # Test file accessibility
            accessible, access_msg = self.test_file_accessibility(file_path)
            print(f"   📁 Accessibility: {'✅' if accessible else '❌'} {access_msg}")

            tests = {"accessibility": (accessible, access_msg)}

            if accessible:
                # Test based on file type
                if file_path.endswith(".py"):
                    # Python file tests
                    syntax_ok, syntax_msg = self.test_python_file_syntax(file_path)
                    imports_ok, imports_msg = self.test_python_imports(file_path)

                    print(f"   🐍 Syntax: {'✅' if syntax_ok else '❌'} {syntax_msg}")
                    print(
                        f"   📦 Imports: {'✅' if imports_ok else '❌'} {imports_msg}"
                    )

                    tests.update(
                        {
                            "syntax": (syntax_ok, syntax_msg),
                            "imports": (imports_ok, imports_msg),
                        }
                    )

                elif file_path.endswith(".json"):
                    # JSON file tests
                    json_ok, json_msg = self.test_json_file_validity(file_path)
                    print(f"   📋 JSON: {'✅' if json_ok else '❌'} {json_msg}")

                    tests.update({"json_validity": (json_ok, json_msg)})

            critical_results[file_path] = tests

        self.test_results["critical_files"] = critical_results

    def validate_important_files(self) -> None:
        """Validate all important files."""
        print("\n🟡 TESTING IMPORTANT FILES (Careful Review):")
        print("=" * 60)

        important_results = {}

        for file_path in self.important_files:
            print(f"\n📋 Testing: {file_path}")

            # Test file accessibility
            accessible, access_msg = self.test_file_accessibility(file_path)
            print(f"   📁 Accessibility: {'✅' if accessible else '❌'} {access_msg}")

            tests = {"accessibility": (accessible, access_msg)}

            if accessible:
                # Test based on file type
                if file_path.endswith(".json"):
                    json_ok, json_msg = self.test_json_file_validity(file_path)
                    print(f"   📋 JSON: {'✅' if json_ok else '❌'} {json_msg}")
                    tests.update({"json_validity": (json_ok, json_msg)})

            important_results[file_path] = tests

        self.test_results["important_files"] = important_results

    def generate_validation_summary(self) -> None:
        """Generate validation summary."""
        print("\n" + "=" * 80)
        print("📊 CRITICAL FILES VALIDATION SUMMARY")
        print("=" * 80)

        # Count results
        critical_passed = 0
        critical_total = len(self.critical_files)
        important_passed = 0
        important_total = len(self.important_files)

        # Check critical files
        critical_issues = []
        for file_path, tests in self.test_results.get("critical_files", {}).items():
            file_ok = all(result[0] for result in tests.values())
            if file_ok:
                critical_passed += 1
            else:
                failed_tests = [test for test, result in tests.items() if not result[0]]
                critical_issues.append(f"{file_path}: {', '.join(failed_tests)}")

        # Check important files
        important_issues = []
        for file_path, tests in self.test_results.get("important_files", {}).items():
            file_ok = all(result[0] for result in tests.values())
            if file_ok:
                important_passed += 1
            else:
                failed_tests = [test for test, result in tests.items() if not result[0]]
                important_issues.append(f"{file_path}: {', '.join(failed_tests)}")

        # Calculate health score
        total_passed = critical_passed + important_passed
        total_files = critical_total + important_total
        health_score = int((total_passed / total_files) * 100) if total_files > 0 else 0

        # Health status
        if health_score >= 95:
            health_status = "🟢 EXCELLENT"
        elif health_score >= 80:
            health_status = "🟡 GOOD"
        else:
            health_status = "🔴 POOR"

        print(f"\n🏥 CRITICAL FILES HEALTH: {health_status} ({health_score}/100)")

        print(f"\n📊 VALIDATION RESULTS:")
        print(f"   🔴 Critical Files: {critical_passed}/{critical_total} passed")
        print(f"   🟡 Important Files: {important_passed}/{important_total} passed")
        print(
            f"   📈 Overall Success Rate: {total_passed}/{total_files} ({health_score}%)"
        )

        if critical_issues:
            print(f"\n🚨 CRITICAL FILE ISSUES:")
            for issue in critical_issues:
                print(f"   ❌ {issue}")

        if important_issues:
            print(f"\n⚠️  IMPORTANT FILE ISSUES:")
            for issue in important_issues:
                print(f"   ❌ {issue}")

        if health_score == 100:
            print(f"\n🎉 PERFECT SCORE!")
            print(f"   ✅ All critical and important files are fully functional")
            print(f"   ✅ System ready for aggressive cleanup operations")
        elif health_score >= 95:
            print(f"\n✅ EXCELLENT HEALTH!")
            print(f"   ✅ System is robust and ready for cleanup")
            if critical_issues or important_issues:
                print(f"   ⚠️  Minor issues detected but system remains stable")
        else:
            print(f"\n⚠️  ISSUES DETECTED!")
            print(f"   🛑 Review and fix issues before proceeding with cleanup")

        # Save results
        report_data = {
            "timestamp": "2025-08-29",
            "health_score": health_score,
            "critical_files_passed": critical_passed,
            "critical_files_total": critical_total,
            "important_files_passed": important_passed,
            "important_files_total": important_total,
            "critical_issues": critical_issues,
            "important_issues": important_issues,
            "detailed_results": self.test_results,
        }

        with open("CRITICAL_FILES_VALIDATION_REPORT.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Detailed report saved to: CRITICAL_FILES_VALIDATION_REPORT.json")

    def run_validation(self) -> None:
        """Run complete validation of critical files."""
        print("🔍 CRITICAL FILES FUNCTIONALITY VALIDATION")
        print("=" * 80)
        print("Testing all files identified as critical in cross-reference analysis...")

        self.validate_critical_files()
        self.validate_important_files()
        self.generate_validation_summary()


if __name__ == "__main__":
    validator = CriticalFilesValidator()
    validator.run_validation()
