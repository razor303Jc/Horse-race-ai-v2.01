#!/usr/bin/env python3
"""
🏇 Dynamic Pipeline Time Allocation System
Distributes pipeline stages optimally from 05:00 to race start time

This system calculates optimal time slots for each pipeline stage based on:
- Download completion time (05:00)
- First race time (dynamically detected)
- Stage complexity and duration requirements
- ML model training cycles (longest duration)
- Monte Carlo simulations
- Real-time adjustments

Author: AI Assistant
Date: August 13, 2025
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PipelineTimeAllocator:
    """Dynamically allocates time slots for pipeline stages based on available time window"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config/dynamic_pipeline_timing.json")
        self.project_root = Path(__file__).parent

        # Stage definitions with estimated durations and dependencies
        self.stage_definitions = {
            "data_download": {
                "duration_minutes": 5,
                "description": "Download daily racing data",
                "prerequisites": [],
                "critical": True,
                "fixed_time": "05:00",  # Fixed schedule
            },
            "data_validation": {
                "duration_minutes": 2,
                "description": "Validate downloaded data integrity",
                "prerequisites": ["data_download"],
                "critical": True,
            },
            "data_preprocessing": {
                "duration_minutes": 10,
                "description": "Clean and preprocess race data",
                "prerequisites": ["data_validation"],
                "critical": True,
            },
            "feature_engineering": {
                "duration_minutes": 15,
                "description": "Extract and engineer features for ML models",
                "prerequisites": ["data_preprocessing"],
                "critical": True,
            },
            "ml_model_training": {
                "duration_minutes": 120,  # 2 hours - longest stage
                "description": "Train/retrain ML models (Random Forest, XGBoost, Neural Networks)",
                "prerequisites": ["feature_engineering"],
                "critical": True,
                "scalable": True,  # Can be shortened if time is limited
            },
            "monte_carlo_simulations": {
                "duration_minutes": 45,
                "description": "Run Monte Carlo simulations for race outcomes",
                "prerequisites": ["ml_model_training"],
                "critical": True,
                "scalable": True,
            },
            "composite_scoring": {
                "duration_minutes": 20,
                "description": "Calculate composite scores and ratings",
                "prerequisites": ["monte_carlo_simulations"],
                "critical": True,
            },
            "betting_strategies": {
                "duration_minutes": 15,
                "description": "Generate betting recommendations",
                "prerequisites": ["composite_scoring"],
                "critical": True,
            },
            "report_generation": {
                "duration_minutes": 10,
                "description": "Generate analysis reports and insights",
                "prerequisites": ["betting_strategies"],
                "critical": False,
            },
            "ai_selections": {
                "duration_minutes": 5,
                "description": "Finalize AI selections for races",
                "prerequisites": ["betting_strategies"],
                "critical": True,
            },
            "pre_race_updates": {
                "duration_minutes": 10,
                "description": "Last-minute data updates and adjustments",
                "prerequisites": ["ai_selections"],
                "critical": True,
                "buffer_stage": True,  # Runs until race time
            },
        }

    def detect_first_race_time(self) -> Optional[datetime]:
        """Detect the first race time from downloaded data"""
        try:
            # Check multiple possible data locations
            data_paths = [
                "data/daily_downloads/cards_data/races/races.csv",
                "data/daily_downloads/results_data/races/races.csv",
            ]

            today = datetime.now().strftime("%Y-%m-%d")

            for data_path in data_paths:
                if Path(data_path).exists():
                    df = pd.read_csv(data_path)

                    # Filter for today's races
                    todays_races = df[df["Date"] == today]

                    if len(todays_races) > 0:
                        # Get the earliest race time
                        earliest_time_str = todays_races["race_time"].min()

                        # Parse time and create datetime object
                        time_obj = datetime.strptime(earliest_time_str, "%H:%M").time()
                        first_race_datetime = datetime.combine(
                            datetime.now().date(), time_obj
                        )

                        logger.info(
                            f"✅ First race detected: {first_race_datetime.strftime('%H:%M')}"
                        )
                        return first_race_datetime

                    else:
                        logger.info(f"ℹ️ No races found for today in {data_path}")

            logger.warning("⚠️ No today's races found - using default time")
            return None

        except Exception as e:
            logger.error(f"❌ Error detecting race time: {e}")
            return None

    def calculate_available_time_window(
        self,
        download_time: str = "05:00",
        first_race_time: Optional[datetime] = None,
        prep_minutes: int = 15,
    ) -> Tuple[datetime, datetime, int]:
        """Calculate the available time window for pipeline execution"""

        # Parse download completion time
        download_dt = datetime.strptime(download_time, "%H:%M").time()
        download_datetime = datetime.combine(datetime.now().date(), download_dt)

        # Detect or use default first race time
        if first_race_time is None:
            # Use default assumption: races typically start around 14:00
            default_race_time = datetime.combine(
                datetime.now().date(), datetime.strptime("14:00", "%H:%M").time()
            )
            first_race_time = default_race_time
            logger.warning(f"⚠️ Using default first race time: 14:00")

        # Calculate pipeline completion deadline (15 minutes before first race)
        pipeline_deadline = first_race_time - timedelta(minutes=prep_minutes)

        # Calculate total available minutes
        available_minutes = int(
            (pipeline_deadline - download_datetime).total_seconds() / 60
        )

        logger.info(
            f"⏰ Time window: {download_datetime.strftime('%H:%M')} → {pipeline_deadline.strftime('%H:%M')} ({available_minutes} minutes)"
        )

        return download_datetime, pipeline_deadline, available_minutes

    def allocate_stage_times(
        self, download_time: str = "05:00", first_race_time: Optional[datetime] = None
    ) -> Dict:
        """Allocate optimal time slots for each pipeline stage"""

        # Calculate available time window
        start_time, end_time, total_minutes = self.calculate_available_time_window(
            download_time, first_race_time
        )

        # Calculate total required time for all stages
        total_required = sum(
            stage["duration_minutes"] for stage in self.stage_definitions.values()
        )

        logger.info(
            f"📊 Time Analysis: Required={total_required}min, Available={total_minutes}min"
        )

        # Create allocation strategy
        if total_minutes >= total_required:
            return self._allocate_normal_schedule(start_time, end_time, total_minutes)
        else:
            return self._allocate_compressed_schedule(
                start_time, end_time, total_minutes
            )

    def _allocate_normal_schedule(
        self, start_time: datetime, end_time: datetime, total_minutes: int
    ) -> Dict:
        """Allocate stages with normal timing (sufficient time available)"""

        current_time = start_time
        stage_schedule = {}

        # Sort stages by dependency order
        ordered_stages = self._resolve_dependencies()

        for stage_name in ordered_stages:
            stage_info = self.stage_definitions[stage_name]

            # Handle fixed time stages
            if "fixed_time" in stage_info:
                stage_time = datetime.strptime(stage_info["fixed_time"], "%H:%M").time()
                stage_datetime = datetime.combine(current_time.date(), stage_time)
            else:
                stage_datetime = current_time

            # Calculate end time for this stage
            stage_end = stage_datetime + timedelta(
                minutes=stage_info["duration_minutes"]
            )

            stage_schedule[stage_name] = {
                "start_time": stage_datetime.strftime("%H:%M"),
                "end_time": stage_end.strftime("%H:%M"),
                "duration_minutes": stage_info["duration_minutes"],
                "description": stage_info["description"],
                "critical": stage_info.get("critical", False),
            }

            # Update current time for next stage
            if "fixed_time" not in stage_info:
                current_time = stage_end

        # Add buffer time information
        final_stage_end = max(
            datetime.strptime(stage["end_time"], "%H:%M").replace(
                year=start_time.year, month=start_time.month, day=start_time.day
            )
            for stage in stage_schedule.values()
        )

        buffer_minutes = int((end_time - final_stage_end).total_seconds() / 60)

        allocation_summary = {
            "schedule": stage_schedule,
            "timing_analysis": {
                "total_window_minutes": total_minutes,
                "allocated_minutes": sum(
                    stage["duration_minutes"] for stage in stage_schedule.values()
                ),
                "buffer_minutes": buffer_minutes,
                "schedule_type": "normal",
                "first_race_time": end_time.strftime("%H:%M"),
                "pipeline_completion": final_stage_end.strftime("%H:%M"),
            },
        }

        logger.info(f"✅ Normal schedule created with {buffer_minutes} minutes buffer")
        return allocation_summary

    def _allocate_compressed_schedule(
        self, start_time: datetime, end_time: datetime, total_minutes: int
    ) -> Dict:
        """Allocate stages with compressed timing (insufficient time available)"""

        logger.warning(f"⚠️ Time pressure detected - creating compressed schedule")

        # Calculate compression ratio
        total_required = sum(
            stage["duration_minutes"] for stage in self.stage_definitions.values()
        )
        compression_ratio = total_minutes / total_required

        current_time = start_time
        stage_schedule = {}

        ordered_stages = self._resolve_dependencies()

        for stage_name in ordered_stages:
            stage_info = self.stage_definitions[stage_name]

            # Handle fixed time stages
            if "fixed_time" in stage_info:
                stage_time = datetime.strptime(stage_info["fixed_time"], "%H:%M").time()
                stage_datetime = datetime.combine(current_time.date(), stage_time)
                duration = stage_info["duration_minutes"]
            else:
                stage_datetime = current_time

                # Compress scalable stages
                if stage_info.get("scalable", False):
                    duration = max(
                        5, int(stage_info["duration_minutes"] * compression_ratio)
                    )
                else:
                    duration = stage_info["duration_minutes"]

            stage_end = stage_datetime + timedelta(minutes=duration)

            stage_schedule[stage_name] = {
                "start_time": stage_datetime.strftime("%H:%M"),
                "end_time": stage_end.strftime("%H:%M"),
                "duration_minutes": duration,
                "original_duration": stage_info["duration_minutes"],
                "compressed": duration < stage_info["duration_minutes"],
                "description": stage_info["description"],
                "critical": stage_info.get("critical", False),
            }

            if "fixed_time" not in stage_info:
                current_time = stage_end

        allocation_summary = {
            "schedule": stage_schedule,
            "timing_analysis": {
                "total_window_minutes": total_minutes,
                "allocated_minutes": sum(
                    stage["duration_minutes"] for stage in stage_schedule.values()
                ),
                "compression_ratio": compression_ratio,
                "schedule_type": "compressed",
                "first_race_time": end_time.strftime("%H:%M"),
                "warnings": ["Time pressure - some stages compressed"],
            },
        }

        logger.warning(
            f"⚠️ Compressed schedule created (ratio: {compression_ratio:.2f})"
        )
        return allocation_summary

    def _resolve_dependencies(self) -> List[str]:
        """Resolve stage dependencies and return ordered execution list"""

        ordered = []
        remaining = set(self.stage_definitions.keys())

        while remaining:
            # Find stages with no unresolved dependencies
            ready = []
            for stage in remaining:
                prereqs = self.stage_definitions[stage].get("prerequisites", [])
                if all(req in ordered for req in prereqs):
                    ready.append(stage)

            if not ready:
                # Circular dependency or error
                logger.error(f"❌ Dependency resolution failed. Remaining: {remaining}")
                ordered.extend(remaining)
                break

            # Add ready stages to execution order
            ordered.extend(ready)
            remaining -= set(ready)

        return ordered

    def save_schedule_config(
        self, allocation: Dict, config_path: Optional[Path] = None
    ) -> None:
        """Save the calculated schedule to configuration file"""

        config_path = config_path or self.config_path
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata
        allocation["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "next_update": (datetime.now() + timedelta(days=1)).isoformat(),
        }

        with open(config_path, "w") as f:
            json.dump(allocation, f, indent=2)

        logger.info(f"✅ Schedule saved to {config_path}")

    def print_schedule_summary(self, allocation: Dict) -> None:
        """Print a human-readable schedule summary"""

        print("🏇 Daily Pipeline Schedule")
        print("=" * 50)

        schedule = allocation["schedule"]
        analysis = allocation["timing_analysis"]

        print(f"📊 Timing Analysis:")
        print(f"   Total window: {analysis['total_window_minutes']} minutes")
        print(f"   Schedule type: {analysis['schedule_type']}")
        print(f"   First race: {analysis['first_race_time']}")

        if "compression_ratio" in analysis:
            print(f"   Compression ratio: {analysis['compression_ratio']:.2f}")

        print(f"\n⏰ Stage Schedule:")

        for stage_name, stage_info in schedule.items():
            status = "🔴" if stage_info.get("critical") else "🟡"
            compressed = " (COMPRESSED)" if stage_info.get("compressed") else ""

            print(
                f"   {status} {stage_info['start_time']}-{stage_info['end_time']}: "
                f"{stage_name.replace('_', ' ').title()}{compressed}"
            )
            print(
                f"      Duration: {stage_info['duration_minutes']}min - {stage_info['description']}"
            )

        if "warnings" in analysis:
            print(f"\n⚠️ Warnings:")
            for warning in analysis["warnings"]:
                print(f"   • {warning}")


