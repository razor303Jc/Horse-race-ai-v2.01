"""
🏃‍♂️ C2 Test Runner Script
=========================

Script to run comprehensive C2 Command Center test suite with
organized test execution and reporting.
"""

import subprocess
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path


class C2TestRunner:
    """Test runner for C2 Command Center test suite"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {}
        self.start_time = None
        
    def run_test_suite(self, test_type="all", verbose=False, stop_on_first_failure=False):
        """Run specified test suite"""
        
        print("🎯 C2 Command Center Test Suite")
        print("=" * 50)
        print(f"Test Directory: {self.test_dir}")
        print(f"Test Type: {test_type}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        self.start_time = time.time()
        
        # Define test suites
        test_suites = {
            "unit": {
                "name": "Unit Tests",
                "path": "unit/test_c2_api_endpoints.py",
                "description": "API endpoint unit tests"
            },
            "integration": {
                "name": "Integration Tests", 
                "path": "integration/test_node_red_flows.py",
                "description": "Node-RED flow integration tests"
            },
            "system": {
                "name": "System Tests",
                "path": "system/test_c2_command_center.py", 
                "description": "End-to-end system tests"
            },
            "performance": {
                "name": "Performance Tests",
                "path": "performance/test_c2_performance.py",
                "description": "Performance and load tests"
            }
        }
        
        # Determine which tests to run
        if test_type == "all":
            suites_to_run = test_suites
        elif test_type in test_suites:
            suites_to_run = {test_type: test_suites[test_type]}
        else:
            print(f"❌ Unknown test type: {test_type}")
            print(f"Available types: {', '.join(test_suites.keys())}, all")
            return False
        
        # Run each test suite
        overall_success = True
        for suite_name, suite_info in suites_to_run.items():
            success = self._run_single_suite(
                suite_name, 
                suite_info, 
                verbose=verbose,
                stop_on_failure=stop_on_first_failure
            )
            
            if not success:
                overall_success = False
                if stop_on_first_failure:
                    print(f"⏹️ Stopping on first failure: {suite_name}")
                    break
        
        # Print summary
        self._print_summary()
        
        return overall_success
    
    def _run_single_suite(self, suite_name, suite_info, verbose=False, stop_on_failure=False):
        """Run a single test suite"""
        
        print(f"🧪 {suite_info['name']}")
        print(f"   {suite_info['description']}")
        print(f"   File: {suite_info['path']}")
        
        test_file = self.test_dir / suite_info['path']
        
        if not test_file.exists():
            print(f"   ❌ Test file not found: {test_file}")
            self.results[suite_name] = {
                "status": "error",
                "message": "Test file not found",
                "duration": 0
            }
            return False
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_file),
            "--tb=short"
        ]
        
        # Add conditional arguments
        if stop_on_failure:
            cmd.append("-x")
        if verbose:
            cmd.append("-v")
        
        # Add output capture
        cmd.extend(["--capture=no", "--no-header"])
        
        # Run tests
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.test_dir,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            
            # Parse results
            if result.returncode == 0:
                print(f"   ✅ PASSED ({duration:.1f}s)")
                status = "passed"
            else:
                print(f"   ❌ FAILED ({duration:.1f}s)")
                status = "failed"
                if verbose:
                    print(f"   Error output: {result.stderr}")
            
            self.results[suite_name] = {
                "status": status,
                "return_code": result.returncode,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"   ⏰ TIMEOUT ({duration:.1f}s)")
            self.results[suite_name] = {
                "status": "timeout",
                "duration": duration,
                "message": "Test suite timed out"
            }
            return False
        
        except Exception as e:
            duration = time.time() - start_time
            print(f"   💥 ERROR ({duration:.1f}s): {e}")
            self.results[suite_name] = {
                "status": "error",
                "duration": duration,
                "message": str(e)
            }
            return False
    
    def _print_summary(self):
        """Print test execution summary"""
        
        if not self.start_time:
            return
        
        total_duration = time.time() - self.start_time
        
        print("\n" + "=" * 50)
        print("📊 Test Execution Summary")
        print("=" * 50)
        
        # Count results
        total_suites = len(self.results)
        passed_suites = sum(1 for r in self.results.values() if r["status"] == "passed")
        failed_suites = sum(1 for r in self.results.values() if r["status"] == "failed")
        error_suites = sum(1 for r in self.results.values() if r["status"] == "error")
        timeout_suites = sum(1 for r in self.results.values() if r["status"] == "timeout")
        
        print(f"Total Suites:    {total_suites}")
        print(f"Passed:          {passed_suites} ✅")
        print(f"Failed:          {failed_suites} ❌")
        print(f"Errors:          {error_suites} 💥")
        print(f"Timeouts:        {timeout_suites} ⏰")
        print(f"Total Duration:  {total_duration:.1f}s")
        print()
        
        # Detailed results
        for suite_name, result in self.results.items():
            status_icon = {
                "passed": "✅",
                "failed": "❌", 
                "error": "💥",
                "timeout": "⏰"
            }.get(result["status"], "❓")
            
            print(f"{status_icon} {suite_name:12} ({result['duration']:5.1f}s) - {result['status']}")
        
        # Overall result
        print()
        if passed_suites == total_suites:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {failed_suites + error_suites + timeout_suites} of {total_suites} suites had issues")
        
        # Save results to file
        self._save_results()
    
    def _save_results(self):
        """Save test results to JSON file"""
        
        results_file = self.test_dir / "c2_test_results.json"
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "duration": time.time() - self.start_time if self.start_time else 0,
            "suites": self.results,
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results.values() if r["status"] == "passed"),
                "failed": sum(1 for r in self.results.values() if r["status"] == "failed"),
                "errors": sum(1 for r in self.results.values() if r["status"] == "error"),
                "timeouts": sum(1 for r in self.results.values() if r["status"] == "timeout")
            }
        }
        
        try:
            with open(results_file, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"📄 Results saved to: {results_file}")
        except Exception as e:
            print(f"⚠️  Could not save results: {e}")
    
    def check_prerequisites(self):
        """Check test prerequisites"""
        
        print("🔍 Checking Prerequisites")
        print("-" * 30)
        
        # Check Python packages
        required_packages = [
            "pytest", "requests", "psutil", "psycopg2"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package} (missing)")
                missing_packages.append(package)
        
        # Check services
        print("\n🌐 Checking Services")
        print("-" * 20)
        
        services = {
            "Node-RED": "http://localhost:1881/",
            "Web App": "http://localhost:3000/health",
        }
        
        import requests
        available_services = []
        
        for service_name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name} ({url})")
                    available_services.append(service_name)
                else:
                    print(f"⚠️  {service_name} ({url}) - Status {response.status_code}")
            except Exception:
                print(f"❌ {service_name} ({url}) - Not accessible")
        
        print(f"\n📈 {len(available_services)}/{len(services)} services available")
        print(f"📦 {len(required_packages) - len(missing_packages)}/{len(required_packages)} packages installed")
        
        if missing_packages:
            print(f"\n⚠️  Install missing packages: pip install {' '.join(missing_packages)}")
        
        return len(missing_packages) == 0


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="C2 Command Center Test Runner")
    parser.add_argument(
        "test_type", 
        nargs='?', 
        default="all",
        choices=["all", "unit", "integration", "system", "performance"],
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "-x", "--stop-on-first-failure",
        action="store_true", 
        help="Stop on first test failure"
    )
    parser.add_argument(
        "--check-prereqs",
        action="store_true",
        help="Check prerequisites only"
    )
    
    args = parser.parse_args()
    
    runner = C2TestRunner()
    
    if args.check_prereqs:
        runner.check_prerequisites()
        return
    
    # Check prerequisites first
    if not runner.check_prerequisites():
        print("\n❌ Prerequisites not met. Install missing packages and ensure services are running.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # Run tests
    success = runner.run_test_suite(
        test_type=args.test_type,
        verbose=args.verbose,
        stop_on_first_failure=args.stop_on_first_failure
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
