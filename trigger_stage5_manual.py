#!/usr/bin/env python3
"""
🚀 Stage 5 Manual Trigger
========================

Manually trigger Stage 5 and subsequent post-training stages
"""

import logging
import subprocess
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def trigger_stage5():
    """Manually trigger Stage 5 model validation"""
    logger.info("🔍 Manually triggering Stage 5: Model Validation")

    try:
        # Run the Phase 5 model validator directly
        result = subprocess.run(
            ["python", "/app/tools/pipeline/phase5_model_validator.py"],
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode == 0:
            logger.info("✅ Stage 5: Model validation completed successfully!")
            logger.info("Output summary:")
            # Show last few lines of output
            output_lines = result.stdout.strip().split("\n")
            for line in output_lines[-10:]:
                logger.info(f"   {line}")
            return True
        else:
            logger.error("❌ Stage 5: Model validation failed")
            logger.error(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("❌ Stage 5: Model validation timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Stage 5: Exception occurred: {e}")
        return False


def trigger_stage6():
    """Manually trigger Stage 6 prediction service"""
    logger.info("🔮 Manually triggering Stage 6: Prediction Service")

    try:
        # Run the Phase 6 prediction service
        result = subprocess.run(
            ["python", "/app/tools/pipeline/phase6_simple_prediction_service.py"],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            logger.info("✅ Stage 6: Prediction service started successfully!")
            logger.info("Output summary:")
            output_lines = result.stdout.strip().split("\n")
            for line in output_lines[-5:]:
                logger.info(f"   {line}")
            return True
        else:
            logger.error("❌ Stage 6: Prediction service failed")
            logger.error(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("❌ Stage 6: Prediction service timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Stage 6: Exception occurred: {e}")
        return False


def verify_stage5_outputs():
    """Verify Stage 5 created proper outputs"""
    logger.info("🔍 Verifying Stage 5 outputs...")

    import json
    from pathlib import Path

    # Check production models
    production_dir = Path("/app/models/production")
    if production_dir.exists():
        models = list(production_dir.glob("*.joblib"))
        logger.info(f"✅ Found {len(models)} production models")

        # Check manifest
        manifest_file = production_dir / "production_manifest.json"
        if manifest_file.exists():
            with open(manifest_file, "r") as f:
                manifest = json.load(f)
            active_models = len(manifest.get("active_models", []))
            logger.info(f"✅ Production manifest: {active_models} active models")
        else:
            logger.warning("⚠️ No production manifest found")
    else:
        logger.error("❌ No production directory found")
        return False

    # Check metadata
    metadata_file = Path("/app/models/model_metadata.json")
    if metadata_file.exists():
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        total = metadata.get("total_models", 0)
        valid = metadata.get("valid_models", 0)
        logger.info(f"✅ Model metadata: {valid}/{total} valid models")
    else:
        logger.warning("⚠️ No model metadata found")

    return True


def main():
    """Main trigger function"""
    logger.info("🚀 Starting Stage 5+ Manual Trigger")

    # Step 1: Verify current models and trigger Stage 5
    logger.info("=" * 50)
    stage5_success = trigger_stage5()

    if stage5_success:
        # Step 2: Verify Stage 5 outputs
        logger.info("=" * 50)
        verify_stage5_outputs()

        # Step 3: Trigger Stage 6
        logger.info("=" * 50)
        stage6_success = trigger_stage6()

        if stage6_success:
            logger.info("🎉 Stages 5-6 completed successfully!")
        else:
            logger.error("❌ Stage 6 failed, but Stage 5 completed")
    else:
        logger.error("❌ Stage 5 failed")


if __name__ == "__main__":
    main()
