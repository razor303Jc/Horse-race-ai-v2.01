#!/usr/bin/env python3
"""
Enhanced AI Selections with ML features
"""

import sys

sys.path.append("/app")

import psycopg2
import numpy as np


def enhanced_ai_selections():
    """Generate enhanced AI selections with proper ML features"""
    print("🚀 ENHANCED AI HORSE RACING SELECTIONS")
    print("=" * 60)

    try:
        # Connect to cards database
        conn = psycopg2.connect(
            host="postgres",
            database="cards_horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )
        cursor = conn.cursor()

        # Get races with good data
        cursor.execute(
            """
            SELECT r.race_id, r.course, r.race_time, COUNT(*) as horse_count
            FROM races r
            JOIN racecard_details rd ON r.race_id = rd.race_id
            GROUP BY r.race_id, r.course, r.race_time
            HAVING COUNT(*) >= 6
            ORDER BY r.race_time
            LIMIT 3
        """
        )

        races = cursor.fetchall()

        for race_id, course, race_time, horse_count in races:
            print(f"\\n🏁 Race {race_id}: {course} ({horse_count} horses)")
            print(f"🕐 Time: {race_time}")
            print("-" * 50)

            # Get unique horses for this race
            cursor.execute(
                """
                SELECT DISTINCT ON (rd.name, rd.jockey)
                       rd.name as horse_name, rd.jockey, rd.trainer,
                       COALESCE(rd.odds_decimal, 6.0) as odds,
                       COALESCE(rd.age, 4) as age,
                       rd.weight
                FROM racecard_details rd
                WHERE rd.race_id = %s
                ORDER BY rd.name, rd.jockey, rd.horse_number
            """,
                (race_id,),
            )

            horses = cursor.fetchall()

            if len(horses) < 3:
                print("❌ Not enough horses for analysis")
                continue

            # Enhanced AI scoring
            selections = []
            for name, jockey, trainer, odds, age, weight in horses:
                # Convert to float safely
                try:
                    odds_f = float(odds)
                    age_f = float(age)
                    # Handle weight strings like "10-1", "63.95", etc
                    weight_str = str(weight) if weight else "140"
                    try:
                        weight_f = float(weight_str)
                    except:
                        # Extract first number if format like "10-1"
                        import re

                        nums = re.findall(r"\d+\.?\d*", weight_str)
                        weight_f = float(nums[0]) if nums else 140.0
                except:
                    continue

                if odds_f <= 0:
                    odds_f = 10.0

                # Advanced AI features
                implied_prob = 1.0 / odds_f
                log_odds = np.log(odds_f)
                age_factor = 1.0 / (1.0 + abs(age_f - 5))  # Peak at age 5
                weight_factor = 1.0 / (weight_f / 140.0)  # Lighter is better

                # AI composite score
                ai_score = (
                    implied_prob * 40  # 40% odds
                    + age_factor * 30  # 30% age
                    + weight_factor * 20  # 20% weight
                    + (1.0 / log_odds) * 10  # 10% odds log
                ) * 100

                # Value calculation (high score vs low odds)
                value_score = ai_score / odds_f

                selections.append(
                    {
                        "name": name,
                        "jockey": jockey,
                        "trainer": trainer,
                        "odds": odds_f,
                        "age": age_f,
                        "weight": weight_f,
                        "ai_score": ai_score,
                        "value_score": value_score,
                    }
                )

            # Sort by AI score
            selections.sort(key=lambda x: x["ai_score"], reverse=True)

            print("🤖 TOP AI SELECTIONS:")
            for i, horse in enumerate(selections[:5]):
                print(f"\\n{i+1}. {horse['name']} ⭐")
                print(f"   🏃 Jockey: {horse['jockey']}")
                print(f"   👨‍🏫 Trainer: {horse['trainer']}")
                print(f"   💰 Odds: {horse['odds']:.1f}/1")
                print(f"   🎂 Age: {int(horse['age'])}")
                print(f"   ⚖️  Weight: {int(horse['weight'])}")
                print(f"   🤖 AI Score: {horse['ai_score']:.1f}%")
                print(f"   💎 Value: {horse['value_score']:.2f}")

            # Best value pick
            best_value = max(selections, key=lambda x: x["value_score"])
            print(
                f"\\n💰 BEST VALUE: {best_value['name']} (Value: {best_value['value_score']:.2f})"
            )

        conn.close()
        print("\\n" + "=" * 60)
        print("✅ ENHANCED AI SELECTIONS COMPLETE!")
        print("🎯 Good luck with your bets!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    enhanced_ai_selections()
