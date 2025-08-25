#!/usr/bin/env python3
"""
Simple Training Runner for Progressive Cycle Training

Lightweight training script that can be called by the progressive trainer
with different cycle and session parameters.
"""

import logging
import sys
import os
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_enhanced_training(cycles: int, sessions: int, level: int) -> bool:
    """Run enhanced AI training with specified parameters"""

    logger.info(f"🚀 Starting Enhanced Training - Level {level}")
    logger.info(f"   📊 Cycles: {cycles}, Sessions: {sessions}")

    # Use the deployed enhanced model for training
    base_dir = Path("/home/jc/Documents/Horse-race-ai-v2.04")
    enhanced_model = base_dir / "src/ai_selections.py"

    try:
        # Run the enhanced AI model
        cmd = ["python", str(enhanced_model)]

        logger.info(f"   🔧 Executing enhanced AI training...")

        result = subprocess.run(
            cmd,
            cwd=str(base_dir),
            capture_output=True,
            text=True,
            timeout=1200,  # 20 minute timeout
        )

        if result.returncode == 0:
            logger.info(f"   ✅ Training Level {level} completed successfully")
            logger.info(f"   📊 Output: {len(result.stdout)} characters")
            return True
        else:
            logger.error(f"   ❌ Training Level {level} failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"   ⏰ Training Level {level} timed out")
        return False
    except Exception as e:
        logger.error(f"   ❌ Training Level {level} error: {e}")
        return False


def main():
    """Main training runner function"""

    parser = argparse.ArgumentParser(description="Enhanced AI Training Runner")
    parser.add_argument(
        "--cycles", type=int, default=10, help="Number of training cycles"
    )
    parser.add_argument(
        "--sessions", type=int, default=1000, help="Number of training sessions"
    )
    parser.add_argument("--level", type=int, default=1, help="Training level")

    args = parser.parse_args()

    print(f"🧠 Enhanced Training Runner - Level {args.level}")
    print(f"📊 Cycles: {args.cycles}, Sessions: {args.sessions}")
    print()

    success = run_enhanced_training(args.cycles, args.sessions, args.level)

    if success:
        print(f"✅ Training Level {args.level} completed successfully!")
        return 0
    else:
        print(f"❌ Training Level {args.level} failed!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
