#!/usr/bin/env python3
"""
Deploy Remaining Python Scripts as Exec Nodes
==============================================

Expand our exec node pattern to all remaining Python scripts:
1. Data Relationships Pipeline
2. Performance Tracker
3. ML Training
4. AI Selections Generator
"""

import requests
import json
import time
from datetime import datetime

NODE_RED_URL = "http://c2.horse-racing.local"

# Configuration for remaining Python scripts
PYTHON_SCRIPTS = {
    "data_relationships": {
        "name": "📊 Data Relationships",
        "script": "/app/tools/data_processing/automated_relationships_pipeline.py",
        "container": "horse_racing_data_pipeline_clean",
        "timeout": "600",  # 10 minutes
        "description": "Process jockey/trainer statistics and relationships",
    },
    "performance_tracker": {
        "name": "📈 Performance Tracker",
        "script": "/app/tools/automation/daily_performance_tracker.py",
        "container": "horse_racing_ml_trainer_clean",
        "timeout": "300",  # 5 minutes
        "description": "Track AI model performance metrics",
    },
    "ml_training": {
        "name": "🤖 ML Training",
        "script": "/app/docker/ml_training/unified_ml_trainer.py",
        "container": "horse_racing_ml_trainer_clean",
        "timeout": "1800",  # 30 minutes
        "description": "Train machine learning models",
    },
    "ai_selections": {
        "name": "🎯 AI Selections",
        "script": "/app/scripts/run_real_selections.py",
        "container": "horse_racing_ml_trainer_clean",
        "timeout": "180",  # 3 minutes
        "description": "Generate AI-powered race predictions",
    },
}


def create_exec_node_for_script(script_key, script_config, tab_id, y_position):
    """Create exec node configuration for a Python script"""
    timestamp = int(time.time())
    script_id = f"{script_key}-{timestamp}"

    exec_node = {
        "id": f"exec-{script_id}",
        "type": "exec",
        "z": tab_id,
        "command": "docker",
        "addpay": False,
        "append": f"exec {script_config['container']} python {script_config['script']}",
        "useSpawn": False,
        "timer": "",
        "winHide": False,
        "oldrc": False,
        "name": script_config["name"],
        "env": [{"name": "PYTHONUNBUFFERED", "value": "1", "type": "str"}],
        "timeout": script_config["timeout"],
        "killSignal": "SIGTERM",
        "x": 400,
        "y": y_position,
        "wires": [
            [f"success-{script_id}"],
            [f"error-{script_id}"],
            [f"exit-{script_id}"],
        ],
    }

    # Inject trigger
    inject_node = {
        "id": f"trigger-{script_id}",
        "type": "inject",
        "z": tab_id,
        "name": f"🚀 {script_config['name']}",
        "props": [
            {
                "p": "payload",
                "v": f'{{"action":"{script_key}","timestamp":"{datetime.now().isoformat()}"}}',
                "vt": "json",
            }
        ],
        "repeat": "",
        "crontab": "",
        "once": False,
        "onceDelay": 0.1,
        "topic": "",
        "x": 160,
        "y": y_position,
        "wires": [[f"exec-{script_id}"]],
    }

    # Debug nodes
    success_debug = {
        "id": f"success-{script_id}",
        "type": "debug",
        "z": tab_id,
        "name": f"✅ {script_key} Success",
        "active": True,
        "tosidebar": True,
        "console": False,
        "tostatus": False,
        "complete": "payload",
        "targetType": "msg",
        "x": 650,
        "y": y_position - 20,
        "wires": [],
    }

    error_debug = {
        "id": f"error-{script_id}",
        "type": "debug",
        "z": tab_id,
        "name": f"❌ {script_key} Error",
        "active": True,
        "tosidebar": True,
        "console": False,
        "tostatus": False,
        "complete": "payload",
        "targetType": "msg",
        "x": 650,
        "y": y_position,
        "wires": [],
    }

    exit_debug = {
        "id": f"exit-{script_id}",
        "type": "debug",
        "z": tab_id,
        "name": f"🔄 {script_key} Exit",
        "active": True,
        "tosidebar": True,
        "console": False,
        "tostatus": False,
        "complete": "payload",
        "targetType": "msg",
        "x": 650,
        "y": y_position + 20,
        "wires": [],
    }

    # API endpoint
    api_node = {
        "id": f"api-{script_id}",
        "type": "http in",
        "z": tab_id,
        "name": f"API: {script_key}",
        "url": f"/api/pipeline/{script_key}",
        "method": "post",
        "upload": False,
        "swaggerDoc": "",
        "x": 160,
        "y": y_position + 60,
        "wires": [[f"api-handler-{script_id}"]],
    }

    # API handler
    api_handler = {
        "id": f"api-handler-{script_id}",
        "type": "function",
        "z": tab_id,
        "name": f"{script_key} API Handler",
        "func": f"""// Handle {script_key} API trigger
msg.payload = {{
    action: '{script_key}',
    timestamp: new Date().toISOString(),
    request_id: msg._msgid
}};

// Send immediate response
msg.res.json({{
    success: true,
    message: '{script_config["name"]} triggered via API',
    description: '{script_config["description"]}',
    request_id: msg._msgid
}});

return msg;""",
        "outputs": 1,
        "noerr": 0,
        "x": 380,
        "y": y_position + 60,
        "wires": [[f"exec-{script_id}"]],
    }

    return [
        exec_node,
        inject_node,
        success_debug,
        error_debug,
        exit_debug,
        api_node,
        api_handler,
    ]


