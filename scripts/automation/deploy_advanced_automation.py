#!/usr/bin/env python3
"""
Deploy Long-term Automation Features
===================================

Set up scheduled triggers, file watchers, and advanced automation features:
1. Cron-based scheduled execution
2. File watcher integration
3. Automated pipeline orchestration
4. Performance monitoring and alerting
"""

import requests
import json
import time
from datetime import datetime

NODE_RED_URL = "http://c2.horse-racing.local"


def create_scheduled_automation():
    """Create scheduled automation flows"""

    # Get existing flows
    response = requests.get(f"{NODE_RED_URL}/flows")
    flows = response.json()

    # Find pipeline tab
    pipeline_tab_id = None
    for flow in flows:
        if flow.get("type") == "tab" and "Pipeline" in flow.get("label", ""):
            pipeline_tab_id = flow["id"]
            break

    timestamp = int(time.time())

    # Scheduled automation nodes
    scheduled_nodes = [
        # Daily morning pipeline (7 AM)
        {
            "id": f"daily-morning-{timestamp}",
            "type": "inject",
            "z": pipeline_tab_id,
            "name": "🌅 Daily Morning (7 AM)",
            "props": [{"p": "payload", "v": "daily_morning", "vt": "str"}],
            "repeat": "",
            "crontab": "0 7 * * *",  # 7 AM daily
            "once": False,
            "onceDelay": 0.1,
            "topic": "",
            "x": 160,
            "y": 600,
            "wires": [[f"morning-sequence-{timestamp}"]],
        },
        # Evening performance tracking (6 PM)
        {
            "id": f"daily-evening-{timestamp}",
            "type": "inject",
            "z": pipeline_tab_id,
            "name": "🌆 Daily Evening (6 PM)",
            "props": [{"p": "payload", "v": "daily_evening", "vt": "str"}],
            "repeat": "",
            "crontab": "0 18 * * *",  # 6 PM daily
            "once": False,
            "onceDelay": 0.1,
            "topic": "",
            "x": 160,
            "y": 650,
            "wires": [[f"evening-sequence-{timestamp}"]],
        },
        # Weekly ML training (Sunday 2 AM)
        {
            "id": f"weekly-training-{timestamp}",
            "type": "inject",
            "z": pipeline_tab_id,
            "name": "📚 Weekly ML Training (Sun 2 AM)",
            "props": [{"p": "payload", "v": "weekly_training", "vt": "str"}],
            "repeat": "",
            "crontab": "0 2 * * 0",  # Sunday 2 AM
            "once": False,
            "onceDelay": 0.1,
            "topic": "",
            "x": 160,
            "y": 700,
            "wires": [[f"training-sequence-{timestamp}"]],
        },
        # Morning sequence function
        {
            "id": f"morning-sequence-{timestamp}",
            "type": "function",
            "z": pipeline_tab_id,
            "name": "🌅 Morning Automation Sequence",
            "func": """
// Morning automation sequence
msg.sequence = "morning";
msg.payload = {
    timestamp: new Date().toISOString(),
    sequence: "morning",
    tasks: [
        "data_relationships",
        "performance_tracker",
        "ai_selections"
    ]
};

node.status({fill: "blue", shape: "dot", text: "Starting morning sequence"});
return msg;
            """,
            "outputs": 1,
            "noerr": 0,
            "x": 400,
            "y": 600,
            "wires": [[f"sequence-executor-{timestamp}"]],
        },
        # Evening sequence function
        {
            "id": f"evening-sequence-{timestamp}",
            "type": "function",
            "z": pipeline_tab_id,
            "name": "🌆 Evening Automation Sequence",
            "func": """
// Evening automation sequence
msg.sequence = "evening";
msg.payload = {
    timestamp: new Date().toISOString(),
    sequence: "evening",
    tasks: [
        "performance_tracker",
        "data_relationships"
    ]
};

node.status({fill: "orange", shape: "dot", text: "Starting evening sequence"});
return msg;
            """,
            "outputs": 1,
            "noerr": 0,
            "x": 400,
            "y": 650,
            "wires": [[f"sequence-executor-{timestamp}"]],
        },
        # Training sequence function
        {
            "id": f"training-sequence-{timestamp}",
            "type": "function",
            "z": pipeline_tab_id,
            "name": "📚 Training Automation Sequence",
            "func": """
// Weekly training sequence
msg.sequence = "training";
msg.payload = {
    timestamp: new Date().toISOString(),
    sequence: "training", 
    tasks: [
        "ml_training"
    ]
};

node.status({fill: "purple", shape: "dot", text: "Starting training sequence"});
return msg;
            """,
            "outputs": 1,
            "noerr": 0,
            "x": 400,
            "y": 700,
            "wires": [[f"sequence-executor-{timestamp}"]],
        },
        # Sequence executor
        {
            "id": f"sequence-executor-{timestamp}",
            "type": "function",
            "z": pipeline_tab_id,
            "name": "🔄 Sequence Executor",
            "func": """
// Execute automation sequence
const tasks = msg.payload.tasks;
const sequence = msg.payload.sequence;

// Execute tasks sequentially with delays
tasks.forEach((task, index) => {
    setTimeout(() => {
        // Trigger API call for each task
        const apiMsg = {
            url: `/api/pipeline/${task}`,
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            payload: {
                sequence: sequence,
                task_index: index,
                total_tasks: tasks.length,
                timestamp: new Date().toISOString()
            }
        };
        
        node.send(apiMsg);
        
        node.status({
            fill: "green", 
            shape: "dot", 
            text: `${sequence}: ${task} (${index+1}/${tasks.length})`
        });
        
    }, index * 30000); // 30 second delay between tasks
});

return null; // Don't send msg immediately
            """,
            "outputs": 1,
            "noerr": 0,
            "x": 650,
            "y": 650,
            "wires": [[f"api-caller-{timestamp}"]],
        },
        # API caller
        {
            "id": f"api-caller-{timestamp}",
            "type": "http request",
            "z": pipeline_tab_id,
            "name": "🌐 API Caller",
            "method": "use",
            "ret": "obj",
            "paytoqs": "ignore",
            "url": "",
            "tls": "",
            "persist": False,
            "proxy": "",
            "authType": "",
            "senderr": False,
            "x": 850,
            "y": 650,
            "wires": [[f"sequence-logger-{timestamp}"]],
        },
        # Sequence logger
        {
            "id": f"sequence-logger-{timestamp}",
            "type": "debug",
            "z": pipeline_tab_id,
            "name": "📝 Sequence Logger",
            "active": True,
            "tosidebar": True,
            "console": False,
            "tostatus": False,
            "complete": "payload",
            "targetType": "msg",
            "x": 1050,
            "y": 650,
            "wires": [],
        },
    ]

    return scheduled_nodes


