#!/usr/bin/env python3
"""
Simple PostgreSQL Bulk Loader v2.05
Loads test data efficiently into PostgreSQL entity tables
"""

import pandas as pd
import sys
import time
from pathlib import Path
import argparse
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


def execute_sql(database, sql):
    """Execute SQL via Docker"""
    try:
        cmd = [
            "docker",
            "exec",
            "horse_racing_postgres_clean",
            "psql",
            "-U",
            "horse_racing",
            "-d",
            database,
            "-c",
            sql,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"SQL failed: {result.stderr}")
            return False
        return True

    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        return False


def clear_tables():
    """Clear existing entity data"""
    logger.info("Clearing existing entity tables...")
    tables = ["horses_entity", "jockeys_entity", "trainers_entity"]
    for table in tables:
        sql = f"DELETE FROM {table};"
        execute_sql("results", sql)
        logger.info(f"Cleared {table}")


def load_horses_bulk(csv_path):
    """Load horses using bulk insert"""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loading {len(df)} horses...")

        # Build bulk insert SQL
        values_list = []
        for _, row in df.iterrows():
            # Skip rows with missing id
            if pd.isna(row.get("id")) or str(row.get("id")).strip() == "":
                continue

            horse_id = str(row.get("id", ""))
            horse_name = str(row.get("name", "")).replace("'", "''")
            country = str(row.get("country", "GB"))
            age = int(row.get("age", 0)) if pd.notna(row.get("age")) else 0
            colour = str(row.get("color", "bay"))  # CSV uses 'color'
            sex = str(row.get("sex", "gelding"))
            owner = str(row.get("owner", "Unknown")).replace("'", "''")[
                :100
            ]  # Limit length
            trainer = "Unknown"  # Not in this CSV
            sire = str(row.get("sire", "Unknown")).replace("'", "''")[:100]
            dam = str(row.get("dam", "Unknown")).replace("'", "''")[:100]
            dam_sire = str(row.get("dam_sire", "Unknown")).replace("'", "''")[:100]

            values_list.append(
                f"('{horse_id}','{horse_name}','{country}',{age},'{colour}','{sex}','{owner}','{trainer}','{sire}','{dam}','{dam_sire}',true)"
            )

        if not values_list:
            logger.warning("No valid horse data to insert")
            return False

        # Split into batches to avoid command line length limits
        batch_size = 100
        total_inserted = 0

        for i in range(0, len(values_list), batch_size):
            batch = values_list[i : i + batch_size]
            values_str = ",".join(batch)

            sql = f"""
            INSERT INTO horses_entity (horse_id, horse_name, country, age, colour, sex, owner, trainer, sire, dam, dam_sire, is_active)
            VALUES {values_str};
            """

            if execute_sql("results", sql):
                total_inserted += len(batch)
            else:
                logger.error(f"Failed to insert batch {i//batch_size + 1}")

        logger.info(f"Successfully inserted {total_inserted} horses")
        return total_inserted > 0

    except Exception as e:
        logger.error(f"Failed to load horses: {e}")
        return False


