#!/usr/bin/env python3
"""
🔗 Pipeline Reports Integration System
====================================

Integrates automated reporting with the existing 17-stage dynamic pipeline.
Provides real-time monitoring and comprehensive reporting for all stages.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.monitoring.automated_pipeline_reports import PipelineStageReporter

logger = logging.getLogger(__name__)


class PipelineReportsIntegration:
    """Integration layer for pipeline reporting"""

    def __init__(self, config_path: str = "config/master_schedule.json"):
        """Initialize the integration system"""
        self.config_path = Path(config_path)
        self.reporter = PipelineStageReporter()
        self.current_run_id = None
        self.load_pipeline_config()

        logger.info("🔗 Pipeline Reports Integration initialized")

    def load_pipeline_config(self):
        """Load pipeline configuration from master schedule"""
        try:
            with open(self.config_path, "r") as f:
                self.config = json.load(f)

            self.pipeline_stages = self.config.get("pipeline_stages", {})
            self.metadata = self.config.get("metadata", {})

            logger.info(f"📋 Loaded config with {len(self.pipeline_stages)} stages")

        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            self.config = {}
            self.pipeline_stages = {}
            self.metadata = {}

    def start_daily_pipeline_monitoring(self) -> str:
        """Start monitoring for daily pipeline execution"""
        self.current_run_id = self.reporter.start_pipeline_run()

        # Log pipeline metadata
        download_time = self.metadata.get("download_time", "unknown")
        first_race_time = self.metadata.get("first_race_time", "unknown")
        total_races = self.metadata.get("total_races", 0)

        logger.info(f"🏁 Daily pipeline monitoring started")
        logger.info(f"   Run ID: {self.current_run_id}")
        logger.info(f"   Download Time: {download_time}")
        logger.info(f"   First Race: {first_race_time}")
        logger.info(f"   Total Races: {total_races}")

        return self.current_run_id

    def monitor_stage_execution(self, stage_id: str, **kwargs):
        """Monitor a specific stage execution"""
        if not self.current_run_id:
            self.start_daily_pipeline_monitoring()

        # Get stage configuration
        stage_config = self.pipeline_stages.get(stage_id, {})

        # Start stage monitoring
        stage_metrics = self.reporter.start_stage(stage_id=stage_id, **kwargs)

        logger.info(f"▶️  Monitoring stage: {stage_config.get('description', stage_id)}")

        return stage_metrics

    def complete_stage_monitoring(self, stage_id: str, **kwargs):
        """Complete monitoring for a specific stage"""
        completion_data = self.reporter.complete_stage(stage_id, **kwargs)

        stage_config = self.pipeline_stages.get(stage_id, {})
        expected_duration = stage_config.get("duration_minutes", 0) * 60
        actual_duration = completion_data.get("duration_seconds", 0)

        # Performance analysis
        if expected_duration > 0:
            performance_ratio = actual_duration / expected_duration
            if performance_ratio > 1.5:
                logger.warning(
                    f"⚠️  Stage {stage_id} took {performance_ratio:.1f}x expected time"
                )
            elif performance_ratio < 0.5:
                logger.info(
                    f"⚡ Stage {stage_id} completed {1/performance_ratio:.1f}x faster than expected"
                )

        return completion_data

    def generate_real_time_status(self) -> Dict[str, Any]:
        """Generate real-time pipeline status"""
        if not self.current_run_id:
            return {"status": "No active pipeline run"}

        # Get current pipeline status
        status = (
            self.reporter.metrics_collector.get_current_status()
            if hasattr(self.reporter, "metrics_collector")
            else {}
        )

        # Add pipeline-specific information
        status.update(
            {
                "run_id": self.current_run_id,
                "pipeline_type": "17-stage dynamic pipeline",
                "total_stages": len(self.pipeline_stages),
                "metadata": self.metadata,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return status

    def complete_daily_pipeline(self):
        """Complete daily pipeline monitoring"""
        if not self.current_run_id:
            logger.warning("No active pipeline run to complete")
            return

        self.reporter.complete_pipeline_run()

        # Generate additional reports
        self.generate_comprehensive_reports()

        logger.info(f"🏁 Daily pipeline monitoring completed: {self.current_run_id}")

        completed_run_id = self.current_run_id
        self.current_run_id = None

        return completed_run_id

    def generate_comprehensive_reports(self):
        """Generate all types of comprehensive reports"""
        if not self.current_run_id:
            logger.error("No active run to generate reports for")
            return

        reports_generated = []

        try:
            # Main pipeline report
            html_report = self.reporter.generate_pipeline_report(self.current_run_id)
            if html_report:
                reports_generated.append(("HTML Report", html_report))

            # CSV export for analysis
            csv_export = self.reporter.export_to_csv(self.current_run_id)
            if csv_export:
                reports_generated.append(("CSV Export", csv_export))

            # Stage statistics
            stats = self.reporter.get_stage_statistics(days=1)
            if stats:
                stats_path = (
                    f"monitoring/exports/stage_stats_{self.current_run_id}.json"
                )
                Path(stats_path).parent.mkdir(parents=True, exist_ok=True)

                with open(stats_path, "w") as f:
                    json.dump(stats, f, indent=2)
                reports_generated.append(("Stage Statistics", stats_path))

            # Summary dashboard
            summary_dashboard = self.reporter.generate_summary_dashboard(days=7)
            if summary_dashboard:
                reports_generated.append(("Summary Dashboard", summary_dashboard))

            logger.info(f"📊 Generated {len(reports_generated)} reports:")
            for report_type, report_path in reports_generated:
                logger.info(f"   • {report_type}: {report_path}")

        except Exception as e:
            logger.error(f"Error generating reports: {e}")

    def create_stage_wrapper(self, stage_id: str):
        """Create a context manager wrapper for stage monitoring"""

        class StageMonitor:
            def __init__(self, integration, stage_id):
                self.integration = integration
                self.stage_id = stage_id
                self.stage_metrics = None

            def __enter__(self):
                self.stage_metrics = self.integration.monitor_stage_execution(
                    self.stage_id
                )
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                success = exc_type is None
                completion_data = {
                    "success": success,
                    "error_count": 1 if exc_type else 0,
                    "notes": str(exc_val) if exc_val else "",
                }
                self.integration.complete_stage_monitoring(
                    self.stage_id, **completion_data
                )

            def update_metrics(self, **kwargs):
                """Update stage metrics during execution"""
                # Store metrics for completion
                for key, value in kwargs.items():
                    setattr(self, key, value)

            def complete(self, **kwargs):
                """Manually complete the stage with specific metrics"""
                self.integration.complete_stage_monitoring(self.stage_id, **kwargs)

        return StageMonitor(self, stage_id)

    def get_pipeline_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get pipeline performance summary over time"""
        stage_stats = self.reporter.get_stage_statistics(days)

        summary = {
            "period_days": days,
            "total_stages_monitored": len(stage_stats),
            "avg_success_rate": 0,
            "avg_duration": 0,
            "avg_throughput": 0,
            "avg_quality": 0,
            "performance_trends": {},
            "bottlenecks": [],
            "recommendations": [],
        }

        if stage_stats:
            # Calculate averages
            success_rates = [s["success_rate"] for s in stage_stats.values()]
            durations = [s["avg_duration"] for s in stage_stats.values()]
            throughputs = [
                s["avg_throughput"]
                for s in stage_stats.values()
                if s["avg_throughput"] > 0
            ]
            qualities = [s["avg_quality"] for s in stage_stats.values()]

            summary.update(
                {
                    "avg_success_rate": sum(success_rates) / len(success_rates),
                    "avg_duration": sum(durations) / len(durations),
                    "avg_throughput": (
                        sum(throughputs) / len(throughputs) if throughputs else 0
                    ),
                    "avg_quality": sum(qualities) / len(qualities),
                }
            )

            # Identify bottlenecks (stages taking longer than expected)
            for stage_id, stats in stage_stats.items():
                stage_config = self.pipeline_stages.get(stage_id, {})
                expected_duration = stage_config.get("duration_minutes", 0) * 60

                if (
                    expected_duration > 0
                    and stats["avg_duration"] > expected_duration * 1.5
                ):
                    summary["bottlenecks"].append(
                        {
                            "stage_id": stage_id,
                            "stage_name": stats["stage_name"],
                            "expected_duration": expected_duration,
                            "actual_duration": stats["avg_duration"],
                            "performance_ratio": stats["avg_duration"]
                            / expected_duration,
                        }
                    )

            # Generate recommendations
            if summary["avg_success_rate"] < 95:
                summary["recommendations"].append(
                    "Consider investigating stages with low success rates"
                )

            if summary["bottlenecks"]:
                summary["recommendations"].append(
                    f"Optimize {len(summary['bottlenecks'])} bottleneck stages"
                )

            if summary["avg_quality"] < 95:
                summary["recommendations"].append(
                    "Review data quality issues in preprocessing stages"
                )

        return summary


