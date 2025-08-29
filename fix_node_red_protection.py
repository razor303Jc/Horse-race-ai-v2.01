#!/usr/bin/env python3
"""
Node-RED Protection Fix Analysis
===============================

Analyzes Node-RED dependency issues and provides solutions for:
1. Missing Python scripts referenced by Node-RED
2. Unprotected Node-RED configuration files
3. Protection gaps that need addressing
4. Recommendations for fixing Node-RED setup

This addresses the critical issues found in the Node-RED dependency analysis.
"""

import sys
import json
from pathlib import Path
from tools.analysis.integrated_cleanup_analyzer import IntegratedCleanupAnalyzer


class NodeRedProtectionFixer:
    """Analyzes and fixes Node-RED protection issues"""

    def __init__(self, project_root: str = None):
        default_root = "/home/jc/Documents/Horse-race-ai-v2.04"
        self.project_root = Path(project_root or default_root)
        self.analyzer = IntegratedCleanupAnalyzer(project_root)

    def run_analysis(self):
        """Run focused Node-RED protection analysis"""

        print("🔧 NODE-RED PROTECTION FIX ANALYSIS")
        print("=" * 50)

        # Step 1: Check Node-RED critical files
        print("📋 Step 1: Identifying critical Node-RED files...")
        self._check_critical_node_red_files()

        # Step 2: Find alternative/actual Python scripts
        print("📋 Step 2: Finding actual Python script alternatives...")
        self._find_actual_scripts()

        # Step 3: Check protection status of core Node-RED setup
        print("📋 Step 3: Checking core Node-RED protection...")
        self._check_core_protection()

        # Step 4: Generate fix recommendations
        print("📋 Step 4: Generating fix recommendations...")
        self._generate_fix_recommendations()

    def _check_critical_node_red_files(self):
        """Check for critical Node-RED files that should be protected"""

        critical_node_red_files = [
            "node-red/flows-enhanced.json",
            "node-red/flows-starter.json",
            "node-red/working-flows.json",
            "node-red/package.json",
            "node-red/dashboard-config.json",
            "node-red/database-config.json",
            "node-red/schedule-config.json",
            "docker-compose.node-red.yml",
            "setup_node_red.sh",
            "configure_node_red.sh",
        ]

        print(f"  🔍 Checking {len(critical_node_red_files)} critical files...")

        existing_files = []
        missing_files = []

        for file_path in critical_node_red_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_files.append(file_path)
                print(f"    ✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"    ❌ {file_path} (missing)")

        print(f"\n  📊 Critical file status:")
        print(f"    • Existing: {len(existing_files)}")
        print(f"    • Missing: {len(missing_files)}")

        return existing_files, missing_files

    def _find_actual_scripts(self):
        """Find actual Python scripts that could replace missing ones"""

        # Scripts referenced by Node-RED
        referenced_scripts = [
            "scripts/daily_downloader.py",
            "tools/daily_downloader.py",
            "tools/bulk_uploader/bulk_upload_processor.py",
            "tools/data_quality/csv_data_cleaner.py",
            "tools/database/import_clean_data.py",
            "tools/ml_training/generate_predictions.py",
        ]

        print(f"  🔍 Checking {len(referenced_scripts)} referenced scripts...")

        # Find similar/alternative scripts
        alternatives = {}

        # Look for download-related scripts
        download_alternatives = list(self.project_root.glob("tools/**/download*.py"))
        download_alternatives.extend(
            list(self.project_root.glob("scripts/**/download*.py"))
        )
        download_alternatives.extend(
            list(self.project_root.glob("backup_auto_downloader/**/*.py"))
        )

        if download_alternatives:
            alternatives["daily_downloader.py"] = [
                str(p.relative_to(self.project_root)) for p in download_alternatives[:5]
            ]

        # Look for data processing scripts
        data_proc_alternatives = list(
            self.project_root.glob("tools/data_processing/*.py")
        )
        data_proc_alternatives.extend(
            list(self.project_root.glob("tools/data_quality/*.py"))
        )

        if data_proc_alternatives:
            alternatives["csv_data_cleaner.py"] = [
                str(p.relative_to(self.project_root))
                for p in data_proc_alternatives[:5]
            ]

        # Look for database scripts
        db_alternatives = list(self.project_root.glob("tools/database/*.py"))
        db_alternatives.extend(list(self.project_root.glob("tools/**/import*.py")))

        if db_alternatives:
            alternatives["import_clean_data.py"] = [
                str(p.relative_to(self.project_root)) for p in db_alternatives[:5]
            ]

        # Look for ML/prediction scripts
        ml_alternatives = list(self.project_root.glob("tools/ml_training/*.py"))
        ml_alternatives.extend(list(self.project_root.glob("src/**/prediction*.py")))
        ml_alternatives.extend(list(self.project_root.glob("api/*prediction*.py")))

        if ml_alternatives:
            alternatives["generate_predictions.py"] = [
                str(p.relative_to(self.project_root)) for p in ml_alternatives[:5]
            ]

        print(f"  📝 Found alternatives for {len(alternatives)} script types:")
        for script_type, alts in alternatives.items():
            print(f"    • {script_type}:")
            for alt in alts:
                print(f"      - {alt}")

        return alternatives

    def _check_core_protection(self):
        """Check protection status of core Node-RED functionality"""

        # Get current protection status
        file_analysis = self.analyzer.analyze_project_structure()
        self.analyzer.file_analysis = file_analysis
        recommendations = self.analyzer.generate_cleanup_recommendations()

        protected_files = set()
        for rec in recommendations:
            category = rec["category"]
            if "protected" in category or (
                category.endswith("_files") and "unused" not in category
            ):
                files = rec.get("files", rec.get("items", []))
                protected_files.update(files)

        # Check Node-RED core files
        node_red_core = [
            "node-red/flows-enhanced.json",
            "node-red/flows-starter.json",
            "node-red/working-flows.json",
            "node-red/package.json",
            "docker-compose.node-red.yml",
            "setup_node_red.sh",
        ]

        protected_core = []
        unprotected_core = []

        for core_file in node_red_core:
            if core_file in protected_files:
                protected_core.append(core_file)
            else:
                unprotected_core.append(core_file)

        print(f"  🛡️  Core Node-RED file protection:")
        print(f"    • Protected: {len(protected_core)}")
        print(f"    • Unprotected: {len(unprotected_core)}")

        if unprotected_core:
            print(f"    📝 Unprotected core files:")
            for file in unprotected_core:
                if (self.project_root / file).exists():
                    print(f"      ⚠️  {file} (exists but not protected)")
                else:
                    print(f"      ❌ {file} (missing)")

        return protected_core, unprotected_core

    def _generate_fix_recommendations(self):
        """Generate comprehensive fix recommendations"""

        print(f"\n" + "=" * 60)
        print("🔧 NODE-RED PROTECTION FIX RECOMMENDATIONS")
        print("=" * 60)

        print(f"\n🎯 PRIORITY 1: PROTECT CRITICAL NODE-RED FILES")
        print(f"-" * 45)

        critical_files_to_protect = [
            "node-red/flows-enhanced.json",
            "node-red/flows-starter.json",
            "node-red/working-flows.json",
            "node-red/package.json",
            "node-red/dashboard-config.json",
            "node-red/database-config.json",
            "node-red/schedule-config.json",
            "docker-compose.node-red.yml",
            "setup_node_red.sh",
            "configure_node_red.sh",
        ]

        print(f"The following Node-RED files need protection:")
        for file in critical_files_to_protect:
            if (self.project_root / file).exists():
                print(f"  ✅ {file} (exists - needs protection)")
            else:
                print(f"  ❌ {file} (missing)")

        print(f"\n🎯 PRIORITY 2: UPDATE PYTHON SCRIPT REFERENCES")
        print(f"-" * 50)

        script_replacements = {
            "tools/daily_downloader.py": [
                "tools/data_processing/daily_downloads_manager.py",
                "tools/data_management/enhanced_download_system.py",
                "backup_auto_downloader/src/enhanced_data_downloader.py",
            ],
            "scripts/daily_downloader.py": [
                "tools/data_processing/daily_downloads_manager.py",
                "scripts/daily_advanced_metrics.sh",
            ],
            "tools/data_quality/csv_data_cleaner.py": [
                "tools/data_processing/enhanced_data_cleaning_pipeline.py",
                "tools/data_quality/data_validation_pipeline.py",
            ],
            "tools/database/import_clean_data.py": [
                "tools/database/enhanced_data_importer.py",
                "tools/data_processing/bulk_data_processor.py",
            ],
            "tools/ml_training/generate_predictions.py": [
                "api/prediction_api.py",
                "src/horse_racing_ai/ml/enhanced_ml_pipeline.py",
            ],
        }

        print(f"Replace missing scripts with existing alternatives:")
        for missing, replacements in script_replacements.items():
            print(f"\n  📝 {missing} → Replace with:")
            for replacement in replacements:
                if (self.project_root / replacement).exists():
                    print(f"    ✅ {replacement} (exists)")
                else:
                    print(f"    ❌ {replacement} (also missing)")

        print(f"\n🎯 PRIORITY 3: UPDATE PROTECTION LOGIC")
        print(f"-" * 40)

        print(f"Add Node-RED protection to integrated_cleanup_analyzer.py:")
        print(f"  1. Add 'node-red/' to protected directories")
        print(f"  2. Add Node-RED file patterns to protection logic")
        print(f"  3. Add docker-compose.node-red.yml to critical files")
        print(f"  4. Add setup_node_red.sh and configure_node_red.sh")

        print(f"\n🎯 PRIORITY 4: EXCLUDE NODE-RED CACHE/TEMP FILES")
        print(f"-" * 48)

        print(f"Exclude Node-RED cache and temporary files from protection:")
        print(f"  • node-red/data/.npm/_cacache/ (npm cache)")
        print(f"  • node-red/data/.npm/_logs/ (npm logs)")
        print(f"  • node-red/data/projects/*/.git/ (git repositories)")
        print(f"  • These are regenerable and don't need protection")

        print(f"\n🎯 PRIORITY 5: VERIFY NODE-RED FUNCTIONALITY")
        print(f"-" * 45)

        print(f"After implementing fixes:")
        print(f"  1. Test Node-RED flow execution")
        print(f"  2. Verify script paths in flows")
        print(f"  3. Confirm database connections")
        print(f"  4. Test automation scheduling")

        print(f"\n" + "=" * 60)
        print("✅ IMPLEMENTATION PLAN:")
        print("=" * 60)

        print(f"1. 🔧 Update protection logic for Node-RED files")
        print(f"2. 📝 Update Node-RED flows with correct script paths")
        print(f"3. 🧪 Test Node-RED functionality")
        print(f"4. 🛡️  Re-run protection analysis to verify")
        print(f"5. 🚀 Node-RED will be protected and functional!")


def main():
    """Run Node-RED protection fix analysis"""

    fixer = NodeRedProtectionFixer()
    fixer.run_analysis()

    return 0


if __name__ == "__main__":
    sys.exit(main())