def load_jockeys_bulk(csv_path):
    """Load jockeys using bulk insert"""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loading {len(df)} jockeys...")

        # Build bulk insert SQL
        values_list = []
        for _, row in df.iterrows():
            # Skip rows with missing Jockey_ID
            if pd.isna(row.get("Jockey_ID")) or str(row.get("Jockey_ID")).strip() == "":
                continue

            jockey_id = str(row.get("Jockey_ID", ""))
            jockey_name = str(row.get("Name", "")).replace("'", "''")[:100]
            allowance_claimed = "false"  # Default value

            # Parse percentage strings
            total_races = (
                int(row.get("Total_races", 0))
                if pd.notna(row.get("Total_races"))
                else 0
            )
            total_wins = int(row.get("Wins", 0)) if pd.notna(row.get("Wins")) else 0
            total_placed = (
                int(row.get("Placed", 0)) if pd.notna(row.get("Placed")) else 0
            )

            win_pct = (total_wins / total_races * 100) if total_races > 0 else 0.0
            place_pct = (total_placed / total_races * 100) if total_races > 0 else 0.0

            values_list.append(
                f"('{jockey_id}','{jockey_name}',{allowance_claimed},{total_races},{total_wins},{win_pct:.2f},{total_placed},{place_pct:.2f},true)"
            )

        if not values_list:
            logger.warning("No valid jockey data to insert")
            return False

        # Split into batches
        batch_size = 100
        total_inserted = 0

        for i in range(0, len(values_list), batch_size):
            batch = values_list[i : i + batch_size]
            values_str = ",".join(batch)

            sql = f"""
            INSERT INTO jockeys_entity (jockey_id, jockey_name, allowance_claimed, total_races, total_wins, win_percentage, total_placed, place_percentage, is_active)
            VALUES {values_str};
            """

            if execute_sql("results", sql):
                total_inserted += len(batch)
            else:
                logger.error(f"Failed to insert batch {i//batch_size + 1}")

        logger.info(f"Successfully inserted {total_inserted} jockeys")
        return total_inserted > 0

    except Exception as e:
        logger.error(f"Failed to load jockeys: {e}")
        return False


def load_trainers_bulk(csv_path):
    """Load trainers using bulk insert"""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loading {len(df)} trainers...")

        # Check actual CSV structure
        logger.info(f"CSV columns: {list(df.columns)}")

        # Try to load based on available columns
        values_list = []
        for _, row in df.iterrows():
            # Try different possible ID column names
            trainer_id = None
            for id_col in ["Trainer_ID", "trainer_id", "ID", "id"]:
                if id_col in df.columns and pd.notna(row.get(id_col)):
                    trainer_id = str(row.get(id_col, ""))
                    break

            if not trainer_id or trainer_id.strip() == "":
                continue

            # Try different possible name column names
            trainer_name = "Unknown"
            for name_col in ["Name", "trainer_name", "Trainer_Name"]:
                if name_col in df.columns and pd.notna(row.get(name_col)):
                    trainer_name = str(row.get(name_col, "")).replace("'", "''")[:100]
                    break

            # Try to get stats (with defaults if not available)
            # Note: The CSV has Total_races but we need total_runners for trainers
            total_runners = (
                int(row.get("Total_races", 0))
                if pd.notna(row.get("Total_races", 0))
                else 0
            )
            total_wins = int(row.get("Wins", 0)) if pd.notna(row.get("Wins", 0)) else 0
            total_placed = (
                int(row.get("Placed", 0)) if pd.notna(row.get("Placed", 0)) else 0
            )

            # For flat and jumps, use the available columns
            flat_runners = (
                int(row.get("Flat_AW_races", 0))
                if pd.notna(row.get("Flat_AW_races", 0))
                else 0
            )
            flat_runners += (
                int(row.get("Flat_Turf_races", 0))
                if pd.notna(row.get("Flat_Turf_races", 0))
                else 0
            )
            flat_wins = (
                int(row.get("Flat_AW_wins", 0))
                if pd.notna(row.get("Flat_AW_wins", 0))
                else 0
            )
            flat_wins += (
                int(row.get("Flat_Turf_wins", 0))
                if pd.notna(row.get("Flat_Turf_wins", 0))
                else 0
            )

            jumps_runners = (
                int(row.get("Chase_races", 0))
                if pd.notna(row.get("Chase_races", 0))
                else 0
            )
            jumps_runners += (
                int(row.get("Hurdle_races", 0))
                if pd.notna(row.get("Hurdle_races", 0))
                else 0
            )
            jumps_wins = (
                int(row.get("Chase_wins", 0))
                if pd.notna(row.get("Chase_wins", 0))
                else 0
            )
            jumps_wins += (
                int(row.get("Hurdle_wins", 0))
                if pd.notna(row.get("Hurdle_wins", 0))
                else 0
            )

            win_pct = (total_wins / total_runners * 100) if total_runners > 0 else 0.0
            place_pct = (
                (total_placed / total_runners * 100) if total_runners > 0 else 0.0
            )
            flat_win_rate = (
                (flat_wins / flat_runners * 100) if flat_runners > 0 else 0.0
            )
            jumps_win_rate = (
                (jumps_wins / jumps_runners * 100) if jumps_runners > 0 else 0.0
            )

            values_list.append(
                f"('{trainer_id}','{trainer_name}',{total_runners},{total_wins},{win_pct:.2f},{total_placed},{place_pct:.2f},{flat_runners},{flat_wins},{flat_win_rate:.2f},{jumps_runners},{jumps_wins},{jumps_win_rate:.2f},true)"
            )

        if not values_list:
            logger.warning("No valid trainer data to insert")
            return False

        # Split into batches
        batch_size = 100
        total_inserted = 0

        for i in range(0, len(values_list), batch_size):
            batch = values_list[i : i + batch_size]
            values_str = ",".join(batch)

            sql = f"""
            INSERT INTO trainers_entity (trainer_id, trainer_name, total_runners, total_wins, win_percentage, total_placed, place_percentage, flat_runners, flat_wins, flat_win_rate, jumps_runners, jumps_wins, jumps_win_rate, is_active)
            VALUES {values_str};
            """

            if execute_sql("results", sql):
                total_inserted += len(batch)
            else:
                logger.error(f"Failed to insert batch {i//batch_size + 1}")

        logger.info(f"Successfully inserted {total_inserted} trainers")
        return total_inserted > 0

    except Exception as e:
        logger.error(f"Failed to load trainers: {e}")
        return False


