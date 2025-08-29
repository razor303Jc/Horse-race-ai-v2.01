#!/usr/bin/env python3
"""
Integrated Performance Tracking with Allocation Comparison Demo
Demonstrates performance logging with allocated vs actual time comparison
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

# Setup performance logger
performance_logger = logging.getLogger("pipeline_performance")
performance_handler = logging.FileHandler("project_root / 'logs' / integrated_performance_demo.log")
performance_formatter = logging.Formatter(
    "%(asctime)s - PERFORMANCE - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
performance_handler.setFormatter(performance_formatter)
performance_logger.addHandler(performance_handler)
performance_logger.setLevel(logging.INFO)

# Setup main logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IntegratedPerformanceTracker:
    """Performance tracker with allocation vs actual time comparison"""

    def __init__(self):
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
        self.allocated_times = {}
        self.allocation_comparison = {}

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
        logger.info(f"📋 Allocated {allocated_minutes:.2f}min for {name}")

    def start_stage_timing(self, stage_name: str) -> None:
        """Start timing a pipeline stage"""
        start_time = time.time()
        self.stage_start_times[stage_name] = start_time
        performance_logger.info(f"STAGE_START - {stage_name}")
        logger.info(f"⏱️ Started timing stage: {stage_name}")

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

    def start_phase_timing(self, phase_name: str) -> None:
        """Start timing a pipeline phase"""
        start_time = time.time()
        self.phase_start_times[phase_name] = start_time
        performance_logger.info(f"PHASE_START - {phase_name}")
        logger.info(f"🚀 Started timing phase: {phase_name}")

    def end_phase_timing(self, phase_name: str) -> float:
        """End timing a pipeline phase and log results"""
        end_time = time.time()
        if phase_name in self.phase_start_times:
            duration = end_time - self.phase_start_times[phase_name]
            self.performance_metrics["phase_timings"][phase_name] = duration
            performance_logger.info(f"PHASE_END - {phase_name} - {duration:.3f}s")
            logger.info(f"🏁 Phase {phase_name} completed in {duration:.3f}s")

            # Compare with allocated time if available
            self._compare_allocated_vs_actual(phase_name, duration, "phase")

            return duration
        else:
            logger.warning(f"⚠️ Phase {phase_name} timing not started")
            return 0.0

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
        )

        # Determine status
        if abs(variance_percentage) <= 10:
            status = "ON_TARGET"
            status_emoji = "🎯"
        elif variance_percentage > 10:
            status = "OVER_ALLOCATED"
            status_emoji = "🔴"
        else:
            status = "UNDER_ALLOCATED"
            status_emoji = "🟢"

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

        # Console log with status
        logger.info(
            f"{status_emoji} {name}: Allocated {allocated_minutes:.2f}min, "
            f"Actual {actual_minutes:.2f}min "
            f"({variance_percentage:+.1f}%)"
        )

    def get_allocation_summary(self) -> dict:
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

    def generate_comprehensive_report(self) -> dict:
        """Generate comprehensive performance and allocation report"""
        allocation_summary = self.get_allocation_summary()

        report = {
            "timestamp": datetime.now().isoformat(),
            "performance_summary": {
                "total_phases": len(self.performance_metrics["phase_timings"]),
                "total_stages": len(self.performance_metrics["stage_timings"]),
                "total_phase_time": sum(
                    self.performance_metrics["phase_timings"].values()
                ),
                "total_stage_time": sum(
                    self.performance_metrics["stage_timings"].values()
                ),
            },
            "allocation_comparison": allocation_summary,
            "phase_details": self.performance_metrics["phase_timings"],
            "stage_details": self.performance_metrics["stage_timings"],
            "allocation_accuracy": {
                "accuracy_percentage": (
                    (
                        allocation_summary["on_target"]
                        / max(1, allocation_summary["total_comparisons"])
                    )
                    * 100
                ),
                "average_variance": allocation_summary.get("average_variance", 0),
                "total_time_efficiency": (
                    (
                        allocation_summary["total_allocated_time"]
                        / max(0.1, allocation_summary["total_actual_time"])
                        * 100
                    )
                    if allocation_summary.get("total_actual_time", 0) > 0
                    else 0
                ),
            },
        }

        return report

    def save_comprehensive_report(self, report: dict, filename: str = None) -> None:
        """Save comprehensive report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"project_root / 'logs' / integrated_performance_report_{timestamp}.json"

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "w") as f:
            json.dump(report, f, indent=2, default=str)

        performance_logger.info(f"COMPREHENSIVE_REPORT_SAVED - {filename}")
        logger.info(f"💾 Comprehensive report saved to {filename}")


