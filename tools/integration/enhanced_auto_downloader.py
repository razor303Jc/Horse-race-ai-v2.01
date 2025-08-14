#!/usr/bin/env python3
"""
Auto Downloader Enhanced Integration
===================================

Enhanced auto downloader that integrates with the daily downloads manager and database upload.
This script ties together the complete workflow:
1. Download data using working auto downloader
2. Run daily downloads manager for organization
3. Upload organized data to database
4. Generate comprehensive reports

Integrates with VS Code shell integration for enhanced terminal experience.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import our components
from tools.data_processing.daily_downloads_manager import DailyDownloadsManager
from tools.data_processing.enhanced_database_uploader import EnhancedDatabaseUploader

console = Console()
logger = logging.getLogger(__name__)


class EnhancedAutoDownloader:
    """Enhanced auto downloader with full pipeline integration"""

    def __init__(self):
        self.console = console
        self.today = datetime.now().date()
        self.data_dir = Path("data/daily_downloads")
        self.downloads_manager = DailyDownloadsManager()
        self.database_uploader = EnhancedDatabaseUploader()

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    async def run_complete_pipeline(self) -> Dict:
        """Run the complete download, organize, and upload pipeline"""
        console.print("\n🏇 [bold blue]Enhanced Horse Racing Data Pipeline[/bold blue]")
        console.print(f"📅 Date: {self.today}")

        pipeline_report = {
            "start_time": datetime.now().isoformat(),
            "date": self.today.isoformat(),
            "stages": {},
            "overall_success": False,
            "errors": [],
        }

        try:
            # Stage 1: Download data (using Docker container)
            await self._stage_download_data(pipeline_report)

            # Stage 2: Organize downloaded data
            await self._stage_organize_data(pipeline_report)

            # Stage 3: Upload to database
            await self._stage_upload_data(pipeline_report)

            # Stage 4: Generate final report
            await self._stage_generate_report(pipeline_report)

            pipeline_report["end_time"] = datetime.now().isoformat()
            pipeline_report["overall_success"] = all(
                stage.get("success", False)
                for stage in pipeline_report["stages"].values()
            )

            self._display_pipeline_report(pipeline_report)

            return pipeline_report

        except Exception as e:
            error_msg = f"Pipeline error: {e}"
            pipeline_report["errors"].append(error_msg)
            logger.error(error_msg)
            console.print(f"[red]❌ {error_msg}[/red]")
            return pipeline_report

    async def _stage_download_data(self, report: Dict):
        """Stage 1: Download data using Docker auto downloader"""
        console.print("\n📥 [cyan]Stage 1: Downloading Race Data[/cyan]")

        stage_report = {
            "start_time": datetime.now().isoformat(),
            "success": False,
            "actions": [],
            "errors": [],
        }

        try:
            # Check if Docker container is running
            import subprocess

            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=horserace-auto-downloader",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
            )

            if "horserace-auto-downloader" in result.stdout:
                console.print("✅ Auto-downloader container is running")

                # Trigger download
                download_result = subprocess.run(
                    [
                        "docker",
                        "exec",
                        "horserace-auto-downloader",
                        "python",
                        "/app/run_docker_auto_downloader.py",
                        "--mode",
                        "once",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if download_result.returncode == 0:
                    stage_report["success"] = True
                    stage_report["actions"].append(
                        "Successfully triggered auto-downloader"
                    )
                    console.print("✅ Data download completed")
                else:
                    error_msg = f"Download failed: {download_result.stderr}"
                    stage_report["errors"].append(error_msg)
                    console.print(f"[red]❌ {error_msg}[/red]")
            else:
                error_msg = "Auto-downloader container not running"
                stage_report["errors"].append(error_msg)
                console.print(f"[red]❌ {error_msg}[/red]")

        except Exception as e:
            error_msg = f"Download stage error: {e}"
            stage_report["errors"].append(error_msg)
            logger.error(error_msg)

        stage_report["end_time"] = datetime.now().isoformat()
        report["stages"]["download"] = stage_report

    async def _stage_organize_data(self, report: Dict):
        """Stage 2: Organize data using downloads manager"""
        console.print("\n🗂️ [cyan]Stage 2: Organizing Downloaded Data[/cyan]")

        stage_report = {
            "start_time": datetime.now().isoformat(),
            "success": False,
            "actions": [],
            "errors": [],
        }

        try:
            # Run the downloads manager
            organization_report = self.downloads_manager.run_daily_cleanup()

            if organization_report:
                stage_report["success"] = True
                stage_report["actions"].append(
                    f"Organized {organization_report.get('files_processed', 0)} files"
                )
                stage_report["actions"].append(
                    f"Created {organization_report.get('archives_created', 0)} archives"
                )
                stage_report["actions"].append(
                    f"Removed {organization_report.get('files_removed', 0)} old files"
                )
                console.print("✅ Data organization completed")
            else:
                error_msg = "Organization failed"
                stage_report["errors"].append(error_msg)
                console.print(f"[red]❌ {error_msg}[/red]")

        except Exception as e:
            error_msg = f"Organization stage error: {e}"
            stage_report["errors"].append(error_msg)
            logger.error(error_msg)

        stage_report["end_time"] = datetime.now().isoformat()
        report["stages"]["organize"] = stage_report

    async def _stage_upload_data(self, report: Dict):
        """Stage 3: Upload organized data to database"""
        console.print("\n💾 [cyan]Stage 3: Uploading to Database[/cyan]")

        stage_report = {
            "start_time": datetime.now().isoformat(),
            "success": False,
            "actions": [],
            "errors": [],
        }

        try:
            # Check for upload manifest or prepare one
            upload_files = self.downloads_manager.prepare_for_database_upload()

            if upload_files and any(upload_files.values()):
                # Create simple manifest for upload
                manifest = {"generated": datetime.now().isoformat(), "files": {}}

                for table_name, file_paths in upload_files.items():
                    for file_path in file_paths:
                        manifest["files"][str(file_path)] = {
                            "table": table_name,
                            "size": (
                                file_path.stat().st_size if file_path.exists() else 0
                            ),
                            "modified": (
                                datetime.fromtimestamp(
                                    file_path.stat().st_mtime
                                ).isoformat()
                                if file_path.exists()
                                else ""
                            ),
                        }

                # Save manifest temporarily
                temp_manifest = self.data_dir / "temp_upload_manifest.json"
                with open(temp_manifest, "w") as f:
                    json.dump(manifest, f, indent=2)

                # Run database upload
                upload_report = await self.database_uploader.upload_from_manifest(
                    str(temp_manifest)
                )

                if upload_report and upload_report.get("success", False):
                    stage_report["success"] = True
                    stage_report["actions"].append(
                        f"Uploaded {upload_report.get('tables_uploaded', 0)} tables"
                    )
                    stage_report["actions"].append(
                        f"Inserted {upload_report.get('total_records', 0)} records"
                    )
                    console.print("✅ Database upload completed")

                    # Clean up temp manifest
                    temp_manifest.unlink(missing_ok=True)
                else:
                    error_msg = (
                        f"Upload failed: {upload_report.get('error', 'Unknown error')}"
                    )
                    stage_report["errors"].append(error_msg)
                    console.print(f"[red]❌ {error_msg}[/red]")
            else:
                error_msg = "No files prepared for upload"
                stage_report["errors"].append(error_msg)
                console.print(f"[yellow]⚠️ {error_msg}[/yellow]")

        except Exception as e:
            error_msg = f"Upload stage error: {e}"
            stage_report["errors"].append(error_msg)
            logger.error(error_msg)

        stage_report["end_time"] = datetime.now().isoformat()
        report["stages"]["upload"] = stage_report

    async def _stage_generate_report(self, report: Dict):
        """Stage 4: Generate comprehensive pipeline report"""
        console.print("\n📊 [cyan]Stage 4: Generating Pipeline Report[/cyan]")

        stage_report = {
            "start_time": datetime.now().isoformat(),
            "success": False,
            "actions": [],
            "errors": [],
        }

        try:
            # Create comprehensive report
            report_file = Path(
                f"reports/pipeline_report_{self.today.strftime('%Y%m%d')}.json"
            )
            report_file.parent.mkdir(exist_ok=True)

            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            stage_report["success"] = True
            stage_report["actions"].append(f"Generated report: {report_file}")
            console.print(f"✅ Report saved to: {report_file}")

        except Exception as e:
            error_msg = f"Report generation error: {e}"
            stage_report["errors"].append(error_msg)
            logger.error(error_msg)

        stage_report["end_time"] = datetime.now().isoformat()
        report["stages"]["report"] = stage_report

    def _display_pipeline_report(self, report: Dict):
        """Display comprehensive pipeline report"""
        console.print("\n📈 [bold green]Pipeline Execution Report[/bold green]")

        # Calculate overall duration
        start_time = datetime.fromisoformat(report["start_time"])
        end_time = datetime.fromisoformat(report["end_time"])
        duration = (end_time - start_time).total_seconds()

        # Create summary table
        from rich.table import Table

        summary_table = Table(title="🎯 Pipeline Summary", show_header=True)
        summary_table.add_column("Stage", style="cyan")
        summary_table.add_column("Status", style="green")
        summary_table.add_column("Duration", style="yellow")
        summary_table.add_column("Actions", style="magenta")
        summary_table.add_column("Errors", style="red")

        for stage_name, stage_data in report["stages"].items():
            status = "✅ Success" if stage_data.get("success", False) else "❌ Failed"
            stage_start = datetime.fromisoformat(stage_data["start_time"])
            stage_end = datetime.fromisoformat(stage_data["end_time"])
            stage_duration = f"{(stage_end - stage_start).total_seconds():.2f}s"
            actions_count = len(stage_data.get("actions", []))
            errors_count = len(stage_data.get("errors", []))

            summary_table.add_row(
                stage_name.title(),
                status,
                stage_duration,
                str(actions_count),
                str(errors_count),
            )

        console.print(summary_table)

        # Overall status
        if report["overall_success"]:
            console.print(
                f"\n🎉 [bold green]Pipeline completed successfully in {duration:.2f}s[/bold green]"
            )
        else:
            console.print(
                f"\n⚠️ [bold yellow]Pipeline completed with issues in {duration:.2f}s[/bold yellow]"
            )

        # Show any errors
        all_errors = []
        for stage_data in report["stages"].values():
            all_errors.extend(stage_data.get("errors", []))

        if all_errors:
            console.print("\n❗ [bold red]Errors Encountered:[/bold red]")
            for error in all_errors:
                console.print(f"  • {error}")

    async def run_once(self) -> bool:
        """Run the complete pipeline once"""
        try:
            report = await self.run_complete_pipeline()
            return report["overall_success"]
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return False

    async def run_scheduled(self):
        """Run the pipeline on schedule"""
        import time

        import schedule

        # Schedule for dynamic time (from environment)
        download_time = os.getenv("DOWNLOAD_TIME", "06:01")
        schedule.every().day.at(download_time).do(lambda: asyncio.run(self.run_once()))

        console.print(f"📅 Scheduled enhanced pipeline for {download_time} daily")
        console.print("🔄 Waiting for scheduled time...")

        while True:
            schedule.run_pending()
            time.sleep(60)


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced Auto Downloader with Full Integration"
    )
    parser.add_argument(
        "--mode",
        choices=["once", "scheduled"],
        default="once",
        help="Run mode: 'once' for immediate run, 'scheduled' for daily schedule",
    )

    args = parser.parse_args()

    downloader = EnhancedAutoDownloader()

    if args.mode == "once":
        success = await downloader.run_once()
        sys.exit(0 if success else 1)
    else:
        await downloader.run_scheduled()


if __name__ == "__main__":
    asyncio.run(main())
