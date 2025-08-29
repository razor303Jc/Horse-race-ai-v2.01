#!/usr/bin/env python3
"""
Node-RED Script Path Fixer
Identifies missing Python scripts referenced by Node-RED flows and updates paths to existing alternatives.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


class NodeRedScriptFixer:
    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.04"):
        self.base_path = Path(base_path)
        self.missing_scripts: Dict[str, List[str]] = {}
        self.existing_alternatives: Dict[str, List[str]] = {}
        self.flow_updates_needed: List[Dict] = []

    def analyze_flows(self) -> None:
        """Analyze Node-RED flows to find Python script references."""
        # Check both possible Node-RED locations
        node_red_dirs = [
            self.base_path / "node-red",
            self.base_path / "docker" / "node-red",
        ]

        found_dirs = [d for d in node_red_dirs if d.exists()]
        if not found_dirs:
            print("❌ Node-RED directories not found")
            return

        # Find all flow files in all found directories
        flow_files = []
        for node_red_dir in found_dirs:
            flow_files.extend(list(node_red_dir.glob("**/*.json")))

        print(f"📋 Found {len(flow_files)} Node-RED flow files")

        for flow_file in flow_files:
            try:
                with open(flow_file, "r") as f:
                    flow_data = json.load(f)

                if isinstance(flow_data, list):
                    self._extract_scripts_from_nodes(flow_data, flow_file)

            except (json.JSONDecodeError, Exception) as e:
                print(f"⚠️  Error reading {flow_file}: {e}")

    def _extract_scripts_from_nodes(self, nodes: List[Dict], flow_file: Path) -> None:
        """Extract Python script references from Node-RED nodes."""
        for node in nodes:
            if not isinstance(node, dict):
                continue

            # Check for Python script references in various node properties
            script_patterns = [
                r"python3?\s+([^\s]+\.py)",
                r"exec\s+([^\s]+\.py)",
                r"(?:scripts|tools)/[^\s]*\.py",
                r"/home/jc/Documents/Horse-race-ai-v2\.04/[^\s]*\.py",
            ]

            # Search in common node properties
            properties_to_check = ["command", "filename", "payload", "msg", "code"]

            for prop in properties_to_check:
                if prop in node:
                    value = str(node[prop])
                    for pattern in script_patterns:
                        matches = re.findall(pattern, value)
                        for match in matches:
                            self._check_script_existence(match, flow_file)

    def _check_script_existence(self, script_path: str, flow_file: Path) -> None:
        """Check if a script exists and find alternatives if it doesn't."""
        # Clean up the path
        script_path = script_path.strip().strip("\"'")

        # Convert relative paths to absolute
        if not script_path.startswith("/"):
            full_path = self.base_path / script_path
        else:
            full_path = Path(script_path)

        if not full_path.exists():
            # Find existing alternatives
            script_name = full_path.name
            alternatives = self._find_script_alternatives(script_name)

            if script_path not in self.missing_scripts:
                self.missing_scripts[script_path] = []
            self.missing_scripts[script_path].append(str(flow_file))

            if alternatives:
                self.existing_alternatives[script_path] = alternatives

    def _find_script_alternatives(self, script_name: str) -> List[str]:
        """Find existing Python scripts with similar names or functionality."""
        alternatives = []

        # Search for exact name matches
        for py_file in self.base_path.rglob("*.py"):
            if py_file.name == script_name:
                alternatives.append(str(py_file.relative_to(self.base_path)))

        # Search for similar functionality based on name patterns
        base_name = script_name.replace(".py", "").replace("_", "").replace("-", "")

        for py_file in self.base_path.rglob("*.py"):
            file_base = (
                py_file.name.replace(".py", "").replace("_", "").replace("-", "")
            )

            # Check for similar names or common patterns
            if (
                base_name in file_base
                or file_base in base_name
                or any(
                    pattern in file_base
                    for pattern in [
                        "download",
                        "clean",
                        "import",
                        "predict",
                        "bulk",
                        "upload",
                    ]
                    if pattern in base_name
                )
            ):
                rel_path = str(py_file.relative_to(self.base_path))
                if rel_path not in alternatives:
                    alternatives.append(rel_path)

        return alternatives[:5]  # Limit to top 5 alternatives

    def suggest_fixes(self) -> None:
        """Generate fix suggestions for missing scripts."""
        print("\n" + "=" * 80)
        print("🔧 NODE-RED SCRIPT FIX RECOMMENDATIONS")
        print("=" * 80)

        if not self.missing_scripts:
            print("✅ All Python scripts referenced by Node-RED flows exist!")
            return

        print(f"\n📊 Found {len(self.missing_scripts)} missing script references")

        for missing_script, flow_files in self.missing_scripts.items():
            print(f"\n❌ Missing: {missing_script}")
            print(f"   Referenced in: {', '.join(flow_files)}")

            if missing_script in self.existing_alternatives:
                alternatives = self.existing_alternatives[missing_script]
                print(f"   ✅ Alternatives found:")
                for alt in alternatives:
                    print(f"      - {alt}")

                # Suggest the best alternative
                best_alt = self._select_best_alternative(missing_script, alternatives)
                if best_alt:
                    print(f"   🎯 Recommended: {best_alt}")
                    self.flow_updates_needed.append(
                        {
                            "missing": missing_script,
                            "replacement": best_alt,
                            "flow_files": flow_files,
                        }
                    )
            else:
                print(f"   ⚠️  No alternatives found - script may need to be created")

    def _select_best_alternative(
        self, missing_script: str, alternatives: List[str]
    ) -> str:
        """Select the best alternative script based on naming patterns and location."""
        if not alternatives:
            return ""

        # Priority order: exact match > tools/ directory > api/ directory > others
        for alt in alternatives:
            if (
                missing_script.split("/")[-1] == alt.split("/")[-1]
            ):  # Exact filename match
                return alt

        for alt in alternatives:
            if alt.startswith("tools/"):
                return alt

        for alt in alternatives:
            if alt.startswith("api/"):
                return alt

        return alternatives[0]  # Return first as fallback

    def generate_update_script(self) -> None:
        """Generate a script to update Node-RED flows with correct paths."""
        if not self.flow_updates_needed:
            return

        script_content = """#!/bin/bash
# Auto-generated Node-RED flow update script

echo "🔄 Updating Node-RED flows with correct script paths..."

"""

        for update in self.flow_updates_needed:
            missing = update["missing"]
            replacement = update["replacement"]

            # Generate sed commands to replace paths
            script_content += f"""
# Replace {missing} with {replacement}
find node-red docker/node-red -name "*.json" -type f -exec sed -i 's|{missing}|{replacement}|g' {{}} \\;
"""

        script_content += """
echo "✅ Node-RED flows updated successfully!"
echo "ℹ️  Please restart Node-RED to apply changes"
"""

        script_path = self.base_path / "fix_node_red_paths.sh"
        with open(script_path, "w") as f:
            f.write(script_content)

        os.chmod(script_path, 0o755)
        print(f"\n📝 Update script created: {script_path}")

    def run_analysis(self) -> None:
        """Run the complete analysis and generate recommendations."""
        print("🔍 Analyzing Node-RED flows for Python script references...")
        self.analyze_flows()
        self.suggest_fixes()
        self.generate_update_script()

        # Summary
        print(f"\n📋 SUMMARY:")
        print(f"   Missing scripts: {len(self.missing_scripts)}")
        print(f"   Updates needed: {len(self.flow_updates_needed)}")
        print(f"   Alternatives found: {len(self.existing_alternatives)}")

        if self.flow_updates_needed:
            print(f"\n🚀 Next steps:")
            print(f"   1. Review the recommended alternatives above")
            print(f"   2. Run: ./fix_node_red_paths.sh (if alternatives look good)")
            print(f"   3. Test Node-RED flows after updates")


if __name__ == "__main__":
    fixer = NodeRedScriptFixer()
    fixer.run_analysis()
