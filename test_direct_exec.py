#!/usr/bin/env python3
"""
Direct Exec Node Test - Bypass Node-RED for Direct Testing
=========================================================

This script directly tests our Python script execution using the same
command structure that Node-RED exec nodes will use.
"""

import subprocess
import time
import json
import os
from datetime import datetime


def test_exec_node_command():
    """Test the exact command that will be used in Node-RED exec nodes"""

    print("🧪 DIRECT EXEC NODE COMMAND TEST")
    print("=" * 50)

    # Test Command: Same as Node-RED exec node will use
    exec_command = [
        "docker",
        "exec",
        "horse_racing_data_pipeline_clean",
        "python",
        "/app/tools/manual_pipeline_trigger.py",
        "--help",
    ]

    print(f"📝 Testing Command: {' '.join(exec_command)}")
    print("-" * 50)

    start_time = time.time()

    try:
        # Execute with the same settings as Node-RED
        result = subprocess.run(
            exec_command,
            capture_output=True,
            text=True,
            timeout=30,  # Same timeout as our exec node
            env={**os.environ, "PYTHONUNBUFFERED": "1"},  # Same env var as exec node
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Format results like Node-RED would
        exec_result = {
            "success": result.returncode == 0,
            "execution_time_seconds": round(execution_time, 2),
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timestamp": datetime.now().isoformat(),
        }

        print("📊 EXECUTION RESULTS:")
        print(f"⏱️  Execution Time: {exec_result['execution_time_seconds']}s")
        print(f"🔢 Exit Code: {exec_result['exit_code']}")
        print(f"✅ Success: {exec_result['success']}")

        print("\n📤 STDOUT OUTPUT:")
        print("-" * 30)
        if exec_result["stdout"]:
            print(exec_result["stdout"])
        else:
            print("(No stdout output)")

        print("\n📤 STDERR OUTPUT:")
        print("-" * 30)
        if exec_result["stderr"]:
            print(exec_result["stderr"])
        else:
            print("(No stderr output)")

        # Test validation
        if exec_result["success"]:
            print("\n✅ EXEC NODE TEST: SUCCESS")
            print("🎯 This command is ready for Node-RED integration!")
        else:
            print("\n❌ EXEC NODE TEST: FAILED")
            print("⚠️ Command needs debugging before Node-RED integration")

        return exec_result

    except subprocess.TimeoutExpired:
        print("\n⏰ EXEC NODE TEST: TIMEOUT")
        print("⚠️ Command exceeded 30 second timeout")
        return {"success": False, "error": "timeout"}

    except Exception as e:
        print(f"\n❌ EXEC NODE TEST: EXCEPTION")
        print(f"⚠️ Error: {e}")
        return {"success": False, "error": str(e)}


def test_full_pipeline_command():
    """Test the full pipeline execution command"""

    print("\n\n🚀 FULL PIPELINE COMMAND TEST")
    print("=" * 50)

    # Full pipeline command
    full_command = [
        "docker",
        "exec",
        "horse_racing_data_pipeline_clean",
        "python",
        "/app/tools/manual_pipeline_trigger.py",
        "--all",
    ]

    print(f"📝 Testing Command: {' '.join(full_command)}")
    print("⚠️  WARNING: This will execute the full pipeline!")
    print("🔄 Timeout set to 5 minutes for full pipeline...")
    print("-" * 50)

    response = input("Continue with full pipeline test? (y/N): ")
    if response.lower() != "y":
        print("🛑 Full pipeline test skipped")
        return {"success": False, "skipped": True}

    start_time = time.time()

    try:
        # Execute full pipeline with longer timeout
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes for full pipeline
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )

        end_time = time.time()
        execution_time = end_time - start_time

        exec_result = {
            "success": result.returncode == 0,
            "execution_time_seconds": round(execution_time, 2),
            "exit_code": result.returncode,
            "stdout": result.stdout[:1000]
            + ("..." if len(result.stdout) > 1000 else ""),
            "stderr": result.stderr[:500] + ("..." if len(result.stderr) > 500 else ""),
            "timestamp": datetime.now().isoformat(),
        }

        print("📊 FULL PIPELINE RESULTS:")
        print(f"⏱️  Execution Time: {exec_result['execution_time_seconds']}s")
        print(f"🔢 Exit Code: {exec_result['exit_code']}")
        print(f"✅ Success: {exec_result['success']}")

        if exec_result["stdout"]:
            print("\n📤 STDOUT (truncated):")
            print(exec_result["stdout"])

        if exec_result["stderr"]:
            print("\n📤 STDERR (truncated):")
            print(exec_result["stderr"])

        return exec_result

    except subprocess.TimeoutExpired:
        print("\n⏰ FULL PIPELINE TEST: TIMEOUT")
        print("⚠️ Pipeline exceeded 5 minute timeout")
        return {"success": False, "error": "timeout"}

    except Exception as e:
        print(f"\n❌ FULL PIPELINE TEST: EXCEPTION")
        print(f"⚠️ Error: {e}")
        return {"success": False, "error": str(e)}


