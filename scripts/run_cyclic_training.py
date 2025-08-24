#!/usr/bin/env python3
"""
Cyclic ML Training with Model Saving
Run cyclic training and save models to /trained_models directory
"""

import logging
import sys
import os
import json
import joblib
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = "/home/jc/Documents/Horse-race-ai-v2.04"
sys.path.insert(0, project_root)

from tools.ml_training.cyclic_trainer import CyclicMLTrainer

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CyclicTrainerWithSaving(CyclicMLTrainer):
    """Extended cyclic trainer that saves models to trained_models directory."""

    def __init__(self):
        super().__init__()
        self.trained_models_dir = Path(project_root) / "trained_models"
        self.trained_models_dir.mkdir(exist_ok=True)

        # Create subdirectories
        (self.trained_models_dir / "cyclic").mkdir(exist_ok=True)
        (self.trained_models_dir / "best_models").mkdir(exist_ok=True)

    def save_best_models(self, session_name):
        """Save the best models to trained_models directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        logger.info("💾 Saving best models to trained_models directory...")

        for model_name, model_info in self.best_models.items():
            # Save the model
            model_filename = f"{model_name}_cyclic_{timestamp}.joblib"
            model_path = self.trained_models_dir / "best_models" / model_filename

            # Create model package
            model_package = {
                "model": model_info["model"],
                "scaler": model_info.get("scaler"),
                "features": model_info["features"],
                "performance": {
                    "auc": model_info["auc"],
                    "cycle": model_info["cycle"],
                    "session": model_info["session"],
                },
                "training_info": {
                    "session_name": session_name,
                    "timestamp": timestamp,
                    "total_cycles": len(self.training_history),
                },
            }

            joblib.dump(model_package, model_path)
            logger.info(f"✅ Saved {model_name} (AUC: {model_info['auc']:.4f})")

        # Save training metadata
        metadata = {
            "session_name": session_name,
            "timestamp": timestamp,
            "total_cycles": len(self.training_history),
            "total_sessions": len(self.training_history),
            "best_models": {
                name: {
                    "auc": info["auc"],
                    "cycle": info["cycle"],
                    "session": info["session"],
                    "features_count": len(info["features"]),
                }
                for name, info in self.best_models.items()
            },
            "performance_summary": {
                "max_auc": max(self.performance_trends["auc_scores"]),
                "avg_auc": (
                    sum(self.performance_trends["auc_scores"])
                    / len(self.performance_trends["auc_scores"])
                ),
                "final_auc": (
                    self.performance_trends["auc_scores"][-1]
                    if self.performance_trends["auc_scores"]
                    else 0
                ),
            },
        }

        metadata_filename = f"cyclic_training_metadata_{timestamp}.json"
        metadata_path = self.trained_models_dir / metadata_filename
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

        logger.info(f"📊 Metadata saved: {metadata_path}")

        # Create latest symlink
        latest_metadata = self.trained_models_dir / "latest_cyclic_metadata.json"
        if latest_metadata.exists():
            latest_metadata.unlink()
        latest_metadata.symlink_to(metadata_path.name)

        return metadata_path

    def run_training_cycles(
        self, num_cycles, sessions_per_cycle, session_name, wait_time=2
    ):
        """Override to save models after completion."""
        # Run the original training
        analysis = super().run_training_cycles(
            num_cycles, sessions_per_cycle, session_name, wait_time
        )

        # Save the best models
        self.save_best_models(session_name)

        return analysis


def main():
    """Run cyclic training with model saving."""
    logger.info("🏇 Cyclic ML Training with Model Saving")
    logger.info("=" * 50)

    trainer = CyclicTrainerWithSaving()

    try:
        # Run shorter cycle for testing
        logger.info("🎯 Running Cyclic Training (3 cycles × 3 sessions)")
        analysis = trainer.run_training_cycles(
            num_cycles=3,
            sessions_per_cycle=3,
            session_name="cyclic_training_test",
            wait_time=1,
        )

        logger.info("🎉 Cyclic training completed successfully!")
        logger.info(f"📁 Models saved to: {trainer.trained_models_dir}")

        # List saved files
        logger.info("📋 Saved models:")
        for file in (trainer.trained_models_dir / "best_models").glob("*.joblib"):
            logger.info(f"  🤖 {file.name}")

        return 0

    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
