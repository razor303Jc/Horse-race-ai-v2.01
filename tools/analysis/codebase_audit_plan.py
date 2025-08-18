#!/usr/bin/env python3
"""
🔍 Codebase Audit & Cleanup Plan
=================================

Comprehensive analysis tool to identify:
- Active files used by the system
- Deprecated/unused files
- Import dependencies
- File relationships
- Cleanup recommendations

This will help optimize the Horse Racing AI v2.0 codebase.
"""

import ast
import json
import logging
import os
import re
import sys
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


class CodebaseAuditor:
    """Comprehensive codebase analysis and cleanup planning"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.active_files = set()
        self.unused_files = set()
        self.import_graph = defaultdict(set)
        self.file_dependencies = defaultdict(set)
        self.file_sizes = {}
        self.file_ages = {}
        self.python_files = set()
        self.config_files = set()
        self.docker_files = set()
        self.documentation_files = set()
        self.data_files = set()
        self.test_files = set()
        self.demo_files = set()
        self.legacy_files = set()

        # Key entry points for the system
        self.entry_points = [
            "integrated_auto_pipeline.py",
            "pipeline_comprehensive_fixes.py",
            "simple_form_analyzer.py",
            "start_dev.sh",
            "startup-optimized.sh",
            "run_reports_docker.sh",
            "Makefile",
            "docker-compose.yml",
            "docker-compose.optimized.yml",
            "docker-compose.auto-downloader.yml",
        ]

        # Directories to analyze
        self.core_directories = ["src", "api", "tools", "scripts", "config", "database"]

        # Directories that may contain unused files
        self.potential_cleanup_dirs = [
            "demos",
            "experiments",
            "legacy",
            "cleanup_temp",
            "tests",
        ]

    def scan_codebase(self):
        """Perform comprehensive codebase scan"""

        print("🔍 CODEBASE AUDIT & CLEANUP PLAN")
        print("=" * 40)
        print("🏇 Horse Racing AI v2.0 - File Analysis")
        print()

        # Phase 1: Discover all files
        print("📁 Phase 1: File Discovery...")
        self._discover_all_files()

        # Phase 2: Analyze imports and dependencies
        print("🔗 Phase 2: Dependency Analysis...")
        self._analyze_dependencies()

        # Phase 3: Trace active files from entry points
        print("🎯 Phase 3: Active File Tracing...")
        self._trace_active_files()

        # Phase 4: Identify unused files
        print("🗑️  Phase 4: Unused File Identification...")
        self._identify_unused_files()

        # Phase 5: Generate cleanup recommendations
        print("📋 Phase 5: Cleanup Recommendations...")
        self._generate_recommendations()

        # Phase 6: Create detailed report
        print("📊 Phase 6: Report Generation...")
        self._generate_audit_report()

        print("✅ Codebase audit completed!")

    def _discover_all_files(self):
        """Discover and categorize all files in the workspace"""

        for root, dirs, files in os.walk(self.workspace_root):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d not in ["__pycache__", "node_modules"]
            ]

            for file in files:
                if file.startswith("."):
                    continue

                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.workspace_root)

                # Store file metadata
                try:
                    stat = file_path.stat()
                    self.file_sizes[str(relative_path)] = stat.st_size
                    self.file_ages[str(relative_path)] = stat.st_mtime
                except:
                    continue

                # Categorize files by type
                self._categorize_file(relative_path)

    def _categorize_file(self, file_path: Path):
        """Categorize file by type and purpose"""

        file_str = str(file_path)
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()

        # Python files
        if suffix == ".py":
            self.python_files.add(file_str)

            # Check for specific categories
            if "demo" in file_str or file_str.startswith("demos/"):
                self.demo_files.add(file_str)
            elif "test" in file_str or file_str.startswith("tests/"):
                self.test_files.add(file_str)
            elif "legacy" in file_str or file_str.startswith("legacy/"):
                self.legacy_files.add(file_str)

        # Configuration files
        elif suffix in [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"]:
            self.config_files.add(file_str)

        # Docker files
        elif (
            "dockerfile" in name
            or "docker-compose" in name
            or suffix == ".dockerignore"
        ):
            self.docker_files.add(file_str)

        # Documentation files
        elif suffix in [".md", ".rst", ".txt"] or name == "readme":
            self.documentation_files.add(file_str)

        # Data files
        elif suffix in [".csv", ".json", ".sql", ".db"]:
            if not file_str.startswith("config/"):
                self.data_files.add(file_str)

    def _analyze_dependencies(self):
        """Analyze import dependencies between Python files"""

        for python_file in self.python_files:
            file_path = self.workspace_root / python_file
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse imports using AST
                try:
                    tree = ast.parse(content)
                    imports = self._extract_imports(tree, python_file)
                    self.import_graph[python_file] = imports
                except SyntaxError:
                    # Handle files with syntax errors
                    imports = self._extract_imports_regex(content, python_file)
                    self.import_graph[python_file] = imports

            except Exception as e:
                logger.warning(f"Could not analyze {python_file}: {e}")

    def _extract_imports(self, tree: ast.AST, file_path: str) -> Set[str]:
        """Extract imports from AST"""

        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)

        # Convert external imports to local file paths
        local_imports = set()
        for imp in imports:
            local_file = self._resolve_import_to_file(imp, file_path)
            if local_file:
                local_imports.add(local_file)

        return local_imports

    def _extract_imports_regex(self, content: str, file_path: str) -> Set[str]:
        """Extract imports using regex as fallback"""

        imports = set()

        # Match import statements
        import_patterns = [
            r"^\s*import\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
            r"^\s*from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import",
        ]

        for line in content.split("\n"):
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    imports.add(match.group(1))

        # Convert to local file paths
        local_imports = set()
        for imp in imports:
            local_file = self._resolve_import_to_file(imp, file_path)
            if local_file:
                local_imports.add(local_file)

        return local_imports

    def _resolve_import_to_file(self, import_name: str, importing_file: str) -> str:
        """Resolve import name to actual file path"""

        # Skip standard library and external packages
        if import_name in [
            "os",
            "sys",
            "json",
            "datetime",
            "pathlib",
            "logging",
            "pandas",
            "numpy",
            "matplotlib",
            "sqlite3",
            "psycopg2",
        ]:
            return None

        # Try various resolution strategies
        possible_paths = []

        # Direct module import
        possible_paths.append(f"{import_name.replace('.', '/')}.py")
        possible_paths.append(f"{import_name.replace('.', '/')}/__init__.py")

        # Relative imports from same directory
        importing_dir = str(Path(importing_file).parent)
        if importing_dir != ".":
            possible_paths.append(f"{importing_dir}/{import_name.replace('.', '/')}.py")
            possible_paths.append(
                f"{importing_dir}/{import_name.replace('.', '/')}/__init__.py"
            )

        # Check src/ directory
        possible_paths.append(f"src/{import_name.replace('.', '/')}.py")
        possible_paths.append(f"src/{import_name.replace('.', '/')}/__init__.py")

        # Find matching file
        for path in possible_paths:
            if path in self.python_files:
                return path

        return None

    def _trace_active_files(self):
        """Trace all files that are actively used starting from entry points"""

        # Start with entry points
        to_process = deque()

        for entry_point in self.entry_points:
            if (
                entry_point in self.python_files
                or (self.workspace_root / entry_point).exists()
            ):
                to_process.append(entry_point)
                self.active_files.add(entry_point)

        # Breadth-first search through dependencies
        while to_process:
            current_file = to_process.popleft()

            # Add Python dependencies
            if current_file in self.import_graph:
                for dependency in self.import_graph[current_file]:
                    if dependency not in self.active_files:
                        self.active_files.add(dependency)
                        to_process.append(dependency)

            # Add configuration and data file dependencies
            self._add_file_dependencies(current_file)

    def _add_file_dependencies(self, file_path: str):
        """Add non-Python file dependencies (config, data files, etc.)"""

        if file_path not in self.python_files:
            return

        try:
            full_path = self.workspace_root / file_path
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for file references in strings
            file_patterns = [
                r'["\']([^"\']*\.(?:json|yaml|yml|csv|sql|txt))["\']',
                r'["\']([^"\']*config[^"\']*)["\']',
                r'Path\(["\']([^"\']+)["\']',
                r'open\(["\']([^"\']+)["\']',
            ]

            for pattern in file_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Resolve relative paths
                    potential_file = self._resolve_file_reference(match, file_path)
                    if potential_file and potential_file not in self.active_files:
                        self.active_files.add(potential_file)

        except Exception as e:
            logger.warning(f"Could not analyze file references in {file_path}: {e}")

    def _resolve_file_reference(self, file_ref: str, context_file: str) -> str:
        """Resolve file reference to actual file path"""

        # Try different resolution strategies
        possible_paths = [file_ref, str(Path(context_file).parent / file_ref)]

        for path in possible_paths:
            if (self.workspace_root / path).exists():
                return str(Path(path))

        return None

    def _identify_unused_files(self):
        """Identify files that are not actively used"""

        all_files = set()

        # Collect all files
        for file_set in [
            self.python_files,
            self.config_files,
            self.docker_files,
            self.documentation_files,
            self.data_files,
        ]:
            all_files.update(file_set)

        # Find unused files
        self.unused_files = all_files - self.active_files

        # Always consider these as potentially active
        always_active = {
            "README.md",
            "requirements.txt",
            "pyproject.toml",
            "pytest.ini",
            ".gitignore",
            "horse-racing-ai.code-workspace",
        }

        for file in always_active:
            if file in self.unused_files:
                self.unused_files.remove(file)
                self.active_files.add(file)

    def _generate_recommendations(self):
        """Generate cleanup recommendations"""

        self.recommendations = {
            "safe_to_remove": [],
            "review_required": [],
            "keep_active": [],
            "archive_candidates": [],
        }

        for file in self.unused_files:
            file_path = Path(file)

            # Safe to remove: obvious temporary/generated files
            if any(
                pattern in str(file_path)
                for pattern in [
                    "temp",
                    "tmp",
                    ".bak",
                    ".old",
                    "__pycache__",
                    ".pyc",
                    ".log",
                    "backup",
                ]
            ):
                self.recommendations["safe_to_remove"].append(file)

            # Archive candidates: demos, experiments, legacy
            elif any(
                dir_name in str(file_path)
                for dir_name in ["demos", "experiments", "legacy", "cleanup_temp"]
            ):
                self.recommendations["archive_candidates"].append(file)

            # Review required: everything else
            else:
                self.recommendations["review_required"].append(file)

        # Active files to keep
        self.recommendations["keep_active"] = list(self.active_files)

    def _generate_audit_report(self):
        """Generate comprehensive audit report"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create reports directory
        reports_dir = Path("tools/analysis/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Generate detailed report
        report_data = {
            "audit_timestamp": timestamp,
            "summary": {
                "total_files": len(self.python_files)
                + len(self.config_files)
                + len(self.docker_files)
                + len(self.documentation_files)
                + len(self.data_files),
                "python_files": len(self.python_files),
                "active_files": len(self.active_files),
                "unused_files": len(self.unused_files),
                "safe_to_remove": len(self.recommendations["safe_to_remove"]),
                "archive_candidates": len(self.recommendations["archive_candidates"]),
                "review_required": len(self.recommendations["review_required"]),
            },
            "file_categories": {
                "python_files": list(self.python_files),
                "config_files": list(self.config_files),
                "docker_files": list(self.docker_files),
                "documentation_files": list(self.documentation_files),
                "data_files": list(self.data_files),
                "test_files": list(self.test_files),
                "demo_files": list(self.demo_files),
                "legacy_files": list(self.legacy_files),
            },
            "active_files": list(self.active_files),
            "unused_files": list(self.unused_files),
            "recommendations": self.recommendations,
            "import_graph": {k: list(v) for k, v in self.import_graph.items()},
        }

        # Save JSON report
        json_report = reports_dir / f"codebase_audit_{timestamp}.json"
        with open(json_report, "w") as f:
            json.dump(report_data, f, indent=2)

        # Generate HTML report
        html_report = self._generate_html_report(report_data, timestamp)
        html_file = reports_dir / f"codebase_audit_{timestamp}.html"
        with open(html_file, "w") as f:
            f.write(html_report)

        # Generate cleanup script
        cleanup_script = self._generate_cleanup_script()
        script_file = reports_dir / f"cleanup_script_{timestamp}.sh"
        with open(script_file, "w") as f:
            f.write(cleanup_script)

        print(f"📄 JSON Report: {json_report}")
        print(f"🌐 HTML Report: {html_file}")
        print(f"🧹 Cleanup Script: {script_file}")

        return report_data

    def _generate_html_report(self, data: Dict, timestamp: str) -> str:
        """Generate HTML audit report"""

        summary = data["summary"]

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Codebase Audit Report - Horse Racing AI v2.0</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        .header {{ text-align: center; background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 30px; }}
        .stat-card {{ background: #3498db; color: white; padding: 15px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 1.8em; font-weight: bold; }}
        .stat-label {{ font-size: 0.9em; opacity: 0.9; }}
        .section {{ margin-bottom: 30px; }}
        .section-header {{ background: #34495e; color: white; padding: 10px 15px; border-radius: 5px; margin-bottom: 15px; }}
        .file-list {{ background: #f8f9fa; padding: 15px; border-radius: 5px; max-height: 300px; overflow-y: auto; }}
        .file-item {{ margin: 2px 0; font-family: monospace; font-size: 0.9em; }}
        .recommendation {{ padding: 15px; margin-bottom: 15px; border-radius: 5px; }}
        .safe-remove {{ background: #d4edda; border-left: 4px solid #28a745; }}
        .review-required {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
        .archive {{ background: #cce7ff; border-left: 4px solid #007bff; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Codebase Audit Report</h1>
            <p>Horse Racing AI v2.0 - File Usage Analysis</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{summary['total_files']}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['active_files']}</div>
                <div class="stat-label">Active Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['unused_files']}</div>
                <div class="stat-label">Unused Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['safe_to_remove']}</div>
                <div class="stat-label">Safe to Remove</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['archive_candidates']}</div>
                <div class="stat-label">Archive Candidates</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">📊 File Categories</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">
                <div>
                    <h4>🐍 Python Files ({len(data['file_categories']['python_files'])})</h4>
                    <div class="file-list">
                        {"<br>".join(data['file_categories']['python_files'][:20])}
                        {f"<br>... and {len(data['file_categories']['python_files']) - 20} more" if len(data['file_categories']['python_files']) > 20 else ""}
                    </div>
                </div>
                <div>
                    <h4>⚙️ Config Files ({len(data['file_categories']['config_files'])})</h4>
                    <div class="file-list">
                        {"<br>".join(data['file_categories']['config_files'])}
                    </div>
                </div>
                <div>
                    <h4>🐳 Docker Files ({len(data['file_categories']['docker_files'])})</h4>
                    <div class="file-list">
                        {"<br>".join(data['file_categories']['docker_files'])}
                    </div>
                </div>
                <div>
                    <h4>📚 Documentation ({len(data['file_categories']['documentation_files'])})</h4>
                    <div class="file-list">
                        {"<br>".join(data['file_categories']['documentation_files'])}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">🧹 Cleanup Recommendations</div>
            
            <div class="recommendation safe-remove">
                <h4>✅ Safe to Remove ({len(data['recommendations']['safe_to_remove'])} files)</h4>
                <p>These files can be safely deleted without affecting system functionality:</p>
                <div class="file-list">
                    {"<br>".join(data['recommendations']['safe_to_remove'])}
                </div>
            </div>
            
            <div class="recommendation archive">
                <h4>📦 Archive Candidates ({len(data['recommendations']['archive_candidates'])} files)</h4>
                <p>These files can be moved to an archive directory:</p>
                <div class="file-list">
                    {"<br>".join(data['recommendations']['archive_candidates'][:20])}
                    {f"<br>... and {len(data['recommendations']['archive_candidates']) - 20} more" if len(data['recommendations']['archive_candidates']) > 20 else ""}
                </div>
            </div>
            
            <div class="recommendation review-required">
                <h4>⚠️ Review Required ({len(data['recommendations']['review_required'])} files)</h4>
                <p>These files need manual review before cleanup:</p>
                <div class="file-list">
                    {"<br>".join(data['recommendations']['review_required'][:20])}
                    {f"<br>... and {len(data['recommendations']['review_required']) - 20} more" if len(data['recommendations']['review_required']) > 20 else ""}
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">✅ Active Files</div>
            <p>Files that are actively used by the system ({len(data['active_files'])} files):</p>
            <div class="file-list">
                {"<br>".join(sorted(data['active_files'])[:30])}
                {f"<br>... and {len(data['active_files']) - 30} more" if len(data['active_files']) > 30 else ""}
            </div>
        </div>
    </div>
</body>
</html>
        """

        return html

    def _generate_cleanup_script(self) -> str:
        """Generate automated cleanup script"""

        script = """#!/bin/bash
# Automated Codebase Cleanup Script
# Generated by Horse Racing AI v2.0 Codebase Auditor

echo "🧹 Starting Automated Codebase Cleanup..."
echo "=" * 40

# Create backup directory
backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"

# Create archive directory
archive_dir="archived_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$archive_dir"

echo "📦 Created backup directory: $backup_dir"
echo "📁 Created archive directory: $archive_dir"

# Function to safely remove files
safe_remove() {
    local file="$1"
    if [ -f "$file" ]; then
        echo "🗑️  Removing: $file"
        mv "$file" "$backup_dir/"
    fi
}

# Function to archive files
archive_file() {
    local file="$1"
    if [ -f "$file" ]; then
        echo "📦 Archiving: $file"
        mkdir -p "$archive_dir/$(dirname "$file")"
        mv "$file" "$archive_dir/$file"
    fi
}

echo
echo "🗑️  Removing safe-to-delete files..."
"""

        # Add safe removal commands
        for file in self.recommendations["safe_to_remove"]:
            script += f'safe_remove "{file}"\n'

        script += '\necho\necho "📦 Archiving demo and legacy files..."\n'

        # Add archive commands
        for file in self.recommendations["archive_candidates"]:
            script += f'archive_file "{file}"\n'

        script += """
echo
echo "✅ Cleanup completed!"
echo "📊 Summary:"
echo "   - Backup directory: $backup_dir"
echo "   - Archive directory: $archive_dir"
echo "   - Review required files listed in audit report"
echo
echo "⚠️  Manual review recommended before permanent deletion"
"""

        return script

    def print_summary(self):
        """Print summary of audit results"""

        print()
        print("📊 CODEBASE AUDIT SUMMARY")
        print("=" * 30)
        print(
            f"📁 Total Files Analyzed: {len(self.python_files) + len(self.config_files) + len(self.docker_files) + len(self.documentation_files) + len(self.data_files)}"
        )
        print(f"🐍 Python Files: {len(self.python_files)}")
        print(f"⚙️  Config Files: {len(self.config_files)}")
        print(f"🐳 Docker Files: {len(self.docker_files)}")
        print(f"📚 Documentation: {len(self.documentation_files)}")
        print(f"📊 Data Files: {len(self.data_files)}")
        print()
        print(f"✅ Active Files: {len(self.active_files)}")
        print(f"🗑️  Unused Files: {len(self.unused_files)}")
        print()
        print("🧹 CLEANUP RECOMMENDATIONS:")
        print(
            f"   ✅ Safe to Remove: {len(self.recommendations['safe_to_remove'])} files"
        )
        print(
            f"   📦 Archive Candidates: {len(self.recommendations['archive_candidates'])} files"
        )
        print(
            f"   ⚠️  Review Required: {len(self.recommendations['review_required'])} files"
        )
        print()


def main():
    """Main function"""

    workspace_root = "/home/jc/Documents/Horse-race-ai-v2.02"

    print("🔍 HORSE RACING AI v2.0 - CODEBASE AUDIT")
    print("=" * 50)
    print()

    try:
        auditor = CodebaseAuditor(workspace_root)
        auditor.scan_codebase()
        auditor.print_summary()

        print("📋 Next Steps:")
        print("1. Review the generated HTML report")
        print("2. Examine files marked for review")
        print("3. Run the cleanup script when ready")
        print("4. Archive demo/legacy files")
        print()

    except Exception as e:
        logger.error(f"Audit failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
