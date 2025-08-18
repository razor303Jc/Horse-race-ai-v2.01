#!/usr/bin/env python3
"""
🌐 Stage 7: Web Interface Integration (Container-Optimized)

Stage 7 integrates the React web application with the Stage 6 prediction service.
This version is optimized to work within the container environment.

Key Features:
1. Prediction Service Activation
2. API Configuration for Web Integration
3. Service Health Monitoring
4. Configuration Management
5. Integration Status Reporting
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Stage7WebIntegrationContainer:
    """Stage 7: Container-optimized web integration implementation"""

    def __init__(self):
        self.stage = 7
        self.models_dir = Path("/app/models")
        self.api_port = 8000
        self.web_port = 3000

        # Integration status
        self.integration_status = {
            "stage": self.stage,
            "status": "initializing",
            "prediction_service": False,
            "api_configuration": False,
            "integration_config": False,
            "health_monitoring": False,
        }

    def check_stage6_prerequisites(self) -> bool:
        """Check if Stage 6 prediction service is ready"""
        logger.info("🔍 Checking Stage 6 prerequisites...")

        try:
            # Check Stage 6 service summary
            summary_path = self.models_dir / "stage6_service_summary.json"
            if not summary_path.exists():
                logger.error("❌ Stage 6 service summary not found")
                return False

            with open(summary_path, "r") as f:
                stage6_summary = json.load(f)

            if stage6_summary.get("status") != "operational":
                logger.error("❌ Stage 6 prediction service not operational")
                return False

            logger.info("✅ Stage 6 prerequisites met")
            self.integration_status["prediction_service"] = True
            return True

        except Exception as e:
            logger.error(f"❌ Error checking Stage 6 prerequisites: {e}")
            return False

    def configure_prediction_api(self) -> bool:
        """Configure prediction API for web integration"""
        logger.info("🔧 Configuring prediction API for web integration...")

        try:
            # API configuration for web integration
            api_config = {
                "prediction_service": {
                    "host": "0.0.0.0",
                    "port": self.api_port,
                    "base_url": f"http://localhost:{self.api_port}",
                    "cors_enabled": True,
                    "allowed_origins": [
                        f"http://localhost:{self.web_port}",
                        "http://host.docker.internal:3000",
                        "http://horse_racing_web_app_clean:3000",
                    ],
                },
                "endpoints": {
                    "health": "/health",
                    "predict_horse": "/predict/horse",
                    "predict_race": "/predict/race",
                    "models_status": "/models/status",
                    "docs": "/docs",
                },
                "features": {
                    "real_time_predictions": True,
                    "batch_predictions": True,
                    "model_selection": True,
                    "confidence_scores": True,
                },
                "stage": self.stage,
                "timestamp": datetime.now().isoformat(),
            }

            # Save API configuration
            config_path = self.models_dir / "stage7_api_config.json"
            with open(config_path, "w") as f:
                json.dump(api_config, f, indent=2)

            logger.info("✅ Prediction API configured for web integration")
            self.integration_status["api_configuration"] = True
            return True

        except Exception as e:
            logger.error(f"❌ Error configuring prediction API: {e}")
            return False

    def create_web_integration_config(self) -> bool:
        """Create web application integration configuration"""
        logger.info("🌐 Creating web integration configuration...")

        try:
            # Web integration configuration
            web_config = {
                "web_application": {
                    "name": "Horse Racing AI Dashboard",
                    "port": self.web_port,
                    "framework": "React",
                    "container": "horse_racing_web_app_clean",
                },
                "api_integration": {
                    "prediction_api_url": f"http://host.docker.internal:{self.api_port}",
                    "fallback_urls": [
                        f"http://localhost:{self.api_port}",
                        f"http://horse_racing_ml_trainer_clean:{self.api_port}",
                    ],
                    "timeout": 30,
                    "retry_attempts": 3,
                },
                "real_time_features": {
                    "auto_refresh": True,
                    "refresh_interval": 30000,  # 30 seconds
                    "live_predictions": True,
                    "status_monitoring": True,
                },
                "ui_components": {
                    "prediction_dashboard": True,
                    "model_status_panel": True,
                    "real_time_updates": True,
                    "api_documentation": True,
                },
                "stage": self.stage,
                "timestamp": datetime.now().isoformat(),
            }

            # Save web configuration
            config_path = self.models_dir / "stage7_web_config.json"
            with open(config_path, "w") as f:
                json.dump(web_config, f, indent=2)

            logger.info("✅ Web integration configuration created")
            self.integration_status["integration_config"] = True
            return True

        except Exception as e:
            logger.error(f"❌ Error creating web integration config: {e}")
            return False

    def setup_health_monitoring(self) -> bool:
        """Setup health monitoring for the integrated system"""
        logger.info("💚 Setting up health monitoring...")

        try:
            # Health monitoring configuration
            health_config = {
                "monitoring": {
                    "enabled": True,
                    "check_interval": 60,  # seconds
                    "components": [
                        "prediction_api",
                        "web_application",
                        "model_health",
                        "api_endpoints",
                    ],
                },
                "alerts": {
                    "api_down": True,
                    "model_errors": True,
                    "web_app_errors": True,
                    "performance_degradation": True,
                },
                "health_endpoints": {
                    "prediction_api": f"http://localhost:{self.api_port}/health",
                    "api_status": f"http://localhost:{self.api_port}/models/status",
                },
                "thresholds": {
                    "response_time_ms": 5000,
                    "error_rate_percent": 5,
                    "model_confidence_min": 0.1,
                },
                "stage": self.stage,
                "timestamp": datetime.now().isoformat(),
            }

            # Save health monitoring configuration
            config_path = self.models_dir / "stage7_health_config.json"
            with open(config_path, "w") as f:
                json.dump(health_config, f, indent=2)

            logger.info("✅ Health monitoring configured")
            self.integration_status["health_monitoring"] = True
            return True

        except Exception as e:
            logger.error(f"❌ Error setting up health monitoring: {e}")
            return False

    def create_integration_summary(self) -> Dict:
        """Create comprehensive integration summary"""
        logger.info("📊 Creating Stage 7 integration summary...")

        # Check if all components are configured
        all_configured = all(self.integration_status.values())

        summary = {
            "stage": self.stage,
            "stage_name": "Web Interface Integration",
            "status": "operational" if all_configured else "partial",
            "timestamp": datetime.now().isoformat(),
            "components": self.integration_status,
            "architecture": {
                "prediction_api": {
                    "port": self.api_port,
                    "endpoints": 4,
                    "features": ["predictions", "health", "status", "docs"],
                },
                "web_application": {
                    "port": self.web_port,
                    "framework": "React",
                    "integration_type": "API-based",
                },
            },
            "capabilities": {
                "real_time_predictions": True,
                "web_dashboard": True,
                "api_integration": True,
                "health_monitoring": True,
                "model_selection": True,
                "confidence_scoring": True,
            },
            "access_urls": {
                "web_dashboard": f"http://localhost:{self.web_port}",
                "prediction_api": f"http://localhost:{self.api_port}",
                "api_documentation": f"http://localhost:{self.api_port}/docs",
                "health_check": f"http://localhost:{self.api_port}/health",
            },
            "configuration_files": [
                "stage7_api_config.json",
                "stage7_web_config.json",
                "stage7_health_config.json",
                "stage7_integration_summary.json",
            ],
            "integration_notes": [
                "Prediction API configured for CORS with web app origins",
                "Web app configured to connect to prediction API",
                "Health monitoring setup for system components",
                "Real-time updates enabled with 30-second intervals",
            ],
            "next_stage": {
                "stage": 8,
                "name": "Betting Integration",
                "prerequisites": "Web interface with live prediction API",
            },
        }

        # Save integration summary
        summary_path = self.models_dir / "stage7_integration_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        return summary

    def run_stage7_integration(self) -> bool:
        """Execute Stage 7 web integration"""
        logger.info("🌐 Starting Stage 7: Web Interface Integration")

        try:
            # Step 1: Check Stage 6 prerequisites
            if not self.check_stage6_prerequisites():
                return False

            # Step 2: Configure prediction API
            if not self.configure_prediction_api():
                return False

            # Step 3: Create web integration config
            if not self.create_web_integration_config():
                return False

            # Step 4: Setup health monitoring
            if not self.setup_health_monitoring():
                return False

            # Step 5: Create integration summary
            summary = self.create_integration_summary()

            # Update final status
            self.integration_status["status"] = "operational"

            logger.info("🎉 Stage 7 Web Interface Integration completed!")
            logger.info(f"📊 Integration Status: {summary['status']}")
            logger.info(f"🌐 Web Dashboard: {summary['access_urls']['web_dashboard']}")
            logger.info(
                f"🔮 Prediction API: {summary['access_urls']['prediction_api']}"
            )
            logger.info(f"📚 API Docs: {summary['access_urls']['api_documentation']}")

            return True

        except Exception as e:
            logger.error(f"❌ Stage 7 integration failed: {e}")
            self.integration_status["status"] = "failed"
            return False


def main():
    """Main Stage 7 execution"""
    logger.info("🚀 Initializing Stage 7: Web Interface Integration")

    # Create Stage 7 implementation
    stage7 = Stage7WebIntegrationContainer()

    # Execute Stage 7 integration
    success = stage7.run_stage7_integration()

    if success:
        logger.info("✅ Stage 7 completed successfully!")
        print("\n🌐 Stage 7 Web Interface Integration Complete!")
        print("=" * 60)
        print("🎯 Integration Components:")
        print("  ✅ Prediction API Configuration")
        print("  ✅ Web Application Integration")
        print("  ✅ Health Monitoring Setup")
        print("  ✅ Real-time Updates Configured")
        print("\n🔗 Access Points:")
        print(f"  🌐 Web Dashboard: http://localhost:{stage7.web_port}")
        print(f"  🔮 Prediction API: http://localhost:{stage7.api_port}")
        print(f"  📚 API Documentation: http://localhost:{stage7.api_port}/docs")
        print(f"  💚 Health Check: http://localhost:{stage7.api_port}/health")
        print("\n📋 Next Steps:")
        print("  1. Start prediction API service (if not running)")
        print("  2. Access web dashboard for live predictions")
        print("  3. Test API integration through web interface")
        print("  4. Proceed to Stage 8: Betting Integration")
        print("=" * 60)
    else:
        logger.error("❌ Stage 7 failed!")
        print("❌ Web Interface Integration failed!")

    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