def create_pipeline_monitoring_decorator(integration: PipelineReportsIntegration):
    """Create a decorator for automatic stage monitoring"""

    def monitor_stage(stage_id: str):
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Start monitoring
                stage_monitor = integration.create_stage_wrapper(stage_id)

                with stage_monitor:
                    try:
                        # Execute the original function
                        result = func(*args, **kwargs)

                        # Extract metrics from result if it's a dict
                        if isinstance(result, dict) and "metrics" in result:
                            stage_monitor.update_metrics(**result["metrics"])

                        return result

                    except Exception as e:
                        logger.error(f"Error in stage {stage_id}: {e}")
                        raise

            return wrapper

        return decorator

    return monitor_stage


def demonstrate_integration():
    """Demonstrate the pipeline reports integration"""
    print("🔗 PIPELINE REPORTS INTEGRATION DEMO")
    print("=" * 50)

    # Initialize integration
    integration = PipelineReportsIntegration()

    # Start daily pipeline monitoring
    run_id = integration.start_daily_pipeline_monitoring()
    print(f"🚀 Started daily pipeline monitoring: {run_id}")

    # Create monitoring decorator
    monitor_stage = create_pipeline_monitoring_decorator(integration)

    # Demo: Simulate some pipeline stages with the decorator
    @monitor_stage("data_download")
    def simulate_data_download():
        print("   📥 Downloading racing data...")
        import time

        time.sleep(0.5)
        return {
            "metrics": {
                "records_processed": 1200,
                "records_output": 1200,
                "data_quality_score": 98.5,
                "success": True,
            }
        }

    @monitor_stage("feature_engineering")
    def simulate_feature_engineering():
        print("   🔧 Engineering features...")
        import time

        time.sleep(0.3)
        return {
            "metrics": {
                "records_processed": 1200,
                "records_output": 1150,
                "data_quality_score": 96.8,
                "success": True,
            }
        }

    @monitor_stage("ml_model_training")
    def simulate_ml_training():
        print("   🧠 Training ML models...")
        import time

        time.sleep(0.4)
        return {
            "metrics": {
                "records_processed": 1150,
                "records_output": 800,
                "data_quality_score": 94.2,
                "success": True,
            }
        }

    # Execute stages
    print("\n📊 Executing pipeline stages...")
    simulate_data_download()
    simulate_feature_engineering()
    simulate_ml_training()

    # Get real-time status
    print("\n📈 Real-time status:")
    status = integration.generate_real_time_status()
    print(f"   Run ID: {status.get('run_id')}")
    print(f"   Pipeline Type: {status.get('pipeline_type')}")
    print(f"   Total Stages: {status.get('total_stages')}")

    # Complete pipeline
    print("\n🏁 Completing pipeline monitoring...")
    completed_run = integration.complete_daily_pipeline()

    # Get performance summary
    print("\n📊 Performance summary:")
    summary = integration.get_pipeline_performance_summary(days=1)
    print(f"   Stages Monitored: {summary['total_stages_monitored']}")
    print(f"   Avg Success Rate: {summary['avg_success_rate']:.1f}%")
    print(f"   Avg Duration: {summary['avg_duration']:.1f}s")
    print(f"   Bottlenecks: {len(summary['bottlenecks'])}")

    if summary["recommendations"]:
        print("   Recommendations:")
        for rec in summary["recommendations"]:
            print(f"     • {rec}")

    print(
        f"\n✅ Integration demo completed! Check monitoring/reports/ for generated reports."
    )

    return integration


if __name__ == "__main__":
    demonstrate_integration()
