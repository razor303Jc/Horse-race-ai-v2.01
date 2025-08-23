#!/usr/bin/env python3
"""
Daily File Watcher Enhanced Monitoring Integration
=================================================

This script enhances the existing pipeline monitoring with specific focus on
the daily file watcher system and provides detailed analysis of file usage
across the pipeline using the existing function call analysis tools.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import importlib.util

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DailyFileWatcherMonitor:
    """Enhanced monitoring specifically for the daily file watcher pipeline"""

    def __init__(self, base_dir: str = "/home/jc/Documents/Horse-race-ai-v2.04"):
        self.base_dir = Path(base_dir)
        self.logs_dir = self.base_dir / "logs"
        self.data_dir = self.base_dir / "data"
        self.monitoring_dir = self.base_dir / "monitoring"

        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.monitoring_dir.mkdir(exist_ok=True)

        # Status files
        self.status_files = {
            "pipeline_integration": self.data_dir / "pipeline_integration_status.json",
            "daily_watcher": self.data_dir / "daily_watcher_status.json",
            "watcher_state": self.data_dir / "daily_watcher_state.json",
        }

        # Initialize function call analyzer
        self.script_analyzer = None
        self._load_script_analyzer()

    def _load_script_analyzer(self):
        """Load the pipeline script analyzer if available"""
        analyzer_path = self.monitoring_dir / "pipeline_script_analyzer.py"
        if analyzer_path.exists():
            try:
                spec = importlib.util.spec_from_file_location(
                    "pipeline_script_analyzer", analyzer_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.script_analyzer = module.PipelineScriptAnalyzer()
                logger.info("✅ Pipeline script analyzer loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load script analyzer: {e}")
        else:
            logger.warning("Pipeline script analyzer not found")

    def check_pipeline_integration_status(self) -> Dict[str, Any]:
        """Check the current status of the pipeline integration"""
        logger.info("🔍 Checking pipeline integration status...")

        status = {
            "timestamp": datetime.now().isoformat(),
            "integration_running": False,
            "watcher_running": False,
            "processes": {},
            "status_files": {},
            "manual_download_files": [],
            "current_target_date": datetime.now().strftime("%Y-%m-%d"),
        }

        # Check for running processes
        try:
            # Check pipeline integration process
            result = subprocess.run(
                ["pgrep", "-f", "daily_file_watcher_integration.py"],
                capture_output=True,
                text=True,
            )
            if result.stdout.strip():
                status["integration_running"] = True
                pids = result.stdout.strip().split("\n")
                status["processes"]["integration"] = [int(pid) for pid in pids if pid]

            # Check daily watcher process
            result = subprocess.run(
                ["pgrep", "-f", "daily_file_watcher.py"], capture_output=True, text=True
            )
            if result.stdout.strip():
                status["watcher_running"] = True
                pids = result.stdout.strip().split("\n")
                status["processes"]["watcher"] = [int(pid) for pid in pids if pid]

        except Exception as e:
            logger.warning(f"Error checking processes: {e}")

        # Read status files
        for name, file_path in self.status_files.items():
            if file_path.exists():
                try:
                    with open(file_path, "r") as f:
                        status["status_files"][name] = json.load(f)
                except Exception as e:
                    logger.warning(f"Error reading {name} status file: {e}")
                    status["status_files"][name] = {"error": str(e)}

        # Check manual download directory
        manual_download_dir = self.data_dir / "daily_downloads" / "manual_download"
        if manual_download_dir.exists():
            status["manual_download_files"] = [
                {
                    "name": f.name,
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                }
                for f in manual_download_dir.iterdir()
                if f.is_file()
            ]

        return status

    def analyze_pipeline_file_usage(self) -> Dict[str, Any]:
        """Analyze which files are being used in the pipeline"""
        logger.info("📊 Analyzing pipeline file usage...")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "pipeline_files": {},
            "function_calls": {},
            "import_dependencies": {},
            "error": None,
        }

        if not self.script_analyzer:
            analysis["error"] = "Script analyzer not available"
            return analysis

        try:
            # Use the existing script analyzer
            if hasattr(self.script_analyzer, "analyze_manual_downloads"):
                manual_analysis = self.script_analyzer.analyze_manual_downloads()
                analysis["manual_downloads"] = manual_analysis

            if hasattr(self.script_analyzer, "identify_pipeline_scripts"):
                pipeline_scripts = self.script_analyzer.identify_pipeline_scripts()
                analysis["pipeline_scripts"] = pipeline_scripts

            # Get file usage information
            pipeline_patterns = [
                "**/daily_file_watcher*.py",
                "**/pipeline_integration*.py",
                "**/automation/*.py",
                "**/pipeline/*.py",
                "**/data_processing/*.py",
            ]

            for pattern in pipeline_patterns:
                files = list(self.base_dir.glob(pattern))
                if files:
                    analysis["pipeline_files"][pattern] = [
                        {
                            "path": str(f.relative_to(self.base_dir)),
                            "size": f.stat().st_size,
                            "modified": datetime.fromtimestamp(
                                f.stat().st_mtime
                            ).isoformat(),
                        }
                        for f in files
                    ]

        except Exception as e:
            logger.error(f"Error in pipeline file analysis: {e}")
            analysis["error"] = str(e)

        return analysis

    def check_file_watcher_health(self) -> Dict[str, Any]:
        """Check the health of the daily file watcher system"""
        logger.info("🏥 Checking file watcher health...")

        health = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "issues": [],
            "directories": {},
            "expected_files": [],
            "received_files": [],
            "processing_status": "unknown",
        }

        # Check required directories
        required_dirs = [
            "data/daily_downloads/manual_download",
            "data/daily_downloads/cards_data",
            "data/daily_downloads/results_data",
            "data/daily_downloads/processed",
        ]

        for dir_name in required_dirs:
            dir_path = self.base_dir / dir_name
            health["directories"][dir_name] = {
                "exists": dir_path.exists(),
                "writable": dir_path.exists() and os.access(dir_path, os.W_OK),
                "file_count": len(list(dir_path.iterdir())) if dir_path.exists() else 0,
            }

            if not dir_path.exists():
                health["issues"].append(f"Missing directory: {dir_name}")
                health["status"] = "warning"

        # Check for today's expected files
        today = datetime.now().strftime("%Y-%m-%d")
        expected_files = [f"racecards_{today}.zip", f"results_{today}.zip"]
        health["expected_files"] = expected_files

        # Check manual download directory for files
        manual_dir = self.base_dir / "data/daily_downloads/manual_download"
        if manual_dir.exists():
            manual_files = [f.name for f in manual_dir.iterdir() if f.is_file()]

            # Check which expected files are present
            for expected in expected_files:
                # Look for files that match the pattern (allowing for variations)
                found_files = [
                    f
                    for f in manual_files
                    if today in f
                    and any(
                        keyword in f.lower()
                        for keyword in (
                            ["racecards", "cards"]
                            if "racecards" in expected
                            else ["results"]
                        )
                    )
                ]
                if found_files:
                    health["received_files"].extend(found_files)

            # Determine processing status
            if len(health["received_files"]) == len(expected_files):
                health["processing_status"] = "ready_for_processing"
            elif health["received_files"]:
                health["processing_status"] = "partial_files_received"
            else:
                health["processing_status"] = "waiting_for_files"

        # Check log files for errors
        log_files = ["daily_file_watcher.log", "pipeline_integration.log"]
        for log_file in log_files:
            log_path = self.logs_dir / log_file
            if log_path.exists():
                try:
                    # Check last 100 lines for errors
                    result = subprocess.run(
                        ["tail", "-100", str(log_path)], capture_output=True, text=True
                    )
                    if "ERROR" in result.stdout or "CRITICAL" in result.stdout:
                        health["issues"].append(f"Errors found in {log_file}")
                        health["status"] = (
                            "error" if health["status"] != "error" else "error"
                        )
                except Exception as e:
                    logger.warning(f"Could not analyze log file {log_file}: {e}")

        return health

    def generate_monitoring_dashboard(self) -> Dict[str, Any]:
        """Generate a comprehensive monitoring dashboard"""
        logger.info("📊 Generating monitoring dashboard...")

        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "integration_status": self.check_pipeline_integration_status(),
            "file_usage_analysis": self.analyze_pipeline_file_usage(),
            "watcher_health": self.check_file_watcher_health(),
            "summary": {},
        }

        # Generate summary
        integration = dashboard["integration_status"]
        health = dashboard["watcher_health"]

        dashboard["summary"] = {
            "overall_status": (
                "healthy"
                if health["status"] == "healthy" and integration["integration_running"]
                else "warning"
            ),
            "pipeline_running": integration["integration_running"],
            "watcher_running": integration["watcher_running"],
            "files_ready": health["processing_status"] == "ready_for_processing",
            "issues_count": len(health["issues"]),
            "manual_files_count": len(integration["manual_download_files"]),
        }

        return dashboard

    def save_dashboard_report(self, dashboard: Dict[str, Any]) -> str:
        """Save dashboard report to file"""
        timestamp = int(time.time())
        report_file = self.monitoring_dir / f"daily_watcher_report_{timestamp}.json"

        try:
            with open(report_file, "w") as f:
                json.dump(dashboard, f, indent=2)
            logger.info(f"📄 Dashboard report saved to {report_file}")
            return str(report_file)
        except Exception as e:
            logger.error(f"Error saving dashboard report: {e}")
            return ""

    def print_status_summary(self, dashboard: Dict[str, Any]):
        """Print a formatted status summary"""
        print("\n" + "=" * 60)
        print("🎯 DAILY FILE WATCHER MONITORING DASHBOARD")
        print("=" * 60)

        summary = dashboard["summary"]
        integration = dashboard["integration_status"]
        health = dashboard["watcher_health"]

        # Overall Status
        status_emoji = "✅" if summary["overall_status"] == "healthy" else "⚠️"
        print(f"\n{status_emoji} Overall Status: {summary['overall_status'].upper()}")

        # Pipeline Status
        print(f"\n🔄 Pipeline Status:")
        print(
            f"   Integration Running: {'✅ Yes' if summary['pipeline_running'] else '❌ No'}"
        )
        print(
            f"   Watcher Running: {'✅ Yes' if summary['watcher_running'] else '❌ No'}"
        )

        # File Status
        print(f"\n📁 File Status:")
        print(f"   Current Date: {integration['current_target_date']}")
        print(f"   Manual Files: {summary['manual_files_count']}")
        print(f"   Processing Status: {health['processing_status']}")
        print(f"   Files Ready: {'✅ Yes' if summary['files_ready'] else '❌ No'}")

        # Files in Manual Download
        if integration["manual_download_files"]:
            print(f"\n📥 Files in Manual Download:")
            for file_info in integration["manual_download_files"]:
                size_mb = file_info["size"] / (1024 * 1024)
                print(f"   📄 {file_info['name']} ({size_mb:.1f} MB)")

        # Health Issues
        if health["issues"]:
            print(f"\n⚠️ Health Issues ({len(health['issues'])}):")
            for issue in health["issues"]:
                print(f"   🔸 {issue}")

        # Directory Status
        print(f"\n📂 Directory Status:")
        for dir_name, dir_info in health["directories"].items():
            status = "✅" if dir_info["exists"] and dir_info["writable"] else "❌"
            files = dir_info["file_count"]
            print(f"   {status} {dir_name}: {files} files")

        print("\n" + "=" * 60)


def main():
    """Main function"""
    monitor = DailyFileWatcherMonitor()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "status":
            dashboard = monitor.generate_monitoring_dashboard()
            monitor.print_status_summary(dashboard)

        elif command == "report":
            dashboard = monitor.generate_monitoring_dashboard()
            report_file = monitor.save_dashboard_report(dashboard)
            monitor.print_status_summary(dashboard)
            if report_file:
                print(f"\n📄 Detailed report saved to: {report_file}")

        elif command == "integration":
            status = monitor.check_pipeline_integration_status()
            print(json.dumps(status, indent=2))

        elif command == "health":
            health = monitor.check_file_watcher_health()
            print(json.dumps(health, indent=2))

        elif command == "analyze":
            analysis = monitor.analyze_pipeline_file_usage()
            print(json.dumps(analysis, indent=2))

        else:
            print(
                "Usage: python daily_file_watcher_monitor.py [status|report|integration|health|analyze]"
            )
    else:
        # Default: show status
        dashboard = monitor.generate_monitoring_dashboard()
        monitor.print_status_summary(dashboard)


if __name__ == "__main__":
    main()
