#!/usr/bin/env python3
"""
Create database-compatible CSV files with exact column matching
"""

import pandas as pd


def clean_weight(weight_str):
    """Convert UK weight format from dashes to dots"""
    if pd.isna(weight_str) or weight_str == "":
        return None
    try:
        # Convert UK format like "10-2" to "10.2"
        if "-" in str(weight_str):
            return str(weight_str).replace("-", ".")
        return str(weight_str)
    except:
        return None


print("📊 Creating database-compatible records.csv...")
records_df = pd.read_csv("data/daily_downloads/cleaned_records.csv")

# Include weight_uk column now that we can handle the format
columns_to_import = [
    "record_id",
    "race_id",
    "position",
    "horse",
    "age",
    "weight",
    "jockey",
    "trainer",
    "or_rating",
    "fav",
    "sp",
    "extra",
]

# Create subset with only available columns
available_columns = [col for col in columns_to_import if col in records_df.columns]
db_records = records_df[available_columns].copy()

# Clean weight column if present
if "weight" in db_records.columns:
    db_records["weight"] = db_records["weight"].apply(clean_weight)

# Rename columns to match database schema
db_records = db_records.rename(columns={"extra": "gears"})

# Fix numeric columns that should be integers
integer_cols = ["position", "age", "or_rating", "fav"]
for col in integer_cols:
    if col in db_records.columns:
        db_records[col] = (
            pd.to_numeric(db_records[col], errors="coerce").fillna(0).astype(int)
        )

# Save database-ready version
db_records.to_csv("data/daily_downloads/db_records.csv", index=False)
print(
    f"✅ Created db_records.csv: {len(db_records)} rows, columns: {list(db_records.columns)}"
)

print("📊 Creating database-compatible horses.csv...")
horses_df = pd.read_csv("data/daily_downloads/cleaned_horses.csv")

# Create database-ready horses CSV
horses_df.to_csv("data/daily_downloads/db_horses.csv", index=False)
print(
    f"✅ Created db_horses.csv: {len(horses_df)} rows, columns: {list(horses_df.columns)}"
)
