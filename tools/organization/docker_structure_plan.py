#!/usr/bin/env python3
"""
🐳 Docker Structure Organization Plan
=====================================

Comprehensive plan to organize files into proper Docker structure
before implementing comprehensive test framework.

Analysis of current root directory and recommendations for clean organization.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set


class DockerStructureOrganizer:
    """Organize files into proper Docker-friendly structure"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.organization_plan = {}
        self.files_to_move = {}
        self.files_to_keep_root = set()
        self.files_to_remove = set()

    def analyze_current_structure(self):
        """Analyze current file structure and create organization plan"""

        print("🐳 DOCKER STRUCTURE ORGANIZATION PLAN")
        print("=" * 45)
        print("🏇 Horse Racing AI v2.0 - File Organization Analysis")
        print()

        # Scan root directory
        root_files = []
        for item in self.workspace_root.iterdir():
            if item.is_file():
                root_files.append(item.name)

        print(f"📁 Current root directory contains {len(root_files)} files")
        print()

        # Categorize files
        self._categorize_root_files(root_files)

        # Create organization plan
        self._create_organization_plan()

        # Generate recommendations
        self._generate_recommendations()

        print("✅ Analysis complete! Organization plan generated.")

    def _categorize_root_files(self, files: List[str]):
        """Categorize files in root directory"""

        categories = {
            "essential_root": [],
            "docker_files": [],
            "python_scripts": [],
            "shell_scripts": [],
            "config_files": [],
            "documentation": [],
            "test_files": [],
            "temporary_files": [],
            "deployment_files": [],
        }

        for file in files:
            file_lower = file.lower()

            # Essential root files (must stay in root)
            if file in [
                "README.md",
                "Makefile",
                "pyproject.toml",
                "pytest.ini",
                ".gitignore",
                ".env",
                ".flake8",
                "horse-racing-ai.code-workspace",
            ]:
                categories["essential_root"].append(file)
                self.files_to_keep_root.add(file)

            # Docker files
            elif file.startswith("Dockerfile") or file.startswith("docker-compose"):
                categories["docker_files"].append(file)
                self.files_to_keep_root.add(file)

            # Python scripts (should be organized)
            elif file.endswith(".py"):
                categories["python_scripts"].append(file)

            # Shell scripts (should be organized)
            elif file.endswith(".sh"):
                categories["shell_scripts"].append(file)

            # Configuration files
            elif file.endswith((".yml", ".yaml", ".json", ".ini", ".cfg", ".toml")):
                if file not in self.files_to_keep_root:
                    categories["config_files"].append(file)

            # Documentation files
            elif file.endswith((".md", ".txt", ".rst")):
                if file not in self.files_to_keep_root:
                    categories["documentation"].append(file)

            # Test files
            elif file.startswith("test_"):
                categories["test_files"].append(file)

            # Temporary/cache files
            elif any(
                temp in file_lower for temp in ["temp", "cache", "__pycache__", ".pyc"]
            ):
                categories["temporary_files"].append(file)
                self.files_to_remove.add(file)

        self.file_categories = categories

        print("📊 FILE CATEGORIZATION:")
        print("=" * 25)
        for category, files in categories.items():
            if files:
                print(f"📋 {category.replace('_', ' ').title()}: {len(files)} files")
                for file in files[:5]:  # Show first 5
                    print(f"   • {file}")
                if len(files) > 5:
                    print(f"   ... and {len(files) - 5} more")
        print()

    def _create_organization_plan(self):
        """Create detailed organization plan"""

        self.organization_plan = {
            "scripts/": {
                "description": "Organize Python and shell scripts",
                "target_files": [],
                "subdirectories": {
                    "automation/": "Automation scripts",
                    "deployment/": "Deployment scripts",
                    "maintenance/": "Maintenance scripts",
                    "testing/": "Testing scripts",
                    "pipeline/": "Pipeline scripts",
                },
            },
            "docker/scripts/": {
                "description": "Docker-specific scripts",
                "target_files": [],
                "move_from_root": True,
            },
            "docs/": {
                "description": "Centralize all documentation",
                "target_files": [],
                "merge_with_existing": True,
            },
            "config/": {
                "description": "Configuration files",
                "target_files": [],
                "merge_with_existing": True,
            },
            "tests/": {
                "description": "Test files organization",
                "target_files": [],
                "merge_with_existing": True,
            },
        }

        # Categorize files for organization
        for file in self.file_categories["python_scripts"]:
            self._categorize_python_script(file)

        for file in self.file_categories["shell_scripts"]:
            self._categorize_shell_script(file)

        for file in self.file_categories["documentation"]:
            self.organization_plan["docs/"]["target_files"].append(file)

        for file in self.file_categories["config_files"]:
            self.organization_plan["config/"]["target_files"].append(file)

        for file in self.file_categories["test_files"]:
            self.organization_plan["tests/"]["target_files"].append(file)

    def _categorize_python_script(self, filename: str):
        """Categorize Python scripts for organization"""

        file_lower = filename.lower()

        # Pipeline scripts
        if any(
            keyword in file_lower
            for keyword in ["pipeline", "integrated_auto", "comprehensive_fixes"]
        ):
            self.organization_plan["scripts/"]["target_files"].append(
                {
                    "file": filename,
                    "destination": "scripts/pipeline/",
                    "reason": "Pipeline management script",
                }
            )

        # Automation scripts
        elif any(
            keyword in file_lower
            for keyword in ["auto", "launcher", "monitor", "process", "upload"]
        ):
            self.organization_plan["scripts/"]["target_files"].append(
                {
                    "file": filename,
                    "destination": "scripts/automation/",
                    "reason": "Automation script",
                }
            )

        # Deployment scripts
        elif any(
            keyword in file_lower
            for keyword in ["deploy", "container", "docker", "startup", "validate"]
        ):
            self.organization_plan["scripts/"]["target_files"].append(
                {
                    "file": filename,
                    "destination": "scripts/deployment/",
                    "reason": "Deployment script",
                }
            )

        # Testing scripts
        elif any(
            keyword in file_lower for keyword in ["test", "debug", "check", "verify"]
        ):
            self.organization_plan["scripts/"]["target_files"].append(
                {
                    "file": filename,
                    "destination": "scripts/testing/",
                    "reason": "Testing script",
                }
            )

        # Maintenance scripts
        elif any(
            keyword in file_lower
            for keyword in ["fix", "clean", "manage", "status", "health"]
        ):
            self.organization_plan["scripts/"]["target_files"].append(
                {
                    "file": filename,
                    "destination": "scripts/maintenance/",
                    "reason": "Maintenance script",
                }
            )

        # Data management
        elif any(
            keyword in file_lower
            for keyword in ["data", "csv", "schema", "db", "database"]
        ):
            self.organization_plan["scripts/"]["target_files"].append(
                {
                    "file": filename,
                    "destination": "scripts/automation/",
                    "reason": "Data management script",
                }
            )

        # Default to automation
        else:
            self.organization_plan["scripts/"]["target_files"].append(
                {
                    "file": filename,
                    "destination": "scripts/automation/",
                    "reason": "General automation script",
                }
            )

    def _categorize_shell_script(self, filename: str):
        """Categorize shell scripts for organization"""

        file_lower = filename.lower()

        if any(
            keyword in file_lower
            for keyword in ["deploy", "start", "startup", "docker", "service"]
        ):
            self.organization_plan["docker/scripts/"]["target_files"].append(
                {
                    "file": filename,
                    "destination": "docker/scripts/",
                    "reason": "Docker deployment script",
                }
            )
        else:
            self.organization_plan["scripts/"]["target_files"].append(
                {
                    "file": filename,
                    "destination": "scripts/automation/",
                    "reason": "General shell script",
                }
            )

    def _generate_recommendations(self):
        """Generate detailed recommendations"""

        print("📋 ORGANIZATION RECOMMENDATIONS")
        print("=" * 32)

        for target_dir, info in self.organization_plan.items():
            if info["target_files"]:
                print(f"\n📁 {target_dir}")
                print(f"   Purpose: {info['description']}")

                # Count files by destination
                if isinstance(info["target_files"][0], dict):
                    destinations = {}
                    for file_info in info["target_files"]:
                        dest = file_info["destination"]
                        if dest not in destinations:
                            destinations[dest] = []
                        destinations[dest].append(file_info["file"])

                    for dest, files in destinations.items():
                        print(f"   📂 {dest}: {len(files)} files")
                        for file in files[:3]:
                            print(f"      • {file}")
                        if len(files) > 3:
                            print(f"      ... and {len(files) - 3} more")
                else:
                    print(f"   Files to move: {len(info['target_files'])}")
                    for file in info["target_files"][:3]:
                        print(f"      • {file}")
                    if len(info["target_files"]) > 3:
                        print(f"      ... and {len(info['target_files']) - 3} more")

        print(f"\n✅ Files to keep in root: {len(self.files_to_keep_root)}")
        print(f"🗑️  Files to remove: {len(self.files_to_remove)}")

        # Generate summary statistics
        total_to_move = 0
        for info in self.organization_plan.values():
            total_to_move += len(info["target_files"])

        print(f"\n📊 SUMMARY:")
        print(f"   Total files to organize: {total_to_move}")
        print(f"   Target directories: {len(self.organization_plan)}")
        print(f"   Files staying in root: {len(self.files_to_keep_root)}")
        print(f"   Files to cleanup: {len(self.files_to_remove)}")

    def generate_organization_script(self):
        """Generate automated organization script"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create scripts directory if it doesn't exist
        scripts_dir = Path("tools/organization")
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_content = f"""#!/bin/bash
# Docker Structure Organization Script
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo "🐳 Starting Docker Structure Organization..."
echo "=" * 50

