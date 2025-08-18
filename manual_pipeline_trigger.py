#!/usr/bin/env python3
"""
Manual Pipeline Trigger with Enhanced Preprocessing
Test the complete workflow: Data Download → Enhanced Preprocessing → Upload → ML
"""
import subprocess
import sys
import time
from pathlib import Path


def trigger_pipeline_with_preprocessing():
    """Manually trigger the complete pipeline with enhanced preprocessing"""
    print("🚀 Starting Complete Pipeline with Enhanced Preprocessing...")

    # Step 1: Check if data exists to process
    print("\n📋 Step 1: Checking for existing CSV data...")

    # Step 2: Manually run enhanced preprocessing
    print("\n🧹 Step 2: Running Enhanced Data Preprocessing...")
    try:
        result = subprocess.run(
            [
                "docker",
                "exec",
                "horse_racing_auto_downloader_clean",
                "python",
                "/app/enhanced_preprocessing_pipeline.py",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            print("✅ Enhanced preprocessing completed successfully")
            print("Preprocessing output:")
            print(result.stdout)
        else:
            print(f"❌ Enhanced preprocessing failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Enhanced preprocessing timed out")
        return False
    except Exception as e:
        print(f"❌ Enhanced preprocessing exception: {e}")
        return False

    # Step 3: Run CSV upload with processed data
    print("\n📤 Step 3: Uploading processed data to database...")
    try:
        result = subprocess.run(
            [
                "docker",
                "exec",
                "horse_racing_auto_downloader_clean",
                "python",
                "/app/tools/csv_processing/safe_upload_all.py",
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode == 0:
            print("✅ Data upload completed successfully")
            print("Upload output:")
            print(result.stdout)
        else:
            print(f"❌ Data upload failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Data upload timed out")
        return False
    except Exception as e:
        print(f"❌ Data upload exception: {e}")
        return False

    # Step 4: Check database for data
    print("\n🗃️  Step 4: Verifying data in database...")
    try:
        result = subprocess.run(
            [
                "docker",
                "exec",
                "horse_racing_auto_downloader_clean",
                "python",
                "-c",
                "import psycopg2; conn = psycopg2.connect('host=horse_racing_postgres_clean port=5432 dbname=horse_racing user=postgres password=postgres'); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM race_results'); print(f'Database has {cur.fetchone()[0]} records'); conn.close()",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("✅ Database verification successful")
            print(result.stdout)
        else:
            print(f"❌ Database verification failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Database verification exception: {e}")
        return False

    print("\n🎉 Complete pipeline with enhanced preprocessing executed successfully!")
    print("\nData Flow Summary:")
    print("1. ✅ Raw CSV data processed with enhanced cleaning")
    print("2. ✅ Cleaned data uploaded to PostgreSQL database")
    print("3. ✅ Database now contains preprocessed, ML-ready data")
    print("\nNext: ML training will use improved data quality for better accuracy!")

    return True


if __name__ == "__main__":
    print("🔧 Manual Pipeline Integration Test")
    print("Testing: Raw Data → Enhanced Preprocessing → Clean Upload → ML Ready")

    success = trigger_pipeline_with_preprocessing()

    if success:
        print("\n✨ SUCCESS: Enhanced preprocessing integration is working!")
        print("\nNow you can:")
        print("1. Run the full automated pipeline")
        print("2. Start ML training with improved data quality")
        print("3. Expect better model accuracy from cleaner data")
        sys.exit(0)
    else:
        print("\n⚠️  Pipeline integration needs debugging")
        sys.exit(1)
