#!/usr/bin/env python3
"""
🚀 Event-Driven Pipeline Orchestrator - Phase 1 Implementation
Enhanced orchestrator with file watchers and completion events

This extends the daily orchestrator with:
- File system monitoring for download completion
- Stage completion events for dependency management
- Conditional triggers based on data quality
- Resource-aware scheduling for optimal performance

Author: AI Assistant
Date: August 17, 2025
"""

import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional

import psutil

# Import the existing orchestrator
from daily_orchestrator import DailyPipelineOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineEvent:
    """Represents a pipeline event"""

    def __init__(
        self, stage_name: str, event_type: str, success: bool = True, data: Dict = None
    ):
        self.stage_name = stage_name
        self.event_type = event_type  # "stage_start", "stage_complete", "stage_error"
        self.success = success
        self.data = data or {}
        self.timestamp = datetime.now()


class EventBus:
    """Event bus for stage communication"""

    def __init__(self):
        self.events = []
        self.listeners = {}

    def emit(self, event: PipelineEvent):
        """Emit an event"""
        self.events.append(event)
        event_key = f"{event.stage_name}_{event.event_type}"

        logger.info(
            f"📡 Event: {event.stage_name} -> {event.event_type} (success={event.success})"
        )

        if event_key in self.listeners:
            for callback in self.listeners[event_key]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Event callback failed: {e}")

    def listen(self, stage_name: str, event_type: str, callback: Callable):
        """Listen for events"""
        event_key = f"{stage_name}_{event_type}"
        if event_key not in self.listeners:
            self.listeners[event_key] = []
        self.listeners[event_key].append(callback)


class FileWatcher:
    """File system monitoring for pipeline triggers"""

    def __init__(self, watch_paths: List[str]):
        self.watch_paths = [Path(p) for p in watch_paths]
        self.file_callbacks = {}
        self.last_seen = {}
        self.is_monitoring = False
        self.monitor_thread = None

    def add_trigger(self, pattern: str, callback: Callable):
        """Add file pattern trigger"""
        self.file_callbacks[pattern] = callback
        logger.info(f"📁 Added file trigger: {pattern}")

    def start_monitoring(self, interval: int = 10):
        """Start file monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, args=(interval,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info(f"👁️ File monitoring started (checking every {interval}s)")

    def stop_monitoring(self):
        """Stop file monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def _monitor_loop(self, interval: int):
        """File monitoring loop"""
        while self.is_monitoring:
            try:
                self._check_for_changes()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"File monitor error: {e}")
                time.sleep(interval)

    def _check_for_changes(self):
        """Check for file changes"""
        for watch_path in self.watch_paths:
            if not watch_path.exists():
                continue

            # Get current files
            current_files = []
            try:
                current_files = list(watch_path.rglob("*"))
            except Exception as e:
                logger.error(f"Error scanning {watch_path}: {e}")
                continue

            # Compare with last seen
            last_files = self.last_seen.get(str(watch_path), [])
            new_files = set(current_files) - set(last_files)

            # Check new files against patterns
            for new_file in new_files:
                self._handle_new_file(new_file)

            self.last_seen[str(watch_path)] = current_files

    def _handle_new_file(self, file_path: Path):
        """Handle new file detection"""
        for pattern, callback in self.file_callbacks.items():
            if pattern in str(file_path):
                logger.info(f"🔔 File trigger: {pattern} detected -> {file_path.name}")
                try:
                    callback(file_path)
                except Exception as e:
                    logger.error(f"File trigger callback failed: {e}")


class ConditionalTrigger:
    """Conditional trigger system for stages"""

    def __init__(self, stage_name: str):
        self.stage_name = stage_name
        self.conditions = {}
        self.dependencies = []

    def add_condition(self, name: str, check_func: Callable[[], bool]):
        """Add a condition check"""
        self.conditions[name] = check_func

    def add_dependency(self, stage_name: str):
        """Add stage dependency"""
        self.dependencies.append(stage_name)

    def can_trigger(self, completed_stages: set) -> bool:
        """Check if stage can be triggered"""
        # Check dependencies
        for dep in self.dependencies:
            if dep not in completed_stages:
                logger.debug(f"❌ {self.stage_name} waiting for dependency: {dep}")
                return False

        # Check conditions
        for condition_name, check_func in self.conditions.items():
            try:
                if not check_func():
                    logger.debug(
                        f"❌ {self.stage_name} condition failed: {condition_name}"
                    )
                    return False
            except Exception as e:
                logger.error(
                    f"❌ {self.stage_name} condition error: {condition_name} - {e}"
                )
                return False

        return True


