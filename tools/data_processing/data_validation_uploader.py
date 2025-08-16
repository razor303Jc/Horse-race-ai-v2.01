#!/usr/bin/env python3
"""
Automated Data Validation and Upload System
Horse Racing AI v2.02

Automates:
- Data validation checks before pipeline execution
- Data upload to database with integrity verification
- Race card data synchronization
- Database optimization and cleanup
- Integration with pipeline scheduling system

Ensures data quality and consistency for ML training.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/data_validation_upload.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class DataValidationUploader:
    """
    Automated data validation and upload system
    """

    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "port": 5433,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Validation thresholds
        self.validation_config = {
            "min_records_per_day": 50,
            "max_records_per_day": 2000,
            "required_columns": ["race_id", "course", "distance", "horse", "position"],
            "data_quality_threshold": 0.95,  # 95% complete data required
            "duplicate_threshold": 0.02,  # Max 2% duplicates allowed
        }

        # Create directories
        Path("logs").mkdir(exist_ok=True)
        Path("data/validation").mkdir(parents=True, exist_ok=True)
        Path("data/uploads").mkdir(parents=True, exist_ok=True)

    def get_database_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def validate_data_files(self, data_directory: str = "data/raw") -> Dict:
        """
        Validate data files before upload
        """
        logger.info("🔍 Starting data validation process")

        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "files_validated": 0,
            "total_records": 0,
            "validation_errors": [],
            "data_quality_score": 0.0,
            "upload_ready": False,
        }

        try:
            data_path = Path(data_directory)
            if not data_path.exists():
                logger.warning(f"⚠️ Data directory not found: {data_directory}")
                validation_results["validation_errors"].append(
                    f"Data directory missing: {data_directory}"
                )
                return validation_results

            # Find CSV files
            csv_files = list(data_path.glob("*.csv"))
            logger.info(f"📁 Found {len(csv_files)} CSV files to validate")

            if not csv_files:
                validation_results["validation_errors"].append("No CSV files found")
                return validation_results

            total_records = 0
            quality_scores = []

            for csv_file in csv_files:
                file_result = self.validate_single_file(csv_file)
                validation_results["files_validated"] += 1
                total_records += file_result["record_count"]
                quality_scores.append(file_result["quality_score"])

                if file_result["errors"]:
                    validation_results["validation_errors"].extend(
                        [f"{csv_file.name}: {error}" for error in file_result["errors"]]
                    )

            validation_results["total_records"] = total_records
            validation_results["data_quality_score"] = (
                sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            )

            # Determine if data is ready for upload
            validation_results["upload_ready"] = (
                len(validation_results["validation_errors"]) == 0
                and validation_results["data_quality_score"]
                >= self.validation_config["data_quality_threshold"]
                and total_records >= self.validation_config["min_records_per_day"]
            )

            logger.info(
                f"✅ Validation complete: {validation_results['files_validated']} files, "
                f"{total_records} records, "
                f"quality {validation_results['data_quality_score']:.2f}"
            )

        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            validation_results["validation_errors"].append(
                f"Validation process error: {e}"
            )

        return validation_results

    def validate_single_file(self, file_path: Path) -> Dict:
        """Validate a single CSV file"""
        logger.info(f"🔍 Validating file: {file_path.name}")

        result = {
            "file_name": file_path.name,
            "record_count": 0,
            "quality_score": 0.0,
            "errors": [],
            "warnings": [],
        }

        try:
            # Read CSV
            df = pd.read_csv(file_path)
            result["record_count"] = len(df)

            # Check required columns
            missing_cols = [
                col
                for col in self.validation_config["required_columns"]
                if col not in df.columns
            ]
            if missing_cols:
                result["errors"].append(f"Missing columns: {missing_cols}")

            # Check data completeness
            total_cells = df.size
            non_null_cells = df.count().sum()
            completeness = non_null_cells / total_cells if total_cells > 0 else 0

            # Check for duplicates
            duplicate_count = df.duplicated().sum()
            duplicate_rate = duplicate_count / len(df) if len(df) > 0 else 0

            if duplicate_rate > self.validation_config["duplicate_threshold"]:
                result["warnings"].append(f"High duplicate rate: {duplicate_rate:.2%}")

            # Calculate quality score
            result["quality_score"] = completeness * (1 - duplicate_rate)

            # Validate race_id format (should not have .0 suffix)
            if "race_id" in df.columns:
                invalid_race_ids = df[df["race_id"].astype(str).str.endswith(".0")]
                if len(invalid_race_ids) > 0:
                    result["warnings"].append(
                        f"Found {len(invalid_race_ids)} race_ids with .0 suffix"
                    )

            logger.info(
                f"   📊 {result['record_count']} records, "
                f"quality {result['quality_score']:.2f}"
            )

        except Exception as e:
            result["errors"].append(f"File reading error: {e}")
            logger.error(f"❌ Error validating {file_path.name}: {e}")

        return result

    def upload_validated_data(
        self, validation_results: Dict, data_directory: str = "data/raw"
    ) -> Dict:
        """
        Upload validated data to database
        """
        logger.info("📤 Starting data upload process")

        upload_results = {
            "timestamp": datetime.now().isoformat(),
            "upload_successful": False,
            "records_uploaded": 0,
            "tables_updated": [],
            "upload_errors": [],
        }

        if not validation_results["upload_ready"]:
            error_msg = "Data validation failed - upload aborted"
            logger.error(f"❌ {error_msg}")
            upload_results["upload_errors"].append(error_msg)
            return upload_results

        try:
            conn = self.get_database_connection()

            # Upload race data
            race_upload = self.upload_race_data(conn, data_directory)
            upload_results["records_uploaded"] += race_upload["records_uploaded"]
            upload_results["tables_updated"].extend(race_upload["tables_updated"])

            if race_upload["errors"]:
                upload_results["upload_errors"].extend(race_upload["errors"])

            # Upload additional data types as needed
            # records_upload = self.upload_records_data(conn, data_directory)
            # ... additional uploads

            # Commit all changes
            conn.commit()
            upload_results["upload_successful"] = (
                len(upload_results["upload_errors"]) == 0
            )

            logger.info(
                f"✅ Upload complete: {upload_results['records_uploaded']} records"
            )

        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            upload_results["upload_errors"].append(f"Upload process error: {e}")
            if "conn" in locals():
                conn.rollback()
        finally:
            if "conn" in locals():
                conn.close()

        return upload_results

    def upload_race_data(self, conn, data_directory: str) -> Dict:
        """Upload race data specifically"""
        result = {"records_uploaded": 0, "tables_updated": [], "errors": []}

        try:
            # Find race data files
            race_files = list(Path(data_directory).glob("*race*.csv"))

            for race_file in race_files:
                logger.info(f"📤 Uploading {race_file.name}")

                df = pd.read_csv(race_file)

                # Clean race_id format (remove .0 suffix if present)
                if "race_id" in df.columns:
                    df["race_id"] = (
                        df["race_id"].astype(str).str.replace(r"\.0$", "", regex=True)
                    )

                # Prepare insert query
                columns = list(df.columns)
                placeholders = ", ".join(["%s"] * len(columns))

                insert_query = f"""
                INSERT INTO races ({", ".join(columns)})
                VALUES ({placeholders})
                ON CONFLICT (race_id) DO UPDATE SET
                {", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != "race_id"])}
                """

                # Execute batch insert
                cursor = conn.cursor()
                data_tuples = [tuple(row) for row in df.values]

                execute_batch(cursor, insert_query, data_tuples, page_size=1000)

                result["records_uploaded"] += len(data_tuples)
                result["tables_updated"].append("races")

                cursor.close()
                logger.info(f"   ✅ Uploaded {len(data_tuples)} race records")

        except Exception as e:
            result["errors"].append(f"Race data upload error: {e}")
            logger.error(f"❌ Race data upload failed: {e}")

        return result

    def optimize_database(self) -> Dict:
        """
        Optimize database after data upload
        """
        logger.info("⚙️ Starting database optimization")

        optimization_results = {
            "timestamp": datetime.now().isoformat(),
            "operations_completed": [],
            "optimization_errors": [],
        }

        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()

            # Update table statistics
            cursor.execute("ANALYZE races;")
            optimization_results["operations_completed"].append("analyze_races")

            # Vacuum if needed
            cursor.execute("VACUUM ANALYZE races;")
            optimization_results["operations_completed"].append("vacuum_races")

            # Check for orphaned records and cleanup
            cleanup_query = """
            DELETE FROM records WHERE race_id NOT IN (SELECT race_id FROM races);
            """
            cursor.execute(cleanup_query)
            deleted_count = cursor.rowcount

            if deleted_count > 0:
                optimization_results["operations_completed"].append(
                    f"cleaned_{deleted_count}_orphaned_records"
                )

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(
                f"✅ Database optimization complete: "
                f"{len(optimization_results['operations_completed'])} operations"
            )

        except Exception as e:
            logger.error(f"❌ Database optimization failed: {e}")
            optimization_results["optimization_errors"].append(
                f"Optimization error: {e}"
            )

        return optimization_results

    def run_complete_validation_upload(self, data_directory: str = "data/raw") -> Dict:
        """
        Run complete validation and upload process
        """
        logger.info("🚀 Starting complete data validation and upload process")

        start_time = datetime.now()

        complete_results = {
            "process_start": start_time.isoformat(),
            "validation_results": {},
            "upload_results": {},
            "optimization_results": {},
            "overall_success": False,
            "total_duration_minutes": 0.0,
        }

        try:
            # Step 1: Validate data
            complete_results["validation_results"] = self.validate_data_files(
                data_directory
            )

            if complete_results["validation_results"]["upload_ready"]:
                # Step 2: Upload data
                complete_results["upload_results"] = self.upload_validated_data(
                    complete_results["validation_results"], data_directory
                )

                if complete_results["upload_results"]["upload_successful"]:
                    # Step 3: Optimize database
                    complete_results["optimization_results"] = self.optimize_database()

                    complete_results["overall_success"] = True
                    logger.info("✅ Complete validation and upload process successful")
                else:
                    logger.error("❌ Upload failed - skipping optimization")
            else:
                logger.error("❌ Data validation failed - skipping upload")

        except Exception as e:
            logger.error(f"❌ Complete process failed: {e}")
            complete_results["process_error"] = str(e)

        end_time = datetime.now()
        complete_results["process_end"] = end_time.isoformat()
        complete_results["total_duration_minutes"] = (
            end_time - start_time
        ).total_seconds() / 60

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"data/validation/validation_upload_results_{timestamp}.json"

        with open(results_file, "w") as f:
            json.dump(complete_results, f, indent=2)

        logger.info(f"📊 Process results saved: {results_file}")

        return complete_results


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Data Validation and Upload")
    parser.add_argument(
        "--data-dir",
        default="data/raw",
        help="Directory containing data files to validate",
    )
    parser.add_argument(
        "--validate-only", action="store_true", help="Only validate, don't upload"
    )
    parser.add_argument(
        "--upload-only",
        action="store_true",
        help="Skip validation, only upload (not recommended)",
    )

    args = parser.parse_args()

    validator_uploader = DataValidationUploader()

    if args.validate_only:
        results = validator_uploader.validate_data_files(args.data_dir)
        print("\n🔍 Data Validation Results")
        print(f"   Files Validated: {results['files_validated']}")
        print(f"   Total Records: {results['total_records']}")
        print(f"   Data Quality: {results['data_quality_score']:.2%}")
        print(f"   Upload Ready: {results['upload_ready']}")

        if results["validation_errors"]:
            print("\n❌ Validation Errors:")
            for error in results["validation_errors"]:
                print(f"   - {error}")

    elif args.upload_only:
        # Create minimal validation results for upload
        validation_results = {"upload_ready": True}
        results = validator_uploader.upload_validated_data(
            validation_results, args.data_dir
        )
        print("\n📤 Upload Results")
        print(f"   Success: {results['upload_successful']}")
        print(f"   Records Uploaded: {results['records_uploaded']}")

        if results["upload_errors"]:
            print("\n❌ Upload Errors:")
            for error in results["upload_errors"]:
                print(f"   - {error}")

    else:
        # Complete process
        results = validator_uploader.run_complete_validation_upload(args.data_dir)

        print("\n🚀 Complete Validation & Upload Results")
        print(f"   Overall Success: {results['overall_success']}")
        print(f"   Duration: {results['total_duration_minutes']:.1f} minutes")

        if "validation_results" in results:
            val_results = results["validation_results"]
            print(
                f"\n📊 Validation: {val_results['files_validated']} files, "
                f"{val_results['total_records']} records"
            )

        if "upload_results" in results:
            up_results = results["upload_results"]
            print(f"📤 Upload: {up_results['records_uploaded']} records uploaded")

        if "optimization_results" in results:
            opt_results = results["optimization_results"]
            print(
                f"⚙️ Optimization: {len(opt_results['operations_completed'])} operations"
            )


if __name__ == "__main__":
    main()
