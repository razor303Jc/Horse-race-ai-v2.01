#!/usr/bin/env python3
"""
🔗 Data Upload Integration Hook - Enhanced with ML Preprocessing
Automatically runs complete data processing pipeline after every upload

This script integrates with the data upload process to ensure
every new batch of racing data gets:
1. Data relationships fixed (jockey/trainer/course mapping)
2. ML features prepared and scaled (StandardScaler preprocessing)

Two-stage automated workflow:
- Stage 1: Data relationships pipeline (Priority 1A)
- Stage 2: ML feature preprocessing (Priority 1B)

Author: AI Assistant
Date: August 10, 2025
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
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
        self.ml_pipeline_script = (
            self.project_root / "tools" / "ml_pipeline" / "ml_feature_preparation.py"
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
                logger.info("✅ Data relationships pipeline completed successfully")

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

    def run_ml_preprocessing(self) -> bool:
        """Execute the ML feature preparation pipeline after data relationships are fixed."""
        try:
            logger.info("🤖 Starting ML feature preprocessing pipeline...")

            # Build command for ML preprocessing
            cmd = [sys.executable, str(self.ml_pipeline_script)]

            # Run ML pipeline
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=1800  # 30 min timeout
            )

            if result.returncode == 0:
                logger.info("✅ ML preprocessing pipeline completed successfully")

                # Parse output to get key metrics
                output_lines = result.stdout.split("\n")
                ml_metrics = {}
                for line in output_lines:
                    if "Training Data:" in line:
                        # Extract training data metrics
                        try:
                            parts = line.split()
                            samples_idx = next(
                                i for i, part in enumerate(parts) if "samples" in part
                            )
                            ml_metrics["training_samples"] = parts[
                                samples_idx - 1
                            ].replace(",", "")
                        except:
                            pass
                    elif "features" in line and "Training" not in line:
                        try:
                            parts = line.split()
                            features_idx = next(
                                i for i, part in enumerate(parts) if "features" in part
                            )
                            ml_metrics["total_features"] = parts[
                                features_idx - 1
                            ].replace(",", "")
                        except:
                            pass

                # Update status with ML metrics
                ml_status = {
                    "timestamp": datetime.now().isoformat(),
                    "ml_preprocessing_success": True,
                    "ml_metrics": ml_metrics,
                    "stdout": result.stdout[-1000:],
                    "stderr": result.stderr[-1000:] if result.stderr else None,
                }

                # Update or create ML status file
                ml_status_file = (
                    self.project_root / "logs" / "ml_preprocessing_status.json"
                )
                ml_status_file.parent.mkdir(exist_ok=True)
                with open(ml_status_file, "w") as f:
                    json.dump(ml_status, f, indent=2)

                return True
            else:
                logger.error(
                    f"❌ ML preprocessing failed with return code {result.returncode}"
                )
                logger.error(f"stdout: {result.stdout}")
                logger.error(f"stderr: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ ML preprocessing timed out after 30 minutes")
            return False
        except Exception as e:
            logger.error(f"❌ ML preprocessing execution failed: {e}")
            return False

    def post_upload_hook(self) -> bool:
        """Main hook function called after data uploads."""
        logger.info("🔗 Data upload integration hook triggered")

        try:
            # Check if new data requires pipeline run
            if self.check_new_data():
                # Step 1: Run data relationships pipeline
                logger.info("📋 Step 1: Running data relationships pipeline...")
                relationships_success = self.run_pipeline()

                if relationships_success:
                    logger.info("✅ Data relationships processing complete")

                    # Step 2: Run ML preprocessing pipeline
                    logger.info("📋 Step 2: Running ML feature preprocessing...")
                    ml_success = self.run_ml_preprocessing()

                    if ml_success:
                        logger.info("🎉 Complete post-upload processing successful!")
                        logger.info("   ✅ Data relationships fixed")
                        logger.info("   ✅ ML features prepared and scaled")
                        return True
                    else:
                        logger.warning(
                            "⚠️ Data relationships fixed but ML preprocessing failed"
                        )
                        logger.info("   ✅ Data relationships fixed")
                        logger.info("   ❌ ML features preparation failed")
                        # Still return True since core data processing succeeded
                        return True
                else:
                    logger.error("❌ Post-upload data relationships processing failed")
                    logger.info("   ❌ Data relationships processing failed")
                    logger.info("   ⏭️ ML preprocessing skipped")
                    return False

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
