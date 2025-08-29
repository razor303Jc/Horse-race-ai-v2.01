#!/usr/bin/env python3
"""
Initialize Horse Profiling System
=================================

This script initializes the horse profiling tables in the existing database
and demonstrates the horse profiling system functionality.
"""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.horse_racing_ai.analytics.horse_profiling_system import HorseProfilingSystem


def main():
    """Initialize horse profiling system and create necessary tables."""
    print("🐎 Initializing Horse Profiling System for v2.03")
    print("=" * 60)

    # Initialize the profiling system
    profiling_system = HorseProfilingSystem()

    # Create the profiling tables
    print("Creating horse profiling tables...")
    try:
        profiling_system.create_profiling_tables()
        print("✅ Horse profiling tables created successfully!")

        # Test basic functionality
        print("\n🧪 Testing basic functionality...")

        # Test progressive horses identification
        progressive_horses = profiling_system.get_progressive_horses(limit=5)
        print(
            f"✅ Progressive horses query successful: {len(progressive_horses)} horses found"
        )

        print("\n🎉 Horse Profiling System initialization complete!")
        print("\nThe system is now ready to:")
        print("• Classify horses as Progressive/Plateaued/Regressive")
        print("• Analyze condition-specific performance")
        print("• Discover optimal race conditions")
        print("• Generate comprehensive horse profiles")
        print("• Provide betting strategy insights")

    except Exception as e:
        print(f"❌ Error initializing horse profiling system: {e}")
        return False

    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