def main():
    """Main function to demonstrate the time allocation system"""

    print("🏇 Dynamic Pipeline Time Allocation System")
    print("=" * 60)

    allocator = PipelineTimeAllocator()

    # Try to detect real race time, fallback to demonstration
    first_race_time = allocator.detect_first_race_time()

    if first_race_time is None:
        # For demonstration - simulate typical racing scenarios
        scenarios = [
            ("14:15", "Early afternoon racing"),
            ("17:30", "Evening racing"),
            ("12:00", "Early racing (tight schedule)"),
            ("20:00", "Late racing (lots of time)"),
        ]

        for race_time_str, description in scenarios:
            print(f"\n🎯 Scenario: {description}")
            print("-" * 40)

            # Create simulated race time for today
            race_time = datetime.strptime(race_time_str, "%H:%M").time()
            simulated_race_datetime = datetime.combine(datetime.now().date(), race_time)

            # Calculate allocation
            allocation = allocator.allocate_stage_times(
                download_time="05:00", first_race_time=simulated_race_datetime
            )

            # Print summary
            allocator.print_schedule_summary(allocation)

    else:
        # Use real detected race time
        allocation = allocator.allocate_stage_times(
            download_time="05:00", first_race_time=first_race_time
        )

        allocator.print_schedule_summary(allocation)
        allocator.save_schedule_config(allocation)


if __name__ == "__main__":
    main()
