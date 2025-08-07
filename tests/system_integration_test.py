#!/usr/bin/env python3
"""
Complete System Integration Test - 1 Day Workflow
Horse Racing AI v2.0

This test simulates a realistic scenario where:
1. Race cards have been successfully downloaded/generated
2. The system starts and processes the data
3. Monte Carlo analysis runs
4. Fast results are generated
5. NTFY notifications are sent

This demonstrates the complete end-to-end workflow.
"""

import os
import logging
import asyncio
import json
from datetime import datetime, date
from typing import Dict, Any, List

from src.database.database_manager import DatabaseManager
from tests.weekly_race_cards_generator import WeeklyRaceCardsGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Set test database environment
DATABASE_URL = (
    "postgresql://horse_racing_test:test_password_123@"
    "localhost:5434/horse_racing_test_db"
)
os.environ["DATABASE_URL"] = DATABASE_URL


class SystemIntegrationTest:
    """Complete system integration test for 1-day workflow"""

    def __init__(self):
        """Initialize the test environment"""
        self.test_date = date(2025, 8, 9)  # Saturday - premium racing day
        self.db = None
        self.race_generator = None
        self.results = {
            "test_start": datetime.now(),
            "phases": {},
            "race_data": {},
            "monte_carlo_results": {},
            "notifications_sent": [],
            "system_performance": {},
        }

    async def setup_test_environment(self) -> Dict[str, Any]:
        """Phase 1: Set up the test environment and generate race data"""
        logger.info("🚀 PHASE 1: Setting up test environment...")

        phase_start = datetime.now()

        try:
            # Initialize database manager
            self.db = DatabaseManager()
            logger.info("✅ Database manager initialized")

            # Initialize race generator
            self.race_generator = WeeklyRaceCardsGenerator()

            # Connect to test database
            if not self.race_generator.connect_to_database():
                raise Exception("Failed to connect to test database")

            # Create schema
            if not self.race_generator.create_weekly_schema():
                raise Exception("Failed to create database schema")

            # Generate race cards for our test day (Saturday premium racing)
            logger.info(
                f"📅 Generating race cards for {self.test_date} "
                "(Saturday premium racing)"
            )

            # Clear any existing data for this date
            with self.race_generator.conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM racecard_details WHERE race_id IN "
                    "(SELECT race_id FROM races_cards WHERE date = %s)",
                    (self.test_date,),
                )
                cursor.execute(
                    "DELETE FROM races_results WHERE date = %s", (self.test_date,)
                )
                cursor.execute(
                    "DELETE FROM races_cards WHERE date = %s", (self.test_date,)
                )

            # Generate Saturday premium racing schedule
            saturday_courses = [
                "Ascot",
                "Newmarket",
                "York",
                "Sandown Park",
                "Cheltenham",
            ]
            races = self.race_generator.generate_race_card_for_day(
                self.test_date, saturday_courses, 20  # 20 premium Saturday races
            )

            # Insert the race data
            if not self.race_generator.insert_daily_races(races):
                raise Exception("Failed to insert race data")

            # Get summary of generated data
            summary = self.db.get_database_summary()

            phase_result = {
                "status": "success",
                "duration": (datetime.now() - phase_start).total_seconds(),
                "races_generated": len(races),
                "total_runners": sum(race["runners"] for race in races),
                "courses": list(set(race["course"] for race in races)),
                "database_summary": summary,
            }

            self.results["phases"]["setup"] = phase_result
            self.results["race_data"] = {
                "test_date": self.test_date,
                "races": races[:3],  # Store sample races
                "total_races": len(races),
            }

            courses_count = len(set(race["course"] for race in races))
            logger.info(
                f"✅ Phase 1 complete: {len(races)} races generated "
                f"at {courses_count} courses"
            )
            return phase_result

        except Exception as e:
            logger.error(f"❌ Phase 1 failed: {e}")
            phase_result = {
                "status": "error",
                "duration": (datetime.now() - phase_start).total_seconds(),
                "error": str(e),
            }
            self.results["phases"]["setup"] = phase_result
            raise

    async def simulate_system_startup(self) -> Dict[str, Any]:
        """Phase 2: Simulate system startup and data discovery"""
        logger.info("🔄 PHASE 2: System startup and data discovery...")

        phase_start = datetime.now()

        try:
            # Simulate system discovering new race data
            logger.info("🔍 Discovering available race data...")

            # Get today's races (simulating system checking for new data)
            available_races = self.db.get_races(
                date_from=self.test_date, date_to=self.test_date, limit=50
            )

            logger.info(f"📊 Found {len(available_races)} races for processing")

            # Get detailed race information
            race_details = []
            for race in available_races[:5]:  # Process first 5 races as sample
                details = self.db.get_race_details(race["race_id"])
                if details:
                    race_details.append(
                        {
                            "race_id": race["race_id"],
                            "course": race["course"],
                            "race_name": race["race_name"],
                            "runners": len(details["participants"]),
                            "participants": details["participants"][:3],  # Sample
                        }
                    )

            # Simulate system health check
            logger.info("🏥 Running system health check...")

            # Check database performance
            db_start = datetime.now()
            course_stats = self.db.get_course_statistics()
            db_time = (datetime.now() - db_start).total_seconds()

            phase_result = {
                "status": "success",
                "duration": (datetime.now() - phase_start).total_seconds(),
                "races_discovered": len(available_races),
                "race_details_processed": len(race_details),
                "sample_race_details": race_details,
                "database_performance": {
                    "query_time": db_time,
                    "courses_available": len(course_stats),
                },
                "system_ready": True,
            }

            self.results["phases"]["startup"] = phase_result

            logger.info(
                f"✅ Phase 2 complete: System ready with "
                f"{len(available_races)} races"
            )
            return phase_result

        except Exception as e:
            logger.error(f"❌ Phase 2 failed: {e}")
            phase_result = {
                "status": "error",
                "duration": (datetime.now() - phase_start).total_seconds(),
                "error": str(e),
            }
            self.results["phases"]["startup"] = phase_result
            raise

    async def simulate_monte_carlo_analysis(self) -> Dict[str, Any]:
        """Phase 3: Simulate Monte Carlo analysis on race data"""
        logger.info("🎲 PHASE 3: Monte Carlo analysis simulation...")

        phase_start = datetime.now()

        try:
            # Get races for analysis
            races = self.db.get_races(
                date_from=self.test_date, date_to=self.test_date, limit=10
            )

            logger.info(f"🧮 Running Monte Carlo analysis on {len(races)} races...")

            # Simulate Monte Carlo analysis for each race
            monte_carlo_results = []

            for race in races:
                # Get race participants
                race_details = self.db.get_race_details(race["race_id"])
                if not race_details or not race_details["participants"]:
                    continue

                participants = race_details["participants"]

                # Simulate Monte Carlo probability calculations
                # Simulate realistic probability analysis
                logger.info(
                    f"  📈 Analyzing race {race['race_id']} at "
                    f"{race['course']} ({len(participants)} runners)"
                )

                # Simulate realistic probability analysis
                race_analysis = {
                    "race_id": race["race_id"],
                    "course": race["course"],
                    "race_name": race["race_name"],
                    "analysis_timestamp": datetime.now(),
                    "runner_count": len(participants),
                    "predictions": [],
                }

                # Generate realistic predictions for each runner
                for i, participant in enumerate(participants):
                    # Simulate Monte Carlo probability calculation
                    base_prob = 1.0 / len(participants)  # Equal probability baseline

                    # Add realistic variance based on odds
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

                    # Monte Carlo simulation result - weighted combination
                    monte_carlo_prob = (implied_prob * 0.7) + (base_prob * 0.3)

                    # Calculate confidence score
                    confidence = abs(monte_carlo_prob - implied_prob) * 100

                    prediction = {
                        "draw": participant.get("draw", i + 1),
                        "name": participant.get("name", f"Horse {i + 1}"),
                        "jockey": participant.get("jockey", "Unknown"),
                        "original_odds": odds_str,
                        "implied_probability": round(implied_prob * 100, 2),
                        "monte_carlo_probability": round(monte_carlo_prob * 100, 2),
                        "confidence_score": round(confidence, 2),
                    }

                    race_analysis["predictions"].append(prediction)

                # Sort by Monte Carlo probability
                def sort_by_probability(x):
                    return x["monte_carlo_probability"]

                race_analysis["predictions"].sort(key=sort_by_probability, reverse=True)

                # Add race-level statistics
                predictions = race_analysis["predictions"]
                favorite_name = predictions[0]["name"] if predictions else "None"
                favorite_prob = (
                    predictions[0]["monte_carlo_probability"] if predictions else 0
                )
                total_prob = sum(p["monte_carlo_probability"] for p in predictions)

                # Calculate prediction confidence
                if predictions:
                    confidence_sum = sum(p["confidence_score"] for p in predictions)
                    avg_confidence = confidence_sum / len(predictions)
                else:
                    avg_confidence = 0

                race_analysis["statistics"] = {
                    "favorite": favorite_name,
                    "favorite_probability": favorite_prob,
                    "total_probability": total_prob,
                    "prediction_confidence": avg_confidence,
                }

                monte_carlo_results.append(race_analysis)

                # Simulate processing delay
                await asyncio.sleep(0.1)

            total_predictions = sum(len(r["predictions"]) for r in monte_carlo_results)
            sample_analysis = monte_carlo_results[0] if monte_carlo_results else None

            # Calculate average confidence
            if monte_carlo_results:
                confidence_sum = sum(
                    r["statistics"]["prediction_confidence"]
                    for r in monte_carlo_results
                )
                avg_confidence = confidence_sum / len(monte_carlo_results)
                total_runners = sum(len(r["predictions"]) for r in monte_carlo_results)
            else:
                avg_confidence = 0
                total_runners = 0

            phase_result = {
                "status": "success",
                "duration": (datetime.now() - phase_start).total_seconds(),
                "races_analyzed": len(monte_carlo_results),
                "total_predictions": total_predictions,
                "sample_analysis": sample_analysis,
                "analysis_summary": {
                    "avg_confidence": avg_confidence,
                    "total_runners_analyzed": total_runners,
                },
            }

            self.results["phases"]["monte_carlo"] = phase_result
            self.results["monte_carlo_results"] = monte_carlo_results

            logger.info(
                f"✅ Phase 3 complete: Analyzed {len(monte_carlo_results)} races "
                f"with {phase_result['total_predictions']} predictions"
            )
            return phase_result

        except Exception as e:
            logger.error(f"❌ Phase 3 failed: {e}")
            phase_result = {
                "status": "error",
                "duration": (datetime.now() - phase_start).total_seconds(),
                "error": str(e),
            }
            self.results["phases"]["monte_carlo"] = phase_result
            raise

    async def simulate_fast_results_processing(self) -> Dict[str, Any]:
        """Phase 4: Simulate fast results processing and generation"""
        logger.info("⚡ PHASE 4: Fast results processing...")

        phase_start = datetime.now()

        try:
            monte_carlo_data = self.results.get("monte_carlo_results", [])

            if not monte_carlo_data:
                raise Exception(
                    "No Monte Carlo data available for fast results processing"
                )

            logger.info(
                f"⚡ Processing fast results for {len(monte_carlo_data)} races..."
            )

            fast_results = []

            for race_analysis in monte_carlo_data:
                logger.info(
                    f"  🏁 Generating fast results for {race_analysis['race_name']}"
                )

                # Simulate fast results generation
                predictions = race_analysis["predictions"]
                if not predictions:
                    continue

                # Generate top 3 selections
                top_selections = predictions[:3]

                # Create fast result summary
                fast_result = {
                    "race_id": race_analysis["race_id"],
                    "course": race_analysis["course"],
                    "race_name": race_analysis["race_name"],
                    "timestamp": datetime.now(),
                    "top_selections": [
                        {
                            "position": i + 1,
                            "name": sel["name"],
                            "jockey": sel["jockey"],
                            "probability": sel["monte_carlo_probability"],
                            "original_odds": sel["original_odds"],
                            "confidence": sel["confidence_score"],
                        }
                        for i, sel in enumerate(top_selections)
                    ],
                    "race_outlook": self._generate_race_outlook(race_analysis),
                    "betting_recommendation": self._generate_betting_recommendation(
                        top_selections
                    ),
                }

                fast_results.append(fast_result)

                # Simulate processing delay
                await asyncio.sleep(0.05)

            phase_result = {
                "status": "success",
                "duration": (datetime.now() - phase_start).total_seconds(),
                "fast_results_generated": len(fast_results),
                "sample_result": fast_results[0] if fast_results else None,
                "processing_speed": len(fast_results)
                / (datetime.now() - phase_start).total_seconds(),
            }

            self.results["phases"]["fast_results"] = phase_result
            self.results["fast_results"] = fast_results

            logger.info(
                f"✅ Phase 4 complete: Generated {len(fast_results)} fast results"
            )
            return phase_result

        except Exception as e:
            logger.error(f"❌ Phase 4 failed: {e}")
            phase_result = {
                "status": "error",
                "duration": (datetime.now() - phase_start).total_seconds(),
                "error": str(e),
            }
            self.results["phases"]["fast_results"] = phase_result
            raise

    def _generate_race_outlook(self, race_analysis: Dict) -> str:
        """Generate a race outlook summary"""
        stats = race_analysis["statistics"]
        favorite = stats["favorite"]
        favorite_prob = stats["favorite_probability"]

        if favorite_prob > 40:
            return f"Strong favorite: {favorite} dominates with {favorite_prob:.1f}% chance"
        elif favorite_prob > 25:
            return f"Competitive race: {favorite} leads at {favorite_prob:.1f}% but close field"
        else:
            return f"Open race: No clear favorite, {favorite} marginally ahead at {favorite_prob:.1f}%"

    def _generate_betting_recommendation(self, top_selections: List) -> str:
        """Generate betting recommendation"""
        if not top_selections:
            return "No clear recommendations"

        favorite = top_selections[0]
        if favorite["probability"] > 40:
            return f"Strong Win bet: {favorite['name']}"
        elif len(top_selections) >= 2 and top_selections[1]["probability"] > 20:
            return f"Each-way or Place bets: {favorite['name']} and {top_selections[1]['name']}"
        else:
            return f"Cautious approach: Small stakes on {favorite['name']}"

    async def simulate_ntfy_notifications(self) -> Dict[str, Any]:
        """Phase 5: Simulate NTFY notifications"""
        logger.info("📱 PHASE 5: NTFY notifications simulation...")

        phase_start = datetime.now()

        try:
            fast_results = self.results.get("fast_results", [])

            if not fast_results:
                raise Exception("No fast results available for notifications")

            logger.info(
                f"📤 Sending NTFY notifications for {len(fast_results)} races..."
            )

            notifications_sent = []

            # Summary notification
            summary_notification = {
                "type": "daily_summary",
                "title": f"🏁 Racing Analysis Complete - {self.test_date}",
                "message": f"Analyzed {len(fast_results)} races with Monte Carlo predictions. Top picks ready!",
                "priority": "default",
                "timestamp": datetime.now(),
            }
            notifications_sent.append(summary_notification)
            logger.info(f"  📨 Sent summary notification")

            # Individual race notifications for top races
            for i, result in enumerate(fast_results[:3]):  # Top 3 races
                if result["top_selections"]:
                    favorite = result["top_selections"][0]

                    race_notification = {
                        "type": "race_prediction",
                        "title": f'🎯 {result["course"]} - {result["race_name"][:30]}',
                        "message": f'Top pick: {favorite["name"]} ({favorite["probability"]:.1f}%) - {result["betting_recommendation"]}',
                        "priority": (
                            "high" if favorite["probability"] > 35 else "default"
                        ),
                        "timestamp": datetime.now(),
                        "race_data": {
                            "race_id": result["race_id"],
                            "course": result["course"],
                            "top_pick": favorite["name"],
                            "probability": favorite["probability"],
                        },
                    }
                    notifications_sent.append(race_notification)
                    logger.info(f"  📨 Sent notification for {result['course']} race")

                # Simulate sending delay
                await asyncio.sleep(0.1)

            # System performance notification
            total_duration = (
                datetime.now() - self.results["test_start"]
            ).total_seconds()
            perf_notification = {
                "type": "system_performance",
                "title": "⚡ System Performance Report",
                "message": f"Complete analysis in {total_duration:.1f}s. All systems operational.",
                "priority": "low",
                "timestamp": datetime.now(),
                "performance_data": {
                    "total_duration": total_duration,
                    "races_processed": len(fast_results),
                    "processing_rate": len(fast_results) / total_duration,
                },
            }
            notifications_sent.append(perf_notification)
            logger.info(f"  📨 Sent performance notification")

            phase_result = {
                "status": "success",
                "duration": (datetime.now() - phase_start).total_seconds(),
                "notifications_sent": len(notifications_sent),
                "notification_types": list(set(n["type"] for n in notifications_sent)),
            }

            self.results["phases"]["ntfy"] = phase_result
            self.results["notifications_sent"] = notifications_sent

            logger.info(
                f"✅ Phase 5 complete: Sent {len(notifications_sent)} notifications"
            )
            return phase_result

        except Exception as e:
            logger.error(f"❌ Phase 5 failed: {e}")
            phase_result = {
                "status": "error",
                "duration": (datetime.now() - phase_start).total_seconds(),
                "error": str(e),
            }
            self.results["phases"]["ntfy"] = phase_result
            raise

    async def run_complete_test(self) -> Dict[str, Any]:
        """Run the complete system integration test"""
        logger.info("🚀 Starting Complete System Integration Test")
        logger.info("=" * 60)

        try:
            # Phase 1: Setup
            await self.setup_test_environment()

            # Phase 2: System startup
            await self.simulate_system_startup()

            # Phase 3: Monte Carlo analysis
            await self.simulate_monte_carlo_analysis()

            # Phase 4: Fast results
            await self.simulate_fast_results_processing()

            # Phase 5: NTFY notifications
            await self.simulate_ntfy_notifications()

            # Calculate final results
            self.results["test_end"] = datetime.now()
            self.results["total_duration"] = (
                self.results["test_end"] - self.results["test_start"]
            ).total_seconds()
            self.results["status"] = "success"

            # System performance metrics
            self.results["system_performance"] = {
                "total_races_processed": len(self.results.get("fast_results", [])),
                "total_predictions_generated": sum(
                    len(r.get("predictions", []))
                    for r in self.results.get("monte_carlo_results", [])
                ),
                "notifications_sent": len(self.results.get("notifications_sent", [])),
                "processing_rate": len(self.results.get("fast_results", []))
                / self.results["total_duration"],
                "phases_completed": len(
                    [
                        p
                        for p in self.results["phases"].values()
                        if p.get("status") == "success"
                    ]
                ),
            }

            logger.info("🎉 COMPLETE SYSTEM INTEGRATION TEST - SUCCESS!")
            logger.info("=" * 60)

            return self.results

        except Exception as e:
            logger.error(f"❌ SYSTEM INTEGRATION TEST FAILED: {e}")
            self.results["test_end"] = datetime.now()
            self.results["total_duration"] = (
                self.results["test_end"] - self.results["test_start"]
            ).total_seconds()
            self.results["status"] = "failed"
            self.results["final_error"] = str(e)

            return self.results

        finally:
            # Cleanup
            if self.db:
                self.db.close()
            if self.race_generator:
                self.race_generator.close_connection()

    def print_results_summary(self):
        """Print a comprehensive results summary"""
        print("\n" + "=" * 80)
        print("🏁 HORSE RACING AI v2.0 - COMPLETE SYSTEM TEST RESULTS")
        print("=" * 80)

        print(f"📅 Test Date: {self.test_date}")
        print(f"⏱️  Total Duration: {self.results['total_duration']:.2f} seconds")
        print(f"✅ Status: {self.results['status'].upper()}")

        if self.results["status"] == "success":
            perf = self.results["system_performance"]
            print(f"\n📊 PERFORMANCE METRICS:")
            print(f"   🏁 Races Processed: {perf['total_races_processed']}")
            print(f"   🎯 Predictions Generated: {perf['total_predictions_generated']}")
            print(f"   📱 Notifications Sent: {perf['notifications_sent']}")
            print(f"   ⚡ Processing Rate: {perf['processing_rate']:.2f} races/second")
            print(f"   ✅ Phases Completed: {perf['phases_completed']}/5")

            print(f"\n🔄 PHASE BREAKDOWN:")
            for phase_name, phase_data in self.results["phases"].items():
                status = "✅" if phase_data["status"] == "success" else "❌"
                print(
                    f"   {status} {phase_name.title()}: {phase_data['duration']:.2f}s"
                )

            if self.results.get("fast_results"):
                sample_result = self.results["fast_results"][0]
                print(f"\n🎯 SAMPLE PREDICTION:")
                print(f"   🏟️  {sample_result['course']} - {sample_result['race_name']}")
                if sample_result["top_selections"]:
                    top_pick = sample_result["top_selections"][0]
                    print(
                        f"   🥇 Top Pick: {top_pick['name']} ({top_pick['probability']:.1f}%)"
                    )
                    print(f"   🏇 Jockey: {top_pick['jockey']}")
                    print(
                        f"   💰 Recommendation: {sample_result['betting_recommendation']}"
                    )

        print("\n" + "=" * 80)


async def main():
    """Main test execution"""
    test = SystemIntegrationTest()

    # Run the complete test
    results = await test.run_complete_test()

    # Print summary
    test.print_results_summary()

    # Save detailed results
    results_file = f"system_integration_test_{test.test_date}_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📁 Detailed results saved to: {results_file}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
