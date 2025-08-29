#!/usr/bin/env python3
"""
Enhanced Pipeline Monitor with Comprehensive Logging
Horse Racing AI v2.04

Features:
- Real-time pipeline monitoring
- Comprehensive logging system
- Task validation and tracking
- Performance metrics collection
- Advanced error handling
- Integration with Node-RED dashboard
"""

import json
import logging
import os
import sys
import time
import asyncio
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import signal


# Setup comprehensive logging
class PipelineLogger:
    """Enhanced logging system for pipeline operations"""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Create multiple log handlers
        self.setup_loggers()

    def setup_loggers(self):
        """Setup multiple specialized loggers"""

        # Main pipeline logger
        self.pipeline_logger = self._create_logger(
            "pipeline", self.log_dir / "pipeline_monitor.log", level=logging.INFO
        )

        # Performance logger
        self.performance_logger = self._create_logger(
            "performance", self.log_dir / "performance_metrics.log", level=logging.INFO
        )

        # Error logger
        self.error_logger = self._create_logger(
            "errors", self.log_dir / "pipeline_errors.log", level=logging.ERROR
        )

        # Task logger
        self.task_logger = self._create_logger(
            "tasks", self.log_dir / "task_execution.log", level=logging.DEBUG
        )

    def _create_logger(self, name: str, log_file: Path, level: int) -> logging.Logger:
        """Create a specialized logger"""
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger


