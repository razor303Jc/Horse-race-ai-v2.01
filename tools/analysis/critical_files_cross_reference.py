#!/usr/bin/env python3
"""
Critical System Files Cross-Reference Analysis
Cross-references all protection findings to identify most critical files for elevated protection
and additional unwanted files for removal.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter


class CriticalSystemAnalyzer:
    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.04"):
        self.base_path = Path(base_path)
        self.critical_files: Dict[str, Dict] = {}
        self.unwanted_files: Dict[str, Dict] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.file_importance_scores: Dict[str, int] = {}

        # Setup logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def load_analysis_reports(self) -> Dict[str, Dict]:
        """Load all existing analysis reports for cross-referencing."""
        reports = {}

        report_files = [
            "SYSTEM_FUNCTIONALITY_VALIDATION_REPORT.json",
            "NODE_RED_DEPENDENCY_ANALYSIS_REPORT.json",
            "NODE_RED_PROTECTION_SUMMARY.json",
        ]

        for report_file in report_files:
            report_path = self.base_path / report_file
            if report_path.exists():
                try:
                    with open(report_path, "r") as f:
                        reports[report_file] = json.load(f)
                    print(f"✅ Loaded {report_file}")
                except Exception as e:
                    print(f"⚠️  Error loading {report_file}: {e}")
            else:
                print(f"❌ {report_file} not found")

        return reports

    def analyze_critical_dependencies(self) -> None:
        """Analyze critical file dependencies across all systems."""
        print("\n🔍 ANALYZING CRITICAL DEPENDENCIES...")

        # Critical system entry points
        entry_points = [
            "api/prediction_api.py",
            "api/ml_management_api.py",
            "tools/data_processing/daily_downloads_manager.py",
            "tools/pipeline/quick_csv_import.py",
            "tools/data_quality/csv_data_cleaner.py",
            "src/automation/human_like_downloader.py",
            "tools/analysis/integrated_cleanup_analyzer.py",
        ]

        # Core configuration files
        config_files = [
            "config/pipeline_integration_config.json",
            "config/daily_watcher_config.json",
            "ML_CONFIG.yaml",
            "docker-compose.yml",
            "pyproject.toml",
            "requirements.txt",
        ]

        # Database and schema files
        db_files = [
            "AI_SCHEMA.sql",
            "database/ai_predictions_enhanced_schema.sql",
            "database/postgres_schema.sql",
        ]

        # Node-RED automation files
        node_red_files = [
            "node-red/flows-enhanced.json",
            "node-red/working-flows.json",
            "docker/node-red/settings.js",
        ]

        # Score files by importance
        for file_path in entry_points:
            self._score_file_importance(file_path, 100, "Core Entry Point")

        for file_path in config_files:
            self._score_file_importance(file_path, 90, "Critical Configuration")

        for file_path in db_files:
            self._score_file_importance(file_path, 85, "Database Schema")

        for file_path in node_red_files:
            self._score_file_importance(file_path, 80, "Automation Flow")

    def _score_file_importance(self, file_path: str, score: int, category: str) -> None:
        """Score a file's importance and add to critical files."""
        full_path = self.base_path / file_path
        if full_path.exists():
            self.file_importance_scores[file_path] = score
            self.critical_files[file_path] = {
                "score": score,
                "category": category,
                "exists": True,
                "size": full_path.stat().st_size if full_path.is_file() else 0,
            }
            print(f"  🎯 {category}: {file_path} (Score: {score})")
        else:
            print(f"  ❌ Missing critical file: {file_path}")

    def identify_unwanted_patterns(self) -> None:
        """Identify patterns of unwanted files for removal."""
        print("\n🗑️  IDENTIFYING UNWANTED FILE PATTERNS...")

        unwanted_patterns = {
            "Backup Files": ["*backup*", "*-backup-*", "*.backup", "*.bak"],
            "Temporary Files": ["*temp*", "*tmp*", "*.tmp", ".*.swp"],
            "Cache Files": ["*cache*", "*__pycache__*", "*.pyc", "*.pyo"],
            "Log Files": ["*.log", "*logs*", "*.out"],
            "Git Artifacts": [".git/objects/*", ".git/logs/*", ".git/hooks/*"],
            "Node Modules": ["node_modules/*", "*package-lock.json"],
            "Build Artifacts": ["dist/*", "build/*", "*.egg-info/*"],
            "IDE Files": [".vscode/*", ".idea/*", "*.swp", "*.swo"],
            "Test Coverage": ["coverage/*", ".coverage", "htmlcov/*"],
            "Old Versions": ["*_old", "*_v1", "*_v2", "*_deprecated"],
        }

        for category, patterns in unwanted_patterns.items():
            files_found = []
            for pattern in patterns:
                matches = list(self.base_path.rglob(pattern))
                files_found.extend(matches)

            if files_found:
                print(f"  📁 {category}: {len(files_found)} files")
                self.unwanted_files[category] = {
                    "count": len(files_found),
                    "files": [
                        str(f.relative_to(self.base_path)) for f in files_found[:10]
                    ],
                    "total_size": sum(
                        f.stat().st_size for f in files_found if f.is_file()
                    ),
                }

    def analyze_dependency_chains(self) -> None:
        """Analyze file dependency chains to find critical paths."""
        print("\n🔗 ANALYZING DEPENDENCY CHAINS...")

        # Find Python files and their imports
        python_files = list(self.base_path.rglob("*.py"))
        import_patterns = {}

        for py_file in python_files[:50]:  # Sample first 50 for performance
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Simple import detection
                imports = []
                for line in content.split("\n"):
                    line = line.strip()
                    if (
                        line.startswith("import ") or line.startswith("from ")
                    ) and "." in line:
                        imports.append(line)

                if imports:
                    rel_path = str(py_file.relative_to(self.base_path))
                    import_patterns[rel_path] = len(imports)

            except Exception:
                continue

        # Find most import-heavy files (likely critical)
        top_importers = sorted(
            import_patterns.items(), key=lambda x: x[1], reverse=True
        )[:10]

        print("  📊 Top files by import count (likely critical):")
        for file_path, import_count in top_importers:
            self._score_file_importance(
                file_path, 70 + min(import_count, 20), "High Dependency"
            )

    def generate_elevated_protection_list(self) -> List[str]:
        """Generate list of files needing elevated protection."""
        # Sort by importance score
        critical_sorted = sorted(
            self.critical_files.items(), key=lambda x: x[1]["score"], reverse=True
        )

        elevated_files = []
        for file_path, info in critical_sorted:
            if info["score"] >= 80:  # High importance threshold
                elevated_files.append(file_path)

        return elevated_files

    def calculate_cleanup_potential(self) -> Dict[str, int]:
        """Calculate potential space savings from cleanup."""
        cleanup_stats = {}

        for category, info in self.unwanted_files.items():
            cleanup_stats[category] = {
                "files": info["count"],
                "size_mb": round(info["total_size"] / (1024 * 1024), 2),
            }

        return cleanup_stats

    def generate_cross_reference_report(self) -> None:
        """Generate comprehensive cross-reference report."""
        print("\n" + "=" * 80)
        print("📊 CRITICAL SYSTEM FILES CROSS-REFERENCE ANALYSIS")
        print("=" * 80)

        # Load existing reports
        reports = self.load_analysis_reports()

        # Analyze critical dependencies
        self.analyze_critical_dependencies()

        # Analyze dependency chains
        self.analyze_dependency_chains()

        # Identify unwanted files
        self.identify_unwanted_patterns()

        # Generate elevated protection list
        elevated_files = self.generate_elevated_protection_list()

        # Calculate cleanup potential
        cleanup_stats = self.calculate_cleanup_potential()

        print(f"\n🎯 ELEVATED PROTECTION RECOMMENDATIONS:")
        print(f"   📈 {len(elevated_files)} files identified for elevated protection")

        print(f"\n📋 TOP CRITICAL FILES (Score ≥ 80):")
        for file_path in elevated_files[:15]:
            info = self.critical_files[file_path]
            print(f"   🔥 {file_path} (Score: {info['score']}, {info['category']})")

        print(f"\n🗑️  CLEANUP OPPORTUNITIES:")
        total_files = sum(stats["files"] for stats in cleanup_stats.values())
        total_size = sum(stats["size_mb"] for stats in cleanup_stats.values())
        print(f"   📊 {total_files:,} unwanted files identified")
        print(f"   💾 {total_size:.1f} MB potential space savings")

        print(f"\n📁 CLEANUP BY CATEGORY:")
        for category, stats in sorted(
            cleanup_stats.items(), key=lambda x: x[1]["size_mb"], reverse=True
        ):
            print(f"   • {category}: {stats['files']} files, {stats['size_mb']} MB")

        # Generate protection recommendations
        print(f"\n🛡️  PROTECTION LEVEL RECOMMENDATIONS:")

        print(f"\n   🔴 CRITICAL (Never Delete):")
        critical_never_delete = [
            f for f in elevated_files if self.critical_files[f]["score"] >= 95
        ]
        for file_path in critical_never_delete[:10]:
            print(f"     - {file_path}")

        print(f"\n   🟡 IMPORTANT (Careful Review):")
        important_files = [
            f for f in elevated_files if 80 <= self.critical_files[f]["score"] < 95
        ]
        for file_path in important_files[:10]:
            print(f"     - {file_path}")

        print(f"\n   🟢 SAFE TO REVIEW:")
        print(
            f"     - Backup files: {cleanup_stats.get('Backup Files', {}).get('files', 0)} files"
        )
        print(
            f"     - Cache files: {cleanup_stats.get('Cache Files', {}).get('files', 0)} files"
        )
        print(
            f"     - Temporary files: {cleanup_stats.get('Temporary Files', {}).get('files', 0)} files"
        )

        # Save comprehensive report
        report_data = {
            "timestamp": "2025-08-29",
            "analysis_type": "cross_reference_critical_files",
            "critical_files": self.critical_files,
            "elevated_protection_files": elevated_files,
            "unwanted_files_stats": cleanup_stats,
            "total_unwanted_files": total_files,
            "total_potential_savings_mb": total_size,
            "protection_recommendations": {
                "critical_never_delete": critical_never_delete,
                "important_careful_review": important_files,
                "safe_cleanup_categories": list(cleanup_stats.keys()),
            },
        }

        with open("CRITICAL_FILES_CROSS_REFERENCE_REPORT.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n💡 NEXT STEPS:")
        print(
            f"   1. 🔧 Update protection logic for {len(elevated_files)} critical files"
        )
        print(f"   2. 🗑️  Implement safe cleanup for {total_files:,} unwanted files")
        print(f"   3. 📊 Prioritize {len(critical_never_delete)} never-delete files")
        print(f"   4. 🔍 Review {len(important_files)} important files")

        print(f"\n📄 Report saved to: CRITICAL_FILES_CROSS_REFERENCE_REPORT.json")
        print("=" * 80)

    def run_analysis(self) -> None:
        """Run the complete cross-reference analysis."""
        print("🔍 Starting critical system files cross-reference analysis...")
        self.generate_cross_reference_report()


if __name__ == "__main__":
    analyzer = CriticalSystemAnalyzer()
    analyzer.run_analysis()
