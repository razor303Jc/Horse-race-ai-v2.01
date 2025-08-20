#!/usr/bin/env python3
"""
Robust CSV to PostgreSQL uploader with data cleaning
"""

import psycopg2
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5434,
    "database": "horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}


def clean_numeric_value(value, default=0):
    """Convert value to numeric, handling NaN and empty strings"""
    if pd.isna(value) or value == "" or value == "None":
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def clean_float_value(value, default=0.0):
    """Convert value to float, handling NaN and empty strings"""
    if pd.isna(value) or value == "" or value == "None":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def clean_string_value(value, max_length=None):
    """Clean string value, handling NaN"""
    if pd.isna(value) or value == "None":
        return ""
    result = str(value).strip()
    if max_length:
        result = result[:max_length]
    return result


def upload_race_cards_robust():
    """Upload race card data with robust data cleaning"""

    print("🚀 Robust Race Card Database Upload")
    print("=" * 50)

    # Check data files
    base_dir = Path(
        "/home/jc/Documents/Horse-race-ai-v2.03/data/daily_downloads/cards_data"
    )

    files = {
        "races": base_dir / "races" / "races.csv",
        "horses": base_dir / "horses" / "horses.csv",
        "entries": base_dir / "racecard_details" / "racecard_details.csv",
    }

    print("📁 Checking data files...")
    for name, path in files.items():
        if path.exists():
            df = pd.read_csv(path)
            print(f"  ✅ {name}: {len(df)} records")
        else:
            print(f"  ❌ {name}: Missing - {path}")
            return

    # Connect to database
    print("\n🔗 Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("  ✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        return

    results = {}

    try:
        # 1. Upload races with data cleaning
        print("\n📋 Uploading race cards...")
        races_df = pd.read_csv(files["races"])
        race_count = 0
        race_errors = 0

        for _, row in races_df.iterrows():
            try:
                # Clean and convert data with robust handling
                race_time_str = f"{row['Date']} {row['race_time']}"
                race_time = pd.to_datetime(race_time_str)
                race_date = pd.to_datetime(row["Date"]).date()

                # Generate course_id if missing
                course_id = clean_numeric_value(row.get("course_id"))
                if course_id == 0:
                    # Generate a hash-based course_id from course name
                    course_id = abs(hash(str(row["Course"]))) % 10000

                cur.execute(
                    """
                    INSERT INTO race_cards (
                        race_id, race_number, race_time, course_id, course,
                        race_type, race_date, race_name, class, age_restriction,
                        distance, surface, prize, runners_racecard, runners
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (race_id) DO UPDATE SET
                        race_time = EXCLUDED.race_time,
                        updated_at = CURRENT_TIMESTAMP
                """,
                    (
                        int(row["Race_ID"]),
                        clean_numeric_value(row.get("race_number"), 1),
                        race_time,
                        course_id,
                        clean_string_value(row["Course"], 100),
                        clean_string_value(row.get("Race_type"), 50),
                        race_date,
                        clean_string_value(row.get("Race_name"), 200),
                        clean_string_value(row.get("Class"), 20),
                        clean_string_value(row.get("Years"), 20),
                        clean_string_value(row.get("Distance"), 50),
                        clean_string_value(row.get("Surface"), 50),
                        clean_string_value(row.get("Prize"), 50),
                        clean_numeric_value(row.get("Runners_racecard")),
                        clean_numeric_value(row.get("Runners")),
                    ),
                )
                race_count += 1
            except Exception as e:
                print(f"    ❌ Race {row['Race_ID']}: {e}")
                race_errors += 1

        conn.commit()
        print(
            f"  ✅ Races: {race_count}/{len(races_df)} uploaded ({race_errors} errors)"
        )
        results["races"] = {
            "uploaded": race_count,
            "total": len(races_df),
            "errors": race_errors,
        }

        # 2. Upload horses with data cleaning
        print("\n🐎 Uploading horses...")
        horses_df = pd.read_csv(files["horses"])
        horse_count = 0
        horse_errors = 0

        for _, row in horses_df.iterrows():
            try:
                cur.execute(
                    """
                    INSERT INTO horses (
                        horse_id, name, country, age, color, owner,
                        sire, dam, sex, total_races, wins
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (horse_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        updated_at = CURRENT_TIMESTAMP  
                """,
                    (
                        int(row["id"]),
                        clean_string_value(row.get("name"), 100),
                        clean_string_value(row.get("country"), 10),
                        clean_numeric_value(row.get("age")),
                        clean_string_value(row.get("color"), 30),
                        clean_string_value(row.get("owner"), 200),
                        clean_string_value(row.get("sire"), 100),
                        clean_string_value(row.get("dam"), 100),
                        clean_string_value(row.get("sex"), 20),
                        clean_float_value(row.get("Total_races")),
                        clean_float_value(row.get("Wins")),
                    ),
                )
                horse_count += 1
            except Exception as e:
                print(f"    ❌ Horse {row['id']}: {e}")
                horse_errors += 1

        conn.commit()
        print(
            f"  ✅ Horses: {horse_count}/{len(horses_df)} uploaded ({horse_errors} errors)"
        )
        results["horses"] = {
            "uploaded": horse_count,
            "total": len(horses_df),
            "errors": horse_errors,
        }

        # 3. Upload race entries with data cleaning
        print("\n🏇 Uploading race entries...")
        entries_df = pd.read_csv(files["entries"])
        entry_count = 0
        entry_errors = 0

        for _, row in entries_df.iterrows():
            try:
                cur.execute(
                    """
                    INSERT INTO race_entries (
                        race_id, horse_id, horse_name, age, draw,
                        jockey, trainer, odds, odds_decimal
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (race_id, horse_id) DO UPDATE SET
                        odds = EXCLUDED.odds,
                        odds_decimal = EXCLUDED.odds_decimal,
                        updated_at = CURRENT_TIMESTAMP
                """,
                    (
                        int(row["race_id"]),
                        int(row["Horse_ID"]),
                        clean_string_value(row.get("Name"), 100),
                        clean_numeric_value(row.get("Age")),
                        clean_numeric_value(row.get("Draw")),
                        clean_string_value(row.get("jockey"), 100),
                        clean_string_value(row.get("trainer"), 100),
                        clean_string_value(row.get("odds"), 20),
                        clean_float_value(row.get("odds_decimal")),
                    ),
                )
                entry_count += 1
            except Exception as e:
                print(
                    f"    ❌ Entry race_id={row['race_id']}, horse_id={row['Horse_ID']}: {e}"
                )
                entry_errors += 1

        conn.commit()
        print(
            f"  ✅ Entries: {entry_count}/{len(entries_df)} uploaded ({entry_errors} errors)"
        )
        results["entries"] = {
            "uploaded": entry_count,
            "total": len(entries_df),
            "errors": entry_errors,
        }

        # 4. Verify data and show sample
        print("\n🔍 Verifying data...")
        cur.execute("SELECT COUNT(*) FROM race_cards")
        race_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM horses")
        horse_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM race_entries")
        entry_count = cur.fetchone()[0]

        print(f"  📊 Database contains:")
        print(f"    - {race_count} races")
        print(f"    - {horse_count} horses")
        print(f"    - {entry_count} race entries")

        # Sample today's races with entries
        cur.execute(
            """
            SELECT rc.race_time, rc.course, rc.race_name, rc.runners,
                   COUNT(re.entry_id) as entries_count
            FROM race_cards rc
            LEFT JOIN race_entries re ON rc.race_id = re.race_id
            WHERE rc.race_date = CURRENT_DATE
            GROUP BY rc.race_id, rc.race_time, rc.course, rc.race_name, rc.runners
            ORDER BY rc.race_time 
            LIMIT 5
        """
        )
        sample_races = cur.fetchall()

        print(f"\n  📅 Sample races with entries:")
        for race in sample_races:
            race_time, course, race_name, runners, entries = race
            print(f"    - {race_time.strftime('%H:%M')} {course} - {race_name}")
            print(f"      Expected: {runners} runners, Actual entries: {entries}")

        # Data quality summary
        total_uploaded = sum(
            r.get("uploaded", 0) for r in results.values() if isinstance(r, dict)
        )
        total_records = sum(
            r.get("total", 0) for r in results.values() if isinstance(r, dict)
        )
        total_errors = sum(
            r.get("errors", 0) for r in results.values() if isinstance(r, dict)
        )

        print(f"\n📊 Upload Summary:")
        print(f"  Total Records: {total_records}")
        print(f"  Successfully Uploaded: {total_uploaded}")
        print(f"  Errors: {total_errors}")
        print(f"  Success Rate: {(total_uploaded/total_records*100):.1f}%")

        print("\n✅ Robust upload completed!")
        print(f"\n📋 Detailed Results:")
        print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        conn.rollback()
        import traceback

        traceback.print_exc()

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    upload_race_cards_robust()
