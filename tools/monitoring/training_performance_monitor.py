#!/usr/bin/env python3
"""
🔍 Real-time ML Training Monitor
===============================

Monitors training performance for 500-session run with enhanced tracking.
Provides detailed performance metrics and progress visualization.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/training_monitor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class TrainingPerformanceMonitor:
    """Real-time training performance monitor"""

    def __init__(self):
        self.start_time = datetime.now()
        self.metrics_history = []
        self.session_history = []

        # Performance tracking
        self.target_sessions = 500
        self.cycles_per_session = 10
        self.total_target_cycles = self.target_sessions * self.cycles_per_session

        # Create monitoring directories
        Path("logs").mkdir(exist_ok=True)
        Path("monitoring").mkdir(exist_ok=True)
        Path("monitoring/charts").mkdir(exist_ok=True)

    def log_session_start(self, session_id: int):
        """Log session start with detailed information"""
        elapsed = datetime.now() - self.start_time
        progress = (session_id / self.target_sessions) * 100

        logger.info("=" * 60)
        logger.info(f"🚀 SESSION {session_id}/{self.target_sessions} STARTING")
        logger.info(f"📊 Progress: {progress:.1f}% complete")
        logger.info(f"⏱️  Elapsed time: {elapsed}")
        logger.info(f"🎯 Target: {self.cycles_per_session} cycles in this session")

        if session_id > 1:
            sessions_per_hour = session_id / (elapsed.total_seconds() / 3600)
            estimated_completion = self.start_time + timedelta(
                hours=self.target_sessions / sessions_per_hour
            )
            logger.info(f"📈 Rate: {sessions_per_hour:.1f} sessions/hour")
            logger.info(
                f"🏁 Est. completion: {estimated_completion.strftime('%H:%M:%S')}"
            )

        logger.info("=" * 60)

    def log_cycle_performance(
        self,
        session_id: int,
        cycle_id: int,
        accuracy: float,
        duration: float,
        improvement: float,
    ):
        """Log individual cycle performance"""
        total_cycles = (session_id - 1) * self.cycles_per_session + cycle_id
        cycle_progress = (total_cycles / self.total_target_cycles) * 100

        # Store metrics
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "cycle_id": cycle_id,
            "total_cycles": total_cycles,
            "accuracy": accuracy,
            "duration": duration,
            "improvement": improvement,
            "progress": cycle_progress,
        }
        self.metrics_history.append(metrics)

        # Enhanced logging with performance indicators
        status = "🔥" if improvement > 0.01 else "📈" if improvement > 0 else "📊"
        logger.info(
            f"   {status} Cycle {cycle_id:2d}: Acc={accuracy:.4f} "
            f"({improvement:+.4f}) | {duration:.1f}s | {cycle_progress:.1f}% total"
        )

        # Performance warnings
        if duration > 60:
            logger.warning(f"⚠️  Slow cycle detected: {duration:.1f}s")
        if accuracy < 0.5:
            logger.warning(f"⚠️  Low accuracy detected: {accuracy:.4f}")

    def log_session_summary(
        self,
        session_id: int,
        avg_accuracy: float,
        best_accuracy: float,
        total_duration: float,
        session_improvement: float,
    ):
        """Log comprehensive session summary"""

        # Store session data
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "avg_accuracy": avg_accuracy,
            "best_accuracy": best_accuracy,
            "total_duration": total_duration,
            "session_improvement": session_improvement,
            "cycles_completed": self.cycles_per_session,
        }
        self.session_history.append(session_data)

        # Calculate running averages
        if len(self.session_history) >= 10:
            recent_avg = sum(s["avg_accuracy"] for s in self.session_history[-10:]) / 10
            recent_improvement = (
                sum(s["session_improvement"] for s in self.session_history[-10:]) / 10
            )
        else:
            recent_avg = avg_accuracy
            recent_improvement = session_improvement

        # Session summary with performance analysis
        logger.info("")
        logger.info(f"📊 SESSION {session_id} COMPLETE:")
        logger.info(
            f"   ⏱️  Duration: {total_duration:.1f}s ({total_duration/60:.1f} min)"
        )
        logger.info(f"   🎯 Avg Accuracy: {avg_accuracy:.4f}")
        logger.info(f"   🏆 Best Accuracy: {best_accuracy:.4f}")
        logger.info(f"   📈 Improvement: {session_improvement:+.4f}")
        logger.info(f"   📊 Recent 10-session avg: {recent_avg:.4f}")
        logger.info(f"   🔥 Recent improvement rate: {recent_improvement:+.4f}")

        # Performance trend analysis
        if session_id > 1:
            prev_session = (
                self.session_history[-2] if len(self.session_history) > 1 else None
            )
            if prev_session:
                accuracy_trend = avg_accuracy - prev_session["avg_accuracy"]
                trend_emoji = (
                    "📈" if accuracy_trend > 0 else "📉" if accuracy_trend < 0 else "➡️"
                )
                logger.info(f"   {trend_emoji} Trend vs prev: {accuracy_trend:+.4f}")

        # Milestone celebrations
        if session_id % 50 == 0:
            logger.info(f"🎉 MILESTONE: {session_id} sessions completed!")
            self.generate_progress_report(session_id)

        logger.info("")

    def generate_progress_report(self, current_session: int):
        """Generate detailed progress report"""
        elapsed = datetime.now() - self.start_time
        progress = (current_session / self.target_sessions) * 100

        logger.info("🎯 PROGRESS REPORT")
        logger.info("-" * 40)
        logger.info(
            f"Sessions: {current_session}/{self.target_sessions} ({progress:.1f}%)"
        )
        logger.info(f"Elapsed: {elapsed}")

        if current_session > 0:
            sessions_per_hour = current_session / (elapsed.total_seconds() / 3600)
            remaining_sessions = self.target_sessions - current_session
            eta = remaining_sessions / sessions_per_hour if sessions_per_hour > 0 else 0

            logger.info(f"Rate: {sessions_per_hour:.1f} sessions/hour")
            logger.info(f"ETA: {eta:.1f} hours remaining")

        # Performance statistics
        if self.session_history:
            avg_accuracy = sum(s["avg_accuracy"] for s in self.session_history) / len(
                self.session_history
            )
            best_overall = max(s["best_accuracy"] for s in self.session_history)
            total_improvement = sum(
                s["session_improvement"] for s in self.session_history
            )

            logger.info(f"Avg accuracy: {avg_accuracy:.4f}")
            logger.info(f"Best overall: {best_overall:.4f}")
            logger.info(f"Total improvement: {total_improvement:+.4f}")

        logger.info("-" * 40)

    def save_metrics_to_file(self):
        """Save metrics to JSON file for analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save cycle metrics
        with open(f"monitoring/cycle_metrics_{timestamp}.json", "w") as f:
            json.dump(self.metrics_history, f, indent=2)

        # Save session summaries
        with open(f"monitoring/session_summaries_{timestamp}.json", "w") as f:
            json.dump(self.session_history, f, indent=2)

        logger.info(f"📊 Metrics saved to monitoring/metrics_{timestamp}.json")

    def create_performance_chart(self):
        """Create real-time performance visualization"""
        if not self.session_history:
            return

        try:
            # Extract data for plotting
            sessions = [s["session_id"] for s in self.session_history]
            avg_accuracies = [s["avg_accuracy"] for s in self.session_history]
            best_accuracies = [s["best_accuracy"] for s in self.session_history]
            improvements = [s["session_improvement"] for s in self.session_history]

            # Create subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

            # Accuracy trends
            ax1.plot(
                sessions, avg_accuracies, "b-", label="Average Accuracy", linewidth=2
            )
            ax1.plot(
                sessions, best_accuracies, "g-", label="Best Accuracy", linewidth=2
            )
            ax1.set_title("Training Accuracy Over Time")
            ax1.set_xlabel("Session")
            ax1.set_ylabel("Accuracy")
            ax1.legend()
            ax1.grid(True)

            # Improvement trends
            ax2.bar(sessions, improvements, alpha=0.7, color="orange")
            ax2.axhline(y=0, color="red", linestyle="--", alpha=0.5)
            ax2.set_title("Session Improvements")
            ax2.set_xlabel("Session")
            ax2.set_ylabel("Improvement")
            ax2.grid(True)

            # Duration trends
            durations = [s["total_duration"] for s in self.session_history]
            ax3.plot(sessions, durations, "r-", linewidth=2)
            ax3.set_title("Session Duration Over Time")
            ax3.set_xlabel("Session")
            ax3.set_ylabel("Duration (seconds)")
            ax3.grid(True)

            # Progress visualization
            progress_values = [(s / self.target_sessions) * 100 for s in sessions]
            ax4.plot(sessions, progress_values, "purple", linewidth=3)
            ax4.fill_between(sessions, progress_values, alpha=0.3, color="purple")
            ax4.set_title(
                f"Training Progress ({len(sessions)}/{self.target_sessions} sessions)"
            )
            ax4.set_xlabel("Session")
            ax4.set_ylabel("Progress (%)")
            ax4.set_ylim(0, 100)
            ax4.grid(True)

            plt.tight_layout()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plt.savefig(
                f"monitoring/charts/training_progress_{timestamp}.png",
                dpi=300,
                bbox_inches="tight",
            )
            plt.close()

            logger.info(
                f"📊 Performance chart saved to monitoring/charts/training_progress_{timestamp}.png"
            )

        except Exception as e:
            logger.warning(f"⚠️  Could not create chart: {e}")

    def final_summary(self):
        """Generate final training summary"""
        total_elapsed = datetime.now() - self.start_time

        logger.info("🏁 TRAINING COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"Total time: {total_elapsed}")
        logger.info(f"Sessions completed: {len(self.session_history)}")
        logger.info(f"Total cycles: {len(self.metrics_history)}")

        if self.session_history:
            avg_accuracy = sum(s["avg_accuracy"] for s in self.session_history) / len(
                self.session_history
            )
            best_overall = max(s["best_accuracy"] for s in self.session_history)
            total_improvement = sum(
                s["session_improvement"] for s in self.session_history
            )
            avg_duration = sum(s["total_duration"] for s in self.session_history) / len(
                self.session_history
            )

            logger.info(f"Overall avg accuracy: {avg_accuracy:.4f}")
            logger.info(f"Best accuracy achieved: {best_overall:.4f}")
            logger.info(f"Total improvement: {total_improvement:+.4f}")
            logger.info(f"Avg session duration: {avg_duration:.1f}s")

            sessions_per_hour = len(self.session_history) / (
                total_elapsed.total_seconds() / 3600
            )
            logger.info(f"Training rate: {sessions_per_hour:.1f} sessions/hour")

        # Save final results
        self.save_metrics_to_file()
        self.create_performance_chart()

        logger.info("=" * 60)
