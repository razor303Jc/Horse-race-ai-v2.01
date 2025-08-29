#!/usr/bin/env python3
"""
🧪 Rebuilded Test Framework Runner
=================================

Main test runner for the rebuilded Horse Racing AI v2.04 test framework.
Provides comprehensive test execution with categorization, reporting, and CI/CD integration.
"""

import argparse
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Optional
import json

# Test framework root
TEST_ROOT = Path(__file__).parent
PROJECT_ROOT = TEST_ROOT.parent

class TestFrameworkRunner:
    """Main test framework runner"""
    
    def __init__(self):
        self.test_root = TEST_ROOT
        self.reports_dir = TEST_ROOT / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def run_unit_tests(self, components: Optional[List[str]] = None, verbose: bool = False) -> bool:
        """Run unit tests"""
        print("🧪 Running Unit Tests")
        print("=" * 40)
        
        cmd = ["python", "-m", "pytest", str(self.test_root / "unit")]
        
        if components:
            # Filter by specific components
            for component in components:
                cmd.extend(["-k", component])
        
        if verbose:
            cmd.append("-v")
        
        cmd.extend([
            "--tb=short",
            "--durations=10",
            f"--html={self.reports_dir}/unit_tests_report.html",
            "--self-contained-html"
        ])
        
        result = subprocess.run(cmd, cwd=PROJECT_ROOT)
        return result.returncode == 0
    
    def run_integration_tests(self, verbose: bool = False) -> bool:
        """Run integration tests"""
        print("🔗 Running Integration Tests")
        print("=" * 40)
        
        cmd = [
            "python", "-m", "pytest", 
            str(self.test_root / "integration"),
            "-m", "integration"
        ]
        
        if verbose:
            cmd.append("-v")
        
        cmd.extend([
            "--tb=short",
            f"--html={self.reports_dir}/integration_tests_report.html",
            "--self-contained-html"
        ])
        
        result = subprocess.run(cmd, cwd=PROJECT_ROOT)
        return result.returncode == 0
    
    def run_system_tests(self, verbose: bool = False) -> bool:
        """Run system tests"""
        print("🏗️ Running System Tests")
        print("=" * 40)
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_root / "system"),
            "-m", "system"
        ]
        
        if verbose:
            cmd.append("-v")
        
        cmd.extend([
            "--tb=short",
            f"--html={self.reports_dir}/system_tests_report.html",
            "--self-contained-html"
        ])
        
        result = subprocess.run(cmd, cwd=PROJECT_ROOT)
        return result.returncode == 0
    
    def run_performance_tests(self, verbose: bool = False) -> bool:
        """Run performance tests"""
        print("⚡ Running Performance Tests")
        print("=" * 40)
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_root / "performance"), 
            "-m", "performance",
            "--benchmark-only",
            "--benchmark-sort=mean"
        ]
        
        if verbose:
            cmd.append("-v")
        
        cmd.extend([
            f"--benchmark-json={self.reports_dir}/performance_benchmark.json",
            f"--html={self.reports_dir}/performance_tests_report.html",
            "--self-contained-html"
        ])
        
        result = subprocess.run(cmd, cwd=PROJECT_ROOT)
        return result.returncode == 0
    
    def run_component_tests(self, component: str, verbose: bool = False) -> bool:
        """Run tests for specific component"""
        print(f"🎯 Running {component.title()} Component Tests")
        print("=" * 40)
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_root),
            "-m", component
        ]
        
        if verbose:
            cmd.append("-v")
        
        cmd.extend([
            "--tb=short",
            f"--html={self.reports_dir}/{component}_tests_report.html",
            "--self-contained-html"
        ])
        
        result = subprocess.run(cmd, cwd=PROJECT_ROOT)
        return result.returncode == 0
    
    def run_smoke_tests(self, verbose: bool = False) -> bool:
        """Run smoke tests (critical functionality)"""
        print("💨 Running Smoke Tests")
        print("=" * 40)
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_root),
            "-m", "smoke or critical",
            "--maxfail=1"  # Stop on first failure for smoke tests
        ]
        
        if verbose:
            cmd.append("-v")
        
        cmd.extend([
            "--tb=short",
            f"--html={self.reports_dir}/smoke_tests_report.html",
            "--self-contained-html"
        ])
        
        result = subprocess.run(cmd, cwd=PROJECT_ROOT)
        return result.returncode == 0
    
    def run_coverage_analysis(self, verbose: bool = False) -> bool:
        """Run full test suite with coverage analysis"""
        print("📊 Running Coverage Analysis")
        print("=" * 40)
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_root),
            "--cov=src",
            "--cov=tools", 
            "--cov=api",
            "--cov=docker",
            "--cov-report=html:" + str(self.reports_dir / "coverage"),
            "--cov-report=json:" + str(self.reports_dir / "coverage.json"),
            "--cov-report=term-missing",
            "--cov-branch",
            "--cov-fail-under=80"
        ]
        
        if verbose:
            cmd.append("-v")
        
        result = subprocess.run(cmd, cwd=PROJECT_ROOT)
        return result.returncode == 0
    
    def generate_test_report(self) -> Dict:
        """Generate comprehensive test report"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "framework_version": "1.0",
            "test_categories": {
                "unit": self.count_tests("unit"),
                "integration": self.count_tests("integration"),
                "system": self.count_tests("system"),
                "performance": self.count_tests("performance")
            },
            "component_coverage": {
                "bulk_uploader": self.count_component_tests("bulk_uploader"),
                "pipeline": self.count_component_tests("pipeline"),
                "ml_training": self.count_component_tests("ml"),
                "api": self.count_component_tests("api"),
                "database": self.count_component_tests("database")
            },
            "reports_generated": list(self.reports_dir.glob("*.html")) + list(self.reports_dir.glob("*.json"))
        }
        
        # Save report
        report_file = self.reports_dir / "test_framework_summary.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report
    
    def count_tests(self, category: str) -> int:
        """Count tests in a category"""
        try:
            result = subprocess.run([
                "python", "-m", "pytest",
                str(self.test_root / category),
                "--collect-only", "--quiet"
            ], capture_output=True, text=True, cwd=PROJECT_ROOT)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if "test session starts" in line or "tests collected" in line:
                        continue
                    if "collected" in line:
                        return int(line.split()[0])
            return 0
        except:
            return 0
    
    def count_component_tests(self, component: str) -> int:
        """Count tests for a specific component"""
        try:
            result = subprocess.run([
                "python", "-m", "pytest",
                str(self.test_root),
                "-m", component,
                "--collect-only", "--quiet"
            ], capture_output=True, text=True, cwd=PROJECT_ROOT)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if "collected" in line and "test" in line:
                        return int(line.split()[0])
            return 0
        except:
            return 0
    
    def run_all_tests(self, verbose: bool = False, include_performance: bool = False) -> bool:
        """Run all test categories"""
        print("🚀 Running Complete Test Suite")
        print("=" * 50)
        
        results = []
        
        # Run smoke tests first
        results.append(("Smoke Tests", self.run_smoke_tests(verbose)))
        
        # Run unit tests
        results.append(("Unit Tests", self.run_unit_tests(verbose=verbose)))
        
        # Run integration tests
        results.append(("Integration Tests", self.run_integration_tests(verbose)))
        
        # Run system tests
        results.append(("System Tests", self.run_system_tests(verbose)))
        
        # Run performance tests if requested
        if include_performance:
            results.append(("Performance Tests", self.run_performance_tests(verbose)))
        
        # Generate coverage report
        results.append(("Coverage Analysis", self.run_coverage_analysis(verbose)))
        
        # Generate summary report
        summary = self.generate_test_report()
        
        # Print results
        print("\n📊 Test Suite Results")
        print("=" * 30)
        for test_type, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_type}: {status}")
        
        print(f"\nTotal Tests Found:")
        for category, count in summary["component_coverage"].items():
            print(f"  {category}: {count} tests")
        
        print(f"\nReports saved to: {self.reports_dir}")
        
        # Return overall success
        return all(result[1] for result in results)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Rebuilded Test Framework Runner for Horse Racing AI v2.04"
    )
    
    parser.add_argument(
        "--category",
        choices=["unit", "integration", "system", "performance", "all"],
        default="unit",
        help="Test category to run"
    )
    
    parser.add_argument(
        "--component", 
        choices=["bulk_uploader", "pipeline", "ml", "api", "database"],
        help="Run tests for specific component"
    )
    
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run smoke tests only"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true", 
        help="Run with coverage analysis"
    )
    
    parser.add_argument(
        "--performance",
        action="store_true",
        help="Include performance tests in all runs"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--components",
        nargs="+",
        help="Filter unit tests by components"
    )
    
    args = parser.parse_args()
    
    runner = TestFrameworkRunner()
    
    # Determine what to run
    success = True
    
    if args.smoke:
        success = runner.run_smoke_tests(args.verbose)
    elif args.component:
        success = runner.run_component_tests(args.component, args.verbose)
    elif args.coverage:
        success = runner.run_coverage_analysis(args.verbose)
    elif args.category == "unit":
        success = runner.run_unit_tests(args.components, args.verbose)
    elif args.category == "integration":
        success = runner.run_integration_tests(args.verbose)
    elif args.category == "system":
        success = runner.run_system_tests(args.verbose)
    elif args.category == "performance":
        success = runner.run_performance_tests(args.verbose)
    elif args.category == "all":
        success = runner.run_all_tests(args.verbose, args.performance)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
