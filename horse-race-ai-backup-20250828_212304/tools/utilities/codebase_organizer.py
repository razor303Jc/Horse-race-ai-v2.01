#!/usr/bin/env python3
"""
🧹 Codebase Organization Script
Cleans up the root directory by moving scripts to proper locations
and removes hardcoded times throughout the system

Author: AI Assistant  
Date: August 14, 2025
"""

import json
import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CodebaseOrganizer:
    """Organizes scripts and removes hardcoded times"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.backup_dir = self.project_root / "archive" / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def organize_scripts(self) -> Dict[str, List[str]]:
        """Move scripts from root to organized directory structure"""
        
        results = {
            "moved": [],
            "errors": [],
            "backed_up": [],
            "created_dirs": []
        }
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        results["created_dirs"].append(str(self.backup_dir))
        
        # Define script organization plan
        script_moves = [
            # Monitoring scripts -> tools/monitoring/
            ("live_06_01_download_monitor.py", "tools/monitoring/live_download_monitor.py"),
            ("live_test_monitor.py", "tools/monitoring/live_test_monitor.py"),
            ("integrated_performance_demo.py", "tools/monitoring/performance_monitor.py"),
            ("performance_timing_demo.py", "tools/monitoring/performance_timing_demo.py"),
            
            # Pipeline scripts -> tools/pipeline/
            ("daily_pipeline_orchestrator.py", "tools/pipeline/daily_orchestrator.py"),
            ("integrated_auto_pipeline.py", "tools/pipeline/integrated_pipeline.py"),
            ("apply_critical_pipeline_fixes.py", "tools/pipeline/critical_fixes.py"),
            ("apply_phase2_reliability.py", "tools/pipeline/reliability_fixes.py"),
            
            # Data processing scripts -> tools/data_processing/
            ("daily_csv_uploader.py", "tools/data_processing/csv_uploader.py"),
            ("column_smart_uploader.py", "tools/data_processing/smart_uploader.py"),
            ("corrected_csv_uploader.py", "tools/data_processing/corrected_uploader.py"),
            ("smart_daily_uploader.py", "tools/data_processing/daily_uploader.py"),
            
            # Analysis scripts -> tools/analysis/
            ("daily_news_analyzer.py", "tools/analysis/news_analyzer.py"),
            ("daily_tips_analyzer.py", "tools/analysis/tips_analyzer.py"),
            ("advanced_racing_analytics.py", "tools/analysis/racing_analytics.py"),
            ("ai_form_analyzer_fixed.py", "tools/analysis/form_analyzer.py"),
            ("ai_reward_analyzer.py", "tools/analysis/reward_analyzer.py"),
            ("simple_form_analyzer.py", "tools/analysis/simple_form_analyzer.py"),
            
            # Utility scripts -> tools/utilities/
            ("qwen_auto_updater.py", "tools/utilities/qwen_updater.py"),
            ("qwen_docker_updater.py", "tools/utilities/qwen_docker_updater.py"),
            ("enhanced_error_handling.py", "tools/utilities/error_handling.py"),
            ("verify_cleanup.py", "tools/utilities/cleanup_verifier.py"),
            ("verify_critical_fixes.py", "tools/utilities/fix_verifier.py"),
            ("organize_docker_scripts.py", "tools/utilities/docker_organizer.py"),
            ("documentation_analysis_report.py", "tools/utilities/documentation_analyzer.py"),
            
            # Testing scripts -> tools/testing/
            ("test_17_stage_integration.py", "tools/testing/integration_test.py"),
            ("test_complete_pipeline.py", "tools/testing/pipeline_test.py"),
            ("test_enhanced_integration.py", "tools/testing/enhanced_integration_test.py"),
            ("test_production_models.py", "tools/testing/production_models_test.py"),
            ("test_validation_fixes.py", "tools/testing/validation_fixes_test.py"),
            ("test_news_notifications.py", "tools/testing/news_notifications_test.py"),
            ("test_woocommerce_keys.py", "tools/testing/woocommerce_keys_test.py"),
        ]
        
        # Execute moves
        for source_file, target_path in script_moves:
            success = self._move_script(source_file, target_path, results)
            if success:
                results["moved"].append(f"{source_file} → {target_path}")
        
        return results
    
    def _move_script(self, source_file: str, target_path: str, results: Dict) -> bool:
        """Move a single script file"""
        
        source_path = self.project_root / source_file
        target_full_path = self.project_root / target_path
        backup_path = self.backup_dir / source_file
        
        if not source_path.exists():
            logger.debug(f"⏭️ Skipping {source_file} (not found)")
            return False
        
        try:
            # Create target directory
            target_full_path.parent.mkdir(parents=True, exist_ok=True)
            if str(target_full_path.parent) not in results["created_dirs"]:
                results["created_dirs"].append(str(target_full_path.parent))
            
            # Create backup
            shutil.copy2(source_path, backup_path)
            results["backed_up"].append(str(backup_path))
            
            # Move file
            shutil.move(str(source_path), str(target_full_path))
            logger.info(f"📁 Moved {source_file} → {target_path}")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to move {source_file}: {e}"
            results["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
            return False
    
    def clean_root_directory(self) -> Dict[str, List[str]]:
        """Clean up remaining files in root directory"""
        
        results = {
            "moved_to_archive": [],
            "errors": [],
            "documentation_files": []
        }
        
        # Files to move to archive
        archive_patterns = [
            "*.md",  # Documentation files (except README.md)
            "analyze_*.py",
            "pipeline_*.py", 
            "deploy_*.py",
            "start_*.py",
            "*.log",
            "*.db"
        ]
        
        # Keep these files in root
        keep_in_root = {
            "README.md",
            "requirements.txt", 
            "requirements-auto-downloader.txt",
            "docker-compose.yml",
            "docker-compose.auto-downloader.yml",
            "Dockerfile",
            "Dockerfile.react",
            "Dockerfile.mkdocs", 
            "Dockerfile.news-analyzer",
            "Dockerfile.reports",
            "Dockerfile.updated",
            "app.py",
            "main.py",
            "Makefile",
            "pyproject.toml",
            "pytest.ini",
            "mkdocs.yml",
            ".env",
            ".env.docker",
            ".env.example",
            ".flake8",
            ".gitignore",
            "horse-racing-ai.code-workspace",
            "dynamic_pipeline_timing.py"  # Keep this for now until integration is complete
        }
        
        # Create archive subdirectories
        archive_docs = self.backup_dir / "documentation"
        archive_scripts = self.backup_dir / "scripts"
        archive_configs = self.backup_dir / "configs"
        
        for archive_dir in [archive_docs, archive_scripts, archive_configs]:
            archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Process files in root
        for file_path in self.project_root.iterdir():
            if file_path.is_file() and file_path.name not in keep_in_root:
                try:
                    # Determine archive location
                    if file_path.suffix == '.md':
                        archive_target = archive_docs / file_path.name
                        results["documentation_files"].append(file_path.name)
                    elif file_path.suffix == '.py':
                        archive_target = archive_scripts / file_path.name
                    elif file_path.suffix in ['.json', '.yml', '.yaml', '.conf']:
                        archive_target = archive_configs / file_path.name
                    else:
                        archive_target = self.backup_dir / file_path.name
                    
                    # Move to archive
                    shutil.move(str(file_path), str(archive_target))
                    results["moved_to_archive"].append(f"{file_path.name} → {archive_target}")
                    logger.info(f"📦 Archived {file_path.name}")
                    
                except Exception as e:
                    error_msg = f"Failed to archive {file_path.name}: {e}"
                    results["errors"].append(error_msg)
                    logger.error(f"❌ {error_msg}")
        
        return results
    
    def update_import_paths(self) -> Dict[str, int]:
        """Update import paths in moved scripts"""
        
        results = {
            "files_updated": 0,
            "imports_fixed": 0,
            "errors": 0
        }
        
        # Find all Python files in tools directory
        tools_dir = self.project_root / "tools"
        
        for py_file in tools_dir.rglob("*.py"):
            try:
                updated = self._fix_imports_in_file(py_file)
                if updated:
                    results["files_updated"] += 1
                    results["imports_fixed"] += updated
                    
            except Exception as e:
                logger.error(f"❌ Error updating imports in {py_file}: {e}")
                results["errors"] += 1
        
        return results
    
    def _fix_imports_in_file(self, file_path: Path) -> int:
        """Fix import paths in a single file"""
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            fixes_made = 0
            
            # Common import fixes
            import_fixes = [
                # Add project root to path
                ("import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))", "import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))\nfrom pathlib import Path\n\n# Add project root to path\nproject_root = Path(__file__).parent.parent.parent\nsys.path.insert(0, str(project_root))"),
                
                # Fix relative imports
                ("from dynamic_pipeline_timing", "from dynamic_pipeline_timing"),
                ("import daily_pipeline_orchestrator", "from tools.pipeline.daily_orchestrator import DailyPipelineOrchestrator"),
                ("import live_06_01_download_monitor", "from tools.monitoring.live_download_monitor import check_download_status"),
                
                # Fix hardcoded paths
                ("/tmp/", "project_root / 'logs' / "),
                ("logs/", "project_root / 'logs' / "),
                ("config/", "project_root / 'config' / "),
                ("data/", "project_root / 'data' / "),
            ]
            
            for old_import, new_import in import_fixes:
                if old_import in content and new_import not in content:
                    content = content.replace(old_import, new_import)
                    fixes_made += 1
            
            # Save if changes were made
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                logger.info(f"🔧 Fixed {fixes_made} imports in {file_path.name}")
                return fixes_made
            
            return 0
            
        except Exception as e:
            logger.error(f"Error fixing imports in {file_path}: {e}")
            return 0
    
    def remove_hardcoded_times(self) -> Dict[str, int]:
        """Remove hardcoded times and replace with dynamic configuration"""
        
        results = {
            "files_updated": 0,
            "times_replaced": 0,
            "errors": 0
        }
        
        # Find all Python files
        for py_file in self.project_root.rglob("*.py"):
            if "archive" in str(py_file) or ".venv" in str(py_file):
                continue
                
            try:
                updated = self._remove_hardcoded_times_in_file(py_file)
                if updated:
                    results["files_updated"] += 1
                    results["times_replaced"] += updated
                    
            except Exception as e:
                logger.error(f"❌ Error updating times in {py_file}: {e}")
                results["errors"] += 1
        
        return results
    
    def _remove_hardcoded_times_in_file(self, file_path: Path) -> int:
        """Remove hardcoded times from a single file"""
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            replacements_made = 0
            
            # Common hardcoded time patterns to replace
            time_replacements = [
                # Replace specific times with config references
                ('"06:01"', 'config.get("download_time", "06:01")'),
                ('"06:25"', 'config.get("download_time", "06:25")'),
                ('"14:00"', 'config.get("first_race_time", "14:00")'),
                ('"13:00"', 'config.get("relationships_time", "13:00")'),
                ('"15:00"', 'config.get("analysis_time", "15:00")'),
                
                # Replace schedule dictionaries
                ('schedule_time": "06:01"', 'schedule_time": config.get("download_time", "06:01")'),
                ('schedule_time": "06:25"', 'schedule_time": config.get("download_time", "06:25")'),
                
                # Replace cron expressions
                ('1 6 * * *', f'{config.get("download_minute", 1)} {config.get("download_hour", 6)} * * *'),
                ('25 6 * * *', f'{config.get("download_minute", 25)} {config.get("download_hour", 6)} * * *'),
            ]
            
            for old_time, new_time in time_replacements:
                if old_time in content:
                    content = content.replace(old_time, new_time)
                    replacements_made += 1
            
            # Add configuration loading if not present
            if replacements_made > 0 and "config.get(" in content and "def load_config" not in content:
                config_loader = '''
def load_dynamic_config():
    """Load dynamic configuration from file"""
    config_file = Path("config/dynamic_schedule.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f).get("metadata", {})
    return {}

config = load_dynamic_config()
'''
                # Insert after imports
                lines = content.split('\n')
                import_end = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith(('#', 'import', 'from')):
                        import_end = i
                        break
                
                lines.insert(import_end, config_loader)
                content = '\n'.join(lines)
                replacements_made += 1
            
            # Save if changes were made
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                logger.info(f"⏰ Removed {replacements_made} hardcoded times in {file_path.name}")
                return replacements_made
            
            return 0
            
        except Exception as e:
            logger.error(f"Error removing hardcoded times in {file_path}: {e}")
            return 0
    
    def generate_organization_report(self, move_results: Dict, clean_results: Dict, 
                                   import_results: Dict, time_results: Dict) -> str:
        """Generate comprehensive organization report"""
        
        report_file = self.project_root / "reports" / f"organization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate totals
        total_moved = len(move_results.get("moved", []))
        total_archived = len(clean_results.get("moved_to_archive", []))
        total_errors = len(move_results.get("errors", [])) + len(clean_results.get("errors", []))
        
        report_content = f"""# 🧹 Codebase Organization Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Organization Summary

