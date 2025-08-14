#!/usr/bin/env python3
"""
🧪 Test Complete Daily Pipeline - All 17 Stages
Test the expanded daily pipeline orchestrator with all analytics stages
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from pathlib import Path

from daily_pipeline_orchestrator import DailyPipelineOrchestrator

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))


async def test_complete_pipeline():
    """Test the complete daily pipeline with all 17 stages."""
    print("🧪 TESTING COMPLETE DAILY PIPELINE")
    print("=" * 50)

    orchestrator = DailyPipelineOrchestrator()

    try:
        print("🚀 Starting complete pipeline test...")
        print("📋 This will test all 17 stages:")
        print("   📥 Data Download")
        print("   🔗 Relationship Processing")
        print("   🧠 Contextual Analysis")
        print("   📊 Form Scoring")
        print("   ⚡ Power Ratings")
        print("   🏃 Speed & Pace Analysis")
        print("   🎲 Monte Carlo Simulation")
        print("   🤖 ML Model Training")
        print("   📈 Race Trends Analysis")
        print("   🎯 Composite Scoring")
        print("   💰 Betting Strategies")
        print("   📚 Report Generation")
        print("")

        # Run the complete pipeline
        await orchestrator.run_complete_pipeline_now()

        print("")
        print("✅ COMPLETE PIPELINE TEST FINISHED")
        print("📊 Check the logs for detailed results")

        # Show final status
        status = orchestrator.pipeline_status
        print("\n📋 FINAL STATUS:")
        print(f"   Last Run: {status.get('last_run')}")
        print(f"   Success Count: {status.get('success_count', 0)}")
        print(f"   Failure Count: {status.get('failure_count', 0)}")

        if status.get("stages_completed"):
            print(f"   Stages Completed: {len(status['stages_completed'])}")
            for stage in status["stages_completed"]:
                print(f"      ✅ {stage}")

        if status.get("analytics_results"):
            print(f"   Analytics Results: {len(status['analytics_results'])} stages")
            for stage, results in status["analytics_results"].items():
                success = "✅" if results.get("success") else "❌"
                print(f"      {success} {stage}")

    except Exception as e:
        print(f"❌ PIPELINE TEST FAILED: {e}")
        import traceback

        traceback.print_exc()


async def test_individual_stages():
    """Test individual pipeline stages."""
    print("🧪 TESTING INDIVIDUAL STAGES")
    print("=" * 50)

    orchestrator = DailyPipelineOrchestrator()

    # Test each major analytics stage
    test_stages = [
        ("Form Scoring Analysis", orchestrator.form_scoring_analysis),
        ("Power Ratings Calculation", orchestrator.power_ratings_calculation),
        ("Speed & Pace Analysis", orchestrator.speed_pace_analysis),
        ("Monte Carlo Simulation", orchestrator.monte_carlo_simulation),
        ("ML Model Training", orchestrator.ml_model_training),
        ("Race Trends Analysis", orchestrator.race_trends_analysis),
        ("Composite Scoring", orchestrator.composite_scoring_integration),
        ("Betting Strategies", orchestrator.betting_strategies_analysis),
    ]

    results = {}

    for stage_name, stage_func in test_stages:
        try:
            print(f"\n🧪 Testing: {stage_name}")
            result = await stage_func()

            success = result.get("success", False)
            status_icon = "✅" if success else "❌"

            print(f"{status_icon} {stage_name}: {'SUCCESS' if success else 'FAILED'}")

            # Show key metrics
            for key, value in result.items():
                if key not in ["success", "errors"] and isinstance(value, (int, float)):
                    print(f"   📊 {key}: {value}")

            if result.get("errors"):
                print(f"   ❌ Errors: {len(result['errors'])}")
                for error in result["errors"][:2]:  # Show first 2 errors
                    print(f"      - {error}")

            results[stage_name] = result

        except Exception as e:
            print(f"❌ {stage_name} EXCEPTION: {e}")
            results[stage_name] = {"success": False, "error": str(e)}

    # Summary
    print(f"\n📊 INDIVIDUAL STAGE TEST SUMMARY")
    print("=" * 50)

    successful = sum(1 for r in results.values() if r.get("success"))
    total = len(results)
    success_rate = (successful / total) * 100

    print(f"Success Rate: {success_rate:.1f}% ({successful}/{total})")
    print(
        f"Pipeline Health: {'EXCELLENT' if success_rate >= 90 else 'GOOD' if success_rate >= 70 else 'NEEDS ATTENTION'}"
    )


def main():
    """Main test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Test Complete Daily Pipeline")
    parser.add_argument(
        "--complete", action="store_true", help="Test complete pipeline"
    )
    parser.add_argument(
        "--individual", action="store_true", help="Test individual stages"
    )
    parser.add_argument("--all", action="store_true", help="Test everything")

    args = parser.parse_args()

    if args.complete or args.all:
        print("🚀 Running complete pipeline test...")
        asyncio.run(test_complete_pipeline())

    if args.individual or args.all:
        print("\n🧪 Running individual stage tests...")
        asyncio.run(test_individual_stages())

    if not any([args.complete, args.individual, args.all]):
        print("🧪 Daily Pipeline Test Suite")
        print("=" * 30)
        print("Options:")
        print("  --complete    Test complete 17-stage pipeline")
        print("  --individual  Test individual stages")
        print("  --all         Test everything")
        print("")
        print("Example: python test_complete_pipeline.py --all")


if __name__ == "__main__":
    main()
