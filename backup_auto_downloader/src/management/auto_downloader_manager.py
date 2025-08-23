#!/usr/bin/env python3
"""
Auto-Downloader Management System
Horse Racing AI v2.0

Manages auto-downloader processes and transitions to live feeds.
"""

import os
import signal
import psutil
import logging
from typing import List, Dict, Any
from datetime import datetime
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AutoDownloaderManager:
    """Manages auto-downloader processes and configuration"""

    def __init__(self):
        self.config_file = "config/auto_downloader_config.json"
        self.disabled_processes = []
        self.running_processes = []

    def find_auto_downloader_processes(self) -> List[Dict[str, Any]]:
        """Find all running auto-downloader processes"""
        processes = []

        # Keywords that identify auto-downloader processes
        keywords = [
            "playwright",
            "scraper",
            "auto_download",
            "enhanced_auto_download",
            "enhanced_playwright",
            "download_demo",
            "betdaq_demo",
            "generate_race",
        ]

        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = " ".join(proc.info["cmdline"]) if proc.info["cmdline"] else ""

                # Check if any keyword is in the command line
                for keyword in keywords:
                    if keyword in cmdline.lower():
                        # Exclude this script itself
                        if "auto_downloader_manager" not in cmdline:
                            processes.append(
                                {
                                    "pid": proc.info["pid"],
                                    "name": proc.info["name"],
                                    "cmdline": cmdline,
                                    "keyword": keyword,
                                }
                            )
                            break

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return processes

    def terminate_auto_downloaders(self) -> Dict[str, Any]:
        """Terminate all running auto-downloader processes"""
        processes = self.find_auto_downloader_processes()
        results = {"terminated": [], "failed": [], "total_found": len(processes)}

        if not processes:
            logger.info("✅ No auto-downloader processes found")
            return results

        logger.info(f"🔍 Found {len(processes)} auto-downloader processes")

        for proc_info in processes:
            try:
                pid = proc_info["pid"]
                process = psutil.Process(pid)

                logger.info(f"🛑 Terminating PID {pid}: {proc_info['name']}")

                # Try graceful termination first
                process.terminate()

                # Wait up to 5 seconds for graceful termination
                try:
                    process.wait(timeout=5)
                    results["terminated"].append(proc_info)
                    logger.info(f"✅ Gracefully terminated PID {pid}")

                except psutil.TimeoutExpired:
                    # Force kill if graceful termination fails
                    logger.warning(f"⚠️ Forcing termination of PID {pid}")
                    process.kill()
                    results["terminated"].append(proc_info)
                    logger.info(f"💀 Force killed PID {pid}")

            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.error(f"❌ Failed to terminate PID {proc_info['pid']}: {e}")
                results["failed"].append({**proc_info, "error": str(e)})

        logger.info(f"🎯 Terminated {len(results['terminated'])} processes")
        return results

    def disable_auto_downloader_scripts(self) -> Dict[str, Any]:
        """Disable auto-downloader scripts by renaming them"""
        script_patterns = [
            "demos/*auto_download*.py",
            "demos/*playwright*.py",
            "demos/*scraper*.py",
            "src/scrapers/*.py",
            "scripts/*download*.sh",
        ]

        disabled_files = []
        failed_files = []

        import glob

        for pattern in script_patterns:
            files = glob.glob(pattern)

            for file_path in files:
                try:
                    # Skip if already disabled
                    if file_path.endswith(".disabled"):
                        continue

                    disabled_path = f"{file_path}.disabled"
                    os.rename(file_path, disabled_path)
                    disabled_files.append(
                        {"original": file_path, "disabled": disabled_path}
                    )
                    logger.info(f"🚫 Disabled: {file_path}")

                except OSError as e:
                    failed_files.append({"file": file_path, "error": str(e)})
                    logger.error(f"❌ Failed to disable {file_path}: {e}")

        return {
            "disabled": disabled_files,
            "failed": failed_files,
            "total_disabled": len(disabled_files),
        }

    def create_live_feed_config(self) -> str:
        """Create configuration for live feed system"""
        config = {
            "live_feeds": {
                "enabled": True,
                "primary_source": "racing_post",
                "fallback_sources": ["timeform", "betfair"],
                "update_interval_minutes": 15,
                "data_retention_days": 30,
            },
            "auto_downloaders": {
                "enabled": False,
                "disabled_timestamp": datetime.now().isoformat(),
                "disabled_reason": "Replaced with live feed integration",
            },
            "monte_carlo": {
                "enabled": True,
                "real_time_analysis": True,
                "notification_threshold": 0.25,
            },
            "ntfy": {
                "enabled": True,
                "live_feed_alerts": True,
                "race_analysis_alerts": True,
            },
        }

        # Ensure config directory exists
        os.makedirs("config", exist_ok=True)

        config_path = "config/live_feed_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"✅ Created live feed configuration: {config_path}")
        return config_path

    def run_transition_to_live_feeds(self) -> Dict[str, Any]:
        """Complete transition from auto-downloaders to live feeds"""
        logger.info("🔄 Starting transition to live feeds...")

        results = {"timestamp": datetime.now().isoformat(), "transition_steps": {}}

        # Step 1: Terminate running auto-downloaders
        logger.info("📍 Step 1: Terminating auto-downloaders")
        termination_result = self.terminate_auto_downloaders()
        results["transition_steps"]["termination"] = termination_result

        # Step 2: Disable auto-downloader scripts
        logger.info("📍 Step 2: Disabling auto-downloader scripts")
        disable_result = self.disable_auto_downloader_scripts()
        results["transition_steps"]["script_disabling"] = disable_result

        # Step 3: Create live feed configuration
        logger.info("📍 Step 3: Creating live feed configuration")
        config_path = self.create_live_feed_config()
        results["transition_steps"]["configuration"] = {
            "config_file": config_path,
            "status": "created",
        }

        # Summary
        total_terminated = termination_result["total_found"]
        total_disabled = disable_result["total_disabled"]

        logger.info("🎉 TRANSITION COMPLETE!")
        logger.info(f"   🛑 Terminated: {total_terminated} processes")
        logger.info(f"   🚫 Disabled: {total_disabled} scripts")
        logger.info(f"   ⚙️  Configuration: {config_path}")
        logger.info("   🔄 System ready for live feed integration")

        results["summary"] = {
            "status": "success",
            "processes_terminated": total_terminated,
            "scripts_disabled": total_disabled,
            "config_created": True,
            "ready_for_live_feeds": True,
        }

        return results

    def status_report(self) -> Dict[str, Any]:
        """Generate a status report of the current system state"""
        # Check for running auto-downloaders
        running_downloaders = self.find_auto_downloader_processes()

        # Check if live feed config exists
        live_feed_config_exists = os.path.exists("config/live_feed_config.json")

        # Check disabled scripts
        import glob

        disabled_scripts = glob.glob("**/*.disabled", recursive=True)

        report = {
            "timestamp": datetime.now().isoformat(),
            "auto_downloaders": {
                "running_processes": len(running_downloaders),
                "processes": running_downloaders,
            },
            "live_feeds": {
                "config_exists": live_feed_config_exists,
                "ready_for_integration": live_feed_config_exists
                and len(running_downloaders) == 0,
            },
            "disabled_scripts": {
                "count": len(disabled_scripts),
                "files": disabled_scripts,
            },
            "system_status": (
                "ready_for_live_feeds"
                if (live_feed_config_exists and len(running_downloaders) == 0)
                else "transition_needed"
            ),
        }

        return report

    def print_status_report(self):
        """Print a formatted status report"""
        report = self.status_report()

        print("\n" + "=" * 60)
        print("🔍 AUTO-DOWNLOADER SYSTEM STATUS REPORT")
        print("=" * 60)

        print(f"📅 Report Time: {report['timestamp']}")

        # Auto-downloaders status
        running_count = report["auto_downloaders"]["running_processes"]
        if running_count == 0:
            print("✅ Auto-downloaders: All terminated")
        else:
            print(f"⚠️  Auto-downloaders: {running_count} still running")
            for proc in report["auto_downloaders"]["processes"]:
                print(f"   🔄 PID {proc['pid']}: {proc['name']}")

        # Live feeds status
        if report["live_feeds"]["config_exists"]:
            print("✅ Live feed config: Created")
        else:
            print("❌ Live feed config: Missing")

        if report["live_feeds"]["ready_for_integration"]:
            print("🚀 System Status: READY FOR LIVE FEEDS")
        else:
            print("⚠️  System Status: TRANSITION NEEDED")

        # Disabled scripts
        disabled_count = report["disabled_scripts"]["count"]
        print(f"🚫 Disabled scripts: {disabled_count}")

        print("=" * 60)

        return report


def main():
    """Main execution function"""
    manager = AutoDownloaderManager()

    print("🚀 Auto-Downloader Management System")
    print("🔄 Transitioning to Live Feed Integration")

    # Get initial status
    print("\n📊 INITIAL STATUS:")
    manager.print_status_report()

    # Perform transition
    print("\n🔄 PERFORMING TRANSITION...")
    results = manager.run_transition_to_live_feeds()

    # Show final status
    print("\n📊 FINAL STATUS:")
    final_report = manager.print_status_report()

    # Save transition log
    log_file = f"logs/auto_downloader_transition_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("logs", exist_ok=True)

    with open(log_file, "w") as f:
        json.dump(
            {"transition_results": results, "final_status": final_report}, f, indent=2
        )

    print(f"\n📁 Transition log saved: {log_file}")

    if final_report["system_status"] == "ready_for_live_feeds":
        print("\n🎉 SUCCESS: System ready for live feed integration!")
        print("   Next steps:")
        print("   1. Configure API keys for Racing Post/Timeform")
        print("   2. Test live feed connections")
        print("   3. Start live data monitoring")
    else:
        print("\n⚠️  ATTENTION: Manual intervention may be required")


if __name__ == "__main__":
    main()
