"""
Complete CSV to Database Processor
Maps ALL CSV columns to database tables with proper NULL handling
Preserves ALL data - converts blank/NULL/"-" to appropriate defaults
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch


class CompleteCsvDatabaseProcessor:
    def __init__(self, config_path: str = "config/complete_csv_column_mapping.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.connection = None
        self.logger = self.setup_logging()

    def setup_logging(self):
        """Setup logging for the processor"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("logs/complete_csv_processor.log"),
                logging.StreamHandler(),
            ],
        )
        return logging.getLogger(__name__)

    def load_config(self) -> Dict:
        """Load the complete CSV column mapping configuration"""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in configuration file: {e}")
            raise

    def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "horse_racing"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "password"),
                port=os.getenv("DB_PORT", "5432"),
            )
            self.connection.autocommit = False
            self.logger.info("Connected to PostgreSQL database")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise

    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")

    def clean_value(self, value: Any, data_type: str) -> Any:
        """
        Clean and convert values based on NULL handling rules
        - Integers: blank/""/"-"/"NULL" -> 0
        - Decimals: blank/""/"-"/"NULL" -> 0.0
        - Strings: blank/""/"-"/"NULL" -> "none"
        """
        global_null_values = self.config["global_null_handling"]["null_values"]

        # Check if value is null-like
        if pd.isna(value) or str(value).strip() in global_null_values:
            if data_type == "integers":
                return self.config["global_null_handling"]["integer_replacement"]
            elif data_type == "decimals":
                return self.config["global_null_handling"]["decimal_replacement"]
            elif data_type == "strings":
                return self.config["global_null_handling"]["string_replacement"]

        # Convert to appropriate type
        try:
            if data_type == "integers":
                return int(float(str(value).strip()))
            elif data_type == "decimals":
                return float(str(value).strip())
            elif data_type == "strings":
                return str(value).strip()
        except (ValueError, TypeError):
            # If conversion fails, use default value
            if data_type == "integers":
                return self.config["global_null_handling"]["integer_replacement"]
            elif data_type == "decimals":
                return self.config["global_null_handling"]["decimal_replacement"]
            else:
                return self.config["global_null_handling"]["string_replacement"]

        return value

    def get_column_data_type(self, table: str, column: str) -> str:
        """Get the data type for a column in a table"""
        table_config = self.config["table_mappings"][table]
        null_handling = table_config["null_handling"]

        if column in null_handling.get("integers", []):
            return "integers"
        elif column in null_handling.get("decimals", []):
            return "decimals"
        elif column in null_handling.get("strings", []):
            return "strings"
        else:
            return "strings"  # Default to string

    def create_table_if_not_exists(self, table_name: str):
        """Create database table to match CSV structure exactly"""
        table_config = self.config["table_mappings"][table_name]
        column_mapping = table_config["column_mapping"]
        null_handling = table_config["null_handling"]

        # Build CREATE TABLE statement
        columns = []
        for db_column, csv_column in column_mapping.items():
            if db_column in null_handling["integers"]:
                columns.append(f"{db_column} INTEGER DEFAULT 0")
            elif db_column in null_handling["decimals"]:
                columns.append(f"{db_column} DECIMAL DEFAULT 0.0")
            else:
                columns.append(f"{db_column} TEXT DEFAULT 'none'")

        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            {', '.join(columns)},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(create_sql)
            self.connection.commit()
            cursor.close()
            self.logger.info(f"Table {table_name} created/verified successfully")
        except Exception as e:
            self.logger.error(f"Failed to create table {table_name}: {e}")
            self.connection.rollback()
            raise

    def process_csv_file(self, csv_path: str, table_name: str) -> int:
        """Process a single CSV file and insert ALL data into database"""
        if not os.path.exists(csv_path):
            self.logger.warning(f"CSV file not found: {csv_path}")
            return 0

        try:
            # Read CSV file
            df = pd.read_csv(csv_path)
            self.logger.info(f"Read {len(df)} rows from {csv_path}")

            if df.empty:
                self.logger.warning(f"CSV file is empty: {csv_path}")
                return 0

            # Get table configuration
            table_config = self.config["table_mappings"][table_name]
            column_mapping = table_config["column_mapping"]

            # Create table if it doesn't exist
            self.create_table_if_not_exists(table_name)

            # Process each row
            processed_rows = []
            for _, row in df.iterrows():
                processed_row = {}
                for db_column, csv_column in column_mapping.items():
                    if csv_column in df.columns:
                        data_type = self.get_column_data_type(table_name, db_column)
                        processed_row[db_column] = self.clean_value(
                            row[csv_column], data_type
                        )
                    else:
                        # Column missing from CSV - use default value
                        data_type = self.get_column_data_type(table_name, db_column)
                        processed_row[db_column] = self.clean_value(None, data_type)

                processed_rows.append(processed_row)

            # Insert into database
            if processed_rows:
                inserted_count = self.insert_rows(table_name, processed_rows)
                self.logger.info(f"Inserted {inserted_count} rows into {table_name}")
                return inserted_count

        except Exception as e:
            self.logger.error(f"Error processing CSV file {csv_path}: {e}")
            raise

        return 0

    def insert_rows(self, table_name: str, rows: List[Dict]) -> int:
        """Insert rows into database table"""
        if not rows:
            return 0

        try:
            cursor = self.connection.cursor()

            # Get column names from first row
            columns = list(rows[0].keys())
            placeholders = ", ".join(["%s"] * len(columns))
            column_names = ", ".join(columns)

            insert_sql = f"""
            INSERT INTO {table_name} ({column_names})
            VALUES ({placeholders})
            """

            # Convert rows to tuples
            values = [tuple(row[col] for col in columns) for row in rows]

            execute_batch(cursor, insert_sql, values, page_size=1000)
            self.connection.commit()
            cursor.close()

            return len(values)

        except Exception as e:
            self.logger.error(f"Failed to insert rows into {table_name}: {e}")
            self.connection.rollback()
            raise

    def process_all_csv_files(self) -> Dict[str, int]:
        """Process all CSV files according to configuration"""
        results = {}

        try:
            self.connect_database()

            for table_name, table_config in self.config["table_mappings"].items():
                total_inserted = 0

                for csv_file in table_config["csv_files"]:
                    inserted_count = self.process_csv_file(csv_file, table_name)
                    total_inserted += inserted_count

                results[table_name] = total_inserted
                self.logger.info(
                    f"Table {table_name}: {total_inserted} total rows processed"
                )

        except Exception as e:
            self.logger.error(f"Error in process_all_csv_files: {e}")
            raise
        finally:
            self.close_connection()

        return results

    def validate_csv_mapping(self) -> Dict[str, List[str]]:
        """Validate that all CSV columns are mapped"""
        validation_results = {}

        for table_name, table_config in self.config["table_mappings"].items():
            missing_mappings = []

            for csv_file in table_config["csv_files"]:
                if os.path.exists(csv_file):
                    try:
                        df = pd.read_csv(csv_file, nrows=1)  # Just read headers
                        csv_columns = set(df.columns)
                        mapped_columns = set(table_config["column_mapping"].values())

                        unmapped = csv_columns - mapped_columns
                        if unmapped:
                            missing_mappings.extend(list(unmapped))

                    except Exception as e:
                        self.logger.error(
                            f"Error reading CSV headers from {csv_file}: {e}"
                        )

            validation_results[table_name] = list(set(missing_mappings))

        return validation_results


def main():
    """Main function to process all CSV files"""
    processor = CompleteCsvDatabaseProcessor()

    # Validate mapping
    print("Validating CSV column mappings...")
    validation_results = processor.validate_csv_mapping()

    for table, missing in validation_results.items():
        if missing:
            print(f"⚠️  Table {table} has unmapped columns: {missing}")
        else:
            print(f"✅ Table {table} - all columns mapped")

    # Process all files
    print("\nProcessing all CSV files...")
    results = processor.process_all_csv_files()

    print("\n📊 Processing Results:")
    total_rows = 0
    for table, count in results.items():
        print(f"  {table}: {count:,} rows")
        total_rows += count

    print(f"\n🎯 Total rows processed: {total_rows:,}")
    print("✅ Complete CSV processing finished successfully!")


if __name__ == "__main__":
    main()
