#!/usr/bin/env python3
"""
Manual Pipeline Trigger for Post-Bulk-Upload Processing
======================================================

This script manually triggers all the pipeline stages that should have
run automatically after bulk upload, but didn't due to bypassing the
normal daily file watcher system.

Stages to trigger:
1. Data Relationships Pipeline (jockeys/trainers stats)
2. Performance Tracking (AI model performance)
3. Horse Mapping (cross-database relationships)
4. AI Selections Performance Analysis

Usage:
    python tools/manual_pipeline_trigger.py --all
    python tools/manual_pipeline_trigger.py --stage relationships
    python tools/manual_pipeline_trigger.py --stage performance
    python tools/manual_pipeline_trigger.py --date 2025-08-26
"""

import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime, date
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ManualPipelineTrigger:
    """Manual trigger for pipeline stages after bulk upload"""

    def __init__(self, target_date=None):
        self.project_root = project_root
        self.target_date = target_date or date.today().strftime("%Y-%m-%d")
        self.results = {}

    def run_data_relationships_pipeline(self):
        """Run the automated data relationships pipeline"""
        logger.info("🔄 Starting Data Relationships Pipeline...")

        script_path = (
            self.project_root
            / "tools/data_processing/automated_relationships_pipeline.py"
        )

        if not script_path.exists():
            logger.error(f"❌ Script not found: {script_path}")
            return False

        try:
            # Run with Docker environment for database access
            cmd = [
                "docker",
                "exec",
                "horse_racing_data_pipeline_clean",
                "python",
                "/app/tools/data_processing/automated_relationships_pipeline.py",
            ]

            logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode == 0:
                logger.info("✅ Data Relationships Pipeline completed successfully")
                self.results["relationships"] = {
                    "status": "success",
                    "output": result.stdout,
                }
                return True
            else:
                logger.error(f"❌ Data Relationships Pipeline failed: {result.stderr}")
                self.results["relationships"] = {
                    "status": "failed",
                    "error": result.stderr,
                }
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Data Relationships Pipeline timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error running Data Relationships Pipeline: {e}")
            return False

    def run_performance_tracker(self):
        """Run the daily performance tracker"""
        logger.info("📊 Starting Performance Tracker...")

        script_path = (
            self.project_root / "tools/automation/daily_performance_tracker.py"
        )

        if not script_path.exists():
            logger.error(f"❌ Script not found: {script_path}")
            return False

        try:
            # Run with Docker environment for database access
            cmd = [
                "docker",
                "exec",
                "horse_racing_ml_trainer_clean",
                "python",
                "/app/tools/automation/daily_performance_tracker.py",
            ]

            logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                logger.info("✅ Performance Tracker completed successfully")
                self.results["performance"] = {
                    "status": "success",
                    "output": result.stdout,
                }
                return True
            else:
                logger.error(f"❌ Performance Tracker failed: {result.stderr}")
                self.results["performance"] = {
                    "status": "failed",
                    "error": result.stderr,
                }
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Performance Tracker timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error running Performance Tracker: {e}")
            return False

    def run_horse_mapping(self):
        """Run horse mapping between databases"""
        logger.info("🐎 Starting Horse Mapping...")

        # Check if we have a horse mapping script
        mapping_scripts = [
            "tools/data_processing/smart_relationship_mapper_v2.py",
            "tools/data_processing/fix_data_relationships.py",
        ]

        script_path = None
        for script in mapping_scripts:
            full_path = self.project_root / script
            if full_path.exists():
                script_path = full_path
                break

        if not script_path:
            logger.warning("⚠️ No horse mapping script found, skipping...")
            return True

        try:
            # Run with Docker environment for database access
            cmd = [
                "docker",
                "exec",
                "horse_racing_data_pipeline_clean",
                "python",
                f"/app/{script_path.relative_to(self.project_root)}",
            ]

            logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                logger.info("✅ Horse Mapping completed successfully")
                self.results["mapping"] = {"status": "success", "output": result.stdout}
                return True
            else:
                logger.error(f"❌ Horse Mapping failed: {result.stderr}")
                self.results["mapping"] = {"status": "failed", "error": result.stderr}
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Horse Mapping timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error running Horse Mapping: {e}")
            return False

    def check_database_status_before(self):
        """Check database table counts before processing"""
        logger.info("📋 Checking database status before processing...")

        cmd = [
            "docker",
            "exec",
            "horse_racing_web_app_clean",
            "python",
            "-c",
            """
import psycopg2

# Cards database
conn = psycopg2.connect(
    host='postgres',
    database='cards_horse_racing_db', 
    user='horse_racing',
    password='secure_password_123'
)
cursor = conn.cursor()

tables = ['jockeys_stats', 'trainers_stats', 'ai_model_performance', 'ai_race_summary']
print('BEFORE - Cards DB:')
for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'  {table}: {count} records')

cursor.close()
conn.close()

# Results database  
conn = psycopg2.connect(
    host='postgres',
    database='results_horse_racing_db',
    user='horse_racing', 
    password='secure_password_123'
)
cursor = conn.cursor()

tables = ['horses_mapping', 'ai_selections_performance']
print('BEFORE - Results DB:')
for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'  {table}: {count} records')

cursor.close()
conn.close()
""",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(result.stdout)
            else:
                logger.warning(f"Status check failed: {result.stderr}")
        except Exception as e:
            logger.warning(f"Could not check database status: {e}")

    def check_database_status_after(self):
        """Check database table counts after processing"""
        logger.info("📋 Checking database status after processing...")

        cmd = [
            "docker",
            "exec",
            "horse_racing_web_app_clean",
            "python",
            "-c",
            """
import psycopg2

# Cards database
conn = psycopg2.connect(
    host='postgres',
    database='cards_horse_racing_db',
    user='horse_racing',
    password='secure_password_123'
)
cursor = conn.cursor()

tables = ['jockeys_stats', 'trainers_stats', 'ai_model_performance', 'ai_race_summary']
print('AFTER - Cards DB:')
for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'  {table}: {count} records')

cursor.close()
conn.close()

# Results database
conn = psycopg2.connect(
    host='postgres',
    database='results_horse_racing_db',
    user='horse_racing',
    password='secure_password_123'
)
cursor = conn.cursor()

tables = ['horses_mapping', 'ai_selections_performance']
print('AFTER - Results DB:')
for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'  {table}: {count} records')

cursor.close()
conn.close()
""",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(result.stdout)
            else:
                logger.warning(f"Status check failed: {result.stderr}")
        except Exception as e:
            logger.warning(f"Could not check database status: {e}")

    def run_all_stages(self):
        """Run all pipeline stages in correct order"""
        logger.info(f"🚀 Starting Manual Pipeline Trigger for {self.target_date}")
        logger.info("=" * 60)

        self.check_database_status_before()

        success_count = 0
        total_stages = 3

        # Stage 1: Data Relationships (jockeys/trainers stats)
        if self.run_data_relationships_pipeline():
            success_count += 1

        # Stage 2: Horse Mapping (cross-database relationships)
        if self.run_horse_mapping():
            success_count += 1

        # Stage 3: Performance Tracking (AI model performance)
        if self.run_performance_tracker():
            success_count += 1

        self.check_database_status_after()

        # Summary
        logger.info("=" * 60)
        logger.info(
            f"📊 Pipeline Summary: {success_count}/{total_stages} stages completed successfully"
        )

        if success_count == total_stages:
            logger.info("✅ All pipeline stages completed successfully!")
            return True
        else:
            logger.warning(
                f"⚠️ Only {success_count} out of {total_stages} stages completed"
            )
            return False

    def run_specific_stage(self, stage):
        """Run a specific pipeline stage"""
        logger.info(f"🎯 Running specific stage: {stage}")

        if stage == "relationships":
            return self.run_data_relationships_pipeline()
        elif stage == "performance":
            return self.run_performance_tracker()
        elif stage == "mapping":
            return self.run_horse_mapping()
        else:
            logger.error(f"❌ Unknown stage: {stage}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Manual Pipeline Trigger")
    parser.add_argument("--all", action="store_true", help="Run all pipeline stages")
    parser.add_argument(
        "--stage",
        choices=["relationships", "performance", "mapping"],
        help="Run specific stage",
    )
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)")

    args = parser.parse_args()

    if not args.all and not args.stage:
        parser.print_help()
        return

    trigger = ManualPipelineTrigger(args.date)

    if args.all:
        success = trigger.run_all_stages()
    else:
        success = trigger.run_specific_stage(args.stage)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
