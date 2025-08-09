#!/usr/bin/env python3
"""
Horse Racing AI Project Scanner
Analyzes project structure and populates PostgreSQL database for AI models
"""

import os
import sys
import ast
import hashlib
import psycopg2
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class ProjectScanner:
    def __init__(self, project_path: str, db_name: str = "coding_models_db"):
        self.project_path = Path(project_path)
        self.db_name = db_name
        self.project_id = None
        self.conn = None

        # Supported file extensions
        self.code_extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".cs": "C#",
            ".php": "PHP",
            ".rb": "Ruby",
            ".go": "Go",
            ".rs": "Rust",
            ".sh": "Shell",
            ".sql": "SQL",
            ".html": "HTML",
            ".css": "CSS",
            ".json": "JSON",
            ".xml": "XML",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".md": "Markdown",
            ".txt": "Text",
            ".conf": "Config",
            ".ini": "Config",
            ".cfg": "Config",
            ".toml": "TOML",
            ".dockerfile": "Docker",
            ".makefile": "Makefile",
        }

        # Directories to skip
        self.skip_dirs = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            "dist",
            "build",
            ".eggs",
            "*.egg-info",
            ".tox",
            "cache",
            "logs",
            "models",
            "trained_models",
            "test_models",
        }

    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            # Use peer authentication with correct port
            return psycopg2.connect(database=self.db_name, user="jc", port=5435)
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return None

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file content"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return "unknown"

    def detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        ext = file_path.suffix.lower()
        if file_path.name.lower() in ["dockerfile", "makefile"]:
            return self.code_extensions.get("." + file_path.name.lower(), "Unknown")
        return self.code_extensions.get(ext, "Unknown")

    def calculate_complexity(self, content: str) -> int:
        """Simple complexity metric based on control structures"""
        try:
            tree = ast.parse(content)
            complexity = 0
            for node in ast.walk(tree):
                if isinstance(
                    node,
                    (
                        ast.If,
                        ast.For,
                        ast.While,
                        ast.Try,
                        ast.FunctionDef,
                        ast.ClassDef,
                    ),
                ):
                    complexity += 1
            return complexity
        except:
            return 0

    def extract_python_elements(self, file_path: Path) -> List[Dict]:
        """Extract classes, functions, etc. from Python files"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            elements = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    elements.append(
                        {
                            "name": node.name,
                            "type": "function",
                            "signature": f"def {node.name}(...)",
                            "docstring": ast.get_docstring(node) or "",
                            "start_line": node.lineno,
                            "end_line": getattr(node, "end_lineno", node.lineno),
                            "complexity_score": self.calculate_complexity(
                                ast.get_source_segment(content, node) or ""
                            ),
                        }
                    )
                elif isinstance(node, ast.ClassDef):
                    elements.append(
                        {
                            "name": node.name,
                            "type": "class",
                            "signature": f"class {node.name}:",
                            "docstring": ast.get_docstring(node) or "",
                            "start_line": node.lineno,
                            "end_line": getattr(node, "end_lineno", node.lineno),
                            "complexity_score": self.calculate_complexity(
                                ast.get_source_segment(content, node) or ""
                            ),
                        }
                    )

            return elements
        except:
            return []

    def extract_dependencies(self) -> List[Dict]:
        """Extract project dependencies from requirements.txt, pyproject.toml, etc."""
        dependencies = []

        # Check requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0]
                            dependencies.append(
                                {
                                    "name": pkg_name,
                                    "type": "pip",
                                    "source": "requirements.txt",
                                }
                            )
            except:
                pass

        # Check pyproject.toml
        pyproject_file = self.project_path / "pyproject.toml"
        if pyproject_file.exists():
            dependencies.append(
                {"name": "pyproject.toml", "type": "config", "source": "pyproject.toml"}
            )

        return dependencies

    def register_project(self):
        """Register project in database"""
        cursor = self.conn.cursor()

        project_data = {
            "name": self.project_path.name,
            "description": "Advanced ML system for horse racing predictions and betting",
            "language": "Python",
            "framework": "Machine Learning / Flask",
            "repository_url": "",
            "root_path": str(self.project_path.absolute()),
        }

        try:
            cursor.execute(
                """
                INSERT INTO projects (name, description, language, framework, repository_url, root_path)
                VALUES (%(name)s, %(description)s, %(language)s, %(framework)s, %(repository_url)s, %(root_path)s)
                ON CONFLICT (name) DO UPDATE SET
                    description = EXCLUDED.description,
                    language = EXCLUDED.language,
                    framework = EXCLUDED.framework,
                    repository_url = EXCLUDED.repository_url,
                    root_path = EXCLUDED.root_path
                RETURNING id
                """,
                project_data,
            )

            result = cursor.fetchone()
            if result:
                self.project_id = result[0]
                self.conn.commit()
                print(f"✅ Project registered with ID: {self.project_id}")
            else:
                print("❌ Failed to register project")
                return False

        except Exception as e:
            print(f"❌ Error registering project: {e}")
            self.conn.rollback()
            return False

        return True

    def scan_files(self):
        """Scan all files in the project"""
        if not self.project_id:
            return

        cursor = self.conn.cursor()
        file_count = 0

        for file_path in self.project_path.rglob("*"):
            # Skip directories and files in skip_dirs
            if file_path.is_dir():
                continue

            if any(skip_dir in file_path.parts for skip_dir in self.skip_dirs):
                continue

            try:
                if file_path.stat().st_size > 10 * 1024 * 1024:  # Skip files > 10MB
                    continue

                relative_path = file_path.relative_to(self.project_path)

                file_data = {
                    "project_id": self.project_id,
                    "file_path": str(relative_path),
                    "file_name": file_path.name,
                    "file_type": (
                        file_path.suffix[1:] if file_path.suffix else "unknown"
                    ),
                    "size_bytes": file_path.stat().st_size,
                    "language": self.detect_language(file_path),
                    "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime),
                    "content_hash": self.calculate_file_hash(file_path),
                }

                cursor.execute(
                    """
                    INSERT INTO files (project_id, file_path, file_name, file_type, size_bytes,
                                     language, last_modified, content_hash)
                    VALUES (%(project_id)s, %(file_path)s, %(file_name)s, %(file_type)s,
                           %(size_bytes)s, %(language)s, %(last_modified)s, %(content_hash)s)
                    ON CONFLICT (project_id, file_path) DO UPDATE SET
                        file_name = EXCLUDED.file_name,
                        file_type = EXCLUDED.file_type,
                        size_bytes = EXCLUDED.size_bytes,
                        language = EXCLUDED.language,
                        last_modified = EXCLUDED.last_modified,
                        content_hash = EXCLUDED.content_hash
                    RETURNING id
                    """,
                    file_data,
                )

                result = cursor.fetchone()
                if result:
                    file_id = result[0]
                    file_count += 1

                    # Extract code elements for Python files
                    if file_path.suffix == ".py":
                        elements = self.extract_python_elements(file_path)
                        for element in elements:
                            element["file_id"] = file_id

                            cursor.execute(
                                """
                                INSERT INTO code_elements (file_id, name, type, signature, docstring,
                                                         start_line, end_line, complexity_score)
                                VALUES (%(file_id)s, %(name)s, %(type)s, %(signature)s, %(docstring)s,
                                       %(start_line)s, %(end_line)s, %(complexity_score)s)
                                ON CONFLICT (file_id, name, type) DO UPDATE SET
                                    signature = EXCLUDED.signature,
                                    docstring = EXCLUDED.docstring,
                                    start_line = EXCLUDED.start_line,
                                    end_line = EXCLUDED.end_line,
                                    complexity_score = EXCLUDED.complexity_score
                                """,
                                element,
                            )

                if file_count % 50 == 0:
                    print(f"   📁 Processed {file_count} files...")
                    self.conn.commit()

            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
                continue

        # Store dependencies
        dependencies = self.extract_dependencies()
        for dep in dependencies:
            dep["project_id"] = self.project_id
            cursor.execute(
                """
                INSERT INTO dependencies (project_id, name, type, source)
                VALUES (%(project_id)s, %(name)s, %(type)s, %(source)s)
                ON CONFLICT (project_id, name) DO NOTHING
                """,
                dep,
            )

        self.conn.commit()
        print(f"✅ Processed {file_count} files and {len(dependencies)} dependencies")

    def print_summary(self):
        """Print scan summary"""
        if not self.project_id:
            return

        cursor = self.conn.cursor()

        # File count
        cursor.execute(
            "SELECT COUNT(*) FROM files WHERE project_id = %s", (self.project_id,)
        )
        file_count = cursor.fetchone()[0]

        # Code elements count
        cursor.execute(
            "SELECT COUNT(*) FROM code_elements ce JOIN files f ON ce.file_id = f.id WHERE f.project_id = %s",
            (self.project_id,),
        )
        elements_count = cursor.fetchone()[0]

        # Dependencies count
        cursor.execute(
            "SELECT COUNT(*) FROM dependencies WHERE project_id = %s",
            (self.project_id,),
        )
        deps_count = cursor.fetchone()[0]

        print(f"\n📊 Scan Summary:")
        print(f"   📁 Files: {file_count}")
        print(f"   🔧 Code Elements: {elements_count}")
        print(f"   📦 Dependencies: {deps_count}")
        print("✅ Scan complete!")

    def scan_project(self):
        """Main scanning method"""
        print(f"🔍 Scanning project: {self.project_path}")

        # Connect to database
        self.conn = self.connect_db()
        if not self.conn:
            return False

        try:
            # Register project
            if not self.register_project():
                return False

            # Scan files
            self.scan_files()

            # Print summary
            self.print_summary()

            return True

        except Exception as e:
            print(f"❌ Error during scan: {e}")
            if self.conn:
                self.conn.rollback()
            return False
        finally:
            if self.conn:
                self.conn.close()


def main():
    """Main function"""
    project_path = os.getcwd()

    scanner = ProjectScanner(project_path)

    if scanner.scan_project():
        print(f"\n🎯 Project scan results saved to database")
        print(f"💡 You can now use AI models with full project context!")
    else:
        print(f"\n❌ Scan failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
