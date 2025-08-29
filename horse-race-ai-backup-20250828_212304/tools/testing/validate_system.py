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
            with open(config_file, encoding="utf-8") as f:
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

        # Also check all running containers for services that might be
        # running from separate compose files
        docker_ps_result = subprocess.run(
            ["docker", "ps"], capture_output=True, text=True
        )

        # Expected services with their check patterns
        expected_services = {
            "postgres": "horse_racing_postgres",
            "redis": "horse_racing_redis",
            "pipeline-manager": "horse-race-ai-v201_pipeline-manager_1",
            "horse-racing-ai": "horse-race-ai-v201_horse-racing-ai_1",
            "ntfy": "horse_racing_ntfy",
            "auto-downloader": "horserace-auto-downloader",
            "mkdocs": "horse_racing_docs",
        }

        service_status = {}
        services_count = 0

        # Check docker-compose services first
        if result.returncode == 0:
            output = result.stdout

            for service_name, container_pattern in expected_services.items():
                service_running = container_pattern in output and "Up" in output
                service_status[service_name] = service_running
                if service_running:
                    services_count += 1

        # For services not found in docker-compose, check docker ps
        if docker_ps_result.returncode == 0:
            docker_output = docker_ps_result.stdout

            for service_name, container_pattern in expected_services.items():
                if not service_status.get(service_name, False):
                    # Check if it's running as a standalone container
                    service_running = container_pattern in docker_output
                    if service_running:
                        service_status[service_name] = True
                        services_count += 1

        services_total = len(expected_services)
        print(f"✅ Docker services running: {services_count}/{services_total}")
        for service_name, is_running in service_status.items():
            status_icon = "✅" if is_running else "❌"
            print(f"  {service_name.title()}: {status_icon}")

        # Core services that must be running
        core_services = ["postgres", "redis", "pipeline-manager", "auto-downloader"]
        core_running = all(service_status.get(svc, False) for svc in core_services)

        if not core_running:
            print("❌ Core services must be running")
            all_tests_passed = False

    except (subprocess.CalledProcessError, OSError) as e:
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
            "docs/operations/17_STAGE_PIPELINE_PLANNING.md",
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
        # Re-check config file exists for this test
        config_file = Path("config/complete_17_stage_config.json")
        if config_file.exists():
            with open(config_file, encoding="utf-8") as f:
                config = json.load(f)
            stages = config.get("stages", [])

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

            hours = total_duration / 60
            print(f"✅ Total duration: {total_duration} min ({hours:.1f} hrs)")
            print(f"✅ Critical: {critical_stages}, Optional: {optional_stages}")

            if 0 < total_duration < 1440:  # Between 0 and 24 hours
                print("✅ Pipeline duration is reasonable")
            else:
                print("❌ Pipeline duration is unreasonable")
                all_tests_passed = False
        else:
            print("❌ Cannot test timing - config file missing")
            all_tests_passed = False
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
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
