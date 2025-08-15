#!/usr/bin/env python3

import psycopg2
import os

db_config = {
    "host": "localhost",
    "port": 5433,
    "database": "horse_racing_db",
    "user": "horse_racing",
    "password": os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
}

try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    print("🏇 Database Schema Analysis")
    print("=" * 50)

    # Get table names
    cursor.execute(
        """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """
    )
    tables = cursor.fetchall()

    print(f"📊 Found {len(tables)} tables:")
    for table in tables:
        print(f"  • {table[0]}")

    print()

    # Get columns for key tables
    for table_name in ["records", "races", "horses"]:
        cursor.execute(
            """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position;
        """,
            (table_name,),
        )
        columns = cursor.fetchall()

        if columns:
            print(f"🏆 {table_name.upper()} table columns:")
            for col_name, data_type in columns:
                print(f"  • {col_name} ({data_type})")
            print()

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