- **Scripts Moved**: {total_moved}
- **Files Archived**: {total_archived}
- **Imports Fixed**: {import_results.get("imports_fixed", 0)} in {import_results.get("files_updated", 0)} files
- **Hardcoded Times Removed**: {time_results.get("times_replaced", 0)} in {time_results.get("files_updated", 0)} files
- **Total Errors**: {total_errors}

## 📁 Script Reorganization

### ✅ Successfully Moved
"""
        
        for move in move_results.get("moved", []):
            report_content += f"- {move}\n"
        
        if move_results.get("errors"):
            report_content += "\n### ❌ Move Errors\n"
            for error in move_results["errors"]:
                report_content += f"- {error}\n"
        
        report_content += f"""
## 📦 Root Directory Cleanup

### Files Archived
"""
        
        for archived in clean_results.get("moved_to_archive", []):
            report_content += f"- {archived}\n"
        
        report_content += f"""
### Documentation Files
"""
        
        for doc in clean_results.get("documentation_files", []):
            report_content += f"- {doc}\n"
        
        report_content += f"""
## 🔧 Import Path Updates

- **Files Updated**: {import_results.get("files_updated", 0)}
- **Import Statements Fixed**: {import_results.get("imports_fixed", 0)}
- **Errors**: {import_results.get("errors", 0)}

