#!/usr/bin/env python3
import psycopg2

# Try the database connection the entity loader uses
try:
    import sys

    sys.path.append("/home/jc/Documents/Horse-race-ai-v2.05")
    from config.database_config import db_config

    # Use the same connection as entity loader
    host = "localhost"  # Override since we're running from host
    conn = psycopg2.connect(
        host=host,
        port=5432,
        user="horse_racing",
        password="horse_racing_password",
        database="postgres",
    )
    cursor = conn.cursor()

    print("Connected to database successfully")

    # List all tables
    cursor.execute(
        """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """
    )
    tables = cursor.fetchall()
    print(f"Tables found: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")

    # Check if race_participants exists specifically
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'race_participants'
        );
    """
    )
    exists = cursor.fetchone()[0]
    print(f"race_participants exists: {exists}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
