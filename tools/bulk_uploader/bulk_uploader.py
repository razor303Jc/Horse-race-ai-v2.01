#!/usr/bin/env python3
"""
Bulk Uploader - Comprehensive Data Processing and Upload System
Based on analysis of existing upload infrastructure with enhancements for scalability
"""

import os
import sys
import json
import pandas as pd
import psycopg2
import psycopg2.extras
import psycopg2.sql
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
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
        if os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER"):
            # Docker container environment - use container network
            return {
                "host": os.environ.get(
                    "DB_HOST", "postgres"
                ),  # postgres container alias
                "port": os.environ.get("DB_PORT", "5432"),
                "database": os.environ.get("DB_NAME", "results_horse_racing_db"),
                "user": os.environ.get("DB_USER", "horse_racing"),
                "password": os.environ.get("DB_PASSWORD", "secure_password_123"),
            }
        else:
            # Local development environment - check if we can use Docker network
            # Try to connect via docker network first, fallback to localhost
            docker_config = {
                "host": "postgres",
                "port": "5432",
                "database": "results_horse_racing_db",
                "user": "horse_racing",
                "password": "secure_password_123",
            }

            # Test docker network connection first
            try:
                import psycopg2

                test_conn = psycopg2.connect(**docker_config)
                test_conn.close()
                self.logger.info(
                    "Using Docker network connection to postgres container"
                )
                return docker_config
            except:
                # Fallback to localhost or environment variables
                self.logger.info(
                    "Docker network unavailable, using localhost configuration"
                )
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
        self, root_path: Path, recursive: bool = True, exclude_dirs: List[str] = None
    ) -> List[Path]:
        """Discover data files in directory with exclusion support"""
        files = []
        exclude_dirs = exclude_dirs or []

        if recursive:
            for file_path in root_path.rglob("*"):
                # Check if any parent directory is in exclude list
                if any(excl_dir in str(file_path) for excl_dir in exclude_dirs):
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

        # Define classification rules based on existing patterns
        classification_rules = {
            "horses": ["horse", "mapped_horses"],
            "jockeys_stats": ["jockey", "mapped_jockeys_stats"],
            "trainers_stats": ["trainer", "mapped_trainers_stats"],
            "races": ["race", "mapped_races"],
            "records": ["record", "result", "mapped_records"],
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
                            "estimated_rows": sum(1 for _ in open(file_path))
                            - 1,  # Subtract header
                            "sample_data": df_sample.head(3).to_dict("records"),
                        }
                    )
                except Exception as e:
                    self.logger.warning(
                        f"Could not extract CSV metadata from {file_path}: {e}"
                    )

            return metadata

        except Exception as e:
            self.logger.error(f"Error extracting metadata from {file_path}: {e}")
            return {"file_path": str(file_path), "error": str(e)}


