#!/usr/bin/env python3
"""
Quick check of today's race data
"""

import psycopg2
import pandas as pd

# Database connection
db_config = {
    "host": "localhost",
    "port": 5434,
    "database": "horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}

try:
    with psycopg2.connect(**db_config) as connection:
        query = """
            SELECT 
                rc.course,
                rc.race_number,
                rc.race_time,
                COUNT(*) as runners,
                COUNT(DISTINCT re.horse_name) as unique_horses
            FROM race_entries re
            JOIN race_cards rc ON re.race_id = rc.race_id
            WHERE rc.race_date = CURRENT_DATE
            GROUP BY rc.course, rc.race_number, rc.race_time
            ORDER BY rc.course, rc.race_number
        """

        df = pd.read_sql_query(query, connection)
        print("Today's Race Summary:")
        print("=" * 50)
        print(df.to_string(index=False))
        print(f"\nTotal races: {len(df)}")
        print(f"Total runners: {df['runners'].sum()}")
        print(f"Average field size: {df['runners'].mean():.1f}")

except Exception as e:
    print(f"Error: {e}")
