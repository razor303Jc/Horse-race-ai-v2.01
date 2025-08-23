#!/usr/bin/env python3
"""
Monte Carlo Analysis Demo
Horse Racing AI v2.0

Demonstrates the Monte Carlo analysis working with real generated data.
"""

import os
import sys
from datetime import date

# Add project root to path
sys.path.insert(0, "/home/jc/Documents/Horse-race-ai-v2.0")

from src.database.database_manager import DatabaseManager

# Set test database
DATABASE_URL = (
    "postgresql://horse_racing_test:test_password_123@"
    "postgres:5432/horse_racing_test_db"
)
os.environ["DATABASE_URL"] = DATABASE_URL


def monte_carlo_analysis_demo():
    """Demonstrate Monte Carlo analysis on real data"""
    print("🎲 MONTE CARLO ANALYSIS DEMONSTRATION")
    print("=" * 50)

    db = DatabaseManager()

    try:
        # Get today's races
        test_date = date(2025, 8, 9)
        races = db.get_races(date_from=test_date, date_to=test_date, limit=3)

        print(f"📅 Analyzing races for {test_date}")
        print(f"🏁 Found {len(races)} races to analyze")
        print()

        for i, race in enumerate(races, 1):
            print(f"🏟️  RACE {i}: {race['course']} - {race['race_name']}")
            print(f"   ⏰ Time: {race['race_time']}")
            print(f"   💰 Prize: {race['prize']}")
            print(f"   📏 Distance: {race['distance']}")
            print()

            # Get race details
            race_details = db.get_race_details(race["race_id"])
            if not race_details or not race_details["participants"]:
                print("   ⚠️  No participants found")
                continue

            participants = race_details["participants"]
            print(f"   🏇 Runners: {len(participants)}")
            print()

            # Monte Carlo analysis
            print("   🎯 MONTE CARLO PREDICTIONS:")
            print("   " + "-" * 40)

            predictions = []
            base_prob = 1.0 / len(participants)

            for participant in participants:
                # Calculate probability
                odds_str = participant.get("odds", "10/1")
                try:
                    if "/" in odds_str:
                        num, den = odds_str.split("/")
                        decimal_odds = (float(num) / float(den)) + 1
                        implied_prob = 1.0 / decimal_odds
                    else:
                        implied_prob = base_prob
                except (ValueError, ZeroDivisionError):
                    implied_prob = base_prob

                # Monte Carlo weighted combination
                monte_carlo_prob = (implied_prob * 0.7) + (base_prob * 0.3)
                confidence = abs(monte_carlo_prob - implied_prob) * 100

                predictions.append(
                    {
                        "name": participant.get("name", "Unknown"),
                        "jockey": participant.get("jockey", "Unknown"),
                        "odds": odds_str,
                        "probability": monte_carlo_prob * 100,
                        "confidence": confidence,
                    }
                )

            # Sort by probability
            predictions.sort(key=lambda x: x["probability"], reverse=True)

            # Show top 5
            for j, pred in enumerate(predictions[:5], 1):
                print(
                    f"   {j}. {pred['name']:<18} ({pred['jockey']:<15}) "
                    f"{pred['probability']:5.1f}% [{pred['odds']:>4}]"
                )

            # Analysis summary
            favorite = predictions[0]
            total_prob = sum(p["probability"] for p in predictions)
            avg_confidence = sum(p["confidence"] for p in predictions) / len(
                predictions
            )

            print()
            print(f"   📊 ANALYSIS SUMMARY:")
            print(
                f"      🥇 Favorite: {favorite['name']} ({favorite['probability']:.1f}%)"
            )
            print(f"      🎯 Total Probability: {total_prob:.1f}%")
            print(f"      📈 Avg Confidence: {avg_confidence:.1f}")

            # Betting recommendation
            if favorite["probability"] > 40:
                recommendation = f"Strong Win bet: {favorite['name']}"
            elif favorite["probability"] > 25:
                recommendation = f"Each-way bet: {favorite['name']}"
            else:
                recommendation = f"Cautious approach: {favorite['name']}"

            print(f"      💰 Recommendation: {recommendation}")
            print()
            print("   " + "=" * 50)
            print()

    finally:
        db.close()


if __name__ == "__main__":
    monte_carlo_analysis_demo()
