#!/usr/bin/env python3
import json
import re


def replace_dashboard_template():
    # Read the C2 template
    with open("c2-dashboard-template.html", "r", encoding="utf-8") as f:
        new_template = f.read()

    # Read the current flows.json
    with open("flows.json", "r", encoding="utf-8") as f:
        flows_content = f.read()

    # Parse the JSON to work with the structure
    flows_data = json.loads(flows_content)

    # Find the dashboard template node and update it
    for node in flows_data:
        if isinstance(node, dict) and node.get("id") == "dashboard_template":
            print("Found dashboard template node, updating...")
            node["template"] = new_template
            break
    else:
        print("❌ Dashboard template node not found!")
        return False

    # Write back to flows.json
    with open("flows.json", "w", encoding="utf-8") as f:
        json.dump(flows_data, f, indent=2, ensure_ascii=False)

    print("✅ C2 Dashboard template successfully updated!")
    print(f"📏 New template size: {len(new_template)} characters")
    print("🎯 Enhanced features added:")
    print("   • Modern C2 Command Center UI")
    print("   • NTFY Integration with real-time notifications")
    print("   • Tabbed interface (Overview, Operations, NTFY Control, Console)")
    print("   • Real-time system monitoring")
    print("   • Enhanced visual design with animations")
    print("   • Command palette for quick actions")
    return True


if __name__ == "__main__":
    replace_dashboard_template()
