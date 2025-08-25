#!/usr/bin/env python3
"""
Enhanced Data Cleaner - Handles All Data Type Issues
Converts percentages, handles NULL values, fixes data types automatically
"""

import pandas as pd
import numpy as np
import re
from decimal import Decimal, InvalidOperation


class EnhancedDataCleaner:
    """
    Enhanced data cleaning for CSV-to-Database uploads
    Handles all data type conversion issues automatically
    """

    def __init__(self):
        self.null_values = [
            "-",
            "",
            "None",
            "NULL",
            "null",
            "nan",
            "NaN",
            "NA",
            pd.NA,
            np.nan,
        ]

    def clean_percentage_value(self, value):
        """Convert percentage strings to decimal values"""
        if pd.isna(value) or value in self.null_values:
            return None

        if isinstance(value, str):
            # Remove % symbol and convert to decimal
            if "%" in value:
                try:
                    numeric_part = value.replace("%", "").strip()
                    return float(numeric_part) / 100.0
                except (ValueError, TypeError):
                    return None

        # If already numeric, assume it's a decimal (not percentage)
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def clean_integer_value(self, value):
        """Convert values to integers, handling various edge cases"""
        if pd.isna(value) or value in self.null_values:
            return None

        if isinstance(value, str):
            value = value.strip()
            if value in self.null_values:
                return None

        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def clean_decimal_value(self, value):
        """Convert values to decimal/float, handling various edge cases"""
        if pd.isna(value) or value in self.null_values:
            return None

        if isinstance(value, str):
            value = value.strip()
            if value in self.null_values:
                return None

            # Handle percentage values
            if "%" in value:
                return self.clean_percentage_value(value)

        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def clean_string_value(self, value):
        """Clean string values"""
        if pd.isna(value) or value in self.null_values:
            return None

        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned in self.null_values or cleaned == "":
                return None
            return cleaned

        # Convert non-string values to string
        try:
            return str(value).strip()
        except:
            return None

    def get_database_column_type(self, table_name: str, column_name: str) -> str:
        """
        Determine the expected database column type
        This helps us apply the right cleaning function
        """
        # Common patterns for different data types
        percentage_columns = [
            "win_rate",
            "place_rate",
            "percentage_wins",
            "percentage_placed",
        ]
        integer_columns = [
            "id",
            "race_id",
            "horse_id",
            "jockey_id",
            "trainer_id",
            "wins",
            "runs",
            "total_races",
            "horse_number",
            "place",
            "draw",
            "age",
        ]
        decimal_columns = [
            "sp",
            "horse_rate",
            "distance_btn",
            "finish_time",
        ] + percentage_columns

        if column_name in percentage_columns:
            return "percentage"
        elif column_name in integer_columns:
            return "integer"
        elif column_name in decimal_columns:
            return "decimal"
        elif column_name.endswith("_time") or column_name.endswith("_rate"):
            return "decimal"
        elif "id" in column_name.lower():
            return "integer"
        else:
            return "string"

    def clean_dataframe_for_upload(
        self, df: pd.DataFrame, table_name: str
    ) -> pd.DataFrame:
        """
        Clean entire DataFrame for database upload
        Apply appropriate cleaning based on column types
        """
        print(f"🧹 Enhanced cleaning for {table_name}")

        cleaned_df = df.copy()

        for column in cleaned_df.columns:
            column_type = self.get_database_column_type(table_name, column)

            print(f"   🔧 Cleaning {column} as {column_type}")

            if column_type == "percentage":
                cleaned_df[column] = cleaned_df[column].apply(
                    self.clean_percentage_value
                )
            elif column_type == "integer":
                cleaned_df[column] = cleaned_df[column].apply(self.clean_integer_value)
            elif column_type == "decimal":
                cleaned_df[column] = cleaned_df[column].apply(self.clean_decimal_value)
            else:  # string
                cleaned_df[column] = cleaned_df[column].apply(self.clean_string_value)

        # Remove rows where all values are None (but keep rows with some valid data)
        initial_rows = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(how="all")
        final_rows = len(cleaned_df)

        if initial_rows != final_rows:
            print(f"   📊 Removed {initial_rows - final_rows} completely empty rows")

        return cleaned_df


def main():
    """Test the enhanced data cleaner"""
    cleaner = EnhancedDataCleaner()

    # Test percentage conversion
    test_percentages = ["15.64%", "0%", "100%", "-", "", "None"]
    print("Testing percentage conversion:")
    for val in test_percentages:
        result = cleaner.clean_percentage_value(val)
        print(f"  '{val}' → {result}")

    # Test integer conversion
    test_integers = ["123", "-", "", "0", "1.0", "None"]
    print("\nTesting integer conversion:")
    for val in test_integers:
        result = cleaner.clean_integer_value(val)
        print(f"  '{val}' → {result}")


if __name__ == "__main__":
    main()
