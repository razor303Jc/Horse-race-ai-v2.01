#!/usr/bin/env python3

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port="5434",
    database="horse_racing_db",
    user="horse_racing",
    password="secure_password_123",
)

cur = conn.cursor()

# Check counts in each advanced metrics table
tables = [
    "horse_power_ratings",
    "horse_speed_ratings",
    "horse_form_scores",
    "monte_carlo_simulations",
    "horse_advanced_metrics",
]

print("Database Population Summary:")
print("=" * 50)
for table in tables:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    count = cur.fetchone()[0]
    print(f"{table}: {count} records")

print("\n" + "=" * 50)

# Show sample data from each table
print("\nSample Power Ratings (first 3):")
cur.execute(
    "SELECT horse_id, power_rating, base_rating, consistency_rating FROM horse_power_ratings LIMIT 3"
)
for row in cur.fetchall():
    print(f"  Horse {row[0]}: Power={row[1]}, Base={row[2]}, Consistency={row[3]}")

print("\nSample Monte Carlo Results (first 3):")
cur.execute(
    "SELECT horse_id, win_probability, place_probability, show_probability FROM monte_carlo_simulations LIMIT 3"
)
for row in cur.fetchall():
    print(f"  Horse {row[0]}: Win={row[1]:.1%}, Place={row[2]:.1%}, Show={row[3]:.1%}")

conn.close()
