#!/usr/bin/env python3
"""
Advanced Data Processing Pipeline Integration
===========================================

Integrates V2.01's sophisticated CSV mapping and data normalization into the main pipeline.
This replaces basic preprocessing with the advanced V2.01 column mapping system.

Key Features:
- Advanced CSV mapping with data validation
- Multi-source data support (cards_data + results_data)
- Automated data type conversion and cleaning
- Integration with existing data quality pipeline
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
import psycopg2

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import existing tools
from tools.data_processing.advanced_csv_mapper import AdvancedCSVMapper


class AdvancedDataProcessingPipeline:
    """
    Enhanced data processing pipeline that integrates V2.01's advanced features
    with the existing V2.03 automation infrastructure
    """

    def __init__(self, pipeline_config=None):
        self.project_root = project_root
        self.pipeline_config = pipeline_config or {}
        self.logger = self.setup_logging()

        # Initialize advanced CSV mapper
        self.csv_mapper = AdvancedCSVMapper("config/complete_csv_column_mapping.json")

        # Pipeline state
        self.processing_results = {}
        self.errors = []

    def setup_logging(self):
        """Setup pipeline logging"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)

        log_file = (
            log_dir
            / f"advanced_data_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        return logging.getLogger(__name__)

    def discover_data_sources(self):
        """
        Discover available data sources (cards_data + results_data)
        """
        self.logger.info("🔍 Step 1: Discovering data sources...")

        data_sources = {"cards_data": [], "results_data": [], "daily_downloads": []}

        # Check for different data source types
        base_data_dir = self.project_root / "data"

        # Daily downloads (current system)
        daily_dir = base_data_dir / "daily_downloads"
        if daily_dir.exists():
            for subdir in ["cards_data", "results_data"]:
                subdir_path = daily_dir / subdir
                if subdir_path.exists():
                    csv_files = list(subdir_path.rglob("*.csv"))
                    data_sources[subdir].extend(csv_files)
                    self.logger.info(f"Found {len(csv_files)} CSV files in {subdir}")

        # Preprocessed data
        preprocessed_dir = base_data_dir / "preprocessed"
        if preprocessed_dir.exists():
            csv_files = list(preprocessed_dir.rglob("*.csv"))
            data_sources["daily_downloads"].extend(csv_files)
            self.logger.info(f"Found {len(csv_files)} preprocessed CSV files")

        self.processing_results["data_sources"] = data_sources
        return data_sources

    def apply_advanced_csv_mapping(self, data_sources):
        """
        Apply V2.01's advanced CSV mapping to all discovered data sources
        """
        self.logger.info("🗂️ Step 2: Applying advanced CSV mapping...")

        mapped_data = {}

        try:
            # Process each data source type
            for source_type, csv_files in data_sources.items():
                if not csv_files:
                    continue

                self.logger.info(
                    f"Processing {len(csv_files)} files from {source_type}"
                )
                mapped_data[source_type] = {}

                for csv_file in csv_files:
                    try:
                        # Determine table type from file path/name
                        table_type = self.determine_table_type(csv_file)

                        if table_type:
                            # Apply advanced mapping
                            mapped_df = self.csv_mapper.process_csv_file(
                                csv_file, table_type, validate_data=True
                            )

                            if mapped_df is not None and not mapped_df.empty:
                                mapped_data[source_type][table_type] = mapped_df
                                self.logger.info(
                                    f"✅ Mapped {len(mapped_df)} rows for {table_type}"
                                )
                            else:
                                self.logger.warning(f"⚠️ No data mapped for {csv_file}")
                        else:
                            self.logger.warning(
                                f"⚠️ Could not determine table type for {csv_file}"
                            )

                    except Exception as e:
                        self.logger.error(f"❌ Failed to process {csv_file}: {e}")
                        self.errors.append(f"CSV processing {csv_file}: {e}")

            self.processing_results["mapped_data"] = mapped_data
            return mapped_data

        except Exception as e:
            self.logger.error(f"❌ Advanced CSV mapping failed: {e}")
            self.errors.append(f"Advanced CSV mapping: {e}")
            return {}

    def determine_table_type(self, csv_file_path):
        """
        Determine database table type from CSV file path/name
        """
        file_path = str(csv_file_path).lower()
        file_name = csv_file_path.name.lower()

        # Map file patterns to table types
        if "race" in file_name and "card" not in file_name:
            return "races"
        elif "record" in file_name or "racecard" in file_name:
            return "records"
        elif "horse" in file_name:
            return "horses"
        elif "jockey" in file_name:
            return "jockeys_stats"
        elif "trainer" in file_name:
            return "trainers_stats"
        elif "complete_mapped_races" in file_name:
            return "races"
        elif "complete_mapped_records" in file_name:
            return "records"

        return None

    def merge_multi_source_data(self, mapped_data):
        """
        Merge data from multiple sources (cards_data + results_data)
        with conflict resolution and deduplication
        """
        self.logger.info("🔀 Step 3: Merging multi-source data...")

        merged_data = {}

        try:
            # Get all unique table types across sources
            all_table_types = set()
            for source_data in mapped_data.values():
                all_table_types.update(source_data.keys())

            for table_type in all_table_types:
                self.logger.info(f"Merging {table_type} data from multiple sources")

                # Collect all dataframes for this table type
                dfs_to_merge = []
                for source_type, source_data in mapped_data.items():
                    if table_type in source_data:
                        df = source_data[table_type].copy()
                        df["data_source"] = source_type
                        dfs_to_merge.append(df)

                if dfs_to_merge:
                    # Merge with conflict resolution
                    merged_df = self.merge_with_conflict_resolution(
                        dfs_to_merge, table_type
                    )
                    merged_data[table_type] = merged_df
                    self.logger.info(
                        f"✅ Merged {len(merged_df)} rows for {table_type}"
                    )

            self.processing_results["merged_data"] = merged_data
            return merged_data

        except Exception as e:
            self.logger.error(f"❌ Multi-source merge failed: {e}")
            self.errors.append(f"Multi-source merge: {e}")
            return {}

    def merge_with_conflict_resolution(self, dfs_to_merge, table_type):
        """
        Merge dataframes with intelligent conflict resolution
        """
        if len(dfs_to_merge) == 1:
            return dfs_to_merge[0].drop("data_source", axis=1, errors="ignore")

        # Concatenate all dataframes
        combined_df = pd.concat(dfs_to_merge, ignore_index=True)

        # Define key columns for deduplication
        key_columns = self.get_key_columns(table_type)

        if key_columns:
            # Remove duplicates, keeping the most recent/complete record
            combined_df = combined_df.drop_duplicates(subset=key_columns, keep="last")

        return combined_df.drop("data_source", axis=1, errors="ignore")

    def get_key_columns(self, table_type):
        """
        Get key columns for deduplication based on table type
        """
        key_mapping = {
            "races": ["race_id"],
            "records": ["record_id", "race_id", "horse_id"],
            "horses": ["horse_id"],
            "jockeys_stats": ["jockey_id"],
            "trainers_stats": ["trainer_id"],
        }
        return key_mapping.get(table_type, [])

    def validate_processed_data(self, merged_data):
        """
        Step 4: Validate processed data quality and completeness
        """
        self.logger.info("✅ Step 4: Validating processed data...")

        validation_results = {}

        try:
            for table_type, df in merged_data.items():
                validation = {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "null_percentage": (
                        df.isnull().sum().sum() / (len(df) * len(df.columns))
                    )
                    * 100,
                    "duplicate_rows": df.duplicated().sum(),
                    "data_quality_score": 0,
                }

                # Calculate data quality score
                quality_score = (
                    100
                    - validation["null_percentage"]
                    - (validation["duplicate_rows"] / len(df) * 10)
                )
                validation["data_quality_score"] = max(0, min(100, quality_score))

                validation_results[table_type] = validation

                self.logger.info(
                    f"📊 {table_type}: {validation['row_count']} rows, "
                    f"Quality Score: {validation['data_quality_score']:.1f}%"
                )

            self.processing_results["validation"] = validation_results
            return validation_results

        except Exception as e:
            self.logger.error(f"❌ Data validation failed: {e}")
            self.errors.append(f"Data validation: {e}")
            return {}

    def save_processed_data(self, merged_data):
        """
        Step 5: Save processed data to standardized location
        """
        self.logger.info("💾 Step 5: Saving processed data...")

        try:
            # Create output directory
            output_dir = self.project_root / "data" / "advanced_processed"
            output_dir.mkdir(exist_ok=True)

            saved_files = {}

            for table_type, df in merged_data.items():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = (
                    output_dir / f"{table_type}_advanced_processed_{timestamp}.csv"
                )

                df.to_csv(output_file, index=False)
                saved_files[table_type] = str(output_file)

                self.logger.info(
                    f"✅ Saved {table_type}: {len(df)} rows to {output_file.name}"
                )

            self.processing_results["saved_files"] = saved_files
            return saved_files

        except Exception as e:
            self.logger.error(f"❌ Failed to save processed data: {e}")
            self.errors.append(f"Save processed data: {e}")
            return {}

    def save_pipeline_results(self):
        """Save pipeline results for tracking and monitoring"""
        results_file = (
            self.project_root / "reports" / "advanced_data_processing_results.json"
        )

        pipeline_results = {
            "pipeline_run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "processing_results": self.processing_results,
            "errors": self.errors,
            "success": len(self.errors) == 0,
        }

        with open(results_file, "w") as f:
            json.dump(pipeline_results, f, indent=2, default=str)

        self.logger.info(f"Pipeline results saved to: {results_file}")
        return pipeline_results

    def run_advanced_processing_pipeline(self):
        """
        Execute the complete advanced data processing pipeline

        Returns:
            bool: True if pipeline completed successfully, False otherwise
        """
        self.logger.info("🚀 Starting Advanced Data Processing Pipeline")
        self.logger.info("=" * 60)

        pipeline_steps = [
            ("Data Source Discovery", self.discover_data_sources),
            (
                "Advanced CSV Mapping",
                lambda: self.apply_advanced_csv_mapping(
                    self.processing_results.get("data_sources", {})
                ),
            ),
            (
                "Multi-Source Data Merge",
                lambda: self.merge_multi_source_data(
                    self.processing_results.get("mapped_data", {})
                ),
            ),
            (
                "Data Validation",
                lambda: self.validate_processed_data(
                    self.processing_results.get("merged_data", {})
                ),
            ),
            (
                "Save Processed Data",
                lambda: self.save_processed_data(
                    self.processing_results.get("merged_data", {})
                ),
            ),
        ]

        success_count = 0
        total_steps = len(pipeline_steps)

        for step_name, step_function in pipeline_steps:
            self.logger.info(f"\n📋 Executing: {step_name}")
            try:
                result = step_function()
                if result is not None:
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
        self.logger.info("📊 ADVANCED PROCESSING PIPELINE SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Steps completed: {success_count}/{total_steps}")
        self.logger.info(f"Errors encountered: {len(self.errors)}")

        if self.errors:
            self.logger.error("❌ Pipeline completed with errors:")
            for error in self.errors:
                self.logger.error(f"  - {error}")
        else:
            self.logger.info("✅ Advanced processing pipeline completed successfully!")

        return success_count == total_steps and len(self.errors) == 0


# Integration hook for main pipeline
def run_advanced_data_processing_pipeline(config=None):
    """
    Main entry point for pipeline integration
    Called by the main pipeline orchestrator
    """
    pipeline = AdvancedDataProcessingPipeline(config)
    return pipeline.run_advanced_processing_pipeline()


if __name__ == "__main__":
    # Allow running standalone for testing
    pipeline = AdvancedDataProcessingPipeline()
    success = pipeline.run_advanced_processing_pipeline()

    if not success:
        sys.exit(1)
    else:
        print("\n🎉 Advanced Data Processing Pipeline completed successfully!")
