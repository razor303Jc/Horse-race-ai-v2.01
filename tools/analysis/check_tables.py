#!/usr/bin/env python3
"""
Quick Database Table Checker
"""
import psycopg2


def main():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        )

        tables = cursor.fetchall()
        print("📋 Available Tables:")
        for table in tables:
            print(f"  • {table[0]}")

        conn.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
