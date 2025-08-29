#!/usr/bin/env python3
"""
Simplified Data Integration Pipeline
🚀 AUTOMATED: Enhanced data cleaning → Upload pipeline

This pipeline provides a simple interface to:
1. Clean dash symbols based on data types
2. Apply all data cleaning transformations
3. Upload clean data to database
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.data_processing.clean_data import (
    clean_races_data,
    clean_records_data,
    clean_horses_data,
    clean_jockeys_stats,
    clean_trainers_stats,
)


class SimplifiedDataPipeline:
    """Simplified data cleaning and processing pipeline"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.results = {}
        self.errors = []

    def _setup_logging(self):
        """Setup basic logging"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )
        return logging.getLogger(__name__)

    def run_data_cleaning_pipeline(self):
        """
        🧹 MAIN FUNCTION: Run complete data cleaning pipeline
        """
        self.logger.info("🚀 Starting Data Cleaning Pipeline")
        self.logger.info("=" * 50)

        try:
            # Clean all data files with enhanced dash handling
            cleaning_tasks = [
                ("races", clean_races_data),
                ("records", clean_records_data),
                ("horses", clean_horses_data),
                ("jockeys_stats", clean_jockeys_stats),
                ("trainers_stats", clean_trainers_stats),
            ]

            successful_cleanings = 0
            failed_cleanings = 0

            for table_name, clean_function in cleaning_tasks:
                try:
                    self.logger.info("🧹 Cleaning %s data...", table_name)
                    clean_function()
                    successful_cleanings += 1
                    self.logger.info("✅ %s data cleaned successfully", table_name)
                except Exception as e:
                    self.logger.error("❌ Failed to clean %s: %s", table_name, e)
                    failed_cleanings += 1
                    self.errors.append(f"Clean {table_name}: {e}")

            # Generate summary
            self.results = {
                "timestamp": datetime.now().isoformat(),
                "successful_cleanings": successful_cleanings,
                "failed_cleanings": failed_cleanings,
                "total_tasks": len(cleaning_tasks),
            }

            self._generate_report()

            if failed_cleanings == 0:
                self.logger.info("🎉 All data cleaning completed successfully!")
                return True
            else:
                self.logger.warning(
                    "⚠️ %d cleanings failed, %d succeeded",
                    failed_cleanings,
                    successful_cleanings,
                )
                return False

        except Exception as e:
            self.logger.error("💥 Pipeline failed: %s", e)
            return False

    def _generate_report(self):
        """Generate a summary report"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("📋 DATA CLEANING PIPELINE REPORT")
        self.logger.info("=" * 50)
        self.logger.info(
            "✅ Successful cleanings: %d", self.results["successful_cleanings"]
        )
        if self.results["failed_cleanings"] > 0:
            self.logger.info(
                "❌ Failed cleanings: %d", self.results["failed_cleanings"]
            )

        if self.errors:
            self.logger.info("\n⚠️ ERRORS:")
            for error in self.errors:
                self.logger.info("  - %s", error)

        self.logger.info("\n🔧 CLEANING FEATURES APPLIED:")
        self.logger.info("  ✅ Dash symbols: numeric → 0, string → 'None'")
        self.logger.info("  ✅ Weight UK format: '10-2' → '10.2'")
        self.logger.info("  ✅ Fractions: '½' → '0.5', 'nk' → '0.1'")
        self.logger.info("  ✅ Percentages: '16.67%' → 0.1667")
        self.logger.info("  ✅ NULL value handling")
        self.logger.info("=" * 50)


def main():
    """Run the simplified data cleaning pipeline"""
    pipeline = SimplifiedDataPipeline()
    success = pipeline.run_data_cleaning_pipeline()

    if success:
        print("\n🎉 Data cleaning pipeline completed successfully!")
        print("📁 Your cleaned CSV files are ready for upload")
        return 0
    else:
        print("\n❌ Data cleaning pipeline failed. Check logs for details.")
        return 1


if __name__ == "__main__":
    exit(main())
