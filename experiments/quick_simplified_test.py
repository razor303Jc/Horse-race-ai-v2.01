#!/usr/bin/env python3
"""
Quick Test of Simplified Cyclic Training
Tests the simplified training system with a small dataset.
"""

import sys
import logging

# Add project path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")

from simplified_cyclic_training import SimplifiedCyclicTraining

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def quick_test():
    """Run quick test with small dataset"""
    print("🧪 QUICK SIMPLIFIED CYCLIC TRAINING TEST")
    print("=" * 50)

    trainer = SimplifiedCyclicTraining(db_path="quick_test.db")

    # Generate small dataset
    trainer.generate_training_data(num_horses=500, num_days=90, start_date="2024-01-01")

    # Run short training cycle
    trainer.run_training_cycles(total_cycles=20, evaluation_interval=5)


if __name__ == "__main__":
    quick_test()
