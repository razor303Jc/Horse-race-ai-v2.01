#!/usr/bin/env python3
"""
Manual Card Extraction Script
Extract today's race cards from the processed ZIP file
"""

import os
import zipfile
import shutil
from pathlib import Path


def main():
    """Extract today's cards ZIP file"""

    # Paths
    processed_dir = Path("data/daily_downloads/processed/2025-08-27")
    cards_zip = processed_dir / "cards_2025-08-27_071132_uk-racecards-2025-08-27.zip"
    target_dir = Path("data/daily_downloads/cards_data/2025-08-27")

    if not cards_zip.exists():
        print(f"❌ Cards ZIP not found: {cards_zip}")
        return

    print(f"📦 Extracting: {cards_zip}")

    # Clear target directory
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    # Extract ZIP file
    with zipfile.ZipFile(cards_zip, "r") as zip_ref:
        zip_ref.extractall(target_dir)

    print(f"✅ Extracted to: {target_dir}")

    # List extracted contents
    print("\n📁 Extracted contents:")
    for item in target_dir.rglob("*"):
        if item.is_file():
            print(f"   {item.relative_to(target_dir)}")


if __name__ == "__main__":
    main()
