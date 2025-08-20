#!/usr/bin/env python3
"""
Production System Launcher
==========================

Backward compatibility launcher for the production system.
This script maintains the same interface while using the reorganized codebase.

Usage:
    python production_system.py start
    python production_system.py stop
    python production_system.py status

Author: Horse Racing AI System V2.03
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the actual production system
from horse_racing_ai.orchestration.production_system import main

if __name__ == "__main__":
    main()

import os
import sys
import logging
import argparse
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/production_system.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ProductionSystemManager:
    """Manages the complete production system"""

    def __init__(self):
        self.processes = {}
        self.services_status = {}
        self.config_created = False

        # Ensure log directory exists
        os.makedirs("logs", exist_ok=True)

        logger.info("Production System Manager initialized")

    def create_all_configs(self):
        """Create all required configuration files"""
        logger.info("Creating configuration files...")

        # 1. Create race data API config
        self._create_race_data_config()

        # 2. Create betting exchange config
        self._create_betting_exchange_config()

        # 3. Create alert system config
        self._create_alert_config()

        # 4. Create live execution config
        self._create_live_execution_config()

        # 5. Create production dashboard config
        self._create_production_config()

        self.config_created = True
        logger.info("✅ All configuration files created")

    def _create_race_data_config(self):
        """Create race data API configuration"""
        config = {
            "base_url": "https://api.theracingapi.com",
            "api_key": "YOUR_RACING_API_KEY_HERE",
            "betfair_app_key": "YOUR_BETFAIR_APP_KEY",
            "betfair_username": "YOUR_BETFAIR_USERNAME",
            "betfair_password": "YOUR_BETFAIR_PASSWORD",
            "update_interval": 30,
            "max_retries": 3,
            "sources": {
                "primary": "racing_api",
                "secondary": "betfair",
                "backup": "oddschecker",
            },
            "race_filters": {
                "countries": ["GB", "IRE"],
                "race_types": ["FLAT", "JUMPS"],
                "min_field_size": 4,
                "max_field_size": 40,
            },
        }

        os.makedirs("config", exist_ok=True)
        with open("config/race_data_api_config.json", "w") as f:
            json.dump(config, f, indent=2)

    def _create_betting_exchange_config(self):
        """Create betting exchange configuration"""
        config = {
            "exchanges": {
                "betfair": {
                    "enabled": True,
                    "app_key": "YOUR_BETFAIR_APP_KEY",
                    "username": "YOUR_BETFAIR_USERNAME",
                    "password": "YOUR_BETFAIR_PASSWORD",
                    "commission_rate": 0.05,
                    "delay_factor": 1.0,
                }
            },
            "risk_management": {
                "max_daily_stake": 200.0,
                "max_single_stake": 50.0,
                "max_exposure": 500.0,
                "stop_loss_percentage": 20.0,
                "max_consecutive_losses": 5,
                "min_balance_threshold": 100.0,
            },
            "strategy_settings": {
                "80/20": {"max_odds": 10.0, "min_odds": 2.0, "default_stake": 15.0},
                "dutching": {
                    "max_selections": 4,
                    "min_total_probability": 0.7,
                    "default_total_stake": 25.0,
                },
            },
        }

        with open("config/betting_exchange_config.json", "w") as f:
            json.dump(config, f, indent=2)

    def _create_alert_config(self):
        """Create alert system configuration"""
        config = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your-email@gmail.com",
                "password": "your-gmail-app-password",
                "use_tls": True,
                "from_email": "Horse Racing AI <your-email@gmail.com>",
            },
            "sms": {
                "account_sid": "YOUR_TWILIO_ACCOUNT_SID",
                "auth_token": "YOUR_TWILIO_AUTH_TOKEN",
                "from_number": "+1234567890",
            },
            "throttle_minutes": 30,
            "severity_levels": {
                "info": ["email"],
                "warning": ["email"],
                "error": ["email", "sms"],
                "critical": ["email", "sms"],
            },
            "default_recipients": [
                {
                    "name": "Primary Trader",
                    "email": "trader@yourdomain.com",
                    "phone": "+44123456789",
                    "alert_types": ["all"],
                }
            ],
        }

        with open("config/alert_config.json", "w") as f:
            json.dump(config, f, indent=2)

    def _create_live_execution_config(self):
        """Create live execution configuration"""
        config = {
            "execution_mode": "simulation",
            "monitoring_interval": 30,
            "opportunity_scan_interval": 60,
            "max_concurrent_positions": 5,
            "max_daily_stake": 200.0,
            "max_single_stake": 50.0,
            "min_confidence_threshold": 0.65,
            "enable_80_20_strategy": True,
            "enable_dutching_strategy": True,
            "auto_place_bets": False,
            "require_manual_approval": True,
            "alert_on_opportunities": True,
            "alert_on_performance": True,
        }

        with open("config/live_execution_config.json", "w") as f:
            json.dump(config, f, indent=2)

    def _create_production_config(self):
        """Create production configuration files"""
        # This would call the production_dashboard.py create-config function
        try:
            subprocess.run(
                [sys.executable, "production_dashboard.py", "create-config"],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not create production config: {e}")

    def start_dashboard(self):
        """Start the web dashboard"""
        logger.info("Starting web dashboard...")

        try:
            # Start dashboard in background
            process = subprocess.Popen(
                [sys.executable, "-m", "src.horse_racing_ai.monitoring.dashboard_app"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.processes["dashboard"] = process
            self.services_status["dashboard"] = "STARTING"

            # Give it a moment to start
            time.sleep(3)

            if process.poll() is None:  # Still running
                self.services_status["dashboard"] = "RUNNING"
                logger.info("✅ Web dashboard started on http://localhost:5000")
            else:
                self.services_status["dashboard"] = "FAILED"
                logger.error("❌ Failed to start web dashboard")

        except Exception as e:
            logger.error(f"Error starting dashboard: {e}")
            self.services_status["dashboard"] = "FAILED"

    def start_live_execution(self):
        """Start live strategy execution"""
        logger.info("Starting live strategy execution...")

        try:
            # Start execution in background
            process = subprocess.Popen(
                [sys.executable, "live_strategy_execution.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.processes["execution"] = process
            self.services_status["execution"] = "STARTING"

            # Give it a moment to start
            time.sleep(5)

            if process.poll() is None:  # Still running
                self.services_status["execution"] = "RUNNING"
                logger.info("✅ Live strategy execution started")
            else:
                self.services_status["execution"] = "FAILED"
                logger.error("❌ Failed to start live execution")

        except Exception as e:
            logger.error(f"Error starting live execution: {e}")
            self.services_status["execution"] = "FAILED"

    def start_monitoring(self):
        """Start system monitoring"""
        logger.info("Starting system monitoring...")

        try:
            # Start monitoring in background
            process = subprocess.Popen(
                [sys.executable, "scripts/complete_live_integration.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.processes["monitoring"] = process
            self.services_status["monitoring"] = "STARTING"

            # Give it a moment to start
            time.sleep(3)

            if process.poll() is None:  # Still running
                self.services_status["monitoring"] = "RUNNING"
                logger.info("✅ System monitoring started")
            else:
                self.services_status["monitoring"] = "FAILED"
                logger.error("❌ Failed to start monitoring")

        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            self.services_status["monitoring"] = "FAILED"

    def start_all_services(self):
        """Start all production services"""
        logger.info("🚀 Starting all production services...")

        if not self.config_created:
            self.create_all_configs()

        # Start services in order
        self.start_dashboard()
        time.sleep(2)

        self.start_monitoring()
        time.sleep(2)

        self.start_live_execution()
        time.sleep(2)

        # Report status
        self._report_status()

    def stop_all_services(self):
        """Stop all production services"""
        logger.info("🛑 Stopping all production services...")

        for service_name, process in self.processes.items():
            try:
                logger.info(f"Stopping {service_name}...")
                process.terminate()
                process.wait(timeout=10)
                self.services_status[service_name] = "STOPPED"
                logger.info(f"✅ {service_name} stopped")
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {service_name}...")
                process.kill()
                self.services_status[service_name] = "KILLED"
            except Exception as e:
                logger.error(f"Error stopping {service_name}: {e}")
                self.services_status[service_name] = "ERROR"

    def _report_status(self):
        """Report system status"""
        logger.info("📊 PRODUCTION SYSTEM STATUS")
        logger.info("=" * 40)

        for service, status in self.services_status.items():
            status_icon = {
                "RUNNING": "✅",
                "STARTING": "🔄",
                "STOPPED": "⭕",
                "FAILED": "❌",
                "KILLED": "💀",
                "ERROR": "⚠️",
            }.get(status, "❓")

            logger.info(f"{status_icon} {service.title()}: {status}")

        logger.info("=" * 40)

        # Service URLs
        if self.services_status.get("dashboard") == "RUNNING":
            logger.info("🌐 Web Dashboard: http://localhost:5000")

        # Instructions
        running_services = sum(
            1 for status in self.services_status.values() if status == "RUNNING"
        )
        total_services = len(self.services_status)

        if running_services == total_services:
            logger.info("🎉 All services running successfully!")
            logger.info("📱 Monitor the dashboard for live updates")
            logger.info("📧 Configure email/SMS alerts in config files")
            logger.info("🔧 Switch to 'live' mode when ready for real trading")
        else:
            logger.warning(f"⚠️ {running_services}/{total_services} services running")
            logger.info("💡 Check logs for error details")
            logger.info("🔧 Edit config files and restart if needed")

    def monitor_services(self):
        """Monitor running services"""
        logger.info("👁️ Starting service monitoring...")

        try:
            while True:
                # Check service health
                for service_name, process in list(self.processes.items()):
                    if process.poll() is not None:  # Process ended
                        self.services_status[service_name] = "FAILED"
                        logger.error(
                            f"❌ Service {service_name} has stopped unexpectedly"
                        )

                # Log status periodically
                if datetime.now().minute % 15 == 0 and datetime.now().second < 10:
                    running_count = sum(
                        1
                        for status in self.services_status.values()
                        if status == "RUNNING"
                    )
                    logger.info(
                        f"📊 Services status: {running_count}/{len(self.services_status)} running"
                    )

                time.sleep(10)

        except KeyboardInterrupt:
            logger.info("🛑 Service monitoring stopped")


def main():
    """Main production system launcher"""
    parser = argparse.ArgumentParser(description="Horse Racing AI Production System")
    parser.add_argument(
        "command",
        choices=["setup", "start", "stop", "status", "monitor", "create-config"],
        help="Command to execute",
    )
    parser.add_argument(
        "--service",
        choices=["dashboard", "execution", "monitoring", "all"],
        default="all",
        help="Specific service to control",
    )

    args = parser.parse_args()

    manager = ProductionSystemManager()

    try:
        if args.command == "create-config":
            print("🔧 Creating configuration files...")
            manager.create_all_configs()
            print("✅ Configuration files created in config/ directory")
            print("📝 Edit the config files with your API keys and settings")
            print("🚀 Run 'python production_system.py start' to launch")

        elif args.command == "setup":
            print("🔧 Setting up production system...")
            manager.create_all_configs()
            print("✅ Setup complete!")
            print("📝 Next steps:")
            print("   1. Edit config files with your API keys")
            print("   2. Run: python production_system.py start")

        elif args.command == "start":
            print("🚀 Starting Horse Racing AI Production System...")
            print("=" * 50)

            if args.service == "all":
                manager.start_all_services()
            elif args.service == "dashboard":
                manager.start_dashboard()
            elif args.service == "execution":
                manager.start_live_execution()
            elif args.service == "monitoring":
                manager.start_monitoring()

            print("\n🎯 System started!")
            print("📊 Monitor at: http://localhost:5000")
            print("🔄 Press Ctrl+C to stop all services")

            # Monitor services
            manager.monitor_services()

        elif args.command == "stop":
            print("🛑 Stopping production system...")
            manager.stop_all_services()
            print("✅ All services stopped")

        elif args.command == "status":
            # This would check running processes
            print("📊 Production System Status:")
            print("=" * 30)
            print("🌐 Dashboard: Check http://localhost:5000")
            print("📁 Logs: Check logs/ directory")
            print("⚙️ Config: Check config/ directory")

        elif args.command == "monitor":
            print("👁️ Monitoring production system...")
            manager.monitor_services()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        manager.stop_all_services()
        print("✅ Production system stopped")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
