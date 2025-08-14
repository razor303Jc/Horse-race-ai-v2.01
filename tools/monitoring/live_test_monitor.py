#!/usr/bin/env python3
"""
🔴 LIVE TEST MONITOR - Auto-Downloader at 06:01
Track performance and results of the live test
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("live_test_monitor.log")],
)
logger = logging.getLogger(__name__)


class LiveTestMonitor:
    """Monitor the live test performance at 06:01"""

    def __init__(self):
        self.test_start_time = "06:01"
        self.stage_schedule = {
            "06:01": "Data Download",
            "11:30": "Data Relationships",
            "12:00": "Contextual Analysis",
            "12:30": "Form Scoring",
            "13:00": "Power Ratings",
            "13:30": "Speed Analysis",
            "14:00": "Monte Carlo",
            "14:30": "ML Training",
            "15:00": "Race Trends",
            "15:30": "Composite Scoring",
            "16:00": "Betting Strategies",
            "16:30": "Report Generation",
            "17:00": "AI Selections",
            "17:30": "Pre-race Updates",
            "20:00": "Performance Analysis",
        }

    def get_time_until_test(self):
        """Calculate time until 06:01 test"""
        now = datetime.now()
        today_test = now.replace(hour=11, minute=1, second=0, microsecond=0)

        if now > today_test:
            # Test time has passed today, calculate for tomorrow
            tomorrow_test = today_test + timedelta(days=1)
            return tomorrow_test - now
        else:
            return today_test - now

    def check_container_status(self):
        """Check if auto-downloader container is ready"""
        import subprocess

        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=horserace-auto-downloader",
                    "--format",
                    "{{.Status}}",
                ],
                capture_output=True,
                text=True,
            )
            return "Up" in result.stdout and "healthy" in result.stdout
        except Exception as e:
            logger.error(f"Error checking container status: {e}")
            return False

    def check_database_connection(self):
        """Check if database is accessible"""
        try:
            import psycopg2

            conn = psycopg2.connect(
                host="localhost",
                port=5433,
                database="horse_racing_db",
                user="horse_racing",
                password="secure_password_123",
            )
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    def get_current_stage(self):
        """Get the current expected pipeline stage"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # Find the most recent stage that should have started
        active_stage = None
        for time_str, stage in self.pipeline_schedule.items():
            if current_time >= time_str:
                active_stage = f"{time_str} - {stage}"

        return active_stage or "Pre-test phase"

    async def monitor_live_test(self):
        """Monitor the live test progress"""
        logger.info("🔴 LIVE TEST MONITOR STARTED")
        logger.info("=" * 50)

        # Check system readiness
        container_ready = self.check_container_status()
        db_ready = self.check_database_connection()

        logger.info(
            f"Auto-downloader Container: {'✅ READY' if container_ready else '❌ NOT READY'}"
        )
        logger.info(
            f"Database Connection: {'✅ READY' if db_ready else '❌ NOT READY'}"
        )

        if not (container_ready and db_ready):
            logger.error("❌ System not ready for live test!")
            return

        # Show time until test
        time_until = self.get_time_until_test()
        if time_until.total_seconds() > 0:
            hours, remainder = divmod(int(time_until.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            logger.info(f"⏰ Time until test: {hours:02d}:{minutes:02d}:{seconds:02d}")
        else:
            logger.info("🚀 Test time has arrived or passed!")

        # Show current expected stage
        current_stage = self.get_current_stage()
        logger.info(f"📊 Current Stage: {current_stage}")

        # Monitor progress
        logger.info("\n🔄 Monitoring pipeline progress...")
        logger.info("Will check every 5 minutes for updates...")

        while True:
            await asyncio.sleep(300)  # Check every 5 minutes

            now = datetime.now()
            current_stage = self.get_current_stage()
            logger.info(
                f"⏰ {now.strftime('%H:%M:%S')} - Current Stage: {current_stage}"
            )

            # Check if we're in the test window (06:01 - 20:30)
            if now.hour >= 11 and now.hour < 21:
                # Monitor container logs for activity
                try:
                    import subprocess

                    result = subprocess.run(
                        ["docker", "logs", "--tail", "5", "horserace-auto-downloader"],
                        capture_output=True,
                        text=True,
                    )
                    if result.stdout:
                        logger.info("📋 Recent auto-downloader activity:")
                        for line in result.stdout.strip().split("\n")[-3:]:
                            logger.info(f"   {line}")
                except Exception as e:
                    logger.warning(f"Could not check container logs: {e}")

    def get_test_summary(self):
        """Generate a summary of test readiness"""
        summary = {
            "test_time": "06:01 BST",
            "container_status": self.check_container_status(),
            "database_status": self.check_database_connection(),
            "time_until_test": str(self.get_time_until_test()),
            "pipeline_stages": len(self.pipeline_schedule),
            "estimated_completion": "20:00 BST",
        }
        return summary


async def main():
    """Main monitoring function"""
    monitor = LiveTestMonitor()

    print("🔴 LIVE TEST MONITOR")
    print("=" * 40)
    print("Auto-downloader scheduled for 06:01 BST")
    print("Complete 17-stage pipeline will execute")
    print("")

    # Show test summary
    summary = monitor.get_test_summary()
    print(f"Test Time: {summary['test_time']}")
    print(f"Container Ready: {'✅' if summary['container_status'] else '❌'}")
    print(f"Database Ready: {'✅' if summary['database_status'] else '❌'}")
    print(f"Pipeline Stages: {summary['pipeline_stages']}")
    print(f"Est. Completion: {summary['estimated_completion']}")
    print("")

    # Start monitoring
    await monitor.monitor_live_test()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Live test monitoring stopped")
    except Exception as e:
        print(f"❌ Monitor error: {e}")
        sys.exit(1)
