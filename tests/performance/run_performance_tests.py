#!/usr/bin/env python3
"""
Performance Test Runner - Phase 3 Priority 3
Orchestrates and executes the complete performance testing suite

Author: AI Assistant
Date: August 12, 2025
"""

import argparse
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from performance_config import (
    get_performance_config, 
    setup_performance_environment,
    validate_performance_environment,
    ENVIRONMENT_CONFIG
)


def run_performance_tests(test_type: str = "all", verbose: bool = True):
    """
    Run performance tests based on specified type.
    
    Args:
        test_type: Type of tests to run ('all', 'load', 'concurrent', 'resource', 'benchmark')
        verbose: Whether to show detailed output
    """
    print("🚀 Performance Testing Suite - Phase 3 Priority 3")
    print("=" * 60)
    
    # Setup and validate environment
    if verbose:
        print("\n🔧 Setting up test environment...")
    setup_performance_environment()
    
    if not validate_performance_environment():
        print("❌ Environment validation failed. Aborting tests.")
        return False
    
    # Get configuration
    config = get_performance_config()
    
    if verbose:
        print(f"\n📋 Test Configuration:")
        print(f"   🔄 Iterations: {config['execution']['default_iterations']}")
        print(f"   ⏱️  Timeout: {config['execution']['timeout_seconds']}s")
        print(f"   👥 Workers: {config['execution']['parallel_workers']}")
    
    # Import pytest here to avoid issues if not available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not available. Please install with: pip install pytest")
        return False
    
    # Define test modules and their descriptions
    test_modules = {
        'load': {
            'file': 'test_load_testing.py',
            'name': 'Load Testing',
            'description': 'High-volume data processing performance'
        },
        'concurrent': {
            'file': 'test_concurrent_execution.py',
            'name': 'Concurrent Execution',
            'description': 'Multi-threaded and async performance'
        },
        'resource': {
            'file': 'test_resource_monitoring.py',
            'name': 'Resource Monitoring',
            'description': 'System resource usage validation'
        },
        'benchmark': {
            'file': 'benchmark_performance.py',
            'name': 'Performance Benchmarks',
            'description': 'Comprehensive performance benchmarking'
        }
    }
    
    # Determine which tests to run
    if test_type == "all":
        tests_to_run = list(test_modules.keys())
    elif test_type in test_modules:
        tests_to_run = [test_type]
    else:
        print(f"❌ Unknown test type: {test_type}")
        print(f"Available types: {', '.join(['all'] + list(test_modules.keys()))}")
        return False
    
    # Execute tests
    overall_start_time = time.time()
    test_results = {}
    
    for test_key in tests_to_run:
        test_info = test_modules[test_key]
        test_file = Path(__file__).parent / test_info['file']
        
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            test_results[test_key] = {'status': 'file_not_found'}
            continue
        
        print(f"\n{'='*20} {test_info['name']} {'='*20}")
        print(f"📝 {test_info['description']}")
        print(f"📁 Running: {test_info['file']}")
        
        # Prepare pytest arguments
        pytest_args = [
            str(test_file),
            '-v',  # Verbose output
            '--tb=short',  # Short traceback format
            '--disable-warnings',  # Reduce noise
        ]
        
        if not verbose:
            pytest_args.append('-q')  # Quiet mode
        
        # Run the test
        start_time = time.time()
        result = pytest.main(pytest_args)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Record results
        test_results[test_key] = {
            'status': 'passed' if result == 0 else 'failed',
            'exit_code': result,
            'execution_time': execution_time,
            'test_file': test_info['file']
        }
        
        # Display results
        if result == 0:
            print(f"✅ {test_info['name']} PASSED ({execution_time:.2f}s)")
        else:
            print(f"❌ {test_info['name']} FAILED (exit code: {result}, {execution_time:.2f}s)")
    
    overall_end_time = time.time()
    total_execution_time = overall_end_time - overall_start_time
    
    # Generate summary report
    print(f"\n{'='*60}")
    print("📊 PERFORMANCE TESTING SUMMARY")
    print(f"{'='*60}")
    
    passed_tests = sum(1 for r in test_results.values() if r['status'] == 'passed')
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"🎯 Overall Results:")
    print(f"   ✅ Passed: {passed_tests}/{total_tests}")
    print(f"   📊 Success Rate: {success_rate:.1f}%")
    print(f"   ⏱️  Total Time: {total_execution_time:.2f}s")
    
    print(f"\n📋 Individual Test Results:")
    for test_key, result in test_results.items():
        test_name = test_modules[test_key]['name']
        status_icon = "✅" if result['status'] == 'passed' else "❌"
        status_text = result['status'].upper()
        time_text = f"{result.get('execution_time', 0):.2f}s"
        
        print(f"   {status_icon} {test_name}: {status_text} ({time_text})")
    
    # Save detailed results
    results_file = ENVIRONMENT_CONFIG['paths']['reports_dir'] / 'performance_test_results.json'
    try:
        import json
        detailed_results = {
            'timestamp': time.time(),
            'test_type': test_type,
            'total_execution_time': total_execution_time,
            'success_rate': success_rate,
            'configuration': config,
            'test_results': test_results
        }
        
        with open(results_file, 'w') as f:
            json.dump(detailed_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️  Could not save results file: {e}")
    
    # Final assessment
    if success_rate >= 80:
        print(f"\n🎉 PERFORMANCE TESTING SUCCESSFUL!")
        print(f"   Phase 3 Priority 3 performance validation COMPLETE")
        return True
    else:
        print(f"\n⚠️  PERFORMANCE TESTING INCOMPLETE")
        print(f"   Some tests failed - review results and address issues")
        return False


def main():
    """Main entry point for performance test runner."""
    parser = argparse.ArgumentParser(
        description="Horse Racing AI Performance Testing Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Types:
  all         Run all performance tests (default)
  load        Run load testing only
  concurrent  Run concurrent execution tests only
  resource    Run resource monitoring tests only
  benchmark   Run performance benchmarks only

Examples:
  python run_performance_tests.py
  python run_performance_tests.py --type load
  python run_performance_tests.py --type benchmark --quiet
        """
    )
    
    parser.add_argument(
        '--type', '-t',
        choices=['all', 'load', 'concurrent', 'resource', 'benchmark'],
        default='all',
        help='Type of performance tests to run (default: all)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Run in quiet mode with minimal output'
    )
    
    parser.add_argument(
        '--config-check',
        action='store_true',
        help='Only check configuration and environment, do not run tests'
    )
    
    args = parser.parse_args()
    
    # Configuration check mode
    if args.config_check:
        print("🔍 Performance Testing Configuration Check")
        print("=" * 50)
        
        setup_performance_environment()
        is_valid = validate_performance_environment()
        
        config = get_performance_config()
        print(f"\n📋 Current Configuration:")
        print(f"   🔄 Default iterations: {config['execution']['default_iterations']}")
        print(f"   ⏱️  Timeout: {config['execution']['timeout_seconds']}s")
        print(f"   👥 Workers: {config['execution']['parallel_workers']}")
        print(f"   🎯 Success threshold: {config['thresholds']['success_rate_min']:.1%}")
        
        if is_valid:
            print("\n✅ Configuration and environment are ready for testing")
            return 0
        else:
            print("\n❌ Configuration or environment issues detected")
            return 1
    
    # Run performance tests
    verbose = not args.quiet
    success = run_performance_tests(test_type=args.type, verbose=verbose)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
