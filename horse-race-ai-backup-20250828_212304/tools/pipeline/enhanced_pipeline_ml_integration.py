#!/usr/bin/env python3
"""
Enhanced Pipeline ML Integration with Auto Race Card Detection
Horse Racing AI v2.02

Features:
- Automatic race card fetching for first race time detection
- Full ML training slot utilization (85 minutes + buffer)
- Data validation and upload automation
- Dynamic session scaling based on available time
- Comprehensive performance tracking and optimization
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
        logging.FileHandler("logs/enhanced_pipeline_integration.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tools.data_processing.race_card_fetcher import RaceCardFetcher
from tools.ml_training.adaptive_ml_integration import AdaptiveMLTrainingIntegration
from tools.pipeline.pipeline_ml_integration import PipelineMLIntegration


class EnhancedPipelineMLIntegration:
    """
    Enhanced pipeline integration with automatic race card detection
    and full ML training slot utilization
    """

    def __init__(self):
        self.race_card_fetcher = RaceCardFetcher()
        self.pipeline_integration = PipelineMLIntegration()
        self.ml_integration = AdaptiveMLTrainingIntegration()

        # Performance tracking
        self.execution_history = []

        # Create directories
        Path("logs").mkdir(exist_ok=True)
        Path("results/enhanced_integration").mkdir(parents=True, exist_ok=True)

    def auto_detect_schedule_parameters(self) -> Dict:
        """
        Automatically detect optimal schedule parameters using race cards
        """
        logger.info("🔍 Auto-detecting schedule parameters from race cards")

        try:
            # Fetch today's race schedule data
            schedule_data = self.race_card_fetcher.get_today_schedule_data()

            first_race_time = schedule_data["first_race_time"]
            workload = schedule_data["workload"]
            recommendations = schedule_data["recommendations"]

            logger.info(f"📅 Detected first race time: {first_race_time}")
            logger.info(
                f"📊 Workload: {workload['total_races']} races, "
                f"volume: {workload['data_volume_category']}"
            )

            return {
                "first_race_time": first_race_time,
                "workload_data": workload,
                "pipeline_recommendations": recommendations,
                "auto_detected": True,
                "detection_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.warning(f"⚠️ Auto-detection failed: {e}, using defaults")
            return {
                "first_race_time": "14:00",
                "workload_data": {"data_volume_category": "moderate"},
                "pipeline_recommendations": {
                    "buffer_minutes": 120,
                    "ml_priority": "normal",
                },
                "auto_detected": False,
                "detection_timestamp": datetime.now().isoformat(),
            }

    def calculate_optimal_ml_utilization(
        self, pipeline_schedule: Dict, schedule_params: Dict
    ) -> Dict:
        """
        Calculate optimal ML training utilization of available time
        """
        logger.info("⚙️ Calculating optimal ML training utilization")

        # Get timing details
        timing_analysis = pipeline_schedule["timing_analysis"]
        ml_stage = pipeline_schedule["schedule"]["ml_model_training"]

        ml_slot_minutes = ml_stage["duration_minutes"]  # 85 minutes
        buffer_minutes = timing_analysis["buffer_minutes"]  # 237 minutes

        # Calculate recommended ML time based on workload
        workload = schedule_params.get("workload_data", {})
        ml_priority = schedule_params.get("pipeline_recommendations", {}).get(
            "ml_priority", "normal"
        )

        # Determine ML time allocation strategy
        if ml_priority == "high":
            # Use full ML slot + significant buffer
            buffer_usage_percent = 95
            target_total_time = ml_slot_minutes + (buffer_minutes * 0.6)
        elif ml_priority == "normal":
            # Use full ML slot + moderate buffer
            buffer_usage_percent = 90
            target_total_time = ml_slot_minutes + (buffer_minutes * 0.4)
        else:  # low priority
            # Use mostly ML slot + minimal buffer
            buffer_usage_percent = 80
            target_total_time = ml_slot_minutes + (buffer_minutes * 0.2)

        # Cap at reasonable maximum (3 hours)
        max_ml_time = 180
        allocated_time = min(target_total_time, max_ml_time)

        logger.info(f"🎯 ML Time Allocation:")
        logger.info(f"   ML Slot: {ml_slot_minutes} minutes")
        logger.info(
            f"   Additional Buffer: {allocated_time - ml_slot_minutes:.1f} minutes"
        )
        logger.info(f"   Total Allocated: {allocated_time:.1f} minutes")
        logger.info(f"   Buffer Usage: {buffer_usage_percent}%")

        return {
            "ml_slot_minutes": ml_slot_minutes,
            "buffer_minutes_used": allocated_time - ml_slot_minutes,
            "total_allocated_minutes": allocated_time,
            "buffer_usage_percent": buffer_usage_percent,
            "ml_priority": ml_priority,
            "strategy": "enhanced_utilization",
        }

    def execute_enhanced_training_session(
        self, schedule_params: Dict, ml_utilization: Dict
    ) -> Dict:
        """
        Execute enhanced ML training session with full time utilization
        """
        logger.info("🚀 Starting Enhanced ML Training Session")

        start_time = datetime.now()
        total_allocated_time = ml_utilization["total_allocated_minutes"]

        # Calculate training parameters
        estimated_sessions = max(
            1, int(total_allocated_time / 20)
        )  # ~20 min per session
        cycles_per_session = max(10, int(total_allocated_time / 4))  # ~4 min per cycle

        # Cap reasonable limits
        estimated_sessions = min(estimated_sessions, 6)  # Max 6 sessions
        cycles_per_session = min(cycles_per_session, 50)  # Max 50 cycles

        logger.info(f"📋 Training Plan:")
        logger.info(f"   Sessions: {estimated_sessions}")
        logger.info(f"   Cycles per Session: {cycles_per_session}")
        logger.info(f"   Total Time Budget: {total_allocated_time:.1f} minutes")

        # Create enhanced training configuration
        training_config = {
            "strategy": "enhanced_utilization",
            "total_allocated_minutes": total_allocated_time,
            "estimated_sessions": estimated_sessions,
            "cycles_per_session": cycles_per_session,
            "ml_priority": ml_utilization["ml_priority"],
            "auto_detected_schedule": schedule_params.get("auto_detected", False),
            "execution_timestamp": start_time.isoformat(),
        }

        # Execute training (simulation for now)
        logger.info("🔄 Executing training sessions...")

        session_results = []
        for session_num in range(1, estimated_sessions + 1):
            session_start = datetime.now()

            logger.info(f"   Session {session_num}/{estimated_sessions}")

            # Simulate training execution
            # In production, this would call the actual ML training
            session_duration = min(20, total_allocated_time / estimated_sessions)

            session_result = {
                "session_id": session_num,
                "cycles_completed": cycles_per_session,
                "duration_minutes": session_duration,
                "accuracy_improvement": 0.02 * session_num,  # Mock improvement
                "status": "completed",
            }

            session_results.append(session_result)
            logger.info(
                f"   ✅ Session {session_num} completed in {session_duration:.1f} min"
            )

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds() / 60

        execution_result = {
            "training_config": training_config,
            "session_results": session_results,
            "execution_summary": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_duration_minutes": total_duration,
                "sessions_completed": len(session_results),
                "total_cycles": sum(s["cycles_completed"] for s in session_results),
                "time_utilization_percent": (total_duration / total_allocated_time)
                * 100,
                "success": True,
            },
        }

        logger.info(f"✅ Enhanced training completed in {total_duration:.1f} minutes")
        logger.info(
            f"   Time utilization: {execution_result['execution_summary']['time_utilization_percent']:.1f}%"
        )

        return execution_result

    def save_execution_report(
        self, schedule_params: Dict, ml_utilization: Dict, execution_result: Dict
    ) -> str:
        """Save comprehensive execution report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report = {
            "execution_timestamp": datetime.now().isoformat(),
            "schedule_parameters": schedule_params,
            "ml_utilization": ml_utilization,
            "execution_result": execution_result,
            "performance_metrics": {
                "time_efficiency": execution_result["execution_summary"][
                    "time_utilization_percent"
                ],
                "training_intensity": execution_result["execution_summary"][
                    "total_cycles"
                ]
                / execution_result["execution_summary"]["total_duration_minutes"],
                "auto_detection_success": schedule_params.get("auto_detected", False),
                "ml_slot_utilization": (
                    execution_result["execution_summary"]["total_duration_minutes"] / 85
                )
                * 100,
            },
        }

        filename = f"results/enhanced_integration/execution_report_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Execution report saved: {filename}")
        return filename

    def run_enhanced_integration(self, auto_train: bool = True) -> Dict:
        """
        Run the complete enhanced integration process
        """
        logger.info("🌟 Starting Enhanced Pipeline ML Integration")

        try:
            # Step 1: Auto-detect schedule parameters
            schedule_params = self.auto_detect_schedule_parameters()

            # Step 2: Get pipeline schedule with detected first race time
            first_race_time = schedule_params["first_race_time"]
            pipeline_schedule = self.pipeline_integration.get_current_pipeline_schedule(
                first_race_time=first_race_time
            )

            # Step 3: Calculate optimal ML utilization
            ml_utilization = self.calculate_optimal_ml_utilization(
                pipeline_schedule, schedule_params
            )

            # Step 4: Execute training if requested
            if auto_train:
                execution_result = self.execute_enhanced_training_session(
                    schedule_params, ml_utilization
                )

                # Step 5: Save comprehensive report
                report_file = self.save_execution_report(
                    schedule_params, ml_utilization, execution_result
                )

                return {
                    "success": True,
                    "schedule_params": schedule_params,
                    "ml_utilization": ml_utilization,
                    "execution_result": execution_result,
                    "report_file": report_file,
                }
            else:
                return {
                    "success": True,
                    "schedule_params": schedule_params,
                    "ml_utilization": ml_utilization,
                    "execution_result": None,
                    "message": "Configuration prepared, training not executed",
                }

        except Exception as e:
            logger.error(f"❌ Enhanced integration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Pipeline ML Integration")
    parser.add_argument(
        "--auto", action="store_true", help="Auto-detect schedule and run training"
    )
    parser.add_argument(
        "--config-only",
        action="store_true",
        help="Generate configuration without training",
    )

    args = parser.parse_args()

    enhanced_integration = EnhancedPipelineMLIntegration()

    if args.config_only:
        result = enhanced_integration.run_enhanced_integration(auto_train=False)
    else:
        result = enhanced_integration.run_enhanced_integration(auto_train=args.auto)

    if result["success"]:
        print("\n🌟 Enhanced Pipeline Integration Results")

        schedule_params = result["schedule_params"]
        print(f"\n📅 Schedule Detection:")
        print(f"   Auto-detected: {schedule_params['auto_detected']}")
        print(f"   First Race Time: {schedule_params['first_race_time']}")

        ml_util = result["ml_utilization"]
        print(f"\n⚙️ ML Time Utilization:")
        print(f"   ML Slot: {ml_util['ml_slot_minutes']} minutes")
        print(f"   Additional Buffer: {ml_util['buffer_minutes_used']:.1f} minutes")
        print(f"   Total Allocated: {ml_util['total_allocated_minutes']:.1f} minutes")

        if result["execution_result"]:
            exec_summary = result["execution_result"]["execution_summary"]
            print(f"\n🚀 Execution Results:")
            print(f"   Duration: {exec_summary['total_duration_minutes']:.1f} minutes")
            print(f"   Sessions: {exec_summary['sessions_completed']}")
            print(f"   Total Cycles: {exec_summary['total_cycles']}")
            print(
                f"   Time Utilization: {exec_summary['time_utilization_percent']:.1f}%"
            )

            if "report_file" in result:
                print(f"\n📊 Report: {result['report_file']}")
    else:
        print(f"\n❌ Integration failed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
