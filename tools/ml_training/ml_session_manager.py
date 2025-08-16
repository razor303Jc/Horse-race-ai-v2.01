#!/usr/bin/env python3
"""
ML Session Manager for 2000x50-Cycle Training
Horse Racing AI v2.02

Manages 2000 sessions of 50 cycles each, with review after each session.
Total: 100,000 training cycles with comprehensive performance tracking.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tools.ml_training.automated_ml_cycle_manager import MLTrainingCycleManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/ml_session_manager.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class MLSessionManager:
    """Manages multiple 10-cycle training sessions with small waits"""

    def __init__(self):
        self.target_sessions = 1000
        self.cycles_per_session = 10
        self.total_cycles = self.target_sessions * self.cycles_per_session
        self.sessions_completed = 0
        self.start_time = None
        self.session_results = []
        self.small_wait = 5.0  # 5 second wait between sessions

        # Create results directory
        self.results_dir = Path("results/ml_sessions")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Initialized ML Session Manager:")
        logger.info(f"  Target Sessions: {self.target_sessions:,}")
        logger.info(f"  Cycles per Session: {self.cycles_per_session}")
        logger.info(f"  Total Cycles: {self.total_cycles:,}")

    async def run_single_session(self, session_id: int) -> Dict:
        """Run a single 50-cycle training session"""
        session_start = datetime.now()
        logger.info(f"🚀 Starting Session {session_id}/{self.target_sessions}")

        try:
            # Initialize cycle manager for this session
            cycle_manager = MLTrainingCycleManager()

            # Run the training cycles
            await cycle_manager.run_training_cycles()

            # Get session results
            session_results = cycle_manager.generate_performance_report()
            session_end = datetime.now()
            session_duration = (session_end - session_start).total_seconds()

            # Calculate accuracy improvement
            baseline = cycle_manager.baseline_accuracy
            best = cycle_manager.best_accuracy
            improvement = ((best - baseline) / baseline) * 100 if baseline > 0 else 0

            # Add session metadata
            session_summary = {
                "session_id": session_id,
                "start_time": session_start.isoformat(),
                "end_time": session_end.isoformat(),
                "duration_seconds": session_duration,
                "cycles_completed": len(cycle_manager.metrics_history),
                "best_accuracy": best,
                "baseline_accuracy": baseline,
                "accuracy_improvement": improvement,
                "total_records_processed": sum(
                    m.records_processed for m in cycle_manager.metrics_history
                ),
                "avg_cycle_time": (
                    session_duration / len(cycle_manager.metrics_history)
                    if cycle_manager.metrics_history
                    else 0
                ),
                "performance_report": session_results,
            }

            # Save session results
            session_file = self.results_dir / f"session_{session_id:04d}_results.json"
            with open(session_file, "w") as f:
                json.dump(session_summary, f, indent=2, default=str)

            logger.info(f"✅ Session {session_id} completed in {session_duration:.1f}s")
            baseline_acc = cycle_manager.baseline_accuracy
            best_acc = cycle_manager.best_accuracy
            logger.info(f"   Accuracy: {baseline_acc:.4f} → {best_acc:.4f}")
            improvement = session_summary["accuracy_improvement"]
            logger.info(f"   Improvement: {improvement:+.2f}%")

            return session_summary

        except Exception as e:
            logger.error(f"❌ Session {session_id} failed: {e}")
            return {"session_id": session_id, "error": str(e), "status": "failed"}

    def calculate_eta(self, current_session: int, session_duration: float) -> str:
        """Calculate estimated time to completion"""
        remaining_sessions = self.target_sessions - current_session
        eta_seconds = remaining_sessions * session_duration

        if eta_seconds < 3600:
            return f"{eta_seconds/60:.1f} minutes"
        elif eta_seconds < 86400:
            return f"{eta_seconds/3600:.1f} hours"
        else:
            return f"{eta_seconds/86400:.1f} days"

    def generate_progress_report(self, session_id: int) -> None:
        """Generate comprehensive progress report"""
        if not self.session_results:
            return

        successful_sessions = [s for s in self.session_results if "error" not in s]

        if not successful_sessions:
            return

        # Calculate statistics
        total_cycles = sum(s["cycles_completed"] for s in successful_sessions)
        total_records = sum(s["total_records_processed"] for s in successful_sessions)
        avg_improvement = sum(
            s["accuracy_improvement"] for s in successful_sessions
        ) / len(successful_sessions)
        best_session = max(successful_sessions, key=lambda x: x["accuracy_improvement"])
        avg_session_time = sum(
            s["duration_seconds"] for s in successful_sessions
        ) / len(successful_sessions)

        # Progress percentage
        progress_pct = (session_id / self.target_sessions) * 100

        print("\n" + "=" * 60)
        print(f"📊 ML TRAINING PROGRESS REPORT - Session {session_id}")
        print("=" * 60)
        print(f"📈 OVERALL PROGRESS:")
        print(
            f"   Sessions: {session_id:,}/{self.target_sessions:,} ({progress_pct:.1f}%)"
        )
        print(f"   Total Cycles: {total_cycles:,}/{self.total_cycles:,}")
        print(f"   Total Records: {total_records:,}")
        print()
        print(f"🎯 PERFORMANCE METRICS:")
        print(f"   Average Improvement: {avg_improvement:+.2f}%")
        print(
            f"   Best Session: #{best_session['session_id']} ({best_session['accuracy_improvement']:+.2f}%)"
        )
        print(f"   Average Session Time: {avg_session_time:.1f} seconds")
        print()
        print(f"⏰ TIMING:")
        if session_id > 1:
            eta = self.calculate_eta(session_id, avg_session_time)
            print(f"   ETA for completion: {eta}")
        print(f"   Sessions per hour: {3600/avg_session_time:.1f}")
        print("=" * 60)

    async def run_all_sessions(self, start_session: int = 1) -> None:
        """Run all 1000 training sessions with small waits"""
        self.start_time = datetime.now()
        logger.info(
            f"🚀 Starting ML Session Manager - {self.target_sessions:,} sessions"
        )

        for session_id in range(start_session, self.target_sessions + 1):
            try:
                # Run the session
                session_result = await self.run_single_session(session_id)
                self.session_results.append(session_result)
                self.sessions_completed = session_id

                # Generate progress report every 10 sessions
                if session_id % 10 == 0:
                    self.generate_progress_report(session_id)

                # Save checkpoint every 50 sessions
                if session_id % 50 == 0:
                    await self.save_checkpoint()

                # Small wait between sessions (5 seconds)
                logger.info(f"⏸️  Small wait ({self.small_wait}s) before next session...")
                await asyncio.sleep(self.small_wait)

            except KeyboardInterrupt:
                logger.info(f"⏸️  Training interrupted at session {session_id}")
                await self.save_checkpoint()
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in session {session_id}: {e}")
                continue

        # Final report
        await self.generate_final_report()

    async def save_checkpoint(self) -> None:
        """Save progress checkpoint"""
        checkpoint = {
            "sessions_completed": self.sessions_completed,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "checkpoint_time": datetime.now().isoformat(),
            "session_results_summary": len(self.session_results),
            "successful_sessions": len(
                [s for s in self.session_results if "error" not in s]
            ),
        }

        checkpoint_file = self.results_dir / "training_checkpoint.json"
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint, f, indent=2)

        logger.info(
            f"💾 Checkpoint saved: {self.sessions_completed} sessions completed"
        )

    async def generate_final_report(self) -> None:
        """Generate comprehensive final report"""
        if not self.session_results:
            logger.warning("No session results to report")
            return

        successful_sessions = [s for s in self.session_results if "error" not in s]
        failed_sessions = [s for s in self.session_results if "error" in s]

        end_time = datetime.now()
        total_duration = (
            (end_time - self.start_time).total_seconds() if self.start_time else 0
        )

        final_report = {
            "training_summary": {
                "total_sessions_attempted": len(self.session_results),
                "successful_sessions": len(successful_sessions),
                "failed_sessions": len(failed_sessions),
                "success_rate": (
                    (len(successful_sessions) / len(self.session_results)) * 100
                    if self.session_results
                    else 0
                ),
                "total_duration_hours": total_duration / 3600,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": end_time.isoformat(),
            },
            "performance_statistics": {},
            "session_details": self.session_results[-10:],  # Last 10 sessions
        }

        if successful_sessions:
            total_cycles = sum(s["cycles_completed"] for s in successful_sessions)
            total_records = sum(
                s["total_records_processed"] for s in successful_sessions
            )
            improvements = [s["accuracy_improvement"] for s in successful_sessions]

            final_report["performance_statistics"] = {
                "total_cycles_completed": total_cycles,
                "total_records_processed": total_records,
                "average_improvement_per_session": sum(improvements)
                / len(improvements),
                "best_improvement": max(improvements),
                "worst_improvement": min(improvements),
                "median_improvement": sorted(improvements)[len(improvements) // 2],
                "cycles_per_hour": (
                    total_cycles / (total_duration / 3600) if total_duration > 0 else 0
                ),
            }

        # Save final report
        report_file = (
            self.results_dir
            / f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(final_report, f, indent=2, default=str)

        # Print summary
        print("\n" + "=" * 70)
        print("🎉 ML TRAINING CAMPAIGN COMPLETED!")
        print("=" * 70)
        print(f"📊 FINAL STATISTICS:")
        print(
            f"   Sessions: {len(successful_sessions)}/{len(self.session_results)} successful"
        )
        print(
            f"   Total Cycles: {final_report['performance_statistics'].get('total_cycles_completed', 0):,}"
        )
        print(f"   Total Duration: {total_duration/3600:.1f} hours")
        if successful_sessions:
            print(
                f"   Average Improvement: {final_report['performance_statistics']['average_improvement_per_session']:+.2f}%"
            )
            print(
                f"   Best Session: {final_report['performance_statistics']['best_improvement']:+.2f}%"
            )
        print(f"📁 Report saved: {report_file}")
        print("=" * 70)


async def main():
    """Main execution function"""
    print("🤖 ML Session Manager - 2000x50 Cycle Training")
    print("=" * 50)

    # Check for resume option
    if len(sys.argv) > 1 and sys.argv[1] == "resume":
        checkpoint_file = Path("results/ml_sessions/training_checkpoint.json")
        if checkpoint_file.exists():
            with open(checkpoint_file) as f:
                checkpoint = json.load(f)
            start_session = checkpoint["sessions_completed"] + 1
            print(f"📂 Resuming from session {start_session}")
        else:
            print("❌ No checkpoint found, starting from beginning")
            start_session = 1
    else:
        start_session = 1

    manager = MLSessionManager()
    await manager.run_all_sessions(start_session)


if __name__ == "__main__":
    asyncio.run(main())
