#!/usr/bin/env python3
"""
🚀 Manual Pipeline Trigger
=========================

Manually trigger pipeline stages after successful 15:15 download
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.pipeline.event_driven_orchestrator import EventDrivenPipelineOrchestrator


def main():
    print("🚀 Manual Pipeline Trigger - Post 15:15 Download")
    print("=" * 50)

    orchestrator = EventDrivenPipelineOrchestrator()

    # Manually mark data_download as complete since it happened at 15:15
    orchestrator.completed_stages.add("data_download")
    print("✅ Marked data_download as completed (15:15 success)")

    # Start monitoring
    orchestrator.start_monitoring()
    print("🔍 Event-driven monitoring started")

    # Manually trigger data validation since files are present
    print("\n🎯 Triggering data validation...")
    result = orchestrator.trigger_stage("data_validation")
    if result:
        print("✅ Data validation triggered successfully")
    else:
        print("❌ Data validation trigger failed")

    # Wait a bit for validation to complete, then trigger preprocessing
    print("\n⏳ Waiting for validation to complete...")
    time.sleep(10)

    print("\n🎯 Triggering data preprocessing...")
    result = orchestrator.trigger_stage("data_preprocessing")
    if result:
        print("✅ Data preprocessing triggered successfully")
    else:
        print("❌ Data preprocessing trigger failed")

    print("\n🔄 Pipeline monitoring active. Press Ctrl+C to stop...")
    try:
        while True:
            time.sleep(5)
            # Show active stages
            if orchestrator.active_stages:
                print(f"🔄 Active stages: {orchestrator.active_stages}")
            if orchestrator.completed_stages:
                print(f"✅ Completed stages: {orchestrator.completed_stages}")
    except KeyboardInterrupt:
        print("\n🛑 Manual pipeline trigger stopped")


if __name__ == "__main__":
    main()
