#!/usr/bin/env python3
"""
🧪 Stage 7 Web Integration Testing Framework

Tests the complete web interface integration with prediction service,
validating all Stage 7 components and functionality.

Test Categories:
1. Web Container Health Tests
2. Prediction API Integration Tests  
3. UI Component Integration Tests
4. Real-time Update Tests
5. End-to-End Integration Tests
"""

import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Stage7TestFramework:
    """Comprehensive testing framework for Stage 7 web integration"""
    
    def __init__(self):
        self.stage = 7
        self.models_dir = Path("/app/models")
        self.web_container = "horse_racing_web_app_clean"
        self.ml_container = "horse_racing_ml_trainer_clean"
        self.test_results = []
        
    def run_test(self, test_name: str, test_func) -> bool:
        """Execute a test and record results"""
        logger.info(f"🧪 Running test: {test_name}")
        
        try:
            start_time = datetime.now()
            result = test_func()
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.test_results.append({
                "test_name": test_name,
                "result": "PASS" if result else "FAIL",
                "duration": duration,
                "timestamp": start_time.isoformat()
            })
            
            if result:
                logger.info(f"✅ {test_name} - PASSED ({duration:.2f}s)")
            else:
                logger.error(f"❌ {test_name} - FAILED ({duration:.2f}s)")
                
            return result
            
        except Exception as e:
            logger.error(f"❌ {test_name} - ERROR: {e}")
            self.test_results.append({
                "test_name": test_name,
                "result": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    def test_web_container_health(self) -> bool:
        """Test web container health and accessibility"""
        try:
            # Check container status
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.web_container}", 
                 "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if not result.stdout.strip():
                logger.error("Web container not running")
                return False
                
            # Test web app accessibility
            health_check = subprocess.run(
                ["docker", "exec", self.web_container, 
                 "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                 "http://localhost:3000"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            return health_check.stdout.strip() == "200"
            
        except Exception as e:
            logger.error(f"Web container health test failed: {e}")
            return False
    
    def test_prediction_api_health(self) -> bool:
        """Test prediction API health and endpoints"""
        try:
            # Test health endpoint
            health_response = subprocess.run(
                ["docker", "exec", self.ml_container,
                 "curl", "-s", "-w", "%{http_code}", 
                 "http://localhost:8000/health"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "200" not in health_response.stdout:
                logger.error("Prediction API health check failed")
                return False
            
            # Test models status endpoint
            models_response = subprocess.run(
                ["docker", "exec", self.ml_container,
                 "curl", "-s", "-w", "%{http_code}", 
                 "http://localhost:8000/models/status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return "200" in models_response.stdout
            
        except Exception as e:
            logger.error(f"Prediction API health test failed: {e}")
            return False
    
    def test_prediction_functionality(self) -> bool:
        """Test prediction API functionality with sample data"""
        try:
            # Create sample prediction request
            sample_data = {
                "features": [0.5] * 20,  # 20 features
                "model_name": "RandomForestClassifier"
            }
            
            # Save to temporary file
            test_file = "/tmp/stage7_test_prediction.json"
            with open(test_file, 'w') as f:
                json.dump(sample_data, f)
            
            # Copy to ML container
            subprocess.run(
                ["docker", "cp", test_file, 
                 f"{self.ml_container}:/tmp/test_prediction.json"],
                check=True
            )
            
            # Test prediction endpoint
            prediction_response = subprocess.run(
                ["docker", "exec", self.ml_container,
                 "curl", "-s", "-X", "POST",
                 "http://localhost:8000/predict/horse",
                 "-H", "Content-Type: application/json",
                 "-d", "@/tmp/test_prediction.json"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if prediction_response.returncode != 0:
                return False
                
            # Parse response
            try:
                result = json.loads(prediction_response.stdout)
                return ("prediction" in result and 
                       "confidence" in result and
                       "model_used" in result)
            except json.JSONDecodeError:
                return False
                
        except Exception as e:
            logger.error(f"Prediction functionality test failed: {e}")
            return False
    
    def test_api_integration(self) -> bool:
        """Test web app to prediction API integration"""
        try:
            # Test if web container can reach prediction API
            api_test = subprocess.run(
                ["docker", "exec", self.web_container,
                 "curl", "-s", "-w", "%{http_code}",
                 "http://host.docker.internal:8000/health"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            return "200" in api_test.stdout
            
        except Exception as e:
            logger.error(f"API integration test failed: {e}")
            return False
    
    def test_stage7_configuration(self) -> bool:
        """Test Stage 7 configuration files"""
        try:
            # Check for Stage 7 configuration files
            config_files = [
                "stage7_api_config.json",
                "stage7_realtime_config.json",
                "stage7_integration_summary.json"
            ]
            
            for config_file in config_files:
                config_path = self.models_dir / config_file
                if not config_path.exists():
                    logger.error(f"Configuration file {config_file} not found")
                    return False
                    
                # Validate JSON structure
                try:
                    with open(config_path, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in {config_file}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration test failed: {e}")
            return False
    
    def test_web_ui_functionality(self) -> bool:
        """Test web UI functionality and components"""
        try:
            # Test if React app is serving properly
            react_test = subprocess.run(
                ["docker", "exec", self.web_container,
                 "curl", "-s", "http://localhost:3000"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if react_test.returncode != 0:
                return False
                
            # Check for key HTML elements
            html_content = react_test.stdout
            required_elements = [
                "<div id=\"root\">",
                "Horse Racing",
                "Dashboard"
            ]
            
            return all(element in html_content for element in required_elements)
            
        except Exception as e:
            logger.error(f"Web UI functionality test failed: {e}")
            return False
    
    def test_real_time_capabilities(self) -> bool:
        """Test real-time update capabilities"""
        try:
            # Check if real-time configuration exists
            config_path = self.models_dir / "stage7_realtime_config.json"
            if not config_path.exists():
                return False
                
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Validate real-time configuration structure
            required_keys = ["websocket", "polling", "notifications"]
            return all(key in config for key in required_keys)
            
        except Exception as e:
            logger.error(f"Real-time capabilities test failed: {e}")
            return False
    
    def test_end_to_end_workflow(self) -> bool:
        """Test complete end-to-end prediction workflow"""
        try:
            # Simulate complete prediction workflow
            
            # 1. Test API health
            if not self.test_prediction_api_health():
                return False
                
            # 2. Test prediction functionality
            if not self.test_prediction_functionality():
                return False
                
            # 3. Test web integration
            if not self.test_api_integration():
                return False
                
            logger.info("✅ End-to-end workflow test completed")
            return True
            
        except Exception as e:
            logger.error(f"End-to-end workflow test failed: {e}")
            return False
    
    def generate_test_report(self) -> Dict:
        """Generate comprehensive test report"""
        logger.info("📊 Generating Stage 7 test report...")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results 
                          if result["result"] == "PASS")
        failed_tests = sum(1 for result in self.test_results 
                          if result["result"] == "FAIL")
        error_tests = sum(1 for result in self.test_results 
                         if result["result"] == "ERROR")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "stage": self.stage,
            "test_suite": "Stage 7 Web Integration Tests",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate": f"{success_rate:.1f}%"
            },
            "test_results": self.test_results,
            "status": "PASS" if failed_tests == 0 and error_tests == 0 else "FAIL",
            "recommendations": self.generate_recommendations()
        }
        
        # Save test report
        report_path = self.models_dir / "stage7_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for specific failures
        failed_tests = [result for result in self.test_results 
                       if result["result"] in ["FAIL", "ERROR"]]
        
        if any("web_container" in test["test_name"].lower() 
               for test in failed_tests):
            recommendations.append(
                "Restart web container: docker restart horse_racing_web_app_clean"
            )
        
        if any("prediction_api" in test["test_name"].lower() 
               for test in failed_tests):
            recommendations.append(
                "Check prediction API service in ML container"
            )
        
        if any("integration" in test["test_name"].lower() 
               for test in failed_tests):
            recommendations.append(
                "Verify network connectivity between containers"
            )
        
        if not recommendations:
            recommendations.append("All tests passed - Stage 7 ready for production")
        
        return recommendations
    
    def run_all_tests(self) -> bool:
        """Run all Stage 7 tests"""
        logger.info("🧪 Starting Stage 7 comprehensive test suite")
        
        test_suite = [
            ("Web Container Health", self.test_web_container_health),
            ("Prediction API Health", self.test_prediction_api_health),
            ("Prediction Functionality", self.test_prediction_functionality),
            ("API Integration", self.test_api_integration),
            ("Stage 7 Configuration", self.test_stage7_configuration),
            ("Web UI Functionality", self.test_web_ui_functionality),
            ("Real-time Capabilities", self.test_real_time_capabilities),
            ("End-to-End Workflow", self.test_end_to_end_workflow)
        ]
        
        # Execute all tests
        all_passed = True
        for test_name, test_func in test_suite:
            if not self.run_test(test_name, test_func):
                all_passed = False
        
        # Generate test report
        report = self.generate_test_report()
        
        # Display results
        logger.info("📊 Stage 7 Test Results:")
        logger.info(f"Total Tests: {report['summary']['total_tests']}")
        logger.info(f"Passed: {report['summary']['passed']}")
        logger.info(f"Failed: {report['summary']['failed']}")
        logger.info(f"Errors: {report['summary']['errors']}")
        logger.info(f"Success Rate: {report['summary']['success_rate']}")
        
        if report["status"] == "PASS":
            logger.info("🎉 All Stage 7 tests passed!")
        else:
            logger.error("❌ Some Stage 7 tests failed")
            logger.info("💡 Recommendations:")
            for rec in report["recommendations"]:
                logger.info(f"  - {rec}")
        
        return all_passed


def main():
    """Main test execution"""
    logger.info("🚀 Starting Stage 7 Web Integration Tests")
    
    # Create test framework
    test_framework = Stage7TestFramework()
    
    # Run all tests
    success = test_framework.run_all_tests()
    
    if success:
        print("✅ Stage 7 tests completed successfully!")
        print("🌐 Web interface integration fully validated")
    else:
        print("❌ Stage 7 tests completed with failures")
        print("🔧 Check test report for recommendations")
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
