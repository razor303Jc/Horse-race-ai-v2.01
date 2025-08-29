#!/usr/bin/env python3
"""
Bulk Uploader CLI Interface
Command-line interface for the bulk uploader system
"""

import sys
import argparse
from pathlib import Path
import json
from datetime import datetime
import yaml

# Add the bulk uploader to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bulk_uploader import BulkUploader, BulkUploadConfig


def print_banner():
    """Print application banner"""
    print("🚀 Horse Racing Data Bulk Uploader v1.0")
    print("=" * 50)


def print_job_status(job_status, detailed=False):
    """Print job status information"""
    status_icon = {
        "pending": "⏳",
        "processing": "🔄",
        "completed": "✅",
        "failed": "❌",
    }

    icon = status_icon.get(job_status["status"], "❓")
    print(f"{icon} {job_status['table_name']} - {job_status['status'].upper()}")

    if detailed:
        print(f"   File: {Path(job_status['file_path']).name}")
        print(
            f"   Records: {job_status['records_uploaded']}/{job_status['records_total']}"
        )

        if job_status["start_time"]:
            start_time = datetime.fromisoformat(job_status["start_time"])
            print(f"   Started: {start_time.strftime('%H:%M:%S')}")

        if job_status["end_time"]:
            end_time = datetime.fromisoformat(job_status["end_time"])
            duration = end_time - start_time if job_status["start_time"] else None
            print(f"   Completed: {end_time.strftime('%H:%M:%S')}")
            if duration:
                print(f"   Duration: {duration.total_seconds():.1f}s")

        if job_status["error_message"]:
            print(f"   Error: {job_status['error_message']}")

        print()


def cmd_upload(args):
    """Execute bulk upload command"""
    print_banner()

    # Validate path
    if not args.path.exists():
        print(f"❌ Path does not exist: {args.path}")
        return 1

    # Initialize uploader
    print("🔧 Initializing bulk uploader...")
    try:
        uploader = BulkUploader(args.config)
    except Exception as e:
        print(f"❌ Failed to initialize uploader: {e}")
        return 1

    # Test database connection
    print("🔌 Testing database connection...")
    if not uploader.db_manager.test_connection():
        print("❌ Database connection failed")
        return 1
    print("✅ Database connection successful")

    # Discover files
    print(f"🔍 Discovering files in {args.path}")
    try:
        job_ids = uploader.discover_and_queue_files(args.path, args.recursive)
    except Exception as e:
        print(f"❌ File discovery failed: {e}")
        return 1

    if not job_ids:
        print("❌ No files found to process")
        return 1

    print(f"📋 Queued {len(job_ids)} files for processing:")
    for job_id in job_ids:
        job = uploader.jobs[job_id]
        print(f"   • {job.file_path.name} → {job.table_name}")

    # Confirm upload if not forced
    if not args.force:
        confirm = input("\n🤔 Proceed with bulk upload? (y/N): ")
        if confirm.lower() != "y":
            print("⏹️  Upload cancelled")
            return 0

    # Process all jobs
    print("\n🚀 Starting bulk upload process...")
    try:
        results = uploader.process_all_jobs(args.workers)
    except Exception as e:
        print(f"❌ Bulk upload failed: {e}")
        return 1

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

    # Show detailed results if requested
    if args.verbose:
        print("\n📋 DETAILED RESULTS:")
        for job_id in job_ids:
            job_status = uploader.get_job_status(job_id)
            print_job_status(job_status, detailed=True)

    # Save results if requested
    if args.output:
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": results,
            "jobs": [uploader.get_job_status(job_id) for job_id in job_ids],
        }

        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"💾 Results saved to {args.output}")

    return 0 if results["failed"] == 0 else 1


def cmd_status(args):
    """Show status of upload jobs"""
    print_banner()

    # Initialize uploader (to access job tracking)
    uploader = BulkUploader(args.config)

    # Load status from file if available
    status_file = Path("/tmp/bulk_upload_status.json")
    if status_file.exists():
        try:
            with open(status_file) as f:
                status_data = json.load(f)

            print("📊 Recent Upload Status:")
            print(f"   Timestamp: {status_data.get('timestamp', 'Unknown')}")

            if "jobs" in status_data:
                for job in status_data["jobs"]:
                    print_job_status(job, detailed=args.verbose)

        except Exception as e:
            print(f"❌ Error reading status file: {e}")
            return 1
    else:
        print("ℹ️  No recent upload status available")

    return 0


