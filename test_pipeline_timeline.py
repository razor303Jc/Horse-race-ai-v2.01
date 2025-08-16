#!/usr/bin/env python3
"""Test pipeline timeline with 00:01 start"""
import sys

sys.path.insert(0, "docker/pipeline_management")
from datetime import datetime

from dynamic_pipeline_timing import PipelineTimeAllocator

# Test with proper datetime conversion
allocator = PipelineTimeAllocator()

# Convert string to datetime properly
first_race_dt = datetime.combine(
    datetime.now().date(), datetime.strptime("13:45", "%H:%M").time()
)

schedule = allocator.allocate_stage_times("00:01", first_race_dt)

print("🕛 CORRECT Pipeline Timeline (00:01 → 13:45):")
print(
    f'   Total window: {schedule["timing_analysis"]["total_window_minutes"]} minutes ({schedule["timing_analysis"]["total_window_minutes"]/60:.1f} hours)'
)
print(
    f'   Buffer: {schedule["timing_analysis"]["buffer_minutes"]} minutes ({schedule["timing_analysis"]["buffer_minutes"]/60:.1f} hours)'
)

print("\n📋 All Stages in Chronological Order:")
for stage_name, stage in sorted(
    schedule["schedule"].items(), key=lambda x: x[1]["start_time"]
):
    print(
        f'   {stage["start_time"]} - {stage["end_time"]} ({stage["duration_minutes"]:2d}m) {stage_name}'
    )

print(f"\n🔍 ML Training Details:")
ml_stage = schedule["schedule"]["ml_model_training"]
print(f'   Scheduled: {ml_stage["start_time"]} - {ml_stage["end_time"]}')
print(f'   Duration: {ml_stage["duration_minutes"]} minutes')
is_before_race = ml_stage["start_time"] < "13:45"
print(f'   Before racing starts: {"✅ YES" if is_before_race else "❌ NO - PROBLEM!"}')

# Check for data processing stages
print(f"\n📥 Data Processing Stages:")
data_stages = [
    name
    for name in schedule["schedule"].keys()
    if "data" in name.lower()
    or "upload" in name.lower()
    or "validation" in name.lower()
]
for stage_name in data_stages:
    stage = schedule["schedule"][stage_name]
    print(
        f'   {stage["start_time"]} - {stage["end_time"]} ({stage["duration_minutes"]:2d}m) {stage_name}'
    )
