#!/usr/bin/env python3
"""
Direct Name Column Fix - Simple and Fast
"""
import psycopg2


def fix_name_mapping():
    """Direct SQL fix for name mapping"""
    print("🎯 DIRECT NAME COLUMN FIX")
    print("=" * 40)

    # Test database connection
    config = {
        "host": "horse_racing_postgres_clean",
        "port": 5432,
        "database": "results_horse_racing_db",
        "user": "horse_racing",
        "password": "secure_password_123",
    }

    try:
        conn = psycopg2.connect(**config)
        print("✅ Database connected")

        with conn.cursor() as cur:
            # Check current state
            cur.execute("SELECT COUNT(*) FROM jockeys_stats")
            jockey_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM trainers_stats")
            trainer_count = cur.fetchone()[0]

            print(f"📊 Current counts:")
            print(f"   jockeys_stats: {jockey_count} records")
            print(f"   trainers_stats: {trainer_count} records")

            # Show table schemas
            cur.execute(
                """
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'jockeys_stats' 
                ORDER BY ordinal_position
            """
            )
            jockey_schema = cur.fetchall()

            cur.execute(
                """
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'trainers_stats' 
                ORDER BY ordinal_position  
            """
            )
            trainer_schema = cur.fetchall()

            print(f"\\n📋 jockeys_stats schema:")
            for col, dtype, nullable in jockey_schema:
                print(
                    f"   {col}: {dtype} ({'nullable' if nullable == 'YES' else 'required'})"
                )

            print(f"\\n📋 trainers_stats schema:")
            for col, dtype, nullable in trainer_schema:
                print(
                    f"   {col}: {dtype} ({'nullable' if nullable == 'YES' else 'required'})"
                )

        conn.close()
        print("\\n✅ Analysis complete")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    fix_name_mapping()
