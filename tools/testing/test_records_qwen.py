#!/usr/bin/env python3
"""
Test Qwen2.5's solution specifically on records.csv
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01")

from qwen_bigint_solution import QwenBigintSolver


def test_records_csv():
    """Test records.csv specifically"""
    solver = QwenBigintSolver()

    try:
        print("🧬 Testing records.csv with Qwen2.5's solution")
        print("=" * 60)

        df = solver.process_problematic_csv(
            "project_root / 'data' / horseracedatabase/results_project_root / 'data' / records/records.csv", "race_results"
        )

        print(f"✅ SUCCESS: records.csv processed!")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        print("\n📊 Sample data:")
        print(df.head().to_string())

        return True

    except Exception as e:
        print(f"❌ FAILED: records.csv - {e}")
        return False


if __name__ == "__main__":
    test_records_csv()
