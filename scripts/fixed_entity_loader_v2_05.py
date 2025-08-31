#!/usr/bin/env python3
"""
Fixed Entity Data Loader for PostgreSQL v2.05
Properly map CSV columns to PostgreSQL schema and load complete entity data
Uses centralized database configuration for reliable connections
"""
import subprocess
import pandas as pd
import logging
import sys
from pathlib import Path
import psycopg2

# Add the project root to the path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config.database_config import db_config, execute_sql_command

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def execute_sql(database_type, sql_command):
    """Execute SQL command via database config"""
    return execute_sql_command(database_type, sql_command)


def update_index_tables():
    """Update index tables with any new entities from race_results"""
    logging.info("Updating index tables with new entities...")

    # Database configuration for direct connection
    DB_CONFIG = {
        "host": "localhost",
        "database": "results_horse_racing_db",
        "user": "horse_racing",
        "password": "horse_racing_password",
        "port": "5432",
    }

    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Update horses_index
        cursor.execute(
            """
            INSERT INTO horses_index (horse_name, horse_id)
            SELECT DISTINCT horse_name, horse_id 
            FROM race_results 
            WHERE horse_name IS NOT NULL 
            AND horse_name != ''
            AND NOT EXISTS (
                SELECT 1 FROM horses_index 
                WHERE horses_index.horse_name = race_results.horse_name
                AND horses_index.horse_id = race_results.horse_id
            )
        """
        )
        new_horses = cursor.rowcount

        # Update jockeys_index
        cursor.execute(
            """
            INSERT INTO jockeys_index (jockey_name, jockey_id)
            SELECT DISTINCT jockey_name, 
                   ROW_NUMBER() OVER (ORDER BY jockey_name) + COALESCE(
                       (SELECT MAX(jockey_id) FROM jockeys_index), 0
                   ) as jockey_id
            FROM race_results 
            WHERE jockey_name IS NOT NULL 
            AND jockey_name != ''
            AND NOT EXISTS (
                SELECT 1 FROM jockeys_index 
                WHERE jockeys_index.jockey_name = race_results.jockey_name
            )
        """
        )
        new_jockeys = cursor.rowcount

        # Update trainers_index
        cursor.execute(
            """
            INSERT INTO trainers_index (trainer_name, trainer_id)
            SELECT DISTINCT trainer_name,
                   ROW_NUMBER() OVER (ORDER BY trainer_name) + COALESCE(
                       (SELECT MAX(trainer_id) FROM trainers_index), 0
                   ) as trainer_id
            FROM race_results 
            WHERE trainer_name IS NOT NULL 
            AND trainer_name != ''
            AND NOT EXISTS (
                SELECT 1 FROM trainers_index 
                WHERE trainers_index.trainer_name = race_results.trainer_name
            )
        """
        )
        new_trainers = cursor.rowcount

        # Commit changes
        conn.commit()

        total_new = new_horses + new_jockeys + new_trainers
        if total_new > 0:
            logging.info(
                f"Added {new_horses} horses, {new_jockeys} jockeys, "
                f"{new_trainers} trainers to index tables"
            )
        else:
            logging.info("Index tables are up to date - no new entities found")

        return True

    except Exception as e:
        logging.error(f"Index table update failed: {e}")
        if "conn" in locals():
            conn.rollback()
        return False
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()


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


