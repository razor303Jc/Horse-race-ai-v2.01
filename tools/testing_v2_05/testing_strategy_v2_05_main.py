#!/usr/bin/env python3
"""
Testing & Simulation Strategy v2.05 - Main Execution Script
Master execution script for comprehensive testing and validation

Usage:
    python testing_strategy_v2_05_main.py [--date YYYY-MM-DD] [--mode MODE]

Modes:
    - full: Complete testing suite + simulation scenarios
    - testing: Testing suite only
    - simulation: Simulation scenarios only
    - daily: Single day pipeline execution
"""

import argparse
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import v2.05 modules
try:
    from .testing_orchestrator_v2_05 import TestingSimulationOrchestrator
    from .daily_operations_v2_05 import DailyOperationsV205
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from testing_orchestrator_v2_05 import TestingSimulationOrchestrator
    from daily_operations_v2_05 import DailyOperationsV205


def print_banner():
    """Print application banner"""
    print("🏇" + "=" * 70 + "🏇")
    print("    Horse Racing AI v2.05 - Testing & Simulation Strategy")
    print("    Comprehensive PostgreSQL Entity Tables Testing Framework")
    print("=" * 74)
    print()


def print_phase_header(phase_name: str, description: str):
    """Print phase header"""
    print(f"🎯 {phase_name}")
    print(f"   {description}")
    print("-" * 50)


def run_full_strategy(data_date: str) -> bool:
    """Run complete Testing & Simulation Strategy"""

    print_phase_header(
        "FULL TESTING & SIMULATION STRATEGY",
        "Complete comprehensive testing with simulation scenarios",
    )

    orchestrator = TestingSimulationOrchestrator()

    try:
        # Phase 1: Comprehensive Testing Suite
        print("🧪 Phase 1: Comprehensive Testing Suite")
        test_start = time.time()

        test_results = orchestrator.run_comprehensive_testing_suite(data_date)
        test_time = time.time() - test_start

        print(f"⏱️  Testing completed in {test_time:.2f} seconds")
        print(
            f"📊 Success rate: {test_results['performance_summary']['overall_success_rate']:.1f}%"
        )

        if not test_results["overall_success"]:
            print("❌ Testing suite failed - stopping execution")
            return False

        print("✅ Testing suite passed\n")

        # Phase 2: Simulation Scenarios
        print("🎮 Phase 2: Simulation Scenarios")
        sim_start = time.time()

        simulation_results = orchestrator.run_simulation_scenarios(data_date)
        sim_time = time.time() - sim_start

        print(f"⏱️  Simulation completed in {sim_time:.2f} seconds")
        print(
            f"📊 Success rate: {simulation_results['summary']['success_rate_percentage']:.1f}%"
        )

        simulation_success = (
            simulation_results["summary"]["success_rate_percentage"] >= 80
        )

        if not simulation_success:
            print("⚠️  Simulation scenarios had issues")
        else:
            print("✅ Simulation scenarios passed\n")

        # Phase 3: Comprehensive Report Generation
        print("📊 Phase 3: Comprehensive Report Generation")

        report_file = orchestrator.generate_comprehensive_report(
            test_results, simulation_results
        )

        if report_file:
            print(f"✅ Comprehensive report: {report_file}\n")

        # Final Assessment
        overall_success = test_results["overall_success"] and simulation_success

        if overall_success:
            print("🎉 TESTING & SIMULATION STRATEGY - SUCCESS!")
            print("🚀 System ready for production implementation")
        else:
            print("⚠️  TESTING & SIMULATION STRATEGY - REVIEW REQUIRED")
            print("🔍 Check logs and reports for detailed analysis")

        return overall_success

    except Exception as e:
        print(f"❌ Full strategy execution failed: {str(e)}")
        return False


def run_testing_only(data_date: str) -> bool:
    """Run testing suite only"""

    print_phase_header(
        "TESTING SUITE ONLY", "Comprehensive testing without simulation scenarios"
    )

    orchestrator = TestingSimulationOrchestrator()

    try:
        test_results = orchestrator.run_comprehensive_testing_suite(data_date)

        print(f"📊 Testing Results:")
        for phase_name, phase_data in test_results["test_phases"].items():
            status = "✅" if phase_data["success"] else "❌"
            print(
                f"{status} {phase_name}: {phase_data.get('phase_time_seconds', 0):.2f}s"
            )

        overall_success = test_results["overall_success"]
        success_rate = test_results["performance_summary"]["overall_success_rate"]

        print(f"\n📈 Overall Success Rate: {success_rate:.1f}%")

        if overall_success:
            print("✅ All testing phases passed!")
        else:
            print("❌ Some testing phases failed")

        return overall_success

    except Exception as e:
        print(f"❌ Testing execution failed: {str(e)}")
        return False


