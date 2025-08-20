#!/usr/bin/env python3
"""
🧪 Quick System Validation Test
Fast integration test focusing on core functionality

Author: AI Assistant
Date: August 20, 2025
"""

import logging
import time
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run quick system validation."""
    logger.info("🧪 Quick System Validation Test")
    logger.info("=" * 50)

    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))

    total_start = time.time()
    tests_passed = 0
    tests_total = 0

    # Test 1: AI Generator Import and Initialization
    tests_total += 1
    try:
        from tools.ml_training.ai_selections_generator import AISelectionsGenerator

        generator = AISelectionsGenerator()
        logger.info("✅ Test 1: AI Generator initialization")
        tests_passed += 1
    except Exception as e:
        logger.error(f"❌ Test 1: AI Generator failed - {e}")

    # Test 2: Database Connectivity
    tests_total += 1
    try:
        df = generator.get_todays_races()
        if len(df) > 0:
            logger.info(f"✅ Test 2: Database connectivity - {len(df)} rows")
            tests_passed += 1
        else:
            logger.error("❌ Test 2: Database connectivity - No data")
    except Exception as e:
        logger.error(f"❌ Test 2: Database connectivity failed - {e}")

    # Test 3: Feature Engineering Performance
    tests_total += 1
    try:
        if len(df) > 0:
            start_time = time.time()
            df_features = generator.engineer_features(df)
            fe_time = time.time() - start_time

            if fe_time < 0.2 and len(df_features.columns) >= 15:
                logger.info(
                    f"✅ Test 3: Feature engineering - {fe_time:.3f}s, {len(df_features.columns)} features"
                )
                tests_passed += 1
            else:
                logger.error(
                    f"❌ Test 3: Feature engineering too slow - {fe_time:.3f}s"
                )
    except Exception as e:
        logger.error(f"❌ Test 3: Feature engineering failed - {e}")

    # Test 4: Model Loading
    tests_total += 1
    try:
        if len(generator.models) >= 4:
            logger.info(f"✅ Test 4: Model loading - {len(generator.models)} models")
            tests_passed += 1
        else:
            logger.error(
                f"❌ Test 4: Model loading - Only {len(generator.models)} models"
            )
    except Exception as e:
        logger.error(f"❌ Test 4: Model loading failed - {e}")

    # Test 5: API Server Status
    tests_total += 1
    try:
        import requests

        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Test 5: API server responding")
            tests_passed += 1
        else:
            logger.error(f"❌ Test 5: API server error {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Test 5: API server failed - {e}")

    # Summary
    total_time = time.time() - total_start
    logger.info("=" * 50)
    logger.info(f"🎯 QUICK VALIDATION SUMMARY")
    logger.info(f"   Tests Passed: {tests_passed}/{tests_total}")
    logger.info(f"   Success Rate: {tests_passed/tests_total*100:.1f}%")
    logger.info(f"   Total Time: {total_time:.2f} seconds")

    if tests_passed == tests_total:
        logger.info("🎉 ALL TESTS PASSED - System is healthy!")
        return True
    elif tests_passed >= tests_total * 0.8:
        logger.info("⚠️ MOSTLY PASSING - Minor issues detected")
        return True
    else:
        logger.info("❌ MULTIPLE FAILURES - System needs attention")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