def deploy_remaining_scripts():
    """Deploy all remaining Python scripts as exec nodes"""
    print("🚀 DEPLOYING REMAINING PYTHON SCRIPTS")
    print("=" * 50)

    # Get existing flows
    response = requests.get(f"{NODE_RED_URL}/flows")
    if response.status_code != 200:
        print(f"❌ Failed to get flows: {response.status_code}")
        return False

    flows = response.json()

    # Find pipeline tab
    pipeline_tab_id = None
    for flow in flows:
        if flow.get("type") == "tab" and "Pipeline" in flow.get("label", ""):
            pipeline_tab_id = flow["id"]
            break

    if not pipeline_tab_id:
        print("❌ Pipeline tab not found!")
        return False

    print(f"✅ Found pipeline tab: {pipeline_tab_id}")

    # Create nodes for all scripts
    new_nodes = []
    y_position = 300  # Start below existing nodes

    for script_key, script_config in PYTHON_SCRIPTS.items():
        print(f"📝 Creating nodes for: {script_config['name']}")
        script_nodes = create_exec_node_for_script(
            script_key, script_config, pipeline_tab_id, y_position
        )
        new_nodes.extend(script_nodes)
        y_position += 120  # Space between script groups

    # Add comment node for organization
    comment_node = {
        "id": f"comment-{int(time.time())}",
        "type": "comment",
        "z": pipeline_tab_id,
        "name": "🐍 Python Script Automation",
        "info": "Automated execution of Horse Racing AI Python scripts via Docker containers",
        "x": 400,
        "y": 250,
        "wires": [],
    }
    new_nodes.append(comment_node)

    # Deploy all flows
    all_flows = flows + new_nodes

    try:
        print("📤 Deploying expanded flows...")
        response = requests.post(
            f"{NODE_RED_URL}/flows",
            json=all_flows,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 204:
            print("✅ All Python scripts deployed successfully!")
            return True
        else:
            print(f"❌ Deployment failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False


def test_script_endpoints():
    """Test all deployed script endpoints"""
    print("\n🧪 TESTING ALL SCRIPT ENDPOINTS")
    print("=" * 50)

    test_results = {}

    for script_key, script_config in PYTHON_SCRIPTS.items():
        try:
            print(f"Testing {script_config['name']}...")
            response = requests.post(
                f"{NODE_RED_URL}/api/pipeline/{script_key}",
                json={"test": True, "timestamp": datetime.now().isoformat()},
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ {script_config['name']}: API responding")
                test_results[script_key] = True
            else:
                print(f"❌ {script_config['name']}: Failed ({response.status_code})")
                test_results[script_key] = False

        except Exception as e:
            print(f"❌ {script_config['name']}: Error - {e}")
            test_results[script_key] = False

    return test_results


def create_master_control_panel():
    """Create a master control panel for all scripts"""
    print("\n🎛️ CREATING MASTER CONTROL PANEL")
    print("=" * 50)

    # Get flows again
    response = requests.get(f"{NODE_RED_URL}/flows")
    flows = response.json()

    # Find pipeline tab
    pipeline_tab_id = None
    for flow in flows:
        if flow.get("type") == "tab" and "Pipeline" in flow.get("label", ""):
            pipeline_tab_id = flow["id"]
            break

    timestamp = int(time.time())

    # Master control panel nodes
    control_nodes = [
        {
            "id": f"master-panel-{timestamp}",
            "type": "ui_template",
            "z": pipeline_tab_id,
            "name": "🎛️ Master Control Panel",
            "group": "",
            "order": 0,
            "width": 12,
            "height": 8,
            "format": """
<div style="background: #1a1a2e; color: #fff; padding: 20px; border-radius: 10px;">
    <h2>🏇 Horse Racing AI - Pipeline Control</h2>
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 20px;">
        <button onclick="triggerScript('manual_pipeline')" style="background: #00ff88; color: #000; padding: 15px; border: none; border-radius: 8px; font-weight: bold;">
            🔄 Manual Pipeline
        </button>
        <button onclick="triggerScript('data_relationships')" style="background: #667eea; color: #fff; padding: 15px; border: none; border-radius: 8px; font-weight: bold;">
            📊 Data Relationships
        </button>
        <button onclick="triggerScript('performance_tracker')" style="background: #764ba2; color: #fff; padding: 15px; border: none; border-radius: 8px; font-weight: bold;">
            📈 Performance Tracker
        </button>
        <button onclick="triggerScript('ml_training')" style="background: #ff6b6b; color: #fff; padding: 15px; border: none; border-radius: 8px; font-weight: bold;">
            🤖 ML Training
        </button>
        <button onclick="triggerScript('ai_selections')" style="background: #ffd93d; color: #000; padding: 15px; border: none; border-radius: 8px; font-weight: bold;">
            🎯 AI Selections
        </button>
        <button onclick="runAllScripts()" style="background: linear-gradient(45deg, #667eea, #764ba2); color: #fff; padding: 15px; border: none; border-radius: 8px; font-weight: bold;">
            🚀 Run All Scripts
        </button>
    </div>
    <div id="status" style="margin-top: 20px; padding: 10px; background: #333; border-radius: 5px;">
        ✅ All systems ready
    </div>
</div>

<script>
function triggerScript(scriptName) {
    document.getElementById('status').innerHTML = `🔄 Triggering ${scriptName}...`;
    
    fetch(`/api/pipeline/${scriptName}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({timestamp: new Date().toISOString()})
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('status').innerHTML = `✅ ${data.message}`;
    })
    .catch(error => {
        document.getElementById('status').innerHTML = `❌ Error: ${error.message}`;
    });
}

function runAllScripts() {
    const scripts = ['manual_pipeline', 'data_relationships', 'performance_tracker', 'ml_training', 'ai_selections'];
    let completed = 0;
    
    document.getElementById('status').innerHTML = '🚀 Running all scripts...';
    
    scripts.forEach((script, index) => {
        setTimeout(() => {
            triggerScript(script);
            completed++;
            if (completed === scripts.length) {
                setTimeout(() => {
                    document.getElementById('status').innerHTML = '🎉 All scripts triggered!';
                }, 1000);
            }
        }, index * 2000); // 2 second delay between scripts
    });
}
</script>
            """,
            "storeOutMessages": True,
            "fwdInMessages": True,
            "resendOnRefresh": False,
            "templateScope": "local",
            "x": 900,
            "y": 100,
            "wires": [[]],
        }
    ]

    # Add control panel
    all_flows = flows + control_nodes

    try:
        response = requests.post(
            f"{NODE_RED_URL}/flows",
            json=all_flows,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 204:
            print("✅ Master control panel created!")
            return True
        else:
            print(f"❌ Control panel creation failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Control panel error: {e}")
        return False


def main():
    """Main deployment process for remaining scripts"""
    print("🏇 Horse Racing AI - Complete Python Script Automation")
    print("=" * 70)
    print(f"📅 Deployment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Target URL: {NODE_RED_URL}")
    print("")

    print("📋 DEPLOYING SCRIPTS:")
    for script_key, script_config in PYTHON_SCRIPTS.items():
        print(f"  • {script_config['name']}: {script_config['description']}")
    print("")

    # Deploy remaining scripts
    if deploy_remaining_scripts():
        print("\n🎉 ALL SCRIPTS DEPLOYED!")

        # Test endpoints
        test_results = test_script_endpoints()

        successful_tests = sum(test_results.values())
        total_tests = len(test_results)

        if successful_tests == total_tests:
            print(f"\n✅ ALL {total_tests} ENDPOINTS OPERATIONAL!")

            # Create master control panel
            if create_master_control_panel():
                print("\n🎛️ MASTER CONTROL PANEL CREATED!")

                print("\n🎯 COMPLETE AUTOMATION READY!")
                print("=" * 50)
                print("📋 AVAILABLE AUTOMATIONS:")
                print("• Manual Pipeline Trigger")
                print("• Data Relationships Processing")
                print("• Performance Tracking")
                print("• ML Model Training")
                print("• AI Selections Generation")
                print("")
                print("🌐 ACCESS POINTS:")
                print(f"• Editor: {NODE_RED_URL}/#flow/pipeline-control-tab")
                print(f"• API Base: {NODE_RED_URL}/api/pipeline/")
                print("• Manual Triggers: Click inject nodes in editor")
                print("• Master Panel: Available in Node-RED UI")

                return True
            else:
                print("\n⚠️ Scripts deployed but control panel failed")
        else:
            print(f"\n⚠️ {successful_tests}/{total_tests} endpoints working")

    return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
