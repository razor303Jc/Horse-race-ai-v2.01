#!/usr/bin/env python3
"""
Test updated pipeline timing with early morning ML training
"""
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path.cwd()))


def test_updated_pipeline_timing():
    """Test the updated pipeline with early morning ML training"""

    print("🧪 Testing Updated Pipeline Timing with Early Morning ML")
    print("=" * 70)

    try:
        # Import the updated pipeline allocator
        sys.path.append("docker/pipeline_management")
        from dynamic_pipeline_timing import PipelineTimeAllocator

        # Create allocator
        allocator = PipelineTimeAllocator()

        # Test with 00:01 download and 13:45 first race
        print("\n📋 Testing with updated schedule:")
        print("   - Auto-download: 00:01")
        print("   - First race: 13:45")
        print("   - Expected ML training: 00:30-04:00")

        # Allocate time slots
        schedule = allocator.allocate_stage_times(
            download_time="00:01", first_race_time="13:45"
        )

        # Check if ML training is in early morning
        stage_schedule = schedule.get("stage_schedule", {})
        ml_training = stage_schedule.get("ml_model_training", {})

        print(f"\n✅ PIPELINE ALLOCATION RESULTS:")
        print(f"   Total stages: {len(stage_schedule)}")
        print(
            f"   ML training allocated: {ml_training.get('duration_minutes', 0)} minutes"
        )
        print(f"   ML training phase: {ml_training.get('phase', 'unknown')}")

        # Check timing analysis
        timing_analysis = schedule.get("timing_analysis", {})
        print(f"\n📊 TIMING ANALYSIS:")
        print(f"   Schedule type: {timing_analysis.get('schedule_type', 'unknown')}")
        print(f"   Time pressure: {timing_analysis.get('time_pressure', 0):.2f}")
        print(f"   Available minutes: {timing_analysis.get('available_minutes', 0)}")
        print(
            f"   Required minutes: {timing_analysis.get('total_required_minutes', 0)}"
        )

        # Look for early morning ML training window
        early_ml_found = False
        if "early_ml_training" in [
            stage.get("phase") for stage in stage_schedule.values()
        ]:
            early_ml_found = True
            print(f"\n🎯 EARLY MORNING ML TRAINING: ✅ Found")
        else:
            print(f"\n🎯 EARLY MORNING ML TRAINING: ❌ Not found")

        # Show key stages timing
        key_stages = ["data_download", "ml_model_training", "monte_carlo_simulations"]
        print(f"\n⏰ KEY STAGES TIMING:")
        for stage_name in key_stages:
            stage = stage_schedule.get(stage_name, {})
            duration = stage.get("duration_minutes", 0)
            phase = stage.get("phase", "unknown")
            print(f"   {stage_name}: {duration} min ({phase})")

        return {
            "success": True,
            "early_ml_found": early_ml_found,
            "ml_training_minutes": ml_training.get("duration_minutes", 0),
            "total_stages": len(stage_schedule),
            "schedule_type": timing_analysis.get("schedule_type", "unknown"),
        }

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = test_updated_pipeline_timing()

    if result["success"]:
        print(f"\n🎉 Pipeline timing test completed!")
        if result.get("early_ml_found"):
            print(f"✅ Early morning ML training successfully configured")
        else:
            print(f"⚠️ Early morning ML training needs verification")
    else:
        print(f"\n💥 Test failed: {result.get('error', 'Unknown error')}")
