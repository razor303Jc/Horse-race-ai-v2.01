#!/usr/bin/env python3
"""
Custom Root Directory Cleanup 2025
==================================

Specifically designed for current state with data pipeline, analysis tools,
and documentation. Preserves important working files while organizing clutter.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


class SmartCleanup:
    """Smart cleanup that preserves important working files"""

    def __init__(self):
        self.root = Path("/home/jc/Documents/Horse-race-ai-v2.01")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Files to KEEP in root (essential/active files)
        self.keep_in_root = {
            # Core application files
            "main.py",
            "app.py",
            "Dockerfile",
            "docker-compose.yml",
            "requirements.txt",
            "pyproject.toml",
            "README.md",
            "Makefile",
            ".env",
            ".env.example",
            ".gitignore",
            ".flake8",
            # Currently active data pipeline (keep in root for easy access)
            "daily_data_uploader.py",
            "production_pipeline.py",
            "csv_column_mapper.py",
            "pipeline_integration.py",
            "qwen_bigint_solution.py",
            "working_auto_downloader.py",
            # Essential database files
            "create_database_schema.sql",
            "horse_racing_data_schema.sql",
            # Essential shell scripts
            "start_docker.sh",
            "start_web_app.sh",
        }

        # Directory structure to create
        self.directories = {
            "tools/analysis": "Database analysis and exploration tools",
            "tools/data_processing": "Data processing and validation tools",
            "tools/testing": "Standalone test scripts",
            "tools/utilities": "Utility and helper scripts",
            "docs/reports": "Analysis reports and summaries",
            "docs/guides": "Setup and configuration guides",
            "legacy/old_ai_modules": "Legacy AI modules and experiments",
            "legacy/old_scripts": "Old scripts and deprecated tools",
            "database/schemas": "Database schema files and migrations",
            "web/components": "Web application components",
            "configs/docker": "Docker configuration files",
        }

    def create_directories(self):
        """Create organized directory structure"""
        print("📁 Creating organized directory structure...")
        for dir_path, description in self.directories.items():
            full_path = self.root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {dir_path} - {description}")

    def organize_files(self):
        """Organize files into appropriate directories"""

        # Analysis tools
        analysis_files = [
            "analyze_horse_duplicates.py",
            "analyze_racecards.py",
            "analyze_racecards_fixed.py",
            "check_horse_structure.py",
            "check_tables.py",
            "database_explorer.py",
            "detailed_data_explorer.py",
            "investigate_racecards.py",
            "quick_data_insights.py",
        ]

        # Data processing tools (but not the main pipeline files)
        data_processing_files = [
            "csv_column_mapper_broken.py",
            "csv_column_mapper_fixed.py",
            "column_mapper.py",
            "smart_csv_processor.py",
            "data_validator.py",
            "clean_slate_upload.py",
            "complete_upload_solution.py",
            "simple_clean_slate.py",
            "qwen_auto_downloader.py",
        ]

        # Testing files
        testing_files = [
            "test_cleanup.py",
            "test_csv_processing.py",
            "test_database_integration.py",
            "test_docker_validation.py",
            "test_fixed_downloader.py",
            "test_human_login_integration.py",
            "test_improved_column_mapping.py",
            "test_ollama_models.py",
            "test_ollama_models_fixed.py",
            "test_records_qwen.py",
            "test_validated_upload.py",
            "test_zip_extraction.py",
            "final_test.py",
            "simple_final_test.py",
            "quick_racing_test.py",
        ]

        # Utility scripts
        utility_files = [
            "debug_csv_values.py",
            "debug_upload_issues.py",
            "diagnose_overflow.py",
            "run_docker_auto_downloader.py",
            "manual_test_downloader.py",
            "quick_lint_fixer.py",
            "quick_ollama_test.py",
            "simple_whiterabbit_test.py",
            "simple_whiterabbit_test_fixed.py",
            "simple_woocommerce_test.py",
        ]

        # Legacy AI modules
        legacy_ai_files = [
            "ai_betting_bot.py",
            "ai_code_analyzer.py",
            "ai_form_analyzer.py",
            "ai_form_analyzer_fixed.py",
            "ai_project_organizer.py",
            "ai_racing_commentator.py",
            "background_racing_analyzer.py",
            "dynamic_racing_analyzer.py",
            "racing_media_analyzer.py",
        ]

        # Legacy scripts
        legacy_script_files = [
            "final_comprehensive_ai_demonstration.py",
            "flask_racing_integration.py",
            "webapp_racing_interface.py",
        ]

        # Database schema files
        database_files = [
            "database_schema_plan.md",
            "update_all_ids_to_bigint.sql",
            "update_primary_ids_to_bigint.sql",
            "upgrade_schema_for_large_ids.sql",
            "update_racing_schema.py",
            "update_schema_bigint.py",
            "convert_all_integers.py",
            "fix_integer_columns.py",
            "clear_database_data.py",
        ]

        # Docker configs
        docker_files = [
            "docker-compose.auto-downloader.yml",
            "docker-compose.auto-downloader-fixed.yml",
            "docker-compose.ntfy.yml",
            "docker-compose.test.yml",
            "Dockerfile.auto",
            "Dockerfile.react",
            "Dockerfile.test",
        ]

        # Documentation - Reports
        report_files = [
            "DATABASE_ANALYSIS_SUMMARY.md",
            "DATA_UPLOAD_PIPELINE_SUCCESS_REPORT.md",
            "MISSION_ACCOMPLISHED_DATA_UPLOAD.md",
            "RACE_CARDS_ANALYSIS_SUMMARY.md",
            "AUTO_DOWNLOADER_SUCCESS_SUMMARY.md",
            "COMPLETE_ML_PIPELINE_ANALYSIS.md",
            "ML_MODELS_ANALYSIS_DEEP_DIVE.md",
            "ZIP_EXTRACTION_DATABASE_ANALYSIS.md",
            "BIGINT_ANALYSIS_FOR_QWEN.md",
            "AUTO_DOWNLOADER_ANALYSIS_FOR_QWEN.md",
        ]

        # Documentation - Guides
        guide_files = [
            "AI_CODING_MODELS_COMPLETE.md",
            "DOCKER_AUTO_DOWNLOADER_GUIDE.md",
            "DOCKER_SUCCESS_SUMMARY.md",
            "HUMAN_LOGIN_INTEGRATION_SUMMARY.md",
            "LOGIN_CONFIGURATION_SUMMARY.md",
            "OLLAMA_APPLICATIONS_GUIDE.md",
            "QWEN_AI_RECOMMENDATIONS.md",
            "QWEN_AUTO_DOWNLOADER_FIX_PLAN.md",
            "TIMEOUT_UPDATES.md",
            "PIPELINE_ANALYSIS_TODO.md",
        ]

        # Shell scripts and other utilities
        shell_files = [
            "manage_docker_auto_downloader.sh",
            "start_docker_auto_downloader.sh",
            "start_docker_racing.sh",
        ]

        # Define move operations
        move_operations = {
            "tools/analysis": analysis_files,
            "tools/data_processing": data_processing_files,
            "tools/testing": testing_files,
            "tools/utilities": utility_files + shell_files,
            "legacy/old_ai_modules": legacy_ai_files,
            "legacy/old_scripts": legacy_script_files,
            "database/schemas": database_files,
            "configs/docker": docker_files,
            "docs/reports": report_files,
            "docs/guides": guide_files,
        }

        print("\n📦 Organizing files...")
        moved_count = 0

        for target_dir, file_list in move_operations.items():
            for filename in file_list:
                source_path = self.root / filename
                if source_path.exists() and filename not in self.keep_in_root:
                    target_path = self.root / target_dir / filename

                    # Ensure target directory exists
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # Move the file
                    shutil.move(str(source_path), str(target_path))
                    print(f"  ✅ {filename} → {target_dir}/")
                    moved_count += 1
                elif filename in self.keep_in_root:
                    print(f"  🔒 Kept in root: {filename}")

        print(f"\n📊 Total files moved: {moved_count}")

    def create_readme_files(self):
        """Create README files for organized directories"""

        readme_content = {
            "tools/analysis": """# Database Analysis Tools

