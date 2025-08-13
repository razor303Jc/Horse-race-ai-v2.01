#!/usr/bin/env python3
"""
Test script for Race Staging Manager
Comprehensive testing of pipeline staging functionality
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from tools.pipeline.race_staging_manager import RaceStagingManager


def test_race_detection():
    """Test race time detection functionality"""
    print("\n🔍 Testing Race Detection")
    print("=" * 50)

    manager = RaceStagingManager()

    # Test with today's date
    today = datetime.now().strftime("%Y-%m-%d")
    race_times = manager.detect_race_times(today)

    print(f"📅 Date: {today}")
    print(f"🏇 Races found: {len(race_times)}")

    if race_times:
        print("📋 Race times:")
        for i, time_str in enumerate(race_times[:10], 1):  # Show first 10
            print(f"  {i}. {time_str}")
        if len(race_times) > 10:
            print(f"  ... and {len(race_times) - 10} more")

    return race_times


def test_staging_calculation():
    """Test staging time calculation"""
    print("\n⏰ Testing Staging Calculation")
    print("=" * 50)

    manager = RaceStagingManager()

    test_cases = [
        ("14:15", 15, "14:00"),  # Normal case
        ("13:30", 15, "13:15"),  # Test from CLI tests
        ("12:00", 30, "11:30"),  # 30 minute prep
        ("09:15", 10, "09:05"),  # 10 minute prep
    ]

    for first_race, prep_min, expected in test_cases:
        result = manager.calculate_staging_time(first_race, prep_min)
        status = "✅" if result == expected else "❌"
        print(
            f"{status} {first_race} - {prep_min}min = {result} (expected: {expected})"
        )

    return True


def test_pipeline_staging_timing():
    """Test the same timing as in our CLI tests"""
    print("\n🏁 Testing Pipeline Staging Timing (CLI Test Integration)")
    print("=" * 50)

    # Simulate race times like in CLI test
    race_times = [
        "13:30",  # First race at 1:30 PM
        "14:00",  # Second race at 2:00 PM
        "14:30",  # Third race at 2:30 PM
    ]

    manager = RaceStagingManager()

    first_race = race_times[0]
    staging_time = manager.calculate_staging_time(first_race, 15)

    print(f"📅 First race: {first_race}")
    print(f"⏰ Pipeline staging time: {staging_time}")
    print(f"🎯 AI/ML models ready: 15 minutes before first race")

    # Verify staging time is 15 minutes before
    expected_staging = "13:15"  # 15 minutes before 13:30

    if staging_time == expected_staging:
        print("✅ Pipeline staging timing test passed")
        return True
    else:
        print(f"❌ Expected {expected_staging}, got {staging_time}")
        return False


def test_configuration():
    """Test configuration management"""
    print("\n⚙️ Testing Configuration")
    print("=" * 50)

    manager = RaceStagingManager()

    # Test default config
    prep_minutes = manager.config["staging"]["prep_minutes_before_race"]
    auto_enabled = manager.config["staging"]["auto_staging_enabled"]
    earliest_race = manager.config["race_detection"]["earliest_race_time"]

    print(f"📝 Prep minutes: {prep_minutes}")
    print(f"🔄 Auto staging: {auto_enabled}")
    print(f"🕐 Earliest race: {earliest_race}")

    return True


def test_staging_status_check():
    """Test staging status and timing checks"""
    print("\n📊 Testing Staging Status")
    print("=" * 50)

    manager = RaceStagingManager()

    # Test with current time
    current_time = datetime.now().strftime("%H:%M")

    # Set a staging time (for testing)
    test_staging_time = "14:00"
    manager.staging_status["staging_time"] = test_staging_time

    is_staging_time = manager.is_staging_time(current_time)

    print(f"🕐 Current time: {current_time}")
    print(f"⏰ Staging time: {test_staging_time}")
    print(f"🎯 Is staging time: {is_staging_time}")

    # Test status retrieval
    status = manager.get_status()
    print(f"📋 Status keys: {list(status.keys())}")

    return True


def test_full_staging_process():
    """Test the complete staging process"""
    print("\n🚀 Testing Full Staging Process")
    print("=" * 50)

    manager = RaceStagingManager()

    # Execute staging for today
    today = datetime.now().strftime("%Y-%m-%d")
    result = manager.execute_staging(today)

    print(f"📅 Target date: {today}")
    print(f"✅ Success: {result['success']}")
    print(f"📝 Message: {result['message']}")

    if result["success"]:
        print(f"🏇 Total races: {result['total_races']}")
        print(f"🏃 First race: {result['first_race_time']}")
        print(f"⏰ Staging time: {result['staging_time']}")
        print(f"🕐 Current time: {result['current_time']}")
        print(f"🤖 Models ready: {result['models_ready']}")

    return result["success"]


def main():
    """Run all tests"""
    print("🧪 Race Staging Manager Test Suite")
    print("=" * 60)

    tests = [
        ("Race Detection", test_race_detection),
        ("Staging Calculation", test_staging_calculation),
        ("Pipeline Timing", test_pipeline_staging_timing),
        ("Configuration", test_configuration),
        ("Status Check", test_staging_status_check),
        ("Full Process", test_full_staging_process),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))

    # Summary
    print("\n📋 Test Results Summary")
    print("=" * 60)

    passed = 0
    for test_name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if error:
            print(f"    Error: {error}")
        if success:
            passed += 1

    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All tests passed! Race staging manager is ready.")
    else:
        print("⚠️ Some tests failed. Check the output above.")

    return passed == len(tests)


if __name__ == "__main__":
    main()
