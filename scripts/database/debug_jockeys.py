#!/usr/bin/env python3
"""
Debug script to test jockeys_stats upload
"""

import pandas as pd
from pathlib import Path
import sys

sys.path.append("/app")

from tools.bulk_uploader.column_mappings import get_column_mapping, get_database_mapping


def debug_process_csv():
    csv_file_path = (
        "/app/data/daily_downloads/processed/2025-08-26/jockeys_stats/jockeys_stats.csv"
    )
    csv_filename = Path(csv_file_path).name

    print(f"\n📄 Processing: {csv_filename}")

    # Get mapping information
    column_mapping = get_column_mapping(csv_filename)
    db_mapping = get_database_mapping(csv_filename)

    print(f"🔍 Column mapping type: {type(column_mapping)}")
    print(f"🔍 Column mapping value: {column_mapping}")
    print(f"🔍 DB mapping type: {type(db_mapping)}")
    print(f"🔍 DB mapping value: {db_mapping}")

    if not db_mapping:
        print(f"❌ No database mapping found for {csv_filename}")
        return False

    if not column_mapping:
        print(f"❌ No column mapping found for {csv_filename}")
        return False

    database = db_mapping["database"]
    table = db_mapping["table"]

    print(f"🎯 Target: {database}.{table}")
    return True


if __name__ == "__main__":
    result = debug_process_csv()
    print(f"Result: {result}")
