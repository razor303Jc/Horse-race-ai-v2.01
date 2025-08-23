#!/usr/bin/env python3
"""
# REMOVED: 🕒 Auto-Downloader Schedule Manager CLI
=====================================

# REMOVED: A command-line tool to manage the auto-downloader's scheduled start time.

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
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ScheduleManager:
# REMOVED:     """Manages auto-downloader scheduling configuration."""

    def __init__(self):
        """Initialize the scheduler manager."""
        self.project_root = Path(__file__).parent.parent.parent

    def get_config_files(self) -> List[Path]:
        """Get all configuration files."""
        patterns = [
            "config/daily_pipeline_config*.json",
            "config/config/daily_pipeline_config*.json",
        ]
        files = []
        for pattern in patterns:
            files.extend(self.project_root.glob(pattern))
        return [f for f in files if f.exists()]

    def get_schedule_files(self) -> List[Path]:
        """Get Python files with schedule definitions."""
        files = [
# REMOVED:             "run_docker_auto_downloader.py",  # Root file used by Docker
# REMOVED:             "tools/utilities/run_docker_auto_downloader.py",
# REMOVED:             "docker/automation/run_docker_auto_downloader.py",
        ]
        return [
            self.project_root / f for f in files if (self.project_root / f).exists()
        ]

    def validate_time(self, time_str: str) -> str:
        """Validate and normalize time format."""
        pattern = r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
        if not re.match(pattern, time_str):
            raise ValueError(f"Invalid time format: {time_str}")

        hour, minute = time_str.split(":")
        return f"{int(hour):02d}:{int(minute):02d}"

    def get_current_schedules(self) -> Dict[str, str]:
        """Get current schedule from all sources."""
        schedules = {}

        # Check JSON configs
        for config_file in self.get_config_files():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                    if "schedule" in config and "download_time" in config["schedule"]:
                        time_val = config["schedule"]["download_time"]
                        schedules[str(config_file)] = time_val
            except Exception as e:
                logger.warning(f"Could not read {config_file}: {e}")

        # Check Python files
        for schedule_file in self.get_schedule_files():
            try:
                with open(schedule_file, "r") as f:
                    content = f.read()

                patterns = [
                    r'schedule\.every\(\)\.day\.at\("([0-9]{1,2}:[0-9]{2})"\)',
                    r'"download_time":\s*"([0-9]{1,2}:[0-9]{2})"',
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        schedules[str(schedule_file)] = matches[-1]
                        break

            except Exception as e:
                logger.warning(f"Could not read {schedule_file}: {e}")

        return schedules

    def update_json_config(self, config_file: Path, new_time: str) -> bool:
        """Update JSON configuration file."""
        try:
            with open(config_file, "r") as f:
                config = json.load(f)

            if "schedule" not in config:
                config["schedule"] = {}

            old_time = config["schedule"].get("download_time", "unknown")
            config["schedule"]["download_time"] = new_time

            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)

            logger.info(f"Updated {config_file.name}: {old_time} → {new_time}")
            return True

        except Exception as e:
            logger.error(f"Failed to update {config_file}: {e}")
            return False

    def update_python_file(self, python_file: Path, new_time: str) -> bool:
        """Update Python file with new schedule time."""
        try:
            with open(python_file, "r") as f:
                content = f.read()

            original_content = content

            # Update patterns
            patterns = [
                # schedule.every().day.at("XX:XX")
                (
                    r'(schedule\.every\(\)\.day\.at\(")([0-9]{1,2}:[0-9]{2})("\))',
                    rf"\g<1>{new_time}\g<3>",
                ),
                # "download_time": "XX:XX"
                (
                    r'("download_time":\s*")([0-9]{1,2}:[0-9]{2})(")',
                    rf"\g<1>{new_time}\g<3>",
                ),
                # Print statements
                (
                    r"(Scheduled auto downloader for )([0-9]{1,2}:[0-9]{2})( daily)",
                    rf"\g<1>{new_time}\g<3>",
                ),
                # Comments
                (
                    r"(# Schedule for )([0-9]{1,2}:[0-9]{2})( daily)",
                    rf"\g<1>{new_time}\g<3>",
                ),
            ]

            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

            if content != original_content:
                with open(python_file, "w") as f:
                    f.write(content)
                logger.info(f"Updated {python_file.name}")
                return True
            else:
                logger.info(f"No updates needed in {python_file.name}")
                return True

        except Exception as e:
            logger.error(f"Failed to update {python_file}: {e}")
            return False

    def update_schedule(self, new_time: str, restart: bool = True) -> bool:
        """Update schedule across all files."""
        try:
            new_time = self.validate_time(new_time)
        except ValueError as e:
            logger.error(str(e))
            return False

        logger.info(f"Updating schedule to {new_time}")

        success_count = 0

        # Update JSON files
        for config_file in self.get_config_files():
            if self.update_json_config(config_file, new_time):
                success_count += 1

        # Update Python files
        for schedule_file in self.get_schedule_files():
            if self.update_python_file(schedule_file, new_time):
                success_count += 1

        total_files = len(self.get_config_files()) + len(self.get_schedule_files())

        if success_count == total_files:
            logger.info("All files updated successfully")
            if restart:
                return self.restart_container()
            return True
        else:
            logger.warning(f"Only {success_count}/{total_files} files updated")
            return False

    def restart_container(self) -> bool:
# REMOVED:         """Restart the auto-downloader container."""
        try:
            logger.info("Restarting container...")

            # Stop and remove
            subprocess.run(
# REMOVED:                 ["docker", "stop", "horse_racing_auto_downloader_clean"],
                check=True,
                capture_output=True,
            )
            subprocess.run(
# REMOVED:                 ["docker", "rm", "horse_racing_auto_downloader_clean"],
                check=True,
                capture_output=True,
            )

            # Start new container
            cmd = [
                "docker-compose",
                "-f",
                "docker-compose.clean.yml",
                "up",
                "-d",
# REMOVED:                 "auto-downloader",
            ]
            subprocess.run(cmd, cwd=self.project_root, check=True, capture_output=True)

            logger.info("Container restarted successfully")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to restart container: {e}")
            return False

    def show_status(self) -> None:
        """Display current schedule status."""
# REMOVED:         print("🕒 Auto-Downloader Schedule Status")
        print("=" * 40)

        schedules = self.get_current_schedules()

        if not schedules:
            print("❌ No schedule configuration found")
            return

        # Group by time
        time_groups = {}
        for file_path, time_val in schedules.items():
            if time_val not in time_groups:
                time_groups[time_val] = []
            time_groups[time_val].append(Path(file_path).name)

        for time_val, files in time_groups.items():
            print(f"\n⏰ Schedule: {time_val}")
            for file_name in files:
                print(f"   📄 {file_name}")

        if len(time_groups) == 1:
            print(f"\n✅ Consistent schedule: {list(time_groups.keys())[0]}")
        else:
            print(f"\n⚠️  Found {len(time_groups)} different schedule times")

        # Check container
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
# REMOVED:                     "name=horse_racing_auto_downloader_clean",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
# REMOVED:             if "horse_racing_auto_downloader_clean" in result.stdout:
                print("\n🐳 Container: ✅ Running")
            else:
                print("\n🐳 Container: ❌ Not running")
        except subprocess.CalledProcessError:
            print("\n🐳 Container: ❓ Status unknown")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
# REMOVED:         description="Auto-Downloader Schedule Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python schedule_manager.py status
  python schedule_manager.py set 04:00
  python schedule_manager.py set 06:30 --no-restart
  python schedule_manager.py restart
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Status command
    subparsers.add_parser("status", help="Show current schedule")

    # Set command
    set_parser = subparsers.add_parser("set", help="Set new schedule time")
    set_parser.add_argument("time", help="Time in HH:MM format")
    set_parser.add_argument(
        "--no-restart", action="store_true", help="Skip container restart"
    )

    # Restart command
    subparsers.add_parser("restart", help="Restart container")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = ScheduleManager()

    if args.command == "status":
        manager.show_status()

    elif args.command == "set":
        restart = not args.no_restart
        if manager.update_schedule(args.time, restart):
            print(f"\n✅ Schedule updated to {args.time}")
        else:
            print("\n❌ Failed to update schedule")
            sys.exit(1)

    elif args.command == "restart":
        if manager.restart_container():
            print("✅ Container restarted")
        else:
            print("❌ Failed to restart container")
            sys.exit(1)


if __name__ == "__main__":
    main()
