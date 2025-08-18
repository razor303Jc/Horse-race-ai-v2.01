#!/usr/bin/env python3
"""
Complete CSV Processor - Port 5432
Maps ALL CSV columns to database with proper NULL handling
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2


class CompleteCsvProcessor:
    """Process all CSV files with complete column mapping and NULL handling"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.conn = None
        self.cursor = None

    def connect_to_database(self):
        """Connect to PostgreSQL database with correct port 5432"""
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                port="5432",  # Correct port
                database="horse_racing_db",
                user="horse_racing",
                password="secure_password_123",
            )
            self.cursor = self.conn.cursor()
            print("✅ Connected to database (port 5432)")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def load_mapping_config(self):
        """Load the complete column mapping configuration"""
        config_file = self.project_root / "config" / "complete_csv_column_mapping.json"
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load mapping config: {e}")
            return None

    def handle_null_value(self, value, column_type):
        """Handle NULL/blank/'-' values according to data type"""
        if pd.isna(value) or value == "" or value == "-" or value == "NULL":
            if column_type in ["integer", "numeric", "decimal", "bigint"]:
                return 0
            else:  # varchar, text, date, etc.
                return "none"
        return value

    def get_table_schema(self, table_name):
        """Get the column types for a table"""
        try:
            self.cursor.execute(
                """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """,
                (table_name,),
            )

            schema = {}
            for row in self.cursor.fetchall():
                schema[row[0]] = row[1]
            return schema
        except Exception as e:
            print(f"❌ Failed to get schema for {table_name}: {e}")
            return {}

    def process_csv_file(self, csv_path, table_name, column_mapping):
        """Process a single CSV file with complete column mapping"""
        print(f"\n📄 Processing {csv_path} -> {table_name}")

        if not Path(csv_path).exists():
            print(f"⚠️  File not found: {csv_path}")
            return False

        try:
            # Load CSV
            df = pd.read_csv(csv_path)
            print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")

            # Get table schema for NULL handling
            schema = self.get_table_schema(table_name)

            # Create mapped dataframe
            mapped_data = {}

            for db_column, csv_column in column_mapping.items():
                if csv_column in df.columns:
                    # Apply NULL handling based on column type
                    column_type = schema.get(db_column, "varchar")
                    mapped_data[db_column] = df[csv_column].apply(
                        lambda x: self.handle_null_value(x, column_type)
                    )
                    print(f"  ✅ {db_column} <- {csv_column}")
                else:
                    print(f"  ⚠️  Column not found: {csv_column}")
                    # Fill with default values
                    column_type = schema.get(db_column, "varchar")
                    default_value = (
                        0
                        if column_type in ["integer", "numeric", "decimal", "bigint"]
                        else "none"
                    )
                    mapped_data[db_column] = [default_value] * len(df)

            # Create mapped DataFrame
            mapped_df = pd.DataFrame(mapped_data)

            # Save mapped CSV
            output_file = (
                self.project_root
                / "data"
                / "daily_downloads"
                / f"complete_mapped_{table_name}.csv"
            )
            mapped_df.to_csv(output_file, index=False)
            print(f"💾 Saved mapped data: {output_file}")

            return True

        except Exception as e:
            print(f"❌ Error processing {csv_path}: {e}")
            return False

    def process_all_csv_files(self):
        """Process all CSV files according to the mapping configuration"""
        print("🚀 Starting complete CSV processing...")

        if not self.connect_to_database():
            return False

        config = self.load_mapping_config()
        if not config:
            return False

        processed_count = 0

        for table_name, table_config in config["table_mappings"].items():
            print(f"\n🔄 Processing table: {table_name}")

            csv_files = table_config["csv_files"]
            column_mapping = table_config["column_mapping"]

            for csv_file in csv_files:
                csv_path = self.project_root / csv_file
                if self.process_csv_file(csv_path, table_name, column_mapping):
                    processed_count += 1

        print(f"\n✅ Processing complete! {processed_count} files processed")

        # Close database connection
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

        return True


def main():
    """Main function"""
    print("🏇 Complete CSV Processor - Port 5432")
    print("=" * 50)

    processor = CompleteCsvProcessor()
    success = processor.process_all_csv_files()

    if success:
        print("\n🎉 All CSV files processed successfully!")
        print("🔍 Check data/daily_downloads/ for complete_mapped_*.csv files")
    else:
        print("\n❌ Processing failed")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