## ⏰ Hardcoded Time Removal

- **Files Updated**: {time_results.get("files_updated", 0)}
- **Time References Replaced**: {time_results.get("times_replaced", 0)}
- **Errors**: {time_results.get("errors", 0)}

## 📂 New Directory Structure

```
tools/
├── analysis/          # Data analysis scripts
├── cli/              # Command line tools
├── data_processing/   # Data processing utilities
├── database/         # Database tools
├── integration/      # Integration management
├── ml_pipeline/      # Machine learning pipeline
├── monitoring/       # Monitoring and reporting
├── pipeline/         # Pipeline orchestration
├── security/         # Security tools
├── testing/          # Test scripts
└── utilities/        # General utilities
```

## 🗄️ Archive Location

All moved files have been backed up to:
`{self.backup_dir}`

## 🏆 Organization Status: {"✅ COMPLETE" if total_errors == 0 else "⚠️ COMPLETED WITH ERRORS"}

The codebase has been successfully organized with all scripts moved to appropriate directories.
{"All operations completed without errors." if total_errors == 0 else f"Completed with {total_errors} errors - see details above."}
"""
        
        # Save report
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        logger.info(f"📝 Organization report saved to {report_file}")
        return str(report_file)
    
    def run_full_organization(self) -> Dict:
        """Run complete codebase organization"""
        
        logger.info("🧹 Starting full codebase organization...")
        start_time = datetime.now()
        
        try:
            # Step 1: Move scripts to organized structure
            logger.info("📁 Step 1: Moving scripts to organized structure...")
            move_results = self.organize_scripts()
            
            # Step 2: Clean up root directory
            logger.info("🗂️ Step 2: Cleaning up root directory...")
            clean_results = self.clean_root_directory()
            
            # Step 3: Update import paths
            logger.info("🔧 Step 3: Updating import paths...")
            import_results = self.update_import_paths()
            
            # Step 4: Remove hardcoded times
            logger.info("⏰ Step 4: Removing hardcoded times...")
            time_results = self.remove_hardcoded_times()
            
            # Step 5: Generate report
            logger.info("📝 Step 5: Generating organization report...")
            report_file = self.generate_organization_report(
                move_results, clean_results, import_results, time_results
            )
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "total_time": total_time,
                "move_results": move_results,
                "clean_results": clean_results,
                "import_results": import_results,
                "time_results": time_results,
                "report_file": report_file,
                "backup_location": str(self.backup_dir)
            }
            
            logger.info(f"✅ Organization completed in {total_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Organization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_time": (datetime.now() - start_time).total_seconds()
            }


def main():
    """Main organization function"""
    
    print("🧹 Codebase Organization Script")
    print("=" * 50)
    
    organizer = CodebaseOrganizer()
    
    # Run organization
    result = organizer.run_full_organization()
    
    if result["success"]:
        print(f"\n✅ Organization completed successfully!")
        print(f"⏱️ Total time: {result['total_time']:.2f}s")
        print(f"📁 Scripts moved: {len(result['move_results'].get('moved', []))}")
        print(f"📦 Files archived: {len(result['clean_results'].get('moved_to_archive', []))}")
        print(f"🔧 Import fixes: {result['import_results'].get('imports_fixed', 0)}")
        print(f"⏰ Time fixes: {result['time_results'].get('times_replaced', 0)}")
        print(f"📝 Report: {result['report_file']}")
        print(f"🗄️ Backup: {result['backup_location']}")
        
        # Show next steps
        print(f"\n🎯 Next Steps:")
        print(f"   1. Review the organization report")
        print(f"   2. Test that moved scripts still work")
        print(f"   3. Update any remaining references")
        print(f"   4. Run the pipeline integration")
        
    else:
        print(f"\n❌ Organization failed: {result.get('error', 'Unknown error')}")
        print(f"⏱️ Time before failure: {result['total_time']:.2f}s")


if __name__ == "__main__":
    main()
