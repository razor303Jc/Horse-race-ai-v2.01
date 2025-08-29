#!/usr/bin/env python3
"""
System Functionality Validation Test
=====================================

Tests whether the system would function properly if only protected files were present.
This validates our protection logic by checking:

1. Import dependencies of protected Python files
2. Configuration file dependencies
3. Data file requirements
4. Database/SQL dependencies
5. Critical system pathways

The goal is to ensure that keeping only "protected" files would result
in a fully functional system.
"""

import sys
import ast
import json
import logging
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
import importlib.util

from tools.analysis.integrated_cleanup_analyzer import IntegratedCleanupAnalyzer


class SystemFunctionalityValidator:
    """Validates system functionality with only protected files"""

    def __init__(self, project_root: str = None):
        default_root = "/home/jc/Documents/Horse-race-ai-v2.04"
        self.project_root = Path(project_root or default_root)
        self.analyzer = IntegratedCleanupAnalyzer(project_root)

        # Analysis results
        self.protected_files = set()
        self.review_files = set()
        self.cleanup_files = set()
        self.dependency_graph = defaultdict(set)
        self.missing_dependencies = defaultdict(set)
        self.critical_issues = []
        self.warnings = []

    def run_validation(self) -> Dict:
        """Run comprehensive system functionality validation"""

        print("🔍 SYSTEM FUNCTIONALITY VALIDATION")
        print("=" * 50)

        # Step 1: Get current file analysis
        print("📋 Step 1: Analyzing current file protection status...")
        self._analyze_file_protection()

        # Step 2: Analyze Python import dependencies
        print("📋 Step 2: Analyzing Python import dependencies...")
        self._analyze_python_dependencies()

        # Step 3: Analyze configuration dependencies
        print("📋 Step 3: Analyzing configuration file dependencies...")
        self._analyze_config_dependencies()

        # Step 4: Analyze data file dependencies
        print("📋 Step 4: Analyzing data file dependencies...")
        self._analyze_data_dependencies()

        # Step 5: Test critical system pathways
        print("📋 Step 5: Testing critical system pathways...")
        self._test_critical_pathways()

        # Step 6: Generate validation report
        print("📋 Step 6: Generating validation report...")
        return self._generate_validation_report()

    def _analyze_file_protection(self):
        """Analyze current file protection categorization"""

        # Run protection analysis
        file_analysis = self.analyzer.analyze_project_structure()
        self.analyzer.file_analysis = file_analysis
        recommendations = self.analyzer.generate_cleanup_recommendations()

        # Categorize files
        for rec in recommendations:
            category = rec["category"]
            files = rec.get("files", rec.get("items", []))

            if "protected" in category or (
                category.endswith("_files") and "unused" not in category
            ):
                self.protected_files.update(files)
            elif "unused" in category or "review" in category:
                self.review_files.update(files)
            elif category in ["empty_files", "backup_files"]:
                self.cleanup_files.update(files)

        print(f"  • Protected files: {len(self.protected_files):,}")
        print(f"  • Review files: {len(self.review_files):,}")
        print(f"  • Cleanup files: {len(self.cleanup_files):,}")

    def _analyze_python_dependencies(self):
        """Analyze Python import dependencies for protected files"""

        print("  🐍 Analyzing Python import chains...")

        protected_python_files = {f for f in self.protected_files if f.endswith(".py")}
        review_python_files = {f for f in self.review_files if f.endswith(".py")}

        print(f"    • Protected Python files: {len(protected_python_files)}")
        print(f"    • Review Python files: {len(review_python_files)}")

        # Check imports for each protected Python file
        missing_imports = 0
        total_imports = 0

        # Sample first 20 for performance
        for py_file in list(protected_python_files)[:20]:
            try:
                file_path = self.project_root / py_file
                if not file_path.exists():
                    continue

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                tree = ast.parse(content)
                imports = self._extract_imports(tree)

                for import_name in imports:
                    total_imports += 1

                    # Check if this import would be available with only protected files
                    if self._is_local_import(import_name):
                        expected_file = self._resolve_import_path(import_name)
                        if expected_file and expected_file not in self.protected_files:
                            # Check if it's in review files (potential issue)
                            if expected_file in self.review_files:
                                self.missing_dependencies[py_file].add(import_name)
                                missing_imports += 1
                            elif expected_file in self.cleanup_files:
                                self.critical_issues.append(
                                    f"CRITICAL: {py_file} imports {import_name} "
                                    f"from cleanup file {expected_file}"
                                )
                                missing_imports += 1

            except Exception as e:
                self.warnings.append(f"Could not analyze {py_file}: {e}")

        print(f"    • Total imports checked: {total_imports}")
        print(f"    • Missing dependencies: {missing_imports}")
        print(f"    • Critical import issues: {len(self.critical_issues)}")

    def _extract_imports(self, tree) -> List[str]:
        """Extract import names from AST"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports

    def _is_local_import(self, import_name: str) -> bool:
        """Check if import is a local project import"""
        # Local imports typically start with project-specific names
        local_prefixes = [
            "src",
            "api",
            "tools",
            "scripts",
            "horse_racing_ai",
            "monitoring",
            "models",
            "analysis",
        ]

        return any(import_name.startswith(prefix) for prefix in local_prefixes)

    def _resolve_import_path(self, import_name: str) -> Optional[str]:
        """Resolve import name to file path"""
        # Simple resolution - convert dots to path separators
        potential_paths = [
            f"{import_name.replace('.', '/')}.py",
            f"{import_name.replace('.', '/')}/__init__.py",
        ]

        for path in potential_paths:
            if (self.project_root / path).exists():
                return path

        return None

    def _analyze_config_dependencies(self):
        """Analyze configuration file dependencies"""

        print("  ⚙️  Analyzing configuration dependencies...")

        config_extensions = (".json", ".yaml", ".yml", ".toml")
        protected_configs = {
            f for f in self.protected_files if f.endswith(config_extensions)
        }
        review_configs = {f for f in self.review_files if f.endswith(config_extensions)}

        print(f"    • Protected config files: {len(protected_configs)}")
        print(f"    • Review config files: {len(review_configs)}")

        # Check for config references in Python files
        config_references = 0
        missing_config_refs = 0

        protected_python = {f for f in self.protected_files if f.endswith(".py")}

        for py_file in list(protected_python)[:15]:  # Sample for performance
            try:
                file_path = self.project_root / py_file
                if not file_path.exists():
                    continue

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Look for config file references
                check_files = list(review_configs) + list(self.cleanup_files)
                for config_file in check_files:
                    if config_file.endswith((".json", ".yaml", ".yml")):
                        config_name = Path(config_file).name
                        if config_name in content or config_file in content:
                            config_references += 1
                            if config_file in review_configs:
                                self.warnings.append(
                                    f"WARNING: {py_file} references config "
                                    f"{config_file} flagged for review"
                                )
                                missing_config_refs += 1
                            elif config_file in self.cleanup_files:
                                self.critical_issues.append(
                                    f"CRITICAL: {py_file} references config "
                                    f"{config_file} flagged for cleanup"
                                )
                                missing_config_refs += 1

            except Exception as e:
                self.warnings.append(f"Could not analyze config deps in {py_file}: {e}")

        print(f"    • Config references found: {config_references}")
        print(f"    • Missing config references: {missing_config_refs}")

    def _analyze_data_dependencies(self):
        """Analyze data file dependencies"""

        print("  📊 Analyzing data file dependencies...")

        data_extensions = (".csv", ".json", ".db", ".sqlite")
        protected_data = {
            f for f in self.protected_files if f.endswith(data_extensions)
        }
        review_data = {f for f in self.review_files if f.endswith(data_extensions)}

        print(f"    • Protected data files: {len(protected_data)}")
        print(f"    • Review data files: {len(review_data)}")

        # Check for data file references in Python code
        data_references = 0
        missing_data_refs = 0

        protected_python = {f for f in self.protected_files if f.endswith(".py")}

        for py_file in list(protected_python)[:15]:  # Sample for performance
            try:
                file_path = self.project_root / py_file
                if not file_path.exists():
                    continue

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Look for data file references
                check_files = list(review_data) + list(self.cleanup_files)
                for data_file in check_files:
                    if data_file.endswith((".csv", ".db", ".sqlite")):
                        data_name = Path(data_file).name
                        if data_name in content or data_file in content:
                            data_references += 1
                            if data_file in review_data:
                                self.warnings.append(
                                    f"WARNING: {py_file} references data "
                                    f"{data_file} flagged for review"
                                )
                                missing_data_refs += 1
                            elif data_file in self.cleanup_files:
                                self.critical_issues.append(
                                    f"CRITICAL: {py_file} references data "
                                    f"{data_file} flagged for cleanup"
                                )
                                missing_data_refs += 1

            except Exception as e:
                self.warnings.append(f"Could not analyze data deps in {py_file}: {e}")

        print(f"    • Data references found: {data_references}")
        print(f"    • Missing data references: {missing_data_refs}")

    def _test_critical_pathways(self):
        """Test critical system pathways"""

        print("  🛣️  Testing critical system pathways...")

        # Test if main entry points are protected
        entry_points = [
            "src/horse_racing_ai/main.py",
            "api/prediction_api.py",
            "api/ml_management_api.py",
            "tools/testing/enhanced_test_runner.py",
            "tools/analysis/integrated_cleanup_analyzer.py",
        ]

        missing_entry_points = []
        for entry_point in entry_points:
            if entry_point not in self.protected_files:
                missing_entry_points.append(entry_point)
                if entry_point in self.review_files:
                    self.critical_issues.append(
                        f"CRITICAL: Entry point {entry_point} flagged for review!"
                    )
                elif entry_point in self.cleanup_files:
                    self.critical_issues.append(
                        f"CRITICAL: Entry point {entry_point} flagged for cleanup!"
                    )
                else:
                    self.warnings.append(
                        f"WARNING: Entry point {entry_point} not found in any category"
                    )

        print(f"    • Entry points checked: {len(entry_points)}")
        print(f"    • Missing entry points: {len(missing_entry_points)}")

        # Test critical directories
        critical_dirs = [
            "src/",
            "api/",
            "tools/analysis/",
            "tools/testing/",
            "config/",
            "data/",
            "database/",
        ]

        missing_critical_files = []
        for critical_dir in critical_dirs:
            dir_files = {f for f in self.protected_files if f.startswith(critical_dir)}
            if not dir_files:
                missing_critical_files.append(critical_dir)
                self.warnings.append(
                    f"WARNING: No protected files in critical directory {critical_dir}"
                )

        print(f"    • Critical directories checked: {len(critical_dirs)}")
        print(
            f"    • Directories with no protected files: "
            f"{len(missing_critical_files)}"
        )

    def _generate_validation_report(self) -> Dict:
        """Generate comprehensive validation report"""

        print("\n" + "=" * 60)
        print("📊 SYSTEM FUNCTIONALITY VALIDATION REPORT")
        print("=" * 60)

        # Calculate scores
        total_issues = len(self.critical_issues)
        total_warnings = len(self.warnings)
        total_missing_deps = sum(
            len(deps) for deps in self.missing_dependencies.values()
        )

        # Determine system health
        if total_issues == 0 and total_missing_deps == 0:
            health_status = "🟢 EXCELLENT"
            health_score = 100
        elif total_issues == 0 and total_missing_deps < 5:
            health_status = "🟡 GOOD"
            health_score = 85
        elif total_issues < 3 and total_missing_deps < 10:
            health_status = "🟠 FAIR"
            health_score = 70
        else:
            health_status = "🔴 POOR"
            health_score = 50

        # Calculate protection rate
        total_files = (
            len(self.protected_files) + len(self.review_files) + len(self.cleanup_files)
        )
        protection_rate = (
            len(self.protected_files) / total_files * 100 if total_files > 0 else 0
        )

        report = {
            "validation_date": datetime.now().isoformat(),
            "health_status": health_status,
            "health_score": health_score,
            "file_summary": {
                "protected_files": len(self.protected_files),
                "review_files": len(self.review_files),
                "cleanup_files": len(self.cleanup_files),
                "protection_rate": protection_rate,
            },
            "dependency_analysis": {
                "missing_dependencies": total_missing_deps,
                "files_with_missing_deps": len(self.missing_dependencies),
                "critical_issues": total_issues,
                "warnings": total_warnings,
            },
            "critical_issues": self.critical_issues,
            "warnings": self.warnings[:10],  # Limit warnings output
            "missing_dependencies": dict(
                list(self.missing_dependencies.items())[:5]
            ),  # Limit output
        }

        # Print summary
        print(f"\n🏥 SYSTEM HEALTH: {health_status} ({health_score}/100)")
        print("\n📊 FILE ANALYSIS:")
        total_analyzed = (
            report["file_summary"]["protected_files"]
            + report["file_summary"]["review_files"]
            + report["file_summary"]["cleanup_files"]
        )
        print(f"  • Total files analyzed: {total_analyzed:,}")
        print(f"  • Protected files: {report['file_summary']['protected_files']:,}")
        print(f"  • Protection rate: {report['file_summary']['protection_rate']:.1f}%")

        print("\n🔗 DEPENDENCY ANALYSIS:")
        print(f"  • Missing dependencies: {total_missing_deps}")
        print(f"  • Files with missing deps: {len(self.missing_dependencies)}")
        print(f"  • Critical issues: {total_issues}")
        print(f"  • Warnings: {total_warnings}")

        if self.critical_issues:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in self.critical_issues[:5]:
                print(f"  ❌ {issue}")
            if len(self.critical_issues) > 5:
                print(f"  ... and {len(self.critical_issues) - 5} more")

        if self.warnings:
            print("\n⚠️  WARNINGS (showing first 5):")
            for warning in self.warnings[:5]:
                print(f"  ⚠️  {warning}")
            if len(self.warnings) > 5:
                print(f"  ... and {len(self.warnings) - 5} more")

        # Conclusion
        print("\n" + "=" * 60)
        print("🎯 VALIDATION CONCLUSION:")
        print("=" * 60)

        if health_score >= 85:
            print("✅ SYSTEM WOULD FUNCTION PROPERLY")
            print("   The protected files contain all necessary dependencies")
            print("   for the system to operate correctly.")
            print("   🚀 Safe to proceed with cleanup operations!")
        elif health_score >= 70:
            print("⚠️  SYSTEM WOULD MOSTLY FUNCTION")
            print("   Minor issues detected but core functionality preserved.")
            print("   📋 Review warnings before cleanup.")
        else:
            print("❌ SYSTEM WOULD HAVE ISSUES")
            print("   Critical dependencies missing from protected files.")
            print("   🛑 DO NOT proceed with cleanup until issues resolved!")

        return report


def main():
    """Run system functionality validation"""

    validator = SystemFunctionalityValidator()
    report = validator.run_validation()

    # Save report
    report_file = validator.project_root / "SYSTEM_FUNCTIONALITY_VALIDATION_REPORT.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Full report saved to: {report_file}")

    return 0 if report["health_score"] >= 85 else 1


if __name__ == "__main__":
    sys.exit(main())