class EventDrivenOrchestrator(DailyPipelineOrchestrator):
    """Enhanced orchestrator with event-driven capabilities"""

    def __init__(self):
        super().__init__()

        # Event system
        self.event_bus = EventBus()

        # File monitoring
        self.file_watcher = FileWatcher(
            [
                str(self.project_root / "data" / "daily_downloads"),
                str(self.project_root / "data" / "results"),
            ]
        )

        # Stage tracking
        self.completed_stages = set()
        self.active_stages = set()
        self.stage_triggers = {}

        # Setup triggers
        self._setup_stage_triggers()
        self._setup_file_triggers()
        self._setup_event_listeners()

    def _setup_stage_triggers(self):
        """Setup conditional triggers for each stage"""

        # Data validation trigger
        data_validation = ConditionalTrigger("data_validation")
        data_validation.add_dependency("data_download")
        data_validation.add_condition(
            "files_present", self._check_download_files_present
        )
        data_validation.add_condition("files_valid", self._check_file_sizes_valid)
        self.stage_triggers["data_validation"] = data_validation

        # Data preprocessing trigger
        data_preprocessing = ConditionalTrigger("data_preprocessing")
        data_preprocessing.add_dependency("data_validation")
        data_preprocessing.add_condition("quality_check", self._check_data_quality)
        self.stage_triggers["data_preprocessing"] = data_preprocessing

        # ML training trigger
        ml_training = ConditionalTrigger("ml_model_training")
        ml_training.add_dependency("feature_engineering")
        ml_training.add_condition("time_window", self._check_ml_time_window)
        ml_training.add_condition("resources", self._check_system_resources)
        self.stage_triggers["ml_model_training"] = ml_training

        # Monte Carlo trigger
        monte_carlo = ConditionalTrigger("monte_carlo_simulations")
        monte_carlo.add_dependency("composite_scoring")
        monte_carlo.add_condition("resources", self._check_computational_resources)
        self.stage_triggers["monte_carlo_simulations"] = monte_carlo

        # Pre-race updates trigger
        prerace = ConditionalTrigger("pre_race_updates")
        prerace.add_dependency("report_generation")
        prerace.add_condition("time_proximity", self._check_race_proximity)
        self.stage_triggers["pre_race_updates"] = prerace

    def _setup_file_triggers(self):
        """Setup file system triggers"""

        # Download completion triggers
        self.file_watcher.add_trigger("races.csv", self._on_races_file_detected)
        self.file_watcher.add_trigger("horses.csv", self._on_horses_file_detected)
        self.file_watcher.add_trigger(
            "racecard_details.csv", self._on_racecard_file_detected
        )

        # Results triggers
        self.file_watcher.add_trigger("results_", self._on_results_file_detected)

    def _setup_event_listeners(self):
        """Setup event listeners for stage completion"""

        # Listen for stage completions to trigger downstream stages
        self.event_bus.listen(
            "data_download", "stage_complete", self._on_download_complete
        )
        self.event_bus.listen(
            "data_validation", "stage_complete", self._on_validation_complete
        )
        self.event_bus.listen(
            "data_preprocessing", "stage_complete", self._on_preprocessing_complete
        )
        self.event_bus.listen(
            "feature_engineering",
            "stage_complete",
            self._on_feature_engineering_complete,
        )
        self.event_bus.listen(
            "ml_model_training", "stage_complete", self._on_ml_training_complete
        )

    # File detection callbacks
    def _on_races_file_detected(self, file_path: Path):
        """Handle races.csv detection"""
        logger.info(f"🏇 Races file detected: {file_path}")
        self._mark_stage_complete(
            "data_download", {"trigger": "file_detection", "file": str(file_path)}
        )

    def _on_horses_file_detected(self, file_path: Path):
        """Handle horses.csv detection"""
        logger.info(f"🐎 Horses file detected: {file_path}")
        # Additional validation could be added here

    def _on_racecard_file_detected(self, file_path: Path):
        """Handle racecard_details.csv detection"""
        logger.info(f"📋 Racecard file detected: {file_path}")
        # Could trigger specific racecard processing

    def _on_results_file_detected(self, file_path: Path):
        """Handle results file detection"""
        logger.info(f"🏆 Results file detected: {file_path}")
        self.try_trigger_stage("results_analysis", {"results_file": str(file_path)})

    # Event callbacks
    def _on_download_complete(self, event: PipelineEvent):
        """Handle download completion"""
        logger.info("📥 Download complete - checking validation trigger")
        self.try_trigger_stage("data_validation")

    def _on_validation_complete(self, event: PipelineEvent):
        """Handle validation completion"""
        logger.info("✅ Validation complete - checking preprocessing trigger")
        self.try_trigger_stage("data_preprocessing")

    def _on_preprocessing_complete(self, event: PipelineEvent):
        """Handle preprocessing completion"""
        logger.info("🔄 Preprocessing complete - checking feature engineering trigger")
        self.try_trigger_stage("feature_engineering")

    def _on_feature_engineering_complete(self, event: PipelineEvent):
        """Handle feature engineering completion"""
        logger.info("🧠 Feature engineering complete - checking ML training trigger")
        self.try_trigger_stage("ml_model_training")

    def _on_ml_training_complete(self, event: PipelineEvent):
        """Handle ML training completion"""
        logger.info("🤖 ML training complete - checking downstream triggers")
        # Could trigger multiple stages in parallel
        self.try_trigger_stage("monte_carlo_simulations")
        self.try_trigger_stage("composite_scoring")

    # Condition check functions
    def _check_download_files_present(self) -> bool:
        """Check if download files are present"""
        required_files = [
            "data/daily_downloads/cards_data/races/races.csv",
            "data/daily_downloads/cards_data/horses/horses.csv",
        ]

        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return False
        return True

    def _check_file_sizes_valid(self) -> bool:
        """Check if files have reasonable sizes"""
        files_to_check = [
            "data/daily_downloads/cards_data/races/races.csv",
            "data/daily_downloads/cards_data/horses/horses.csv",
        ]

        for file_path in files_to_check:
            full_path = self.project_root / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                if size < 100:  # Very small file might indicate error
                    return False
        return True

    def _check_data_quality(self) -> bool:
        """Check data quality metrics"""
        # Placeholder - would implement actual quality checks
        return True

    def _check_ml_time_window(self) -> bool:
        """Check if in optimal ML training window"""
        current_hour = datetime.now().hour
        # Early morning window: 00:30 - 04:00
        return 0 <= current_hour <= 4 or current_hour >= 23

    def _check_system_resources(self) -> bool:
        """Check if system resources are available"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            return cpu_usage < 80 and memory_usage < 80
        except Exception:
            return True  # Assume OK if can't check

    def _check_computational_resources(self) -> bool:
        """Check if computational resources are available"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            # More strict requirements for Monte Carlo
            return cpu_usage < 60 and memory_usage < 70
        except Exception:
            return True

    def _check_race_proximity(self) -> bool:
        """Check if close to race time"""
        # Placeholder - would check actual race schedule
        current_time = datetime.now()
        # Assume races start at 13:00, stop updates 15 minutes before
        race_start = current_time.replace(hour=13, minute=0, second=0)
        cutoff_time = race_start - timedelta(minutes=15)
        return current_time < cutoff_time

    def try_trigger_stage(self, stage_name: str, trigger_data: Dict = None) -> bool:
        """Attempt to trigger a stage if conditions are met"""

        # Check if already active
        if stage_name in self.active_stages:
            logger.debug(f"⏸️ {stage_name} already active")
            return False

        # Check if already completed
        if stage_name in self.completed_stages:
            logger.debug(f"✅ {stage_name} already completed")
            return False

        # Check trigger conditions
        trigger = self.stage_triggers.get(stage_name)
        if trigger and not trigger.can_trigger(self.completed_stages):
            return False

        # All checks passed - trigger stage
        logger.info(f"🚀 Triggering stage: {stage_name}")
        self._execute_stage(stage_name, trigger_data)
        return True

    def _execute_stage(self, stage_name: str, trigger_data: Dict = None):
        """Execute a pipeline stage"""
        self.active_stages.add(stage_name)

        # Emit start event
        start_event = PipelineEvent(stage_name, "stage_start", data=trigger_data)
        self.event_bus.emit(start_event)

        # Run in thread to avoid blocking
        thread = threading.Thread(
            target=self._run_stage_thread, args=(stage_name, trigger_data)
        )
        thread.daemon = True
        thread.start()

    def _run_stage_thread(self, stage_name: str, trigger_data: Dict = None):
        """Run stage in separate thread"""
        try:
            logger.info(f"▶️ Executing {stage_name}")
            start_time = time.time()

            # Map to actual stage methods
            stage_methods = {
                "data_validation": self.validate_downloaded_data,
                "data_preprocessing": self.process_data_relationships,
                "feature_engineering": self.generate_contextual_analysis,
                "ml_model_training": self.train_ml_models,
                "monte_carlo_simulations": self.run_monte_carlo_analysis,
                "composite_scoring": self.calculate_composite_scores,
                "betting_strategies": self.generate_betting_strategies,
                "ai_selections": self.generate_ai_selections,
                "report_generation": self.generate_reports,
                "pre_race_updates": self.update_prerace_data,
                "results_analysis": self._run_results_analysis,
            }

            # Execute stage method
            method = stage_methods.get(stage_name)
            if method:
                result = (
                    asyncio.run(method())
                    if asyncio.iscoroutinefunction(method)
                    else method()
                )
                success = (
                    result.get("success", True) if isinstance(result, dict) else True
                )
            else:
                logger.warning(f"No method found for stage: {stage_name}")
                success = False

            execution_time = time.time() - start_time

            if success:
                self._mark_stage_complete(
                    stage_name,
                    {"execution_time": execution_time, "trigger_data": trigger_data},
                )
            else:
                logger.error(f"❌ {stage_name} failed")
                error_event = PipelineEvent(stage_name, "stage_error", success=False)
                self.event_bus.emit(error_event)

        except Exception as e:
            logger.error(f"💥 {stage_name} exception: {e}")
            error_event = PipelineEvent(
                stage_name, "stage_error", success=False, data={"error": str(e)}
            )
            self.event_bus.emit(error_event)

        finally:
            self.active_stages.discard(stage_name)

    def _mark_stage_complete(self, stage_name: str, result_data: Dict = None):
        """Mark stage as complete and emit event"""
        self.completed_stages.add(stage_name)

        logger.info(f"✅ {stage_name} completed")

        complete_event = PipelineEvent(
            stage_name, "stage_complete", success=True, data=result_data
        )
        self.event_bus.emit(complete_event)

    def _run_results_analysis(self):
        """Run results analysis"""
        logger.info("🏆 Running results analysis")
        time.sleep(2)  # Simulate processing
        return {"success": True, "records_processed": 100}

    def start_event_driven_pipeline(self):
        """Start the event-driven pipeline system"""
        logger.info("🚀 Starting Event-Driven Pipeline System")

        # Start file monitoring
        self.file_watcher.start_monitoring()

        # Start periodic trigger checks
        trigger_thread = threading.Thread(target=self._trigger_check_loop)
        trigger_thread.daemon = True
        trigger_thread.start()

        logger.info("✅ Event-driven pipeline system started")

        # Simulate initial download completion if files already exist
        if self._check_download_files_present():
            logger.info("📁 Existing files detected - triggering pipeline")
            self._mark_stage_complete("data_download", {"trigger": "existing_files"})

    def _trigger_check_loop(self):
        """Periodic trigger condition checking"""
        while True:
            try:
                # Check time-sensitive stages
                time_sensitive = ["ml_model_training", "pre_race_updates"]

                for stage in time_sensitive:
                    if (
                        stage not in self.completed_stages
                        and stage not in self.active_stages
                    ):
                        self.try_trigger_stage(stage)

                time.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Trigger check error: {e}")
                time.sleep(60)

    def get_pipeline_status(self) -> Dict:
        """Get current pipeline status"""
        return {
            "completed_stages": list(self.completed_stages),
            "active_stages": list(self.active_stages),
            "total_events": len(self.event_bus.events),
            "file_patterns_monitored": len(self.file_watcher.file_callbacks),
            "timestamp": datetime.now().isoformat(),
        }

    def shutdown(self):
        """Shutdown the orchestrator"""
        logger.info("🛑 Shutting down event-driven orchestrator")
        self.file_watcher.stop_monitoring()


def main():
    """Main function to test the event-driven orchestrator"""
    print("🚀 Event-Driven Pipeline Orchestrator - Phase 1")
    print("=" * 60)

    orchestrator = EventDrivenOrchestrator()

    try:
        # Start the system
        orchestrator.start_event_driven_pipeline()

        # Monitor for 60 seconds
        for i in range(60):
            status = orchestrator.get_pipeline_status()
            completed = len(status["completed_stages"])
            active = len(status["active_stages"])

            print(
                f"\r⏱️  {i+1:2d}s | Completed: {completed} | Active: {active} | Events: {status['total_events']}",
                end="",
                flush=True,
            )
            time.sleep(1)

        print(f"\n\n📊 Final Status:")
        final_status = orchestrator.get_pipeline_status()
        print(f"✅ Completed: {final_status['completed_stages']}")
        print(f"⚡ Active: {final_status['active_stages']}")
        print(f"📝 Events: {final_status['total_events']}")
        print(f"👁️  File patterns: {final_status['file_patterns_monitored']}")

    finally:
        orchestrator.shutdown()


if __name__ == "__main__":
    main()
