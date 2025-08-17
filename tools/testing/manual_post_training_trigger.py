#!/usr/bin/env python3
"""
🚀 Manual Post-Training Pipeline Trigger
=====================================

Manually triggers Phase 5 & 6 for testing when models are ready.
"""

import logging
import subprocess
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def trigger_phase5():
    """Manually trigger Phase 5: Model Validation"""
    logger.info("🚀 Manually triggering Phase 5: Model Validation")
    
    try:
        result = subprocess.run(
            ["python", "/app/tools/pipeline/phase5_model_validator.py"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        logger.info(f"Phase 5 exit code: {result.returncode}")
        if result.stdout:
            logger.info(f"Phase 5 output: {result.stdout[-500:]}")
        if result.stderr:
            logger.info(f"Phase 5 stderr: {result.stderr[-500:]}")
            
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"❌ Phase 5 failed: {e}")
        return False


def trigger_phase6():
    """Manually trigger Phase 6: Prediction Service"""
    logger.info("🚀 Manually triggering Phase 6: Prediction Service")
    
    try:
        result = subprocess.run(
            ["python", "/app/tools/pipeline/phase6_simple_prediction_service.py"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        logger.info(f"Phase 6 exit code: {result.returncode}")
        if result.stdout:
            logger.info(f"Phase 6 output: {result.stdout[-500:]}")
        if result.stderr:
            logger.info(f"Phase 6 stderr: {result.stderr[-500:]}")
            
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"❌ Phase 6 failed: {e}")
        return False


def main():
    """Manual Phase 5 & 6 trigger test"""
    logger.info("🧪 Manual Post-Training Pipeline Test")
    
    # Check models exist
    models_dir = Path("/app/models")
    if not models_dir.exists():
        logger.error("❌ No models directory found")
        return
        
    model_files = list(models_dir.glob("*.joblib")) + list(models_dir.glob("*.pkl"))
    logger.info(f"📊 Found {len(model_files)} model files")
    
    if not model_files:
        logger.error("❌ No model files found")
        return
    
    # Trigger Phase 5
    if trigger_phase5():
        logger.info("✅ Phase 5 completed successfully")
        
        # Trigger Phase 6
        if trigger_phase6():
            logger.info("✅ Phase 6 completed successfully")
            logger.info("🎉 Post-training pipeline completed!")
        else:
            logger.warning("⚠️ Phase 6 had issues but continuing...")
    else:
        logger.error("❌ Phase 5 failed")


if __name__ == "__main__":
    main()
