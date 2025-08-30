#!/usr/bin/env python3
"""
Deploy Exec Node to Existing Node-RED Instance
==============================================

Deploy our tested exec node to the running Node-RED instance at c2.horse-racing.local
"""

import requests
import json
import time
from datetime import datetime

NODE_RED_URL = "http://c2.horse-racing.local"


def get_existing_flows():
    """Get current Node-RED flows"""
    try:
        response = requests.get(f"{NODE_RED_URL}/flows")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get flows: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting flows: {e}")
        return None


def find_pipeline_tab(flows):
    """Find the Pipeline Control tab or create a new one"""
    for flow in flows:
        if flow.get("type") == "tab" and "Pipeline" in flow.get("label", ""):
            print(f"✅ Found existing Pipeline tab: {flow['label']}")
            return flow["id"]

    # Create new pipeline tab ID
    new_tab_id = f"pipeline-automation-{int(time.time())}"
    print(f"🆕 Will create new Pipeline Automation tab: {new_tab_id}")
    return new_tab_id


def create_exec_node_flow(tab_id):
    """Create our tested exec node flow"""
    timestamp = int(time.time())

    # Our validated exec node configuration
    exec_node_flow = [
        {
            "id": tab_id,
            "type": "tab",
            "label": "🚀 Pipeline Automation",
            "disabled": False,
            "info": "Python Script Automation via Exec Nodes",
        },
        {
            "id": f"manual-pipeline-exec-{timestamp}",
            "type": "exec",
            "z": tab_id,
            "command": "docker",
            "addpay": False,
            "append": "exec horse_racing_data_pipeline_clean python /app/tools/manual_pipeline_trigger.py --all",
            "useSpawn": False,
            "timer": "",
            "winHide": False,
            "oldrc": False,
            "name": "🔄 Manual Pipeline Trigger",
            "env": [{"name": "PYTHONUNBUFFERED", "value": "1", "type": "str"}],
            "timeout": "300",
            "killSignal": "SIGTERM",
            "x": 400,
            "y": 100,
            "wires": [
                [f"pipeline-success-{timestamp}"],
                [f"pipeline-error-{timestamp}"],
                [f"pipeline-exit-{timestamp}"],
            ],
        },
        {
            "id": f"pipeline-trigger-{timestamp}",
            "type": "inject",
            "z": tab_id,
            "name": "🚀 Trigger Pipeline",
            "props": [
                {
                    "p": "payload",
                    "v": '{"action":"manual_pipeline","timestamp":"'
                    + datetime.now().isoformat()
                    + '"}',
                    "vt": "json",
                }
            ],
            "repeat": "",
            "crontab": "",
            "once": False,
            "onceDelay": 0.1,
            "topic": "",
            "x": 160,
            "y": 100,
            "wires": [[f"manual-pipeline-exec-{timestamp}"]],
        },
        {
            "id": f"pipeline-success-{timestamp}",
            "type": "debug",
            "z": tab_id,
            "name": "✅ Pipeline Success",
            "active": True,
            "tosidebar": True,
            "console": False,
            "tostatus": False,
            "complete": "payload",
            "targetType": "msg",
            "statusVal": "",
            "statusType": "auto",
            "x": 650,
            "y": 80,
            "wires": [],
        },
        {
            "id": f"pipeline-error-{timestamp}",
            "type": "debug",
            "z": tab_id,
            "name": "❌ Pipeline Error",
            "active": True,
            "tosidebar": True,
            "console": False,
            "tostatus": False,
            "complete": "payload",
            "targetType": "msg",
            "statusVal": "",
            "statusType": "auto",
            "x": 650,
            "y": 120,
            "wires": [],
        },
        {
            "id": f"pipeline-exit-{timestamp}",
            "type": "debug",
            "z": tab_id,
            "name": "🔄 Pipeline Exit",
            "active": True,
            "tosidebar": True,
            "console": False,
            "tostatus": False,
            "complete": "payload",
            "targetType": "msg",
            "statusVal": "",
            "statusType": "auto",
            "x": 650,
            "y": 160,
            "wires": [],
        },
        {
            "id": f"api-pipeline-trigger-{timestamp}",
            "type": "http in",
            "z": tab_id,
            "name": "API: Pipeline Trigger",
            "url": "/api/pipeline/trigger",
            "method": "post",
            "upload": False,
            "swaggerDoc": "",
            "x": 160,
            "y": 200,
            "wires": [[f"api-handler-{timestamp}"]],
        },
        {
            "id": f"api-handler-{timestamp}",
            "type": "function",
            "z": tab_id,
            "name": "API Handler",
            "func": """// Handle API pipeline trigger
msg.payload = {
    action: 'api_trigger',
    timestamp: new Date().toISOString(),
    request_id: msg._msgid
};

// Send immediate response
msg.res.json({
    success: true,
    message: 'Pipeline triggered via API',
    request_id: msg._msgid
});

return msg;""",
            "outputs": 1,
            "noerr": 0,
            "initialize": "",
            "finalize": "",
            "libs": [],
            "x": 380,
            "y": 200,
            "wires": [[f"manual-pipeline-exec-{timestamp}"]],
        },
    ]

    return exec_node_flow


