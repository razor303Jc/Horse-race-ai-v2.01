#!/usr/bin/env python3
"""
Save Training Models to Trained Models Directory
===============================================

This script trains models and saves them to the proper trained_models directory
at /home/jc/Documents/Horse-race-ai-v2.04/trained_models

Features:
- Uses existing training framework
- Saves to correct directory structure
- Creates backup of models
- Generates model metadata
"""

import os
import sys
import json
import logging
import joblib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = "/home/jc/Documents/Horse-race-ai-v2.04"
sys.path.insert(0, project_root)

from scripts.train_advanced_metrics_models import AdvancedMetricsMLTrainer

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelSaver:
    """Saves trained models to the proper trained_models directory."""

    def __init__(self):
        """Initialize the model saver."""
        self.project_root = Path(project_root)
        self.trained_models_dir = self.project_root / "trained_models"
        self.trained_models_dir.mkdir(exist_ok=True)

        # Create subdirectories
        (self.trained_models_dir / "individual").mkdir(exist_ok=True)
        (self.trained_models_dir / "ensembles").mkdir(exist_ok=True)
        (self.trained_models_dir / "metadata").mkdir(exist_ok=True)

        logger.info(f"📁 Models will be saved to: {self.trained_models_dir}")

    def train_and_save_models(self) -> Dict[str, Any]:
        """Train models and save to trained_models directory."""
        logger.info("🚀 Starting model training and saving process...")

        # Initialize trainer with custom models directory
        trainer = AdvancedMetricsMLTrainer()
        trainer.models_dir = self.trained_models_dir / "individual"

        try:
            # Load data
            train_df, test_df = trainer.load_training_data()
            logger.info(
                f"📊 Loaded {len(train_df)} training, {len(test_df)} test records"
            )

            # Train models
            logger.info("🤖 Training individual models...")
            win_results = trainer.train_win_probability_models(train_df)
            position_results = trainer.train_finishing_position_models(train_df)
            place_results = trainer.train_place_probability_models(train_df)

            # Ensemble results are included in the individual training methods
            ensemble_results = {
                "win_ensemble": win_results.get("ensemble", {}),
                "position_ensemble": position_results.get("ensemble", {}),
                "place_ensemble": place_results.get("ensemble", {}),
            }

            # Save models with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save complete model package
            model_package = {
                "models": trainer.models,
                "scalers": trainer.scalers,
                "feature_columns": trainer.feature_columns,
                "timestamp": timestamp,
                "win_results": win_results,
                "position_results": position_results,
                "place_results": place_results,
                "ensemble_results": ensemble_results,
            }

            # Main model package
            package_filename = f"complete_model_package_{timestamp}.joblib"
            main_package_path = self.trained_models_dir / package_filename
            joblib.dump(model_package, main_package_path)

            # Save individual models
            for model_name, model in trainer.models.items():
                model_filename = f"{model_name}_{timestamp}.joblib"
                model_path = self.trained_models_dir / "individual" / model_filename
                joblib.dump(model, model_path)
                logger.info(f"💾 Saved {model_name}")

            # Save scalers
            scalers_path = self.trained_models_dir / f"scalers_{timestamp}.joblib"
            joblib.dump(trainer.scalers, scalers_path)

            # Save metadata
            metadata = {
                "timestamp": timestamp,
                "training_date": datetime.now().isoformat(),
                "model_count": len(trainer.models),
                "feature_columns": trainer.feature_columns,
                "performance_metrics": {
                    "win_models": win_results,
                    "position_models": position_results,
                    "place_models": place_results,
                    "ensemble_models": ensemble_results,
                },
                "data_path": trainer.data_path,
                "saved_files": {
                    "main_package": str(main_package_path),
                    "scalers": str(scalers_path),
                    "individual_models": [
                        str(
                            self.trained_models_dir
                            / "individual"
                            / f"{name}_{timestamp}.joblib"
                        )
                        for name in trainer.models.keys()
                    ],
                },
            }

            metadata_filename = f"training_metadata_{timestamp}.json"
            metadata_path = self.trained_models_dir / "metadata" / metadata_filename
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2, default=str)

            # Create latest symlinks
            latest_package = self.trained_models_dir / "latest_model_package.joblib"
            latest_metadata = self.trained_models_dir / "latest_metadata.json"

            if latest_package.exists():
                latest_package.unlink()
            if latest_metadata.exists():
                latest_metadata.unlink()

            latest_package.symlink_to(main_package_path.name)
            latest_metadata.symlink_to(f"metadata/training_metadata_{timestamp}.json")

            logger.info("✅ Model training and saving completed successfully!")
            logger.info(f"📦 Main package: {main_package_path}")
            logger.info(f"📊 Metadata: {metadata_path}")
            logger.info("🔗 Latest links created")

            return metadata

        except Exception as e:
            logger.error(f"❌ Error during training: {e}")
            raise

    def list_saved_models(self):
        """List all saved models."""
        logger.info("📋 Saved models in trained_models directory:")

        for item in sorted(self.trained_models_dir.iterdir()):
            if item.is_file() and item.suffix == ".joblib":
                logger.info(f"  📦 {item.name}")
            elif item.is_dir():
                logger.info(f"  📁 {item.name}/")
                for subitem in sorted(item.iterdir()):
                    if subitem.suffix == ".joblib":
                        logger.info(f"    📦 {subitem.name}")


def main():
    """Main execution function."""
    logger.info("🏇 Horse Racing AI - Model Training and Saving")
    logger.info("=" * 50)

    try:
        # Initialize model saver
        saver = ModelSaver()

        # Train and save models
        metadata = saver.train_and_save_models()

        # List saved models
        saver.list_saved_models()

        logger.info("🎉 Training and saving process completed successfully!")
        logger.info(f"🏆 Trained {metadata['model_count']} models")

        return 0

    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
