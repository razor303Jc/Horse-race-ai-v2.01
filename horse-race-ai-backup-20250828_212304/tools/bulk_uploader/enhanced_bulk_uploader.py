#!/usr/bin/env python3
"""
Enhanced Bulk Uploader with Integrated Data Processing
Incorporates all existing pipeline data cleaning and processing patterns
"""

import os
import sys
import json
import pandas as pd
import psycopg2
import psycopg2.extras
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import logging
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml
import hashlib
import re


@dataclass
class UploadJob:
    """Represents a single upload job"""

    job_id: str
    file_path: Path
    table_name: str
    status: str = "pending"  # pending, processing, completed, failed
    records_total: int = 0
    records_processed: int = 0
    records_uploaded: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    validation_results: Dict = field(default_factory=dict)


@dataclass
class BulkUploadConfig:
    """Configuration for bulk upload operations"""

    batch_size: int = 1000
    max_workers: int = 4
    validation_level: str = "strict"  # strict, moderate, lenient
    conflict_resolution: str = "ignore"  # ignore, update, error
    foreign_key_handling: str = "ordered"  # ordered, disabled
    max_memory_usage: str = "1GB"
    retry_attempts: int = 3
    retry_delay: float = 1.0  # seconds
    connection_pool_size: int = 10


class DatabaseConnectionManager:
    """Manages database connections with environment detection"""

    def __init__(self):
        self.config = self._detect_environment()
        self.connection_pool = []
        self.logger = logging.getLogger(__name__)

    def _detect_environment(self) -> Dict[str, str]:
        """Detect database environment and return appropriate config"""
        # Check if running in Docker container
        if (
            os.path.exists("/.dockerenv")
            or os.environ.get("DOCKER_CONTAINER")
            or os.path.exists("/app")
        ):  # Common Docker app directory

            # Try Docker network connection first
            docker_config = {
                "host": "postgres",  # Container alias in Docker network
                "port": "5432",
                "database": "results_horse_racing_db",
                "user": "horse_racing",
                "password": "secure_password_123",
            }

            # Test Docker connection
            try:
                import psycopg2

                test_conn = psycopg2.connect(**docker_config)
                test_conn.close()
                self.logger.info("Using Docker network connection")
                return docker_config
            except Exception:
                # Fall back to environment variables
                pass

        # Local development or environment variable configuration
        return {
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": os.environ.get("DB_PORT", "5432"),
            "database": os.environ.get("DB_NAME", "results_horse_racing_db"),
            "user": os.environ.get("DB_USER", "horse_racing"),
            "password": os.environ.get("DB_PASSWORD", "secure_password_123"),
        }

    def get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(**self.config)
            conn.autocommit = False
            return conn
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise

    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            return False


