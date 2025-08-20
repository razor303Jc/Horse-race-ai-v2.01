#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5434,
    database="horse_racing_db",
    user="horse_racing",
    password="secure_password_123",
)
cursor = conn.cursor()

print("🏁 RACES table columns:")
cursor.execute(
    "SELECT column_name FROM information_schema.columns WHERE table_name = 'races'"
)
for row in cursor.fetchall():
    print(f"  {row[0]}")

print("\n📝 RECORDS table columns:")
cursor.execute(
    "SELECT column_name FROM information_schema.columns WHERE table_name = 'records'"
)
for row in cursor.fetchall():
    print(f"  {row[0]}")

cursor.execute("SELECT COUNT(*) FROM races")
race_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM records")
record_count = cursor.fetchone()[0]

print(f"\nData: {race_count} races, {record_count} records")

cursor.close()
conn.close()
