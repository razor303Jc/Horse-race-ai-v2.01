#!/usr/bin/env python3
"""
🚀 Racing Data Pipeline Automation
=================================

Complete automation system that integrates file watching, CSV processing,
and database upload in the correct order for the horse racing AI system.

Features:
- File watcher integration with enhanced pipeline
- Automated CSV mapping and validation
- Docker-based database uploads
- Comprehensive error handling and logging
- Step-by-step pipeline orchestration

Usage:
    python tools/automation/pipeline_automation.py --start-watcher
    python tools/automation/pipeline_automation.py --process-existing
    python tools/automation/pipeline_automation.py --run-pipeline
"""

import argparse
import asyncio
import logging
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
logger = logging.getLogger(__name__)


class PipelineAutomation:
    """Main pipeline automation coordinator"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.04"):
        self.base_path = Path(base_path)
        self.setup_logging()

    def setup_logging(self):
        """Setup comprehensive logging"""
        logs_dir = self.base_path / "logs"
        logs_dir.mkdir(exist_ok=True)

        log_file = logs_dir / "pipeline_automation.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(str(log_file)), logging.StreamHandler()],
        )

        logger.info("🚀 Pipeline automation initialized")

    async def start_file_watcher(self):
        """Start the enhanced file watcher service"""
        try:
            console.print(
                Panel.fit(
                    "🔍 Starting Enhanced File Watcher Service\n\n"
                    "• Monitors: data/daily_downloads/manual_download/\n"
                    "• Extracts: ZIP files automatically\n"
                    "• Triggers: Complete data pipeline\n"
                    "• Uploads: All data to database\n\n"
                    "Drop your ZIP files and watch the magic happen! ✨",
                    title="File Watcher Service",
                    border_style="green",
                )
            )

            # Import and start the enhanced file watcher
            sys.path.append(str(self.base_path / "tools/automation"))
            from file_watcher_enhanced import FileWatcherManager

            watcher_manager = FileWatcherManager(str(self.base_path))

            # Process any existing files first
            logger.info("🔍 Processing any existing ZIP files...")
            await watcher_manager.process_existing_files()

            # Start the watcher service
            logger.info("🔄 Starting file watcher service...")
            watcher_manager.start_watching()

            logger.info("✅ File watcher service started successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start file watcher: {e}")
            return False

    async def process_existing_files(self):
        """Process any existing ZIP files in manual_download"""
        try:
            console.print(
                Panel.fit(
                    "📁 Processing Existing ZIP Files\n\n"
                    "• Scans: manual_download directory\n"
                    "• Extracts: All ZIP files found\n"
                    "• Validates: Data integrity\n"
                    "• Triggers: Complete pipeline\n\n"
                    "Processing your existing data...",
                    title="Existing File Processing",
                    border_style="blue",
                )
            )

            # Import enhanced file watcher
            sys.path.append(str(self.base_path / "tools/automation"))
            from file_watcher_enhanced import FileWatcherManager

            watcher_manager = FileWatcherManager(str(self.base_path))
            await watcher_manager.process_existing_files()

            logger.info("✅ Existing files processed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to process existing files: {e}")
            return False

    async def run_complete_pipeline(self):
        """Execute the complete data processing pipeline manually"""
        try:
            console.print(
                Panel.fit(
                    "⚙️ Running Complete Data Pipeline\n\n"
                    "Step 1: CSV Mapping & Validation\n"
                    "Step 2: Database Upload via Docker\n"
                    "Step 3: ML Model Update Trigger\n\n"
                    "Processing all racing data...",
                    title="Pipeline Execution",
                    border_style="yellow",
                )
            )

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:

                # Step 1: CSV Mapping
                task1 = progress.add_task("🗂️ Processing CSV files...", total=None)
                csv_result = await self._run_csv_mapper()
                progress.update(task1, completed=True)

                if not csv_result:
                    console.print("❌ CSV processing failed")
                    return False

                # Step 2: Database Upload
                task2 = progress.add_task("🗄️ Uploading to database...", total=None)
                upload_result = await self._run_database_upload()
                progress.update(task2, completed=True)

                if not upload_result:
                    console.print("❌ Database upload failed")
                    return False

                # Step 3: ML Updates
                task3 = progress.add_task("🤖 Updating ML models...", total=None)
                await self._trigger_ml_updates()
                progress.update(task3, completed=True)

            console.print("\n✅ Complete pipeline executed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Pipeline execution failed: {e}")
            return False

    async def _run_csv_mapper(self):
        """Execute the advanced CSV mapper"""
        try:
            mapper_script = (
                self.base_path / "tools/data_processing/advanced_csv_mapper.py"
            )

            if not mapper_script.exists():
                logger.error(f"CSV mapper script not found: {mapper_script}")
                return False

            logger.info("🔄 Executing advanced CSV mapper...")
            process = subprocess.run(
                [sys.executable, str(mapper_script)],
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )

            if process.returncode == 0:
                logger.info("✅ CSV mapping completed successfully")
                return True
            else:
                logger.error(f"❌ CSV mapping failed with code {process.returncode}")
                logger.error(f"Error: {process.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ CSV mapping timed out")
            return False
        except Exception as e:
            logger.error(f"❌ CSV mapping execution failed: {e}")
            return False

    async def _run_database_upload(self):
        """Execute the database uploader using Docker"""
        try:
            logger.info("🐳 Executing database uploader via Docker...")

            docker_command = [
                "docker",
                "run",
                "--rm",
                "--network",
                "horse_racing_network",
                "-v",
                f"{self.base_path}:/app",
                "-e",
                "DB_HOST=horse_racing_postgres_clean",
                "-e",
                "DB_PORT=5432",
                "-e",
                "DB_NAME=horse_racing_db",
                "-e",
                "DB_USER=horse_racing",
                "-e",
                "DB_PASSWORD=secure_password_123",
                "horse-racing-ai_data-pipeline",
                "python",
                "/app/tools/data_processing/simple_database_uploader.py",
            ]

            process = subprocess.run(
                docker_command,
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )

            if process.returncode == 0:
                logger.info("✅ Database upload completed successfully")
                return True
            else:
                logger.error(
                    f"❌ Database upload failed with code {process.returncode}"
                )
                logger.error(f"Error: {process.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Database upload timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Database upload execution failed: {e}")
            return False

    async def _trigger_ml_updates(self):
        """Trigger ML model updates"""
        try:
            logger.info("🤖 ML model update trigger - ready for implementation")
            # Placeholder for ML model retraining
            # Future: Trigger model retraining, update APIs, etc.
            return True
        except Exception as e:
            logger.error(f"❌ ML update trigger failed: {e}")
            return False

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "base_path": str(self.base_path),
            "manual_download_path": str(
                self.base_path / "data/daily_downloads/manual_download"
            ),
            "csv_mapper_available": (
                self.base_path / "tools/data_processing/advanced_csv_mapper.py"
            ).exists(),
            "database_uploader_available": (
                self.base_path / "tools/data_processing/database_uploader.py"
            ).exists(),
        }

        # Check for existing ZIP files
        manual_dir = self.base_path / "data/daily_downloads/manual_download"
        if manual_dir.exists():
            zip_files = list(manual_dir.glob("*.zip"))
            status["pending_zip_files"] = len(zip_files)
            status["zip_files"] = [f.name for f in zip_files]
        else:
            status["pending_zip_files"] = 0
            status["zip_files"] = []

        return status


async def main():
    """Main entry point with CLI arguments"""
    parser = argparse.ArgumentParser(description="Racing Data Pipeline Automation")
    parser.add_argument(
        "--start-watcher", action="store_true", help="Start the file watcher service"
    )
    parser.add_argument(
        "--process-existing", action="store_true", help="Process existing ZIP files"
    )
    parser.add_argument(
        "--run-pipeline", action="store_true", help="Run the complete pipeline manually"
    )
    parser.add_argument("--status", action="store_true", help="Show pipeline status")
    parser.add_argument(
        "--base-path",
        type=str,
        default="/home/jc/Documents/Horse-race-ai-v2.04",
        help="Base path for the project",
    )

    args = parser.parse_args()

    automation = PipelineAutomation(args.base_path)

    if args.status:
        status = automation.get_pipeline_status()
        console.print(
            Panel.fit(
                f"📊 Pipeline Status\n\n"
                f"• Base Path: {status['base_path']}\n"
                f"• CSV Mapper: {'✅' if status['csv_mapper_available'] else '❌'}\n"
                f"• Database Uploader: {'✅' if status['database_uploader_available'] else '❌'}\n"
                f"• Pending ZIP Files: {status['pending_zip_files']}\n"
                f"• Files: {', '.join(status['zip_files']) if status['zip_files'] else 'None'}\n\n"
                f"Last Updated: {status['timestamp']}",
                title="Pipeline Status",
                border_style="cyan",
            )
        )
        return

    if args.start_watcher:
        await automation.start_file_watcher()
    elif args.process_existing:
        await automation.process_existing_files()
    elif args.run_pipeline:
        await automation.run_complete_pipeline()
    else:
        console.print(
            Panel.fit(
                "🚀 Racing Data Pipeline Automation\n\n"
                "Available commands:\n"
                "• --start-watcher    : Start file watcher service\n"
                "• --process-existing : Process existing ZIP files\n"
                "• --run-pipeline     : Run complete pipeline manually\n"
                "• --status          : Show pipeline status\n\n"
                "Example: python pipeline_automation.py --start-watcher",
                title="Pipeline Automation Help",
                border_style="blue",
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
