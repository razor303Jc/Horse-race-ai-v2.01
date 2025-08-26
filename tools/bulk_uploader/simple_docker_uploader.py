#!/usr/bin/env python3
"""
Simple Docker Container Bulk Uploader
Direct Docker network connection approach
"""

import os
import sys
import pandas as pd
import psycopg2
import psycopg2.extras
from pathlib import Path
import logging
import json


def setup_logging():
    """Setup simple logging"""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def get_docker_db_connection():
    """Get database connection using Docker network"""
    config = {
        "host": "postgres",  # Docker container alias
        "port": 5432,
        "database": "results_horse_racing_db",
        "user": "horse_racing",
        "password": "secure_password_123",
    }

    return psycopg2.connect(**config)


def test_connection():
    """Test database connection"""
    try:
        conn = get_docker_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def load_column_mappings():
    """Load column mappings from config"""
    config_file = Path("/app/config/complete_csv_column_mapping.json")

    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        return config["table_mappings"]
    except Exception as e:
        print(f"⚠️ Could not load column mappings: {e}")
        return {}


def clean_dash_symbols(df, table_name, mappings):
    """Clean dash symbols based on data type"""
    logger = logging.getLogger(__name__)
    logger.info(f"Cleaning dash symbols for {table_name}...")

    table_config = mappings.get(table_name, {})
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
        logger.info(f"Cleaned {cleaned_count} dash symbols")

    return df


def clean_percentage_fields(df, percentage_columns):
    """Convert percentage strings like '16.67%' to decimal numbers"""
    for col in percentage_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("%", "").str.replace("nan", "0")
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0) / 100
    return df


def apply_column_mapping(df, table_name, mappings):
    """Apply column mapping from CSV to database schema"""
    table_config = mappings.get(table_name, {})
    column_mapping = table_config.get("column_mapping", {})

    if column_mapping:
        # Reverse mapping (CSV column -> DB column)
        reverse_mapping = {v: k for k, v in column_mapping.items()}
        df = df.rename(columns=reverse_mapping)
        logging.getLogger(__name__).info(f"Applied column mappings for {table_name}")

    return df


def process_table_data(df, table_name, mappings):
    """Process table data with cleaning"""
    logger = logging.getLogger(__name__)
    logger.info(f"Processing {table_name} data: {len(df)} rows")

    # Step 1: Apply column mapping
    df = apply_column_mapping(df, table_name, mappings)

    # Step 2: Clean dash symbols
    df = clean_dash_symbols(df, table_name, mappings)

    # Step 3: Table-specific cleaning
    if table_name == "horses":
        # Fix percentage fields
        percentage_cols = [
            "percentage_wins",
            "percentage_placed",
            "flat_aw_rate",
            "flat_aw_placed_rate",
        ]
        df = clean_percentage_fields(df, percentage_cols)

        # Fix numeric fields
        numeric_fields = ["horse_id", "age", "total_races", "wins", "placed"]
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)

    elif table_name == "records":
        # Fix numeric fields
        numeric_fields = ["record_id", "race_id", "horse_id", "position"]
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)

        # Handle weight_uk
        if "weight_uk" in df.columns:
            df["weight_uk"] = pd.to_numeric(df["weight_uk"], errors="coerce").fillna(0)

    # Remove empty rows
    initial_rows = len(df)
    df = df.dropna(how="all")
    removed_rows = initial_rows - len(df)
    if removed_rows > 0:
        logger.info(f"Removed {removed_rows} empty rows")

    logger.info(f"Processed {table_name}: {len(df)} rows ready")
    return df


