#!/usr/bin/env python3
"""
File Watcher Service Runner
Starts the file watcher service for continuous monitoring
"""

import sys
import signal
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.automation.file_watcher_enhanced import FileWatcherManager

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down file watcher...")
    sys.exit(0)


def main():
    """Main service runner"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("🚀 Starting File Watcher Service")
    logger.info("📁 Monitoring: data/daily_downloads/manual_download/")
    logger.info("🔄 Auto-processing: ZIP files → data extraction → pipeline trigger")
    logger.info("🛑 Press Ctrl+C to stop")

    try:
        manager = FileWatcherManager()

        # Process any existing files first
        import asyncio

        asyncio.run(manager.process_existing_files())

        # Start continuous monitoring
        manager.start_watching()

    except KeyboardInterrupt:
        logger.info("🛑 File watcher service stopped by user")
    except Exception as e:
        logger.error(f"❌ File watcher service failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
