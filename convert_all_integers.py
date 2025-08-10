#!/usr/bin/env python3
"""
Convert All Integer Columns to BIGINT
====================================

Convert ALL remaining INTEGER columns to BIGINT to handle any large values.
This is the safest approach for horse racing data.
"""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def convert_all_integers_to_bigint():
    """Convert ALL INTEGER columns to BIGINT"""
    print("🔧 Converting ALL Integer Columns to BIGINT")
    print("=" * 60)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False

    try:
        conn = psycopg2.connect(database_url)
        with conn.cursor() as cur:

            # Get all INTEGER columns
            all_integers_sql = """
                SELECT table_name, column_name
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND data_type = 'integer'
                ORDER BY table_name, column_name;
            """

            cur.execute(all_integers_sql)
            integer_columns = cur.fetchall()

            if not integer_columns:
                print("✅ No INTEGER columns found!")
                return True

            print(f"Found {len(integer_columns)} INTEGER columns to convert:")
            for table, column in integer_columns:
                print(f"  {table}.{column}")

            print(f"\n🔄 Converting {len(integer_columns)} columns to BIGINT...")

            success_count = 0
            for table, column in integer_columns:
                try:
                    update_sql = (
                        f"ALTER TABLE {table} ALTER COLUMN {column} TYPE BIGINT"
                    )
                    print(f"  Converting {table}.{column}...")
                    cur.execute(update_sql)
                    conn.commit()  # Commit each one individually
                    print(f"    ✅ Success")
                    success_count += 1
                except Exception as e:
                    conn.rollback()  # Rollback failed operation
                    print(f"    ❌ Error: {e}")

            print(
                f"\n🎉 Successfully converted {success_count}/{len(integer_columns)} columns!"
            )

            # Final verification
            cur.execute(all_integers_sql)
            remaining = cur.fetchall()

            if remaining:
                print(f"\n⚠️ {len(remaining)} INTEGER columns still remain:")
                for table, column in remaining:
                    print(f"  {table}.{column}")
            else:
                print("\n✅ All columns are now BIGINT, VARCHAR, or other safe types!")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = convert_all_integers_to_bigint()
    exit(0 if success else 1)
