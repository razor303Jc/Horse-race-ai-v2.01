#!/usr/bin/env python3
"""
Bulk Uploader Docker Container Script
Optimized for running bulk uploads inside Docker containers
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import logging

# Add the bulk uploader to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bulk_uploader import BulkUploader, BulkUploadConfig


def setup_container_logging():
    """Setup logging for container environment"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("/app/logs/bulk_uploader.log"),
        ],
    )


def get_container_config() -> BulkUploadConfig:
    """Get configuration optimized for container environment"""
    return BulkUploadConfig(
        batch_size=int(os.environ.get("BULK_BATCH_SIZE", "1000")),
        max_workers=int(os.environ.get("BULK_MAX_WORKERS", "4")),
        validation_level=os.environ.get("BULK_VALIDATION_LEVEL", "strict"),
        conflict_resolution=os.environ.get("BULK_CONFLICT_RESOLUTION", "ignore"),
        retry_attempts=int(os.environ.get("BULK_RETRY_ATTEMPTS", "3")),
        connection_pool_size=int(os.environ.get("BULK_CONNECTION_POOL", "10")),
    )


def process_daily_downloads():
    """Process files from daily downloads directory"""
    print("🚀 Starting bulk upload for daily downloads")
    print("=" * 50)

    # Setup logging
    setup_container_logging()
    logger = logging.getLogger(__name__)

    # Data directory
    data_dir = Path("/app/data/daily_downloads")
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return 1

    # Initialize uploader with container config
    config = get_container_config()
    uploader = BulkUploader()
    uploader.config = config

    # Test database connection
    print("🔌 Testing database connection...")
    if not uploader.db_manager.test_connection():
        print("❌ Database connection failed")
        logger.error("Database connection failed")
        return 1

    print("✅ Database connection successful")
    logger.info("Database connection established")

    try:
        # Discover and queue files
        print(f"🔍 Discovering files in {data_dir}")
        job_ids = uploader.discover_and_queue_files(data_dir, recursive=False)

        if not job_ids:
            print("ℹ️  No files found to process")
            logger.info("No files found for processing")
            return 0

        print(f"📋 Queued {len(job_ids)} files for processing:")
        for job_id in job_ids:
            job = uploader.jobs[job_id]
            print(f"   • {job.file_path.name} → {job.table_name}")
            logger.info(f"Queued {job.file_path.name} for {job.table_name}")

        # Process all jobs
        print("\n🚀 Starting bulk upload process...")
        results = uploader.process_all_jobs()

        # Display results
        print("\n📊 BULK UPLOAD RESULTS:")
        print(f"   Total jobs: {results['total_jobs']}")
        print(f"   Successful: {results['successful']}")
        print(f"   Failed: {results['failed']}")

        success_rate = (
            (results["successful"] / results["total_jobs"] * 100)
            if results["total_jobs"] > 0
            else 0
        )
        print(f"   Success rate: {success_rate:.1f}%")

        # Log results
        logger.info(
            f"Bulk upload completed: {results['successful']}/{results['total_jobs']} successful"
        )

        # Show detailed results
        print("\n📋 DETAILED RESULTS:")
        for job_id, result in results["job_results"].items():
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['table']} - {result['records']} records")

            if result["error"]:
                print(f"      Error: {result['error']}")
                logger.error(f"Job {job_id} failed: {result['error']}")
            else:
                logger.info(
                    f"Job {job_id} completed: {result['records']} records uploaded"
                )

        # Save status for monitoring
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "container_run": True,
            "summary": results,
            "jobs": [uploader.get_job_status(job_id) for job_id in job_ids],
        }

        status_file = Path("/app/data/bulk_upload_status.json")
        with open(status_file, "w") as f:
            json.dump(status_data, f, indent=2)

        print(f"\n💾 Status saved to {status_file}")

        # Return appropriate exit code
        return 0 if results["failed"] == 0 else 1

    except Exception as e:
        print(f"❌ Bulk upload failed: {e}")
        logger.error(f"Bulk upload failed: {e}", exc_info=True)
        return 1


def process_specific_files():
    """Process specific files passed as environment variables"""
    files_env = os.environ.get("BULK_UPLOAD_FILES", "")
    if not files_env:
        print("❌ No files specified in BULK_UPLOAD_FILES environment variable")
        return 1

    files = [Path(f.strip()) for f in files_env.split(",")]

    print(f"🚀 Processing {len(files)} specific files")
    print("=" * 50)

    # Setup logging
    setup_container_logging()
    logger = logging.getLogger(__name__)

    # Initialize uploader
    config = get_container_config()
    uploader = BulkUploader()
    uploader.config = config

    # Test database connection
    if not uploader.db_manager.test_connection():
        print("❌ Database connection failed")
        return 1

    try:
        successful = 0
        failed = 0

        for file_path in files:
            if not file_path.exists():
                print(f"⚠️ File not found: {file_path}")
                logger.warning(f"File not found: {file_path}")
                failed += 1
                continue

            # Classify file
            table_name = uploader.discovery_engine.classify_file(file_path)
            if not table_name:
                print(f"⚠️ Could not classify file: {file_path}")
                logger.warning(f"Could not classify file: {file_path}")
                failed += 1
                continue

            print(f"\n📄 Processing {file_path.name} → {table_name}")

            # Create and process job
            job_id = uploader._generate_job_id(file_path)
            from bulk_uploader import UploadJob

            job = UploadJob(job_id=job_id, file_path=file_path, table_name=table_name)
            uploader.jobs[job_id] = job

            if uploader.process_job(job_id):
                print(f"✅ Successfully processed {file_path.name}")
                logger.info(f"Successfully processed {file_path.name}")
                successful += 1
            else:
                print(f"❌ Failed to process {file_path.name}")
                logger.error(f"Failed to process {file_path.name}: {job.error_message}")
                failed += 1

        # Summary
        total = successful + failed
        success_rate = (successful / total * 100) if total > 0 else 0

        print(f"\n📊 PROCESSING SUMMARY:")
        print(f"   Total files: {total}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        print(f"   Success rate: {success_rate:.1f}%")

        return 0 if failed == 0 else 1

    except Exception as e:
        print(f"❌ Processing failed: {e}")
        logger.error(f"Processing failed: {e}", exc_info=True)
        return 1


def main():
    """Main container entry point"""
    mode = os.environ.get("BULK_UPLOAD_MODE", "daily_downloads")

    if mode == "daily_downloads":
        return process_daily_downloads()
    elif mode == "specific_files":
        return process_specific_files()
    else:
        print(f"❌ Unknown upload mode: {mode}")
        print("Available modes: daily_downloads, specific_files")
        return 1


if __name__ == "__main__":
    sys.exit(main())
