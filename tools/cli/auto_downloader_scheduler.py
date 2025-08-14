#!/usr/bin/env python3
"""
🕒 Auto-Downloader Schedule Manager CLI
=====================================

A command-line tool to manage and update the auto-downloader's scheduled start time.
This tool handles updating the schedule across all configuration files and
Docker containers.

Features:
- View current schedule configuration
- Update schedule time in all relevant files
- Restart Docker container to apply changes
- Validate schedule configuration
- Support for different time formats

Author: AI Assistant
Date: August 13, 2025
"""

import argparse
import json
import logging
import re
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AutoDownloaderScheduler:
    """Manages auto-downloader scheduling configuration."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the scheduler manager."""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.config_files = self._discover_config_files()
        self.schedule_files = self._discover_schedule_files()

    def _discover_config_files(self) -> List[Path]:
        """Discover all configuration files that might contain schedule settings."""
        config_patterns = [
            "project_root / 'config' / project_root / 'config' / daily_pipeline_config*.json",
            "project_root / 'config' / daily_pipeline_config*.json",
            "project_root / 'config' / pipeline_config*.json",
        ]

        config_files = []
        for pattern in config_patterns:
            config_files.extend(self.project_root.glob(pattern))

        return [f for f in config_files if f.exists()]

    def _discover_schedule_files(self) -> List[Path]:
        """Discover Python files that contain hardcoded schedule times."""
        schedule_files = [
            "tools/utilities/run_docker_auto_downloader.py",
            "docker/automation/run_docker_auto_downloader.py",
            "daily_pipeline_orchestrator.py",
            "project_root / 'config' / daily_pipeline_config_manager.py",
        ]

        return [
            self.project_root / f
            for f in schedule_files
            if (self.project_root / f).exists()
        ]

    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format (HH:MM)."""
        pattern = r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
        return bool(re.match(pattern, time_str))

    def _normalize_time_format(self, time_str: str) -> str:
        """Normalize time to HH:MM format."""
        if not self._validate_time_format(time_str):
            raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM format.")

        # Ensure zero-padding
        hour, minute = time_str.split(":")
        return f"{int(hour):02d}:{int(minute):02d}"

    def get_current_schedule(self) -> Dict[str, str]:
        """Get current schedule configuration from all sources."""
        schedule_info = {}

        # Check JSON config files
        for config_file in self.config_files:
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                    if "schedule" in config and "download_time" in config["schedule"]:
                        download_time = config["schedule"]["download_time"]
                        schedule_info[str(config_file)] = download_time
            except Exception as e:
                logger.warning(f"Could not read config file {config_file}: {e}")

        # Check Python files for hardcoded schedules
        for schedule_file in self.schedule_files:
            try:
                with open(schedule_file, "r") as f:
                    content = f.read()

                    # Look for schedule.every().day.at("XX:XX") patterns
                    schedule_patterns = [
                        r'schedule\.every\(\)\.day\.at\("([0-9]{1,2}:[0-9]{2})"\)',
                        r'"download_time":\s*"([0-9]{1,2}:[0-9]{2})"',
                        r"'download_time':\s*'([0-9]{1,2}:[0-9]{2})'",
                    ]

                    found_times = []
                    for pattern in schedule_patterns:
                        matches = re.findall(pattern, content)
                        found_times.extend(matches)

                    if found_times:
                        # Use the last found time (most recent)
                        schedule_info[str(schedule_file)] = found_times[-1]

            except Exception as e:
                logger.warning(f"Could not read schedule file {schedule_file}: {e}")

        return schedule_info

    def update_json_config(self, config_file: Path, new_time: str) -> bool:
        """Update schedule time in JSON configuration file."""
        try:
            with open(config_file, "r") as f:
                config = json.load(f)

            if "schedule" not in config:
                config["schedule"] = {}

            old_time = config["schedule"].get("download_time", "unknown")
            config["schedule"]["download_time"] = new_time

            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)

            logger.info(f"✅ Updated {config_file}: {old_time} → {new_time}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update {config_file}: {e}")
            return False

    def update_python_schedule(self, python_file: Path, new_time: str) -> bool:
        """Update hardcoded schedule time in Python file."""
        try:
            with open(python_file, "r") as f:
                content = f.read()

            # Track changes made
            changes_made = []
            original_content = content

            # Update schedule.every().day.at("XX:XX") patterns
            def replace_schedule_pattern(match):
                old_time = match.group(1)
                changes_made.append(f"{old_time} → {new_time}")
                return match.group(0).replace(old_time, new_time)

            patterns_to_update = [
                (
                    r'(schedule\.every\(\)\.day\.at\(")([0-9]{1,2}:[0-9]{2})("\))',
                    r"\g<1>" + new_time + r"\g<3>",
                ),
                (
                    r'("download_time":\s*")([0-9]{1,2}:[0-9]{2})(")',
                    r"\g<1>" + new_time + r"\g<3>",
                ),
                (
                    r"('download_time':\s*')([0-9]{1,2}:[0-9]{2})(')",
                    r"\g<1>" + new_time + r"\g<3>",
                ),
                # Update print statements with schedule time
                (
                    r'(print\("📅 Scheduled auto downloader for )([0-9]{1,2}:[0-9]{2})( daily"\))',
                    r"\g<1>" + new_time + r"\g<3>",
                ),
                (
                    r'(print\(f"📅 Scheduling daily pipeline to run at )([0-9]{1,2}:[0-9]{2})("\))',
                    r"\g<1>{new_time}" + r"\g<3>",
                ),
            ]

            for pattern, replacement in patterns_to_update:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content

            # Update comment references to schedule time
            comment_patterns = [
                (
                    r"(# Schedule for )([0-9]{1,2}:[0-9]{2})( daily)",
                    r"\g<1>" + new_time + r"\g<3>",
                ),
                (
                    r"(from data download \()([0-9]{1,2}:[0-9]{2})(\))",
                    r"\g<1>" + new_time + r"\g<3>",
                ),
                (
                    r"(📥 )([0-9]{1,2}:[0-9]{2})( - Data Download)",
                    r"\g<1>" + new_time + r"\g<3>",
                ),
                (
                    r"(📈 )([0-9]{1,2}:[0-9]{2})( - Race Trends Analysis)",
                    r"\g<1>" + new_time + r"\g<3>",
                ),
            ]

            for pattern, replacement in comment_patterns:
                content = re.sub(pattern, replacement, content)

            if content != original_content:
                with open(python_file, "w") as f:
                    f.write(content)
                logger.info(
                    f"✅ Updated {python_file}: Schedule time changed to {new_time}"
                )
                return True
            else:
                logger.info(f"ℹ️  No schedule updates needed in {python_file}")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to update {python_file}: {e}")
            return False

    def update_schedule(self, new_time: str, restart_container: bool = True) -> bool:
        """Update schedule time across all configuration files."""
        try:
            new_time = self._normalize_time_format(new_time)
        except ValueError as e:
            logger.error(f"❌ {e}")
            return False

        logger.info(f"🕒 Updating auto-downloader schedule to {new_time}")

        success_count = 0
        total_files = len(self.config_files) + len(self.schedule_files)

        # Update JSON config files
        for config_file in self.config_files:
            if self.update_json_config(config_file, new_time):
                success_count += 1

        # Update Python schedule files
        for schedule_file in self.schedule_files:
            if self.update_python_schedule(schedule_file, new_time):
                success_count += 1

        logger.info(f"📊 Updated {success_count}/{total_files} files successfully")

        if success_count == total_files:
            logger.info("✅ All configuration files updated successfully")

            if restart_container:
                return self.restart_container()
            return True
        else:
            logger.warning("⚠️  Some files could not be updated")
            return False

    def restart_container(self) -> bool:
        """Restart the auto-downloader Docker container."""
        try:
            logger.info("🔄 Restarting auto-downloader container...")

            # Stop container
            subprocess.run(
                ["docker", "stop", "horserace-auto-downloader"],
                check=True,
                capture_output=True,
                text=True,
            )

            # Remove container
            subprocess.run(
                ["docker", "rm", "horserace-auto-downloader"],
                check=True,
                capture_output=True,
                text=True,
            )

            # Rebuild and start container
            subprocess.run(
                [
                    "docker-compose",
                    "-f",
                    "docker-compose.auto-downloader.yml",
                    "up",
                    "-d",
                    "auto-downloader",
                ],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info("✅ Container restarted successfully")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to restart container: {e}")
            logger.error(f"Command output: {e.stderr}")
            return False

    def validate_container_schedule(self) -> bool:
        """Validate that the container is using the correct schedule."""
        try:
            # Check container logs for schedule confirmation
            result = subprocess.run(
                ["docker", "logs", "horserace-auto-downloader", "--tail", "20"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Look for schedule confirmation in logs
            if "📅 Scheduled auto downloader for" in result.stdout:
                logger.info("✅ Container schedule confirmed in logs")
                return True
            else:
                logger.warning("⚠️  Could not confirm schedule in container logs")
                return False

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Could not check container logs: {e}")
            return False

    def show_status(self) -> None:
        """Display current schedule status."""
        print("🕒 Auto-Downloader Schedule Status")
        print("=" * 50)

        current_schedules = self.get_current_schedule()

        if not current_schedules:
            print("❌ No schedule configuration found")
            return

        # Group by time to show consistency
        time_groups = {}
        for file_path, schedule_time in current_schedules.items():
            if schedule_time not in time_groups:
                time_groups[schedule_time] = []
            time_groups[schedule_time].append(file_path)

        for schedule_time, files in time_groups.items():
            print(f"\n⏰ Schedule Time: {schedule_time}")
            for file_path in files:
                print(f"   📄 {Path(file_path).name}")

        if len(time_groups) == 1:
            print(f"\n✅ All configurations consistent: {list(time_groups.keys())[0]}")
        else:
            print(
                f"\n⚠️  Inconsistent schedule times found across {len(time_groups)} different values"
            )

        # Check container status
        print(f"\n🐳 Container Status:")
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=horserace-auto-downloader",
                    "--format",
                    "table {{.Names}}\t{{.Status}}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            if "horserace-auto-downloader" in result.stdout:
                print("   ✅ Container is running")
                self.validate_container_schedule()
            else:
                print("   ❌ Container is not running")
        except subprocess.CalledProcessError:
            print("   ❓ Could not check container status")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Auto-Downloader Schedule Manager CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show current schedule status
  python auto_downloader_scheduler.py status
  
  # Update schedule to 04:00 and restart container
  python auto_downloader_scheduler.py set 04:00
  
  # Update schedule without restarting container
  python auto_downloader_scheduler.py set 06:30 --no-restart
  
  # Restart container with current configuration
  python auto_downloader_scheduler.py restart
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show current schedule status")

    # Set command
    set_parser = subparsers.add_parser("set", help="Set new schedule time")
    set_parser.add_argument(
        "time", help="New schedule time in HH:MM format (e.g., 04:00)"
    )
    set_parser.add_argument(
        "--no-restart",
        action="store_true",
        help="Do not restart container after updating schedule",
    )

    # Restart command
    restart_parser = subparsers.add_parser(
        "restart", help="Restart auto-downloader container"
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate current configuration"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize scheduler
    scheduler = AutoDownloaderScheduler()

    if args.command == "status":
        scheduler.show_status()

    elif args.command == "set":
        restart_container = not args.no_restart
        success = scheduler.update_schedule(
            args.time, restart_container=restart_container
        )
        if success:
            print(f"\n✅ Schedule successfully updated to {args.time}")
            if restart_container:
                print("✅ Container restarted with new schedule")
        else:
            print("\n❌ Failed to update schedule")
            sys.exit(1)

    elif args.command == "restart":
        success = scheduler.restart_container()
        if success:
            print("✅ Container restarted successfully")
        else:
            print("❌ Failed to restart container")
            sys.exit(1)

    elif args.command == "validate":
        scheduler.show_status()
        if scheduler.validate_container_schedule():
            print("\n✅ Configuration is valid")
        else:
            print("\n❌ Configuration validation failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
