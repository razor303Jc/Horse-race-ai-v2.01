#!/usr/bin/env python3
"""
Node-RED Pipeline Automation Deployment Verification
====================================================

This script verifies that our exec node deployment is working correctly
and provides instructions for manual testing in the Node-RED editor.
"""

import requests
import json
import time
from datetime import datetime


def check_node_red_status():
    """Check if Node-RED is accessible"""
    print("🔍 CHECKING NODE-RED STATUS")
    print("=" * 40)

    try:
        response = requests.get("http://localhost:1880/", timeout=5)
        if response.status_code == 200:
            print("✅ Node-RED web interface: ACCESSIBLE")
            return True
        else:
            print(f"❌ Node-RED returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Node-RED connection failed: {e}")
        return False


def check_pipeline_automation_tab():
    """Check if Pipeline Automation tab was deployed"""
    print("\n🚀 CHECKING PIPELINE AUTOMATION DEPLOYMENT")
    print("=" * 50)

    try:
        response = requests.get("http://localhost:1880/flows", timeout=5)
        if response.status_code == 200:
            flows = response.json()

            # Look for our pipeline automation tab
            pipeline_tab = None
            for flow in flows:
                if flow.get("type") == "tab" and "🚀 Pipeline Automation" in flow.get(
                    "label", ""
                ):
                    pipeline_tab = flow
                    break

            if pipeline_tab:
                print("✅ Pipeline Automation tab: DEPLOYED")
                print(f"   Tab ID: {pipeline_tab['id']}")
                print(f"   Label: {pipeline_tab['label']}")

                # Count nodes in the tab
                tab_nodes = [f for f in flows if f.get("z") == pipeline_tab["id"]]
                print(f"   Nodes: {len(tab_nodes)} deployed")

                # List key nodes
                exec_nodes = [n for n in tab_nodes if n.get("type") == "exec"]
                inject_nodes = [n for n in tab_nodes if n.get("type") == "inject"]
                http_nodes = [n for n in tab_nodes if n.get("type") == "http in"]

                print(f"   - Exec nodes: {len(exec_nodes)}")
                print(f"   - Trigger buttons: {len(inject_nodes)}")
                print(f"   - API endpoints: {len(http_nodes)}")

                return True, pipeline_tab["id"]
            else:
                print("❌ Pipeline Automation tab: NOT FOUND")
                return False, None
        else:
            print(f"❌ Failed to get flows: {response.status_code}")
            return False, None

    except Exception as e:
        print(f"❌ Flow check failed: {e}")
        return False, None


