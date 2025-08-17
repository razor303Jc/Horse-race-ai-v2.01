#!/usr/bin/env python3
"""
🧪 Test ML Training Completion Detection
"""

import sys
import time
from pathlib import Path

# Add the tools directory to the path
sys.path.append('/app/tools/pipeline')

from proper_pipeline_orchestrator import PipelineOrchestrator

def test_ml_completion_detection():
    print("🧪 Testing ML Training Completion Detection")
    
    orchestrator = PipelineOrchestrator()
    
    # Check if ML training is marked as complete
    print(f"📊 ML pipeline stage status: {orchestrator.stage_status.get('ml_pipeline', 'Not found')}")
    
    # Check if we have trained models
    models_available = orchestrator.check_ml_training_complete()
    print(f"🤖 Models available: {models_available}")
    
    # Check if post-training is pending
    post_training_pending = orchestrator.is_ml_training_complete_and_pending()
    print(f"⏱️ Post-training pending: {post_training_pending}")
    
    if post_training_pending:
        print("🚀 Triggering post-training pipeline...")
        orchestrator.trigger_post_training_pipeline()
    else:
        print("⏸️ Post-training not ready yet")

if __name__ == "__main__":
    test_ml_completion_detection()
