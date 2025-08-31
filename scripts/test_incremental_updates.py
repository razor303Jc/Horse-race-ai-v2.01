#!/usr/bin/env python3
"""
Test script to demonstrate incremental index table updates
Loads a different day's data to show the pipeline working with new entities
"""

import subprocess
import sys
from pathlib import Path


def load_additional_day():
    """Load another day's data to test incremental updates"""
    print("🧪 Testing Incremental Index Table Updates")
    print("=" * 50)

    # Check available data days
    data_dir = Path("data")
    available_days = [
        d.name for d in data_dir.iterdir() if d.is_dir() and d.name.startswith("2025")
    ]

    print(f"Available data days: {available_days}")

    # Modify the entity loader to use a different day
    if len(available_days) > 1:
        new_day = (
            available_days[1]
            if available_days[0] == "2025-08-26"
            else available_days[0]
        )
        print(f"Testing with data from: {new_day}")

        # Create a modified version that loads from the new day
        create_test_loader(new_day)

        # Run the test loader
        result = subprocess.run(
            [sys.executable, "scripts/test_incremental_loader.py"],
            capture_output=True,
            text=True,
        )

        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0
    else:
        print("❌ Need at least 2 days of data to test incremental updates")
        return False


def create_test_loader(target_day):
    """Create a test loader script for a specific day"""

    script_content = f'''#!/usr/bin/env python3
"""
Test incremental loader for {target_day}
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.fixed_entity_loader_v2_05 import load_results_data, update_index_tables, verify_data_loading
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def load_test_day_data():
    """Load results data from {target_day}"""
    print("🔄 Loading additional race results from {target_day}...")
    
    # Temporarily modify the data path for this test
    import scripts.fixed_entity_loader_v2_05 as loader
    
    # Store original path functions
    original_path = loader.Path
    
    # Create a custom path function for this test
    def test_path(*args):
        if len(args) > 0 and str(args[0]).startswith("data/"):
            new_path = str(args[0]).replace("2025-08-26", "{target_day}")
            return original_path(new_path)
        return original_path(*args)
    
    # Monkey patch the Path class
    loader.Path = test_path
    
    try:
        # Load only results data (not entities, to avoid duplicates)
        success = load_results_data()
        
        if success:
            print("✅ New race results loaded successfully")
            
            # Update index tables with any new entities
            print("🔄 Updating index tables with new entities...")
            index_success = update_index_tables()
            
            if index_success:
                print("✅ Index tables updated successfully")
            else:
                print("⚠️  Index table update had issues")
            
            # Show final counts
            total_records = verify_data_loading()
            print(f"📊 Total records now: {{total_records}}")
            
        return success
        
    finally:
        # Restore original path
        loader.Path = original_path

if __name__ == "__main__":
    success = load_test_day_data()
    exit(0 if success else 1)
'''

    with open("scripts/test_incremental_loader.py", "w") as f:
        f.write(script_content)


if __name__ == "__main__":
    success = load_additional_day()
    print(f"\\n{'✅ Test completed successfully!' if success else '❌ Test failed!'}")
