#!/usr/bin/env python3
"""
🧪 Enhanced Test Runner with Integrated Cleanup
==============================================

Enhanced test framework that automatically runs file/function analysis
alongside unit tests to provide comprehensive project health reports.

This system:
1. Runs all unit tests with detailed reporting
2. Executes integrated cleanup analysis during test runs
3. Generates combined test + cleanup reports
4. Provides recommendations for code organization
5. Ensures only needed files/functions remain in the project

Author: AI Assistant
Date: August 29, 2025
Version: 2.0.0
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Add the tools directory to the path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools" / "analysis"))

try:
    from integrated_cleanup_analyzer import IntegratedCleanupAnalyzer
except ImportError:
    print("❌ Could not import IntegratedCleanupAnalyzer")
    print("Make sure tools/analysis/integrated_cleanup_analyzer.py exists")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedTestRunner:
    """Enhanced test runner with integrated cleanup analysis"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or PROJECT_ROOT)
        self.test_root = self.project_root / "tests"
        self.reports_dir = self.project_root / "data" / "test_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Initialize cleanup analyzer
        self.cleanup_analyzer = IntegratedCleanupAnalyzer(str(self.project_root))

        # Test results
        self.test_results = {}
        self.cleanup_results = {}
        self.combined_report = {}

    def run_unit_tests(self, verbose: bool = True) -> Dict:
        """Run unit tests with comprehensive reporting"""
        logger.info("🧪 Running unit tests...")

        test_results = {
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "duration": 0,
            "summary": {},
            "details": {},
        }

        start_time = time.time()

        try:
            # Prepare pytest command
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                str(self.test_root),
                "--tb=short",
                "--json-report",
                f"--json-report-file={self.reports_dir}/pytest_results.json",
                "--cov=src",
                "--cov=tools",
                "--cov-report=html:data/test_reports/coverage_html",
                "--cov-report=json:data/test_reports/coverage.json",
            ]

            if verbose:
                cmd.append("-v")

            # Run tests
            logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600,  # 10 minute timeout
            )

            test_results["exit_code"] = result.returncode
            test_results["stdout"] = result.stdout
            test_results["stderr"] = result.stderr
            test_results["duration"] = time.time() - start_time

            # Load detailed JSON results if available
            json_report_path = self.reports_dir / "pytest_results.json"
            if json_report_path.exists():
                with open(json_report_path, "r") as f:
                    detailed_results = json.load(f)
                test_results["details"] = detailed_results

                # Extract summary
                if "summary" in detailed_results:
                    test_results["summary"] = detailed_results["summary"]

            # Determine overall status
            if result.returncode == 0:
                test_results["status"] = "passed"
            else:
                test_results["status"] = "failed"

        except subprocess.TimeoutExpired:
            test_results["status"] = "timeout"
            test_results["error"] = "Tests timed out after 10 minutes"
            test_results["duration"] = time.time() - start_time
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            test_results["duration"] = time.time() - start_time

        self.test_results = test_results
        return test_results

    def run_integration_tests(self) -> Dict:
        """Run integration tests"""
        logger.info("🔗 Running integration tests...")

        integration_results = {
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "tests_run": [],
        }

        try:
            # Run integration tests specifically
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                str(self.test_root / "integration"),
                "--tb=short",
                "-v",
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root, timeout=300
            )

            integration_results["exit_code"] = result.returncode
            integration_results["stdout"] = result.stdout
            integration_results["stderr"] = result.stderr
            integration_results["status"] = (
                "passed" if result.returncode == 0 else "failed"
            )

        except Exception as e:
            integration_results["status"] = "error"
            integration_results["error"] = str(e)

        return integration_results

    def run_cleanup_analysis(self) -> Dict:
        """Run integrated cleanup analysis"""
        logger.info("🧹 Running integrated cleanup analysis...")

        try:
            # Run the full cleanup analysis
            start_time = time.time()

            # Analyze project structure
            structure_analysis = self.cleanup_analyzer.analyze_project_structure()

            # Analyze Python usage
            python_analysis = self.cleanup_analyzer.analyze_python_usage()

            # Generate cleanup recommendations
            recommendations = self.cleanup_analyzer.generate_cleanup_recommendations()

            cleanup_results = {
                "timestamp": datetime.now().isoformat(),
                "duration": time.time() - start_time,
                "status": "completed",
                "structure_analysis": structure_analysis,
                "python_analysis": python_analysis,
                "recommendations": recommendations,
                "total_files": structure_analysis.get("total_files", 0),
                "total_recommendations": len(recommendations),
            }

            self.cleanup_results = cleanup_results
            return cleanup_results

        except Exception as e:
            logger.error(f"Cleanup analysis failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e),
            }

    def generate_combined_report(self) -> str:
        """Generate combined test + cleanup report"""
        logger.info("📊 Generating combined report...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"combined_test_cleanup_report_{timestamp}.md"

        with open(report_path, "w") as f:
            f.write("# 🧪 Combined Test & Cleanup Analysis Report\\n")
            f.write(f"Generated: {datetime.now().isoformat()}\\n\\n")

            # Executive Summary
            f.write("## 📈 Executive Summary\\n\\n")

            # Important notice
            f.write("**Note**: SQL and database files are excluded from cleanup ")
            f.write("analysis as they require special handling.\\n\\n")

            # Test Results Summary
            test_status = self.test_results.get("status", "unknown")
            test_emoji = {
                "passed": "✅",
                "failed": "❌",
                "timeout": "⏰",
                "error": "🚨",
            }.get(test_status, "❓")
            f.write(f"### {test_emoji} Test Results\\n")
            f.write(f"- **Status**: {test_status}\\n")
            duration = self.test_results.get("duration", 0)
            f.write(f"- **Duration**: {duration:.2f} seconds\\n")

            if "summary" in self.test_results:
                summary = self.test_results["summary"]
                f.write(f"- **Tests Passed**: {summary.get('passed', 0)}\\n")
                f.write(f"- **Tests Failed**: {summary.get('failed', 0)}\\n")
                f.write(f"- **Tests Skipped**: {summary.get('skipped', 0)}\\n")
                f.write(f"- **Total Tests**: {summary.get('total', 0)}\\n")

            # Cleanup Results Summary
            f.write("\\n### 🧹 Cleanup Analysis\\n")
            if self.cleanup_results.get("status") == "completed":
                total_files = self.cleanup_results.get("total_files", 0)
                total_recs = self.cleanup_results.get("total_recommendations", 0)
                duration = self.cleanup_results.get("duration", 0)
                f.write(f"- **Total Files Analyzed**: {total_files}\\n")
                f.write(f"- **Cleanup Recommendations**: {total_recs}\\n")
                f.write(f"- **Analysis Duration**: {duration:.2f} seconds\\n")
            else:
                status = self.cleanup_results.get("status", "error")
                f.write(f"- **Status**: {status}\\n")
                if "error" in self.cleanup_results:
                    f.write(f"- **Error**: {self.cleanup_results['error']}\\n")

            # Detailed Test Results
            f.write("\\n## 🧪 Detailed Test Results\\n\\n")

            if test_status == "passed":
                f.write("✅ All tests passed successfully!\\n\\n")
            elif test_status == "failed":
                f.write("❌ Some tests failed. See details below:\\n\\n")
                if self.test_results.get("stderr"):
                    f.write("### Error Output\\n")
                    f.write("```\\n")
                    f.write(self.test_results["stderr"][:2000])  # Limit output
                    if len(self.test_results["stderr"]) > 2000:
                        f.write("\\n... (truncated)")
                    f.write("\\n```\\n\\n")

            # Test Coverage (if available)
            coverage_path = self.reports_dir / "coverage.json"
            if coverage_path.exists():
                try:
                    with open(coverage_path, "r") as cov_file:
                        coverage_data = json.load(cov_file)

                    f.write("### 📊 Test Coverage\\n")
                    totals = coverage_data.get("totals", {})
                    coverage_pct = totals.get("percent_covered", 0)
                    f.write(f"- **Coverage Percentage**: {coverage_pct:.1f}%\\n")
                    f.write(f"- **Lines Covered**: {totals.get('covered_lines', 0)}\\n")
                    f.write(f"- **Lines Missing**: {totals.get('missing_lines', 0)}\\n")
                    total_lines = totals.get("num_statements", 0)
                    f.write(f"- **Total Lines**: {total_lines}\\n\\n")
                except Exception as e:
                    f.write(f"- **Coverage Error**: {e}\\n\\n")

            # Detailed Cleanup Analysis
            f.write("\\n## 🧹 Detailed Cleanup Analysis\\n\\n")

            if self.cleanup_results.get("status") == "completed":
                # File Categories
                f.write("### 📁 File Categories\\n")
                structure = self.cleanup_results.get("structure_analysis", {})
                categories = structure.get("categories", {})

                for category, files in categories.items():
                    if files:
                        cat_title = category.replace("_", " ").title()
                        f.write(f"- **{cat_title}**: {len(files)} files\\n")

                # Cleanup Recommendations
                f.write("\\n### 🎯 Cleanup Recommendations\\n")
                recommendations = self.cleanup_results.get("recommendations", [])

                if recommendations:
                    # Group by priority
                    high_priority = [
                        r for r in recommendations if r.get("priority") == "high"
                    ]
                    medium_priority = [
                        r for r in recommendations if r.get("priority") == "medium"
                    ]
                    low_priority = [
                        r for r in recommendations if r.get("priority") == "low"
                    ]

                    if high_priority:
                        f.write("\\n#### 🔴 High Priority\\n")
                        for rec in high_priority:
                            cat_title = rec["category"].replace("_", " ").title()
                            f.write(f"- **{cat_title}**: {rec['description']}\\n")
                            f.write(f"  - Action: {rec['action']}\\n")
                            f.write(f"  - Safety: {rec['safety']}\\n")
                            if "files" in rec:
                                f.write(f"  - Files: {len(rec['files'])}\\n")
                            f.write("\\n")

                    if medium_priority:
                        f.write("\\n#### 🟡 Medium Priority\\n")
                        for rec in medium_priority:
                            cat_title = rec["category"].replace("_", " ").title()
                            f.write(f"- **{cat_title}**: {rec['description']}\\n")

                    if low_priority:
                        f.write("\\n#### 🟢 Low Priority\\n")
                        for rec in low_priority:
                            cat_title = rec["category"].replace("_", " ").title()
                            f.write(f"- **{cat_title}**: {rec['description']}\\n")

                else:
                    f.write("\\n✅ No cleanup recommendations - ")
                    f.write("project is well organized!\\n")

            # Action Items
            f.write("\\n## 🎯 Recommended Actions\\n\\n")

            # Test-related actions
            if test_status != "passed":
                f.write("### 🧪 Test Issues\\n")
                f.write("1. **Fix failing tests** - Address test failures ")
                f.write("before proceeding\\n")
                f.write("2. **Review test coverage** - Ensure adequate ")
                f.write("test coverage\\n")
                f.write("3. **Update test documentation** - Keep test ")
                f.write("documentation current\\n\\n")

            # Cleanup-related actions
            if self.cleanup_results.get("recommendations"):
                f.write("### 🧹 Cleanup Actions\\n")
                f.write("1. **Review high-priority recommendations** - ")
                f.write("Address critical cleanup items\\n")
                f.write("2. **Execute safe cleanup operations** - ")
                f.write("Remove obviously unused files\\n")
                f.write("3. **Archive or organize large files** - ")
                f.write("Optimize storage usage\\n")
                f.write("4. **Update project documentation** - ")
                f.write("Reflect cleaned-up structure\\n\\n")

            # Next Steps
            f.write("\\n## 🚀 Next Steps\\n\\n")
            f.write("1. **Address test failures** (if any)\\n")
            f.write("2. **Execute recommended cleanup operations**\\n")
            f.write("3. **Re-run analysis** to verify improvements\\n")
            f.write("4. **Update project documentation**\\n")
            f.write("5. **Schedule regular cleanup analysis**\\n")

            # Footer
            f.write("\\n---\\n")
            f.write("*Report generated by Enhanced Test Runner with ")
            f.write("Integrated Cleanup v2.0.0*\\n")

        logger.info(f"📋 Combined report generated: {report_path}")
        return str(report_path)

    def execute_safe_cleanup(self, dry_run: bool = True) -> Dict:
        """Execute safe cleanup operations"""
        logger.info(f"🧹 Executing safe cleanup (dry_run={dry_run})...")

        if not self.cleanup_results:
            logger.warning("No cleanup analysis available - run cleanup analysis first")
            return {"error": "No cleanup analysis available"}

        return self.cleanup_analyzer.execute_safe_cleanup(dry_run=dry_run)

    def run_full_test_suite(
        self, include_cleanup: bool = True, execute_cleanup: bool = False
    ) -> str:
        """Run the complete test suite with integrated analysis"""
        logger.info("🚀 Starting full test suite with integrated analysis...")

        start_time = time.time()

        try:
            # 1. Run unit tests
            logger.info("Step 1/5: Running unit tests...")
            self.run_unit_tests()

            # 2. Run integration tests
            logger.info("Step 2/5: Running integration tests...")
            _ = self.run_integration_tests()  # Results stored but not used

            # 3. Run cleanup analysis if requested
            if include_cleanup:
                logger.info("Step 3/5: Running cleanup analysis...")
                self.run_cleanup_analysis()
            else:
                logger.info("Step 3/5: Skipping cleanup analysis...")

            # 4. Execute safe cleanup if requested
            if execute_cleanup and self.cleanup_results:
                logger.info("Step 4/5: Executing safe cleanup...")
                cleanup_execution = self.execute_safe_cleanup(dry_run=False)
                self.cleanup_results["execution"] = cleanup_execution
            else:
                logger.info("Step 4/5: Skipping cleanup execution...")

            # 5. Generate combined report
            logger.info("Step 5/5: Generating combined report...")
            report_path = self.generate_combined_report()

            total_duration = time.time() - start_time
            logger.info(f"✅ Full test suite completed in {total_duration:.2f} seconds")
            logger.info(f"📋 Report available at: {report_path}")

            return report_path

        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            raise


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced Test Runner with Integrated Cleanup"
    )
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument(
        "--no-cleanup", action="store_true", help="Skip cleanup analysis"
    )
    parser.add_argument(
        "--execute-cleanup", action="store_true", help="Execute safe cleanup operations"
    )
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--cleanup-only", action="store_true", help="Run only cleanup analysis"
    )
    parser.add_argument(
        "--dry-run-cleanup", action="store_true", help="Show what cleanup would do"
    )

    args = parser.parse_args()

    runner = EnhancedTestRunner(args.project_root)

    try:
        if args.cleanup_only:
            # Run only cleanup analysis
            logger.info("Running cleanup analysis only...")
            runner.run_cleanup_analysis()
            report_path = runner.cleanup_analyzer.generate_comprehensive_report()
            print(f"\\n📋 Cleanup analysis complete! Report: {report_path}")

        elif args.unit_only:
            # Run only unit tests
            logger.info("Running unit tests only...")
            runner.run_unit_tests()

            # Simple test report
            test_status = runner.test_results.get("status", "unknown")
            if test_status == "passed":
                print("\\n✅ All unit tests passed!")
            else:
                print(f"\\n❌ Unit tests {test_status}")

        elif args.dry_run_cleanup:
            # Show what cleanup would do
            logger.info("Running dry-run cleanup analysis...")
            runner.run_cleanup_analysis()
            cleanup_execution = runner.execute_safe_cleanup(dry_run=True)

            print("\\n🧹 DRY RUN - Files that would be removed:")
            for file_path in cleanup_execution.get("files_removed", []):
                print(f"  ❌ {file_path}")
            space_saved = cleanup_execution.get("space_saved", 0)
            print(f"\\n💾 Total space that would be saved: {space_saved:,} bytes")

        else:
            # Run full test suite
            report_path = runner.run_full_test_suite(
                include_cleanup=not args.no_cleanup,
                execute_cleanup=args.execute_cleanup,
            )

            print(f"\\n🎉 Test suite complete!")
            print(f"📋 Full report available at: {report_path}")

            # Show quick summary
            test_status = runner.test_results.get("status", "unknown")
            test_emoji = {
                "passed": "✅",
                "failed": "❌",
                "timeout": "⏰",
                "error": "🚨",
            }.get(test_status, "❓")
            print(f"{test_emoji} Tests: {test_status}")

            if runner.cleanup_results:
                cleanup_status = runner.cleanup_results.get("status", "unknown")
                cleanup_emoji = {"completed": "✅", "error": "❌"}.get(
                    cleanup_status, "❓"
                )
                recommendations = len(runner.cleanup_results.get("recommendations", []))
                print(f"{cleanup_emoji} Cleanup: {recommendations} recommendations")

    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
