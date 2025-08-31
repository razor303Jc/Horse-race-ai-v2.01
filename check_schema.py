#!/usr/bin/env python3
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="horse_racing",
        password="horse_racing_password",
        database="postgres",
    )
    cursor = conn.cursor()

    # Check if race_results table exists
    cursor.execute(
        """
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'race_results' 
        ORDER BY ordinal_position;
    """
    )
    columns = cursor.fetchall()

    if columns:
        print("race_results table structure:")
        for col_name, data_type, nullable in columns:
            print(
                f"  {col_name}: {data_type} {'NULL' if nullable == 'YES' else 'NOT NULL'}"
            )
    else:
        print("race_results table does not exist")

        # Check what tables do exist
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """
        )
        tables = cursor.fetchall()
        print(f"\nExisting tables:")
        for table in tables:
            print(f"  {table[0]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
