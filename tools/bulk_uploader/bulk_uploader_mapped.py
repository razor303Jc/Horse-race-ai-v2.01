#!/usr/bin/env python3
"""
Bulk Uploader with Proper Column Mapping
Uses the column mappings and data cleaning rules
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

    def clean_percentage_fields(self, df, column_mappings):
        """Clean percentage fields (remove % symbol)"""
        percentage_fields = self.cleaning_rules["percentage_fields"]

        for csv_col, db_col in column_mappings.items():
            if db_col in percentage_fields and csv_col in df.columns:
                # Remove % symbol and keep as string (database expects varchar)
                df[csv_col] = df[csv_col].astype(str).str.replace("%", "", regex=False)

    def clean_weight_fields(self, df, column_mappings):
        """Convert UK weight format (e.g., '10-2' -> '10.2')"""
        weight_fields = self.cleaning_rules["weight_fields"]

        for csv_col, db_col in column_mappings.items():
            if db_col in weight_fields and csv_col in df.columns:
                # Convert UK weight format
                df[csv_col] = df[csv_col].astype(str).apply(self._convert_uk_weight)

    def _convert_uk_weight(self, weight_str):
        """Convert UK weight format to decimal"""
        if pd.isna(weight_str) or weight_str in ["", "-", "None"]:
            return None

        weight_str = str(weight_str).strip()

        # Pattern: "10-2" -> "10.2"
        match = re.match(r"^(\d+)-(\d+)$", weight_str)
        if match:
            pounds = int(match.group(1))
            ounces = int(match.group(2))
            return f"{pounds}.{ounces}"

        return weight_str

    def clean_prize_fields(self, df, column_mappings):
        """Clean prize fields (remove currency symbols)"""
        prize_fields = self.cleaning_rules["prize_fields"]

        for csv_col, db_col in column_mappings.items():
            if db_col in prize_fields and csv_col in df.columns:
                # Remove currency symbols like €, £, $
                df[csv_col] = (
                    df[csv_col].astype(str).str.replace(r"[€£$,]", "", regex=True)
                )

    def clean_dataframe(self, df, csv_filename):
        """Apply all cleaning rules to dataframe"""
        column_mappings = get_column_mapping(csv_filename)

        print(f"🧹 Cleaning data for {csv_filename}")

        # Apply cleaning rules
        self.clean_dash_symbols(df, column_mappings)
        self.clean_percentage_fields(df, column_mappings)
        self.clean_weight_fields(df, column_mappings)
        self.clean_prize_fields(df, column_mappings)

        print(f"✅ Data cleaning completed")
        return df


class BulkUploaderWithMapping:
    """Bulk uploader with proper column mapping and data cleaning"""

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
        print(f"🗂️  Column mappings: {len(column_mapping)} columns")

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
                else:
                    print(f"⚠️  CSV column '{csv_col}' not found in file")

            # Rename columns
            df_mapped = df[list(mapped_columns.keys())].rename(columns=mapped_columns)
            print(f"✅ Mapped {len(mapped_columns)} columns")

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
            return False

    def upload_dataframe(self, df, database, table):
        """Upload dataframe to database table"""
        try:
            conn = self.get_connection(database)

            with conn:
                # Prepare data for bulk insert
                columns = list(df.columns)

                # Convert DataFrame to list of tuples
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

                # Build bulk insert query with conflict handling
                placeholders = ",".join(["%s"] * len(columns))
                columns_str = ",".join(columns)

                query = f"""
                    INSERT INTO {table} ({columns_str}) 
                    VALUES ({placeholders})
                    ON CONFLICT DO NOTHING
                """

                # Execute bulk insert
                with conn.cursor() as cur:
                    psycopg2.extras.execute_values(
                        cur, query, data_tuples, template=None, page_size=1000
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

    def process_directory(self, directory_path):
        """Process all CSV files in directory (excluding non_target)"""
        directory = Path(directory_path)

        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            return

        print(f"🔍 Scanning directory: {directory}")

        # Find all CSV files, excluding non_target
        csv_files = []
        for csv_file in directory.rglob("*.csv"):
            if "non_target" not in str(csv_file):
                csv_files.append(csv_file)

        if not csv_files:
            print("❌ No CSV files found")
            return

        print(f"📋 Found {len(csv_files)} CSV files to process")

        # Process each file
        successful = 0
        failed = 0

        for csv_file in sorted(csv_files):
            print(f"\n{'='*60}")
            rel_path = csv_file.relative_to(directory)
            print(f"📁 File: {rel_path}")

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
    print("🚀 Bulk Uploader with Column Mapping")
    print("=" * 50)

    # Process the daily downloads directory
    data_dir = "/app/data/daily_downloads/processed"

    uploader = BulkUploaderWithMapping()
    uploader.process_directory(data_dir)


if __name__ == "__main__":
    main()