@dataclass
class TaskMetrics:
    """Metrics for individual pipeline tasks"""

    task_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: str = "running"
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    output_size: int = 0
    error_message: Optional[str] = None

    def complete(self, status: str = "success", error: str = None):
        """Mark task as complete"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = status
        if error:
            self.error_message = error


class EnhancedPipelineMonitor:
    """Comprehensive pipeline monitoring and logging system"""

    def __init__(self):
        self.logger = PipelineLogger()
        self.tasks: Dict[str, TaskMetrics] = {}
        self.system_metrics: Dict[str, Any] = {}
        self.pipeline_status = "idle"
        self.start_time = datetime.now()
        self.stats_cache = {}  # Cache for generated statistics

        # Task definitions with advanced mathematical functions
        self.available_tasks = {
            "data_validation": {
                "description": "Comprehensive data validation and quality checks",
                "script": "tools/automation/automated_data_pipeline.py",
                "args": ["--stage=validation", "--logging=verbose"],
                "estimated_duration": 120,
                "category": "data_processing",
            },
            "data_processing": {
                "description": "Advanced data processing and feature engineering",
                "script": "tools/automation/automated_data_pipeline.py",
                "args": ["--stage=processing", "--logging=verbose"],
                "estimated_duration": 300,
                "category": "data_processing",
            },
            "data_upload": {
                "description": "Database upload and integrity verification",
                "script": "tools/automation/automated_data_pipeline.py",
                "args": ["--stage=upload", "--logging=verbose"],
                "estimated_duration": 180,
                "category": "data_processing",
            },
            "power_ratings": {
                "description": "Calculate comprehensive power ratings (0-140 scale)",
                "script": "tools/advanced_metrics_pipeline.py",
                "args": ["--metric=power_ratings", "--logging=verbose"],
                "estimated_duration": 240,
                "category": "ratings_analytics",
            },
            "speed_ratings": {
                "description": "Speed figure analysis and pace ratings",
                "script": "tools/advanced_metrics_pipeline.py",
                "args": ["--metric=speed_ratings", "--logging=verbose"],
                "estimated_duration": 180,
                "category": "ratings_analytics",
            },
            "form_scoring": {
                "description": "Advanced form analysis and scoring system",
                "script": "tools/advanced_metrics_pipeline.py",
                "args": ["--metric=form_scoring", "--logging=verbose"],
                "estimated_duration": 150,
                "category": "ratings_analytics",
            },
            "monte_carlo_simulation": {
                "description": "Monte Carlo race outcome simulations (10,000 runs)",
                "script": "scripts/complete_pipeline_runner.py",
                "args": ["--phase=monte_carlo", "--logging=verbose"],
                "estimated_duration": 420,
                "category": "ml_analysis",
            },
            "ml_training": {
                "description": "Comprehensive ML model training (4 ensemble models)",
                "script": "tools/ml_training/unified_ml_trainer.py",
                "args": ["--mode=comprehensive", "--logging=verbose"],
                "estimated_duration": 1800,
                "category": "ml_analysis",
            },
            "ai_selections": {
                "description": "Generate AI race selections and predictions",
                "script": "scripts/run_real_selections.py",
                "args": ["--mode=live", "--logging=verbose"],
                "estimated_duration": 300,
                "category": "ml_analysis",
            },
            "performance_tracking": {
                "description": "Comprehensive performance tracking and analysis",
                "script": "scripts/race_results_tracker.py",
                "args": ["--mode=comprehensive", "--logging=verbose"],
                "estimated_duration": 240,
                "category": "analytics",
            },
            "betting_strategies": {
                "description": "Advanced betting strategies (80/20, Dutching, etc.)",
                "script": "scripts/train_strategy_aware_models.py",
                "args": ["--execute", "--logging=verbose"],
                "estimated_duration": 360,
                "category": "betting_analysis",
            },
            "live_betting_monitor": {
                "description": "Live betting opportunities and odds monitoring",
                "script": "tools/pipeline/betting_integration_system.py",
                "args": ["--mode=live", "--logging=verbose"],
                "estimated_duration": 60,
                "category": "betting_analysis",
            },
            "risk_assessment": {
                "description": "Comprehensive risk analysis and portfolio management",
                "script": "tools/pipeline/betting_integration_system.py",
                "args": ["--mode=risk_assessment", "--logging=verbose"],
                "estimated_duration": 180,
                "category": "betting_analysis",
            },
            "staking_systems": {
                "description": "Advanced staking systems and bankroll management",
                "script": "tools/pipeline/betting_integration_system.py",
                "args": ["--mode=staking", "--logging=verbose"],
                "estimated_duration": 120,
                "category": "betting_analysis",
            },
            "fast_results": {
                "description": "Quick analysis for immediate race predictions",
                "script": "scripts/complete_pipeline_runner.py",
                "args": ["--mode=fast", "--logging=verbose"],
                "estimated_duration": 180,
                "category": "fast_analysis",
            },
        }

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.pipeline_logger.info(
            f"Received signal {signum}, shutting down gracefully..."
        )
        self.shutdown()
        sys.exit(0)

    async def start_task(self, task_name: str, custom_args: List[str] = None) -> str:
        """Start a pipeline task with comprehensive monitoring"""

        if task_name not in self.available_tasks:
            error_msg = f"Unknown task: {task_name}"
            self.logger.error_logger.error(error_msg)
            return f"ERROR: {error_msg}"

        task_config = self.available_tasks[task_name]
        task_id = f"{task_name}_{int(time.time())}"

        # Create task metrics
        self.tasks[task_id] = TaskMetrics(
            task_name=task_name, start_time=datetime.now()
        )

        # Log task start
        self.logger.task_logger.info(f"🚀 Starting task: {task_name} (ID: {task_id})")
        self.logger.task_logger.info(f"📋 Description: {task_config['description']}")
        self.logger.task_logger.info(
            f"⏱️ Estimated duration: {task_config['estimated_duration']} seconds"
        )

        try:
            # Build command
            script_path = Path(task_config["script"])
            args = custom_args or task_config["args"]

            if not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_path}")

            # Execute task
            cmd = [sys.executable, str(script_path)] + args

            self.logger.task_logger.info(f"🔧 Executing: {' '.join(cmd)}")

            # Run with monitoring
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path.cwd(),
            )

            # Monitor process
            stdout, stderr = await process.communicate()

            # Process results
            if process.returncode == 0:
                self.tasks[task_id].complete("success")
                self.tasks[task_id].output_size = len(stdout)

                success_msg = f"✅ Task {task_name} completed successfully"
                self.logger.task_logger.info(success_msg)
                self.logger.task_logger.info(
                    f"📊 Duration: {self.tasks[task_id].duration:.2f} seconds"
                )

                return f"SUCCESS: {success_msg}\\nOutput size: {len(stdout)} bytes"
            else:
                error_msg = stderr.decode("utf-8") if stderr else "Unknown error"
                self.tasks[task_id].complete("error", error_msg)

                self.logger.error_logger.error(
                    f"❌ Task {task_name} failed: {error_msg}"
                )

                return f"ERROR: Task {task_name} failed\\n{error_msg}"

        except Exception as e:
            error_msg = str(e)
            self.tasks[task_id].complete("error", error_msg)
            self.logger.error_logger.error(
                f"❌ Task {task_name} exception: {error_msg}"
            )

            return f"EXCEPTION: {error_msg}"

    def get_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Process information
            running_tasks = len(
                [t for t in self.tasks.values() if t.status == "running"]
            )
            completed_tasks = len(
                [t for t in self.tasks.values() if t.status == "success"]
            )
            failed_tasks = len([t for t in self.tasks.values() if t.status == "error"])

            metrics = {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": (disk.used / disk.total) * 100,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_free_gb": disk.free / (1024**3),
                },
                "pipeline": {
                    "status": self.pipeline_status,
                    "uptime_minutes": (datetime.now() - self.start_time).total_seconds()
                    / 60,
                    "running_tasks": running_tasks,
                    "completed_tasks": completed_tasks,
                    "failed_tasks": failed_tasks,
                    "total_tasks": len(self.tasks),
                },
                "tasks": {
                    task_id: asdict(metrics) for task_id, metrics in self.tasks.items()
                },
            }

            self.system_metrics = metrics

            # Log performance metrics
            self.logger.performance_logger.info(
                f"📊 System: CPU {cpu_percent:.1f}% | "
                f"Memory {memory.percent:.1f}% | "
                f"Disk {(disk.used/disk.total)*100:.1f}% | "
                f"Tasks: {running_tasks} running, {completed_tasks} completed, {failed_tasks} failed"
            )

            return metrics

        except Exception as e:
            self.logger.error_logger.error(f"Failed to collect system metrics: {e}")
            return {"error": str(e)}

    def get_pipeline_summary(self) -> str:
        """Generate comprehensive pipeline summary"""

        metrics = self.get_system_metrics()

        summary = f"""