class ValidationEngine:
    """Comprehensive validation engine based on existing patterns"""

    def __init__(self, db_manager: DatabaseConnectionManager, config: BulkUploadConfig):
        self.db_manager = db_manager
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Column mappings from existing schema guardian
        self.column_mappings = {
            "horses": {
                "id": "horse_id",
                "name": "horse_name",
                "UptoDate": "uptodate",
                "uptodate": "uptodate",
            },
            "jockeys_stats": {
                "UptoDate": "uptodate",
                "Jockey_ID": "jockey_id",
                "Name": "jockey_name",
            },
            "trainers_stats": {
                "UptoDate": "uptodate",
                "Trainer_ID": "trainer_id",
                "Name": "trainer_name",
            },
            "records": {"id": "record_id", "Race_ID": "race_id"},
            "races": {"Race_ID": "race_id"},
        }

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
                self.logger.warning(f"Unsupported file format: {file_path.suffix}")
                results["issues"].append(f"Unsupported file format: {file_path.suffix}")
                return results

            # Get table schema
            db_schema = self.get_table_schema(table_name)
            if not db_schema:
                results["issues"].append(
                    f"Could not retrieve schema for table: {table_name}"
                )
                return results

            csv_columns = list(df_sample.columns)
            db_columns = list(db_schema.keys())
            table_mappings = self.column_mappings.get(table_name, {})

            # Validate each column
            for csv_col in csv_columns:
                if csv_col in db_columns:
                    # Direct match
                    results["column_mapping"][csv_col] = csv_col
                elif csv_col in table_mappings:
                    # Mapping available
                    mapped_col = table_mappings[csv_col]
                    if mapped_col in db_columns:
                        results["column_mapping"][csv_col] = mapped_col
                        results["fixes"].append(f"Map '{csv_col}' to '{mapped_col}'")
                    else:
                        results["issues"].append(
                            f"Mapped column '{mapped_col}' doesn't exist"
                        )
                else:
                    # Look for case-insensitive match
                    matches = [
                        db_col
                        for db_col in db_columns
                        if db_col.lower() == csv_col.lower()
                    ]
                    if matches:
                        results["column_mapping"][csv_col] = matches[0]
                        results["fixes"].append(
                            f"Fix case: '{csv_col}' → '{matches[0]}'"
                        )
                    else:
                        results["issues"].append(f"No match for CSV column '{csv_col}'")

            # Check for required columns
            required_columns = [
                col
                for col, schema in db_schema.items()
                if not schema["nullable"] and schema["default"] is None
            ]

            mapped_db_columns = set(results["column_mapping"].values())
            missing_required = set(required_columns) - mapped_db_columns

            if missing_required:
                for col in missing_required:
                    results["issues"].append(f"Missing required column: {col}")

            # Determine if validation passed
            results["valid"] = len(results["issues"]) == 0

            self.logger.info(
                f"Validation for {file_path.name} → {table_name}: "
                f"{'PASSED' if results['valid'] else 'FAILED'}"
            )

            return results

        except Exception as e:
            self.logger.error(f"Error validating {file_path}: {e}")
            results["issues"].append(f"Validation error: {str(e)}")
            return results

    def validate_data_integrity(
        self, df: pd.DataFrame, table_name: str
    ) -> Dict[str, Any]:
        """Validate data integrity based on existing patterns"""
        results = {"valid": True, "warnings": [], "errors": []}

        try:
            # Check for completely empty rows
            empty_rows = df.isnull().all(axis=1).sum()
            if empty_rows > 0:
                results["warnings"].append(f"Found {empty_rows} completely empty rows")

            # Check for duplicate records based on primary key columns
            if table_name == "horses" and "horse_id" in df.columns:
                duplicates = df.duplicated(subset=["horse_id"]).sum()
                if duplicates > 0:
                    results["warnings"].append(
                        f"Found {duplicates} duplicate horse_id values"
                    )

            elif table_name == "races" and "race_id" in df.columns:
                duplicates = df.duplicated(subset=["race_id"]).sum()
                if duplicates > 0:
                    results["warnings"].append(
                        f"Found {duplicates} duplicate race_id values"
                    )

            # Date format validation
            date_columns = [
                col
                for col in df.columns
                if any(
                    date_word in col.lower()
                    for date_word in ["date", "time", "uptodate"]
                )
            ]

            for col in date_columns:
                try:
                    pd.to_datetime(df[col], errors="coerce")
                except Exception:
                    results["errors"].append(f"Invalid date format in column: {col}")

            # Check for obviously invalid data
            numeric_columns = df.select_dtypes(include=["number"]).columns
            for col in numeric_columns:
                if (df[col] < 0).any():
                    negative_count = (df[col] < 0).sum()
                    results["warnings"].append(
                        f"Found {negative_count} negative values in {col}"
                    )

            if results["errors"]:
                results["valid"] = False

            return results

        except Exception as e:
            self.logger.error(f"Error in data integrity validation: {e}")
            results["valid"] = False
            results["errors"].append(f"Integrity validation error: {str(e)}")
            return results


