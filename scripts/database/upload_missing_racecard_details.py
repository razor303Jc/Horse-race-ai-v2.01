#!/usr/bin/env python3
"""
Manual upload script for missing racecard details for today (2025-08-26)
This populates the racecard_details table that the bulk uploader missed.
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import sys


def upload_racecard_details():
    """Upload today's racecard details to the database"""

    # Database connection
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="cards_horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )
        cursor = conn.cursor()
        print("✅ Connected to cards database")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

    # Read the CSV file
    try:
        df = pd.read_csv("/tmp/racecard_details.csv")
        print(f"📝 Loaded {len(df)} racecard entries from CSV")
        print(f"📋 Columns: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Failed to read CSV: {e}")
        return False

    # Check current racecard_details count for today
    cursor.execute(
        """
        SELECT COUNT(*) FROM racecard_details rd 
        JOIN races r ON rd.race_id = r.race_id 
        WHERE r.date = %s
    """,
        ("2025-08-26",),
    )
    current_count = cursor.fetchone()[0]
    print(f"📊 Current racecard_details for today: {current_count}")

    if current_count > 0:
        print("⚠️  Data already exists for today. Skipping upload.")
        return True

    # Prepare data for insertion
    insert_data = []
    successful_rows = 0
    failed_rows = 0

    for index, row in df.iterrows():
        try:
            # Map CSV columns to database columns
            record = (
                int(row["id"]) if pd.notna(row["id"]) else None,
                int(row["race_id"]) if pd.notna(row["race_id"]) else None,
                int(row["horse_number"]) if pd.notna(row["horse_number"]) else None,
                int(row["Draw"]) if pd.notna(row["Draw"]) else None,
                int(row["Horse_ID"]) if pd.notna(row["Horse_ID"]) else None,
                str(row["Country"]) if pd.notna(row["Country"]) else None,
                str(row["Name"]) if pd.notna(row["Name"]) else None,
                int(row["Age"]) if pd.notna(row["Age"]) else None,
                str(row["weight_uk"]) if pd.notna(row["weight_uk"]) else None,
                float(row["weight"]) if pd.notna(row["weight"]) else None,
                str(row["gears"]) if pd.notna(row["gears"]) else None,
                int(row["Horse_rate"]) if pd.notna(row["Horse_rate"]) else None,
                int(row["jockey_ID"]) if pd.notna(row["jockey_ID"]) else None,
                str(row["jockey"]) if pd.notna(row["jockey"]) else None,
                int(row["trainer_ID"]) if pd.notna(row["trainer_ID"]) else None,
                str(row["trainer"]) if pd.notna(row["trainer"]) else None,
                str(row["fav"]) if pd.notna(row["fav"]) else None,
                str(row["odds"]) if pd.notna(row["odds"]) else None,
                float(row["odds_decimal"]) if pd.notna(row["odds_decimal"]) else None,
                (
                    str(row["Timeform_comments"])
                    if pd.notna(row["Timeform_comments"])
                    else None
                ),
            )
            insert_data.append(record)
            successful_rows += 1
        except Exception as e:
            print(f"⚠️  Failed to process row {index}: {e}")
            failed_rows += 1

    print(f"✅ Prepared {successful_rows} records for insertion")
    if failed_rows > 0:
        print(f"⚠️  Failed to prepare {failed_rows} records")

    # Insert data using execute_values for efficiency
    try:
        insert_query = """
            INSERT INTO racecard_details (
                id, race_id, horse_number, draw, horse_id, country, name, age,
                weight_uk, weight, gears, horse_rate, jockey_id, jockey,
                trainer_id, trainer, fav, odds, odds_decimal, timeform_comments
            ) VALUES %s
            ON CONFLICT (id) DO NOTHING
        """

        execute_values(cursor, insert_query, insert_data, template=None, page_size=100)

        conn.commit()

        # Verify insertion
        cursor.execute(
            """
            SELECT COUNT(*) FROM racecard_details rd 
            JOIN races r ON rd.race_id = r.race_id 
            WHERE r.date = %s
        """,
            ("2025-08-26",),
        )
        final_count = cursor.fetchone()[0]

        print(f"🎉 Successfully inserted racecard details!")
        print(f"📊 Final count for today: {final_count}")

        # Show sample data
        cursor.execute(
            """
            SELECT rd.name, rd.jockey, rd.trainer, r.course, r.race_time
            FROM racecard_details rd 
            JOIN races r ON rd.race_id = r.race_id 
            WHERE r.date = %s
            LIMIT 5
        """,
            ("2025-08-26",),
        )
        samples = cursor.fetchall()
        print("\n🏇 Sample today's entries:")
        for sample in samples:
            print(
                f"   - {sample[0]} | J: {sample[1]} | T: {sample[2]} | {sample[3]} {sample[4]}"
            )

        return True

    except Exception as e:
        print(f"❌ Failed to insert data: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("🚀 Manual Racecard Details Uploader")
    print("=" * 50)
    success = upload_racecard_details()
    if success:
        print("\n✅ Upload completed successfully!")
    else:
        print("\n❌ Upload failed!")
        sys.exit(1)
