#!/usr/bin/env python3
"""
Timing Scenario Test Suite
Tests the file watcher system under different timing conditions
"""

import asyncio
import pandas as pd
from datetime import datetime, time, timedelta
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.automation.file_watcher_enhanced import RacingDataFileWatcher


class TimingTestSuite:
    """Test suite for timing scenarios"""

    def __init__(self):
        self.watcher = RacingDataFileWatcher()

    async def test_timing_scenarios(self):
        """Test various timing scenarios"""

        # Create sample race data for testing
        test_races = self.create_test_race_data()

        print("🧪 Testing Timing Scenarios")
        print("=" * 50)

        # Test Scenario 1: Optimal timing (morning download)
        await self.test_scenario("OPTIMAL", test_races, "09:00:00")

        # Test Scenario 2: Good timing (late morning)
        await self.test_scenario("GOOD", test_races, "11:30:00")

        # Test Scenario 3: Rushed timing (close to race)
        await self.test_scenario("RUSHED", test_races, "13:00:00")

        # Test Scenario 4: Critical timing (very close)
        await self.test_scenario("CRITICAL", test_races, "13:35:00")

        # Test Scenario 5: Emergency timing (after first race)
        await self.test_scenario("EMERGENCY", test_races, "14:30:00")

    def create_test_race_data(self):
        """Create sample race data for testing"""

        # Sample races throughout the day
        race_times = [
            "13:50:00",
            "14:25:00",
            "15:00:00",
            "15:35:00",
            "16:10:00",
            "16:45:00",
            "17:20:00",
            "17:55:00",
            "18:30:00",
            "19:05:00",
            "19:40:00",
            "20:15:00",
            "20:50:00",
        ]

        courses = ["York", "Kempton", "Carlisle", "Worcester", "Sligo"]

        races_data = []
        for i, race_time in enumerate(race_times):
            today = datetime.now().strftime("%Y-%m-%d")
            races_data.append(
                {
                    "Race_ID": f"R{i+1:03d}",
                    "race_time": f"{today} {race_time}",
                    "Course": courses[i % len(courses)],
                    "race_number": i + 1,
                }
            )

        return pd.DataFrame(races_data)

    async def test_scenario(
        self, scenario_name: str, races_df: pd.DataFrame, simulated_time: str
    ):
        """Test a specific timing scenario"""

        print(f"\n📊 Testing {scenario_name} Scenario")
        print(f"🕐 Simulated Current Time: {simulated_time}")
        print(f"🏇 First Race Time: 13:50:00")

        # Simulate the current time for testing
        current_datetime = datetime.now().replace(
            hour=int(simulated_time.split(":")[0]),
            minute=int(simulated_time.split(":")[1]),
            second=int(simulated_time.split(":")[2]),
        )

        # Manually calculate what the timing analysis should show
        first_race_time = time(13, 50, 0)
        first_race_datetime = datetime.combine(current_datetime.date(), first_race_time)
        time_diff = first_race_datetime - current_datetime
        minutes_until = int(time_diff.total_seconds() / 60)

        # Prepare races data with datetime
        races_df["race_datetime"] = pd.to_datetime(races_df["race_time"])

        # Mock the current time and test
        original_now = datetime.now

        def mock_now():
            return current_datetime

        # Temporarily replace datetime.now
        import datetime as dt_module

        dt_module.datetime.now = mock_now

        try:
            # Test the timing analysis
            timing_result = await self.watcher.analyze_timing_situation(
                races_df, first_race_time
            )

            print(f"⏰ Minutes until first race: {minutes_until}")
            print(
                f"🎯 Timing Category: {timing_result.get('timing_category', 'ERROR')}"
            )
            print(
                f"🔧 Processing Mode: {timing_result.get('processing_mode', 'ERROR')}"
            )
            print(f"🚨 Alert Level: {timing_result.get('alert_level', 'ERROR')}")
            print(
                f"📊 Available Races: {timing_result.get('available_races', 'ERROR')}"
            )
            print(f"❌ Missed Races: {timing_result.get('missed_races', 'ERROR')}")

            # Show recommendations
            recommendations = timing_result.get("recommendations", [])
            print("💡 Recommendations:")
            for rec in recommendations[:2]:  # Show first 2 recommendations
                print(f"   • {rec}")

        except Exception as e:
            print(f"❌ Test failed: {e}")
        finally:
            # Restore original datetime.now
            dt_module.datetime.now = original_now

        print("-" * 50)


async def main():
    """Run the timing test suite"""

    print("🚀 Starting Timing Analysis Test Suite")
    print("🎯 Testing file watcher timing intelligence")
    print()

    test_suite = TimingTestSuite()
    await test_suite.test_timing_scenarios()

    print()
    print("✅ Timing test suite completed!")
    print()
    print("📋 Summary of Timing Categories:")
    print("🟢 OPTIMAL: 3+ hours before first race")
    print("🟡 GOOD: 1-3 hours before first race")
    print("🟠 RUSHED: 20-60 minutes before first race")
    print("🔴 CRITICAL: <20 minutes before first race")
    print("🚨 EMERGENCY: After first race has started")


if __name__ == "__main__":
    asyncio.run(main())
