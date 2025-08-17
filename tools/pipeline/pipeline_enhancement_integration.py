#!/usr/bin/env python3
"""
🔧 Production Pipeline Integration - Event-Driven Triggers
Integration module to add event-driven capabilities to existing daily orchestrator

This module enhances the existing pipeline with:
- File monitoring for download completion detection
- Event-based stage triggering
- Conditional execution based on data quality and resources
- Intelligent scheduling and retry mechanisms

Author: AI Assistant
Date: August 17, 2025
"""

import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class PipelineEventManager:
    """Manages pipeline events and stage coordination"""

    def __init__(self):
        self.events = []
        self.stage_listeners = {}
        self.completion_callbacks = {}

    def on_stage_complete(self, stage_name: str, callback: Callable):
        """Register callback for stage completion"""
        if stage_name not in self.completion_callbacks:
            self.completion_callbacks[stage_name] = []
        self.completion_callbacks[stage_name].append(callback)

    def emit_stage_complete(self, stage_name: str, result: Dict = None):
        """Emit stage completion event"""
        event = {
            "stage": stage_name,
            "timestamp": datetime.now().isoformat(),
            "result": result or {},
            "event_type": "stage_complete",
        }
        self.events.append(event)

        logger.info(f"📡 Stage complete: {stage_name}")

        # Trigger callbacks
        if stage_name in self.completion_callbacks:
            for callback in self.completion_callbacks[stage_name]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Stage completion callback failed: {e}")


class FileMonitor:
    """File system monitoring for pipeline triggers"""

    def __init__(self, watch_directories: List[str]):
        self.watch_directories = [Path(d) for d in watch_directories]
        self.triggers = {}
        self.is_monitoring = False
        self.monitor_thread = None
        self.last_scan = {}

    def add_file_trigger(self, file_pattern: str, callback: Callable):
        """Add file trigger for specific patterns"""
        self.triggers[file_pattern] = callback
        logger.info(f"📁 Added file trigger: {file_pattern}")

    def start_monitoring(self, scan_interval: int = 30):
        """Start file monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, args=(scan_interval,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        logger.info(f"👁️ File monitoring started (scan every {scan_interval}s)")

    def stop_monitoring(self):
        """Stop file monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)

    def _monitoring_loop(self, scan_interval: int):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                self._scan_for_changes()
                time.sleep(scan_interval)
            except Exception as e:
                logger.error(f"File monitoring error: {e}")
                time.sleep(scan_interval)

    def _scan_for_changes(self):
        """Scan directories for file changes"""
        for watch_dir in self.watch_directories:
            if not watch_dir.exists():
                continue

            try:
                # Get all files recursively
                current_files = set()
                for item in watch_dir.rglob("*"):
                    if item.is_file():
                        current_files.add(str(item))

                # Compare with last scan
                dir_key = str(watch_dir)
                last_files = self.last_scan.get(dir_key, set())
                new_files = current_files - last_files

                # Check new files against triggers
                for new_file in new_files:
                    self._process_new_file(Path(new_file))

                self.last_scan[dir_key] = current_files

            except Exception as e:
                logger.error(f"Error scanning {watch_dir}: {e}")

    def _process_new_file(self, file_path: Path):
        """Process newly detected file"""
        for pattern, callback in self.triggers.items():
            if pattern in str(file_path):
                logger.info(f"🔔 File trigger: {pattern} -> {file_path.name}")
                try:
                    callback(file_path)
                except Exception as e:
                    logger.error(f"File trigger callback error: {e}")


