#!/usr/bin/env python3
"""
🎯 Demo: Integrated Test + Cleanup Analysis
==========================================

Demonstration script showing the new integrated test and cleanup
functionality that addresses the user's request to "intergrate when
the unit tests run the function & file script runs at the same time
and then write its report".

This script shows:
1. How the enhanced test runner works
2. How it integrates file/function analysis with testing
3. How it generates combined reports
4. How it helps organize the "mess" of files

Usage Examples:
- python demo_integrated_cleanup.py --demo-basic
- python demo_integrated_cleanup.py --demo-cleanup-only
- python demo_integrated_cleanup.py --demo-full
"""

import sys
import subprocess
from pathlib import Path
import argparse

PROJECT_ROOT = Path(__file__).parent


def demo_basic_integration():
    """Demo basic integrated test + cleanup"""
    print("🎯 DEMO: Basic Integration - Tests + Cleanup Analysis")
    print("=" * 60)
    print("This runs both unit tests AND file/function analysis together,")
    print("then generates a combined report as requested.")
    print()

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "tests" / "run_tests.py"),
        "--enhanced",
        "--category",
        "unit",
        "--verbose",
    ]

    print(f"Running: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, timeout=300)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Demo timed out")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


def demo_cleanup_only():
    """Demo cleanup analysis only"""
    print("🧹 DEMO: Cleanup Analysis Only")
    print("=" * 40)
    print("This runs only the file/function analysis to help organize")
    print("the 'mess' of files and identify what can be cleaned up.")
    print()

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "tests" / "run_tests.py"),
        "--cleanup-only",
        "--verbose",
    ]

    print(f"Running: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, timeout=300)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Demo timed out")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


def demo_full_integration():
    """Demo full integration with cleanup execution"""
    print("🚀 DEMO: Full Integration - Tests + Cleanup + Execution")
    print("=" * 55)
    print("This runs the complete integrated system:")
    print("1. Unit and integration tests")
    print("2. File and function analysis")
    print("3. Cleanup recommendations")
    print("4. Safe cleanup execution (dry run)")
    print("5. Combined comprehensive report")
    print()

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "tools" / "testing" / "enhanced_test_runner.py"),
        "--dry-run-cleanup",
    ]

    print(f"Running: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, timeout=600)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Demo timed out")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


def show_usage_examples():
    """Show usage examples for the integrated system"""
    print("📋 USAGE EXAMPLES: Integrated Test + Cleanup System")
    print("=" * 55)
    print()

    print("1. Run tests with integrated cleanup analysis:")
    print("   python tests/run_tests.py --enhanced")
    print()

    print("2. Run only cleanup analysis (no tests):")
    print("   python tests/run_tests.py --cleanup-only")
    print()

    print("3. Run tests + cleanup analysis + safe cleanup execution:")
    print("   python tests/run_tests.py --enhanced --execute-cleanup")
    print()

    print("4. Run enhanced test suite directly:")
    print("   python tools/testing/enhanced_test_runner.py")
    print()

    print("5. Preview what cleanup would do (dry run):")
    print("   python tools/testing/enhanced_test_runner.py --dry-run-cleanup")
    print()

    print("6. Run specific test category with cleanup:")
    print("   python tests/run_tests.py --enhanced --category integration")
    print()

    print("KEY BENEFITS:")
    print("✅ Automatic file/function analysis during test runs")
    print("✅ Combined test + cleanup reports")
    print("✅ Identifies unused/removable files")
    print("✅ Helps organize the 'mess' of project files")
    print("✅ Safe cleanup operations with dry-run preview")
    print("✅ Integrates with existing test framework")


def main():
    parser = argparse.ArgumentParser(
        description="Demo the integrated test + cleanup system"
    )

    parser.add_argument(
        "--demo-basic",
        action="store_true",
        help="Demo basic integration (tests + cleanup analysis)",
    )

    parser.add_argument(
        "--demo-cleanup-only", action="store_true", help="Demo cleanup analysis only"
    )

    parser.add_argument(
        "--demo-full",
        action="store_true",
        help="Demo full integration with cleanup execution",
    )

    parser.add_argument(
        "--show-examples", action="store_true", help="Show usage examples"
    )

    args = parser.parse_args()

    if args.show_examples:
        show_usage_examples()
    elif args.demo_basic:
        success = demo_basic_integration()
        sys.exit(0 if success else 1)
    elif args.demo_cleanup_only:
        success = demo_cleanup_only()
        sys.exit(0 if success else 1)
    elif args.demo_full:
        success = demo_full_integration()
        sys.exit(0 if success else 1)
    else:
        print("🎯 Integrated Test + Cleanup Analysis Demo")
        print("=" * 45)
        print()
        print("This demo shows the new integrated system that addresses your request:")
        print('"intergrate when the unit tests run the function & file script')
        print('runs at the same time and then write its report"')
        print()
        print("Available demos:")
        print("  --demo-basic       : Tests + cleanup analysis")
        print("  --demo-cleanup-only: Cleanup analysis only")
        print("  --demo-full        : Full integration with cleanup execution")
        print("  --show-examples    : Show usage examples")
        print()
        print("The system helps organize the 'mess' of files by:")
        print("• Analyzing all project files and functions")
        print("• Identifying unused/removable content")
        print("• Generating cleanup recommendations")
        print("• Creating combined test + cleanup reports")
        print("• Executing safe cleanup operations")


if __name__ == "__main__":
    main()
