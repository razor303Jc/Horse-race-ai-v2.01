#!/usr/bin/env python3
"""
Check Today's AI Horse Selections
"""

import psycopg2
from datetime import datetime, date
import json


def get_todays_selections():
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            host="localhost",
            port=5434,
            database="horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )
        cursor = conn.cursor()

        # Get today's date
        today = date.today()
        print(f'🏇 AI Horse Selections for {today.strftime("%A, %B %d, %Y")}')
        print("=" * 60)

        # Check for races today
        cursor.execute(
            """
            SELECT DISTINCT race_id, race_time, course_name, race_name, race_date
            FROM races 
            WHERE DATE(race_date) = %s
            ORDER BY race_time
        """,
            (today,),
        )

        races_today = cursor.fetchall()

        if races_today:
            print(f"\n✅ Found {len(races_today)} races scheduled for today!")

            for race_id, race_time, course_name, race_name, race_date in races_today:
                print(f"\n🏁 Race {race_id}: {race_name}")
                print(f"📍 Course: {course_name}")
                print(f"⏰ Time: {race_time}")
                print(f"📅 Date: {race_date}")

                # Get AI selections for this race
                cursor.execute(
                    """
                    SELECT horse_name, win_probability, place_probability, 
                           jockey_name, trainer_name, OR_rating
                    FROM records 
                    WHERE race_id = %s
                    ORDER BY win_probability DESC
                    LIMIT 5
                """,
                    (race_id,),
                )

                selections = cursor.fetchall()
                if selections:
                    print("🤖 AI Top 5 Selections:")
                    for i, (
                        horse,
                        win_prob,
                        place_prob,
                        jockey,
                        trainer,
                        rating,
                    ) in enumerate(selections, 1):
                        rating_str = f" (OR: {rating})" if rating else ""
                        print(f"  {i}. {horse}{rating_str}")
                        print(f"     🎯 Win: {win_prob:.1%} | Place: {place_prob:.1%}")
                        print(f"     🏇 {jockey} | 👨‍🏫 {trainer}")
                else:
                    print("   ❌ No AI predictions available for this race")

                print("-" * 50)
        else:
            print("❌ No races found for today")
            print("\n🔍 Let me check recent races and system status...")

            # Check recent races
            cursor.execute(
                """
                SELECT DISTINCT race_id, race_date, race_time, course_name, race_name
                FROM races 
                ORDER BY race_date DESC, race_time DESC
                LIMIT 3
            """
            )

            recent_races = cursor.fetchall()
            if recent_races:
                print("\n📅 Most Recent Races with AI Predictions:")
                for (
                    race_id,
                    race_date,
                    race_time,
                    course_name,
                    race_name,
                ) in recent_races:
                    print(f"\n🏁 {race_date} - {race_name}")
                    print(f"📍 {course_name} at {race_time}")

                    cursor.execute(
                        """
                        SELECT horse_name, win_probability, place_probability
                        FROM records 
                        WHERE race_id = %s
                        ORDER BY win_probability DESC
                        LIMIT 3
                    """,
                        (race_id,),
                    )

                    selections = cursor.fetchall()
                    if selections:
                        print("🤖 AI Top 3:")
                        for i, (horse, win_prob, place_prob) in enumerate(
                            selections, 1
                        ):
                            print(
                                f"  {i}. {horse} - Win: {win_prob:.1%}, Place: {place_prob:.1%}"
                            )

            # Check system status
            print("\n🔧 System Status Check:")
            cursor.execute("SELECT COUNT(*) FROM races")
            race_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM records")
            record_count = cursor.fetchone()[0]

            cursor.execute("SELECT MAX(race_date) FROM races")
            latest_date = cursor.fetchone()[0]

            print(f"📊 Database Status:")
            print(f"   Total Races: {race_count:,}")
            print(f"   Total Records: {record_count:,}")
            print(f"   Latest Data: {latest_date}")

            if latest_date and latest_date < today:
                print(
                    f"\n⚠️  Data appears to be outdated. Latest data is from {latest_date}"
                )
                print("💡 Recommendation: Run the auto-downloader to get today's data")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check if PostgreSQL Docker container is running")
        print("2. Verify database credentials")
        print("3. Run the data pipeline to populate today's data")


if __name__ == "__main__":
    get_todays_selections()
