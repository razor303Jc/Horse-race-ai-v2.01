#!/usr/bin/env python3
"""
Automated Data Processing Pipeline - Cards Upload Module
Implements all the fixes discovered during historical cards upload process

This module provides automated data cleaning, validation, and upload
functionality to prevent the data processing issues documented in
DATA_PROCESSING_ISSUES_CARDS_UPLOAD.md
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import logging
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CardsDataProcessor:
    """Automated data processor for race cards with comprehensive error handling"""

    def __init__(self, db_config: Dict, config_path: str = None):
        self.db_config = db_config
        self.config_path = (
            config_path or "/home/jc/Documents/Horse-race-ai-v2.04/config"
        )
        self.column_mappings = self._load_column_mappings()
        self.field_types = self._load_field_types()
        self.upload_order = [
            "races",
            "horses",
            "racecard_details",
            "jockeys_stats",
            "trainers_stats",
        ]

    def _load_column_mappings(self) -> Dict:
        """Load column mapping configuration"""
        try:
            mapping_file = Path(self.config_path) / "cards_column_mappings.json"
            if mapping_file.exists():
                with open(mapping_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load column mappings: {e}")

        # Default mappings from our experience
        return {"races": {"race_date": "date"}, "racecard_details": {}, "horses": {}}

    def _load_field_types(self) -> Dict:
        """Load field type configuration"""
        try:
            types_file = Path(self.config_path) / "cards_field_types.json"
            if types_file.exists():
                with open(types_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load field types: {e}")

        # Default field types from our experience
        return {
            "races": {
                "integer_fields": [
                    "race_id",
                    "race_number",
                    "course_id",
                    "runners_racecard",
                    "runners",
                    "draw",
                    "ew_racecard",
                    "ew",
                    "places_ew_racecard",
                    "places_ew",
                ],
                "numeric_fields": ["prize", "distance"],
                "percentage_fields": [],
                "id_fields": [],
            },
            "racecard_details": {
                "integer_fields": ["race_id", "number", "age"],
                "numeric_fields": ["odds", "weight"],
                "percentage_fields": [],
                "id_fields": ["detail_id"],
            },
            "horses": {
                "integer_fields": ["horse_id", "age"],
                "numeric_fields": [],
                "percentage_fields": [],
                "id_fields": [],
            },
        }

    def clean_integer_field(self, value: Any) -> Optional[int]:
        """Clean integer field with PostgreSQL overflow protection"""
        if pd.isna(value) or value == "" or value is None:
            return None
        try:
            val = int(float(value))
            # PostgreSQL 32-bit integer limits
            if val > 2147483647 or val < -2147483648:
                logger.warning(f"Integer overflow detected: {val} -> NULL")
                return None
            return val
        except (ValueError, TypeError):
            return None

    def clean_numeric_field(self, value: Any) -> Optional[float]:
        """Clean numeric field"""
        if pd.isna(value) or value == "" or value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def clean_percentage_field(self, value: Any) -> Optional[float]:
        """Clean percentage field (handles % symbols)"""
        if pd.isna(value) or value == "":
            return None
        if isinstance(value, str) and "%" in value:
            return float(value.replace("%", ""))
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def remove_duplicate_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate columns (e.g., 'odds.1' when 'odds' exists)"""
        original_cols = list(df.columns)
        duplicate_patterns = [".1", ".2", ".3"]  # Common pandas duplicate suffixes

        cols_to_drop = []
        for col in df.columns:
            for pattern in duplicate_patterns:
                if col.endswith(pattern):
                    base_col = col.replace(pattern, "")
                    if base_col in df.columns:
                        cols_to_drop.append(col)
                        logger.info(
                            f"Removing duplicate column: {col} (keeping {base_col})"
                        )

        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)

        return df

    def apply_column_mappings(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Apply column name mappings for a specific table"""
        if table_name in self.column_mappings:
            mappings = self.column_mappings[table_name]
            for old_col, new_col in mappings.items():
                if old_col in df.columns and new_col not in df.columns:
                    df = df.rename(columns={old_col: new_col})
                    logger.info(f"Column mapping applied: {old_col} -> {new_col}")
        return df

    def clean_data_types(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Apply data type cleaning based on field type configuration"""
        if table_name not in self.field_types:
            return df

        field_config = self.field_types[table_name]

        # Clean integer fields
        for field in field_config.get("integer_fields", []):
            if field in df.columns:
                original_nulls = df[field].isna().sum()
                df[field] = df[field].apply(self.clean_integer_field)
                new_nulls = df[field].isna().sum()
                if new_nulls > original_nulls:
                    logger.warning(
                        f"Cleaned {new_nulls - original_nulls} invalid integers in {field}"
                    )

        # Clean numeric fields
        for field in field_config.get("numeric_fields", []):
            if field in df.columns:
                df[field] = df[field].apply(self.clean_numeric_field)

        # Clean percentage fields
        for field in field_config.get("percentage_fields", []):
            if field in df.columns:
                df[field] = df[field].apply(self.clean_percentage_field)

        return df

    def generate_id_fields(
        self, df: pd.DataFrame, table_name: str, db_cursor
    ) -> pd.DataFrame:
        """Generate required ID fields that are not auto-increment"""
        if table_name not in self.field_types:
            return df

        id_fields = self.field_types[table_name].get("id_fields", [])

        for field in id_fields:
            if field not in df.columns:
                if field == "detail_id" and table_name == "racecard_details":
                    # Get current max detail_id from database
                    try:
                        db_cursor.execute(
                            "SELECT COALESCE(MAX(detail_id), 0) FROM racecard_details"
                        )
                        max_id = db_cursor.fetchone()[0]
                        df[field] = range(max_id + 1, max_id + 1 + len(df))
                        logger.info(
                            f"Generated {len(df)} sequential IDs for {field} starting from {max_id + 1}"
                        )
                    except Exception as e:
                        logger.error(f"Could not generate IDs for {field}: {e}")
                        # Fallback to simple sequential numbering
                        df[field] = range(1, len(df) + 1)

        return df

    def validate_foreign_keys(
        self, df: pd.DataFrame, table_name: str, db_cursor
    ) -> pd.DataFrame:
        """Validate and filter foreign key relationships"""
        if table_name == "racecard_details" and "race_id" in df.columns:
            # Get valid race_ids from races table
            db_cursor.execute(
                "SELECT DISTINCT race_id FROM races WHERE race_id IS NOT NULL"
            )
            valid_race_ids = set(row[0] for row in db_cursor.fetchall())

            if valid_race_ids:
                before_count = len(df)
                df = df[df["race_id"].isin(valid_race_ids)].copy()
                after_count = len(df)

                if before_count != after_count:
                    logger.warning(
                        f"Filtered out {before_count - after_count} rows with invalid race_ids"
                    )
            else:
                logger.error("No valid race_ids found in races table!")
                return pd.DataFrame()  # Return empty DataFrame

        return df

    def auto_clean_dataframe(
        self, df: pd.DataFrame, table_name: str, db_cursor=None
    ) -> pd.DataFrame:
        """Apply comprehensive data cleaning pipeline"""
        logger.info(f"Starting auto-clean for {table_name}: {len(df)} rows")

        # 1. Remove duplicate columns
        df = self.remove_duplicate_columns(df)

        # 2. Apply column mappings
        df = self.apply_column_mappings(df, table_name)

        # 3. Clean data types
        df = self.clean_data_types(df, table_name)

        # 4. Generate ID fields (requires database connection)
        if db_cursor:
            df = self.generate_id_fields(df, table_name, db_cursor)

        # 5. Validate foreign keys (requires database connection)
        if db_cursor:
            df = self.validate_foreign_keys(df, table_name, db_cursor)

        # 6. Handle NaN values
        df = df.where(pd.notnull(df), None)

        logger.info(f"Auto-clean complete for {table_name}: {len(df)} rows remaining")
        return df

    def get_table_columns(self, table_name: str, db_cursor) -> List[str]:
        """Get column names for a database table"""
        db_cursor.execute(
            f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            AND column_name != 'created_at'
            ORDER BY ordinal_position
        """
        )
        return [row[0] for row in db_cursor.fetchall()]

    def upload_table_data(
        self, df: pd.DataFrame, table_name: str, db_cursor, db_connection
    ) -> int:
        """Upload data to database table with proper error handling"""
        if len(df) == 0:
            logger.warning(f"No data to upload for {table_name}")
            return 0

        try:
            # Get database columns
            db_columns = self.get_table_columns(table_name, db_cursor)

            # Find matching columns
            csv_columns = list(df.columns)
            matched_columns = [col for col in csv_columns if col in db_columns]

            if not matched_columns:
                logger.error(f"No matching columns found for {table_name}")
                return 0

            logger.info(
                f"Uploading {len(matched_columns)} columns to {table_name}: {matched_columns}"
            )

            # Use only matched columns
            df_upload = df[matched_columns].copy()

            # Prepare data for insertion
            data = [tuple(row) for row in df_upload.values]
            cols = ",".join(matched_columns)

            # Determine conflict resolution strategy
            conflict_clauses = {
                "races": "ON CONFLICT (race_id) DO NOTHING",
                "horses": "ON CONFLICT (horse_id) DO NOTHING",
                "racecard_details": "ON CONFLICT DO NOTHING",
                "jockeys_stats": "ON CONFLICT DO NOTHING",
                "trainers_stats": "ON CONFLICT DO NOTHING",
            }

            conflict_clause = conflict_clauses.get(table_name, "ON CONFLICT DO NOTHING")
            query = f"INSERT INTO {table_name} ({cols}) VALUES %s {conflict_clause}"

            # Execute upload in batches
            execute_values(db_cursor, query, data, page_size=100)
            inserted_count = db_cursor.rowcount

            db_connection.commit()
            logger.info(
                f"Successfully uploaded {inserted_count} records to {table_name}"
            )
            return inserted_count

        except Exception as e:
            logger.error(f"Error uploading to {table_name}: {e}")
            db_connection.rollback()
            return 0

    def process_and_upload_all(self, csv_files: Dict[str, Path]) -> Dict[str, Any]:
        """Process and upload all CSV files with comprehensive error handling"""
        results = {"successful": [], "failed": [], "warnings": [], "statistics": {}}

        # Connect to database
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            results["failed"].append(("database_connection", str(e)))
            return results

        try:
            # Process tables in correct order (respecting foreign keys)
            for table_name in self.upload_order:
                if table_name in csv_files:
                    csv_file = csv_files[table_name]

                    try:
                        # Load CSV
                        df = pd.read_csv(csv_file)
                        logger.info(
                            f"Processing {table_name} from {csv_file.name}: {len(df)} rows"
                        )

                        # Auto-clean data
                        df_clean = self.auto_clean_dataframe(df, table_name, cursor)

                        if len(df_clean) == 0:
                            results["warnings"].append(
                                f"{table_name}: No valid data after cleaning"
                            )
                            continue

                        # Upload to database
                        uploaded_count = self.upload_table_data(
                            df_clean, table_name, cursor, conn
                        )

                        if uploaded_count > 0:
                            results["successful"].append((table_name, uploaded_count))
                            results["statistics"][table_name] = {
                                "original_rows": len(df),
                                "cleaned_rows": len(df_clean),
                                "uploaded_rows": uploaded_count,
                            }
                        else:
                            results["failed"].append(
                                (table_name, "Upload returned 0 rows")
                            )

                    except Exception as e:
                        logger.error(f"Error processing {table_name}: {e}")
                        results["failed"].append((table_name, str(e)))
                        conn.rollback()

        finally:
            cursor.close()
            conn.close()

        return results


# Example usage
def main():
    """Example usage of the CardsDataProcessor"""

    # Database configuration
    db_config = {
        "host": "postgres",
        "port": 5432,
        "database": "cards_horse_racing_db",
        "user": "horse_racing",
        "password": "secure_password_123",
    }

    # Initialize processor
    processor = CardsDataProcessor(db_config)

    # Define CSV files to process
    csv_files = {
        "races": Path("/tmp/historical_cards_upload/races_20250822.csv"),
        "racecard_details": Path(
            "/tmp/historical_cards_upload/racecard_details_20250822.csv"
        ),
        "horses": Path("/tmp/historical_cards_upload/horses_20250822.csv"),
    }

    # Process and upload
    results = processor.process_and_upload_all(csv_files)

    # Report results
    print("\n📊 Upload Results:")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"Warnings: {results['warnings']}")
    print(f"Statistics: {results['statistics']}")


if __name__ == "__main__":
    main()
