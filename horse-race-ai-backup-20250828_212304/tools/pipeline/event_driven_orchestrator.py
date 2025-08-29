#!/usr/bin/env python3
"""
🚀 Event-Driven Pipeline Trigger System
Enhanced orchestration with intelligent event-based triggering

This system replaces time-based sequential triggers with intelligent
event-driven orchestration for optimal pipeline performance.

Author: AI Assistant
Date: December 2024
"""

import asyncio
import json
import logging
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional

import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Types of pipeline triggers"""

    TIME_BASED = "time_based"
    EVENT_DRIVEN = "event_driven"
    CONDITION_BASED = "condition_based"
    RESOURCE_AWARE = "resource_aware"
    DEPENDENCY_BASED = "dependency_based"


@dataclass
class TriggerCondition:
    """Individual trigger condition"""

    name: str
    check_function: Callable
    threshold: Optional[float] = None
    required: bool = True
    description: str = ""


@dataclass
class StageEvent:
    """Pipeline stage event"""

    stage_name: str
    event_type: str  # "started", "completed", "failed"
    timestamp: datetime
    data: Dict = None
    success: bool = True
    metrics: Dict = None


class EventBus:
    """Simple event bus for inter-stage communication"""

    def __init__(self):
        self.subscribers = {}
        self.event_log = []

    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event: StageEvent):
        """Publish event to subscribers"""
        self.event_log.append(event)
        event_key = f"{event.stage_name}_{event.event_type}"

        if event_key in self.subscribers:
            for callback in self.subscribers[event_key]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Event callback failed: {e}")


class ResourceMonitor:
    """Monitor system resources for intelligent triggering"""

    def __init__(self):
        self.thresholds = {
            "cpu": 80.0,  # Percentage
            "memory": 80.0,  # Percentage
            "disk_io": 70.0,  # Percentage
        }

    def get_current_usage(self) -> Dict[str, float]:
        """Get current system resource usage"""
        return {
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
            "disk_io": self._get_disk_io_percent(),
            "available_cores": psutil.cpu_count(),
            "available_memory_gb": psutil.virtual_memory().available / (1024**3),
        }

    def _get_disk_io_percent(self) -> float:
        """Estimate disk I/O usage percentage"""
        try:
            io_stats = psutil.disk_io_counters()
            if hasattr(self, "_last_io_stats"):
                # Calculate I/O rate (simplified)
                read_rate = io_stats.read_bytes - self._last_io_stats.read_bytes
                write_rate = io_stats.write_bytes - self._last_io_stats.write_bytes
                total_rate = (read_rate + write_rate) / (1024 * 1024)  # MB/s
                # Rough approximation: >100MB/s = high usage
                return min(total_rate / 100 * 100, 100)
            else:
                self._last_io_stats = io_stats
                return 0.0
        except Exception:
            return 0.0

    def resources_available_for_stage(self, stage_requirements: Dict) -> bool:
        """Check if resources are available for stage execution"""
        current = self.get_current_usage()

        cpu_ok = current["cpu"] < self.thresholds["cpu"]
        memory_ok = current["memory"] < self.thresholds["memory"]
        io_ok = current["disk_io"] < self.thresholds["disk_io"]

        # Check stage-specific requirements
        if "min_memory_gb" in stage_requirements:
            min_memory = stage_requirements["min_memory_gb"]
            memory_ok = memory_ok and current["available_memory_gb"] >= min_memory

        if "min_cpu_cores" in stage_requirements:
            min_cores = stage_requirements["min_cpu_cores"]
            cpu_ok = cpu_ok and current["available_cores"] >= min_cores

        return cpu_ok and memory_ok and io_ok


class FileWatcher:
    """Watch for file system events to trigger pipeline stages"""

    def __init__(self, watch_directories: List[str]):
        self.watch_directories = watch_directories
        self.callbacks = {}
        self.last_check = {}

    def add_file_trigger(self, pattern: str, callback: Callable):
        """Add file pattern trigger"""
        self.callbacks[pattern] = callback

    def check_for_new_files(self):
        """Check for new files (simple polling implementation)"""
        for directory in self.watch_directories:
            dir_path = Path(directory)
            if not dir_path.exists():
                continue

            # Get current files
            current_files = set(dir_path.rglob("*"))
            last_files = self.last_check.get(directory, set())

            # Check for new files
            new_files = current_files - last_files

            for new_file in new_files:
                self._handle_new_file(new_file)

            self.last_check[directory] = current_files

    def _handle_new_file(self, file_path: Path):
        """Handle new file detection"""
        for pattern, callback in self.callbacks.items():
            if pattern in str(file_path):
                logger.info(f"🔍 File trigger: {file_path} matches {pattern}")
                callback(file_path)


class StageTrigger:
    """Base class for stage-specific triggers"""

    def __init__(self, stage_name: str):
        self.stage_name = stage_name
        self.conditions = []
        self.dependencies = []
        self.resource_requirements = {}

    def add_condition(self, condition: TriggerCondition):
        """Add trigger condition"""
        self.conditions.append(condition)

    def add_dependency(self, stage_name: str):
        """Add stage dependency"""
        self.dependencies.append(stage_name)

    def set_resource_requirements(self, requirements: Dict):
        """Set resource requirements"""
        self.resource_requirements = requirements

    def can_trigger(
        self, completed_stages: set, resource_monitor: ResourceMonitor
    ) -> Dict:
        """Check if stage can be triggered"""
        result = {
            "can_trigger": True,
            "reasons": [],
            "conditions_met": {},
            "dependencies_met": True,
            "resources_available": True,
        }

        # Check dependencies
        missing_deps = set(self.dependencies) - completed_stages
        if missing_deps:
            result["can_trigger"] = False
            result["dependencies_met"] = False
            result["reasons"].append(f"Missing dependencies: {missing_deps}")

        # Check conditions
        for condition in self.conditions:
            try:
                condition_result = condition.check_function()
                result["conditions_met"][condition.name] = condition_result

                if condition.required and not condition_result:
                    result["can_trigger"] = False
                    result["reasons"].append(
                        f"Required condition not met: {condition.name}"
                    )

            except Exception as e:
                logger.error(f"Condition check failed for {condition.name}: {e}")
                if condition.required:
                    result["can_trigger"] = False
                    result["reasons"].append(
                        f"Condition check failed: {condition.name}"
                    )

        # Check resources
        if not resource_monitor.resources_available_for_stage(
            self.resource_requirements
        ):
            result["can_trigger"] = False
            result["resources_available"] = False
            result["reasons"].append("Insufficient system resources")

        return result


class EventDrivenPipelineOrchestrator:
    """Enhanced pipeline orchestrator with event-driven triggers"""

    def __init__(self):
        self.event_bus = EventBus()
        self.resource_monitor = ResourceMonitor()
        self.file_watcher = FileWatcher(
            [
                "/home/jc/Documents/Horse-race-ai-v2.02/data/daily_downloads",
                "/home/jc/Documents/Horse-race-ai-v2.02/data/uploads",
            ]
        )

        self.stage_triggers = {}
        self.completed_stages = set()
        self.active_stages = set()
        self.stage_results = {}

        self.setup_triggers()
        self.setup_file_watchers()

    def setup_triggers(self):
        """Setup stage-specific triggers"""

        # Data Validation Trigger
        validation_trigger = StageTrigger("data_validation")
        validation_trigger.add_condition(
            TriggerCondition(
                "files_present",
                self._check_download_files_present,
                description="Check if download files are present",
            )
        )
        validation_trigger.add_condition(
            TriggerCondition(
                "file_sizes_valid",
                self._check_file_sizes_valid,
                description="Validate file sizes are reasonable",
            )
        )
        validation_trigger.add_dependency("data_download")
        self.stage_triggers["data_validation"] = validation_trigger

        # Data Preprocessing Trigger
        preprocessing_trigger = StageTrigger("data_preprocessing")
        preprocessing_trigger.add_condition(
            TriggerCondition(
                "validation_passed",
                lambda: self._check_stage_success("data_validation"),
                description="Data validation completed successfully",
            )
        )
        preprocessing_trigger.add_dependency("data_validation")
        preprocessing_trigger.set_resource_requirements({"min_memory_gb": 2.0})
        self.stage_triggers["data_preprocessing"] = preprocessing_trigger

        # ML Training Trigger (Early Morning)
        ml_trigger = StageTrigger("ml_model_training")
        ml_trigger.add_condition(
            TriggerCondition(
                "time_window_available",
                self._check_ml_training_time_window,
                description="Check if in early morning training window",
            )
        )
        ml_trigger.add_condition(
            TriggerCondition(
                "training_data_sufficient",
                self._check_training_data_sufficient,
                description="Check if sufficient training data available",
            )
        )
        ml_trigger.add_dependency("feature_engineering")
        ml_trigger.set_resource_requirements({"min_memory_gb": 4.0, "min_cpu_cores": 2})
        self.stage_triggers["ml_model_training"] = ml_trigger

        # Monte Carlo Trigger
        mc_trigger = StageTrigger("monte_carlo_simulations")
        mc_trigger.add_condition(
            TriggerCondition(
                "analytics_complete",
                self._check_analytics_stages_complete,
                description="All analytics stages completed",
            )
        )
        mc_trigger.add_condition(
            TriggerCondition(
                "race_data_finalized",
                self._check_race_data_finalized,
                description="Race data is finalized and ready",
            )
        )
        mc_trigger.set_resource_requirements({"min_memory_gb": 3.0, "min_cpu_cores": 4})
        self.stage_triggers["monte_carlo_simulations"] = mc_trigger

        # Pre-race Updates Trigger (Time-sensitive)
        prerace_trigger = StageTrigger("pre_race_updates")
        prerace_trigger.add_condition(
            TriggerCondition(
                "time_before_race",
                self._check_time_before_race,
                description="Check time remaining before race",
            )
        )
        prerace_trigger.add_condition(
            TriggerCondition(
                "live_data_available",
                self._check_live_data_available,
                description="Live race data is available",
            )
        )
        self.stage_triggers["pre_race_updates"] = prerace_trigger

    def setup_file_watchers(self):
        """Setup file system watchers"""

        # Watch for download completion
        self.file_watcher.add_file_trigger(
            "races.csv",
            lambda file_path: self.trigger_stage(
                "data_validation", {"trigger_file": str(file_path)}
            ),
        )

        # Watch for results files
        self.file_watcher.add_file_trigger(
            "results_",
            lambda file_path: self.trigger_stage(
                "results_analysis", {"results_file": str(file_path)}
            ),
        )

    def trigger_stage(self, stage_name: str, trigger_data: Dict = None):
        """Trigger a pipeline stage if conditions are met"""
        if stage_name in self.active_stages:
            logger.info(f"⏸️ Stage {stage_name} already active, skipping trigger")
            return False

        if stage_name not in self.stage_triggers:
            logger.warning(f"⚠️ No trigger defined for stage {stage_name}")
            return False

        trigger = self.stage_triggers[stage_name]
        check_result = trigger.can_trigger(self.completed_stages, self.resource_monitor)

        if check_result["can_trigger"]:
            logger.info(f"🚀 Triggering stage: {stage_name}")
            self._execute_stage(stage_name, trigger_data)
            return True
        else:
            logger.info(
                f"⏳ Cannot trigger {stage_name}: {', '.join(check_result['reasons'])}"
            )
            return False

    def _execute_stage(self, stage_name: str, trigger_data: Dict = None):
        """Execute a pipeline stage"""
        self.active_stages.add(stage_name)

        # Publish stage started event
        start_event = StageEvent(
            stage_name=stage_name,
            event_type="started",
            timestamp=datetime.now(),
            data=trigger_data,
        )
        self.event_bus.publish(start_event)

        # Execute stage in separate thread
        thread = threading.Thread(
            target=self._run_stage_async, args=(stage_name, trigger_data)
        )
        thread.start()

    def _run_stage_async(self, stage_name: str, trigger_data: Dict = None):
        """Run stage asynchronously"""
        try:
            # Simulate stage execution (replace with actual stage logic)
            start_time = time.time()
            success = self._simulate_stage_execution(stage_name)
            execution_time = time.time() - start_time

            # Store results
            self.stage_results[stage_name] = {
                "success": success,
                "execution_time": execution_time,
                "trigger_data": trigger_data,
                "completed_at": datetime.now(),
            }

            if success:
                self.completed_stages.add(stage_name)

            # Publish completion event
            completion_event = StageEvent(
                stage_name=stage_name,
                event_type="completed" if success else "failed",
                timestamp=datetime.now(),
                success=success,
                metrics={"execution_time": execution_time},
            )
            self.event_bus.publish(completion_event)

            # Check for downstream triggers
            self._check_downstream_triggers(stage_name)

        except Exception as e:
            logger.error(f"❌ Stage {stage_name} execution failed: {e}")

        finally:
            self.active_stages.discard(stage_name)

    def _simulate_stage_execution(self, stage_name: str) -> bool:
        """Simulate stage execution (replace with actual implementation)"""
        import random

        execution_time = random.uniform(1, 5)  # Simulate work
        time.sleep(execution_time)
        return random.random() > 0.1  # 90% success rate

    def _check_downstream_triggers(self, completed_stage: str):
        """Check if any stages can now be triggered"""
        for stage_name, trigger in self.stage_triggers.items():
            if completed_stage in trigger.dependencies:
                logger.info(
                    f"🔍 Checking if {stage_name} can be triggered after {completed_stage}"
                )
                self.trigger_stage(stage_name)

    # Condition check methods
    def _check_download_files_present(self) -> bool:
        """Check if required download files are present"""
        required_files = [
            "data/daily_downloads/cards_data/races/races.csv",
            "data/daily_downloads/results_data/races/races.csv",
        ]
        return all(Path(f).exists() for f in required_files)

    def _check_file_sizes_valid(self) -> bool:
        """Check if file sizes are reasonable"""
        try:
            min_size = 1024  # 1KB minimum
            files_to_check = ["data/daily_downloads/cards_data/races/races.csv"]

            for file_path in files_to_check:
                if Path(file_path).exists():
                    size = Path(file_path).stat().st_size
                    if size < min_size:
                        return False
            return True
        except:
            return False

    def _check_stage_success(self, stage_name: str) -> bool:
        """Check if a stage completed successfully"""
        return stage_name in self.completed_stages and self.stage_results.get(
            stage_name, {}
        ).get("success", False)

    def _check_ml_training_time_window(self) -> bool:
        """Check if in optimal ML training time window"""
        current_hour = datetime.now().hour
        return 0 <= current_hour <= 4  # 00:00 - 04:00

    def _check_training_data_sufficient(self) -> bool:
        """Check if sufficient training data is available"""
        # Placeholder - would check actual data volumes
        return True

    def _check_analytics_stages_complete(self) -> bool:
        """Check if all analytics stages are complete"""
        analytics_stages = ["power_ratings", "speed_analysis", "form_scoring"]
        return all(stage in self.completed_stages for stage in analytics_stages)

    def _check_race_data_finalized(self) -> bool:
        """Check if race data is finalized"""
        # Placeholder - would check data completeness
        return True

    def _check_time_before_race(self) -> bool:
        """Check time remaining before first race"""
        # Placeholder - would check actual race times
        return True

    def _check_live_data_available(self) -> bool:
        """Check if live race data is available"""
        # Placeholder - would check live data feeds
        return True

    def start_monitoring(self):
        """Start the event-driven monitoring system"""
        logger.info("🚀 Starting event-driven pipeline orchestrator")

        # Start file watcher
        file_watch_thread = threading.Thread(target=self._file_watch_loop)
        file_watch_thread.daemon = True
        file_watch_thread.start()

        # Start resource monitoring
        resource_thread = threading.Thread(target=self._resource_monitor_loop)
        resource_thread.daemon = True
        resource_thread.start()

        logger.info("✅ Event-driven orchestrator started")

    def _file_watch_loop(self):
        """File watching loop"""
        while True:
            try:
                self.file_watcher.check_for_new_files()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"File watcher error: {e}")
                time.sleep(60)

    def _resource_monitor_loop(self):
        """Resource monitoring loop"""
        while True:
            try:
                usage = self.resource_monitor.get_current_usage()
                logger.debug(
                    f"💻 Resource usage: CPU {usage['cpu']:.1f}%, Memory {usage['memory']:.1f}%"
                )
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Resource monitor error: {e}")
                time.sleep(60)


def main():
    """Run the event-driven pipeline orchestrator"""
    orchestrator = EventDrivenPipelineOrchestrator()
    orchestrator.start_monitoring()

    # Example: Trigger initial stage
    orchestrator.trigger_stage("data_validation")

    try:
        while True:
            time.sleep(10)
            # Could add more sophisticated scheduling logic here
    except KeyboardInterrupt:
        logger.info("🛑 Event-driven orchestrator stopped")


if __name__ == "__main__":
    main()
