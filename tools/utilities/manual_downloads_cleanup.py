#!/usr/bin/env python3
"""
Manual Downloads Directory Cleanup Utility
==========================================

Quick utility for manually cleaning specific file types from data/daily_downloads.
Useful for testing or when you need immediate cleanup without waiting for
retention periods.
"""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()


def list_files_by_type(downloads_dir: Path):
    """List all files categorized by type."""

    files = {
        "original_csv": [],
        "mapped_csv": [],
        "cleaned_csv": [],
        "manifest_json": [],
        "other_json": [],
        "zip_files": [],
        "temp_files": [],
    }

    if not downloads_dir.exists():
        console.print(f"❌ Directory {downloads_dir} does not exist")
        return files

    for file_path in downloads_dir.rglob("*"):
        if file_path.is_file():
            file_name = file_path.name

            if file_name.startswith("mapped_") and file_name.endswith(".csv"):
                files["mapped_csv"].append(file_path)
            elif file_name.startswith("cleaned_") and file_name.endswith(".csv"):
                files["cleaned_csv"].append(file_path)
            elif file_name.endswith(".csv"):
                files["original_csv"].append(file_path)
            elif "manifest" in file_name and file_name.endswith(".json"):
                files["manifest_json"].append(file_path)
            elif file_name.endswith(".json"):
                files["other_json"].append(file_path)
            elif file_name.endswith(".zip"):
                files["zip_files"].append(file_path)
            elif file_name.endswith((".tmp", ".temp", ".lock", ".partial")):
                files["temp_files"].append(file_path)

    return files


def display_files_table(files_dict):
    """Display files in a table format."""

    table = Table(title="📁 Files in data/daily_downloads", border_style="blue")
    table.add_column("File Type", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("Examples", style="white")

    for file_type, file_list in files_dict.items():
        examples = ", ".join([f.name for f in file_list[:3]])
        if len(file_list) > 3:
            examples += f", ... (+{len(file_list) - 3} more)"

        table.add_row(
            file_type.replace("_", " ").title(),
            str(len(file_list)),
            examples if examples else "None",
        )

    console.print(table)


def clean_file_type(files_dict, file_type: str, force: bool = False):
    """Clean files of a specific type."""

    if file_type not in files_dict:
        console.print(f"❌ Unknown file type: {file_type}")
        return False

    files_to_remove = files_dict[file_type]

    if not files_to_remove:
        console.print(f"ℹ️ No {file_type.replace('_', ' ')} files found")
        return True

    file_type_display = file_type.replace("_", " ")
    console.print(f"\n🗑️ Found {len(files_to_remove)} {file_type_display} files:")
    for file_path in files_to_remove:
        console.print(f"   • {file_path.relative_to(Path('data/daily_downloads'))}")

    if not force:
        prompt_text = f"\nRemove all {len(files_to_remove)} {file_type_display} files?"
        if not Confirm.ask(prompt_text):
            console.print("❌ Cancelled")
            return False

    removed_count = 0
    total_size = 0

    for file_path in files_to_remove:
        try:
            size = file_path.stat().st_size
            file_path.unlink()
            removed_count += 1
            total_size += size
            console.print(f"✅ Removed: {file_path.name}")
        except Exception as e:
            console.print(f"❌ Error removing {file_path.name}: {e}")

    freed_mb = total_size / 1024 / 1024
    console.print(f"\n🎉 Removed {removed_count} files, freed {freed_mb:.1f} MB")
    return True


def main():
    """Main utility function."""

    parser = argparse.ArgumentParser(
        description="Manual cleanup utility for daily downloads"
    )
    parser.add_argument("--list", action="store_true", help="List all files by type")
    parser.add_argument(
        "--clean",
        choices=[
            "original_csv",
            "mapped_csv",
            "cleaned_csv",
            "manifest_json",
            "other_json",
            "zip_files",
            "temp_files",
            "all",
        ],
        help="Clean specific file type",
    )
    parser.add_argument(
        "--force", action="store_true", help="Skip confirmation prompts"
    )
    parser.add_argument(
        "--dir", default="data/daily_downloads", help="Downloads directory path"
    )

    args = parser.parse_args()

    downloads_dir = Path(args.dir)

    # Get all files categorized by type
    files_dict = list_files_by_type(downloads_dir)

    if args.list or not any([args.clean]):
        console.print(f"📂 Analyzing directory: {downloads_dir}")
        display_files_table(files_dict)

        if not args.clean:
            console.print("\nUse --clean <type> to remove specific file types")
            console.print("Use --list to see this breakdown again")
            return True

    if args.clean:
        if args.clean == "all":
            console.print("🧹 Cleaning ALL file types...")

            # Clean in order of priority (temp files first, important files last)
            clean_order = [
                "temp_files",
                "cleaned_csv",
                "mapped_csv",
                "manifest_json",
                "zip_files",
                "original_csv",
                "other_json",
            ]

            for file_type in clean_order:
                if files_dict[file_type]:
                    console.print(f"\n--- Cleaning {file_type.replace('_', ' ')} ---")
                    clean_file_type(files_dict, file_type, args.force)
        else:
            clean_file_type(files_dict, args.clean, args.force)

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n🛑 Cleanup cancelled by user")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Error: {e}")
        sys.exit(1)
