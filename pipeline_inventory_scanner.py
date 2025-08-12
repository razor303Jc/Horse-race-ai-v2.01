#!/usr/bin/env python3
"""
🔍 Pipeline Component Inventory Scanner
Analyzes all files in demos, experiments, and legacy directories to create detailed inventory
"""

import ast
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class ComponentInventoryScanner:
    """Scans and analyzes pipeline components."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.inventory = {
            "scan_date": datetime.now().isoformat(),
            "directories": {},
            "recommendations": {},
        }

    def scan_directory(self, directory: str) -> Dict:
        """Scan a directory and analyze Python files."""
        dir_path = self.project_root / directory
        if not dir_path.exists():
            return {}

        dir_info = {
            "path": str(dir_path),
            "files": {},
            "summary": {
                "total_files": 0,
                "python_files": 0,
                "disabled_files": 0,
                "production_ready": 0,
                "test_files": 0,
            },
        }

        for file_path in dir_path.rglob("*.py"):
            if file_path.is_file():
                file_info = self.analyze_file(file_path)
                relative_path = file_path.relative_to(dir_path)
                dir_info["files"][str(relative_path)] = file_info

                # Update summary
                dir_info["summary"]["total_files"] += 1
                if file_path.suffix == ".py":
                    dir_info["summary"]["python_files"] += 1
                if "disabled" in file_path.name or file_path.name.endswith(".disabled"):
                    dir_info["summary"]["disabled_files"] += 1
                if any(
                    keyword in file_path.name.lower()
                    for keyword in ["production", "final", "complete"]
                ):
                    dir_info["summary"]["production_ready"] += 1
                if any(
                    keyword in file_path.name.lower()
                    for keyword in ["test", "quick", "simple", "demo"]
                ):
                    dir_info["summary"]["test_files"] += 1

        return dir_info

    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a Python file for key information."""
        file_info = {
            "name": file_path.name,
            "size_kb": round(file_path.stat().st_size / 1024, 2),
            "last_modified": datetime.fromtimestamp(
                file_path.stat().st_mtime
            ).isoformat(),
            "functions": [],
            "classes": [],
            "imports": [],
            "docstring": "",
            "complexity_score": 0,
            "recommendation": "unknown",
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST for detailed analysis
            try:
                tree = ast.parse(content)
                file_info.update(self.extract_ast_info(tree))
            except:
                pass

            # Extract docstring
            lines = content.split("\n")
            if len(lines) > 0 and ('"""' in lines[0] or "'''" in lines[0]):
                docstring_lines = []
                in_docstring = False
                for line in lines[:20]:  # Check first 20 lines
                    if '"""' in line or "'''" in line:
                        if in_docstring:
                            break
                        in_docstring = True
                        docstring_lines.append(line.strip())
                    elif in_docstring:
                        docstring_lines.append(line.strip())
                file_info["docstring"] = " ".join(docstring_lines)[:200]

            # Determine recommendation
            file_info["recommendation"] = self.determine_recommendation(
                file_path, file_info
            )

        except Exception as e:
            file_info["error"] = str(e)

        return file_info

    def extract_ast_info(self, tree: ast.AST) -> Dict:
        """Extract information from AST."""
        info = {"functions": [], "classes": [], "imports": [], "complexity_score": 0}

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                info["functions"].append(node.name)
                info["complexity_score"] += 1
            elif isinstance(node, ast.ClassDef):
                info["classes"].append(node.name)
                info["complexity_score"] += 2
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    info["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    info["imports"].append(node.module)

        return info

    def determine_recommendation(self, file_path: Path, file_info: Dict) -> str:
        """Determine recommendation for file."""
        name = file_path.name.lower()

        # Disabled files
        if "disabled" in name or name.endswith(".disabled"):
            return "REMOVE - Disabled"

        # Test/development files
        if any(keyword in name for keyword in ["test", "quick", "simple", "demo"]):
            if any(
                keyword in name for keyword in ["final", "complete", "comprehensive"]
            ):
                return "KEEP - Important demo"
            return "REMOVE - Test/Development"

        # Production files
        if any(
            keyword in name
            for keyword in ["production", "final", "complete", "comprehensive"]
        ):
            return "KEEP - Production ready"

        # Legacy files
        if "legacy" in str(file_path):
            return "ARCHIVE - Legacy code"

        # ML/Training files
        if any(
            keyword in name for keyword in ["ml", "training", "model", "prediction"]
        ):
            if file_info["complexity_score"] > 10:
                return "KEEP - Complex ML system"
            return "CONSOLIDATE - Merge with main ML system"

        # Pipeline files
        if any(
            keyword in name for keyword in ["pipeline", "orchestrator", "scheduler"]
        ):
            return "KEEP - Pipeline component"

        # Auto-downloaders
        if "auto" in name and "download" in name:
            if "enhanced" in name or "playwright" in name:
                return "REMOVE - Superseded"
            return "KEEP - Core functionality"

        return "REVIEW - Manual assessment needed"

    def generate_recommendations(self):
        """Generate overall recommendations."""
        total_files = sum(
            dir_info["summary"]["total_files"]
            for dir_info in self.inventory["directories"].values()
        )

        keep_files = []
        remove_files = []
        consolidate_files = []
        archive_files = []

        for dir_name, dir_info in self.inventory["directories"].items():
            for file_name, file_info in dir_info["files"].items():
                full_path = f"{dir_name}/{file_name}"
                recommendation = file_info["recommendation"]

                if recommendation.startswith("KEEP"):
                    keep_files.append(full_path)
                elif recommendation.startswith("REMOVE"):
                    remove_files.append(full_path)
                elif recommendation.startswith("CONSOLIDATE"):
                    consolidate_files.append(full_path)
                elif recommendation.startswith("ARCHIVE"):
                    archive_files.append(full_path)

        self.inventory["recommendations"] = {
            "summary": {
                "total_files": total_files,
                "keep": len(keep_files),
                "remove": len(remove_files),
                "consolidate": len(consolidate_files),
                "archive": len(archive_files),
            },
            "actions": {
                "keep": keep_files,
                "remove": remove_files,
                "consolidate": consolidate_files,
                "archive": archive_files,
            },
            "cleanup_commands": self.generate_cleanup_commands(
                remove_files, archive_files
            ),
        }

    def generate_cleanup_commands(
        self, remove_files: List[str], archive_files: List[str]
    ) -> Dict:
        """Generate shell commands for cleanup."""
        commands = {
            "remove_disabled": [
                "find demos/ -name '*.disabled' -delete",
                "find experiments/ -name '*.disabled' -delete",
            ],
            "remove_test_files": [],
            "archive_legacy": [
                "mkdir -p archive/legacy",
                "mv legacy/* archive/legacy/",
                "rmdir legacy",
            ],
            "consolidate_ml": [
                "# Review and merge ML training files",
                "# experiments/enhanced_ml_trainer.py (keep)",
                "# + experiments/ml_training_pipeline.py (merge)",
                "# + experiments/production_cyclic_training.py (merge)",
            ],
        }

        # Add specific remove commands
        for file_path in remove_files:
            if "test" in file_path or "quick" in file_path or "simple" in file_path:
                commands["remove_test_files"].append(f"rm {file_path}")

        return commands

    def run_full_scan(self):
        """Run complete inventory scan."""
        print("🔍 Starting Pipeline Component Inventory Scan...")

        # Scan directories
        directories = ["demos", "experiments", "legacy"]

        for directory in directories:
            print(f"📁 Scanning {directory}/...")
            self.inventory["directories"][directory] = self.scan_directory(directory)

        # Generate recommendations
        print("🎯 Generating recommendations...")
        self.generate_recommendations()

        # Save inventory
        inventory_file = self.project_root / "PIPELINE_INVENTORY.json"
        with open(inventory_file, "w") as f:
            json.dump(self.inventory, f, indent=2)

        print(f"✅ Inventory saved to: {inventory_file}")

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print inventory summary."""
        print("\n" + "=" * 60)
        print("📊 PIPELINE COMPONENT INVENTORY SUMMARY")
        print("=" * 60)

        for dir_name, dir_info in self.inventory["directories"].items():
            summary = dir_info["summary"]
            print(f"\n📁 {dir_name.upper()}/")
            print(f"   Total files: {summary['total_files']}")
            print(f"   Python files: {summary['python_files']}")
            print(f"   Disabled files: {summary['disabled_files']}")
            print(f"   Production ready: {summary['production_ready']}")
            print(f"   Test files: {summary['test_files']}")

        rec = self.inventory["recommendations"]["summary"]
        print(f"\n🎯 RECOMMENDATIONS SUMMARY")
        print(f"   KEEP: {rec['keep']} files")
        print(f"   REMOVE: {rec['remove']} files")
        print(f"   CONSOLIDATE: {rec['consolidate']} files")
        print(f"   ARCHIVE: {rec['archive']} files")

        print(f"\n💾 Potential space saved: ~{rec['remove'] + rec['archive']} files")
        print(
            f"📈 Pipeline efficiency gain: ~{(rec['remove'] + rec['archive']) / rec['total_files'] * 100:.1f}%"
        )


def main():
    """Main entry point."""
    scanner = ComponentInventoryScanner()
    scanner.run_full_scan()


if __name__ == "__main__":
    main()
