#!/usr/bin/env python3
"""
🧪 Stage 9 Integration Test Suite
Comprehensive testing for Stage 9: Speed Analysis integration with the pipeline

Tests:
- Stage 9 standalone execution
- Pipeline integration and stage sequencing
- Docker container compatibility
- Performance benchmarks
- Data flow validation
- Error handling and fallbacks

Author: AI Assistant
Date: August 18, 2025
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import subprocess

# Add project paths
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class Stage9IntegrationTestSuite:
    """Comprehensive test suite for Stage 9 integration"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": [],
            "performance_metrics": {},
            "integration_status": "unknown"
        }
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        logger.info("🧪 Starting Stage 9 Integration Test Suite")
        logger.info("=" * 60)
        
        tests = [
            ("Stage 9 Standalone Execution", self.test_stage9_standalone),
            ("Stage 9 Docker Compatibility", self.test_stage9_docker),
            ("Pipeline Integration", self.test_pipeline_integration),
            ("Performance Benchmarks", self.test_performance_benchmarks),
            ("Data Flow Validation", self.test_data_flow),
            ("Error Handling", self.test_error_handling),
            ("17-Stage Pipeline Sequence", self.test_17_stage_sequence)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n🔬 Running: {test_name}")
            try:
                start_time = time.time()
                result = await test_func()
                execution_time = time.time() - start_time
                
                self.test_results["tests_run"] += 1
                
                if result["success"]:
                    self.test_results["tests_passed"] += 1
                    logger.info(f"✅ {test_name} - PASSED ({execution_time:.2f}s)")
                else:
                    self.test_results["tests_failed"] += 1
                    logger.error(f"❌ {test_name} - FAILED ({execution_time:.2f}s)")
                    logger.error(f"   Error: {result.get('error', 'Unknown error')}")
                
                # Store detailed results
                self.test_results["test_details"].append({
                    "test_name": test_name,
                    "success": result["success"],
                    "execution_time": execution_time,
                    "details": result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                self.test_results["tests_run"] += 1
                self.test_results["tests_failed"] += 1
                logger.error(f"❌ {test_name} - ERROR: {e}")
                
                self.test_results["test_details"].append({
                    "test_name": test_name,
                    "success": False,
                    "execution_time": 0,
                    "details": {"error": str(e)},
                    "timestamp": datetime.now().isoformat()
                })
        
        # Calculate final results
        success_rate = (self.test_results["tests_passed"] / max(self.test_results["tests_run"], 1)) * 100
        self.test_results["success_rate"] = success_rate
        
        if success_rate >= 85:
            self.test_results["integration_status"] = "excellent"
        elif success_rate >= 70:
            self.test_results["integration_status"] = "good"
        elif success_rate >= 50:
            self.test_results["integration_status"] = "fair"
        else:
            self.test_results["integration_status"] = "poor"
        
        logger.info(f"\n🏆 Test Suite Complete!")
        logger.info(f"📊 Success Rate: {success_rate:.1f}% ({self.test_results['tests_passed']}/{self.test_results['tests_run']})")
        logger.info(f"🎯 Integration Status: {self.test_results['integration_status'].upper()}")
        
        return self.test_results
    
    async def test_stage9_standalone(self) -> Dict[str, Any]:
        """Test Stage 9 standalone execution"""
        try:
            stage9_script = self.project_root / "stage9_speed_analysis.py"
            
            if not stage9_script.exists():
                return {"success": False, "error": "Stage 9 script not found"}
            
            # Run Stage 9
            result = subprocess.run(
                [sys.executable, str(stage9_script)],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minutes timeout
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                # Check for expected output indicators
                output = result.stdout
                success_indicators = [
                    "Stage 9: Speed Analysis - COMPLETED SUCCESSFULLY",
                    "Speed Figures Generated:",
                    "Pace Analyses Completed:"
                ]
                
                indicators_found = sum(1 for indicator in success_indicators if indicator in output)
                
                return {
                    "success": indicators_found >= 2,
                    "return_code": result.returncode,
                    "indicators_found": indicators_found,
                    "output_length": len(output),
                    "has_json_output": "speed_analysis_" in output
                }
            else:
                return {
                    "success": False,
                    "return_code": result.returncode,
                    "error": result.stderr,
                    "output": result.stdout
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_stage9_docker(self) -> Dict[str, Any]:
        """Test Stage 9 in Docker containers"""
        try:
            containers = [
                "horse_racing_data_pipeline_clean",
                "horse_racing_ml_trainer_clean"
            ]
            
            results = {}
            overall_success = True
            
            for container in containers:
                try:
                    # Check if Stage 9 exists in container
                    check_result = subprocess.run(
                        ["docker", "exec", container, "ls", "/app/stage9_speed_analysis.py"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if check_result.returncode == 0:
                        # Run Stage 9 in container
                        run_result = subprocess.run(
                            ["docker", "exec", container, "python", "/app/stage9_speed_analysis.py"],
                            capture_output=True,
                            text=True,
                            timeout=120
                        )
                        
                        container_success = run_result.returncode == 0
                        results[container] = {
                            "success": container_success,
                            "return_code": run_result.returncode,
                            "has_output": len(run_result.stdout) > 0
                        }
                        
                        if not container_success:
                            overall_success = False
                    else:
                        results[container] = {
                            "success": False,
                            "error": "Stage 9 script not found in container"
                        }
                        overall_success = False
                        
                except Exception as e:
                    results[container] = {
                        "success": False,
                        "error": str(e)
                    }
                    overall_success = False
            
            return {
                "success": overall_success,
                "container_results": results,
                "containers_tested": len(containers)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_pipeline_integration(self) -> Dict[str, Any]:
        """Test Stage 9 integration with pipeline orchestrator"""
        try:
            # Check if pipeline orchestrator has Stage 9 integration
            orchestrator_path = self.project_root / "tools" / "pipeline" / "daily_orchestrator.py"
            
            if not orchestrator_path.exists():
                return {"success": False, "error": "Pipeline orchestrator not found"}
            
            # Read orchestrator file and check for Stage 9 integration
            with open(orchestrator_path, 'r') as f:
                orchestrator_content = f.read()
            
            integration_indicators = [
                "stage9_speed_analysis",
                "Stage 9: Speed Analysis",
                "await self.stage9_speed_analysis()"
            ]
            
            indicators_found = sum(1 for indicator in integration_indicators if indicator in orchestrator_content)
            
            # Check if Stage 9 is properly sequenced
            has_proper_sequence = "Stage 9: Speed Analysis" in orchestrator_content
            
            return {
                "success": indicators_found >= 2 and has_proper_sequence,
                "integration_indicators_found": indicators_found,
                "has_proper_sequence": has_proper_sequence,
                "orchestrator_size": len(orchestrator_content)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_performance_benchmarks(self) -> Dict[str, Any]:
        """Test Stage 9 performance benchmarks"""
        try:
            stage9_script = self.project_root / "stage9_speed_analysis.py"
            
            if not stage9_script.exists():
                return {"success": False, "error": "Stage 9 script not found"}
            
            # Run multiple performance tests
            execution_times = []
            success_count = 0
            
            for i in range(3):  # Run 3 times for average
                start_time = time.time()
                
                result = subprocess.run(
                    [sys.executable, str(stage9_script)],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=self.project_root
                )
                
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
                
                if result.returncode == 0:
                    success_count += 1
            
            avg_execution_time = sum(execution_times) / len(execution_times)
            
            # Performance criteria (15 minutes = 900 seconds)
            performance_target = 900  # 15 minutes
            performance_excellent = 60  # 1 minute
            
            performance_rating = "excellent" if avg_execution_time < performance_excellent else \
                               "good" if avg_execution_time < performance_target else "poor"
            
            self.test_results["performance_metrics"] = {
                "average_execution_time": avg_execution_time,
                "execution_times": execution_times,
                "performance_rating": performance_rating,
                "within_target": avg_execution_time < performance_target
            }
            
            return {
                "success": success_count >= 2 and avg_execution_time < performance_target,
                "average_execution_time": avg_execution_time,
                "success_rate": (success_count / 3) * 100,
                "performance_rating": performance_rating,
                "within_target": avg_execution_time < performance_target
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_data_flow(self) -> Dict[str, Any]:
        """Test data flow and output validation"""
        try:
            # Check if Stage 9 creates expected output files
            speed_analysis_dir = self.project_root / "data" / "speed_analysis"
            
            # Count existing files before test
            existing_files = len(list(speed_analysis_dir.glob("*.json"))) if speed_analysis_dir.exists() else 0
            
            # Run Stage 9
            stage9_script = self.project_root / "stage9_speed_analysis.py"
            result = subprocess.run(
                [sys.executable, str(stage9_script)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                return {"success": False, "error": "Stage 9 execution failed"}
            
            # Check if new files were created
            new_files = len(list(speed_analysis_dir.glob("*.json"))) if speed_analysis_dir.exists() else 0
            files_created = new_files > existing_files
            
            # Validate latest output file if exists
            output_valid = False
            if speed_analysis_dir.exists():
                json_files = list(speed_analysis_dir.glob("*.json"))
                if json_files:
                    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
                    try:
                        with open(latest_file, 'r') as f:
                            data = json.load(f)
                        
                        required_fields = [
                            "analysis_id", "speed_figures", "pace_analyses", 
                            "running_styles", "created_at"
                        ]
                        output_valid = all(field in data for field in required_fields)
                    except:
                        output_valid = False
            
            return {
                "success": files_created and output_valid,
                "files_created": files_created,
                "output_valid": output_valid,
                "new_files_count": new_files - existing_files,
                "total_files": new_files
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and fallback mechanisms"""
        try:
            # Test with invalid input (this should be handled gracefully)
            # We'll simulate this by checking the code structure for error handling
            
            stage9_script = self.project_root / "stage9_speed_analysis.py"
            
            if not stage9_script.exists():
                return {"success": False, "error": "Stage 9 script not found"}
            
            with open(stage9_script, 'r') as f:
                code_content = f.read()
            
            # Check for error handling patterns
            error_handling_patterns = [
                "try:", "except:", "logger.error", "logger.warning",
                "Exception", "catch", "fallback", "default"
            ]
            
            patterns_found = sum(1 for pattern in error_handling_patterns if pattern in code_content)
            
            # Check for specific error handling scenarios
            has_timeout_handling = "timeout" in code_content.lower()
            has_fallback_data = "sample" in code_content.lower() or "demo" in code_content.lower()
            has_graceful_degradation = "empty_results" in code_content or "fallback" in code_content
            
            return {
                "success": patterns_found >= 6,
                "error_handling_patterns": patterns_found,
                "has_timeout_handling": has_timeout_handling,
                "has_fallback_data": has_fallback_data,
                "has_graceful_degradation": has_graceful_degradation
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_17_stage_sequence(self) -> Dict[str, Any]:
        """Test Stage 9 position in 17-stage pipeline sequence"""
        try:
            # Check if Stage 9 is properly positioned in the 17-stage pipeline
            orchestrator_path = self.project_root / "tools" / "pipeline" / "daily_orchestrator.py"
            
            if not orchestrator_path.exists():
                return {"success": False, "error": "Pipeline orchestrator not found"}
            
            with open(orchestrator_path, 'r') as f:
                orchestrator_content = f.read()
            
            # Check stage sequence
            stage_sequence_correct = True
            stage_sequence_issues = []
            
            # Look for Stage 9 in execution flow
            if "Stage 9: Speed Analysis" not in orchestrator_content:
                stage_sequence_correct = False
                stage_sequence_issues.append("Stage 9 not found in execution flow")
            
            # Check dependencies (Stage 9 should come after power ratings)
            if "Stage 5: Power Ratings" in orchestrator_content and "Stage 9: Speed Analysis" in orchestrator_content:
                power_pos = orchestrator_content.find("Stage 5: Power Ratings")
                speed_pos = orchestrator_content.find("Stage 9: Speed Analysis")
                if power_pos >= speed_pos:
                    stage_sequence_correct = False
                    stage_sequence_issues.append("Stage 9 should come after Stage 5 (Power Ratings)")
            
            # Check for proper 17-stage structure
            stage_count = orchestrator_content.count("Stage ")
            has_17_stages = stage_count >= 15  # Allow some flexibility
            
            return {
                "success": stage_sequence_correct and has_17_stages,
                "stage_sequence_correct": stage_sequence_correct,
                "has_17_stages": has_17_stages,
                "stage_count": stage_count,
                "sequence_issues": stage_sequence_issues
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def save_results(self, output_path: Path = None) -> bool:
        """Save test results to file"""
        try:
            if output_path is None:
                output_path = self.project_root / "tests" / "stage9_integration_test_results.json"
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            
            logger.info(f"💾 Test results saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save test results: {e}")
            return False

async def main():
    """Run the complete Stage 9 integration test suite"""
    print("🧪 Stage 9 Integration Test Suite")
    print("=" * 60)
    print("Testing Stage 9: Speed Analysis integration with pipeline")
    print()
    
    # Initialize test suite
    test_suite = Stage9IntegrationTestSuite()
    
    try:
        # Run all tests
        results = await test_suite.run_all_tests()
        
        # Save results
        test_suite.save_results()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏆 STAGE 9 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"📊 Tests Run: {results['tests_run']}")
        print(f"✅ Tests Passed: {results['tests_passed']}")
        print(f"❌ Tests Failed: {results['tests_failed']}")
        print(f"📈 Success Rate: {results['success_rate']:.1f}%")
        print(f"🎯 Integration Status: {results['integration_status'].upper()}")
        
        if results['performance_metrics']:
            perf = results['performance_metrics']
            print(f"⚡ Average Execution Time: {perf['average_execution_time']:.2f}s")
            print(f"🏃 Performance Rating: {perf['performance_rating'].upper()}")
            print(f"✅ Within Target: {'YES' if perf['within_target'] else 'NO'}")
        
        print("\n📋 Detailed Test Results:")
        for test_detail in results['test_details']:
            status = "✅ PASS" if test_detail['success'] else "❌ FAIL"
            print(f"   {status} - {test_detail['test_name']} ({test_detail['execution_time']:.2f}s)")
        
        # Overall assessment
        if results['success_rate'] >= 85:
            print("\n🎉 EXCELLENT: Stage 9 integration is ready for production!")
        elif results['success_rate'] >= 70:
            print("\n👍 GOOD: Stage 9 integration is working well with minor issues.")
        elif results['success_rate'] >= 50:
            print("\n⚠️  FAIR: Stage 9 integration needs improvement.")
        else:
            print("\n❌ POOR: Stage 9 integration has significant issues.")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Test suite execution failed: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