def load_races_data():
    """Load races data from CSV to races table"""
    logging.info("Loading races data...")

    csv_path = "data/2025-08-26/races/races.csv"
    df = pd.read_csv(csv_path)

    # CSV to Database column mapping
    column_mapping = {
        "Race_ID": "race_id",
        "race_number": "race_number",
        "race_time": "race_time",
        "course_id": "course_id",
        "Course": "course",
        "Race_type": "race_type",
        "Date": "date",
        "Race_name": "race_name",
        "Class": "class",
        "Years": "years",
        "Distance": "distance",
        "Surface": "surface",
        "Prize": "prize",
        "Runners_racecard": "runners_racecard",
        "Runners": "runners",
        "Draw": "draw",
        "EW_racecard": "ew_racecard",
        "EW": "ew",
        "Places_EW_racecard": "places_ew_racecard",
        "Places_EW": "places_ew",
    }

    # Rename columns to match database schema
    df = df.rename(columns=column_mapping)

    # Clean and process data
    df = df.fillna(
        {
            "race_id": "",
            "race_number": 0,
            "race_time": "",
            "course_id": 0,
            "course": "",
            "race_type": "",
            "date": "",
            "race_name": "",
            "class": "",
            "years": "",
            "distance": "",
            "surface": "",
            "prize": "",
            "runners_racecard": 0,
            "runners": 0,
            "draw": "",
            "ew_racecard": 0,
            "ew": 0,
            "places_ew_racecard": 0,
            "places_ew": 0,
        }
    )

    successful_inserts = 0
    batch_size = 500

    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i : i + batch_size]
        values = []

        for _, row in batch_df.iterrows():
            try:
                # Handle NULL values properly
                race_id = (
                    int(row["race_id"])
                    if pd.notna(row["race_id"]) and row["race_id"] != ""
                    else None
                )
                race_number = (
                    int(row["race_number"])
                    if pd.notna(row["race_number"]) and row["race_number"] != ""
                    else 0
                )
                race_time = str(row["race_time"]) if pd.notna(row["race_time"]) else ""
                course_id = (
                    int(row["course_id"])
                    if pd.notna(row["course_id"]) and row["course_id"] != ""
                    else 0
                )
                course = str(row["course"]) if pd.notna(row["course"]) else ""
                race_type = str(row["race_type"]) if pd.notna(row["race_type"]) else ""
                date = str(row["date"]) if pd.notna(row["date"]) else None
                race_name = str(row["race_name"]) if pd.notna(row["race_name"]) else ""
                class_val = str(row["class"]) if pd.notna(row["class"]) else ""
                years = str(row["years"]) if pd.notna(row["years"]) else ""
                distance = str(row["distance"]) if pd.notna(row["distance"]) else ""
                surface = str(row["surface"]) if pd.notna(row["surface"]) else ""
                prize = str(row["prize"]) if pd.notna(row["prize"]) else ""
                runners_racecard = (
                    int(row["runners_racecard"])
                    if pd.notna(row["runners_racecard"])
                    and row["runners_racecard"] != ""
                    else 0
                )
                runners = (
                    int(row["runners"])
                    if pd.notna(row["runners"]) and row["runners"] != ""
                    else 0
                )
                draw = str(row["draw"]) if pd.notna(row["draw"]) else ""
                ew_racecard = (
                    int(row["ew_racecard"])
                    if pd.notna(row["ew_racecard"]) and row["ew_racecard"] != ""
                    else 0
                )
                ew = int(row["ew"]) if pd.notna(row["ew"]) and row["ew"] != "" else 0
                places_ew_racecard = (
                    int(row["places_ew_racecard"])
                    if pd.notna(row["places_ew_racecard"])
                    and row["places_ew_racecard"] != ""
                    else 0
                )
                places_ew = (
                    int(row["places_ew"])
                    if pd.notna(row["places_ew"]) and row["places_ew"] != ""
                    else 0
                )

                if race_id is None:
                    continue

                value = f"({race_id}, {race_number}, '{race_time}', {course_id}, '{course.replace("'", "''")}', '{race_type}', '{date}', '{race_name.replace("'", "''")}', '{class_val}', '{years}', '{distance}', '{surface}', '{prize}', {runners_racecard}, {runners}, '{draw}', {ew_racecard}, {ew}, {places_ew_racecard}, {places_ew})"
                values.append(value)

            except Exception as e:
                logging.warning(f"Skipping invalid race record: {e}")
                continue

        if values:
            sql = f"""
                INSERT INTO races (race_id, race_number, race_time, course_id, course, race_type, date, race_name, class, years, distance, surface, prize, runners_racecard, runners, draw, ew_racecard, ew, places_ew_racecard, places_ew)
                VALUES {', '.join(values)}
                ON CONFLICT (race_id) DO NOTHING;
            """

            if execute_sql("results", sql):
                successful_inserts += len(values)
                logging.info(f"Inserted batch {i//batch_size + 1}: {len(values)} races")
            else:
                logging.error(f"Failed to insert batch {i//batch_size + 1}")

    logging.info(f"Successfully loaded {successful_inserts} races")
    return successful_inserts > 0


def map_place_code(place_value):
    """Map horse racing place codes to integers

    Args:
        place_value: Place value from CSV (could be number or code)

    Returns:
        int: Numeric place (1,2,3...) or mapped code (F=999, PU=998, etc.)
    """
    if pd.isna(place_value) or place_value == "":
        return 0

    place_str = str(place_value).strip().upper()

    # Non-finish codes mapped to high numbers
    place_codes = {
        "F": 999,  # Fell
        "PU": 998,  # Pulled Up
        "U": 997,  # Unseated
        "RR": 996,  # Refused to Race
        "BD": 995,  # Brought Down
        "SU": 994,  # Slipped Up
        "UR": 993,  # Unseated Rider
        "R": 992,  # Refused
        "DNF": 991,  # Did Not Finish
        "DSQ": 990,  # Disqualified
        "LTO": 989,  # Left at start
        "CO": 988,  # Carried Out
        "VOID": 987,  # Void
    }

    # Try to convert to integer first (normal finishing positions)
    try:
        return int(place_str)
    except ValueError:
        # If not a number, check if it's a known code
        return place_codes.get(place_str, 0)