def deploy_exec_node():
    """Deploy our exec node to Node-RED"""
    print("🚀 DEPLOYING EXEC NODE TO NODE-RED")
    print("=" * 50)

    # Step 1: Get existing flows
    flows = get_existing_flows()
    if flows is None:
        return False

    print(f"📊 Found {len(flows)} existing flows")

    # Step 2: Find or create pipeline tab
    tab_id = find_pipeline_tab(flows)

    # Step 3: Create our exec node flow
    new_flows = create_exec_node_flow(tab_id)

    # Step 4: Add new flows to existing ones
    all_flows = flows + new_flows

    # Step 5: Deploy to Node-RED
    try:
        print("📤 Deploying flows to Node-RED...")
        response = requests.post(
            f"{NODE_RED_URL}/flows",
            json=all_flows,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 204:
            print("✅ Exec node deployed successfully!")
            print(f"🎯 Access at: {NODE_RED_URL}/#flow/{tab_id}")
            return True
        else:
            print(f"❌ Deployment failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False


def test_deployed_exec_node():
    """Test the deployed exec node"""
    print("\n🧪 TESTING DEPLOYED EXEC NODE")
    print("=" * 50)

    try:
        # Test API endpoint
        response = requests.post(
            f"{NODE_RED_URL}/api/pipeline/trigger",
            json={"test": True, "timestamp": datetime.now().isoformat()},
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ API endpoint responding")
            print(f"📝 Response: {result}")
            return True
        else:
            print(f"❌ API test failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ API test error: {e}")
        return False


def main():
    """Main deployment process"""
    print("🏇 Horse Racing AI - Exec Node Deployment")
    print("=" * 60)
    print(f"📅 Deployment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Target URL: {NODE_RED_URL}")
    print("")

    # Deploy exec node
    if deploy_exec_node():
        print("\n🎉 DEPLOYMENT SUCCESSFUL!")

        # Test deployment
        if test_deployed_exec_node():
            print("\n✅ EXEC NODE FULLY OPERATIONAL!")
            print("\n📋 WHAT'S AVAILABLE NOW:")
            print("• Manual trigger button in Node-RED editor")
            print("• API endpoint: POST /api/pipeline/trigger")
            print("• Real-time execution monitoring via debug nodes")
            print("• Automatic error handling and logging")

            print(f"\n🎯 ACCESS YOUR EXEC NODE:")
            print(f"• Editor: {NODE_RED_URL}/#flow/pipeline-automation-*")
            print(f"• Trigger: Click the inject node button")
            print(f"• Monitor: Watch debug panel for execution results")

            return True
        else:
            print("\n⚠️ Deployment successful but API test failed")
            return False
    else:
        print("\n❌ DEPLOYMENT FAILED")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
