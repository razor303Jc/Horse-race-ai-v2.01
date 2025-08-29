#!/usr/bin/env python3
"""
Test File Watcher Service
Tests the file watcher to ensure it's ready for continuous operation.
"""

import sys
import os
import subprocess
import time
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_file_watcher_status():
    """Test if the file watcher service is ready."""
    logger.info("🔍 Testing file watcher service status...")

    # Check if manual_download directory exists
    manual_download_dir = project_root / "manual_download"
    if not manual_download_dir.exists():
        logger.info(f"📁 Creating manual_download directory: {manual_download_dir}")
        manual_download_dir.mkdir(exist_ok=True)

    logger.info(f"✅ Manual download directory ready: {manual_download_dir}")

    # Check pipeline automation script
    pipeline_script = project_root / "tools" / "automation" / "pipeline_automation.py"
    if not pipeline_script.exists():
        logger.error(f"❌ Pipeline automation script not found: {pipeline_script}")
        return False

    logger.info(f"✅ Pipeline automation script ready: {pipeline_script}")

    # Check file watcher script
    watcher_script = project_root / "tools" / "automation" / "file_watcher_enhanced.py"
    if not watcher_script.exists():
        logger.error(f"❌ File watcher script not found: {watcher_script}")
        return False

    logger.info(f"✅ File watcher script ready: {watcher_script}")

    # Check Docker containers
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info("🐳 Docker containers status:")
        logger.info(result.stdout)

        if "horse_racing_postgres_clean" not in result.stdout:
            logger.error("❌ PostgreSQL container not running")
            return False

        logger.info("✅ PostgreSQL container is running")

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error checking Docker containers: {e}")
        return False

    return True


def test_pipeline_execution():
    """Test a quick pipeline execution."""
    logger.info("🚀 Testing pipeline execution...")

    try:
        # Change to project directory
        os.chdir(project_root)

        # Run the pipeline
        result = subprocess.run(
            [
                sys.executable,
                "tools/automation/pipeline_automation.py",
                "--run-pipeline",
            ],
            capture_output=True,
            text=True,
            timeout=60,  # 1 minute timeout
        )

        if result.returncode == 0:
            logger.info("✅ Pipeline test execution successful")
            return True
        else:
            logger.error(f"❌ Pipeline test failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("❌ Pipeline test timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Pipeline test error: {e}")
        return False


def show_watcher_commands():
    """Show commands to start the file watcher."""
    logger.info(
        """
╭────────────────────────────────────────╮
│          File Watcher Ready!           │
│                                        │
│ 🎯 To start continuous monitoring:     │
│                                        │
│ python tools/automation/pipeline_automation.py --start-watcher │
│                                        │
│ 📁 Drop ZIP files in: manual_download/ │
│                                        │
│ 🔄 Pipeline will automatically:        │
│ • Detect new ZIP files                 │
│ • Extract and validate data            │
│ • Map CSV columns                      │
│ • Upload to database                   │
│ • Update ML models                     │
│                                        │
│ 📊 Monitor progress in logs            │
╰────────────────────────────────────────╯
    """
    )


def main():
    """Main test function."""
    logger.info("🧪 Starting file watcher service test...")

    # Test file watcher status
    if not test_file_watcher_status():
        logger.error("❌ File watcher service test failed")
        return 1

    # Test pipeline execution
    if not test_pipeline_execution():
        logger.error("❌ Pipeline execution test failed")
        return 1

    logger.info("✅ All tests passed! File watcher service is ready.")
    show_watcher_commands()

    return 0


if __name__ == "__main__":
    sys.exit(main())
