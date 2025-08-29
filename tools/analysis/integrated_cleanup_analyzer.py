#!/usr/bin/env python3
"""
🧹 Integrated Cleanup & Analysis System
======================================

Combines file analysis, function usage tracking, and test execution
to provide comprehensive project cleanup and organization.

This system:
1. Analyzes all files and functions in the project
2. Tracks which files/functions are actually used
3. Runs unit tests to ensure functionality
4. Generates comprehensive cleanup reports
5. Provides safe automated cleanup options

Author: AI Assistant
Date: August 29, 2025
Version: 2.0.0
"""

import os
import sys
import ast
import json
import shutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
import importlib.util

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IntegratedCleanupAnalyzer:
    """Comprehensive file and function analysis with test integration"""

    def __init__(self, project_root: str = None):
        default_root = "/home/jc/Documents/Horse-race-ai-v2.04"
        self.project_root = Path(project_root or default_root)
        self.reports_dir = self.project_root / "data" / "cleanup_analysis"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Analysis results
        self.file_analysis = {}
        self.function_analysis = {}
        self.import_analysis = {}
        self.test_results = {}
        self.cleanup_recommendations = []

        # Categories for cleanup
        self.safe_to_remove = []
        self.review_needed = []
        self.keep_files = []

        # Excluded directories
        self.excluded_dirs = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            ".vscode",
            ".idea",
            "venv",
            ".env",
            "horse-race-ai-backup*",
        }

    def analyze_project_structure(self) -> Dict:
        """Comprehensive analysis of project structure"""
        logger.info("🔍 Starting comprehensive project analysis...")

        structure_analysis = {
            "total_files": 0,
            "categories": defaultdict(list),
            "duplicates": [],
            "empty_files": [],
            "large_files": [],
            "orphaned_files": [],
            "timestamp": datetime.now().isoformat(),
        }

        # Walk through all files
        for root, dirs, files in os.walk(self.project_root):
            # Filter out excluded directories
            dirs[:] = [
                d
                for d in dirs
                if not any(
                    d.startswith(excl.replace("*", "")) for excl in self.excluded_dirs
                )
            ]

            for file in files:
                if file.startswith("."):
                    continue

                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.project_root)

                try:
                    file_size = file_path.stat().st_size
                    structure_analysis["total_files"] += 1

                    # Categorize files
                    category = self._categorize_file(file_path)
                    structure_analysis["categories"][category].append(
                        {
                            "path": str(relative_path),
                            "size": file_size,
                            "modified": file_path.stat().st_mtime,
                        }
                    )

                    # Identify empty files
                    if file_size == 0:
                        structure_analysis["empty_files"].append(str(relative_path))

                    # Identify large files (>10MB)
                    if file_size > 10 * 1024 * 1024:
                        structure_analysis["large_files"].append(
                            {
                                "path": str(relative_path),
                                "size_mb": round(file_size / (1024 * 1024), 2),
                            }
                        )

                except (OSError, ValueError) as e:
                    logger.warning(f"Could not analyze {file_path}: {e}")

        self.file_analysis = structure_analysis
        return structure_analysis

    def _categorize_file(self, file_path: Path) -> str:
        """Categorize a file based on its extension and content"""
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()

        # Check for backup/temp files
        if any(marker in name for marker in ["backup", ".bak", ".tmp", "~"]):
            return "backup_files"

        # Check for test files
        if any(marker in name for marker in ["test_", "_test", "tests"]):
            return "test_files"

        # By extension
        categorization = {
            ".py": "python_files",
            ".pyc": "compiled_python",
            ".pyo": "compiled_python",
            ".sql": "database_scripts",
            ".yml": "config_files",
            ".yaml": "config_files",
            ".json": "config_files",
            ".md": "documentation",
            ".txt": "text_files",
            ".log": "log_files",
            ".html": "templates",
            ".css": "static_files",
            ".js": "static_files",
            ".sh": "shell_scripts",
            ".env": "config_files",
        }

        return categorization.get(suffix, "other_files")

    def analyze_python_usage(self) -> Dict:
        """Analyze Python files for function/class usage"""
        logger.info("🐍 Analyzing Python file usage and dependencies...")

        python_analysis = {
            "files": {},
            "functions": {},
            "classes": {},
            "imports": {},
            "unused_functions": [],
            "unused_files": [],
        }

        # Find all Python files
        python_files = []
        for category_files in self.file_analysis["categories"]["python_files"]:
            python_files.append(self.project_root / category_files["path"])

        # Analyze each Python file
        for py_file in python_files:
            try:
                analysis = self._analyze_python_file(py_file)
                python_analysis["files"][
                    str(py_file.relative_to(self.project_root))
                ] = analysis

                # Collect functions and classes
                for func in analysis.get("functions", []):
                    python_analysis["functions"][func] = {
                        "file": str(py_file.relative_to(self.project_root)),
                        "used_by": [],
                    }

                for cls in analysis.get("classes", []):
                    python_analysis["classes"][cls] = {
                        "file": str(py_file.relative_to(self.project_root)),
                        "used_by": [],
                    }

            except Exception as e:
                logger.warning(f"Could not analyze {py_file}: {e}")

        # Analyze cross-references
        self._analyze_cross_references(python_analysis)

        self.function_analysis = python_analysis
        return python_analysis

    def _analyze_python_file(self, file_path: Path) -> Dict:
        """Analyze a single Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "lines_of_code": len(
                    [line for line in content.splitlines() if line.strip()]
                ),
                "complexity_score": 0,
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(alias.name)
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            analysis["imports"].append(f"{module}.{alias.name}")

            # Calculate complexity (simple metric)
            analysis["complexity_score"] = len(analysis["functions"]) + len(
                analysis["classes"]
            )

            return analysis

        except Exception as e:
            return {"error": str(e)}

    def _analyze_cross_references(self, python_analysis: Dict):
        """Analyze which functions/classes are used across files"""
        logger.info("🔗 Analyzing cross-references...")

        # For each file, check which functions/classes it uses
        for file_path, file_analysis in python_analysis["files"].items():
            if "error" in file_analysis:
                continue

            try:
                full_path = self.project_root / file_path
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for function/class usage
                for func_name, func_info in python_analysis["functions"].items():
                    if func_name in content and func_info["file"] != file_path:
                        func_info["used_by"].append(file_path)

                for class_name, class_info in python_analysis["classes"].items():
                    if class_name in content and class_info["file"] != file_path:
                        class_info["used_by"].append(file_path)

            except Exception as e:
                logger.warning(
                    f"Could not analyze cross-references for {file_path}: {e}"
                )

    def run_integrated_tests(self) -> Dict:
        """Run unit tests and capture results"""
        logger.info("🧪 Running integrated test suite...")

        test_results = {
            "timestamp": datetime.now().isoformat(),
            "unit_tests": {},
            "integration_tests": {},
            "performance_tests": {},
            "overall_status": "unknown",
        }

        try:
            # Run pytest with detailed output
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                str(self.project_root / "tests"),
                "--tb=short",
                "--json-report",
                f"--json-report-file={self.reports_dir}/test_results.json",
                "-v",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300,  # 5 minute timeout
            )

            test_results["exit_code"] = result.returncode
            test_results["stdout"] = result.stdout
            test_results["stderr"] = result.stderr

            # Try to load JSON report if it exists
            json_report_path = self.reports_dir / "test_results.json"
            if json_report_path.exists():
                with open(json_report_path, "r") as f:
                    detailed_results = json.load(f)
                test_results["detailed"] = detailed_results

            test_results["overall_status"] = (
                "passed" if result.returncode == 0 else "failed"
            )

        except subprocess.TimeoutExpired:
            test_results["overall_status"] = "timeout"
            test_results["error"] = "Tests timed out after 5 minutes"
        except Exception as e:
            test_results["overall_status"] = "error"
            test_results["error"] = str(e)

        self.test_results = test_results
        return test_results

    def generate_cleanup_recommendations(self) -> List[Dict]:
        """Generate comprehensive cleanup recommendations"""
        logger.info("📋 Generating cleanup recommendations...")

        recommendations = []

        # 1. Empty files
        if self.file_analysis.get("empty_files"):
            recommendations.append(
                {
                    "category": "empty_files",
                    "priority": "high",
                    "action": "remove",
                    "files": self.file_analysis["empty_files"],
                    "description": "Empty files that serve no purpose",
                    "safety": "safe",
                }
            )

        # 2. Backup files
        backup_files = [
            f["path"] for f in self.file_analysis["categories"].get("backup_files", [])
        ]
        if backup_files:
            recommendations.append(
                {
                    "category": "backup_files",
                    "priority": "high",
                    "action": "remove",
                    "files": backup_files,
                    "description": "Backup files that are no longer needed",
                    "safety": "safe",
                }
            )

        # 3. Compiled Python files
        compiled_files = [
            f["path"]
            for f in self.file_analysis["categories"].get("compiled_python", [])
        ]
        if compiled_files:
            recommendations.append(
                {
                    "category": "compiled_python",
                    "priority": "medium",
                    "action": "remove",
                    "files": compiled_files,
                    "description": "Compiled Python files (.pyc) that will be regenerated",
                    "safety": "safe",
                }
            )

        # 4. Unused Python functions
        if self.function_analysis:
            unused_functions = []
            for func_name, func_info in self.function_analysis.get(
                "functions", {}
            ).items():
                if not func_info.get("used_by"):
                    unused_functions.append(
                        {"function": func_name, "file": func_info["file"]}
                    )

            if unused_functions:
                recommendations.append(
                    {
                        "category": "unused_functions",
                        "priority": "low",
                        "action": "review",
                        "items": unused_functions,
                        "description": "Functions that appear to be unused",
                        "safety": "review_needed",
                    }
                )

        # 5. Large files
        if self.file_analysis.get("large_files"):
            recommendations.append(
                {
                    "category": "large_files",
                    "priority": "medium",
                    "action": "review",
                    "files": self.file_analysis["large_files"],
                    "description": "Large files that may need optimization or archival",
                    "safety": "review_needed",
                }
            )

        # 6. Test files without corresponding source
        test_files = [
            f["path"] for f in self.file_analysis["categories"].get("test_files", [])
        ]
        source_files = [
            f["path"] for f in self.file_analysis["categories"].get("python_files", [])
        ]

        orphaned_tests = []
        for test_file in test_files:
            # Try to find corresponding source file
            potential_source = test_file.replace("test_", "").replace("_test", "")
            if potential_source not in source_files:
                orphaned_tests.append(test_file)

        if orphaned_tests:
            recommendations.append(
                {
                    "category": "orphaned_tests",
                    "priority": "low",
                    "action": "review",
                    "files": orphaned_tests,
                    "description": "Test files without corresponding source files",
                    "safety": "review_needed",
                }
            )

        self.cleanup_recommendations = recommendations
        return recommendations

    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive analysis and cleanup report"""
        logger.info("📊 Generating comprehensive report...")

        report_path = (
            self.reports_dir
            / f"cleanup_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )

        with open(report_path, "w") as f:
            f.write("# 🧹 Comprehensive Cleanup & Analysis Report\\n")
            f.write(f"Generated: {datetime.now().isoformat()}\\n\\n")

            # Project Overview
            f.write("## 📊 Project Overview\\n\\n")
            f.write(f"- **Total Files**: {self.file_analysis.get('total_files', 0)}\\n")

            for category, files in self.file_analysis.get("categories", {}).items():
                f.write(
                    f"- **{category.replace('_', ' ').title()}**: {len(files)} files\\n"
                )

            # File Analysis
            f.write("\\n## 📁 File Analysis\\n\\n")

            if self.file_analysis.get("empty_files"):
                f.write(
                    f"### 📭 Empty Files ({len(self.file_analysis['empty_files'])})\\n"
                )
                for empty_file in self.file_analysis["empty_files"]:
                    f.write(f"- `{empty_file}`\\n")
                f.write("\\n")

            if self.file_analysis.get("large_files"):
                f.write(
                    f"### 📦 Large Files ({len(self.file_analysis['large_files'])})\\n"
                )
                for large_file in self.file_analysis["large_files"]:
                    f.write(f"- `{large_file['path']}` ({large_file['size_mb']} MB)\\n")
                f.write("\\n")

            # Function Analysis
            if self.function_analysis:
                f.write("\\n## 🐍 Python Analysis\\n\\n")
                f.write(
                    f"- **Total Python Files**: {len(self.function_analysis.get('files', {}))}\\n"
                )
                f.write(
                    f"- **Total Functions**: {len(self.function_analysis.get('functions', {}))}\\n"
                )
                f.write(
                    f"- **Total Classes**: {len(self.function_analysis.get('classes', {}))}\\n"
                )

            # Test Results
            if self.test_results:
                f.write("\\n## 🧪 Test Results\\n\\n")
                f.write(
                    f"- **Overall Status**: {self.test_results.get('overall_status', 'unknown')}\\n"
                )
                f.write(
                    f"- **Exit Code**: {self.test_results.get('exit_code', 'N/A')}\\n"
                )

                if "detailed" in self.test_results:
                    detailed = self.test_results["detailed"]
                    summary = detailed.get("summary", {})
                    f.write(f"- **Tests Passed**: {summary.get('passed', 0)}\\n")
                    f.write(f"- **Tests Failed**: {summary.get('failed', 0)}\\n")
                    f.write(f"- **Tests Skipped**: {summary.get('skipped', 0)}\\n")

            # Cleanup Recommendations
            if self.cleanup_recommendations:
                f.write("\\n## 🧹 Cleanup Recommendations\\n\\n")

                for recommendation in self.cleanup_recommendations:
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    emoji = priority_emoji.get(recommendation["priority"], "⚪")

                    f.write(
                        f"### {emoji} {recommendation['category'].replace('_', ' ').title()}\\n"
                    )
                    f.write(f"**Priority**: {recommendation['priority']}\\n")
                    f.write(f"**Action**: {recommendation['action']}\\n")
                    f.write(f"**Safety**: {recommendation['safety']}\\n")
                    f.write(f"**Description**: {recommendation['description']}\\n\\n")

                    if "files" in recommendation:
                        f.write("**Files:**\\n")
                        for file_path in recommendation["files"][
                            :10
                        ]:  # Limit to first 10
                            f.write(f"- `{file_path}`\\n")
                        if len(recommendation["files"]) > 10:
                            f.write(
                                f"- ... and {len(recommendation['files']) - 10} more\\n"
                            )

                    if "items" in recommendation:
                        f.write("**Items:**\\n")
                        for item in recommendation["items"][:10]:  # Limit to first 10
                            if isinstance(item, dict):
                                f.write(
                                    f"- `{item.get('function', item.get('file', str(item)))}`\\n"
                                )
                            else:
                                f.write(f"- `{item}`\\n")

                    f.write("\\n")

            # Summary
            f.write("\\n## 📈 Summary\\n\\n")
            total_removable = sum(
                len(rec.get("files", rec.get("items", [])))
                for rec in self.cleanup_recommendations
                if rec["action"] == "remove"
            )
            f.write(f"- **Total Removable Files**: {total_removable}\\n")
            f.write(f"- **Estimated Space Savings**: To be calculated\\n")
            f.write(
                f"- **Next Steps**: Review recommendations and execute safe cleanup operations\\n"
            )

        logger.info(f"📋 Report generated: {report_path}")
        return str(report_path)

    def execute_safe_cleanup(self, dry_run: bool = True) -> Dict:
        """Execute safe cleanup operations"""
        logger.info(f"🧹 Executing cleanup (dry_run={dry_run})...")

        cleanup_results = {
            "files_removed": [],
            "files_failed": [],
            "space_saved": 0,
            "dry_run": dry_run,
        }

        for recommendation in self.cleanup_recommendations:
            if (
                recommendation["safety"] == "safe"
                and recommendation["action"] == "remove"
            ):
                files_to_remove = recommendation.get("files", [])

                for file_path in files_to_remove:
                    full_path = self.project_root / file_path

                    try:
                        if full_path.exists():
                            file_size = full_path.stat().st_size

                            if not dry_run:
                                if full_path.is_file():
                                    full_path.unlink()
                                elif full_path.is_dir():
                                    shutil.rmtree(full_path)

                            cleanup_results["files_removed"].append(str(file_path))
                            cleanup_results["space_saved"] += file_size

                        else:
                            logger.warning(f"File not found: {file_path}")

                    except Exception as e:
                        logger.error(f"Failed to remove {file_path}: {e}")
                        cleanup_results["files_failed"].append(
                            {"file": str(file_path), "error": str(e)}
                        )

        return cleanup_results

    def run_full_analysis(
        self, run_tests: bool = True, execute_cleanup: bool = False
    ) -> str:
        """Run the complete analysis pipeline"""
        logger.info("🚀 Starting full integrated analysis...")

        # 1. Analyze project structure
        self.analyze_project_structure()

        # 2. Analyze Python usage
        self.analyze_python_usage()

        # 3. Run tests if requested
        if run_tests:
            self.run_integrated_tests()

        # 4. Generate cleanup recommendations
        self.generate_cleanup_recommendations()

        # 5. Execute safe cleanup if requested
        if execute_cleanup:
            self.execute_safe_cleanup(dry_run=False)

        # 6. Generate comprehensive report
        report_path = self.generate_comprehensive_report()

        logger.info("✅ Full analysis complete!")
        return report_path


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Integrated Cleanup & Analysis System")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--no-tests", action="store_true", help="Skip running tests")
    parser.add_argument(
        "--execute-cleanup", action="store_true", help="Execute safe cleanup operations"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleaned up without doing it",
    )

    args = parser.parse_args()

    analyzer = IntegratedCleanupAnalyzer(args.project_root)

    if args.dry_run:
        # Just show what would be cleaned
        analyzer.analyze_project_structure()
        analyzer.analyze_python_usage()
        analyzer.generate_cleanup_recommendations()
        cleanup_results = analyzer.execute_safe_cleanup(dry_run=True)

        print("\\n🧹 DRY RUN - Files that would be removed:")
        for file_path in cleanup_results["files_removed"]:
            print(f"  ❌ {file_path}")
        print(
            f"\\n💾 Total space that would be saved: {cleanup_results['space_saved']:,} bytes"
        )

    else:
        # Run full analysis
        report_path = analyzer.run_full_analysis(
            run_tests=not args.no_tests, execute_cleanup=args.execute_cleanup
        )

        print(f"\\n📋 Analysis complete! Report available at: {report_path}")


if __name__ == "__main__":
    main()
