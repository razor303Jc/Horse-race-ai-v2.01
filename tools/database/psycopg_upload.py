#!/usr/bin/env python3
"""
Simple CSV to PostgreSQL uploader using psycopg2
"""

import psycopg2
import pandas as pd
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


def upload_race_cards():
    """Upload race card data to PostgreSQL using psycopg2"""

    print("🚀 Race Card Database Upload")
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
        # 1. Upload races
        print("\n📋 Uploading race cards...")
        races_df = pd.read_csv(files["races"])
        race_count = 0

        for _, row in races_df.iterrows():
            try:
                # Clean and convert data
                race_time = pd.to_datetime(f"{row['Date']} {row['race_time']}")
                race_date = pd.to_datetime(row["Date"]).date()

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
                        int(row.get("race_number", 0)),
                        race_time,
                        int(row.get("course_id", 0)),
                        str(row["Course"])[:100],
                        str(row.get("Race_type", ""))[:50],
                        race_date,
                        str(row.get("Race_name", ""))[:200],
                        str(row.get("Class", ""))[:20],
                        str(row.get("Years", ""))[:20],
                        str(row.get("Distance", ""))[:50],
                        str(row.get("Surface", ""))[:50],
                        str(row.get("Prize", ""))[:50],
                        int(row.get("Runners_racecard", 0)),
                        int(row.get("Runners", 0)),
                    ),
                )
                race_count += 1
            except Exception as e:
                print(f"    ❌ Race {row['Race_ID']}: {e}")

        conn.commit()
        print(f"  ✅ Races: {race_count}/{len(races_df)} uploaded")
        results["races"] = {"uploaded": race_count, "total": len(races_df)}

        # 2. Upload horses
        print("\n🐎 Uploading horses...")
        horses_df = pd.read_csv(files["horses"])
        horse_count = 0

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
                        str(row.get("name", ""))[:100],
                        str(row.get("country", ""))[:10],
                        int(row.get("age", 0)),
                        str(row.get("color", ""))[:30],
                        str(row.get("owner", ""))[:200],
                        str(row.get("sire", ""))[:100],
                        str(row.get("dam", ""))[:100],
                        str(row.get("sex", ""))[:20],
                        (
                            float(row.get("Total_races", 0))
                            if pd.notna(row.get("Total_races"))
                            else 0
                        ),
                        float(row.get("Wins", 0)) if pd.notna(row.get("Wins")) else 0,
                    ),
                )
                horse_count += 1
            except Exception as e:
                print(f"    ❌ Horse {row['id']}: {e}")

        conn.commit()
        print(f"  ✅ Horses: {horse_count}/{len(horses_df)} uploaded")
        results["horses"] = {"uploaded": horse_count, "total": len(horses_df)}

        # 3. Upload race entries
        print("\n🏇 Uploading race entries...")
        entries_df = pd.read_csv(files["entries"])
        entry_count = 0

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
                        str(row.get("Name", ""))[:100],
                        int(row.get("Age", 0)),
                        int(row.get("Draw", 0)),
                        str(row.get("jockey", ""))[:100],
                        str(row.get("trainer", ""))[:100],
                        str(row.get("odds", ""))[:20],
                        (
                            float(row.get("odds_decimal", 0))
                            if pd.notna(row.get("odds_decimal"))
                            else 0
                        ),
                    ),
                )
                entry_count += 1
            except Exception as e:
                print(f"    ❌ Entry: {e}")

        conn.commit()
        print(f"  ✅ Entries: {entry_count}/{len(entries_df)} uploaded")
        results["entries"] = {"uploaded": entry_count, "total": len(entries_df)}

        # 4. Verify data
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

        # Sample today's races
        cur.execute(
            "SELECT race_time, course, race_name, runners FROM race_cards ORDER BY race_time LIMIT 5"
        )
        sample_races = cur.fetchall()

        print(f"\n  📅 Sample races:")
        for race in sample_races:
            race_time, course, race_name, runners = race
            print(
                f"    - {race_time.strftime('%H:%M')} {course} - {race_name} ({runners} runners)"
            )

        print("\n✅ Upload completed successfully!")
        print(f"\n📊 Results Summary:")
        print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        conn.rollback()

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    upload_race_cards()
