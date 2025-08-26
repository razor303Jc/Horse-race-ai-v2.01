#!/usr/bin/env python3
"""
CSV Column Mapping Configuration
Defines how to map CSV columns to database columns
"""

# Column mappings for each CSV file type
CSV_COLUMN_MAPPINGS = {
    "horses.csv": {
        # Direct mappings (CSV column -> DB column)
        "id": "id",
        "uptodate": "uptodate",
        "state": "state",
        "race_id_last_race": "race_id_last_race",
        "date_last_race": "date_last_race",
        "name": "name",
        "country": "country",
        "age": "age",
        "color": "color",
        "owner": "owner",
        "sire": "sire",
        "dam": "dam",
        "dam_sire": "dam_sire",
        "sex": "sex",
        "Total_races": "total_races",  # Case conversion
        "Wins": "wins",  # Case conversion
        "Percentage_wins": "percentage_wins",  # Case conversion
        "placed": "placed",
        "Percentage_placed": "percentage_placed",  # Case conversion
        "Flat_AW_races": "flat_aw_races",  # Case conversion
        "Flat_AW_wins": "flat_aw_wins",  # Case conversion
        "Flat_AW_rate": "flat_aw_rate",  # Case conversion
        "Flat_AW_placed": "flat_aw_placed",  # Case conversion
        "Flat_AW_placed_rate": "flat_aw_placed_rate",  # Case conversion
        "Flat_Turf_races": "flat_turf_races",  # Case conversion
        "Flat_Turf_wins": "flat_turf_wins",  # Case conversion
        "Flat_Turf_rate": "flat_turf_rate",  # Case conversion
        "Flat_Turf_placed": "flat_turf_placed",  # Case conversion
        "Flat_Turf_placed_rate": "flat_turf_placed_rate",  # Case conversion
        "Chase_races": "chase_races",  # Case conversion
        "Chase_wins": "chase_wins",  # Case conversion
        "Chase_rate": "chase_rate",  # Case conversion
        "Chase_placed": "chase_placed",  # Case conversion
        "Chase_placed_rate": "chase_placed_rate",  # Case conversion
        "Hurdle_races": "hurdle_races",  # Case conversion
        "Hurdle_wins": "hurdle_wins",  # Case conversion
        "Hurdle_rate": "hurdle_rate",  # Case conversion
        "Hurdle_placed": "hurdle_placed",  # Case conversion
        "Hurdle_placed_rate": "hurdle_placed_rate",  # Case conversion
    },
    "races.csv": {
        "Race_ID": "race_id",  # Case conversion
        "race_number": "race_number",
        "race_time": "race_time",
        "course_id": "course_id",
        "Course": "course",  # Case conversion
        "Race_type": "race_type",  # Case conversion
        "Date": "date",  # Case conversion
        "Race_name": "race_name",  # Case conversion
        "Class": "class",  # Case conversion (reserved word)
        "Years": "years",  # Case conversion
        "Distance": "distance",  # Case conversion
        "Surface": "surface",  # Case conversion
        "Prize": "prize",  # Case conversion
        "Runners_racecard": "runners_racecard",  # Case conversion
        "Runners": "runners",  # Case conversion
        "Draw": "draw",  # Case conversion
        "EW_racecard": "ew_racecard",  # Case conversion
        "EW": "ew",  # Case conversion
        "Places_EW_racecard": "places_ew_racecard",  # Case conversion
        "Places_EW": "places_ew",  # Case conversion
    },
    "racecard_details.csv": {
        "id": "id",
        "race_id": "race_id",
        "horse_number": "horse_number",
        "Draw": "draw",  # Case conversion
        "Horse_ID": "horse_id",  # Case conversion
        "Country": "country",  # Case conversion
        "Name": "name",  # Case conversion
        "Age": "age",  # Case conversion
        "weight_uk": "weight_uk",
        "weight": "weight",
        "gears": "gears",
        "Horse_rate": "horse_rate",  # Case conversion
        "jockey_ID": "jockey_id",  # Case conversion
        "jockey": "jockey",
        "trainer_ID": "trainer_id",  # Case conversion
        "trainer": "trainer",
        "fav": "fav",
        "odds": "odds",
        "odds_decimal": "odds_decimal",
        "Timeform_comments": "timeform_comments",  # Case conversion
    },
    "records.csv": {
        "ID": "id",  # Case conversion
        "Race_ID": "race_id",  # Case conversion
        "Horse_number": "horse_number",  # Case conversion
        "Place": "place",  # Case conversion
        "Draw": "draw",  # Case conversion
        "Horse_ID": "horse_id",  # Case conversion
        "Country": "country",  # Case conversion
        "Name": "name",  # Case conversion
        "Age": "age",  # Case conversion
        "weight_uk": "weight_uk",
        "weight": "weight",
        "gears": "gears",
        "Horse_rate": "horse_rate",  # Case conversion
        "jockey_ID": "jockey_id",  # Case conversion
        "jockey": "jockey",
        "trainer_ID": "trainer_id",  # Case conversion
        "trainer": "trainer",
        "fav": "fav",
        "SP": "sp",  # Case conversion
        "Distance_btn": "distance_btn",  # Case conversion
        "Distance_btn_total": "distance_btn_total",  # Case conversion
        "distance_sec_1": "distance_sec_1",
        "sectional_time_1": "sectional_time_1",
        "distance_sec_2": "distance_sec_2",
        "sectional_time_2": "sectional_time_2",
        "distance_sec_3": "distance_sec_3",
        "sectional_time_3": "sectional_time_3",
        "distance_sec_4": "distance_sec_4",
        "sectional_time_4": "sectional_time_4",
        "distance_sec_5": "distance_sec_5",
        "sectional_time_5": "sectional_time_5",
        "distance_sec_6": "distance_sec_6",
        "sectional_time_6": "sectional_time_6",
        "distance_sec_7": "distance_sec_7",
        "sectional_time_7": "sectional_time_7",
        "distance_sec_8": "distance_sec_8",
        "sectional_time_8": "sectional_time_8",
        "distance_sec_9": "distance_sec_9",
        "sectional_time_9": "sectional_time_9",
        "distance_sec_10": "distance_sec_10",
        "sectional_time_10": "sectional_time_10",
        "distance_sec_11": "distance_sec_11",
        "sectional_time_11": "sectional_time_11",
        "distance_sec_12": "distance_sec_12",
        "sectional_time_12": "sectional_time_12",
        "distance_sec_13": "distance_sec_13",
        "sectional_time_13": "sectional_time_13",
        "distance_sec_14": "distance_sec_14",
        "sectional_time_14": "sectional_time_14",
        "distance_sec_15": "distance_sec_15",
        "sectional_time_15": "sectional_time_15",
        "distance_sec_16": "distance_sec_16",
        "sectional_time_16": "sectional_time_16",
        "distance_sec_17": "distance_sec_17",
        "sectional_time_17": "sectional_time_17",
        "distance_sec_18": "distance_sec_18",
        "sectional_time_18": "sectional_time_18",
        "finish_time": "finish_time",
        "distance_speed_early_race": "distance_speed_early_race",
        "speed_achieved_early_race": "speed_achieved_early_race",
        "distance_speed_mid_race": "distance_speed_mid_race",
        "speed_achieved_mid_race": "speed_achieved_mid_race",
        "distance_speed_finish_race": "distance_speed_finish_race",
        "speed_achieved_finish_race": "speed_achieved_finish_race",
    },
    "results_races.csv": {
        "Race_ID": "race_id",  # Case conversion
        "race_number": "race_number",
        "race_time": "race_time",
        "course_id": "course_id",
        "Course": "course",  # Case conversion
        "Race_type": "race_type",  # Case conversion
        "Date": "date",  # Case conversion
        "Race_name": "race_name",  # Case conversion
        "Class": "class",  # Case conversion
        "Years": "years",  # Case conversion
        "Distance": "distance",  # Case conversion
        "Surface": "surface",  # Case conversion
        "Prize": "prize",  # Case conversion
        "Runners_racecard": "runners_racecard",  # Case conversion
        "Runners": "runners",  # Case conversion
        "Draw": "draw",  # Case conversion
        "EW_racecard": "ew_racecard",  # Case conversion
        "EW": "ew",  # Case conversion
        "Places_EW_racecard": "places_ew_racecard",  # Case conversion
        "Places_EW": "places_ew",  # Case conversion
    },
    "jockeys_stats.csv": {
        "Jockey_ID": "jockey_id",  # Case conversion
        "Name": "jockey_name",  # Case conversion
        "Total_races": "runs",  # Case conversion and field name change
        "Wins": "wins",  # Case conversion
        "Percentage_wins": "win_rate",  # Case conversion, will need special handling for %
        "Percentage_placed": "place_rate",  # Case conversion, will need special handling for %
    },
    "trainers_stats.csv": {
        "Trainer_ID": "trainer_id",  # Case conversion
        "Name": "trainer_name",  # Case conversion
        "Total_races": "runs",  # Case conversion and field name change
        "Wins": "wins",  # Case conversion
        "Percentage_wins": "win_rate",  # Case conversion, will need special handling for %
        "Percentage_placed": "place_rate",  # Case conversion, will need special handling for %
    },
    "results_horses.csv": {
        # Simplified mapping to match results database horses table structure
        "id": "horse_id",  # Map to horse_id instead of id
        "name": "horse_name",  # Map to horse_name instead of name
        "age": "age",
        "sex": "sex",
        "color": "color",
        "sire": "sire",
        "dam": "dam",
        "owner": "owner",
        # Note: breeder field is not in CSV, will be NULL
        # Note: created_at is auto-generated
    },
}

