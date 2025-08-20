#!/usr/bin/env python3
"""
Test script for Horse Base API connectivity.
Run this after setting up your .env file to validate API access.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

async def test_horse_base_connection():
    """Test Horse Base web scraping connection and credentials."""
    try:
        from src.services.external_apis import HorseBaseWebScraper
        from src.core.config import get_settings
        
        settings = get_settings()
        
        print("🏇 Testing Horse Base Web Scraping Connection")
        print("=" * 50)
        
        # Check configuration
        if not settings.horse_race_base_username:
            print("❌ HORSE_RACE_BASE_USERNAME not configured in .env file")
            return False
            
        if not settings.horse_race_base_password:
            print("❌ HORSE_RACE_BASE_PASSWORD not configured in .env file")
            return False
            
        print(f"✅ Username configured: {settings.horse_race_base_username}")
        print(f"✅ Password configured: {'*' * len(settings.horse_race_base_password)}")
        print(f"✅ Base URL: {settings.horse_race_base_url}")
        
        # Test web scraping connection
        async with HorseBaseWebScraper() as scraper:
            print("🔄 Testing login and session management...")
            
            # Test health check (includes login)
            is_healthy = await scraper.health_check()
            if is_healthy:
                print("✅ Horse Base login successful")
            else:
                print("❌ Horse Base login failed")
                return False
            
            # Try to fetch today's races
            print("🔄 Testing data access for today's races...")
            try:
                races = await scraper.get_today_races()
                print(f"✅ Successfully fetched {len(races)} races for today")
                
                if races:
                    sample_race = races[0]
                    print(f"   Sample race: {sample_race.track_name} Race {sample_race.race_number}")
                    print(f"   Race ID: {sample_race.race_id}")
                else:
                    print("   No races found for today (this might be normal)")
                    
            except Exception as e:
                print(f"⚠️  Data access test failed: {e}")
                print("   This might be due to account limitations or site structure changes")
        
        print("\n🎉 Horse Base web scraping connection test completed successfully!")
        print("\n📋 Next Steps:")
        print("   1. Copy .env.template to .env")
        print("   2. Run ./setup_dev.sh to install dependencies")
        print("   3. Start development with the web scraper")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you've run ./setup_dev.sh to install dependencies")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_horse_base_connection())
    sys.exit(0 if success else 1)
