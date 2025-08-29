#!/usr/bin/env python3
"""
Database Schema Setup for Horse Racing AI v2.0
Creates the required tables for massive dataset generation
"""

import psycopg2
import sys


def setup_schema(database_url):
    """Set up the database schema"""

    # Read the schema file
    with open("basic_racing_schema.sql", "r") as f:
        schema_sql = f.read()

    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        print("🔧 Setting up database schema...")

        # Execute schema
        cursor.execute(schema_sql)
        conn.commit()

        print("✅ Database schema created successfully!")

        # Verify tables exist
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """
        )

        tables = cursor.fetchall()
        print(f"📊 Created tables: {[table[0] for table in tables]}")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Schema setup failed: {e}")
        return False


if __name__ == "__main__":
    database_url = "postgresql://horse_racing_test:test_password_123@postgres:5432/horse_racing_test_db"

    if len(sys.argv) > 1:
        database_url = sys.argv[1]

    success = setup_schema(database_url)
    sys.exit(0 if success else 1)
