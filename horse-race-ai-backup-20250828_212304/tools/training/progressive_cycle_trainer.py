#!/usr/bin/env python3
"""
Progressive Cycle Training System

Automated progressive training system that scales from 10 cycles (1000 sessions)
to advanced levels (20 cycles, 2000 sessions) up to 10,000 sessions.
Runs autonomously through the night with optimization checkpoints.
"""

import logging
import sys
import os
import time
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import signal
import threading
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "/home/jc/Documents/Horse-race-ai-v2.04/logs/progressive_training.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ProgressiveCycleTrainer:
    """Progressive training system with scaling complexity"""

    def __init__(self):
        self.base_dir = Path("/home/jc/Documents/Horse-race-ai-v2.04")
        self.logs_dir = self.base_dir / "logs"
        self.models_dir = self.base_dir / "trained_models"
        self.reports_dir = self.base_dir / "reports"

        # Create directories
        for dir_path in [self.logs_dir, self.models_dir, self.reports_dir]:
            dir_path.mkdir(exist_ok=True)

        # Training configuration
        self.training_levels = [
            {
                "level": 1,
                "cycles": 10,
                "sessions": 1000,
                "wait_minutes": 15,
                "description": "Initial Training Phase",
            },
            {
                "level": 2,
                "cycles": 20,
                "sessions": 2000,
                "wait_minutes": 20,
                "description": "Enhanced Training Phase",
            },
            {
                "level": 3,
                "cycles": 40,
                "sessions": 4000,
                "wait_minutes": 25,
                "description": "Advanced Training Phase",
            },
            {
                "level": 4,
                "cycles": 80,
                "sessions": 8000,
                "wait_minutes": 30,
                "description": "Expert Training Phase",
            },
            {
                "level": 5,
                "cycles": 100,
                "sessions": 10000,
                "wait_minutes": 35,
                "description": "Master Training Phase",
            },
        ]

        self.current_level = 1
        self.start_time = datetime.now()
        self.training_history = []
        self.is_running = True

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
        self.is_running = False
        self.save_training_progress()

    def execute_docker_query(self, database: str, query: str) -> Optional[str]:
        """Execute SQL query via Docker"""
        try:
            cmd = [
                "docker",
                "exec",
                "horse_racing_postgres_clean",
                "psql",
                "-U",
                "horse_racing",
                "-d",
                database,
                "-t",
                "-A",
                "-F",
                "|",
                "-c",
                query,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                logger.error(f"Query failed: {result.stderr}")
                return None

            return result.stdout.strip()

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return None

    def get_enriched_data_stats(self) -> Dict:
        """Get current enriched data statistics"""
        stats = {}

        # Power ratings count
        power_count = self.execute_docker_query(
            "advanced_racing_metrics_db", "SELECT COUNT(*) FROM horse_power_ratings;"
        )
        stats["power_ratings"] = int(power_count) if power_count else 0

        # Speed ratings count
        speed_count = self.execute_docker_query(
            "advanced_racing_metrics_db",
            "SELECT COUNT(*) FROM horse_speed_pace_ratings;",
        )
        stats["speed_ratings"] = int(speed_count) if speed_count else 0

        # Monte Carlo count
        monte_count = self.execute_docker_query(
            "advanced_racing_metrics_db",
            "SELECT COUNT(*) FROM monte_carlo_simulations;",
        )
        stats["monte_carlo"] = int(monte_count) if monte_count else 0

        # Total enriched records
        stats["total_enriched"] = (
            stats["power_ratings"] + stats["speed_ratings"] + stats["monte_carlo"]
        )

        return stats

    def run_enhanced_training_cycle(self, level_config: Dict) -> Dict:
        """Run a single enhanced training cycle"""
        logger.info(
            f"🚀 Starting {level_config['description']} - Level {level_config['level']}"
        )
        logger.info(
            f"   📊 Cycles: {level_config['cycles']}, Sessions: {level_config['sessions']}"
        )

        cycle_start = datetime.now()

        # Get current data stats
        data_stats = self.get_enriched_data_stats()
        logger.info(
            f"   📊 Training Data: {data_stats['total_enriched']} enriched records"
        )

        # Run enhanced AI training
        try:
            training_cmd = [
                "python",
                str(self.base_dir / "tools/training/simple_training_runner.py"),
                "--cycles",
                str(level_config["cycles"]),
                "--sessions",
                str(level_config["sessions"]),
                "--level",
                str(level_config["level"]),
            ]

            logger.info(f"   🔧 Executing: {' '.join(training_cmd)}")

            result = subprocess.run(
                training_cmd,
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minute timeout
            )

            if result.returncode == 0:
                logger.info(f"   ✅ Training cycle completed successfully")
                training_output = result.stdout
            else:
                logger.error(f"   ❌ Training failed: {result.stderr}")
                training_output = f"ERROR: {result.stderr}"

        except subprocess.TimeoutExpired:
            logger.error(f"   ⏰ Training cycle timed out after 30 minutes")
            training_output = "ERROR: Timeout"
        except Exception as e:
            logger.error(f"   ❌ Training cycle failed: {e}")
            training_output = f"ERROR: {e}"

        cycle_end = datetime.now()
        cycle_duration = cycle_end - cycle_start

        # Create cycle report
        cycle_report = {
            "level": level_config["level"],
            "description": level_config["description"],
            "cycles": level_config["cycles"],
            "sessions": level_config["sessions"],
            "start_time": cycle_start.isoformat(),
            "end_time": cycle_end.isoformat(),
            "duration_minutes": cycle_duration.total_seconds() / 60,
            "data_stats": data_stats,
            "training_output": training_output[:2000],  # Truncate for storage
            "success": result.returncode == 0 if "result" in locals() else False,
        }

        self.training_history.append(cycle_report)

        return cycle_report

    def optimize_and_review(self, level_config: Dict, cycle_report: Dict):
        """Perform optimization and review after training cycle"""
        logger.info(
            f"🔍 Starting optimization and review for Level {level_config['level']}"
        )

        # Run model validation
        try:
            validation_cmd = [
                "python",
                str(self.base_dir / "tools/ml_training/direct_ai_validation.py"),
            ]

            result = subprocess.run(
                validation_cmd,
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.info(f"   ✅ Model validation completed")
                validation_output = result.stdout
            else:
                logger.error(f"   ❌ Validation failed: {result.stderr}")
                validation_output = f"ERROR: {result.stderr}"

        except Exception as e:
            logger.error(f"   ❌ Validation failed: {e}")
            validation_output = f"ERROR: {e}"

        # Save optimization report
        optimization_report = {
            "level": level_config["level"],
            "optimization_time": datetime.now().isoformat(),
            "cycle_performance": cycle_report,
            "validation_output": validation_output[:1000],
            "recommendations": self.generate_recommendations(cycle_report),
        }

        # Save to file
        report_file = (
            self.reports_dir / f'optimization_report_level_{level_config["level"]}.json'
        )
        with open(report_file, "w") as f:
            json.dump(optimization_report, f, indent=2)

        logger.info(f"   📄 Optimization report saved: {report_file}")

    def generate_recommendations(self, cycle_report: Dict) -> List[str]:
        """Generate optimization recommendations based on cycle performance"""
        recommendations = []

        # Duration-based recommendations
        if cycle_report["duration_minutes"] > 20:
            recommendations.append(
                "Consider reducing batch size for faster training cycles"
            )
        elif cycle_report["duration_minutes"] < 5:
            recommendations.append(
                "Training completed quickly - consider increasing complexity"
            )

        # Data-based recommendations
        total_data = cycle_report["data_stats"]["total_enriched"]
        if total_data < 500:
            recommendations.append(
                "Low enriched data volume - consider expanding historical enrichment"
            )
        elif total_data > 2000:
            recommendations.append(
                "High data volume available - excellent for advanced training"
            )

        # Success-based recommendations
        if cycle_report["success"]:
            recommendations.append("Training cycle successful - ready for next level")
        else:
            recommendations.append(
                "Training issues detected - review logs and configuration"
            )

        return recommendations

    def wait_with_progress(self, minutes: int, level: int):
        """Wait with progress indication"""
        logger.info(
            f"⏰ Waiting {minutes} minutes before Level {level + 1} (optimization period)..."
        )

        total_seconds = minutes * 60
        interval = 60  # Update every minute

        for elapsed in range(0, total_seconds, interval):
            if not self.is_running:
                break

            remaining = (total_seconds - elapsed) // 60
            logger.info(
                f"   ⏳ {remaining} minutes remaining until next training level..."
            )
            time.sleep(min(interval, total_seconds - elapsed))

    def save_training_progress(self):
        """Save current training progress to file"""
        progress_data = {
            "start_time": self.start_time.isoformat(),
            "current_time": datetime.now().isoformat(),
            "current_level": self.current_level,
            "total_levels": len(self.training_levels),
            "training_history": self.training_history,
            "is_running": self.is_running,
        }

        progress_file = self.logs_dir / "progressive_training_progress.json"
        with open(progress_file, "w") as f:
            json.dump(progress_data, f, indent=2)

        logger.info(f"📄 Training progress saved: {progress_file}")

    def create_final_report(self):
        """Create comprehensive final training report"""
        end_time = datetime.now()
        total_duration = end_time - self.start_time

        # Calculate statistics
        total_cycles = sum(h["cycles"] for h in self.training_history)
        total_sessions = sum(h["sessions"] for h in self.training_history)
        successful_levels = sum(1 for h in self.training_history if h["success"])

        final_report = {
            "training_session": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_duration_hours": total_duration.total_seconds() / 3600,
                "levels_completed": len(self.training_history),
                "levels_successful": successful_levels,
            },
            "training_statistics": {
                "total_cycles": total_cycles,
                "total_sessions": total_sessions,
                "average_cycle_duration": (
                    sum(h["duration_minutes"] for h in self.training_history)
                    / len(self.training_history)
                    if self.training_history
                    else 0
                ),
                "success_rate": (
                    (successful_levels / len(self.training_history)) * 100
                    if self.training_history
                    else 0
                ),
            },
            "level_details": self.training_history,
            "final_data_stats": self.get_enriched_data_stats(),
            "completion_status": (
                "COMPLETED"
                if self.current_level > len(self.training_levels)
                else "INTERRUPTED"
            ),
        }

        # Save final report
        final_report_file = (
            self.reports_dir
            / f'progressive_training_final_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        with open(final_report_file, "w") as f:
            json.dump(final_report, f, indent=2)

        # Create markdown summary
        markdown_report = f"""
# 🧠 Progressive Cycle Training - Final Report

**Training Session:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}  
**Total Duration:** {total_duration.total_seconds() / 3600:.1f} hours  
**Status:** {final_report['completion_status']}

## 📊 Training Statistics

- **Levels Completed:** {len(self.training_history)} / {len(self.training_levels)}
- **Success Rate:** {final_report['training_statistics']['success_rate']:.1f}%
- **Total Training Cycles:** {total_cycles:,}
- **Total Training Sessions:** {total_sessions:,}
- **Average Cycle Duration:** {final_report['training_statistics']['average_cycle_duration']:.1f} minutes

## 🎯 Level Performance Summary

"""

        for i, history in enumerate(self.training_history, 1):
            status = "✅" if history["success"] else "❌"
            markdown_report += f"""
### Level {history['level']}: {history['description']}
- **Status:** {status} {'Success' if history['success'] else 'Failed'}
- **Cycles:** {history['cycles']:,} | **Sessions:** {history['sessions']:,}
- **Duration:** {history['duration_minutes']:.1f} minutes
- **Data Used:** {history['data_stats']['total_enriched']} enriched records
"""

        markdown_report += f"""

## 📈 Final System Status

- **Power Ratings:** {final_report['final_data_stats']['power_ratings']} records
- **Speed/Pace Ratings:** {final_report['final_data_stats']['speed_ratings']} records  
- **Monte Carlo Simulations:** {final_report['final_data_stats']['monte_carlo']} records
- **Total Enriched Features:** {final_report['final_data_stats']['total_enriched']} records

## 🚀 Next Steps

{'✅ Progressive training completed successfully! Enhanced AI model fully optimized.' if final_report['completion_status'] == 'COMPLETED' else '⚠️ Training interrupted. Review logs and restart from current level.'}

---

*Progressive Cycle Training System v2.04*
"""

        markdown_file = (
            self.reports_dir
            / f'progressive_training_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        )
        with open(markdown_file, "w") as f:
            f.write(markdown_report)

        logger.info(f"📄 Final report saved: {final_report_file}")
        logger.info(f"📄 Summary report saved: {markdown_file}")

        return final_report

    def run_progressive_training(self):
        """Run the complete progressive training sequence"""
        logger.info("🚀 Starting Progressive Cycle Training System v2.04")
        logger.info("=" * 60)
        logger.info(f"📅 Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🎯 Training Levels: {len(self.training_levels)} levels planned")
        logger.info(f"📊 Maximum Training: 10,000 sessions across all levels")
        print()

        try:
            for level_config in self.training_levels:
                if not self.is_running:
                    logger.info("🛑 Training interrupted by user")
                    break

                self.current_level = level_config["level"]

                # Run training cycle
                cycle_report = self.run_enhanced_training_cycle(level_config)

                # Perform optimization and review
                self.optimize_and_review(level_config, cycle_report)

                # Save progress
                self.save_training_progress()

                # Wait before next level (except for last level)
                if (
                    level_config["level"] < len(self.training_levels)
                    and self.is_running
                ):
                    self.wait_with_progress(
                        level_config["wait_minutes"], level_config["level"]
                    )

                logger.info(f"🎯 Level {level_config['level']} completed!")
                print()

            # Create final report
            final_report = self.create_final_report()

            if final_report["completion_status"] == "COMPLETED":
                logger.info("🎉 Progressive training completed successfully!")
                logger.info(
                    "🚀 Enhanced AI model fully optimized and ready for deployment"
                )
            else:
                logger.info("⚠️ Progressive training interrupted")
                logger.info("💡 Review logs and restart from current level")

        except Exception as e:
            logger.error(f"❌ Critical error in progressive training: {e}")
            self.save_training_progress()
            raise


def main():
    """Main function for progressive cycle training"""

    print("🧠 Progressive Cycle Training System v2.04")
    print("=" * 50)
    print("🎯 Enhanced AI Model Progressive Training")
    print("� Scaling: 10 cycles → 10,000 sessions")
    print("⏰ Autonomous overnight training with optimization")
    print()

    try:
        trainer = ProgressiveCycleTrainer()
        trainer.run_progressive_training()
        return 0

    except KeyboardInterrupt:
        print("\n🛑 Training interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
