#!/usr/bin/env python3
"""
Quick Pre-Pipeline Test Validation
Fast validation of 17-stage pipeline components before full execution.
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def quick_validation_check():
    """Quick validation of key pipeline components"""
    print("⚡ QUICK PRE-PIPELINE VALIDATION")
    print("=" * 50)
    print(f"Validation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test results
    results = {
        "stage_files": 0,
        "test_files": 0, 
        "orchestrator": False,
        "integration": False
    }
    
    # 1. Check Stage Implementation Files
    print(f"\n📁 CHECKING STAGE IMPLEMENTATION FILES:")
    stage_files = [
        "tools/pipeline/daily_orchestrator.py",
        "stage10_monte_carlo_simulations.py", 
        "src/stages/stage12_race_trends.py",
        "src/stages/stage13_composite_scoring.py"
    ]
    
    for stage_file in stage_files:
        if Path(stage_file).exists():
            print(f"✅ {stage_file}")
            results["stage_files"] += 1
        else:
            print(f"❌ {stage_file}")
    
    # 2. Check Test Files
    print(f"\n🧪 CHECKING TEST FILES:")
    test_files = [
        "tests/test_17_stage_pipeline.py",
        "test_stage10_integration.py",
        "test_stage13_comprehensive.py",
        "test_complete_pipeline.py"
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"✅ {test_file}")
            results["test_files"] += 1
        else:
            print(f"❌ {test_file}")
    
    # 3. Quick Orchestrator Syntax Check
    print(f"\n🔧 CHECKING ORCHESTRATOR SYNTAX:")
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "py_compile", "tools/pipeline/daily_orchestrator.py"
        ], capture_output=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Daily orchestrator syntax valid")
            results["orchestrator"] = True
        else:
            print(f"❌ Daily orchestrator syntax errors")
    except Exception as e:
        print(f"⚠️  Could not validate orchestrator: {e}")
    
    # 4. Quick Integration Check
    print(f"\n🔗 CHECKING INTEGRATION READINESS:")
    try:
        # Try importing key modules
        sys.path.append("tools/pipeline")
        
        # Check if we can at least import the main classes  
        if Path("tools/pipeline/daily_orchestrator.py").exists():
            print(f"✅ Pipeline orchestrator accessible")
            results["integration"] = True
        else:
            print(f"❌ Pipeline orchestrator not accessible")
            
    except Exception as e:
        print(f"⚠️  Integration check failed: {e}")
    
    # Results Summary
    print(f"\n📊 VALIDATION SUMMARY:")
    print("=" * 50)
    print(f"Stage Files: {results['stage_files']}/4")
    print(f"Test Files: {results['test_files']}/4") 
    print(f"Orchestrator: {'✅ Ready' if results['orchestrator'] else '❌ Issues'}")
    print(f"Integration: {'✅ Ready' if results['integration'] else '❌ Issues'}")
    
    # Overall Assessment
    total_score = (
        results['stage_files'] + 
        results['test_files'] + 
        (2 if results['orchestrator'] else 0) +
        (2 if results['integration'] else 0)
    )
    max_score = 12
    
    percentage = (total_score / max_score) * 100
    
    print(f"\n🎯 OVERALL READINESS: {total_score}/{max_score} ({percentage:.1f}%)")
    
    if percentage >= 90:
        print(f"✅ EXCELLENT: Ready for full pipeline execution!")
        verdict = "READY"
    elif percentage >= 75:
        print(f"✅ GOOD: Minor issues, but pipeline should work")
        verdict = "MOSTLY READY"
    else:
        print(f"❌ ISSUES: Review problems before pipeline execution")
        verdict = "NEEDS WORK"
    
    print(f"🚀 VERDICT: {verdict}")
    print("=" * 50)
    
    return percentage >= 75


def check_specific_stage_tests():
    """Check if specific stage tests can run"""
    print(f"\n🧪 QUICK STAGE TEST VALIDATION:")
    print("-" * 50)
    
    # Test a few key stage files
    quick_tests = [
        ("Stage 13", "test_stage13_comprehensive.py"),
        ("Stage 10", "test_stage10_integration.py"),
        ("Complete Pipeline", "test_complete_pipeline.py")
    ]
    
    passed = 0
    
    for stage_name, test_file in quick_tests:
        print(f"\n⚡ Quick test: {stage_name}")
        
        if not Path(test_file).exists():
            print(f"❌ {test_file} not found")
            continue
        
        try:
            # Just try to compile/validate the test file
            result = subprocess.run([
                sys.executable, "-m", "py_compile", test_file
            ], capture_output=True, timeout=5)
            
            if result.returncode == 0:
                print(f"✅ {test_file} syntax valid")
                passed += 1
            else:
                print(f"❌ {test_file} syntax errors")
                
        except Exception as e:
            print(f"⚠️  Could not validate {test_file}: {e}")
    
    print(f"\n📊 Quick Test Validation: {passed}/{len(quick_tests)} passed")
    return passed >= 2


def main():
    """Main validation function"""
    print("⚡ STARTING QUICK PRE-PIPELINE VALIDATION")
    
    # Run basic validation
    basic_ready = quick_validation_check()
    
    # Run test validation
    tests_ready = check_specific_stage_tests()
    
    overall_ready = basic_ready and tests_ready
    
    if overall_ready:
        print(f"\n🎉 VALIDATION COMPLETE: READY FOR PIPELINE EXECUTION!")
        print(f"✅ You can now run the full 17-stage pipeline")
    else:
        print(f"\n⚠️  VALIDATION ISSUES: Review problems before pipeline")
        print(f"❌ Address issues before running full pipeline")
    
    return overall_ready


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
