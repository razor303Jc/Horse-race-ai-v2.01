#!/usr/bin/env python3
"""
Fixed Bulk Uploader with Proper SQL Formatting
"""

import psycopg2
import psycopg2.extras
import pandas as pd
import re
from pathlib import Path
from column_mappings import get_column_mapping, get_database_mapping, get_cleaning_rules


class DataCleaner:
    """Handles data cleaning based on pipeline patterns"""

    def __init__(self):
        self.cleaning_rules = get_cleaning_rules()

    def clean_dash_symbols(self, df, column_mappings):
        """Replace dash symbols based on data type"""
        for csv_col, db_col in column_mappings.items():
            if csv_col in df.columns:
                # Replace various dash symbols with appropriate values
                mask = df[csv_col].astype(str).str.match(r"^-+$")

                if db_col in self.cleaning_rules["percentage_fields"]:
                    df.loc[mask, csv_col] = "0%"
                elif df[csv_col].dtype in ["int64", "float64"]:
                    df.loc[mask, csv_col] = None
                else:
                    # For text fields, replace with empty string
                    df.loc[mask, csv_col] = ""

    def clean_numeric_fields(self, df, column_mappings):
        """Clean numeric fields - convert empty strings to None for integer/float columns"""
        for csv_col, db_col in column_mappings.items():
            if csv_col in df.columns:
                # Check if this should be a numeric field based on database column name
                if (
                    db_col in self.cleaning_rules.get("integer_fields", [])
                    or "rate" in db_col
                    or "id" in db_col
                ):
                    # Convert empty strings and non-numeric values to None for integer fields
                    df[csv_col] = df[csv_col].astype(str)
                    # Replace empty strings, whitespace-only strings, and non-numeric strings with None
                    mask = (
                        df[csv_col].str.strip().isin(["", "nan", "NaN", "NULL", "null"])
                    )
                    df.loc[mask, csv_col] = None

                    # Try to convert to numeric, setting errors to None
                    df[csv_col] = pd.to_numeric(df[csv_col], errors="coerce")

    def clean_race_results_fields(self, df, column_mappings):
        """Clean race results specific fields like place codes"""
        for csv_col, db_col in column_mappings.items():
            if csv_col in df.columns and db_col == "place":
                # Handle special place codes in race results
                df[csv_col] = df[csv_col].astype(str)

                # Map special race result codes to NULL (they can't be converted to integers)
                special_codes = [
                    "RR",
                    "PU",
                    "UR",
                    "F",
                    "BD",
                    "RF",
                    "SU",
                    "RO",
                    "DNF",
                    "DSQ",
                ]
                mask = df[csv_col].isin(special_codes)
                df.loc[mask, csv_col] = None

                # Convert remaining to numeric, handling errors
                df[csv_col] = pd.to_numeric(df[csv_col], errors="coerce")

    def clean_percentage_fields(self, df, column_mappings):
        """Clean percentage fields - convert from '12.34%' to 12.34"""
        for csv_col, db_col in column_mappings.items():
            if csv_col in df.columns and (
                db_col.endswith("_rate") or db_col.endswith("_percentage")
            ):
                # Convert percentage strings to numeric values
                df[csv_col] = df[csv_col].astype(str)

                # Remove % symbol and convert to float
                df[csv_col] = df[csv_col].str.replace("%", "", regex=False)
                df[csv_col] = pd.to_numeric(df[csv_col], errors="coerce")

    def clean_dataframe(self, df, csv_filename):
        """Apply all cleaning rules to dataframe"""
        column_mappings = get_column_mapping(csv_filename)

        print(f"🧹 Cleaning data for {csv_filename}")

        # Apply cleaning rules
        self.clean_dash_symbols(df, column_mappings)

        # Clean percentage fields for stats files BEFORE numeric cleaning
        if csv_filename in ["jockeys_stats.csv", "trainers_stats.csv"]:
            self.clean_percentage_fields(df, column_mappings)

        # Clean numeric fields (convert empty strings to None for integer fields)
        self.clean_numeric_fields(df, column_mappings)

        # Clean race results specific fields (place codes, etc.)
        if csv_filename == "records.csv":
            self.clean_race_results_fields(df, column_mappings)

        print("✅ Data cleaning completed")
        return df


