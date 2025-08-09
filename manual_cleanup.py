#!/usr/bin/env python3
"""
Quick Manual Cleanup Helper
============================
Manual organization of obvious file movements while AI works.
"""

import shutil
from datetime import datetime
from pathlib import Path


def quick_cleanup():
    """Quick manual organization of obvious files."""
    project_root = Path("/home/jc/Documents/Horse-race-ai-v2.01")

    print("🧹 QUICK MANUAL CLEANUP")
    print("=" * 30)

    # Create backup timestamp
    backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Files that are clearly AI models
    ai_models = [
        "ai_code_analyzer.py",
        "ai_betting_bot.py",
        "ai_racing_commentator.py",
        "ai_form_analyzer.py",
        "ai_project_organizer.py",
    ]

    # Files that are clearly test/demo files
    test_files = [
        "test_ollama_models.py",
        "quick_ollama_test.py",
        "quick_racing_test.py",
        "simple_whiterabbit_test.py",
        "quick_lint_fixer.py",
    ]

    # Files that are clearly analysis scripts
    analysis_files = [
        "racing_media_analyzer.py",
        "dynamic_racing_analyzer.py",
        "background_racing_analyzer.py",
    ]

    # Files that are old/fixed versions
    archive_files = ["ai_form_analyzer_fixed.py"]

    # Create directories if they don't exist
    dirs_to_create = {
        "src/ai_models": "AI model implementations",
        "src/analyzers": "Analysis scripts",
        "tests/ollama": "Ollama model tests",
        "scripts/utils": "Utility scripts",
        "archive/old_versions": "Old file versions",
    }

    for dir_path, description in dirs_to_create.items():
        full_path = project_root / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created: {dir_path} - {description}")

    # Move AI model files
    for filename in ai_models:
        source = project_root / filename
        if source.exists():
            dest = project_root / "src/ai_models" / filename
            if not dest.exists():
                shutil.move(str(source), str(dest))
                print(f"🤖 Moved AI model: {filename} → src/ai_models/")

    # Move test files
    for filename in test_files:
        source = project_root / filename
        if source.exists():
            dest = project_root / "tests/ollama" / filename
            if not dest.exists():
                shutil.move(str(source), str(dest))
                print(f"🧪 Moved test: {filename} → tests/ollama/")

    # Move analysis files
    for filename in analysis_files:
        source = project_root / filename
        if source.exists():
            dest = project_root / "src/analyzers" / filename
            if not dest.exists():
                shutil.move(str(source), str(dest))
                print(f"📊 Moved analyzer: {filename} → src/analyzers/")

    # Archive old files
    for filename in archive_files:
        source = project_root / filename
        if source.exists():
            dest = project_root / "archive/old_versions" / filename
            if not dest.exists():
                shutil.move(str(source), str(dest))
                print(f"📦 Archived: {filename} → archive/old_versions/")

    print("\\n✅ Quick cleanup complete!")
    print("🤖 AI organizer is still working on comprehensive analysis...")


if __name__ == "__main__":
    quick_cleanup()
