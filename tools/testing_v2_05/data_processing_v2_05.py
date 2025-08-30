#!/usr/bin/env python3
"""
Data Processing System v2.05 - Horse Racing AI Testing & Simulation Strategy
Enhanced data processing pipeline for PostgreSQL entity tables with
performance optimization and comprehensive error handling

Features:
- CSV data extraction and processing
- PostgreSQL entity table population
- Batch processing with performance monitoring
- Error recovery and data integrity validation
- Memory-efficient processing for large datasets
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import json
import zipfile
import time
from contextlib import contextmanager

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingStats:
    """Statistics for data processing operations"""

    start_time: datetime
    end_time: Optional[datetime] = None
    total_records: int = 0
    processed_records: int = 0
    error_records: int = 0
    processing_time_seconds: float = 0.0
    memory_peak_mb: float = 0.0

    def complete(self):
        """Mark processing as complete and calculate final stats"""
        self.end_time = datetime.now()
        self.processing_time_seconds = (self.end_time - self.start_time).total_seconds()


class DataProcessorV205:
    """Enhanced data processing system for Testing & Simulation Strategy"""

    def __init__(
        self, connection_config: Optional[Dict[str, str]] = None, batch_size: int = 1000
    ):
        """Initialize data processor"""
        self.connection_config = connection_config or self._get_default_config()
        self.batch_size = batch_size
        self.processing_stats = {}

        # Entity table mappings
        self.entity_mappings = {
            "horses": {
                "table_name": "horses_entity",
                "csv_mapping": {
                    "horse_id": "Horse_ID",
                    "horse_name": "Name",
                    "country": "Country",
                    "age": "Age",
                    "colour": "colour",
                    "sex": "sex",
                    "owner": "owner",
                    "trainer": "trainer",
                    "sire": "sire",
                    "dam": "dam",
                    "dam_sire": "dam_sire",
                },
                "required_fields": ["horse_id", "horse_name"],
            },
            "jockeys": {
                "table_name": "jockeys_entity",
                "csv_mapping": {
                    "jockey_id": "jockey_ID",
                    "jockey_name": "jockey",
                    "allowance_claimed": "allowance_claimed",
                    "total_races": "races",
                    "total_wins": "wins",
                    "win_percentage": "win_rate",
                    "total_placed": "placed",
                    "place_percentage": "place_rate",
                },
                "required_fields": ["jockey_id", "jockey_name"],
            },
            "trainers": {
                "table_name": "trainers_entity",
                "csv_mapping": {
                    "trainer_id": "trainer_ID",
                    "trainer_name": "trainer",
                    "total_runners": "runners",
                    "total_wins": "wins",
                    "win_percentage": "win_rate",
                    "total_placed": "placed",
                    "place_percentage": "place_rate",
                    "flat_runners": "flat_runners",
                    "flat_wins": "flat_wins",
                    "flat_win_rate": "flat_win_rate",
                    "jumps_runners": "jumps_runners",
                    "jumps_wins": "jumps_wins",
                    "jumps_win_rate": "jumps_win_rate",
                },
                "required_fields": ["trainer_id", "trainer_name"],
            },
        }

        logger.info("🔄 Data Processor v2.05 initialized")
        logger.info(f"📊 Batch size: {batch_size}")

    def _get_default_config(self) -> Dict[str, str]:
        """Get default PostgreSQL connection configuration"""
        return {
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": os.environ.get("DB_PORT", "5432"),
            "database": os.environ.get("DB_NAME", "results"),
            "user": os.environ.get("DB_USER", "horse_racing"),
            "password": os.environ.get("DB_PASSWORD", "secure_password_123"),
        }

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_config)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def extract_csv_from_archive(
        self, archive_path: str, extract_to: Optional[str] = None
    ) -> List[str]:
        """Extract CSV files from ZIP archive"""

        if not Path(archive_path).exists():
            raise FileNotFoundError(f"Archive not found: {archive_path}")

        extract_to = extract_to or "/tmp/csv_extraction"
        extract_dir = Path(extract_to)
        extract_dir.mkdir(parents=True, exist_ok=True)

        extracted_files = []

        try:
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

                # Find CSV files
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        if file.endswith(".csv"):
                            full_path = os.path.join(root, file)
                            extracted_files.append(full_path)

            logger.info(f"📦 Extracted {len(extracted_files)} CSV files")
            return extracted_files

        except Exception as e:
            logger.error(f"❌ Archive extraction failed: {str(e)}")
            raise

    def process_entity_csv(
        self, csv_file: str, entity_type: str, validate_data: bool = True
    ) -> ProcessingStats:
        """Process CSV file for specific entity type"""

        stats = ProcessingStats(start_time=datetime.now())

        try:
            if entity_type not in self.entity_mappings:
                raise ValueError(f"Unknown entity type: {entity_type}")

            mapping = self.entity_mappings[entity_type]

            # Read CSV with chunking for memory efficiency
            chunk_size = self.batch_size
            total_processed = 0

            logger.info(f"📊 Processing {entity_type} data from {csv_file}")

            for chunk_num, df_chunk in enumerate(
                pd.read_csv(csv_file, chunksize=chunk_size)
            ):
                logger.info(f"📦 Processing chunk {chunk_num + 1}")

                # Transform data
                transformed_data = self._transform_entity_data(
                    df_chunk, mapping, validate_data
                )

                # Insert into database
                if transformed_data:
                    inserted_count = self._insert_entity_batch(
                        transformed_data, mapping["table_name"]
                    )
                    total_processed += inserted_count
                    stats.processed_records = total_processed

                stats.total_records = total_processed

            stats.complete()
            self.processing_stats[entity_type] = stats

            logger.info(f"✅ {entity_type} processing complete")
            logger.info(f"📈 Processed {total_processed} records")

            return stats

        except Exception as e:
            logger.error(f"❌ Entity processing failed: {str(e)}")
            stats.complete()
            stats.error_records = stats.total_records - stats.processed_records
            raise

    def _transform_entity_data(
        self, df: pd.DataFrame, mapping: Dict[str, Any], validate: bool = True
    ) -> List[Dict[str, Any]]:
        """Transform CSV data to entity table format"""

        transformed_records = []
        csv_mapping = mapping["csv_mapping"]
        required_fields = mapping["required_fields"]

        for _, row in df.iterrows():
            try:
                record = {}

                # Map CSV columns to entity columns
                for entity_col, csv_col in csv_mapping.items():
                    if csv_col in df.columns:
                        value = row[csv_col]

                        # Handle null values
                        if pd.isna(value):
                            record[entity_col] = None
                        else:
                            # Convert data types
                            record[entity_col] = self._convert_value(value, entity_col)
                    else:
                        record[entity_col] = None

                # Validate required fields
                if validate:
                    missing_required = [
                        field for field in required_fields if record.get(field) is None
                    ]
                    if missing_required:
                        logger.warning(
                            f"Skipping record with missing required fields: "
                            f"{missing_required}"
                        )
                        continue

                # Add metadata
                record["created_at"] = datetime.now()
                record["updated_at"] = datetime.now()
                record["is_active"] = True

                transformed_records.append(record)

            except Exception as e:
                logger.warning(f"Record transformation error: {str(e)}")
                continue

        return transformed_records

    def _convert_value(self, value: Any, field_name: str) -> Any:
        """Convert value to appropriate type for database"""

        if pd.isna(value) or value is None:
            return None

        # Integer fields
        if field_name.endswith("_id") or field_name in [
            "age",
            "total_races",
            "total_wins",
            "total_placed",
            "flat_runners",
            "flat_wins",
            "jumps_runners",
            "jumps_wins",
        ]:
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return None

        # Percentage fields
        if "percentage" in field_name or "rate" in field_name:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None

        # Boolean fields
        if field_name == "allowance_claimed":
            if isinstance(value, str):
                return value.lower() in ["true", "1", "yes", "y"]
            return bool(value)

        # String fields
        if isinstance(value, str):
            return value.strip()[:255]  # Limit length

        return str(value)[:255]

    def _insert_entity_batch(
        self, records: List[Dict[str, Any]], table_name: str
    ) -> int:
        """Insert batch of records into entity table"""

        if not records:
            return 0

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get column names (excluding auto-increment id)
                columns = [col for col in records[0].keys() if col != "id"]

                # Prepare data tuples
                data_tuples = []
                for record in records:
                    tuple_data = tuple(record.get(col) for col in columns)
                    data_tuples.append(tuple_data)

                # Generate SQL with UPSERT
                placeholders = ", ".join(["%s"] * len(columns))
                unique_col = f"{table_name.replace('_entity', '')}_id"

                sql = f"""
                    INSERT INTO {table_name} ({', '.join(columns)})
                    VALUES ({placeholders})
                    ON CONFLICT ({unique_col}) DO UPDATE SET
                    {', '.join([
                        f"{col} = EXCLUDED.{col}" 
                        for col in columns 
                        if col not in [unique_col, 'created_at']
                    ])},
                    updated_at = CURRENT_TIMESTAMP
                """

                # Execute batch insert
                execute_values(
                    cursor,
                    sql,
                    data_tuples,
                    template=f"({placeholders})",
                    page_size=self.batch_size,
                )

                conn.commit()
                inserted_count = len(data_tuples)

                logger.info(f"📥 Inserted {inserted_count} records to {table_name}")
                return inserted_count

        except Exception as e:
            logger.error(f"❌ Batch insert failed: {str(e)}")
            raise

    def process_complete_dataset(self, data_date: str) -> Dict[str, ProcessingStats]:
        """Process complete dataset for a specific date"""

        data_path = (
            f"/home/jc/Documents/Horse-race-ai-v2.05/data/"
            f"raw_csv_archives/{data_date}"
        )

        if not Path(data_path).exists():
            raise FileNotFoundError(f"Data path not found: {data_path}")

        results = {}

        # Process cards data (horses)
        cards_zip = f"{data_path}/raw_csv_cards_{data_date}_105906.zip"
        if Path(cards_zip).exists():
            extracted_files = self.extract_csv_from_archive(
                cards_zip, f"/tmp/cards_{data_date}"
            )

            horses_file = None
            for file in extracted_files:
                if "horses" in Path(file).name.lower():
                    horses_file = file
                    break

            if horses_file:
                results["horses"] = self.process_entity_csv(horses_file, "horses")

        # Process results data (jockeys, trainers)
        results_zip = f"{data_path}/raw_csv_results_{data_date}_105906.zip"
        if Path(results_zip).exists():
            extracted_files = self.extract_csv_from_archive(
                results_zip, f"/tmp/results_{data_date}"
            )

            for entity_type in ["jockeys", "trainers"]:
                entity_file = None
                for file in extracted_files:
                    if f"{entity_type}_stats" in Path(file).name.lower():
                        entity_file = file
                        break

                if entity_file:
                    results[entity_type] = self.process_entity_csv(
                        entity_file, entity_type
                    )

        return results

    def verify_entity_data(self, entity_type: str) -> Dict[str, Any]:
        """Verify entity data integrity after processing"""

        if entity_type not in self.entity_mappings:
            raise ValueError(f"Unknown entity type: {entity_type}")

        table_name = self.entity_mappings[entity_type]["table_name"]

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)

                # Basic counts
                cursor.execute(f"SELECT COUNT(*) as total FROM {table_name}")
                total_count = cursor.fetchone()["total"]

                # Check for duplicates
                unique_col = f"{entity_type}_id"
                cursor.execute(
                    f"""
                    SELECT COUNT(*) as duplicates 
                    FROM (
                        SELECT {unique_col}, COUNT(*) 
                        FROM {table_name} 
                        GROUP BY {unique_col} 
                        HAVING COUNT(*) > 1
                    ) t
                """
                )
                duplicate_count = cursor.fetchone()["duplicates"]

                # Check null values in required fields
                cursor.execute(
                    f"""
                    SELECT COUNT(*) as null_ids 
                    FROM {table_name} 
                    WHERE {unique_col} IS NULL
                """
                )
                null_ids = cursor.fetchone()["null_ids"]

                verification_result = {
                    "entity_type": entity_type,
                    "table_name": table_name,
                    "total_records": total_count,
                    "duplicate_ids": duplicate_count,
                    "null_ids": null_ids,
                    "data_integrity": (
                        "PASS" if (duplicate_count == 0 and null_ids == 0) else "FAIL"
                    ),
                }

                logger.info(f"✅ Verification complete for {entity_type}")
                return verification_result

        except Exception as e:
            logger.error(f"❌ Verification failed: {str(e)}")
            return {"error": str(e)}

    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of all processing operations"""

        summary = {
            "total_entities_processed": len(self.processing_stats),
            "total_records_processed": sum(
                stats.processed_records for stats in self.processing_stats.values()
            ),
            "total_processing_time": sum(
                stats.processing_time_seconds
                for stats in self.processing_stats.values()
            ),
            "entity_details": {},
        }

        for entity_type, stats in self.processing_stats.items():
            summary["entity_details"][entity_type] = {
                "records_processed": stats.processed_records,
                "processing_time_seconds": stats.processing_time_seconds,
                "records_per_second": (
                    stats.processed_records / stats.processing_time_seconds
                    if stats.processing_time_seconds > 0
                    else 0
                ),
            }

        return summary


def main():
    """Main function for testing data processing functionality"""

    # Initialize data processor
    processor = DataProcessorV205(batch_size=500)

    print("🔄 Data Processing v2.05 - Testing & Simulation Strategy")
    print("=" * 60)

    # Test with 2025-08-26 dataset
    test_date = "2025-08-26"

    try:
        print(f"📊 Processing complete dataset for {test_date}...")
        results = processor.process_complete_dataset(test_date)

        print(f"\n✅ Processing completed for {len(results)} entity types")

        # Verify data integrity
        print("\n🔍 Verifying data integrity...")
        for entity_type in results.keys():
            verification = processor.verify_entity_data(entity_type)
            print(f"📋 {entity_type}: {verification}")

        # Get summary
        summary = processor.get_processing_summary()
        print(f"\n📈 Processing Summary:")
        print(f"🔢 Total records: {summary['total_records_processed']}")
        print(f"⏱️ Total time: {summary['total_processing_time']:.2f}s")

    except Exception as e:
        print(f"❌ Processing failed: {str(e)}")

    print("\n🎯 Data Processing v2.05 testing complete!")


if __name__ == "__main__":
    main()
