#!/usr/bin/env python3
"""
Database Explorer - Explore all our racing databases
Shows comprehensive statistics and sample data from our generated datasets
"""

import sqlite3
import pandas as pd
import sys
from pathlib import Path


def explore_database(db_path: str):
    """Explore a SQLite database and show comprehensive statistics"""
    if not Path(db_path).exists():
        print(f"❌ Database {db_path} not found")
        return

    print(f"\n🗃️  EXPLORING DATABASE: {db_path}")
    print("=" * 80)

    try:
        conn = sqlite3.connect(db_path)

        # Get all tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("❌ No tables found in database")
            return

        print(f"📊 TABLES FOUND: {len(tables)}")

        total_records = 0

        for (table_name,) in tables:
            print(f"\n📋 TABLE: {table_name}")
            print("-" * 40)

            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"   📝 Columns: {len(columns)}")
            for col in columns:
                print(f"      • {col[1]} ({col[2]})")

            # Get record count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"   📊 Records: {count:,}")

            # Show sample data if records exist
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                samples = cursor.fetchall()

                if samples:
                    print(f"   🔍 Sample Data:")
                    column_names = [col[1] for col in columns]

                    for i, sample in enumerate(samples[:2]):  # Show first 2 rows
                        print(f"      Row {i+1}:")
                        for j, value in enumerate(sample):
                            if j < len(column_names):
                                # Truncate long values
                                str_val = str(value)
                                if len(str_val) > 30:
                                    str_val = str_val[:27] + "..."
                                print(f"        {column_names[j]}: {str_val}")

        print(f"\n🎯 TOTAL RECORDS ACROSS ALL TABLES: {total_records:,}")

        # Get database size
        db_size = Path(db_path).stat().st_size
        print(f"💾 DATABASE SIZE: {db_size / (1024*1024):.2f} MB")

        conn.close()

    except Exception as e:
        print(f"❌ Error exploring database: {e}")


def main():
    """Main function to explore all databases"""
    print("🔍 HORSE RACING DATABASE EXPLORER")
    print("=" * 80)

    # Find all .db files
    db_files = list(Path(".").glob("*.db"))

    if not db_files:
        print("❌ No database files found!")
        return

    print(f"📋 FOUND {len(db_files)} DATABASE FILES:")
    for db in db_files:
        print(f"   • {db}")

    # Explore each database
    for db_file in sorted(db_files):
        explore_database(str(db_file))

    print("\n🎉 DATABASE EXPLORATION COMPLETE!")

    # Show recommendations based on findings
    print("\n💡 RECOMMENDATIONS:")
    print("   🐘 For PostgreSQL: Consider migrating large datasets to PostgreSQL")
    print("   📊 For Analysis: Use pandas to load data for detailed analysis")
    print(
        "   🚀 For ML Training: Current SQLite databases are perfect for our ML pipeline"
    )


if __name__ == "__main__":
    main()
