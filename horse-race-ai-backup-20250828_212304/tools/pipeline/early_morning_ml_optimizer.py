#!/usr/bin/env python3
"""
Early Morning ML Training Pipeline Optimizer
Horse Racing AI v2.02

Optimizes the pipeline to run ML training in the early morning hours
immediately after data download and validation, making full use of
the 13+ hour window from 00:01 to 13:45.

Key changes:
- Move ML training to Phase 2 (right after data acquisition)
- Extend ML training time to use available hours
- Schedule data upload and validation in parallel/sequence
- Ensure ML training completes by 6-7 AM, well before racing
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/early_morning_ml_optimizer.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Import the pipeline timing system
sys.path.insert(0, str(Path(__file__).parent.parent / "docker" / "pipeline_management"))
from dynamic_pipeline_timing import PipelineTimeAllocator


class EarlyMorningMLOptimizer:
    """
    Optimizes pipeline for early morning ML training
    """

    def __init__(self):
        # Create optimized stage definitions for early ML training
        self.optimized_stage_definitions = {
            # Phase 1: Data Acquisition (00:01 - 00:30, ~30 minutes)
            "data_download": {
                "duration_minutes": 5,
                "optimum_minutes": 8,
                "minimum_minutes": 3,
                "description": "Download daily racing data from manual data loading",
                "prerequisites": [],
                "critical": True,
                "phase": "data_acquisition",
                "early_start": True,
            },
            "data_validation_upload": {
                "duration_minutes": 15,  # Combined validation + upload
                "optimum_minutes": 20,
                "minimum_minutes": 10,
                "description": "Validate data quality and upload to database",
                "prerequisites": ["data_download"],
                "critical": True,
                "phase": "data_acquisition",
                "enhanced": True,  # Uses our new data validation uploader
            },
            "data_preprocessing": {
                "duration_minutes": 8,  # Reduced since upload handles some processing
                "description": "Clean and preprocess race data",
                "prerequisites": ["data_validation_upload"],
                "critical": True,
                "phase": "data_acquisition",
            },
            # Phase 2: EARLY MORNING ML TRAINING (00:30 - 03:30, ~180 minutes)
            "early_ml_training": {
                "duration_minutes": 180,  # 3 HOURS of ML training!
                "optimum_minutes": 240,  # Up to 4 hours if available
                "minimum_minutes": 90,  # At least 1.5 hours
                "description": "Intensive ML model training in early morning hours",
                "prerequisites": ["data_preprocessing"],
                "critical": True,
                "phase": "early_ml_training",
                "scalable": True,
                "enhanced_training": True,  # Uses our enhanced training system
                "target_window": "00:30-06:00",  # Complete well before racing
            },
            # Phase 3: Feature Engineering (03:30 - 05:00, ~90 minutes)
            "feature_engineering": {
                "duration_minutes": 45,
                "optimum_minutes": 60,
                "minimum_minutes": 30,
                "description": "Advanced feature engineering with ML insights",
                "prerequisites": ["early_ml_training"],
                "critical": True,
                "phase": "feature_engineering",
                "enhanced": True,  # Can use ML model insights
            },
            "advanced_analytics": {
                "duration_minutes": 45,
                "description": "Advanced analytics using trained models",
                "prerequisites": ["feature_engineering"],
                "critical": True,
                "phase": "feature_engineering",
            },
            # Phase 4: Simulation and Strategy (05:00 - 07:00, ~120 minutes)
            "monte_carlo_simulations": {
                "duration_minutes": 60,  # More time for better simulations
                "description": "Monte Carlo simulations with trained models",
                "prerequisites": ["advanced_analytics"],
                "critical": True,
                "phase": "simulation",
            },
            "strategy_optimization": {
                "duration_minutes": 40,
                "description": "Optimize betting strategies",
                "prerequisites": ["monte_carlo_simulations"],
                "critical": True,
                "phase": "simulation",
            },
            "final_selections": {
                "duration_minutes": 20,
                "description": "Generate final race selections",
                "prerequisites": ["strategy_optimization"],
                "critical": True,
                "phase": "simulation",
            },
            # Phase 5: Pre-Race Preparation (07:00 - 13:30, ~390 minutes buffer)
            "race_card_analysis": {
                "duration_minutes": 30,
                "description": "Analyze race cards and update predictions",
                "prerequisites": ["final_selections"],
                "critical": True,
                "phase": "pre_race",
            },
            "market_monitoring": {
                "duration_minutes": 60,  # Continuous monitoring
                "description": "Monitor betting markets and adjust",
                "prerequisites": ["race_card_analysis"],
                "critical": False,
                "phase": "pre_race",
                "continuous": True,
            },
            "final_preparation": {
                "duration_minutes": 15,
                "description": "Final race preparation",
                "prerequisites": ["market_monitoring"],
                "critical": True,
                "phase": "pre_race",
            },
        }

        # Create directories
        Path("logs").mkdir(exist_ok=True)
        Path("results/early_ml_optimization").mkdir(parents=True, exist_ok=True)

    def calculate_optimized_timeline(
        self, download_start: str = "00:01", first_race_time: str = "13:45"
    ) -> Dict:
        """
        Calculate optimized timeline with early morning ML training
        """
        logger.info(
            f"🌅 Calculating early morning ML timeline: {download_start} → {first_race_time}"
        )

        # Convert times to datetime
        download_dt = datetime.combine(
            datetime.now().date(), datetime.strptime(download_start, "%H:%M").time()
        )

        race_dt = datetime.combine(
            datetime.now().date(), datetime.strptime(first_race_time, "%H:%M").time()
        )

        # Calculate total available time
        total_minutes = int((race_dt - download_dt).total_seconds() / 60)

        logger.info(
            f"📊 Total available time: {total_minutes} minutes ({total_minutes/60:.1f} hours)"
        )

        # Schedule stages chronologically
        current_time = download_dt
        schedule = {}
        phase_timings = {}

        # Group stages by phase
        phases = {}
        for stage_name, stage_def in self.optimized_stage_definitions.items():
            phase = stage_def["phase"]
            if phase not in phases:
                phases[phase] = []
            phases[phase].append((stage_name, stage_def))

        # Schedule phases in order
        phase_order = [
            "data_acquisition",
            "early_ml_training",
            "feature_engineering",
            "simulation",
            "pre_race",
        ]

        total_allocated = 0

        for phase in phase_order:
            if phase not in phases:
                continue

            phase_start = current_time
            phase_duration = 0

            logger.info(f"📋 Scheduling {phase} phase...")

            for stage_name, stage_def in phases[phase]:
                # Determine duration to use
                duration = stage_def["duration_minutes"]

                # For ML training, use more time if available
                if stage_name == "early_ml_training":
                    remaining_time = int((race_dt - current_time).total_seconds() / 60)
                    # Reserve at least 6 hours (360 min) for remaining phases
                    available_for_ml = remaining_time - 360

                    if available_for_ml > duration:
                        duration = min(
                            available_for_ml, stage_def.get("optimum_minutes", duration)
                        )
                        logger.info(
                            f"🤖 Extended ML training to {duration} minutes (was {stage_def['duration_minutes']})"
                        )

                # Schedule the stage
                stage_start = current_time
                stage_end = stage_start + timedelta(minutes=duration)

                schedule[stage_name] = {
                    "start_time": stage_start.strftime("%H:%M"),
                    "end_time": stage_end.strftime("%H:%M"),
                    "duration_minutes": duration,
                    "description": stage_def["description"],
                    "phase": phase,
                    "critical": stage_def.get("critical", False),
                }

                current_time = stage_end
                phase_duration += duration
                total_allocated += duration

                logger.info(
                    f"   {stage_start.strftime('%H:%M')} - {stage_end.strftime('%H:%M')} "
                    f"({duration:2d}m) {stage_name}"
                )

            phase_end = current_time
            phase_timings[phase] = {
                "start_time": phase_start.strftime("%H:%M"),
                "end_time": phase_end.strftime("%H:%M"),
                "duration_minutes": phase_duration,
            }

            logger.info(
                f"✅ {phase} complete: {phase_start.strftime('%H:%M')} - {phase_end.strftime('%H:%M')} ({phase_duration} min)"
            )

        # Calculate buffer time
        pipeline_end = current_time
        buffer_minutes = int((race_dt - pipeline_end).total_seconds() / 60)

        result = {
            "timeline": {
                "download_start": download_start,
                "first_race_time": first_race_time,
                "pipeline_completion": pipeline_end.strftime("%H:%M"),
                "total_window_minutes": total_minutes,
                "allocated_minutes": total_allocated,
                "buffer_minutes": buffer_minutes,
            },
            "schedule": schedule,
            "phase_timings": phase_timings,
            "ml_training_details": {
                "start_time": schedule["early_ml_training"]["start_time"],
                "end_time": schedule["early_ml_training"]["end_time"],
                "duration_minutes": schedule["early_ml_training"]["duration_minutes"],
                "before_racing": schedule["early_ml_training"]["end_time"]
                < first_race_time,
            },
        }

        logger.info(f"🎯 Pipeline Summary:")
        logger.info(
            f"   Total time: {total_minutes} minutes ({total_minutes/60:.1f} hours)"
        )
        logger.info(
            f"   ML training: {schedule['early_ml_training']['duration_minutes']} minutes "
            f"({schedule['early_ml_training']['duration_minutes']/60:.1f} hours)"
        )
        logger.info(
            f"   Buffer time: {buffer_minutes} minutes ({buffer_minutes/60:.1f} hours)"
        )
        logger.info(
            f"   ML completes at: {schedule['early_ml_training']['end_time']} "
            f"(racing starts {first_race_time})"
        )

        return result

    def save_optimized_configuration(self, timeline: Dict) -> str:
        """Save the optimized configuration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/early_ml_optimization/optimized_timeline_{timestamp}.json"

        config = {
            "configuration_type": "early_morning_ml_optimized",
            "creation_timestamp": datetime.now().isoformat(),
            "optimization_summary": {
                "ml_training_hours": timeline["ml_training_details"]["duration_minutes"]
                / 60,
                "total_pipeline_hours": timeline["timeline"]["allocated_minutes"] / 60,
                "buffer_hours": timeline["timeline"]["buffer_minutes"] / 60,
                "ml_completion_time": timeline["ml_training_details"]["end_time"],
                "racing_start_time": timeline["timeline"]["first_race_time"],
            },
            "optimized_timeline": timeline,
        }

        with open(filename, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"💾 Optimized configuration saved: {filename}")
        return filename

    def compare_with_original(self, optimized_timeline: Dict) -> Dict:
        """Compare optimized timeline with original"""
        # Get original timeline using standard allocator
        allocator = PipelineTimeAllocator()

        try:
            first_race_dt = datetime.combine(
                datetime.now().date(),
                datetime.strptime(
                    optimized_timeline["timeline"]["first_race_time"], "%H:%M"
                ).time(),
            )

            original_schedule = allocator.allocate_stage_times("00:01", first_race_dt)

            comparison = {
                "original": {
                    "ml_training_time": original_schedule["schedule"][
                        "ml_model_training"
                    ]["start_time"]
                    + " - "
                    + original_schedule["schedule"]["ml_model_training"]["end_time"],
                    "ml_duration_minutes": original_schedule["schedule"][
                        "ml_model_training"
                    ]["duration_minutes"],
                    "total_buffer_minutes": original_schedule["timing_analysis"][
                        "buffer_minutes"
                    ],
                },
                "optimized": {
                    "ml_training_time": optimized_timeline["ml_training_details"][
                        "start_time"
                    ]
                    + " - "
                    + optimized_timeline["ml_training_details"]["end_time"],
                    "ml_duration_minutes": optimized_timeline["ml_training_details"][
                        "duration_minutes"
                    ],
                    "total_buffer_minutes": optimized_timeline["timeline"][
                        "buffer_minutes"
                    ],
                },
                "improvements": {},
            }

            # Calculate improvements
            ml_time_improvement = (
                optimized_timeline["ml_training_details"]["duration_minutes"]
                - original_schedule["schedule"]["ml_model_training"]["duration_minutes"]
            )

            comparison["improvements"] = {
                "ml_training_time_increase_minutes": ml_time_improvement,
                "ml_training_time_increase_hours": ml_time_improvement / 60,
                "ml_training_multiplier": optimized_timeline["ml_training_details"][
                    "duration_minutes"
                ]
                / original_schedule["schedule"]["ml_model_training"][
                    "duration_minutes"
                ],
                "ml_now_in_early_morning": True,
                "ml_completes_before_racing": optimized_timeline["ml_training_details"][
                    "before_racing"
                ],
            }

        except Exception as e:
            logger.warning(f"⚠️ Could not compare with original: {e}")
            comparison = {"error": str(e)}

        return comparison


