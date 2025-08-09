#!/usr/bin/env python3
"""
AI-Powered Project Organizer using Qwen2.5-Coder
================================================
Analyzes project structure and automatically organizes files into proper directories.
"""

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


class ProjectOrganizer:
    """AI-powered project organization using Qwen2.5-Coder."""

    def __init__(self, project_root="/home/jc/Documents/Horse-race-ai-v2.01"):
        self.project_root = Path(project_root)
        self.coder_model = "qwen2.5-coder:7b"
        self.backup_dir = (
            self.project_root
            / "archive"
            / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

    def query_coder(self, prompt, timeout=300):
        """Query Qwen2.5-Coder for organization decisions."""
        try:
            result = subprocess.run(
                ["ollama", "run", self.coder_model],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"

    def analyze_project_structure(self):
        """Analyze current project structure and get AI recommendations."""
        print("🔍 ANALYZING PROJECT STRUCTURE WITH QWEN2.5-CODER")
        print("=" * 60)

        # Get current directory structure
        structure = self._get_directory_structure()

        prompt = f"""Analyze this Python project structure and provide organization recommendations:

CURRENT PROJECT STRUCTURE:
{structure}

PROJECT TYPE: Horse Racing AI System with:
- Flask web application
- Machine learning models 
- Database integration
- Docker containers
- Analysis scripts
- Testing framework

PROVIDE JSON RESPONSE WITH:
{{
    "file_moves": [
        {{"source": "filename.py", "destination": "proper/directory/", "reason": "explanation"}},
    ],
    "directories_to_create": [
        {{"path": "new/directory", "purpose": "what it contains"}}
    ],
    "files_to_archive": [
        {{"file": "old_file.py", "reason": "why it should be archived"}}
    ],
    "cleanup_actions": [
        {{"action": "remove duplicates", "files": ["file1", "file2"]}},
        {{"action": "rename", "from": "old_name", "to": "new_name"}}
    ]
}}

Focus on:
1. Moving AI scripts to appropriate directories
2. Organizing documentation files
3. Separating test files from main code
4. Creating logical directory structure
5. Archiving unused/old files
6. Following Python project best practices"""

        response = self.query_coder(prompt)
        print("🤖 AI ANALYSIS COMPLETE")
        print(response)
        return response

    def _get_directory_structure(self):
        """Get current directory structure as text."""
        structure = []

        # Get root level files
        for item in sorted(self.project_root.iterdir()):
            if item.name.startswith("."):
                continue
            if item.is_file():
                size = item.stat().st_size
                modified = datetime.fromtimestamp(item.stat().st_mtime).strftime(
                    "%Y-%m-%d"
                )
                structure.append(
                    f"FILE: {item.name} ({size} bytes, modified: {modified})"
                )
            elif item.is_dir():
                structure.append(f"DIR:  {item.name}/")

        return "\\n".join(structure)

    def execute_organization_plan(self, plan_json):
        """Execute the AI-generated organization plan."""
        print("\\n🚀 EXECUTING AI ORGANIZATION PLAN")
        print("=" * 50)

        try:
            plan = json.loads(plan_json) if isinstance(plan_json, str) else plan_json
        except:
            print("❌ Could not parse AI plan. Executing manual organization...")
            self.manual_organization()
            return

        # Create backup
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"📦 Created backup directory: {self.backup_dir}")

        # Create new directories
        if "directories_to_create" in plan:
            for dir_info in plan["directories_to_create"]:
                new_dir = self.project_root / dir_info["path"]
                new_dir.mkdir(parents=True, exist_ok=True)
                print(f"📁 Created: {dir_info['path']} - {dir_info['purpose']}")

        # Archive old files
        if "files_to_archive" in plan:
            for file_info in plan["files_to_archive"]:
                self._archive_file(file_info["file"], file_info["reason"])

        # Move files to proper locations
        if "file_moves" in plan:
            for move_info in plan["file_moves"]:
                self._move_file(
                    move_info["source"], move_info["destination"], move_info["reason"]
                )

        # Execute cleanup actions
        if "cleanup_actions" in plan:
            for action in plan["cleanup_actions"]:
                self._execute_cleanup_action(action)

        print("\\n✅ PROJECT ORGANIZATION COMPLETE!")

    def _archive_file(self, filename, reason):
        """Archive a file with backup."""
        source = self.project_root / filename
        if source.exists():
            dest = self.backup_dir / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            source.unlink()
            print(f"📦 Archived: {filename} - {reason}")

    def _move_file(self, source_name, dest_dir, reason):
        """Move file to new directory."""
        source = self.project_root / source_name
        dest_path = self.project_root / dest_dir
        dest_path.mkdir(parents=True, exist_ok=True)

        if source.exists():
            dest_file = dest_path / source.name
            shutil.move(str(source), str(dest_file))
            print(f"📁 Moved: {source_name} → {dest_dir} - {reason}")

    def _execute_cleanup_action(self, action):
        """Execute specific cleanup action."""
        if action["action"] == "remove duplicates":
            for filename in action["files"]:
                file_path = self.project_root / filename
                if file_path.exists():
                    self._archive_file(filename, "Duplicate file cleanup")
        elif action["action"] == "rename":
            old_path = self.project_root / action["from"]
            new_path = self.project_root / action["to"]
            if old_path.exists():
                old_path.rename(new_path)
                print(f"✏️ Renamed: {action['from']} → {action['to']}")

    def manual_organization(self):
        """Fallback manual organization if AI plan fails."""
        print("🔧 EXECUTING MANUAL ORGANIZATION...")

        # Create standard directories
        directories = {
            "src/ai_models": "AI model implementations",
            "src/analyzers": "Analysis and prediction scripts",
            "src/web": "Web application components",
            "src/utils": "Utility functions",
            "tests/ai_models": "AI model tests",
            "tests/integration": "Integration tests",
            "docs/ai": "AI documentation",
            "docs/api": "API documentation",
            "scripts/ai": "AI utility scripts",
            "scripts/setup": "Setup and deployment scripts",
        }

        for dir_path, purpose in directories.items():
            (self.project_root / dir_path).mkdir(parents=True, exist_ok=True)
            print(f"📁 Created: {dir_path} - {purpose}")

        # Move AI files
        ai_files = [
            ("ai_code_analyzer.py", "src/ai_models/"),
            ("ai_betting_bot.py", "src/ai_models/"),
            ("ai_racing_commentator.py", "src/ai_models/"),
            ("ai_form_analyzer.py", "src/ai_models/"),
            ("test_ollama_models.py", "tests/ai_models/"),
            ("quick_ollama_test.py", "tests/ai_models/"),
        ]

        for source, dest in ai_files:
            self._move_file(source, dest, "AI model organization")

        # Move analysis scripts
        analysis_files = [
            ("racing_media_analyzer.py", "src/analyzers/"),
            ("dynamic_racing_analyzer.py", "src/analyzers/"),
            ("background_racing_analyzer.py", "src/analyzers/"),
        ]

        for source, dest in analysis_files:
            self._move_file(source, dest, "Analysis script organization")

        # Move web files
        web_files = [
            ("webapp_racing_interface.py", "src/web/"),
            ("flask_racing_integration.py", "src/web/"),
        ]

        for source, dest in web_files:
            self._move_file(source, dest, "Web component organization")

        # Archive old files
        old_files = [
            "ai_form_analyzer_fixed.py",
            "simple_whiterabbit_test.py",
            "quick_racing_test.py",
        ]

        for filename in old_files:
            self._archive_file(filename, "Old/temporary file cleanup")

    def create_project_summary(self):
        """Create a summary of the organized project structure."""
        print("\\n📋 CREATING PROJECT SUMMARY")
        print("=" * 40)

        prompt = f"""Create a comprehensive project summary for this organized horse racing AI system:

ORGANIZED STRUCTURE:
{self._get_directory_structure()}

Create a detailed README section that explains:
1. Project architecture overview
2. Directory structure and purpose
3. Key AI components and their roles
4. How to navigate the codebase
5. Development workflow
6. File organization rationale

Format as markdown with clear sections and descriptions."""

        response = self.query_coder(prompt)

        # Save summary
        summary_file = self.project_root / "PROJECT_STRUCTURE.md"
        with open(summary_file, "w") as f:
            f.write(response)

        print(f"📄 Project summary saved to: {summary_file.name}")
        return response


def main():
    """Run the AI project organizer."""
    print("🤖 AI-POWERED PROJECT ORGANIZER")
    print("Using Qwen2.5-Coder for Intelligent File Organization")
    print("=" * 60)

    organizer = ProjectOrganizer()

    print("What would you like to do?")
    print("1. Analyze project structure")
    print("2. Execute full AI organization")
    print("3. Manual organization")
    print("4. Create project summary")
    print("5. Complete reorganization (AI + Summary)")

    choice = input("\\nEnter choice (1-5): ").strip()

    if choice == "1":
        organizer.analyze_project_structure()
    elif choice == "2":
        plan = organizer.analyze_project_structure()
        organizer.execute_organization_plan(plan)
    elif choice == "3":
        organizer.manual_organization()
    elif choice == "4":
        organizer.create_project_summary()
    elif choice == "5":
        print("🚀 COMPLETE PROJECT REORGANIZATION")
        print("=" * 40)
        plan = organizer.analyze_project_structure()
        organizer.execute_organization_plan(plan)
        organizer.create_project_summary()
    else:
        print("Invalid choice. Running analysis...")
        organizer.analyze_project_structure()


if __name__ == "__main__":
    main()
