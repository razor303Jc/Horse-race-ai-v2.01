#!/usr/bin/env python3
"""
Enhanced Data Integration Pipeline - Complete Data Cleaning Before Upload
🚀 AUTOMATED PIPELINE: Dash symbols → Data cleaning → Quality validation → Upload

This pipeline integrates all data cleaning tools in the correct order:
1. Clean dash symbols (numeric: "-" → 0, string: "-" → "None")
2. Run weight converter (UK format "10-2" → kg)
3. Run distance converter (UK format "6f" → meters)
4. Apply comprehensive data cleaning
5. Validate data quality
6. Upload to database with error handling
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import all cleaning tools
from tools.data_processing.clean_data import (
    clean_races_data,
    clean_records_data,
    clean_horses_data,
    clean_jockeys_stats,
    clean_trainers_stats,
)
from tools.data_processing.weight_converter import WeightConverter
from tools.data_processing.distance_converter import DistanceConverter
from tools.data_validation.comprehensive_data_audit import DataMappingAuditor
from tools.data_processing.upload_mapped_data import upload_csv_to_database


class EnhancedDataIntegrationPipeline:
    """Complete data integration pipeline with quality checks"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.weight_converter = WeightConverter()
        self.distance_converter = DistanceConverter()
        self.data_auditor = DataMappingAuditor()
        self.processing_results = {}
        self.errors = []

    def _setup_logging(self):
        """Setup logging for pipeline operations"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("data/logs/enhanced_data_pipeline.log"),
                logging.StreamHandler(),
            ],
        )
        return logging.getLogger(__name__)

    def run_complete_pipeline(self):
        """
        🚀 MAIN PIPELINE: Complete data cleaning and upload workflow
        """
        self.logger.info("🚀 Starting Enhanced Data Integration Pipeline")
        self.logger.info("=" * 60)

        try:
            # Step 1: Apply comprehensive data cleaning (includes dash symbol cleaning)
            success = self.run_data_cleaning()
            if not success:
                self.logger.error("❌ Data cleaning failed, stopping pipeline")
                return False

            # Step 2: Run weight conversion
            success = self.run_weight_conversion()
            if not success:
                self.logger.warning("⚠️ Weight conversion had issues, continuing...")

            # Step 3: Run distance conversion
            success = self.run_distance_conversion()
            if not success:
                self.logger.warning("⚠️ Distance conversion had issues, continuing...")

            # Step 4: Data quality validation
            success = self.run_data_quality_validation()
            if not success:
                self.logger.warning("⚠️ Data quality issues found, check logs")

            # Step 5: Upload to database
            success = self.run_database_upload()
            if not success:
                self.logger.error("❌ Database upload failed")
                return False

            self.logger.info("✅ Enhanced Data Integration Pipeline completed")
            self._generate_completion_report()
            return True

        except Exception as e:
            self.logger.error(f"💥 Pipeline failed with error: {e}")
            self.errors.append(f"Pipeline error: {e}")
            return False

    def run_data_cleaning(self):
        """
        Step 1: Comprehensive data cleaning including dash symbols
        """
        self.logger.info("🧹 Step 1: Comprehensive Data Cleaning")

        try:
            # Clean all data types with enhanced dash symbol handling
            self.logger.info("  📊 Cleaning races data...")
            clean_races_data()

            self.logger.info("  📊 Cleaning records data...")
            clean_records_data()

            self.logger.info("  📊 Cleaning horses data...")
            clean_horses_data()

            self.logger.info("  📊 Cleaning jockeys stats...")
            clean_jockeys_stats()

            self.logger.info("  📊 Cleaning trainers stats...")
            clean_trainers_stats()

            self.processing_results["data_cleaning"] = {
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "tables_cleaned": [
                    "races",
                    "records",
                    "horses",
                    "jockeys_stats",
                    "trainers_stats",
                ],
            }

            self.logger.info("✅ Data cleaning completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"❌ Data cleaning failed: {e}")
            self.errors.append(f"Data cleaning: {e}")
            return False

    def run_weight_conversion(self):
        """
        Step 2: Convert UK weight formats in CSV files
        """
        self.logger.info("⚖️ Step 2: Weight Conversion")

        try:
            # Process CSV files directly for weight conversion
            records_file = Path("data/daily_downloads/complete_mapped_records.csv")
            if records_file.exists():
                df = pd.read_csv(records_file)
                original_count = len(df)

                # Apply weight conversion to weight_uk column
                if "weight_uk" in df.columns:
                    converted_count = 0
                    for idx, row in df.iterrows():
                        if pd.notna(row["weight_uk"]):
                            converted_kg = self.weight_converter.convert_uk_to_kg(
                                str(row["weight_uk"])
                            )
                            if converted_kg:
                                df.at[idx, "weight"] = converted_kg
                                converted_count += 1

                    # Save updated CSV
                    df.to_csv(records_file, index=False)

                    conversion_stats = {
                        "total_records": original_count,
                        "weights_converted": converted_count,
                    }
                else:
                    conversion_stats = {"message": "No weight_uk column found"}
            else:
                conversion_stats = {"message": "Records file not found"}

            self.processing_results["weight_conversion"] = {
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "conversions": conversion_stats,
            }

            self.logger.info(f"✅ Weight conversion completed: {conversion_stats}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Weight conversion failed: {e}")
            self.errors.append(f"Weight conversion: {e}")
            return False

    def run_distance_conversion(self):
        """
        Step 3: Convert UK distance formats in CSV files
        """
        self.logger.info("🏃 Step 3: Distance Conversion")

        try:
            # Process CSV files directly for distance conversion
            races_file = Path("data/daily_downloads/complete_mapped_races.csv")
            if races_file.exists():
                df = pd.read_csv(races_file)
                original_count = len(df)

                # Apply distance conversion to distance column
                if "distance" in df.columns:
                    converted_count = 0
                    for idx, row in df.iterrows():
                        if pd.notna(row["distance"]):
                            converted_meters = (
                                self.distance_converter.convert_to_meters(
                                    str(row["distance"])
                                )
                            )
                            if converted_meters:
                                df.at[idx, "distance_meters"] = converted_meters
                                converted_count += 1

                    # Save updated CSV
                    df.to_csv(races_file, index=False)

                    conversion_stats = {
                        "total_records": original_count,
                        "distances_converted": converted_count,
                    }
                else:
                    conversion_stats = {"message": "No distance column found"}
            else:
                conversion_stats = {"message": "Races file not found"}

            self.processing_results["distance_conversion"] = {
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "conversions": conversion_stats,
            }

            self.logger.info(f"✅ Distance conversion completed: {conversion_stats}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Distance conversion failed: {e}")
            self.errors.append(f"Distance conversion: {e}")
            return False

    def run_data_quality_validation(self):
        """
        Step 4: Comprehensive data quality validation
        """
        self.logger.info("🔍 Step 4: Data Quality Validation")

        try:
            if not self.data_auditor.connect_to_database():
                self.logger.warning(
                    "⚠️ Could not connect to database for quality validation"
                )
                return False

            # Run full data quality audit
            self.data_auditor.run_full_audit()

            # Log any issues found
            if self.data_auditor.issues:
                issue_count = len(self.data_auditor.issues)
                self.logger.warning("⚠️ Data quality issues found: %d", issue_count)
                for issue in self.data_auditor.issues:
                    self.logger.warning("  - %s", issue)

            if self.data_auditor.recommendations:
                rec_count = len(self.data_auditor.recommendations)
                self.logger.info("💡 Recommendations: %d", rec_count)
                for rec in self.data_auditor.recommendations:
                    self.logger.info("  - %s", rec)

            self.processing_results["data_validation"] = {
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "issues_found": len(self.data_auditor.issues),
                "recommendations": len(self.data_auditor.recommendations),
            }

            self.logger.info("✅ Data quality validation completed")
            return True

        except Exception as e:
            self.logger.error(f"❌ Data quality validation failed: {e}")
            self.errors.append(f"Data validation: {e}")
            return False

    def run_database_upload(self):
        """
        Step 5: Upload cleaned data to database
        """
        self.logger.info("📤 Step 5: Database Upload")

        try:
            # Define data files and their corresponding tables
            upload_tasks = [
                ("data/daily_downloads/complete_mapped_races.csv", "races"),
                ("data/daily_downloads/complete_mapped_records.csv", "records"),
                ("data/daily_downloads/complete_mapped_horses.csv", "horses"),
                (
                    "data/daily_downloads/complete_mapped_jockeys_stats.csv",
                    "jockeys_stats",
                ),
                (
                    "data/daily_downloads/complete_mapped_trainers_stats.csv",
                    "trainers_stats",
                ),
            ]

            successful_uploads = 0
            failed_uploads = 0

            for csv_file, table_name in upload_tasks:
                file_path = Path(csv_file)
                if file_path.exists():
                    try:
                        self.logger.info(f"  📊 Uploading {csv_file} to {table_name}")
                        upload_csv_to_database(csv_file, table_name)
                        successful_uploads += 1
                        self.logger.info(f"  ✅ {table_name} uploaded successfully")
                    except Exception as e:
                        self.logger.error(f"  ❌ Failed to upload {table_name}: {e}")
                        failed_uploads += 1
                        self.errors.append(f"Upload {table_name}: {e}")
                else:
                    self.logger.warning(f"  ⚠️ File not found: {csv_file}")
                    failed_uploads += 1

            self.processing_results["database_upload"] = {
                "timestamp": datetime.now().isoformat(),
                "status": "completed" if failed_uploads == 0 else "partial",
                "successful_uploads": successful_uploads,
                "failed_uploads": failed_uploads,
            }

            if failed_uploads == 0:
                self.logger.info("✅ All database uploads completed successfully")
                return True
            else:
                self.logger.warning(
                    f"⚠️ {failed_uploads} uploads failed, {successful_uploads} succeeded"
                )
                return False

        except Exception as e:
            self.logger.error(f"❌ Database upload failed: {e}")
            self.errors.append(f"Database upload: {e}")
            return False

    def _generate_completion_report(self):
        """Generate a completion report for the pipeline"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📋 ENHANCED DATA INTEGRATION PIPELINE REPORT")
        self.logger.info("=" * 60)

        for step, results in self.processing_results.items():
            status_icon = "✅" if results["status"] == "completed" else "⚠️"
            self.logger.info(f"{status_icon} {step.upper()}: {results['status']}")

            if step == "data_cleaning":
                self.logger.info(
                    f"  - Tables cleaned: {', '.join(results['tables_cleaned'])}"
                )
            elif step == "weight_conversion" and "conversions" in results:
                self.logger.info(f"  - Conversions: {results['conversions']}")
            elif step == "distance_conversion" and "conversions" in results:
                self.logger.info(f"  - Conversions: {results['conversions']}")
            elif step == "data_validation":
                self.logger.info(f"  - Issues found: {results['issues_found']}")
                self.logger.info(f"  - Recommendations: {results['recommendations']}")
            elif step == "database_upload":
                self.logger.info(
                    f"  - Successful uploads: {results['successful_uploads']}"
                )
                if results["failed_uploads"] > 0:
                    self.logger.info(f"  - Failed uploads: {results['failed_uploads']}")

        if self.errors:
            self.logger.info(f"\n⚠️ ERRORS ENCOUNTERED ({len(self.errors)}):")
            for error in self.errors:
                self.logger.info(f"  - {error}")

        self.logger.info("=" * 60)


def main():
    """Run the enhanced data integration pipeline"""
    pipeline = EnhancedDataIntegrationPipeline()
    success = pipeline.run_complete_pipeline()

    if success:
        print("🎉 Enhanced Data Integration Pipeline completed successfully!")
        return 0
    else:
        print("❌ Enhanced Data Integration Pipeline failed. Check logs for details.")
        return 1


if __name__ == "__main__":
    exit(main())
