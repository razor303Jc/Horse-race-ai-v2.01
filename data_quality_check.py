#!/usr/bin/env python3
"""
Data Quality Check Script
========================
Check the actual data in the database tables to identify potential issues
"""

import subprocess
import sys
import os

# Add project root to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.05")
from config.database_config import db_config


def run_sql_query(query, description):
    """Run SQL query and return results"""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")

    cmd = db_config.get_docker_exec_command("results", f'psql -c "{query}"')
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Exception: {e}")


def main():
    print("🏇 Database Data Quality Analysis")
    print("=" * 60)

    # 1. Check horses_entity data
    run_sql_query(
        "SELECT COUNT(*) as total, MIN(horse_id) as min_id, MAX(horse_id) as max_id, COUNT(DISTINCT horse_id) as unique_ids FROM horses_entity;",
        "Horses Entity - ID Distribution",
    )

    run_sql_query(
        "SELECT horse_id, horse_name, age, sex, trainer, rating FROM horses_entity LIMIT 5;",
        "Horses Entity - Sample Data",
    )

    # 2. Check jockeys_entity data
    run_sql_query(
        "SELECT COUNT(*) as total, MIN(jockey_id) as min_id, MAX(jockey_id) as max_id, COUNT(DISTINCT jockey_id) as unique_ids FROM jockeys_entity;",
        "Jockeys Entity - ID Distribution",
    )

    run_sql_query(
        "SELECT jockey_id, jockey_name, claim_allowance, wins, runs, win_rate FROM jockeys_entity LIMIT 5;",
        "Jockeys Entity - Sample Data",
    )

    # 3. Check trainers_entity data
    run_sql_query(
        "SELECT COUNT(*) as total, MIN(trainer_id) as min_id, MAX(trainer_id) as max_id, COUNT(DISTINCT trainer_id) as unique_ids FROM trainers_entity;",
        "Trainers Entity - ID Distribution",
    )

    run_sql_query(
        "SELECT trainer_id, trainer_name, total_races, wins, win_percentage FROM trainers_entity LIMIT 5;",
        "Trainers Entity - Sample Data",
    )

    # 4. Check races data
    run_sql_query(
        "SELECT COUNT(*) as total, MIN(race_id) as min_id, MAX(race_id) as max_id, COUNT(DISTINCT race_id) as unique_ids FROM races;",
        "Races - ID Distribution",
    )

    run_sql_query(
        "SELECT race_id, race_number, course, race_type, date, race_name FROM races LIMIT 5;",
        "Races - Sample Data",
    )

    # 5. Check race_results data - THE CRITICAL ONE
    run_sql_query(
        "SELECT COUNT(*) as total, MIN(race_id) as min_race_id, MAX(race_id) as max_race_id, COUNT(DISTINCT race_id) as unique_race_ids FROM race_results;",
        "Race Results - Race ID Distribution",
    )

    run_sql_query(
        "SELECT race_id, horse_name, place, jockey_name, trainer_name, sp FROM race_results LIMIT 10;",
        "Race Results - Sample Data",
    )

    # 6. Check for data integrity issues
    run_sql_query(
        "SELECT place, COUNT(*) as count FROM race_results GROUP BY place ORDER BY place;",
        "Race Results - Place Code Distribution (Check our mapping worked)",
    )

    run_sql_query(
        "SELECT COUNT(*) as results_count, COUNT(DISTINCT race_id) as unique_races FROM race_results;",
        "Race Results - Results per Race Analysis",
    )

    # 7. Check for orphaned data
    run_sql_query(
        "SELECT COUNT(*) as orphaned_results FROM race_results r LEFT JOIN races ra ON r.race_id = ra.race_id WHERE ra.race_id IS NULL;",
        "Data Integrity - Orphaned Race Results (results without races)",
    )

    print(f"\n{'='*60}")
    print("✅ Data Quality Analysis Complete")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