def main():
    """Main execution"""
    optimizer = EarlyMorningMLOptimizer()

    # Calculate optimized timeline
    timeline = optimizer.calculate_optimized_timeline("00:01", "13:45")

    # Save configuration
    config_file = optimizer.save_optimized_configuration(timeline)

    # Compare with original
    comparison = optimizer.compare_with_original(timeline)

    print("\n🌅 Early Morning ML Training Optimization Results")
    print("=" * 60)

    print(f"\n⏰ Timeline Summary:")
    print(f"   Download Start: {timeline['timeline']['download_start']}")
    print(f"   First Race: {timeline['timeline']['first_race_time']}")
    print(f"   Pipeline Complete: {timeline['timeline']['pipeline_completion']}")
    print(
        f"   Total Window: {timeline['timeline']['total_window_minutes']/60:.1f} hours"
    )

    print(f"\n🤖 ML Training Details:")
    ml_details = timeline["ml_training_details"]
    print(f"   Training Window: {ml_details['start_time']} - {ml_details['end_time']}")
    print(
        f"   Duration: {ml_details['duration_minutes']} minutes ({ml_details['duration_minutes']/60:.1f} hours)"
    )
    print(
        f"   Completes Before Racing: {'✅ YES' if ml_details['before_racing'] else '❌ NO'}"
    )

    if "improvements" in comparison:
        print(f"\n📊 Improvements vs Original:")
        imp = comparison["improvements"]
        print(
            f"   ML Time Increase: +{imp['ml_training_time_increase_minutes']} minutes ({imp['ml_training_time_increase_hours']:.1f} hours)"
        )
        print(
            f"   ML Time Multiplier: {imp['ml_training_multiplier']:.1f}x more training time"
        )
        print(f"   Early Morning Schedule: ✅ YES (was during racing hours)")

    print(f"\n📋 Phase Schedule:")
    for phase, timing in timeline["phase_timings"].items():
        print(
            f"   {timing['start_time']} - {timing['end_time']} ({timing['duration_minutes']:3d}m) {phase}"
        )

    print(f"\n💾 Configuration saved: {config_file}")


if __name__ == "__main__":
    main()
