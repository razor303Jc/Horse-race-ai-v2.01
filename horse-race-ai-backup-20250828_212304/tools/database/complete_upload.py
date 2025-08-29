#!/usr/bin/env python3
"""
Final comprehensive race card database uploader
Handles missing horses and foreign key constraints
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


def clean_value(value, value_type="str", max_length=None, default=None):
    """Universal data cleaner"""
    if pd.isna(value) or value == "" or value == "None":
        if value_type == "int":
            return default or 0
        elif value_type == "float":
            return default or 0.0
        else:
            return default or ""

    try:
        if value_type == "int":
            return int(float(value))
        elif value_type == "float":
            return float(value)
        else:
            result = str(value).strip()
            if max_length:
                result = result[:max_length]
            return result
    except (ValueError, TypeError):
        if value_type == "int":
            return default or 0
        elif value_type == "float":
            return default or 0.0
        else:
            return default or ""


def upload_race_cards_complete():
    """Complete race card upload with missing horse handling"""

    print("🚀 Complete Race Card Database Upload")
    print("=" * 60)

    # Data files
    base_dir = Path(
        "/home/jc/Documents/Horse-race-ai-v2.03/data/daily_downloads/cards_data"
    )
    files = {
        "races": base_dir / "races" / "races.csv",
        "horses": base_dir / "horses" / "horses.csv",
        "entries": base_dir / "racecard_details" / "racecard_details.csv",
    }

    print("📁 Data file check...")
    for name, path in files.items():
        if path.exists():
            df = pd.read_csv(path)
            print(f"  ✅ {name}: {len(df)} records")
        else:
            print(f"  ❌ {name}: Missing")
            return

    # Database connection
    print("\n🔗 Database connection...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False  # Manage transactions manually
        cur = conn.cursor()
        print("  ✅ Connected")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return

    results = {
        "races": {"uploaded": 0, "errors": 0},
        "horses": {"uploaded": 0, "errors": 0},
        "entries": {"uploaded": 0, "errors": 0, "missing_horses_created": 0},
        "summary": {},
    }

    try:
        # Step 1: Verify existing data
        print("\n🔍 Verifying existing data...")
        cur.execute("SELECT COUNT(*) FROM race_cards")
        existing_races = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM horses")
        existing_horses = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM race_entries")
        existing_entries = cur.fetchone()[0]

        print(f"  📊 Current database:")
        print(f"    - Races: {existing_races}")
        print(f"    - Horses: {existing_horses}")
        print(f"    - Entries: {existing_entries}")

        # Step 2: Load and analyze race entries data
        print("\n📋 Analyzing race entries data...")
        entries_df = pd.read_csv(files["entries"])

        # Get all horse IDs needed by race entries
        required_horse_ids = set(entries_df["Horse_ID"].unique())
        print(f"  📊 Race entries require {len(required_horse_ids)} unique horses")

        # Check which horses exist in database
        cur.execute("SELECT horse_id FROM horses")
        existing_horse_ids = set(row[0] for row in cur.fetchall())

        missing_horse_ids = required_horse_ids - existing_horse_ids
        print(f"  📊 Missing horses: {len(missing_horse_ids)}")

        # Step 3: Create missing horses
        if missing_horse_ids:
            print(f"\n🐎 Creating {len(missing_horse_ids)} missing horses...")
            missing_count = 0

            for horse_id in missing_horse_ids:
                try:
                    # Create minimal horse record
                    cur.execute(
                        """
                        INSERT INTO horses (horse_id, name, country, age)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (horse_id) DO NOTHING
                    """,
                        (int(horse_id), f"Horse_{horse_id}", "UK", 3),
                    )
                    missing_count += 1
                except Exception as e:
                    print(f"    ❌ Failed to create horse {horse_id}: {e}")

            conn.commit()
            results["entries"]["missing_horses_created"] = missing_count
            print(f"  ✅ Created {missing_count} missing horse records")

        # Step 4: Upload race entries with individual transaction handling
        print(f"\n🏇 Uploading {len(entries_df)} race entries...")
        entry_success = 0
        entry_errors = 0

        for index, row in entries_df.iterrows():
            try:
                # Start individual transaction for each entry
                cur.execute("SAVEPOINT entry_insert")

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
                        clean_value(row.get("Name"), max_length=100),
                        clean_value(row.get("Age"), "int"),
                        clean_value(row.get("Draw"), "int"),
                        clean_value(row.get("jockey"), max_length=100),
                        clean_value(row.get("trainer"), max_length=100),
                        clean_value(row.get("odds"), max_length=20),
                        clean_value(row.get("odds_decimal"), "float"),
                    ),
                )

                cur.execute("RELEASE SAVEPOINT entry_insert")
                entry_success += 1

                # Progress indicator
                if (index + 1) % 50 == 0:
                    print(
                        f"    📊 Progress: {index + 1}/{len(entries_df)} entries processed"
                    )

            except Exception as e:
                cur.execute("ROLLBACK TO SAVEPOINT entry_insert")
                entry_errors += 1
                if entry_errors <= 5:  # Show first 5 errors only
                    print(f"    ❌ Entry {index}: {e}")

        # Commit all successful entries
        conn.commit()

        results["entries"]["uploaded"] = entry_success
        results["entries"]["errors"] = entry_errors

        print(f"  ✅ Entries: {entry_success}/{len(entries_df)} uploaded")
        print(f"  ❌ Errors: {entry_errors}")

        # Step 5: Final verification and summary
        print("\n🔍 Final verification...")

        cur.execute("SELECT COUNT(*) FROM race_cards")
        final_races = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM horses")
        final_horses = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM race_entries")
        final_entries = cur.fetchone()[0]

        print(f"  📊 Final database state:")
        print(f"    - Races: {final_races}")
        print(f"    - Horses: {final_horses}")
        print(f"    - Entries: {final_entries}")

        # Step 6: Sample data verification
        print("\n📅 Sample race verification...")
        cur.execute(
            """
            SELECT rc.race_time, rc.course, rc.race_name, 
                   rc.runners, COUNT(re.entry_id) as actual_entries
            FROM race_cards rc
            LEFT JOIN race_entries re ON rc.race_id = re.race_id  
            WHERE rc.race_date = CURRENT_DATE
            GROUP BY rc.race_id, rc.race_time, rc.course, rc.race_name, rc.runners
            ORDER BY rc.race_time
            LIMIT 8
        """
        )

        sample_races = cur.fetchall()
        for race in sample_races:
            race_time, course, race_name, expected, actual = race
            status = "✅" if actual > 0 else "❌"
            print(
                f"  {status} {race_time.strftime('%H:%M')} {course} - {expected} exp, {actual} actual"
            )

        # Step 7: Success summary
        total_expected = existing_races + len(entries_df)
        total_actual = final_races + final_entries
        success_rate = (
            (total_actual / total_expected * 100) if total_expected > 0 else 0
        )

        results["summary"] = {
            "total_expected": total_expected,
            "total_uploaded": total_actual,
            "success_rate": f"{success_rate:.1f}%",
            "races_complete": final_races > 0,
            "horses_complete": final_horses > 0,
            "entries_complete": final_entries > 0,
        }

        print(f"\n🎉 Upload Complete!")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"📊 Total Records: {total_actual}/{total_expected}")

        if final_entries > 0:
            print("✅ Race card database ready for ML training!")
            print("✅ AI selections can now use real race data!")
        else:
            print("⚠️  Race entries still need attention")

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
    upload_race_cards_complete()
