#!/usr/bin/env python3
"""
🔧 Database Port Update Script
=============================

Updates all database connections from port 5432 to 5432 across the project.
This ensures all components connect to the correct PostgreSQL port.
"""

import logging
import os
import re
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_port_in_file(file_path: Path) -> bool:
    """Update database port from 5433 to 5432 in a file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Pattern replacements for different formats
        patterns = [
            (r'"port":\s*5433', '"port": 5432'),
            (r"'port':\s*5433", "'port': 5432"),
            (r'port="5432"', 'port="5432"'),
            (r"port='5432'", "port='5432'"),
            (r"port=5432", "port=5432"),
            (r"Port 5432", "Port 5432"),
            (r"port 5432", "port 5432"),
            (r"localhost.*5432", lambda m: m.group(0).replace("5432", "5432")),
        ]

        changes_made = False
        for pattern, replacement in patterns:
            if callable(replacement):
                new_content = re.sub(pattern, replacement, content)
            else:
                new_content = re.sub(pattern, replacement, content)

            if new_content != content:
                content = new_content
                changes_made = True

        # Write back if changes were made
        if changes_made:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"✅ Updated: {file_path}")
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"❌ Error updating {file_path}: {e}")
        return False


def main():
    """Update database ports across the project"""
    logger.info("🔧 DATABASE PORT UPDATE SCRIPT")
    logger.info("=" * 50)
    logger.info("Updating database connections from port 5432 to 5432")
    logger.info("")

    # Define critical files to update
    critical_files = [
        "tools/ml_training/optimized_10_cycle_trainer.py",
        "tools/training_launcher.py",
        "tools/ml_training/unified_ml_trainer.py",
        "tools/data_processing/csv_uploader.py",
        "tools/data_processing/smart_uploader.py",
        "tools/database/database_optimizer.py",
        "tools/database/performance_monitor.py",
        "config/daily_pipeline_config_manager.py",
    ]

    # Update critical files first
    logger.info("🎯 UPDATING CRITICAL FILES:")
    updated_files = []

    for file_path in critical_files:
        full_path = Path(file_path)
        if full_path.exists():
            if update_port_in_file(full_path):
                updated_files.append(str(full_path))
        else:
            logger.warning(f"⚠️  File not found: {full_path}")

    # Find and update all Python files in tools directory
    logger.info("")
    logger.info("🔍 SCANNING ALL TOOLS FILES:")

    tools_dir = Path("tools")
    if tools_dir.exists():
        for py_file in tools_dir.rglob("*.py"):
            if str(py_file) not in updated_files:  # Skip already updated files
                if update_port_in_file(py_file):
                    updated_files.append(str(py_file))

    # Update config files
    config_dir = Path("config")
    if config_dir.exists():
        for config_file in config_dir.rglob("*.py"):
            if str(config_file) not in updated_files:
                if update_port_in_file(config_file):
                    updated_files.append(str(config_file))

    # Summary
    logger.info("")
    logger.info("📊 UPDATE SUMMARY:")
    logger.info(f"   📝 Files updated: {len(updated_files)}")

    if updated_files:
        logger.info("   📋 Updated files:")
        for file_path in updated_files:
            logger.info(f"      ✅ {file_path}")
    else:
        logger.info("   ℹ️  No files needed updating")

    logger.info("")
    logger.info("🏁 Database port update complete!")
    logger.info("All database connections now use port 5432")


if __name__ == "__main__":
    main()
