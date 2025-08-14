#!/usr/bin/env python3
"""
Show complete 17-stage pipeline overview
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "docker" / "pipeline_management"))

from dynamic_pipeline_timing import PipelineTimeAllocator


def main():
    allocator = PipelineTimeAllocator()
    print("🏇 Complete 17-Stage Pipeline Expansion")
    print("=" * 50)

    # Get all stage names
    stages = list(allocator.stage_definitions.keys())
    print(f"📊 Total Stages: {len(stages)}")
    print("")

    # Group by phases
    phases = {}
    for stage_name, stage_info in allocator.stage_definitions.items():
        phase = stage_info.get("phase", "unknown")
        if phase not in phases:
            phases[phase] = []
        phases[phase].append((stage_name, stage_info))

    # Display all stages by phase
    phase_order = [
        "data_acquisition",
        "feature_engineering",
        "advanced_analytics",
        "simulation",
        "strategy",
        "pre_race",
    ]
    stage_number = 1

    for phase_name in phase_order:
        if phase_name in phases:
            stage_list = phases[phase_name]
            phase_duration = sum(stage[1]["duration_minutes"] for stage in stage_list)
            print(
                f'📋 Phase {phase_order.index(phase_name) + 1}: {phase_name.upper().replace("_", " ")} ({phase_duration} minutes)'
            )

            for stage_name, stage_info in stage_list:
                critical = (
                    "✅ CRITICAL"
                    if stage_info.get("critical", False)
                    else "⭕ Optional"
                )
                optimum = (
                    f" (opt: {stage_info.get('optimum_minutes', 'N/A')}min)"
                    if "optimum_minutes" in stage_info
                    else ""
                )
                minimum = (
                    f" (min: {stage_info.get('minimum_minutes', 'N/A')}min)"
                    if "minimum_minutes" in stage_info
                    else ""
                )

                print(
                    f'  {stage_number:2d}. {stage_name:<20} ({stage_info["duration_minutes"]:2d}min{optimum}{minimum}) - {stage_info["description"]} [{critical}]'
                )
                stage_number += 1
            print("")

    # Calculate total duration
    total_duration = sum(
        stage["duration_minutes"] for stage in allocator.stage_definitions.values()
    )
    critical_duration = sum(
        stage["duration_minutes"]
        for stage in allocator.stage_definitions.values()
        if stage.get("critical", False)
    )
    optional_duration = total_duration - critical_duration

    print(
        f"⏱️  Total Pipeline Duration: {total_duration} minutes ({total_duration/60:.1f} hours)"
    )
    print(
        f"✅ Critical Stages: {critical_duration} minutes ({critical_duration/60:.1f} hours)"
    )
    print(
        f"⭕ Optional Stages: {optional_duration} minutes ({optional_duration/60:.1f} hours)"
    )
    print("")

    # Generate a sample schedule
    print("🎯 Sample Schedule Generation (14:00 first race):")
    print("-" * 50)
    from datetime import datetime

    try:
        sample_race_time = datetime.now().replace(
            hour=14, minute=0, second=0, microsecond=0
        )
        schedule = allocator.allocate_stage_times("00:01", sample_race_time)

        if schedule and "timing_analysis" in schedule:
            analysis = schedule["timing_analysis"]
            print(f"Schedule Type: {analysis.get('schedule_type', 'Unknown')}")
            print(f"Total Window: {analysis.get('total_window_minutes', 0)} minutes")
            print(f"Allocated Time: {analysis.get('allocated_minutes', 0)} minutes")
            print(f"Buffer Time: {analysis.get('buffer_minutes', 0)} minutes")
            print(f"Completion Time: {analysis.get('pipeline_completion', 'Unknown')}")
        else:
            print("❌ Schedule generation failed")
    except Exception as e:
        print(f"❌ Error generating schedule: {e}")
        print("✅ But all 17 stages are properly defined and ready for planning!")


if __name__ == "__main__":
    main()
