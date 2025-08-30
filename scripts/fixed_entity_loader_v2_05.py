#!/usr/bin/env python3
"""
Fixed Entity Data Loader for PostgreSQL v2.05
Properly map CSV columns to PostgreSQL schema and load complete entity data
"""
import subprocess
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def execute_sql(database, sql_command):
    """Execute SQL command via docker exec"""
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
        sql_command,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.returncode == 0:
            return True
        else:
            logging.error(f"SQL failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        logging.error(f"Failed to execute SQL: {e}")
        return False


def load_horses_data():
    """Load horses data with proper column mapping"""
    logging.info("Loading horses entity data...")

    csv_file = Path("data/2025-08-26/horses/horses.csv")
    if not csv_file.exists():
        logging.error(f"Horses CSV not found: {csv_file}")
        return False

    # Read CSV
    df = pd.read_csv(csv_file)
    logging.info(f"Loaded {len(df)} horses from CSV")

    # Clear existing data
    execute_sql("results", "DELETE FROM horses_entity;")

    successful_inserts = 0
    batch_size = 100

    for i in range(0, len(df), batch_size):
        batch = df.iloc[i : i + batch_size]

        # Build INSERT statement with proper column mapping
        values = []
        for _, row in batch.iterrows():
            try:
                # Map CSV columns to database columns
                horse_id = int(row["id"]) if pd.notna(row["id"]) else None
                horse_name = (
                    str(row["name"]).replace("'", "''")
                    if pd.notna(row["name"])
                    else "Unknown"
                )
                age = (
                    int(row["age"])
                    if pd.notna(row["age"]) and str(row["age"]).isdigit()
                    else None
                )
                sex = str(row["sex"]) if pd.notna(row["sex"]) else "Unknown"
                trainer = "Unknown"  # No trainer info in this CSV
                rating = None  # No rating info in this CSV

                value = f"({horse_id}, '{horse_name}', {age if age else 'NULL'}, '{sex}', '{trainer}', {rating if rating else 'NULL'})"
                values.append(value)

            except Exception as e:
                logging.warning(f"Skipping invalid horse record: {e}")
                continue

        if values:
            sql = f"""
                INSERT INTO horses_entity (horse_id, horse_name, age, sex, trainer, rating)
                VALUES {', '.join(values)};
            """

            if execute_sql("results", sql):
                successful_inserts += len(values)
                logging.info(
                    f"Inserted batch {i//batch_size + 1}: {len(values)} horses"
                )
            else:
                logging.error(f"Failed to insert batch {i//batch_size + 1}")

    logging.info(f"Successfully loaded {successful_inserts} horses")
    return successful_inserts > 0


def load_jockeys_data():
    """Load jockeys data with proper column mapping"""
    logging.info("Loading jockeys entity data...")

    csv_file = Path("data/2025-08-26/jockeys_stats/jockeys_stats.csv")
    if not csv_file.exists():
        logging.error(f"Jockeys CSV not found: {csv_file}")
        return False

    # Read CSV
    df = pd.read_csv(csv_file)
    logging.info(f"Loaded {len(df)} jockeys from CSV")

    # Clear existing data
    execute_sql("results", "DELETE FROM jockeys_entity;")

    successful_inserts = 0
    batch_size = 100

    for i in range(0, len(df), batch_size):
        batch = df.iloc[i : i + batch_size]

        # Build INSERT statement with proper column mapping
        values = []
        for _, row in batch.iterrows():
            try:
                # Map CSV columns to database columns
                jockey_id = (
                    int(row["Jockey_ID"]) if pd.notna(row["Jockey_ID"]) else None
                )
                jockey_name = (
                    str(row["Name"]).replace("'", "''")
                    if pd.notna(row["Name"])
                    else "Unknown"
                )
                claim_allowance = (
                    int(row.get("claim_allowance", 0))
                    if pd.notna(row.get("claim_allowance", 0))
                    else 0
                )
                wins = (
                    int(row["Wins"])
                    if pd.notna(row["Wins"]) and str(row["Wins"]).isdigit()
                    else 0
                )
                runs = (
                    int(row["Total_races"])
                    if pd.notna(row["Total_races"])
                    and str(row["Total_races"]).isdigit()
                    else 0
                )
                win_rate = (
                    float(row["Percentage_wins"])
                    if pd.notna(row["Percentage_wins"])
                    and str(row["Percentage_wins"]).replace(".", "").isdigit()
                    else 0.0
                )

                value = f"({jockey_id}, '{jockey_name}', {claim_allowance}, {wins}, {runs}, {win_rate})"
                values.append(value)

            except Exception as e:
                logging.warning(f"Skipping invalid jockey record: {e}")
                continue

        if values:
            sql = f"""
                INSERT INTO jockeys_entity (jockey_id, jockey_name, claim_allowance, wins, runs, win_rate)
                VALUES {', '.join(values)};
            """

            if execute_sql("results", sql):
                successful_inserts += len(values)
                logging.info(
                    f"Inserted batch {i//batch_size + 1}: {len(values)} jockeys"
                )
            else:
                logging.error(f"Failed to insert batch {i//batch_size + 1}")

    logging.info(f"Successfully loaded {successful_inserts} jockeys")
    return successful_inserts > 0


def load_trainers_data():
    """Load trainers data with proper column mapping"""
    logging.info("Loading trainers entity data...")

    csv_file = Path("data/2025-08-26/trainers_stats/trainers_stats.csv")
    if not csv_file.exists():
        logging.error(f"Trainers CSV not found: {csv_file}")
        return False

    # Read CSV
    df = pd.read_csv(csv_file)
    logging.info(f"Loaded {len(df)} trainers from CSV")

    # Clear existing data
    execute_sql("results", "DELETE FROM trainers_entity;")

    successful_inserts = 0
    batch_size = 100

    for i in range(0, len(df), batch_size):
        batch = df.iloc[i : i + batch_size]

        # Build INSERT statement with proper column mapping
        values = []
        for _, row in batch.iterrows():
            try:
                # Map CSV columns to database columns
                trainer_id = (
                    int(row["Trainer_ID"]) if pd.notna(row["Trainer_ID"]) else None
                )
                trainer_name = (
                    str(row["Name"]).replace("'", "''")
                    if pd.notna(row["Name"])
                    else "Unknown"
                )
                total_races = (
                    int(row["Total_races"])
                    if pd.notna(row["Total_races"])
                    and str(row["Total_races"]).isdigit()
                    else 0
                )
                wins = (
                    int(row["Wins"])
                    if pd.notna(row["Wins"]) and str(row["Wins"]).isdigit()
                    else 0
                )
                win_percentage = (
                    float(row["Percentage_wins"])
                    if pd.notna(row["Percentage_wins"])
                    and str(row["Percentage_wins"]).replace(".", "").isdigit()
                    else 0.0
                )
                placed = (
                    int(row["Placed"])
                    if pd.notna(row["Placed"]) and str(row["Placed"]).isdigit()
                    else 0
                )
                place_percentage = (
                    float(row["Percentage_placed"])
                    if pd.notna(row["Percentage_placed"])
                    and str(row["Percentage_placed"]).replace(".", "").isdigit()
                    else 0.0
                )

                value = f"({trainer_id}, '{trainer_name}', {total_races}, {wins}, {win_percentage}, {placed}, {place_percentage})"
                values.append(value)

            except Exception as e:
                logging.warning(f"Skipping invalid trainer record: {e}")
                continue

        if values:
            sql = f"""
                INSERT INTO trainers_entity (trainer_id, trainer_name, total_races, wins, win_percentage, placed, place_percentage)
                VALUES {', '.join(values)};
            """

            if execute_sql("results", sql):
                successful_inserts += len(values)
                logging.info(
                    f"Inserted batch {i//batch_size + 1}: {len(values)} trainers"
                )
            else:
                logging.error(f"Failed to insert batch {i//batch_size + 1}")

    logging.info(f"Successfully loaded {successful_inserts} trainers")
    return successful_inserts > 0


def verify_data_loading():
    """Verify all entity data loaded successfully"""
    logging.info("Verifying entity data loading...")

    # Check record counts
    tables = ["horses_entity", "jockeys_entity", "trainers_entity", "races"]

    total_records = 0
    for table in tables:
        result = subprocess.run(
            [
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
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            count = int(result.stdout.strip())
            total_records += count
            logging.info(f"{table}: {count} records")
        else:
            logging.error(f"Failed to count {table}")

    logging.info(f"Total records in database: {total_records}")
    return total_records


def main():
    """Load complete entity data into PostgreSQL"""
    print("🚀 Loading Complete Entity Data into PostgreSQL v2.05")
    print("=" * 60)

    success = True

    # Load entity data
    success &= load_horses_data()
    success &= load_jockeys_data()
    success &= load_trainers_data()

    # Verify loading
    total_records = verify_data_loading()

    if success and total_records > 10000:
        print(f"\n✅ Entity Data Loading Complete!")
        print(f"📊 Total Records: {total_records}")
        print(f"🏇 Ready for realistic racing simulation testing!")
        return 0
    else:
        print(f"\n❌ Entity Data Loading Failed!")
        print(f"📊 Total Records: {total_records}")
        return 1


if __name__ == "__main__":
    exit(main())
