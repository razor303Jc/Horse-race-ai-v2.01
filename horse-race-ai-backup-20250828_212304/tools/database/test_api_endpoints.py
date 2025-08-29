#!/usr/bin/env python3
"""
Test API endpoint for real race card data
Demonstrates integration with uploaded race data
"""

import asyncpg
import json
from datetime import datetime

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5434,
    "database": "horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}


async def test_race_data_api():
    """Test API-style queries against uploaded race data"""

    print("🧪 Testing Race Data API Endpoints")
    print("=" * 50)

    try:
        # Connect to database
        connection_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        conn = await asyncpg.connect(connection_string)

        # Test 1: Get today's races (API endpoint simulation)
        print("\n📅 API Test 1: /api/todays_races")
        races = await conn.fetch(
            """
            SELECT race_id, race_time, course, race_name, runners, 
                   distance, surface, prize
            FROM race_cards 
            WHERE race_date = CURRENT_DATE 
            ORDER BY race_time
        """
        )

        print(f"  ✅ Found {len(races)} races for today")
        for race in races[:3]:  # Show first 3
            print(
                f"    - {race['race_time'].strftime('%H:%M')} {race['course']}: {race['race_name']}"
            )

        # Test 2: Get race card with entries (API endpoint simulation)
        print("\n🐎 API Test 2: /api/race_card/{race_id}")
        if races:
            race_id = races[0]["race_id"]
            race_card = await conn.fetch(
                """
                SELECT re.horse_name, re.age, re.draw, re.jockey, 
                       re.trainer, re.odds, re.odds_decimal,
                       h.total_races, h.wins
                FROM race_entries re
                JOIN horses h ON re.horse_id = h.horse_id
                WHERE re.race_id = $1
                ORDER BY re.odds_decimal
            """,
                race_id,
            )

            print(f"  ✅ Race {race_id} has {len(race_card)} entries")
            for entry in race_card[:3]:  # Show first 3
                print(
                    f"    - {entry['horse_name']} ({entry['age']}yo) - {entry['jockey']} - {entry['odds']}"
                )

        # Test 3: ML training data sample (AI selections preparation)
        print("\n🤖 API Test 3: /api/ml_training_data")
        ml_data = await conn.fetch(
            """
            SELECT race_time, course, distance, horse_name, age, 
                   odds_decimal, total_races, wins
            FROM ml_training_view 
            WHERE race_time::date = CURRENT_DATE
            LIMIT 5
        """
        )

        print(f"  ✅ ML training data: {len(ml_data)} sample records")
        for record in ml_data:
            win_rate = (
                (record["wins"] / record["total_races"] * 100)
                if record["total_races"] > 0
                else 0
            )
            print(
                f"    - {record['horse_name']}: {win_rate:.1f}% win rate, odds {record['odds_decimal']}"
            )

        # Test 4: Course summary (venue analysis)
        print("\n🏟️ API Test 4: /api/course_summary")
        course_stats = await conn.fetch(
            """
            SELECT course, COUNT(*) as race_count, 
                   SUM(runners) as total_runners,
                   AVG(runners) as avg_runners
            FROM race_cards 
            WHERE race_date = CURRENT_DATE
            GROUP BY course
            ORDER BY race_count DESC
        """
        )

        print(f"  ✅ Today's racing at {len(course_stats)} venues:")
        for venue in course_stats:
            print(
                f"    - {venue['course']}: {venue['race_count']} races, avg {venue['avg_runners']:.1f} runners"
            )

        # Test 5: Favorites analysis (betting insights)
        print("\n💰 API Test 5: /api/favorites_analysis")
        favorites = await conn.fetch(
            """
            SELECT rc.course, re.horse_name, re.odds_decimal, re.jockey
            FROM race_entries re
            JOIN race_cards rc ON re.race_id = rc.race_id
            WHERE rc.race_date = CURRENT_DATE 
              AND re.odds_decimal > 0
              AND re.odds_decimal = (
                  SELECT MIN(re2.odds_decimal) 
                  FROM race_entries re2 
                  WHERE re2.race_id = re.race_id 
                    AND re2.odds_decimal > 0
              )
            ORDER BY rc.race_time
            LIMIT 8
        """
        )

        print(f"  ✅ Today's favorites (lowest odds):")
        for fav in favorites:
            print(
                f"    - {fav['course']}: {fav['horse_name']} ({fav['odds_decimal']:.2f}) - {fav['jockey']}"
            )

        print(f"\n🎉 All API tests successful!")
        print(f"🚀 Race card database is ready for AI selections!")

        await conn.close()

    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_race_data_api())