🏇 HORSE RACING AI PIPELINE SUMMARY
==================================
⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🕒 Uptime: {metrics['pipeline']['uptime_minutes']:.1f} minutes
📊 Status: {metrics['pipeline']['status'].upper()}

🖥️ SYSTEM METRICS:
- CPU Usage: {metrics['system']['cpu_percent']:.1f}%
- Memory Usage: {metrics['system']['memory_percent']:.1f}%
- Disk Usage: {metrics['system']['disk_percent']:.1f}%
- Available Memory: {metrics['system']['memory_available_gb']:.2f} GB
- Free Disk Space: {metrics['system']['disk_free_gb']:.2f} GB

📋 TASK STATISTICS:
- Running Tasks: {metrics['pipeline']['running_tasks']}
- Completed Tasks: {metrics['pipeline']['completed_tasks']}
- Failed Tasks: {metrics['pipeline']['failed_tasks']}
- Total Tasks Executed: {metrics['pipeline']['total_tasks']}

🎯 AVAILABLE PIPELINE TASKS:
"""

        # Add available tasks by category
        categories = {}
        for task_name, config in self.available_tasks.items():
            category = config["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append((task_name, config))

        for category, tasks in categories.items():
            summary += f"\n📦 {category.upper().replace('_', ' ')}:\n"
            for task_name, config in tasks:
                duration_min = config["estimated_duration"] // 60
                summary += (
                    f"  • {task_name}: {config['description']} (~{duration_min}min)\\n"
                )

        return summary

    def generate_task_statistics(self, task_name: str = None) -> Dict[str, Any]:
        """Generate detailed statistics for completed tasks"""

        stats = {
            "timestamp": datetime.now().isoformat(),
            "overall_stats": {},
            "task_results": {},
            "performance_metrics": {},
            "success_summary": {},
        }

        # Filter tasks based on task_name if provided
        relevant_tasks = {}
        if task_name:
            relevant_tasks = {
                k: v for k, v in self.tasks.items() if v.task_name == task_name
            }
        else:
            relevant_tasks = self.tasks

        if not relevant_tasks:
            stats["message"] = (
                f"No tasks found for: {task_name}"
                if task_name
                else "No tasks executed yet"
            )
            return stats

        # Calculate overall statistics
        total_tasks = len(relevant_tasks)
        successful_tasks = len(
            [t for t in relevant_tasks.values() if t.status == "success"]
        )
        failed_tasks = len([t for t in relevant_tasks.values() if t.status == "failed"])
        running_tasks = len(
            [t for t in relevant_tasks.values() if t.status == "running"]
        )

        # Calculate execution times
        completed_tasks = [t for t in relevant_tasks.values() if t.duration is not None]
        avg_duration = (
            sum(t.duration for t in completed_tasks) / len(completed_tasks)
            if completed_tasks
            else 0
        )
        total_duration = sum(t.duration for t in completed_tasks)

        stats["overall_stats"] = {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "success_rate": (
                round((successful_tasks / total_tasks) * 100, 2)
                if total_tasks > 0
                else 0
            ),
            "average_duration": round(avg_duration, 2),
            "total_duration": round(total_duration, 2),
            "data_processed_mb": sum(t.output_size for t in relevant_tasks.values())
            / (1024 * 1024),
        }

        # Generate task-specific results
        for task_id, task in relevant_tasks.items():
            task_stats = {
                "name": task.task_name,
                "status": task.status,
                "start_time": task.start_time.isoformat(),
                "duration": task.duration,
                "output_size_kb": (
                    round(task.output_size / 1024, 2) if task.output_size else 0
                ),
                "category": self.available_tasks.get(task.task_name, {}).get(
                    "category", "unknown"
                ),
            }

            if task.end_time:
                task_stats["end_time"] = task.end_time.isoformat()
            if task.error_message:
                task_stats["error"] = task.error_message

            stats["task_results"][task_id] = task_stats

        # Performance metrics
        stats["performance_metrics"] = {
            "fastest_task": (
                min(completed_tasks, key=lambda t: t.duration).task_name
                if completed_tasks
                else None
            ),
            "slowest_task": (
                max(completed_tasks, key=lambda t: t.duration).task_name
                if completed_tasks
                else None
            ),
            "most_data_produced": (
                max(relevant_tasks.values(), key=lambda t: t.output_size).task_name
                if relevant_tasks
                else None
            ),
            "system_load": self.get_system_load_summary(),
        }

        # Generate success summary message
        if successful_tasks > 0:
            stats["success_summary"] = {
                "message": f"✅ {successful_tasks}/{total_tasks} tasks completed successfully",
                "details": f"Generated {stats['overall_stats']['data_processed_mb']:.2f} MB of data in {stats['overall_stats']['total_duration']:.1f} seconds",
                "recommendations": self.generate_performance_recommendations(
                    stats["overall_stats"]
                ),
            }
        elif failed_tasks > 0:
            stats["success_summary"] = {
                "message": f"❌ {failed_tasks}/{total_tasks} tasks failed",
                "details": "Check error logs for detailed failure information",
                "recommendations": [
                    "Review error logs",
                    "Check system resources",
                    "Verify data dependencies",
                ],
            }
        else:
            stats["success_summary"] = {
                "message": f"⏳ {running_tasks} tasks currently running",
                "details": "Tasks are being processed...",
                "recommendations": [
                    "Monitor progress in real-time",
                    "Check system performance",
                ],
            }

        # Cache the stats
        self.stats_cache[task_name or "all"] = stats

        return stats

    def generate_performance_recommendations(self, stats: Dict) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        if stats["success_rate"] < 90:
            recommendations.append(
                "Consider reviewing failed tasks and system dependencies"
            )

        if stats["average_duration"] > 300:  # 5 minutes
            recommendations.append(
                "Tasks taking longer than expected - consider system optimization"
            )

        if stats["data_processed_mb"] > 1000:  # 1GB
            recommendations.append(
                "Large data volumes processed - consider archiving older results"
            )

        if not recommendations:
            recommendations.append("System performing optimally")

        return recommendations

    def get_system_load_summary(self) -> Dict[str, float]:
        """Get current system load summary"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
            }
        except Exception:
            return {"cpu_percent": 0, "memory_percent": 0, "disk_percent": 0}

    def save_metrics_report(self) -> str:
        """Save comprehensive metrics report to file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.logger.log_dir / f"pipeline_report_{timestamp}.json"

        try:
            metrics = self.get_system_metrics()

            # Add summary information
            report = {
                "report_timestamp": datetime.now().isoformat(),
                "pipeline_summary": self.get_pipeline_summary(),
                "detailed_metrics": metrics,
                "available_tasks": self.available_tasks,
            }

            with open(report_file, "w") as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.pipeline_logger.info(f"📄 Metrics report saved: {report_file}")

            return str(report_file)

        except Exception as e:
            self.logger.error_logger.error(f"Failed to save metrics report: {e}")
            return f"ERROR: {e}"

    def shutdown(self):
        """Graceful shutdown of monitoring system"""

        self.logger.pipeline_logger.info("🛑 Pipeline monitor shutting down...")

        # Complete any running tasks
        for task_id, task in self.tasks.items():
            if task.status == "running":
                task.complete("interrupted", "Monitor shutdown")

        # Save final report
        self.save_metrics_report()

        self.logger.pipeline_logger.info("✅ Pipeline monitor shutdown complete")


# CLI Interface
async def main():
    """Main CLI interface for pipeline monitoring"""

    monitor = EnhancedPipelineMonitor()

    if len(sys.argv) < 2:
        print("🏇 Enhanced Pipeline Monitor - Available Commands:")
        print("=" * 50)
        print("python3 enhanced_pipeline_monitor.py <command> [args]")
        print()
        print("Commands:")
        print("  status          - Show current pipeline status")
        print("  metrics         - Display system metrics")
        print("  tasks           - List available tasks")
        print("  run <task>      - Execute a specific task")
        print("  report          - Generate comprehensive report")
        print("  monitor         - Start continuous monitoring")
        print()
        print("Example:")
        print("  python3 enhanced_pipeline_monitor.py run ml_training")
        print("  python3 enhanced_pipeline_monitor.py run fast_results")
        return

    command = sys.argv[1].lower()

    if command == "status":
        print(monitor.get_pipeline_summary())

    elif command == "metrics":
        metrics = monitor.get_system_metrics()
        print(json.dumps(metrics, indent=2, default=str))

    elif command == "tasks":
        print("🎯 Available Pipeline Tasks:")
        print("=" * 40)
        for task_name, config in monitor.available_tasks.items():
            print(f"• {task_name}")
            print(f"  Description: {config['description']}")
            print(f"  Category: {config['category']}")
            print(f"  Estimated Duration: {config['estimated_duration']}s")
            print()

    elif command == "run" and len(sys.argv) > 2:
        task_name = sys.argv[2]
        print(f"🚀 Executing task: {task_name}")
        result = await monitor.start_task(task_name)
        print(result)

    elif command == "report":
        report_file = monitor.save_metrics_report()
        print(f"📄 Report saved: {report_file}")

    elif command == "stats":
        task_name = sys.argv[2] if len(sys.argv) > 2 else None
        stats = monitor.generate_task_statistics(task_name)
        print(json.dumps(stats, indent=2))

    elif command == "monitor":
        print("🔍 Starting continuous monitoring (Ctrl+C to stop)...")
        try:
            while True:
                monitor.get_system_metrics()
                await asyncio.sleep(30)  # Update every 30 seconds
        except KeyboardInterrupt:
            monitor.shutdown()

    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python3 enhanced_pipeline_monitor.py' for help")


if __name__ == "__main__":
    asyncio.run(main())
