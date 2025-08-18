#!/usr/bin/env python3
"""
🌐 Stage 7: Web Interface Integration with Prediction Service

Stage 7 integrates the React web application with the Stage 6 prediction service,
creating a complete web-based interface for horse racing predictions.

Key Features:
1. React Web App Integration with Stage 6 API
2. Real-time Prediction Interface
3. Web Dashboard with Live Data
4. API Integration Testing
5. Complete UI/UX Integration

Dependencies: 
- Stage 6: Prediction Service must be operational
- React Web App: Running in docker container
- FastAPI: Prediction endpoints accessible
"""

import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Stage7WebIntegration:
    """Stage 7: Web Interface Integration Implementation"""
    
    def __init__(self):
        self.stage = 7
        self.models_dir = Path("/app/models")
        self.web_container = "horse_racing_web_app_clean"
        self.ml_container = "horse_racing_ml_trainer_clean"
        self.prediction_api_port = 8000
        self.web_app_port = 3000
        self.prediction_api_url = f"http://localhost:{self.prediction_api_port}"
        self.web_app_url = f"http://localhost:{self.web_app_port}"
        
        # Integration status
        self.integration_status = {
            "stage": self.stage,
            "status": "initializing",
            "prediction_service": False,
            "web_app": False,
            "api_integration": False,
            "ui_components": False,
            "real_time_updates": False
        }
        
    def check_stage6_prerequisites(self) -> bool:
        """Check if Stage 6 prediction service is operational"""
        logger.info("🔍 Checking Stage 6 prerequisites...")
        
        try:
            # Check if Stage 6 service summary exists
            summary_path = self.models_dir / "stage6_service_summary.json"
            if not summary_path.exists():
                logger.error("❌ Stage 6 service summary not found")
                return False
                
            with open(summary_path, 'r') as f:
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
    
    def check_web_app_status(self) -> bool:
        """Check web application container status"""
        logger.info("🌐 Checking web application status...")
        
        try:
            # Check if web container is running
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.web_container}", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if not result.stdout.strip():
                logger.error(f"❌ Web container {self.web_container} not running")
                return False
                
            if "unhealthy" in result.stdout.lower():
                logger.warning("⚠️ Web container marked as unhealthy, attempting to restart...")
                return self.restart_web_container()
                
            logger.info("✅ Web application container running")
            self.integration_status["web_app"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking web app status: {e}")
            return False
    
    def restart_web_container(self) -> bool:
        """Restart the web application container"""
        logger.info("🔄 Restarting web application container...")
        
        try:
            # Restart the container
            subprocess.run(
                ["docker", "restart", self.web_container],
                check=True,
                timeout=30
            )
            
            # Wait for container to start
            time.sleep(10)
            
            # Check status again
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.web_container}", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout.strip() and "up" in result.stdout.lower():
                logger.info("✅ Web container restarted successfully")
                return True
            else:
                logger.error("❌ Web container restart failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error restarting web container: {e}")
            return False
    
    def start_prediction_api(self) -> bool:
        """Start the prediction API service in the ML container"""
        logger.info("🚀 Starting prediction API service...")
        
        try:
            # Start the prediction API in background
            subprocess.Popen(
                [
                    "docker", "exec", "-d", self.ml_container,
                    "python", "/app/api/prediction_api.py"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for API to start
            time.sleep(5)
            
            # Test API health
            if self.test_prediction_api():
                logger.info("✅ Prediction API started successfully")
                return True
            else:
                logger.error("❌ Prediction API failed to start properly")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting prediction API: {e}")
            return False
    
    def test_prediction_api(self) -> bool:
        """Test the prediction API endpoints"""
        logger.info("🧪 Testing prediction API endpoints...")
        
        try:
            # Test health endpoint
            health_response = subprocess.run(
                [
                    "docker", "exec", self.ml_container,
                    "curl", "-s", f"http://localhost:{self.prediction_api_port}/health"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if health_response.returncode != 0:
                logger.error("❌ API health check failed")
                return False
            
            # Test prediction endpoint with sample data
            sample_features = [0.5] * 20  # 20 features as expected by our models
            prediction_data = {
                "features": sample_features,
                "model_name": "RandomForestClassifier"
            }
            
            # Create temporary test file
            test_file = "/tmp/test_prediction.json"
            with open(test_file, 'w') as f:
                json.dump(prediction_data, f)
            
            # Copy to container and test
            subprocess.run(
                ["docker", "cp", test_file, f"{self.ml_container}:/tmp/test_prediction.json"],
                check=True
            )
            
            prediction_response = subprocess.run(
                [
                    "docker", "exec", self.ml_container,
                    "curl", "-s", "-X", "POST",
                    f"http://localhost:{self.prediction_api_port}/predict/horse",
                    "-H", "Content-Type: application/json",
                    "-d", "@/tmp/test_prediction.json"
                ],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if prediction_response.returncode == 0:
                try:
                    result = json.loads(prediction_response.stdout)
                    if "prediction" in result and "confidence" in result:
                        logger.info("✅ Prediction API endpoints working")
                        self.integration_status["api_integration"] = True
                        return True
                except json.JSONDecodeError:
                    pass
            
            logger.error("❌ Prediction API endpoints not responding correctly")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error testing prediction API: {e}")
            return False
    
    def configure_web_api_integration(self) -> bool:
        """Configure web app to integrate with prediction API"""
        logger.info("🔧 Configuring web-API integration...")
        
        try:
            # Create API configuration for the web app
            api_config = {
                "prediction_api": {
                    "base_url": f"http://localhost:{self.prediction_api_port}",
                    "endpoints": {
                        "health": "/health",
                        "predict_horse": "/predict/horse",
                        "predict_race": "/predict/race",
                        "models_status": "/models/status"
                    }
                },
                "integration": {
                    "real_time_updates": True,
                    "update_interval": 30000,  # 30 seconds
                    "retry_attempts": 3
                },
                "stage": 7,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save API configuration
            config_path = self.models_dir / "stage7_api_config.json"
            with open(config_path, 'w') as f:
                json.dump(api_config, f, indent=2)
            
            logger.info("✅ Web-API integration configured")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configuring web-API integration: {e}")
            return False
    
    def test_web_integration(self) -> bool:
        """Test complete web integration"""
        logger.info("🌐 Testing complete web integration...")
        
        try:
            # Test if web app can reach prediction API
            test_script = f"""
            # Test web app integration
            curl -s http://localhost:{self.web_app_port} > /dev/null
            if [ $? -eq 0 ]; then
                echo "Web app accessible"
            else
                echo "Web app not accessible"
                exit 1
            fi
            
            # Test prediction API from within web container
            curl -s http://host.docker.internal:{self.prediction_api_port}/health > /dev/null
            if [ $? -eq 0 ]; then
                echo "Prediction API accessible from web container"
            else
                echo "Prediction API not accessible from web container"
                exit 1
            fi
            """
            
            # Execute test in web container
            result = subprocess.run(
                ["docker", "exec", self.web_container, "sh", "-c", test_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and "accessible" in result.stdout:
                logger.info("✅ Web integration tests passed")
                self.integration_status["ui_components"] = True
                return True
            else:
                logger.error(f"❌ Web integration tests failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing web integration: {e}")
            return False
    
    def setup_real_time_updates(self) -> bool:
        """Setup real-time updates between web app and prediction service"""
        logger.info("⚡ Setting up real-time updates...")
        
        try:
            # Create real-time update configuration
            realtime_config = {
                "websocket": {
                    "enabled": True,
                    "port": 8001,
                    "path": "/ws"
                },
                "polling": {
                    "enabled": True,
                    "interval": 30,  # seconds
                    "endpoints": [
                        "/models/status",
                        "/health"
                    ]
                },
                "notifications": {
                    "predictions": True,
                    "system_status": True,
                    "model_updates": True
                }
            }
            
            # Save real-time configuration
            config_path = self.models_dir / "stage7_realtime_config.json"
            with open(config_path, 'w') as f:
                json.dump(realtime_config, f, indent=2)
            
            logger.info("✅ Real-time updates configured")
            self.integration_status["real_time_updates"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up real-time updates: {e}")
            return False
    
    def generate_stage7_summary(self) -> Dict:
        """Generate comprehensive Stage 7 integration summary"""
        logger.info("📊 Generating Stage 7 integration summary...")
        
        summary = {
            "stage": self.stage,
            "stage_name": "Web Interface Integration",
            "status": "operational" if all(self.integration_status.values()) else "partial",
            "timestamp": datetime.now().isoformat(),
            "integration_components": self.integration_status,
            "architecture": {
                "prediction_service": {
                    "container": self.ml_container,
                    "port": self.prediction_api_port,
                    "api_url": self.prediction_api_url
                },
                "web_application": {
                    "container": self.web_container,
                    "port": self.web_app_port,
                    "app_url": self.web_app_url
                }
            },
            "capabilities": {
                "real_time_predictions": self.integration_status["api_integration"],
                "web_dashboard": self.integration_status["web_app"],
                "ui_integration": self.integration_status["ui_components"],
                "live_updates": self.integration_status["real_time_updates"]
            },
            "endpoints": {
                "web_app": f"http://localhost:{self.web_app_port}",
                "prediction_api": f"http://localhost:{self.prediction_api_port}",
                "api_docs": f"http://localhost:{self.prediction_api_port}/docs"
            },
            "next_stage": {
                "stage": 8,
                "name": "Betting Integration",
                "prerequisites": "Web interface operational with live predictions"
            }
        }
        
        # Save summary
        summary_path = self.models_dir / "stage7_integration_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def run_stage7_integration(self) -> bool:
        """Execute complete Stage 7 web integration"""
        logger.info("🌐 Starting Stage 7: Web Interface Integration")
        
        try:
            # Step 1: Check Stage 6 prerequisites
            if not self.check_stage6_prerequisites():
                return False
            
            # Step 2: Check web application status
            if not self.check_web_app_status():
                return False
            
            # Step 3: Start prediction API
            if not self.start_prediction_api():
                return False
            
            # Step 4: Configure web-API integration
            if not self.configure_web_api_integration():
                return False
            
            # Step 5: Test web integration
            if not self.test_web_integration():
                return False
            
            # Step 6: Setup real-time updates
            if not self.setup_real_time_updates():
                return False
            
            # Step 7: Generate summary
            summary = self.generate_stage7_summary()
            
            # Final status update
            self.integration_status["status"] = "operational"
            
            logger.info("🎉 Stage 7 Web Interface Integration completed successfully!")
            logger.info(f"📊 Integration Status: {summary['status']}")
            logger.info(f"🌐 Web App: {summary['endpoints']['web_app']}")
            logger.info(f"🔮 Prediction API: {summary['endpoints']['prediction_api']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Stage 7 integration failed: {e}")
            self.integration_status["status"] = "failed"
            return False

def main():
    """Main Stage 7 execution"""
    logger.info("🚀 Initializing Stage 7: Web Interface Integration")
    
    # Create Stage 7 implementation
    stage7 = Stage7WebIntegration()
    
    # Execute Stage 7 integration
    success = stage7.run_stage7_integration()
    
    if success:
        logger.info("✅ Stage 7 completed successfully!")
        print("🌐 Web Interface Integration completed!")
        print(f"Access web app: http://localhost:{stage7.web_app_port}")
        print(f"Access API docs: http://localhost:{stage7.prediction_api_port}/docs")
    else:
        logger.error("❌ Stage 7 failed!")
        print("❌ Web Interface Integration failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