# Database and table mapping for each file type
FILE_DATABASE_MAPPING = {
    "horses.csv": {"database": "cards_horse_racing_db", "table": "horses"},
    "races.csv": {"database": "cards_horse_racing_db", "table": "races"},
    "racecard_details.csv": {
        "database": "cards_horse_racing_db",
        "table": "racecard_details",
    },
    "records.csv": {
        "database": "results_horse_racing_db",
        "table": "records",
    },
    "results_races.csv": {
        "database": "results_horse_racing_db",
        "table": "races",
    },
    "jockeys_stats.csv": {
        "database": "results_horse_racing_db",
        "table": "jockeys_stats",
    },
    "trainers_stats.csv": {
        "database": "results_horse_racing_db",
        "table": "trainers_stats",
    },
    "results_horses.csv": {
        "database": "results_horse_racing_db",
        "table": "horses",
    },
}

# Data cleaning rules for special values
DATA_CLEANING_RULES = {
    # Replace dash/hyphen with appropriate values based on data type
    "dash_replacements": {
        "numeric": None,
        "text": "",
        "percentage": "0%",
    },
    # Percentage fields (remove % and convert to decimal)
    "percentage_fields": [
        "percentage_wins",
        "percentage_placed",
        "flat_aw_rate",
        "flat_aw_placed_rate",
        "flat_turf_rate",
        "flat_turf_placed_rate",
        "chase_rate",
        "chase_placed_rate",
        "hurdle_rate",
        "hurdle_placed_rate",
    ],
    # Integer fields that need empty string to NULL conversion
    "integer_fields": [
        "id",
        "race_id",
        "horse_id",
        "horse_number",
        "draw",
        "age",
        "horse_rate",
        "jockey_id",
        "trainer_id",
        "place",
        "total_races",
        "wins",
        "placed",
        "flat_aw_races",
        "flat_aw_wins",
        "flat_aw_placed",
        "flat_turf_races",
        "flat_turf_wins",
        "flat_turf_placed",
        "chase_races",
        "chase_wins",
        "chase_placed",
        "hurdle_races",
        "hurdle_wins",
        "hurdle_placed",
    ],
    # Weight field conversion (e.g., "9-7" -> standardized format)
    "weight_fields": ["weight_uk"],
    # Distance field conversion (e.g., "2m 2f 60y" -> standardized format)
    "distance_fields": ["distance"],
    # Prize field cleaning (remove currency symbols)
    "prize_fields": ["prize"],
}


