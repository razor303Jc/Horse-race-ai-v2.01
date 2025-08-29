#!/usr/bin/env python3
"""
Test script to upload race card data to PostgreSQL
Run this after manual download processing
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from tools.database.race_card_uploader import RaceCardDatabaseUploader


async def run_upload():
    """Test the race card database upload"""

    # Set data directory
    cards_data_dir = Path(
        "/home/jc/Documents/Horse-race-ai-v2.03/data/daily_downloads/cards_data"
    )

    print("🚀 Starting Race Card Database Upload")
    print(f"📁 Data directory: {cards_data_dir}")

    # Check if data directory exists
    if not cards_data_dir.exists():
        print(f"❌ Data directory not found: {cards_data_dir}")
        return

    # Check for required files
    required_files = [
        cards_data_dir / "races" / "races.csv",
        cards_data_dir / "horses" / "horses.csv",
        cards_data_dir / "racecard_details" / "racecard_details.csv",
    ]

    missing_files = [f for f in required_files if not f.exists()]
    if missing_files:
        print(f"❌ Missing required files:")
        for f in missing_files:
            print(f"   - {f}")
        return

    print("✅ All required files found")

    # Initialize uploader and process data
    try:
        uploader = RaceCardDatabaseUploader()
        results = await uploader.process_race_cards_data(cards_data_dir)

        print("\n📊 Upload Results:")
        print("=" * 50)

        for table_name, stats in results.items():
            if isinstance(stats, dict) and "processed" in stats:
                print(f"\n{table_name.upper()}:")
                print(f"  Processed: {stats['processed']}")
                print(f"  Inserted:  {stats['inserted']}")
                print(f"  Updated:   {stats['updated']}")
                print(f"  Failed:    {stats['failed']}")

                success_rate = (
                    ((stats["inserted"] + stats["updated"]) / stats["processed"] * 100)
                    if stats["processed"] > 0
                    else 0
                )
                print(f"  Success:   {success_rate:.1f}%")

        if results.get("errors"):
            print(f"\n❌ ERRORS ({len(results['errors'])}):")
            for error in results["errors"]:
                print(f"  - {error}")

        print("\n✅ Database upload completed!")

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_upload())
