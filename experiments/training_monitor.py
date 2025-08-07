#!/usr/bin/env python3
"""
Training Monitor and Auto-Restart System
Monitors the cyclic training process and automatically restarts if needed.
"""

import os
import sys
import time
import subprocess
import logging
import json
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("training_monitor.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class TrainingMonitor:
    """
    Monitors cyclic training and provides automatic restart capability
    """

    def __init__(self):
        self.training_script = "production_cyclic_training.py"
        self.monitor_interval = 30  # Check every 30 seconds
        self.restart_attempts = 5
        self.current_attempt = 0

        logger.info("🔍 Training Monitor initialized")

    def check_training_status(self):
        """Check if training is running and progressing"""
        try:
            # Check if results file exists and is being updated
            results_file = Path("cyclic_training_results.json")
            if results_file.exists():
                # Check file modification time
                mod_time = results_file.stat().st_mtime
                current_time = time.time()

                # If file was modified in last 5 minutes, training is active
                if current_time - mod_time < 300:  # 5 minutes
                    return True, "Training active - results file recently updated"
                else:
                    return False, "Training stalled - no recent updates"
            else:
                return False, "Results file not found - training may not have started"

        except Exception as e:
            return False, f"Error checking status: {e}"

    def get_training_progress(self):
        """Get current training progress"""
        try:
            results_file = Path("cyclic_training_results.json")
            if results_file.exists():
                with open(results_file, "r") as f:
                    data = json.load(f)

                cycles = data.get("cycles", [])
                if cycles:
                    latest_cycle = cycles[-1]
                    cycle_num = latest_cycle.get("cycle", 0)
                    auc = latest_cycle.get("auc", 0)
                    return cycle_num, auc

            return 0, 0.0

        except Exception as e:
            logger.warning(f"Error getting progress: {e}")
            return 0, 0.0

    def start_training(self):
        """Start the training process"""
        try:
            logger.info("🚀 Starting cyclic training...")

            # Start training as background process
            process = subprocess.Popen(
                [sys.executable, self.training_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            logger.info(f"✅ Training started with PID: {process.pid}")
            return process

        except Exception as e:
            logger.error(f"❌ Failed to start training: {e}")
            return None

    def monitor_and_restart(self):
        """Main monitoring loop with auto-restart"""
        logger.info("🔍 Starting training monitor...")
        logger.info(f"   📊 Check interval: {self.monitor_interval}s")
        logger.info(f"   🔄 Max restart attempts: {self.restart_attempts}")

        training_process = None
        last_cycle = 0
        last_check_time = time.time()

        while self.current_attempt < self.restart_attempts:
            try:
                # Check if we need to start training
                if training_process is None:
                    training_process = self.start_training()
                    if training_process is None:
                        self.current_attempt += 1
                        logger.error(
                            f"Failed to start training. Attempt {self.current_attempt}/{self.restart_attempts}"
                        )
                        time.sleep(60)  # Wait before retry
                        continue

                # Monitor training progress
                time.sleep(self.monitor_interval)

                # Check process status
                if training_process.poll() is not None:
                    # Process has finished
                    stdout, stderr = training_process.communicate()

                    if training_process.returncode == 0:
                        logger.info("🎉 Training completed successfully!")
                        break
                    else:
                        logger.error(
                            f"❌ Training failed with code {training_process.returncode}"
                        )
                        logger.error(f"Error: {stderr}")

                        # Restart training
                        self.current_attempt += 1
                        if self.current_attempt < self.restart_attempts:
                            logger.info(
                                f"🔄 Restarting training. Attempt {self.current_attempt + 1}/{self.restart_attempts}"
                            )
                            training_process = None
                            continue
                        else:
                            logger.error(
                                "❌ Max restart attempts reached. Stopping monitor."
                            )
                            break

                # Check training progress
                current_cycle, current_auc = self.get_training_progress()
                current_time = time.time()

                if current_cycle > last_cycle:
                    logger.info(
                        f"📊 Progress Update: Cycle {current_cycle}, AUC: {current_auc:.4f}"
                    )
                    last_cycle = current_cycle
                    last_check_time = current_time
                elif (
                    current_time - last_check_time > 600
                ):  # 10 minutes without progress
                    logger.warning(
                        "⚠️ No progress detected for 10 minutes. Checking process..."
                    )

                    # Check if process is still running
                    if training_process.poll() is None:
                        logger.info("Process still running, continuing to monitor...")
                        last_check_time = current_time
                    else:
                        logger.error("Process has stopped unexpectedly!")
                        training_process = None

                # Show status every 5 minutes
                if int(current_time) % 300 == 0:
                    status, message = self.check_training_status()
                    logger.info(f"🔍 Status Check: {message}")

            except KeyboardInterrupt:
                logger.info("🛑 Monitor stopped by user")
                if training_process and training_process.poll() is None:
                    logger.info("Terminating training process...")
                    training_process.terminate()
                break

            except Exception as e:
                logger.error(f"❌ Monitor error: {e}")
                time.sleep(30)

        logger.info("🔍 Training monitor finished")

    def show_current_status(self):
        """Show current training status"""
        logger.info("📊 CURRENT TRAINING STATUS")
        logger.info("=" * 40)

        cycle, auc = self.get_training_progress()
        status, message = self.check_training_status()

        logger.info(f"   🔄 Current Cycle: {cycle}/1000")
        logger.info(f"   🎯 Latest AUC: {auc:.4f}")
        logger.info(f"   📊 Status: {message}")

        # Check for log files
        log_files = []
        for file in Path(".").glob("*.log"):
            if file.name.startswith("production_training"):
                log_files.append(file.name)

        if log_files:
            logger.info(f"   📝 Log Files: {', '.join(log_files)}")

        # Check results file
        results_file = Path("cyclic_training_results.json")
        if results_file.exists():
            size = results_file.stat().st_size
            mod_time = datetime.fromtimestamp(results_file.stat().st_mtime)
            logger.info(f"   💾 Results File: {size} bytes, updated {mod_time}")


def main():
    """Main function"""
    monitor = TrainingMonitor()

    # Show initial status
    monitor.show_current_status()

    # Start monitoring with auto-restart
    monitor.monitor_and_restart()


if __name__ == "__main__":
    main()
