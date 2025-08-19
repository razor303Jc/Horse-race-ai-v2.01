#!/usr/bin/env python3
"""
🚀 Proper Pipeline Orchestrator
==============================

Real pipeline coordinator that:
1. Monitors for downloaded data files
2. Triggers CSV import automatically
3. Orchestrates pipeline stages in sequence
4. Handles dependencies and error recovery
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/pipeline_orchestrator.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Production pipeline orchestrator with file monitoring and stage management"""

    def __init__(self):
        self.data_dir = Path("/app/data/daily_downloads")
        self.logs_dir = Path("/app/logs")
        self.stage_status = {}
        self.last_file_check = {}

        # Database connection for pipeline stages
        self.db_config = {
            "host": "horse_racing_postgres_clean",
            "port": 5432,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }  # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        logger.info("🚀 Pipeline Orchestrator initialized")

    def start_orchestration(self):
        """Start the main orchestration loop"""
        logger.info("🎯 Starting pipeline orchestration...")

        while True:
            try:
                # Check for new downloads
                if self.check_for_new_downloads():
                    logger.info("📁 New download detected! Starting pipeline...")
                    self.run_pipeline_sequence()

                # Check if ML training has completed and post-training is needed
                if self.is_ml_training_complete_and_pending():
                    logger.info(
                        "🎓 ML training completed! Starting post-training pipeline..."
                    )
                    self.trigger_post_training_pipeline()

                # Check stage status periodically
                self.monitor_pipeline_health()

                # Wait before next check
                time.sleep(30)

            except KeyboardInterrupt:
                logger.info("🛑 Pipeline orchestrator stopped")
                break
            except Exception as e:
                logger.error(f"❌ Orchestrator error: {e}")
                time.sleep(60)  # Wait longer on errors

    def check_for_new_downloads(self) -> bool:
        """Check if new data files have been downloaded"""
        try:
            results_dir = self.data_dir / "results_data"
            cards_dir = self.data_dir / "cards_data"

            # Check if both directories exist with CSV files
            if not (results_dir.exists() and cards_dir.exists()):
                return False

            # Look for races.csv files as indicators
            results_races = results_dir / "races" / "races.csv"
            cards_races = cards_dir / "races" / "races.csv"

            if not (results_races.exists() and cards_races.exists()):
                return False

            # Check if files are newer than last check
            current_files = {
                "results_races": results_races.stat().st_mtime,
                "cards_races": cards_races.stat().st_mtime,
            }

            # Compare with last check
            if hasattr(self, "last_download_check"):
                if current_files == self.last_download_check:
                    return False  # No changes

            self.last_download_check = current_files

            # Validate file sizes (basic check)
            if results_races.stat().st_size < 1000 or cards_races.stat().st_size < 1000:
                logger.warning("⚠️ Downloaded files seem too small")
                return False

            logger.info(f"✅ Valid download detected:")
            logger.info(f"   📊 Results: {results_races.stat().st_size} bytes")
            logger.info(f"   📊 Cards: {cards_races.stat().st_size} bytes")

            return True

        except Exception as e:
            logger.error(f"❌ Error checking downloads: {e}")
            return False

    def run_pipeline_sequence(self):
        """Run the complete pipeline sequence"""
        logger.info("🚀 Starting pipeline sequence...")

        # Stage 1: Data Validation (already done in auto-downloader)
        self.mark_stage_complete("data_download", "Auto-downloader completed")

        # Stage 2: CSV Import
        if self.run_csv_import():
            self.mark_stage_complete("csv_import", "Database import successful")

            # Stage 2.5: Automated Data Quality Pipeline
            if self.run_data_quality_pipeline():
                self.mark_stage_complete(
                    "data_quality", "Data validation and conversion successful"
                )

                # Stage 3: Advanced Data Processing
                if self.run_advanced_data_processing():
                    self.mark_stage_complete(
                        "advanced_data_processing",
                        "V2.01 advanced processing completed",
                    )

                    # Stage 4: Enhanced ML Ensemble System
                    if self.run_enhanced_ml_ensemble():
                        self.mark_stage_complete(
                            "enhanced_ml_ensemble", "V2.01 ensemble models deployed"
                        )

                        # Stage 5: Performance Tracking Integration
                        if self.run_performance_tracking():
                            self.mark_stage_complete(
                                "performance_tracking", "Real-time monitoring active"
                            )

                            # Stage 6: Betting Integration System
                            if self.run_betting_integration():
                                self.mark_stage_complete(
                                    "betting_integration",
                                    "Automated betting system active",
                                )

                                # Stage 7: Contextual AI Enhancement System
                                if self.run_contextual_ai_enhancement():
                                    self.mark_stage_complete(
                                        "contextual_ai_enhancement",
                                        "Contextual AI analysis active",
                                    )

                                    # Stage 8: Data Architecture Improvements
                                    if self.run_data_architecture_improvements():
                                        self.mark_stage_complete(
                                            "data_architecture_improvements",
                                            "Data architecture enhanced",
                                        )

                                        # Final Stage: Legacy ML Pipeline (for compatibility)
                                        self.trigger_ml_pipeline()
                                    else:
                                        logger.error(
                                            "❌ Data architecture improvements failed"
                                        )
                                else:
                                    logger.error("❌ Contextual AI enhancement failed")
                            else:
                                logger.error("❌ Betting integration failed")
                        else:
                            logger.error("❌ Performance tracking failed")
                    else:
                        logger.error("❌ Enhanced ML ensemble failed")
                else:
                    logger.error("❌ Advanced data processing failed")
            else:
                logger.error("❌ Data quality pipeline failed")
        else:
            logger.error("❌ CSV import failed")

    def run_csv_import(self) -> bool:
        """Run CSV import using existing tools"""
        logger.info("📊 Stage 2: Starting CSV Import...")

        try:
            # Use the complete upload solution
            result = subprocess.run(
                ["python", "/app/tools/data_processing/corrected_uploader.py"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                logger.info("✅ CSV import completed successfully")
                logger.info(f"Import output: {result.stdout[-200:]}")  # Last 200 chars
                return True
            else:
                logger.error(f"❌ CSV import failed: {result.stderr}")

                # Try alternative uploader
                logger.info("🔄 Trying alternative CSV uploader...")
                result = subprocess.run(
                    ["python", "/app/tools/data_processing/database_uploader.py"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if result.returncode == 0:
                    logger.info("✅ Alternative CSV import successful")
                    return True
                else:
                    logger.error(f"❌ Both CSV importers failed")
                    return False

        except subprocess.TimeoutExpired:
            logger.error("❌ CSV import timed out")
            return False
        except Exception as e:
            logger.error(f"❌ CSV import exception: {e}")
            return False

    def run_data_quality_pipeline(self) -> bool:
        """Run automated data quality pipeline with validation and conversion"""
        logger.info("🔍 Stage 2.5: Starting Data Quality Pipeline...")

        try:
            # Run the automated data quality pipeline
            result = subprocess.run(
                ["python", "/app/tools/pipeline/automated_data_quality_pipeline.py"],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes for data quality checks
            )

            if result.returncode == 0:
                logger.info("✅ Data quality pipeline completed successfully")
                logger.info(f"📊 Output: {result.stdout[-500:]}")  # Last 500 chars
                return True
            else:
                logger.error(f"❌ Data quality pipeline failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Data quality pipeline timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Data quality pipeline exception: {e}")
            return False

    def run_advanced_data_processing(self) -> bool:
        """Run V2.01 advanced data processing pipeline"""
        logger.info("🚀 Stage 3: Starting Advanced Data Processing...")

        try:
            result = subprocess.run(
                [
                    "python",
                    "/app/tools/pipeline/advanced_data_processing_integration.py",
                ],
                capture_output=True,
                text=True,
                timeout=900,  # 15 minutes for advanced processing
            )

            if result.returncode == 0:
                logger.info("✅ Advanced data processing completed successfully")
                logger.info(f"📊 Output: {result.stdout[-500:]}")
                return True
            else:
                logger.error(f"❌ Advanced data processing failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Advanced data processing timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Advanced data processing exception: {e}")
            return False

    def run_enhanced_ml_ensemble(self) -> bool:
        """Run V2.01 enhanced ML ensemble system"""
        logger.info("🤖 Stage 4: Starting Enhanced ML Ensemble...")

        try:
            result = subprocess.run(
                ["python", "/app/tools/pipeline/enhanced_ml_ensemble_integration.py"],
                capture_output=True,
                text=True,
                timeout=1200,  # 20 minutes for ML training
            )

            if result.returncode == 0:
                logger.info("✅ Enhanced ML ensemble completed successfully")
                logger.info(f"📊 Output: {result.stdout[-500:]}")
                return True
            else:
                logger.error(f"❌ Enhanced ML ensemble failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Enhanced ML ensemble timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Enhanced ML ensemble exception: {e}")
            return False

    def run_performance_tracking(self) -> bool:
        """Run real-time performance tracking system"""
        logger.info("📊 Stage 5: Starting Performance Tracking...")

        try:
            result = subprocess.run(
                ["python", "/app/tools/pipeline/performance_tracking_integration.py"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes for performance tracking
            )

            if result.returncode == 0:
                logger.info("✅ Performance tracking completed successfully")
                logger.info(f"📊 Output: {result.stdout[-500:]}")
                return True
            else:
                logger.error(f"❌ Performance tracking failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Performance tracking timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Performance tracking exception: {e}")
            return False

    def run_betting_integration(self) -> bool:
        """Run automated betting integration system"""
        logger.info("🎯 Stage 6: Starting Betting Integration...")

        try:
            result = subprocess.run(
                ["python", "/app/tools/pipeline/betting_pipeline_integration.py"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes for betting integration
            )

            if result.returncode == 0:
                logger.info("✅ Betting integration completed successfully")
                logger.info(f"🎯 Output: {result.stdout[-500:]}")
                return True
            else:
                logger.error(f"❌ Betting integration failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Betting integration timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Betting integration exception: {e}")
            return False

    def run_contextual_ai_enhancement(self) -> bool:
        """Run contextual AI enhancement system"""
        logger.info("🧠 Stage 7: Starting Contextual AI Enhancement...")

        try:
            result = subprocess.run(
                ["python", "/app/tools/pipeline/run_contextual_ai_stage.py"],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes for contextual AI analysis
            )

            if result.returncode == 0:
                logger.info("✅ Contextual AI enhancement completed successfully")
                logger.info(f"🧠 Output: {result.stdout[-500:]}")
                return True
            else:
                logger.error(f"❌ Contextual AI enhancement failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Contextual AI enhancement timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Contextual AI enhancement exception: {e}")
            return False

    def run_data_architecture_improvements(self) -> bool:
        """Run data architecture improvements system"""
        logger.info("🏗️ Stage 8: Starting Data Architecture Improvements...")

        try:
            result = subprocess.run(
                ["python", "/app/tools/pipeline/run_data_architecture_stage.py"],
                capture_output=True,
                text=True,
                timeout=900,  # 15 minutes for comprehensive data architecture work
            )

            if result.returncode == 0:
                logger.info("✅ Data architecture improvements completed successfully")
                logger.info(f"🏗️ Output: {result.stdout[-500:]}")
                return True
            else:
                logger.error(
                    f"❌ Data architecture improvements failed: {result.stderr}"
                )
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Data architecture improvements timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Data architecture improvements exception: {e}")
            return False

    def run_data_preprocessing(self) -> bool:
        """Run data preprocessing and relationship building"""
        logger.info("🔄 Stage 3: Starting Data Preprocessing...")

        try:
            # Run automated relationships pipeline
            result = subprocess.run(
                [
                    "python",
                    "/app/tools/data_processing/automated_relationships_pipeline.py",
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                logger.info("✅ Data preprocessing completed")
                return True
            else:
                logger.error(f"❌ Data preprocessing failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Data preprocessing timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Data preprocessing exception: {e}")
            return False

    def trigger_ml_pipeline(self):
        """Trigger ML training and analysis pipeline"""
        logger.info("🤖 Stage 4: Triggering ML Pipeline...")

        try:
            # Run ML training orchestrator in background
            subprocess.Popen(
                ["python", "/app/tools/ml_training/ml_training_orchestrator.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            logger.info("✅ ML pipeline triggered (running in background)")
            self.mark_stage_complete("ml_pipeline", "ML training started")

            # Schedule post-training stages check
            self.schedule_post_training_check()

        except Exception as e:
            logger.error(f"❌ ML pipeline trigger failed: {e}")

    def schedule_post_training_check(self):
        """Schedule periodic checks for ML training completion"""
        logger.info("⏱️ Scheduling post-training pipeline checks...")
        # Will check every 5 minutes for training completion
        # This allows the orchestrator to detect when models are ready

    def check_ml_training_complete(self) -> bool:
        """Check if ML training has completed and models are ready"""
        try:
            # Check for saved models directory
            models_dir = Path("/app/models")
            if models_dir.exists():
                # Look for recently created model files
                model_files = list(models_dir.glob("*.joblib")) + list(
                    models_dir.glob("*.pkl")
                )
                if model_files:
                    # Check if any models were created in the last 2 hours
                    recent_models = [
                        f for f in model_files if time.time() - f.stat().st_mtime < 7200
                    ]
                    if recent_models:
                        logger.info(f"✅ Found {len(recent_models)} trained models")
                        return True

            return False
        except Exception as e:
            logger.warning(f"⚠️ Error checking ML training status: {e}")
            return False

    def is_ml_training_complete_and_pending(self) -> bool:
        """Check if ML training is complete but post-training hasn't run yet"""
        # Only proceed if ML training stage is complete
        if "ml_pipeline" not in self.stage_status:
            return False

        if self.stage_status["ml_pipeline"]["status"] != "completed":
            return False

        # Check if post-training stages haven't been started yet
        post_training_stages = [
            "model_validation",
            "prediction_service",
            "web_interface",
            "betting_integration",
        ]

        for stage in post_training_stages:
            if stage in self.stage_status:
                return False  # Post-training already started

        # Check if models are actually ready
        return self.check_ml_training_complete()

    def trigger_post_training_pipeline(self):
        """Trigger post-training stages: validation, prediction service, web interface"""
        logger.info("🚀 Stage 5: Starting Post-Training Pipeline...")

        # Stage 5: Model Validation & Saving
        if self.run_model_validation():
            self.mark_stage_complete("model_validation", "Models validated and saved")

            # Stage 8: Start Prediction Service
            if self.start_prediction_service():
                self.mark_stage_complete("prediction_service", "Prediction API active")

                # Stage 9: Start Web Interface
                if self.start_web_interface():
                    self.mark_stage_complete("web_interface", "Web dashboard active")

                    # Stage 10: Enable Betting Integration
                    self.enable_betting_integration()

    def run_model_validation(self) -> bool:
        """Run Phase 5: Model validation and organization"""
        logger.info("🔍 Phase 5: Running model validation...")

        try:
            # Use the dedicated Phase 5 model validator
            validation_script = "/app/tools/pipeline/phase5_model_validator.py"

            result = subprocess.run(
                ["python", validation_script],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                logger.info("✅ Phase 5: Model validation completed successfully")
                logger.info(
                    f"Validation output: {result.stdout[-500:]}"
                )  # Last 500 chars
                return True
            else:
                logger.error(f"❌ Phase 5: Model validation failed")
                logger.error(f"Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Phase 5: Model validation timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Phase 5: Model validation exception: {e}")
            return False

    def start_prediction_service(self) -> bool:
        """Run Phase 6: Start prediction API service"""
        logger.info("🔮 Phase 6: Starting prediction service...")

        try:
            # Use the dedicated Phase 6 prediction service launcher
            service_script = "/app/tools/pipeline/phase6_prediction_service.py"

            result = subprocess.run(
                ["python", service_script],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                logger.info("✅ Phase 6: Prediction service started successfully")
                logger.info(f"Service output: {result.stdout[-500:]}")  # Last 500 chars
                return True
            else:
                logger.error(f"❌ Phase 6: Prediction service startup failed")
                logger.error(f"Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Phase 6: Prediction service startup timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Phase 6: Prediction service exception: {e}")
            return False

    def start_web_interface(self) -> bool:
        """Start the web dashboard interface"""
        logger.info("🌐 Starting Web Dashboard Interface...")

        try:
            # Check if web app exists
            web_script = "/app/src/web/enhanced_web_application.py"
            if Path(web_script).exists():
                # Start web interface in background
                subprocess.Popen(
                    ["python", web_script],
                    cwd="/app",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                logger.info("✅ Web dashboard started")
                return True
            else:
                logger.warning("⚠️ Web interface not found, skipping...")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to start web interface: {e}")
            return False

    def enable_betting_integration(self):
        """Enable betting strategies and recommendations"""
        logger.info("💰 Stage 10: Enabling Betting Integration...")

        try:
            # Check if betting strategies exist
            betting_script = "/app/src/horse_racing_ai/betting/advanced_strategies.py"
            if Path(betting_script).exists():
                logger.info("✅ Betting strategies module available")
                self.mark_stage_complete(
                    "betting_integration", "Betting strategies enabled"
                )
            else:
                logger.info("📝 No betting integration found, skipping...")
                self.mark_stage_complete(
                    "betting_integration", "Betting integration skipped"
                )

        except Exception as e:
            logger.error(f"❌ Betting integration failed: {e}")

    def mark_stage_complete(self, stage_name: str, message: str):
        """Mark a pipeline stage as complete"""
        timestamp = datetime.now().isoformat()
        self.stage_status[stage_name] = {
            "completed_at": timestamp,
            "message": message,
            "status": "completed",
        }

        logger.info(f"✅ Stage completed: {stage_name} - {message}")

        # Save status to file
        status_file = self.logs_dir / "pipeline_status.json"
        with open(status_file, "w") as f:
            json.dump(self.stage_status, f, indent=2)

    def monitor_pipeline_health(self):
        """Monitor overall pipeline health"""
        try:
            # Check database connectivity
            import psycopg2

            conn = psycopg2.connect(**self.db_config)
            conn.close()

            # Log status every 10 minutes
            if not hasattr(self, "_last_health_log"):
                self._last_health_log = 0

            current_time = time.time()
            if current_time - self._last_health_log > 600:  # 10 minutes
                completed_stages = len(
                    [
                        s
                        for s in self.stage_status.values()
                        if s["status"] == "completed"
                    ]
                )
                logger.info(
                    f"💚 Pipeline Health: {completed_stages} stages completed, Database connected"
                )
                self._last_health_log = current_time

        except Exception as e:
            logger.warning(f"⚠️ Health check issue: {e}")

    def get_status_summary(self) -> dict:
        """Get current pipeline status summary"""
        return {
            "orchestrator_uptime": datetime.now().isoformat(),
            "completed_stages": len(
                [s for s in self.stage_status.values() if s["status"] == "completed"]
            ),
            "stage_details": self.stage_status,
            "data_directory_exists": self.data_dir.exists(),
            "last_download_check": getattr(self, "last_download_check", None),
        }


def main():
    """Main orchestrator function"""
    logger.info("🚀 Starting Proper Pipeline Orchestrator")

    # Create and start orchestrator
    orchestrator = PipelineOrchestrator()

    try:
        orchestrator.start_orchestration()
    except Exception as e:
        logger.error(f"❌ Fatal orchestrator error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
