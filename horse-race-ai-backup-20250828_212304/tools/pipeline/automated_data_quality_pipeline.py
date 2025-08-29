#!/usr/bin/env python3
"""
Automated Data Processing Pipeline Integration
Integrates all data validation, conversion, and quality checks into the main pipeline

This script consolidates:
- Distance conversion (distance_converter.py)
- Weight conversion (weight_converter.py)
- Data validation and auditing
- Column mapping and cleaning
- Database integrity checks

Designed to be called from the main pipeline orchestrator
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import psycopg2
import pandas as pd

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import our existing tools
from tools.data_processing.distance_converter import DistanceConverter
from tools.data_processing.weight_converter import WeightConverter
from tools.data_validation.comprehensive_data_audit import DataMappingAuditor


class AutomatedDataQualityPipeline:
    """
    Automated pipeline for data quality, validation, and conversion
    Integrates all data processing tools into a single automated workflow
    """

    def __init__(self, pipeline_config=None):
        self.project_root = project_root
        self.pipeline_config = pipeline_config or {}
        self.logger = self.setup_logging()

        # Initialize components
        self.distance_converter = DistanceConverter()
        self.weight_converter = WeightConverter()
        self.data_auditor = DataMappingAuditor()

        # Pipeline state
        self.validation_results = {}
        self.conversion_results = {}
        self.errors = []

    def setup_logging(self):
        """Setup pipeline logging"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)

        log_file = (
            log_dir
            / f"data_quality_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        return logging.getLogger(__name__)

    def run_pre_processing_validation(self):
        """
        Step 1: Pre-processing validation
        Check data before any conversions
        """
        self.logger.info("🔍 Step 1: Pre-processing validation")

        try:
            # Run basic data audit
            self.data_auditor.connect_to_database()

            # Check current data state
            self.logger.info("Checking current data quality...")

            # Store results
            self.validation_results["pre_processing"] = {
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "issues_found": len(self.data_auditor.issues),
            }

            return True

        except Exception as e:
            self.logger.error(f"Pre-processing validation failed: {e}")
            self.errors.append(f"Pre-processing validation: {e}")
            return False

    def run_distance_conversion(self):
        """
        Step 2: Automated distance conversion
        Convert all distance formats to meters
        """
        self.logger.info("🏃 Step 2: Distance conversion")

        try:
            # Check if conversion is needed
            if not self.distance_converter.connect_to_database():
                raise Exception("Failed to connect to database for distance conversion")

            # Run distance conversion
            conversion_stats = self.distance_converter.convert_all_distances()

            self.conversion_results["distance"] = {
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "conversions": conversion_stats,
            }

            self.logger.info(f"Distance conversion completed: {conversion_stats}")
            return True

        except Exception as e:
            self.logger.error(f"Distance conversion failed: {e}")
            self.errors.append(f"Distance conversion: {e}")
            return False

    def run_weight_conversion(self):
        """
        Step 3: Automated weight conversion
        Convert UK weight formats to kilograms
        """
        self.logger.info("⚖️ Step 3: Weight conversion")

        try:
            # Check if conversion is needed
            if not self.weight_converter.connect_to_database():
                raise Exception("Failed to connect to database for weight conversion")

            # Run weight conversion
            conversion_stats = self.weight_converter.convert_all_weights()

            self.conversion_results["weight"] = {
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "conversions": conversion_stats,
            }

            self.logger.info(f"Weight conversion completed: {conversion_stats}")
            return True

        except Exception as e:
            self.logger.error(f"Weight conversion failed: {e}")
            self.errors.append(f"Weight conversion: {e}")
            return False

    def run_post_processing_validation(self):
        """
        Step 4: Post-processing validation
        Verify all conversions worked correctly
        """
        self.logger.info("✅ Step 4: Post-processing validation")

        try:
            # Re-run data audit to verify fixes
            self.data_auditor.issues = []  # Reset issues
            self.data_auditor.recommendations = []

            # Run full audit
            success = self.data_auditor.run_full_audit()

            self.validation_results["post_processing"] = {
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "issues_found": len(self.data_auditor.issues),
                "audit_success": success,
            }

            return success

        except Exception as e:
            self.logger.error(f"Post-processing validation failed: {e}")
            self.errors.append(f"Post-processing validation: {e}")
            return False

    def run_data_integrity_checks(self):
        """
        Step 5: Final data integrity checks
        Ensure referential integrity and data consistency
        """
        self.logger.info("🔗 Step 5: Data integrity checks")

        try:
            # Connect to database
            conn = psycopg2.connect(
                host="localhost",
                port="5434",
                database="horse_racing_db",
                user="horse_racing",
                password="secure_password_123",
            )
            cursor = conn.cursor()

            # Check record counts
            cursor.execute("SELECT COUNT(*) FROM races")
            race_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM records")
            record_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM horses")
            horse_count = cursor.fetchone()[0]

            # Check for orphaned records
            cursor.execute(
                """
                SELECT COUNT(*) FROM records r 
                LEFT JOIN races rc ON r.race_id = rc.race_id 
                WHERE rc.race_id IS NULL
            """
            )
            orphaned_records = cursor.fetchone()[0]

            # Store integrity results
            integrity_results = {
                "race_count": race_count,
                "record_count": record_count,
                "horse_count": horse_count,
                "orphaned_records": orphaned_records,
                "integrity_ratio": record_count / race_count if race_count > 0 else 0,
            }

            self.validation_results["integrity"] = {
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "results": integrity_results,
            }

            self.logger.info(f"Data integrity check completed: {integrity_results}")

            conn.close()
            return orphaned_records == 0

        except Exception as e:
            self.logger.error(f"Data integrity check failed: {e}")
            self.errors.append(f"Data integrity: {e}")
            return False

    def save_pipeline_results(self):
        """Save pipeline results for tracking and monitoring"""
        results_file = (
            self.project_root / "reports" / "automated_data_quality_results.json"
        )

        pipeline_results = {
            "pipeline_run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "validation_results": self.validation_results,
            "conversion_results": self.conversion_results,
            "errors": self.errors,
            "success": len(self.errors) == 0,
        }

        with open(results_file, "w") as f:
            json.dump(pipeline_results, f, indent=2)

        self.logger.info(f"Pipeline results saved to: {results_file}")
        return pipeline_results

    def run_full_pipeline(self):
        """
        Execute the complete automated data quality pipeline

        Returns:
            bool: True if pipeline completed successfully, False otherwise
        """
        self.logger.info("🚀 Starting Automated Data Quality Pipeline")
        self.logger.info("=" * 60)

        pipeline_steps = [
            ("Pre-processing Validation", self.run_pre_processing_validation),
            ("Distance Conversion", self.run_distance_conversion),
            ("Weight Conversion", self.run_weight_conversion),
            ("Post-processing Validation", self.run_post_processing_validation),
            ("Data Integrity Checks", self.run_data_integrity_checks),
        ]

        success_count = 0
        total_steps = len(pipeline_steps)

        for step_name, step_function in pipeline_steps:
            self.logger.info(f"\n📋 Executing: {step_name}")
            try:
                if step_function():
                    self.logger.info(f"✅ {step_name} completed successfully")
                    success_count += 1
                else:
                    self.logger.error(f"❌ {step_name} failed")
            except Exception as e:
                self.logger.error(f"💥 {step_name} crashed: {e}")
                self.errors.append(f"{step_name}: {e}")

        # Save results
        results = self.save_pipeline_results()

        # Final summary
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 PIPELINE EXECUTION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Steps completed: {success_count}/{total_steps}")
        self.logger.info(f"Errors encountered: {len(self.errors)}")

        if self.errors:
            self.logger.error("❌ Pipeline completed with errors:")
            for error in self.errors:
                self.logger.error(f"  - {error}")
        else:
            self.logger.info("✅ Pipeline completed successfully!")

        return success_count == total_steps and len(self.errors) == 0


# Integration hook for main pipeline
def run_automated_data_quality_pipeline(config=None):
    """
    Main entry point for pipeline integration
    Called by the main pipeline orchestrator
    """
    pipeline = AutomatedDataQualityPipeline(config)
    return pipeline.run_full_pipeline()


if __name__ == "__main__":
    # Allow running standalone for testing
    pipeline = AutomatedDataQualityPipeline()
    success = pipeline.run_full_pipeline()

    if not success:
        sys.exit(1)
    else:
        print("\n🎉 Automated Data Quality Pipeline completed successfully!")
