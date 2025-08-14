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
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

# Setup logging with performance tracking
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Performance logging setup with fallback
performance_logger = logging.getLogger("performance")
try:
    # Try to create logs directory if it doesn't exist
    import os

    os.makedirs("logs", exist_ok=True)
    performance_handler = logging.FileHandler("logs/pipeline_performance.log")
    performance_formatter = logging.Formatter("%(asctime)s - PERF - %(message)s")
    performance_handler.setFormatter(performance_formatter)
    performance_logger.addHandler(performance_handler)
except (PermissionError, OSError):
    # Fall back to console logging if file logging fails
    performance_handler = logging.StreamHandler()
    performance_formatter = logging.Formatter("%(asctime)s - PERF - %(message)s")
    performance_handler.setFormatter(performance_formatter)
    performance_logger.addHandler(performance_handler)
performance_logger.setLevel(logging.INFO)


class PipelineTimeAllocator:
    """Dynamically allocates time slots for pipeline stages based on available time window"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config/dynamic_pipeline_timing.json")
        self.project_root = Path(__file__).parent

        # Performance tracking
        self.performance_metrics = {
            "phase_timings": {},
            "stage_timings": {},
            "total_allocation_time": 0,
            "optimization_passes": 0,
            "compression_events": 0,
            "skipped_stages": 0,
        }
        self.phase_start_times = {}
        self.stage_start_times = {}

        # Allocation vs Actual comparison tracking
        self.allocated_times = {}  # Stores allocated time for each stage/phase
        self.allocation_comparison = {}  # Stores comparison results

        # Time allocation modes
        self.TIME_MODES = {
            "OPTIMUM": "optimum_minutes",  # Best performance time
            "STANDARD": "duration_minutes",  # Normal operation time
            "MINIMUM": "minimum_minutes",  # Absolute minimum time
            "COMPRESSED": "compressed",  # Dynamic compression
            "NO_TIME": "no_time",  # No time allocated
        }

        # Full 17-Stage Pipeline Definitions with optimum/minimum/no-time allocations
        self.stage_definitions = {
            # Phase 1: Data Acquisition and Validation (25 minutes)
            "data_download": {
                "duration_minutes": 5,  # Standard duration
                "optimum_minutes": 8,  # Best performance time
                "minimum_minutes": 3,  # Absolute minimum time
                "no_time_action": "fail",  # Cannot be skipped
                "description": "Download daily racing data",
                "prerequisites": [],
                "critical": True,
                "fixed_time": "05:00",  # Fixed schedule from auto-downloader
                "phase": "data_acquisition",
            },
            "data_validation": {
                "duration_minutes": 3,
                "optimum_minutes": 5,
                "minimum_minutes": 2,
                "no_time_action": "fail",  # Critical validation cannot be skipped
                "description": "Validate downloaded data integrity and completeness",
                "prerequisites": ["data_download"],
                "critical": True,
                "phase": "data_acquisition",
            },
            "data_preprocessing": {
                "duration_minutes": 12,
                "description": "Clean and preprocess race data",
                "prerequisites": ["data_validation"],
                "critical": True,
                "phase": "data_acquisition",
            },
            "data_relationships": {
                "duration_minutes": 8,
                "description": "Process data relationships and linkages",
                "prerequisites": ["data_preprocessing"],
                "critical": True,
                "phase": "data_acquisition",
            },
            # Phase 2: Feature Engineering and Analysis (45 minutes)
            "feature_engineering": {
                "duration_minutes": 18,
                "description": "Extract and engineer features for ML models",
                "prerequisites": ["data_relationships"],
                "critical": True,
                "phase": "feature_engineering",
            },
            "contextual_analysis": {
                "duration_minutes": 15,
                "description": "Generate contextual analysis and insights",
                "prerequisites": ["feature_engineering"],
                "critical": True,
                "phase": "feature_engineering",
            },
            "form_scoring": {
                "duration_minutes": 12,
                "description": "Calculate detailed form scores and ratings",
                "prerequisites": ["contextual_analysis"],
                "critical": True,
                "phase": "feature_engineering",
            },
            # Phase 3: Advanced Analytics (120 minutes)
            "power_ratings": {
                "duration_minutes": 20,
                "description": "Generate power ratings and speed figures",
                "prerequisites": ["form_scoring"],
                "critical": True,
                "phase": "advanced_analytics",
            },
            "speed_analysis": {
                "duration_minutes": 15,
                "description": "Comprehensive speed and pace analysis",
                "prerequisites": ["power_ratings"],
                "critical": True,
                "phase": "advanced_analytics",
            },
            "ml_model_training": {
                "duration_minutes": 85,  # Reduced from 120 to fit 17 stages
                "optimum_minutes": 120,  # Ideal time for full training
                "minimum_minutes": 30,  # Quick training with limited data
                "no_time_action": "basic",  # Use existing models if no time
                "description": "Train/retrain ML models (RF, XGBoost, Neural Networks)",
                "prerequisites": ["speed_analysis"],
                "critical": True,
                "scalable": True,  # Can be shortened if time is limited
                "phase": "advanced_analytics",
            },
            # Phase 4: Simulation and Optimization (50 minutes)
            "monte_carlo_simulations": {
                "duration_minutes": 30,  # Reduced from 45
                "description": "Run Monte Carlo simulations for race outcomes",
                "prerequisites": ["ml_model_training"],
                "critical": True,
                "scalable": True,
                "phase": "simulation",
            },
            "race_trends": {
                "duration_minutes": 10,
                "description": "Analyze race trends and patterns",
                "prerequisites": ["monte_carlo_simulations"],
                "critical": True,
                "phase": "simulation",
            },
            "composite_scoring": {
                "duration_minutes": 10,
                "description": "Calculate composite scores and final ratings",
                "prerequisites": ["race_trends"],
                "critical": True,
                "phase": "simulation",
            },
            # Phase 5: Strategy and Selection (35 minutes)
            "betting_strategies": {
                "duration_minutes": 15,
                "description": "Generate betting recommendations and strategies",
                "prerequisites": ["composite_scoring"],
                "critical": True,
                "phase": "strategy",
            },
            "ai_selections": {
                "duration_minutes": 8,
                "description": "Finalize AI selections for races",
                "prerequisites": ["betting_strategies"],
                "critical": True,
                "phase": "strategy",
            },
            "report_generation": {
                "duration_minutes": 12,
                "description": "Generate comprehensive analysis reports",
                "prerequisites": ["ai_selections"],
                "critical": False,
                "phase": "strategy",
            },
            # Phase 6: Pre-Race Operations (15 minutes)
            "pre_race_updates": {
                "duration_minutes": 15,
                "description": "Last-minute data updates and live adjustments",
                "prerequisites": ["report_generation"],
                "critical": True,
                "buffer_stage": True,  # Runs until race time
                "phase": "pre_race",
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

    def start_phase_timing(self, phase_name: str) -> None:
        """Start timing a pipeline phase"""
        start_time = time.time()
        self.phase_start_times[phase_name] = start_time
        performance_logger.info(f"PHASE_START - {phase_name}")
        logger.debug(f"⏱️ Started timing phase: {phase_name}")

    def end_phase_timing(self, phase_name: str) -> float:
        """End timing a pipeline phase and log results"""
        end_time = time.time()
        if phase_name in self.phase_start_times:
            duration = end_time - self.phase_start_times[phase_name]
            self.performance_metrics["phase_timings"][phase_name] = duration
            performance_logger.info(f"PHASE_END - {phase_name} - {duration:.3f}s")
            logger.info(f"⏱️ Phase {phase_name} completed in {duration:.3f}s")
            return duration
        else:
            logger.warning(f"⚠️ Phase {phase_name} timing not started")
            return 0.0

    def start_stage_timing(self, stage_name: str) -> None:
        """Start timing a pipeline stage"""
        start_time = time.time()
        self.stage_start_times[stage_name] = start_time
        performance_logger.info(f"STAGE_START - {stage_name}")
        logger.debug(f"⏱️ Started timing stage: {stage_name}")

    def end_stage_timing(self, stage_name: str) -> float:
        """End timing a pipeline stage and log results"""
        end_time = time.time()
        if stage_name in self.stage_start_times:
            duration = end_time - self.stage_start_times[stage_name]
            self.performance_metrics["stage_timings"][stage_name] = duration
            performance_logger.info(f"STAGE_END - {stage_name} - {duration:.3f}s")
            logger.info(f"⏱️ Stage {stage_name} completed in {duration:.3f}s")

            # Compare with allocated time if available
            self._compare_allocated_vs_actual(stage_name, duration, "stage")

            return duration
        else:
            logger.warning(f"⚠️ Stage {stage_name} timing not started")
            return 0.0

    def set_allocated_time(
        self, name: str, allocated_minutes: float, allocation_type: str = "stage"
    ) -> None:
        """Set the allocated time for a stage or phase"""
        allocated_seconds = allocated_minutes * 60
        self.allocated_times[name] = {
            "allocated_seconds": allocated_seconds,
            "allocated_minutes": allocated_minutes,
            "type": allocation_type,
            "timestamp": datetime.now().isoformat(),
        }
        performance_logger.info(
            f"ALLOCATION_SET - {name} - {allocated_minutes:.2f}min - {allocation_type}"
        )

    def _compare_allocated_vs_actual(
        self, name: str, actual_seconds: float, timing_type: str
    ) -> None:
        """Compare allocated time vs actual execution time"""
        if name not in self.allocated_times:
            return

        allocated_data = self.allocated_times[name]
        allocated_seconds = allocated_data["allocated_seconds"]
        allocated_minutes = allocated_data["allocated_minutes"]
        actual_minutes = actual_seconds / 60

        # Calculate variance
        variance_seconds = actual_seconds - allocated_seconds
        variance_minutes = actual_minutes - allocated_minutes
        variance_percentage = (
            (variance_seconds / allocated_seconds) * 100 if allocated_seconds > 0 else 0
        )  # Determine status
        if abs(variance_percentage) <= 10:
            status = "ON_TARGET"
        elif variance_percentage > 10:
            status = "OVER_ALLOCATED"
        else:
            status = "UNDER_ALLOCATED"

        # Store comparison result
        comparison_result = {
            "allocated_minutes": allocated_minutes,
            "actual_minutes": actual_minutes,
            "variance_minutes": variance_minutes,
            "variance_percentage": variance_percentage,
            "status": status,
            "type": timing_type,
            "timestamp": datetime.now().isoformat(),
        }

        self.allocation_comparison[name] = comparison_result

        # Log the comparison
        performance_logger.info(
            f"ALLOCATION_COMPARE - {name} - "
            f"Allocated:{allocated_minutes:.2f}min - "
            f"Actual:{actual_minutes:.2f}min - "
            f"Variance:{variance_percentage:.1f}% - "
            f"Status:{status}"
        )

        # Console log for significant variances
        if abs(variance_percentage) > 25:
            if variance_percentage > 0:
                logger.warning(
                    f"🟡 {name} took {actual_minutes:.2f}min "
                    f"(allocated {allocated_minutes:.2f}min, "
                    f"+{variance_percentage:.1f}% over)"
                )
            else:
                logger.info(
                    f"🟢 {name} completed in {actual_minutes:.2f}min "
                    f"(allocated {allocated_minutes:.2f}min, "
                    f"{abs(variance_percentage):.1f}% under)"
                )

    def get_allocation_summary(self) -> Dict:
        """Get comprehensive allocation vs actual performance summary"""
        summary = {
            "total_comparisons": len(self.allocation_comparison),
            "on_target": 0,
            "over_allocated": 0,
            "under_allocated": 0,
            "average_variance": 0,
            "total_allocated_time": 0,
            "total_actual_time": 0,
            "details": [],
        }

        if not self.allocation_comparison:
            return summary

        total_variance = 0
        for name, comparison in self.allocation_comparison.items():
            # Count status types
            if comparison["status"] == "ON_TARGET":
                summary["on_target"] += 1
            elif comparison["status"] == "OVER_ALLOCATED":
                summary["over_allocated"] += 1
            else:
                summary["under_allocated"] += 1

            # Accumulate totals
            summary["total_allocated_time"] += comparison["allocated_minutes"]
            summary["total_actual_time"] += comparison["actual_minutes"]
            total_variance += comparison["variance_percentage"]

            # Add to details
            summary["details"].append(
                {
                    "name": name,
                    "allocated": comparison["allocated_minutes"],
                    "actual": comparison["actual_minutes"],
                    "variance_pct": comparison["variance_percentage"],
                    "status": comparison["status"],
                }
            )

        # Calculate averages
        summary["average_variance"] = total_variance / len(self.allocation_comparison)
        summary["total_variance_minutes"] = (
            summary["total_actual_time"] - summary["total_allocated_time"]
        )
        summary["total_variance_percentage"] = (
            (
                (summary["total_actual_time"] - summary["total_allocated_time"])
                / summary["total_allocated_time"]
                * 100
            )
            if summary["total_allocated_time"] > 0
            else 0
        )

        return summary

    def log_allocation_performance(self, allocation_type: str, duration: float) -> None:
        """Log allocation algorithm performance"""
        self.performance_metrics["total_allocation_time"] += duration
        self.performance_metrics["optimization_passes"] += 1

        performance_logger.info(f"ALLOCATION - {allocation_type} - {duration:.3f}s")
        logger.info(f"🔧 {allocation_type} allocation completed in {duration:.3f}s")

    def log_compression_event(
        self, compression_ratio: float, stages_affected: int
    ) -> None:
        """Log time compression events"""
        self.performance_metrics["compression_events"] += 1

        performance_logger.info(
            f"COMPRESSION - ratio:{compression_ratio:.3f} - stages:{stages_affected}"
        )
        logger.warning(
            f"🗜️ Time compression applied: {compression_ratio:.3f} ratio "
            f"affecting {stages_affected} stages"
        )

    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "phase_performance": {},
            "stage_performance": {},
            "allocation_performance": {
                "total_time": self.performance_metrics["total_allocation_time"],
                "average_time": (
                    self.performance_metrics["total_allocation_time"]
                    / max(1, self.performance_metrics["optimization_passes"])
                ),
                "optimization_passes": self.performance_metrics["optimization_passes"],
                "compression_events": self.performance_metrics["compression_events"],
            },
            "efficiency_metrics": {},
        }

        # Phase performance analysis
        for phase, duration in self.performance_metrics["phase_timings"].items():
            phase_stages = [
                name
                for name, info in self.stage_definitions.items()
                if info.get("phase") == phase
            ]
            stage_durations = [
                self.performance_metrics["stage_timings"].get(stage, 0)
                for stage in phase_stages
            ]

            report["phase_performance"][phase] = {
                "duration": duration,
                "stage_count": len(phase_stages),
                "average_stage_time": (
                    sum(stage_durations) / max(1, len(stage_durations))
                ),
                "fastest_stage": min(stage_durations) if stage_durations else 0,
                "slowest_stage": max(stage_durations) if stage_durations else 0,
            }

        # Stage performance analysis
        for stage, duration in self.performance_metrics["stage_timings"].items():
            stage_info = self.stage_definitions.get(stage, {})
            # Convert to seconds
            expected_duration = stage_info.get("duration_minutes", 0) * 60

            report["stage_performance"][stage] = {
                "actual_duration": duration,
                "expected_duration": expected_duration,
                "performance_ratio": duration / max(0.1, expected_duration),
                "phase": stage_info.get("phase", "unknown"),
                "critical": stage_info.get("critical", False),
            }

        # Efficiency metrics
        total_stage_time = sum(self.performance_metrics["stage_timings"].values())
        total_phase_time = sum(self.performance_metrics["phase_timings"].values())

        report["efficiency_metrics"] = {
            "total_execution_time": total_stage_time,
            "phase_overhead": total_phase_time - total_stage_time,
            "average_stage_time": (
                total_stage_time
                / max(1, len(self.performance_metrics["stage_timings"]))
            ),
            "performance_variability": self._calculate_performance_variability(),
            "bottleneck_stages": self._identify_bottleneck_stages(),
        }

        # Add allocation comparison analysis
        allocation_summary = self.get_allocation_summary()
        report["allocation_comparison"] = allocation_summary

        return report

    def _calculate_performance_variability(self) -> float:
        """Calculate performance variability across stages"""
        if not self.performance_metrics["stage_timings"]:
            return 0.0

        durations = list(self.performance_metrics["stage_timings"].values())
        mean_duration = sum(durations) / len(durations)
        variance = sum((d - mean_duration) ** 2 for d in durations) / len(durations)
        return (variance**0.5) / mean_duration if mean_duration > 0 else 0.0

    def _identify_bottleneck_stages(self) -> List[Dict]:
        """Identify stages that are performance bottlenecks"""
        bottlenecks = []

        for stage, duration in self.performance_metrics["stage_timings"].items():
            stage_info = self.stage_definitions.get(stage, {})
            expected_duration = stage_info.get("duration_minutes", 0) * 60

            if expected_duration > 0 and duration > expected_duration * 1.5:
                bottlenecks.append(
                    {
                        "stage": stage,
                        "actual_duration": duration,
                        "expected_duration": expected_duration,
                        "slowdown_factor": duration / expected_duration,
                        "phase": stage_info.get("phase", "unknown"),
                    }
                )

        return sorted(bottlenecks, key=lambda x: x["slowdown_factor"], reverse=True)

    def save_performance_report(
        self, report: Dict, filename: Optional[str] = None
    ) -> None:
        """Save performance report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/performance_report_{timestamp}.json"

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "w") as f:
            json.dump(report, f, indent=2, default=str)

        performance_logger.info(f"REPORT_SAVED - {filename}")
        logger.info(f"💾 Performance report saved to {filename}")

    def reset_performance_metrics(self) -> None:
        """Reset all performance tracking metrics"""
        self.performance_metrics = {
            "phase_timings": {},
            "stage_timings": {},
            "total_allocation_time": 0,
            "optimization_passes": 0,
            "compression_events": 0,
            "skipped_stages": 0,
        }
        self.phase_start_times = {}
        self.stage_start_times = {}

        performance_logger.info("METRICS_RESET")
        logger.info("🔄 Performance metrics reset")

    def performance_context(self, name: str, context_type: str = "stage"):
        """Context manager for automatic performance tracking"""
        return PerformanceContext(self, name, context_type)

    def calculate_optimal_duration(
        self, stage_name: str, available_time: int, time_pressure: float
    ) -> Tuple[int, str]:
        """Calculate optimal duration for a stage based on time pressure"""
        stage_info = self.stage_definitions[stage_name]

        # Get timing options
        optimum = stage_info.get(
            "optimum_minutes", stage_info["duration_minutes"] * 1.5
        )
        standard = stage_info["duration_minutes"]
        minimum = stage_info.get("minimum_minutes", max(1, standard // 2))

        # Apply time pressure logic
        if time_pressure < 0.7:  # Low pressure - use optimum
            return int(optimum), "optimum"
        elif time_pressure < 1.2:  # Normal pressure - use standard
            return standard, "standard"
        elif time_pressure < 2.0:  # High pressure - use minimum
            return minimum, "minimum"
        else:  # Critical pressure - compressed time
            compressed = max(1, minimum // 2)
            return compressed, "compressed"


class PerformanceContext:
    """Context manager for automatic timing of pipeline operations"""

    def __init__(self, timing_manager, name: str, context_type: str = "stage"):
        self.timing_manager = timing_manager
        self.name = name
        self.context_type = context_type

    def __enter__(self):
        if self.context_type == "phase":
            self.timing_manager.start_phase_timing(self.name)
        else:
            self.timing_manager.start_stage_timing(self.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context_type == "phase":
            self.timing_manager.end_phase_timing(self.name)
        else:
            self.timing_manager.end_stage_timing(self.name)

    # Move methods back to PipelineTimeAllocator class
    def handle_no_time_stage(self, stage_name: str) -> Dict:
        """Handle stage that gets zero time allocation"""
        stage_info = self.stage_definitions[stage_name]

        # Get timing options
        optimum = stage_info.get(
            "optimum_minutes", stage_info["duration_minutes"] * 1.5
        )
        standard = stage_info["duration_minutes"]
        minimum = stage_info.get("minimum_minutes", max(1, standard // 2))

        # Determine mode based on time pressure
        if time_pressure <= 0.7:  # High pressure - 70% or less available time
            if available_time < minimum:
                # No time available - check action
                no_time_action = stage_info.get("no_time_action", "skip")
                if no_time_action == "fail":
                    return minimum, "CRITICAL_MINIMUM"  # Must run minimum
                elif no_time_action == "basic":
                    return max(1, minimum // 2), "BASIC_ONLY"
                else:  # skip
                    return 0, "NO_TIME"
            else:
                return minimum, "MINIMUM"
        elif time_pressure <= 1.0:  # Normal pressure - exactly enough time
            return min(standard, available_time), "STANDARD"
        else:  # Low pressure - more than enough time
            return min(optimum, available_time), "OPTIMUM"

    def handle_no_time_stage(self, stage_name: str) -> Dict:
        """Handle stage with no time allocation"""
        stage_info = self.stage_definitions[stage_name]
        no_time_action = stage_info.get("no_time_action", "skip")

        return {
            "start_time": "SKIPPED",
            "end_time": "SKIPPED",
            "duration_minutes": 0,
            "action": no_time_action,
            "description": stage_info["description"],
            "critical": stage_info.get("critical", False),
            "skipped": True,
            "reason": f"No time available - action: {no_time_action}",
        }

    def allocate_enhanced_schedule(
        self, download_time: str = "06:01", first_race_time: Optional[datetime] = None
    ) -> Dict:
        """Enhanced allocation with optimum/minimum/no-time logic"""
        logger.info(
            "🎯 Creating enhanced schedule with optimum/minimum/no-time logic..."
        )

        # Calculate available time window
        start_time, end_time, total_minutes = self.calculate_available_time_window(
            download_time, first_race_time
        )

        # Calculate total required time and pressure
        total_required = sum(
            stage["duration_minutes"] for stage in self.stage_definitions.values()
        )
        time_pressure = total_minutes / total_required if total_required > 0 else 1.0

        logger.info(
            f"📊 Time pressure: {time_pressure:.2f} ({total_minutes}min available / {total_required}min required)"
        )

        current_time = start_time
        stage_schedule = {}
        remaining_time = total_minutes

        # Get ordered stages
        ordered_stages = self._resolve_dependencies()

        for stage_name in ordered_stages:
            stage_info = self.stage_definitions[stage_name]

            # Handle fixed time stages
            if "fixed_time" in stage_info:
                stage_time = datetime.strptime(stage_info["fixed_time"], "%H:%M").time()
                stage_datetime = datetime.combine(current_time.date(), stage_time)
                duration = stage_info["duration_minutes"]
                timing_mode = "FIXED"
            else:
                stage_datetime = current_time
                duration, timing_mode = self.calculate_optimal_duration(
                    stage_name, remaining_time, time_pressure
                )

            # Handle no-time stages
            if duration == 0:
                stage_schedule[stage_name] = self.handle_no_time_stage(stage_name)
                continue

            # Calculate end time
            stage_end = stage_datetime + timedelta(minutes=duration)

            stage_schedule[stage_name] = {
                "start_time": stage_datetime.strftime("%H:%M"),
                "end_time": stage_end.strftime("%H:%M"),
                "duration_minutes": duration,
                "timing_mode": timing_mode,
                "description": stage_info["description"],
                "critical": stage_info.get("critical", False),
                "optimum_minutes": stage_info.get(
                    "optimum_minutes", stage_info["duration_minutes"] * 1.5
                ),
                "minimum_minutes": stage_info.get(
                    "minimum_minutes", max(1, stage_info["duration_minutes"] // 2)
                ),
                "no_time_action": stage_info.get("no_time_action", "skip"),
            }

            # Update time tracking
            if "fixed_time" not in stage_info:
                current_time = stage_end
                remaining_time -= duration

        # Calculate summary
        allocated_time = sum(
            stage.get("duration_minutes", 0) for stage in stage_schedule.values()
        )
        skipped_stages = sum(
            1 for stage in stage_schedule.values() if stage.get("skipped", False)
        )

        return {
            "schedule": stage_schedule,
            "timing_analysis": {
                "total_window_minutes": total_minutes,
                "allocated_minutes": allocated_time,
                "remaining_minutes": total_minutes - allocated_time,
                "time_pressure": time_pressure,
                "skipped_stages": skipped_stages,
                "timing_modes_used": list(
                    set(
                        stage.get("timing_mode", "UNKNOWN")
                        for stage in stage_schedule.values()
                    )
                ),
                "compression_ratio": (
                    allocated_time / total_required if total_required > 0 else 1.0
                ),
            },
            "download_time": download_time,
            "first_race_time": (
                first_race_time.strftime("%H:%M")
                if first_race_time
                else "Auto-detected"
            ),
            "enhanced_features": {
                "optimum_allocation": time_pressure > 1.2,
                "minimum_allocation": time_pressure < 0.7,
                "no_time_handling": skipped_stages > 0,
                "dynamic_compression": time_pressure < 1.0,
            },
        }

    def calculate_17_stage_allocation(
        self, download_time: str = "06:25", first_race_time: Optional[datetime] = None
    ) -> Dict:
        """Enhanced allocation specifically designed for all 17 pipeline stages"""
        logger.info("🎯 Calculating optimal 17-stage pipeline allocation...")

        # Calculate available time window
        start_time, end_time, total_minutes = self.calculate_available_time_window(
            download_time, first_race_time
        )

        # Calculate total required time for all 17 stages
        total_required = sum(
            stage["duration_minutes"] for stage in self.stage_definitions.values()
        )

        # Get phase breakdown
        phase_analysis = self._analyze_phases()

        logger.info(
            f"📊 17-Stage Analysis: Required={total_required}min, "
            f"Available={total_minutes}min, Phases={len(phase_analysis)}"
        )

        # Choose allocation strategy based on available time
        if total_minutes >= (total_required + 30):  # 30min buffer minimum
            return self._allocate_17_stage_optimal(
                start_time, end_time, total_minutes, phase_analysis
            )
        elif total_minutes >= total_required:
            return self._allocate_17_stage_tight(
                start_time, end_time, total_minutes, phase_analysis
            )
        else:
            return self._allocate_17_stage_compressed(
                start_time, end_time, total_minutes, phase_analysis
            )

    def _analyze_phases(self) -> Dict:
        """Analyze the 6 phases of the 17-stage pipeline"""
        phases = {}

        for stage_name, stage_info in self.stage_definitions.items():
            phase = stage_info.get("phase", "unknown")
            if phase not in phases:
                phases[phase] = {
                    "stages": [],
                    "total_duration": 0,
                    "critical_stages": 0,
                    "scalable_stages": 0,
                }

            phases[phase]["stages"].append(stage_name)
            phases[phase]["total_duration"] += stage_info["duration_minutes"]

            if stage_info.get("critical", False):
                phases[phase]["critical_stages"] += 1
            if stage_info.get("scalable", False):
                phases[phase]["scalable_stages"] += 1

        return phases

    def _allocate_17_stage_optimal(
        self,
        start_time: datetime,
        end_time: datetime,
        total_minutes: int,
        phase_analysis: Dict,
    ) -> Dict:
        """Optimal allocation with buffer time for all 17 stages"""
        logger.info("✅ Creating optimal 17-stage schedule with buffer time")

        current_time = start_time
        stage_schedule = {}

        # Add small buffer between phases (2 minutes each)
        phase_buffer = 2

        # Sort stages by dependency order
        ordered_stages = self._resolve_dependencies()

        for stage_name in ordered_stages:
            stage_info = self.stage_definitions[stage_name]

            # Handle fixed time stages (like auto-downloader at 06:25)
            if "fixed_time" in stage_info:
                stage_time = datetime.strptime(stage_info["fixed_time"], "%H:%M").time()
                stage_datetime = datetime.combine(current_time.date(), stage_time)
            else:
                stage_datetime = current_time

            # Use full duration in optimal mode
            duration = stage_info["duration_minutes"]
            stage_end = stage_datetime + timedelta(minutes=duration)

            stage_schedule[stage_name] = {
                "start_time": stage_datetime.strftime("%H:%M"),
                "end_time": stage_end.strftime("%H:%M"),
                "duration_minutes": duration,
                "description": stage_info["description"],
                "critical": stage_info.get("critical", False),
                "phase": stage_info.get("phase", "unknown"),
            }

            # Update current time with small buffer between phases
            if "fixed_time" not in stage_info:
                next_stage_idx = ordered_stages.index(stage_name) + 1
                if next_stage_idx < len(ordered_stages) and self.stage_definitions[
                    ordered_stages[next_stage_idx]
                ].get("phase") != stage_info.get("phase"):
                    # Add buffer between phases
                    current_time = stage_end + timedelta(minutes=phase_buffer)
                else:
                    current_time = stage_end

        return self._finalize_schedule(
            stage_schedule, start_time, end_time, total_minutes, "optimal"
        )

    def _allocate_17_stage_tight(
        self,
        start_time: datetime,
        end_time: datetime,
        total_minutes: int,
        phase_analysis: Dict,
    ) -> Dict:
        """Tight allocation with minimal buffer for all 17 stages"""
        logger.info("⚡ Creating tight 17-stage schedule with minimal buffer")

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

            # Use full duration but no buffers
            duration = stage_info["duration_minutes"]
            stage_end = stage_datetime + timedelta(minutes=duration)

            stage_schedule[stage_name] = {
                "start_time": stage_datetime.strftime("%H:%M"),
                "end_time": stage_end.strftime("%H:%M"),
                "duration_minutes": duration,
                "description": stage_info["description"],
                "critical": stage_info.get("critical", False),
                "phase": stage_info.get("phase", "unknown"),
            }

            if "fixed_time" not in stage_info:
                current_time = stage_end

        return self._finalize_schedule(
            stage_schedule, start_time, end_time, total_minutes, "tight"
        )

    def _allocate_17_stage_compressed(
        self,
        start_time: datetime,
        end_time: datetime,
        total_minutes: int,
        phase_analysis: Dict,
    ) -> Dict:
        """Compressed allocation for all 17 stages with intelligent scaling"""
        logger.warning(
            "⚠️ Creating compressed 17-stage schedule - time pressure detected"
        )

        # Calculate compression needed
        total_required = sum(
            stage["duration_minutes"] for stage in self.stage_definitions.values()
        )
        compression_ratio = total_minutes / total_required

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
                duration = stage_info["duration_minutes"]  # Don't compress fixed stages
            else:
                stage_datetime = current_time

                # Intelligent compression based on stage characteristics
                if stage_info.get("scalable", False):
                    # Scalable stages can be compressed more aggressively
                    duration = max(
                        5, int(stage_info["duration_minutes"] * compression_ratio)
                    )
                elif stage_info.get("critical", True):
                    # Critical stages get minimal compression
                    duration = max(
                        int(stage_info["duration_minutes"] * 0.8),  # Max 20% reduction
                        int(stage_info["duration_minutes"] * compression_ratio),
                    )
                else:
                    # Non-critical stages can be compressed more
                    duration = max(
                        3, int(stage_info["duration_minutes"] * compression_ratio)
                    )

            stage_end = stage_datetime + timedelta(minutes=duration)

            stage_schedule[stage_name] = {
                "start_time": stage_datetime.strftime("%H:%M"),
                "end_time": stage_end.strftime("%H:%M"),
                "duration_minutes": duration,
                "original_duration": stage_info["duration_minutes"],
                "compressed": duration < stage_info["duration_minutes"],
                "compression_ratio": duration / stage_info["duration_minutes"],
                "description": stage_info["description"],
                "critical": stage_info.get("critical", False),
                "phase": stage_info.get("phase", "unknown"),
            }

            if "fixed_time" not in stage_info:
                current_time = stage_end

        return self._finalize_schedule(
            stage_schedule,
            start_time,
            end_time,
            total_minutes,
            "compressed",
            compression_ratio,
        )

    def _finalize_schedule(
        self,
        stage_schedule: Dict,
        start_time: datetime,
        end_time: datetime,
        total_minutes: int,
        schedule_type: str,
        compression_ratio: float = 1.0,
    ) -> Dict:
        """Finalize schedule with analysis and validation"""

        # Calculate final timings
        allocated_minutes = sum(
            stage["duration_minutes"] for stage in stage_schedule.values()
        )

        final_stage_end = max(
            datetime.strptime(stage["end_time"], "%H:%M").replace(
                year=start_time.year, month=start_time.month, day=start_time.day
            )
            for stage in stage_schedule.values()
        )

        buffer_minutes = int((end_time - final_stage_end).total_seconds() / 60)

        # Build analysis
        timing_analysis = {
            "total_window_minutes": total_minutes,
            "allocated_minutes": allocated_minutes,
            "buffer_minutes": buffer_minutes,
            "schedule_type": schedule_type,
            "first_race_time": end_time.strftime("%H:%M"),
            "pipeline_completion": final_stage_end.strftime("%H:%M"),
            "total_stages": len(stage_schedule),
            "phases_covered": len(
                set(stage.get("phase", "unknown") for stage in stage_schedule.values())
            ),
        }

        if compression_ratio < 1.0:
            timing_analysis["compression_ratio"] = compression_ratio
            timing_analysis["warnings"] = [
                f"Time pressure - {compression_ratio:.1%} compression applied",
                "Some stages may have reduced accuracy",
            ]

        allocation_summary = {
            "schedule": stage_schedule,
            "timing_analysis": timing_analysis,
        }

        logger.info(
            f"✅ {schedule_type.title()} 17-stage schedule: "
            f"{allocated_minutes}min allocated, {buffer_minutes}min buffer"
        )

        return allocation_summary

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

    # Demonstrate enhanced allocation logic
    print(f"\n🚀 Enhanced Allocation Logic Demo")
    print("=" * 50)

    enhanced_scenarios = [
        ("14:15", "Normal time pressure"),
        ("12:00", "High time pressure - minimum allocation"),
        ("10:30", "Extreme time pressure - some stages skipped"),
        ("18:00", "Low time pressure - optimum allocation"),
    ]

    for race_time_str, description in enhanced_scenarios:
        print(f"\n🎯 Enhanced Scenario: {description}")
        print("-" * 40)

        race_time = datetime.strptime(race_time_str, "%H:%M").time()
        simulated_race_datetime = datetime.combine(datetime.now().date(), race_time)

        # Use enhanced allocation
        enhanced_allocation = allocator.allocate_enhanced_schedule(
            download_time="06:01", first_race_time=simulated_race_datetime
        )

        # Print enhanced summary
        print(f"⏰ Time Window: 06:01 → {race_time_str}")
        print(
            f"📊 Time Pressure: {enhanced_allocation['timing_analysis']['time_pressure']:.2f}"
        )
        print(
            f"🎯 Modes Used: {', '.join(enhanced_allocation['timing_analysis']['timing_modes_used'])}"
        )
        print(
            f"⏭️ Skipped Stages: {enhanced_allocation['timing_analysis']['skipped_stages']}"
        )

        # Show a few example stages
        for stage_name, stage_info in list(enhanced_allocation["schedule"].items())[:3]:
            if stage_info.get("skipped", False):
                print(f"   ⏭️ {stage_name}: SKIPPED ({stage_info['reason']})")
            else:
                mode = stage_info.get("timing_mode", "STANDARD")
                print(
                    f"   ⏰ {stage_name}: {stage_info['duration_minutes']}min ({mode})"
                )


if __name__ == "__main__":
    main()
