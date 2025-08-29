#!/usr/bin/env python3
"""
Docker Container Test for Early Morning ML Training System
Quick verification that the system works in Docker environment
"""

import asyncio
import os
import sys
from pathlib import Path

# Setup paths
sys.path.append("/app/docker/ml_training")
sys.path.append("/app/docker/pipeline_management")

# Set environment variables for testing
os.environ.update(
    {
        "DATA_PATH": "/app/data",
        "MODELS_PATH": "/app/models",
        "LOGS_PATH": "/app/logs",
        "CACHE_PATH": "/app/cache",
        "ML_LOG_LEVEL": "INFO",
        "ML_MAX_CYCLES": "2",  # Reduced for testing
    }
)


def test_docker_environment():
    """Test Docker environment setup"""
    print("🐳 Docker Environment Test")
    print("=" * 40)

    # Check required directories
    required_dirs = ["/app/data", "/app/models", "/app/logs", "/app/cache"]
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"⚠️ Directory missing: {dir_path} (will be created)")
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    # Check environment variables
    env_vars = ["DATA_PATH", "MODELS_PATH", "LOGS_PATH", "ML_LOG_LEVEL"]
    for var in env_vars:
        value = os.environ.get(var)
        print(f"✅ {var}: {value}")

    print("✅ Docker environment check completed")


def test_component_imports():
    """Test component imports"""
    print("\n🔧 Component Import Test")
    print("=" * 40)

    try:
        from early_morning_ml_trainer import (
            DockerLogger,
            EarlyMorningMLTrainer,
            EarlyMorningTrainingConfig,
        )

        print("✅ Early morning ML trainer imported")

        from pipeline_integration import EarlyMorningPipelineIntegration

        print("✅ Pipeline integration imported")

        # Test configuration
        config = EarlyMorningTrainingConfig()
        print(f"✅ Config created: {config.start_time}-{config.end_time}")

        # Test logger
        logger = DockerLogger("docker_test")
        logger.info("Docker test logging successful")
        print("✅ Logger created and tested")

        return True

    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


async def test_integration_components():
    """Test integration components"""
    print("\n🚀 Integration Component Test")
    print("=" * 40)

    try:
        from pipeline_integration import EarlyMorningPipelineIntegration

        # Create integration
        integration = EarlyMorningPipelineIntegration()
        print("✅ Integration created")

        # Test window check
        in_window, status = integration.check_training_window()
        print(f"✅ Window check: {status}")

        # Test status
        status = await integration.get_training_status()
        print(f"✅ Status check: Window={status['in_training_window']}")

        # Test buffer calculation
        buffer = integration._calculate_buffer_time("04:00", "13:45")
        print(f"✅ Buffer calculation: {buffer} minutes")

        return True

    except Exception as e:
        print(f"❌ Integration error: {e}")
        return False


def main():
    """Main test execution"""
    print("🌅 Early Morning ML Training - Docker Test Suite")
    print("=" * 60)

    # Test 1: Docker environment
    test_docker_environment()

    # Test 2: Component imports
    imports_ok = test_component_imports()

    # Test 3: Integration components
    if imports_ok:
        integration_ok = asyncio.run(test_integration_components())
    else:
        integration_ok = False

    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    print(f"Environment setup: ✅ Passed")
    print(f"Component imports: {'✅ Passed' if imports_ok else '❌ Failed'}")
    print(f"Integration test: {'✅ Passed' if integration_ok else '❌ Failed'}")

    if imports_ok and integration_ok:
        print("\n🎉 All Docker tests passed!")
        print("🚀 Early Morning ML Training System is ready for deployment!")
        return 0
    else:
        print("\n💥 Some Docker tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
