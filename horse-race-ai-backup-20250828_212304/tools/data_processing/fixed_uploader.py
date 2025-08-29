#!/usr/bin/env python3
"""
Fixed CSV Uploader - With Correct Database Schema Mapping
"""

from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Database configuration
DATABASE_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "database": "horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}


def find_latest_csv_files():
    """Find the most recent CSV files from daily downloads"""
    downloads_dir = Path("data/daily_downloads")
    csv_files = {}

    # Look for records.csv (race results)
    records_files = list(downloads_dir.rglob("records/records.csv"))
    if records_files:
        csv_files["records"] = str(max(records_files, key=lambda f: f.stat().st_mtime))

    # Look for races.csv (race cards) in cards_data
    races_files = list(downloads_dir.glob("cards_data/races/races.csv"))
    if races_files:
        csv_files["races"] = str(max(races_files, key=lambda f: f.stat().st_mtime))

    return csv_files


def create_correct_column_mapping(csv_columns, table_name):
    """Create mapping based on actual database schema"""

    mappings = {
        "records": {
            # CSV column -> Database column (based on actual schema)
            "Race_ID": "race_id",
            "Horse_number": "horse_number",
            "Place": "position",  # Changed from finished_position
            "Draw": "draw",
            "Horse_ID": "horse_id",
            "Country": "country",
            "Name": "horse",  # Changed from horse_name
            "Age": "age",  # Changed from horse_age
            "weight_uk": "weight_uk",  # Correct column name
            "OR": "or_rating",
            "Jockey_ID": "jockey_id",
            "Jockey": "jockey",
            "Trainer_ID": "trainer_id",
            "Trainer": "trainer",
            "Fav": "fav",
            "SP": "sp",
        },
        "races": {
            # CSV column -> Database column (based on actual schema)
            "Race_ID": "race_id",
            "race_number": "race_number",
            "race_time": "race_time",
            "course_id": "course_id",
            "Course": "course",
            "Race_type": "race_type",
            "Date": "date",
            "Race_name": "race_name",
            "Class": "class",  # Changed from class_level
            "Years": "years",
            "Distance": "distance",
            "Surface": "surface",
            "Prize": "prize",
            "Runners_racecard": "runners_racecard",
            "Runners": "runners",
        },
    }

    # Get mapping for this table
    table_mapping = mappings.get(table_name, {})

    # Build final mapping for available columns
    final_mapping = {}
    for csv_col in csv_columns:
        if csv_col in table_mapping:
            final_mapping[csv_col] = table_mapping[csv_col]

    return final_mapping


def clear_table(table_name, conn):
    """Clear existing data from table"""
    try:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {table_name}")
            conn.commit()
            print(f"   🧹 Cleared table {table_name}")
            return True
    except Exception as e:
        print(f"   ❌ Error clearing {table_name}: {e}")
        return False


def process_csv_to_table(csv_path, table_name, conn):
    """Process CSV file and upload to database table"""
    try:
        print(f"📊 Processing {csv_path} -> {table_name}")

        # Read CSV
        df = pd.read_csv(csv_path)
        print(f"   Original: {len(df)} rows, {len(df.columns)} columns")

        # Get available columns
        csv_columns = df.columns.tolist()
        print(f"   Available CSV columns: {csv_columns[:10]}...")  # Show first 10

        # Create column mapping
        column_mapping = create_correct_column_mapping(csv_columns, table_name)
        print(f"   Column mappings: {column_mapping}")

        if not column_mapping:
            print(f"   ⚠️ No matching columns found for {table_name}")
            return 0

        # Select and rename columns
        df_mapped = df[list(column_mapping.keys())].rename(columns=column_mapping)

        # Convert data types and handle nulls
        for col in df_mapped.columns:
            if col in ["race_id", "horse_id", "jockey_id", "trainer_id"]:
                df_mapped[col] = df_mapped[col].astype(str).fillna("none")
            elif col in [
                "horse_number",
                "position",
                "draw",
                "age",
                "or_rating",
                "fav",
                "race_number",
                "course_id",
                "runners_racecard",
                "runners",
            ]:
                df_mapped[col] = (
                    pd.to_numeric(df_mapped[col], errors="coerce").fillna(0).astype(int)
                )
            elif col in ["weight_uk", "sp"]:
                df_mapped[col] = pd.to_numeric(df_mapped[col], errors="coerce").fillna(
                    0.0
                )
            else:
                df_mapped[col] = df_mapped[col].astype(str).fillna("none")

        # Handle date formatting if present
        if "date" in df_mapped.columns:
            # Convert date format
            df_mapped["date"] = pd.to_datetime(
                df_mapped["date"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")
            print(f"   📅 Sample dates: {df_mapped['date'].dropna().head(3).tolist()}")

        # Insert data
        records = df_mapped.to_dict("records")

        if records:
            columns = list(df_mapped.columns)

            with conn.cursor() as cur:
                insert_query = f"""
                INSERT INTO {table_name} ({','.join(columns)})
                VALUES %s
                """

                execute_values(
                    cur,
                    insert_query,
                    [tuple(record.values()) for record in records],
                    template=None,
                    page_size=100,
                )
                conn.commit()

                print(f"   ✅ Uploaded {len(records)} records to {table_name}")
                return len(records)
        else:
            print(f"   ⚠️ No valid records to upload")
            return 0

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 0


def main():
    print("🎯 Fixed CSV Uploader - With Correct Schema Mapping")
    print("=" * 60)

    # Find CSV files
    csv_files = find_latest_csv_files()

    if not csv_files:
        print("❌ No CSV files found")
        return

    print(f"📁 Found {len(csv_files)} CSV files:")
    for table, path in csv_files.items():
        print(f"   {table}: {path}")

    # Connect to database
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        print("\n✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    try:
        # Clear existing data
        print("\n🧹 Clearing existing data...")
        for table in csv_files.keys():
            clear_table(table, conn)

        # Process each CSV file
        total_uploaded = 0
        for table, csv_path in csv_files.items():
            print(f"\n🔄 Processing {table}...")
            uploaded = process_csv_to_table(csv_path, table, conn)
            total_uploaded += uploaded

        # Final status
        print(f"\n📊 Final Database Status:")
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM races")
            race_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM records")
            record_count = cur.fetchone()[0]

            print(f"   📋 Races: {race_count}")
            print(f"   🐎 Records: {record_count}")
            print(f"   📤 Total uploaded: {total_uploaded}")

        print("\n✅ Upload completed successfully!")

    except Exception as e:
        print(f"❌ Upload failed: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
