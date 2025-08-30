#!/usr/bin/env python3
"""
Complete Racing Data Loader v2.05
Load full racing dataset including races, results, records, and racecard details
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


def create_racing_tables():
    """Create complete racing database schema"""
    logger.info("Creating racing database tables...")

    # Create races table
    races_sql = """
    CREATE TABLE IF NOT EXISTS races (
        id SERIAL PRIMARY KEY,
        race_id INTEGER UNIQUE NOT NULL,
        race_number INTEGER,
        race_time VARCHAR(10),
        course_id INTEGER,
        course VARCHAR(100),
        race_type VARCHAR(50),
        date DATE,
        race_name VARCHAR(200),
        class VARCHAR(50),
        years VARCHAR(50),
        distance VARCHAR(50),
        surface VARCHAR(50),
        prize VARCHAR(50),
        runners_racecard INTEGER,
        runners INTEGER,
        draw VARCHAR(20),
        ew_racecard INTEGER,
        ew INTEGER,
        places_ew_racecard INTEGER,
        places_ew INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # Create race results table
    results_sql = """
    CREATE TABLE IF NOT EXISTS race_results (
        id SERIAL PRIMARY KEY,
        race_id INTEGER NOT NULL,
        horse_number INTEGER,
        place INTEGER,
        draw INTEGER,
        horse_id INTEGER,
        horse_name VARCHAR(100),
        country VARCHAR(10),
        age INTEGER,
        weight_uk VARCHAR(20),
        weight DECIMAL(5,2),
        jockey_id INTEGER,
        jockey_name VARCHAR(100),
        trainer_id INTEGER,
        trainer_name VARCHAR(100),
        fav VARCHAR(10),
        sp DECIMAL(8,2),
        distance_btn VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (race_id) REFERENCES races(race_id)
    );
    """

    # Create indexes
    indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_races_race_id ON races(race_id);
    CREATE INDEX IF NOT EXISTS idx_races_date ON races(date);
    CREATE INDEX IF NOT EXISTS idx_races_course ON races(course);
    CREATE INDEX IF NOT EXISTS idx_race_results_race_id ON race_results(race_id);
    CREATE INDEX IF NOT EXISTS idx_race_results_horse_id ON race_results(horse_id);
    CREATE INDEX IF NOT EXISTS idx_race_results_place ON race_results(place);
    """

    # Execute schema creation
    execute_sql("results", races_sql)
    execute_sql("results", results_sql)
    execute_sql("results", indexes_sql)

    logger.info("Racing database schema created successfully")


def load_races_data(csv_path):
    """Load races data"""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loading {len(df)} races...")

        # Clear existing data
        execute_sql("results", "DELETE FROM race_results;")
        execute_sql("results", "DELETE FROM races;")

        # Build bulk insert
        values_list = []
        for _, row in df.iterrows():
            race_id = int(row.get("Race_ID", 0))
            race_number = (
                int(row.get("race_number", 0))
                if pd.notna(row.get("race_number"))
                else 0
            )
            race_time = str(row.get("race_time", ""))
            course_id = (
                int(row.get("course_id", 0)) if pd.notna(row.get("course_id")) else 0
            )
            course = str(row.get("Course", "")).replace("'", "''")
            race_type = str(row.get("Race_type", "")).replace("'", "''")
            date = str(row.get("Date", "2025-08-26"))
            race_name = str(row.get("Race_name", "")).replace("'", "''")[:200]
            race_class = str(row.get("Class", "")).replace("'", "''")
            years = str(row.get("Years", "")).replace("'", "''")
            distance = str(row.get("Distance", "")).replace("'", "''")
            surface = str(row.get("Surface", "")).replace("'", "''")
            prize = str(row.get("Prize", "")).replace("'", "''")
            runners_racecard = (
                int(row.get("Runners_racecard", 0))
                if pd.notna(row.get("Runners_racecard"))
                else 0
            )
            runners = int(row.get("Runners", 0)) if pd.notna(row.get("Runners")) else 0
            draw = str(row.get("Draw", ""))
            ew_racecard = (
                int(row.get("EW_racecard", 0))
                if pd.notna(row.get("EW_racecard"))
                else 0
            )
            ew = int(row.get("EW", 0)) if pd.notna(row.get("EW")) else 0
            places_ew_racecard = (
                int(row.get("Places_EW_racecard", 0))
                if pd.notna(row.get("Places_EW_racecard"))
                else 0
            )
            places_ew = (
                int(row.get("Places_EW", 0)) if pd.notna(row.get("Places_EW")) else 0
            )

            values_list.append(
                f"({race_id},{race_number},'{race_time}',{course_id},'{course}','{race_type}','{date}','{race_name}','{race_class}','{years}','{distance}','{surface}','{prize}',{runners_racecard},{runners},'{draw}',{ew_racecard},{ew},{places_ew_racecard},{places_ew})"
            )

        if values_list:
            # Split into batches
            batch_size = 50
            total_inserted = 0

            for i in range(0, len(values_list), batch_size):
                batch = values_list[i : i + batch_size]
                values_str = ",".join(batch)

                sql = f"""
                INSERT INTO races (race_id, race_number, race_time, course_id, course, race_type, date, race_name, class, years, distance, surface, prize, runners_racecard, runners, draw, ew_racecard, ew, places_ew_racecard, places_ew)
                VALUES {values_str};
                """

                if execute_sql("results", sql):
                    total_inserted += len(batch)

            logger.info(f"Successfully inserted {total_inserted} races")
            return total_inserted > 0

        return False

    except Exception as e:
        logger.error(f"Failed to load races: {e}")
        return False


def load_records_data(csv_path):
    """Load race records/results data"""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loading {len(df)} race records...")

        # Build bulk insert
        values_list = []
        for _, row in df.iterrows():
            race_id = int(row.get("Race_ID", 0)) if pd.notna(row.get("Race_ID")) else 0
            horse_number = (
                int(row.get("Horse_number", 0))
                if pd.notna(row.get("Horse_number"))
                else 0
            )
            place = int(row.get("Place", 0)) if pd.notna(row.get("Place")) else 0
            draw = int(row.get("Draw", 0)) if pd.notna(row.get("Draw")) else 0
            horse_id = (
                int(row.get("Horse_ID", 0)) if pd.notna(row.get("Horse_ID")) else 0
            )
            horse_name = str(row.get("Name", "")).replace("'", "''")[:100]
            country = str(row.get("Country", "GB"))[:10]
            age = int(row.get("Age", 0)) if pd.notna(row.get("Age")) else 0
            weight_uk = str(row.get("weight_uk", ""))[:20]
            weight = float(row.get("weight", 0)) if pd.notna(row.get("weight")) else 0.0
            jockey_id = (
                int(row.get("jockey_ID", 0)) if pd.notna(row.get("jockey_ID")) else 0
            )
            jockey_name = str(row.get("jockey", "")).replace("'", "''")[:100]
            trainer_id = (
                int(row.get("trainer_ID", 0)) if pd.notna(row.get("trainer_ID")) else 0
            )
            trainer_name = str(row.get("trainer", "")).replace("'", "''")[:100]
            fav = str(row.get("fav", ""))[:10]
            sp = float(row.get("SP", 0)) if pd.notna(row.get("SP")) else 0.0
            distance_btn = str(row.get("Distance_btn", ""))[:20]

            if race_id > 0:  # Only include records with valid race_id
                values_list.append(
                    f"({race_id},{horse_number},{place},{draw},{horse_id},'{horse_name}','{country}',{age},'{weight_uk}',{weight},{jockey_id},'{jockey_name}',{trainer_id},'{trainer_name}','{fav}',{sp},'{distance_btn}')"
                )

        if values_list:
            # Split into batches
            batch_size = 50
            total_inserted = 0

            for i in range(0, len(values_list), batch_size):
                batch = values_list[i : i + batch_size]
                values_str = ",".join(batch)

                sql = f"""
                INSERT INTO race_results (race_id, horse_number, place, draw, horse_id, horse_name, country, age, weight_uk, weight, jockey_id, jockey_name, trainer_id, trainer_name, fav, sp, distance_btn)
                VALUES {values_str};
                """

                if execute_sql("results", sql):
                    total_inserted += len(batch)

            logger.info(f"Successfully inserted {total_inserted} race results")
            return total_inserted > 0

        return False

    except Exception as e:
        logger.error(f"Failed to load race records: {e}")
        return False


def validate_racing_data():
    """Validate loaded racing data"""
    try:
        results = {}
        tables = [
            "races",
            "race_results",
            "horses_entity",
            "jockeys_entity",
            "trainers_entity",
        ]

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
    parser = argparse.ArgumentParser(description="Complete racing data loader v2.05")
    parser.add_argument("--dataset", default="2025-08-26", help="Dataset date")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / args.dataset

    start_time = time.time()
    logger.info(f"Starting complete racing data load for {args.dataset}")

    # Create racing schema
    create_racing_tables()

    # Load racing data
    success = True

    # Load races
    races_csv = data_dir / "races" / "races.csv"
    if races_csv.exists():
        success &= load_races_data(races_csv)
    else:
        logger.warning(f"Races CSV not found: {races_csv}")

    # Load records (race results)
    records_csv = data_dir / "records" / "records.csv"
    if records_csv.exists():
        success &= load_records_data(records_csv)
    else:
        logger.warning(f"Records CSV not found: {records_csv}")

    # Validate results
    validation_results = validate_racing_data()

    duration = time.time() - start_time
    logger.info(f"Complete racing data loading completed in {duration:.2f} seconds")

    if validation_results and sum(validation_results.values()) > 0:
        total_records = sum(validation_results.values())
        print(f"\\n✅ Complete Racing Data Load Successful!")
        print(f"📊 Complete Dataset Summary:")
        for table, count in validation_results.items():
            print(f"   {table}: {count:,} records")
        print(f"\\n📈 Total Records: {total_records:,}")
        print(f"🏇 Ready for realistic racing simulation testing!")
        return 0
    else:
        print(f"\\n❌ Complete Racing Data Load Failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
