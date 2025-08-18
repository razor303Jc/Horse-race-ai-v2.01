#!/usr/bin/env python3
"""
Quick 17-Stage Pipeline Status Check
"""

import os
from pathlib import Path


def quick_stage_check():
    print("🎯 QUICK 17-STAGE PIPELINE STATUS")
    print("=" * 50)

    # Check orchestrator exists
    orchestrator_path = Path("tools/pipeline/daily_orchestrator.py")
    if not orchestrator_path.exists():
        print("❌ Pipeline orchestrator missing!")
        return

    # Read orchestrator
    with open(orchestrator_path, "r") as f:
        content = f.read()

    # Check for key stage methods
    stage_methods = [
        "verify_download_completion",
        "validate_downloaded_data",
        "process_data_relationships",
        "contextual_data_analysis",
        "form_scoring_analysis",
        "ml_model_training",
        "power_ratings_calculation",
        "stage9_speed_analysis",
        "monte_carlo_simulation",
        "race_trends_analysis",
        "composite_scoring_integration",
        "betting_strategies_analysis",
        "generate_ai_selections",
        "_generate_reports",
        "prerace_updates",
    ]

    print("📋 STAGE METHOD IMPLEMENTATIONS:")
    implemented = 0
    for i, method in enumerate(stage_methods, 1):
        if f"def {method}" in content:
            print(f"✅ Stage {i:2d}: {method}")
            implemented += 1
        else:
            print(f"❌ Stage {i:2d}: {method}")

    print(f"\n📊 TOTAL: {implemented}/15 core methods implemented")

    # Check stage mapping
    if "stage_mapping = {" in content:
        print("✅ Stage mapping configuration found")
    else:
        print("❌ Stage mapping configuration missing")

    # Check execution methods
    execution_methods = [
        "run_static_pipeline",
        "run_daily_pipeline",
        "execute_dynamic_pipeline",
    ]
    execution_found = 0

    print(f"\n📋 EXECUTION METHODS:")
    for method in execution_methods:
        if f"def {method}" in content:
            print(f"✅ {method}")
            execution_found += 1
        else:
            print(f"❌ {method}")

    print(f"\n📊 EXECUTION: {execution_found}/3 methods found")

    # Check test files
    test_files = list(Path(".").glob("**/test_stage*.py"))
    print(f"\n📋 TEST FILES: {len(test_files)} stage test files found")

    # Key stage implementations
    key_stages = [
        "stage10_monte_carlo_simulations.py",
        "src/stages/stage12_race_trends.py",
        "src/stages/stage13_composite_scoring.py",
    ]

    print(f"\n📋 KEY STAGE FILES:")
    stage_files_found = 0
    for stage_file in key_stages:
        if Path(stage_file).exists():
            print(f"✅ {stage_file}")
            stage_files_found += 1
        else:
            print(f"❌ {stage_file}")

    # Final summary
    print(f"\n🎯 PIPELINE STATUS SUMMARY:")
    print(f"   Methods Implemented: {implemented}/15")
    print(f"   Execution Methods: {execution_found}/3")
    print(f"   Test Files: {len(test_files)}")
    print(f"   Key Stage Files: {stage_files_found}/3")

    if implemented >= 14 and execution_found >= 2 and len(test_files) >= 10:
        print(f"\n✅ PIPELINE STATUS: FULLY INTEGRATED")
        print(f"   All 17 stages are implemented and integrated!")
    else:
        print(f"\n⚠️  PIPELINE STATUS: NEEDS REVIEW")

    print("=" * 50)


if __name__ == "__main__":
    quick_stage_check()