Tools for exploring and analyzing the database contents:

- `analyze_horse_duplicates.py` - Check for duplicate horses and age anomalies
- `database_explorer.py` - Comprehensive database exploration
- `investigate_racecards.py` - Detailed race cards analysis
- `quick_data_insights.py` - Quick database statistics

Run any tool directly: `python analyze_horse_duplicates.py`
""",
            "tools/data_processing": """# Data Processing Tools

Additional data processing and validation tools (legacy/experimental):

- `csv_column_mapper_*.py` - Various column mapping implementations
- `data_validator.py` - Data validation utilities
- `clean_slate_upload.py` - Clean database upload tools

**Note**: Main production pipeline is in root: `daily_data_uploader.py`
""",
            "docs/reports": """# Analysis Reports

Auto-generated analysis and status reports:

- `DATABASE_ANALYSIS_SUMMARY.md` - Complete database overview (21,251 records)
- `RACE_CARDS_ANALYSIS_SUMMARY.md` - Race cards analysis (297 real entries)
- `DATA_UPLOAD_PIPELINE_SUCCESS_REPORT.md` - Pipeline status (100% success)
- `MISSION_ACCOMPLISHED_DATA_UPLOAD.md` - Project completion summary

All reports reflect current system status and are automatically updated.
""",
        }

        print("\n📝 Creating README files...")
        for dir_name, content in readme_content.items():
            readme_path = self.root / dir_name / "README.md"
            with open(readme_path, "w") as f:
                f.write(content)
            print(f"  ✅ Created: {dir_name}/README.md")

    def cleanup_logs_and_cache(self):
        """Clean up log files and cache"""
        print("\n🧹 Cleaning up logs and cache...")

        # Move log files
        log_files = list(self.root.glob("*.log"))
        if log_files:
            logs_dir = self.root / "logs"
            logs_dir.mkdir(exist_ok=True)
            for log_file in log_files:
                if (
                    log_file.name != "daily_upload.log"
                ):  # Keep main pipeline log in root
                    shutil.move(str(log_file), str(logs_dir / log_file.name))
                    print(f"  📝 Moved log: {log_file.name} → logs/")

    def create_summary(self):
        """Create cleanup summary"""
        summary = f"""# 🧹 Custom Root Directory Cleanup Summary

