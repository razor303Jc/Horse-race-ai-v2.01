#!/usr/bin/env python3
"""
Simple script to add breeder column to horses table and rerun upload
"""

import sqlite3
import os
import sys


def add_breeder_column():
    """Add breeder column to horses table if it doesn't exist"""
    db_path = "data/racing_data.db"

    if not os.path.exists(db_path):
        print("Database doesn't exist yet - will be created during upload")
        return True

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if horses table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='horses'"
        )
        if not cursor.fetchone():
            print("Horses table doesn't exist yet - will be created during upload")
            conn.close()
            return True

        # Check if breeder column exists
        cursor.execute("PRAGMA table_info(horses)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns in horses table: {columns}")

        if "breeder" not in columns:
            cursor.execute("ALTER TABLE horses ADD COLUMN breeder TEXT")
            conn.commit()
            print("✅ Added breeder column to horses table")
        else:
            print("✅ Breeder column already exists")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_upload():
    """Run the database upload"""
    try:
        os.system("python tools/data_processing/enhanced_database_uploader.py")
    except Exception as e:
        print(f"❌ Upload failed: {e}")


if __name__ == "__main__":
    print("🔧 Adding breeder column to database...")
    if add_breeder_column():
        print("🚀 Running database upload...")
        run_upload()
    else:
        print("❌ Failed to update database schema")
        sys.exit(1)
