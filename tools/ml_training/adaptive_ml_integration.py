#!/usr/bin/env python3
"""
Adaptive ML Training Pipeline Integration
Horse Racing AI v2.02

Integrates ML training cycles into the dynamic pipeline system with:
- Data growth adaptation (larger datasets = longer training)
- Buffer time management
- Cycle/session adjustment based on available time
- Pipeline timing integration
- Resource scaling

This module plugs into the existing dynamic_pipeline_timing.py system.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psycopg2

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/adaptive_ml_training.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AdaptiveMLTrainingIntegration:
    """
    Adaptive ML training that integrates with dynamic pipeline timing.
    Automatically adjusts cycles, sessions, and timeouts based on:
    - Available buffer time
    - Current data size
    - Pipeline constraints
    """

    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "port": 5433,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Base training parameters (scale with data)
        self.base_config = {
            "min_cycles_per_session": 10,
            "max_cycles_per_session": 50,
            "base_session_duration": 60,  # minutes for 1000 records
            "min_session_duration": 20,  # absolute minimum
            "max_session_duration": 240,  # maximum allowed (4 hours)
            "cycle_overhead": 2,  # seconds between cycles
            "data_scale_factor": 0.05,  # time increase per 1000 records
        }

        # Pipeline integration - use full ML slot + buffer time
        self.pipeline_buffer_usage = 0.9  # Use 90% of additional buffer
        self.use_full_ml_slot = True  # Use the dedicated 85-minute ML slot

        # Performance tracking
        self.performance_history = []

        # Create directories
        Path("logs").mkdir(exist_ok=True)
        Path("results/adaptive_training").mkdir(parents=True, exist_ok=True)

    def get_database_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def assess_data_scale(self) -> Dict:
        """Assess current data scale to determine training requirements"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()

            # Get data counts
            cursor.execute("SELECT COUNT(*) FROM races")
            total_races = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM records")
            total_records = cursor.fetchone()[0]

            # Get recent data (last 30 days for active training)
            cursor.execute(
                """
                SELECT COUNT(*) FROM races 
                WHERE date >= CURRENT_DATE - INTERVAL '30 days'
            """
            )
            recent_races = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*) FROM records rec
                JOIN races r ON r.race_id = rec.race_id
                WHERE r.date >= CURRENT_DATE - INTERVAL '30 days'
            """
            )
            recent_records = cursor.fetchone()[0]

            # Calculate data characteristics
            avg_horses_per_race = total_records / max(1, total_races)

            conn.close()

            # Determine data scale category
            if recent_records < 1000:
                scale_category = "small"
                complexity_factor = 0.5
            elif recent_records < 5000:
                scale_category = "medium"
                complexity_factor = 1.0
            elif recent_records < 20000:
                scale_category = "large"
                complexity_factor = 1.5
            else:
                scale_category = "very_large"
                complexity_factor = 2.0

            data_assessment = {
                "total_races": total_races,
                "total_records": total_records,
                "recent_races": recent_races,
                "recent_records": recent_records,
                "avg_horses_per_race": avg_horses_per_race,
                "scale_category": scale_category,
                "complexity_factor": complexity_factor,
                "training_records": recent_records,  # Use recent data for training
            }

            logger.info(
                f"📊 Data Assessment: {scale_category} scale, "
                f"{recent_records} training records, "
                f"complexity factor: {complexity_factor}"
            )

            return data_assessment

        except Exception as e:
            logger.error(f"❌ Error assessing data scale: {e}")
            return {
                "scale_category": "small",
                "complexity_factor": 0.5,
                "training_records": 500,
                "error": str(e),
            }

    def calculate_adaptive_training_config(
        self,
        available_buffer_minutes: int,
        data_assessment: Dict,
        ml_slot_minutes: int = 85,
    ) -> Dict:
        """
        Calculate optimal training configuration based on available time and data scale
        Uses the full ML training slot (85 min) plus additional buffer time
        """

        # Extract data characteristics
        training_records = data_assessment.get("training_records", 500)
        complexity_factor = data_assessment.get("complexity_factor", 1.0)
        scale_category = data_assessment["scale_category"]

        # Calculate base time requirement (scales with data size)
        base_time_needed = (
            self.base_config["base_session_duration"]
            * (training_records / 1000)
            * complexity_factor
        )

        # Apply constraints
        ideal_time_needed = max(
            self.base_config["min_session_duration"],
            min(self.base_config["max_session_duration"], base_time_needed),
        )

        # Calculate total available time: ML slot + portion of buffer
        available_buffer_time = available_buffer_minutes * self.pipeline_buffer_usage
        total_available_time = ml_slot_minutes + available_buffer_time

        logger.info(
            f"⏰ Time Analysis: Need {ideal_time_needed:.1f}min, "
            f"ML Slot {ml_slot_minutes}min + Buffer {available_buffer_time:.1f}min "
            f"= {total_available_time:.1f}min total"
        )

        # Determine training strategy and actual allocation
        if total_available_time >= ideal_time_needed:
            strategy = "optimal"
            allocated_time = min(ideal_time_needed, total_available_time)
        elif total_available_time >= ml_slot_minutes:
            strategy = "extended"  # Use full ML slot + some buffer
            allocated_time = total_available_time
        elif ml_slot_minutes >= self.base_config["min_session_duration"]:
            strategy = "standard"  # Use ML slot only
            allocated_time = ml_slot_minutes
        else:
            strategy = "minimal"
            allocated_time = max(10, ml_slot_minutes)

        # Calculate cycles and sessions based on allocated time and strategy
        if strategy == "optimal":
            cycles_per_session = min(
                self.base_config["max_cycles_per_session"],
                max(
                    self.base_config["min_cycles_per_session"],
                    int(training_records / 50),  # More cycles for more data
                ),
            )
        elif strategy == "extended":
            # Use more cycles since we have extra time
            cycles_per_session = min(
                self.base_config["max_cycles_per_session"],
                max(
                    int(allocated_time / 2),  # ~2 min per cycle
                    self.base_config["min_cycles_per_session"] * 2,
                ),
            )
        elif strategy == "standard":
            # Use ML slot efficiently
            cycles_per_session = max(
                self.base_config["min_cycles_per_session"],
                min(
                    int(allocated_time / 2),  # ~2 min per cycle
                    self.base_config["max_cycles_per_session"],
                ),
            )
        else:  # minimal
            cycles_per_session = self.base_config["min_cycles_per_session"]

        # Calculate cycle timing
        total_overhead = cycles_per_session * self.base_config["cycle_overhead"] / 60
        available_training_time = allocated_time - total_overhead
        time_per_cycle = available_training_time / cycles_per_session

        # Determine wait times
        if allocated_time >= 30:
            wait_between_cycles = 2.0
            wait_between_sessions = 5.0
        elif allocated_time >= 15:
            wait_between_cycles = 1.0
            wait_between_sessions = 2.0
        else:
            wait_between_cycles = 0.5
            wait_between_sessions = 1.0

        training_config = {
            "strategy": strategy,
            "allocated_time_minutes": allocated_time,
            "cycles_per_session": cycles_per_session,
            "estimated_session_duration": allocated_time,
            "time_per_cycle_minutes": time_per_cycle,
            "wait_between_cycles": wait_between_cycles,
            "wait_between_sessions": wait_between_sessions,
            "training_records": training_records,
            "scale_category": scale_category,
            "fits_in_buffer": strategy != "minimal",
            "recommendations": self._generate_recommendations(
                strategy, allocated_time, data_assessment
            ),
        }

        logger.info(
            f"🎯 Training Config: {strategy} strategy, "
            f"{cycles_per_session} cycles, {allocated_time:.1f}min allocated"
        )

        return training_config

    def _generate_recommendations(
        self, strategy: str, allocated_time: float, data_assessment: Dict
    ) -> List[str]:
        """Generate recommendations for optimization"""
        recommendations = []

        if strategy == "minimal":
            recommendations.extend(
                [
                    "⚠️ Very limited training time - consider earlier pipeline start",
                    "💡 Consider running additional training sessions outside pipeline",
                    "🔧 Optimize data preprocessing to reduce training time",
                ]
            )
        elif strategy == "compressed":
            recommendations.extend(
                [
                    "⚙️ Training time compressed - some performance trade-offs expected",
                    "📈 Consider incremental learning to maintain model quality",
                ]
            )
        else:  # optimal
            recommendations.append("✅ Optimal training time available")

        # Data-specific recommendations
        if data_assessment["scale_category"] in ["large", "very_large"]:
            recommendations.extend(
                [
                    "📊 Large dataset detected - consider data sampling strategies",
                    "🚀 Consider distributed training for very large datasets",
                    "💾 Implement model checkpointing for long training sessions",
                ]
            )

        return recommendations

    def integrate_with_pipeline_timing(self, pipeline_schedule: Dict) -> Dict:
        """
        Integrate ML training with pipeline timing system
        """

        # Get pipeline timing info
        timing_analysis = pipeline_schedule.get("timing_analysis", {})
        buffer_minutes = timing_analysis.get("buffer_minutes", 30)
        schedule_type = timing_analysis.get("schedule_type", "normal")

        # Get ML training slot duration
        ml_stage = pipeline_schedule.get("schedule", {}).get("ml_model_training", {})
        ml_slot_minutes = ml_stage.get("duration_minutes", 85)

        # Assess current data scale
        data_assessment = self.assess_data_scale()

        # Calculate adaptive training configuration with ML slot + buffer
        training_config = self.calculate_adaptive_training_config(
            buffer_minutes, data_assessment, ml_slot_minutes
        )

        # Update pipeline schedule with ML training details
        ml_stage = pipeline_schedule["schedule"].get("ml_model_training", {})

        # Enhance ML stage with adaptive configuration
        enhanced_ml_stage = {
            **ml_stage,
            "adaptive_config": training_config,
            "data_scale": data_assessment,
            "buffer_usage": f"{buffer_minutes * self.pipeline_buffer_usage:.1f}/{buffer_minutes} minutes",
            "training_mode": training_config["strategy"],
        }

        # Create integrated schedule
        integrated_schedule = {
            **pipeline_schedule,
            "schedule": {
                **pipeline_schedule["schedule"],
                "ml_model_training": enhanced_ml_stage,
            },
            "ml_training_integration": {
                "adaptive_config": training_config,
                "data_assessment": data_assessment,
                "integration_timestamp": datetime.now().isoformat(),
                "recommendations": training_config["recommendations"],
            },
        }

        logger.info(f"🔗 ML training integrated with {schedule_type} pipeline schedule")

        return integrated_schedule

    def save_integration_config(self, integrated_config: Dict) -> str:
        """Save integrated configuration for execution"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_file = f"results/adaptive_training/integrated_config_{timestamp}.json"

        with open(config_file, "w") as f:
            json.dump(integrated_config, f, indent=2, default=str)

        logger.info(f"💾 Integrated configuration saved: {config_file}")
        return config_file

    def execute_adaptive_training(self, training_config: Dict) -> Dict:
        """Execute training with adaptive configuration"""
        from tools.ml_training.optimized_10_cycle_trainer import OptimizedMLTrainer

        # Create trainer with adaptive configuration
        trainer = OptimizedMLTrainer()

        # Update trainer configuration
        trainer.cycles_per_session = training_config["cycles_per_session"]
        trainer.wait_between_cycles = training_config["wait_between_cycles"]
        trainer.wait_between_sessions = training_config["wait_between_sessions"]

        # Execute single training session
        start_time = datetime.now()
        summary = trainer.run_training_session(1)
        end_time = datetime.now()

        actual_duration = (end_time - start_time).total_seconds() / 60

        # Performance tracking
        performance_result = {
            "timestamp": start_time.isoformat(),
            "strategy": training_config["strategy"],
            "allocated_time": training_config["allocated_time_minutes"],
            "actual_duration": actual_duration,
            "cycles_completed": training_config["cycles_per_session"],
            "efficiency": summary.avg_accuracy if summary else 0.0,
            "fit_in_allocation": actual_duration
            <= training_config["allocated_time_minutes"],
        }

        self.performance_history.append(performance_result)

        logger.info(
            f"📈 Training completed: {actual_duration:.1f}min "
            f"(allocated: {training_config['allocated_time_minutes']:.1f}min)"
        )

        return performance_result


