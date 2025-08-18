#!/usr/bin/env python3
"""
Simple Horse Racing AI Project Scanner
"""

import os
import psycopg2
from pathlib import Path


def main():
    # Connect to database
    try:
        conn = psycopg2.connect(database="coding_models_db", user="jc", port=5435)
        cursor = conn.cursor()
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # Register project
    project_data = {
        "name": "Horse-race-ai-v2.01",
        "description": "Advanced ML system for horse racing predictions and betting",
        "language": "Python",
        "framework": "Machine Learning / Flask",
        "repository_url": "",
        "root_path": "/home/jc/Documents/Horse-race-ai-v2.01",
    }

    try:
        cursor.execute(
            """
            INSERT INTO projects (name, description, language, framework, repository_url, root_path)
            VALUES (%(name)s, %(description)s, %(language)s, %(framework)s, %(repository_url)s, %(root_path)s)
            RETURNING id
            """,
            project_data,
        )

        project_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Project registered with ID: {project_id}")

    except Exception as e:
        print(f"❌ Error registering project: {e}")
        conn.rollback()
        return

    # Count Python files
    project_path = Path("/home/jc/Documents/Horse-race-ai-v2.01")
    python_files = list(project_path.rglob("*.py"))

    # Filter out cache and build directories
    skip_dirs = {
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "cache",
        "logs",
    }
    python_files = [
        f
        for f in python_files
        if not any(skip_dir in f.parts for skip_dir in skip_dirs)
    ]

    print(f"📁 Found {len(python_files)} Python files to scan")

    # Process a sample of files
    sample_files = python_files[:50]  # Process first 50 files only

    for i, file_path in enumerate(sample_files):
        try:
            relative_path = file_path.relative_to(project_path)

            file_data = {
                "project_id": project_id,
                "file_path": str(relative_path),
                "file_name": file_path.name,
                "file_type": "py",
                "size_bytes": file_path.stat().st_size,
                "language": "Python",
                "last_modified": "2025-08-09 10:00:00",
                "content_hash": "sample_hash",
            }

            cursor.execute(
                """
                INSERT INTO files (project_id, file_path, file_name, file_type, size_bytes,
                                 language, last_modified, content_hash)
                VALUES (%(project_id)s, %(file_path)s, %(file_name)s, %(file_type)s,
                       %(size_bytes)s, %(language)s, %(last_modified)s, %(content_hash)s)
                """,
                file_data,
            )

            if (i + 1) % 10 == 0:
                print(f"   📁 Processed {i + 1} files...")
                conn.commit()

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            continue

    conn.commit()

    # Summary
    cursor.execute("SELECT COUNT(*) FROM files WHERE project_id = %s", (project_id,))
    file_count = cursor.fetchone()[0]

    print(f"\n✅ Successfully processed {file_count} files")
    print(f"🎯 Project data saved to database!")
    print(f"💡 You can now use AI models with project context!")

    conn.close()


if __name__ == "__main__":
    main()
