#!/usr/bin/env python3
"""
Real-time Processing Monitor
Horse Racing AI v2.02

Monitors daily pipeline and triggers ML training with fresh data.
Features:
- Real-time data validation monitoring
- Automatic ML training trigger
- Performance optimization tracking
- Race_ID compatibility
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import psycopg2

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/realtime_processor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class RealTimeProcessor:
    """Real-time processing monitor and ML trigger"""

    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "port": 5433,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        self.last_check_time = datetime.now()
        self.last_data_count = 0
        self.monitoring_interval = 300  # 5 minutes

        # Create logs directory
        Path("logs").mkdir(exist_ok=True)

    def get_database_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def check_new_data(self) -> Dict:
        """Check for new data in the database"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()

            # Check current data counts
            cursor.execute("SELECT COUNT(*) FROM races")
            race_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM records")
            record_count = cursor.fetchone()[0]

            # Check latest date
            cursor.execute("SELECT MAX(date) FROM races")
            latest_date = cursor.fetchone()[0]

            # Check recent additions (last hour)
            cursor.execute(
                """
                SELECT COUNT(*) FROM races 
                WHERE date >= CURRENT_DATE
            """
            )
            today_races = cursor.fetchone()[0]

            conn.close()

            data_status = {
                "timestamp": datetime.now(),
                "total_races": race_count,
                "total_records": record_count,
                "latest_race_date": latest_date,
                "today_races": today_races,
                "new_data_detected": record_count > self.last_data_count,
            }

            self.last_data_count = record_count
            return data_status

        except Exception as e:
            logger.error(f"❌ Error checking database: {e}")
            return {"error": str(e)}

    def validate_data_quality(self) -> Dict:
        """Validate data quality for ML training"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()

            # Check data relationships
            cursor.execute(
                """
                SELECT COUNT(*) FROM races r
                INNER JOIN records rec ON r.race_id = rec.race_id
            """
            )
            joined_records = cursor.fetchone()[0]

            # Check data completeness
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN position IS NOT NULL THEN 1 END) as with_position,
                    COUNT(CASE WHEN horse IS NOT NULL THEN 1 END) as with_horse,
                    COUNT(CASE WHEN jockey IS NOT NULL THEN 1 END) as with_jockey
                FROM records
            """
            )
            completeness = cursor.fetchone()

            conn.close()

            quality_score = (joined_records / max(1, completeness[0])) * 100

            return {
                "joined_records": joined_records,
                "total_records": completeness[0],
                "records_with_position": completeness[1],
                "records_with_horse": completeness[2],
                "records_with_jockey": completeness[3],
                "quality_score": quality_score,
                "ml_ready": quality_score > 80 and joined_records > 100,
            }

        except Exception as e:
            logger.error(f"❌ Error validating data quality: {e}")
            return {"error": str(e)}

    def trigger_ml_training(self):
        """Trigger optimized ML training when new data is available"""
        logger.info("🚀 Triggering ML training with fresh data...")

        try:
            import subprocess

            # Run optimized training
            result = subprocess.run(
                ["python", "tools/ml_training/optimized_10_cycle_trainer.py", "--test"],
                capture_output=True,
                text=True,
                cwd="/home/jc/Documents/Horse-race-ai-v2.02",
            )

            if result.returncode == 0:
                logger.info("✅ ML training completed successfully")
                return True
            else:
                logger.error(f"❌ ML training failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Error triggering ML training: {e}")
            return False

    def monitor_realtime(self):
        """Monitor for real-time data updates"""
        logger.info("🔍 Starting real-time monitoring...")
        logger.info(f"📋 Checking every {self.monitoring_interval} seconds")

        try:
            while True:
                # Check for new data
                data_status = self.check_new_data()

                if "error" in data_status:
                    logger.error(f"❌ Monitoring error: {data_status['error']}")
                    time.sleep(60)  # Wait 1 minute on error
                    continue

                logger.info(
                    f"📊 Data Status: {data_status['total_races']} races, "
                    f"{data_status['total_records']} records, "
                    f"Latest: {data_status['latest_race_date']}"
                )

                # Check if new data was detected
                if data_status["new_data_detected"]:
                    logger.info("🆕 New data detected!")

                    # Validate data quality
                    quality = self.validate_data_quality()

                    if "error" not in quality and quality["ml_ready"]:
                        logger.info(
                            f"✅ Data quality good ({quality['quality_score']:.1f}%), "
                            f"triggering ML training..."
                        )
                        self.trigger_ml_training()
                    else:
                        logger.warning(
                            f"⚠️ Data quality needs improvement "
                            f"({quality.get('quality_score', 0):.1f}%)"
                        )

                # Wait for next check
                time.sleep(self.monitoring_interval)

        except KeyboardInterrupt:
            logger.info("🛑 Real-time monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")

    def run_single_check(self):
        """Run single data check and quality validation"""
        logger.info("🔍 Running single data check...")

        data_status = self.check_new_data()
        if "error" in data_status:
            logger.error(f"❌ Data check failed: {data_status['error']}")
            return

        logger.info("📊 Current Data Status:")
        logger.info(f"   Total Races: {data_status['total_races']}")
        logger.info(f"   Total Records: {data_status['total_records']}")
        logger.info(f"   Latest Date: {data_status['latest_race_date']}")
        logger.info(f"   Today's Races: {data_status['today_races']}")

        quality = self.validate_data_quality()
        if "error" not in quality:
            logger.info("🎯 Data Quality Assessment:")
            logger.info(f"   Joined Records: {quality['joined_records']}")
            logger.info(f"   Quality Score: {quality['quality_score']:.1f}%")
            logger.info(f"   ML Ready: {'✅ Yes' if quality['ml_ready'] else '❌ No'}")

            if quality["ml_ready"]:
                logger.info("🚀 Data is ready for ML training!")


def main():
    """Main entry point"""
    import sys

    processor = RealTimeProcessor()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            processor.run_single_check()
        elif sys.argv[1] == "--trigger":
            processor.trigger_ml_training()
        else:
            logger.info(
                "Usage: --check | --trigger | (no args for continuous monitoring)"
            )
    else:
        processor.monitor_realtime()


if __name__ == "__main__":
    main()
