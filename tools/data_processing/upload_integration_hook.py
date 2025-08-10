#!/usr/bin/env python3
"""
🔗 Data Upload Integration Hook
Automatically runs data relationships pipeline after every upload

This script integrates with the data upload process to ensure
every new batch of racing data gets properly processed.

Author: AI Assistant
Date: August 10, 2025
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(project_root / "logs" / "upload_integration.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class DataUploadIntegration:
    """Integration hook for running pipeline after data uploads."""

    def __init__(self):
        self.project_root = project_root
        self.pipeline_script = (
            self.project_root
            / "tools"
            / "data_processing"
            / "automated_relationships_pipeline.py"
        )
        self.config_file = (
            self.project_root / "config" / "data_relationships_pipeline.json"
        )
        self.status_file = self.project_root / "logs" / "last_pipeline_run.json"

    def check_new_data(self) -> bool:
        """Check if new data has been uploaded since last pipeline run."""
        try:
            import psycopg2

            # Connect to database
            conn = psycopg2.connect(
                host="localhost",
                port=5433,
                database="horse_racing_db",
                user="horse_racing",
                password="secure_password_123",
            )
            cursor = conn.cursor()

            # Get latest record timestamp
            cursor.execute(
                """
                SELECT MAX(created_at) FROM race_results
                UNION ALL
                SELECT MAX(created_at) FROM horses
                UNION ALL
                SELECT MAX(created_at) FROM jockey_stats
                UNION ALL
                SELECT MAX(created_at) FROM trainer_stats
                ORDER BY 1 DESC LIMIT 1
            """
            )

            latest_data = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            # Check last pipeline run
            if self.status_file.exists():
                with open(self.status_file, "r") as f:
                    last_run = json.load(f)
                    last_run_time = datetime.fromisoformat(last_run["timestamp"])

                    if latest_data and latest_data > last_run_time:
                        logger.info(
                            f"🆕 New data detected: {latest_data} > {last_run_time}"
                        )
                        return True
                    else:
                        logger.info("ℹ️  No new data since last pipeline run")
                        return False
            else:
                logger.info("🆕 No previous pipeline run found - running pipeline")
                return True

        except Exception as e:
            logger.error(f"❌ Error checking for new data: {e}")
            # Run pipeline on error to be safe
            return True

    def run_pipeline(self) -> bool:
        """Execute the automated relationships pipeline."""
        try:
            logger.info("🚀 Starting automated relationships pipeline...")

            # Build command
            cmd = [
                sys.executable,
                str(self.pipeline_script),
                "--config",
                str(self.config_file),
            ]

            # Run pipeline
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=3600  # 1 hour timeout
            )

            if result.returncode == 0:
                logger.info("✅ Pipeline completed successfully")

                # Update status file
                status = {
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "stdout": result.stdout[-1000:],  # Last 1000 chars
                    "stderr": result.stderr[-1000:] if result.stderr else None,
                }

                with open(self.status_file, "w") as f:
                    json.dump(status, f, indent=2)

                return True
            else:
                logger.error(f"❌ Pipeline failed with return code {result.returncode}")
                logger.error(f"stdout: {result.stdout}")
                logger.error(f"stderr: {result.stderr}")

                # Update status file with failure
                status = {
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }

                with open(self.status_file, "w") as f:
                    json.dump(status, f, indent=2)

                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Pipeline timed out after 1 hour")
            return False
        except Exception as e:
            logger.error(f"❌ Error running pipeline: {e}")
            return False

    def post_upload_hook(self) -> bool:
        """Main hook function called after data uploads."""
        logger.info("🔗 Data upload integration hook triggered")

        try:
            # Check if new data requires pipeline run
            if self.check_new_data():
                success = self.run_pipeline()

                if success:
                    logger.info("🎉 Post-upload data relationships processing complete")
                else:
                    logger.error("❌ Post-upload data relationships processing failed")

                return success
            else:
                logger.info("ℹ️  No pipeline run needed - data is up to date")
                return True

        except Exception as e:
            logger.error(f"❌ Post-upload hook failed: {e}")
            return False


def main():
    """Command line interface for the integration hook."""
    import argparse

    parser = argparse.ArgumentParser(description="Data Upload Integration Hook")
    parser.add_argument(
        "--force", action="store_true", help="Force pipeline run regardless of new data"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check for new data, don't run pipeline",
    )
    args = parser.parse_args()

    integration = DataUploadIntegration()

    if args.check_only:
        has_new_data = integration.check_new_data()
        print(f"New data detected: {has_new_data}")
        return has_new_data

    if args.force:
        print("🔧 Force mode: Running pipeline regardless of new data")
        success = integration.run_pipeline()
    else:
        success = integration.post_upload_hook()

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