def create_file_watcher():
    """Create file watcher automation"""

    # Get existing flows
    response = requests.get(f"{NODE_RED_URL}/flows")
    flows = response.json()

    # Find pipeline tab
    pipeline_tab_id = None
    for flow in flows:
        if flow.get("type") == "tab" and "Pipeline" in flow.get("label", ""):
            pipeline_tab_id = flow["id"]
            break

    timestamp = int(time.time())

    # File watcher nodes
    file_watcher_nodes = [
        # File watcher inject (every 5 minutes)
        {
            "id": f"file-watcher-{timestamp}",
            "type": "inject",
            "z": pipeline_tab_id,
            "name": "📁 File Watcher (5 min)",
            "props": [{"p": "payload", "v": "check_files", "vt": "str"}],
            "repeat": "300",  # Every 5 minutes
            "crontab": "",
            "once": True,
            "onceDelay": 10,
            "topic": "",
            "x": 160,
            "y": 800,
            "wires": [[f"file-checker-{timestamp}"]],
        },
        # File checker function
        {
            "id": f"file-checker-{timestamp}",
            "type": "function",
            "z": pipeline_tab_id,
            "name": "📁 File Checker",
            "func": """
// Check for new files that need processing
const fs = require('fs');
const path = require('path');

// Data directories to monitor
const dataDirs = [
    '/data/upload',
    '/data/incoming',
    '/data/racecard',
    '/data/results'
];

let newFiles = [];

dataDirs.forEach(dir => {
    try {
        if (fs.existsSync(dir)) {
            const files = fs.readdirSync(dir);
            const recentFiles = files.filter(file => {
                const filePath = path.join(dir, file);
                const stats = fs.statSync(filePath);
                const ageMinutes = (Date.now() - stats.mtime.getTime()) / (1000 * 60);
                return ageMinutes < 10; // Files newer than 10 minutes
            });
            
            if (recentFiles.length > 0) {
                newFiles.push({
                    directory: dir,
                    files: recentFiles,
                    count: recentFiles.length
                });
            }
        }
    } catch (err) {
        // Directory doesn't exist or no access
    }
});

if (newFiles.length > 0) {
    msg.payload = {
        timestamp: new Date().toISOString(),
        new_files_detected: true,
        directories: newFiles,
        total_files: newFiles.reduce((sum, dir) => sum + dir.count, 0)
    };
    
    node.status({
        fill: "yellow",
        shape: "dot", 
        text: `${msg.payload.total_files} new files detected`
    });
    
    return msg;
} else {
    // No new files, don't send message
    node.status({fill: "green", shape: "dot", text: "No new files"});
    return null;
}
            """,
            "outputs": 1,
            "noerr": 0,
            "x": 400,
            "y": 800,
            "wires": [[f"file-processor-{timestamp}"]],
        },
        # File processor
        {
            "id": f"file-processor-{timestamp}",
            "type": "function",
            "z": pipeline_tab_id,
            "name": "⚙️ File Processor",
            "func": """
// Process detected files by triggering appropriate pipeline
const directories = msg.payload.directories;
let actions = [];

directories.forEach(dir => {
    const dirName = dir.directory.split('/').pop();
    
    switch(dirName) {
        case 'racecard':
        case 'upload':
            actions.push('data_relationships');
            break;
        case 'results':
            actions.push('performance_tracker');
            break;
        case 'incoming':
            actions.push('manual_pipeline');
            break;
    }
});

// Remove duplicates
actions = [...new Set(actions)];

msg.payload = {
    ...msg.payload,
    triggered_actions: actions,
    processing_mode: 'file_triggered'
};

node.status({
    fill: "blue",
    shape: "dot",
    text: `Triggering ${actions.length} actions`
});

return msg;
            """,
            "outputs": 1,
            "noerr": 0,
            "x": 650,
            "y": 800,
            "wires": [[f"action-trigger-{timestamp}"]],
        },
        # Action trigger
        {
            "id": f"action-trigger-{timestamp}",
            "type": "function",
            "z": pipeline_tab_id,
            "name": "🚀 Action Trigger",
            "func": """
// Trigger actions based on detected files
const actions = msg.payload.triggered_actions;

actions.forEach((action, index) => {
    setTimeout(() => {
        const apiMsg = {
            url: `/api/pipeline/${action}`,
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            payload: {
                trigger_type: 'file_watcher',
                file_count: msg.payload.total_files,
                timestamp: new Date().toISOString()
            }
        };
        
        node.send(apiMsg);
        
    }, index * 5000); // 5 second delay between actions
});

return null;
            """,
            "outputs": 1,
            "noerr": 0,
            "x": 850,
            "y": 800,
            "wires": [[f"api-caller-{timestamp}"]],
        },
    ]

    return file_watcher_nodes