def get_column_mapping(csv_filename):
    """Get column mapping for a specific CSV file"""
    return CSV_COLUMN_MAPPINGS.get(csv_filename, {})


def get_database_mapping(csv_filename):
    """Get database and table for a specific CSV file"""
    return FILE_DATABASE_MAPPING.get(csv_filename, None)


def get_cleaning_rules():
    """Get data cleaning rules"""
    return DATA_CLEANING_RULES


def print_mapping_summary():
    """Print summary of all mappings"""
    print("🗂️  CSV FILE MAPPINGS SUMMARY")
    print("=" * 50)

    for csv_file, db_info in FILE_DATABASE_MAPPING.items():
        print(f"\n📄 {csv_file}")
        print(f"   → {db_info['database']}.{db_info['table']}")

        column_mapping = CSV_COLUMN_MAPPINGS.get(csv_file, {})
        print(f"   Columns: {len(column_mapping)} mapped")

        # Show first few mappings as examples
        for i, (csv_col, db_col) in enumerate(list(column_mapping.items())[:3]):
            if csv_col != db_col:
                print(f"     • {csv_col} → {db_col}")
            else:
                print(f"     • {csv_col} (exact match)")

        if len(column_mapping) > 3:
            print(f"     ... and {len(column_mapping) - 3} more")


if __name__ == "__main__":
    print_mapping_summary()
