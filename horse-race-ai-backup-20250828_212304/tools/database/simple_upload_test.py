#!/usr/bin/env python3
"""
Simple test script for race card database upload
"""

import asyncio
import asyncpg
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


async def test_database_upload():
    """Test uploading race card data to PostgreSQL"""

    print("🚀 Testing Race Card Database Upload")
    print("=" * 50)

    # Check data files
    cards_data_dir = Path(
        "/home/jc/Documents/Horse-race-ai-v2.03/data/daily_downloads/cards_data"
    )

    files_to_check = {
        "races": cards_data_dir / "races" / "races.csv",
        "horses": cards_data_dir / "horses" / "horses.csv",
        "entries": cards_data_dir / "racecard_details" / "racecard_details.csv",
    }

    print("📁 Checking data files...")
    for name, file_path in files_to_check.items():
        if file_path.exists():
            df = pd.read_csv(file_path)
            print(f"  ✅ {name}: {len(df)} records")
        else:
            print(f"  ❌ {name}: File not found - {file_path}")
            return

    # Connect to database
    print("\n🔗 Connecting to database...")
    try:
        connection_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        pool = await asyncpg.create_pool(connection_string, min_size=1, max_size=3)
        print("  ✅ Database connection established")
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return

    results = {}

    try:
        # 1. Upload race cards
        print("\n📋 Uploading race cards...")
        races_df = pd.read_csv(files_to_check["races"])

        async with pool.acquire() as conn:
            race_count = 0
            for _, row in races_df.iterrows():
                try:
                    # Convert data types
                    race_time = pd.to_datetime(f"{row['Date']} {row['race_time']}")
                    race_date = pd.to_datetime(row["Date"]).date()

                    await conn.execute(
                        """
                        INSERT INTO race_cards (
                            race_id, race_number, race_time, course_id, course,
                            race_type, race_date, race_name, class, age_restriction,
                            distance, surface, prize, runners_racecard, runners
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                        ON CONFLICT (race_id) DO UPDATE SET
                            race_time = EXCLUDED.race_time,
                            updated_at = CURRENT_TIMESTAMP
                    """,
                        int(row["Race_ID"]),
                        int(row.get("race_number", 0)),
                        race_time,
                        int(row.get("course_id", 0)),
                        str(row["Course"]),
                        str(row.get("Race_type", "")),
                        race_date,
                        str(row.get("Race_name", "")),
                        str(row.get("Class", "")),
                        str(row.get("Years", "")),
                        str(row.get("Distance", "")),
                        str(row.get("Surface", "")),
                        str(row.get("Prize", "")),
                        int(row.get("Runners_racecard", 0)),
                        int(row.get("Runners", 0)),
                    )
                    race_count += 1
                except Exception as e:
                    print(f"    ❌ Failed to insert race {row['Race_ID']}: {e}")

        print(f"  ✅ Races uploaded: {race_count}/{len(races_df)}")
        results["races"] = {"uploaded": race_count, "total": len(races_df)}

        # 2. Upload horses
        print("\n🐎 Uploading horses...")
        horses_df = pd.read_csv(files_to_check["horses"])

        async with pool.acquire() as conn:
            horse_count = 0
            for _, row in horses_df.iterrows():
                try:
                    await conn.execute(
                        """
                        INSERT INTO horses (
                            horse_id, name, country, age, color, owner,
                            sire, dam, sex, total_races, wins
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        ON CONFLICT (horse_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            updated_at = CURRENT_TIMESTAMP
                    """,
                        int(row["id"]),
                        str(row.get("name", "")),
                        str(row.get("country", "")),
                        int(row.get("age", 0)),
                        str(row.get("color", "")),
                        str(row.get("owner", "")),
                        str(row.get("sire", "")),
                        str(row.get("dam", "")),
                        str(row.get("sex", "")),
                        float(row.get("Total_races", 0)),
                        float(row.get("Wins", 0)),
                    )
                    horse_count += 1
                except Exception as e:
                    print(f"    ❌ Failed to insert horse {row['id']}: {e}")

        print(f"  ✅ Horses uploaded: {horse_count}/{len(horses_df)}")
        results["horses"] = {"uploaded": horse_count, "total": len(horses_df)}

        # 3. Upload race entries
        print("\n🏇 Uploading race entries...")
        entries_df = pd.read_csv(files_to_check["entries"])

        async with pool.acquire() as conn:
            entry_count = 0
            for _, row in entries_df.iterrows():
                try:
                    await conn.execute(
                        """
                        INSERT INTO race_entries (
                            race_id, horse_id, horse_name, age, draw,
                            jockey, trainer, odds, odds_decimal
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        ON CONFLICT (race_id, horse_id) DO UPDATE SET
                            odds = EXCLUDED.odds,
                            odds_decimal = EXCLUDED.odds_decimal,
                            updated_at = CURRENT_TIMESTAMP
                    """,
                        int(row["race_id"]),
                        int(row["Horse_ID"]),
                        str(row.get("Name", "")),
                        int(row.get("Age", 0)),
                        int(row.get("Draw", 0)),
                        str(row.get("jockey", "")),
                        str(row.get("trainer", "")),
                        str(row.get("odds", "")),
                        float(row.get("odds_decimal", 0)),
                    )
                    entry_count += 1
                except Exception as e:
                    print(f"    ❌ Failed to insert entry: {e}")

        print(f"  ✅ Race entries uploaded: {entry_count}/{len(entries_df)}")
        results["entries"] = {"uploaded": entry_count, "total": len(entries_df)}

        # 4. Verify data
        print("\n🔍 Verifying uploaded data...")
        async with pool.acquire() as conn:
            # Count records in each table
            race_count = await conn.fetchval("SELECT COUNT(*) FROM race_cards")
            horse_count = await conn.fetchval("SELECT COUNT(*) FROM horses")
            entry_count = await conn.fetchval("SELECT COUNT(*) FROM race_entries")

            print(f"  📊 Database contains:")
            print(f"    - {race_count} races")
            print(f"    - {horse_count} horses")
            print(f"    - {entry_count} race entries")

            # Sample today's races
            todays_races = await conn.fetch("SELECT * FROM todays_races LIMIT 5")
            print(f"\n  📅 Today's races (sample):")
            for race in todays_races:
                print(
                    f"    - {race['race_time'].strftime('%H:%M')} {race['course']} - {race['race_name']} ({race['runners']} runners)"
                )

        print("\n✅ Upload test completed successfully!")
        print(f"\n📊 Final Results:")
        print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"\n❌ Upload test failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(test_database_upload())
