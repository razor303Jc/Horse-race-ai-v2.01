#!/usr/bin/env python3
"""
🔍 Enhanced Pipeline Monitor with Function Call Analysis
======================================================

Advanced monitoring system that tracks pipeline file usage, function calls,
and provides comprehensive analysis of what files are being used in the pipeline.

Features:
- Real-time pipeline status monitoring
- Function call analysis and tracking
- File usage discovery across pipeline stages
- Enhanced logging with structured output
- Integration with existing analysis tools
"""

import asyncio
import json
import logging
import os
import subprocess
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import psutil
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "/home/jc/Documents/Horse-race-ai-v2.04/logs/enhanced_pipeline_monitor.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class FunctionCallTracker:
    """Track function calls and file usage across the pipeline"""

    def __init__(self):
        self.project_root = Path("/home/jc/Documents/Horse-race-ai-v2.04")
        self.function_calls = {}
        self.file_usage = {}
        self.import_graph = {}

        # Integration with existing script analyzer
        self.script_analyzer_path = (
            self.project_root / "monitoring" / "pipeline_script_analyzer.py"
        )
        self.analysis_results = {}
        self.pipeline_files = set()

    def analyze_pipeline_files(self) -> Dict[str, List[str]]:
        """Discover all Python files used in the pipeline"""
        logger.info("🔍 Analyzing pipeline file usage...")

        pipeline_patterns = [
            "**/*pipeline*",
            "**/daily_*",
            "**/automation/*",
            "**/monitoring/*",
            "**/analysis/*",
            "scripts/**/*.py",
            "tools/**/*.py",
        ]

        pipeline_files = {}

        for pattern in pipeline_patterns:
            files = list(self.project_root.glob(pattern))
            py_files = [f for f in files if f.suffix == ".py"]
            if py_files:
                pipeline_files[pattern] = [
                    str(f.relative_to(self.project_root)) for f in py_files
                ]

        return pipeline_files

    def analyze_function_calls(self, file_path: Path) -> Dict[str, List[str]]:
        """Analyze function calls within a Python file"""
        if not file_path.exists() or file_path.suffix != ".py":
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Basic function call detection (could be enhanced with AST)
            import re

            # Find function definitions
            function_defs = re.findall(r"def\s+(\w+)\s*\(", content)

            # Find function calls
            function_calls = re.findall(r"(\w+)\s*\(", content)

            # Find imports
            imports = re.findall(r"(?:from\s+(\S+)\s+)?import\s+(\S+)", content)

            return {
                "definitions": function_defs,
                "calls": function_calls,
                "imports": imports,
                "file_size": len(content),
                "line_count": content.count("\n") + 1,
            }

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return {}

    def generate_pipeline_map(self) -> Dict[str, any]:
        """Generate comprehensive pipeline file usage map"""
        logger.info("🗺️ Generating pipeline usage map...")

        pipeline_files = self.analyze_pipeline_files()
        detailed_analysis = {}

        for pattern, files in pipeline_files.items():
            detailed_analysis[pattern] = []

            for file_rel_path in files:
                file_path = self.project_root / file_rel_path
                analysis = self.analyze_function_calls(file_path)

                detailed_analysis[pattern].append(
                    {
                        "file": file_rel_path,
                        "analysis": analysis,
                        "last_modified": datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).isoformat(),
                        "size_bytes": file_path.stat().st_size,
                    }
                )

        return detailed_analysis


class PipelineFileWatcher(FileSystemEventHandler):
    """Watch for changes in pipeline files"""

    def __init__(self, monitor):
        self.monitor = monitor

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".py"):
            logger.info(f"📝 Pipeline file modified: {event.src_path}")
            self.monitor.log_file_change(event.src_path, "modified")

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".py"):
            logger.info(f"✨ Pipeline file created: {event.src_path}")
            self.monitor.log_file_change(event.src_path, "created")


