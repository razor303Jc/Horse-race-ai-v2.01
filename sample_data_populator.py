#!/usr/bin/env python3
"""
Simple Test Data Populator for Results Database
Creates sample data to test advanced metrics calculations
"""

import psycopg2
import pandas as pd
from datetime import datetime, date, timedelta
import random

# Docker database config
db_config = {
    "host": "postgres",
    "port": 5432,
    "user": "horse_racing",
    "password": "horse_racing_password",
    "database": "results_horse_racing_db",
}


def create_sample_data():
    """Create sample racing data for testing"""

    # Sample horses
    horses = [
        "Thunderbolt",
        "Lightning Storm",
        "Golden Arrow",
        "Midnight Express",
        "Fire Spirit",
        "Wind Walker",
        "Storm Chaser",
        "Silver Bullet",
        "Racing Legend",
        "Speed Demon",
        "Victory Lane",
        "Champion's Pride",
    ]

    # Sample courses
    courses = ["Ascot", "Cheltenham", "Epsom", "Newmarket", "York"]

    # Sample classes
    classes = ["Class 1", "Class 2", "Class 3", "Class 4", "Handicap", "Listed"]

    # Sample jockeys
    jockeys = ["A Smith", "B Jones", "C Johnson", "D Williams", "E Brown", "F Wilson"]

    # Sample trainers
    trainers = ["Trainer A", "Trainer B", "Trainer C", "Trainer D", "Trainer E"]

    # Generate race data
    races_data = []
    records_data = []

    race_id = 1
    record_id = 1

    # Generate 50 races over the last 6 months
    for i in range(50):
        race_date = date.today() - timedelta(days=random.randint(1, 180))

        race = {
            "race_id": race_id,
            "race_number": random.randint(1, 8),
            "race_time": f"{random.randint(13, 18)}:{random.randint(10, 59):02d}",
            "course": random.choice(courses),
            "race_type": "Flat",
            "date": race_date,
            "race_name": f"Test Race {i+1}",
            "class": random.choice(classes),
            "distance": f"{random.choice(['6f', '7f', '1m', '1m2f', '1m4f', '1m6f'])}",
            "surface": random.choice(["Good", "Firm", "Soft", "Heavy"]),
            "runners": random.randint(6, 16),
        }
        races_data.append(race)

        # Generate runners for this race
        num_runners = race["runners"]
        race_horses = random.sample(horses, min(num_runners, len(horses)))

        for position, horse in enumerate(race_horses, 1):
            record = {
                "record_id": record_id,
                "race_id": race_id,
                "horse_name": horse,
                "jockey": random.choice(jockeys),
                "trainer": random.choice(trainers),
                "position": position,
                "finishing_position": position,
                "starting_price": round(random.uniform(1.5, 25.0), 2),
                "weight": f"{random.randint(8, 10)}-{random.randint(0, 13)}",
                "age": random.randint(2, 8),
            }
            records_data.append(record)
            record_id += 1

        race_id += 1

    return pd.DataFrame(races_data), pd.DataFrame(records_data)


def populate_database():
    """Populate the results database with sample data"""
    print("🚀 Populating Results Database with Sample Data")
    print("=" * 50)

    try:
        # Connect to database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        print("✅ Connected to results_horse_racing_db")

        # Clear existing data
        cursor.execute("DELETE FROM result_records")
        cursor.execute("DELETE FROM result_races")
        print("🧹 Cleared existing data")

        # Generate sample data
        races_df, records_df = create_sample_data()
        print(f"📊 Generated {len(races_df)} races and {len(records_df)} records")

        # Insert races
        for _, race in races_df.iterrows():
            cursor.execute(
                """
                INSERT INTO result_races 
                (race_id, race_number, race_time, course, race_type, date, 
                 race_name, class, distance, surface, runners)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    race["race_id"],
                    race["race_number"],
                    race["race_time"],
                    race["course"],
                    race["race_type"],
                    race["date"],
                    race["race_name"],
                    race["class"],
                    race["distance"],
                    race["surface"],
                    race["runners"],
                ),
            )

        # Insert records
        for _, record in records_df.iterrows():
            cursor.execute(
                """
                INSERT INTO result_records 
                (record_id, race_id, horse_name, jockey, trainer, position,
                 finishing_position, starting_price, weight, age)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    record["record_id"],
                    record["race_id"],
                    record["horse_name"],
                    record["jockey"],
                    record["trainer"],
                    record["position"],
                    record["finishing_position"],
                    record["starting_price"],
                    record["weight"],
                    record["age"],
                ),
            )

        conn.commit()
        print("✅ Sample data inserted successfully")

        # Verify data
        cursor.execute("SELECT COUNT(*) FROM result_races")
        race_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM result_records")
        record_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT horse_name) FROM result_records")
        horse_count = cursor.fetchone()[0]

        print(f"📈 Database populated with:")
        print(f"   🏇 {race_count} races")
        print(f"   📊 {record_count} race records")
        print(f"   🐎 {horse_count} unique horses")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Failed to populate database: {e}")
        return False


if __name__ == "__main__":
    populate_database()
