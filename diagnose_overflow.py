#!/usr/bin/env python3
"""
Diagnose Integer Overflow
========================

Find the exact column causing integer overflow in race_results and racecard_details.
"""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def diagnose_integer_overflow():
    """Find which columns are still INTEGER in the problematic tables"""
    print("🔍 Diagnosing Integer Overflow")
    print("=" * 50)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False

    try:
        conn = psycopg2.connect(database_url)
        with conn.cursor() as cur:

            # Check all columns in race_results and racecard_details
            problem_tables = ["race_results", "racecard_details"]

            for table in problem_tables:
                print(f"\n📋 {table.upper()} table schema:")

                schema_sql = """
                    SELECT column_name, data_type, character_maximum_length,
                           numeric_precision, numeric_scale
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                    ORDER BY ordinal_position;
                """

                cur.execute(schema_sql, (table,))
                columns = cur.fetchall()

                for col_name, data_type, char_len, num_prec, num_scale in columns:
                    if data_type == "integer":
                        print(f"  🔴 {col_name}: {data_type} *** PROBLEM ***")
                    elif data_type == "bigint":
                        print(f"  ✅ {col_name}: {data_type}")
                    elif data_type == "character varying":
                        print(f"  ✅ {col_name}: {data_type}({char_len})")
                    else:
                        print(f"  ℹ️ {col_name}: {data_type}")

            # Now find ALL integer columns in the database
            print(f"\n🔍 ALL INTEGER columns in database:")
            all_integers_sql = """
                SELECT table_name, column_name, data_type
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND data_type = 'integer'
                ORDER BY table_name, column_name;
            """

            cur.execute(all_integers_sql)
            integer_columns = cur.fetchall()

            if integer_columns:
                print(f"Found {len(integer_columns)} INTEGER columns:")
                for table, column, dtype in integer_columns:
                    print(f"  {table}.{column}")
            else:
                print("✅ No INTEGER columns found!")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = diagnose_integer_overflow()
    exit(0 if success else 1)