def validate_load():
    """Validate loaded data"""
    try:
        results = {}
        tables = ["horses_entity", "jockeys_entity", "trainers_entity"]

        for table in tables:
            cmd = [
                "docker",
                "exec",
                "horse_racing_postgres_clean",
                "psql",
                "-U",
                "horse_racing",
                "-d",
                "results",
                "-t",
                "-c",
                f"SELECT COUNT(*) FROM {table};",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                count = int(result.stdout.strip())
                results[table] = count
                logger.info(f"{table}: {count:,} records")
            else:
                results[table] = 0

        return results

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return {}


def main():
    parser = argparse.ArgumentParser(description="Simple PostgreSQL bulk loader v2.05")
    parser.add_argument("--dataset", default="2025-08-26", help="Dataset date")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / args.dataset

    start_time = time.time()
    logger.info(f"Starting bulk data load for {args.dataset}")

    # Clear tables
    clear_tables()

    # Load data
    success = True

    # Load horses
    horses_csv = data_dir / "horses" / "horses.csv"
    if horses_csv.exists():
        success &= load_horses_bulk(horses_csv)
    else:
        logger.warning(f"Horses CSV not found: {horses_csv}")

    # Load jockeys
    jockeys_csv = data_dir / "jockeys_stats" / "jockeys_stats.csv"
    if jockeys_csv.exists():
        success &= load_jockeys_bulk(jockeys_csv)
    else:
        logger.warning(f"Jockeys CSV not found: {jockeys_csv}")

    # Load trainers
    trainers_csv = data_dir / "trainers_stats" / "trainers_stats.csv"
    if trainers_csv.exists():
        success &= load_trainers_bulk(trainers_csv)
    else:
        logger.warning(f"Trainers CSV not found: {trainers_csv}")

    # Validate results
    validation_results = validate_load()

    duration = time.time() - start_time
    logger.info(f"Bulk data loading completed in {duration:.2f} seconds")

    if validation_results and sum(validation_results.values()) > 0:
        total_records = sum(validation_results.values())
        print(f"\\n✅ PostgreSQL Bulk Data Load Complete!")
        print(f"📊 Results Summary:")
        for table, count in validation_results.items():
            print(f"   {table}: {count:,} records")
        print(f"\\n📈 Total Records Loaded: {total_records:,}")
        print(f"🚀 Ready for comprehensive testing!")
        return 0
    else:
        print(f"\\n❌ PostgreSQL Data Load Failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
