#!/usr/bin/env python3
"""
Test script to verify the enhanced preprocessing integration in pipeline
"""
import subprocess
import sys
from pathlib import Path


def test_enhanced_preprocessing():
    """Test the enhanced preprocessing pipeline functionality"""
    print("🧪 Testing Enhanced Preprocessing Integration...")

    # Test if the enhanced preprocessing pipeline can run
    try:
        result = subprocess.run(
            ["python", "enhanced_preprocessing_pipeline.py"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print("✅ Enhanced preprocessing pipeline runs successfully")
            print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Enhanced preprocessing failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Enhanced preprocessing timed out")
        return False
    except Exception as e:
        print(f"❌ Enhanced preprocessing exception: {e}")
        return False


def test_pipeline_coordinator():
    """Test the pipeline coordinator integration"""
    print("🧪 Testing Pipeline Coordinator Integration...")

    try:
        # Import the pipeline coordinator to check if it loads properly
        from tools.pipeline_coordinator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator()
        print("✅ Pipeline coordinator imports successfully")

        # Check if the enhanced preprocessing method exists
        if hasattr(orchestrator, "run_enhanced_preprocessing"):
            print("✅ Enhanced preprocessing method exists in pipeline")
            return True
        else:
            print("❌ Enhanced preprocessing method not found in pipeline")
            return False

    except Exception as e:
        print(f"❌ Pipeline coordinator test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Pipeline Integration Tests...")

    # Test 1: Enhanced preprocessing pipeline
    preprocessing_ok = test_enhanced_preprocessing()

    # Test 2: Pipeline coordinator integration
    coordinator_ok = test_pipeline_coordinator()

    # Summary
    print("\n📊 Test Results Summary:")
    print(f"Enhanced Preprocessing: {'✅ PASS' if preprocessing_ok else '❌ FAIL'}")
    print(f"Pipeline Integration: {'✅ PASS' if coordinator_ok else '❌ FAIL'}")

    if preprocessing_ok and coordinator_ok:
        print("\n🎉 All tests passed! Enhanced preprocessing is ready for integration.")
        print("\nNext steps:")
        print("1. Run pipeline coordinator to trigger data download")
        print("2. Enhanced preprocessing will clean the CSV data")
        print("3. Clean data will be uploaded to database")
        print("4. ML training will use improved data quality")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        sys.exit(1)