class SimpleBulkUploader:
    """Simplified bulk uploader with proper SQL formatting"""

    def __init__(self):
        self.db_config = {
            "host": "postgres",
            "port": 5432,
            "user": "horse_racing",
            "password": "secure_password_123",
        }
        self.cleaner = DataCleaner()

    def get_connection(self, database):
        """Get database connection"""
        config = self.db_config.copy()
        config["database"] = database
        return psycopg2.connect(**config)

    def upload_dataframe(self, df, database, table):
        """Upload dataframe to database table using execute_values"""
        try:
            conn = self.get_connection(database)

            with conn:
                # Prepare data for bulk insert
                columns = list(df.columns)
                columns_str = ",".join(
                    f'"{col}"' for col in columns
                )  # Quote column names

                # Convert DataFrame to list of tuples
                data_tuples = []
                for _, row in df.iterrows():
                    row_data = tuple(None if pd.isna(val) else val for val in row)
                    data_tuples.append(row_data)

                # Use execute_values with proper template
                with conn.cursor() as cur:
                    # Create the insert statement
                    insert_sql = f"INSERT INTO {table} ({columns_str}) VALUES %s ON CONFLICT DO NOTHING"

                    # Execute bulk insert
                    psycopg2.extras.execute_values(
                        cur, insert_sql, data_tuples, template=None, page_size=1000
                    )

                conn.commit()
                print(f"✅ Bulk insert completed: {len(data_tuples)} rows")
                return True

        except Exception as e:
            print(f"❌ Upload error: {e}")
            try:
                conn.rollback()
            except:
                pass
            return False

    def process_csv_file(self, csv_file_path):
        """Process a single CSV file"""
        csv_filename = Path(csv_file_path).name

        print(f"\n📄 Processing: {csv_filename}")

        # Get mapping information
        column_mapping = get_column_mapping(csv_filename)
        db_mapping = get_database_mapping(csv_filename)

        if not db_mapping:
            print(f"❌ No database mapping found for {csv_filename}")
            return False

        if not column_mapping:
            print(f"❌ No column mapping found for {csv_filename}")
            return False

        database = db_mapping["database"]
        table = db_mapping["table"]

        print(f"🎯 Target: {database}.{table}")

        try:
            # Load CSV file
            print("📖 Loading CSV file...")
            df = pd.read_csv(csv_file_path)
            print(f"📊 Loaded {len(df)} rows")

            # Clean data
            df = self.cleaner.clean_dataframe(df, csv_filename)

            # Apply column mapping
            print("🔄 Applying column mappings...")
            mapped_columns = {}
            for csv_col, db_col in column_mapping.items():
                if csv_col in df.columns:
                    mapped_columns[csv_col] = db_col

            # Rename columns and select only mapped ones
            df_mapped = df[list(mapped_columns.keys())].rename(columns=mapped_columns)
            print(f"✅ Mapped {len(mapped_columns)} columns")

            # Show sample data
            print("📋 Sample data (first 2 rows):")
            print(df_mapped.head(2).to_string())

            # Upload to database
            print("🚀 Uploading to database...")
            success = self.upload_dataframe(df_mapped, database, table)

            if success:
                print(
                    f"✅ Successfully uploaded {len(df_mapped)} rows to {database}.{table}"
                )
                return True
            else:
                print(f"❌ Upload failed for {csv_filename}")
                return False

        except Exception as e:
            print(f"❌ Error processing {csv_filename}: {e}")
            import traceback

            traceback.print_exc()
            return False

    def process_directory(self, directory_path):
        """Process all CSV files in directory (excluding non_target)"""
        directory = Path(directory_path)

        print(f"🔍 Scanning directory: {directory}")

        # Find all CSV files, excluding non_target
        csv_files = []
        for csv_file in directory.rglob("*.csv"):
            if "non_target" not in str(csv_file):
                csv_files.append(csv_file)

        print(f"📋 Found {len(csv_files)} CSV files:")
        for csv_file in sorted(csv_files):
            rel_path = csv_file.relative_to(directory)
            print(f"  • {rel_path}")

        # Process each file
        successful = 0
        failed = 0

        for csv_file in sorted(csv_files):
            print(f"\n{'='*60}")
            rel_path = csv_file.relative_to(directory)
            print(f"📁 Processing: {rel_path}")

            if self.process_csv_file(csv_file):
                successful += 1
            else:
                failed += 1

        # Summary
        total = successful + failed
        success_rate = (successful / total * 100) if total > 0 else 0

        print(f"\n{'='*60}")
        print("📊 PROCESSING SUMMARY")
        print(f"Total files: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {success_rate:.1f}%")


def main():
    """Main function"""
    print("🚀 Simple Bulk Uploader with Column Mapping")
    print("=" * 50)

    # Process the daily downloads directory
    data_dir = "/app/data/daily_downloads/processed"

    uploader = SimpleBulkUploader()
    uploader.process_directory(data_dir)


if __name__ == "__main__":
    main()