def demonstrate_integrated_performance_tracking():
    """Demonstrate integrated performance tracking with allocation comparison"""
    tracker = IntegratedPerformanceTracker()

    print("🚀 Integrated Performance Tracking Demo")
    print("=" * 60)
    print("📋 This demo shows allocation vs actual time comparison")
    print("=" * 60)

    # Define a pipeline with allocated times
    pipeline_phases = [
        {
            "name": "data_acquisition",
            "allocated_minutes": 3.0,
            "stages": [
                {"name": "data_download", "allocated_minutes": 1.2},
                {"name": "data_validation", "allocated_minutes": 0.8},
                {"name": "data_preprocessing", "allocated_minutes": 1.0},
            ],
        },
        {
            "name": "analysis",
            "allocated_minutes": 4.0,
            "stages": [
                {"name": "feature_extraction", "allocated_minutes": 1.5},
                {"name": "model_training", "allocated_minutes": 2.0},
                {"name": "predictions", "allocated_minutes": 0.5},
            ],
        },
        {
            "name": "output_generation",
            "allocated_minutes": 2.0,
            "stages": [
                {"name": "report_generation", "allocated_minutes": 1.0},
                {"name": "file_upload", "allocated_minutes": 0.5},
                {"name": "notifications", "allocated_minutes": 0.5},
            ],
        },
    ]

    # Execute pipeline with allocation tracking
    for phase in pipeline_phases:
        phase_name = phase["name"]
        phase_allocated = phase["allocated_minutes"]

        # Set phase allocation
        tracker.set_allocated_time(phase_name, phase_allocated, "phase")

        # Start phase timing
        tracker.start_phase_timing(phase_name)

        # Execute stages within phase
        for stage in phase["stages"]:
            stage_name = stage["name"]
            stage_allocated = stage["allocated_minutes"]

            # Set stage allocation
            tracker.set_allocated_time(stage_name, stage_allocated, "stage")

            # Execute stage with realistic timing variations
            tracker.start_stage_timing(stage_name)

            # Simulate varying execution times (some over, some under allocation)
            base_time = stage_allocated * 60  # Convert to seconds
            variation_factor = 0.5 + (hash(stage_name) % 100) / 100  # 0.5 to 1.5
            actual_time = base_time * variation_factor

            time.sleep(min(actual_time, 2.0))  # Cap at 2 seconds for demo

            tracker.end_stage_timing(stage_name)

        # End phase timing
        tracker.end_phase_timing(phase_name)

    print("\n" + "=" * 60)
    print("📊 Generating Comprehensive Performance Report")
    print("=" * 60)

    # Generate and save comprehensive report
    report = tracker.generate_comprehensive_report()
    tracker.save_comprehensive_report(report)

    # Display allocation comparison summary
    allocation_summary = report["allocation_comparison"]
    print(f"\n📈 Allocation Accuracy Summary:")
    print(f"   Total Comparisons: {allocation_summary['total_comparisons']}")
    print(f"   On Target (±10%): {allocation_summary['on_target']}")
    print(f"   Over Allocated: {allocation_summary['over_allocated']}")
    print(f"   Under Allocated: {allocation_summary['under_allocated']}")
    print(f"   Average Variance: {allocation_summary['average_variance']:.1f}%")

    print(f"\n⏱️ Time Comparison:")
    print(f"   Total Allocated: {allocation_summary['total_allocated_time']:.2f}min")
    print(f"   Total Actual: {allocation_summary['total_actual_time']:.2f}min")
    print(f"   Total Variance: {allocation_summary['total_variance_percentage']:.1f}%")

    accuracy_data = report["allocation_accuracy"]
    print(f"\n🎯 Allocation Accuracy Metrics:")
    print(f"   Accuracy Rate: {accuracy_data['accuracy_percentage']:.1f}%")
    print(f"   Time Efficiency: {accuracy_data['total_time_efficiency']:.1f}%")

    print(f"\n📋 Detailed Stage Comparison:")
    for detail in allocation_summary["details"]:
        status_emoji = (
            "🎯"
            if detail["status"] == "ON_TARGET"
            else "🔴" if detail["status"] == "OVER_ALLOCATED" else "🟢"
        )
        print(
            f"   {status_emoji} {detail['name']}: "
            f"Allocated {detail['allocated']:.2f}min, "
            f"Actual {detail['actual']:.2f}min "
            f"({detail['variance_pct']:+.1f}%)"
        )

    return report


if __name__ == "__main__":
    try:
        report = demonstrate_integrated_performance_tracking()
        print("\n" + "=" * 60)
        print("✅ Integrated performance tracking demo completed successfully!")
        print("📁 Check project_root / 'logs' /  directory for detailed performance logs and reports")

    except Exception as e:
        print(f"❌ Error during integrated performance demo: {e}")
        performance_logger.error(f"DEMO_ERROR - {str(e)}")
