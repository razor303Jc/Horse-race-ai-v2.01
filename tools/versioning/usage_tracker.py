#!/usr/bin/env python3
"""
📊 Horse Racing AI - System Usage Tracker
Monitors file access patterns and system component usage

This tool:
1. Monitors which files are actually used by running systems
2. Tracks import patterns and execution flows
3. Identifies unused components
4. Generates usage reports for cleanup decisions

Author: AI Assistant
Date: August 26, 2025
Version: 1.0.0
"""

import json
import os
import sys
import time
import psutil
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SystemUsageTracker:
    """Tracks system usage patterns and file access"""

    def __init__(self, project_root: Optional[str] = None):
        default_root = "/home/jc/Documents/Horse-race-ai-v2.04"
        self.project_root = Path(project_root or default_root)

        # Tracking data
        self.usage_data = {
            "file_access": {},
            "process_monitoring": {},
            "docker_activity": {},
            "import_tracking": {},
            "entry_point_usage": {},
            "last_updated": datetime.now().isoformat(),
        }

        # Output paths
        self.output_dir = self.project_root / "data" / "usage_tracking"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.usage_file = self.output_dir / "usage_data.json"
        self.load_existing_data()

    def load_existing_data(self):
        """Load existing usage data"""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, "r") as f:
                    existing_data = json.load(f)
                    # Merge with current structure
                    for key in self.usage_data:
                        if key in existing_data:
                            self.usage_data[key] = existing_data[key]
                logger.info("📥 Loaded existing usage data")
            except Exception as e:
                logger.warning(f"Error loading usage data: {e}")

    def save_usage_data(self):
        """Save usage data to file"""
        self.usage_data["last_updated"] = datetime.now().isoformat()
        with open(self.usage_file, "w") as f:
            json.dump(self.usage_data, f, indent=2)

    def track_file_access(self, file_path: Path, context: str = "manual"):
        """Record file access"""
        try:
            relative_path = str(file_path.relative_to(self.project_root))
        except ValueError:
            # File outside project root
            relative_path = str(file_path)

        if relative_path not in self.usage_data["file_access"]:
            self.usage_data["file_access"][relative_path] = []

        access_record = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "size": file_path.stat().st_size if file_path.exists() else 0,
        }

        self.usage_data["file_access"][relative_path].append(access_record)

        # Keep only recent records (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        self.usage_data["file_access"][relative_path] = [
            record
            for record in self.usage_data["file_access"][relative_path]
            if datetime.fromisoformat(record["timestamp"]) > cutoff_date
        ]

    def scan_running_python_processes(self) -> List[Dict]:
        """Scan for running Python processes and their file usage"""
        python_processes = []

        for proc in psutil.process_iter(["pid", "name", "cmdline", "cwd"]):
            try:
                if proc.info["name"] and "python" in proc.info["name"].lower():
                    cmdline = proc.info["cmdline"] or []
                    if len(cmdline) > 1:
                        script_path = cmdline[1]

                        # Check if it's a project file
                        try:
                            abs_script_path = Path(script_path).resolve()
                            if (
                                self.project_root in abs_script_path.parents
                                or abs_script_path == self.project_root
                            ):
                                process_info = {
                                    "pid": proc.info["pid"],
                                    "script": str(abs_script_path),
                                    "cmdline": cmdline,
                                    "cwd": proc.info["cwd"],
                                    "timestamp": datetime.now().isoformat(),
                                }
                                python_processes.append(process_info)

                                # Track this file access
                                self.track_file_access(
                                    abs_script_path, "running_process"
                                )
                        except (ValueError, OSError):
                            continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return python_processes

    def check_docker_activity(self) -> Dict:
        """Check Docker container activity and file usage"""
        docker_info = {
            "containers_running": [],
            "volumes_mounted": [],
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Get running containers
            result = subprocess.run(
                ["docker", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        container_info = json.loads(line)
                        docker_info["containers_running"].append(
                            {
                                "name": container_info.get("Names", ""),
                                "image": container_info.get("Image", ""),
                                "status": container_info.get("Status", ""),
                                "ports": container_info.get("Ports", ""),
                            }
                        )

            # Get volume information
            volumes_result = subprocess.run(
                ["docker", "volume", "ls", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if volumes_result.returncode == 0:
                for line in volumes_result.stdout.strip().split("\n"):
                    if line:
                        volume_info = json.loads(line)
                        docker_info["volumes_mounted"].append(volume_info)

        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            json.JSONDecodeError,
        ) as e:
            logger.warning(f"Error checking Docker activity: {e}")
        except FileNotFoundError:
            logger.info("Docker not available")

        return docker_info

    def scan_recent_git_activity(self) -> List[Dict]:
        """Scan recent Git commits to see which files are actively modified"""
        git_activity = []

        try:
            # Get commits from last 30 days
            since_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--since",
                    since_date,
                    "--name-only",
                    "--pretty=format:%H|%ad|%s",
                    "--date=iso",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=15,
            )

            if result.returncode == 0:
                current_commit = None
                for line in result.stdout.split("\n"):
                    if "|" in line:  # Commit info line
                        parts = line.split("|", 2)
                        current_commit = {
                            "hash": parts[0],
                            "date": parts[1],
                            "message": parts[2] if len(parts) > 2 else "",
                            "files": [],
                        }
                        git_activity.append(current_commit)
                    elif line.strip() and current_commit:  # File name
                        current_commit["files"].append(line.strip())

                        # Track file access
                        file_path = self.project_root / line.strip()
                        if file_path.exists():
                            self.track_file_access(file_path, "git_modified")

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            logger.warning(f"Error checking Git activity: {e}")
        except FileNotFoundError:
            logger.info("Git not available")

        return git_activity

    def analyze_import_usage(self, file_path: Path) -> List[str]:
        """Analyze which files are imported by a given file"""
        imports = []

        if not file_path.exists() or not file_path.suffix == ".py":
            return imports

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple import detection (could be enhanced with AST)
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("import ") or line.startswith("from "):
                    imports.append(line)

                    # Try to resolve to project files
                    if "from ." in line or any(
                        word in line for word in ["src", "tools", "docker"]
                    ):
                        # This could be a local import
                        self.track_file_access(file_path, "import_analysis")

        except Exception as e:
            logger.warning(f"Error analyzing imports in {file_path}: {e}")

        return imports

    def scan_shell_scripts(self) -> List[Dict]:
        """Scan shell scripts to see which Python files they execute"""
        shell_activity = []

        for script_file in self.project_root.glob("*.sh"):
            try:
                with open(script_file, "r") as f:
                    content = f.read()

                # Look for Python file executions
                executed_files = []
                for line in content.split("\n"):
                    if "python" in line and ".py" in line:
                        # Extract potential Python file paths
                        words = line.split()
                        for word in words:
                            if word.endswith(".py"):
                                executed_files.append(word)

                                # Track access
                                potential_file = self.project_root / word
                                if potential_file.exists():
                                    self.track_file_access(
                                        potential_file,
                                        f"shell_script:{script_file.name}",
                                    )

                if executed_files:
                    shell_activity.append(
                        {
                            "script": str(script_file.relative_to(self.project_root)),
                            "executed_files": executed_files,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

            except Exception as e:
                logger.warning(f"Error analyzing shell script {script_file}: {e}")

        return shell_activity

    def scan_docker_files(self) -> List[Dict]:
        """Scan Docker files to see which files they reference"""
        docker_activity = []

        # Check docker-compose files
        compose_files = list(self.project_root.glob("docker-compose*.yml")) + list(
            self.project_root.glob("docker-compose*.yaml")
        )

        for compose_file in compose_files:
            try:
                with open(compose_file, "r") as f:
                    content = f.read()

                # Look for file references (COPY, volume mounts, etc.)
                referenced_files = []
                for line in content.split("\n"):
                    line = line.strip()

                    # Look for volume mounts or file references
                    if ":" in line and ("/" in line or "." in line):
                        if any(
                            keyword in line
                            for keyword in ["COPY", "volume", "mount", ".py", ".sh"]
                        ):
                            referenced_files.append(line)

                if referenced_files:
                    docker_activity.append(
                        {
                            "file": str(compose_file.relative_to(self.project_root)),
                            "type": "docker-compose",
                            "references": referenced_files,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                    # Track this file as accessed
                    self.track_file_access(compose_file, "docker_analysis")

            except Exception as e:
                logger.warning(f"Error analyzing Docker file {compose_file}: {e}")

        # Check Dockerfiles
        dockerfiles = list(self.project_root.glob("**/Dockerfile*"))

        for dockerfile in dockerfiles:
            try:
                with open(dockerfile, "r") as f:
                    content = f.read()

                referenced_files = []
                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("COPY") or line.startswith("ADD"):
                        referenced_files.append(line)

                if referenced_files:
                    docker_activity.append(
                        {
                            "file": str(dockerfile.relative_to(self.project_root)),
                            "type": "dockerfile",
                            "references": referenced_files,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                    self.track_file_access(dockerfile, "docker_analysis")

            except Exception as e:
                logger.warning(f"Error analyzing Dockerfile {dockerfile}: {e}")

        return docker_activity

    def run_comprehensive_scan(self) -> Dict:
        """Run comprehensive usage tracking scan"""
        logger.info("🔍 Starting comprehensive usage scan...")

        scan_results = {
            "timestamp": datetime.now().isoformat(),
            "python_processes": self.scan_running_python_processes(),
            "docker_activity": self.check_docker_activity(),
            "git_activity": self.scan_recent_git_activity(),
            "shell_scripts": self.scan_shell_scripts(),
            "docker_files": self.scan_docker_files(),
        }

        # Update usage data
        self.usage_data["process_monitoring"] = scan_results["python_processes"]
        self.usage_data["docker_activity"] = scan_results["docker_activity"]

        # Save data
        self.save_usage_data()

        logger.info("✅ Comprehensive scan completed")
        return scan_results

    def generate_usage_report(self) -> Dict:
        """Generate comprehensive usage report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "files_tracked": len(self.usage_data["file_access"]),
                "active_files": 0,
                "unused_files": 0,
                "recent_activity": 0,
            },
            "file_activity": {},
            "recommendations": [],
        }

        # Analyze file activity
        recent_cutoff = datetime.now() - timedelta(days=7)
        active_files = []
        unused_files = []

        for file_path, access_records in self.usage_data["file_access"].items():
            if not access_records:
                unused_files.append(file_path)
                continue

            # Check for recent activity
            recent_access = False
            for record in access_records:
                if datetime.fromisoformat(record["timestamp"]) > recent_cutoff:
                    recent_access = True
                    break

            file_info = {
                "file": file_path,
                "total_accesses": len(access_records),
                "recent_access": recent_access,
                "last_access": (
                    access_records[-1]["timestamp"] if access_records else None
                ),
                "contexts": list(set(record["context"] for record in access_records)),
            }

            if recent_access:
                active_files.append(file_info)
                report["summary"]["recent_activity"] += 1
            else:
                unused_files.append(file_path)

            report["file_activity"][file_path] = file_info

        report["summary"]["active_files"] = len(active_files)
        report["summary"]["unused_files"] = len(unused_files)

        # Generate recommendations
        if unused_files:
            report["recommendations"].append(
                {
                    "type": "cleanup",
                    "priority": "medium",
                    "description": f"Consider reviewing {len(unused_files)} files with no recent activity",
                    "files": unused_files[:10],  # Show first 10
                }
            )

        if len(active_files) > 0:
            most_used = sorted(
                active_files, key=lambda x: x["total_accesses"], reverse=True
            )[:5]
            report["recommendations"].append(
                {
                    "type": "optimization",
                    "priority": "low",
                    "description": "Most frequently accessed files - consider optimizing",
                    "files": [f["file"] for f in most_used],
                }
            )

        return report

    def export_tracking_data(self, output_path: Optional[Path] = None) -> Path:
        """Export all tracking data"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"usage_export_{timestamp}.json"

        # Run fresh scan before export
        scan_results = self.run_comprehensive_scan()

        export_data = {
            "usage_data": self.usage_data,
            "latest_scan": scan_results,
            "usage_report": self.generate_usage_report(),
            "export_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"📤 Exported tracking data to: {output_path}")
        return output_path


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Track system usage patterns")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--scan", action="store_true", help="Run comprehensive scan")
    parser.add_argument("--report", action="store_true", help="Generate usage report")
    parser.add_argument("--export", action="store_true", help="Export tracking data")
    parser.add_argument(
        "--monitor",
        type=int,
        metavar="MINUTES",
        help="Monitor continuously for specified minutes",
    )

    args = parser.parse_args()

    try:
        tracker = SystemUsageTracker(args.project_root)

        if args.scan:
            print("🔍 Running comprehensive usage scan...")
            results = tracker.run_comprehensive_scan()
            print(
                f"✅ Scan complete - found {len(results['python_processes'])} Python processes"
            )
            print(
                f"📦 Docker containers: {len(results['docker_activity']['containers_running'])}"
            )
            print(f"📝 Git commits (30 days): {len(results['git_activity'])}")

        if args.report:
            print("📊 Generating usage report...")
            report = tracker.generate_usage_report()
            print(f"📁 Files tracked: {report['summary']['files_tracked']}")
            print(f"🟢 Active files: {report['summary']['active_files']}")
            print(f"🔴 Unused files: {report['summary']['unused_files']}")
            print(f"📈 Recent activity: {report['summary']['recent_activity']}")

            if report["recommendations"]:
                print("\n💡 Recommendations:")
                for rec in report["recommendations"]:
                    print(f"  {rec['type'].upper()}: {rec['description']}")

        if args.export:
            print("📤 Exporting tracking data...")
            export_path = tracker.export_tracking_data()
            print(f"✅ Exported to: {export_path}")

        if args.monitor:
            print(f"👁️ Monitoring for {args.monitor} minutes...")
            end_time = datetime.now() + timedelta(minutes=args.monitor)

            while datetime.now() < end_time:
                tracker.run_comprehensive_scan()
                time.sleep(60)  # Check every minute

            print("✅ Monitoring complete")

        return 0

    except KeyboardInterrupt:
        print("\n🛑 Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Operation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