def create_node_red_exec_node_config(test_results):
    """Generate Node-RED exec node configuration based on test results"""

    if not test_results.get("success"):
        print("\n⚠️ Cannot create Node-RED config - tests failed")
        return None

    print("\n📋 GENERATING NODE-RED EXEC NODE CONFIG")
    print("=" * 50)

    exec_node_config = {
        "id": "manual-pipeline-exec-node",
        "type": "exec",
        "z": "pipeline-automation-tab",
        "command": "docker",
        "addpay": False,
        "append": "exec horse_racing_data_pipeline_clean python /app/tools/manual_pipeline_trigger.py --all",
        "useSpawn": False,
        "timer": "",
        "winHide": False,
        "oldrc": False,
        "name": "Manual Pipeline Trigger (Tested)",
        "env": [{"name": "PYTHONUNBUFFERED", "value": "1", "type": "str"}],
        "timeout": str(
            int(test_results["execution_time_seconds"] * 3 + 60)
        ),  # 3x test time + buffer
        "killSignal": "SIGTERM",
        "x": 400,
        "y": 200,
        "wires": [
            ["pipeline-success-handler"],
            ["pipeline-error-handler"],
            ["pipeline-exit-handler"],
        ],
    }

    config_file = "/home/jc/Documents/Horse-race-ai-v2.05/tested_exec_node_config.json"
    with open(config_file, "w") as f:
        json.dump(exec_node_config, f, indent=2)

    print(f"✅ Node-RED exec node config saved to: {config_file}")
    print(f"⏱️  Timeout set to: {exec_node_config['timeout']} seconds")
    print("🎯 Ready for Node-RED import!")

    return exec_node_config


def main():
    """Main test execution"""
    print("🏇 Horse Racing AI - Direct Exec Node Test")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    # Test 1: Help command (quick test)
    help_results = test_exec_node_command()

    if help_results.get("success"):
        print("\n🎯 Help command test successful - proceeding to pipeline test")

        # Test 2: Full pipeline (optional)
        pipeline_results = test_full_pipeline_command()

        if pipeline_results.get("success"):
            print("\n🎉 ALL TESTS SUCCESSFUL!")
            create_node_red_exec_node_config(pipeline_results)
        elif pipeline_results.get("skipped"):
            print("\n✅ Help test passed, pipeline test skipped")
            print("🎯 Exec node ready for Node-RED integration")
        else:
            print("\n⚠️ Pipeline test failed, but help test passed")
            print("🎯 Basic exec node ready, full pipeline needs debugging")
    else:
        print("\n❌ Help command test failed")
        print("🛑 Exec node not ready for Node-RED integration")
        return False

    print("\n📋 NEXT STEPS:")
    print("1. 🎛️  Open Node-RED editor at: http://localhost:1880/admin")
    print("2. 📝 Create new flow tab: 'Pipeline Automation'")
    print("3. 🔧 Add exec node with tested configuration")
    print("4. 🧪 Test exec node within Node-RED")
    print("5. 🚀 Deploy to C2 dashboard")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
