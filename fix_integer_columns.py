#!/usr/bin/env python3
"""
Fix Remaining Integer Columns
============================

Convert any remaining INTEGER columns to BIGINT with proper casting.
"""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def fix_remaining_integer_columns():
    """Fix any remaining INTEGER columns that need to be BIGINT"""
    print("🔧 Fixing Remaining Integer Columns")
    print("=" * 50)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False

    try:
        conn = psycopg2.connect(database_url)
        with conn.cursor() as cur:

            # Check which columns are still INTEGER
            check_sql = """
                SELECT table_name, column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND data_type = 'integer'
                AND (column_name LIKE '%id%' OR column_name LIKE '%_id' OR column_name = 'id')
                ORDER BY table_name, column_name;
            """

            cur.execute(check_sql)
            integer_columns = cur.fetchall()

            if not integer_columns:
                print("✅ No INTEGER ID columns found - all good!")
                return True

            print(f"Found {len(integer_columns)} INTEGER columns to fix:")
            for table, column, dtype in integer_columns:
                print(f"  {table}.{column} ({dtype})")

            print("\n🔄 Converting to BIGINT with proper casting...")

            success_count = 0
            for table, column, dtype in integer_columns:
                try:
                    # Use explicit casting to handle existing data
                    update_sql = f"ALTER TABLE {table} ALTER COLUMN {column} TYPE BIGINT USING {column}::BIGINT"
                    print(f"  Converting {table}.{column}...")
                    cur.execute(update_sql)
                    conn.commit()  # Commit each one individually
                    print(f"    ✅ Success")
                    success_count += 1
                except Exception as e:
                    conn.rollback()  # Rollback failed operation
                    print(f"    ❌ Error: {e}")

            print(f"\n✅ Converted {success_count} columns to BIGINT")

            # Final verification
            cur.execute(check_sql)
            remaining = cur.fetchall()

            if remaining:
                print(f"\n⚠️ {len(remaining)} INTEGER columns still remain:")
                for table, column, dtype in remaining:
                    print(f"  {table}.{column}")
            else:
                print("\n🎉 All ID columns are now BIGINT or VARCHAR!")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = fix_remaining_integer_columns()
    exit(0 if success else 1)
