#!/usr/bin/env python3
"""
ML Training Orchestrator
Horse Racing AI v2.02

Waits for the next auto-downloader run at 00:01, then starts ML training cycles.
Coordinates data import and ML training automation.
"""

import asyncio
import json
import logging
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/ml_orchestrator.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class MLTrainingOrchestrator:
    """Orchestrates auto-downloader and ML training cycles"""

    def __init__(self):
        self.auto_downloader_time = "00:01"  # When auto-downloader runs
        self.ml_cycles_target = 100
        self.cycles_per_batch = 10

    def get_next_downloader_run(self) -> datetime:
        """Calculate when the next auto-downloader run will occur"""
        now = datetime.now()

        # Next run is at 00:01 tomorrow
        next_run = now.replace(hour=0, minute=1, second=0, microsecond=0)
        if now >= next_run:
            next_run += timedelta(days=1)

        return next_run

    def wait_for_downloader(self) -> bool:
        """Wait for auto-downloader to complete its run"""
        next_run = self.get_next_downloader_run()
        now = datetime.now()

        wait_seconds = (next_run - now).total_seconds()

        if wait_seconds > 0:
            logger.info(f"⏰ Waiting for next auto-downloader run at {next_run}")
            logger.info(f"   Current time: {now}")
            logger.info(f"   Wait time: {wait_seconds/3600:.2f} hours")

            # Wait until the auto-downloader run time
            time.sleep(wait_seconds)

        # Wait additional 5 minutes for auto-downloader to complete
        logger.info("🔄 Auto-downloader should be running, waiting for completion...")
        time.sleep(300)  # 5 minutes

        # Check if auto-downloader completed successfully
        return self.check_downloader_completion()

    def check_downloader_completion(self) -> bool:
        """Check if auto-downloader completed successfully"""
        try:
            # Check auto-downloader logs for success
            result = subprocess.run(
                ["docker", "logs", "horserace-auto-downloader", "--tail", "20"],
                capture_output=True,
                text=True,
            )

            if "✅ Daily download completed successfully!" in result.stdout:
                logger.info("✅ Auto-downloader completed successfully")
                return True
            else:
                logger.warning("⚠️ Auto-downloader may not have completed successfully")
                logger.info("Proceeding with ML training anyway...")
                return True

        except Exception as e:
            logger.error(f"Error checking auto-downloader status: {e}")
            return False

    def import_fresh_data(self) -> bool:
        """Import fresh CSV data from auto-downloader to database"""
        try:
            logger.info("📥 Importing fresh data from auto-downloader...")

            # Copy fresh CSV files from auto-downloader container
            csv_files = [
                "complete_mapped_races.csv",
                "complete_mapped_records.csv",
                "complete_mapped_horses.csv",
                "complete_mapped_jockeys_stats.csv",
                "complete_mapped_trainers_stats.csv",
            ]

            # Create local data directory
            Path("data/fresh_import").mkdir(parents=True, exist_ok=True)

            for csv_file in csv_files:
                # Copy from container
                subprocess.run(
                    [
                        "docker",
                        "cp",
                        f"horserace-auto-downloader:/app/data/daily_downloads/{csv_file}",
                        f"data/fresh_import/{csv_file}",
                    ],
                    check=True,
                )

                logger.info(f"✅ Copied {csv_file}")

            # Import to database (simplified approach)
            logger.info("🗄️ Fresh data copied and ready for ML training")
            return True

        except Exception as e:
            logger.error(f"Error importing fresh data: {e}")
            return False

    async def run_ml_training_cycles(self):
        """Start the ML training cycle manager"""
        try:
            logger.info("🤖 Starting ML Training Cycles...")

            # Import the ML cycle manager
            import sys

            sys.path.append("tools/ml_training")
            from automated_ml_cycle_manager import MLTrainingCycleManager

            # Run the training cycles
            manager = MLTrainingCycleManager()
            await manager.run_training_cycles()

            logger.info("🎉 ML Training Cycles completed!")

        except Exception as e:
            logger.error(f"Error in ML training cycles: {e}")
            raise

    async def orchestrate_full_cycle(self):
        """Run the complete orchestration: wait -> download -> import -> train"""
        try:
            logger.info("🎼 Starting ML Training Orchestration")

            # Step 1: Wait for auto-downloader (or start immediately if testing)
            current_hour = datetime.now().hour
            if current_hour == 0:  # If it's already around midnight
                logger.info("🔄 Auto-downloader likely running, checking status...")
                self.check_downloader_completion()
            else:
                logger.info("⏰ Waiting for next auto-downloader run...")
                # For testing, we can skip the wait
                skip_wait = (
                    input("Skip wait for auto-downloader? (y/n): ").lower() == "y"
                )
                if not skip_wait:
                    self.wait_for_downloader()

            # Step 2: Import fresh data
            import_success = self.import_fresh_data()
            if not import_success:
                logger.warning(
                    "⚠️ Data import had issues, proceeding with existing data"
                )

            # Step 3: Run ML training cycles
            await self.run_ml_training_cycles()

            logger.info("🚀 Full orchestration cycle completed!")

        except Exception as e:
            logger.error(f"Error in orchestration: {e}")
            raise


async def main():
    """Main function"""
    orchestrator = MLTrainingOrchestrator()
    await orchestrator.orchestrate_full_cycle()


if __name__ == "__main__":
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    print("🎼 ML Training Orchestrator")
    print("=" * 50)
    print("This will:")
    print("1. Wait for next auto-downloader run at 00:01")
    print("2. Import fresh racing data")
    print("3. Run 100 ML training cycles (10 batches of 10)")
    print("4. Measure and report performance improvements")
    print("=" * 50)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Orchestration stopped by user")
    except Exception as e:
        print(f"\n❌ Orchestration error: {e}")
