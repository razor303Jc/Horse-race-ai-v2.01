#!/usr/bin/env python3
"""
Simple System Integration Test - 1 Day Workflow
Horse Racing AI v2.0

Quick test of the complete system workflow.
"""

import os
import logging
import asyncio
import json
from datetime import datetime, date

from src.database.database_manager import DatabaseManager
from tests.weekly_race_cards_generator import WeeklyRaceCardsGenerator

# Setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = (
    "postgresql://horse_racing_test:test_password_123@"
    "postgres:5432/horse_racing_test_db"
)
os.environ["DATABASE_URL"] = DATABASE_URL


class QuickSystemTest:
    """Quick system integration test"""

    def __init__(self):
        self.test_date = date(2025, 8, 9)  # Saturday
        self.db = None
        self.race_generator = None
        self.results = {}

    async def run_test(self):
        """Run the quick system test"""
        logger.info("🚀 Starting Quick System Test")
        start_time = datetime.now()

        try:
            # Phase 1: Setup and data generation
            logger.info("📊 Phase 1: Generating race data...")
            self.db = DatabaseManager()
            self.race_generator = WeeklyRaceCardsGenerator()

            if not self.race_generator.connect_to_database():
                raise Exception("Database connection failed")

            if not self.race_generator.create_weekly_schema():
                raise Exception("Schema creation failed")

            # Generate Saturday premium races
            courses = ["Ascot", "Newmarket", "York", "Sandown Park", "Cheltenham"]
            races = self.race_generator.generate_race_card_for_day(
                self.test_date, courses, 15
            )

            if not self.race_generator.insert_daily_races(races):
                raise Exception("Race insertion failed")

            logger.info(f"✅ Generated {len(races)} races")

            # Phase 2: System discovery
            logger.info("🔍 Phase 2: System discovery...")
            available_races = self.db.get_races(
                date_from=self.test_date, date_to=self.test_date, limit=20
            )
            logger.info(f"✅ Discovered {len(available_races)} races")

            # Phase 3: Monte Carlo simulation
            logger.info("🎲 Phase 3: Monte Carlo analysis...")
            predictions = []
            for race in available_races[:5]:  # Test first 5 races
                race_details = self.db.get_race_details(race["race_id"])
                if race_details and race_details["participants"]:
                    participants = race_details["participants"]
                    race_predictions = self._simulate_monte_carlo(race, participants)
                    predictions.append(race_predictions)

            logger.info(f"✅ Analyzed {len(predictions)} races")

            # Phase 4: Fast results
            logger.info("⚡ Phase 4: Fast results generation...")
            fast_results = []
            for prediction in predictions:
                result = self._generate_fast_result(prediction)
                fast_results.append(result)

            logger.info(f"✅ Generated {len(fast_results)} fast results")

            # Phase 5: Notifications
            logger.info("📱 Phase 5: NTFY notifications...")
            notifications = self._generate_notifications(fast_results)
            logger.info(f"✅ Generated {len(notifications)} notifications")

            # Results
            duration = (datetime.now() - start_time).total_seconds()
            self.results = {
                "status": "success",
                "duration": duration,
                "races_generated": len(races),
                "races_analyzed": len(predictions),
                "fast_results": len(fast_results),
                "notifications": len(notifications),
                "sample_prediction": predictions[0] if predictions else None,
                "sample_result": fast_results[0] if fast_results else None,
            }

            logger.info(f"🎉 Test completed successfully in {duration:.2f}s")
            return self.results

        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            self.results = {
                "status": "failed",
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds(),
            }
            return self.results

        finally:
            if self.db:
                self.db.close()
            if self.race_generator:
                self.race_generator.close_connection()

    def _simulate_monte_carlo(self, race, participants):
        """Simulate Monte Carlo analysis for a race"""
        predictions = []
        base_prob = 1.0 / len(participants)

        for participant in participants:
            # Extract odds and calculate probability
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

            # Monte Carlo probability (weighted combination)
            monte_carlo_prob = (implied_prob * 0.7) + (base_prob * 0.3)

            prediction = {
                "name": participant.get("name", "Unknown"),
                "jockey": participant.get("jockey", "Unknown"),
                "odds": odds_str,
                "probability": round(monte_carlo_prob * 100, 2),
                "confidence": round(abs(monte_carlo_prob - implied_prob) * 100, 2),
            }
            predictions.append(prediction)

        # Sort by probability
        predictions.sort(key=lambda x: x["probability"], reverse=True)

        return {
            "race_id": race["race_id"],
            "course": race["course"],
            "race_name": race["race_name"],
            "predictions": predictions,
            "favorite": predictions[0]["name"] if predictions else "None",
            "favorite_probability": predictions[0]["probability"] if predictions else 0,
        }

    def _generate_fast_result(self, prediction):
        """Generate fast result from prediction"""
        top_3 = prediction["predictions"][:3]

        return {
            "race_id": prediction["race_id"],
            "course": prediction["course"],
            "race_name": prediction["race_name"],
            "top_picks": [
                {
                    "position": i + 1,
                    "name": pick["name"],
                    "jockey": pick["jockey"],
                    "probability": pick["probability"],
                    "odds": pick["odds"],
                }
                for i, pick in enumerate(top_3)
            ],
            "recommendation": self._get_recommendation(top_3[0] if top_3 else None),
        }

    def _get_recommendation(self, favorite):
        """Get betting recommendation"""
        if not favorite:
            return "No clear recommendation"

        prob = favorite["probability"]
        if prob > 40:
            return f"Strong Win bet: {favorite['name']}"
        elif prob > 25:
            return f"Each-way bet: {favorite['name']}"
        else:
            return f"Cautious approach: {favorite['name']}"

    def _generate_notifications(self, fast_results):
        """Generate NTFY notifications"""
        notifications = []

        # Summary notification
        notifications.append(
            {
                "type": "summary",
                "title": f"🏁 Analysis Complete - {self.test_date}",
                "message": f"Analyzed {len(fast_results)} races. Top picks ready!",
                "timestamp": datetime.now(),
            }
        )

        # Top race notifications
        for result in fast_results[:3]:
            if result["top_picks"]:
                top_pick = result["top_picks"][0]
                notifications.append(
                    {
                        "type": "race_tip",
                        "title": f'🎯 {result["course"]}',
                        "message": (
                            f'Top pick: {top_pick["name"]} '
                            f'({top_pick["probability"]:.1f}%)'
                        ),
                        "timestamp": datetime.now(),
                    }
                )

        return notifications

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🏁 QUICK SYSTEM TEST RESULTS")
        print("=" * 60)

        if self.results.get("status") == "success":
            print("✅ Status: SUCCESS")
            print(f"⏱️  Duration: {self.results['duration']:.2f}s")
            print(f"🏁 Races Generated: {self.results['races_generated']}")
            print(f"🎯 Races Analyzed: {self.results['races_analyzed']}")
            print(f"⚡ Fast Results: {self.results['fast_results']}")
            print(f"📱 Notifications: {self.results['notifications']}")

            if self.results.get("sample_result"):
                sample = self.results["sample_result"]
                print("\n🎯 SAMPLE RESULT:")
                print(f"   🏟️  {sample['course']} - {sample['race_name'][:40]}")
                if sample["top_picks"]:
                    top = sample["top_picks"][0]
                    print(f"   🥇 {top['name']} ({top['probability']:.1f}%)")
                    print(f"   💰 {sample['recommendation']}")
        else:
            print("❌ Status: FAILED")
            print(f"⚠️  Error: {self.results.get('error', 'Unknown')}")

        print("=" * 60)


async def main():
    """Main test execution"""
    test = QuickSystemTest()
    results = await test.run_test()
    test.print_summary()

    # Save results
    results_file = f"quick_system_test_{test.test_date}_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📁 Results saved to: {results_file}")
    return results


if __name__ == "__main__":
    asyncio.run(main())
