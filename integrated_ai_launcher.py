#!/usr/bin/env python3
"""
🚀 Integrated Horse Racing AI System Launcher
=============================================

Unified launcher that coordinates:
1. 500-session ML training (running in background)
2. Pre-race pipeline for live betting analysis
3. Paper trading system for signal execution
4. Real-time monitoring and reporting

This brings together all components for comprehensive horse racing AI.
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from threading import Thread

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/integrated_system.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class IntegratedHorseRacingAI:
    """Unified system coordinating all horse racing AI components"""

    def __init__(self):
        self.base_dir = Path("/app")
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.base_dir / "logs"

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "live_betting").mkdir(parents=True, exist_ok=True)

        # Component status tracking
        self.components = {
            "ml_training": {"status": "stopped", "process": None},
            "pre_race_pipeline": {"status": "stopped", "process": None},
            "paper_trading": {"status": "stopped", "process": None},
            "monitoring": {"status": "stopped", "process": None},
        }

        logger.info("🚀 Integrated Horse Racing AI System initialized")

    def check_ml_training_status(self) -> dict:
        """Check status of 500-session ML training"""
        try:
            # Check if training container is running
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=horse_racing_ml_trainer_clean",
                    "--format",
                    "{{.Status}}",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and "Up" in result.stdout:
                # Try to get latest training output
                log_result = subprocess.run(
                    ["docker", "logs", "--tail", "10", "horse_racing_ml_trainer_clean"],
                    capture_output=True,
                    text=True,
                )

                if "SESSION" in log_result.stdout:
                    # Extract current session info
                    lines = log_result.stdout.strip().split("\n")
                    for line in reversed(lines):
                        if "SESSION" in line and "COMPLETE" in line:
                            return {
                                "status": "running",
                                "latest_log": line,
                                "container_status": "running",
                            }
                        elif "SESSION" in line and "/" in line:
                            return {
                                "status": "running",
                                "latest_log": line,
                                "container_status": "running",
                            }

                return {
                    "status": "running",
                    "latest_log": "Training active",
                    "container_status": "running",
                }
            else:
                return {
                    "status": "stopped",
                    "latest_log": "Container not running",
                    "container_status": "stopped",
                }

        except Exception as e:
            logger.error(f"❌ Error checking ML training: {e}")
            return {
                "status": "error",
                "latest_log": str(e),
                "container_status": "unknown",
            }

    def run_pre_race_analysis(self):
        """Execute pre-race analysis pipeline"""
        logger.info("🏇 Starting pre-race analysis...")

        try:
            # Import and run the pre-race pipeline
            sys.path.append(str(self.base_dir / "tools" / "live_betting"))
            from pre_race_pipeline import PreRacePipeline

            pipeline = PreRacePipeline()
            pipeline.run_pre_race_analysis()

            logger.info("✅ Pre-race analysis completed")
            return True

        except Exception as e:
            logger.error(f"❌ Pre-race analysis failed: {e}")
            return False

    def run_paper_trading(self):
        """Execute paper trading based on latest signals"""
        logger.info("📈 Starting paper trading execution...")

        try:
            # Import and run paper trading system
            sys.path.append(str(self.base_dir / "tools" / "live_betting"))
            from paper_trading import PaperTradingSystem

            trading_system = PaperTradingSystem()

            # Look for latest signals
            signals_dir = self.data_dir / "live_betting" / "signals"
            if signals_dir.exists():
                signal_files = list(signals_dir.glob("signals_*.json"))
                if signal_files:
                    # Process most recent signals
                    latest_signals = max(signal_files, key=lambda f: f.stat().st_mtime)
                    trading_system.process_betting_signals(str(latest_signals))

                    # Show dashboard
                    trading_system.print_dashboard()
                else:
                    logger.info("📭 No betting signals found")
            else:
                logger.info("📂 Signals directory not found")

            logger.info("✅ Paper trading execution completed")
            return True

        except Exception as e:
            logger.error(f"❌ Paper trading failed: {e}")
            return False

    def monitor_system_health(self):
        """Monitor overall system health and performance"""
        logger.info("👀 Starting system health monitoring...")

        while True:
            try:
                # Check ML training status
                ml_status = self.check_ml_training_status()

                # Log status update every 5 minutes
                logger.info("=" * 60)
                logger.info("🖥️  SYSTEM STATUS UPDATE")
                logger.info("=" * 60)
                logger.info(f"🤖 ML Training: {ml_status['status'].upper()}")
                if ml_status["latest_log"]:
                    logger.info(f"   📊 Latest: {ml_status['latest_log']}")

                # Check disk space
                disk_usage = subprocess.run(
                    ["df", "-h", "/app"], capture_output=True, text=True
                )
                if disk_usage.returncode == 0:
                    lines = disk_usage.stdout.strip().split("\n")
                    if len(lines) > 1:
                        usage_info = lines[1].split()
                        if len(usage_info) >= 5:
                            logger.info(
                                f"💾 Disk Usage: {usage_info[4]} of {usage_info[1]} used"
                            )

                # Check database connectivity
                try:
                    import psycopg2

                    conn = psycopg2.connect(
                        host="horse_racing_postgres_clean",
                        port=5432,
                        database="horse_racing_db",
                        user="horse_racing",
                        password="secure_password_123",
                    )
                    conn.close()
                    logger.info("🗄️  Database: CONNECTED")
                except Exception as db_e:
                    logger.warning(f"🗄️  Database: ERROR - {db_e}")

                logger.info("=" * 60)

                # Sleep for 5 minutes
                time.sleep(300)

            except KeyboardInterrupt:
                logger.info("🛑 System monitoring stopped")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                time.sleep(60)

    def run_integrated_pipeline(self):
        """Run the complete integrated pipeline"""
        logger.info("🚀 LAUNCHING INTEGRATED HORSE RACING AI SYSTEM")
        logger.info("=" * 80)

        try:
            # 1. Check ML training status
            logger.info("1️⃣ Checking ML Training Status...")
            ml_status = self.check_ml_training_status()
            logger.info(f"   Status: {ml_status['status']}")
            logger.info(f"   Details: {ml_status['latest_log']}")

            if ml_status["status"] != "running":
                logger.warning("⚠️ ML training not detected as running")
                logger.info("   You may want to restart the 500-session training")

            # 2. Run pre-race analysis
            logger.info("\n2️⃣ Running Pre-Race Analysis...")
            pre_race_success = self.run_pre_race_analysis()

            if pre_race_success:
                # 3. Execute paper trading
                logger.info("\n3️⃣ Executing Paper Trading...")
                trading_success = self.run_paper_trading()

                if trading_success:
                    logger.info("\n✅ All components executed successfully!")
                else:
                    logger.warning("\n⚠️ Paper trading had issues")
            else:
                logger.warning("\n⚠️ Pre-race analysis had issues")

            # 4. Start monitoring (optional)
            if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
                logger.info("\n4️⃣ Starting Continuous Monitoring...")
                self.monitor_system_health()
            else:
                logger.info(
                    "\n4️⃣ Single execution complete. Use --monitor flag for continuous monitoring."
                )

        except KeyboardInterrupt:
            logger.info("\n🛑 System stopped by user")
        except Exception as e:
            logger.error(f"\n❌ System error: {e}")

    def generate_system_report(self):
        """Generate comprehensive system status report"""
        logger.info("📊 GENERATING SYSTEM REPORT")
        logger.info("=" * 80)

        # ML Training status
        ml_status = self.check_ml_training_status()

        # System resources
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            logger.info(f"🖥️  CPU Usage: {cpu_percent:.1f}%")
            logger.info(
                f"🧠 Memory: {memory.percent:.1f}% used ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)"
            )
            logger.info(
                f"💾 Disk: {disk.percent:.1f}% used ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)"
            )
        except ImportError:
            logger.info("🖥️  System resource monitoring requires psutil")

        # Database status
        try:
            import psycopg2

            conn = psycopg2.connect(
                host="horse_racing_postgres_clean",
                port=5432,
                database="horse_racing_db",
                user="horse_racing",
                password="secure_password_123",
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM races")
            race_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM horses")
            horse_count = cursor.fetchone()[0]
            conn.close()

            logger.info(
                f"🗄️  Database: CONNECTED ({race_count:,} races, {horse_count:,} horses)"
            )
        except Exception as db_e:
            logger.info(f"🗄️  Database: ERROR - {db_e}")

        # ML Training status
        logger.info(f"🤖 ML Training: {ml_status['status'].upper()}")
        if ml_status["latest_log"]:
            logger.info(f"   Latest: {ml_status['latest_log']}")

        # File system status
        live_betting_dir = self.data_dir / "live_betting"
        if live_betting_dir.exists():
            predictions = (
                len(list((live_betting_dir / "predictions").glob("*.json")))
                if (live_betting_dir / "predictions").exists()
                else 0
            )
            signals = (
                len(list((live_betting_dir / "signals").glob("*.json")))
                if (live_betting_dir / "signals").exists()
                else 0
            )
            logger.info(
                f"📁 Live Betting: {predictions} predictions, {signals} signal files"
            )

        logger.info("=" * 80)


def main():
    """Main execution function"""
    system = IntegratedHorseRacingAI()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--report":
            system.generate_system_report()
        elif sys.argv[1] == "--monitor":
            system.run_integrated_pipeline()
        elif sys.argv[1] == "--pre-race":
            system.run_pre_race_analysis()
        elif sys.argv[1] == "--trading":
            system.run_paper_trading()
        else:
            print("Available options:")
            print("  --report     Generate system status report")
            print("  --monitor    Run full pipeline with continuous monitoring")
            print("  --pre-race   Run only pre-race analysis")
            print("  --trading    Run only paper trading")
    else:
        system.run_integrated_pipeline()


if __name__ == "__main__":
    main()