def deploy_advanced_automation():
    """Deploy all advanced automation features"""
    print("🚀 DEPLOYING ADVANCED AUTOMATION")
    print("=" * 50)

    # Get existing flows
    response = requests.get(f"{NODE_RED_URL}/flows")
    if response.status_code != 200:
        print(f"❌ Failed to get flows: {response.status_code}")
        return False

    flows = response.json()
    print(f"📊 Current flows: {len(flows)}")

    # Create automation nodes
    scheduled_nodes = create_scheduled_automation()
    file_watcher_nodes = create_file_watcher()

    print(f"📝 Created {len(scheduled_nodes)} scheduled automation nodes")
    print(f"📝 Created {len(file_watcher_nodes)} file watcher nodes")

    # Combine all flows
    all_flows = flows + scheduled_nodes + file_watcher_nodes

    # Deploy
    try:
        print("📤 Deploying advanced automation...")
        response = requests.post(
            f"{NODE_RED_URL}/flows",
            json=all_flows,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 204:
            print("✅ Advanced automation deployed successfully!")
            return True
        else:
            print(f"❌ Deployment failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False


def create_monitoring_dashboard():
    """Create monitoring and alerting dashboard"""
    print("\n📊 CREATING MONITORING DASHBOARD")
    print("=" * 50)

    # Get flows
    response = requests.get(f"{NODE_RED_URL}/flows")
    flows = response.json()

    # Find pipeline tab
    pipeline_tab_id = None
    for flow in flows:
        if flow.get("type") == "tab" and "Pipeline" in flow.get("label", ""):
            pipeline_tab_id = flow["id"]
            break

    timestamp = int(time.time())

    # Monitoring nodes
    monitoring_nodes = [
        # System monitor (every minute)
        {
            "id": f"system-monitor-{timestamp}",
            "type": "inject",
            "z": pipeline_tab_id,
            "name": "📊 System Monitor (1 min)",
            "props": [{"p": "payload", "v": "monitor", "vt": "str"}],
            "repeat": "60",  # Every minute
            "crontab": "",
            "once": True,
            "onceDelay": 5,
            "topic": "",
            "x": 160,
            "y": 900,
            "wires": [[f"health-checker-{timestamp}"]],
        },
        # Health checker
        {
            "id": f"health-checker-{timestamp}",
            "type": "function",
            "z": pipeline_tab_id,
            "name": "🏥 Health Checker",
            "func": """
// Check system health
const { exec } = require('child_process');

// Check Docker containers
exec('docker ps --format "table {{.Names}}\\t{{.Status}}"', (error, stdout, stderr) => {
    if (!error) {
        const containers = stdout.split('\\n').slice(1).filter(line => line.trim());
        
        msg.payload = {
            timestamp: new Date().toISOString(),
            system_health: {
                containers_running: containers.length,
                containers: containers.map(line => {
                    const parts = line.split('\\t');
                    return {
                        name: parts[0],
                        status: parts[1]
                    };
                })
            }
        };
        
        node.send(msg);
    }
});

return null;
            """,
            "outputs": 1,
            "noerr": 0,
            "x": 400,
            "y": 900,
            "wires": [[f"health-logger-{timestamp}"]],
        },
        # Health logger
        {
            "id": f"health-logger-{timestamp}",
            "type": "debug",
            "z": pipeline_tab_id,
            "name": "📝 Health Logger",
            "active": True,
            "tosidebar": True,
            "console": False,
            "tostatus": False,
            "complete": "payload",
            "targetType": "msg",
            "x": 650,
            "y": 900,
            "wires": [],
        },
    ]

    # Add monitoring nodes to flows
    all_flows = flows + monitoring_nodes

    try:
        response = requests.post(
            f"{NODE_RED_URL}/flows",
            json=all_flows,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 204:
            print("✅ Monitoring dashboard created!")
            return True
        else:
            print(f"❌ Monitoring creation failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Monitoring error: {e}")
        return False


def main():
    """Deploy complete long-term automation"""
    print("🏇 Horse Racing AI - Advanced Automation Deployment")
    print("=" * 70)
    print(f"📅 Deployment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Target URL: {NODE_RED_URL}")
    print("")

    print("🎯 DEPLOYING AUTOMATION FEATURES:")
    print("• ⏰ Scheduled Triggers (Daily morning, evening, weekly)")
    print("• 📁 File Watcher (5-minute intervals)")
    print("• 📊 System Monitoring (Real-time health checks)")
    print("• 🔄 Automated Pipeline Orchestration")
    print("")

    # Deploy advanced automation
    if deploy_advanced_automation():
        print("\n✅ ADVANCED AUTOMATION DEPLOYED!")

        # Create monitoring
        if create_monitoring_dashboard():
            print("\n🎉 COMPLETE LONG-TERM AUTOMATION READY!")
            print("=" * 60)

            print("📋 AUTOMATION SCHEDULE:")
            print("• 🌅 Daily 7 AM: Morning pipeline sequence")
            print("• 🌆 Daily 6 PM: Evening performance tracking")
            print("• 📚 Sunday 2 AM: Weekly ML training")
            print("• 📁 Every 5 min: File watcher checks")
            print("• 📊 Every 1 min: System health monitoring")

            print("\n🌐 MANAGEMENT:")
            print(f"• Node-RED Editor: {NODE_RED_URL}/#flow/pipeline-control-tab")
            print(f"• API Base: {NODE_RED_URL}/api/pipeline/")
            print("• Scheduled automation runs automatically")
            print("• File changes trigger appropriate pipelines")
            print("• System health continuously monitored")

            print("\n🎯 AUTOMATION IS NOW FULLY AUTONOMOUS!")

            return True
        else:
            print("\n⚠️ Automation deployed but monitoring failed")
    else:
        print("\n❌ Advanced automation deployment failed")

    return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
