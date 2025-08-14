#!/usr/bin/env python3
"""
🎯 Comprehensive System Validation Script
Validates the complete 17-stage pipeline system
"""

import json
import subprocess
import sys
from pathlib import Path


def main():
    print("🎯 COMPREHENSIVE SYSTEM VALIDATION")
    print("=" * 50)

    all_tests_passed = True

    # Test 1: Configuration validation
    print("\n📋 Testing 17-Stage Configuration...")
    try:
        config_file = Path("config/complete_17_stage_config.json")
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
            stages = config.get("stages", [])
            print(f"✅ Configuration loaded: {len(stages)} stages found")

            # Validate phases
            phases = {}
            for stage in stages:
                phase = stage.get("phase", "unknown")
                phases[phase] = phases.get(phase, 0) + 1
            print(f"📊 Phase distribution: {phases}")

            if len(stages) == 17:
                print("✅ All 17 stages present")
            else:
                print(f"❌ Expected 17 stages, found {len(stages)}")
                all_tests_passed = False
        else:
            print("❌ Configuration file not found")
            all_tests_passed = False
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        all_tests_passed = False

    # Test 2: Docker services
    print("\n🐳 Testing Docker Services...")
    try:
        # Check docker-compose services
        result = subprocess.run(
            ["docker-compose", "ps"], capture_output=True, text=True
        )

        # Also check all running docker containers for optimized pipeline
        docker_ps_result = subprocess.run(
            ["docker", "ps"], capture_output=True, text=True
        )

        services_count = 0
        postgres_running = False
        redis_running = False
        pipeline_running = False

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            services = [line for line in lines if "horse_racing" in line]
            services_count += len(services)

            # Check specific core services
            postgres_running = any(
                "postgres" in line and "Up" in line for line in services
            )
            redis_running = any("redis" in line and "Up" in line for line in services)

        # Check for optimized pipeline manager in docker ps
        if docker_ps_result.returncode == 0:
            docker_lines = docker_ps_result.stdout.strip().split("\n")
            pipeline_running = any(
                "horse_racing_pipeline_manager_optimized" in line and "Up" in line
                for line in docker_lines
            )
            if pipeline_running:
                services_count += 1

        print(f"✅ Docker services running: {services_count} services")
        print(f'  PostgreSQL: {"✅" if postgres_running else "❌"}')
        print(f'  Redis: {"✅" if redis_running else "❌"}')
        print(f'  Pipeline Manager: {"✅" if pipeline_running else "❌"}')

        if not (postgres_running and redis_running):
            all_tests_passed = False

    except Exception as e:
        print(f"❌ Docker test failed: {e}")
        all_tests_passed = False

    # Test 3: File structure
    print("\n📁 Testing File Structure...")
    try:
        critical_files = [
            "docker-compose.yml",
            "docker-compose.optimized.yml",
            "Dockerfile.data-optimized",
            "Dockerfile.pipeline-optimized",
            "Dockerfile.web-optimized",
            "config/complete_17_stage_config.json",
            "config/complete_csv_column_mapping.json",
            "17_STAGE_PIPELINE_PLANNING.md",
        ]

        missing_files = []
        for file_path in critical_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if not missing_files:
            print(f"✅ All {len(critical_files)} critical files present")
        else:
            print(f"❌ Missing files: {missing_files}")
            all_tests_passed = False

    except Exception as e:
        print(f"❌ File structure test failed: {e}")
        all_tests_passed = False

    # Test 4: Pipeline timing analysis
    print("\n⏱️ Testing Pipeline Timing...")
    try:
        if config_file.exists():
            total_duration = 0
            critical_stages = 0
            optional_stages = 0

            for stage in stages:
                duration = stage.get("duration_minutes", 0)
                total_duration += duration
                if stage.get("critical", False):
                    critical_stages += 1
                else:
                    optional_stages += 1

            print(
                f"✅ Total pipeline duration: {total_duration} minutes ({total_duration/60:.1f} hours)"
            )
            print(
                f"✅ Critical stages: {critical_stages}, Optional stages: {optional_stages}"
            )

            if total_duration > 0 and total_duration < 1440:  # Between 0 and 24 hours
                print("✅ Pipeline duration is reasonable")
            else:
                print("❌ Pipeline duration is unreasonable")
                all_tests_passed = False
        else:
            print("❌ Cannot test timing - config file missing")
            all_tests_passed = False
    except Exception as e:
        print(f"❌ Timing test failed: {e}")
        all_tests_passed = False

    # Final summary
    print("\n🎉 SYSTEM VALIDATION COMPLETE")
    print("=" * 50)

    if all_tests_passed:
        print("🎊 ALL TESTS PASSED - SYSTEM IS READY!")
        return 0
    else:
        print("⚠️ Some tests failed - Review and fix issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