## ✅ CLEANUP COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 🎯 **STRATEGY**
- **Preserved essential files** in root for easy access
- **Organized supporting files** into logical subdirectories  
- **Maintained working pipeline** structure
- **Created clear documentation** for each category

### 📁 **NEW ORGANIZATION**

#### **ROOT DIRECTORY** (Essential Files Only)
- **Core Pipeline**: `daily_data_uploader.py`, `production_pipeline.py`
- **Core Config**: `requirements.txt`, `Dockerfile`, `docker-compose.yml`
- **Essential DB**: `create_database_schema.sql`
- **Core Scripts**: `main.py`, `app.py`, startup scripts

#### **ORGANIZED SUBDIRECTORIES**
- `tools/analysis/` - Database analysis and exploration tools
- `tools/data_processing/` - Additional data processing utilities
- `tools/testing/` - Standalone test scripts  
- `tools/utilities/` - Helper scripts and utilities
- `docs/reports/` - Auto-generated analysis reports
- `docs/guides/` - Setup and configuration guides
- `legacy/old_ai_modules/` - Previous AI experiments
- `legacy/old_scripts/` - Deprecated scripts
- `database/schemas/` - Database migration files
- `configs/docker/` - Docker configuration files

### 🚀 **BENEFITS**
- **Cleaner root** - Only essential files visible
- **Logical grouping** - Related files together
- **Preserved functionality** - All tools still accessible
- **Better navigation** - Easy to find specific tools
- **Professional structure** - Industry-standard layout

### 📋 **USAGE**
- **Main pipeline**: Run directly from root
- **Analysis tools**: `python tools/analysis/analyze_horse_duplicates.py`
- **Documentation**: Check `docs/reports/` for latest analysis
- **Legacy tools**: Available in `legacy/` directories

---
*Root directory successfully organized and optimized for production use*
"""

        with open(self.root / "CLEANUP_SUMMARY.md", "w") as f:
            f.write(summary)

        print("📄 Created: CLEANUP_SUMMARY.md")

    def run_cleanup(self):
        """Execute the complete cleanup process"""
        print("🧹 CUSTOM ROOT DIRECTORY CLEANUP")
        print("=" * 50)
        print("🎯 Strategy: Preserve essential files, organize supporting files")
        print()

        try:
            self.create_directories()
            self.organize_files()
            self.create_readme_files()
            self.cleanup_logs_and_cache()
            self.create_summary()

            print("\n" + "=" * 50)
            print("✅ CUSTOM CLEANUP COMPLETE!")
            print("🎯 Root directory is now professionally organized")
            print("📋 Check CLEANUP_SUMMARY.md for details")

        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            import traceback

            traceback.print_exc()


def main():
    """Main execution"""
    cleanup = SmartCleanup()
    cleanup.run_cleanup()


if __name__ == "__main__":
    main()