def cmd_validate(args):
    """Validate files without uploading"""
    print_banner()

    if not args.path.exists():
        print(f"❌ Path does not exist: {args.path}")
        return 1

    # Initialize uploader
    uploader = BulkUploader(args.config)

    # Discover files
    print(f"🔍 Discovering and validating files in {args.path}")
    job_ids = uploader.discover_and_queue_files(args.path, args.recursive)

    if not job_ids:
        print("❌ No files found to validate")
        return 1

    validation_passed = 0
    validation_failed = 0

    for job_id in job_ids:
        job = uploader.jobs[job_id]
        print(f"\n🔍 Validating {job.file_path.name} → {job.table_name}")

        # Run validation only
        try:
            validation_results = uploader.validation_engine.validate_file_structure(
                job.file_path, job.table_name
            )

            if validation_results["valid"]:
                print("✅ Validation passed")
                validation_passed += 1
            else:
                print("❌ Validation failed")
                validation_failed += 1

                if args.verbose:
                    for issue in validation_results.get("issues", []):
                        print(f"   - {issue}")

                    for fix in validation_results.get("fixes", []):
                        print(f"   + {fix}")

        except Exception as e:
            print(f"❌ Validation error: {e}")
            validation_failed += 1

    # Summary
    total = validation_passed + validation_failed
    success_rate = (validation_passed / total * 100) if total > 0 else 0

    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"   Total files: {total}")
    print(f"   Passed: {validation_passed}")
    print(f"   Failed: {validation_failed}")
    print(f"   Success rate: {success_rate:.1f}%")

    return 0 if validation_failed == 0 else 1


def cmd_test_connection(args):
    """Test database connection"""
    print_banner()

    try:
        uploader = BulkUploader(args.config)

        print("🔌 Testing database connection...")
        if uploader.db_manager.test_connection():
            print("✅ Database connection successful")

            # Show connection details
            config = uploader.db_manager.config
            print(f"   Host: {config['host']}")
            print(f"   Port: {config['port']}")
            print(f"   Database: {config['database']}")
            print(f"   User: {config['user']}")

            return 0
        else:
            print("❌ Database connection failed")
            return 1

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return 1


def cmd_config(args):
    """Show or create configuration"""
    print_banner()

    if args.create:
        # Create default configuration file
        config_path = args.create

        if config_path.exists() and not args.force:
            print(f"❌ Configuration file already exists: {config_path}")
            print("   Use --force to overwrite")
            return 1

        # Load default config and save as YAML
        default_config = BulkUploadConfig()

        config_dict = {
            "processing": {
                "batch_size": default_config.batch_size,
                "max_workers": default_config.max_workers,
                "validation_level": default_config.validation_level,
                "conflict_resolution": default_config.conflict_resolution,
                "foreign_key_handling": default_config.foreign_key_handling,
                "max_memory_usage": default_config.max_memory_usage,
                "retry_attempts": default_config.retry_attempts,
                "retry_delay": default_config.retry_delay,
                "connection_pool_size": default_config.connection_pool_size,
            }
        }

        with open(config_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)

        print(f"✅ Configuration file created: {config_path}")
        return 0

    else:
        # Show current configuration
        try:
            uploader = BulkUploader(args.config)
            config = uploader.config

            print("🔧 Current Configuration:")
            print(f"   Batch size: {config.batch_size}")
            print(f"   Max workers: {config.max_workers}")
            print(f"   Validation level: {config.validation_level}")
            print(f"   Conflict resolution: {config.conflict_resolution}")
            print(f"   Foreign key handling: {config.foreign_key_handling}")
            print(f"   Max memory usage: {config.max_memory_usage}")
            print(f"   Retry attempts: {config.retry_attempts}")
            print(f"   Connection pool size: {config.connection_pool_size}")

            return 0

        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Horse Racing Data Bulk Uploader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload all files in directory
  %(prog)s upload /path/to/data

  # Upload with custom config and 8 workers
  %(prog)s upload /path/to/data --config config.yaml --workers 8

  # Validate files without uploading
  %(prog)s validate /path/to/data --verbose

  # Test database connection
  %(prog)s test-connection

  # Show upload status
  %(prog)s status --verbose
        """,
    )

    # Global options
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload data files")
    upload_parser.add_argument("path", type=Path, help="Path to data directory")
    upload_parser.add_argument(
        "--recursive", "-r", action="store_true", help="Search recursively"
    )
    upload_parser.add_argument(
        "--workers", "-w", type=int, help="Number of worker threads"
    )
    upload_parser.add_argument(
        "--force", "-f", action="store_true", help="Skip confirmation"
    )
    upload_parser.add_argument("--output", "-o", type=Path, help="Save results to file")
    upload_parser.set_defaults(func=cmd_upload)

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate files without uploading"
    )
    validate_parser.add_argument("path", type=Path, help="Path to data directory")
    validate_parser.add_argument(
        "--recursive", "-r", action="store_true", help="Search recursively"
    )
    validate_parser.set_defaults(func=cmd_validate)

    # Status command
    status_parser = subparsers.add_parser("status", help="Show upload status")
    status_parser.set_defaults(func=cmd_status)

    # Test connection command
    test_parser = subparsers.add_parser(
        "test-connection", help="Test database connection"
    )
    test_parser.set_defaults(func=cmd_test_connection)

    # Config command
    config_parser = subparsers.add_parser("config", help="Show or create configuration")
    config_parser.add_argument(
        "--create", type=Path, help="Create configuration file at path"
    )
    config_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing file"
    )
    config_parser.set_defaults(func=cmd_config)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
