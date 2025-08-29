#!/usr/bin/env python3
"""
Check Today's AI Horse Selections
Updated with correct column names
"""

import psycopg2
from datetime import datetime, date
import sys
import os

# Add the project root to the path
sys.path.insert(0, "/home/jc/Documents/Horse-race-ai-v2.03")


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

        # Check for races today (using correct column names)
        cursor.execute(
            """
            SELECT DISTINCT race_id, race_time, course, race_name, date
            FROM races 
            WHERE DATE(date) = %s
            ORDER BY race_time
        """,
            (today,),
        )

        races_today = cursor.fetchall()

        if races_today:
            print(f"\n✅ Found {len(races_today)} races scheduled for today!")

            for race_id, race_time, course, race_name, race_date in races_today:
                print(f"\n🏁 Race {race_id}: {race_name}")
                print(f"📍 Course: {course}")
                print(f"⏰ Time: {race_time}")
                print(f"📅 Date: {race_date}")

                # Get AI selections for this race (using correct column names)
                cursor.execute(
                    """
                    SELECT horse, jockey, trainer, or_rating, position, sp
                    FROM records 
                    WHERE race_id = %s
                    ORDER BY position ASC
                    LIMIT 10
                """,
                    (race_id,),
                )

                selections = cursor.fetchall()
                if selections:
                    print("🤖 Race Results & AI Analysis:")
                    for i, (horse, jockey, trainer, rating, position, sp) in enumerate(
                        selections, 1
                    ):
                        rating_str = f" (OR: {rating})" if rating else ""
                        position_str = f"#{position}" if position else "DNS"
                        sp_str = f" SP: {sp}" if sp else ""

                        print(f"  {position_str} {horse}{rating_str}{sp_str}")
                        print(f"     🏇 {jockey} | 👨‍🏫 {trainer}")

                        if i >= 5:  # Show top 5
                            break
                else:
                    print("   ❌ No data available for this race")

                print("-" * 50)
        else:
            print("❌ No races found for today")
            print("\n🔍 Let me check recent races and run AI predictions...")

            # Check recent races
            cursor.execute(
                """
                SELECT DISTINCT race_id, date, race_time, course, race_name
                FROM races 
                ORDER BY date DESC, race_time DESC
                LIMIT 5
            """
            )

            recent_races = cursor.fetchall()
            if recent_races:
                print("\n📅 Most Recent Races in Database:")
                for race_id, race_date, race_time, course, race_name in recent_races:
                    print(f"\n🏁 {race_date} - {race_name}")
                    print(f"📍 {course} at {race_time}")

                    cursor.execute(
                        """
                        SELECT horse, position, or_rating, sp
                        FROM records 
                        WHERE race_id = %s
                        ORDER BY position ASC
                        LIMIT 3
                    """,
                        (race_id,),
                    )

                    results = cursor.fetchall()
                    if results:
                        print("🏆 Top 3 Finishers:")
                        for i, (horse, position, rating, sp) in enumerate(results, 1):
                            pos_str = f"#{position}" if position else "DNS"
                            rating_str = f" (OR: {rating})" if rating else ""
                            sp_str = f" SP: {sp}" if sp else ""
                            print(f"  {pos_str} {horse}{rating_str}{sp_str}")

            # Check system status
            print("\n🔧 System Status Check:")
            cursor.execute("SELECT COUNT(*) FROM races")
            race_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM records")
            record_count = cursor.fetchone()[0]

            cursor.execute("SELECT MAX(date) FROM races")
            latest_date = cursor.fetchone()[0]

            print(f"📊 Database Status:")
            print(f"   Total Races: {race_count:,}")
            print(f"   Total Records: {record_count:,}")
            print(f"   Latest Data: {latest_date}")

            # Let's try to run AI predictions on recent data
            if race_count > 0:
                print("\n🤖 Running AI Predictions on Recent Data...")
                try:
                    # Import and run the horse profiling system
                    from src.horse_racing_ai.postgres_horse_profiling import (
                        PostgreSQLHorseProfilingSystem,
                    )

                    profiler = PostgreSQLHorseProfilingSystem()

                    # Get a recent race for analysis
                    cursor.execute(
                        """
                        SELECT race_id, course, race_name, date
                        FROM races 
                        ORDER BY date DESC 
                        LIMIT 1
                    """
                    )

                    recent_race = cursor.fetchone()
                    if recent_race:
                        race_id, course, race_name, race_date = recent_race
                        print(
                            f"\n🔮 AI Analysis for: {race_name} at {course} ({race_date})"
                        )

                        # Get horses from this race
                        cursor.execute(
                            """
                            SELECT DISTINCT horse, or_rating, position
                            FROM records 
                            WHERE race_id = %s
                            ORDER BY position ASC
                        """,
                            (race_id,),
                        )

                        horses = cursor.fetchall()

                        if horses:
                            print("\n🧠 AI Horse Performance Analysis:")
                            for horse, rating, position in horses[:5]:
                                # Get horse profile
                                profile = profiler.analyze_horse_form_trend(horse)

                                if profile:
                                    trend = profile.get("trend", "Unknown")
                                    performance = profile.get("recent_performance", {})

                                    print(f"\n🐎 {horse}")
                                    print(f"   📈 Form Trend: {trend}")
                                    print(f"   🎯 OR Rating: {rating}")
                                    print(f"   🏁 Finished: #{position}")

                                    if performance:
                                        avg_pos = performance.get("avg_position", "N/A")
                                        races = performance.get("races_analyzed", 0)
                                        print(
                                            f"   📊 Recent Avg Position: {avg_pos} ({races} races)"
                                        )

                except Exception as e:
                    print(f"   ⚠️ AI Analysis unavailable: {e}")
                    print("   💡 Tip: Ensure all dependencies are installed")

            if latest_date and latest_date < today:
                print(
                    f"\n⚠️  Data appears to be outdated. Latest data is from {latest_date}"
                )
                print(
                    "💡 Recommendation: Run the auto-downloader to get today's racing data"
                )
                print(
                    "   Command: docker-compose -f docker-compose.clean.yml restart auto-downloader"
                )

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
