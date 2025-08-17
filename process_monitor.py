#!/usr/bin/env python3
"""
🔍 Real-Time Process Monitor for Horse Racing AI
===============================================

Comprehensive monitoring system for tracking all process triggers:
- Auto-downloader schedule and execution
- File download events and triggers
- Pipeline stage activations
- Database operations and data flow
- Error conditions and system health

Features:
- Real-time log monitoring
- Process trigger detection
- Event timeline tracking
- System health dashboard
- Alert notifications

Author: AI Assistant
Date: August 17, 2025
"""

import asyncio
import json
import logging
import os
import queue
import re
import subprocess
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class TriggerEvent:
    """Data class for tracking trigger events"""

    timestamp: str
    event_type: str
    source: str
    message: str
    status: str
    details: Dict = None


class ProcessMonitor:
    """Real-time process and trigger monitoring system"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.events = []
        self.max_events = 1000
        self.event_queue = queue.Queue()
        self.monitoring = False

        # Monitoring targets
        self.log_files = self._discover_log_files()
        self.containers = self._discover_containers()
        self.watch_directories = self._discover_watch_directories()

        # Event patterns
        self.trigger_patterns = self._setup_trigger_patterns()

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup monitoring logger"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            handlers=[
                logging.FileHandler(self.project_root / "logs" / "monitor.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _discover_log_files(self) -> List[Path]:
        """Discover all relevant log files"""
        log_patterns = [
            "logs/*.log",
            "data/logs/*.log",
            "logs/auto_downloader/*.log",
            "logs/pipeline/*.log",
        ]

        log_files = []
        for pattern in log_patterns:
            log_files.extend(self.project_root.glob(pattern))

        return [f for f in log_files if f.exists()]

    def _discover_containers(self) -> List[str]:
        """Discover running Docker containers"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=True,
            )
            containers = [name.strip() for name in result.stdout.splitlines()]
            return [
                c for c in containers if "horse" in c.lower() or "racing" in c.lower()
            ]
        except:
            return []

    def _discover_watch_directories(self) -> List[Path]:
        """Discover directories to watch for file changes"""
        watch_dirs = ["data/daily_downloads", "data/processed", "data/results", "logs"]

        return [
            self.project_root / d
            for d in watch_dirs
            if (self.project_root / d).exists()
        ]

    def _setup_trigger_patterns(self) -> Dict[str, List[str]]:
        """Setup regex patterns for different trigger types"""
        return {
            "schedule": [
                r"📅.*Scheduled.*downloader.*for.*(\d{2}:\d{2})",
                r"⏰.*Schedule.*time.*(\d{2}:\d{2})",
                r"🕒.*Running.*scheduled.*task",
                r"Starting.*scheduled.*download",
            ],
            "download": [
                r"📥.*Download.*started",
                r"📄.*Downloaded.*file.*(.+\.csv)",
                r"✅.*Download.*complete",
                r"❌.*Download.*failed",
                r"📊.*Files.*downloaded.*(\d+)",
            ],
            "pipeline": [
                r"🚀.*Pipeline.*started",
                r"📊.*Stage.*(\w+).*started",
                r"✅.*Stage.*(\w+).*completed",
                r"❌.*Stage.*(\w+).*failed",
                r"📈.*Processing.*(\d+).*records",
            ],
            "database": [
                r"📊.*Database.*operation",
                r"💾.*Saved.*(\d+).*records",
                r"🔍.*Query.*executed",
                r"📝.*Record.*(\w+).*ID.*(\d+)",
            ],
            "file_events": [
                r"📁.*File.*created.*(.+)",
                r"📦.*Archive.*created.*(.+)",
                r"🧹.*Cleaned.*(\d+).*files",
                r"🔒.*Moved.*to.*secure.*storage",
            ],
            "errors": [
                r"❌.*Error.*(.+)",
                r"⚠️.*Warning.*(.+)",
                r"💥.*Exception.*(.+)",
                r"🚨.*Alert.*(.+)",
            ],
        }

    def add_event(
        self,
        event_type: str,
        source: str,
        message: str,
        status: str = "info",
        details: Dict = None,
    ):
        """Add a new trigger event"""
        event = TriggerEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            source=source,
            message=message,
            status=status,
            details=details or {},
        )

        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events.pop(0)

        self.event_queue.put(event)

        # Log the event
        status_icon = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "trigger": "🔔",
        }.get(status, "📋")

        self.logger.info(f"{status_icon} [{event_type}] {source}: {message}")

    def parse_log_line(self, line: str, source: str) -> Optional[TriggerEvent]:
        """Parse a log line for trigger patterns"""
        for event_type, patterns in self.trigger_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    details = {"groups": match.groups()} if match.groups() else {}

                    # Determine status from line content
                    status = "info"
                    if (
                        "❌" in line
                        or "error" in line.lower()
                        or "failed" in line.lower()
                    ):
                        status = "error"
                    elif "⚠️" in line or "warning" in line.lower():
                        status = "warning"
                    elif (
                        "✅" in line
                        or "complete" in line.lower()
                        or "success" in line.lower()
                    ):
                        status = "success"
                    elif (
                        "🔔" in line
                        or "trigger" in line.lower()
                        or "scheduled" in line.lower()
                    ):
                        status = "trigger"

                    return TriggerEvent(
                        timestamp=datetime.now().isoformat(),
                        event_type=event_type,
                        source=source,
                        message=line.strip(),
                        status=status,
                        details=details,
                    )
        return None

    def monitor_container_logs(self, container_name: str):
        """Monitor Docker container logs in real-time"""
        try:
            process = subprocess.Popen(
                ["docker", "logs", "-f", container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            while self.monitoring:
                line = process.stdout.readline()
                if line:
                    event = self.parse_log_line(line, f"docker:{container_name}")
                    if event:
                        self.events.append(event)
                        self.event_queue.put(event)

                # Check for errors
                error_line = process.stderr.readline()
                if error_line:
                    self.add_event(
                        "errors",
                        f"docker:{container_name}",
                        error_line.strip(),
                        "error",
                    )

                if not line and not error_line:
                    time.sleep(0.1)

        except Exception as e:
            self.add_event(
                "errors", "monitor", f"Container log monitoring failed: {e}", "error"
            )

    def monitor_log_file(self, log_file: Path):
        """Monitor a log file for changes"""
        try:
            if not log_file.exists():
                return

            with open(log_file, "r") as f:
                f.seek(0, 2)  # Go to end of file

                while self.monitoring:
                    line = f.readline()
                    if line:
                        event = self.parse_log_line(line, f"file:{log_file.name}")
                        if event:
                            self.events.append(event)
                            self.event_queue.put(event)
                    else:
                        time.sleep(0.1)

        except Exception as e:
            self.add_event(
                "errors", "monitor", f"Log file monitoring failed: {e}", "error"
            )

    def monitor_file_changes(self, directory: Path):
        """Monitor directory for file changes"""
        try:
            if not directory.exists():
                return

            seen_files = set()
            if directory.is_dir():
                seen_files = set(f.name for f in directory.rglob("*") if f.is_file())

            while self.monitoring:
                current_files = set()
                if directory.is_dir():
                    current_files = set(
                        f.name for f in directory.rglob("*") if f.is_file()
                    )

                # Check for new files
                new_files = current_files - seen_files
                for new_file in new_files:
                    self.add_event(
                        "file_events",
                        f"watch:{directory.name}",
                        f"New file detected: {new_file}",
                        "trigger",
                    )

                seen_files = current_files
                time.sleep(5)  # Check every 5 seconds

        except Exception as e:
            self.add_event("errors", "monitor", f"File monitoring failed: {e}", "error")

    def check_auto_downloader_status(self):
        """Check auto-downloader container status"""
        while self.monitoring:
            try:
                # Check container status
                result = subprocess.run(
                    [
                        "docker",
                        "ps",
                        "--filter",
                        "name=auto",
                        "--format",
                        "{{.Status}}",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                if result.stdout.strip():
                    status = result.stdout.strip()
                    if "Up" in status:
                        self.add_event(
                            "schedule",
                            "auto-downloader",
                            f"Container running: {status}",
                            "success",
                        )
                    else:
                        self.add_event(
                            "schedule",
                            "auto-downloader",
                            f"Container status: {status}",
                            "warning",
                        )
                else:
                    self.add_event(
                        "schedule", "auto-downloader", "Container not found", "error"
                    )

            except Exception as e:
                self.add_event(
                    "errors", "monitor", f"Status check failed: {e}", "error"
                )

            time.sleep(30)  # Check every 30 seconds

    def start_monitoring(self):
        """Start all monitoring threads"""
        self.monitoring = True
        self.add_event("system", "monitor", "🚀 Process monitoring started", "success")

        threads = []

        # Monitor Docker containers
        for container in self.containers:
            thread = threading.Thread(
                target=self.monitor_container_logs, args=(container,)
            )
            thread.daemon = True
            thread.start()
            threads.append(thread)
            self.add_event(
                "system",
                "monitor",
                f"Started monitoring container: {container}",
                "info",
            )

        # Monitor log files
        for log_file in self.log_files:
            thread = threading.Thread(target=self.monitor_log_file, args=(log_file,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            self.add_event(
                "system", "monitor", f"Started monitoring log: {log_file.name}", "info"
            )

        # Monitor directories
        for watch_dir in self.watch_directories:
            thread = threading.Thread(
                target=self.monitor_file_changes, args=(watch_dir,)
            )
            thread.daemon = True
            thread.start()
            threads.append(thread)
            self.add_event(
                "system",
                "monitor",
                f"Started monitoring directory: {watch_dir.name}",
                "info",
            )

        # Monitor auto-downloader status
        status_thread = threading.Thread(target=self.check_auto_downloader_status)
        status_thread.daemon = True
        status_thread.start()
        threads.append(status_thread)

        return threads

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        self.add_event("system", "monitor", "🛑 Process monitoring stopped", "info")

    def get_recent_events(
        self, limit: int = 50, event_type: str = None
    ) -> List[TriggerEvent]:
        """Get recent events"""
        events = (
            self.events[-limit:]
            if not event_type
            else [e for e in self.events[-limit * 2 :] if e.event_type == event_type][
                -limit:
            ]
        )
        return events

    def display_dashboard(self):
        """Display real-time monitoring dashboard"""
        while self.monitoring:
            os.system("clear" if os.name == "posix" else "cls")

            print("🔍 REAL-TIME PROCESS MONITOR DASHBOARD")
            print("=" * 80)
            print(f"⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📊 Total Events: {len(self.events)}")
            print(
                f"🐳 Containers: {len(self.containers)} | 📁 Log Files: {len(self.log_files)}"
            )
            print(f"👁️  Watch Dirs: {len(self.watch_directories)}")

            # Show recent events by type
            event_types = [
                "schedule",
                "download",
                "pipeline",
                "database",
                "file_events",
                "errors",
            ]

            for event_type in event_types:
                recent = self.get_recent_events(5, event_type)
                if recent:
                    print(f"\n📋 {event_type.upper()} EVENTS:")
                    print("-" * 40)
                    for event in recent[-3:]:  # Show last 3
                        time_str = datetime.fromisoformat(event.timestamp).strftime(
                            "%H:%M:%S"
                        )
                        status_icon = {
                            "info": "ℹ️",
                            "success": "✅",
                            "warning": "⚠️",
                            "error": "❌",
                            "trigger": "🔔",
                        }.get(event.status, "📋")
                        print(
                            f"   {time_str} {status_icon} [{event.source}] {event.message[:60]}..."
                        )

            # Show system status
            print(f"\n🎯 SYSTEM STATUS:")
            print("-" * 40)
            print(f"   🟢 Monitoring Active: {self.monitoring}")
            print(
                f"   🐳 Containers Found: {', '.join(self.containers) if self.containers else 'None'}"
            )
            print(f"   📅 Auto-Downloader Schedule: 13:30")
            print(
                f"   ⏳ Next Check: {(datetime.now() + timedelta(seconds=30)).strftime('%H:%M:%S')}"
            )

            time.sleep(5)  # Update every 5 seconds


def main():
    """Main monitoring function"""
    print("🔍 Starting Horse Racing AI Process Monitor")
    print("=" * 60)

    project_root = Path(__file__).parent
    monitor = ProcessMonitor(project_root)

    # Ensure log directory exists
    (project_root / "logs").mkdir(exist_ok=True)

    print("🚀 Initializing monitoring systems...")

    try:
        # Start monitoring
        threads = monitor.start_monitoring()

        print(f"✅ Started {len(threads)} monitoring threads")
        print("🔍 Monitoring active - Press Ctrl+C to stop")
        print("=" * 60)

        # Show initial status
        print(f"\n📊 MONITORING TARGETS:")
        print(f"   🐳 Containers: {monitor.containers}")
        print(f"   📁 Log Files: {[f.name for f in monitor.log_files]}")
        print(f"   👁️  Watch Dirs: {[d.name for d in monitor.watch_directories]}")

        # Start dashboard
        monitor.display_dashboard()

    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")
        monitor.stop_monitoring()
        print("✅ Monitor stopped")


if __name__ == "__main__":
    main()
