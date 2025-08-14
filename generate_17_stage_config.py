#!/usr/bin/env python3
"""
Generate complete 17-stage configuration
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "docker" / "pipeline_management"))

from dynamic_pipeline_timing import PipelineTimeAllocator


def main():
    # Create allocator and generate full 17-stage schedule
    allocator = PipelineTimeAllocator()
    first_race_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
    schedule = allocator.allocate_stage_times("00:01", first_race_time)

    # Create comprehensive config with all 17 stages
    config = {
        "component_name": "pipeline_orchestrator_17_stage",
        "dynamic_schedule": {
            "enabled": True,
            "last_updated": datetime.now().isoformat(),
            "download_time": "00:01",
            "first_race_time": "14:00",
            "total_window_minutes": schedule["timing_analysis"]["total_window_minutes"],
            "schedule_type": schedule["timing_analysis"]["schedule_type"],
            "buffer_minutes": schedule["timing_analysis"]["buffer_minutes"],
        },
        "stages": [],
    }

    # Add all stages from the schedule
    if "schedule" in schedule:
        for stage_name, stage_info in schedule["schedule"].items():
            stage_config = {
                "name": stage_name,
                "start_time": stage_info["start_time"],
                "end_time": stage_info["end_time"],
                "duration_minutes": stage_info["duration_minutes"],
                "description": stage_info["description"],
                "critical": stage_info.get("critical", False),
                "phase": allocator.stage_definitions[stage_name].get(
                    "phase", "unknown"
                ),
            }
            config["stages"].append(stage_config)

    # Sort stages by start time for proper ordering
    config["stages"].sort(key=lambda x: x["start_time"])

    # Add timing summary
    config["timing"] = {
        "start_time": min(stage["start_time"] for stage in config["stages"]),
        "completion_time": max(stage["end_time"] for stage in config["stages"]),
        "total_duration": schedule["timing_analysis"]["allocated_minutes"],
        "stage_count": len(config["stages"]),
        "phase_count": len(set(stage["phase"] for stage in config["stages"])),
    }

    # Save the complete 17-stage configuration
    with open("config/complete_17_stage_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Generated complete 17-stage configuration")
    print(f'📊 Total stages: {len(config["stages"])}')
    print(f'⏱️ Total duration: {config["timing"]["total_duration"]} minutes')
    print(f'🎯 Schedule type: {config["dynamic_schedule"]["schedule_type"]}')
    print(f"📁 Saved to: config/complete_17_stage_config.json")

    # Show first few stages
    print("\n🎯 First 5 stages:")
    for i, stage in enumerate(config["stages"][:5], 1):
        print(
            f'  {i}. {stage["name"]} ({stage["start_time"]}-{stage["end_time"]}) - {stage["description"][:50]}...'
        )


if __name__ == "__main__":
    main()
