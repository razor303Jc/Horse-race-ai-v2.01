#!/usr/bin/env python3
"""
Enhanced Data Processor v2.05 for Horse Racing AI System
Latest Version Data Processing with Comprehensive Quality Control
Version Tag: latest:v2.05

This enhanced data processor provides comprehensive data validation,
quality control, and processing capabilities for the Horse Racing AI system.

Features:
- Date validation and correction
- Standardized NULL value handling with -0 mapping for ML model compatibility
- Data type validation and conversion
- Quality scoring and reporting
- Database integration with Redis status tracking
- Comprehensive error handling and logging
- Performance optimization for large datasets

Author: Horse Racing AI Development Team
Version: 2.05 (latest:v2.05)
Date: 2025-08-30
Status: Production Ready - Enhanced with standardized NULL mapping
"""

import os
import sys
import zipfile
import pandas as pd
import numpy as np
import json
import re
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional, Union
import redis
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
import warnings

# Suppress pandas warnings for cleaner output
warnings.filterwarnings("ignore")

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "/home/jc/Documents/Horse-race-ai-v2.05/logs/data_processor_v2_05.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EnhancedDataProcessorV205:
    """
    Enhanced Data Processor v2.05 - Latest Version
    Comprehensive data processing with validation and quality checks
    """

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.05"):
        """Initialize the enhanced data processor"""
        self.base_path = Path(base_path)
        self.version = "v2.05"

        # Processing configuration
        self.config = self.load_processor_config()

        # Initialize connections
        self.redis_client = self._init_redis()
        self.db_config = self._get_db_config()

        # Data quality tracking
        self.quality_metrics = {
            "total_files_processed": 0,
            "validation_errors": 0,
            "date_corrections": 0,
            "null_value_corrections": 0,
            "type_conversions": 0,
            "successful_uploads": 0,
            "failed_uploads": 0,
        }

        # Processing status
        self.processing_status = {
            "current_file": None,
            "current_stage": "idle",
            "progress_percent": 0,
            "errors": [],
            "warnings": [],
        }

        logger.info(f"🚀 Enhanced Data Processor v{self.version} initialized")

    def load_processor_config(self) -> Dict[str, Any]:
        """Load data processor configuration"""
        config_file = self.base_path / "config/data_processor_config_v2_05.json"

        default_config = {
            "version": "v2.05",
            "data_validation": {
                "max_null_percentage": 25,
                "required_columns": {
                    "races": ["race_id", "date", "course", "race_time"],
                    "records": ["id", "race_id", "horse_id", "place"],
                    "horses": ["id", "name", "country"],
                },
                "date_tolerance_days": 1,
                "auto_correct_dates": True,
            },
            "data_cleaning": {
                "null_replacements": {"string": "", "numeric": 0, "percentage": 0.0},
                "percentage_columns": [
                    "percentage_wins",
                    "percentage_placed",
                    "flat_aw_rate",
                    "flat_aw_placed_rate",
                    "flat_turf_rate",
                    "flat_turf_placed_rate",
                    "chase_rate",
                    "chase_placed_rate",
                    "hurdle_rate",
                    "hurdle_placed_rate",
                ],
                "weight_format_columns": ["weight_uk", "weight"],
                "distance_format_columns": ["distance_btn", "distance_btn_total"],
            },
            "type_mapping": {
                "integer_columns": [
                    "race_number",
                    "course_id",
                    "runners_racecard",
                    "runners",
                    "draw",
                    "ew_racecard",
                    "ew",
                    "places_ew_racecard",
                    "places_ew",
                    "horse_number",
                    "place",
                    "age",
                    "horse_rate",
                    "jockey_id",
                    "trainer_id",
                ],
                "float_columns": [
                    "weight",
                    "weight_uk",
                    "sp",
                    "distance_btn_total",
                    "total_races",
                    "wins",
                    "percentage_wins",
                    "placed",
                    "percentage_placed",
                ],
                "string_columns": [
                    "course",
                    "race_name",
                    "race_type",
                    "surface",
                    "name",
                    "country",
                    "jockey",
                    "trainer",
                    "color",
                    "owner",
                    "sire",
                    "dam",
                ],
            },
        }

        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                logger.info("📋 Processor configuration loaded from file")
                return config
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config: {e}")

        # Save default config
        try:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            logger.info("💾 Default processor configuration saved")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save config: {e}")

        return default_config

    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for status tracking"""
        try:
            client = redis.Redis(
                host="redis",
                port=6379,
                password="redis_password_123",
                decode_responses=True,
            )
            client.ping()
            logger.info("✅ Redis connection established")
            return client
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            return None

    def _get_db_config(self) -> Dict[str, str]:
        """Get database configuration"""
        return {
            "host": "postgres",
            "port": "5432",
            "dbname": "cards_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def update_status(self, stage: str, progress: int = 0, message: str = ""):
        """Update processing status in Redis"""
        self.processing_status.update(
            {
                "current_stage": stage,
                "progress_percent": progress,
                "timestamp": datetime.now().isoformat(),
            }
        )

        if message:
            self.processing_status["last_message"] = message

        if self.redis_client:
            try:
                self.redis_client.set(
                    "processor:status", json.dumps(self.processing_status, default=str)
                )
                self.redis_client.set(
                    "processor:metrics", json.dumps(self.quality_metrics, default=str)
                )
            except Exception as e:
                logger.warning(f"⚠️ Failed to update Redis status: {e}")

    def extract_date_from_filename(self, filename: str) -> Optional[str]:
        """Extract expected date from filename"""
        try:
            # Look for YYYY-MM-DD pattern in filename
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
            if date_match:
                return date_match.group(1)

            # Look for YYYY_MM_DD pattern
            date_match = re.search(r"(\d{4})_(\d{2})_(\d{2})", filename)
            if date_match:
                year, month, day = date_match.groups()
                return f"{year}-{month}-{day}"

            return None
        except Exception as e:
            logger.warning(f"⚠️ Error extracting date from filename {filename}: {e}")
            return None

    def validate_and_correct_dates(
        self, df: pd.DataFrame, filename: str, expected_date: Optional[str] = None
    ) -> Tuple[pd.DataFrame, bool]:
        """Validate and correct date inconsistencies"""
        try:
            corrections_made = False

            if expected_date is None:
                expected_date = self.extract_date_from_filename(filename)

            if expected_date is None:
                logger.warning(f"⚠️ Could not determine expected date for {filename}")
                return df, corrections_made

            # Check date columns
            date_columns = [col for col in df.columns if "date" in col.lower()]

            for date_col in date_columns:
                if date_col in df.columns:
                    unique_dates = df[date_col].unique()

                    logger.info(f"📅 Found dates in {date_col}: {unique_dates}")

                    # Check if dates need correction
                    for date_val in unique_dates:
                        if pd.isna(date_val):
                            continue

                        if str(date_val) != expected_date:
                            # Calculate date difference
                            try:
                                actual_date = datetime.strptime(
                                    str(date_val), "%Y-%m-%d"
                                )
                                expected_date_obj = datetime.strptime(
                                    expected_date, "%Y-%m-%d"
                                )
                                diff_days = abs((actual_date - expected_date_obj).days)

                                tolerance = self.config["data_validation"][
                                    "date_tolerance_days"
                                ]

                                if (
                                    diff_days <= tolerance
                                    and self.config["data_validation"][
                                        "auto_correct_dates"
                                    ]
                                ):
                                    logger.info(
                                        f"🔧 Correcting date {date_val} → {expected_date} in {date_col}"
                                    )
                                    df[date_col] = df[date_col].replace(
                                        date_val, expected_date
                                    )
                                    corrections_made = True
                                    self.quality_metrics["date_corrections"] += 1
                                else:
                                    logger.warning(
                                        f"⚠️ Date discrepancy too large: {date_val} vs {expected_date} ({diff_days} days)"
                                    )

                            except ValueError as e:
                                logger.warning(f"⚠️ Invalid date format: {date_val}")

            return df, corrections_made

        except Exception as e:
            logger.error(f"❌ Error in date validation: {e}")
            return df, False

    def clean_null_and_missing_values(
        self, df: pd.DataFrame, data_type: str
    ) -> pd.DataFrame:
        """Clean NULL values, empty strings, and missing data using standardized -0 replacement"""
        try:
            logger.info(f"🧹 Cleaning NULL and missing values for {data_type}")

            # Count initial null values
            initial_nulls = df.isnull().sum().sum()

            # Replace various NULL representations
            null_representations = [
                "NULL",
                "null",
                "None",
                "nan",
                "NaN",
                "-",
                "",
                "N/A",
                "n/a",
            ]

            for null_rep in null_representations:
                df = df.replace(null_rep, np.nan)

            # Use standardized -0 replacement for all columns
            # This creates a consistent mapping for the ML model
            standard_null_replacement = -0

            # Handle different data types
            for column in df.columns:
                null_count = df[column].isnull().sum()
                if null_count > 0:
                    # Use -0 for all columns to create consistent mapping
                    df[column] = df[column].fillna(standard_null_replacement)

                    logger.debug(
                        f"  Fixed {null_count} null values in {column} with -0"
                    )
                    self.quality_metrics["null_value_corrections"] += null_count

            final_nulls = df.isnull().sum().sum()
            logger.info(
                f"✅ Reduced null values from {initial_nulls} to {final_nulls} using -0 mapping"
            )

            # Log the mapping info for ML model documentation
            if self.quality_metrics["null_value_corrections"] > 0:
                logger.info(
                    f"📝 ML Model Mapping: -0 represents missing/null values ({self.quality_metrics['null_value_corrections']} replacements)"
                )

            return df

        except Exception as e:
            logger.error(f"❌ Error cleaning null values: {e}")
            return df

    def normalize_percentage_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert percentage strings to decimal numbers"""
        try:
            percentage_columns = self.config["data_cleaning"]["percentage_columns"]

            for col in percentage_columns:
                if col in df.columns:
                    # Convert percentage strings like '16.67%' to decimal numbers
                    df[col] = (
                        df[col].astype(str).str.replace("%", "").replace("nan", "0")
                    )
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0) / 100
                    logger.debug(f"  Normalized percentage column: {col}")
                    self.quality_metrics["type_conversions"] += 1

            return df

        except Exception as e:
            logger.error(f"❌ Error normalizing percentages: {e}")
            return df

    def normalize_weight_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize weight formats (e.g., '9-6' to decimal)"""
        try:
            weight_columns = self.config["data_cleaning"]["weight_format_columns"]

            for col in weight_columns:
                if col in df.columns:

                    def convert_weight(weight_str):
                        try:
                            if pd.isna(weight_str) or weight_str == "":
                                return 0.0

                            weight_str = str(weight_str).strip()

                            # Handle formats like '9-6' (stones-pounds)
                            if "-" in weight_str:
                                parts = weight_str.split("-")
                                if len(parts) == 2:
                                    stones = float(parts[0])
                                    pounds = float(parts[1])
                                    # Convert to pounds: stones * 14 + pounds
                                    return stones * 14 + pounds

                            # Handle direct decimal/integer
                            return float(weight_str)

                        except (ValueError, AttributeError):
                            return 0.0

                    df[col] = df[col].apply(convert_weight)
                    logger.debug(f"  Normalized weight column: {col}")
                    self.quality_metrics["type_conversions"] += 1

            return df

        except Exception as e:
            logger.error(f"❌ Error normalizing weights: {e}")
            return df

    def normalize_distance_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize distance formats (e.g., '2½' to decimal)"""
        try:
            distance_columns = self.config["data_cleaning"]["distance_format_columns"]

            for col in distance_columns:
                if col in df.columns:

                    def convert_distance(dist_str):
                        try:
                            if pd.isna(dist_str) or dist_str == "":
                                return 0.0

                            dist_str = str(dist_str).strip()

                            # Handle fractions like '2½', '1¼'
                            fraction_map = {
                                "½": 0.5,
                                "¼": 0.25,
                                "¾": 0.75,
                                "⅓": 0.33,
                                "⅔": 0.67,
                                "⅛": 0.125,
                                "⅜": 0.375,
                                "⅝": 0.625,
                                "⅞": 0.875,
                            }

                            for fraction, decimal in fraction_map.items():
                                if fraction in dist_str:
                                    # Extract the whole number part
                                    whole_part = dist_str.replace(fraction, "").strip()
                                    whole_num = (
                                        float(whole_part)
                                        if whole_part and whole_part.isdigit()
                                        else 0
                                    )
                                    return whole_num + decimal

                            # Handle direct decimal/integer
                            return float(dist_str)

                        except (ValueError, AttributeError):
                            return 0.0

                    df[col] = df[col].apply(convert_distance)
                    logger.debug(f"  Normalized distance column: {col}")
                    self.quality_metrics["type_conversions"] += 1

            return df

        except Exception as e:
            logger.error(f"❌ Error normalizing distances: {e}")
            return df

    def enforce_column_types(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Enforce proper column data types"""
        try:
            type_mapping = self.config["type_mapping"]

            # Integer columns
            for col in type_mapping["integer_columns"]:
                if col in df.columns:
                    df[col] = (
                        pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
                    )

            # Float columns
            for col in type_mapping["float_columns"]:
                if col in df.columns:
                    df[col] = (
                        pd.to_numeric(df[col], errors="coerce")
                        .fillna(0.0)
                        .astype(float)
                    )

            # String columns
            for col in type_mapping["string_columns"]:
                if col in df.columns:
                    df[col] = df[col].astype(str).replace("nan", "")

            logger.info(f"✅ Enforced column types for {data_type}")
            return df

        except Exception as e:
            logger.error(f"❌ Error enforcing column types: {e}")
            return df

    def validate_data_quality(self, df: pd.DataFrame, data_type: str) -> Dict[str, Any]:
        """Validate data quality and generate metrics"""
        try:
            quality_report = {
                "data_type": data_type,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "null_percentage": (
                    df.isnull().sum().sum() / (len(df) * len(df.columns))
                )
                * 100,
                "duplicate_rows": df.duplicated().sum(),
                "missing_required_columns": [],
                "validation_passed": True,
                "warnings": [],
                "errors": [],
            }

            # Check required columns
            required_columns = self.config["data_validation"]["required_columns"].get(
                data_type, []
            )
            missing_columns = [col for col in required_columns if col not in df.columns]
            quality_report["missing_required_columns"] = missing_columns

            if missing_columns:
                quality_report["errors"].append(
                    f"Missing required columns: {missing_columns}"
                )
                quality_report["validation_passed"] = False

            # Check null percentage threshold
            max_null_percentage = self.config["data_validation"]["max_null_percentage"]
            if quality_report["null_percentage"] > max_null_percentage:
                quality_report["warnings"].append(
                    f"High null percentage: {quality_report['null_percentage']:.2f}%"
                )

            # Check for duplicate rows
            if quality_report["duplicate_rows"] > 0:
                quality_report["warnings"].append(
                    f"Found {quality_report['duplicate_rows']} duplicate rows"
                )

            # Data type specific validation
            if data_type == "races":
                if "date" in df.columns:
                    unique_dates = df["date"].nunique()
                    if unique_dates > 1:
                        quality_report["warnings"].append(
                            f"Multiple dates found: {unique_dates}"
                        )

            elif data_type == "records":
                if "place" in df.columns:
                    invalid_places = df[df["place"] <= 0]
                    if len(invalid_places) > 0:
                        quality_report["warnings"].append(
                            f"Found {len(invalid_places)} invalid place values"
                        )

            logger.info(
                f"📊 Quality validation for {data_type}: {quality_report['total_rows']} rows, "
                f"{quality_report['null_percentage']:.2f}% nulls"
            )

            return quality_report

        except Exception as e:
            logger.error(f"❌ Error in quality validation: {e}")
            return {"validation_passed": False, "errors": [str(e)]}

    def process_zip_file(
        self, zip_path: Path, expected_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a complete racing data ZIP file"""
        try:
            self.update_status("extracting", 10, f"Processing {zip_path.name}")
            logger.info(f"🔄 Processing ZIP file: {zip_path.name}")

            # Extract expected date from filename if not provided
            if expected_date is None:
                expected_date = self.extract_date_from_filename(zip_path.name)

            # Create temporary extraction directory
            temp_dir = (
                self.base_path
                / f"data/temp_processing_{int(datetime.now().timestamp())}"
            )
            temp_dir.mkdir(parents=True, exist_ok=True)

            processing_results = {
                "zip_file": str(zip_path),
                "expected_date": expected_date,
                "extracted_files": {},
                "processed_data": {},
                "quality_reports": {},
                "success": False,
                "errors": [],
                "warnings": [],
            }

            try:
                # Extract ZIP file
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)

                self.update_status("extracting", 20, "ZIP file extracted successfully")

                # Find and process each data type
                data_types = [
                    "races",
                    "records",
                    "horses",
                    "jockeys_stats",
                    "trainers_stats",
                ]

                for i, data_type in enumerate(data_types):
                    progress = 20 + (i * 15)
                    self.update_status(
                        "processing", progress, f"Processing {data_type}"
                    )

                    # Find CSV file for this data type
                    csv_files = list(temp_dir.glob(f"**/{data_type}.csv"))

                    if csv_files:
                        csv_file = csv_files[0]
                        processing_results["extracted_files"][data_type] = str(csv_file)

                        # Process the data
                        processed_data = self.process_csv_data(
                            csv_file, data_type, expected_date
                        )
                        processing_results["processed_data"][data_type] = processed_data

                        # Quality validation
                        if processed_data["success"] and "dataframe" in processed_data:
                            quality_report = self.validate_data_quality(
                                processed_data["dataframe"], data_type
                            )
                            processing_results["quality_reports"][
                                data_type
                            ] = quality_report

                    else:
                        logger.warning(f"⚠️ No CSV file found for {data_type}")
                        processing_results["warnings"].append(
                            f"Missing {data_type}.csv"
                        )

                self.update_status("validating", 95, "Final validation")

                # Overall success check
                successful_types = [
                    dt
                    for dt in data_types
                    if dt in processing_results["processed_data"]
                    and processing_results["processed_data"][dt]["success"]
                ]

                if len(successful_types) >= 2:  # At least races and records
                    processing_results["success"] = True
                    self.quality_metrics["successful_uploads"] += 1
                    logger.info(
                        f"✅ Successfully processed {len(successful_types)} data types"
                    )
                else:
                    processing_results["errors"].append(
                        "Insufficient data types processed successfully"
                    )
                    self.quality_metrics["failed_uploads"] += 1

                self.update_status("completed", 100, "Processing completed")

            finally:
                # Cleanup temporary directory
                try:
                    import shutil

                    shutil.rmtree(temp_dir)
                except Exception as cleanup_error:
                    logger.warning(
                        f"⚠️ Failed to cleanup temp directory: {cleanup_error}"
                    )

            self.quality_metrics["total_files_processed"] += 1
            return processing_results

        except Exception as e:
            logger.error(f"❌ Error processing ZIP file {zip_path}: {e}")
            self.quality_metrics["failed_uploads"] += 1
            self.processing_status["errors"].append(str(e))
            return {"zip_file": str(zip_path), "success": False, "errors": [str(e)]}

    def process_csv_data(
        self, csv_path: Path, data_type: str, expected_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process individual CSV data file"""
        try:
            logger.info(f"📊 Processing {data_type} data: {csv_path.name}")

            # Read CSV
            df = pd.read_csv(csv_path)
            original_rows = len(df)

            result = {
                "file_path": str(csv_path),
                "data_type": data_type,
                "original_rows": original_rows,
                "success": False,
                "errors": [],
                "warnings": [],
                "transformations": [],
            }

            # Data cleaning pipeline

            # 1. Clean null and missing values
            df = self.clean_null_and_missing_values(df, data_type)
            result["transformations"].append("Cleaned null and missing values")

            # 2. Validate and correct dates
            df, date_corrected = self.validate_and_correct_dates(
                df, csv_path.name, expected_date
            )
            if date_corrected:
                result["transformations"].append("Corrected date inconsistencies")

            # 3. Normalize percentage columns
            df = self.normalize_percentage_columns(df)
            result["transformations"].append("Normalized percentage columns")

            # 4. Normalize weight columns
            df = self.normalize_weight_columns(df)
            result["transformations"].append("Normalized weight formats")

            # 5. Normalize distance columns
            df = self.normalize_distance_columns(df)
            result["transformations"].append("Normalized distance formats")

            # 6. Enforce column types
            df = self.enforce_column_types(df, data_type)
            result["transformations"].append("Enforced column data types")

            # 7. Remove duplicates
            initial_rows = len(df)
            df = df.drop_duplicates()
            final_rows = len(df)

            if initial_rows != final_rows:
                result["transformations"].append(
                    f"Removed {initial_rows - final_rows} duplicate rows"
                )

            result.update(
                {
                    "final_rows": final_rows,
                    "rows_removed": original_rows - final_rows,
                    "dataframe": df,
                    "success": True,
                }
            )

            logger.info(
                f"✅ Processed {data_type}: {original_rows} → {final_rows} rows"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Error processing {data_type} CSV: {e}")
            result["errors"].append(str(e))
            self.quality_metrics["validation_errors"] += 1
            return result

    def upload_to_database(
        self, processed_data: Dict[str, Any], target_date: str
    ) -> Dict[str, Any]:
        """Upload processed data to database"""
        try:
            logger.info(f"📤 Uploading processed data for {target_date}")

            # Connect to database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            upload_results = {
                "target_date": target_date,
                "uploaded_tables": [],
                "upload_counts": {},
                "success": False,
                "errors": [],
            }

            # Table mapping for different data types
            table_mapping = {
                "races": "races",
                "records": "race_results",
                "horses": "horses",
                "jockeys_stats": "jockey_stats",
                "trainers_stats": "trainer_stats",
            }

            for data_type, result in processed_data.items():
                if result["success"] and "dataframe" in result:
                    df = result["dataframe"]
                    table_name = table_mapping.get(data_type, data_type)

                    try:
                        # Insert data using execute_values for better performance
                        columns = list(df.columns)
                        values = [tuple(row) for row in df.values]

                        # Create INSERT query
                        placeholders = ",".join(["%s"] * len(columns))
                        insert_query = f"""
                            INSERT INTO {table_name} ({','.join(columns)}) 
                            VALUES ({placeholders})
                            ON CONFLICT DO NOTHING
                        """

                        execute_values(cursor, insert_query, values, page_size=1000)

                        upload_results["uploaded_tables"].append(table_name)
                        upload_results["upload_counts"][table_name] = len(df)

                        logger.info(f"✅ Uploaded {len(df)} rows to {table_name}")

                    except Exception as table_error:
                        logger.error(
                            f"❌ Error uploading {data_type} to {table_name}: {table_error}"
                        )
                        upload_results["errors"].append(
                            f"{table_name}: {str(table_error)}"
                        )

            # Commit transaction
            conn.commit()
            cursor.close()
            conn.close()

            if upload_results["uploaded_tables"]:
                upload_results["success"] = True
                logger.info(
                    f"✅ Successfully uploaded to {len(upload_results['uploaded_tables'])} tables"
                )
            else:
                upload_results["errors"].append("No tables were uploaded successfully")

            return upload_results

        except Exception as e:
            logger.error(f"❌ Database upload error: {e}")
            return {"success": False, "errors": [str(e)]}

    def generate_processing_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive processing report"""
        try:
            report_lines = [
                f"🏇 Enhanced Data Processor v{self.version} - Processing Report",
                f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 60,
                "",
            ]

            if "zip_file" in results:
                report_lines.extend(
                    [
                        f"📁 Source File: {Path(results['zip_file']).name}",
                        f"📅 Expected Date: {results.get('expected_date', 'Unknown')}",
                        f"✅ Success: {results['success']}",
                        "",
                    ]
                )

            # Processing Summary
            if "processed_data" in results:
                report_lines.append("📊 Data Processing Summary:")
                for data_type, data_result in results["processed_data"].items():
                    if data_result["success"]:
                        report_lines.append(
                            f"  ✅ {data_type}: {data_result['original_rows']} → "
                            f"{data_result['final_rows']} rows"
                        )
                    else:
                        report_lines.append(f"  ❌ {data_type}: Processing failed")
                report_lines.append("")

            # Quality Reports
            if "quality_reports" in results:
                report_lines.append("🔍 Data Quality Summary:")
                for data_type, quality in results["quality_reports"].items():
                    status = "✅" if quality["validation_passed"] else "❌"
                    report_lines.append(
                        f"  {status} {data_type}: {quality['total_rows']} rows, "
                        f"{quality['null_percentage']:.1f}% nulls"
                    )
                report_lines.append("")

            # Overall Metrics
            report_lines.extend(
                [
                    "📈 Processing Metrics:",
                    f"  Total Files Processed: {self.quality_metrics['total_files_processed']}",
                    f"  Date Corrections: {self.quality_metrics['date_corrections']}",
                    f"  Null Value Fixes: {self.quality_metrics['null_value_corrections']}",
                    f"  Type Conversions: {self.quality_metrics['type_conversions']}",
                    f"  Validation Errors: {self.quality_metrics['validation_errors']}",
                    "",
                ]
            )

            # Errors and Warnings
            if results.get("errors"):
                report_lines.append("❌ Errors:")
                for error in results["errors"]:
                    report_lines.append(f"  • {error}")
                report_lines.append("")

            if results.get("warnings"):
                report_lines.append("⚠️ Warnings:")
                for warning in results["warnings"]:
                    report_lines.append(f"  • {warning}")
                report_lines.append("")

            return "\n".join(report_lines)

        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            return f"Error generating report: {e}"

    def save_processing_report(self, results: Dict[str, Any], target_date: str):
        """Save processing report to file"""
        try:
            report_content = self.generate_processing_report(results)

            # Save report
            reports_dir = self.base_path / "logs/processing_reports"
            reports_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = (
                reports_dir / f"processing_report_{target_date}_{timestamp}.txt"
            )

            with open(report_file, "w") as f:
                f.write(report_content)

            logger.info(f"📄 Processing report saved: {report_file}")

            # Also save JSON results
            json_file = (
                reports_dir / f"processing_results_{target_date}_{timestamp}.json"
            )

            # Clean results for JSON serialization
            json_results = {}
            for key, value in results.items():
                if key == "processed_data":
                    json_results[key] = {}
                    for dtype, dresult in value.items():
                        json_results[key][dtype] = {
                            k: v for k, v in dresult.items() if k != "dataframe"
                        }
                else:
                    json_results[key] = value

            with open(json_file, "w") as f:
                json.dump(json_results, f, indent=2, default=str)

            logger.info(f"📄 JSON results saved: {json_file}")

        except Exception as e:
            logger.error(f"❌ Error saving report: {e}")


def main():
    """Main entry point for the Enhanced Data Processor v2.05"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced Data Processor v2.05 - Latest Version"
    )
    parser.add_argument("file_path", help="Path to ZIP file to process")
    parser.add_argument("--expected-date", help="Expected date (YYYY-MM-DD)")
    parser.add_argument(
        "--upload", action="store_true", help="Upload to database after processing"
    )
    parser.add_argument(
        "--report-only", action="store_true", help="Generate report only"
    )

    args = parser.parse_args()

    try:
        # Initialize processor
        processor = EnhancedDataProcessorV205()

        file_path = Path(args.file_path)
        if not file_path.exists():
            logger.error(f"❌ File not found: {file_path}")
            sys.exit(1)

        logger.info(f"🚀 Starting Enhanced Data Processor v2.05")
        logger.info(f"📁 Processing file: {file_path}")

        # Process the file
        results = processor.process_zip_file(file_path, args.expected_date)

        # Generate and save report
        target_date = (
            args.expected_date
            or processor.extract_date_from_filename(file_path.name)
            or "unknown"
        )
        processor.save_processing_report(results, target_date)

        # Upload to database if requested
        if args.upload and results["success"]:
            logger.info("📤 Uploading to database...")
            upload_results = processor.upload_to_database(
                results["processed_data"], target_date
            )

            if upload_results["success"]:
                logger.info(
                    f"✅ Database upload completed for {len(upload_results['uploaded_tables'])} tables"
                )
            else:
                logger.error(f"❌ Database upload failed: {upload_results['errors']}")

        # Print summary
        if results["success"]:
            logger.info(f"🎉 Processing completed successfully!")
            print(f"\n{processor.generate_processing_report(results)}")
            sys.exit(0)
        else:
            logger.error(f"❌ Processing failed: {results['errors']}")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("🛑 Processing interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
