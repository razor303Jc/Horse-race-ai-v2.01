#!/usr/bin/env python3
"""
Node-RED Dependency Analysis
=============================

Analyzes Node-RED setup to identify:
1. Node-RED configuration files and their protection status
2. Python scripts triggered by Node-RED flows
3. Dependencies and file references
4. Protection gaps that could break Node-RED automation

This ensures Node-RED workflows remain functional after cleanup operations.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from tools.analysis.integrated_cleanup_analyzer import IntegratedCleanupAnalyzer


class NodeRedDependencyAnalyzer:
    """Analyzes Node-RED dependencies and protection status"""

    def __init__(self, project_root: str = None):
        default_root = "/home/jc/Documents/Horse-race-ai-v2.04"
        self.project_root = Path(project_root or default_root)
        self.analyzer = IntegratedCleanupAnalyzer(project_root)

        # Analysis results
        self.node_red_files = set()
        self.python_scripts_used = set()
        self.config_files_used = set()
        self.missing_files = set()
        self.protected_files = set()
        self.review_files = set()
        self.cleanup_files = set()
        self.protection_issues = []
        self.warnings = []

    def run_analysis(self) -> Dict:
        """Run comprehensive Node-RED dependency analysis"""

        print("🔍 NODE-RED DEPENDENCY ANALYSIS")
        print("=" * 50)

        # Step 1: Identify Node-RED files
        print("📋 Step 1: Identifying Node-RED files...")
        self._find_node_red_files()

        # Step 2: Get current protection status
        print("📋 Step 2: Analyzing current file protection...")
        self._get_protection_status()

        # Step 3: Analyze flow files for Python script references
        print("📋 Step 3: Extracting Python script dependencies...")
        self._analyze_flow_dependencies()

        # Step 4: Check protection status of dependencies
        print("📋 Step 4: Checking protection status...")
        self._check_dependency_protection()

        # Step 5: Verify file existence
        print("📋 Step 5: Verifying file existence...")
        self._verify_file_existence()

        # Step 6: Generate analysis report
        print("📋 Step 6: Generating dependency report...")
        return self._generate_analysis_report()

    def _find_node_red_files(self):
        """Find all Node-RED related files"""

        # Node-RED directory files
        node_red_dir = self.project_root / "node-red"
        if node_red_dir.exists():
            for file_path in node_red_dir.rglob("*"):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(self.project_root))
                    self.node_red_files.add(rel_path)

        # Node-RED setup and config files in root
        node_red_patterns = [
            "*node*red*",
            "docker-compose.node-red.yml",
            "configure_node_red.sh",
            "setup_node_red.sh",
            "verify_node_red.sh",
        ]

        for pattern in node_red_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(self.project_root))
                    self.node_red_files.add(rel_path)

        print(f"  • Found {len(self.node_red_files)} Node-RED files")

    def _get_protection_status(self):
        """Get current file protection status"""

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

        print(f"  • Total protected files: {len(self.protected_files):,}")
        print(f"  • Total review files: {len(self.review_files):,}")

    def _analyze_flow_dependencies(self):
        """Analyze Node-RED flow files for Python script dependencies"""

        python_script_pattern = re.compile(r'python\s+([^\s"]+\.py)')
        script_path_pattern = re.compile(r'((?:tools|scripts|src|api)/[^\s"]+\.py)')

        flow_files = [f for f in self.node_red_files if f.endswith(".json")]

        print(f"  • Analyzing {len(flow_files)} flow files...")

        for flow_file in flow_files:
            try:
                file_path = self.project_root / flow_file
                if not file_path.exists():
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Look for Python script executions
                python_matches = python_script_pattern.findall(content)
                for match in python_matches:
                    # Clean up the path
                    script_path = match.strip()
                    if script_path.startswith("/workspace/"):
                        script_path = script_path[11:]  # Remove /workspace/ prefix
                    self.python_scripts_used.add(script_path)

                # Look for script paths in general
                path_matches = script_path_pattern.findall(content)
                for match in path_matches:
                    self.python_scripts_used.add(match.strip())

                # Look for config file references
                if "config" in content.lower():
                    config_patterns = re.findall(
                        r'([^\s"]+\.(?:json|yaml|yml|toml))', content
                    )
                    for config_file in config_patterns:
                        if any(
                            dir_name in config_file
                            for dir_name in ["config", "node-red"]
                        ):
                            self.config_files_used.add(config_file)

            except Exception as e:
                self.warnings.append(f"Could not analyze {flow_file}: {e}")

        print(f"  • Found {len(self.python_scripts_used)} Python script dependencies")
        print(f"  • Found {len(self.config_files_used)} config file dependencies")

        # Show the scripts found
        if self.python_scripts_used:
            print("  📝 Python scripts referenced:")
            for script in sorted(self.python_scripts_used):
                print(f"    - {script}")

    def _check_dependency_protection(self):
        """Check protection status of Node-RED dependencies"""

        print(f"  🛡️  Checking protection status...")

        # Check Node-RED files themselves
        node_red_protected = 0
        node_red_review = 0
        node_red_unprotected = 0

        for nr_file in self.node_red_files:
            if nr_file in self.protected_files:
                node_red_protected += 1
            elif nr_file in self.review_files:
                node_red_review += 1
            else:
                node_red_unprotected += 1
                if not nr_file.startswith("horse-race-ai-backup-"):
                    self.protection_issues.append(
                        f"CRITICAL: Node-RED file {nr_file} is not protected!"
                    )

        print(f"    • Node-RED files protected: {node_red_protected}")
        print(f"    • Node-RED files for review: {node_red_review}")
        print(f"    • Node-RED files unprotected: {node_red_unprotected}")

        # Check Python script dependencies
        scripts_protected = 0
        scripts_review = 0
        scripts_missing = 0

        for script in self.python_scripts_used:
            if script in self.protected_files:
                scripts_protected += 1
            elif script in self.review_files:
                scripts_review += 1
                self.protection_issues.append(
                    f"WARNING: Node-RED uses {script} which is flagged for review"
                )
            else:
                scripts_missing += 1
                self.protection_issues.append(
                    f"CRITICAL: Node-RED uses {script} which is not protected!"
                )

        print(f"    • Python scripts protected: {scripts_protected}")
        print(f"    • Python scripts for review: {scripts_review}")
        print(f"    • Python scripts missing protection: {scripts_missing}")

        # Check config file dependencies
        configs_protected = 0
        configs_review = 0
        configs_missing = 0

        for config in self.config_files_used:
            if config in self.protected_files:
                configs_protected += 1
            elif config in self.review_files:
                configs_review += 1
                self.warnings.append(
                    f"WARNING: Node-RED uses config {config} flagged for review"
                )
            else:
                configs_missing += 1
                self.protection_issues.append(
                    f"WARNING: Node-RED uses config {config} which is not protected"
                )

        print(f"    • Config files protected: {configs_protected}")
        print(f"    • Config files for review: {configs_review}")
        print(f"    • Config files missing protection: {configs_missing}")

    def _verify_file_existence(self):
        """Verify that referenced files actually exist"""

        print(f"  📂 Verifying file existence...")

        all_dependencies = (
            self.node_red_files | self.python_scripts_used | self.config_files_used
        )

        existing_count = 0
        missing_count = 0

        for file_path in all_dependencies:
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_count += 1
            else:
                missing_count += 1
                self.missing_files.add(file_path)
                if not file_path.startswith("horse-race-ai-backup-"):
                    self.protection_issues.append(
                        f"ERROR: Referenced file {file_path} does not exist!"
                    )

        print(f"    • Files existing: {existing_count}")
        print(f"    • Files missing: {missing_count}")

        if self.missing_files:
            print("    📝 Missing files:")
            for missing in sorted(self.missing_files):
                if not missing.startswith("horse-race-ai-backup-"):
                    print(f"      - {missing}")

    def _generate_analysis_report(self) -> Dict:
        """Generate comprehensive Node-RED analysis report"""

        print("\n" + "=" * 60)
        print("📊 NODE-RED DEPENDENCY ANALYSIS REPORT")
        print("=" * 60)

        # Calculate health score
        total_issues = len(
            [issue for issue in self.protection_issues if "CRITICAL" in issue]
        )
        total_warnings = len(
            [issue for issue in self.protection_issues if "WARNING" in issue]
        )

        # Determine Node-RED health
        if total_issues == 0:
            if total_warnings == 0:
                health_status = "🟢 EXCELLENT"
                health_score = 100
            elif total_warnings < 3:
                health_status = "🟡 GOOD"
                health_score = 85
            else:
                health_status = "🟠 FAIR"
                health_score = 70
        else:
            health_status = "🔴 POOR"
            health_score = 50

        report = {
            "analysis_date": "2025-08-29",
            "health_status": health_status,
            "health_score": health_score,
            "node_red_files": {
                "total_files": len(self.node_red_files),
                "protected": len(
                    [f for f in self.node_red_files if f in self.protected_files]
                ),
                "review": len(
                    [f for f in self.node_red_files if f in self.review_files]
                ),
                "files": sorted(list(self.node_red_files)),
            },
            "python_dependencies": {
                "total_scripts": len(self.python_scripts_used),
                "protected": len(
                    [s for s in self.python_scripts_used if s in self.protected_files]
                ),
                "review": len(
                    [s for s in self.python_scripts_used if s in self.review_files]
                ),
                "scripts": sorted(list(self.python_scripts_used)),
            },
            "config_dependencies": {
                "total_configs": len(self.config_files_used),
                "protected": len(
                    [c for c in self.config_files_used if c in self.protected_files]
                ),
                "review": len(
                    [c for c in self.config_files_used if c in self.review_files]
                ),
                "configs": sorted(list(self.config_files_used)),
            },
            "issues": {
                "critical_issues": total_issues,
                "warnings": total_warnings,
                "missing_files": len(self.missing_files),
                "details": self.protection_issues,
            },
        }

        # Print summary
        print(f"\n🏥 NODE-RED HEALTH: {health_status} ({health_score}/100)")

        print(f"\n📁 NODE-RED FILES:")
        print(f"  • Total Node-RED files: {report['node_red_files']['total_files']}")
        print(f"  • Protected: {report['node_red_files']['protected']}")
        print(f"  • For review: {report['node_red_files']['review']}")

        print(f"\n🐍 PYTHON SCRIPT DEPENDENCIES:")
        print(
            f"  • Total scripts used: {report['python_dependencies']['total_scripts']}"
        )
        print(f"  • Protected: {report['python_dependencies']['protected']}")
        print(f"  • For review: {report['python_dependencies']['review']}")

        print(f"\n⚙️  CONFIG FILE DEPENDENCIES:")
        print(
            f"  • Total configs used: {report['config_dependencies']['total_configs']}"
        )
        print(f"  • Protected: {report['config_dependencies']['protected']}")
        print(f"  • For review: {report['config_dependencies']['review']}")

        print(f"\n🚨 ISSUES SUMMARY:")
        print(f"  • Critical issues: {total_issues}")
        print(f"  • Warnings: {total_warnings}")
        print(f"  • Missing files: {len(self.missing_files)}")

        if self.protection_issues:
            print(f"\n📝 DETAILED ISSUES:")
            for issue in self.protection_issues[:10]:
                print(f"  • {issue}")
            if len(self.protection_issues) > 10:
                print(f"  ... and {len(self.protection_issues) - 10} more")

        # Conclusion
        print(f"\n" + "=" * 60)
        print("🎯 NODE-RED ANALYSIS CONCLUSION:")
        print("=" * 60)

        if health_score >= 85:
            print("✅ NODE-RED SETUP IS WELL PROTECTED")
            print("   All critical dependencies are preserved.")
            print("   🚀 Node-RED workflows will continue functioning!")
        elif health_score >= 70:
            print("⚠️  NODE-RED SETUP MOSTLY PROTECTED")
            print("   Minor issues detected. Review warnings.")
            print("   📋 Check flagged dependencies before cleanup.")
        else:
            print("❌ NODE-RED SETUP HAS CRITICAL ISSUES")
            print("   Important dependencies missing from protection.")
            print("   🛑 Fix protection issues before cleanup!")

        return report


def main():
    """Run Node-RED dependency analysis"""

    analyzer = NodeRedDependencyAnalyzer()
    report = analyzer.run_analysis()

    # Save report
    report_file = analyzer.project_root / "NODE_RED_DEPENDENCY_ANALYSIS_REPORT.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Full report saved to: {report_file}")

    return 0 if report["health_score"] >= 85 else 1


if __name__ == "__main__":
    sys.exit(main())
