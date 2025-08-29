#!/usr/bin/env python3
"""
Performance Timing Demo for Dynamic Pipeline
Demonstrates the performance logging capabilities implemented in dynamic_pipeline_timing.py
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path

# Setup performance logger
performance_logger = logging.getLogger("pipeline_performance")
performance_handler = logging.FileHandler("project_root / 'logs' / performance_timing_demo.log")
performance_formatter = logging.Formatter(
    "%(asctime)s - PERFORMANCE - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
performance_handler.setFormatter(performance_formatter)
performance_logger.addHandler(performance_handler)
performance_logger.setLevel(logging.INFO)

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)


class PerformanceTracker:
    """Simplified performance tracking demonstration"""

    def __init__(self):
        self.phase_timings = {}
        self.stage_timings = {}
        self.phase_start_times = {}
        self.stage_start_times = {}

    def start_phase_timing(self, phase_name: str) -> None:
        """Start timing a pipeline phase"""
        start_time = time.time()
        self.phase_start_times[phase_name] = start_time
        performance_logger.info(f"PHASE_START - {phase_name}")
        print(f"⏱️ Started timing phase: {phase_name}")

    def end_phase_timing(self, phase_name: str) -> float:
        """End timing a pipeline phase and log results"""
        end_time = time.time()
        if phase_name in self.phase_start_times:
            duration = end_time - self.phase_start_times[phase_name]
            self.phase_timings[phase_name] = duration
            performance_logger.info(f"PHASE_END - {phase_name} - {duration:.3f}s")
            print(f"⏱️ Phase {phase_name} completed in {duration:.3f}s")
            return duration
        else:
            print(f"⚠️ Phase {phase_name} timing not started")
            return 0.0

    def start_stage_timing(self, stage_name: str) -> None:
        """Start timing a pipeline stage"""
        start_time = time.time()
        self.stage_start_times[stage_name] = start_time
        performance_logger.info(f"STAGE_START - {stage_name}")
        print(f"⏱️ Started timing stage: {stage_name}")

    def end_stage_timing(self, stage_name: str) -> float:
        """End timing a pipeline stage and log results"""
        end_time = time.time()
        if stage_name in self.stage_start_times:
            duration = end_time - self.stage_start_times[stage_name]
            self.stage_timings[stage_name] = duration
            performance_logger.info(f"STAGE_END - {stage_name} - {duration:.3f}s")
            print(f"⏱️ Stage {stage_name} completed in {duration:.3f}s")
            return duration
        else:
            print(f"⚠️ Stage {stage_name} timing not started")
            return 0.0

    def generate_performance_report(self) -> dict:
        """Generate comprehensive performance report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "phase_performance": {},
            "stage_performance": {},
            "summary": {
                "total_phases": len(self.phase_timings),
                "total_stages": len(self.stage_timings),
                "total_phase_time": sum(self.phase_timings.values()),
                "total_stage_time": sum(self.stage_timings.values()),
                "average_phase_time": (
                    sum(self.phase_timings.values()) / max(1, len(self.phase_timings))
                ),
                "average_stage_time": (
                    sum(self.stage_timings.values()) / max(1, len(self.stage_timings))
                ),
                "fastest_phase": (
                    min(self.phase_timings.values()) if self.phase_timings else 0
                ),
                "slowest_phase": (
                    max(self.phase_timings.values()) if self.phase_timings else 0
                ),
                "fastest_stage": (
                    min(self.stage_timings.values()) if self.stage_timings else 0
                ),
                "slowest_stage": (
                    max(self.stage_timings.values()) if self.stage_timings else 0
                ),
            },
        }

        # Phase performance details
        for phase, duration in self.phase_timings.items():
            report["phase_performance"][phase] = {
                "duration": duration,
                "percentage_of_total": (
                    (duration / sum(self.phase_timings.values()) * 100)
                    if self.phase_timings
                    else 0
                ),
            }

        # Stage performance details
        for stage, duration in self.stage_timings.items():
            report["stage_performance"][stage] = {
                "duration": duration,
                "percentage_of_total": (
                    (duration / sum(self.stage_timings.values()) * 100)
                    if self.stage_timings
                    else 0
                ),
            }

        return report

    def save_performance_report(self, report: dict, filename: str = None) -> None:
        """Save performance report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"project_root / 'logs' / performance_report_{timestamp}.json"

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "w") as f:
            json.dump(report, f, indent=2, default=str)

        performance_logger.info(f"REPORT_SAVED - {filename}")
        print(f"💾 Performance report saved to {filename}")


def simulate_pipeline_execution():
    """Simulate a pipeline execution with performance tracking"""
    tracker = PerformanceTracker()

    print("🚀 Starting Performance Timing Demo")
    print("=" * 50)

    # Simulate Phase 1: Data Download
    tracker.start_phase_timing("data_download")

    # Simulate stages within the phase
    stages = ["validate_credentials", "fetch_data", "process_data"]
    for stage in stages:
        tracker.start_stage_timing(stage)
        # Simulate some work with random delays
        time.sleep(0.5 + (hash(stage) % 10) / 20)  # 0.5-1.0 seconds
        tracker.end_stage_timing(stage)

    tracker.end_phase_timing("data_download")

    # Simulate Phase 2: Analysis
    tracker.start_phase_timing("analysis")

    analysis_stages = ["form_analysis", "betting_odds", "predictions"]
    for stage in analysis_stages:
        tracker.start_stage_timing(stage)
        # Simulate varying work loads
        time.sleep(0.3 + (hash(stage) % 15) / 30)  # 0.3-0.8 seconds
        tracker.end_stage_timing(stage)

    tracker.end_phase_timing("analysis")

    # Simulate Phase 3: Output Generation
    tracker.start_phase_timing("output_generation")

    output_stages = ["generate_tips", "create_reports", "upload_results"]
    for stage in output_stages:
        tracker.start_stage_timing(stage)
        # Simulate final stage work
        time.sleep(0.2 + (hash(stage) % 8) / 40)  # 0.2-0.4 seconds
        tracker.end_stage_timing(stage)

    tracker.end_phase_timing("output_generation")

    print("\n" + "=" * 50)
    print("📊 Generating Performance Report")

    # Generate and save performance report
    report = tracker.generate_performance_report()
    tracker.save_performance_report(report)

    # Display summary
    print("\n📈 Performance Summary:")
    print(f"   Total Phases: {report['summary']['total_phases']}")
    print(f"   Total Stages: {report['summary']['total_stages']}")
    print(f"   Total Execution Time: {report['summary']['total_phase_time']:.3f}s")
    print(f"   Average Phase Time: {report['summary']['average_phase_time']:.3f}s")
    print(f"   Average Stage Time: {report['summary']['average_stage_time']:.3f}s")

    print("\n🔥 Performance Analysis:")
    print(f"   Fastest Phase: {report['summary']['fastest_phase']:.3f}s")
    print(f"   Slowest Phase: {report['summary']['slowest_phase']:.3f}s")
    print(f"   Fastest Stage: {report['summary']['fastest_stage']:.3f}s")
    print(f"   Slowest Stage: {report['summary']['slowest_stage']:.3f}s")

    print("\n🎯 Phase Breakdown:")
    for phase, details in report["phase_performance"].items():
        print(
            f"   {phase}: {details['duration']:.3f}s "
            f"({details['percentage_of_total']:.1f}%)"
        )

    print("\n⚡ Top 3 Slowest Stages:")
    sorted_stages = sorted(
        report["stage_performance"].items(),
        key=lambda x: x[1]["duration"],
        reverse=True,
    )[:3]
    for i, (stage, details) in enumerate(sorted_stages, 1):
        print(
            f"   {i}. {stage}: {details['duration']:.3f}s "
            f"({details['percentage_of_total']:.1f}%)"
        )

    return report


if __name__ == "__main__":
    try:
        report = simulate_pipeline_execution()
        print("\n✅ Performance timing demo completed successfully!")
        print(f"📁 Check project_root / 'logs' /  directory for detailed performance logs and reports")

    except Exception as e:
        print(f"❌ Error during performance demo: {e}")
        performance_logger.error(f"DEMO_ERROR - {str(e)}")
