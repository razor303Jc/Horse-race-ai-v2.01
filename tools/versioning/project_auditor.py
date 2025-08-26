#!/usr/bin/env python3
"""
🎯 Horse Racing AI - Project Audit Orchestrator
Main coordinator for comprehensive project audit and cleanup

This tool:
1. Orchestrates the complete audit process
2. Coordinates dependency mapping, usage tracking, and cleanup validation
3. Provides safe, step-by-step cleanup execution
4. Manages backups and rollback procedures
5. Generates comprehensive reports and recommendations

Author: AI Assistant
Date: August 26, 2025
Version: 1.0.0
"""

import json
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import logging

# Add project tools to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from dependency_mapper import DependencyMapper
    from file_version_manager import FileVersionManager
    from usage_tracker import SystemUsageTracker
    from cleanup_validator import CleanupValidator
except ImportError as e:
    print(f"❌ Error importing audit tools: {e}")
    print("Make sure all audit tools are in the same directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProjectAuditor:
    """Main orchestrator for project audit and cleanup"""

    def __init__(self, project_root: Optional[str] = None):
        default_root = "/home/jc/Documents/Horse-race-ai-v2.04"
        self.project_root = Path(project_root or default_root)

        # Initialize components
        self.dependency_mapper = DependencyMapper(str(self.project_root))
        self.version_manager = FileVersionManager(str(self.project_root))
        self.usage_tracker = SystemUsageTracker(str(self.project_root))
        self.cleanup_validator = CleanupValidator(str(self.project_root))

        # Audit results
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "phase": "initialized",
            "dependency_analysis": {},
            "usage_analysis": {},
            "cleanup_candidates": [],
            "validation_results": {},
            "recommendations": [],
            "actions_taken": [],
        }

        # Output directory
        self.output_dir = self.project_root / "data" / "audit"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Safety settings
        self.dry_run = True
        self.backup_created = False
        self.max_files_per_batch = 10

    def create_audit_backup(self) -> Path:
        """Create complete project backup before any changes"""
        logger.info("💾 Creating complete project backup...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.project_root.parent / f"horse-race-ai-backup-{timestamp}"

        try:
            # Copy entire project (excluding large directories)
            exclude_patterns = {
                ".git",
                "__pycache__",
                ".pytest_cache",
                ".venv",
                "venv",
                "node_modules",
                "data/backups",
                "logs",
                "ml_cache",
                "cache",
            }

            shutil.copytree(
                self.project_root,
                backup_dir,
                ignore=shutil.ignore_patterns(*exclude_patterns),
            )

            # Create backup manifest
            manifest = {
                "backup_timestamp": datetime.now().isoformat(),
                "source_project": str(self.project_root),
                "backup_location": str(backup_dir),
                "excluded_patterns": list(exclude_patterns),
                "backup_size_mb": self.get_directory_size(backup_dir) / (1024 * 1024),
            }

            with open(backup_dir / "BACKUP_MANIFEST.json", "w") as f:
                json.dump(manifest, f, indent=2)

            self.backup_created = True
            logger.info(f"✅ Backup created: {backup_dir}")
            return backup_dir

        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            raise

    def get_directory_size(self, directory: Path) -> int:
        """Calculate directory size in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                try:
                    total_size += filepath.stat().st_size
                except (OSError, FileNotFoundError):
                    continue
        return total_size

    def run_dependency_analysis(self) -> Dict:
        """Run comprehensive dependency analysis"""
        logger.info("🔍 Phase 1: Running dependency analysis...")

        try:
            # Run dependency mapping
            dependency_results = self.dependency_mapper.run_complete_analysis()

            # Extract key metrics
            unused_files = self.dependency_mapper.find_unused_files()
            circular_deps = self.dependency_mapper.detect_circular_dependencies()
            complexity_metrics = self.dependency_mapper.calculate_complexity_metrics()

            self.audit_results["dependency_analysis"] = {
                "success": True,
                "total_files": len(self.dependency_mapper.python_files),
                "unused_files": list(unused_files),
                "circular_dependencies": circular_deps,
                "complexity_metrics": complexity_metrics,
                "entry_points": list(self.dependency_mapper.entry_points),
            }

            logger.info(
                f"✅ Dependency analysis complete - {len(unused_files)} unused files found"
            )
            return self.audit_results["dependency_analysis"]

        except Exception as e:
            logger.error(f"❌ Dependency analysis failed: {e}")
            self.audit_results["dependency_analysis"] = {
                "success": False,
                "error": str(e),
            }
            return self.audit_results["dependency_analysis"]

    def run_usage_analysis(self) -> Dict:
        """Run comprehensive usage analysis"""
        logger.info("📊 Phase 2: Running usage analysis...")

        try:
            # Run usage tracking
            usage_results = self.usage_tracker.run_comprehensive_scan()
            usage_report = self.usage_tracker.generate_usage_report()

            self.audit_results["usage_analysis"] = {
                "success": True,
                "scan_results": usage_results,
                "usage_report": usage_report,
            }

            logger.info(
                f"✅ Usage analysis complete - {usage_report['summary']['files_tracked']} files tracked"
            )
            return self.audit_results["usage_analysis"]

        except Exception as e:
            logger.error(f"❌ Usage analysis failed: {e}")
            self.audit_results["usage_analysis"] = {"success": False, "error": str(e)}
            return self.audit_results["usage_analysis"]

    def identify_cleanup_candidates(self) -> List[Dict]:
        """Identify files safe for cleanup"""
        logger.info("🎯 Phase 3: Identifying cleanup candidates...")

        candidates = []

        try:
            # Get unused files from dependency analysis
            unused_files = self.audit_results["dependency_analysis"].get(
                "unused_files", []
            )

            # Get removal candidates from version manager
            version_candidates = self.version_manager.get_removal_candidates()

            # Combine and analyze
            all_candidate_files = set(unused_files)

            for candidate in version_candidates:
                all_candidate_files.add(candidate["file"])

            # Analyze each candidate for safety
            for file_path in all_candidate_files:
                full_path = self.project_root / file_path

                if not full_path.exists():
                    continue

                # Check safety
                safety_check = self.version_manager.check_safe_to_modify(full_path)

                # Categorize by risk and type
                file_info = {
                    "file": file_path,
                    "full_path": str(full_path),
                    "safety_check": safety_check,
                    "file_type": self.categorize_file_type(full_path),
                    "size_mb": full_path.stat().st_size / (1024 * 1024),
                    "last_modified": datetime.fromtimestamp(
                        full_path.stat().st_mtime
                    ).isoformat(),
                }

                # Add reasons for removal
                reasons = []
                if file_path in unused_files:
                    reasons.append("Not imported by any other file")

                for vc in version_candidates:
                    if vc["file"] == file_path:
                        reasons.append(vc["reason"])

                file_info["removal_reasons"] = reasons
                file_info["recommended_action"] = self.recommend_action(file_info)

                candidates.append(file_info)

            # Sort by safety and impact
            candidates.sort(
                key=lambda x: (
                    x["safety_check"]["risk_level"] == "low",
                    -x["size_mb"],
                    x["file_type"] == "documentation",
                ),
                reverse=True,
            )

            self.audit_results["cleanup_candidates"] = candidates

            logger.info(f"✅ Found {len(candidates)} cleanup candidates")
            return candidates

        except Exception as e:
            logger.error(f"❌ Cleanup candidate identification failed: {e}")
            return []

    def categorize_file_type(self, file_path: Path) -> str:
        """Categorize file by type"""
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()

        if suffix == ".md" or "readme" in name or "doc" in name:
            return "documentation"
        elif suffix == ".py":
            if "test" in name or "test" in str(file_path.parent):
                return "test"
            elif "tool" in str(file_path.parent) or "script" in str(file_path.parent):
                return "tool"
            else:
                return "code"
        elif suffix in [".yml", ".yaml", ".json"]:
            return "configuration"
        elif suffix == ".sh":
            return "script"
        elif suffix in [".backup", ".old", ".tmp"]:
            return "backup"
        else:
            return "other"

    def recommend_action(self, file_info: Dict) -> str:
        """Recommend action for a file"""
        safety = file_info["safety_check"]
        file_type = file_info["file_type"]

        if safety["risk_level"] == "critical":
            return "KEEP - Critical system file"
        elif safety["entry_point"]:
            return "KEEP - Entry point file"
        elif len(safety["dependents"]) > 0:
            return "KEEP - Has dependents"
        elif file_type == "backup" and safety["risk_level"] == "low":
            return "SAFE_REMOVE - Backup file"
        elif file_type == "documentation" and "deprecated" in " ".join(
            file_info["removal_reasons"]
        ):
            return "SAFE_REMOVE - Deprecated documentation"
        elif safety["risk_level"] == "low" and file_info["size_mb"] > 1:
            return "ARCHIVE - Large unused file"
        elif safety["risk_level"] == "low":
            return "SAFE_REMOVE - Unused low-risk file"
        else:
            return "REVIEW_REQUIRED - Manual review needed"

    def execute_safe_cleanup(
        self, candidates: List[Dict], dry_run: bool = True
    ) -> Dict:
        """Execute safe cleanup of identified files"""
        logger.info(f"🧹 Phase 4: Executing cleanup (dry_run={dry_run})...")

        cleanup_results = {
            "dry_run": dry_run,
            "files_processed": 0,
            "files_removed": 0,
            "files_archived": 0,
            "space_saved_mb": 0,
            "actions": [],
            "errors": [],
        }

        # Filter to safe actions only
        safe_candidates = [
            c
            for c in candidates
            if c["recommended_action"].startswith(("SAFE_REMOVE", "ARCHIVE"))
        ]

        # Limit batch size for safety
        batch_candidates = safe_candidates[: self.max_files_per_batch]

        archive_dir = (
            self.project_root
            / "data"
            / "archive"
            / datetime.now().strftime("%Y%m%d_%H%M%S")
        )

        for candidate in batch_candidates:
            file_path = Path(candidate["full_path"])
            action = candidate["recommended_action"]

            try:
                cleanup_results["files_processed"] += 1

                if not dry_run:
                    # Register file in version system before modification
                    version_id = self.version_manager.register_file(
                        file_path,
                        {
                            "cleanup_action": action,
                            "removal_reasons": candidate["removal_reasons"],
                        },
                    )

                    # Create backup
                    self.version_manager.create_backup(file_path, version_id)

                if action.startswith("SAFE_REMOVE"):
                    if not dry_run:
                        file_path.unlink()
                        cleanup_results["files_removed"] += 1

                    action_record = {
                        "action": "removed",
                        "file": str(candidate["file"]),
                        "size_mb": candidate["size_mb"],
                        "reason": " | ".join(candidate["removal_reasons"]),
                    }

                elif action.startswith("ARCHIVE"):
                    if not dry_run:
                        archive_dir.mkdir(parents=True, exist_ok=True)
                        archive_path = archive_dir / candidate["file"]
                        archive_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(file_path), str(archive_path))
                        cleanup_results["files_archived"] += 1

                    action_record = {
                        "action": "archived",
                        "file": str(candidate["file"]),
                        "size_mb": candidate["size_mb"],
                        "archive_location": (
                            str(archive_dir / candidate["file"])
                            if not dry_run
                            else "DRY_RUN"
                        ),
                    }

                cleanup_results["space_saved_mb"] += candidate["size_mb"]
                cleanup_results["actions"].append(action_record)

                if dry_run:
                    logger.info(
                        f"🔍 [DRY RUN] Would {action_record['action']}: {candidate['file']}"
                    )
                else:
                    logger.info(
                        f"✅ {action_record['action'].title()}: {candidate['file']}"
                    )

            except Exception as e:
                error_record = {
                    "file": str(candidate["file"]),
                    "error": str(e),
                    "action_attempted": action,
                }
                cleanup_results["errors"].append(error_record)
                logger.error(f"❌ Error processing {candidate['file']}: {e}")

        self.audit_results["cleanup_results"] = cleanup_results

        if dry_run:
            logger.info(
                f"🔍 [DRY RUN] Would process {cleanup_results['files_processed']} files, saving {cleanup_results['space_saved_mb']:.1f} MB"
            )
        else:
            logger.info(
                f"✅ Cleanup complete - processed {cleanup_results['files_processed']} files, saved {cleanup_results['space_saved_mb']:.1f} MB"
            )

        return cleanup_results

    def validate_system_integrity(self) -> Dict:
        """Validate system integrity after cleanup"""
        logger.info("🔧 Phase 5: Validating system integrity...")

        try:
            validation_results = self.cleanup_validator.run_comprehensive_validation()

            self.audit_results["validation_results"] = validation_results

            status = validation_results["overall_status"]
            if status == "SUCCESS":
                logger.info("✅ System validation passed - all systems operational")
            elif status == "WARNING":
                logger.warning("⚠️ System validation completed with warnings")
            else:
                logger.error(f"❌ System validation failed: {status}")

            return validation_results

        except Exception as e:
            logger.error(f"❌ System validation failed: {e}")
            validation_results = {"overall_status": "VALIDATION_ERROR", "error": str(e)}
            self.audit_results["validation_results"] = validation_results
            return validation_results

    def generate_comprehensive_report(self) -> Path:
        """Generate comprehensive audit report"""
        logger.info("📄 Generating comprehensive audit report...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"audit_report_{timestamp}.md"

        # Calculate summary statistics
        total_files_analyzed = self.audit_results["dependency_analysis"].get(
            "total_files", 0
        )
        cleanup_candidates = len(self.audit_results.get("cleanup_candidates", []))

        cleanup_results = self.audit_results.get("cleanup_results", {})
        files_processed = cleanup_results.get("files_processed", 0)
        space_saved = cleanup_results.get("space_saved_mb", 0)

        validation_status = self.audit_results.get("validation_results", {}).get(
            "overall_status", "NOT_RUN"
        )

        report_content = f"""# 🔍 Horse Racing AI - Project Audit Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Project: {self.project_root}

## 📊 Executive Summary

### Analysis Results
- **Total Files Analyzed**: {total_files_analyzed}
- **Cleanup Candidates Found**: {cleanup_candidates}
- **Files Processed**: {files_processed}
- **Space Saved**: {space_saved:.1f} MB
- **System Status**: {validation_status}

### Key Metrics
"""

        # Add dependency analysis results
        if "dependency_analysis" in self.audit_results:
            dep_results = self.audit_results["dependency_analysis"]
            if dep_results.get("success"):
                report_content += f"""
#### Dependency Analysis
- **Unused Files**: {len(dep_results.get('unused_files', []))}
- **Circular Dependencies**: {len(dep_results.get('circular_dependencies', []))}
- **Entry Points**: {len(dep_results.get('entry_points', []))}
"""

        # Add usage analysis results
        if "usage_analysis" in self.audit_results:
            usage_results = self.audit_results["usage_analysis"]
            if usage_results.get("success"):
                usage_report = usage_results.get("usage_report", {}).get("summary", {})
                report_content += f"""
#### Usage Analysis
- **Files Tracked**: {usage_report.get('files_tracked', 0)}
- **Active Files**: {usage_report.get('active_files', 0)}
- **Unused Files**: {usage_report.get('unused_files', 0)}
- **Recent Activity**: {usage_report.get('recent_activity', 0)}
"""

        # Add cleanup details
        if cleanup_results:
            report_content += f"""
## 🧹 Cleanup Results

### Actions Taken
- **Files Removed**: {cleanup_results.get('files_removed', 0)}
- **Files Archived**: {cleanup_results.get('files_archived', 0)}
- **Errors Encountered**: {len(cleanup_results.get('errors', []))}

### Space Optimization
- **Total Space Saved**: {cleanup_results.get('space_saved_mb', 0):.1f} MB
- **Files Processed**: {cleanup_results.get('files_processed', 0)}
"""

            if cleanup_results.get("actions"):
                report_content += "\n### Detailed Actions\n"
                for action in cleanup_results["actions"]:
                    report_content += f"- **{action['action'].title()}**: `{action['file']}` ({action['size_mb']:.2f} MB)\n"

        # Add validation results
        if "validation_results" in self.audit_results:
            val_results = self.audit_results["validation_results"]
            summary = val_results.get("summary", {})

            report_content += f"""
## 🔧 System Validation

### Overall Status: {val_results.get('overall_status', 'UNKNOWN')}

### Test Results
- **Total Tests**: {summary.get('tests_total', 0)}
- **Passed**: {summary.get('tests_passed', 0)} ✅
- **Failed**: {summary.get('tests_failed', 0)} ❌
- **Warnings**: {summary.get('warnings', 0)} ⚠️
- **Critical Failures**: {summary.get('critical_failures', 0)} 🚨

### Recommendation
{summary.get('recommendation', 'No recommendation available')}
"""

        # Add recommendations
        report_content += "\n## 💡 Recommendations\n"

        if cleanup_candidates > 0:
            report_content += f"1. **Cleanup Opportunities**: {cleanup_candidates} files identified for potential removal\n"

        if validation_status == "SUCCESS":
            report_content += "2. **System Health**: All systems operational - cleanup was successful\n"
        elif validation_status in ["WARNING", "FAILURE"]:
            report_content += (
                "2. **System Health**: Some issues detected - monitor system closely\n"
            )
        elif validation_status == "CRITICAL_FAILURE":
            report_content += (
                "2. **System Health**: Critical issues detected - consider rollback\n"
            )

        report_content += """
## 🚀 Next Steps

1. **Review Report**: Examine detailed findings and recommendations
2. **Monitor System**: Watch for any issues after cleanup
3. **Regular Audits**: Schedule periodic audits to maintain project health
4. **Documentation**: Update project documentation based on findings

---
*Report generated by Horse Racing AI Project Auditor v1.0.0*
"""

        # Save report
        with open(report_file, "w") as f:
            f.write(report_content)

        # Also save JSON results
        json_file = self.output_dir / f"audit_results_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(self.audit_results, f, indent=2)

        logger.info(f"📄 Comprehensive report saved: {report_file}")
        return report_file

    def run_complete_audit(
        self, dry_run: bool = True, create_backup: bool = True
    ) -> Dict:
        """Run complete audit process"""
        logger.info("🚀 Starting Complete Project Audit")
        logger.info("=" * 60)

        self.dry_run = dry_run

        try:
            # Phase 0: Backup (if requested)
            if create_backup and not dry_run:
                backup_path = self.create_audit_backup()
                self.audit_results["backup_path"] = str(backup_path)

            # Phase 1: Dependency Analysis
            self.audit_results["phase"] = "dependency_analysis"
            self.run_dependency_analysis()

            # Phase 2: Usage Analysis
            self.audit_results["phase"] = "usage_analysis"
            self.run_usage_analysis()

            # Phase 3: Identify Cleanup Candidates
            self.audit_results["phase"] = "cleanup_identification"
            candidates = self.identify_cleanup_candidates()

            # Phase 4: Execute Cleanup
            if candidates:
                self.audit_results["phase"] = "cleanup_execution"
                self.execute_safe_cleanup(candidates, dry_run=dry_run)

            # Phase 5: Validate System (only if not dry run)
            if not dry_run:
                self.audit_results["phase"] = "validation"
                self.validate_system_integrity()

            # Phase 6: Generate Report
            self.audit_results["phase"] = "reporting"
            report_path = self.generate_comprehensive_report()

            self.audit_results["phase"] = "completed"
            self.audit_results["report_path"] = str(report_path)

            logger.info("🎉 Complete audit finished successfully!")
            return self.audit_results

        except Exception as e:
            logger.error(f"❌ Audit failed during {self.audit_results['phase']}: {e}")
            self.audit_results["phase"] = "failed"
            self.audit_results["error"] = str(e)
            raise


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run comprehensive project audit")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument(
        "--execute", action="store_true", help="Execute cleanup (default is dry-run)"
    )
    parser.add_argument("--no-backup", action="store_true", help="Skip backup creation")
    parser.add_argument(
        "--max-files", type=int, default=10, help="Maximum files to process per batch"
    )

    args = parser.parse_args()

    try:
        auditor = ProjectAuditor(args.project_root)
        auditor.max_files_per_batch = args.max_files

        dry_run = not args.execute
        create_backup = not args.no_backup

        if dry_run:
            print("🔍 Running in DRY RUN mode - no files will be modified")
        else:
            print("⚠️ EXECUTING mode - files will be modified!")
            if create_backup:
                print("💾 Backup will be created before any changes")

            # Confirm before proceeding
            response = input("Continue? [y/N]: ")
            if response.lower() != "y":
                print("❌ Audit cancelled by user")
                return 1

        results = auditor.run_complete_audit(
            dry_run=dry_run, create_backup=create_backup
        )

        # Print summary
        print("\n🎯 Audit Summary:")
        print(
            f"📁 Files analyzed: {results['dependency_analysis'].get('total_files', 0)}"
        )

        candidates = len(results.get("cleanup_candidates", []))
        print(f"🗑️ Cleanup candidates: {candidates}")

        cleanup_results = results.get("cleanup_results", {})
        if cleanup_results:
            print(f"📦 Files processed: {cleanup_results.get('files_processed', 0)}")
            print(f"💾 Space saved: {cleanup_results.get('space_saved_mb', 0):.1f} MB")

        validation = results.get("validation_results", {})
        if validation:
            print(f"🔧 System status: {validation.get('overall_status', 'UNKNOWN')}")

        print(f"📄 Report: {results.get('report_path', 'Not generated')}")

        return 0

    except KeyboardInterrupt:
        print("\n🛑 Audit interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Audit failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
