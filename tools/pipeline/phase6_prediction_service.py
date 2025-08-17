#!/usr/bin/env python3
"""
🔮 Phase 6: Prediction Service Activation System
==============================================

Launches and manages the real-time prediction API service.
Triggered after Phase 5 model validation to start serving predictions.

Features:
- Production model loading and validation
- FastAPI prediction service startup
- Health monitoring and service recovery
- Model hot-swapping capabilities
- Performance metrics collection
"""

import json
import logging
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests
import psutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PredictionServiceManager:
    """Manages the prediction API service lifecycle"""
    
    def __init__(self):
        self.api_port = 8000
        self.api_host = "0.0.0.0"
        self.models_dir = Path("/app/models/production")
        self.service_pid_file = Path("/app/logs/prediction_service.pid")
        self.api_script = Path("/app/api/prediction_api.py")
        self.health_check_url = f"http://localhost:{self.api_port}/health"
        
        # Ensure directories exist
        Path("/app/logs").mkdir(exist_ok=True)
    
    def check_production_models(self) -> bool:
        """Verify production models are available and valid"""
        logger.info("🔍 Checking production models availability...")
        
        try:
            manifest_path = self.models_dir / "production_manifest.json"
            
            if not manifest_path.exists():
                logger.error("❌ Production manifest not found")
                return False
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            active_models = manifest.get("active_models", [])
            if not active_models:
                logger.error("❌ No active models found in production manifest")
                return False
            
            # Verify model files exist
            missing_models = []
            for model_id in active_models:
                model_info = manifest["models"].get(model_id, {})
                model_path = Path(model_info.get("file_path", ""))
                
                if not model_path.exists():
                    missing_models.append(model_id)
            
            if missing_models:
                logger.error(f"❌ Missing model files: {missing_models}")
                return False
            
            logger.info(f"✅ Found {len(active_models)} production-ready models")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking production models: {e}")
            return False
    
    def check_api_dependencies(self) -> bool:
        """Verify API script and dependencies are available"""
        logger.info("🔧 Checking API dependencies...")
        
        try:
            # Check if API script exists
            if not self.api_script.exists():
                logger.error(f"❌ API script not found: {self.api_script}")
                return False
            
            # Check if required packages are available
            required_packages = ["fastapi", "uvicorn", "joblib", "numpy", "pandas"]
            missing_packages = []
            
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                logger.error(f"❌ Missing packages: {missing_packages}")
                return False
            
            logger.info("✅ All API dependencies available")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking API dependencies: {e}")
            return False
    
    def is_service_running(self) -> bool:
        """Check if prediction service is already running"""
        try:
            if self.service_pid_file.exists():
                with open(self.service_pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    if "uvicorn" in process.name() or "prediction_api" in " ".join(process.cmdline()):
                        return True
            
            return False
            
        except Exception:
            return False
    
    def stop_existing_service(self) -> bool:
        """Stop any existing prediction service"""
        logger.info("🛑 Stopping existing prediction service...")
        
        try:
            if self.service_pid_file.exists():
                with open(self.service_pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    process.terminate()
                    process.wait(timeout=10)
                    logger.info(f"✅ Stopped existing service (PID: {pid})")
                
                self.service_pid_file.unlink()
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Error stopping existing service: {e}")
            return True  # Continue anyway
    
    def start_prediction_service(self) -> bool:
        """Start the FastAPI prediction service"""
        logger.info("🚀 Starting prediction service...")
        
        try:
            # Stop any existing service
            self.stop_existing_service()
            
            # Start new service
            cmd = [
                "python", "-m", "uvicorn",
                "api.prediction_api:app",
                "--host", self.api_host,
                "--port", str(self.api_port),
                "--reload",
                "--access-log"
            ]
            
            # Start process
            process = subprocess.Popen(
                cmd,
                cwd="/app",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Save PID
            with open(self.service_pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait a moment for startup
            time.sleep(5)
            
            # Verify service started
            if self.verify_service_health():
                logger.info(f"✅ Prediction service started successfully (PID: {process.pid})")
                return True
            else:
                logger.error("❌ Service started but health check failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start prediction service: {e}")
            return False
    
    def verify_service_health(self) -> bool:
        """Verify the prediction service is healthy and responding"""
        logger.info("🏥 Verifying service health...")
        
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    f"http://localhost:{self.api_port}/health",
                    timeout=5
                )
                
                if response.status_code == 200:
                    health_data = response.json()
                    logger.info(f"✅ Service healthy: {health_data.get('status', 'unknown')}")
                    return True
                    
            except requests.exceptions.RequestException:
                if attempt < max_attempts - 1:
                    logger.info(f"⏳ Health check attempt {attempt + 1}/{max_attempts}, retrying...")
                    time.sleep(2)
                else:
                    logger.error("❌ Service health check failed after all attempts")
        
        return False
    
    def test_prediction_endpoint(self) -> bool:
        """Test the prediction endpoint with sample data"""
        logger.info("🧪 Testing prediction endpoint...")
        
        try:
            # Sample test data for a horse prediction
            test_data = {
                "horse_name": "Test Horse",
                "horse_age": 4,
                "draw": 5,
                "win_odds": 3.5,
                "place_odds": 1.8,
                "barrier": 5,
                "margin": 0.0,
                "horse_weight_kg": 500.0,
                "handicap_weight": 58.0
            }
            
            response = requests.post(
                f"http://localhost:{self.api_port}/predict/horse",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                prediction = response.json()
                logger.info(f"✅ Prediction test successful: {prediction.get('confidence', 'N/A')}")
                return True
            else:
                logger.error(f"❌ Prediction test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Prediction test error: {e}")
            return False
    
    def setup_service_monitoring(self) -> bool:
        """Setup monitoring for the prediction service"""
        logger.info("📊 Setting up service monitoring...")
        
        try:
            # Create monitoring configuration
            monitoring_config = {
                "service_name": "horse_racing_prediction_api",
                "port": self.api_port,
                "health_check_url": self.health_check_url,
                "restart_on_failure": True,
                "max_restart_attempts": 3,
                "monitoring_interval": 60,
                "setup_timestamp": datetime.now().isoformat()
            }
            
            # Save monitoring config
            config_path = Path("/app/logs/service_monitoring.json")
            with open(config_path, 'w') as f:
                json.dump(monitoring_config, f, indent=2)
            
            logger.info("✅ Service monitoring configured")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup monitoring: {e}")
            return False
    
    def run_phase6_pipeline(self) -> bool:
        """Run the complete Phase 6 prediction service activation"""
        logger.info("🚀 Starting Phase 6: Prediction Service Activation")
        
        try:
            # Step 1: Check production models
            if not self.check_production_models():
                return False
            
            # Step 2: Check API dependencies
            if not self.check_api_dependencies():
                return False
            
            # Step 3: Start prediction service
            if not self.start_prediction_service():
                return False
            
            # Step 4: Verify service health
            if not self.verify_service_health():
                return False
            
            # Step 5: Test prediction endpoint
            if not self.test_prediction_endpoint():
                logger.warning("⚠️ Prediction test failed, but service appears to be running")
            
            # Step 6: Setup monitoring
            self.setup_service_monitoring()
            
            logger.info("✅ Phase 6: Prediction service activation completed successfully")
            logger.info(f"🌐 Prediction API available at: http://localhost:{self.api_port}")
            logger.info(f"📖 API documentation at: http://localhost:{self.api_port}/docs")
            return True
            
        except Exception as e:
            logger.error(f"❌ Phase 6 activation failed: {e}")
            return False


def main():
    """Main prediction service activation function"""
    manager = PredictionServiceManager()
    success = manager.run_phase6_pipeline()
    
    if success:
        logger.info("🎉 Phase 6 completed: Prediction service is active!")
        exit(0)
    else:
        logger.error("❌ Phase 6 failed: Prediction service activation issues")
        exit(1)


if __name__ == "__main__":
    main()
