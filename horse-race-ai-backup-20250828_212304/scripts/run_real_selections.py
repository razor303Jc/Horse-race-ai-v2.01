#!/usr/bin/env python3
"""
🎯 Real Racing Data AI Selections - August 20, 2025
==================================================

Run enhanced AI selections with today's real racing data.
"""

import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import our enhanced generator
from enhanced_ai_selections_generator import EnhancedAISelectionsGenerator


def main():
    """Run real data AI selections."""
    print("🎯 REAL RACING DATA AI SELECTIONS")
    print("📅 August 20, 2025")
    print("=" * 50)

    try:
        # Initialize generator
        logger.info("🤖 Initializing Enhanced AI Selections Generator...")
        generator = EnhancedAISelectionsGenerator()

        # Show model status
        if generator.advanced_models:
            print(f"✅ Advanced Models: {len(generator.advanced_models)} loaded")
            print(f"   Features: {len(generator.feature_columns)} metrics")
        else:
            print("⚠️ Using fallback mode")

        print()

        # Run daily selections
        logger.info("🚀 Running daily selections with real data...")
        generator.run_daily_selections()

        print("\n✅ Real data AI selections completed!")

    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