def bulk_upload_table(df, table_name):
    """Upload DataFrame to database table"""
    logger = logging.getLogger(__name__)

    try:
        conn = get_docker_db_connection()

        with conn:
            # Prepare data for bulk insert
            columns = list(df.columns)

            # Convert DataFrame to list of tuples
            data_tuples = []
            for _, row in df.iterrows():
                row_data = []
                for col in columns:
                    value = row[col]
                    if pd.isna(value):
                        row_data.append(None)
                    else:
                        row_data.append(value)
                data_tuples.append(tuple(row_data))

            # Build bulk insert query
            placeholders = ",".join(["%s"] * len(columns))
            columns_str = ",".join(columns)

            query = f"""
                INSERT INTO {table_name} ({columns_str}) 
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """

            # Execute bulk insert
            batch_size = 1000
            uploaded_count = 0

            with conn.cursor() as cur:
                for i in range(0, len(data_tuples), batch_size):
                    batch = data_tuples[i : i + batch_size]

                    psycopg2.extras.execute_values(
                        cur, query, batch, template=None, page_size=batch_size
                    )

                    uploaded_count += len(batch)

                    # Log progress
                    batch_num = (i // batch_size) + 1
                    total_batches = (len(data_tuples) + batch_size - 1) // batch_size
                    logger.info(
                        f"Batch {batch_num}/{total_batches} "
                        f"({uploaded_count}/{len(data_tuples)})"
                    )

            conn.commit()
            logger.info(f"Uploaded {uploaded_count} records to {table_name}")
            return True, uploaded_count

    except Exception as e:
        logger.error(f"Upload failed for {table_name}: {e}")
        return False, 0


def discover_and_process_files():
    """Discover and process files from processed directory"""
    logger = setup_logging()

    # Test database connection
    logger.info("Testing database connection...")
    if not test_connection():
        return False
    logger.info("✅ Database connection successful")

    # Load column mappings
    logger.info("Loading column mappings...")
    mappings = load_column_mappings()
    if not mappings:
        logger.error("❌ Could not load column mappings")
        return False
    logger.info("✅ Column mappings loaded")

    # Find processed files
    processed_dir = Path("/app/data/daily_downloads/processed")
    if not processed_dir.exists():
        logger.error(f"❌ Processed directory not found: {processed_dir}")
        return False

    # Look for CSV files (excluding non_target)
    files_found = []
    for date_dir in processed_dir.iterdir():
        if (
            date_dir.is_dir()
            and date_dir.name.startswith("2025-08-")
            and "non_target" not in str(date_dir)
        ):

            for csv_file in date_dir.glob("complete_mapped_*.csv"):
                files_found.append(csv_file)

    logger.info(f"Found {len(files_found)} CSV files to process")

    if not files_found:
        logger.error("❌ No CSV files found")
        return False

    # Process files by table type
    table_stats = {}

    for file_path in files_found:
        # Classify file
        file_name = file_path.name.lower()
        table_name = None

        if "horses" in file_name:
            table_name = "horses"
        elif "jockeys_stats" in file_name:
            table_name = "jockeys_stats"
        elif "trainers_stats" in file_name:
            table_name = "trainers_stats"
        elif "races" in file_name:
            table_name = "races"
        elif "records" in file_name:
            table_name = "records"

        if not table_name:
            logger.warning(f"⚠️ Could not classify: {file_path.name}")
            continue

        logger.info(f"📄 Processing {file_path.name} → {table_name}")

        try:
            # Load and process data
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} rows from {file_path.name}")

            # Process the data
            df = process_table_data(df, table_name, mappings)

            # Upload to database
            success, count = bulk_upload_table(df, table_name)

            if success:
                logger.info(f"✅ {file_path.name}: {count} records uploaded")
                if table_name not in table_stats:
                    table_stats[table_name] = 0
                table_stats[table_name] += count
            else:
                logger.error(f"❌ {file_path.name}: Upload failed")

        except Exception as e:
            logger.error(f"❌ Error processing {file_path.name}: {e}")
            continue

    # Summary
    logger.info("\n📊 UPLOAD SUMMARY:")
    total_records = 0
    for table, count in table_stats.items():
        logger.info(f"   {table}: {count} records")
        total_records += count

    logger.info(f"🎉 Total records uploaded: {total_records}")
    return True


def main():
    """Main function"""
    print("🚀 Simple Docker Bulk Uploader")
    print("=" * 50)

    try:
        success = discover_and_process_files()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
