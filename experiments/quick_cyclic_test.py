#!/usr/bin/env python3
"""
Quick Cyclic Training Test
Tests the cyclic training system with a smaller dataset and fewer cycles.
"""

import os
import sys
import logging
from datetime import datetime

# Add project path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")

from ml_cyclic_training_system import MLCyclicTrainingSystem

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def quick_test():
    """Run a quick test of the cyclic training system"""
    logger.info("🧪 QUICK CYCLIC TRAINING TEST")
    logger.info("=" * 50)

    # Initialize system with test parameters
    training_system = MLCyclicTrainingSystem(
        db_path="test_cycles.db", models_dir="test_models", results_dir="test_results"
    )

    # Generate smaller dataset for testing
    logger.info("📊 Generating test dataset...")
    training_system.generate_training_data(
        num_horses=1000,  # Smaller for testing
        num_days=180,  # 6 months
        start_date="2024-01-01",
    )

    # Run fewer cycles for testing
    logger.info("🔄 Starting test training cycles...")
    training_system.run_training_cycles(
        total_cycles=20,  # Fewer cycles for testing
        evaluation_interval=5,  # Evaluate every 5 cycles
        data_increment_pct=0.1,
    )

    logger.info("✅ Quick test completed!")


if __name__ == "__main__":
    quick_test()
