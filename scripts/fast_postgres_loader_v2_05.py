#!/usr/bin/env python3
"""
Fast PostgreSQL Data Loader v2.05 using COPY command
Load 2025-08-26 dataset into PostgreSQL entity tables efficiently
"""

import pandas as pd
import os
import sys
import time
from pathlib import Path
import argparse
import logging
import subprocess
import tempfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


class FastPostgreSQLLoader:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent

    def execute_sql(self, database, sql):
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

    def clear_tables(self):
        """Clear existing entity data"""
        logger.info("Clearing existing entity tables...")
        tables = ["horses_entity", "jockeys_entity", "trainers_entity"]
        for table in tables:
            sql = f"DELETE FROM {table};"
            self.execute_sql("results", sql)
            logger.info(f"Cleared {table}")

    def copy_csv_to_container(self, local_path, container_path="/tmp/data.csv"):
        """Copy CSV file to Docker container"""
        try:
            cmd = [
                "docker",
                "cp",
                str(local_path),
                f"horse_racing_postgres_clean:{container_path}",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to copy file to container: {e}")
            return False

    def load_horses_fast(self, csv_path):
        """Load horses using PostgreSQL COPY command"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Processing {len(df)} horses for bulk load...")

            # Create temporary CSV with correct format
            processed_data = []
            for _, row in df.iterrows():
                # Skip rows with missing id
                if pd.isna(row.get("id")) or str(row.get("id")).strip() == "":
                    continue

                processed_data.append(
                    {
                        "horse_id": str(row.get("id", "")),
                        "horse_name": str(row.get("name", "")).replace("'", "''"),
                        "country": str(row.get("country", "Unknown")),
                        "age": (
                            int(row.get("age", 0)) if pd.notna(row.get("age")) else 0
                        ),
                        "colour": str(
                            row.get("color", "Unknown")
                        ),  # Note: CSV has 'color' not 'colour'
                        "sex": str(row.get("sex", "Unknown")),
                        "owner": str(row.get("owner", "Unknown")).replace("'", "''"),
                        "trainer": "Unknown",  # Not in this CSV
                        "sire": str(row.get("sire", "Unknown")).replace("'", "''"),
                        "dam": str(row.get("dam", "Unknown")).replace("'", "''"),
                        "dam_sire": str(row.get("dam_sire", "Unknown")).replace(
                            "'", "''"
                        ),
                        "is_active": True,
                    }
                )

            if not processed_data:
                logger.warning("No valid horse data to load")
                return False

            # Create temporary CSV file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as tmp_file:
                tmp_file.write(
                    "horse_id,horse_name,country,age,colour,sex,owner,trainer,sire,dam,dam_sire,is_active\\n"
                )
                for horse in processed_data:
                    tmp_file.write(
                        f"{horse['horse_id']},{horse['horse_name']},{horse['country']},{horse['age']},{horse['colour']},{horse['sex']},{horse['owner']},{horse['trainer']},{horse['sire']},{horse['dam']},{horse['dam_sire']},{horse['is_active']}\\n"
                    )
                tmp_csv_path = tmp_file.name

            # Copy to container
            if not self.copy_csv_to_container(tmp_csv_path):
                os.unlink(tmp_csv_path)
                return False

            # Execute COPY command
            copy_sql = """
            COPY horses_entity (horse_id, horse_name, country, age, colour, sex, owner, trainer, sire, dam, dam_sire, is_active)
            FROM '/tmp/data.csv' WITH CSV HEADER;
            """

            success = self.execute_sql("results", copy_sql)

            # Cleanup
            os.unlink(tmp_csv_path)
            subprocess.run(
                ["docker", "exec", "horse_racing_postgres_clean", "rm", "/tmp/data.csv"]
            )

            if success:
                logger.info(f"Successfully bulk loaded {len(processed_data)} horses")
            return success

        except Exception as e:
            logger.error(f"Failed to load horses: {e}")
            return False

    def load_jockeys_fast(self, csv_path):
        """Load jockeys using PostgreSQL COPY command"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Processing {len(df)} jockeys for bulk load...")

            # Create temporary CSV with correct format
            processed_data = []
            for _, row in df.iterrows():
                # Skip rows with missing jockey_id
                if (
                    pd.isna(row.get("jockey_id"))
                    or str(row.get("jockey_id")).strip() == ""
                ):
                    continue

                total_races = (
                    int(row.get("total_races", 0))
                    if pd.notna(row.get("total_races"))
                    else 0
                )
                total_wins = (
                    int(row.get("total_wins", 0))
                    if pd.notna(row.get("total_wins"))
                    else 0
                )
                total_placed = (
                    int(row.get("total_placed", 0))
                    if pd.notna(row.get("total_placed"))
                    else 0
                )

                win_pct = (total_wins / total_races * 100) if total_races > 0 else 0.0
                place_pct = (
                    (total_placed / total_races * 100) if total_races > 0 else 0.0
                )

                processed_data.append(
                    {
                        "jockey_id": str(row.get("jockey_id", "")),
                        "jockey_name": str(row.get("jockey_name", "")).replace(
                            "'", "''"
                        ),
                        "allowance_claimed": bool(row.get("allowance_claimed", False)),
                        "total_races": total_races,
                        "total_wins": total_wins,
                        "win_percentage": round(win_pct, 2),
                        "total_placed": total_placed,
                        "place_percentage": round(place_pct, 2),
                        "is_active": True,
                    }
                )

            if not processed_data:
                logger.warning("No valid jockey data to load")
                return False

            # Create temporary CSV file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as tmp_file:
                tmp_file.write(
                    "jockey_id,jockey_name,allowance_claimed,total_races,total_wins,win_percentage,total_placed,place_percentage,is_active\\n"
                )
                for jockey in processed_data:
                    tmp_file.write(
                        f"{jockey['jockey_id']},{jockey['jockey_name']},{jockey['allowance_claimed']},{jockey['total_races']},{jockey['total_wins']},{jockey['win_percentage']},{jockey['total_placed']},{jockey['place_percentage']},{jockey['is_active']}\\n"
                    )
                tmp_csv_path = tmp_file.name

            # Copy to container and execute COPY
            if not self.copy_csv_to_container(tmp_csv_path):
                os.unlink(tmp_csv_path)
                return False

            copy_sql = """
            COPY jockeys_entity (jockey_id, jockey_name, allowance_claimed, total_races, total_wins, win_percentage, total_placed, place_percentage, is_active)
            FROM '/tmp/data.csv' WITH CSV HEADER;
            """

            success = self.execute_sql("results", copy_sql)

            # Cleanup
            os.unlink(tmp_csv_path)
            subprocess.run(
                ["docker", "exec", "horse_racing_postgres_clean", "rm", "/tmp/data.csv"]
            )

            if success:
                logger.info(f"Successfully bulk loaded {len(processed_data)} jockeys")
            return success

        except Exception as e:
            logger.error(f"Failed to load jockeys: {e}")
            return False

    def load_trainers_fast(self, csv_path):
        """Load trainers using PostgreSQL COPY command"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Processing {len(df)} trainers for bulk load...")

            # Create temporary CSV with correct format
            processed_data = []
            for _, row in df.iterrows():
                # Skip rows with missing trainer_id
                if (
                    pd.isna(row.get("trainer_id"))
                    or str(row.get("trainer_id")).strip() == ""
                ):
                    continue

                total_runners = (
                    int(row.get("total_runners", 0))
                    if pd.notna(row.get("total_runners"))
                    else 0
                )
                total_wins = (
                    int(row.get("total_wins", 0))
                    if pd.notna(row.get("total_wins"))
                    else 0
                )
                total_placed = (
                    int(row.get("total_placed", 0))
                    if pd.notna(row.get("total_placed"))
                    else 0
                )

                flat_runners = (
                    int(row.get("flat_runners", 0))
                    if pd.notna(row.get("flat_runners"))
                    else 0
                )
                flat_wins = (
                    int(row.get("flat_wins", 0))
                    if pd.notna(row.get("flat_wins"))
                    else 0
                )
                jumps_runners = (
                    int(row.get("jumps_runners", 0))
                    if pd.notna(row.get("jumps_runners"))
                    else 0
                )
                jumps_wins = (
                    int(row.get("jumps_wins", 0))
                    if pd.notna(row.get("jumps_wins"))
                    else 0
                )

                win_pct = (
                    (total_wins / total_runners * 100) if total_runners > 0 else 0.0
                )
                place_pct = (
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
                        "trainer_name": str(row.get("trainer_name", "")).replace(
                            "'", "''"
                        ),
                        "total_runners": total_runners,
                        "total_wins": total_wins,
                        "win_percentage": round(win_pct, 2),
                        "total_placed": total_placed,
                        "place_percentage": round(place_pct, 2),
                        "flat_runners": flat_runners,
                        "flat_wins": flat_wins,
                        "flat_win_rate": round(flat_win_rate, 2),
                        "jumps_runners": jumps_runners,
                        "jumps_wins": jumps_wins,
                        "jumps_win_rate": round(jumps_win_rate, 2),
                        "is_active": True,
                    }
                )

            if not processed_data:
                logger.warning("No valid trainer data to load")
                return False

            # Create temporary CSV file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as tmp_file:
                tmp_file.write(
                    "trainer_id,trainer_name,total_runners,total_wins,win_percentage,total_placed,place_percentage,flat_runners,flat_wins,flat_win_rate,jumps_runners,jumps_wins,jumps_win_rate,is_active\\n"
                )
                for trainer in processed_data:
                    tmp_file.write(
                        f"{trainer['trainer_id']},{trainer['trainer_name']},{trainer['total_runners']},{trainer['total_wins']},{trainer['win_percentage']},{trainer['total_placed']},{trainer['place_percentage']},{trainer['flat_runners']},{trainer['flat_wins']},{trainer['flat_win_rate']},{trainer['jumps_runners']},{trainer['jumps_wins']},{trainer['jumps_win_rate']},{trainer['is_active']}\\n"
                    )
                tmp_csv_path = tmp_file.name

            # Copy to container and execute COPY
            if not self.copy_csv_to_container(tmp_csv_path):
                os.unlink(tmp_csv_path)
                return False

            copy_sql = """
            COPY trainers_entity (trainer_id, trainer_name, total_runners, total_wins, win_percentage, total_placed, place_percentage, flat_runners, flat_wins, flat_win_rate, jumps_runners, jumps_wins, jumps_win_rate, is_active)
            FROM '/tmp/data.csv' WITH CSV HEADER;
            """

            success = self.execute_sql("results", copy_sql)

            # Cleanup
            os.unlink(tmp_csv_path)
            subprocess.run(
                ["docker", "exec", "horse_racing_postgres_clean", "rm", "/tmp/data.csv"]
            )

            if success:
                logger.info(f"Successfully bulk loaded {len(processed_data)} trainers")
            return success

        except Exception as e:
            logger.error(f"Failed to load trainers: {e}")
            return False

    def validate_load(self):
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

    def load_test_dataset(self, dataset_date="2025-08-26"):
        """Load complete test dataset using fast COPY method"""
        start_time = time.time()
        logger.info(
            f"Loading PostgreSQL test data for {dataset_date} using fast COPY method"
        )

        data_dir = self.project_root / "data" / dataset_date

        # Clear existing data
        self.clear_tables()

        # Load entity data using fast method
        success = True

        # Load horses (using 'id' column from CSV)
        horses_csv = data_dir / "horses" / "horses.csv"
        if horses_csv.exists():
            success &= self.load_horses_fast(horses_csv)
        else:
            logger.warning(f"Horses CSV not found: {horses_csv}")

        # Load jockeys
        jockeys_csv = data_dir / "jockeys_stats" / "jockeys_stats.csv"
        if jockeys_csv.exists():
            success &= self.load_jockeys_fast(jockeys_csv)
        else:
            logger.warning(f"Jockeys CSV not found: {jockeys_csv}")

        # Load trainers
        trainers_csv = data_dir / "trainers_stats" / "trainers_stats.csv"
        if trainers_csv.exists():
            success &= self.load_trainers_fast(trainers_csv)
        else:
            logger.warning(f"Trainers CSV not found: {trainers_csv}")

        # Validate results
        validation_results = self.validate_load()

        duration = time.time() - start_time
        logger.info(f"Fast data loading completed in {duration:.2f} seconds")

        return validation_results if success else False


def main():
    parser = argparse.ArgumentParser(description="Fast PostgreSQL data loader v2.05")
    parser.add_argument("--dataset", default="2025-08-26", help="Dataset date")
    args = parser.parse_args()

    loader = FastPostgreSQLLoader()
    results = loader.load_test_dataset(args.dataset)

    if results:
        total_records = sum(results.values())
        print(f"\\n✅ Fast PostgreSQL Data Load Complete!")
        print(f"📊 Results Summary:")
        for table, count in results.items():
            print(f"   {table}: {count:,} records")
        print(f"\\n📈 Total Records Loaded: {total_records:,}")
        print(f"🚀 Ready for comprehensive testing with real data!")
        return 0
    else:
        print(f"\\n❌ PostgreSQL Data Load Failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
