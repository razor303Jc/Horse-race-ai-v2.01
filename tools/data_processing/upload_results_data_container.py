#!/usr/bin/env python3
"""
🔧 PIPELINE DAILY UPLOAD SYSTEM FIX
===================================

Fixed pipeline daily upload system based on successful bulk uploader methodology.
This addresses all the critical issues identified in CRITICAL_PIPELINE_FINDINGS_REPORT.md:

FIXED ISSUES:
✅ Column mapping mismatches (horses "id" issue)
✅ Case sensitivity problems (UptoDate vs uptodate)
✅ Data cleaning for "-" strings in integer fields
✅ Multi-database support (cards + results)
✅ Comprehensive data validation

ARCHITECTURE:
- Uses proven bulk uploader column mapping approach
- Enhanced data cleaning pipeline
- Multi-database architecture support
- Container-compatible configuration
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Container-compatible database configurations
CARDS_DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("CARDS_DB_NAME", "cards_horse_racing_db"),
    "user": os.getenv("DB_USER", "horse_racing"),
    "password": os.getenv("DB_PASSWORD", "secure_password_123"),
}

RESULTS_DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("RESULTS_DB_NAME", "results_horse_racing_db"),
    "user": os.getenv("DB_USER", "horse_racing"),
    "password": os.getenv("DB_PASSWORD", "secure_password_123"),
}

# Column mappings based on successful bulk uploader system
CSV_COLUMN_MAPPINGS = {
    "horses": {
        "database": "cards",
        "csv_to_db": {
            "horse_name": "horse_name",
            "age": "age",
            "weight": "weight",
            "jockey": "jockey",
            "trainer": "trainer",
            "odds": "odds",
            "form": "form",
            "wearing": "wearing",
            "horse_rating": "horse_rating",
            "trainer_stats": "trainer_stats",
            "jockey_stats": "jockey_stats",
            "recent_form": "recent_form",
            "days_since_last_run": "days_since_last_run",
            "course_and_distance_wins": "course_and_distance_wins",
            "course_and_distance_runs": "course_and_distance_runs",
            "course_wins": "course_wins",
            "course_runs": "course_runs",
            "distance_wins": "distance_wins",
            "distance_runs": "distance_runs",
            "race_id": "race_id",
        },
    },
    "races": {
        "database": "cards",
        "csv_to_db": {
            "race_time": "race_time",
            "race_name": "race_name",
            "distance": "distance",
            "going": "going",
            "race_class": "race_class",
            "surface": "surface",
            "total_prize": "total_prize",
            "age_band": "age_band",
            "field_size": "field_size",
            "favorite_odds": "favorite_odds",
            "race_id": "race_id",
        },
    },
    "racecard_details": {
        "database": "cards",
        "csv_to_db": {
            "horse_name": "horse_name",
            "saddle_cloth": "saddle_cloth",
            "draw": "draw",
            "horse_age": "horse_age",
            "horse_weight": "horse_weight",
            "jockey_name": "jockey_name",
            "trainer_name": "trainer_name",
            "horse_price": "horse_price",
            "place_price": "place_price",
            "jockey_claim": "jockey_claim",
            "wearing": "wearing",
            "form_figures": "form_figures",
            "days_since_last_run": "days_since_last_run",
            "official_rating": "official_rating",
            "jockey_record": "jockey_record",
            "trainer_record": "trainer_record",
            "race_id": "race_id",
        },
    },
    "results_horses": {
        "database": "results",
        "csv_to_db": {
            "id": "horse_id",  # FIX: Map CSV "id" to database "horse_id"
            "horse_name": "horse_name",
            "age": "age",
            "weight": "weight",
            "jockey": "jockey",
            "trainer": "trainer",
            "odds": "odds",
            "form": "form",
            "wearing": "wearing",
            "horse_rating": "horse_rating",
            "trainer_stats": "trainer_stats",
            "jockey_stats": "jockey_stats",
            "recent_form": "recent_form",
            "days_since_last_run": "days_since_last_run",
            "course_and_distance_wins": "course_and_distance_wins",
            "course_and_distance_runs": "course_and_distance_runs",
            "course_wins": "course_wins",
            "course_runs": "course_runs",
            "distance_wins": "distance_wins",
            "distance_runs": "distance_runs",
            "race_id": "race_id",
        },
    },
    "results_races": {
        "database": "results",
        "csv_to_db": {
            "race_time": "race_time",
            "race_name": "race_name",
            "distance": "distance",
            "going": "going",
            "race_class": "race_class",
            "surface": "surface",
            "total_prize": "total_prize",
            "age_band": "age_band",
            "field_size": "field_size",
            "favorite_odds": "favorite_odds",
            "race_id": "race_id",
        },
    },
    "records": {
        "database": "results",
        "csv_to_db": {
            "horse_name": "horse_name",
            "finish_position": "finish_position",
            "starting_price": "starting_price",
            "jockey": "jockey",
            "trainer": "trainer",
            "age": "age",
            "weight": "weight",
            "equipment": "equipment",
            "comment": "comment",
            "race_id": "race_id",
        },
    },
    "jockeys_stats": {
        "database": "results",
        "csv_to_db": {
            "jockey_name": "jockey_name",
            "rides": "rides",
            "wins": "wins",
            "places": "places",
            "win_percentage": "win_percentage",
            "place_percentage": "place_percentage",
            "stake": "stake",
            "profit_loss": "profit_loss",
            "roi": "roi",
            "uptodate": "uptodate",  # FIX: Handle case sensitivity CSV "UptoDate" -> DB "uptodate"
            "a_e": "a_e",
            "iv": "iv",
            "pts": "pts",
        },
    },
    "trainers_stats": {
        "database": "results",
        "csv_to_db": {
            "trainer_name": "trainer_name",
            "runners": "runners",
            "wins": "wins",
            "places": "places",
            "win_percentage": "win_percentage",
            "place_percentage": "place_percentage",
            "stake": "stake",
            "profit_loss": "profit_loss",
            "roi": "roi",
            "uptodate": "uptodate",  # FIX: Handle case sensitivity CSV "UptoDate" -> DB "uptodate"
            "a_e": "a_e",
            "iv": "iv",
            "pts": "pts",
        },
    },
}


class DataCleaner:
    """Enhanced data cleaning based on bulk uploader success"""

    @staticmethod
    def clean_percentage_fields(df: pd.DataFrame, col: str) -> pd.DataFrame:
        """Clean percentage fields - remove % symbol and convert to float"""
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("%", "").replace("", None)
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    @staticmethod
    def clean_numeric_fields(df: pd.DataFrame, col: str) -> pd.DataFrame:
        """Clean numeric fields - convert '-' strings to NULL"""
        if col in df.columns:
            # First replace problematic strings with None
            df[col] = df[col].replace("-", None)
            df[col] = df[col].replace("", None)
            df[col] = df[col].replace("None", None)
            # Then convert to numeric, coercing errors to NaN
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    @staticmethod
    def clean_race_results_fields(df: pd.DataFrame) -> pd.DataFrame:
        """Clean race results specific fields"""
        # Handle finish_position field which may contain non-numeric values
        if "finish_position" in df.columns:
            # Convert ordinal positions like "1st", "2nd" to integers
            df["finish_position"] = df["finish_position"].astype(str)
            df["finish_position"] = df["finish_position"].str.replace(
                r"[^\d]", "", regex=True
            )
            df["finish_position"] = pd.to_numeric(
                df["finish_position"], errors="coerce"
            )
        return df

    @staticmethod
    def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to handle case sensitivity issues"""
        # Create mapping for case-insensitive column matching
        column_mapping = {}
        for col in df.columns:
            # Handle specific case sensitivity fixes
            if col.lower() == "uptodate":
                column_mapping[col] = "uptodate"
            else:
                column_mapping[col] = col.lower()

        df = df.rename(columns=column_mapping)
        return df