class DataDiscoveryEngine:
    """Discovers and classifies data files for processing"""

    def __init__(self, config: BulkUploadConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.supported_formats = {".csv", ".json", ".xlsx", ".xls"}

    def discover_files(
        self,
        root_path: Path,
        recursive: bool = True,
        exclude_dirs: Optional[List[str]] = None,
    ) -> List[Path]:
        """Discover data files in directory, excluding specified directories"""
        if exclude_dirs is None:
            exclude_dirs = ["non_target"]

        files = []

        if recursive:
            for file_path in root_path.rglob("*"):
                # Skip if in excluded directory
                if any(excl in str(file_path) for excl in exclude_dirs):
                    continue

                if (
                    file_path.is_file()
                    and file_path.suffix.lower() in self.supported_formats
                ):
                    files.append(file_path)
        else:
            for file_path in root_path.iterdir():
                if (
                    file_path.is_file()
                    and file_path.suffix.lower() in self.supported_formats
                ):
                    files.append(file_path)

        return sorted(files)

    def classify_file(self, file_path: Path) -> Optional[str]:
        """Classify file to determine target table"""
        file_name = file_path.name.lower()

        # Classification rules based on existing patterns
        classification_rules = {
            "horses": ["horse", "mapped_horses", "complete_mapped_horses"],
            "jockeys_stats": [
                "jockey",
                "mapped_jockeys_stats",
                "complete_mapped_jockeys_stats",
            ],
            "trainers_stats": [
                "trainer",
                "mapped_trainers_stats",
                "complete_mapped_trainers_stats",
            ],
            "races": ["race", "mapped_races", "complete_mapped_races"],
            "records": [
                "record",
                "result",
                "mapped_records",
                "complete_mapped_records",
            ],
        }

        for table_name, keywords in classification_rules.items():
            if any(keyword in file_name for keyword in keywords):
                return table_name

        return None

    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from data file"""
        try:
            metadata = {
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime),
                "format": file_path.suffix.lower(),
            }

            # Extract basic data info based on format
            if file_path.suffix.lower() == ".csv":
                try:
                    # Read first few rows to get column info
                    df_sample = pd.read_csv(file_path, nrows=10)
                    metadata.update(
                        {
                            "columns": list(df_sample.columns),
                            "estimated_rows": sum(1 for _ in open(file_path)) - 1,
                            "sample_data": df_sample.head(3).to_dict("records"),
                        }
                    )
                except Exception as e:
                    self.logger.warning(f"Could not extract CSV metadata: {e}")

            return metadata

        except Exception as e:
            self.logger.error(f"Error extracting metadata from {file_path}: {e}")
            return {"file_path": str(file_path), "error": str(e)}


class EnhancedDataProcessor:
    """Data processor with all pipeline cleaning patterns integrated"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.column_mappings = self._load_column_mappings()

    def _load_column_mappings(self) -> Dict:
        """Load column mappings from configuration file"""
        config_file = Path("config/complete_csv_column_mapping.json")

        # Try different paths
        possible_paths = [
            config_file,
            Path("../config/complete_csv_column_mapping.json"),
            Path("../../config/complete_csv_column_mapping.json"),
            Path("/app/config/complete_csv_column_mapping.json"),
        ]

        for path in possible_paths:
            try:
                if path.exists():
                    with open(path, "r") as f:
                        config = json.load(f)
                    self.logger.info(f"Loaded column mappings from {path}")
                    return config["table_mappings"]
            except Exception as e:
                self.logger.warning(f"Could not load mappings from {path}: {e}")

        # Return default mappings if config file not found
        self.logger.warning("Using default column mappings")
        return self._get_default_mappings()

    def _get_default_mappings(self) -> Dict:
        """Default column mappings based on existing patterns"""
        return {
            "horses": {
                "column_mapping": {
                    "horse_id": "id",
                    "horse_name": "name",
                    "uptodate": "uptodate",
                },
                "null_handling": {
                    "integers": ["horse_id", "age", "total_races", "wins"],
                    "decimals": ["percentage_wins", "percentage_placed"],
                    "strings": ["horse_name", "country", "uptodate"],
                },
            },
            "jockeys_stats": {
                "column_mapping": {
                    "jockey_id": "Jockey_ID",
                    "uptodate": "UptoDate",
                    "jockey_name": "Name",
                },
                "null_handling": {
                    "integers": ["total_races", "wins", "placed"],
                    "decimals": ["percentage_wins", "percentage_placed"],
                    "strings": ["jockey_id", "jockey_name", "uptodate"],
                },
            },
            "trainers_stats": {
                "column_mapping": {
                    "trainer_id": "Trainer_ID",
                    "uptodate": "UptoDate",
                    "trainer_name": "Name",
                },
                "null_handling": {
                    "integers": ["total_races", "wins", "placed"],
                    "decimals": ["percentage_wins", "percentage_placed"],
                    "strings": ["trainer_id", "trainer_name", "uptodate"],
                },
            },
            "records": {
                "column_mapping": {
                    "record_id": "ID",
                    "race_id": "Race_ID",
                    "horse_id": "Horse_ID",
                },
                "null_handling": {
                    "integers": ["record_id", "race_id", "horse_id", "position"],
                    "decimals": ["weight_uk", "sp", "distance_btn"],
                    "strings": ["horse", "jockey", "trainer"],
                },
            },
            "races": {
                "column_mapping": {
                    "race_id": "Race_ID",
                    "course": "Course",
                    "race_name": "Race_name",
                },
                "null_handling": {
                    "integers": ["race_number", "runners", "draw"],
                    "decimals": [],
                    "strings": ["race_id", "course", "race_name"],
                },
            },
        }

    def clean_dash_symbols(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Clean dash/hyphen symbols based on data type - from existing pipeline"""
        self.logger.info(f"Cleaning dash symbols for {table_name}...")

        table_config = self.column_mappings.get(table_name, {})
        null_handling = table_config.get("null_handling", {})

        integer_fields = null_handling.get("integers", [])
        decimal_fields = null_handling.get("decimals", [])
        string_fields = null_handling.get("strings", [])

        cleaned_count = 0

        for column in df.columns:
            if column == "weight_uk":
                # Special handling for UK weight format "10-2" -> "10.2"
                mask = df[column].astype(str).str.match(r"^\d+-\d+$")
                if mask.any():
                    df.loc[mask, column] = (
                        df.loc[mask, column].astype(str).str.replace("-", ".")
                    )
                    cleaned_count += mask.sum()

                # Convert standalone "-" to 0 for weight
                standalone_dash = df[column].astype(str) == "-"
                if standalone_dash.any():
                    df.loc[standalone_dash, column] = 0
                    cleaned_count += standalone_dash.sum()

            elif column in integer_fields:
                # Integer fields: "-" → 0
                dash_mask = df[column].astype(str) == "-"
                if dash_mask.any():
                    df.loc[dash_mask, column] = 0
                    cleaned_count += dash_mask.sum()

            elif column in decimal_fields:
                # Decimal fields: "-" → 0
                dash_mask = df[column].astype(str) == "-"
                if dash_mask.any():
                    df.loc[dash_mask, column] = 0
                    cleaned_count += dash_mask.sum()

            elif column in string_fields:
                # String fields: "-" → "None"
                dash_mask = df[column].astype(str) == "-"
                if dash_mask.any():
                    df.loc[dash_mask, column] = "None"
                    cleaned_count += dash_mask.sum()

        if cleaned_count > 0:
            self.logger.info(f"Cleaned {cleaned_count} dash symbols")

        return df

    def clean_percentage_fields(
        self, df: pd.DataFrame, percentage_columns: List[str]
    ) -> pd.DataFrame:
        """Convert percentage strings like '16.67%' to decimal numbers"""
        for col in percentage_columns:
            if col in df.columns:
                df[col] = (
                    df[col].astype(str).str.replace("%", "").str.replace("nan", "0")
                )
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0) / 100
        return df

    def clean_distance_fields(
        self, df: pd.DataFrame, distance_fields: List[str]
    ) -> pd.DataFrame:
        """Convert racing distance fractions to decimals"""
        for field in distance_fields:
            if field in df.columns:
                df[field] = df[field].astype(str)
                # Convert fractions to decimals
                df[field] = df[field].str.replace("½", "0.5")
                df[field] = df[field].str.replace("¼", "0.25")
                df[field] = df[field].str.replace("¾", "0.75")
                df[field] = df[field].str.replace("nk", "0.1")  # neck
                df[field] = df[field].str.replace("hd", "0.05")  # head
                df[field] = df[field].str.replace("sh", "0.01")  # short head
                df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)
        return df

    def clean_table_specific_data(
        self, df: pd.DataFrame, table_name: str
    ) -> pd.DataFrame:
        """Apply table-specific cleaning based on existing pipeline patterns"""

        if table_name == "races":
            # Fix draw field - convert 'Low' to 0
            if "draw" in df.columns:
                df["draw"] = df["draw"].replace("Low", 0)
                df["draw"] = (
                    pd.to_numeric(df["draw"], errors="coerce").fillna(0).astype(int)
                )

            # Clean integer fields
            integer_fields = [
                "race_number",
                "course_id",
                "runners_racecard",
                "runners",
                "ew_racecard",
                "ew",
                "places_ew_racecard",
                "places_ew",
            ]
            for field in integer_fields:
                if field in df.columns:
                    df[field] = (
                        pd.to_numeric(df[field], errors="coerce").fillna(0).astype(int)
                    )

        elif table_name == "records":
            # Remove columns that don't exist in database
            columns_to_remove = []
            for col in df.columns:
                if (
                    "odds" in col.lower()
                    and col not in ["sp"]
                    or col
                    in [
                        "result_race_id",
                        "result_horse_number",
                        "result_id",
                        "timeform_comments",
                    ]
                ):
                    columns_to_remove.append(col)

            if columns_to_remove:
                df = df.drop(columns=columns_to_remove, errors="ignore")
                self.logger.info(f"Removed columns: {columns_to_remove}")

            # Fix numeric fields
            numeric_fields = [
                "record_id",
                "race_id",
                "horse_number",
                "position",
                "draw",
                "horse_id",
                "age",
                "or_rating",
                "jockey_id",
                "trainer_id",
                "fav",
            ]
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)

            # Clean distance fields with fractions
            distance_fields = ["distance_btn", "distance_btn_total"]
            df = self.clean_distance_fields(df, distance_fields)

            # Handle weight_uk field
            if "weight_uk" in df.columns:
                df["weight_uk"] = pd.to_numeric(
                    df["weight_uk"], errors="coerce"
                ).fillna(0)

            # Handle SP (starting price) field
            if "sp" in df.columns:
                df["sp"] = pd.to_numeric(df["sp"], errors="coerce").fillna(0)

        elif table_name == "horses":
            # Fix percentage fields
            percentage_cols = [
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
            ]
            df = self.clean_percentage_fields(df, percentage_cols)

            # Fix numeric fields
            numeric_fields = [
                "horse_id",
                "race_id_last_race",
                "age",
                "total_races",
                "wins",
                "placed",
            ]
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)

        elif table_name in ["jockeys_stats", "trainers_stats"]:
            # Fix percentage fields for stats tables
            percentage_cols = [
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
            ]
            df = self.clean_percentage_fields(df, percentage_cols)

        return df

    def apply_column_mapping(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Apply column mapping from CSV to database schema"""
        table_config = self.column_mappings.get(table_name, {})
        column_mapping = table_config.get("column_mapping", {})

        if column_mapping:
            # Reverse mapping (CSV column -> DB column)
            reverse_mapping = {v: k for k, v in column_mapping.items()}
            df = df.rename(columns=reverse_mapping)
            self.logger.info(f"Applied column mappings for {table_name}")

        return df

    def process_file_data(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Complete data processing pipeline"""
        self.logger.info(f"Processing {table_name} data: {len(df)} rows")

        # Step 1: Apply column mapping
        df = self.apply_column_mapping(df, table_name)

        # Step 2: Clean dash symbols
        df = self.clean_dash_symbols(df, table_name)

        # Step 3: Apply table-specific cleaning
        df = self.clean_table_specific_data(df, table_name)

        # Step 4: Remove empty rows
        initial_rows = len(df)
        df = df.dropna(how="all")
        removed_rows = initial_rows - len(df)
        if removed_rows > 0:
            self.logger.info(f"Removed {removed_rows} empty rows")

        self.logger.info(f"Processed {table_name}: {len(df)} rows ready")
        return df


class ValidationEngine:
    """Validation engine integrated with data processing"""

    def __init__(
        self,
        db_manager: DatabaseConnectionManager,
        data_processor: EnhancedDataProcessor,
        config: BulkUploadConfig,
    ):
        self.db_manager = db_manager
        self.data_processor = data_processor
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_table_schema(self, table_name: str) -> Dict[str, Dict]:
        """Get database schema for table"""
        try:
            conn = self.db_manager.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position
                """,
                    (table_name,),
                )

                schema = {}
                for row in cur.fetchall():
                    schema[row[0]] = {
                        "type": row[1],
                        "nullable": row[2] == "YES",
                        "default": row[3],
                    }

            conn.close()
            return schema

        except Exception as e:
            self.logger.error(f"Error getting schema for {table_name}: {e}")
            return {}

    def validate_file_structure(
        self, file_path: Path, table_name: str
    ) -> Dict[str, Any]:
        """Validate file structure against table schema"""
        results = {
            "valid": False,
            "issues": [],
            "fixes": [],
            "column_mapping": {},
            "estimated_rows": 0,
        }

        try:
            # Load data sample
            if file_path.suffix.lower() == ".csv":
                df_sample = pd.read_csv(file_path, nrows=100)
                results["estimated_rows"] = sum(1 for _ in open(file_path)) - 1
            else:
                results["issues"].append(f"Unsupported format: {file_path.suffix}")
                return results

            # Get column mappings
            table_config = self.data_processor.column_mappings.get(table_name, {})
            column_mapping = table_config.get("column_mapping", {})

            # Apply reverse mapping for validation
            reverse_mapping = {v: k for k, v in column_mapping.items()}

            csv_columns = list(df_sample.columns)
            mapped_columns = []

            for csv_col in csv_columns:
                if csv_col in reverse_mapping:
                    mapped_col = reverse_mapping[csv_col]
                    results["column_mapping"][csv_col] = mapped_col
                    mapped_columns.append(mapped_col)
                    results["fixes"].append(f"Map '{csv_col}' to '{mapped_col}'")
                else:
                    # Look for case-insensitive match
                    found_match = False
                    for map_csv, map_db in reverse_mapping.items():
                        if csv_col.lower() == map_csv.lower():
                            results["column_mapping"][csv_col] = map_db
                            mapped_columns.append(map_db)
                            results["fixes"].append(
                                f"Case match: '{csv_col}' to '{map_db}'"
                            )
                            found_match = True
                            break

                    if not found_match:
                        results["issues"].append(f"No mapping for column: {csv_col}")

            # Basic validation - if we have column mappings, we're probably good
            if results["column_mapping"]:
                results["valid"] = True

            return results

        except Exception as e:
            self.logger.error(f"Error validating {file_path}: {e}")
            results["issues"].append(f"Validation error: {str(e)}")
            return results


class BulkUploadEngine:
    """Handles bulk upload operations with data processing"""

    def __init__(
        self,
        db_manager: DatabaseConnectionManager,
        data_processor: EnhancedDataProcessor,
        config: BulkUploadConfig,
    ):
        self.db_manager = db_manager
        self.data_processor = data_processor
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Foreign key constraint ordering
        self.upload_order = {
            "races": 1,  # Parent table
            "horses": 2,  # Independent
            "jockeys_stats": 2,  # Independent
            "trainers_stats": 2,  # Independent
            "records": 3,  # Child table with foreign keys
        }

    def upload_dataframe(
        self, df: pd.DataFrame, table_name: str, job: UploadJob
    ) -> Tuple[bool, str]:
        """Upload DataFrame to database table"""
        try:
            conn = self.db_manager.get_connection()

            with conn:
                # Prepare data for bulk insert
                columns = list(df.columns)

                # Convert DataFrame to list of tuples for bulk insert
                data_tuples = []
                for _, row in df.iterrows():
                    row_data = []
                    for col in columns:
                        value = row[col]
                        # Handle pandas NaT and NaN values
                        if pd.isna(value):
                            row_data.append(None)
                        else:
                            row_data.append(value)
                    data_tuples.append(tuple(row_data))

                # Build bulk insert query
                placeholders = ",".join(["%s"] * len(columns))
                columns_str = ",".join(columns)

                if self.config.conflict_resolution == "ignore":
                    query = f"""
                        INSERT INTO {table_name} ({columns_str}) 
                        VALUES ({placeholders})
                        ON CONFLICT DO NOTHING
                    """
                else:
                    query = f"""
                        INSERT INTO {table_name} ({columns_str}) 
                        VALUES ({placeholders})
                    """

                # Execute bulk insert with progress tracking
                batch_size = self.config.batch_size
                uploaded_count = 0

                with conn.cursor() as cur:
                    for i in range(0, len(data_tuples), batch_size):
                        batch = data_tuples[i : i + batch_size]
                        current_batch = (i // batch_size) + 1

                        try:
                            psycopg2.extras.execute_values(
                                cur, query, batch, template=None, page_size=batch_size
                            )

                            uploaded_count += len(batch)
                            job.records_processed = uploaded_count

                            # Log progress
                            total_batches = (
                                len(data_tuples) + batch_size - 1
                            ) // batch_size
                            self.logger.info(
                                f"Batch {current_batch}/{total_batches} "
                                f"({uploaded_count}/{len(data_tuples)})"
                            )

                        except Exception as e:
                            self.logger.error(f"Error in batch {current_batch}: {e}")
                            if self.config.conflict_resolution == "error":
                                raise
                            continue

                job.records_uploaded = uploaded_count
                conn.commit()

                msg = f"Uploaded {uploaded_count} records to {table_name}"
                self.logger.info(msg)
                return True, msg

        except Exception as e:
            error_msg = f"Upload failed for {table_name}: {str(e)}"
            self.logger.error(error_msg)
            try:
                if "conn" in locals():
                    conn.rollback()
            except Exception:
                pass
            return False, error_msg


class BulkUploader:
    """Main bulk uploader orchestrator with integrated data processing"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self._setup_logging()

        # Initialize components
        self.db_manager = DatabaseConnectionManager()
        self.data_processor = EnhancedDataProcessor()
        self.discovery_engine = DataDiscoveryEngine(self.config)
        self.validation_engine = ValidationEngine(
            self.db_manager, self.data_processor, self.config
        )
        self.upload_engine = BulkUploadEngine(
            self.db_manager, self.data_processor, self.config
        )

        # Job tracking
        self.jobs: Dict[str, UploadJob] = {}

        self.logger = logging.getLogger(__name__)

    def _load_config(self, config_path: Optional[Path]) -> BulkUploadConfig:
        """Load configuration from file or use defaults"""
        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    config_data = yaml.safe_load(f)
                return BulkUploadConfig(**config_data.get("processing", {}))
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")
                print("Using default configuration")

        return BulkUploadConfig()

    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("/tmp/bulk_uploader.log"),
            ],
        )

    def _generate_job_id(self, file_path: Path) -> str:
        """Generate unique job ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
        return f"job_{timestamp}_{file_hash}"

    def discover_and_queue_files(
        self,
        root_path: Path,
        recursive: bool = True,
        exclude_dirs: Optional[List[str]] = None,
    ) -> List[str]:
        """Discover files and queue them for processing"""
        self.logger.info(f"Discovering files in {root_path}")

        files = self.discovery_engine.discover_files(root_path, recursive, exclude_dirs)
        job_ids = []

        for file_path in files:
            table_name = self.discovery_engine.classify_file(file_path)
            if not table_name:
                self.logger.warning(f"Could not classify file: {file_path}")
                continue

            job_id = self._generate_job_id(file_path)
            job = UploadJob(job_id=job_id, file_path=file_path, table_name=table_name)

            # Extract metadata
            metadata = self.discovery_engine.extract_metadata(file_path)
            job.records_total = metadata.get("estimated_rows", 0)

            self.jobs[job_id] = job
            job_ids.append(job_id)

            self.logger.info(f"Queued {file_path.name} → {table_name} ({job_id})")

        return job_ids

    def process_job(self, job_id: str) -> bool:
        """Process a single upload job with full data processing"""
        if job_id not in self.jobs:
            self.logger.error(f"Job {job_id} not found")
            return False

        job = self.jobs[job_id]
        job.status = "processing"
        job.start_time = datetime.now()

        try:
            self.logger.info(f"Processing job {job_id}: {job.file_path.name}")

            # Step 1: Validate file structure
            validation_results = self.validation_engine.validate_file_structure(
                job.file_path, job.table_name
            )
            job.validation_results = validation_results

            if (
                not validation_results["valid"]
                and self.config.validation_level == "strict"
            ):
                job.status = "failed"
                job.error_message = f"Validation failed: {validation_results['issues']}"
                return False

            # Step 2: Load and process data
            self.logger.info("Loading and processing file data...")
            if job.file_path.suffix.lower() == ".csv":
                df = pd.read_csv(job.file_path)
            else:
                job.status = "failed"
                job.error_message = f"Unsupported format: {job.file_path.suffix}"
                return False

            # Apply comprehensive data processing
            df = self.data_processor.process_file_data(df, job.table_name)
            job.records_total = len(df)

            # Step 3: Upload to database
            self.logger.info("Uploading to database...")
            upload_success, upload_msg = self.upload_engine.upload_dataframe(
                df, job.table_name, job
            )

            if upload_success:
                job.status = "completed"
                job.end_time = datetime.now()
                self.logger.info(f"Job {job_id} completed: {upload_msg}")
                return True
            else:
                job.status = "failed"
                job.error_message = upload_msg
                return False

        except Exception as e:
            job.status = "failed"
            job.error_message = f"Unexpected error: {str(e)}"
            job.end_time = datetime.now()
            self.logger.error(f"Job {job_id} failed: {e}")
            return False

    def process_all_jobs(self, max_workers: Optional[int] = None) -> Dict[str, Any]:
        """Process all queued jobs with foreign key constraint ordering"""
        if not self.jobs:
            return {"message": "No jobs to process"}

        # Sort jobs by upload order
        sorted_jobs = sorted(
            self.jobs.items(),
            key=lambda x: self.upload_engine.upload_order.get(x[1].table_name, 99),
        )

        workers = max_workers or self.config.max_workers
        results = {
            "total_jobs": len(self.jobs),
            "successful": 0,
            "failed": 0,
            "job_results": {},
        }

        self.logger.info(f"Processing {len(self.jobs)} jobs")

        # Process jobs respecting foreign key constraints
        current_order = 1
        while sorted_jobs:
            # Get all jobs for current order level
            current_batch = []
            remaining_jobs = []

            for job_id, job in sorted_jobs:
                order = self.upload_engine.upload_order.get(job.table_name, 99)
                if order == current_order:
                    current_batch.append((job_id, job))
                else:
                    remaining_jobs.append((job_id, job))

            if not current_batch:
                current_order += 1
                if current_order > 10:  # Safety break
                    break
                continue

            # Process current batch
            for job_id, job in current_batch:
                success = self.process_job(job_id)
                results["job_results"][job_id] = {
                    "success": success,
                    "table": job.table_name,
                    "records": job.records_uploaded,
                    "error": job.error_message,
                }
                if success:
                    results["successful"] += 1
                else:
                    results["failed"] += 1

            sorted_jobs = remaining_jobs
            current_order += 1

        # Generate summary
        success_rate = (
            (results["successful"] / results["total_jobs"] * 100)
            if results["total_jobs"] > 0
            else 0
        )
        self.logger.info(
            f"Bulk upload completed: {results['successful']}/"
            f"{results['total_jobs']} successful ({success_rate:.1f}%)"
        )

        return results

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        if job_id not in self.jobs:
            return None

        job = self.jobs[job_id]
        return {
            "job_id": job_id,
            "file_path": str(job.file_path),
            "table_name": job.table_name,
            "status": job.status,
            "records_total": job.records_total,
            "records_processed": job.records_processed,
            "records_uploaded": job.records_uploaded,
            "start_time": job.start_time.isoformat() if job.start_time else None,
            "end_time": job.end_time.isoformat() if job.end_time else None,
            "error_message": job.error_message,
            "validation_results": job.validation_results,
        }

    def get_all_jobs_status(self) -> List[Dict[str, Any]]:
        """Get status of all jobs"""
        return [
            self.get_job_status(job_id)
            for job_id in self.jobs.keys()
            if self.get_job_status(job_id) is not None
        ]


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Bulk Uploader")
    parser.add_argument("path", type=Path, help="Path to data directory")
    parser.add_argument("--config", type=Path, help="Configuration file")
    parser.add_argument("--recursive", action="store_true", help="Search recursively")
    parser.add_argument(
        "--exclude-dirs",
        nargs="+",
        default=["non_target"],
        help="Directories to exclude",
    )
    parser.add_argument("--workers", type=int, help="Number of workers")
    parser.add_argument(
        "--test-connection", action="store_true", help="Test database connection"
    )

    args = parser.parse_args()

    # Initialize uploader
    uploader = BulkUploader(args.config)

    # Test connection if requested
    if args.test_connection:
        if uploader.db_manager.test_connection():
            print("✅ Database connection successful")
            return 0
        else:
            print("❌ Database connection failed")
            return 1

    # Verify path exists
    if not args.path.exists():
        print(f"❌ Path does not exist: {args.path}")
        return 1

    try:
        # Discover and queue files (excluding non_target)
        print(f"🔍 Discovering files in {args.path} (excluding {args.exclude_dirs})")
        job_ids = uploader.discover_and_queue_files(
            args.path, args.recursive, args.exclude_dirs
        )

        if not job_ids:
            print("❌ No files found to process")
            return 1

        print(f"📋 Queued {len(job_ids)} files for processing")

        # Process all jobs
        print("🚀 Starting bulk upload with data processing...")
        results = uploader.process_all_jobs(args.workers)

        # Display results
        print("\n📊 BULK UPLOAD RESULTS:")
        print(f"   Total jobs: {results['total_jobs']}")
        print(f"   Successful: {results['successful']}")
        print(f"   Failed: {results['failed']}")

        total = results["total_jobs"]
        success_rate = (results["successful"] / total * 100) if total > 0 else 0
        print(f"   Success rate: {success_rate:.1f}%")

        # Show detailed results
        print("\n📋 DETAILED RESULTS:")
        for job_id, result in results["job_results"].items():
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['table']} - {result['records']} records")
            if result["error"]:
                print(f"      Error: {result['error']}")

        return 0 if results["failed"] == 0 else 1

    except Exception as e:
        print(f"❌ Bulk upload failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
