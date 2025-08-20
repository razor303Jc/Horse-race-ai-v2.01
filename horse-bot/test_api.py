#!/usr/bin/env python3
"""
Test script for the Horse Race Handicapping AI API using test data.
"""

import sys
import asyncio
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.data_provider import get_data_provider


async def test_api_functionality():
    """Test the API functionality with test data."""
    print("🚀 Testing Horse Race Handicapping AI API")
    print("=" * 50)
    
    try:
        # Initialize data provider
        data_provider = get_data_provider()
        
        # Test health check
        print("🏥 Testing Health Check:")
        health = await data_provider.health_check()
        source_info = data_provider.get_data_source_info()
        
        print(f"   📊 Data Source: {source_info['current_source']}")
        print(f"   🌍 Environment: {source_info['environment']}")
        print(f"   ❤️ Status: {health['status']}")
        print(f"   🎲 Test Data: {'✅' if health['test_data_available'] else '❌'}")
        
        if health.get('test_data_summary'):
            summary = health['test_data_summary']
            print(f"   📈 Summary: {summary['race_cards']} cards, {summary['total_races']} races, {summary['horses']} horses")
        
        # Test today's races
        print(f"\n🏁 Testing Today's Races:")
        races = await data_provider.get_todays_races()
        print(f"   📅 Found {len(races)} races today")
        
        if races:
            sample_race = races[0]
            print(f"   🏟️ Sample: {sample_race['track_name']} Race {sample_race['race_number']}")
            print(f"   📏 Distance: {sample_race['distance']} furlongs")
            print(f"   🐎 Field Size: {sample_race['field_size']} horses")
            print(f"   💰 Purse: £{sample_race.get('purse', 0):,}")
            
            # Test race by ID
            print(f"\n🔍 Testing Race Lookup by ID:")
            race_id = sample_race['race_id']
            race_detail = await data_provider.get_race_by_id(race_id)
            if race_detail:
                print(f"   ✅ Found race: {race_detail['track_name']} Race {race_detail['race_number']}")
            else:
                print(f"   ❌ Race not found")
        
        # Test specific date
        print(f"\n📅 Testing Races by Date:")
        date_races = await data_provider.get_races_by_date("2025-07-22")
        print(f"   📊 Found {len(date_races)} races for 2025-07-22")
        
        # Test horse search
        print(f"\n🐎 Testing Horse Search:")
        horses = await data_provider.search_horses("Thunder")
        print(f"   🔍 Found {len(horses)} horses with 'Thunder' in name")
        if horses:
            sample_horse = horses[0]
            print(f"   📝 Sample: {sample_horse['name']} (Age {sample_horse['age']})")
        
        # Test horse profile
        if horses:
            print(f"\n👤 Testing Horse Profile:")
            horse_name = horses[0]['name']
            horse_profile = await data_provider.get_horse_profile(horse_name)
            if horse_profile:
                career = horse_profile['career_record']
                print(f"   🐎 {horse_profile['name']}: {career['wins']} wins from {career['starts']} starts")
                print(f"   💰 Earnings: £{career['earnings']:,}")
        
        # Test jockey stats
        print(f"\n👤 Testing Jockey Stats:")
        jockey_stats = await data_provider.get_jockey_stats("R. Moore")
        if jockey_stats:
            stats_2024 = jockey_stats['stats_2024']
            print(f"   🏇 {jockey_stats['name']}: {stats_2024['win_percentage']}% win rate")
            print(f"   🏆 2024: {stats_2024['wins']} wins from {stats_2024['rides']} rides")
        
        # Test trainer stats
        print(f"\n👨‍🏫 Testing Trainer Stats:")
        trainer_stats = await data_provider.get_trainer_stats("A. Balding")
        if trainer_stats:
            stats_2024 = trainer_stats['stats_2024']
            print(f"   🏇 {trainer_stats['name']}: {stats_2024['win_percentage']}% win rate")
            print(f"   🏠 Stable Size: {trainer_stats['stable_size']} horses")
        
        # Test track info
        print(f"\n🏟️ Testing Track Info:")
        track_info = await data_provider.get_track_info("EPM")
        if track_info:
            print(f"   🏁 {track_info['name']} ({track_info['code']})")
            print(f"   🌱 Surfaces: {', '.join(track_info['surfaces'])}")
        
        # Test race results
        if races and len(races) > 5:  # Use a past race for results
            print(f"\n🏆 Testing Race Results:")
            past_race_id = races[5]['race_id']  # Use a different race
            results = await data_provider.get_race_results(past_race_id)
            if results:
                print(f"   🏁 Race {results['race_id']}: {results['status']}")
                if results.get('results'):
                    winner = results['results'][0]
                    print(f"   🥇 Winner: {winner['horse_name']} ({winner['jockey']})")
        
        print(f"\n✅ All API tests completed successfully!")
        print(f"\n📚 Available endpoints (when FastAPI is running):")
        print(f"   🏥 Health: /api/v1/health/detailed")
        print(f"   🏁 Today's Races: /api/v1/races/today")
        print(f"   📅 Races by Date: /api/v1/races/date/YYYY-MM-DD")
        print(f"   🔍 Race by ID: /api/v1/races/{{race_id}}")
        print(f"   🏆 Race Results: /api/v1/races/{{race_id}}/results")
        print(f"   🐎 Horse Profile: /api/v1/participants/horses/{{horse_name}}")
        print(f"   🔍 Horse Search: /api/v1/participants/horses/search?q={{query}}")
        print(f"   👤 Jockey Stats: /api/v1/participants/jockeys/{{jockey_name}}")
        print(f"   👨‍🏫 Trainer Stats: /api/v1/participants/trainers/{{trainer_name}}")
        print(f"   🏟️ Track Info: /api/v1/participants/tracks/{{track_code}}")
        print(f"   📊 Data Summary: /api/v1/races/data/summary")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_api_functionality())
