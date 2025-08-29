#!/usr/bin/env python3
"""
🔧 Quick Column Name Fixer
=========================

Immediate solution to fix column names in current CSV files to match database schema.
This is a temporary fix while we develop the comprehensive intelligent mapper.
"""

import pandas as pd
from pathlib import Path

# Exact column mappings for each table based on database schema
COLUMN_MAPPINGS = {
    "races": {
        "Race_ID": "race_id",
        "race_number": "race_number",
        "race_time": "race_time",
        "course_id": "course_id",
        "Course": "course",
        "Race_type": "race_type",
        "Date": "date",
        "Race_name": "race_name",
        "Class": "class",
        "Years": "years",
        "Distance": "distance",
        "Surface": "surface",
        "Prize": "prize",
        "Runners_racecard": "runners_racecard",
        "Runners": "runners",
        "Draw": "draw",
        "EW_racecard": "ew_racecard",
        "EW": "ew",
        "Places_EW_racecard": "places_ew_racecard",
        "Places_EW": "places_ew",
    },
    "horses": {
        "id": "horse_id",
        "name": "horse_name",
        "age": "age",
        "sex": "sex",
        "color": "color",
        "sire": "sire",
        "dam": "dam",
        "owner": "owner",
        # Skip columns not in DB: uptodate, state, race_id_last_race, etc.
    },
    "jockeys_stats": {
        "Jockey_ID": "jockey_id",
        "Name": "jockey_name",
        "Wins": "wins",
        "Total_races": "runs",
        "Percentage_wins": "win_rate",
        "Percentage_placed": "place_rate",
        # Skip other columns not in DB
    },
    "trainers_stats": {
        "Trainer_ID": "trainer_id",
        "Name": "trainer_name",
        "Wins": "wins",
        "Total_races": "runs",
        "Percentage_wins": "win_rate",
        "Percentage_placed": "place_rate",
        # Skip other columns not in DB
    },
    "racecard_details": {
        "race_id": "race_id",
        "Name": "horse_name",
        "jockey": "jockey",
        "trainer": "trainer",
        "horse_number": "number",
        "odds_decimal": "odds",
        "weight": "weight",
        "Age": "age",
        # Combine other fields into 'extra' field
        "form_fields": [
            "Draw",
            "Horse_ID",
            "Country",
            "weight_uk",
            "gears",
            "Horse_rate",
            "fav",
            "odds",
            "Timeform_comments",
        ],
    },
}


def fix_csv_columns(input_file: Path, output_file: Path, table_name: str):
    """Fix column names in CSV file to match database schema"""

    print(f"\n🔧 Fixing {input_file.name} for {table_name} table...")

    try:
        # Load CSV
        df = pd.read_csv(input_file)
        print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")

        if table_name not in COLUMN_MAPPINGS:
            print(f"❌ No mapping defined for table: {table_name}")
            return False

        mapping = COLUMN_MAPPINGS[table_name]
        new_df = pd.DataFrame()

        # Apply column mappings
        for old_col, new_col in mapping.items():
            if old_col == "form_fields":
                # Special handling for racecard_details extra field
                extra_data = []
                for _, row in df.iterrows():
                    extra_info = {}
                    for field in new_col:  # new_col contains the list of fields
                        if field in df.columns:
                            extra_info[field] = row[field]
                    extra_data.append(str(extra_info) if extra_info else "")
                new_df["extra"] = extra_data
                continue

            if old_col in df.columns:
                new_df[new_col] = df[old_col]
                print(f"  ✅ {old_col} → {new_col}")
            else:
                print(f"  ⚠️ Column '{old_col}' not found in CSV")

        # Special handling for percentage fields (remove % and convert to decimal)
        for col in new_df.columns:
            if "rate" in col and new_df[col].dtype == "object":
                # Convert percentage strings to decimal
                new_df[col] = (
                    new_df[col].astype(str).str.replace("%", "").replace("", "0")
                )
                new_df[col] = pd.to_numeric(new_df[col], errors="coerce").fillna(0)

        # Fill NaN values appropriately
        for col in new_df.columns:
            if new_df[col].dtype in ["object"]:
                new_df[col] = new_df[col].fillna("")
            else:
                new_df[col] = new_df[col].fillna(0)

        # Save fixed CSV
        output_file.parent.mkdir(exist_ok=True)
        new_df.to_csv(output_file, index=False)

        print(f"💾 Saved fixed CSV: {output_file}")
        print(
            f"📊 Output: {len(new_df)} rows, {len(new_df.columns)} columns: {list(new_df.columns)}"
        )

        return True

    except Exception as e:
        print(f"❌ Failed to fix {input_file}: {e}")
        return False


def main():
    """Fix all current CSV files"""

    print("🔧 Quick Column Name Fixer")
    print("=" * 50)

    base_dir = Path("/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads")
    output_dir = base_dir / "fixed"

    # Files to fix
    files_to_fix = [
        ("mapped_races.csv", "races"),
        ("mapped_horses.csv", "horses"),
        ("mapped_jockeys_stats.csv", "jockeys_stats"),
        ("mapped_trainers_stats.csv", "trainers_stats"),
        ("mapped_racecard_details.csv", "racecard_details"),
    ]

    success_count = 0

    for filename, table_name in files_to_fix:
        input_file = base_dir / filename
        output_file = output_dir / f"fixed_{filename}"

        if input_file.exists():
            if fix_csv_columns(input_file, output_file, table_name):
                success_count += 1
        else:
            print(f"⚠️ File not found: {input_file}")

    print(f"\n📊 SUMMARY: {success_count}/{len(files_to_fix)} files fixed successfully")

    if success_count == len(files_to_fix):
        print("🎉 All files fixed! Ready for database upload.")
        print(f"📁 Fixed files saved in: {output_dir}")
    else:
        print("⚠️ Some files failed to process")


if __name__ == "__main__":
    main()
