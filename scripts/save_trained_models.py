#!/usr/bin/env python3
"""
Quick model save utility after training completion
"""

import joblib
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append("src")

from ml.enhanced_trainer import EnhancedMLTrainer


def main():
    """Re-run training and save models"""

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Ensure models directory exists
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    trainer = EnhancedMLTrainer()

    try:
        # Quick re-train and save
        print("🚀 Quick model training and save...")
        trainer.train_models(sample_size=10000)  # Smaller sample for quick save

        print("✅ Models training completed and saved!")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
