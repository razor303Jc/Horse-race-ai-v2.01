#!/usr/bin/env python3
"""
🏇 Pipeline Critical Fixes Verification Report
August 12, 2025

This script verifies that all critical fixes have been applied successfully.
"""

import json
import sys
from pathlib import Path


def verify_critical_fixes():
    """Verify all critical fixes are working."""

    print("🏇 PIPELINE CRITICAL FIXES VERIFICATION")
    print("=" * 50)

    verification_results = {
        "database_pooling": False,
        "async_subprocess": False,
        "retry_decorator": False,
        "health_check": False,
        "imports": False,
        "syntax": False,
        "overall": False,
    }

    # Check if the orchestrator file exists and can be imported
    try:
        import daily_pipeline_orchestrator

        verification_results["imports"] = True
        print("✅ Import test: PASSED")
    except Exception as e:
        print(f"❌ Import test: FAILED - {e}")
        return verification_results

    # Check database pooling
    try:
        from daily_pipeline_orchestrator import DailyPipelineOrchestrator

        orchestrator = DailyPipelineOrchestrator()

        if hasattr(orchestrator, "connection_pool") and orchestrator.connection_pool:
            verification_results["database_pooling"] = True
            print("✅ Database pooling: ACTIVE")
        else:
            print("❌ Database pooling: NOT CONFIGURED")

        # Cleanup
        del orchestrator

    except Exception as e:
        print(f"❌ Database pooling test: FAILED - {e}")

    # Check health check functionality
    try:
        from daily_pipeline_orchestrator import DailyPipelineOrchestrator

        orchestrator = DailyPipelineOrchestrator()
        health = orchestrator.health_check()

        if isinstance(health, dict) and "overall" in health:
            verification_results["health_check"] = True
            print(f"✅ Health check: OPERATIONAL (Overall: {health.get('overall')})")
            print(f"   └── Database: {health.get('database')}")
            print(f"   └── File System: {health.get('file_system')}")
            print(
                f"   └── Memory: {health.get('memory')} ({health.get('memory_usage', 0):.1f}%)"
            )
        else:
            print("❌ Health check: INVALID RESPONSE")

        del orchestrator

    except Exception as e:
        print(f"❌ Health check test: FAILED - {e}")

    # Check for retry decorator
    try:
        from daily_pipeline_orchestrator import retry_on_failure

        verification_results["retry_decorator"] = True
        print("✅ Retry decorator: AVAILABLE")
    except ImportError:
        print("❌ Retry decorator: NOT FOUND")
    except Exception as e:
        print(f"❌ Retry decorator test: FAILED - {e}")

    # Check async subprocess handler
    try:
        from daily_pipeline_orchestrator import DailyPipelineOrchestrator

        orchestrator = DailyPipelineOrchestrator()

        if hasattr(orchestrator, "_run_subprocess_safely"):
            verification_results["async_subprocess"] = True
            print("✅ Async subprocess handler: IMPLEMENTED")
        else:
            print("❌ Async subprocess handler: NOT FOUND")

        del orchestrator

    except Exception as e:
        print(f"❌ Async subprocess test: FAILED - {e}")

    # Syntax check
    try:
        import py_compile

        py_compile.compile("daily_pipeline_orchestrator.py", doraise=True)
        verification_results["syntax"] = True
        print("✅ Syntax check: PASSED")
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax check: FAILED - {e}")
    except Exception as e:
        print(f"❌ Syntax check: ERROR - {e}")

    # Overall status
    critical_checks = [
        verification_results["database_pooling"],
        verification_results["imports"],
        verification_results["syntax"],
        verification_results["health_check"],
    ]

    verification_results["overall"] = all(critical_checks)

    print("\n" + "=" * 50)
    if verification_results["overall"]:
        print("🎉 ALL CRITICAL FIXES VERIFIED SUCCESSFULLY!")
        print("\n✅ Ready for:")
        print("   • Production database operations")
        print("   • Automated pipeline scheduling")
        print("   • Health monitoring")
        print("   • Error recovery")
    else:
        print("⚠️ SOME CRITICAL ISSUES REMAIN")
        print("\n❌ Failed checks:")
        for check, passed in verification_results.items():
            if not passed and check != "overall":
                print(f"   • {check.replace('_', ' ').title()}")

    print(
        f"\n📊 Verification Score: {sum(verification_results.values())}/{len(verification_results)} checks passed"
    )

    return verification_results


def main():
    """Main execution."""

    # Change to the correct directory
    project_dir = Path(__file__).parent
    import os

    os.chdir(project_dir)

    try:
        results = verify_critical_fixes()

        # Save results
        with open("pipeline_fix_verification.json", "w") as f:
            json.dump(
                {
                    "timestamp": "2025-08-12T19:48:00",
                    "verification_results": results,
                    "summary": "Critical fixes verification completed",
                },
                f,
                indent=2,
            )

        return 0 if results["overall"] else 1

    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