class ConditionalStageRunner:
    """Manages conditional stage execution"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.conditions = {}
        self.dependencies = {}
        self.completed_stages = set()

    def add_stage_condition(
        self, stage_name: str, condition_name: str, check_func: Callable[[], bool]
    ):
        """Add condition for stage execution"""
        if stage_name not in self.conditions:
            self.conditions[stage_name] = {}
        self.conditions[stage_name][condition_name] = check_func

    def add_stage_dependency(self, stage_name: str, depends_on: List[str]):
        """Add stage dependencies"""
        self.dependencies[stage_name] = depends_on

    def can_run_stage(self, stage_name: str) -> bool:
        """Check if stage can run based on conditions and dependencies"""

        # Check dependencies
        stage_deps = self.dependencies.get(stage_name, [])
        for dep in stage_deps:
            if dep not in self.completed_stages:
                logger.debug(f"❌ {stage_name} waiting for dependency: {dep}")
                return False

        # Check conditions
        stage_conditions = self.conditions.get(stage_name, {})
        for condition_name, check_func in stage_conditions.items():
            try:
                if not check_func():
                    logger.debug(f"❌ {stage_name} condition failed: {condition_name}")
                    return False
            except Exception as e:
                logger.error(f"❌ {stage_name} condition error: {condition_name} - {e}")
                return False

        return True

    def mark_stage_complete(self, stage_name: str):
        """Mark stage as completed"""
        self.completed_stages.add(stage_name)
        logger.info(f"✅ Stage marked complete: {stage_name}")

    def try_run_stage(self, stage_name: str, method_name: str = None) -> bool:
        """Try to run stage if conditions are met"""
        if not self.can_run_stage(stage_name):
            return False

        logger.info(f"🚀 Running stage: {stage_name}")

        # Get method from orchestrator
        if method_name is None:
            method_name = stage_name.replace("_", "")

        if hasattr(self.orchestrator, method_name):
            try:
                method = getattr(self.orchestrator, method_name)
                result = method()

                if isinstance(result, dict) and result.get("success", True):
                    self.mark_stage_complete(stage_name)
                    return True
                else:
                    logger.error(f"❌ Stage failed: {stage_name}")
                    return False

            except Exception as e:
                logger.error(f"💥 Stage execution error: {stage_name} - {e}")
                return False
        else:
            logger.warning(f"⚠️ No method found for stage: {stage_name}")
            return False


class EventDrivenPipelineEnhancer:
    """Enhances existing pipeline orchestrator with event-driven capabilities"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.event_manager = PipelineEventManager()
        self.file_monitor = FileMonitor(
            [
                str(self.orchestrator.project_root / "data" / "daily_downloads"),
                str(self.orchestrator.project_root / "data" / "results"),
            ]
        )
        self.stage_runner = ConditionalStageRunner(orchestrator)

        self._setup_file_triggers()
        self._setup_stage_conditions()
        self._setup_stage_dependencies()
        self._setup_event_listeners()

    def _setup_file_triggers(self):
        """Setup file system triggers"""

        # Download completion triggers
        self.file_monitor.add_file_trigger(
            "races.csv", lambda f: self._on_download_file_detected("races", f)
        )
        self.file_monitor.add_file_trigger(
            "horses.csv", lambda f: self._on_download_file_detected("horses", f)
        )
        self.file_monitor.add_file_trigger(
            "racecard_details.csv",
            lambda f: self._on_download_file_detected("racecard", f),
        )

        # Results file triggers
        self.file_monitor.add_file_trigger(
            "upload_manifest.json", lambda f: self._on_upload_complete(f)
        )

    def _setup_stage_conditions(self):
        """Setup conditional execution rules"""

        # Data validation conditions
        self.stage_runner.add_stage_condition(
            "data_validation", "files_present", self._check_core_files_present
        )
        self.stage_runner.add_stage_condition(
            "data_validation", "file_sizes_valid", self._check_file_sizes_valid
        )

        # ML training conditions
        self.stage_runner.add_stage_condition(
            "ml_training", "time_window", self._check_ml_time_window
        )
        self.stage_runner.add_stage_condition(
            "ml_training", "system_resources", self._check_system_resources
        )

        # Pre-race conditions
        self.stage_runner.add_stage_condition(
            "pre_race_updates", "race_proximity", self._check_race_proximity
        )

    def _setup_stage_dependencies(self):
        """Setup stage dependency graph"""

        dependencies = {
            "data_validation": ["data_download"],
            "data_preprocessing": ["data_validation"],
            "feature_engineering": ["data_preprocessing"],
            "ml_training": ["feature_engineering"],
            "contextual_analysis": ["ml_training"],
            "form_scoring": ["contextual_analysis"],
            "power_ratings": ["contextual_analysis"],
            "speed_analysis": ["contextual_analysis"],
            "monte_carlo": ["form_scoring", "power_ratings", "speed_analysis"],
            "composite_scoring": ["monte_carlo"],
            "betting_strategies": ["composite_scoring"],
            "ai_selections": ["betting_strategies"],
            "report_generation": ["ai_selections"],
            "pre_race_updates": ["report_generation"],
        }

        for stage, deps in dependencies.items():
            self.stage_runner.add_stage_dependency(stage, deps)

    def _setup_event_listeners(self):
        """Setup event listeners for stage coordination"""

        # Download triggers validation
        self.event_manager.on_stage_complete(
            "data_download",
            lambda e: self.stage_runner.try_run_stage(
                "data_validation", "validate_downloaded_data"
            ),
        )

        # Validation triggers preprocessing
        self.event_manager.on_stage_complete(
            "data_validation",
            lambda e: self.stage_runner.try_run_stage(
                "data_preprocessing", "process_data_relationships"
            ),
        )

        # Preprocessing triggers feature engineering
        self.event_manager.on_stage_complete(
            "data_preprocessing",
            lambda e: self.stage_runner.try_run_stage(
                "feature_engineering", "generate_contextual_analysis"
            ),
        )

        # Feature engineering triggers ML training
        self.event_manager.on_stage_complete(
            "feature_engineering",
            lambda e: self.stage_runner.try_run_stage("ml_training", "train_ml_models"),
        )

    # File event handlers
    def _on_download_file_detected(self, file_type: str, file_path: Path):
        """Handle download file detection"""
        logger.info(f"📥 Download file detected: {file_type} -> {file_path.name}")

        # Check if all core files are present
        if self._check_core_files_present():
            logger.info(
                "🎯 All core files detected - triggering data_download completion"
            )
            self.event_manager.emit_stage_complete(
                "data_download",
                {
                    "trigger": "file_detection",
                    "file_type": file_type,
                    "file_path": str(file_path),
                },
            )

    def _on_upload_complete(self, file_path: Path):
        """Handle upload completion"""
        logger.info(f"📤 Upload manifest detected: {file_path.name}")
        # Could trigger additional processing or verification

    # Condition check methods
    def _check_core_files_present(self) -> bool:
        """Check if core download files are present"""
        required_files = [
            "data/daily_downloads/cards_data/races/races.csv",
            "data/daily_downloads/cards_data/horses/horses.csv",
            "data/daily_downloads/cards_data/racecard_details/racecard_details.csv",
        ]

        project_root = self.orchestrator.project_root
        for file_path in required_files:
            full_path = project_root / file_path
            if not full_path.exists():
                return False
        return True

    def _check_file_sizes_valid(self) -> bool:
        """Check if files have reasonable sizes (>1KB)"""
        required_files = [
            "data/daily_downloads/cards_data/races/races.csv",
            "data/daily_downloads/cards_data/horses/horses.csv",
        ]

        project_root = self.orchestrator.project_root
        for file_path in required_files:
            full_path = project_root / file_path
            if full_path.exists() and full_path.stat().st_size < 1024:
                return False
        return True

    def _check_ml_time_window(self) -> bool:
        """Check if in optimal ML training window (early morning)"""
        current_hour = datetime.now().hour
        return 0 <= current_hour <= 4 or current_hour >= 23

    def _check_system_resources(self) -> bool:
        """Check if system resources are available"""
        try:
            import psutil

            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            return cpu_usage < 80 and memory_usage < 80
        except ImportError:
            return True  # Assume OK if psutil not available

    def _check_race_proximity(self) -> bool:
        """Check if close to race time"""
        # Placeholder - would implement actual race schedule checking
        return True

    def start_enhanced_monitoring(self):
        """Start the enhanced event-driven monitoring"""
        logger.info("🚀 Starting enhanced pipeline monitoring")

        # Start file monitoring
        self.file_monitor.start_monitoring(scan_interval=30)

        # Check for existing files on startup
        if self._check_core_files_present():
            logger.info("📁 Existing files detected on startup")
            self.event_manager.emit_stage_complete(
                "data_download", {"trigger": "startup_detection"}
            )

        logger.info("✅ Enhanced monitoring started")

    def stop_enhanced_monitoring(self):
        """Stop enhanced monitoring"""
        logger.info("🛑 Stopping enhanced monitoring")
        self.file_monitor.stop_monitoring()

    def get_enhancement_status(self) -> Dict:
        """Get status of enhancement system"""
        return {
            "completed_stages": list(self.stage_runner.completed_stages),
            "total_events": len(self.event_manager.events),
            "file_triggers": len(self.file_monitor.triggers),
            "monitoring_active": self.file_monitor.is_monitoring,
            "timestamp": datetime.now().isoformat(),
        }


