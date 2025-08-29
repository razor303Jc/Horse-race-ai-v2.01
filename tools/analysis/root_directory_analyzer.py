#!/usr/bin/env python3
"""
🏠 Root Directory Cleanup Analyzer
==================================

Analyzes the root directory to identify:
1. Protected files that must stay in root
2. Files that should be moved to appropriate directories
3. Cleanup opportunities and organization plan

Author: AI Assistant
Date: August 29, 2025
"""

import os
import re
from pathlib import Path
from datetime import datetime
import json
from collections import defaultdict


class RootDirectoryAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.analysis_results = {
            "total_files": 0,
            "total_size": 0,
            "protected_files": [],
            "move_candidates": {},
            "cleanup_opportunities": [],
            "directory_suggestions": {},
        }

        # Define protected files that must stay in root
        self.protected_patterns = {
            "docker_compose": ["docker-compose*.yml", "docker-compose*.yaml"],
            "environment": [".env", "example.env", "*.env"],
            "build_tools": [
                "Makefile",
                "pyproject.toml",
                "requirements.txt",
                "setup.py",
            ],
            "git_config": [".gitignore", ".git*"],
            "readme": ["README.md"],
            "config_files": ["pytest.ini", ".flake8", ".pre-commit-config.yaml"],
            "package_files": ["package.json", "package-lock.json"],
            "license": ["LICENSE", "LICENSE.txt", "LICENSE.md"],
        }

        # Define target directories for different file types
        self.target_directories = {
            "docs": [
                "*.md",
                "*_REPORT.md",
                "*_SUMMARY.md",
                "*_GUIDE.md",
                "*_DOCUMENTATION.md",
            ],
            "scripts": [
                "*.sh",
                "*.py",
                "*_trigger.py",
                "*_test.py",
                "extract_*.py",
                "upload_*.py",
            ],
            "config": ["*.yml", "*.yaml", "*.json", "*_flows.json", "*_config.py"],
            "analysis": [
                "*_analysis.py",
                "*_analyzer.py",
                "*_audit.py",
                "*_summary.py",
            ],
            "logs": ["*.log", "*_output.log"],
            "backup": ["*-backup-*/", "*_backup*"],
            "temp": ["temp_*", "__pycache__", ".pytest_cache", "*_cache"],
        }

    def analyze_root_directory(self):
        """Comprehensive analysis of root directory"""
        print("🏠 Starting Root Directory Cleanup Analysis...")

        # Get all items in root directory
        root_items = list(self.project_root.iterdir())

        for item in root_items:
            if item.is_file():
                self._analyze_file(item)
            elif item.is_dir() and not item.name.startswith("."):
                self._analyze_directory(item)

        # Generate suggestions
        self._generate_suggestions()

        return self.analysis_results

    def _analyze_file(self, file_path):
        """Analyze individual file for protection or movement"""
        relative_path = file_path.relative_to(self.project_root)
        file_size = file_path.stat().st_size

        self.analysis_results["total_files"] += 1
        self.analysis_results["total_size"] += file_size

        # Check if file should be protected
        if self._is_protected_file(file_path):
            self.analysis_results["protected_files"].append(
                {
                    "path": str(relative_path),
                    "size": file_size,
                    "reason": self._get_protection_reason(file_path),
                    "category": self._get_file_category(file_path),
                }
            )
        else:
            # File is a candidate for moving
            target_dir = self._suggest_target_directory(file_path)
            if target_dir not in self.analysis_results["move_candidates"]:
                self.analysis_results["move_candidates"][target_dir] = []

            self.analysis_results["move_candidates"][target_dir].append(
                {
                    "path": str(relative_path),
                    "size": file_size,
                    "type": self._get_file_type(file_path),
                    "priority": self._get_move_priority(file_path),
                }
            )

    def _analyze_directory(self, dir_path):
        """Analyze directory structure"""
        relative_path = dir_path.relative_to(self.project_root)

        # Some directories might be candidates for cleanup
        if self._is_temp_directory(dir_path):
            self.analysis_results["cleanup_opportunities"].append(
                {
                    "type": "temp_directory",
                    "path": str(relative_path),
                    "reason": "Temporary directory that may be cleaned up",
                }
            )

    def _is_protected_file(self, file_path):
        """Check if file should be protected in root"""
        filename = file_path.name

        for category, patterns in self.protected_patterns.items():
            for pattern in patterns:
                if self._matches_pattern(filename, pattern):
                    return True

        return False

    def _get_protection_reason(self, file_path):
        """Get reason why file is protected"""
        filename = file_path.name

        for category, patterns in self.protected_patterns.items():
            for pattern in patterns:
                if self._matches_pattern(filename, pattern):
                    return f"Protected as {category.replace('_', ' ')}"

        return "Unknown protection reason"

    def _get_file_category(self, file_path):
        """Get file category for protected files"""
        filename = file_path.name

        for category, patterns in self.protected_patterns.items():
            for pattern in patterns:
                if self._matches_pattern(filename, pattern):
                    return category

        return "unknown"

    def _suggest_target_directory(self, file_path):
        """Suggest target directory for file"""
        filename = file_path.name.lower()

        # Check specific patterns first
        for target_dir, patterns in self.target_directories.items():
            for pattern in patterns:
                if self._matches_pattern(filename, pattern.lower()):
                    return target_dir

        # Special logic for specific file types
        if filename.endswith(".py"):
            if any(keyword in filename for keyword in ["test_", "_test", "debug_"]):
                return "tests"
            elif any(
                keyword in filename for keyword in ["analyze", "analysis", "audit"]
            ):
                return "analysis"
            elif any(
                keyword in filename
                for keyword in ["script", "process_", "upload_", "extract_"]
            ):
                return "scripts"
            else:
                return "src"

        if filename.endswith(".md"):
            if any(
                keyword in filename
                for keyword in ["todo", "report", "summary", "guide", "documentation"]
            ):
                return "docs"

        if filename.endswith((".json", ".yml", ".yaml")):
            return "config"

        if filename.endswith((".log", "_output")):
            return "logs"

        return "misc"

    def _get_file_type(self, file_path):
        """Get file type description"""
        filename = file_path.name.lower()

        if filename.endswith(".py"):
            return "Python script"
        elif filename.endswith(".md"):
            return "Markdown documentation"
        elif filename.endswith((".json", ".yml", ".yaml")):
            return "Configuration file"
        elif filename.endswith(".sh"):
            return "Shell script"
        elif filename.endswith(".log"):
            return "Log file"
        elif filename.endswith(".sql"):
            return "SQL script"
        else:
            return "Other file"

    def _get_move_priority(self, file_path):
        """Get priority for moving file (high, medium, low)"""
        filename = file_path.name.lower()

        # High priority (should be moved immediately)
        if any(
            keyword in filename for keyword in ["temp_", "debug_", "_test.py", "backup"]
        ):
            return "high"

        # Medium priority (organizational improvement)
        if filename.endswith((".py", ".sh", ".json", ".yml")):
            return "medium"

        # Low priority (documentation)
        if filename.endswith(".md"):
            return "low"

        return "medium"

    def _is_temp_directory(self, dir_path):
        """Check if directory is temporary"""
        dirname = dir_path.name.lower()
        temp_patterns = ["temp_", "__pycache__", ".pytest_cache", "backup-", "_cache"]

        return any(pattern in dirname for pattern in temp_patterns)

    def _matches_pattern(self, filename, pattern):
        """Check if filename matches pattern (supports wildcards)"""
        pattern_regex = pattern.replace("*", ".*")
        return re.match(f"^{pattern_regex}$", filename, re.IGNORECASE) is not None

    def _generate_suggestions(self):
        """Generate directory organization suggestions"""
        move_candidates = self.analysis_results["move_candidates"]

        for target_dir, files in move_candidates.items():
            if not files:
                continue

            high_priority = [f for f in files if f["priority"] == "high"]
            medium_priority = [f for f in files if f["priority"] == "medium"]
            low_priority = [f for f in files if f["priority"] == "low"]

            total_size = sum(f["size"] for f in files)

            self.analysis_results["directory_suggestions"][target_dir] = {
                "total_files": len(files),
                "total_size": total_size,
                "high_priority": len(high_priority),
                "medium_priority": len(medium_priority),
                "low_priority": len(low_priority),
                "description": self._get_directory_description(target_dir),
            }

    def _get_directory_description(self, target_dir):
        """Get description for target directory"""
        descriptions = {
            "docs": "Documentation and markdown files",
            "scripts": "Executable scripts and utilities",
            "config": "Configuration files and settings",
            "analysis": "Analysis and audit scripts",
            "logs": "Log files and output",
            "backup": "Backup directories and files",
            "temp": "Temporary files and cache",
            "tests": "Test files and debugging scripts",
            "src": "Source code files",
            "misc": "Miscellaneous files",
        }

        return descriptions.get(target_dir, "Other files")

    def generate_cleanup_plan(self):
        """Generate comprehensive cleanup plan"""
        plan = []
        plan.append("🏠 ROOT DIRECTORY CLEANUP PLAN")
        plan.append("=" * 50)
        plan.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        plan.append(f"Total Files in Root: {self.analysis_results['total_files']}")
        plan.append(f"Total Size: {self.analysis_results['total_size']:,} bytes")
        plan.append("")

        # Protected files
        plan.append("🔒 PROTECTED FILES (STAY IN ROOT)")
        plan.append("-" * 40)
        protected_by_category = defaultdict(list)
        for pfile in self.analysis_results["protected_files"]:
            protected_by_category[pfile["category"]].append(pfile)

        for category, files in protected_by_category.items():
            plan.append(f"\n{category.replace('_', ' ').title()}:")
            for pfile in files:
                plan.append(f"  ✅ {pfile['path']} ({pfile['size']:,} bytes)")
        plan.append("")

        # Files to move
        plan.append("📦 FILES TO MOVE")
        plan.append("-" * 40)
        total_files_to_move = sum(
            len(files) for files in self.analysis_results["move_candidates"].values()
        )
        plan.append(f"Total files to move: {total_files_to_move}")
        plan.append("")

        for target_dir, suggestion in self.analysis_results[
            "directory_suggestions"
        ].items():
            if suggestion["total_files"] > 0:
                plan.append(f"📁 {target_dir}/ ({suggestion['description']})")
                plan.append(f"   Files: {suggestion['total_files']}")
                plan.append(f"   Size: {suggestion['total_size']:,} bytes")
                plan.append(
                    f"   Priority: High:{suggestion['high_priority']}, "
                    f"Medium:{suggestion['medium_priority']}, Low:{suggestion['low_priority']}"
                )

                # Show some example files
                files = self.analysis_results["move_candidates"][target_dir]
                for file_info in files[:3]:
                    plan.append(f"     • {file_info['path']} ({file_info['type']})")
                if len(files) > 3:
                    plan.append(f"     ... and {len(files) - 3} more files")
                plan.append("")

        # Cleanup opportunities
        if self.analysis_results["cleanup_opportunities"]:
            plan.append("🗑️ CLEANUP OPPORTUNITIES")
            plan.append("-" * 40)
            for opportunity in self.analysis_results["cleanup_opportunities"]:
                plan.append(f"• {opportunity['path']} - {opportunity['reason']}")
            plan.append("")

        # Recommendations
        plan.append("💡 RECOMMENDATIONS")
        plan.append("-" * 40)
        plan.append("1. **High Priority**: Move temp/debug files immediately")
        plan.append("2. **Medium Priority**: Organize scripts and config files")
        plan.append("3. **Low Priority**: Move documentation files")
        plan.append("4. **Cleanup**: Remove temporary directories")
        plan.append("")

        plan.append("📊 EXPECTED RESULTS")
        plan.append("-" * 40)
        plan.append(
            f"Root files after cleanup: {len(self.analysis_results['protected_files'])}"
        )
        plan.append(f"Files moved: {total_files_to_move}")
        plan.append(f"Organization improvement: Significant")

        return "\n".join(plan)


def main():
    """Main execution function"""
    project_root = Path(__file__).parent.parent.parent

    analyzer = RootDirectoryAnalyzer(project_root)
    results = analyzer.analyze_root_directory()

    # Generate and print plan
    plan = analyzer.generate_cleanup_plan()
    print(plan)

    # Save detailed results
    results_file = project_root / "ROOT_CLEANUP_ANALYSIS.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Detailed results saved to: {results_file}")


if __name__ == "__main__":
    main()