def load_results_data():
    """Load results data from CSV to race_results table"""
    logging.info("Loading results data...")

    csv_path = "data/2025-08-26/records/records.csv"
    df = pd.read_csv(csv_path)

    # CSV to Database column mapping (matching actual race_results table in Docker)
    column_mapping = {
        "Race_ID": "race_id",
        "Name": "horse_name",
        "Place": "place",
        "jockey": "jockey_name",
        "trainer": "trainer_name",
        "SP": "sp",
        "Distance_btn": "distance_btn",
        "Age": "age",
        "weight": "weight",
        "Horse_ID": "horse_id",
        "Country": "country",
        "Draw": "draw",
        "Horse_number": "horse_number",
        "fav": "fav",
    }

    # Rename columns to match database schema
    df = df.rename(columns=column_mapping)

    # Clean and process data - only keep columns that exist in database schema
    essential_columns = [
        "race_id",
        "horse_name",
        "place",
        "jockey_name",
        "trainer_name",
        "sp",
        "distance_btn",
        "age",
        "weight",
        "horse_id",
        "country",
        "draw",
        "horse_number",
        "fav",
    ]

    # Keep only columns that exist in both CSV and our mapping
    available_columns = [col for col in essential_columns if col in df.columns]
    df = df[available_columns]

    # Fill NaN values
    df = df.fillna(
        {
            "race_id": 0,
            "horse_name": "",
            "place": 0,
            "jockey_name": "",
            "trainer_name": "",
            "sp": 0.0,
            "distance_btn": "",
            "age": 0,
            "weight": 0.0,
            "horse_id": 0,
            "country": "",
            "draw": 0,
            "horse_number": 0,
            "fav": "",
        }
    )

    successful_inserts = 0
    batch_size = 500

    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i : i + batch_size]
        values = []

        for _, row in batch_df.iterrows():
            try:
                # Handle NULL values properly - map to actual table columns
                race_id = (
                    int(row["race_id"])
                    if pd.notna(row["race_id"]) and row["race_id"] != ""
                    else 0
                )
                horse_name = (
                    str(row["horse_name"]) if pd.notna(row["horse_name"]) else ""
                )
                place = map_place_code(row["place"])
                jockey_name = (
                    str(row["jockey_name"]) if pd.notna(row["jockey_name"]) else ""
                )
                trainer_name = (
                    str(row["trainer_name"]) if pd.notna(row["trainer_name"]) else ""
                )
                sp = (
                    float(row["sp"]) if pd.notna(row["sp"]) and row["sp"] != "" else 0.0
                )
                distance_btn = (
                    str(row["distance_btn"]) if pd.notna(row["distance_btn"]) else ""
                )
                age = (
                    int(row["age"]) if pd.notna(row["age"]) and row["age"] != "" else 0
                )
                weight = (
                    float(row["weight"])
                    if pd.notna(row["weight"]) and row["weight"] != ""
                    else 0.0
                )
                horse_id = (
                    int(row["horse_id"])
                    if pd.notna(row["horse_id"]) and row["horse_id"] != ""
                    else 0
                )
                country = str(row["country"]) if pd.notna(row["country"]) else ""
                draw = (
                    int(row["draw"])
                    if pd.notna(row["draw"]) and row["draw"] != ""
                    else 0
                )
                horse_number = (
                    int(row["horse_number"])
                    if pd.notna(row["horse_number"]) and row["horse_number"] != ""
                    else 0
                )
                fav = str(row["fav"]) if pd.notna(row["fav"]) else ""

                if race_id == 0 or horse_name == "":
                    continue

                # Escape quotes in strings
                safe_horse_name = horse_name.replace("'", "''")
                safe_jockey_name = jockey_name.replace("'", "''")
                safe_trainer_name = trainer_name.replace("'", "''")
                safe_distance_btn = distance_btn.replace("'", "''")
                safe_country = country.replace("'", "''")
                safe_fav = fav.replace("'", "''")

                value = f"({race_id}, {horse_number}, {place}, {draw}, {horse_id}, '{safe_horse_name}', '{safe_country}', {age}, {weight}, {sp}, '{safe_jockey_name}', '{safe_trainer_name}', '{safe_fav}', '{safe_distance_btn}')"
                values.append(value)

            except Exception as e:
                logging.warning(f"Skipping invalid results record: {e}")
                continue

        if values:
            sql = f"""
                INSERT INTO race_results (race_id, horse_number, place, draw, horse_id, horse_name, country, age, weight, sp, jockey_name, trainer_name, fav, distance_btn)
                VALUES {', '.join(values)};
            """

            if execute_sql("results", sql):
                successful_inserts += len(values)
                logging.info(
                    f"Inserted batch {i//batch_size + 1}: {len(values)} results"
                )
            else:
                logging.error(f"Failed to insert batch {i//batch_size + 1}")

    logging.info(f"Successfully loaded {successful_inserts} results")
    return successful_inserts > 0


def verify_data_loading():
    """Verify all entity data loaded successfully"""
    logging.info("Verifying entity data loading...")

    # Check record counts
    tables = [
        "horses_entity",
        "jockeys_entity",
        "trainers_entity",
        "races",
        "race_results",
    ]

    total_records = 0
    for table in tables:
        cmd = db_config.get_docker_exec_command(
            "results", f"SELECT COUNT(*) FROM {table};"
        )
        cmd.append("-t")  # Add tuples-only flag

        result = subprocess.run(cmd, capture_output=True, text=True)

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

    # Load race and results data
    success &= load_races_data()
    success &= load_results_data()

    # Update index tables with new entities
    if success:
        print("\n🔄 Updating index tables...")
        index_success = update_index_tables()
        if index_success:
            print("✅ Index tables updated successfully")
        else:
            print("⚠️  Index table update had issues - check logs")

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
