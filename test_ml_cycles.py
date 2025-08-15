#!/usr/bin/env python3
"""
ML Training Test Runner
Quick test of ML training cycles with existing data
"""

import asyncio
import sys
from pathlib import Path

# Add the tools directory to path
sys.path.append("tools/ml_training")


async def test_ml_cycles():
    """Test ML training cycles with reduced parameters"""
    print("🧪 Testing ML Training Cycles")
    print("=" * 40)

    try:
        from automated_ml_cycle_manager import MLTrainingCycleManager

        # Create a test manager with reduced cycles
        manager = MLTrainingCycleManager()

        # Override for testing
        manager.target_cycles = 10  # Test with 10 cycles
        manager.cycles_per_batch = 5  # 2 batches of 5 cycles
        manager.target_batches = 2

        print(f"Test Parameters:")
        print(f"- Total cycles: {manager.target_cycles}")
        print(f"- Cycles per batch: {manager.cycles_per_batch}")
        print(f"- Total batches: {manager.target_batches}")
        print("\n🚀 Starting test run...")

        await manager.run_training_cycles()

        print("\n✅ Test completed successfully!")
        print(f"Final accuracy: {manager.best_accuracy:.4f}")
        print(
            f"Improvement: +{((manager.best_accuracy-manager.baseline_accuracy)/manager.baseline_accuracy)*100:.2f}%"
        )

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    # Create directories
    Path("logs").mkdir(exist_ok=True)
    Path("results/ml_performance").mkdir(parents=True, exist_ok=True)

    asyncio.run(test_ml_cycles())
