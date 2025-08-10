#!/usr/bin/env python3
"""
Update Database Schema to BIGINT
===============================

Update all ID columns to BIGINT to handle large horse racing database IDs.
Horse racing databases often use very large ID values (100M+) that exceed
standard INTEGER limits but are well within BIGINT range.
"""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def update_schema_to_bigint():
    """Update all ID columns in the database to BIGINT"""
    print("🔧 Updating Database Schema to BIGINT")
    print("=" * 60)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False

    try:
        conn = psycopg2.connect(database_url)
        with conn.cursor() as cur:

            # Schema updates for all ID columns
            schema_updates = [
                # Race Results table
                "ALTER TABLE race_results ALTER COLUMN race_result_id TYPE BIGINT",
                "ALTER TABLE race_results ALTER COLUMN race_id TYPE BIGINT",
                "ALTER TABLE race_results ALTER COLUMN horse_id TYPE BIGINT",
                "ALTER TABLE race_results ALTER COLUMN jockey_id TYPE BIGINT",
                "ALTER TABLE race_results ALTER COLUMN trainer_id TYPE BIGINT",
                # Horses table
                "ALTER TABLE horses ALTER COLUMN horse_id_numeric TYPE BIGINT",
                # Jockey Stats table
                "ALTER TABLE jockey_stats ALTER COLUMN jockey_id TYPE BIGINT",
                # Trainer Stats table
                "ALTER TABLE trainer_stats ALTER COLUMN trainer_id TYPE BIGINT",
                # Races Cards table
                "ALTER TABLE races_cards ALTER COLUMN race_id TYPE BIGINT",
                # Racecard Details table
                "ALTER TABLE racecard_details ALTER COLUMN racecard_id TYPE BIGINT",
                "ALTER TABLE racecard_details ALTER COLUMN race_id TYPE BIGINT",
                "ALTER TABLE racecard_details ALTER COLUMN horse_id TYPE BIGINT",
                "ALTER TABLE racecard_details ALTER COLUMN jockey_id TYPE BIGINT",
                "ALTER TABLE racecard_details ALTER COLUMN trainer_id TYPE BIGINT",
            ]

            print("📊 Checking current column types...")

            # Check current column types before update
            check_columns_sql = """
                SELECT table_name, column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND column_name LIKE '%id%'
                AND data_type = 'integer'
                ORDER BY table_name, column_name;
            """

            cur.execute(check_columns_sql)
            integer_columns = cur.fetchall()

            if integer_columns:
                print(f"Found {len(integer_columns)} INTEGER ID columns to update:")
                for table, column, dtype in integer_columns:
                    print(f"  {table}.{column} ({dtype})")
            else:
                print("No INTEGER ID columns found - schema may already be updated")

            print(f"\n🔄 Applying {len(schema_updates)} schema updates...")

            success_count = 0
            for i, update_sql in enumerate(schema_updates, 1):
                try:
                    print(f"  {i:2d}. {update_sql}")
                    cur.execute(update_sql)
                    print(f"      ✅ Success")
                    success_count += 1
                except Exception as e:
                    if "does not exist" in str(e):
                        print(f"      ⏭️ Column doesn't exist - skipping")
                    elif "already" in str(e).lower():
                        print(f"      ✅ Already BIGINT - skipping")
                    else:
                        print(f"      ❌ Error: {e}")

            # Commit all changes
            conn.commit()

            print(f"\n📊 Verifying updates...")

            # Check column types after update
            cur.execute(check_columns_sql)
            remaining_integer_columns = cur.fetchall()

            if remaining_integer_columns:
                print(
                    f"⚠️ {len(remaining_integer_columns)} INTEGER ID columns still remain:"
                )
                for table, column, dtype in remaining_integer_columns:
                    print(f"  {table}.{column} ({dtype})")
            else:
                print("✅ All ID columns successfully updated to BIGINT!")

            # Show final column types for ID columns
            final_check_sql = """
                SELECT table_name, column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND column_name LIKE '%id%'
                ORDER BY table_name, column_name;
            """

            cur.execute(final_check_sql)
            all_id_columns = cur.fetchall()

            print(f"\n📋 Final ID column types:")
            for table, column, dtype in all_id_columns:
                status = "✅" if dtype == "bigint" else "⚠️"
                print(f"  {status} {table}.{column} ({dtype})")

        conn.close()
        print(f"\n🎉 Schema update completed! {success_count} updates applied.")
        return True

    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        return False


if __name__ == "__main__":
    success = update_schema_to_bigint()
    exit(0 if success else 1)
