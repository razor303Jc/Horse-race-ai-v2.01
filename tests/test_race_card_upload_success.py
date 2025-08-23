#!/usr/bin/env python3
"""
Race Card Upload Success Test
============================

Validates that race card data is properly uploaded and available.
"""

import os
import psycopg2
from urllib.parse import urlparse

# Use DATABASE_URL from environment like Docker containers do
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://horse_racing:secure_password_123@postgres:5432/horse_racing_db",
)

# Parse DATABASE_URL for Docker container usage
parsed_url = urlparse(DATABASE_URL)
DATABASE_CONFIG = {
    "host": parsed_url.hostname or "postgres",
    "port": parsed_url.port or 5432,
    "database": parsed_url.path.lstrip("/") if parsed_url.path else "horse_racing_db",
    "user": parsed_url.username or "horse_racing",
    "password": parsed_url.password or "secure_password_123",
}


def test_race_card_data():
    """Test that race card data is properly loaded"""
    print("🧪 Testing Race Card Data Upload")
    print("=" * 50)

    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)

        with conn.cursor() as cur:
            # Test 1: Check race card races
            cur.execute("SELECT COUNT(*) FROM card_races")
            race_count = cur.fetchone()[0]
            print(f"✅ Race count: {race_count}")

            # Test 2: Check race card entries
            cur.execute("SELECT COUNT(*) FROM card_records")
            record_count = cur.fetchone()[0]
            print(f"✅ Race card entries: {record_count}")

            # Test 3: Check supporting data
            cur.execute("SELECT COUNT(*) FROM horses")
            horse_count = cur.fetchone()[0]
            print(f"✅ Horses: {horse_count}")

            cur.execute("SELECT COUNT(*) FROM jockeys_stats")
            jockey_count = cur.fetchone()[0]
            print(f"✅ Jockeys: {jockey_count}")

            cur.execute("SELECT COUNT(*) FROM trainers_stats")
            trainer_count = cur.fetchone()[0]
            print(f"✅ Trainers: {trainer_count}")

            # Test 4: Check data integrity - race card entries match races
            cur.execute(
                """
                SELECT COUNT(*) 
                FROM card_records cr
                JOIN card_races r ON cr.race_id = r.race_id
            """
            )
            matched_entries = cur.fetchone()[0]
            print(f"✅ Race card entries with valid races: {matched_entries}")

            # Test 5: Sample race card data
            cur.execute(
                """
                SELECT r.race_name, COUNT(cr.*) as entries
                FROM card_races r
                LEFT JOIN card_records cr ON r.race_id = cr.race_id
                GROUP BY r.race_id, r.race_name
                ORDER BY r.race_id
                LIMIT 5
            """
            )

            print("\n📊 Sample Race Card Data:")
            for race_name, entries in cur.fetchall():
                print(f"  - {race_name}: {entries} entries")

        conn.close()

        # Validation
        if race_count > 0 and record_count > 0 and matched_entries == record_count:
            print(f"\n🎉 SUCCESS: Race card data properly uploaded!")
            print(f"   - {race_count} races")
            print(f"   - {record_count} race card entries")
            print(f"   - All entries have valid race references")
            print(
                f"   - Supporting data loaded ({horse_count} horses, {jockey_count} jockeys, {trainer_count} trainers)"
            )
            return True
        else:
            print(f"\n❌ ISSUES FOUND:")
            if race_count == 0:
                print("  - No races loaded")
            if record_count == 0:
                print("  - No race card entries loaded")
            if matched_entries != record_count:
                print(
                    f"  - {record_count - matched_entries} entries have invalid race references"
                )
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_race_card_data()
    if success:
        print("\n✅ RACE CARD UPLOAD TEST PASSED!")
    else:
        print("\n❌ RACE CARD UPLOAD TEST FAILED!")
        exit(1)
