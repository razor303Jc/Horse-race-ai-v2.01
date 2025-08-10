#!/usr/bin/env python3
"""
Clear Database Data
==================

Safely clear all data from horse racing tables for fresh testing.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def clear_database_data():
    """Clear all data from horse racing tables"""
    print("🗄️ Clearing Database Data")
    print("=" * 50)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False

    try:
        import psycopg2

        conn = psycopg2.connect(database_url)
        with conn.cursor() as cur:

            # First, check current record counts
            tables = [
                "race_results",
                "jockey_stats",
                "trainer_stats",
                "horses",
                "races_cards",
                "racecard_details",
            ]

            print("📊 Current record counts:")
            for table in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cur.fetchone()[0]
                    print(f"  {table}: {count:,} records")
                except Exception as e:
                    print(f"  {table}: Error counting - {e}")

            print("\n🧹 Clearing table data...")

            # Clear data from all tables (TRUNCATE is faster than DELETE)
            for table in tables:
                try:
                    cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
                    print(f"  ✅ Cleared {table}")
                except Exception as e:
                    print(f"  ❌ Error clearing {table}: {e}")

            # Commit the changes
            conn.commit()

            print("\n📊 Final record counts:")
            for table in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cur.fetchone()[0]
                    print(f"  {table}: {count:,} records")
                except Exception as e:
                    print(f"  {table}: Error counting - {e}")

        conn.close()
        print("\n✅ Database cleared successfully!")
        return True

    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False


if __name__ == "__main__":
    success = clear_database_data()
    exit(0 if success else 1)