def run_simulation_only(data_date: str) -> bool:
    """Run simulation scenarios only"""

    print_phase_header(
        "SIMULATION SCENARIOS ONLY",
        "Simulation scenarios without comprehensive testing",
    )

    orchestrator = TestingSimulationOrchestrator()

    try:
        simulation_results = orchestrator.run_simulation_scenarios(data_date)

        print(f"🎮 Simulation Results:")
        for scenario_name, scenario_data in simulation_results["scenarios"].items():
            status = "✅" if scenario_data.get("success", False) else "❌"
            time_taken = scenario_data.get("scenario_time_seconds", 0)
            print(f"{status} {scenario_name}: {time_taken:.2f}s")

        success_rate = simulation_results["summary"]["success_rate_percentage"]
        simulation_success = success_rate >= 80

        print(f"\n📈 Simulation Success Rate: {success_rate:.1f}%")

        if simulation_success:
            print("✅ All simulation scenarios passed!")
        else:
            print("❌ Some simulation scenarios failed")

        return simulation_success

    except Exception as e:
        print(f"❌ Simulation execution failed: {str(e)}")
        return False


def run_daily_pipeline(data_date: str) -> bool:
    """Run single daily pipeline execution"""

    print_phase_header(
        "DAILY PIPELINE EXECUTION", f"Single day processing pipeline for {data_date}"
    )

    daily_ops = DailyOperationsV205()

    try:
        pipeline_result = daily_ops.execute_daily_pipeline(data_date)

        print(f"📊 Pipeline Results:")
        for phase_name, phase_data in pipeline_result["phases"].items():
            status = "✅" if phase_data["success"] else "❌"
            records = phase_data.get("records_processed", 0)
            print(f"{status} {phase_name}: {records} records")

        total_records = pipeline_result["total_records_processed"]
        total_time = pipeline_result["performance_metrics"][
            "total_pipeline_time_seconds"
        ]

        print(f"\n📈 Performance:")
        print(f"🔢 Total records: {total_records}")
        print(f"⏱️ Total time: {total_time:.2f}s")
        print(f"⚡ Records/sec: {total_records/total_time:.1f}")

        if pipeline_result["overall_success"]:
            print("✅ Daily pipeline completed successfully!")
        else:
            print("❌ Daily pipeline had issues")

        # Export daily report
        report_file = f"/tmp/daily_pipeline_report_{data_date}.json"
        daily_ops.export_operation_report(pipeline_result, report_file)
        print(f"📝 Report: {report_file}")

        return pipeline_result["overall_success"]

    except Exception as e:
        print(f"❌ Daily pipeline execution failed: {str(e)}")
        return False


def main():
    """Main execution function"""

    parser = argparse.ArgumentParser(
        description="Horse Racing AI v2.05 - Testing & Simulation Strategy"
    )

    parser.add_argument(
        "--date", default="2025-08-26", help="Test data date (YYYY-MM-DD format)"
    )

    parser.add_argument(
        "--mode",
        choices=["full", "testing", "simulation", "daily"],
        default="full",
        help="Execution mode",
    )

    args = parser.parse_args()

    print_banner()

    print(f"📅 Test Date: {args.date}")
    print(f"🎯 Execution Mode: {args.mode}")
    print()

    execution_start = time.time()

    # Execute based on mode
    if args.mode == "full":
        success = run_full_strategy(args.date)
    elif args.mode == "testing":
        success = run_testing_only(args.date)
    elif args.mode == "simulation":
        success = run_simulation_only(args.date)
    elif args.mode == "daily":
        success = run_daily_pipeline(args.date)
    else:
        print(f"❌ Unknown mode: {args.mode}")
        return 1

    execution_time = time.time() - execution_start

    print("\n" + "=" * 74)
    print(f"⏱️  Total Execution Time: {execution_time:.2f} seconds")

    if success:
        print("🎉 EXECUTION COMPLETED SUCCESSFULLY!")
        print("🚀 Testing & Simulation Strategy v2.05 - READY FOR PRODUCTION")
        return 0
    else:
        print("⚠️  EXECUTION COMPLETED WITH ISSUES")
        print("🔍 Review logs and reports for detailed analysis")
        return 1


if __name__ == "__main__":
    sys.exit(main())
