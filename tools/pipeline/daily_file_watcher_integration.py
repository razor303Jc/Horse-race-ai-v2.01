#!/usr/bin/env python3
"""
Daily File Watcher Pipeline Integration
Horse Racing AI v2.04 - Pipeline Integration

Integrates the daily file watcher with the existing pipeline orchestrator
to provide seamless event-driven data processing.
"""

import asyncio
import json
import logging
import sys
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Callable

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import existing pipeline components
try:
    from tools.pipeline.event_driven_orchestrator import EventBus, StageEvent
    from tools.pipeline.pipeline_enhancement_integration import (
        EventDrivenPipelineEnhancer,
    )
    from tools.automation.daily_file_watcher import DailyRacingFileWatcher
except ImportError as e:
    logging.error(f"Failed to import pipeline components: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DailyFileWatcherPipelineIntegration:
    """Integrates daily file watcher with pipeline orchestrator"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.04"):
        self.base_path = Path(base_path)
        self.project_root = self.base_path

        # Initialize components
        self.event_bus = EventBus()
        self.file_watcher = DailyRacingFileWatcher(str(base_path))
        self.pipeline_enhancer = None

        # Integration state
        self.integration_state = {
            "watcher_active": False,
            "pipeline_active": False,
            "last_files_processed": None,
            "pending_pipeline_triggers": [],
            "daily_completion_status": {},
        }

        # Setup event handlers
        self.setup_event_handlers()

        # Pipeline configuration
        self.pipeline_config = self.load_pipeline_config()

        logger.info("🔗 Daily File Watcher Pipeline Integration initialized")

    def load_pipeline_config(self) -> Dict[str, Any]:
        """Load pipeline configuration"""
        config_file = self.base_path / "config" / "daily_watcher_config.json"

        default_config = {
            "pipeline_integration": {
                "auto_trigger": True,
                "trigger_delay_seconds": 30,
                "validation_required": True,
                "stages_to_trigger": [
                    "data_validation",
                    "database_upload",
                    "relationship_analysis",
                    "ml_model_update",
                    "contextual_analysis",
                ],
            }
        }

        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                return config.get("daily_watcher_config", {}).get(
                    "pipeline_integration", default_config["pipeline_integration"]
                )
            except Exception as e:
                logger.warning(f"Failed to load pipeline config: {e}")

        return default_config["pipeline_integration"]

    def setup_event_handlers(self):
        """Setup event handlers for pipeline integration"""

        # Override file watcher's completion check to trigger pipeline
        original_trigger_pipeline = self.file_watcher.trigger_daily_pipeline

        async def enhanced_trigger_pipeline():
            """Enhanced pipeline trigger with event bus integration"""
            try:
                # Call original trigger
                await original_trigger_pipeline()

                # Publish pipeline trigger event
                event = StageEvent(
                    stage_name="daily_files_ready",
                    event_type="completed",
                    timestamp=datetime.now(),
                    data={
                        "target_date": self.file_watcher.current_target_date,
                        "files_processed": {
                            "cards": self.file_watcher.required_files_per_day["cards"],
                            "results": self.file_watcher.required_files_per_day[
                                "results"
                            ],
                        },
                    },
                    success=True,
                )

                self.event_bus.publish(event)
                logger.info(
                    f"📡 Published pipeline trigger event for {self.file_watcher.current_target_date}"
                )

                # Trigger pipeline stages if configured
                if self.pipeline_config.get("auto_trigger", True):
                    await self.trigger_pipeline_stages()

            except Exception as e:
                logger.error(f"❌ Error in enhanced pipeline trigger: {e}")

        # Replace the trigger method
        self.file_watcher.trigger_daily_pipeline = enhanced_trigger_pipeline

    async def trigger_pipeline_stages(self):
        """Trigger configured pipeline stages"""
        try:
            logger.info("🚀 Triggering pipeline stages for daily data processing")

            # Add delay if configured
            delay = self.pipeline_config.get("trigger_delay_seconds", 30)
            if delay > 0:
                logger.info(f"⏳ Waiting {delay} seconds before triggering pipeline...")
                await asyncio.sleep(delay)

            # Get stages to trigger
            stages = self.pipeline_config.get("stages_to_trigger", [])

            for stage in stages:
                try:
                    await self.trigger_pipeline_stage(stage)
                except Exception as e:
                    logger.error(f"❌ Failed to trigger stage {stage}: {e}")

            logger.info("✅ Pipeline stages triggered successfully")

        except Exception as e:
            logger.error(f"❌ Error triggering pipeline stages: {e}")

    async def trigger_pipeline_stage(self, stage_name: str):
        """Trigger a specific pipeline stage"""
        try:
            logger.info(f"🔄 Triggering pipeline stage: {stage_name}")

            # Create stage event
            event = StageEvent(
                stage_name=stage_name,
                event_type="triggered",
                timestamp=datetime.now(),
                data={
                    "triggered_by": "daily_file_watcher",
                    "target_date": self.file_watcher.current_target_date,
                    "source": "file_completion",
                },
            )

            self.event_bus.publish(event)

            # Stage-specific triggers
            if stage_name == "data_validation":
                await self.trigger_data_validation()
            elif stage_name == "database_upload":
                await self.trigger_database_upload()
            elif stage_name == "relationship_analysis":
                await self.trigger_relationship_analysis()
            elif stage_name == "ml_model_update":
                await self.trigger_ml_model_update()
            elif stage_name == "contextual_analysis":
                await self.trigger_contextual_analysis()
            else:
                logger.warning(f"⚠️ Unknown stage: {stage_name}")

        except Exception as e:
            logger.error(f"❌ Error triggering stage {stage_name}: {e}")

    async def trigger_data_validation(self):
        """Trigger data validation stage"""
        try:
            logger.info("🔍 Triggering data validation...")

            # Validate cards data
            cards_dir = (
                self.base_path
                / "data/daily_downloads/cards_data"
                / self.file_watcher.current_target_date
            )
            if cards_dir.exists():
                valid_cards = await self.file_watcher.validate_cards_data(cards_dir)
                logger.info(
                    f"📋 Cards validation: {'✅ Passed' if valid_cards else '❌ Failed'}"
                )

            # Validate results data
            results_dir = (
                self.base_path
                / "data/daily_downloads/results_data"
                / self.file_watcher.current_target_date
            )
            if results_dir.exists():
                valid_results = await self.file_watcher.validate_results_data(
                    results_dir
                )
                logger.info(
                    f"🏁 Results validation: {'✅ Passed' if valid_results else '❌ Failed'}"
                )

        except Exception as e:
            logger.error(f"❌ Data validation error: {e}")

    async def trigger_database_upload(self):
        """Trigger database upload stage"""
        try:
            logger.info("📤 Triggering database upload...")

            # Import and run database uploader
            upload_script = self.project_root / "scripts" / "database_uploader.py"
            if upload_script.exists():
                import subprocess

                result = subprocess.run(
                    [
                        sys.executable,
                        str(upload_script),
                        "--date",
                        self.file_watcher.current_target_date,
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    logger.info("✅ Database upload completed")
                else:
                    logger.error(f"❌ Database upload failed: {result.stderr}")
            else:
                logger.warning("⚠️ Database uploader script not found")

        except Exception as e:
            logger.error(f"❌ Database upload error: {e}")

    async def trigger_relationship_analysis(self):
        """Trigger relationship analysis stage"""
        try:
            logger.info("🔗 Triggering relationship analysis...")

            # Run relationship analysis
            analysis_script = (
                self.project_root / "tools" / "data_relationships_pipeline.py"
            )
            if analysis_script.exists():
                import subprocess

                result = subprocess.run(
                    [
                        sys.executable,
                        str(analysis_script),
                        "--date",
                        self.file_watcher.current_target_date,
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    logger.info("✅ Relationship analysis completed")
                else:
                    logger.error(f"❌ Relationship analysis failed: {result.stderr}")
            else:
                logger.warning("⚠️ Relationship analysis script not found")

        except Exception as e:
            logger.error(f"❌ Relationship analysis error: {e}")

    async def trigger_ml_model_update(self):
        """Trigger ML model update stage"""
        try:
            logger.info("🧠 Triggering ML model update...")

            # Run ML model training
            ml_script = (
                self.project_root
                / "tools"
                / "ml_training"
                / "enhanced_ml_ensemble_integration.py"
            )
            if ml_script.exists():
                import subprocess

                result = subprocess.run(
                    [
                        sys.executable,
                        str(ml_script),
                        "--retrain",
                        "--date",
                        self.file_watcher.current_target_date,
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    logger.info("✅ ML model update completed")
                else:
                    logger.error(f"❌ ML model update failed: {result.stderr}")
            else:
                logger.warning("⚠️ ML training script not found")

        except Exception as e:
            logger.error(f"❌ ML model update error: {e}")

    async def trigger_contextual_analysis(self):
        """Trigger contextual analysis stage"""
        try:
            logger.info("📊 Triggering contextual analysis...")

            # Run contextual analysis
            analysis_script = self.project_root / "tools" / "contextual_ai_enhance.py"
            if analysis_script.exists():
                import subprocess

                result = subprocess.run(
                    [
                        sys.executable,
                        str(analysis_script),
                        "--date",
                        self.file_watcher.current_target_date,
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    logger.info("✅ Contextual analysis completed")
                else:
                    logger.error(f"❌ Contextual analysis failed: {result.stderr}")
            else:
                logger.warning("⚠️ Contextual analysis script not found")

        except Exception as e:
            logger.error(f"❌ Contextual analysis error: {e}")

    def start_integrated_watcher(self):
        """Start the integrated file watcher with pipeline connection"""
        try:
            logger.info("🚀 Starting integrated daily file watcher...")

            # Mark watcher as active
            self.integration_state["watcher_active"] = True

            # Create and start file watcher in thread
            from tools.automation.daily_file_watcher import DailyFileWatcherManager

            self.watcher_manager = DailyFileWatcherManager(str(self.base_path))

            # Start watcher in separate thread
            watcher_thread = threading.Thread(
                target=self._run_watcher_sync, daemon=True
            )
            watcher_thread.start()

            logger.info("✅ Integrated file watcher started")

        except Exception as e:
            logger.error(f"❌ Failed to start integrated watcher: {e}")
            self.integration_state["watcher_active"] = False

    def _run_watcher_sync(self):
        """Run watcher in synchronous context"""
        try:
            asyncio.run(self._run_watcher_async())
        except Exception as e:
            logger.error(f"❌ Watcher thread error: {e}")

    async def _run_watcher_async(self):
        """Run watcher asynchronously"""
        try:
            # Process existing files
            await self.watcher_manager.process_existing_files()

            # Start watching
            self.watcher_manager.start_watching()

            # Run continuous monitoring
            await self.watcher_manager.run_continuous()

        except Exception as e:
            logger.error(f"❌ Async watcher error: {e}")

    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        return {
            "integration_active": self.integration_state["watcher_active"],
            "current_target_date": self.file_watcher.current_target_date,
            "files_status": {
                "cards": self.file_watcher.required_files_per_day["cards"],
                "results": self.file_watcher.required_files_per_day["results"],
            },
            "completed_days": list(self.file_watcher.completed_days),
            "pipeline_config": self.pipeline_config,
            "event_log_count": len(self.event_bus.event_log),
            "last_updated": datetime.now().isoformat(),
        }

    def save_integration_status(self):
        """Save integration status to file"""
        try:
            status = self.get_integration_status()
            status_file = self.base_path / "data" / "pipeline_integration_status.json"

            with open(status_file, "w") as f:
                json.dump(status, f, indent=2)

            logger.info(f"💾 Integration status saved to {status_file}")

        except Exception as e:
            logger.error(f"❌ Failed to save integration status: {e}")


class PipelineIntegrationManager:
    """Manages the complete pipeline integration"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.04"):
        self.base_path = base_path
        self.integration = DailyFileWatcherPipelineIntegration(base_path)
        self.running = False

    def start(self):
        """Start the integrated pipeline"""
        try:
            logger.info("🚀 Starting Daily File Watcher Pipeline Integration")

            # Start the integrated watcher
            self.integration.start_integrated_watcher()

            # Mark as running
            self.running = True

            logger.info("✅ Pipeline integration started successfully")

        except Exception as e:
            logger.error(f"❌ Failed to start pipeline integration: {e}")

    def stop(self):
        """Stop the integrated pipeline"""
        try:
            logger.info("🛑 Stopping pipeline integration...")

            # Stop components
            if hasattr(self.integration, "watcher_manager"):
                self.integration.watcher_manager.stop_watching()

            self.running = False

            logger.info("✅ Pipeline integration stopped")

        except Exception as e:
            logger.error(f"❌ Error stopping pipeline integration: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "running": self.running,
            "integration_status": self.integration.get_integration_status(),
        }


async def main():
    """Main entry point for pipeline integration"""
    logger.info("🏇 Horse Racing AI - Daily File Watcher Pipeline Integration v2.04")

    manager = PipelineIntegrationManager()

    try:
        # Start integration
        manager.start()

        # Keep running
        while manager.running:
            await asyncio.sleep(60)
            manager.integration.save_integration_status()

    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
    finally:
        manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
