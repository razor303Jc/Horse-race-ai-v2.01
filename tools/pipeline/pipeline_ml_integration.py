#!/usr/bin/env python3
"""
Pipeline ML Training Integration Script
Horse Racing AI v2.02

Integrates adaptive ML training into the existing pipeline system.
This script:
1. Reads current pipeline timing from dynamic_pipeline_timing
2. Integrates adaptive ML training configuration
3. Executes training within pipeline constraints
4. Updates pipeline status

Usage:
  python pipeline_ml_integration.py --pipeline-config /path/to/config.json
  python pipeline_ml_integration.py --auto  # Auto-detect current pipeline
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "docker" / "pipeline_management")
)

from tools.ml_training.adaptive_ml_integration import AdaptiveMLTrainingIntegration

# Try to import pipeline timing - handle gracefully if not available
try:
    from dynamic_pipeline_timing import PipelineTimeAllocator

    PIPELINE_TIMING_AVAILABLE = True
except ImportError:
    PIPELINE_TIMING_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Pipeline timing system not available - using fallback")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PipelineMLIntegration:
    """Integrates ML training with dynamic pipeline timing"""

    def __init__(self):
        if PIPELINE_TIMING_AVAILABLE:
            self.pipeline_allocator = PipelineTimeAllocator()
        else:
            self.pipeline_allocator = None
            logger.warning("Using fallback pipeline configuration")

        self.ml_integration = AdaptiveMLTrainingIntegration()

        # Integration tracking
        self.integration_history = []

        # Create directories
        Path("logs").mkdir(exist_ok=True)
        Path("results/pipeline_integration").mkdir(parents=True, exist_ok=True)

    def get_current_pipeline_schedule(self, first_race_time=None) -> dict:
        """Get current pipeline schedule from dynamic timing system"""
        try:
            if self.pipeline_allocator:
                # Convert first_race_time string to datetime if provided
                first_race_dt = None
                if first_race_time:
                    first_race_dt = datetime.combine(
                        datetime.now().date(),
                        datetime.strptime(first_race_time, "%H:%M").time(),
                    )

                # Calculate current schedule with 00:01 download time for manual data loading
                schedule = self.pipeline_allocator.allocate_stage_times(
                    download_time="00:01",  # Manual data loading starts at 00:01
                    first_race_time=first_race_dt,
                )

                logger.info(
                    f"📋 Pipeline schedule loaded: "
                    f"{schedule['timing_analysis']['schedule_type']} mode"
                )
                return schedule
            else:
                logger.warning("Pipeline allocator not available, using fallback")
                return self.create_fallback_schedule()

        except Exception as e:
            logger.error(f"❌ Error loading pipeline schedule: {e}")
            # Return minimal fallback schedule
            return self.create_fallback_schedule()

    def create_fallback_schedule(self) -> dict:
        """Create a fallback schedule when pipeline timing is unavailable"""
        return {
            "schedule": {
                "ml_model_training": {
                    "start_time": "16:00",
                    "end_time": "17:25",
                    "duration_minutes": 85,
                    "description": "ML model training",
                    "critical": True,
                }
            },
            "timing_analysis": {
                "total_window_minutes": 480,
                "allocated_minutes": 400,
                "buffer_minutes": 80,
                "schedule_type": "fallback",
            },
        }

    def execute_integrated_training(self, pipeline_schedule: dict = None) -> dict:
        """Execute ML training integrated with pipeline timing"""

        logger.info("🚀 Starting Pipeline-Integrated ML Training")
        start_time = datetime.now()

        try:
            # Get pipeline schedule if not provided
            if pipeline_schedule is None:
                pipeline_schedule = self.get_current_pipeline_schedule()

            # Integrate ML training configuration
            integrated_schedule = self.ml_integration.integrate_with_pipeline_timing(
                pipeline_schedule
            )

            # Extract training configuration
            ml_config = integrated_schedule["ml_training_integration"][
                "adaptive_config"
            ]

            # Log configuration
            logger.info(f"🎯 Training Strategy: {ml_config['strategy']}")
            logger.info(f"📊 Data Scale: {ml_config['scale_category']}")
            logger.info(
                f"⏰ Allocated Time: {ml_config['allocated_time_minutes']:.1f} minutes"
            )
            logger.info(f"🔄 Cycles: {ml_config['cycles_per_session']}")

            # Save integrated configuration
            config_file = self.ml_integration.save_integration_config(
                integrated_schedule
            )

            # Execute training with adaptive configuration
            training_result = self.ml_integration.execute_adaptive_training(ml_config)

            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds() / 60

            # Create execution summary
            execution_summary = {
                "execution_timestamp": start_time.isoformat(),
                "total_duration_minutes": total_duration,
                "pipeline_integration": {
                    "schedule_type": pipeline_schedule["timing_analysis"][
                        "schedule_type"
                    ],
                    "buffer_used": ml_config["allocated_time_minutes"],
                    "buffer_available": pipeline_schedule["timing_analysis"][
                        "buffer_minutes"
                    ],
                    "efficiency": training_result["fit_in_allocation"],
                },
                "training_performance": training_result,
                "config_file": config_file,
                "success": True,
            }

            # Add to history
            self.integration_history.append(execution_summary)

            # Save execution summary
            summary_file = f"results/pipeline_integration/execution_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, "w") as f:
                json.dump(execution_summary, f, indent=2, default=str)

            logger.info(
                f"✅ Training completed successfully in {total_duration:.1f} minutes"
            )
            logger.info(f"📄 Results saved: {summary_file}")

            return execution_summary

        except Exception as e:
            logger.error(f"❌ Integration execution failed: {e}")

            error_summary = {
                "execution_timestamp": start_time.isoformat(),
                "error": str(e),
                "success": False,
            }

            return error_summary

    def monitor_pipeline_integration(self, duration_hours: int = 1):
        """Monitor pipeline integration over time"""

        logger.info(
            f"👀 Starting pipeline integration monitoring for {duration_hours} hours"
        )

        import time
        from datetime import timedelta

        end_time = datetime.now() + timedelta(hours=duration_hours)
        check_interval = 300  # 5 minutes

        monitoring_results = []

        try:
            while datetime.now() < end_time:
                # Check current pipeline status
                pipeline_schedule = self.get_current_pipeline_schedule()

                # Assess if training should run now
                current_time = datetime.now().strftime("%H:%M")
                ml_stage = pipeline_schedule["schedule"].get("ml_model_training", {})
                ml_start = ml_stage.get("start_time", "16:00")
                ml_end = ml_stage.get("end_time", "17:25")

                # Check if we're in ML training window
                if ml_start <= current_time <= ml_end:
                    logger.info(
                        f"🕐 In ML training window ({ml_start}-{ml_end}), executing training..."
                    )
                    result = self.execute_integrated_training(pipeline_schedule)
                    monitoring_results.append(result)
                else:
                    logger.info(
                        f"⏸️ Outside ML training window (current: {current_time}, window: {ml_start}-{ml_end})"
                    )

                # Wait for next check
                time.sleep(check_interval)

        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")

        logger.info(
            f"📊 Monitoring completed: {len(monitoring_results)} training sessions executed"
        )
        return monitoring_results

    def generate_integration_report(self) -> dict:
        """Generate comprehensive integration performance report"""

        if not self.integration_history:
            return {"error": "No integration history available"}

        # Analyze performance trends
        successful_runs = [r for r in self.integration_history if r["success"]]

        if not successful_runs:
            return {"error": "No successful runs to analyze"}

        # Calculate statistics
        durations = [r["total_duration_minutes"] for r in successful_runs]
        buffer_usage = [
            r["pipeline_integration"]["buffer_used"] for r in successful_runs
        ]
        efficiencies = [
            r["training_performance"]["efficiency"] for r in successful_runs
        ]

        report = {
            "summary": {
                "total_runs": len(self.integration_history),
                "successful_runs": len(successful_runs),
                "success_rate": len(successful_runs)
                / len(self.integration_history)
                * 100,
                "avg_duration_minutes": sum(durations) / len(durations),
                "avg_buffer_usage": sum(buffer_usage) / len(buffer_usage),
                "avg_efficiency": sum(efficiencies) / len(efficiencies),
            },
            "trends": {
                "duration_trend": "stable" if len(set(durations)) < 3 else "variable",
                "efficiency_trend": (
                    "improving" if efficiencies[-1] > efficiencies[0] else "stable"
                ),
            },
            "recommendations": self._generate_integration_recommendations(
                successful_runs
            ),
        }

        return report

    def _generate_integration_recommendations(self, successful_runs: list) -> list:
        """Generate recommendations for pipeline integration optimization"""

        recommendations = []

        # Analyze buffer usage
        buffer_usages = [
            r["pipeline_integration"]["buffer_used"] for r in successful_runs
        ]
        avg_buffer_usage = sum(buffer_usages) / len(buffer_usages)

        if avg_buffer_usage < 15:
            recommendations.append(
                "🔧 Consider increasing training cycles - buffer underutilized"
            )
        elif avg_buffer_usage > 60:
            recommendations.append(
                "⚠️ High buffer usage - consider optimizing training time"
            )

        # Analyze efficiency
        efficiencies = [
            r["training_performance"]["efficiency"] for r in successful_runs
        ]
        avg_efficiency = sum(efficiencies) / len(efficiencies)

        if avg_efficiency < 0.6:
            recommendations.append(
                "📈 Consider longer training cycles to improve model performance"
            )

        # Check timing consistency
        durations = [r["total_duration_minutes"] for r in successful_runs]
        duration_variance = max(durations) - min(durations)

        if duration_variance > 10:
            recommendations.append(
                "⏰ High timing variance - review adaptive scaling parameters"
            )

        return recommendations


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Pipeline ML Training Integration")
    parser.add_argument(
        "--auto", action="store_true", help="Auto-detect and run with current pipeline"
    )
    parser.add_argument(
        "--monitor",
        type=int,
        metavar="HOURS",
        help="Monitor pipeline integration for specified hours",
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate integration performance report"
    )

    args = parser.parse_args()

    integration = PipelineMLIntegration()

    if args.monitor:
        integration.monitor_pipeline_integration(args.monitor)
    elif args.report:
        report = integration.generate_integration_report()
        print(json.dumps(report, indent=2))
    elif args.auto:
        result = integration.execute_integrated_training()
        if result["success"]:
            print(f"✅ Training completed successfully")
            print(f"⏰ Duration: {result['total_duration_minutes']:.1f} minutes")
            print(f"🎯 Strategy: {result['training_performance']['strategy']}")
        else:
            print(f"❌ Training failed: {result['error']}")
    else:
        # Interactive mode
        print("🏇 Pipeline ML Training Integration")
        print("=" * 40)
        result = integration.execute_integrated_training()

        if result["success"]:
            print(f"\n✅ Integration completed successfully!")
            print(f"Duration: {result['total_duration_minutes']:.1f} minutes")
            print(f"Strategy: {result['training_performance']['strategy']}")
            print(f"Cycles: {result['training_performance']['cycles_completed']}")
            print(f"Efficiency: {result['training_performance']['efficiency']:.3f}")
        else:
            print(f"\n❌ Integration failed: {result['error']}")


if __name__ == "__main__":
    main()