def enhance_orchestrator(orchestrator):
    """Add event-driven capabilities to existing orchestrator"""

    logger.info("🔧 Enhancing orchestrator with event-driven capabilities")

    # Create enhancer
    enhancer = EventDrivenPipelineEnhancer(orchestrator)

    # Add enhancement methods to orchestrator
    orchestrator.event_enhancer = enhancer
    orchestrator.start_enhanced_monitoring = enhancer.start_enhanced_monitoring
    orchestrator.stop_enhanced_monitoring = enhancer.stop_enhanced_monitoring
    orchestrator.get_enhancement_status = enhancer.get_enhancement_status

    # Override stage completion methods to emit events
    original_methods = {}

    stage_method_mapping = {
        "validate_downloaded_data": "data_validation",
        "process_data_relationships": "data_preprocessing",
        "generate_contextual_analysis": "feature_engineering",
        "train_ml_models": "ml_training",
    }

    for method_name, stage_name in stage_method_mapping.items():
        if hasattr(orchestrator, method_name):
            original_method = getattr(orchestrator, method_name)
            original_methods[method_name] = original_method

            # Create enhanced wrapper
            def create_enhanced_method(orig_method, stage):
                def enhanced_method(*args, **kwargs):
                    logger.info(f"🔄 Enhanced execution: {stage}")
                    result = orig_method(*args, **kwargs)

                    # Emit completion event if successful
                    if isinstance(result, dict) and result.get("success", True):
                        enhancer.event_manager.emit_stage_complete(stage, result)
                        enhancer.stage_runner.mark_stage_complete(stage)

                    return result

                return enhanced_method

            # Replace method with enhanced version
            setattr(
                orchestrator,
                method_name,
                create_enhanced_method(original_method, stage_name),
            )

    logger.info("✅ Orchestrator enhancement complete")
    return enhancer