# Create backup
backup_dir="backup_before_organization_{timestamp}"
echo "📦 Creating backup: $backup_dir"
mkdir -p "$backup_dir"

# Function to safely move files
safe_move() {{
    local source="$1"
    local destination="$2"
    local reason="$3"
    
    if [ -f "$source" ]; then
        echo "📂 Moving $source -> $destination ($reason)"
        mkdir -p "$(dirname "$destination")"
        cp "$source" "$backup_dir/"
        mv "$source" "$destination"
    else
        echo "⚠️  Warning: $source not found"
    fi
}}

# Function to create directory structure
create_dirs() {{
    echo "📁 Creating directory structure..."
"""

        # Add directory creation
        for target_dir, info in self.organization_plan.items():
            script_content += f'    mkdir -p "{target_dir}"\n'
            if "subdirectories" in info:
                for subdir in info["subdirectories"].keys():
                    script_content += f'    mkdir -p "scripts/{subdir}"\n'

        script_content += '}\n\n# Create directories\ncreate_dirs\n\necho\necho "📂 Moving files..."\n'

        # Add file moves
        for target_dir, info in self.organization_plan.items():
            if info["target_files"]:
                script_content += f"\n# Moving files to {target_dir}\n"

                if isinstance(info["target_files"][0], dict):
                    for file_info in info["target_files"]:
                        file = file_info["file"]
                        dest = file_info["destination"] + file
                        reason = file_info["reason"]
                        script_content += f'safe_move "{file}" "{dest}" "{reason}"\n'
                else:
                    for file in info["target_files"]:
                        dest = target_dir + file
                        script_content += (
                            f'safe_move "{file}" "{dest}" "Documentation file"\n'
                        )

        # Add cleanup
        script_content += f"""
echo
echo "🗑️  Cleaning up temporary files..."
"""

        for file in self.files_to_remove:
            script_content += f'rm -f "{file}"\n'

        script_content += """
echo
echo "✅ Organization completed!"
echo "📊 Summary:"
echo "   - Backup created: $backup_dir"
echo "   - Files organized into proper Docker structure"
echo "   - Ready for comprehensive testing"
echo
echo "🧪 Next steps:"
echo "   1. Review organized structure"
echo "   2. Update import paths if needed" 
echo "   3. Run comprehensive test suite"
echo "   4. Update Docker configurations"
"""

        # Save script
        script_file = scripts_dir / f"organize_docker_structure_{timestamp}.sh"
        with open(script_file, "w") as f:
            f.write(script_content)

        # Make executable
        os.chmod(script_file, 0o755)

        # Generate organization report
        report_data = {
            "timestamp": timestamp,
            "organization_plan": self.organization_plan,
            "files_to_keep_root": list(self.files_to_keep_root),
            "files_to_remove": list(self.files_to_remove),
            "file_categories": self.file_categories,
        }

        report_file = scripts_dir / f"organization_plan_{timestamp}.json"
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📜 Organization script: {script_file}")
        print(f"📋 Organization plan: {report_file}")

        return script_file, report_file

    def generate_test_framework_plan(self):
        """Generate plan for comprehensive test framework"""

        test_plan = {
            "test_categories": {
                "unit_tests": {
                    "description": "Test individual components",
                    "target_modules": [
                        "src/horse_racing_ai/",
                        "tools/monitoring/",
                        "tools/analysis/",
                        "scripts/pipeline/",
                        "scripts/automation/",
                    ],
                    "test_files": [
                        "tests/unit/test_pipeline_components.py",
                        "tests/unit/test_monitoring_system.py",
                        "tests/unit/test_ml_models.py",
                        "tests/unit/test_betting_strategies.py",
                        "tests/unit/test_data_processing.py",
                    ],
                },
                "integration_tests": {
                    "description": "Test component interactions",
                    "test_files": [
                        "tests/integration/test_pipeline_integration.py",
                        "tests/integration/test_database_integration.py",
                        "tests/integration/test_docker_services.py",
                        "tests/integration/test_ml_pipeline.py",
                        "tests/integration/test_reporting_system.py",
                    ],
                },
                "system_tests": {
                    "description": "End-to-end system testing",
                    "test_files": [
                        "tests/system/test_complete_pipeline.py",
                        "tests/system/test_betting_workflow.py",
                        "tests/system/test_performance.py",
                        "tests/system/test_error_handling.py",
                    ],
                },
                "docker_tests": {
                    "description": "Docker and deployment testing",
                    "test_files": [
                        "tests/docker/test_container_health.py",
                        "tests/docker/test_service_connectivity.py",
                        "tests/docker/test_data_persistence.py",
                        "tests/docker/test_scaling.py",
                    ],
                },
            },
            "test_infrastructure": {
                "fixtures": "tests/fixtures/",
                "mock_data": "tests/data/",
                "test_configs": "tests/configs/",
                "utilities": "tests/utils/",
            },
            "coverage_targets": {
                "minimum_coverage": "80%",
                "critical_modules": "95%",
                "ml_models": "90%",
                "betting_strategies": "95%",
            },
        }

        print("\n🧪 COMPREHENSIVE TEST FRAMEWORK PLAN")
        print("=" * 40)

        for category, info in test_plan["test_categories"].items():
            print(f"\n📋 {category.replace('_', ' ').title()}")
            print(f"   Purpose: {info['description']}")
            print(f"   Test files: {len(info['test_files'])}")
            for test_file in info["test_files"]:
                print(f"      • {test_file}")

        print(f"\n📊 Coverage Targets:")
        for target, percentage in test_plan["coverage_targets"].items():
            print(f"   • {target.replace('_', ' ').title()}: {percentage}")

        return test_plan


def main():
    """Main function"""

    workspace_root = "/home/jc/Documents/Horse-race-ai-v2.02"

    print("🐳 HORSE RACING AI v2.0 - DOCKER STRUCTURE ORGANIZATION")
    print("=" * 65)
    print()

    try:
        organizer = DockerStructureOrganizer(workspace_root)
        organizer.analyze_current_structure()

        script_file, report_file = organizer.generate_organization_script()
        test_plan = organizer.generate_test_framework_plan()

        print("\n🎯 READY FOR NEXT PHASE:")
        print("=" * 25)
        print("1. ✅ Structure analysis completed")
        print("2. 📜 Organization script generated")
        print("3. 🧪 Test framework plan created")
        print("4. 🐳 Docker structure ready for optimization")
        print()
        print("Execute the organization script when ready:")
        print(f"   bash {script_file}")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