class EnhancedPipelineMonitor:
    """Enhanced pipeline monitoring with function call analysis"""

    def __init__(self):
        self.project_root = Path("/home/jc/Documents/Horse-race-ai-v2.04")
        self.status_file = self.project_root / "data" / "enhanced_monitor_status.json"
        self.function_tracker = FunctionCallTracker()
        self.file_changes = []
        self.pipeline_processes = {}
        self.monitoring_active = False

        # Ensure directories exist
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        (self.project_root / "logs").mkdir(exist_ok=True)

    def log_file_change(self, file_path: str, change_type: str):
        """Log file changes for analysis"""
        change_record = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "change_type": change_type,
            "relative_path": (
                str(Path(file_path).relative_to(self.project_root))
                if self.project_root.name in file_path
                else file_path
            ),
        }

        self.file_changes.append(change_record)

        # Keep only last 100 changes
        if len(self.file_changes) > 100:
            self.file_changes = self.file_changes[-100:]

    def check_pipeline_processes(self) -> Dict[str, any]:
        """Check what pipeline processes are currently running"""
        processes = {}

        try:
            # Check for Python processes related to pipeline
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    cmdline = " ".join(proc.info["cmdline"] or [])

                    # Check for pipeline-related processes
                    pipeline_keywords = [
                        "daily_file_watcher",
                        "pipeline_integration",
                        "complete_pipeline_runner",
                        "pipeline_orchestrator",
                        "data_processor",
                    ]

                    for keyword in pipeline_keywords:
                        if keyword in cmdline:
                            processes[keyword] = {
                                "pid": proc.info["pid"],
                                "cmdline": cmdline,
                                "status": proc.status(),
                                "cpu_percent": proc.cpu_percent(),
                                "memory_mb": proc.memory_info().rss / 1024 / 1024,
                                "create_time": datetime.fromtimestamp(
                                    proc.create_time()
                                ).isoformat(),
                            }
                            break

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            logger.error(f"Error checking processes: {e}")

        return processes

    def check_docker_containers(self) -> Dict[str, str]:
        """Check Docker container status"""
        containers = {}

        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--format",
                    "table {{.Names}}\t{{.Status}}\t{{.Ports}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            name = parts[0].strip()
                            status = parts[1].strip()
                            ports = parts[2].strip() if len(parts) > 2 else ""
                            containers[name] = {"status": status, "ports": ports}

        except Exception as e:
            logger.error(f"Error checking Docker containers: {e}")

        return containers

    def analyze_log_files(self) -> Dict[str, any]:
        """Analyze recent log files for pipeline activity"""
        logs_dir = self.project_root / "logs"
        log_analysis = {}

        if not logs_dir.exists():
            return log_analysis

        try:
            for log_file in logs_dir.glob("*.log"):
                if log_file.stat().st_size > 0:
                    # Get recent entries (last 100 lines)
                    try:
                        result = subprocess.run(
                            ["tail", "-100", str(log_file)],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )

                        if result.returncode == 0:
                            lines = result.stdout.strip().split("\n")

                            # Count different log levels
                            error_count = len([l for l in lines if "ERROR" in l])
                            warning_count = len([l for l in lines if "WARNING" in l])
                            info_count = len([l for l in lines if "INFO" in l])

                            # Find recent activity (last hour)
                            recent_lines = []
                            cutoff_time = datetime.now() - timedelta(hours=1)

                            for line in lines[-20:]:  # Check last 20 lines
                                if line.strip():
                                    recent_lines.append(line)

                            log_analysis[log_file.name] = {
                                "size_bytes": log_file.stat().st_size,
                                "last_modified": datetime.fromtimestamp(
                                    log_file.stat().st_mtime
                                ).isoformat(),
                                "error_count": error_count,
                                "warning_count": warning_count,
                                "info_count": info_count,
                                "recent_activity": recent_lines,
                                "total_lines": len(lines),
                            }

                    except Exception as e:
                        logger.error(f"Error analyzing {log_file}: {e}")

        except Exception as e:
            logger.error(f"Error analyzing logs: {e}")

        return log_analysis

    def generate_status_report(self) -> Dict[str, any]:
        """Generate comprehensive status report"""
        logger.info("📊 Generating enhanced status report...")

        status = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_active": self.monitoring_active,
            "pipeline_processes": self.check_pipeline_processes(),
            "docker_containers": self.check_docker_containers(),
            "file_usage_map": self.function_tracker.generate_pipeline_map(),
            "recent_file_changes": self.file_changes[-10:],  # Last 10 changes
            "log_analysis": self.analyze_log_files(),
            "system_info": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
                "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
            },
        }

        # Save status to file
        try:
            with open(self.status_file, "w") as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving status file: {e}")

        return status

    def print_status_summary(self, status: Dict[str, any]):
        """Print a readable status summary"""
        print("\n🎯 ENHANCED PIPELINE MONITOR - STATUS SUMMARY")
        print("=" * 60)
        print(f"⏰ Timestamp: {status['timestamp']}")
        print(f"🔄 Monitoring Active: {'✅' if status['monitoring_active'] else '❌'}")

        # Pipeline Processes
        print(f"\n🚀 Pipeline Processes ({len(status['pipeline_processes'])} active):")
        if status["pipeline_processes"]:
            for name, proc in status["pipeline_processes"].items():
                print(
                    f"   ✅ {name}: PID {proc['pid']}, CPU {proc['cpu_percent']:.1f}%, RAM {proc['memory_mb']:.1f}MB"
                )
        else:
            print("   ❌ No pipeline processes detected")

        # Docker Containers
        print(f"\n🐳 Docker Containers ({len(status['docker_containers'])} running):")
        if status["docker_containers"]:
            for name, info in status["docker_containers"].items():
                status_emoji = "✅" if "Up" in info["status"] else "❌"
                print(f"   {status_emoji} {name}: {info['status']}")
        else:
            print("   ❌ No Docker containers running")

        # File Usage Summary
        print(f"\n📁 Pipeline File Usage:")
        total_files = sum(len(files) for files in status["file_usage_map"].values())
        print(f"   📊 Total pipeline files tracked: {total_files}")

        for pattern, files in status["file_usage_map"].items():
            if files:
                print(f"   📂 {pattern}: {len(files)} files")

        # Recent Changes
        print(f"\n📝 Recent File Changes ({len(status['recent_file_changes'])}):")
        for change in status["recent_file_changes"][-5:]:  # Last 5
            print(f"   🔄 {change['change_type']}: {change['relative_path']}")

        # Log Analysis
        print(f"\n📋 Log Analysis:")
        if status["log_analysis"]:
            for log_name, analysis in status["log_analysis"].items():
                errors = analysis["error_count"]
                warnings = analysis["warning_count"]
                error_emoji = "🔴" if errors > 0 else "✅"
                warning_emoji = "🟡" if warnings > 0 else "✅"
                print(
                    f"   {error_emoji} {log_name}: {errors} errors, {warnings} warnings"
                )
        else:
            print("   ❌ No log files found")

        # System Resources
        sys_info = status["system_info"]
        cpu_emoji = (
            "🔴"
            if sys_info["cpu_percent"] > 80
            else "🟡" if sys_info["cpu_percent"] > 50 else "✅"
        )
        mem_emoji = (
            "🔴"
            if sys_info["memory_percent"] > 80
            else "🟡" if sys_info["memory_percent"] > 50 else "✅"
        )

        print(f"\n💻 System Resources:")
        print(f"   {cpu_emoji} CPU: {sys_info['cpu_percent']:.1f}%")
        print(f"   {mem_emoji} Memory: {sys_info['memory_percent']:.1f}%")
        print(f"   💾 Disk: {sys_info['disk_usage']:.1f}%")

    async def start_monitoring(self, interval: int = 30):
        """Start continuous monitoring"""
        logger.info("🚀 Starting enhanced pipeline monitoring...")
        self.monitoring_active = True

        # Setup file watcher
        observer = Observer()
        event_handler = PipelineFileWatcher(self)

        # Watch key directories
        watch_dirs = [
            self.project_root / "tools",
            self.project_root / "scripts",
            self.project_root / "src",
            self.project_root / "api",
        ]

        for watch_dir in watch_dirs:
            if watch_dir.exists():
                observer.schedule(event_handler, str(watch_dir), recursive=True)

        observer.start()

        try:
            while self.monitoring_active:
                status = self.generate_status_report()
                self.print_status_summary(status)

                print(f"\n⏱️ Next update in {interval} seconds... (Ctrl+C to stop)")
                print("=" * 60)

                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        finally:
            observer.stop()
            observer.join()
            self.monitoring_active = False

    def run_analysis_tools(self):
        """Run existing analysis tools for comprehensive overview"""
        logger.info("🔧 Running existing analysis tools...")

        analysis_tools = [
            "tools/analysis/pipeline_status_analyzer.py",
            "scripts/utility/pipeline_analysis_report.py",
            "tools/monitoring/pipeline_monitor.py",
        ]

        for tool in analysis_tools:
            tool_path = self.project_root / tool
            if tool_path.exists():
                print(f"\n🔧 Running: {tool}")
                print("-" * 40)
                try:
                    result = subprocess.run(
                        ["python3", str(tool_path)],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=self.project_root,
                    )

                    if result.returncode == 0:
                        print(result.stdout)
                    else:
                        print(f"❌ Error: {result.stderr}")

                except subprocess.TimeoutExpired:
                    print("⏱️ Tool execution timed out")
                except Exception as e:
                    print(f"❌ Error running tool: {e}")
            else:
                print(f"❌ Tool not found: {tool}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Pipeline Monitor")
    parser.add_argument(
        "--interval", type=int, default=30, help="Monitoring interval in seconds"
    )
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument(
        "--analysis", action="store_true", help="Run existing analysis tools"
    )

    args = parser.parse_args()

    monitor = EnhancedPipelineMonitor()

    try:
        if args.analysis:
            monitor.run_analysis_tools()
        elif args.once:
            status = monitor.generate_status_report()
            monitor.print_status_summary(status)
        else:
            asyncio.run(monitor.start_monitoring(args.interval))

    except Exception as e:
        logger.error(f"Monitor error: {e}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()
