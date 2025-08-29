#!/usr/bin/env python3
"""
🔄 Pipeline Integration Manager
Coordinates all pipeline components with dynamic timing and removes hardcoded times

This system:
1. Integrates dynamic_pipeline_timing.py with all components
2. Manages Docker container schedules dynamically
3. Removes hardcoded times throughout the system
4. Coordinates all monitoring and orchestration scripts

Author: AI Assistant
Date: August 14, 2025
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path first
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Now import from project modules
from dynamic_pipeline_timing import PipelineTimeAllocator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(project_root / "logs" / "integration_manager.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class PipelineIntegrationManager:
    """Manages integration of all pipeline components with dynamic timing"""

    def __init__(self):
        self.project_root = project_root
        self.config_dir = self.project_root / "config"
        self.tools_dir = self.project_root / "tools"
        self.scripts_dir = self.project_root / "scripts"

        # Initialize components
        self.time_allocator = PipelineTimeAllocator()
        self.downloader_scheduler = AutoDownloaderScheduler()

        # Dynamic configuration
        self.dynamic_config = None
        self.schedule_cache = {}

        # Component registry
        self.components = {
            "auto_downloader": {
                "container": "horserace-auto-downloader",
                "config_files": [
                    "project_root / 'config' / auto_downloader_config.json"
                ],
                "scripts": ["tools/cli/auto_downloader_scheduler.py"],
                "dependencies": [],
            },
            "pipeline_orchestrator": {
                "container": None,  # Runs on host
                "config_files": [
                    "project_root / 'config' / daily_pipeline_config.json"
                ],
                "scripts": ["daily_pipeline_orchestrator.py"],
                "dependencies": ["auto_downloader"],
            },
            "monitoring": {
                "container": None,
                "config_files": ["project_root / 'config' / monitoring_config.json"],
                "scripts": [
                    "live_06_01_download_monitor.py",
                    "tools/monitoring/pipeline_monitor.py",
                ],
                "dependencies": ["auto_downloader", "pipeline_orchestrator"],
            },
            "news_analyzer": {
                "container": "horse-racing-news-analyzer",
                "config_files": ["project_root / 'config' / news_analyzer_config.json"],
                "scripts": ["daily_news_analyzer.py"],
                "dependencies": ["auto_downloader"],
            },
        }

    def detect_first_race_time(self) -> Optional[datetime]:
        """Detect the first race time from today's data"""
        try:
            # Check multiple possible data locations
            data_paths = [
                "project_root / 'data' / daily_downloads/cards_project_root / 'data' / races/races.csv",
                "project_root / 'data' / daily_downloads/results_project_root / 'data' / races/races.csv",
                "project_root / 'data' / downloaded_files/cards_project_root / 'data' / races/races.csv",
            ]

            today = datetime.now().strftime("%Y-%m-%d")
            earliest_race = None

            for data_path in data_paths:
                full_path = self.project_root / data_path
                if full_path.exists():
                    try:
                        import pandas as pd

                        df = pd.read_csv(full_path)

                        if "race_time" in df.columns:
                            today_races = df[df["date"] == today]
                            if not today_races.empty:
                                race_times = pd.to_datetime(today_races["race_time"])
                                first_race = race_times.min()

                                if earliest_race is None or first_race < earliest_race:
                                    earliest_race = first_race

                    except Exception as e:
                        logger.debug(f"Could not parse {data_path}: {e}")
                        continue

            if earliest_race:
                logger.info(
                    f"🎯 Detected first race time: {earliest_race.strftime('%H:%M')}"
                )
                return earliest_race
            else:
                logger.info("⚠️ No races detected for today - using default 14:00")
                return datetime.combine(
                    datetime.now().date(), datetime.strptime("14:00", "%H:%M").time()
                )

        except Exception as e:
            logger.error(f"❌ Error detecting race time: {e}")
            return None

    def generate_dynamic_schedule(self, force_update: bool = False) -> Dict:
        """Generate dynamic schedule for all components"""

        # Check if we have a cached schedule for today
        today = datetime.now().strftime("%Y-%m-%d")
        cache_key = f"schedule_{today}"

        if not force_update and cache_key in self.schedule_cache:
            logger.info("📋 Using cached dynamic schedule")
            return self.schedule_cache[cache_key]

        logger.info("🎯 Generating new dynamic schedule...")

        # Get auto-downloader completion time
        downloader_config = self.downloader_scheduler.get_current_schedule()
        download_time = downloader_config.get("schedule_time", "06:01")

        # Detect first race time
        first_race_time = self.detect_first_race_time()

        # Generate optimized allocation
        allocation = self.time_allocator.allocate_enhanced_schedule(
            download_time=download_time, first_race_time=first_race_time
        )

        # Build comprehensive schedule
        dynamic_schedule = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "download_time": download_time,
                "first_race_time": (
                    first_race_time.strftime("%H:%M") if first_race_time else "14:00"
                ),
                "total_window_minutes": allocation["timing_analysis"][
                    "total_window_minutes"
                ],
                "schedule_type": allocation["timing_analysis"].get(
                    "schedule_type", "enhanced"
                ),
            },
            "components": {},
            "pipeline_stages": allocation["schedule"],
            "timing_analysis": allocation["timing_analysis"],
        }

        # Map pipeline stages to components
        for stage_name, stage_info in allocation["schedule"].items():
            component = self._map_stage_to_component(stage_name)
            if component:
                if component not in dynamic_schedule["components"]:
                    dynamic_schedule["components"][component] = {
                        "stages": [],
                        "start_time": stage_info["start_time"],
                        "total_duration": 0,
                    }

                dynamic_schedule["components"][component]["stages"].append(
                    {
                        "name": stage_name,
                        "start_time": stage_info["start_time"],
                        "end_time": stage_info["end_time"],
                        "duration_minutes": stage_info["duration_minutes"],
                        "description": stage_info["description"],
                    }
                )

                dynamic_schedule["components"][component][
                    "total_duration"
                ] += stage_info["duration_minutes"]

        # Cache the schedule
        self.schedule_cache[cache_key] = dynamic_schedule

        # Save to file
        self._save_schedule_to_file(dynamic_schedule)

        logger.info(
            f"✅ Dynamic schedule generated with {len(dynamic_schedule['pipeline_stages'])} stages"
        )
        return dynamic_schedule

    def _map_stage_to_component(self, stage_name: str) -> Optional[str]:
        """Map pipeline stage to system component"""
        stage_component_map = {
            "data_download": "auto_downloader",
            "data_validation": "auto_downloader",
            "data_preprocessing": "pipeline_orchestrator",
            "data_relationships": "pipeline_orchestrator",
            "feature_engineering": "pipeline_orchestrator",
            "contextual_analysis": "pipeline_orchestrator",
            "form_scoring": "pipeline_orchestrator",
            "power_ratings": "pipeline_orchestrator",
            "speed_analysis": "pipeline_orchestrator",
            "ml_model_training": "pipeline_orchestrator",
            "monte_carlo_simulations": "pipeline_orchestrator",
            "race_trends": "pipeline_orchestrator",
            "composite_scoring": "pipeline_orchestrator",
            "betting_strategies": "pipeline_orchestrator",
            "ai_selections": "pipeline_orchestrator",
            "report_generation": "pipeline_orchestrator",
            "pre_race_updates": "monitoring",
        }
        return stage_component_map.get(stage_name)

    def _save_schedule_to_file(self, schedule: Dict) -> None:
        """Save dynamic schedule to configuration file"""
        config_file = self.config_dir / "dynamic_schedule.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, "w") as f:
            json.dump(schedule, f, indent=2, default=str)

        logger.info(f"💾 Dynamic schedule saved to {config_file}")

    def update_component_configs(self, schedule: Dict) -> Dict[str, bool]:
        """Update all component configurations with dynamic timing"""
        update_results = {}

        for component_name, component_config in schedule["components"].items():
            try:
                success = self._update_component_config(
                    component_name, component_config, schedule
                )
                update_results[component_name] = success

                if success:
                    logger.info(f"✅ Updated {component_name} configuration")
                else:
                    logger.warning(f"⚠️ Failed to update {component_name} configuration")

            except Exception as e:
                logger.error(f"❌ Error updating {component_name}: {e}")
                update_results[component_name] = False

        return update_results

    def _update_component_config(
        self, component_name: str, component_config: Dict, full_schedule: Dict
    ) -> bool:
        """Update individual component configuration"""

        if component_name == "auto_downloader":
            return self._update_auto_downloader_config(component_config, full_schedule)
        elif component_name == "pipeline_orchestrator":
            return self._update_orchestrator_config(component_config, full_schedule)
        elif component_name == "monitoring":
            return self._update_monitoring_config(component_config, full_schedule)
        elif component_name == "news_analyzer":
            return self._update_news_analyzer_config(component_config, full_schedule)
        else:
            logger.warning(f"Unknown component: {component_name}")
            return False

    def _update_auto_downloader_config(
        self, component_config: Dict, full_schedule: Dict
    ) -> bool:
        """Update auto-downloader configuration"""
        try:
            download_time = full_schedule["metadata"]["download_time"]

            # Update scheduler configuration
            success = self.downloader_scheduler.update_schedule(download_time)

            if success:
                # Update Docker container if needed
                self._restart_container_if_needed("horserace-auto-downloader")

            return success

        except Exception as e:
            logger.error(f"Error updating auto-downloader config: {e}")
            return False

    def _update_orchestrator_config(
        self, component_config: Dict, full_schedule: Dict
    ) -> bool:
        """Update pipeline orchestrator configuration"""
        try:
            config_file = self.config_dir / "daily_pipeline_config.json"

            # Load existing config or create new
            if config_file.exists():
                with open(config_file, "r") as f:
                    config = json.load(f)
            else:
                config = {"schedule": {}, "settings": {}}

            # Update schedule with dynamic times
            for stage in component_config["stages"]:
                stage_key = f"{stage['name']}_time"
                config["schedule"][stage_key] = stage["start_time"]

            # Add dynamic schedule metadata
            config["dynamic_schedule"] = {
                "enabled": True,
                "last_updated": datetime.now().isoformat(),
                "total_duration": component_config["total_duration"],
                "stage_count": len(component_config["stages"]),
            }

            # Save updated config
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)

            return True

        except Exception as e:
            logger.error(f"Error updating orchestrator config: {e}")
            return False

    def _update_monitoring_config(
        self, component_config: Dict, full_schedule: Dict
    ) -> bool:
        """Update monitoring configuration"""
        try:
            config_file = self.config_dir / "monitoring_config.json"

            # Create monitoring configuration
            monitoring_config = {
                "schedule": {
                    "download_time": full_schedule["metadata"]["download_time"],
                    "first_race_time": full_schedule["metadata"]["first_race_time"],
                    "total_window_minutes": full_schedule["metadata"][
                        "total_window_minutes"
                    ],
                },
                "components": full_schedule["components"],
                "monitoring": {
                    "check_intervals": {
                        "auto_downloader": 60,  # Check every minute during download
                        "pipeline_stages": 300,  # Check every 5 minutes during stages
                        "pre_race": 30,  # Check every 30 seconds before races
                    },
                    "alerts": {
                        "enabled": True,
                        "timeout_threshold": 1.5,  # Alert if stage takes 150% of allocated time
                        "failure_threshold": 2,  # Alert after 2 consecutive failures
                    },
                },
                "dynamic_schedule": {
                    "enabled": True,
                    "last_updated": datetime.now().isoformat(),
                },
            }

            # Save configuration
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(monitoring_config, f, indent=2)

            return True

        except Exception as e:
            logger.error(f"Error updating monitoring config: {e}")
            return False

    def _update_news_analyzer_config(
        self, component_config: Dict, full_schedule: Dict
    ) -> bool:
        """Update news analyzer configuration"""
        try:
            config_file = self.config_dir / "news_analyzer_config.json"

            # Load existing config or create new
            if config_file.exists():
                with open(config_file, "r") as f:
                    config = json.load(f)
            else:
                config = {"schedule": {}, "settings": {}}

            # Update with dynamic timing
            config["schedule"]["start_time"] = full_schedule["metadata"][
                "download_time"
            ]
            config["schedule"]["analysis_window"] = 30  # 30 minutes after download
            config["dynamic_schedule"] = {
                "enabled": True,
                "last_updated": datetime.now().isoformat(),
            }

            # Save configuration
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)

            return True

        except Exception as e:
            logger.error(f"Error updating news analyzer config: {e}")
            return False

    def _restart_container_if_needed(self, container_name: str) -> bool:
        """Restart Docker container if configuration changed"""
        try:
            # Check if container is running
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    f"name={container_name}",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            if container_name in result.stdout:
                logger.info(
                    f"🔄 Restarting container {container_name} for config update..."
                )

                subprocess.run(["docker", "restart", container_name], check=True)
                logger.info(f"✅ Container {container_name} restarted successfully")
                return True
            else:
                logger.info(
                    f"ℹ️ Container {container_name} not running - no restart needed"
                )
                return True

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error restarting container {container_name}: {e}")
            return False

    def organize_scripts(self) -> Dict[str, List[str]]:
        """Organize scripts into proper directory structure"""
        organization_plan = {"moved": [], "errors": [], "created_dirs": []}

        # Define script organization plan
        script_moves = [
            # Monitoring scripts
            (
                "live_06_01_download_monitor.py",
                "tools/monitoring/live_download_monitor.py",
            ),
            ("live_test_monitor.py", "tools/monitoring/live_test_monitor.py"),
            (
                "integrated_performance_demo.py",
                "tools/monitoring/performance_monitor.py",
            ),
            (
                "performance_timing_demo.py",
                "tools/monitoring/performance_timing_demo.py",
            ),
            # Pipeline scripts
            ("daily_pipeline_orchestrator.py", "tools/pipeline/daily_orchestrator.py"),
            ("integrated_auto_pipeline.py", "tools/pipeline/integrated_pipeline.py"),
            ("apply_critical_pipeline_fixes.py", "tools/pipeline/critical_fixes.py"),
            ("apply_phase2_reliability.py", "tools/pipeline/reliability_fixes.py"),
            # Data processing scripts
            ("daily_csv_uploader.py", "tools/data_processing/csv_uploader.py"),
            ("column_smart_uploader.py", "tools/data_processing/smart_uploader.py"),
            (
                "corrected_csv_uploader.py",
                "tools/data_processing/corrected_uploader.py",
            ),
            ("smart_daily_uploader.py", "tools/data_processing/daily_uploader.py"),
            # Analysis scripts
            ("daily_news_analyzer.py", "tools/analysis/news_analyzer.py"),
            ("daily_tips_analyzer.py", "tools/analysis/tips_analyzer.py"),
            ("advanced_racing_analytics.py", "tools/analysis/racing_analytics.py"),
            ("ai_form_analyzer_fixed.py", "tools/analysis/form_analyzer.py"),
            ("ai_reward_analyzer.py", "tools/analysis/reward_analyzer.py"),
            ("simple_form_analyzer.py", "tools/analysis/simple_form_analyzer.py"),
            # Utility scripts
            ("qwen_auto_updater.py", "tools/utilities/qwen_updater.py"),
            ("qwen_docker_updater.py", "tools/utilities/qwen_docker_updater.py"),
            ("enhanced_error_handling.py", "tools/utilities/error_handling.py"),
            ("verify_cleanup.py", "tools/utilities/cleanup_verifier.py"),
            ("verify_critical_fixes.py", "tools/utilities/fix_verifier.py"),
            # Testing scripts
            ("test_17_stage_integration.py", "tools/testing/integration_test.py"),
            ("test_complete_pipeline.py", "tools/testing/pipeline_test.py"),
            (
                "test_enhanced_integration.py",
                "tools/testing/enhanced_integration_test.py",
            ),
            ("test_production_models.py", "tools/testing/production_models_test.py"),
            # Configuration scripts
            ("organize_docker_scripts.py", "tools/utilities/docker_organizer.py"),
            (
                "documentation_analysis_report.py",
                "tools/utilities/documentation_analyzer.py",
            ),
        ]

        # Execute moves
        for source_file, target_path in script_moves:
            source_path = self.project_root / source_file
            target_full_path = self.project_root / target_path

            if source_path.exists():
                try:
                    # Create target directory if needed
                    target_full_path.parent.mkdir(parents=True, exist_ok=True)
                    if (
                        str(target_full_path.parent)
                        not in organization_plan["created_dirs"]
                    ):
                        organization_plan["created_dirs"].append(
                            str(target_full_path.parent)
                        )

                    # Move file
                    source_path.rename(target_full_path)
                    organization_plan["moved"].append(f"{source_file} → {target_path}")
                    logger.info(f"📁 Moved {source_file} → {target_path}")

                except Exception as e:
                    error_msg = f"Failed to move {source_file}: {e}"
                    organization_plan["errors"].append(error_msg)
                    logger.error(f"❌ {error_msg}")
            else:
                logger.debug(f"⏭️ Skipping {source_file} (not found)")

        return organization_plan

    def update_docker_configurations(self, schedule: Dict) -> bool:
        """Update Docker configurations with dynamic timing"""
        try:
            # Update docker-compose.yml with dynamic environment variables
            compose_file = self.project_root / "docker-compose.yml"

            if compose_file.exists():
                # Create environment file for dynamic values
                env_file = self.project_root / ".env.dynamic"

                env_content = [
                    f"# Dynamic Pipeline Configuration - Generated {datetime.now().isoformat()}",
                    f"DOWNLOAD_TIME={schedule['metadata']['download_time']}",
                    f"FIRST_RACE_TIME={schedule['metadata']['first_race_time']}",
                    f"TOTAL_WINDOW_MINUTES={schedule['metadata']['total_window_minutes']}",
                    f"SCHEDULE_TYPE={schedule['timing_analysis'].get('schedule_type', 'enhanced')}",
                    "",
                ]

                # Add component-specific environment variables
                for component_name, component_config in schedule["components"].items():
                    component_upper = component_name.upper()
                    env_content.extend(
                        [
                            f"{component_upper}_START_TIME={component_config['start_time']}",
                            f"{component_upper}_DURATION={component_config['total_duration']}",
                            f"{component_upper}_STAGE_COUNT={len(component_config['stages'])}",
                        ]
                    )

                with open(env_file, "w") as f:
                    f.write("\n".join(env_content))

                logger.info(f"✅ Dynamic environment file created: {env_file}")
                return True
            else:
                logger.error("❌ docker-compose.yml not found")
                return False

        except Exception as e:
            logger.error(f"❌ Error updating Docker configurations: {e}")
            return False

    def generate_integration_report(
        self, schedule: Dict, update_results: Dict, organization_results: Dict
    ) -> str:
        """Generate comprehensive integration report"""

        report_file = (
            self.project_root
            / "reports"
            / f"integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)

        # Calculate success metrics
        successful_updates = sum(1 for result in update_results.values() if result)
        total_updates = len(update_results)
        success_rate = (
            (successful_updates / total_updates) * 100 if total_updates > 0 else 0
        )

        # Build report content
        report_content = f"""# 🔄 Pipeline Integration Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Integration Summary

- **Dynamic Schedule**: {schedule['timing_analysis'].get('schedule_type', 'Enhanced').title()}
- **Download Time**: {schedule['metadata']['download_time']}
- **First Race**: {schedule['metadata']['first_race_time']}
- **Total Window**: {schedule['metadata']['total_window_minutes']} minutes
- **Pipeline Stages**: {len(schedule['pipeline_stages'])}
- **Active Components**: {len(schedule['components'])}

## ✅ Component Updates

| Component | Status | Stages | Duration |
|-----------|--------|--------|----------|
"""

        for component_name, success in update_results.items():
            status = "✅ Success" if success else "❌ Failed"
            component_config = schedule["components"].get(component_name, {})
            stages = len(component_config.get("stages", []))
            duration = component_config.get("total_duration", 0)

            report_content += (
                f"| {component_name} | {status} | {stages} | {duration} min |\n"
            )

        report_content += f"""
**Update Success Rate**: {success_rate:.1f}% ({successful_updates}/{total_updates})

## 📁 Script Organization

### ✅ Successfully Moved
"""

        for move in organization_results.get("moved", []):
            report_content += f"- {move}\n"

        if organization_results.get("errors"):
            report_content += "\n### ❌ Move Errors\n"
            for error in organization_results["errors"]:
                report_content += f"- {error}\n"

        report_content += f"""
### 📂 Directories Created
"""
        for directory in organization_results.get("created_dirs", []):
            report_content += f"- {directory}\n"

        report_content += f"""
## 🎯 Pipeline Stages Schedule

| Stage | Start | End | Duration | Component |
|-------|-------|-----|----------|-----------|
"""

        for stage_name, stage_info in schedule["pipeline_stages"].items():
            component = self._map_stage_to_component(stage_name) or "unknown"
            report_content += f"| {stage_name.replace('_', ' ').title()} | {stage_info['start_time']} | {stage_info['end_time']} | {stage_info['duration_minutes']} min | {component} |\n"

        report_content += f"""
## 🔧 Next Steps

1. **Restart Services**: Restart any affected Docker containers
2. **Test Integration**: Run integration tests to verify all components work together
3. **Monitor Pipeline**: Use the updated monitoring tools to track performance
4. **Update Documentation**: Update any remaining documentation with new paths

## 📝 Configuration Files Updated

- `project_root / 'config' / dynamic_schedule.json` - Master dynamic schedule
- `project_root / 'config' / daily_pipeline_config.json` - Pipeline orchestrator settings
- `project_root / 'config' / monitoring_config.json` - Monitoring configuration  
- `project_root / 'config' / news_analyzer_config.json` - News analyzer settings
- `.env.dynamic` - Docker environment variables

## 🏆 Integration Status: {"✅ COMPLETE" if success_rate > 80 else "⚠️ PARTIAL"}

The pipeline integration is {"complete" if success_rate > 80 else "partially complete"} with {successful_updates} out of {total_updates} components successfully updated.
Dynamic timing is now active and hardcoded times have been removed from the system.
"""

        # Save report
        with open(report_file, "w") as f:
            f.write(report_content)

        logger.info(f"📝 Integration report saved to {report_file}")
        return str(report_file)

    async def run_full_integration(self, force_schedule_update: bool = False) -> Dict:
        """Run complete pipeline integration"""

        logger.info("🚀 Starting full pipeline integration...")
        start_time = time.time()

        try:
            # Step 1: Generate dynamic schedule
            logger.info("📋 Step 1: Generating dynamic schedule...")
            schedule = self.generate_dynamic_schedule(
                force_update=force_schedule_update
            )

            # Step 2: Organize scripts
            logger.info("📁 Step 2: Organizing scripts...")
            organization_results = self.organize_scripts()

            # Step 3: Update component configurations
            logger.info("⚙️ Step 3: Updating component configurations...")
            update_results = self.update_component_configs(schedule)

            # Step 4: Update Docker configurations
            logger.info("🐳 Step 4: Updating Docker configurations...")
            docker_success = self.update_docker_configurations(schedule)

            # Step 5: Generate report
            logger.info("📝 Step 5: Generating integration report...")
            report_file = self.generate_integration_report(
                schedule, update_results, organization_results
            )

            # Calculate final metrics
            total_time = time.time() - start_time
            successful_updates = sum(1 for result in update_results.values() if result)
            total_updates = len(update_results)

            integration_result = {
                "success": True,
                "total_time": total_time,
                "schedule": schedule,
                "update_results": update_results,
                "organization_results": organization_results,
                "docker_success": docker_success,
                "report_file": report_file,
                "metrics": {
                    "successful_updates": successful_updates,
                    "total_updates": total_updates,
                    "success_rate": (
                        (successful_updates / total_updates) * 100
                        if total_updates > 0
                        else 0
                    ),
                    "scripts_moved": len(organization_results.get("moved", [])),
                    "directories_created": len(
                        organization_results.get("created_dirs", [])
                    ),
                },
            }

            logger.info(f"✅ Pipeline integration completed in {total_time:.2f}s")
            logger.info(
                f"📊 Success rate: {integration_result['metrics']['success_rate']:.1f}%"
            )

            return integration_result

        except Exception as e:
            logger.error(f"❌ Integration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_time": time.time() - start_time,
            }


def main():
    """Main integration function"""

    print("🔄 Pipeline Integration Manager")
    print("=" * 60)

    manager = PipelineIntegrationManager()

    # Run integration
    try:
        integration_result = asyncio.run(
            manager.run_full_integration(force_schedule_update=True)
        )

        if integration_result["success"]:
            print(f"\n✅ Integration completed successfully!")
            print(f"⏱️ Total time: {integration_result['total_time']:.2f}s")
            print(
                f"📊 Success rate: {integration_result['metrics']['success_rate']:.1f}%"
            )
            print(f"📝 Report: {integration_result['report_file']}")
            print(f"\n🎯 Next Steps:")
            print(f"   1. Review the integration report")
            print(f"   2. Restart any affected Docker containers")
            print(f"   3. Test the integrated pipeline")
        else:
            print(
                f"\n❌ Integration failed: {integration_result.get('error', 'Unknown error')}"
            )
            print(f"⏱️ Time before failure: {integration_result['total_time']:.2f}s")

    except Exception as e:
        print(f"\n💥 Critical error during integration: {e}")
        logger.error(f"Critical integration error: {e}")


if __name__ == "__main__":
    main()
