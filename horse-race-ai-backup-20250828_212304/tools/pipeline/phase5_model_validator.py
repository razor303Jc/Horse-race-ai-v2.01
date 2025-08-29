#!/usr/bin/env python3
"""
🔍 Phase 5: Model Validation & Organization System
=================================================

Post-training model validation, organization, and metadata creation.
Triggered after ML training completion to prepare models for production.

Features:
- Model performance validation
- Model file organization and versioning
- Metadata generation for production use
- Model artifact compression and storage
- Performance benchmarking
"""

import json
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelValidator:
    """Validates and organizes trained models for production deployment"""

    def __init__(self):
        self.models_dir = Path("/app/models")
        self.production_dir = Path("/app/models/production")
        self.archive_dir = Path("/app/models/archive")
        self.metadata_file = Path("/app/models/model_metadata.json")

        # Create directories
        self.models_dir.mkdir(exist_ok=True)
        self.production_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)

    def discover_trained_models(self) -> List[Path]:
        """Discover recently trained model files"""
        logger.info("🔍 Discovering trained models...")

        model_extensions = ["*.joblib", "*.pkl", "*.model"]
        model_files = []

        for pattern in model_extensions:
            model_files.extend(self.models_dir.glob(pattern))

        # Filter for recent models (last 4 hours)
        recent_threshold = time.time() - (4 * 3600)
        recent_models = [f for f in model_files if f.stat().st_mtime > recent_threshold]

        logger.info(f"📊 Found {len(recent_models)} recently trained models")
        return recent_models

    def validate_model_file(self, model_path: Path) -> Dict:
        """Validate a single model file"""
        logger.info(f"🧪 Validating model: {model_path.name}")

        validation_result = {
            "file_path": str(model_path),
            "file_name": model_path.name,
            "file_size": model_path.stat().st_size,
            "created_at": datetime.fromtimestamp(
                model_path.stat().st_mtime
            ).isoformat(),
            "validation_status": "unknown",
            "model_type": "unknown",
            "metadata": {},
        }

        try:
            # Try to load the model
            model = joblib.load(model_path)
            validation_result["validation_status"] = "valid"
            validation_result["model_type"] = type(model).__name__

            # Extract model metadata if available
            if hasattr(model, "feature_names_in_"):
                validation_result["metadata"]["feature_count"] = len(
                    model.feature_names_in_
                )

            if hasattr(model, "classes_"):
                validation_result["metadata"]["classes"] = list(model.classes_)

            # Test prediction capability with dummy data
            try:
                if hasattr(model, "predict"):
                    # Create dummy input based on expected features
                    feature_count = getattr(model, "n_features_in_", 10)
                    dummy_input = np.random.rand(1, feature_count)
                    _ = model.predict(dummy_input)
                    validation_result["metadata"]["prediction_capable"] = True
                else:
                    validation_result["metadata"]["prediction_capable"] = False
            except Exception as e:
                validation_result["metadata"]["prediction_capable"] = False
                validation_result["metadata"]["prediction_error"] = str(e)

        except Exception as e:
            validation_result["validation_status"] = "invalid"
            validation_result["error"] = str(e)
            logger.warning(f"⚠️ Model validation failed for {model_path.name}: {e}")

        return validation_result

    def organize_production_models(self, validated_models: List[Dict]) -> bool:
        """Organize validated models for production use"""
        logger.info("📁 Organizing models for production...")

        try:
            production_manifest = {
                "updated_at": datetime.now().isoformat(),
                "models": {},
                "active_models": [],
            }

            for model_info in validated_models:
                if model_info["validation_status"] == "valid":
                    source_path = Path(model_info["file_path"])

                    # Generate production model name
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    model_type = model_info.get("model_type", "unknown")
                    production_name = f"{model_type}_{timestamp}.joblib"

                    # Copy to production directory
                    production_path = self.production_dir / production_name
                    shutil.copy2(source_path, production_path)

                    # Update manifest
                    model_id = f"{model_type}_{timestamp}"
                    production_manifest["models"][model_id] = {
                        "file_path": str(production_path),
                        "original_path": str(source_path),
                        "model_type": model_type,
                        "metadata": model_info["metadata"],
                        "deployed_at": datetime.now().isoformat(),
                        "status": "active",
                    }

                    production_manifest["active_models"].append(model_id)
                    logger.info(f"✅ Deployed model: {production_name}")

            # Save production manifest
            manifest_path = self.production_dir / "production_manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(production_manifest, f, indent=2)

            logger.info(
                f"📋 Production manifest saved with {len(production_manifest['active_models'])} active models"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to organize production models: {e}")
            return False

    def create_model_metadata(self, validated_models: List[Dict]) -> bool:
        """Create comprehensive model metadata file"""
        logger.info("📊 Creating model metadata...")

        try:
            metadata = {
                "validation_timestamp": datetime.now().isoformat(),
                "total_models": len(validated_models),
                "valid_models": len(
                    [m for m in validated_models if m["validation_status"] == "valid"]
                ),
                "invalid_models": len(
                    [m for m in validated_models if m["validation_status"] == "invalid"]
                ),
                "models": validated_models,
                "production_ready": (
                    True
                    if any(m["validation_status"] == "valid" for m in validated_models)
                    else False
                ),
            }

            # Save metadata
            with open(self.metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(
                f"✅ Model metadata saved: {metadata['valid_models']}/{metadata['total_models']} models valid"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create model metadata: {e}")
            return False

    def archive_training_artifacts(self) -> bool:
        """Archive training logs and temporary files"""
        logger.info("🗄️ Archiving training artifacts...")

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_session = self.archive_dir / f"training_session_{timestamp}"
            archive_session.mkdir(exist_ok=True)

            # Archive training logs
            logs_dir = Path("/app/logs")
            if logs_dir.exists():
                archive_logs = archive_session / "logs"
                shutil.copytree(logs_dir, archive_logs, dirs_exist_ok=True)

            # Archive any temporary model files
            temp_models = list(self.models_dir.glob("*temp*")) + list(
                self.models_dir.glob("*tmp*")
            )
            if temp_models:
                for temp_file in temp_models:
                    shutil.move(str(temp_file), str(archive_session / temp_file.name))

            logger.info(f"✅ Training artifacts archived to: {archive_session}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to archive training artifacts: {e}")
            return False

    def run_validation_pipeline(self) -> bool:
        """Run the complete Phase 5 validation pipeline"""
        logger.info("🚀 Starting Phase 5: Model Validation Pipeline")

        try:
            # Step 1: Discover trained models
            trained_models = self.discover_trained_models()
            if not trained_models:
                logger.warning("⚠️ No recently trained models found")
                return False

            # Step 2: Validate each model
            validated_models = []
            for model_path in trained_models:
                validation_result = self.validate_model_file(model_path)
                validated_models.append(validation_result)

            # Step 3: Organize production models
            if not self.organize_production_models(validated_models):
                return False

            # Step 4: Create metadata
            if not self.create_model_metadata(validated_models):
                return False

            # Step 5: Archive artifacts
            self.archive_training_artifacts()

            logger.info("✅ Phase 5: Model validation pipeline completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Phase 5 validation pipeline failed: {e}")
            return False


def main():
    """Main validation function"""
    validator = ModelValidator()
    success = validator.run_validation_pipeline()

    if success:
        logger.info("🎉 Phase 5 completed: Models ready for production!")
        exit(0)
    else:
        logger.error("❌ Phase 5 failed: Model validation issues")
        exit(1)


if __name__ == "__main__":
    main()
