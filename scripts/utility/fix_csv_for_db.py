#!/usr/bin/env python3
"""
Fix CSV files for database import by cleaning numeric columns
"""

import pandas as pd
import numpy as np

# Fix races.csv
print("📊 Fixing races.csv...")
races_df = pd.read_csv("data/daily_downloads/mapped_races.csv")

# Convert float course_id to integer, handling NaN
races_df["course_id"] = (
    pd.to_numeric(races_df["course_id"], errors="coerce").fillna(0).astype(int)
)

# Convert other float columns to integers where they should be integers
numeric_cols = ["ew", "places_ew", "draw", "ew_racecard", "places_ew_racecard"]
for col in numeric_cols:
    if col in races_df.columns:
        # Convert non-numeric values to NaN, then fill with 0 and convert to int
        races_df[col] = (
            pd.to_numeric(races_df[col], errors="coerce").fillna(0).astype(int)
        )

# Save cleaned version
races_df.to_csv("data/daily_downloads/cleaned_races.csv", index=False)
print(f"✅ Cleaned races: {len(races_df)} rows")

# Fix records.csv
print("📊 Fixing records.csv...")
records_df = pd.read_csv("data/daily_downloads/mapped_records.csv")

# Convert record_id to integer if it's a float
if "record_id" in records_df.columns:
    records_df["record_id"] = (
        pd.to_numeric(records_df["record_id"], errors="coerce").fillna(0).astype(int)
    )

# Save cleaned version
records_df.to_csv("data/daily_downloads/cleaned_records.csv", index=False)
print(f"✅ Cleaned records: {len(records_df)} rows")

# Fix horses.csv
print("📊 Fixing horses.csv...")
horses_df = pd.read_csv("data/daily_downloads/mapped_horses.csv")

# Convert horse_id to integer if it's a float
if "horse_id" in horses_df.columns:
    horses_df["horse_id"] = (
        pd.to_numeric(horses_df["horse_id"], errors="coerce").fillna(0).astype(int)
    )

# Save cleaned version
horses_df.to_csv("data/daily_downloads/cleaned_horses.csv", index=False)
print(f"✅ Cleaned horses: {len(horses_df)} rows")

print("🎯 All CSV files cleaned and ready for database import")
