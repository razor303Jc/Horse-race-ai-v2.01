#!/usr/bin/env python3
"""
🎯 Live Pipeline Reports Launcher
================================

Launches automated reporting for the live horse racing AI pipeline.
Integrates with your 82% accuracy trained model and live betting system.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.monitoring.automated_pipeline_reports import PipelineStageReporter
from tools.monitoring.pipeline_reports_integration import PipelineReportsIntegration

logger = logging.getLogger(__name__)


class LivePipelineReports:
    """Live pipeline reporting for horse racing AI"""

    def __init__(self):
        """Initialize live pipeline reporting"""
        self.integration = PipelineReportsIntegration()
        self.current_run_id = None

        print("🏇 Live Pipeline Reports System")
        print("=" * 50)
        print(f"🎯 Monitoring 17-stage dynamic pipeline")
        print(f"🧠 Integrated with 82% accuracy ML model")
        print(f"💰 Connected to betting strategies system")
        print()

    def start_live_monitoring(self):
        """Start live monitoring for today's pipeline execution"""
        print("🚀 Starting live pipeline monitoring...")

        self.current_run_id = self.integration.start_daily_pipeline_monitoring()

        print(f"   ✅ Run ID: {self.current_run_id}")
        print(f"   📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Display expected stages
        print("📋 Pipeline Stages to Monitor:")
        stage_count = 0
        for stage_id, stage_def in self.integration.reporter.stage_definitions.items():
            stage_count += 1
            critical_icon = "🔴" if stage_def.get("critical", False) else "🟡"
            duration = stage_def.get("expected_duration", 0)
            print(
                f"   {stage_count:2d}. {critical_icon} {stage_def['name']} "
                f"({duration}m) - {stage_def.get('description', '')}"
            )

        print(f"\n   Total Stages: {stage_count}")
        print(
            f"   Expected Duration: {sum(s.get('expected_duration', 0) for s in self.integration.reporter.stage_definitions.values())} minutes"
        )
        print()

        return self.current_run_id

    def monitor_pipeline_stage(self, stage_id: str, **kwargs):
        """Monitor a specific pipeline stage with real-time feedback"""
        stage_def = self.integration.pipeline_stages.get(stage_id, {})
        stage_name = stage_def.get("description", stage_id.replace("_", " ").title())

        print(f"▶️  Starting: {stage_name}")

        # Start stage monitoring
        stage_metrics = self.integration.monitor_stage_execution(stage_id, **kwargs)

        return stage_metrics

    def complete_pipeline_stage(self, stage_id: str, **kwargs):
        """Complete monitoring for a pipeline stage"""
        completion_data = self.integration.complete_stage_monitoring(stage_id, **kwargs)

        stage_def = self.integration.pipeline_stages.get(stage_id, {})
        stage_name = stage_def.get("description", stage_id.replace("_", " ").title())

        success_icon = "✅" if kwargs.get("success", True) else "❌"
        duration = completion_data.get("duration_seconds", 0)
        records = kwargs.get("records_processed", 0)
        quality = kwargs.get("data_quality_score", 100.0)

        print(f"{success_icon} Completed: {stage_name}")
        print(
            f"   📊 Duration: {duration:.2f}s | Records: {records} | Quality: {quality:.1f}%"
        )

        if not kwargs.get("success", True):
            errors = kwargs.get("error_count", 0)
            print(f"   ⚠️  Errors: {errors}")

        print()
        return completion_data

    def generate_live_status_report(self):
        """Generate a live status report"""
        print("📊 LIVE PIPELINE STATUS")
        print("-" * 30)

        status = self.integration.generate_real_time_status()

        print(f"🔄 Run ID: {status.get('run_id', 'No active run')}")
        print(f"📅 Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"🎯 Pipeline: {status.get('pipeline_type', 'Unknown')}")
        print(f"📋 Total Stages: {status.get('total_stages', 0)}")

        metadata = status.get("metadata", {})
        if metadata:
            print(f"⏰ Download Time: {metadata.get('download_time', 'Unknown')}")
            print(f"🏁 First Race: {metadata.get('first_race_time', 'Unknown')}")
            print(f"� Total Races: {metadata.get('total_races', 0)}")

        print()

    def complete_live_monitoring(self):
        """Complete live monitoring and generate all reports"""
        print("🏁 Completing live pipeline monitoring...")

        completed_run = self.integration.complete_daily_pipeline()

        if completed_run:
            print(f"   ✅ Pipeline run completed: {completed_run}")

            # Generate performance summary
            summary = self.integration.get_pipeline_performance_summary(days=1)

            print("\n📈 PERFORMANCE SUMMARY")
            print("-" * 25)
            print(f"   🎯 Success Rate: {summary['avg_success_rate']:.1f}%")
            print(f"   ⏱️  Avg Duration: {summary['avg_duration']:.1f}s per stage")
            print(f"   ⚡ Avg Throughput: {summary['avg_throughput']:.1f} records/sec")
            print(f"   📊 Avg Quality: {summary['avg_quality']:.1f}%")

            if summary["bottlenecks"]:
                print(f"   ⚠️  Bottlenecks: {len(summary['bottlenecks'])} stages")
                for bottleneck in summary["bottlenecks"][:3]:  # Show top 3
                    print(
                        f"      • {bottleneck['stage_name']}: {bottleneck['performance_ratio']:.1f}x slower"
                    )

            if summary["recommendations"]:
                print(f"   💡 Recommendations:")
                for rec in summary["recommendations"]:
                    print(f"      • {rec}")

            print(f"\n📊 Reports Generated:")
            print(
                f"   • HTML Report: monitoring/reports/pipeline_report_{completed_run}.html"
            )
            print(
                f"   • CSV Export: monitoring/exports/pipeline_data_{completed_run}.csv"
            )
            print(
                f"   • Summary Dashboard: monitoring/reports/summary_dashboard_1d.html"
            )

        else:
            print("   ⚠️  No active pipeline run to complete")

        print()
        return completed_run

    def create_stage_context_manager(self, stage_id: str):
        """Create a context manager for automatic stage monitoring"""

        class LiveStageMonitor:
            def __init__(self, live_reports, stage_id):
                self.live_reports = live_reports
                self.stage_id = stage_id
                self.start_time = None
                self.metrics = {}

            def __enter__(self):
                self.start_time = datetime.now()
                self.live_reports.monitor_pipeline_stage(self.stage_id)
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                success = exc_type is None

                # Calculate duration
                duration = (
                    (datetime.now() - self.start_time).total_seconds()
                    if self.start_time
                    else 0
                )

                # Prepare completion data
                completion_data = {
                    "success": success,
                    "duration_seconds": duration,
                    "error_count": 1 if exc_type else 0,
                    "notes": str(exc_val) if exc_val else "",
                    **self.metrics,  # Include any metrics set during execution
                }

                self.live_reports.complete_pipeline_stage(
                    self.stage_id, **completion_data
                )

                return False  # Don't suppress exceptions

            def update_metrics(self, **kwargs):
                """Update metrics during stage execution"""
                self.metrics.update(kwargs)

            def log_progress(self, message: str):
                """Log progress during stage execution"""
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"   [{timestamp}] {message}")

        return LiveStageMonitor(self, stage_id)

    def run_demo_pipeline(self):
        """Run a demonstration of the live pipeline monitoring"""
        print("🎮 Running Demo Pipeline with Live Monitoring")
        print("=" * 50)

        # Start monitoring
        run_id = self.start_live_monitoring()

        # Simulate pipeline stages
        demo_stages = [
            ("data_download", "📥 Downloading today's racing data", 1200, 1200, 98.5),
            ("data_validation", "✅ Validating data integrity", 1200, 1180, 97.2),
            ("feature_engineering", "🔧 Engineering ML features", 1180, 1150, 96.8),
            ("ml_model_training", "🧠 Training models (82% accuracy)", 1150, 800, 94.2),
            ("betting_strategies", "💰 Generating betting strategies", 800, 50, 95.0),
            ("ai_selections", "🎯 Final AI selections", 50, 20, 96.5),
        ]

        print("🔄 Executing Pipeline Stages:")
        print()

        for stage_id, description, records_in, records_out, quality in demo_stages:
            with self.create_stage_context_manager(stage_id) as monitor:
                monitor.log_progress(description)

                # Simulate processing time
                import time

                time.sleep(0.3)

                # Update metrics
                monitor.update_metrics(
                    records_processed=records_in,
                    records_output=records_out,
                    data_quality_score=quality,
                    memory_usage_mb=150.0,
                    cpu_usage_percent=65.0,
                )

                monitor.log_progress(f"Processed {records_in} → {records_out} records")

        # Generate live status
        self.generate_live_status_report()

        # Complete monitoring
        completed_run = self.complete_live_monitoring()

        print("✅ Demo pipeline completed successfully!")
        print(f"🔗 Open: monitoring/reports/pipeline_report_{completed_run}.html")
        print()

        return completed_run


def main():
    """Main function to run live pipeline reports"""

    # Initialize live reporting
    live_reports = LivePipelineReports()

    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "demo":
            # Run demo pipeline
            live_reports.run_demo_pipeline()

        elif command == "start":
            # Start live monitoring
            live_reports.start_live_monitoring()
            print("🔄 Live monitoring started. Use your pipeline scripts and call:")
            print("   • live_reports.monitor_pipeline_stage(stage_id)")
            print("   • live_reports.complete_pipeline_stage(stage_id, **metrics)")
            print("   • live_reports.complete_live_monitoring()")

        elif command == "status":
            # Show current status
            live_reports.generate_live_status_report()

        else:
            print(f"❌ Unknown command: {command}")
            print("Usage: python live_pipeline_reports.py [demo|start|status]")

    else:
        # Default: run demo
        live_reports.run_demo_pipeline()


if __name__ == "__main__":
    main()
