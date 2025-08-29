#!/usr/bin/env python3
"""
Advanced Analytics Pipeline Integration for Horse Racing AI V2.03
Stage 10: Advanced Analytics and Reporting System Integration
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import subprocess
import signal
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import analytics components
try:
    from tools.analytics.advanced_analytics_engine import AdvancedAnalyticsEngine
    from tools.analytics.data_exporter import DataExporter
    from tools.analytics.interactive_charts import InteractiveChartEngine
except ImportError as e:
    print(f"Warning: Could not import analytics components: {e}")
    AdvancedAnalyticsEngine = None
    DataExporter = None
    InteractiveChartEngine = None

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AdvancedAnalyticsPipeline:
    """
    Advanced Analytics Pipeline - Stage 10 Integration
    Provides comprehensive analytics, reporting, and data export capabilities
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Advanced Analytics Pipeline"""
        self.config = self._load_config(config_path)
        self.stage_name = "Stage 10: Advanced Analytics"
        self.process = None
        self.is_running = False

        # Initialize analytics components
        self.analytics_engine = None
        self.data_exporter = None
        self.chart_engine = None

        # Analytics configuration
        self.analytics_config = self.config.get("analytics", {})
        self.schedule_config = self.config.get("schedule", {})

        # Output directories
        self.output_dir = Path(self.config.get("output_directory", "reports/analytics"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)

        return {
            "analytics": {
                "auto_generate_reports": True,
                "report_frequency": "daily",  # 'hourly', 'daily', 'weekly'
                "export_formats": ["json", "csv"],
                "chart_generation": True,
                "dashboard_update": True,
                "cleanup_old_files": True,
                "cleanup_days": 30,
            },
            "schedule": {
                "performance_report_time": "06:00",
                "export_schedule": "08:00",
                "chart_generation_time": "09:00",
                "cleanup_time": "02:00",
            },
            "database_path": "data/racing_data_tracking.db",
            "output_directory": "reports/analytics",
            "enabled": True,
            "dependencies": ["Stage 9: Enhanced API"],
        }

    async def initialize_components(self) -> bool:
        """Initialize analytics components"""
        try:
            logger.info("Initializing analytics components...")

            # Initialize Analytics Engine
            if AdvancedAnalyticsEngine:
                self.analytics_engine = AdvancedAnalyticsEngine(
                    config_path=self.config.get("analytics_config_path")
                )
                logger.info("✅ Analytics Engine initialized")
            else:
                logger.warning("⚠️  Analytics Engine not available")

            # Initialize Data Exporter
            if DataExporter:
                self.data_exporter = DataExporter(
                    config_path=self.config.get("exporter_config_path")
                )
                logger.info("✅ Data Exporter initialized")
            else:
                logger.warning("⚠️  Data Exporter not available")

            # Initialize Chart Engine
            if InteractiveChartEngine:
                self.chart_engine = InteractiveChartEngine(
                    config_path=self.config.get("charts_config_path")
                )
                logger.info("✅ Chart Engine initialized")
            else:
                logger.warning("⚠️  Chart Engine not available")

            return True

        except Exception as e:
            logger.error(f"Error initializing analytics components: {e}")
            return False

    async def generate_daily_performance_report(self) -> Optional[str]:
        """Generate daily performance analytics report"""

        if not self.analytics_engine:
            logger.warning("Analytics Engine not available for report generation")
            return None

        try:
            logger.info("Generating daily performance report...")

            # Generate performance analytics report
            report = await self.analytics_engine.generate_performance_analytics_report()

            if report.data:
                # Export report to JSON
                json_path = await self.analytics_engine.export_report_to_json(report)

                logger.info(f"✅ Daily performance report generated: {json_path}")

                # Log key metrics
                summary = report.data.get("summary_metrics", {})
                logger.info(
                    f"   - Total Predictions: {summary.get('total_predictions', 'N/A')}"
                )
                logger.info(
                    f"   - Accuracy: {summary.get('accuracy_percentage', 'N/A')}%"
                )
                logger.info(
                    f"   - Overall ROI: {summary.get('overall_roi_percentage', 'N/A')}%"
                )

                return json_path
            else:
                logger.warning("No data available for performance report")
                return None

        except Exception as e:
            logger.error(f"Error generating daily performance report: {e}")
            return None

    async def export_data_formats(self) -> List[str]:
        """Export data in configured formats"""

        if not self.data_exporter:
            logger.warning("Data Exporter not available")
            return []

        exported_files = []
        export_formats = self.analytics_config.get("export_formats", ["json", "csv"])

        try:
            logger.info(f"Exporting data in formats: {export_formats}")

            # Define data sources to export
            data_sources = ["races", "predictions", "betting_results"]

            # Date filters for recent data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)  # Last 30 days

            filters = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            }

            for source in data_sources:
                for format_type in export_formats:
                    try:
                        export_file = await self.data_exporter.export_data(
                            data_source=source,
                            format_type=format_type,
                            filters=filters,
                            options={"include_metadata": True},
                        )

                        exported_files.append(export_file)
                        logger.info(
                            f"   ✅ {source} exported to {format_type}: {Path(export_file).name}"
                        )

                    except Exception as e:
                        logger.error(
                            f"   ❌ Error exporting {source} to {format_type}: {e}"
                        )

            logger.info(f"Data export completed: {len(exported_files)} files created")
            return exported_files

        except Exception as e:
            logger.error(f"Error during data export: {e}")
            return exported_files

    async def generate_analytics_charts(self) -> List[str]:
        """Generate analytics charts and visualizations"""

        if not self.chart_engine:
            logger.warning("Chart Engine not available")
            return []

        try:
            logger.info("Generating analytics charts...")

            # Generate standard chart set
            chart_paths = await self.chart_engine.generate_standard_charts()

            # Generate additional custom charts
            custom_charts = []

            try:
                # Weekly performance trend
                weekly_chart = await self.chart_engine.create_custom_chart(
                    data_source="monthly_summary",
                    chart_type="line",
                    x_column="month",
                    y_column="total_profit",
                    title="Weekly Profit Trends",
                    interactive=True,
                )
                custom_charts.append(weekly_chart)

                # Track comparison
                track_chart = await self.chart_engine.create_custom_chart(
                    data_source="track_analysis",
                    chart_type="bar",
                    x_column="track_code",
                    y_column="avg_confidence",
                    title="Average Confidence by Track",
                    interactive=True,
                )
                custom_charts.append(track_chart)

            except Exception as e:
                logger.warning(f"Some custom charts could not be generated: {e}")

            all_charts = chart_paths + custom_charts

            logger.info(
                f"✅ Chart generation completed: {len(all_charts)} charts created"
            )
            for chart in all_charts:
                logger.info(f"   - {Path(chart).name}")

            return all_charts

        except Exception as e:
            logger.error(f"Error generating analytics charts: {e}")
            return []

    async def cleanup_old_files(self) -> bool:
        """Clean up old analytics files"""

        try:
            cleanup_days = self.analytics_config.get("cleanup_days", 30)
            logger.info(f"Cleaning up files older than {cleanup_days} days...")

            # Cleanup analytics reports
            if self.analytics_engine:
                await self.analytics_engine.cleanup_old_reports(cleanup_days)

            # Cleanup exports
            if self.data_exporter:
                await self.data_exporter.cleanup_old_exports(cleanup_days)

            # Cleanup charts
            if self.chart_engine:
                await self.chart_engine.cleanup_old_charts(cleanup_days)

            logger.info("✅ File cleanup completed")
            return True

        except Exception as e:
            logger.error(f"Error during file cleanup: {e}")
            return False

    async def run_analytics_cycle(self) -> Dict[str, Any]:
        """Run a complete analytics cycle"""

        cycle_start = datetime.now()
        results = {
            "cycle_start": cycle_start.isoformat(),
            "performance_report": None,
            "exported_files": [],
            "generated_charts": [],
            "cleanup_completed": False,
            "errors": [],
            "cycle_duration": None,
        }

        try:
            logger.info("🚀 Starting Analytics Cycle...")

            # 1. Generate performance report
            if self.analytics_config.get("auto_generate_reports", True):
                try:
                    report_path = await self.generate_daily_performance_report()
                    results["performance_report"] = report_path
                except Exception as e:
                    error_msg = f"Performance report generation failed: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

            # 2. Export data
            try:
                exported_files = await self.export_data_formats()
                results["exported_files"] = exported_files
            except Exception as e:
                error_msg = f"Data export failed: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

            # 3. Generate charts
            if self.analytics_config.get("chart_generation", True):
                try:
                    chart_paths = await self.generate_analytics_charts()
                    results["generated_charts"] = chart_paths
                except Exception as e:
                    error_msg = f"Chart generation failed: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

            # 4. Cleanup old files
            if self.analytics_config.get("cleanup_old_files", True):
                try:
                    cleanup_success = await self.cleanup_old_files()
                    results["cleanup_completed"] = cleanup_success
                except Exception as e:
                    error_msg = f"File cleanup failed: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

            # Calculate cycle duration
            cycle_end = datetime.now()
            results["cycle_duration"] = (cycle_end - cycle_start).total_seconds()
            results["cycle_end"] = cycle_end.isoformat()

            # Log cycle summary
            logger.info("✅ Analytics Cycle Completed")
            logger.info(f"   - Duration: {results['cycle_duration']:.2f} seconds")
            logger.info(f"   - Reports: {1 if results['performance_report'] else 0}")
            logger.info(f"   - Exports: {len(results['exported_files'])}")
            logger.info(f"   - Charts: {len(results['generated_charts'])}")
            logger.info(f"   - Errors: {len(results['errors'])}")

            return results

        except Exception as e:
            error_msg = f"Analytics cycle failed: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            results["cycle_duration"] = (datetime.now() - cycle_start).total_seconds()
            return results

    async def start(self) -> bool:
        """Start the Advanced Analytics Pipeline"""

        try:
            if not self.config.get("enabled", True):
                logger.info("Advanced Analytics Pipeline is disabled in configuration")
                return False

            logger.info(f"🚀 Starting {self.stage_name}...")

            # Initialize components
            if not await self.initialize_components():
                logger.error("Failed to initialize analytics components")
                return False

            # Run initial analytics cycle
            logger.info("Running initial analytics cycle...")
            cycle_results = await self.run_analytics_cycle()

            if cycle_results["errors"]:
                logger.warning(
                    f"Initial cycle completed with {len(cycle_results['errors'])} errors"
                )
            else:
                logger.info("✅ Initial analytics cycle completed successfully")

            self.is_running = True
            logger.info(f"✅ {self.stage_name} started successfully")

            return True

        except Exception as e:
            logger.error(f"Error starting Advanced Analytics Pipeline: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the Advanced Analytics Pipeline"""

        try:
            logger.info(f"🛑 Stopping {self.stage_name}...")

            self.is_running = False

            # Final cleanup if needed
            if self.analytics_config.get("cleanup_on_stop", False):
                await self.cleanup_old_files()

            logger.info(f"✅ {self.stage_name} stopped successfully")
            return True

        except Exception as e:
            logger.error(f"Error stopping Advanced Analytics Pipeline: {e}")
            return False

    async def restart(self) -> bool:
        """Restart the Advanced Analytics Pipeline"""

        logger.info(f"🔄 Restarting {self.stage_name}...")

        # Stop current process
        stop_success = await self.stop()
        if not stop_success:
            logger.error("Failed to stop pipeline for restart")
            return False

        # Wait a moment
        await asyncio.sleep(2)

        # Start again
        start_success = await self.start()
        if start_success:
            logger.info(f"✅ {self.stage_name} restarted successfully")
        else:
            logger.error("Failed to start pipeline after restart")

        return start_success

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the Advanced Analytics Pipeline"""

        return {
            "stage_name": self.stage_name,
            "is_running": self.is_running,
            "process_id": os.getpid() if self.is_running else None,
            "configuration": {
                "auto_generate_reports": self.analytics_config.get(
                    "auto_generate_reports", False
                ),
                "export_formats": self.analytics_config.get("export_formats", []),
                "chart_generation": self.analytics_config.get(
                    "chart_generation", False
                ),
                "cleanup_enabled": self.analytics_config.get(
                    "cleanup_old_files", False
                ),
            },
            "components": {
                "analytics_engine": self.analytics_engine is not None,
                "data_exporter": self.data_exporter is not None,
                "chart_engine": self.chart_engine is not None,
            },
            "last_updated": datetime.now().isoformat(),
        }


async def main():
    """Main function for testing the Advanced Analytics Pipeline"""

    print("📊 Advanced Analytics Pipeline V2.03")
    print("Stage 10: Advanced Analytics and Reporting")
    print("=" * 50)

    try:
        # Initialize pipeline
        pipeline = AdvancedAnalyticsPipeline()

        # Start pipeline
        print("🚀 Starting Advanced Analytics Pipeline...")
        start_success = await pipeline.start()

        if start_success:
            print("✅ Pipeline started successfully")

            # Show status
            status = pipeline.get_status()
            print(f"\n📊 Pipeline Status:")
            print(f"   - Running: {status['is_running']}")
            print(f"   - Components Available:")
            for component, available in status["components"].items():
                print(f"     • {component}: {'✅' if available else '❌'}")

            # Run a test analytics cycle
            print("\n🔄 Running test analytics cycle...")
            results = await pipeline.run_analytics_cycle()

            print(f"   - Duration: {results.get('cycle_duration', 0):.2f} seconds")
            print(
                f"   - Reports Generated: {1 if results.get('performance_report') else 0}"
            )
            print(f"   - Files Exported: {len(results.get('exported_files', []))}")
            print(f"   - Charts Created: {len(results.get('generated_charts', []))}")
            print(f"   - Errors: {len(results.get('errors', []))}")

            if results.get("errors"):
                print("   - Error Details:")
                for error in results["errors"]:
                    print(f"     • {error}")

            # Stop pipeline
            print("\n🛑 Stopping pipeline...")
            stop_success = await pipeline.stop()

            if stop_success:
                print("✅ Pipeline stopped successfully")
            else:
                print("❌ Error stopping pipeline")
        else:
            print("❌ Failed to start pipeline")

        print("\n✅ Advanced Analytics Pipeline testing completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
