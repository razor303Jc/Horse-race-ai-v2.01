#!/usr/bin/env python3
"""Upload today's race cards to the database"""

import asyncio
import sys
from pathlib import Path
from tools.database.race_card_uploader import RaceCardDatabaseUploader

async def main():
    """Upload today's race cards"""
    print("🚀 Uploading today's race cards to database...")
    
    # Path to today's race card data
    cards_data_dir = Path("/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads/cards_data/2025-08-27")
    
    if not cards_data_dir.exists():
        print(f"❌ Cards data directory not found: {cards_data_dir}")
        return False
    
    print(f"📁 Processing data from: {cards_data_dir}")
    
    # Initialize uploader
    uploader = RaceCardDatabaseUploader()
    
    try:
        # Process and upload all data
        results = await uploader.process_race_cards_data(cards_data_dir)
        
        print("\n" + "="*50)
        print("📊 UPLOAD RESULTS")
        print("="*50)
        
        # Show results for each table
        for table_name, table_results in results.items():
            if isinstance(table_results, dict) and "processed" in table_results:
                print(f"\n🔹 {table_name.upper()}:")
                print(f"   Processed: {table_results['processed']}")
                print(f"   Inserted:  {table_results['inserted']}")
                print(f"   Updated:   {table_results['updated']}")
                print(f"   Failed:    {table_results['failed']}")
        
        # Show any errors
        if "errors" in results and results["errors"]:
            print(f"\n❌ ERRORS:")
            for error in results["errors"]:
                print(f"   - {error}")
        
        print("\n✅ Upload process completed!")
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
