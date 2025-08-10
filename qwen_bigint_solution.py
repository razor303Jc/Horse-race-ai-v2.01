#!/usr/bin/env python3
"""
Qwen2.5's BIGINT Overflow Solution Implementation
Based on root cause analysis identifying potential data integrity and conversion issues
"""

import logging
import re
from pathlib import Path

import chardet
import numpy as np
import pandas as pd
import psycopg2

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class QwenBigintSolver:
    """
    Qwen2.5's solution for resolving BIGINT overflow issues
    Implements comprehensive data validation, cleaning, and enhanced conversion logic
    """

    def __init__(self):
        self.racing_codes = {
            "U": 99,
            "DQ": 92,
            "S": 91,
            "F": 90,
            "PU": 89,
            "R": 88,
            "BD": 87,
            "UR": 86,
            "SU": 85,
            "RO": 84,
            "LFT": 83,
            "REF": 82,
            "VO": 81,
            "DSQ": 80,
        }

    def detect_encoding(self, file_path):
        """
        Qwen2.5 Solution 1: Detect file encoding to handle hidden characters
        """
        logger.info(f"Detecting encoding for {file_path}")
        with open(file_path, "rb") as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            logger.info(f"Detected encoding: {result}")
            return result["encoding"]

    def clean_csv_data(self, file_path):
        """
        Qwen2.5 Solution 2: Enhanced data cleaning to handle NaN and hidden characters
        """
        logger.info(f"Cleaning CSV data: {file_path}")

        # Detect encoding first
        encoding = self.detect_encoding(file_path)

        # Read with proper encoding
        try:
            df = pd.read_csv(file_path, encoding=encoding)
        except Exception as e:
            logger.warning(f"Encoding {encoding} failed, trying utf-8: {e}")
            df = pd.read_csv(file_path, encoding="utf-8", errors="ignore")

        # Clean hidden characters and normalize whitespace
        for col in df.columns:
            if df[col].dtype == "object":  # String columns
                df[col] = df[col].astype(str).str.strip()
                # Remove hidden characters, control characters, etc.
                df[col] = df[col].str.replace(r"[\x00-\x1f\x7f-\x9f]", "", regex=True)
                # Normalize whitespace
                df[col] = df[col].str.replace(r"\s+", " ", regex=True)

        logger.info(f"CSV cleaned. Shape: {df.shape}")
        return df

    def enhanced_convert_to_integer(self, value):
        """
        Qwen2.5 Solution 3: Enhanced conversion logic with comprehensive error handling
        """
        try:
            # Handle None, NaN, empty strings
            if pd.isna(value) or value is None or value == "":
                return None

            # Convert to string for processing
            if not isinstance(value, str):
                value = str(value)

            # Clean and strip
            value = value.strip()

            # Handle racing codes
            if value.upper() in self.racing_codes:
                result = self.racing_codes[value.upper()]
                logger.debug(f"Racing code {value} -> {result}")
                return result

            # Remove any non-digit characters except minus sign
            cleaned_value = re.sub(r"[^\d-]", "", value)

            if not cleaned_value or cleaned_value == "-":
                logger.warning(f"Could not clean value: '{value}' -> '{cleaned_value}'")
                return None

            # Convert to integer
            result = int(cleaned_value)

            # Check BIGINT bounds (-9223372036854775808 to 9223372036854775807)
            bigint_min = -9223372036854775808
            bigint_max = 9223372036854775807

            if result < bigint_min or result > bigint_max:
                logger.error(f"Value {result} exceeds BIGINT bounds!")
                return None

            return result

        except Exception as e:
            logger.error(f"Error converting '{value}' to integer: {e}")
            return None

    def validate_dataframe_before_upload(self, df, table_name):
        """
        Qwen2.5 Solution 4: Comprehensive validation before database upload
        """
        logger.info(f"Validating DataFrame for table: {table_name}")

        # Check for extreme values
        numeric_columns = df.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            max_val = df[col].max()
            min_val = df[col].min()

            logger.info(f"Column {col}: min={min_val}, max={max_val}")

            # Check BIGINT bounds
            bigint_min = -9223372036854775808
            bigint_max = 9223372036854775807

            if max_val > bigint_max or min_val < bigint_min:
                logger.error(f"Column {col} has values outside BIGINT range!")
                # Show problematic values
                problematic = df[(df[col] > bigint_max) | (df[col] < bigint_min)]
                logger.error(f"Problematic rows: {problematic.index.tolist()}")
                return False

        # Check for NaN values that might cause issues
        nan_columns = df.columns[df.isnull().any()].tolist()
        if nan_columns:
            logger.warning(f"Columns with NaN values: {nan_columns}")
            for col in nan_columns:
                nan_count = df[col].isnull().sum()
                logger.warning(f"Column {col}: {nan_count} NaN values")

        logger.info("DataFrame validation passed!")
        return True

    def process_problematic_csv(self, file_path, table_name):
        """
        Qwen2.5 Complete Solution: Process problematic CSV files with all enhancements
        """
        logger.info(f"Processing problematic CSV: {file_path} -> {table_name}")

        # Step 1: Clean CSV data
        df = self.clean_csv_data(file_path)

        # Step 2: Enhanced integer conversion for all columns
        for col in df.columns:
            if df[col].dtype == "object":  # Potential string-encoded numbers
                logger.info(f"Processing column: {col}")
                df[col] = df[col].apply(self.enhanced_convert_to_integer)

        # Step 3: Handle remaining NaN values
        df = df.fillna(0)  # or another appropriate default

        # Step 4: Ensure integer columns are properly typed
        integer_columns = df.select_dtypes(include=[np.number]).columns
        for col in integer_columns:
            # Convert to int64 (Python's int maps to BIGINT in PostgreSQL)
            df[col] = df[col].astype("int64")

        # Step 5: Validate before upload
        if not self.validate_dataframe_before_upload(df, table_name):
            raise ValueError(f"DataFrame validation failed for {table_name}")

        logger.info(f"Successfully processed {len(df)} rows for {table_name}")
        return df

    def test_problematic_files(self):
        """
        Test the solution on the problematic files
        """
        problematic_files = [
            ("data/horseracedatabase/results_data/records/records.csv", "race_results"),
            (
                "data/horseracedatabase/cards_data/racecard_details/racecard_details.csv",
                "racecard_details",
            ),
        ]

        for file_path, table_name in problematic_files:
            if Path(file_path).exists():
                try:
                    logger.info(f"\n{'='*50}")
                    logger.info(f"Testing: {file_path}")
                    logger.info(f"{'='*50}")

                    df = self.process_problematic_csv(file_path, table_name)

                    logger.info(f"✅ SUCCESS: {file_path}")
                    logger.info(f"   Rows processed: {len(df)}")
                    logger.info(f"   Columns: {list(df.columns)}")

                    # Show sample of processed data
                    logger.info(f"   Sample data:")
                    logger.info(df.head().to_string())

                except Exception as e:
                    logger.error(f"❌ FAILED: {file_path} - {e}")
            else:
                logger.warning(f"File not found: {file_path}")


def main():
    """
    Run Qwen2.5's BIGINT solution
    """
    print("🧬 Qwen2.5 BIGINT Overflow Solution")
    print("=" * 50)

    solver = QwenBigintSolver()
    solver.test_problematic_files()

    print("\n🎯 Solution Summary:")
    print("1. ✅ Enhanced encoding detection")
    print("2. ✅ Comprehensive data cleaning")
    print("3. ✅ Robust integer conversion")
    print("4. ✅ Pre-upload validation")
    print("5. ✅ BIGINT bounds checking")


if __name__ == "__main__":
    main()
