#!/usr/bin/env python3

import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port="5434",
    database="horse_racing_db",
    user="horse_racing",
    password="secure_password_123",
)

cur = conn.cursor()

# First check what tables exist
cur.execute(
    """
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('horses', 'race_entries')
"""
)

print("Available tables:")
for row in cur.fetchall():
    print(f"  {row[0]}")

# Check if horses table has data
try:
    cur.execute("SELECT COUNT(*) FROM horses")
    horse_count = cur.fetchone()[0]
    print(f"\nHorses table: {horse_count} records")
except Exception as e:
    print(f"\nHorses table error: {e}")

# Check race_entries structure
try:
    cur.execute(
        """
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'race_entries'
    ORDER BY ordinal_position
    """
    )
    print("\nrace_entries columns:")
    for row in cur.fetchall():
        print(f"  {row[0]}")

except Exception as e:
    print(f"\nrace_entries error: {e}")

conn.close()
