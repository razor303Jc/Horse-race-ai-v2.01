#!/usr/bin/env python3
"""
Super Simple AI Selections - No hanging issues
"""

import sys

sys.path.append("/app")

import psycopg2
import os


def quick_selections():
    """Generate quick AI selections"""
    print("🏇 QUICK AI SELECTIONS")
    print("=" * 40)

    # Connect to cards database
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="cards_horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )
        cursor = conn.cursor()

        # Get one race with horses
        cursor.execute(
            """
            SELECT r.race_id, r.course, r.race_time,
                   rd.horse_name, rd.jockey, 
                   COALESCE(rd.odds, 5.0) as odds,
                   COALESCE(rd.age, 4) as age
            FROM races r
            JOIN racecard_details rd ON r.race_id = rd.race_id
            WHERE r.race_id = 183359
            ORDER BY rd.number
            LIMIT 10
        """
        )

        horses = cursor.fetchall()
        conn.close()

        if not horses:
            print("❌ No horses found")
            return

        print(f"📋 Found {len(horses)} horses in race")
        print()

        race_id, course, race_time = horses[0][0], horses[0][1], horses[0][2]
        print(f"Race {race_id}: {course} at {race_time}")
        print("-" * 40)

        # Simple AI: Lower odds = higher chance
        selections = []
        for _, _, _, name, jockey, odds, age in horses:
            # Simple probability based on odds
            prob = 1.0 / float(odds) if float(odds) > 0 else 0.1
            ai_score = prob * 100

            selections.append(
                {
                    "name": name,
                    "jockey": jockey,
                    "odds": odds,
                    "age": age,
                    "ai_score": ai_score,
                }
            )

        # Sort by AI score
        selections.sort(key=lambda x: x["ai_score"], reverse=True)

        print("🤖 AI SELECTIONS:")
        for i, horse in enumerate(selections[:5]):
            print(f"{i+1}. {horse['name']}")
            print(f"   Jockey: {horse['jockey']}")
            print(f"   Odds: {horse['odds']}/1")
            print(f"   AI Score: {horse['ai_score']:.1f}%")
            print()

        print("✅ Quick selections complete!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    quick_selections()
