#!/usr/bin/env python3
"""
Smart CSV Processor - Modified Qwen2.5 Solution
Handles text data properly for trainer/jockey stats tables
"""

import logging
import re
from pathlib import Path

import chardet
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SmartCSVProcessor:
    """
    Modified Qwen2.5 solution that doesn't convert text fields to integers
    """

    def __init__(self):
        # Define which columns should remain as text for each table
        self.text_columns = {
            "trainer_stats": ["Name", "UptoDate"],
            "jockey_stats": ["Name", "UptoDate"],
            "horses": [
                "name",
                "country",
                "trainer",
                "jockey",
                "color",
                "owner",
                "sire",
                "dam",
                "dam_sire",
                "sex",
            ],
            "race_results": [
                "jockey",
                "trainer",
                "Distance_btn",
                "fav",
                "SP",
                "Country",
                "Name",
                "weight_uk",
                "gears",
            ],
            "racecard_details": [
                "horse_name",
                "odds",
                "Country",
                "Name",
                "weight_uk",
                "gears",
                "fav",
                "Timeform_comments",
            ],
            "races_cards": [
                "Course",
                "race_name",
                "Race_type",
                "Distance",
                "Surface",
                "Prize",
                "Class",
                "Years",
                "race_time",
                "Date",
            ],
        }

        # Columns that should definitely be numeric
        self.numeric_columns = {
            "trainer_stats": [
                "Trainer_ID",
                "Total_races",
                "Wins",
                "Placed",
                "Percentage_wins",
                "Percentage_placed",
            ],
            "jockey_stats": [
                "jockey_ID",
                "Total_races",
                "Wins",
                "Placed",
                "Percentage_wins",
                "Percentage_placed",
            ],
        }

    def detect_encoding(self, file_path):
        """Detect file encoding using chardet"""
        try:
            with open(file_path, "rb") as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding = result["encoding"]
                logger.info(f"Detected encoding for {file_path}: {encoding}")
                return encoding
        except Exception as e:
            logger.warning(f"Failed to detect encoding for {file_path}: {e}")
            return "utf-8"

    def smart_convert_column(self, series, column_name, table_name):
        """
        Smart conversion - keeps text as text, converts numbers to numbers
        """
        # If this column should remain as text, don't convert
        if table_name in self.text_columns:
            if column_name in self.text_columns[table_name]:
                logger.info(f"Keeping {column_name} as text for {table_name}")
                return series.astype(str)

        # If this column should be numeric, try to convert
        if table_name in self.numeric_columns:
            if column_name in self.numeric_columns[table_name]:
                logger.info(f"Converting {column_name} to numeric for {table_name}")
                return pd.to_numeric(series, errors="coerce").fillna(0)

        # For other columns, try to intelligently determine type
        # If it looks like numbers, convert to numeric
        if series.dtype == "object":
            # Try converting to numeric
            numeric_series = pd.to_numeric(series, errors="coerce")
            # If more than 50% can be converted to numbers, treat as numeric
            valid_numbers = numeric_series.notna().sum()
            total_values = len(series)

            if valid_numbers / total_values > 0.5:
                logger.info(f"Converting {column_name} to numeric (auto-detected)")
                return numeric_series.fillna(0)
            else:
                logger.info(f"Keeping {column_name} as text (auto-detected)")
                return series.astype(str)

        return series

    def process_csv_smart(self, file_path, table_name):
        """
        Process CSV with smart column type detection
        """
        logger.info(f"🔄 Smart processing {file_path} for {table_name}")

        try:
            # Detect encoding
            encoding = self.detect_encoding(file_path)

            # Read CSV
            df = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"📊 Loaded {df.shape[0]} rows, {df.shape[1]} columns")

            # Handle duplicates for horses table
            if table_name == "horses":
                original_count = len(df)
                df = df.drop_duplicates(subset=["name", "uptodate"], keep="first")
                if len(df) < original_count:
                    removed = original_count - len(df)
                    logger.info(f"🔄 Removed {removed} duplicate horses")

            # Process each column smartly
            for column in df.columns:
                df[column] = self.smart_convert_column(df[column], column, table_name)

            # Fill NaN values appropriately
            for column in df.columns:
                if df[column].dtype in ["object", "string"]:
                    df[column] = df[column].fillna("Unknown")
                else:
                    df[column] = df[column].fillna(0)

            logger.info(f"✅ Smart processed {df.shape[0]} rows for {table_name}")
            return df

        except Exception as e:
            logger.error(f"❌ Failed to process {file_path}: {e}")
            return None


def test_smart_processing():
    """Test the smart processing"""
    processor = SmartCSVProcessor()

    # Test with trainer stats
    file_path = "project_root / 'data' / horseracedatabase/results_project_root / 'data' / trainers_stats/trainers_stats.csv"
    df = processor.process_csv_smart(file_path, "trainer_stats")

    if df is not None:
        print("✅ Smart processing test successful!")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(
            f"Sample trainer name: {df['Name'].iloc[0] if 'Name' in df.columns else 'N/A'}"
        )
        print(f"Sample data types:")
        for col in df.columns[:5]:
            print(f"  {col}: {df[col].dtype}")
    else:
        print("❌ Smart processing test failed!")


if __name__ == "__main__":
    test_smart_processing()