def main():
    """Test the enhancement system"""
    print("🔧 Pipeline Enhancement System Test")
    print("=" * 50)

    # Mock orchestrator for testing
    class MockOrchestrator:
        def __init__(self):
            self.project_root = Path(__file__).parent.parent.parent

        def validate_downloaded_data(self):
            logger.info("🔍 Mock data validation")
            time.sleep(1)
            return {"success": True, "records": 1500}

        def process_data_relationships(self):
            logger.info("🔄 Mock data preprocessing")
            time.sleep(2)
            return {"success": True, "relationships": 250}

    # Create and enhance orchestrator
    orchestrator = MockOrchestrator()
    enhancer = enhance_orchestrator(orchestrator)

    try:
        # Start enhanced monitoring
        orchestrator.start_enhanced_monitoring()

        # Monitor for 30 seconds
        for i in range(30):
            status = orchestrator.get_enhancement_status()
            completed = len(status["completed_stages"])
            events = status["total_events"]

            print(
                f"\r⏱️  {i+1:2d}s | Completed: {completed} | Events: {events}",
                end="",
                flush=True,
            )
            time.sleep(1)

        print(f"\n\n📊 Final Status:")
        final_status = orchestrator.get_enhancement_status()
        print(f"✅ Completed: {final_status['completed_stages']}")
        print(f"📝 Events: {final_status['total_events']}")
        print(f"👁️  File triggers: {final_status['file_triggers']}")
        print(f"🔄 Monitoring: {final_status['monitoring_active']}")

    finally:
        orchestrator.stop_enhanced_monitoring()


if __name__ == "__main__":
    main()
