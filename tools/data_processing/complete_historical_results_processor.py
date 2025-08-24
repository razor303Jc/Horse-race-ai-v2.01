#!/usr/bin/env python3
"""
Complete Results Historical Data Processor
Process ALL results data from processed directory (Aug 19-23) and upload to results_horse_racing_db
"""

import os
import sys
import zipfile
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tools.data_processing.upload_results_data import upload_csv_to_results_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("data/logs/complete_results_processor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def extract_and_process_zip(zip_path, date_name):
    """Extract zip file and return processed data for all CSV files"""
    logger.info(f"📦 Processing: {zip_path}")

    all_data = {
        "races": pd.DataFrame(),
        "records": pd.DataFrame(),
        "horses": pd.DataFrame(),
        "jockeys_stats": pd.DataFrame(),
        "trainers_stats": pd.DataFrame(),
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract zip file
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # Find CSV files
        csv_files = []
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(".csv"):
                    csv_files.append(os.path.join(root, file))

        logger.info(f"📄 Found {len(csv_files)} CSV files in {date_name}")

        # Process each CSV file
        for csv_file in csv_files:
            filename = os.path.basename(csv_file).lower()

            try:
                # Identify CSV type and read data
                if "race" in filename and "card" not in filename:
                    df = pd.read_csv(csv_file)
                    df["source_date"] = date_name
                    all_data["races"] = pd.concat(
                        [all_data["races"], df], ignore_index=True
                    )
                    logger.info(f"  ✅ Added {len(df)} races from {filename}")

                elif "record" in filename or "result" in filename:
                    df = pd.read_csv(csv_file)
                    df["source_date"] = date_name
                    all_data["records"] = pd.concat(
                        [all_data["records"], df], ignore_index=True
                    )
                    logger.info(f"  ✅ Added {len(df)} records from {filename}")

                elif "horse" in filename:
                    df = pd.read_csv(csv_file)
                    df["source_date"] = date_name
                    all_data["horses"] = pd.concat(
                        [all_data["horses"], df], ignore_index=True
                    )
                    logger.info(f"  ✅ Added {len(df)} horses from {filename}")

                elif "jockey" in filename:
                    df = pd.read_csv(csv_file)
                    df["source_date"] = date_name
                    all_data["jockeys_stats"] = pd.concat(
                        [all_data["jockeys_stats"], df], ignore_index=True
                    )
                    logger.info(f"  ✅ Added {len(df)} jockey stats from {filename}")

                elif "trainer" in filename:
                    df = pd.read_csv(csv_file)
                    df["source_date"] = date_name
                    all_data["trainers_stats"] = pd.concat(
                        [all_data["trainers_stats"], df], ignore_index=True
                    )
                    logger.info(f"  ✅ Added {len(df)} trainer stats from {filename}")

                else:
                    logger.warning(f"  ⚠️ Unknown CSV type: {filename}")

            except Exception as e:
                logger.error(f"  ❌ Error processing {filename}: {e}")

    return all_data


def apply_data_cleaning(df, data_type):
    """Apply enhanced data cleaning to DataFrame"""
    if df.empty:
        return df

    logger.info(f"🧹 Cleaning {data_type} data: {len(df)} rows")

    # Enhanced dash symbol cleaning based on data types
    for col in df.columns:
        if (
            col.lower() in ["horse_rate", "draw", "place", "age"]
            and data_type == "records"
        ):
            # Numeric columns - convert dashes to 0
            df[col] = df[col].astype(str).replace("-", "0")
        elif col.lower() in ["name", "jockey", "trainer", "country"]:
            # String columns - convert dashes to None
            df[col] = df[col].astype(str).replace("-", "None")

        # Convert UK weight format
        if "weight" in col.lower():
            df[col] = (
                df[col].astype(str).str.replace(r"(\d+)-(\d+)", r"\1.\2", regex=True)
            )

    # Handle percentage fields for stats tables
    if data_type in ["jockeys_stats", "trainers_stats"]:
        for col in df.columns:
            if df[col].dtype == "object":
                # Convert percentage strings to decimals
                df[col] = df[col].astype(str).str.replace("%", "")
                df[col] = pd.to_numeric(df[col], errors="ignore")
                # Convert to decimal if it was percentage
                numeric_mask = pd.to_numeric(df[col], errors="coerce").notna()
                if numeric_mask.any():
                    df.loc[numeric_mask, col] = (
                        pd.to_numeric(df[col], errors="coerce") / 100
                    )

    logger.info(f"  ✅ Cleaned {data_type}: {len(df)} rows")
    return df


def prepare_for_database(df, table_name):
    """Prepare DataFrame for database upload with proper type conversion"""
    if df.empty:
        return df

    logger.info(f"🔧 Preparing {table_name} for database: {len(df)} rows")

    # Apply smart data type conversions based on column names
    for col in df.columns:
        col_lower = col.lower()

        if col_lower in [
            "id",
            "race_id",
            "horse_id",
            "horse_number",
            "place",
            "draw",
            "age",
            "jockey_id",
            "trainer_id",
            "horse_rate",
        ]:
            # Convert to integers, handling NaN and float strings
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

        elif (
            col_lower in ["weight", "sp", "finish_time"]
            or "distance" in col_lower
            or "time" in col_lower
            or "speed" in col_lower
        ):
            # Convert to floats, handling NaN
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        else:
            # Keep as strings, handle NaN
            df[col] = df[col].astype(str).replace("nan", None).replace("None", None)

    # Remove duplicate rows based on key columns
    if table_name == "races" and "race_id" in df.columns:
        df = df.drop_duplicates(subset=["race_id"], keep="last")
    elif table_name == "records" and all(
        col in df.columns for col in ["race_id", "horse_number"]
    ):
        df = df.drop_duplicates(subset=["race_id", "horse_number"], keep="last")
    elif table_name == "horses" and "horse_id" in df.columns:
        df = df.drop_duplicates(subset=["horse_id"], keep="last")

    logger.info(f"  ✅ Prepared {table_name}: {len(df)} rows (after deduplication)")
    return df


def process_all_historical_results():
    """Process all historical results data from all date directories"""
    logger.info("🚀 Starting Complete Historical Results Processing")
    logger.info("=" * 70)

    processed_dir = "data/daily_downloads/processed"

    if not os.path.exists(processed_dir):
        logger.error(f"❌ Processed directory not found: {processed_dir}")
        return False

    # Get all date directories, sorted
    date_dirs = []
    for item in os.listdir(processed_dir):
        item_path = os.path.join(processed_dir, item)
        if os.path.isdir(item_path) and item.startswith("2025-08-"):
            date_dirs.append((item_path, item))

    date_dirs.sort()

    if not date_dirs:
        logger.error("❌ No date directories found")
        return False

    logger.info(f"📅 Found {len(date_dirs)} date directories to process")

    # Initialize combined data containers
    combined_data = {
        "races": pd.DataFrame(),
        "records": pd.DataFrame(),
        "horses": pd.DataFrame(),
        "jockeys_stats": pd.DataFrame(),
        "trainers_stats": pd.DataFrame(),
    }

    # Process each date directory
    for date_path, date_name in date_dirs:
        logger.info(f"\n📋 Processing {date_name}")

        # Find results zip file
        results_files = [
            f
            for f in os.listdir(date_path)
            if f.startswith("results_") and f.endswith(".zip")
        ]

        if not results_files:
            logger.warning(f"⚠️ No results zip found in {date_name}")
            continue

        results_zip = os.path.join(date_path, results_files[0])

        # Extract and process data from this zip
        date_data = extract_and_process_zip(results_zip, date_name)

        # Combine with overall data
        for data_type, df in date_data.items():
            if not df.empty:
                combined_data[data_type] = pd.concat(
                    [combined_data[data_type], df], ignore_index=True
                )

    # Clean and upload combined data
    logger.info("\n" + "=" * 70)
    logger.info("🧹 CLEANING AND UPLOADING COMBINED HISTORICAL DATA")
    logger.info("=" * 70)

    upload_results = {}

    for data_type, df in combined_data.items():
        if df.empty:
            logger.warning(f"⚠️ No data found for {data_type}")
            upload_results[data_type] = {"status": "skipped", "reason": "no_data"}
            continue

        logger.info(f"\n📊 Processing {data_type}: {len(df)} total rows")

        try:
            # Apply data cleaning
            cleaned_df = apply_data_cleaning(df.copy(), data_type)

            # Prepare for database
            final_df = prepare_for_database(cleaned_df, data_type)

            # Save to temporary CSV for upload
            temp_csv = f"data/daily_downloads/complete_{data_type}.csv"
            final_df.to_csv(temp_csv, index=False)

            # Only upload tables that match database schema
            if data_type in ["races", "records"]:
                logger.info(f"📤 Uploading {data_type} to database...")
                success = upload_csv_to_results_database(temp_csv, data_type)

                if success:
                    upload_results[data_type] = {
                        "status": "success",
                        "rows": len(final_df),
                    }
                    logger.info(f"✅ Successfully uploaded {len(final_df)} {data_type}")
                else:
                    upload_results[data_type] = {
                        "status": "failed",
                        "rows": len(final_df),
                    }
                    logger.error(f"❌ Failed to upload {data_type}")
            else:
                # Save for later schema fixing
                upload_results[data_type] = {
                    "status": "saved",
                    "rows": len(final_df),
                    "file": temp_csv,
                }
                logger.info(f"💾 Saved {data_type} to {temp_csv} (schema mismatch)")

        except Exception as e:
            logger.error(f"❌ Error processing {data_type}: {e}")
            upload_results[data_type] = {"status": "error", "error": str(e)}

    # Final summary
    logger.info("\n" + "=" * 70)
    logger.info("📋 COMPLETE HISTORICAL RESULTS PROCESSING SUMMARY")
    logger.info("=" * 70)

    for data_type, result in upload_results.items():
        status = result["status"]
        if status == "success":
            logger.info(f"✅ {data_type}: {result['rows']} rows uploaded successfully")
        elif status == "saved":
            logger.info(
                f"💾 {data_type}: {result['rows']} rows saved to {result['file']}"
            )
        elif status == "failed":
            logger.error(f"❌ {data_type}: {result['rows']} rows failed to upload")
        elif status == "error":
            logger.error(f"💥 {data_type}: Processing error - {result['error']}")
        elif status == "skipped":
            logger.warning(f"⚠️ {data_type}: Skipped - {result['reason']}")

    success_count = sum(1 for r in upload_results.values() if r["status"] == "success")
    return success_count > 0


def main():
    """Main function"""
    try:
        # Ensure log directory exists
        os.makedirs("data/logs", exist_ok=True)

        logger.info("🏇 Complete Historical Results Processor")
        logger.info(
            "Processing ALL results data from Aug 19-23 (2025-08-20 to 2025-08-24)"
        )
        logger.info("Target database: results_horse_racing_db")

        success = process_all_historical_results()

        if success:
            print("\n🎉 Complete historical results processing finished!")
            return 0
        else:
            print("\n❌ Historical results processing failed!")
            return 1

    except Exception as e:
        logger.error(f"💥 Processing failed with error: {e}")
        print(f"\n💥 Processing failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
