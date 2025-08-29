#!/usr/bin/env python3
"""
Upload Today's Racing Data - Quick Script for 2025-08-26
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect_cards_db():
    """Connect to cards database"""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="cards_horse_racing_db",
        user="horse_race_user",
        password="secure_password_123",
    )


def connect_results_db():
    """Connect to results database"""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="results_horse_racing_db",
        user="horse_race_user",
        password="secure_password_123",
    )


def upload_races_data():
    """Upload today's race data"""
    data_dir = Path(
        "/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads/processed/2025-08-26"
    )
    races_file = data_dir / "races/races.csv"

    if not races_file.exists():
        logger.error(f"❌ Races file not found: {races_file}")
        return False

    races_df = pd.read_csv(races_file)
    logger.info(f"📊 Processing {len(races_df)} races...")

    conn = connect_cards_db()
    cursor = conn.cursor()

    try:
        # Clear existing data for today
        cursor.execute("DELETE FROM races WHERE date = %s", ("2025-08-26",))
        logger.info(f"🗑️ Cleared existing races for 2025-08-26")

        # Prepare data for insertion
        races_data = []
        for _, row in races_df.iterrows():
            race_data = (
                int(row["Race_ID"]),
                int(row["race_number"]) if pd.notna(row["race_number"]) else None,
                row["race_time"],
                int(row["course_id"]) if pd.notna(row["course_id"]) else None,
                row["Course"],
                row["Race_type"],
                row["Date"],
                row["Race_name"],
                row["Class"],
                row["Years"],
                row["Distance"],
                row["Surface"],
                row["Prize"],
                (
                    int(row["Runners_racecard"])
                    if pd.notna(row["Runners_racecard"])
                    else None
                ),
                int(row["Runners"]) if pd.notna(row["Runners"]) else None,
                row["Draw"] if pd.notna(row["Draw"]) else None,
                int(row["EW_racecard"]) if pd.notna(row["EW_racecard"]) else None,
                int(row["EW"]) if pd.notna(row["EW"]) else None,
                (
                    int(row["Places_EW_racecard"])
                    if pd.notna(row["Places_EW_racecard"])
                    else None
                ),
                int(row["Places_EW"]) if pd.notna(row["Places_EW"]) else None,
            )
            races_data.append(race_data)

        # Insert data
        insert_query = """
        INSERT INTO races (
            race_id, race_number, race_time, course_id, course, race_type, date, race_name,
            class, years, distance, surface, prize, runners_racecard, runners, draw,
            ew_racecard, ew, places_ew_racecard, places_ew
        ) VALUES %s ON CONFLICT (race_id) DO NOTHING
        """

        execute_values(cursor, insert_query, races_data)
        conn.commit()

        logger.info(f"✅ Uploaded {len(races_data)} races to cards database")
        return True

    except Exception as e:
        logger.error(f"❌ Error uploading races: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def upload_horses_data():
    """Upload today's horse data"""
    data_dir = Path(
        "/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads/processed/2025-08-26"
    )
    horses_file = data_dir / "horses/horses.csv"

    if not horses_file.exists():
        logger.error(f"❌ Horses file not found: {horses_file}")
        return False

    horses_df = pd.read_csv(horses_file)
    logger.info(f"🐎 Processing {len(horses_df)} horses...")

    conn = connect_cards_db()
    cursor = conn.cursor()

    try:
        # Clear existing data for today's races
        cursor.execute(
            """
            DELETE FROM racecard_details 
            WHERE race_id IN (SELECT race_id FROM races WHERE date = %s)
        """,
            ("2025-08-26",),
        )
        logger.info(f"🗑️ Cleared existing horses for 2025-08-26")

        # Prepare data for insertion
        horses_data = []
        for _, row in horses_df.iterrows():
            horse_data = (
                int(row["Race_ID"]),
                row["Horse"],
                int(row["Pos_racecard"]) if pd.notna(row["Pos_racecard"]) else None,
                row["Jockey"],
                row["Trainer"],
                float(row["Weight"]) if pd.notna(row["Weight"]) else None,
                float(row["Odds_racecard"]) if pd.notna(row["Odds_racecard"]) else None,
                int(row["Age"]) if pd.notna(row["Age"]) else None,
                row["Form"] if pd.notna(row["Form"]) else None,
                int(row["Draw"]) if pd.notna(row["Draw"]) else None,
            )
            horses_data.append(horse_data)

        # Insert data
        insert_query = """
        INSERT INTO racecard_details (
            race_id, horse, pos_racecard, jockey, trainer, weight, 
            odds_racecard, age, form, draw
        ) VALUES %s ON CONFLICT (race_id, horse) DO NOTHING
        """

        execute_values(cursor, insert_query, horses_data)
        conn.commit()

        logger.info(f"✅ Uploaded {len(horses_data)} horses to cards database")
        return True

    except Exception as e:
        logger.error(f"❌ Error uploading horses: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def upload_results_data():
    """Upload today's results data if available"""
    data_dir = Path(
        "/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads/processed/2025-08-26"
    )

    # Upload records (race results)
    records_file = data_dir / "records/records.csv"
    if records_file.exists():
        records_df = pd.read_csv(records_file)
        logger.info(f"🏆 Processing {len(records_df)} race results...")

        conn = connect_results_db()
        cursor = conn.cursor()

        try:
            # Clear existing results for today
            cursor.execute(
                "DELETE FROM records WHERE date = %s", ("2025-08-25",)
            )  # Note: results are for 25th

            # Insert results data (simplified - you may need to adjust columns)
            results_data = []
            for _, row in records_df.iterrows():
                if pd.notna(row.get("Race_ID")):
                    result_data = (
                        int(row["Race_ID"]),
                        row.get("Horse", ""),
                        int(row.get("Pos", 0)) if pd.notna(row.get("Pos")) else None,
                        row.get("Jockey", ""),
                        row.get("Date", "2025-08-25"),
                    )
                    results_data.append(result_data)

            if results_data:
                insert_query = """
                INSERT INTO records (race_id, horse, pos, jockey, date) 
                VALUES %s ON CONFLICT (race_id, horse) DO NOTHING
                """
                execute_values(cursor, insert_query, results_data)
                conn.commit()
                logger.info(
                    f"✅ Uploaded {len(results_data)} results to results database"
                )

        except Exception as e:
            logger.error(f"❌ Error uploading results: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        logger.info("ℹ️ No results file found (results are typically for previous day)")


def main():
    """Main upload function"""
    logger.info("🏇 UPLOADING TODAY'S RACING DATA (2025-08-26)")
    logger.info("=" * 60)

    success = True

    # Upload race cards
    if upload_races_data():
        logger.info("✅ Races uploaded successfully")
    else:
        logger.error("❌ Failed to upload races")
        success = False

    # Upload horses
    if upload_horses_data():
        logger.info("✅ Horses uploaded successfully")
    else:
        logger.error("❌ Failed to upload horses")
        success = False

    # Upload results (if available)
    upload_results_data()

    if success:
        logger.info("🎉 Data upload completed successfully!")

        # Quick verification
        try:
            conn = connect_cards_db()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM races WHERE date = '2025-08-26'")
            race_count = cursor.fetchone()[0]
            cursor.execute(
                "SELECT COUNT(*) FROM racecard_details WHERE race_id IN (SELECT race_id FROM races WHERE date = '2025-08-26')"
            )
            horse_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            logger.info(
                f"📊 Verification: {race_count} races, {horse_count} horses in database"
            )

        except Exception as e:
            logger.warning(f"⚠️ Verification failed: {e}")
    else:
        logger.error("❌ Data upload had errors!")


if __name__ == "__main__":
    main()
