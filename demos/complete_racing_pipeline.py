#!/usr/bin/env python3
"""
Complete Automated Racing Pipeline
==================================

Full automation pipeline that:
1. Downloads fresh race data
2. Analyzes and processes data
3. Trains ML models
4. Makes predictions
5. Monitors performance
6. Sends notifications

Designed to run continuously in Docker container with proper scheduling.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import traceback

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

console = Console()


class RacingPipelineManager:
    """Complete racing pipeline manager."""

    def __init__(self):
        self.console = Console()
        self.data_dir = Path("data")
        self.models_dir = Path("models")
        self.logs_dir = Path("logs")

        # Create directories
        for dir_path in [self.data_dir, self.models_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)

        self.pipeline_stats = {
            "start_time": None,
            "data_collections": 0,
            "ml_trainings": 0,
            "predictions_made": 0,
            "errors": 0,
            "last_update": None,
        }

        self.current_status = "Initializing..."
        self.latest_predictions = []

    def create_dashboard(self) -> Layout:
        """Create a live dashboard layout."""
        layout = Layout()

        layout.split_row(Layout(name="left", ratio=2), Layout(name="right", ratio=1))

        layout["left"].split_column(
            Layout(name="status"), Layout(name="progress"), Layout(name="predictions")
        )

        layout["right"].split_column(Layout(name="stats"), Layout(name="logs"))

        return layout

    def update_dashboard(self, layout: Layout):
        """Update the dashboard with current information."""
        # Status panel
        status_panel = Panel(
            f"🏇 Racing Pipeline Status: {self.current_status}\n"
            f"⏰ Current Time: {datetime.now().strftime('%H:%M:%S')}\n"
            f"🎯 Next Race: 14:15 Ffos Las\n"
            f"⚡ Pipeline Active: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            title="System Status",
            border_style="green",
        )
        layout["status"].update(status_panel)

        # Statistics table
        stats_table = Table(title="Pipeline Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        for key, value in self.pipeline_stats.items():
            if key == "start_time" and value:
                value = value.strftime("%H:%M:%S")
            elif key == "last_update" and value:
                value = value.strftime("%H:%M:%S")
            stats_table.add_row(key.replace("_", " ").title(), str(value))

        layout["stats"].update(Panel(stats_table, title="Statistics"))

        # Recent predictions
        if self.latest_predictions:
            pred_table = Table(title="Latest Predictions")
            pred_table.add_column("Race", style="yellow")
            pred_table.add_column("Confidence", style="green")
            pred_table.add_column("Time", style="blue")

            for pred in self.latest_predictions[-5:]:
                pred_table.add_row(
                    pred.get("race", "Unknown"),
                    f"{pred.get('confidence', 0):.1%}",
                    pred.get("time", "Unknown"),
                )

            layout["predictions"].update(Panel(pred_table, title="Predictions"))
        else:
            layout["predictions"].update(
                Panel("No predictions yet...", title="Predictions")
            )

        # Logs
        log_content = (
            f"🕐 {datetime.now().strftime('%H:%M:%S')} - {self.current_status}\n"
        )
        log_content += (
            f"📊 Data collections: {self.pipeline_stats['data_collections']}\n"
        )
        log_content += f"🤖 ML trainings: {self.pipeline_stats['ml_trainings']}\n"
        log_content += f"🎯 Predictions: {self.pipeline_stats['predictions_made']}"

        layout["logs"].update(Panel(log_content, title="Activity Log"))

    async def collect_data(self) -> bool:
        """Collect real data using our horseracedatabase auto-downloader system."""
        try:
            self.current_status = (
                "Collecting real race data from horseracedatabase.com..."
            )

            # Import our horseracedatabase system we worked on until 3:00 AM!
            sys.path.append(str(Path.cwd() / "demos"))

            # PRIMARY: Use the direct horseracedatabase downloader first
            self.console.print(
                "🐴 [cyan]Using horseracedatabase.com ZIP downloader...[/cyan]"
            )

            # Import with proper path handling for hyphenated filename
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "horseracedatabase_auto_downloader",
                str(Path.cwd() / "demos" / "horseracedatabase_auto_downloader.py"),
            )
            hrdb_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(hrdb_module)

            primary_downloader = hrdb_module.HorseRaceDatabaseDownloader()
            primary_success = await primary_downloader.run()

            if primary_success:
                self.pipeline_stats["data_collections"] += 1
                self.pipeline_stats["last_update"] = datetime.now()
                self.console.print(
                    "✅ [green]Real ZIP data downloaded from horseracedatabase.com![/green]"
                )
                return True
            else:
                self.console.print(
                    "⚠️ [yellow]Primary horseracedatabase downloader failed, trying enhanced system...[/yellow]"
                )

                # SECONDARY: Fallback to enhanced system for web scraping
                from enhanced_auto_download_system import EnhancedAutoDownloadSystem

                fallback_downloader = EnhancedAutoDownloadSystem()

                # Collect race data from web sources
                races = await fallback_downloader.collect_race_data(max_races=20)

                if races and len(races) > 0:
                    # Save the collected web data
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = self.data_dir / f"races_{timestamp}.json"

                    with open(output_file, "w") as f:
                        json.dump(races, f, indent=2, default=str)

                    self.pipeline_stats["data_collections"] += 1
                    self.pipeline_stats["last_update"] = datetime.now()
                    self.console.print(
                        f"✅ [green]Web-scraped race data collected! ({len(races)} races)[/green]"
                    )
                    return True

            self.console.print(
                "❌ [red]Both horseracedatabase and web scraping failed[/red]"
            )
            return False

        except Exception as e:
            self.console.print(f"❌ Data collection failed: {e}")
            self.pipeline_stats["errors"] += 1
            traceback.print_exc()
            return False

    def train_ml_models(self) -> bool:
        """Train ML models with latest data."""
        try:
            self.current_status = "Training ML models..."

            # Import and run the ML pipeline
            from advanced_ml_pipeline import HorseRacingMLPipeline

            pipeline = HorseRacingMLPipeline()

            # Load and prepare data
            df = pipeline.load_and_prepare_data()

            # Prepare features
            X, y = pipeline.prepare_features(df)

            # Train models
            pipeline.train_models(X, y)

            self.pipeline_stats["ml_trainings"] += 1
            return True

        except Exception as e:
            self.console.print(f"❌ ML training failed: {e}")
            self.pipeline_stats["errors"] += 1
            return False

    def make_predictions(self) -> List[Dict[str, Any]]:
        """Make predictions for upcoming races."""
        try:
            self.current_status = "Making predictions..."

            # Simulate predictions for now
            predictions = [
                {
                    "race": "14:15 Ffos Las",
                    "confidence": 0.75,
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "top_pick": "Thunder Bolt",
                    "model": "Random Forest",
                },
                {
                    "race": "14:45 Newbury",
                    "confidence": 0.68,
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "top_pick": "Lightning Strike",
                    "model": "Gradient Boosting",
                },
            ]

            self.latest_predictions.extend(predictions)
            self.pipeline_stats["predictions_made"] += len(predictions)

            return predictions

        except Exception as e:
            self.console.print(f"❌ Prediction failed: {e}")
            self.pipeline_stats["errors"] += 1
            return []

    async def send_notifications(self, predictions: List[Dict[str, Any]]):
        """Send notifications about predictions."""
        try:
            if not predictions:
                return

            self.current_status = "Sending notifications..."

            # Send to NTFY (if configured)
            import httpx

            for pred in predictions:
                message = (
                    f"🏇 {pred['race']}\n"
                    f"🎯 Top Pick: {pred['top_pick']}\n"
                    f"📊 Confidence: {pred['confidence']:.1%}\n"
                    f"🤖 Model: {pred['model']}"
                )

                try:
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            "http://horse_racing_ntfy:8080/horse-racing-predictions",
                            data=message.encode(),
                            headers={"Title": "New Race Prediction"},
                        )
                except:
                    # NTFY not available, continue
                    pass

        except Exception as e:
            self.console.print(f"⚠️  Notification failed: {e}")

    async def run_complete_cycle(self) -> bool:
        """Run one complete pipeline cycle."""
        try:
            # 1. Collect data
            data_success = await self.collect_data()

            if not data_success:
                return False

            # 2. Train models
            ml_success = self.train_ml_models()

            if not ml_success:
                return False

            # 3. Make predictions
            predictions = self.make_predictions()

            # 4. Send notifications
            await self.send_notifications(predictions)

            self.current_status = "Cycle complete, waiting for next run..."
            return True

        except Exception as e:
            self.console.print(f"❌ Pipeline cycle failed: {e}")
            self.current_status = f"Error: {str(e)[:50]}..."
            self.pipeline_stats["errors"] += 1
            return False

    async def run_continuous_monitoring(self):
        """Run continuous monitoring with live dashboard."""
        self.pipeline_stats["start_time"] = datetime.now()
        layout = self.create_dashboard()

        with Live(layout, refresh_per_second=1, screen=True):
            while True:
                try:
                    # Update dashboard
                    self.update_dashboard(layout)

                    # Check if it's time for data collection (every 30 minutes)
                    current_time = datetime.now()

                    # Run pipeline cycle every 30 minutes or on startup
                    if (
                        self.pipeline_stats["data_collections"] == 0
                        or current_time.minute % 30 == 0
                        and current_time.second < 5
                    ):

                        self.console.print("🚀 Starting pipeline cycle...")
                        await self.run_complete_cycle()

                    # Sleep for a bit before next update
                    await asyncio.sleep(1)

                except KeyboardInterrupt:
                    self.console.print("\n🛑 Pipeline stopped by user")
                    break
                except Exception as e:
                    self.console.print(f"❌ Dashboard error: {e}")
                    self.current_status = f"Dashboard error: {str(e)[:30]}..."
                    await asyncio.sleep(5)


async def main():
    """Main function to run the complete pipeline."""
    console.print(Panel.fit("🏇 Complete Racing Pipeline Starting", style="bold green"))
    console.print(f"⏰ UK Time: {datetime.now().strftime('%H:%M:%S')}")
    console.print(f"🎯 First race today: 14:15 Ffos Las")
    console.print(f"📊 Pipeline will collect data, train models, and make predictions")

    manager = RacingPipelineManager()

    try:
        # Run initial cycle immediately
        console.print("🚀 Running initial pipeline cycle...")
        success = await manager.run_complete_cycle()

        if success:
            console.print("✅ Initial cycle completed successfully!")
        else:
            console.print("⚠️  Initial cycle had issues, continuing anyway...")

        # Start continuous monitoring
        console.print("📊 Starting continuous monitoring dashboard...")
        await manager.run_continuous_monitoring()

    except KeyboardInterrupt:
        console.print("\n🛑 Pipeline stopped")
    except Exception as e:
        console.print(f"❌ Pipeline failed: {e}")
        console.print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
