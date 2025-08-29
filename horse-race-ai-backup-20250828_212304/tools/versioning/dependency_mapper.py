#!/usr/bin/env python3
"""
🔍 Horse Racing AI - Project Dependency Mapper
Analyzes import relationships and creates dependency graphs

This tool:
1. Scans all Python files for import statements
2. Maps dependencies between files
3. Identifies entry points and critical paths
4. Detects unused files and circular dependencies
5. Generates visual dependency graphs

Author: AI Assistant
Date: August 26, 2025
Version: 1.0.0
"""

import ast
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime

try:
    import networkx as nx
    import matplotlib.pyplot as plt

    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False


class DependencyMapper:
    """Maps and analyzes project file dependencies"""

    def __init__(self, project_root: Optional[str] = None):
        default_root = "/home/jc/Documents/Horse-race-ai-v2.04"
        self.project_root = Path(project_root or default_root)
        self.dependencies = {}  # file -> [dependencies]
        self.reverse_dependencies = {}  # file -> [files that depend on it]
        self.imports = {}  # file -> [import statements]
        self.entry_points = set()
        self.python_files = []

        # Output paths
        self.output_dir = self.project_root / "data" / "audit"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scan_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        print("📁 Scanning for Python files...")

        python_files = []
        exclude_dirs = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".venv",
            "venv",
            "node_modules",
        }

        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.project_root)
                    python_files.append(relative_path)

        self.python_files = python_files
        print(f"✅ Found {len(python_files)} Python files")
        return python_files

    def parse_imports(self, file_path: Path) -> List[str]:
        """Parse import statements from a Python file"""
        try:
            with open(self.project_root / file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        for alias in node.names:
                            imports.append(f"{node.module}.{alias.name}")

            return imports

        except Exception as e:
            print(f"⚠️ Error parsing {file_path}: {e}")
            return []

    def resolve_local_imports(
        self, imports: List[str], current_file: Path
    ) -> List[Path]:
        """Resolve imports to actual local project files"""
        local_deps = []

        for imp in imports:
            # Skip standard library and external packages
            if self.is_external_import(imp):
                continue

            # Try to resolve to project files
            resolved = self.resolve_import_to_file(imp, current_file)
            if resolved:
                local_deps.append(resolved)

        return local_deps

    def is_external_import(self, import_name: str) -> bool:
        """Check if import is external (not project code)"""
        external_packages = {
            "os",
            "sys",
            "json",
            "datetime",
            "pathlib",
            "typing",
            "logging",
            "asyncio",
            "aiohttp",
            "requests",
            "pandas",
            "numpy",
            "sklearn",
            "matplotlib",
            "seaborn",
            "psycopg2",
            "sqlalchemy",
            "redis",
            "click",
            "rich",
            "pydantic",
            "playwright",
            "beautifulsoup4",
            "xgboost",
            "lightgbm",
            "joblib",
            "gunicorn",
            "flask",
            "fastapi",
        }

        # Check if it's a standard library or known external package
        return any(import_name.startswith(pkg) for pkg in external_packages)

    def resolve_import_to_file(
        self, import_name: str, current_file: Path
    ) -> Optional[Path]:
        """Try to resolve import to actual project file"""
        # Handle relative imports
        if import_name.startswith("."):
            base_dir = current_file.parent
            import_parts = import_name.lstrip(".").split(".")
        else:
            base_dir = self.project_root
            import_parts = import_name.split(".")

        # Try different file patterns
        possible_files = [
            base_dir / (("/".join(import_parts)) + ".py"),
            base_dir / ("/".join(import_parts)) / "__init__.py",
        ]

        for possible_file in possible_files:
            if possible_file.exists():
                try:
                    return possible_file.relative_to(self.project_root)
                except ValueError:
                    continue

        return None

    def build_dependency_graph(self):
        """Build the complete dependency graph"""
        print("🔗 Building dependency graph...")

        for file_path in self.python_files:
            print(f"  📄 Processing {file_path}")

            # Parse imports
            imports = self.parse_imports(file_path)
            self.imports[str(file_path)] = imports

            # Resolve to local files
            local_deps = self.resolve_local_imports(imports, file_path)
            self.dependencies[str(file_path)] = [str(dep) for dep in local_deps]

            # Build reverse dependencies
            for dep in local_deps:
                dep_str = str(dep)
                if dep_str not in self.reverse_dependencies:
                    self.reverse_dependencies[dep_str] = []
                self.reverse_dependencies[dep_str].append(str(file_path))

        print(f"✅ Dependency graph built with {len(self.dependencies)} files")

    def identify_entry_points(self) -> Set[str]:
        """Identify entry points (files that run as main)"""
        print("🚪 Identifying entry points...")

        entry_points = set()

        for file_path in self.python_files:
            try:
                with open(self.project_root / file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for if __name__ == "__main__":
                if 'if __name__ == "__main__"' in content:
                    entry_points.add(str(file_path))

                # Check for main() function
                if "def main(" in content:
                    entry_points.add(str(file_path))

            except Exception as e:
                continue

        # Add known entry points from shell scripts
        shell_scripts = [
            "start_daily_watcher.sh",
            "start_pipeline_integration.sh",
            "process_manual_data.py",
            "upload_race_data.py",
        ]

        for script in shell_scripts:
            script_path = self.project_root / script
            if script_path.exists() and script.endswith(".py"):
                entry_points.add(script)

        self.entry_points = entry_points
        print(f"✅ Found {len(entry_points)} entry points")
        return entry_points

    def find_unused_files(self) -> Set[str]:
        """Find files that are not imported by anyone"""
        print("🗑️ Finding unused files...")

        imported_files = set()
        for deps in self.dependencies.values():
            imported_files.update(deps)

        all_files = set(str(f) for f in self.python_files)
        unused_files = all_files - imported_files - self.entry_points

        print(f"✅ Found {len(unused_files)} potentially unused files")
        return unused_files

    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies using graph analysis"""
        print("🔄 Detecting circular dependencies...")

        # Create networkx graph
        G = nx.DiGraph()

        for file, deps in self.dependencies.items():
            for dep in deps:
                G.add_edge(file, dep)

        # Find strongly connected components (cycles)
        cycles = []
        try:
            strongly_connected = nx.strongly_connected_components(G)
            for component in strongly_connected:
                if len(component) > 1:  # Only cycles with more than 1 node
                    cycles.append(list(component))
        except Exception as e:
            print(f"⚠️ Error detecting cycles: {e}")

        print(f"✅ Found {len(cycles)} circular dependencies")
        return cycles

    def calculate_complexity_metrics(self) -> Dict:
        """Calculate various complexity metrics"""
        print("📊 Calculating complexity metrics...")

        metrics = {
            "total_files": len(self.python_files),
            "total_dependencies": sum(len(deps) for deps in self.dependencies.values()),
            "avg_dependencies_per_file": 0,
            "max_dependencies": 0,
            "most_dependent_file": "",
            "max_dependents": 0,
            "most_depended_on_file": "",
            "orphaned_files": 0,
            "entry_points": len(self.entry_points),
        }

        if self.dependencies:
            deps_lengths = [len(deps) for deps in self.dependencies.values()]
            metrics["avg_dependencies_per_file"] = sum(deps_lengths) / len(deps_lengths)

            max_deps = max(deps_lengths)
            metrics["max_dependencies"] = max_deps
            for file, deps in self.dependencies.items():
                if len(deps) == max_deps:
                    metrics["most_dependent_file"] = file
                    break

        if self.reverse_dependencies:
            reverse_lengths = [len(deps) for deps in self.reverse_dependencies.values()]
            max_reverse = max(reverse_lengths) if reverse_lengths else 0
            metrics["max_dependents"] = max_reverse
            for file, deps in self.reverse_dependencies.items():
                if len(deps) == max_reverse:
                    metrics["most_depended_on_file"] = file
                    break

        # Count orphaned files (no dependencies and no dependents)
        orphaned = 0
        for file in self.python_files:
            file_str = str(file)
            has_deps = len(self.dependencies.get(file_str, [])) > 0
            has_dependents = len(self.reverse_dependencies.get(file_str, [])) > 0
            if (
                not has_deps
                and not has_dependents
                and file_str not in self.entry_points
            ):
                orphaned += 1

        metrics["orphaned_files"] = orphaned

        print("✅ Complexity metrics calculated")
        return metrics

    def generate_reports(self):
        """Generate comprehensive analysis reports"""
        print("📝 Generating analysis reports...")

        # 1. Dependency report
        dependency_report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "total_files": len(self.python_files),
            "dependencies": self.dependencies,
            "reverse_dependencies": self.reverse_dependencies,
            "imports": self.imports,
            "entry_points": list(self.entry_points),
        }

        # Save dependency data
        with open(self.output_dir / "dependency_graph.json", "w") as f:
            json.dump(dependency_report, f, indent=2)

        # 2. Analysis report
        unused_files = self.find_unused_files()
        circular_deps = self.detect_circular_dependencies()
        metrics = self.calculate_complexity_metrics()

        analysis_report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "unused_files": list(unused_files),
            "circular_dependencies": circular_deps,
            "entry_points": list(self.entry_points),
            "recommendations": self.generate_recommendations(
                unused_files, circular_deps, metrics
            ),
        }

        with open(self.output_dir / "analysis_report.json", "w") as f:
            json.dump(analysis_report, f, indent=2)

        # 3. Human-readable summary
        self.generate_summary_report(metrics, unused_files, circular_deps)

        print("✅ Reports generated in data/audit/")

    def generate_recommendations(
        self, unused_files: Set[str], circular_deps: List, metrics: Dict
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if unused_files:
            recommendations.append(
                f"🗑️ Consider removing {len(unused_files)} unused files to reduce clutter"
            )

        if circular_deps:
            recommendations.append(
                f"🔄 Resolve {len(circular_deps)} circular dependencies to improve maintainability"
            )

        if metrics["orphaned_files"] > 0:
            recommendations.append(
                f"🏝️ Review {metrics['orphaned_files']} orphaned files - may be safe to remove"
            )

        if metrics["max_dependencies"] > 20:
            recommendations.append(
                f"📦 File '{metrics['most_dependent_file']}' has {metrics['max_dependencies']} dependencies - consider refactoring"
            )

        if metrics["avg_dependencies_per_file"] > 10:
            recommendations.append(
                "🔗 High average dependencies per file - consider modularizing"
            )

        return recommendations

    def generate_summary_report(
        self, metrics: Dict, unused_files: Set[str], circular_deps: List
    ):
        """Generate human-readable summary report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        summary = f"""# 🔍 Dependency Analysis Summary
Generated: {timestamp}

## 📊 Project Overview
- **Total Python Files**: {metrics['total_files']}
- **Total Dependencies**: {metrics['total_dependencies']}
- **Average Dependencies per File**: {metrics['avg_dependencies_per_file']:.1f}
- **Entry Points**: {metrics['entry_points']}

## 🎯 Key Findings

### 📈 Complexity Metrics
- **Most Dependent File**: `{metrics['most_dependent_file']}` ({metrics['max_dependencies']} dependencies)
- **Most Depended On**: `{metrics['most_depended_on_file']}` ({metrics['max_dependents']} files depend on it)
- **Orphaned Files**: {metrics['orphaned_files']}

### 🗑️ Cleanup Opportunities
- **Unused Files**: {len(unused_files)} files not imported by any other file
- **Circular Dependencies**: {len(circular_deps)} detected

### 🚪 Entry Points
{chr(10).join(f"- `{ep}`" for ep in sorted(self.entry_points))}

## 🔄 Circular Dependencies
"""

        if circular_deps:
            for i, cycle in enumerate(circular_deps, 1):
                summary += f"\n### Cycle {i}:\n"
                summary += "\n".join(f"- `{file}`" for file in cycle)
        else:
            summary += "\n✅ No circular dependencies detected"

        summary += "\n\n## 🗑️ Potentially Unused Files\n"

        if unused_files:
            # Group by directory for better organization
            unused_by_dir = {}
            for file in sorted(unused_files):
                dir_name = str(Path(file).parent)
                if dir_name not in unused_by_dir:
                    unused_by_dir[dir_name] = []
                unused_by_dir[dir_name].append(Path(file).name)

            for dir_name, files in unused_by_dir.items():
                summary += f"\n### `{dir_name}/`\n"
                summary += "\n".join(f"- `{file}`" for file in files)
        else:
            summary += "\n✅ No unused files detected"

        summary += "\n\n## 💡 Recommendations\n"
        recommendations = self.generate_recommendations(
            unused_files, circular_deps, metrics
        )
        for rec in recommendations:
            summary += f"\n{rec}"

        # Save summary
        with open(self.output_dir / "summary_report.md", "w") as f:
            f.write(summary)

    def create_visual_graph(self, max_nodes: int = 50):
        """Create visual representation of dependency graph"""
        print("📈 Creating visual dependency graph...")

        try:
            import matplotlib.pyplot as plt
            import networkx as nx

            # Create graph with most connected files only
            G = nx.DiGraph()

            # Get most connected files
            file_connections = {}
            for file, deps in self.dependencies.items():
                file_connections[file] = len(deps) + len(
                    self.reverse_dependencies.get(file, [])
                )

            top_files = sorted(
                file_connections.items(), key=lambda x: x[1], reverse=True
            )[:max_nodes]
            top_file_names = {file for file, _ in top_files}

            # Add edges for top files only
            for file, deps in self.dependencies.items():
                if file in top_file_names:
                    for dep in deps:
                        if dep in top_file_names:
                            G.add_edge(file, dep)

            # Create visualization
            plt.figure(figsize=(20, 16))

            # Use spring layout for better visualization
            pos = nx.spring_layout(G, k=1, iterations=50)

            # Draw nodes
            node_colors = []
            for node in G.nodes():
                if node in self.entry_points:
                    node_colors.append("red")  # Entry points in red
                elif len(self.reverse_dependencies.get(node, [])) > 5:
                    node_colors.append("orange")  # Highly depended on in orange
                else:
                    node_colors.append("lightblue")  # Regular files in light blue

            nx.draw_networkx_nodes(
                G, pos, node_color=node_colors, node_size=300, alpha=0.8
            )
            nx.draw_networkx_edges(
                G, pos, edge_color="gray", arrows=True, alpha=0.6, arrowsize=10
            )

            # Add labels with shortened names
            labels = {}
            for node in G.nodes():
                # Shorten long paths for readability
                path_parts = Path(node).parts
                if len(path_parts) > 2:
                    labels[node] = f"{path_parts[-2]}/{path_parts[-1]}"
                else:
                    labels[node] = path_parts[-1]

            nx.draw_networkx_labels(G, pos, labels, font_size=8)

            plt.title(
                f"Dependency Graph - Top {len(G.nodes())} Connected Files\\n"
                + "🔴 Entry Points  🟠 Highly Depended On  🔵 Regular Files",
                fontsize=14,
            )
            plt.axis("off")
            plt.tight_layout()
            plt.savefig(
                self.output_dir / "dependency_graph.png", dpi=300, bbox_inches="tight"
            )
            plt.close()

            print("✅ Visual graph saved as dependency_graph.png")

        except ImportError:
            print("⚠️ matplotlib or networkx not available for visualization")
        except Exception as e:
            print(f"⚠️ Error creating visual graph: {e}")

    def run_complete_analysis(self):
        """Run the complete dependency analysis"""
        print("🚀 Starting Complete Dependency Analysis")
        print("=" * 60)

        # 1. Scan files
        self.scan_python_files()

        # 2. Build dependency graph
        self.build_dependency_graph()

        # 3. Identify entry points
        self.identify_entry_points()

        # 4. Generate reports
        self.generate_reports()

        # 5. Create visual graph
        self.create_visual_graph()

        print("\\n🎉 Analysis Complete!")
        print(f"📄 Reports saved in: {self.output_dir}")
        print("\\n📋 Next Steps:")
        print("1. Review summary_report.md for key findings")
        print("2. Check analysis_report.json for detailed data")
        print("3. Use findings to plan safe file cleanup")

        return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze project dependencies")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--output-dir", help="Output directory for reports")

    args = parser.parse_args()

    try:
        mapper = DependencyMapper(args.project_root)
        if args.output_dir:
            mapper.output_dir = Path(args.output_dir)
            mapper.output_dir.mkdir(parents=True, exist_ok=True)

        success = mapper.run_complete_analysis()
        return 0 if success else 1

    except KeyboardInterrupt:
        print("\\n🛑 Analysis interrupted by user")
        return 1
    except Exception as e:
        print(f"\\n❌ Analysis failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
