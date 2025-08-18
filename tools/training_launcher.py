#!/usr/bin/env python3
"""
🚀 500-Session Training Launcher with Enhanced Monitoring
========================================================

Launches the optimized ML training system for 500 sessions with:
- 10 cycles per session
- Small waits between cycles (1 second)
- Enhanced performance monitoring
- Real-time progress tracking
- Comprehensive reporting
"""

import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/training_launch.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Launch 500-session training with monitoring"""

    logger.info("🚀 LAUNCHING 500-SESSION ML TRAINING")
    logger.info("=" * 60)
    logger.info(f"🕐 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")

    logger.info("📋 TRAINING CONFIGURATION:")
    logger.info("   🎯 Target sessions: 500")
    logger.info("   🔄 Cycles per session: 10")
    logger.info("   📊 Total cycles: 5,000")
    logger.info("   ⏱️  Wait between cycles: 1.0 seconds")
    logger.info("   ⏸️  Wait between sessions: 3.0 seconds")
    logger.info("")

    logger.info("📊 ESTIMATED TIMING:")
    # Based on previous analysis: ~45 seconds per cycle, 10 cycles = ~7.5 minutes per session
    estimated_cycle_time = 45  # seconds
    estimated_session_time = (estimated_cycle_time * 10 + 9 * 1.0) / 60  # minutes
    estimated_total_time = (estimated_session_time + 3.0 / 60) * 500 / 60  # hours

    logger.info(f"   ⏱️  Est. cycle time: {estimated_cycle_time} seconds")
    logger.info(f"   📅 Est. session time: {estimated_session_time:.1f} minutes")
    logger.info(f"   🕐 Est. total time: {estimated_total_time:.1f} hours")
    logger.info("")

    logger.info("🔍 MONITORING FEATURES:")
    logger.info("   📈 Real-time accuracy tracking")
    logger.info("   ⚡ Performance trend analysis")
    logger.info("   📊 Progress charts generation")
    logger.info("   🎯 Milestone celebrations")
    logger.info("   💾 Comprehensive data logging")
    logger.info("")

    # Create necessary directories
    directories = [
        "logs",
        "monitoring",
        "monitoring/charts",
        "results/optimized_training",
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    logger.info("📁 Created monitoring directories")

    # Check database connectivity
    logger.info("🔌 Checking database connectivity...")
    try:
        import psycopg2

        db_config = {
            "host": "localhost",
            "port": 5434,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM races")
        race_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM records")
        record_count = cursor.fetchone()[0]
        conn.close()

        logger.info(f"   ✅ Database connected successfully")
        logger.info(f"   📊 Available races: {race_count:,}")
        logger.info(f"   📋 Available records: {record_count:,}")

    except Exception as e:
        logger.error(f"   ❌ Database connection failed: {e}")
        logger.error(
            "   🔧 Please ensure PostgreSQL is running and database is accessible"
        )
        return False

    logger.info("")
    logger.info("🎯 READY TO START TRAINING!")
    logger.info("=" * 60)

    # Countdown
    for i in range(3, 0, -1):
        logger.info(f"🕐 Starting in {i}...")
        time.sleep(1)

    logger.info("🚀 LAUNCHING ML TRAINING SYSTEM!")
    logger.info("")

    # Import and run the trainer
    try:
        # Add the tools directory to the path to find ml_training
        tools_dir = os.path.dirname(__file__)
        sys.path.insert(0, tools_dir)

        from ml_training.optimized_10_cycle_trainer import OptimizedMLTrainer

        # Create and run trainer
        trainer = OptimizedMLTrainer()
        trainer.run_continuous_training()

        logger.info("")
        logger.info("🏁 TRAINING COMPLETED SUCCESSFULLY!")

    except KeyboardInterrupt:
        logger.info("")
        logger.info("🛑 Training interrupted by user")
        logger.info("📊 Partial results have been saved")

    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        logger.error("🔧 Check logs for detailed error information")
        return False

    logger.info("=" * 60)
    logger.info(f"🕐 End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
