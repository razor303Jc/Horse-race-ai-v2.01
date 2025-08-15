#!/usr/bin/env python3

import os
import sys
import time

import psycopg2

# Add the project root to Python path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.02")

from tools.caching.cached_feature_engineering import CachedFeatureEngineering


def test_cached_feature_engineering():
    """Test the cached feature engineering with real data."""

    print("🏇 Testing Cached Feature Engineering")
    print("=" * 50)

    # Get a sample race_id from the database
    db_config = {
        "host": "localhost",
        "port": 5433,
        "database": "horse_racing_db",
        "user": "horse_racing",
        "password": os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
    }

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Get a recent race with runners (any number)
        cursor.execute(
            """
            SELECT r.race_id, r.date, r.course, COUNT(rec.record_id) as runners
            FROM races r
            JOIN records rec ON r.race_id = rec.race_id
            GROUP BY r.race_id, r.date, r.course
            HAVING COUNT(rec.record_id) >= 1
            ORDER BY COUNT(rec.record_id) DESC, r.date DESC
            LIMIT 5
        """
        )

        races = cursor.fetchall()

        print("🎯 Available races for testing:")
        for i, (race_id, date, course, runners) in enumerate(races, 1):
            print(f"  {i}. {race_id} - {date} - {course} ({runners} runners)")

        if not races:
            print("❌ No suitable races found for testing")
            return

        # Use the first race
        sample_race_id = races[0][0]
        print(f"\n🏁 Testing with race: {sample_race_id}")
        print(f"📅 Date: {races[0][1]}")
        print(f"🏟️  Course: {races[0][2]}")
        print(f"🏇 Runners: {races[0][3]}")

        cursor.close()
        conn.close()

        # Initialize cached feature engineering
        print("\n🚀 Initializing cached feature engineering...")
        cached_fe = CachedFeatureEngineering()

        # Test feature engineering (first run - cache miss)
        print("\n🔄 First run (cache miss expected)...")
        start_time = time.time()
        features_df = cached_fe.create_ml_features_for_race(sample_race_id)
        first_run_time = time.time() - start_time

        print(f"⏱️  First run completed in: {first_run_time:.2f}s")
        print(f"📊 Features created for: {len(features_df)} horses")

        if not features_df.empty:
            print(f"📋 Feature columns: {len(features_df.columns)} features")
            print("   Sample features:", list(features_df.columns)[:10])

            # Test feature engineering (second run - cache hit)
            print("\n🔄 Second run (cache hit expected)...")
            start_time = time.time()
            features_df_cached = cached_fe.create_ml_features_for_race(sample_race_id)
            second_run_time = time.time() - start_time

            print(f"⏱️  Second run completed in: {second_run_time:.2f}s")

            # Calculate speedup
            if second_run_time > 0:
                speedup = first_run_time / second_run_time
                time_saved = first_run_time - second_run_time
                print(f"🚀 Performance improvement: {speedup:.1f}x faster")
                print(f"⚡ Time saved: {time_saved:.2f}s")

            # Verify data consistency
            if features_df.equals(features_df_cached):
                print("✅ Data consistency verified - cached results match original")
            else:
                print("⚠️  Data consistency warning - cached results differ")

        # Display cache analytics
        print("\n📊 Cache Analytics:")
        analytics = cached_fe.get_cache_analytics()

        print(
            f'  • Hit Rate: {analytics["cache_performance"]["hit_rate_percent"]:.1f}%'
        )
        print(f'  • Total Requests: {analytics["cache_performance"]["total_requests"]}')
        print(
            f'  • Time Saved: {analytics["cache_performance"]["time_saved_ms"]:.1f}ms'
        )
        print(f'  • Cache Status: {analytics["cache_status"]}')
        print(f'  • Redis Version: {analytics["redis_info"]["version"]}')
        print(f'  • Redis Memory: {analytics["redis_info"]["memory_mb"]:.1f}MB')

        print("\n🎉 Cached feature engineering test completed successfully!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_cached_feature_engineering()
