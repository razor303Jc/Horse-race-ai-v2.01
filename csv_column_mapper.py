#!/usr/bin/env python3
"""
Column Mapping Solution for Database Upload
===========================================

Maps CSV columns from horseracedatabase.com to our PostgreSQL schema.
Handles the mismatch between downloaded CSV structure and database tables.
"""

import logging
from typing import Dict, List, Optional

import pandas as pd

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
                "id": "horse_id",  # CSV 'id' -> DB 'horse_id' (string field)
                "name": "horse_name",
                "country": "country",
                "age": "foaled",  # We'll calculate birth year from age
                "color": "color",
                "owner": "owner",
                "sire": "sire",
                "dam": "dam",
                "dam_sire": "damsire",  # CSV 'dam_sire' -> DB 'damsire'
                "sex": "sex",
                "uptodate": "uptodate",  # CSV 'uptodate' -> DB 'uptodate'
                # Note: CSV doesn't have trainer/jockey, only race stats
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
                # Note: Database has no 'race_id' field, using available fields
                "race_number": "race_number",
                "race_time": "race_time",
                "Course": "course",  # CSV has 'Course' (capital C)
                "Race_type": "race_type",
                "Date": "date",
                "Race_name": "race_name",
                "Distance": "distance",
                "Surface": "surface",
                "Prize": "prize_money",  # CSV 'Prize' -> DB 'prize_money'
                "Runners": "field_size",  # CSV 'Runners' -> DB 'field_size'
                # Many CSV columns don't have direct database mappings
            },
            "racecard_details": {
                "race_id": "race_id",  # CSV 'race_id' -> DB 'race_id'
                "Draw": "draw",
                "Horse_ID": "horse_name",  # Map to horse_name since DB expects name
                "Name": "horse_name",  # CSV 'Name' also maps to horse_name
                "Age": "horse_age",
                "weight": "horse_weight_kg",
                "jockey": "jockey_name",  # CSV 'jockey' -> DB 'jockey_name'
                "trainer": "trainer_name",  # CSV 'trainer' -> DB 'trainer_name'
                "barrier": "barrier",
                "form": "form",
                "win_odds": "win_odds",
                "place_odds": "place_odds",
                "career_wins": "career_wins",
                "career_runs": "career_runs",
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
            logger.warning(f"No column mapping found for table: {table_name}")
            return pd.DataFrame()

        mapping = self.column_mappings[table_name]
        mapped_df = pd.DataFrame()

        logger.info(f"Mapping columns for {table_name}:")

        for csv_col, db_col in mapping.items():
            if csv_col in df.columns:
                logger.info(f"  {csv_col} -> {db_col}")
                mapped_df[db_col] = df[csv_col].copy()
            else:
                logger.warning(f"  Column {csv_col} not found in CSV")

        # Special handling for horses table date conversion
        if table_name == "horses":
            if "foaled" in mapped_df.columns:
                # Convert age to approximate birth year, then to date
                current_year = 2025  # Using current year as reference

                def age_to_date(age_val):
                    try:
                        if pd.isna(age_val) or age_val == 0:
                            return None
                        age = int(age_val)
                        birth_year = current_year - age
                        # Use January 1st as default birth date
                        return f"{birth_year}-01-01"
                    except (ValueError, TypeError):
                        return None

                logger.info("Converting age values to birth dates...")
                mapped_df["foaled"] = mapped_df["foaled"].apply(age_to_date)

            if "uptodate" in mapped_df.columns:
                # Convert uptodate field (which might be 0 from cleaning) to proper date
                def fix_uptodate(val):
                    try:
                        if pd.isna(val) or val == 0:
                            return "2025-08-09"  # Default to today's date
                        # If it's already a valid date string, keep it
                        if isinstance(val, str) and len(val) == 10:
                            return val
                        return "2025-08-09"
                    except (ValueError, TypeError):
                        return "2025-08-09"

                logger.info("Converting uptodate values to proper dates...")
                mapped_df["uptodate"] = mapped_df["uptodate"].apply(fix_uptodate)

        # Special handling for stats tables with uptodate fields
        if (
            table_name in ["jockey_stats", "trainer_stats"]
            and "uptodate" in mapped_df.columns
        ):

            def fix_uptodate(val):
                try:
                    if pd.isna(val) or val == 0:
                        return "2025-08-09"  # Default to today's date
                    # If it's already a valid date string, keep it
                    if isinstance(val, str) and len(val) == 10:
                        return val
                    return "2025-08-09"
                except (ValueError, TypeError):
                    return "2025-08-09"

            logger.info(
                f"Converting uptodate values to proper dates for {table_name}..."
            )
            mapped_df["uptodate"] = mapped_df["uptodate"].apply(fix_uptodate)

        # Special handling for races_cards table date conversion
        if table_name == "races_cards" and "date" in mapped_df.columns:

            def fix_race_date(val):
                try:
                    if pd.isna(val) or val == 0:
                        return "2025-08-09"  # Default to today's date
                    # If it's already a valid date string, keep it
                    if isinstance(val, str) and len(val) == 10:
                        return val
                    # If it's an integer like 20250810, convert to date format
                    val_str = str(val)
                    if len(val_str) == 8:
                        return f"{val_str[:4]}-{val_str[4:6]}-{val_str[6:8]}"
                    return "2025-08-09"
                except (ValueError, TypeError):
                    return "2025-08-09"

            logger.info(f"Converting date values to proper format for {table_name}...")
            mapped_df["date"] = mapped_df["date"].apply(fix_race_date)

        # Special handling for percentage fields in stats tables
        if table_name in ["jockey_stats", "trainer_stats"]:
            percentage_fields = ["win_percentage", "place_percentage"]
            for field in percentage_fields:
                if field in mapped_df.columns:

                    def convert_percentage(val):
                        try:
                            if pd.isna(val) or val == 0:
                                return 0.00
                            # Convert from basis points (1195) to percentage (11.95)
                            return float(val) / 100.0
                        except (ValueError, TypeError):
                            return 0.00

                    logger.info(
                        f"Converting {field} from basis points to percentages..."
                    )
                    mapped_df[field] = mapped_df[field].apply(convert_percentage)

        logger.info(f"Mapped DataFrame shape: {mapped_df.shape}")
        return mapped_df

    def validate_mapped_data(self, df: pd.DataFrame, table_name: str) -> bool:
        """Validate the mapped DataFrame before database insertion"""
        try:
            if df.empty:
                print(f"❌ Validation failed for {table_name}: DataFrame is empty")
                return False

            # Check for critical columns based on table type
            required_columns = {
                "race_results": ["race_id"],
                "horses": ["horse_name"],  # Database uses horse_name as key
                "jockey_stats": ["jockey_name"],  # Database uses jockey_name as key
                "trainer_stats": ["trainer_name"],  # Database uses trainer_name as key
                "races_cards": ["course"],  # Database needs at least course
                "racecard_details": ["race_id"],
            }

            if table_name in required_columns:
                for col in required_columns[table_name]:
                    if col not in df.columns:
                        print(
                            f"❌ Validation failed for {table_name}: Missing required column {col}"
                        )
                        return False

            print(
                f"✅ Validation passed for {table_name}: {len(df)} rows, {len(df.columns)} columns"
            )
            return True

        except Exception as e:
            print(f"❌ Validation error for {table_name}: {str(e)}")
            return False

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
        "data/daily_downloads/results_data/race_results/race_results.csv": "race_results",
        "data/daily_downloads/results_data/horses/horses.csv": "horses",
        "data/daily_downloads/results_data/jockeys_stats/jockeys_stats.csv": "jockey_stats",
        "data/daily_downloads/results_data/trainers_stats/trainers_stats.csv": "trainer_stats",
        "data/daily_downloads/cards_data/races/races.csv": "races_cards",
        "data/daily_downloads/cards_data/racecard_details/racecard_details.csv": "racecard_details",
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
