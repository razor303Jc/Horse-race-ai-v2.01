#!/usr/bin/env python3
"""
Real Data Integration Manager
=============================

Manages the gradual integration of real racing data with synthetic data,
ensuring seamless operation with existing training and analysis systems.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)


class RealDataIntegrationManager:
    """Manages integration of real racing data with existing systems."""

    def __init__(self):
        """Initialize the integration manager."""
        self.console = console

        # Data directories
        self.data_dir = Path("data")
        self.real_data_dir = self.data_dir / "real_racing_data"
        self.backup_dir = self.data_dir / "backup_data"
        self.integration_logs_dir = self.data_dir / "integration_logs"

        # Create directories
        for directory in [
            self.real_data_dir,
            self.backup_dir,
            self.integration_logs_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        # Integration settings
        self.integration_config = {
            "real_data_percentage": 0.0,
            "target_percentage": 100.0,
            "integration_step": 10.0,
            "quality_threshold": 0.8,
            "backup_count": 5,
            "validation_enabled": True,
        }

        # Load existing config if available
        self._load_integration_config()

        # Integration statistics
        self.integration_stats = {
            "total_integrations": 0,
            "successful_integrations": 0,
            "failed_integrations": 0,
            "real_races_integrated": 0,
            "synthetic_races_remaining": 0,
            "last_integration": None,
            "data_quality_score": 0.0,
            "integration_history": [],
        }

        logger.info("Initialized Real Data Integration Manager")

    def _load_integration_config(self):
        """Load integration configuration from file."""
        config_file = self.data_dir / "integration_config.json"

        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    saved_config = json.load(f)
                    self.integration_config.update(saved_config)
                self.console.print("✅ Loaded integration configuration")
            except Exception as e:
                logger.warning(f"Failed to load integration config: {e}")

    def _save_integration_config(self):
        """Save integration configuration to file."""
        config_file = self.data_dir / "integration_config.json"

        try:
            with open(config_file, "w") as f:
                json.dump(self.integration_config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save integration config: {e}")

    async def validate_real_data(
        self, real_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate real racing data quality."""
        self.console.print("🔍 Validating real data quality...")

        validation_results = {
            "total_races": len(real_data),
            "valid_races": 0,
            "invalid_races": 0,
            "quality_score": 0.0,
            "issues": [],
            "detailed_results": [],
        }

        for i, race in enumerate(real_data):
            race_validation = self._validate_single_race(race, i)
            validation_results["detailed_results"].append(race_validation)

            if race_validation["is_valid"]:
                validation_results["valid_races"] += 1
            else:
                validation_results["invalid_races"] += 1
                validation_results["issues"].extend(race_validation["issues"])

        # Calculate overall quality score
        if validation_results["total_races"] > 0:
            validation_results["quality_score"] = (
                validation_results["valid_races"] / validation_results["total_races"]
            )

        self.console.print(
            f"📊 Data validation complete: {validation_results['quality_score']:.2%} quality"
        )

        return validation_results

    def _validate_single_race(self, race: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate a single race data structure."""

        validation = {
            "race_index": index,
            "is_valid": True,
            "issues": [],
            "warnings": [],
        }

        # Required fields
        required_fields = ["race_id", "track", "horses", "betting_odds"]

        for field in required_fields:
            if field not in race:
                validation["is_valid"] = False
                validation["issues"].append(f"Missing required field: {field}")

        # Validate horses data
        if "horses" in race:
            horses = race["horses"]

            if len(horses) < 3:
                validation["is_valid"] = False
                validation["issues"].append(
                    f"Too few horses: {len(horses)} (minimum 3)"
                )
            elif len(horses) > 20:
                validation["warnings"].append(f"Many horses: {len(horses)}")

            # Validate individual horses
            for horse in horses:
                if not isinstance(horse, dict):
                    validation["is_valid"] = False
                    validation["issues"].append("Invalid horse data structure")
                    continue

                if "name" not in horse:
                    validation["is_valid"] = False
                    validation["issues"].append("Horse missing name")

                if "recent_runs" in horse:
                    runs = horse["recent_runs"]
                    if len(runs) == 0:
                        validation["warnings"].append(
                            f"Horse {horse.get('name', 'unknown')} has no recent runs"
                        )

        # Validate betting odds
        if "betting_odds" in race:
            odds = race["betting_odds"]

            if not isinstance(odds, dict):
                validation["is_valid"] = False
                validation["issues"].append("Invalid betting odds structure")
            elif len(odds) == 0:
                validation["warnings"].append("No betting odds available")

        return validation

    async def create_integration_backup(self, backup_name: Optional[str] = None) -> str:
        """Create backup of current data before integration."""

        if backup_name is None:
            backup_name = f"pre_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        backup_dir = self.backup_dir / backup_name
        backup_dir.mkdir(exist_ok=True)

        # Files to backup
        files_to_backup = [
            "massive_test_race_cards.json",
            "massive_training_data.csv",
            "integration_config.json",
        ]

        backed_up_files = []

        for filename in files_to_backup:
            source_file = self.data_dir / filename

            if source_file.exists():
                backup_file = backup_dir / filename

                try:
                    # Copy file content
                    with open(source_file, "r") as src, open(backup_file, "w") as dst:
                        dst.write(src.read())

                    backed_up_files.append(filename)

                except Exception as e:
                    logger.warning(f"Failed to backup {filename}: {e}")

        # Create backup manifest
        manifest = {
            "backup_name": backup_name,
            "created_at": datetime.now().isoformat(),
            "files": backed_up_files,
            "integration_config": self.integration_config.copy(),
        }

        manifest_file = backup_dir / "backup_manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)

        self.console.print(f"💾 Created backup: {backup_name}")

        return str(backup_dir)

    async def integrate_real_data_gradual(
        self, real_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Gradually integrate real data with existing synthetic data."""

        self.console.print(
            Panel.fit(
                "[bold green]🔄 GRADUAL DATA INTEGRATION[/bold green]\n"
                "[white]Merging real racing data with synthetic training data[/white]",
                border_style="green",
            )
        )

        self.integration_stats["total_integrations"] += 1

        try:
            # Initialize validation results
            validation_results = {"quality_score": 1.0}

            # Validate real data first
            if self.integration_config["validation_enabled"]:
                validation_results = await self.validate_real_data(real_data)

                if (
                    validation_results["quality_score"]
                    < self.integration_config["quality_threshold"]
                ):
                    self.console.print(
                        f"❌ Real data quality too low: {validation_results['quality_score']:.2%}"
                    )
                    self.integration_stats["failed_integrations"] += 1
                    return {
                        "status": "failed",
                        "reason": "Data quality below threshold",
                        "quality_score": validation_results["quality_score"],
                    }

            # Create backup
            backup_path = await self.create_integration_backup()

            # Load existing synthetic data
            synthetic_file = self.data_dir / "massive_test_race_cards.json"

            if not synthetic_file.exists():
                self.console.print("❌ No existing synthetic data found")
                return {"status": "failed", "reason": "No synthetic data found"}

            with open(synthetic_file, "r") as f:
                synthetic_data = json.load(f)

            # Calculate integration amounts
            total_races = len(synthetic_data)
            current_percentage = self.integration_config["real_data_percentage"]
            new_percentage = min(
                current_percentage + self.integration_config["integration_step"],
                self.integration_config["target_percentage"],
            )

            real_races_to_include = int(total_races * (new_percentage / 100))
            real_races_available = len(real_data)

            # Adjust if not enough real data
            if real_races_to_include > real_races_available:
                real_races_to_include = real_races_available
                actual_percentage = (real_races_to_include / total_races) * 100
            else:
                actual_percentage = new_percentage

            # Create integrated dataset
            integrated_data = []

            # Add real data (converted to synthetic format)
            for i in range(real_races_to_include):
                converted_race = self._convert_real_to_training_format(real_data[i])
                integrated_data.append(converted_race)

            # Add remaining synthetic data
            synthetic_races_to_include = total_races - real_races_to_include
            integrated_data.extend(synthetic_data[:synthetic_races_to_include])

            # Shuffle to mix real and synthetic data
            import random

            random.shuffle(integrated_data)

            # Save integrated data
            integration_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            integrated_file = (
                self.data_dir / f"integrated_race_cards_{integration_timestamp}.json"
            )

            with open(integrated_file, "w") as f:
                json.dump(integrated_data, f, indent=2)

            # Update main data file
            with open(synthetic_file, "w") as f:
                json.dump(integrated_data, f, indent=2)

            # Update configuration
            self.integration_config["real_data_percentage"] = actual_percentage
            self._save_integration_config()

            # Update statistics
            self.integration_stats["successful_integrations"] += 1
            self.integration_stats["real_races_integrated"] += real_races_to_include
            self.integration_stats["synthetic_races_remaining"] = (
                synthetic_races_to_include
            )
            self.integration_stats["last_integration"] = datetime.now()
            self.integration_stats["data_quality_score"] = validation_results.get(
                "quality_score", 1.0
            )

            # Add to integration history
            integration_record = {
                "timestamp": datetime.now().isoformat(),
                "real_races_added": real_races_to_include,
                "synthetic_races_remaining": synthetic_races_to_include,
                "real_data_percentage": actual_percentage,
                "backup_path": backup_path,
                "quality_score": validation_results.get("quality_score", 1.0),
            }

            self.integration_stats["integration_history"].append(integration_record)

            # Keep only last 10 history records
            if len(self.integration_stats["integration_history"]) > 10:
                self.integration_stats["integration_history"] = self.integration_stats[
                    "integration_history"
                ][-10:]

            # Log integration details
            await self._log_integration_details(integration_record)

            result = {
                "status": "success",
                "total_races": len(integrated_data),
                "real_races": real_races_to_include,
                "synthetic_races": synthetic_races_to_include,
                "real_data_percentage": actual_percentage,
                "previous_percentage": current_percentage,
                "backup_path": backup_path,
                "integrated_file": str(integrated_file),
            }

            self.console.print(
                f"✅ Integration successful: {actual_percentage:.1f}% real data"
            )

            return result

        except Exception as e:
            logger.error(f"Integration failed: {e}")
            self.integration_stats["failed_integrations"] += 1
            return {"status": "failed", "reason": str(e)}

    def _convert_real_to_training_format(
        self, real_race: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert real race data to training data format."""

        # Extract and convert horses data
        horses_data = {}
        betting_odds = {}

        for horse in real_race.get("horses", []):
            horse_name = horse["name"]

            # Convert recent runs to training format
            horse_performances = []

            for run in horse.get("recent_runs", []):
                perf = {
                    "date": run.get("date", "2024-01-01"),
                    "track": run.get("track", "Unknown"),
                    "distance": run.get("distance", "1200m"),
                    "surface": run.get("surface", "Turf"),
                    "race_class": "Class 4",
                    "field_size": run.get("field_size", 10),
                    "finish_position": run.get("finish_position", 5),
                    "beaten_lengths": run.get("beaten_lengths", 2.5),
                    "time": "1:24.56",
                    "speed_figure": run.get("speed_figure", 75),
                    "pace_figures": {"early": 85, "late": 90},
                    "weight_carried": run.get("weight_carried", "9-0"),
                    "jockey": run.get("jockey", horse.get("jockey", "Unknown")),
                    "trainer": run.get("trainer", horse.get("trainer", "Unknown")),
                    "odds": run.get("odds", 10.0),
                    "purse": 15000,
                    "conditions": "Good",
                    "comments": run.get("comments", ""),
                }
                horse_performances.append(perf)

            # Ensure at least 3 performances
            while len(horse_performances) < 3:
                base_perf = (
                    horse_performances[0]
                    if horse_performances
                    else {
                        "date": "2024-01-01",
                        "track": "Unknown",
                        "distance": "1200m",
                        "surface": "Turf",
                        "race_class": "Class 4",
                        "field_size": 10,
                        "finish_position": 5,
                        "beaten_lengths": 2.5,
                        "time": "1:24.56",
                        "speed_figure": 75,
                        "pace_figures": {"early": 85, "late": 90},
                        "weight_carried": "9-0",
                        "jockey": "Unknown",
                        "trainer": "Unknown",
                        "odds": 10.0,
                        "purse": 15000,
                        "conditions": "Good",
                        "comments": "",
                    }
                )
                horse_performances.append(base_perf.copy())

            horses_data[horse_name] = horse_performances
            betting_odds[horse_name] = horse.get("odds", 10.0)

        # Create race info in training format
        race_info = {
            "race_id": real_race.get("race_id", f"REAL_{int(time.time())}"),
            "track": real_race.get("track", "Unknown Track"),
            "distance": real_race.get("distance", "1200m"),
            "surface": real_race.get("surface", "Turf"),
            "race_class": real_race.get("race_type", "Class 4"),
            "conditions": real_race.get("conditions", "Good"),
            "prize_money": real_race.get("prize_money", 15000),
            "date": real_race.get("race_time", "2024-01-01")[:10],
            "time": "14:30",
        }

        return {
            "race_info": race_info,
            "horses_data": horses_data,
            "betting_odds": betting_odds,
            "source": f"real_data_{real_race.get('source', 'unknown')}",
        }

    async def _log_integration_details(self, integration_record: Dict[str, Any]):
        """Log detailed integration information."""

        log_file = (
            self.integration_logs_dir
            / f"integration_{datetime.now().strftime('%Y%m%d')}.json"
        )

        # Load existing log or create new
        if log_file.exists():
            with open(log_file, "r") as f:
                log_data = json.load(f)
        else:
            log_data = {"date": datetime.now().strftime("%Y-%m-%d"), "integrations": []}

        # Add new integration record
        log_data["integrations"].append(integration_record)

        # Save log
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=2)

    def display_integration_status(self):
        """Display current integration status."""

        table = Table(title="Real Data Integration Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Progress", style="yellow")

        current_percentage = self.integration_config["real_data_percentage"]
        target_percentage = self.integration_config["target_percentage"]

        table.add_row(
            "Real Data Percentage",
            f"{current_percentage:.1f}%",
            f"🎯 Target: {target_percentage:.1f}%",
        )

        table.add_row(
            "Integration Step",
            f"{self.integration_config['integration_step']:.1f}%",
            "",
        )

        table.add_row(
            "Quality Threshold",
            f"{self.integration_config['quality_threshold']:.1%}",
            "",
        )

        table.add_row(
            "Total Integrations", str(self.integration_stats["total_integrations"]), ""
        )

        table.add_row(
            "Successful", str(self.integration_stats["successful_integrations"]), "✅"
        )

        table.add_row(
            "Failed",
            str(self.integration_stats["failed_integrations"]),
            "❌" if self.integration_stats["failed_integrations"] > 0 else "",
        )

        if self.integration_stats["last_integration"]:
            table.add_row(
                "Last Integration",
                self.integration_stats["last_integration"].strftime("%Y-%m-%d %H:%M"),
                "",
            )

        table.add_row(
            "Data Quality Score",
            f"{self.integration_stats['data_quality_score']:.2%}",
            "🟢" if self.integration_stats["data_quality_score"] > 0.8 else "🟡",
        )

        self.console.print(table)

        # Progress towards full real data
        progress_percentage = (current_percentage / target_percentage) * 100
        progress_bar = "█" * int(progress_percentage / 5) + "░" * (
            20 - int(progress_percentage / 5)
        )

        self.console.print(
            f"\n📊 Progress to 100% Real Data: [{progress_bar}] {progress_percentage:.1f}%"
        )

    async def cleanup_old_backups(self, keep_count: Optional[int] = None):
        """Clean up old backup directories."""

        if keep_count is None:
            keep_count = self.integration_config["backup_count"]

        backup_dirs = [d for d in self.backup_dir.iterdir() if d.is_dir()]
        backup_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        if len(backup_dirs) > keep_count:
            dirs_to_remove = backup_dirs[keep_count:]

            for backup_dir in dirs_to_remove:
                try:
                    import shutil

                    shutil.rmtree(backup_dir)
                    self.console.print(f"🗑️ Removed old backup: {backup_dir.name}")
                except Exception as e:
                    logger.warning(f"Failed to remove backup {backup_dir}: {e}")

    async def run_integration_cycle(
        self, real_data_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run a complete integration cycle."""

        self.console.print(
            Panel.fit(
                "[bold blue]🔄 REAL DATA INTEGRATION CYCLE[/bold blue]\n"
                "[white]Gradually replacing synthetic data with real racing data[/white]",
                border_style="blue",
            )
        )

        try:
            # Find latest real data if not specified
            real_data_path: Path

            if real_data_file is None:
                real_data_files = list(
                    self.real_data_dir.glob("real_race_cards_*.json")
                )

                if not real_data_files:
                    self.console.print("❌ No real data files found")
                    return {"status": "failed", "reason": "No real data available"}

                real_data_path = max(real_data_files, key=lambda x: x.stat().st_mtime)
                self.console.print(f"📁 Using latest real data: {real_data_path.name}")
            else:
                real_data_path = Path(real_data_file)

            # Load real data
            with open(real_data_path, "r") as f:
                real_data = json.load(f)

            self.console.print(f"📊 Loaded {len(real_data)} real race cards")

            # Run integration
            result = await self.integrate_real_data_gradual(real_data)

            # Display status
            self.display_integration_status()

            # Cleanup old backups
            await self.cleanup_old_backups()

            return result

        except Exception as e:
            logger.error(f"Integration cycle failed: {e}")
            return {"status": "failed", "reason": str(e)}


async def main():
    """Main function to run integration cycle."""
    manager = RealDataIntegrationManager()

    try:
        result = await manager.run_integration_cycle()

        console.print("\n" + "=" * 60)
        console.print("🎯 Integration Cycle Complete!")
        console.print(f"📊 Result: {result}")

    except KeyboardInterrupt:
        console.print("\n🛑 Integration cancelled by user")
    except Exception as e:
        console.print(f"\n❌ Integration failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
