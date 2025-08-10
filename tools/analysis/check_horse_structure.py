#!/usr/bin/env python3
"""
Check Horse Table Structure
"""

import psycopg2


def get_db_connection():
    """Get database connection with correct credentials"""
    return psycopg2.connect(
        host="localhost",
        port=5433,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )


def check_table_structure():
    """Check the structure of the horses table"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get column names and types
        cursor.execute(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'horses'
            ORDER BY ordinal_position;
        """
        )

        columns = cursor.fetchall()
        print("🐴 HORSES TABLE STRUCTURE:")
        print("=" * 40)
        for col_name, data_type, nullable in columns:
            print(
                f"  {col_name}: {data_type} {'(nullable)' if nullable == 'YES' else '(not null)'}"
            )

        # Get sample data
        print("\n📋 SAMPLE HORSE DATA:")
        print("=" * 40)
        cursor.execute("SELECT * FROM horses LIMIT 5;")
        sample_data = cursor.fetchall()

        # Get column names for display
        cursor.execute(
            """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'horses'
            ORDER BY ordinal_position;
        """
        )
        col_names = [row[0] for row in cursor.fetchall()]

        for i, row in enumerate(sample_data, 1):
            print(f"\nRecord {i}:")
            for col_name, value in zip(col_names, row):
                print(f"  {col_name}: {value}")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    check_table_structure()
