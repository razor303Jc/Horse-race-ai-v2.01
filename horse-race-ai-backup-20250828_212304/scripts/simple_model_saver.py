#!/usr/bin/env python3
"""
Train and Save Models to /trained_models Directory
=================================================

Uses the existing advanced metrics trainer but saves models to the correct directory.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = "/home/jc/Documents/Horse-race-ai-v2.04"
sys.path.insert(0, project_root)

from scripts.train_advanced_metrics_models import AdvancedMetricsMLTrainer

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Train models and save to trained_models directory."""
    logger.info("🎯 Training Models for /trained_models Directory")
    logger.info("=" * 50)

    # Initialize trainer
    trainer = AdvancedMetricsMLTrainer()

    # Set the models directory to our target location
    trainer.models_dir = Path("/home/jc/Documents/Horse-race-ai-v2.04/trained_models")
    trainer.models_dir.mkdir(exist_ok=True)

    try:
        # Run the complete training pipeline
        model_path = trainer.run_complete_training()

        logger.info("✅ Training completed successfully!")
        logger.info(f"📁 Models saved to: {model_path}")
        logger.info(f"🔧 Total models: {len(trainer.models)}")

        # List what was saved
        logger.info("📋 Saved models:")
        for model_name in trainer.models.keys():
            logger.info(f"  🤖 {model_name}")

        return 0

    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
