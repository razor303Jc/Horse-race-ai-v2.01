#!/usr/bin/env python3
"""
Daily Race Release Simulator for Horse Racing AI v2.0

This script simulates the daily release of race cards over a 7-day period,
allowing testing of progressive data availability and daily processing.

Usage:
    python3 tests/daily_race_simulator.py --week-start 2025-08-05 --simulate-days 7
    python3 tests/daily_race_simulator.py --release-today  # Release just today's races
    python3 tests/daily_race_simulator.py --status        # Show current status
"""

import os
import logging
import json
import time
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
import psycopg2
from psycopg2.extras import RealDictCursor

# Import our weekly generator
from weekly_race_cards_generator import WeeklyRaceCardsGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DailyRaceSimulator:
    """Simulate daily race card releases over time"""

    def __init__(self, database_url: str = None):
        """Initialize simulator"""
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://horse_racing_test:test_password_123@localhost:5434/horse_racing_test_db",
        )
        self.generator = WeeklyRaceCardsGenerator(self.database_url)

    def setup_week(self, start_date: date) -> Dict[str, Any]:
        """Set up a complete week's racing schedule"""
        logger.info(f"🗓️ Setting up racing week starting {start_date}")

        # Connect and create schema
        if not self.generator.connect_to_database():
            return {"status": "error", "message": "Database connection failed"}

        if not self.generator.create_weekly_schema():
            return {"status": "error", "message": "Schema creation failed"}

        # Generate weekly schedule (but don't release races yet)
        week_schedule = self.generator.generate_weekly_schedule(start_date)

        logger.info(
            f"✅ Week setup complete: {week_schedule['total_races']} races scheduled"
        )
        return {
            "status": "success",
            "week_schedule": week_schedule,
            "message": f"Week scheduled with {week_schedule['total_races']} races",
        }

    def release_today_races(self, target_date: date = None) -> Dict[str, Any]:
        """Release races for today (or specified date)"""
        if target_date is None:
            target_date = date.today()

        logger.info(f"📅 Releasing races for {target_date}")

        # Connect to database
        if not self.generator.connect_to_database():
            return {"status": "error", "message": "Database connection failed"}

        # Release races for the specified date
        result = self.generator.release_daily_races(target_date)

        if result["status"] == "success":
            logger.info(
                f"✅ Released {result['races_released']} races for {target_date}"
            )
        else:
            logger.error(
                f"❌ Failed to release races: {result.get('message', 'Unknown error')}"
            )

        return result

    def simulate_progressive_release(
        self, start_date: date, days: int = 7, delay_seconds: int = 5
    ) -> Dict[str, Any]:
        """Simulate releasing races day by day with delays"""
        logger.info(f"🚀 Starting {days}-day progressive race release simulation")

        # First setup the complete week
        setup_result = self.setup_week(start_date)
        if setup_result["status"] != "success":
            return setup_result

        simulation_results = {
            "start_date": start_date,
            "simulation_start": datetime.now(),
            "daily_releases": [],
            "total_races": 0,
            "total_runners": 0,
            "status": "running",
        }

        # Release races day by day
        for day_num in range(days):
            current_date = start_date + timedelta(days=day_num)

            logger.info(f"📅 Day {day_num + 1}: Processing {current_date}")
            print(f"\n{'='*60}")
            print(f"DAY {day_num + 1}: {current_date.strftime('%A, %B %d, %Y')}")
            print(f"{'='*60}")

            # Release races for this day
            release_result = self.release_today_races(current_date)

            if release_result["status"] == "success":
                simulation_results["daily_releases"].append(release_result)
                simulation_results["total_races"] += release_result["races_released"]
                simulation_results["total_runners"] += release_result["total_runners"]

                # Show daily summary
                print(f"🏁 Races Released: {release_result['races_released']}")
                print(f"🏇 Total Runners: {release_result['total_runners']}")
                print(f"🏟️ Courses: {', '.join(release_result['courses'])}")
                print(f"⏰ Release Time: {release_result['release_timestamp']}")

                # Show progressive totals
                print(f"\n📊 WEEK PROGRESS:")
                print(f"   Total Races So Far: {simulation_results['total_races']}")
                print(f"   Total Runners So Far: {simulation_results['total_runners']}")
                print(f"   Days Completed: {day_num + 1}/{days}")

            else:
                logger.error(f"❌ Failed to release races for {current_date}")
                print(f"❌ ERROR: {release_result.get('message', 'Unknown error')}")

            # Delay before next day (unless it's the last day)
            if day_num < days - 1:
                print(f"\n⏳ Waiting {delay_seconds} seconds before next day...")
                time.sleep(delay_seconds)

        simulation_results["simulation_end"] = datetime.now()
        simulation_results["duration"] = (
            simulation_results["simulation_end"]
            - simulation_results["simulation_start"]
        ).total_seconds()
        simulation_results["status"] = "completed"

        print(f"\n{'='*60}")
        print("WEEKLY SIMULATION COMPLETE")
        print(f"{'='*60}")
        print(f"📅 Week: {start_date} to {start_date + timedelta(days=6)}")
        print(f"🏁 Total Races Released: {simulation_results['total_races']}")
        print(f"🏇 Total Runners: {simulation_results['total_runners']}")
        print(f"⏱️ Total Duration: {simulation_results['duration']:.2f} seconds")
        print(f"🗓️ Days Processed: {len(simulation_results['daily_releases'])}")
        print(f"{'='*60}")

        return simulation_results

    def get_current_status(self, start_date: date = None) -> Dict[str, Any]:
        """Get current status of race releases"""
        if start_date is None:
            start_date = date.today()

        if not self.generator.connect_to_database():
            return {"status": "error", "message": "Database connection failed"}

        return self.generator.get_week_status(start_date)

    def get_released_races_summary(self, date_filter: date = None) -> Dict[str, Any]:
        """Get summary of released races"""
        try:
            if not self.generator.connect_to_database():
                return {"status": "error", "message": "Database connection failed"}

            with self.generator.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if date_filter:
                    # Get races for specific date
                    cursor.execute(
                        """
                        SELECT rc.course, COUNT(*) as race_count, 
                               SUM(rc.runners) as total_runners,
                               MIN(rc.race_time) as first_race,
                               MAX(rc.race_time) as last_race
                        FROM races_cards rc
                        WHERE rc.date = %s
                        GROUP BY rc.course
                        ORDER BY race_count DESC
                    """,
                        (date_filter,),
                    )
                    daily_summary = cursor.fetchall()

                    cursor.execute(
                        """
                        SELECT COUNT(*) as total_races, SUM(runners) as total_runners
                        FROM races_cards WHERE date = %s
                    """,
                        (date_filter,),
                    )
                    totals = cursor.fetchone()

                    return {
                        "status": "success",
                        "date": date_filter,
                        "daily_summary": [dict(row) for row in daily_summary],
                        "totals": dict(totals) if totals else {},
                    }
                else:
                    # Get overall summary
                    cursor.execute(
                        """
                        SELECT date, COUNT(*) as races, SUM(runners) as runners
                        FROM races_cards
                        WHERE date >= CURRENT_DATE - INTERVAL '7 days'
                        GROUP BY date
                        ORDER BY date DESC
                    """
                    )
                    recent_days = cursor.fetchall()

                    cursor.execute(
                        """
                        SELECT COUNT(DISTINCT course) as courses,
                               COUNT(*) as total_races,
                               SUM(runners) as total_runners
                        FROM races_cards
                        WHERE date >= CURRENT_DATE - INTERVAL '7 days'
                    """
                    )
                    week_totals = cursor.fetchone()

                    return {
                        "status": "success",
                        "recent_days": [dict(row) for row in recent_days],
                        "week_totals": dict(week_totals) if week_totals else {},
                    }

        except Exception as e:
            logger.error(f"Failed to get races summary: {e}")
            return {"status": "error", "message": str(e)}

    def close(self):
        """Close connections"""
        self.generator.close_connection()


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Daily Race Release Simulator")
    parser.add_argument(
        "--week-start",
        type=str,
        help="Week start date (YYYY-MM-DD)",
        default=date.today().isoformat(),
    )
    parser.add_argument(
        "--simulate-days", type=int, help="Number of days to simulate", default=7
    )
    parser.add_argument(
        "--delay", type=int, help="Delay between days in seconds", default=3
    )
    parser.add_argument(
        "--release-today", action="store_true", help="Release just today's races"
    )
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument(
        "--summary", action="store_true", help="Show released races summary"
    )

    args = parser.parse_args()

    try:
        start_date = date.fromisoformat(args.week_start)
    except ValueError:
        logger.error("Invalid date format. Use YYYY-MM-DD")
        return

    simulator = DailyRaceSimulator()

    try:
        if args.release_today:
            # Release just today's races
            result = simulator.release_today_races()
            print(json.dumps(result, indent=2, default=str))

        elif args.status:
            # Show status
            status = simulator.get_current_status(start_date)
            print(json.dumps(status, indent=2, default=str))

        elif args.summary:
            # Show summary
            summary = simulator.get_released_races_summary()
            print(json.dumps(summary, indent=2, default=str))

        else:
            # Run full progressive simulation
            results = simulator.simulate_progressive_release(
                start_date, args.simulate_days, args.delay
            )

            # Save results to file
            results_file = f"weekly_simulation_{start_date}_results.json"
            with open(results_file, "w") as f:
                json.dump(results, f, indent=2, default=str)

            print(f"\n📁 Results saved to: {results_file}")

    finally:
        simulator.close()


if __name__ == "__main__":
    main()
