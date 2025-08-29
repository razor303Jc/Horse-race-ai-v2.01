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
            ".env",
            "horse-race-ai-backup*",
            # Python virtual environments
            "venv",
            "env",
            ".venv",
            ".env",
            "virtualenv",
            "venv*",
            "env*",
            "site-packages",
            # Conda environments
            "conda",
            "miniconda*",
            "anaconda*",
        }

    def _is_virtual_environment(self, dir_name: str) -> bool:
        """Check if a directory is a virtual environment"""
        venv_indicators = [
            "venv",
            "env",
            ".venv",
            ".env",
            "virtualenv",
            "site-packages",
            "Scripts",
            "bin",
            "lib",
        ]

        # Check for exact matches
        if dir_name in venv_indicators:
            return True

        # Check for patterns (e.g., venv39, env311)
        venv_patterns = ["venv", "env", "python"]
        for pattern in venv_patterns:
            if dir_name.startswith(pattern) and any(c.isdigit() for c in dir_name):
                return True

        return False

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
                and not self._is_virtual_environment(d)
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

            # Suppress syntax warnings for files with problematic escape sequences
            import warnings

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=SyntaxWarning)
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

        # IMPORTANT: Never recommend SQL/DB files for cleanup
        protected_extensions = {".sql", ".db", ".sqlite", ".sqlite3", ".mdb"}

        def is_protected_file(file_path: str) -> bool:
            """Check if file should be protected from cleanup"""
            path = Path(file_path)
            path_str = str(path)

            # ELEVATED PROTECTION: Critical system files (Score ≥ 95) - NEVER DELETE
            critical_never_delete = {
                "api/prediction_api.py",
                "api/ml_management_api.py",
                "tools/data_processing/daily_downloads_manager.py",
                "tools/pipeline/quick_csv_import.py",
                "tools/data_quality/csv_data_cleaner.py",
                "src/automation/human_like_downloader.py",
                "tools/analysis/integrated_cleanup_analyzer.py",
            }

            # ELEVATED PROTECTION: Important files (Score 80-94) - CAREFUL REVIEW
            important_files = {
                "config/pipeline_integration_config.json",
                "config/daily_watcher_config.json",
                "ML_CONFIG.yaml",
                "pyproject.toml",
                "AI_SCHEMA.sql",
                "database/ai_predictions_enhanced_schema.sql",
                "node-red/flows-enhanced.json",
                "node-red/working-flows.json",
                "docker/node-red/settings.js",
            }

            # Check for critical files using relative path from project root
            try:
                rel_path = str(Path(file_path).relative_to(self.project_root))
                if rel_path in critical_never_delete or rel_path in important_files:
                    return True
            except ValueError:
                # Path is outside project root, check absolute matches
                if any(critical in path_str for critical in critical_never_delete):
                    return True
                if any(important in path_str for important in important_files):
                    return True

            # SQL/DB protection
            if (
                path.suffix.lower() in protected_extensions
                or "database" in str(path).lower()
                or "queries" in str(path).lower()
                or "schema" in str(path).lower()
            ):
                return True

            # Node-RED protection logic
            if path_str := str(path).lower():
                # Always protect main Node-RED directories and important configs
                if (
                    "node-red/" in path_str
                    and not any(
                        temp in path_str
                        for temp in ["_cacache/", "_logs/", "/tmp/", "/temp/"]
                    )
                    and not (
                        "/.git/objects/" in path_str
                        or "/.git/hooks/" in path_str
                        or "/.git/logs/" in path_str
                    )
                    or path.name
                    in [
                        "docker-compose.node-red.yml",
                        "setup_node_red.sh",
                        "configure_node_red.sh",
                        "verify_node_red.sh",
                    ]
                    or (
                        path.name.startswith(".config.")
                        and "node-red" in path_str
                        and not path.name.endswith(".backup")
                    )
                ):
                    return True

            # JSON protection logic
            if path.suffix.lower() == ".json":
                return is_important_json_file(file_path)

            # CSV protection logic
            if path.suffix.lower() == ".csv":
                return is_important_csv_file(file_path)

            # Python protection logic
            if path.suffix.lower() == ".py":
                return is_important_python_file(file_path)

            return False

        def is_important_json_file(file_path: str) -> bool:
            """Check if JSON file is important and should be protected"""
            path = Path(file_path)
            path_str = str(path).lower()

            # Always protect these JSON file types
            important_patterns = [
                # Configuration files
                "config/",
                "package.json",
                "tsconfig.json",
                "package-lock.json",
                # Core application files
                "alert_config.json",
                "dashboard",
                "schedule-config.json",
                "database-config.json",
                "working-flows.json",
                # Main flow definitions (not backups)
                "core_dashboard_flows",
                "horse_racing_automation_flows.json",
                "horse_racing_python_integration_flows.json",
                "enhanced_pipeline_dashboard.json",
                # Schema and validation rules
                "schema_validation_rules.json",
                "master_schedule.json",
                # Current status files
                "daily_watcher_status.json",
            ]

            # Check if file matches important patterns
            for pattern in important_patterns:
                if pattern in path_str:
                    return True

            # Protect JSON files in certain directories
            protected_dirs = ["config", "docker", "src/web"]
            for protected_dir in protected_dirs:
                if protected_dir in path_str:
                    return True

            # Don't protect clearly temporary/timestamped files
            temporary_patterns = [
                "backup_20",  # dated backups
                "_202508",  # specific date patterns for August 2025
                "_20250817",  # old dates
                "_20250820",  # old dates
                "_20250822",  # old dates
                "_20250823",  # old dates
                "_20250824",  # old dates
                "/monitoring/cycle_metrics_",
                "/monitoring/session_summaries_",
                "/data/ml_training_data/training_features_",
                "/data/speed_analysis/speed_analysis_",
                "/data/logs/pipeline_test_report_",
                "/data/monte_carlo_results/monte_carlo_",
                "pipeline_analysis_",
                "quick_test_report_session_",
            ]

            for temp_pattern in temporary_patterns:
                if temp_pattern in path_str:
                    return False

            # Default to protecting JSON files we're unsure about
            return True

        def is_important_csv_file(file_path: str) -> bool:
            """Check if CSV file is important and should be protected"""
            path = Path(file_path)
            path_str = str(path).lower()

            # ALWAYS protect data in these critical directories
            # These contain valuable racing data needed for testing/training
            protected_data_patterns = [
                "data/daily_downloads/",  # Historical racing data
                "data/extracted_historical/",  # Processed historical data
                "data/current/",  # Current data files
                "data/training/",  # Training datasets
                "data/models/",  # Model-related data
                "data/analysis/",  # Analysis results
            ]

            # Check if in protected data directories
            for protected_pattern in protected_data_patterns:
                if protected_pattern in path_str:
                    return True

            # Protect important CSV file types regardless of location
            important_csv_patterns = [
                "horses.csv",  # Core race data
                "races.csv",  # Race information
                "jockeys_stats.csv",  # Jockey statistics
                "trainers_stats.csv",  # Trainer statistics
                "records.csv",  # Race records
                "racecard_details.csv",  # Race card data
            ]

            # Don't protect clearly temporary/backup CSV files FIRST
            # This takes priority over other patterns
            temporary_csv_patterns = [
                "/backups/",  # Backup directories
                "/temp_card_processing/",  # Temporary processing
                "/temp_extract/",  # Temporary extracts
                "horse-race-ai-backup-",  # Project backups
                "/monitoring/exports/",  # Export dumps
                "_backup_",  # Backup files
                "backup_20",  # Dated backups
                "temp_card_processing",  # Any temp processing
                "temp_extract",  # Any temp extract
            ]

            for temp_pattern in temporary_csv_patterns:
                if temp_pattern in path_str:
                    return False

            # Check file names for important patterns
            filename = path.name.lower()
            for important_pattern in important_csv_patterns:
                if important_pattern in filename:
                    return True

            # For CSV files in data/ folder, be very conservative - protect by default
            # This ensures we don't lose valuable racing data
            if "/data/" in path_str and not any(
                temp in path_str for temp in ["/backup", "/temp", "_backup", "_temp"]
            ):
                return True

            # Default to protecting CSV files we're unsure about
            # Better safe than sorry with data files
            return True

        def is_important_python_file(file_path: str) -> bool:
            """Check if Python file is important and should be protected"""
            path = Path(file_path)
            path_str = str(path).lower()
            filename = path.name.lower()

            # ALWAYS protect Python files in these critical directories
            protected_python_directories = [
                "src/",  # Source code
                "api/",  # API endpoints
                "scripts/",  # Scripts directory
                "tools/analysis/",  # Analysis tools (like this file!)
                "tools/testing/",  # Testing tools
                "tools/schema_guardian/",  # Schema protection
                "horse-bot/src/",  # Horse bot core
                "monitoring/",  # Monitoring scripts
            ]

            # Check if in protected directories
            for protected_dir in protected_python_directories:
                if protected_dir in path_str:
                    return True

            # Protect important Python file patterns by name
            important_python_patterns = [
                # Core application files
                "main.py",
                "__init__.py",
                "config.py",
                "settings.py",
                # APIs and endpoints
                "_api.py",
                "api_",
                "routes.py",
                # Engines and pipelines
                "_engine.py",
                "_pipeline.py",
                "_manager.py",
                # Models and ML
                "_model",
                "_ml_",
                "model_",
                "ml_",
                # Core functionality
                "core_",
                "_core.py",
                "engine_",
                "pipeline_",
                # Database and connections
                "connection.py",
                "database.py",
                "db_",
                # Important managers
                "manager.py",
                "handler.py",
                "processor.py",
            ]

            # Check filename patterns
            for important_pattern in important_python_patterns:
                if important_pattern in filename:
                    return True

            # Don't protect clearly test/backup/temporary Python files FIRST
            # This takes priority over other patterns
            temporary_python_patterns = [
                # Test files
                "test_",
                "_test.py",
                "/tests/",
                # Backup files
                "_backup.py",
                "backup_",
                "_old.py",
                # Temporary files
                "temp_",
                "_temp.py",
                "tmp_",
                # Debug files
                "debug_",
                "_debug.py",
                # Demo files
                "demo_",
                "_demo.py",
                # Verification scripts (these are temporary)
                "verify_",
                "_verify.py",
                # Project backups
                "horse-race-ai-backup-",
            ]

            for temp_pattern in temporary_python_patterns:
                if temp_pattern in path_str:
                    return False

            # Protect Python files in tools/ directory (but exclude temp/test files)
            if "/tools/" in path_str and not any(
                temp in path_str
                for temp in ["test_", "_test", "temp_", "_temp", "demo_", "verify_"]
            ):
                return True

            # Default to protecting Python files we're unsure about
            # Better safe than sorry with source code
            return True

        # 1. Empty files (but exclude protected files)
        if self.file_analysis.get("empty_files"):
            safe_empty_files = [
                f for f in self.file_analysis["empty_files"] if not is_protected_file(f)
            ]
            if safe_empty_files:
                recommendations.append(
                    {
                        "category": "empty_files",
                        "priority": "high",
                        "action": "remove",
                        "files": safe_empty_files,
                        "description": (
                            "Empty files that serve no purpose "
                            "(SQL/DB files excluded)"
                        ),
                        "safety": "safe",
                    }
                )

        # 2. Backup files (but exclude protected files)
        backup_files = [
            f["path"]
            for f in self.file_analysis["categories"].get("backup_files", [])
            if not is_protected_file(f["path"])
        ]
        if backup_files:
            recommendations.append(
                {
                    "category": "backup_files",
                    "priority": "high",
                    "action": "remove",
                    "files": backup_files,
                    "description": (
                        "Backup files that are no longer needed "
                        "(SQL/DB files excluded)"
                    ),
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
                    "description": (
                        "Compiled Python files (.pyc) that will be " "regenerated"
                    ),
                    "safety": "safe",
                }
            )

        # Report SQL/DB files found but explicitly exclude from cleanup
        sql_db_files = []
        json_files = {"protected": [], "potentially_unused": []}

        for category_files in self.file_analysis.get("categories", {}).values():
            for file_info in category_files:
                file_path = file_info.get("path", "")
                if is_protected_file(file_path):
                    # Check if it's JSON to categorize separately
                    if file_path.lower().endswith(".json"):
                        json_files["protected"].append(file_path)
                    else:
                        sql_db_files.append(file_path)

        # Also check for potentially unused JSON files
        for category_files in self.file_analysis.get("categories", {}).values():
            for file_info in category_files:
                file_path = file_info.get("path", "")
                is_json = file_path.lower().endswith(".json")
                if is_json and not is_protected_file(file_path):
                    json_files["potentially_unused"].append(file_path)

        if sql_db_files:
            recommendations.append(
                {
                    "category": "sql_db_files",
                    "priority": "info",
                    "action": "protect",
                    "files": sql_db_files,
                    "description": (
                        "SQL/Database files found and protected from "
                        "cleanup - manual review required"
                    ),
                    "safety": "protected",
                }
            )

        # JSON file analysis and recommendations
        if json_files["protected"]:
            recommendations.append(
                {
                    "category": "json_protected_files",
                    "priority": "info",
                    "action": "protect",
                    "files": json_files["protected"],
                    "description": (
                        "Important JSON files (config, schemas, core flows) "
                        "protected from cleanup"
                    ),
                    "safety": "protected",
                }
            )

        if json_files["potentially_unused"]:
            recommendations.append(
                {
                    "category": "json_unused_files",
                    "priority": "medium",
                    "action": "review",
                    "files": json_files["potentially_unused"],
                    "description": (
                        "JSON files that may be old/unused (timestamped data, "
                        "old backups, temporary results) - review before cleanup"
                    ),
                    "safety": "review_needed",
                }
            )

        # CSV file analysis and recommendations
        csv_files = {"protected": [], "potentially_unused": []}

        for category_files in self.file_analysis.get("categories", {}).values():
            for file_info in category_files:
                file_path = file_info.get("path", "")
                if file_path.lower().endswith(".csv"):
                    if is_protected_file(file_path):
                        csv_files["protected"].append(file_path)
                    else:
                        csv_files["potentially_unused"].append(file_path)

        if csv_files["protected"]:
            recommendations.append(
                {
                    "category": "csv_protected_files",
                    "priority": "info",
                    "action": "protect",
                    "files": csv_files["protected"],
                    "description": (
                        "Important CSV files (racing data, core datasets, "
                        "analysis results) protected from cleanup"
                    ),
                    "safety": "protected",
                }
            )

        if csv_files["potentially_unused"]:
            recommendations.append(
                {
                    "category": "csv_unused_files",
                    "priority": "low",
                    "action": "review",
                    "files": csv_files["potentially_unused"],
                    "description": (
                        "CSV files that may be duplicates/backups "
                        "(temp processing, project backups) - review carefully"
                    ),
                    "safety": "review_needed",
                }
            )

        # Python file analysis and recommendations
        python_files = {"protected": [], "potentially_unused": []}

        for category_files in self.file_analysis.get("categories", {}).values():
            for file_info in category_files:
                file_path = file_info.get("path", "")
                if file_path.lower().endswith(".py"):
                    if is_protected_file(file_path):
                        python_files["protected"].append(file_path)
                    else:
                        python_files["potentially_unused"].append(file_path)

        if python_files["protected"]:
            recommendations.append(
                {
                    "category": "python_protected_files",
                    "priority": "info",
                    "action": "protect",
                    "files": python_files["protected"],
                    "description": (
                        "Important Python files (core code, APIs, engines, "
                        "pipelines) protected from cleanup"
                    ),
                    "safety": "protected",
                }
            )

        if python_files["potentially_unused"]:
            recommendations.append(
                {
                    "category": "python_unused_files",
                    "priority": "low",
                    "action": "review",
                    "files": python_files["potentially_unused"],
                    "description": (
                        "Python files that may be test/debug/demo files "
                        "(test_, debug_, demo_, verify_ files) - review carefully"
                    ),
                    "safety": "review_needed",
                }
            )

        # 4. Node-RED files analysis
        node_red_files = {"protected": [], "cache_temp": []}

        all_files = []
        for category in self.file_analysis.get("categories", {}).values():
            if isinstance(category, list):
                all_files.extend([item["path"] for item in category])

        for file_path in all_files:
            if "node-red" in file_path.lower():
                # Exclude cache and temporary files
                if any(
                    temp in file_path.lower()
                    for temp in ["_cacache/", "_logs/", "/.git/", "/tmp/", "/temp/"]
                ):
                    node_red_files["cache_temp"].append(file_path)
                else:
                    node_red_files["protected"].append(file_path)

        # Check root-level Node-RED files
        node_red_root_files = [
            "docker-compose.node-red.yml",
            "setup_node_red.sh",
            "configure_node_red.sh",
            "verify_node_red.sh",
        ]
        for nr_file in node_red_root_files:
            if (self.project_root / nr_file).exists():
                protected_names = [
                    f.split("/")[-1] for f in node_red_files["protected"]
                ]
                if nr_file not in protected_names:
                    node_red_files["protected"].append(nr_file)

        if node_red_files["protected"]:
            recommendations.append(
                {
                    "category": "node_red_protected_files",
                    "priority": "info",
                    "action": "protect",
                    "files": node_red_files["protected"],
                    "description": (
                        "Node-RED configuration, flows, and setup files "
                        "protected from cleanup (automation system critical)"
                    ),
                    "safety": "protected",
                }
            )

        if node_red_files["cache_temp"]:
            recommendations.append(
                {
                    "category": "node_red_cache_files",
                    "priority": "low",
                    "action": "review",
                    "files": node_red_files["cache_temp"],
                    "description": (
                        "Node-RED cache and temporary files "
                        "(npm cache, logs, git repos) - safe to remove"
                    ),
                    "safety": "safe_to_remove",
                }
            )

        # 5. Unused Python functions
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

        # 5. Large files (but exclude protected files)
        if self.file_analysis.get("large_files"):
            safe_large_files = [
                f
                for f in self.file_analysis["large_files"]
                if not is_protected_file(f["path"])
            ]
            if safe_large_files:
                recommendations.append(
                    {
                        "category": "large_files",
                        "priority": "medium",
                        "action": "review",
                        "files": [f["path"] for f in safe_large_files],
                        "description": (
                            "Large files that may need optimization "
                            "or archival (SQL/DB files excluded)"
                        ),
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

            # Important note about exclusions
            f.write("## ⚠️ Important Notes\\n\\n")
            f.write("- **SQL/Database Files Excluded**: SQL, DB, and database files ")
            f.write("(.sql, .db, .sqlite, etc.) are excluded from cleanup analysis ")
            f.write("as they require special handling and domain expertise.\\n")
            f.write(
                "- **209 SQL files found** in project - these need separate review.\\n\\n"
            )

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
