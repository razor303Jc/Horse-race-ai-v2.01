#!/usr/bin/env python3
"""
PostgreSQL Test Data Loader v2.05
Load 2025-08-26 dataset into PostgreSQL entity tables for comprehensive testing
"""

import pandas as pd
import psycopg2
import psycopg2.extras
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PostgreSQLTestDataLoader:
    def __init__(
        self,
        host="localhost",
        port=5432,
        user="horse_racing",
        password="secure_password_123",
        use_docker=True,
    ):
        self.use_docker = use_docker
        self.connection_params = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
        }
        self.project_root = Path(__file__).parent.parent

    def connect_to_database(self, database_name):
        """Connect to specific PostgreSQL database"""
        try:
            if self.use_docker:
                # For Docker container, use internal connection
                import subprocess

                return True  # We'll use docker exec for operations
            else:
                conn = psycopg2.connect(
                    database=database_name, **self.connection_params
                )
                return conn
        except Exception as e:
            logger.error(f"Failed to connect to database {database_name}: {e}")
            return None

    def execute_docker_sql(self, database, sql, data=None):
        """Execute SQL commands via Docker exec"""
        import subprocess
        import tempfile

        try:
            if data and len(data) > 0:
                # For bulk inserts, use COPY command
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".csv", delete=False
                ) as f:
                    # Convert data to CSV format
                    if isinstance(data[0], dict):
                        df = pd.DataFrame(data)
                        df.to_csv(f.name, index=False, header=False)

                    # Copy file to container
                    subprocess.run(
                        [
                            "docker",
                            "cp",
                            f.name,
                            f"horse_racing_postgres_clean:/tmp/data.csv",
                        ],
                        check=True,
                    )

                    # Execute COPY command
                    copy_sql = sql.replace("INSERT", "\\COPY").replace(
                        "VALUES", "FROM /tmp/data.csv CSV"
                    )
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
                        copy_sql,
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True)

                    # Cleanup
                    os.unlink(f.name)
                    subprocess.run(
                        [
                            "docker",
                            "exec",
                            "horse_racing_postgres_clean",
                            "rm",
                            "/tmp/data.csv",
                        ]
                    )

                    if result.returncode != 0:
                        logger.error(f"SQL execution failed: {result.stderr}")
                        return False
                    return True
            else:
                # Regular SQL command
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
                    logger.error(f"SQL execution failed: {result.stderr}")
                    return False
                return True

        except Exception as e:
            logger.error(f"Docker SQL execution failed: {e}")
            return False

    def load_csv_data(self, csv_path):
        """Load and process CSV data"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(df)} records from {csv_path}")
            return df
        except Exception as e:
            logger.error(f"Failed to load CSV {csv_path}: {e}")
            return None

    def process_horses_data(self, horses_df):
        """Process horses data for entity table"""
        processed_data = []
        for _, row in horses_df.iterrows():
            processed_data.append(
                {
                    "horse_id": str(row.get("horse_id", "")),
                    "horse_name": str(row.get("horse_name", "")),
                    "country": str(row.get("country", "Unknown")),
                    "age": int(row.get("age", 0)) if pd.notna(row.get("age", 0)) else 0,
                    "colour": str(row.get("colour", "Unknown")),
                    "sex": str(row.get("sex", "Unknown")),
                    "owner": str(row.get("owner", "Unknown")),
                    "trainer": str(row.get("trainer", "Unknown")),
                    "sire": str(row.get("sire", "Unknown")),
                    "dam": str(row.get("dam", "Unknown")),
                    "dam_sire": str(row.get("dam_sire", "Unknown")),
                    "is_active": True,
                }
            )
        return processed_data

    def process_jockeys_data(self, jockeys_df):
        """Process jockeys data for entity table"""
        processed_data = []
        for _, row in jockeys_df.iterrows():
            total_races = (
                int(row.get("total_races", 0))
                if pd.notna(row.get("total_races", 0))
                else 0
            )
            total_wins = (
                int(row.get("total_wins", 0))
                if pd.notna(row.get("total_wins", 0))
                else 0
            )
            total_placed = (
                int(row.get("total_placed", 0))
                if pd.notna(row.get("total_placed", 0))
                else 0
            )

            win_percentage = (
                (total_wins / total_races * 100) if total_races > 0 else 0.0
            )
            place_percentage = (
                (total_placed / total_races * 100) if total_races > 0 else 0.0
            )

            processed_data.append(
                {
                    "jockey_id": str(row.get("jockey_id", "")),
                    "jockey_name": str(row.get("jockey_name", "")),
                    "allowance_claimed": bool(row.get("allowance_claimed", False)),
                    "total_races": total_races,
                    "total_wins": total_wins,
                    "win_percentage": round(win_percentage, 2),
                    "total_placed": total_placed,
                    "place_percentage": round(place_percentage, 2),
                    "is_active": True,
                }
            )
        return processed_data

    def process_trainers_data(self, trainers_df):
        """Process trainers data for entity table"""
        processed_data = []
        for _, row in trainers_df.iterrows():
            total_runners = (
                int(row.get("total_runners", 0))
                if pd.notna(row.get("total_runners", 0))
                else 0
            )
            total_wins = (
                int(row.get("total_wins", 0))
                if pd.notna(row.get("total_wins", 0))
                else 0
            )
            total_placed = (
                int(row.get("total_placed", 0))
                if pd.notna(row.get("total_placed", 0))
                else 0
            )

            # Flat racing stats
            flat_runners = (
                int(row.get("flat_runners", 0))
                if pd.notna(row.get("flat_runners", 0))
                else 0
            )
            flat_wins = (
                int(row.get("flat_wins", 0)) if pd.notna(row.get("flat_wins", 0)) else 0
            )

            # Jumps racing stats
            jumps_runners = (
                int(row.get("jumps_runners", 0))
                if pd.notna(row.get("jumps_runners", 0))
                else 0
            )
            jumps_wins = (
                int(row.get("jumps_wins", 0))
                if pd.notna(row.get("jumps_wins", 0))
                else 0
            )

            # Calculate percentages
            win_percentage = (
                (total_wins / total_runners * 100) if total_runners > 0 else 0.0
            )
            place_percentage = (
                (total_placed / total_runners * 100) if total_runners > 0 else 0.0
            )
            flat_win_rate = (
                (flat_wins / flat_runners * 100) if flat_runners > 0 else 0.0
            )
            jumps_win_rate = (
                (jumps_wins / jumps_runners * 100) if jumps_runners > 0 else 0.0
            )

            processed_data.append(
                {
                    "trainer_id": str(row.get("trainer_id", "")),
                    "trainer_name": str(row.get("trainer_name", "")),
                    "total_runners": total_runners,
                    "total_wins": total_wins,
                    "win_percentage": round(win_percentage, 2),
                    "total_placed": total_placed,
                    "place_percentage": round(place_percentage, 2),
                    "flat_runners": flat_runners,
                    "flat_wins": flat_wins,
                    "flat_win_rate": round(flat_win_rate, 2),
                    "jumps_runners": jumps_runners,
                    "jumps_wins": jumps_wins,
                    "jumps_win_rate": round(jumps_win_rate, 2),
                    "is_active": True,
                }
            )
        return processed_data

    def bulk_insert_entities(self, table_name, data_list, database="results"):
        """Bulk insert entity data using PostgreSQL"""
        if not data_list:
            logger.warning(f"No data to insert for {table_name}")
            return False

        try:
            # Clear existing data first
            delete_sql = f"DELETE FROM {table_name};"
            self.execute_docker_sql(database, delete_sql)

            # Prepare bulk insert
            if table_name == "horses_entity":
                insert_sql = """
                INSERT INTO horses_entity (
                    horse_id, horse_name, country, age, colour, sex, 
                    owner, trainer, sire, dam, dam_sire, is_active
                ) VALUES %s
                """
                values = [
                    (
                        d["horse_id"],
                        d["horse_name"],
                        d["country"],
                        d["age"],
                        d["colour"],
                        d["sex"],
                        d["owner"],
                        d["trainer"],
                        d["sire"],
                        d["dam"],
                        d["dam_sire"],
                        d["is_active"],
                    )
                    for d in data_list
                ]
            elif table_name == "jockeys_entity":
                insert_sql = """
                INSERT INTO jockeys_entity (
                    jockey_id, jockey_name, allowance_claimed, total_races,
                    total_wins, win_percentage, total_placed, place_percentage, is_active
                ) VALUES %s
                """
                values = [
                    (
                        d["jockey_id"],
                        d["jockey_name"],
                        d["allowance_claimed"],
                        d["total_races"],
                        d["total_wins"],
                        d["win_percentage"],
                        d["total_placed"],
                        d["place_percentage"],
                        d["is_active"],
                    )
                    for d in data_list
                ]
            elif table_name == "trainers_entity":
                insert_sql = """
                INSERT INTO trainers_entity (
                    trainer_id, trainer_name, total_runners, total_wins,
                    win_percentage, total_placed, place_percentage,
                    flat_runners, flat_wins, flat_win_rate,
                    jumps_runners, jumps_wins, jumps_win_rate, is_active
                ) VALUES %s
                """
                values = [
                    (
                        d["trainer_id"],
                        d["trainer_name"],
                        d["total_runners"],
                        d["total_wins"],
                        d["win_percentage"],
                        d["total_placed"],
                        d["place_percentage"],
                        d["flat_runners"],
                        d["flat_wins"],
                        d["flat_win_rate"],
                        d["jumps_runners"],
                        d["jumps_wins"],
                        d["jumps_win_rate"],
                        d["is_active"],
                    )
                    for d in data_list
                ]

            # Execute via Docker with proper escaping
            values_str = ",".join(
                [
                    "("
                    + ",".join(
                        [f"'{str(v).replace(chr(39), chr(39)+chr(39))}'" for v in val]
                    )
                    + ")"
                    for val in values
                ]
            )
            full_sql = insert_sql.replace("%s", values_str)

            success = self.execute_docker_sql(database, full_sql)
            if success:
                logger.info(
                    f"Successfully inserted {len(data_list)} records into {table_name}"
                )
            return success

        except Exception as e:
            logger.error(f"Bulk insert failed for {table_name}: {e}")
            return False

    def validate_data_load(self, database="results"):
        """Validate the loaded data"""
        try:
            results = {}
            for table in ["horses_entity", "jockeys_entity", "trainers_entity"]:
                count_sql = f"SELECT COUNT(*) FROM {table};"
                # Get count via docker exec
                import subprocess

                cmd = [
                    "docker",
                    "exec",
                    "horse_racing_postgres_clean",
                    "psql",
                    "-U",
                    "horse_racing",
                    "-d",
                    database,
                    "-t",
                    "-c",
                    count_sql,
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    count = int(result.stdout.strip())
                    results[table] = count
                    logger.info(f"{table}: {count} records")
                else:
                    logger.error(f"Failed to count {table}: {result.stderr}")
                    results[table] = 0

            return results
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return {}

    def load_test_dataset(self, dataset_date="2025-08-26"):
        """Load complete test dataset for comprehensive testing"""
        start_time = time.time()
        logger.info(f"Starting PostgreSQL test data load for {dataset_date}")

        # Dataset paths
        data_dir = self.project_root / "data" / dataset_date

        # Load CSV files
        csv_files = {
            "horses": data_dir / "horses.csv",
            "jockeys_stats": data_dir / "jockeys_stats.csv",
            "trainers_stats": data_dir / "trainers_stats.csv",
        }

        # Verify files exist
        for name, path in csv_files.items():
            if not path.exists():
                logger.error(f"Required CSV file missing: {path}")
                return False

        # Load and process data
        try:
            # Horses
            horses_df = self.load_csv_data(csv_files["horses"])
            if horses_df is not None:
                horses_data = self.process_horses_data(horses_df)
                self.bulk_insert_entities("horses_entity", horses_data)

            # Jockeys
            jockeys_df = self.load_csv_data(csv_files["jockeys_stats"])
            if jockeys_df is not None:
                jockeys_data = self.process_jockeys_data(jockeys_df)
                self.bulk_insert_entities("jockeys_entity", jockeys_data)

            # Trainers
            trainers_df = self.load_csv_data(csv_files["trainers_stats"])
            if trainers_df is not None:
                trainers_data = self.process_trainers_data(trainers_df)
                self.bulk_insert_entities("trainers_entity", trainers_data)

            # Validate results
            validation_results = self.validate_data_load()

            end_time = time.time()
            duration = end_time - start_time

            logger.info(f"Data loading completed in {duration:.2f} seconds")
            logger.info(f"Validation results: {validation_results}")

            return validation_results

        except Exception as e:
            logger.error(f"Test data loading failed: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Load PostgreSQL test data for Horse Racing AI v2.05"
    )
    parser.add_argument("--dataset", default="2025-08-26", help="Dataset date to load")
    parser.add_argument(
        "--docker", action="store_true", default=True, help="Use Docker container"
    )
    parser.add_argument("--host", default="localhost", help="PostgreSQL host")
    parser.add_argument("--port", type=int, default=5432, help="PostgreSQL port")
    parser.add_argument("--user", default="horse_racing", help="PostgreSQL user")
    parser.add_argument(
        "--password", default="secure_password_123", help="PostgreSQL password"
    )

    args = parser.parse_args()

    # Initialize loader
    loader = PostgreSQLTestDataLoader(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        use_docker=args.docker,
    )

    # Load test dataset
    results = loader.load_test_dataset(args.dataset)

    if results:
        print(f"\n✅ PostgreSQL Test Data Load Complete!")
        print(f"📊 Results Summary:")
        for table, count in results.items():
            print(f"   {table}: {count:,} records")
        print(f"\n🚀 Ready for comprehensive testing with {args.dataset} dataset!")
        return 0
    else:
        print(f"\n❌ PostgreSQL Test Data Load Failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
