#!/usr/bin/env python3
"""
Column Mapping Solution for Database Upload
===========================================

Maps CSV columns from horseracedatabase.com to our PostgreSQL schema.
Handles the mismatch between downloaded CSV structure and database tables.
"""

import logging
import pandas as pd
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ColumnMapper:
    """
    Maps CSV columns to database columns for each table
    """

    def __init__(self):
        # Define column mappings for each table
        self.column_mappings = {
            "race_results": {
                # CSV column -> Database column
                "ID": "race_result_id",
                "Race_ID": "race_id",
                "Horse_ID": "horse_id",
                "Name": "horse_name",
                "jockey_ID": "jockey_id",
                "jockey": "jockey_name",
                "trainer_ID": "trainer_id",
                "trainer": "trainer_name",
                "Age": "horse_age",
                "weight": "horse_weight_kg",
                "Draw": "draw",
                "Place": "finished_position",
                "SP": "win_odds",
                "finish_time": "time_seconds",
                # Note: Many CSV columns don't have direct database equivalents
                # We'll only map the ones that do exist
            },
            "horses": {
                "id": "horse_id_numeric",
                "name": "horse_name",
                "country": "country",
                "age": "foaled",  # We'll need to calculate birth year from age
                "color": "color",
                "owner": "owner",
                "sire": "sire",
                "dam": "dam",
                "dam_sire": "dam_sire",
                "sex": "sex",
                "Total_races": "runs",
                "Wins": "wins",
                "placed": "places",
                "Percentage_wins": "win_percentage",
                "Percentage_placed": "place_percentage",
                # CSV has more detailed race type stats than our simple schema
            },
            "jockey_stats": {
                "Jockey_ID": "jockey_id",
                "Name": "jockey_name",
                "Total_races": "runs",
                "Wins": "wins",
                "Placed": "places",
                "Percentage_wins": "win_percentage",
                "Percentage_placed": "place_percentage",
                "UptoDate": "uptodate",
                # CSV has detailed race type stats but our schema has simplified version
            },
            "trainer_stats": {
                "Trainer_ID": "trainer_id",
                "Name": "trainer_name",
                "Total_races": "runs",
                "Wins": "wins",
                "Placed": "places",
                "Percentage_wins": "win_percentage",
                "Percentage_placed": "place_percentage",
                "UptoDate": "uptodate",
                # CSV has detailed race type stats but our schema has simplified version
            },
            "races_cards": {
                "Race_ID": "race_id",
                "race_number": "race_number",
                "race_time": "race_time",
                "Course": "course",
                "Race_type": "race_type",
                "Date": "date",
                "Race_name": "race_name",
                "Distance": "distance",
                "Surface": "surface",
                # Many CSV columns don't have direct database mappings
            },
            "racecard_details": {
                "id": "racecard_detail_id",
                "race_id": "race_id",
                "horse_number": "horse_number",
                "Draw": "draw",
                "Horse_ID": "horse_id",
                "Name": "horse_name",
                "Age": "horse_age",
                "weight": "horse_weight_kg",
                "jockey_ID": "jockey_id",
                "jockey": "jockey_name",
                "trainer_ID": "trainer_id",
                "trainer": "trainer_name",
                "odds_decimal": "odds_decimal",
                # Many columns like Timeform_comments don't have mappings
            },
        }

    def map_dataframe_columns(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        Map CSV DataFrame columns to database columns

        Args:
            df: Input DataFrame with CSV columns
            table_name: Target database table name

        Returns:
            DataFrame with mapped columns
        """
        if table_name not in self.column_mappings:
            logger.warning(f"No column mapping defined for table: {table_name}")
            return df

        mapping = self.column_mappings[table_name]
        mapped_df = pd.DataFrame()

        logger.info(f"Mapping columns for {table_name}:")

        # Map each column that exists in both CSV and mapping
        for csv_col, db_col in mapping.items():
            if csv_col in df.columns:
                mapped_df[db_col] = df[csv_col].copy()

                # Handle special data type conversions
                if db_col == "uptodate" and table_name in [
                    "trainer_stats",
                    "jockey_stats",
                ]:
                    # Convert UptoDate column to proper date format
                    # If it's 0, convert to None (NULL), otherwise convert to date
                    mapped_df[db_col] = pd.to_datetime(
                        mapped_df[db_col], errors="coerce"
                    )
                    # Replace NaT with None for SQL NULL
                    mapped_df[db_col] = mapped_df[db_col].where(
                        pd.notna(mapped_df[db_col]), None
                    )

                # Convert percentage columns from basis points to percentages
                if db_col in ["win_percentage", "place_percentage"] and table_name in [
                    "trainer_stats",
                    "jockey_stats",
                    "horses",
                ]:
                    # Convert from basis points (10000 = 100%) to percentage (100.00)
                    mapped_df[db_col] = mapped_df[db_col] / 100.0

                # Convert horse age to foaled year
                if db_col == "foaled" and table_name == "horses":
                    # Calculate foaled year: current_year - age
                    # Assuming current year is 2025 based on the data
                    current_year = 2025
                    mapped_df[db_col] = current_year - mapped_df[db_col]

                logger.info(f"  {csv_col} -> {db_col}")
            else:
                logger.debug(f"  Column '{csv_col}' not found in CSV")

        logger.info(f"Mapped DataFrame shape: {mapped_df.shape}")
        logger.info(f"   Original columns: {len(df.columns)}")
        logger.info(f"   Mapped columns: {len(mapped_df.columns)}")

        return mapped_df

    def validate_mapping(self, csv_file_path: str, table_name: str) -> Dict:
        """
        Validate column mapping for a specific CSV file and table

        Args:
            csv_file_path: Path to the CSV file
            table_name: Target database table name

        Returns:
            Dictionary with validation results
        """
        try:
            # Read just the header to check columns
            df_sample = pd.read_csv(csv_file_path, nrows=1)
            csv_columns = set(df_sample.columns)

            if table_name not in self.column_mappings:
                return {
                    "status": "error",
                    "message": f"No mapping defined for table: {table_name}",
                    "mappable_columns": 0,
                    "total_csv_columns": len(csv_columns),
                }

            mapping = self.column_mappings[table_name]
            mappable_columns = []
            unmappable_columns = []

            for csv_col in csv_columns:
                if csv_col in mapping:
                    mappable_columns.append(csv_col)
                else:
                    unmappable_columns.append(csv_col)

            return {
                "status": "success",
                "table_name": table_name,
                "csv_file": csv_file_path,
                "total_csv_columns": len(csv_columns),
                "mappable_columns": len(mappable_columns),
                "unmappable_columns": len(unmappable_columns),
                "mapped_column_names": mappable_columns,
                "unmapped_column_names": unmappable_columns,
                "mapping_coverage": len(mappable_columns) / len(csv_columns) * 100,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to validate mapping: {str(e)}",
                "csv_file": csv_file_path,
                "table_name": table_name,
            }

    def get_mappable_columns_count(self, csv_file_path: str, table_name: str) -> int:
        """
        Get count of mappable columns for a CSV file

        Returns:
            Number of columns that can be mapped, or 0 if error
        """
        validation = self.validate_mapping(csv_file_path, table_name)
        return validation.get("mappable_columns", 0)


def test_column_mappings():
    """
    Test function to validate column mappings for all known CSV files
    """
    mapper = ColumnMapper()

    # Define the test file mappings
    test_files = {
        "project_root / 'data' / daily_downloads/results_project_root / 'data' / race_results/race_results.csv": "race_results",
        "project_root / 'data' / daily_downloads/results_project_root / 'data' / horses/horses.csv": "horses",
        "project_root / 'data' / daily_downloads/results_project_root / 'data' / jockeys_stats/jockeys_stats.csv": "jockey_stats",
        "project_root / 'data' / daily_downloads/results_project_root / 'data' / trainers_stats/trainers_stats.csv": "trainer_stats",
        "project_root / 'data' / daily_downloads/cards_project_root / 'data' / races/races.csv": "races_cards",
        "project_root / 'data' / daily_downloads/cards_project_root / 'data' / racecard_details/racecard_details.csv": "racecard_details",
    }

    print("🔍 Testing Column Mappings")
    print("=" * 50)

    for csv_file, table_name in test_files.items():
        print(f"\n📊 {table_name.upper()}")
        print(f"File: {csv_file}")

        result = mapper.validate_mapping(csv_file, table_name)

        if result["status"] == "success":
            coverage = result["mapping_coverage"]
            mappable = result["mappable_columns"]
            total = result["total_csv_columns"]

            print(f"✅ Mapping Coverage: {coverage:.1f}% ({mappable}/{total} columns)")
            print(f"   Mapped columns: {', '.join(result['mapped_column_names'][:5])}")
            if len(result["mapped_column_names"]) > 5:
                print(f"   ... and {len(result['mapped_column_names']) - 5} more")

            if result["unmapped_column_names"]:
                print(f"   Unmapped: {', '.join(result['unmapped_column_names'][:3])}")
                if len(result["unmapped_column_names"]) > 3:
                    print(f"   ... and {len(result['unmapped_column_names']) - 3} more")
        else:
            print(f"❌ Error: {result['message']}")


if __name__ == "__main__":
    test_column_mappings()