def test_docker_connectivity():
    """Test Docker container connectivity"""
    print("\n🐳 TESTING DOCKER CONNECTIVITY")
    print("=" * 35)

    try:
        # Test the actual exec command that Node-RED will use
        import subprocess

        result = subprocess.run(
            [
                "docker",
                "exec",
                "horse_racing_data_pipeline_clean",
                "python",
                "--version",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("✅ Docker container access: SUCCESS")
            print(f"   Python version: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker container access: FAILED")
            print(f"   Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Docker test failed: {e}")
        return False


def test_pipeline_script_access():
    """Test access to the pipeline script"""
    print("\n🐍 TESTING PIPELINE SCRIPT ACCESS")
    print("=" * 40)

    try:
        import subprocess

        result = subprocess.run(
            [
                "docker",
                "exec",
                "horse_racing_data_pipeline_clean",
                "python",
                "/app/tools/manual_pipeline_trigger.py",
                "--help",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode == 0 and "usage:" in result.stdout:
            print("✅ Pipeline script access: SUCCESS")
            print("   manual_pipeline_trigger.py is accessible")
            return True
        else:
            print("❌ Pipeline script access: FAILED")
            print(f"   Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Pipeline script test failed: {e}")
        return False


def provide_manual_testing_instructions():
    """Provide instructions for manual testing in Node-RED"""
    print("\n📋 MANUAL TESTING INSTRUCTIONS")
    print("=" * 40)

    print("1. 🎛️  Open Node-RED Editor:")
    print("   → http://localhost:1880/admin")
    print()
    print("2. 📝 Find Pipeline Automation Tab:")
    print("   → Look for '🚀 Pipeline Automation' tab")
    print("   → Click to open the automation flow")
    print()
    print("3. 🧪 Test Docker Connection First:")
    print("   → Click '🔍 TEST CONNECTION' inject button")
    print("   → Check debug panel for '✅ Docker OK' message")
    print("   → Should show Python version from container")
    print()
    print("4. 🚀 Test Pipeline Execution:")
    print("   → Click '🎯 TRIGGER PIPELINE' inject button")
    print("   → Watch debug panel for execution output")
    print("   → Should see pipeline help text or execution results")
    print()
    print("5. 🌐 Test API Endpoint:")
    print("   → Use terminal command:")
    print("   curl -X POST http://localhost:1880/api/pipeline/trigger \\")
    print("     -H 'Content-Type: application/json' \\")
    print('     -d \'{"source":"test"}\'')
    print()
    print("6. 📊 Monitor Execution:")
    print("   → Debug panel shows real-time output")
    print("   → Success: ✅ messages in debug log")
    print("   → Errors: ❌ messages with error details")


def provide_next_steps():
    """Provide instructions for expanding to remaining scripts"""
    print("\n🎯 NEXT PHASE: EXPAND TO REMAINING SCRIPTS")
    print("=" * 50)

    scripts_to_add = [
        {
            "name": "Data Relationships Pipeline",
            "script": "/app/tools/data_processing/automated_relationships_pipeline.py",
            "timeout": "600",
            "description": "Process jockey/trainer statistics and relationships",
        },
        {
            "name": "Performance Tracker",
            "script": "/app/tools/automation/daily_performance_tracker.py",
            "timeout": "300",
            "description": "Track AI model performance metrics",
        },
        {
            "name": "ML Training",
            "script": "/app/docker/ml_training/unified_ml_trainer.py",
            "timeout": "3600",
            "description": "Train machine learning models",
        },
        {
            "name": "AI Selections Generator",
            "script": "/app/scripts/run_real_selections.py",
            "timeout": "180",
            "description": "Generate AI-powered race predictions",
        },
    ]

    print("Ready to add these 4 additional exec nodes:")
    print()

    for i, script in enumerate(scripts_to_add, 1):
        print(f"{i}. 🔧 {script['name']}")
        print(f"   Script: {script['script']}")
        print(f"   Timeout: {script['timeout']}s")
        print(f"   Purpose: {script['description']}")
        print()

    print("📋 Implementation Steps:")
    print("1. Copy the existing exec node pattern")
    print("2. Update script path and timeout for each")
    print("3. Add inject buttons for manual triggers")
    print("4. Connect debug nodes for monitoring")
    print("5. Test each script individually")
    print("6. Create unified dashboard controls")


def main():
    """Main verification process"""
    print("🏇 HORSE RACING AI - EXEC NODE DEPLOYMENT VERIFICATION")
    print("=" * 65)
    print(f"📅 Verification Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Check Node-RED
    node_red_ok = check_node_red_status()
    if not node_red_ok:
        print("\n❌ DEPLOYMENT VERIFICATION FAILED")
        print("Please ensure Node-RED is running with: docker-compose up node-red")
        return False

    # Step 2: Check deployment
    deployment_ok, tab_id = check_pipeline_automation_tab()
    if not deployment_ok:
        print("\n❌ PIPELINE AUTOMATION NOT DEPLOYED")
        print("Please run deployment again or import manually")
        return False

    # Step 3: Test Docker
    docker_ok = test_docker_connectivity()
    if not docker_ok:
        print("\n⚠️ DOCKER CONNECTIVITY ISSUES")
        print("Pipeline may not execute correctly")

    # Step 4: Test script access
    script_ok = test_pipeline_script_access()
    if not script_ok:
        print("\n⚠️ PIPELINE SCRIPT ACCESS ISSUES")
        print("Scripts may not be accessible from container")

    # Results summary
    print("\n📊 VERIFICATION SUMMARY")
    print("=" * 30)
    print(f"Node-RED Status: {'✅ OK' if node_red_ok else '❌ FAIL'}")
    print(f"Deployment Status: {'✅ OK' if deployment_ok else '❌ FAIL'}")
    print(f"Docker Access: {'✅ OK' if docker_ok else '⚠️ ISSUE'}")
    print(f"Script Access: {'✅ OK' if script_ok else '⚠️ ISSUE'}")

    if deployment_ok:
        print("\n🎉 EXEC NODE DEPLOYMENT SUCCESSFUL!")
        print("Ready for manual testing and expansion!")

        provide_manual_testing_instructions()
        provide_next_steps()

        return True
    else:
        print("\n❌ DEPLOYMENT NEEDS ATTENTION")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
