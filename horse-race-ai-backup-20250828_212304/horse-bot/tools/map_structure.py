#!/usr/bin/env python3
"""
Standalone Horse Base Structure Mapper

Run this script to map Horse Base structure with minimal requests,
then generate test data for offline development.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

async def main():
    """Run the structure mapping."""
    try:
        from src.services.structure_mapper import map_horse_base_structure
        await map_horse_base_structure()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please run ./setup_dev.sh first to install dependencies")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