class PipelineDailyUploader:
    """Fixed pipeline daily uploader using bulk uploader methodology"""

    def __init__(self):
        self.cards_conn = None
        self.results_conn = None
        self.processed_files = []
        self.failed_files = []

    def connect_databases(self) -> bool:
        """Connect to both databases"""
        try:
            self.cards_conn = psycopg2.connect(**CARDS_DATABASE_CONFIG)
            self.results_conn = psycopg2.connect(**RESULTS_DATABASE_CONFIG)
            logger.info("✅ Connected to both databases")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    def find_pipeline_csv_files(self) -> Dict[str, Path]:
        """Find CSV files from pipeline processing"""
        data_dir = Path("/app/data/daily_downloads")
        if not data_dir.exists():
            # Fallback for local development
            data_dir = Path("data/daily_downloads")

        csv_files = {}

        # Look for mapped CSV files (processed by pipeline)
        for file_pattern in [
            "mapped_races.csv",
            "mapped_horses.csv",
            "mapped_racecard_details.csv",
            "mapped_records.csv",
            "mapped_jockeys_stats.csv",
            "mapped_trainers_stats.csv",
            "mapped_results_races.csv",
            "mapped_results_horses.csv",
        ]:
            files = list(data_dir.rglob(file_pattern))
            if files:
                # Get most recent file
                latest_file = max(files, key=lambda f: f.stat().st_mtime)
                table_name = file_pattern.replace("mapped_", "").replace(".csv", "")
                csv_files[table_name] = latest_file

        return csv_files

    def get_database_connection(self, file_type: str):
        """Get appropriate database connection for file type"""
        if file_type in CSV_COLUMN_MAPPINGS:
            db_type = CSV_COLUMN_MAPPINGS[file_type]["database"]
            if db_type == "cards":
                return self.cards_conn
            elif db_type == "results":
                return self.results_conn
        return None

    def process_csv_file(self, file_path: Path, table_name: str) -> bool:
        """Process single CSV file with enhanced data cleaning"""
        try:
            logger.info(f"🔄 Processing {file_path} -> {table_name}")

            # Get column mapping
            if table_name not in CSV_COLUMN_MAPPINGS:
                logger.error(f"❌ No column mapping for table: {table_name}")
                return False

            mapping = CSV_COLUMN_MAPPINGS[table_name]["csv_to_db"]
            conn = self.get_database_connection(table_name)

            if not conn:
                logger.error(f"❌ No database connection for table: {table_name}")
                return False

            # Read CSV
            df = pd.read_csv(file_path, low_memory=False)
            logger.info(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")

            if len(df) == 0:
                logger.warning(f"⚠️ Empty file: {file_path}")
                return True

            # Apply data cleaning
            df = DataCleaner.normalize_column_names(df)

            # Clean percentage fields
            percentage_fields = ["win_percentage", "place_percentage", "roi"]
            for field in percentage_fields:
                if field in df.columns:
                    df = DataCleaner.clean_percentage_fields(df, field)

            # Clean numeric fields that might contain "-"
            numeric_fields = [
                "finish_position",
                "starting_price",
                "age",
                "weight",
                "rides",
                "wins",
                "places",
                "runners",
            ]
            for field in numeric_fields:
                if field in df.columns:
                    df = DataCleaner.clean_numeric_fields(df, field)

            # Clean race results specific fields
            df = DataCleaner.clean_race_results_fields(df)

            # Map columns from CSV to database schema
            mapped_data = []
            db_columns = list(mapping.values())

            for _, row in df.iterrows():
                row_data = []
                for csv_col, db_col in mapping.items():
                    # Handle case sensitivity - check both exact match and lowercase
                    value = None
                    if csv_col in row.index:
                        value = row[csv_col]
                    elif csv_col.lower() in row.index:
                        value = row[csv_col.lower()]
                    elif csv_col.title() in row.index:  # Handle UptoDate -> uptodate
                        value = row[csv_col.title()]
                    elif "UptoDate" in row.index and csv_col == "uptodate":
                        value = row["UptoDate"]

                    # Convert to appropriate type
                    if pd.isna(value) or value == "" or value == "-":
                        row_data.append(None)
                    else:
                        row_data.append(value)

                mapped_data.append(tuple(row_data))

            # Insert data
            if mapped_data:
                with conn.cursor() as cur:
                    cols_str = ", ".join(db_columns)
                    placeholders = ", ".join(["%s"] * len(db_columns))

                    query = f"""
                        INSERT INTO {table_name} ({cols_str})
                        VALUES %s
                        ON CONFLICT DO NOTHING
                    """

                    execute_values(cur, query, mapped_data, page_size=1000)
                    conn.commit()

                    # Get final count
                    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                    total_count = cur.fetchone()[0]

                logger.info(
                    f"✅ {table_name}: {len(mapped_data)} rows processed, {total_count} total in database"
                )
                return True
            else:
                logger.warning(f"⚠️ No valid data to insert for {table_name}")
                return True

        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
            if conn:
                conn.rollback()
            return False

    def run_pipeline_upload(self) -> bool:
        """Run the complete pipeline upload process"""
        logger.info("🚀 PIPELINE DAILY UPLOAD SYSTEM - FIXED VERSION")
        logger.info("=" * 60)

        # Connect to databases
        if not self.connect_databases():
            return False

        # Find CSV files
        csv_files = self.find_pipeline_csv_files()
        logger.info(f"📁 Found {len(csv_files)} CSV files:")
        for table, file_path in csv_files.items():
            logger.info(f"   {table}: {file_path}")

        if not csv_files:
            logger.error("❌ No CSV files found for pipeline upload")
            return False

        # Process files in dependency order (races first, then others)
        upload_order = [
            "races",
            "results_races",
            "horses",
            "results_horses",
            "racecard_details",
            "jockeys_stats",
            "trainers_stats",
            "records",
        ]

        successful = 0
        total = len(csv_files)

        for table_name in upload_order:
            if table_name in csv_files:
                file_path = csv_files[table_name]
                if self.process_csv_file(file_path, table_name):
                    successful += 1
                    self.processed_files.append((table_name, file_path))
                else:
                    self.failed_files.append((table_name, file_path))

        # Process any remaining files not in the order
        for table_name, file_path in csv_files.items():
            if table_name not in upload_order:
                if self.process_csv_file(file_path, table_name):
                    successful += 1
                    self.processed_files.append((table_name, file_path))
                else:
                    self.failed_files.append((table_name, file_path))

        # Close connections
        if self.cards_conn:
            self.cards_conn.close()
        if self.results_conn:
            self.results_conn.close()

        # Report results
        logger.info(
            f"\n📊 PIPELINE UPLOAD SUMMARY: {successful}/{total} files processed successfully"
        )

        if successful == total:
            logger.info("🎉 All pipeline uploads completed successfully!")
            return True
        else:
            logger.error("⚠️ Some pipeline uploads failed")
            for table_name, file_path in self.failed_files:
                logger.error(f"   Failed: {table_name} ({file_path})")
            return False


def main():
    """Main execution function"""
    uploader = PipelineDailyUploader()
    success = uploader.run_pipeline_upload()

    if success:
        logger.info("🎯 PIPELINE DAILY UPLOAD SYSTEM - FIXED AND OPERATIONAL")
        sys.exit(0)
    else:
        logger.error("❌ PIPELINE DAILY UPLOAD SYSTEM - FAILURES DETECTED")
        sys.exit(1)


if __name__ == "__main__":
    main()
