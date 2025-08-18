#!/usr/bin/env python3
"""
Enhanced Data Preprocessing Pipeline
Comprehensive CSV data cleaning for ML training with all edge cases handled
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedDataPreprocessor:
    """
    Enhanced data preprocessing pipeline for horse racing CSV data
    Handles all data type conversions, nulls, and format standardization
    """

    def __init__(self):
        # Determine base path - use Docker path if available, otherwise local
        if Path("/app").exists():
            self.base_path = Path("/app")
        else:
            self.base_path = Path("/home/jc/Documents/Horse-race-ai-v2.02")

        # Define null-like values to handle
        self.null_values = [
            "",
            "-",
            "NULL",
            "null",
            "None",
            "none",
            "N/A",
            "n/a",
            "NA",
            "na",
            "~",
            "?",
            "unknown",
            "Unknown",
            "UNKNOWN",
        ]

        # Preprocessing statistics
        self.preprocessing_stats = {
            "rows_processed": 0,
            "columns_processed": 0,
            "nulls_filled": 0,
            "percentages_cleaned": 0,
            "currencies_cleaned": 0,
            "distances_cleaned": 0,
            "weights_cleaned": 0,
            "data_type_conversions": 0,
        }

    def is_null_like(self, value: Any) -> bool:
        """Check if a value should be treated as null"""
        if pd.isna(value) or value is None:
            return True
        if isinstance(value, str):
            return value.strip() in self.null_values
        return False

    def clean_percentage(self, value: Any) -> Optional[float]:
        """
        Clean percentage values - remove % symbol and convert to decimal
        Examples: '85%' -> 0.85, '100%' -> 1.0
        """
        if self.is_null_like(value):
            return None

        try:
            if isinstance(value, str) and "%" in value:
                self.preprocessing_stats["percentages_cleaned"] += 1
                # Remove % and convert to decimal
                numeric_part = value.replace("%", "").strip()
                return float(numeric_part) / 100.0
            else:
                return float(value)
        except (ValueError, TypeError):
            return None

    def clean_currency(self, value: Any) -> Optional[float]:
        """
        Clean currency values - remove symbols and commas
        Examples: '£6,281' -> 6281.0, '$1,000.50' -> 1000.5
        """
        if self.is_null_like(value):
            return None

        try:
            if isinstance(value, str):
                self.preprocessing_stats["currencies_cleaned"] += 1
                # Remove currency symbols and commas
                cleaned = re.sub(r"[£$€,]", "", value.strip())
                return float(cleaned)
            else:
                return float(value)
        except (ValueError, TypeError):
            return None

    def clean_distance(self, value: Any) -> Optional[float]:
        """
        Clean distance values to total meters
        Examples: '1m 2f 5y' -> 1828.8 meters, '6f' -> 1207.0 meters
        1 furlong = 201.168 meters, 1 mile = 1609.344 meters, 1 yard = 0.9144 meters
        """
        if self.is_null_like(value):
            return None

        try:
            if isinstance(value, str):
                self.preprocessing_stats["distances_cleaned"] += 1

                total_meters = 0

                # Extract miles (1609.344 meters each)
                miles_match = re.search(r"(\d+)m(?!\w)", value)
                if miles_match:
                    total_meters += int(miles_match.group(1)) * 1609.344

                # Extract furlongs (201.168 meters each)
                furlongs_match = re.search(r"(\d+)f", value)
                if furlongs_match:
                    total_meters += int(furlongs_match.group(1)) * 201.168

                # Extract yards (0.9144 meters each)
                yards_match = re.search(r"(\d+)y", value)
                if yards_match:
                    total_meters += int(yards_match.group(1)) * 0.9144

                # If no pattern matched, try to parse as number
                if total_meters == 0:
                    return float(value)

                return round(float(total_meters), 2)
            else:
                return float(value)
        except (ValueError, TypeError):
            return None

    def clean_uk_weight(self, value: Any) -> Optional[float]:
        """
        Clean UK weight format by replacing "-" with "."
        Examples: '9-7' -> 9.7, '8-12' -> 8.12, '10-0' -> 10.0
        """
        if self.is_null_like(value):
            return None

        try:
            if isinstance(value, str) and "-" in value:
                self.preprocessing_stats["weights_cleaned"] += 1

                # Replace "-" with "."
                cleaned_weight = value.replace("-", ".")
                return float(cleaned_weight)

            return float(value)
        except (ValueError, TypeError):
            return None

    def clean_odds(self, value: Any) -> Optional[float]:
        """
        Clean betting odds to decimal format
        Examples: '5/1' -> 6.0, '7/2' -> 4.5, '1/2' -> 1.5
        """
        if self.is_null_like(value):
            return None

        try:
            if isinstance(value, str) and "/" in value:
                parts = value.split("/")
                if len(parts) == 2:
                    numerator = float(parts[0])
                    denominator = float(parts[1])
                    return (numerator / denominator) + 1.0  # Convert to decimal odds

            return float(value)
        except (ValueError, TypeError):
            return None

    def clean_time_format(self, value: Any) -> Optional[str]:
        """
        Standardize time formats
        Examples: '2:35.67' -> '2:35.67', '155.67' -> '2:35.67'
        """
        if self.is_null_like(value):
            return None

        try:
            if isinstance(value, (int, float)):
                # Convert seconds to MM:SS.ss format
                total_seconds = float(value)
                minutes = int(total_seconds // 60)
                seconds = total_seconds % 60
                return f"{minutes}:{seconds:05.2f}"

            return str(value).strip()
        except (ValueError, TypeError):
            return None

    def infer_and_clean_column(self, series: pd.Series, column_name: str) -> pd.Series:
        """
        Infer column type and apply appropriate cleaning
        """
        col_name_lower = column_name.lower()

        # Handle specific column patterns
        if any(
            keyword in col_name_lower
            for keyword in ["percentage", "rate", "win_", "place_"]
        ):
            return series.apply(self.clean_percentage)

        elif any(
            keyword in col_name_lower
            for keyword in ["prize", "value", "stake", "£", "$"]
        ):
            return series.apply(self.clean_currency)

        elif any(keyword in col_name_lower for keyword in ["distance", "length"]):
            return series.apply(self.clean_distance)

        elif any(keyword in col_name_lower for keyword in ["weight", "carried"]):
            return series.apply(self.clean_uk_weight)

        elif any(keyword in col_name_lower for keyword in ["odds", "sp", "price"]):
            return series.apply(self.clean_odds)

        elif any(keyword in col_name_lower for keyword in ["time", "finish"]):
            return series.apply(self.clean_time_format)

        else:
            # Generic cleaning based on data content
            sample_values = series.dropna().head(10).astype(str)

            if sample_values.str.contains("%").any():
                return series.apply(self.clean_percentage)
            elif sample_values.str.contains("[£$€]").any():
                return series.apply(self.clean_currency)
            elif sample_values.str.contains(r"\d+[mfy]").any():
                return series.apply(self.clean_distance)
            elif sample_values.str.contains(r"\d+-\d+").any():
                return series.apply(self.clean_uk_weight)
            elif sample_values.str.contains(r"\d+/\d+").any():
                return series.apply(self.clean_odds)
            else:
                # Standard null handling
                return self.clean_standard_nulls(series)

    def clean_standard_nulls(self, series: pd.Series) -> pd.Series:
        """
        Handle standard null values based on inferred data type
        """
        # Try to infer if numeric
        sample = series.dropna().head(100)

        if len(sample) == 0:
            return series

        # Check if numeric
        try:
            pd.to_numeric(sample)
            is_numeric = True
        except:
            is_numeric = False

        if is_numeric:
            # For numeric columns: null -> 0
            cleaned = series.apply(lambda x: 0 if self.is_null_like(x) else x)
            try:
                return pd.to_numeric(cleaned, errors="coerce").fillna(0)
            except:
                return cleaned
        else:
            # For text columns: null -> None
            return series.apply(lambda x: None if self.is_null_like(x) else x)

    def preprocess_dataframe(
        self, df: pd.DataFrame, table_name: str = ""
    ) -> pd.DataFrame:
        """
        Preprocess entire DataFrame with comprehensive cleaning
        """
        logger.info(
            f"🧹 Preprocessing {table_name}: {df.shape[0]} rows, {df.shape[1]} columns"
        )

        preprocessed_df = df.copy()

        for column in df.columns:
            logger.debug(f"Processing column: {column}")

            original_nulls = df[column].isnull().sum()

            # Apply column-specific cleaning
            preprocessed_df[column] = self.infer_and_clean_column(df[column], column)

            # Update statistics
            new_nulls = preprocessed_df[column].isnull().sum()
            if new_nulls < original_nulls:
                self.preprocessing_stats["nulls_filled"] += original_nulls - new_nulls

            self.preprocessing_stats["columns_processed"] += 1

        self.preprocessing_stats["rows_processed"] += len(df)

        logger.info(
            f"✅ Preprocessing complete: {preprocessed_df.shape[0]} rows, {preprocessed_df.shape[1]} columns"
        )

        return preprocessed_df

    def preprocess_csv_file(
        self, file_path: Path, output_path: Optional[Path] = None
    ) -> pd.DataFrame:
        """
        Preprocess a single CSV file
        """
        logger.info(f"📄 Processing CSV: {file_path}")

        try:
            # Read CSV
            df = pd.read_csv(file_path)

            # Preprocess
            table_name = file_path.stem
            preprocessed_df = self.preprocess_dataframe(df, table_name)

            # Save if output path provided
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                preprocessed_df.to_csv(output_path, index=False)
                logger.info(f"💾 Saved preprocessed data: {output_path}")

            return preprocessed_df

        except Exception as e:
            logger.error(f"❌ Error preprocessing {file_path}: {e}")
            raise

    def process_all_csv_files(
        self, input_dir: Optional[str] = None, output_dir: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Process all CSV files in a directory with enhanced preprocessing
        """
        # Use Docker paths if available
        if input_dir is None:
            if self.base_path == Path("/app"):
                input_dir = "/app/data/daily_downloads"
            else:
                input_dir = str(self.base_path / "data" / "daily_downloads")

        if output_dir is None:
            if self.base_path == Path("/app"):
                output_dir = "/app/data/processed"
            else:
                output_dir = str(self.base_path / "data" / "processed")

        input_path = Path(input_dir)
        output_path = Path(output_dir)

        if not input_path.exists():
            logger.error("❌ Input directory not found: %s", input_path)
            return {}

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        processed_files = {}
        csv_files = list(input_path.rglob("*.csv"))

        if not csv_files:
            logger.warning("⚠️ No CSV files found in %s", input_path)
            return {}

        logger.info("🔄 Processing %d CSV files...", len(csv_files))

        for csv_file in csv_files:
            try:
                # Maintain directory structure in output
                relative_path = csv_file.relative_to(input_path)
                output_file = output_path / relative_path
                output_file.parent.mkdir(parents=True, exist_ok=True)

                preprocessed_df = self.preprocess_csv_file(csv_file, output_file)
                processed_files[str(csv_file)] = preprocessed_df

                logger.info("✅ Processed: %s", csv_file.name)

            except Exception as e:
                logger.error("❌ Failed to process %s: %s", csv_file, e)

        logger.info("🎉 Processing complete: %d files processed", len(processed_files))
        return processed_files

    def print_preprocessing_summary(self):
        """
        Print summary of preprocessing operations
        """
        print("\n" + "=" * 60)
        print("🧹 DATA PREPROCESSING SUMMARY")
        print("=" * 60)

        stats = self.preprocessing_stats
        print(f"📊 Rows processed: {stats['rows_processed']:,}")
        print(f"📋 Columns processed: {stats['columns_processed']:,}")
        print(f"🔧 Nulls filled: {stats['nulls_filled']:,}")
        print(f"📈 Percentages cleaned: {stats['percentages_cleaned']:,}")
        print(f"💰 Currencies cleaned: {stats['currencies_cleaned']:,}")
        print(f"📏 Distances cleaned: {stats['distances_cleaned']:,}")
        print(f"⚖️  Weights cleaned: {stats['weights_cleaned']:,}")
        print(f"🔄 Data type conversions: {stats['data_type_conversions']:,}")

        print("\n✅ Preprocessing completed successfully!")
        print("=" * 60)


def main():
    """
    Main function to demonstrate preprocessing pipeline
    """
    preprocessor = EnhancedDataPreprocessor()

    # Use appropriate paths based on environment
    if preprocessor.base_path == Path("/app"):
        # Running in Docker
        input_dir = Path("/app/data/daily_downloads")
        output_dir = Path("/app/data/preprocessed")
    else:
        # Running locally
        input_dir = Path("/home/jc/Documents/Horse-race-ai-v2.02/data/daily_downloads")
        output_dir = Path("/home/jc/Documents/Horse-race-ai-v2.02/data/preprocessed")

    if input_dir.exists():
        results = preprocessor.process_all_csv_files(str(input_dir), str(output_dir))

        # Show sample results
        for file_name, df in results.items():
            if df is not None:
                print(f"\n📄 {file_name}: {df.shape}")
                print(f"   Sample data types: {dict(df.dtypes.head())}")
    else:
        print(f"❌ Input directory not found: {input_dir}")


if __name__ == "__main__":
    main()
