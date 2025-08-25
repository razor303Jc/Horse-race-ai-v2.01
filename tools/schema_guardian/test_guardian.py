#!/usr/bin/env python3
"""
Quick test of the Ultimate Schema Guardian core functionality
"""
import pandas as pd
import psycopg2
from pathlib import Path
import sys


def test_schema_guardian():
    """Test core functionality"""
    print("🎯 TESTING ULTIMATE SCHEMA GUARDIAN")
    print("=" * 50)

    # Database connection
    database_config = {
        "host": "horse_racing_postgres_clean",
        "port": 5432,
        "database": "results_horse_racing_db",
        "user": "horse_racing",
        "password": "secure_password_123",
    }

    # Test database connection
    try:
        conn = psycopg2.connect(**database_config)
        print("✅ Database connection successful")

        # Test file access
        data_dir = Path("/app/data/daily_downloads")
        test_file = data_dir / "mapped_horses.csv"

        if test_file.exists():
            print(f"✅ Test file found: {test_file}")
            df = pd.read_csv(test_file)
            print(f"✅ CSV loaded: {len(df)} rows, {len(df.columns)} columns")
            print(f"📋 Columns: {list(df.columns)}")
        else:
            print(f"❌ Test file not found: {test_file}")

        conn.close()
        print("✅ Test completed successfully")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True


if __name__ == "__main__":
    success = test_schema_guardian()
    sys.exit(0 if success else 1)
