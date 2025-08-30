#!/usr/bin/env python3
"""PostgreSQL Test Data Loader v2.05 - Simplified"""

import pandas as pd
import os
import sys
import time
from pathlib import Path
import argparse
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


class PostgreSQLTestLoader:
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
        tables = ["horses_entity", "jockeys_entity", "trainers_entity"]
        for table in tables:
            sql = f"DELETE FROM {table};"
            self.execute_sql("results", sql)
            logger.info(f"Cleared {table}")

    def load_horses(self, csv_path):
        """Load horses data"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loading {len(df)} horses...")

            for _, row in df.iterrows():
                horse_id = str(row.get("horse_id", ""))
                horse_name = str(row.get("horse_name", "")).replace("'", "''")
                country = str(row.get("country", "Unknown"))
                age = int(row.get("age", 0)) if pd.notna(row.get("age")) else 0
                colour = str(row.get("colour", "Unknown"))
                sex = str(row.get("sex", "Unknown"))
                owner = str(row.get("owner", "Unknown")).replace("'", "''")
                trainer = str(row.get("trainer", "Unknown")).replace("'", "''")
                sire = str(row.get("sire", "Unknown")).replace("'", "''")
                dam = str(row.get("dam", "Unknown")).replace("'", "''")
                dam_sire = str(row.get("dam_sire", "Unknown")).replace("'", "''")

                sql = f"""
                INSERT INTO horses_entity (
                    horse_id, horse_name, country, age, colour, sex,
                    owner, trainer, sire, dam, dam_sire, is_active
                ) VALUES (
                    '{horse_id}', '{horse_name}', '{country}', {age},
                    '{colour}', '{sex}', '{owner}', '{trainer}',
                    '{sire}', '{dam}', '{dam_sire}', true
                );"""

                self.execute_sql("results", sql)

            logger.info(f"Successfully loaded {len(df)} horses")
            return True

        except Exception as e:
            logger.error(f"Failed to load horses: {e}")
            return False

    def load_jockeys(self, csv_path):
        """Load jockeys data"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loading {len(df)} jockeys...")

            for _, row in df.iterrows():
                jockey_id = str(row.get("jockey_id", ""))
                jockey_name = str(row.get("jockey_name", "")).replace("'", "''")
                allowance = "true" if row.get("allowance_claimed") else "false"
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

                sql = f"""
                INSERT INTO jockeys_entity (
                    jockey_id, jockey_name, allowance_claimed, total_races,
                    total_wins, win_percentage, total_placed, place_percentage, is_active
                ) VALUES (
                    '{jockey_id}', '{jockey_name}', {allowance}, {total_races},
                    {total_wins}, {win_pct:.2f}, {total_placed}, {place_pct:.2f}, true
                );"""

                self.execute_sql("results", sql)

            logger.info(f"Successfully loaded {len(df)} jockeys")
            return True

        except Exception as e:
            logger.error(f"Failed to load jockeys: {e}")
            return False

    def load_trainers(self, csv_path):
        """Load trainers data"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loading {len(df)} trainers...")

            for _, row in df.iterrows():
                trainer_id = str(row.get("trainer_id", ""))
                trainer_name = str(row.get("trainer_name", "")).replace("'", "''")
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

                sql = f"""
                INSERT INTO trainers_entity (
                    trainer_id, trainer_name, total_runners, total_wins,
                    win_percentage, total_placed, place_percentage,
                    flat_runners, flat_wins, flat_win_rate,
                    jumps_runners, jumps_wins, jumps_win_rate, is_active
                ) VALUES (
                    '{trainer_id}', '{trainer_name}', {total_runners}, {total_wins},
                    {win_pct:.2f}, {total_placed}, {place_pct:.2f},
                    {flat_runners}, {flat_wins}, {flat_win_rate:.2f},
                    {jumps_runners}, {jumps_wins}, {jumps_win_rate:.2f}, true
                );"""

                self.execute_sql("results", sql)

            logger.info(f"Successfully loaded {len(df)} trainers")
            return True

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
        """Load complete test dataset"""
        start_time = time.time()
        logger.info(f"Loading PostgreSQL test data for {dataset_date}")

        data_dir = self.project_root / "data" / dataset_date

        # Clear existing data
        self.clear_tables()

        # Load entity data
        success = True

        horses_csv = data_dir / "horses" / "horses.csv"
        if horses_csv.exists():
            success &= self.load_horses(horses_csv)

        jockeys_csv = data_dir / "jockeys_stats" / "jockeys_stats.csv"
        if jockeys_csv.exists():
            success &= self.load_jockeys(jockeys_csv)

        trainers_csv = data_dir / "trainers_stats" / "trainers_stats.csv"
        if trainers_csv.exists():
            success &= self.load_trainers(trainers_csv)

        # Validate results
        validation_results = self.validate_load()

        duration = time.time() - start_time
        logger.info(f"Data loading completed in {duration:.2f} seconds")

        return validation_results if success else False


def main():
    parser = argparse.ArgumentParser(description="Load PostgreSQL test data v2.05")
    parser.add_argument("--dataset", default="2025-08-26", help="Dataset date")
    args = parser.parse_args()

    loader = PostgreSQLTestLoader()
    results = loader.load_test_dataset(args.dataset)

    if results:
        print(f"\n✅ PostgreSQL Test Data Load Complete!")
        print(f"📊 Results Summary:")
        for table, count in results.items():
            print(f"   {table}: {count:,} records")
        print(f"\n🚀 Ready for comprehensive testing!")
        return 0
    else:
        print(f"\n❌ PostgreSQL Test Data Load Failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