class BulkProcessingEngine:
    """Processes data files for upload"""

    def __init__(self, validator: ValidationEngine, config: BulkUploadConfig):
        self.validator = validator
        self.config = config
        self.logger = logging.getLogger(__name__)

    def process_file(
        self, file_path: Path, table_name: str, validation_results: Dict
    ) -> Tuple[bool, pd.DataFrame, str]:
        """Process a single file for upload"""
        try:
            self.logger.info(f"Processing {file_path.name} for table {table_name}")

            # Load the full dataset
            if file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
            else:
                return (
                    False,
                    pd.DataFrame(),
                    f"Unsupported file format: {file_path.suffix}",
                )

            # Apply column mappings
            column_mapping = validation_results.get("column_mapping", {})
            if column_mapping:
                df = df.rename(columns=column_mapping)
                self.logger.info(f"Applied column mappings: {column_mapping}")

            # Remove empty rows
            initial_rows = len(df)
            df = df.dropna(how="all")
            removed_rows = initial_rows - len(df)
            if removed_rows > 0:
                self.logger.info(f"Removed {removed_rows} empty rows")

            # Handle NULL values based on database schema
            table_schema = self.validator.get_table_schema(table_name)
            for col, schema_info in table_schema.items():
                if col in df.columns:
                    if not schema_info["nullable"]:
                        # Replace NaN with appropriate default for non-nullable columns
                        if schema_info["type"] in ["integer", "bigint", "smallint"]:
                            df[col] = df[col].fillna(0)
                        elif schema_info["type"] in [
                            "text",
                            "varchar",
                            "character varying",
                        ]:
                            df[col] = df[col].fillna("")
                        elif schema_info["type"] in ["boolean"]:
                            df[col] = df[col].fillna(False)

            # Data type conversions
            self._convert_data_types(df, table_schema)

            # Final validation
            integrity_results = self.validator.validate_data_integrity(df, table_name)
            if not integrity_results["valid"]:
                error_msg = (
                    f"Data integrity validation failed: {integrity_results['errors']}"
                )
                return False, pd.DataFrame(), error_msg

            self.logger.info(
                f"Successfully processed {len(df)} records for {table_name}"
            )
            return True, df, ""

        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, pd.DataFrame(), error_msg

    def _convert_data_types(self, df: pd.DataFrame, table_schema: Dict):
        """Convert DataFrame columns to appropriate data types"""
        for col, schema_info in table_schema.items():
            if col not in df.columns:
                continue

            try:
                if schema_info["type"] in ["integer", "bigint", "smallint"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                elif schema_info["type"] in [
                    "numeric",
                    "decimal",
                    "real",
                    "double precision",
                ]:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                elif schema_info["type"] == "boolean":
                    df[col] = df[col].astype(bool)
                elif (
                    "timestamp" in schema_info["type"] or "date" in schema_info["type"]
                ):
                    df[col] = pd.to_datetime(df[col], errors="coerce")

            except Exception as e:
                self.logger.warning(
                    f"Could not convert column {col} to {schema_info['type']}: {e}"
                )


class BulkUploadEngine:
    """Handles bulk upload operations"""

    def __init__(self, db_manager: DatabaseConnectionManager, config: BulkUploadConfig):
        self.db_manager = db_manager
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Foreign key constraint ordering from existing patterns
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
                # Prepare data tuples and escape any % characters to avoid psycopg2 conflicts
                data_tuples = []
                for _, row in df.iterrows():
                    row_data = []
                    for col in columns:
                        value = row[col]
                        # Handle pandas NaT and NaN values
                        if pd.isna(value):
                            row_data.append(None)
                        else:
                            # Escape % characters in string values to prevent psycopg2 placeholder conflicts
                            if isinstance(value, str) and '%' in value:
                                # Double the % to escape it for psycopg2
                                value = value.replace('%', '%%')
                            row_data.append(value)
                    data_tuples.append(tuple(row_data))

                # Build bulk insert query using psycopg2.sql for safety
                columns_identifiers = [psycopg2.sql.Identifier(col) for col in columns]
                columns_list = psycopg2.sql.SQL(", ").join(columns_identifiers)
                
                # Create placeholder list without using %s strings
                placeholders_list = psycopg2.sql.SQL(",").join(
                    [psycopg2.sql.Placeholder()] * len(columns)
                )

                if self.config.conflict_resolution == "ignore":
                    query = psycopg2.sql.SQL("""
                        INSERT INTO {} ({})
                        VALUES ({})
                        ON CONFLICT DO NOTHING
                    """).format(
                        psycopg2.sql.Identifier(table_name),
                        columns_list,
                        placeholders_list
                    )
                else:
                    query = psycopg2.sql.SQL("""
                        INSERT INTO {} ({})
                        VALUES ({})
                    """).format(
                        psycopg2.sql.Identifier(table_name),
                        columns_list,
                        placeholders_list
                    )

                # Debug: Log the query and first few data points
                self.logger.info(f"Query: {query.as_string(conn)}")
                self.logger.info(f"Sample data: {data_tuples[:2] if data_tuples else 'No data'}")

                # Execute bulk insert with progress tracking
                batch_size = self.config.batch_size
                total_batches = (len(data_tuples) + batch_size - 1) // batch_size
                uploaded_count = 0

                with conn.cursor() as cur:
                    for i in range(0, len(data_tuples), batch_size):
                        batch = data_tuples[i : i + batch_size]
                        current_batch = (i // batch_size) + 1

                        try:
                            # Convert psycopg2.sql.SQL object to string for execute_values
                            query_string = query.as_string(conn)
                            
                            # Debug: Try simple executemany instead of execute_values
                            self.logger.info("Trying executemany approach...")
                            
                            # Create simple insert query for executemany
                            placeholders = ",".join(["%s"] * len(columns))
                            simple_query = f"""
                                INSERT INTO {table_name} ({",".join(columns)}) 
                                VALUES ({placeholders})
                                ON CONFLICT DO NOTHING
                            """
                            
                            cur.executemany(simple_query, batch)
                            uploaded_count += len(batch)

                            # Log progress
                            self.logger.info(
                                f"Uploaded batch {current_batch}/{total_batches} "
                                f"({uploaded_count}/{len(data_tuples)} records)"
                            )

                        except Exception as e:
                            self.logger.error(f"Error in batch {current_batch}: {e}")
                            if self.config.conflict_resolution == "error":
                                raise
                            # Continue with next batch if using lenient error handling
                            continue

                job.records_uploaded = uploaded_count
                conn.commit()

                self.logger.info(
                    f"Successfully uploaded {uploaded_count} records to {table_name}"
                )
                return True, f"Uploaded {uploaded_count} records"

        except Exception as e:
            error_msg = f"Upload failed for {table_name}: {str(e)}"
            self.logger.error(error_msg)
            try:
                conn.rollback()
            except:
                pass
            return False, error_msg


class BulkUploader:
    """Main bulk uploader orchestrator"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self._setup_logging()

        # Initialize components
        self.db_manager = DatabaseConnectionManager()
        self.discovery_engine = DataDiscoveryEngine(self.config)
        self.validation_engine = ValidationEngine(self.db_manager, self.config)
        self.processing_engine = BulkProcessingEngine(
            self.validation_engine, self.config
        )
        self.upload_engine = BulkUploadEngine(self.db_manager, self.config)

        # Job tracking
        self.jobs: Dict[str, UploadJob] = {}

        self.logger = logging.getLogger(__name__)

    def _load_config(self, config_path: Optional[Path]) -> BulkUploadConfig:
        """Load configuration from file or use defaults"""
        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    config_data = yaml.safe_load(f)
                return BulkUploadConfig(**config_data)
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
        self, root_path: Path, recursive: bool = True, exclude_dirs: List[str] = None
    ) -> List[str]:
        """Discover files and queue them for processing"""
        self.logger.info(f"Discovering files in {root_path}")

        if exclude_dirs is None:
            exclude_dirs = []

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

            self.logger.info(f"Queued {file_path.name} → {table_name} (Job: {job_id})")

        return job_ids

    def process_job(self, job_id: str) -> bool:
        """Process a single upload job"""
        if job_id not in self.jobs:
            self.logger.error(f"Job {job_id} not found")
            return False

        job = self.jobs[job_id]
        job.status = "processing"
        job.start_time = datetime.now()

        try:
            self.logger.info(
                f"Processing job {job_id}: {job.file_path.name} → {job.table_name}"
            )

            # Step 1: Validate file structure
            self.logger.info("Step 1: Validating file structure...")
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

            # Step 2: Process file
            self.logger.info("Step 2: Processing file data...")
            success, df, error_msg = self.processing_engine.process_file(
                job.file_path, job.table_name, validation_results
            )

            if not success:
                job.status = "failed"
                job.error_message = error_msg
                return False

            job.records_total = len(df)

            # Step 3: Upload to database
            self.logger.info("Step 3: Uploading to database...")
            upload_success, upload_msg = self.upload_engine.upload_dataframe(
                df, job.table_name, job
            )

            if upload_success:
                job.status = "completed"
                job.end_time = datetime.now()
                self.logger.info(f"Job {job_id} completed successfully: {upload_msg}")
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
        """Process all queued jobs"""
        if not self.jobs:
            return {"message": "No jobs to process"}

        # Sort jobs by upload order to respect foreign key constraints
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

        self.logger.info(f"Processing {len(self.jobs)} jobs with {workers} workers")

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
                # Move to next order level
                current_order += 1
                if current_order > 10:  # Safety break
                    break
                continue

            # Process current batch in parallel
            if len(current_batch) == 1:
                # Single job, process directly
                job_id, job = current_batch[0]
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
            else:
                # Multiple jobs, process in parallel
                with ThreadPoolExecutor(
                    max_workers=min(workers, len(current_batch))
                ) as executor:
                    future_to_job = {
                        executor.submit(self.process_job, job_id): (job_id, job)
                        for job_id, job in current_batch
                    }

                    for future in as_completed(future_to_job):
                        job_id, job = future_to_job[future]
                        try:
                            success = future.result()
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
                        except Exception as e:
                            self.logger.error(
                                f"Job {job_id} failed with exception: {e}"
                            )
                            results["failed"] += 1
                            results["job_results"][job_id] = {
                                "success": False,
                                "table": job.table_name,
                                "records": 0,
                                "error": str(e),
                            }

            sorted_jobs = remaining_jobs
            current_order += 1

        # Generate summary
        success_rate = (
            (results["successful"] / results["total_jobs"] * 100)
            if results["total_jobs"] > 0
            else 0
        )
        self.logger.info(
            f"Bulk upload completed: {results['successful']}/{results['total_jobs']} "
            f"jobs successful ({success_rate:.1f}%)"
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
        return [self.get_job_status(job_id) for job_id in self.jobs.keys()]


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Bulk Uploader for Horse Racing Data")
    parser.add_argument("path", type=Path, help="Path to data directory")
    parser.add_argument("--config", type=Path, help="Path to configuration file")
    parser.add_argument("--recursive", action="store_true", help="Search recursively")
    parser.add_argument("--workers", type=int, help="Number of worker threads")
    parser.add_argument(
        "--test-connection", action="store_true", help="Test database connection only"
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
        # Discover and queue files
        print(f"🔍 Discovering files in {args.path}")
        job_ids = uploader.discover_and_queue_files(args.path, args.recursive)

        if not job_ids:
            print("❌ No files found to process")
            return 1

        print(f"📋 Queued {len(job_ids)} files for processing")

        # Process all jobs
        print("🚀 Starting bulk upload process...")
        results = uploader.process_all_jobs(args.workers)

        # Display results
        print("\n📊 BULK UPLOAD RESULTS:")
        print(f"   Total jobs: {results['total_jobs']}")
        print(f"   Successful: {results['successful']}")
        print(f"   Failed: {results['failed']}")
        print(
            f"   Success rate: {(results['successful']/results['total_jobs']*100):.1f}%"
        )

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
