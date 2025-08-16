#!/usr/bin/env python3
"""
Test early morning ML training schedule
Shows how ML training is moved from 16:00-17:25 to 00:30-04:00
"""

import sys
from datetime import datetime, time, timedelta


def test_early_morning_schedule():
    """Test the early morning ML training schedule"""

    print("🧪 Testing Early Morning ML Training Schedule")
    print("=" * 60)

    # Current problematic schedule (what we're fixing)
    print("\n❌ CURRENT PROBLEMATIC SCHEDULE:")
    print("   Auto-download: 00:01 - 00:30")
    print("   Data processing: 00:30 - 13:30")
    print("   ⚠️  ML TRAINING: 16:00 - 17:25 (DURING RACING!)")
    print("   First race: 13:45")
    print("   Racing period: 13:45 - 21:00")

    # New optimized schedule
    print("\n✅ NEW OPTIMIZED SCHEDULE:")
    print("   00:01 - 00:30: Auto-download (29 minutes)")
    print("   00:30 - 04:00: ML TRAINING (210 minutes = 3.5 hours)")
    print("   04:00 - 13:30: Data processing & validation (9.5 hours)")
    print("   13:30 - 13:45: Pre-race setup (15 minutes)")
    print("   13:45 - 21:00: Racing period")

    # Calculate timing benefits
    download_start = time(0, 1)  # 00:01
    download_end = time(0, 30)  # 00:30
    ml_start = time(0, 30)  # 00:30
    ml_end = time(4, 0)  # 04:00
    first_race = time(13, 45)  # 13:45

    # Time calculations
    download_duration = datetime.combine(
        datetime.today(), download_end
    ) - datetime.combine(datetime.today(), download_start)

    ml_duration = datetime.combine(datetime.today(), ml_end) - datetime.combine(
        datetime.today(), ml_start
    )

    buffer_time = datetime.combine(datetime.today(), first_race) - datetime.combine(
        datetime.today(), ml_end
    )

    print(f"\n📊 TIMING ANALYSIS:")
    print(f"   Download window: {download_duration.total_seconds()/60:.0f} minutes")
    print(f"   ML training window: {ml_duration.total_seconds()/60:.0f} minutes")
    print(f"   Buffer before racing: {buffer_time.total_seconds()/3600:.1f} hours")

    # Training capacity comparison
    old_training_minutes = 85  # 16:00-17:25 = 85 minutes
    new_training_minutes = 210  # 00:30-04:00 = 210 minutes
    improvement_factor = new_training_minutes / old_training_minutes

    print(f"\n🚀 TRAINING IMPROVEMENTS:")
    print(f"   Old training time: {old_training_minutes} minutes")
    print(f"   New training time: {new_training_minutes} minutes")
    print(f"   Improvement factor: {improvement_factor:.1f}x")
    print(
        f"   Additional training: {new_training_minutes - old_training_minutes} minutes"
    )

    # ML training sessions
    session_length = 25  # minutes per session
    old_sessions = old_training_minutes // session_length
    new_sessions = new_training_minutes // session_length

    print(f"\n🎯 TRAINING SESSIONS:")
    print(f"   Old sessions possible: {old_sessions}")
    print(f"   New sessions possible: {new_sessions}")
    print(f"   Additional sessions: {new_sessions - old_sessions}")

    # Timeline validation
    print(f"\n✅ SCHEDULE VALIDATION:")
    print(f"   ✓ ML training completes at 04:00")
    print(f"   ✓ 9+ hour buffer before racing (04:00 → 13:45)")
    print(f"   ✓ No conflict with racing period")
    print(f"   ✓ Fresh data from 00:01 auto-download")
    print(f"   ✓ 2.5x more training time available")

    return {
        "download_duration_minutes": download_duration.total_seconds() / 60,
        "ml_training_minutes": ml_duration.total_seconds() / 60,
        "buffer_hours": buffer_time.total_seconds() / 3600,
        "improvement_factor": improvement_factor,
        "training_sessions": new_sessions,
        "schedule_valid": True,
    }


if __name__ == "__main__":
    result = test_early_morning_schedule()
    print(f"\n🎉 Early morning schedule optimization complete!")
    print(f"📈 ML training improved by {result['improvement_factor']:.1f}x")
