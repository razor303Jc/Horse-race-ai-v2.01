#!/usr/bin/env python3
"""
Historical Cards Data Processor
Processes and uploads card data from processed directories (Aug 22-24) to cards_horse_racing_db
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import logging
from pathlib import Path
import zipfile
import json
import os
import sys
from typing import Dict, List, Tuple, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database configuration for cards database
DATABASE_CONFIG = {
    "host": "172.18.0.3",
    "port": 5432,
    "database": "cards_horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}


class HistoricalCardsProcessor:
    """Processes historical card data from processed directories"""

    def __init__(self):
        self.processed_dir = (
            Path(project_root) / "data" / "daily_downloads" / "processed"
        )
        self.target_dates = [
            "2025-08-24",
            "2025-08-23",
            "2025-08-22",
        ]  # Process in reverse order
        self.temp_extract_dir = Path(project_root) / "temp_card_processing"
        self.temp_extract_dir.mkdir(exist_ok=True)

        # Upload order for foreign key dependencies
        self.upload_order = [
            "races",
            "horses",
            "racecard_details",
            "jockeys_stats",
            "trainers_stats",
        ]

    def extract_and_process_all_dates(self):
        """Extract and process all card data from target dates"""
        logger.info("🏇 Historical Cards Data Processor")
        logger.info("Processing card data from Aug 24-22 (reverse order)")
        logger.info("=" * 50)

        all_data = {}

        for date in self.target_dates:
            logger.info(f"\n📅 Processing date: {date}")
            date_dir = self.processed_dir / date

            # Find card zip file
            card_files = list(date_dir.glob("*card*.zip"))
            if not card_files:
                logger.warning(f"No card files found for {date}")
                continue

            card_file = card_files[0]
            logger.info(f"📦 Found card file: {card_file.name}")

            # Extract and process
            date_data = self.extract_and_process_zip(card_file, date)
            if date_data:
                all_data[date] = date_data

        return all_data

    def extract_and_process_zip(self, zip_path: Path, date: str) -> Dict:
        """Extract and process a single card zip file"""
        extract_dir = self.temp_extract_dir / f"extracted_{date}"
        extract_dir.mkdir(exist_ok=True)

        try:
            # Extract zip file
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            logger.info(f"📂 Extracted to: {extract_dir}")

            # Process each CSV file
            data = {}
            for table_name in self.upload_order:
                csv_file = extract_dir / table_name / f"{table_name}.csv"
                if csv_file.exists():
                    logger.info(f"📊 Processing {table_name}.csv")
                    df = pd.read_csv(csv_file)

                    # Clean and prepare data
                    cleaned_df = self.clean_dataframe(df, table_name)
                    data[table_name] = cleaned_df
                    logger.info(f"   Loaded {len(cleaned_df)} rows")
                else:
                    logger.warning(f"   Missing {table_name}.csv")

            return data

        except Exception as e:
            logger.error(f"Error processing {zip_path}: {e}")
            return {}
        finally:
            # Cleanup
            self.cleanup_temp_dir(extract_dir)

    def clean_dataframe(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Clean and prepare dataframe for database upload"""
        if df.empty:
            return df

        # Standardize column names to lowercase
        df.columns = df.columns.str.lower()

        # Handle dash symbols and missing data
        for col in df.columns:
            if df[col].dtype == "object":
                # Replace various dash representations with None
                df[col] = df[col].replace(["-", "—", "–", "nan", "NaN", ""], None)
                df[col] = df[col].astype(str).replace("nan", None).replace("None", None)

        # Apply table-specific cleaning
        if table_name == "races":
            # Handle race_time column - convert to proper time format
            if "race_time" in df.columns:
                df["race_time"] = pd.to_datetime(
                    df["race_time"], errors="coerce"
                ).dt.time

            # Handle date column
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

            # Handle race_id specifically - use bigint
            if "race_id" in df.columns:
                df["race_id"] = (
                    pd.to_numeric(df["race_id"], errors="coerce")
                    .fillna(0)
                    .astype("Int64")
                )

            # Handle other numeric columns
            numeric_cols = [
                "race_number",
                "course_id",
                "runners",
                "runners_racecard",
                "ew",
                "ew_racecard",
                "places_ew_racecard",
                "places_ew",
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = (
                        pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
                    )

        elif table_name == "horses":
            # Handle race_id and horse_id specifically - use bigint
            big_int_cols = ["race_id", "horse_id"]
            for col in big_int_cols:
                if col in df.columns:
                    df[col] = (
                        pd.to_numeric(df[col], errors="coerce")
                        .fillna(0)
                        .astype("Int64")
                    )

            # Handle other numeric columns
            numeric_cols = ["horse_number", "age", "weight"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = (
                        pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
                    )

            # Handle SP and other float columns
            float_cols = ["sp", "finish_time"]
            for col in float_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        elif table_name == "racecard_details":
            # Handle ID columns specifically - use bigint for large IDs
            big_int_cols = ["race_id", "horse_id", "id"]
            for col in big_int_cols:
                if col in df.columns:
                    df[col] = (
                        pd.to_numeric(df[col], errors="coerce")
                        .fillna(0)
                        .astype("Int64")
                    )

            # Handle other numeric columns
            numeric_cols = [
                "draw",
                "age",
                "jockey_id",
                "trainer_id",
                "horse_rate",
                "horse_number",
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = (
                        pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
                    )

            # Handle weight and odds as float
            float_cols = ["weight", "odds_decimal"]
            for col in float_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        elif table_name in ["jockeys_stats", "trainers_stats"]:
            # Handle stats tables
            id_col = "jockey_id" if table_name == "jockeys_stats" else "trainer_id"
            if id_col in df.columns:
                df[id_col] = (
                    pd.to_numeric(df[id_col], errors="coerce").fillna(0).astype("Int64")
                )

            # Handle percentage columns
            percentage_cols = [
                col
                for col in df.columns
                if "percent" in col.lower() or "rate" in col.lower()
            ]
            for col in percentage_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        return df

    def upload_data_to_database(self, all_data: Dict):
        """Upload all processed data to the cards database"""
        logger.info("\n📤 Uploading data to cards_horse_racing_db")
        logger.info("=" * 40)

        try:
            conn = psycopg2.connect(**DATABASE_CONFIG)
            cursor = conn.cursor()

            # Track total uploads per table
            total_uploads = {table: 0 for table in self.upload_order}

            # Upload data for each date in the correct order
            for date in sorted(all_data.keys()):
                logger.info(f"\n📅 Uploading data for {date}")
                date_data = all_data[date]

                for table_name in self.upload_order:
                    if table_name in date_data:
                        df = date_data[table_name]
                        uploaded = self.upload_table_data(cursor, table_name, df, date)
                        total_uploads[table_name] += uploaded

                        # Commit after each table
                        conn.commit()

            # Final summary
            logger.info("\n🎉 Upload Summary:")
            for table, count in total_uploads.items():
                logger.info(f"   {table}: {count} rows")

            logger.info("\n✅ Historical cards data upload completed successfully!")

        except Exception as e:
            logger.error(f"Database upload error: {e}")
            if "conn" in locals():
                conn.rollback()
        finally:
            if "cursor" in locals():
                cursor.close()
            if "conn" in locals():
                conn.close()

    def upload_table_data(
        self, cursor, table_name: str, df: pd.DataFrame, date: str
    ) -> int:
        """Upload data for a specific table without duplicate checking, skip conflicts"""
        if df.empty:
            logger.info(f"   {table_name}: No data to upload")
            return 0

        try:
            logger.info(f"   {table_name}: {len(df)} rows to upload")

            # Prepare data for insertion
            columns = list(df.columns)
            data_tuples = [tuple(row) for row in df.values]

            # Create insert query with conflict resolution
            placeholders = ",".join(["%s"] * len(columns))
            columns_str = ",".join(columns)
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

            # Execute bulk insert
            cursor.executemany(query, data_tuples)

            # Get the actual number of rows inserted (affected rows)
            rows_inserted = cursor.rowcount
            logger.info(
                f"   ✅ Uploaded {rows_inserted} new rows to {table_name} (skipped {len(data_tuples) - rows_inserted} duplicates)"
            )
            return rows_inserted

        except Exception as e:
            logger.error(f"Error uploading {table_name}: {e}")
            return 0

    def cleanup_temp_dir(self, temp_dir: Path):
        """Clean up temporary extraction directory"""
        try:
            import shutil

            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"Could not clean up {temp_dir}: {e}")

    def verify_database_state(self):
        """Verify the final state of the cards database"""
        logger.info("\n📊 Verifying database state")
        logger.info("=" * 30)

        try:
            conn = psycopg2.connect(**DATABASE_CONFIG)
            cursor = conn.cursor()

            for table in self.upload_order:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"   {table}: {count} rows")

            # Check date coverage for races
            cursor.execute(
                "SELECT date, COUNT(*) FROM races GROUP BY date ORDER BY date"
            )
            results = cursor.fetchall()
            if results:
                logger.info("\n📅 Races by date:")
                for date, count in results:
                    logger.info(f"   {date}: {count} races")

        except Exception as e:
            logger.error(f"Error verifying database: {e}")
        finally:
            if "cursor" in locals():
                cursor.close()
            if "conn" in locals():
                conn.close()


def main():
    """Main execution function"""
    processor = HistoricalCardsProcessor()

    # Step 1: Extract and process all card data
    all_data = processor.extract_and_process_all_dates()

    if not all_data:
        logger.error("No card data found to process")
        return

    # Step 2: Upload to database
    processor.upload_data_to_database(all_data)

    # Step 3: Verify final state
    processor.verify_database_state()


if __name__ == "__main__":
    main()