def main():
    """Main function for testing integration"""
    integration = AdaptiveMLTrainingIntegration()

    # Example pipeline schedule (would come from dynamic_pipeline_timing.py)
    example_pipeline_schedule = {
        "schedule": {
            "ml_model_training": {
                "start_time": "16:00",
                "end_time": "17:25",
                "duration_minutes": 85,
                "description": "Train/retrain ML models",
                "critical": True,
            }
        },
        "timing_analysis": {
            "total_window_minutes": 480,
            "allocated_minutes": 400,
            "buffer_minutes": 80,
            "schedule_type": "normal",
        },
    }

    # Integrate ML training
    integrated_schedule = integration.integrate_with_pipeline_timing(
        example_pipeline_schedule
    )

    # Save configuration
    config_file = integration.save_integration_config(integrated_schedule)

    # Show results
    ml_config = integrated_schedule["ml_training_integration"]["adaptive_config"]
    print(f"\n🎯 Adaptive ML Training Configuration:")
    print(f"   Strategy: {ml_config['strategy']}")
    print(f"   Cycles per session: {ml_config['cycles_per_session']}")
    print(f"   Allocated time: {ml_config['allocated_time_minutes']:.1f} minutes")
    print(f"   Data scale: {ml_config['scale_category']}")

    print(f"\n💡 Recommendations:")
    for rec in ml_config["recommendations"]:
        print(f"   {rec}")


if __name__ == "__main__":
    main()
