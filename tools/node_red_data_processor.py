#!/usr/bin/env python3
"""
Enhanced Data Processing Script for Node-RED Integration
Supports date range and data type selection for selective processing.
"""

import argparse
import sys
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def setup_logging():
    """Setup logging for Node-RED integration"""
    # Create logs directory if it doesn't exist
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "data_processing.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger(__name__)


def validate_date_range(start_date_str, end_date_str):
    """Validate date range parameters"""
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")

        # Check if range is reasonable (max 30 days)
        days_diff = (end_date - start_date).days
        if days_diff > 30:
            raise ValueError("Date range cannot exceed 30 days")

        return start_date, end_date, days_diff

    except ValueError as e:
        if "time data" in str(e):
            raise ValueError("Invalid date format. Use YYYY-MM-DD format")
        raise e


def process_cards_data(start_date, end_date, logger):
    """Process cards data for the specified date range"""
    logger.info(f"Processing cards data from {start_date.date()} to {end_date.date()}")

    try:
        # Import and run cards processing
        from tools.bulk_uploader.bulk_upload_processor import (
            process_cards_for_date_range,
        )

        result = process_cards_for_date_range(start_date, end_date)
        logger.info(f"Cards processing completed successfully: {result}")
        return True, result

    except ImportError:
        # Fallback to calling script directly
        logger.info("Using fallback script execution for cards processing")
        cmd_parts = [
            f"cd {project_root}",
            "python tools/bulk_uploader/bulk_upload_processor.py",
            "--type cards",
            f"--start-date {start_date.date()}",
            f"--end-date {end_date.date()}",
        ]
        command = " && ".join(cmd_parts[:2]) + " " + " ".join(cmd_parts[2:])
        result = os.system(command)

        if result == 0:
            logger.info("Cards processing completed successfully via script")
            return True, "Cards data processed successfully"
        else:
            logger.error(f"Cards processing failed with exit code: {result}")
            return False, f"Cards processing failed with exit code: {result}"

    except Exception as e:
        logger.error(f"Error processing cards data: {str(e)}")
        return False, str(e)


def process_results_data(start_date, end_date, logger):
    """Process results data for the specified date range"""
    logger.info(
        f"Processing results data from {start_date.date()} to {end_date.date()}"
    )

    try:
        # Import and run results processing
        from tools.bulk_uploader.bulk_upload_processor import (
            process_results_for_date_range,
        )

        result = process_results_for_date_range(start_date, end_date)
        logger.info(f"Results processing completed successfully: {result}")
        return True, result

    except ImportError:
        # Fallback to calling script directly
        logger.info("Using fallback script execution for results processing")
        cmd_parts = [
            f"cd {project_root}",
            "python tools/bulk_uploader/bulk_upload_processor.py",
            "--type results",
            f"--start-date {start_date.date()}",
            f"--end-date {end_date.date()}",
        ]
        command = " && ".join(cmd_parts[:2]) + " " + " ".join(cmd_parts[2:])
        result = os.system(command)

        if result == 0:
            logger.info("Results processing completed successfully via script")
            return True, "Results data processed successfully"
        else:
            logger.error(f"Results processing failed with exit code: {result}")
            return False, f"Results processing failed with exit code: {result}"

    except Exception as e:
        logger.error(f"Error processing results data: {str(e)}")
        return False, str(e)


def process_data_by_type(data_type, start_date, end_date, logger):
    """Process data based on type selection"""
    results = []
    overall_success = True

    if data_type in ["cards", "both"]:
        logger.info("Starting cards data processing...")
        success, message = process_cards_data(start_date, end_date, logger)
        results.append(f"Cards: {message}")
        if not success:
            overall_success = False

    if data_type in ["results", "both"]:
        logger.info("Starting results data processing...")
        success, message = process_results_data(start_date, end_date, logger)
        results.append(f"Results: {message}")
        if not success:
            overall_success = False

    return overall_success, results


def generate_summary_report(
    data_type, start_date, end_date, success, results, processing_time
):
    """Generate a summary report of the processing"""
    report = {
        "processing_summary": {
            "data_type": data_type,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days + 1,
            },
            "status": "success" if success else "error",
            "processing_time_seconds": round(processing_time, 2),
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }
    }
    return report


def main():
    """Main processing function"""
    parser = argparse.ArgumentParser(
        description="Process horse racing data with date range and type selection"
    )
    parser.add_argument(
        "--start-date", required=True, help="Start date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--end-date", required=True, help="End date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--type",
        choices=["cards", "results", "both"],
        required=True,
        help="Type of data to process",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format for results",
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging()

    try:
        # Validate inputs
        start_date, end_date, days_count = validate_date_range(
            args.start_date, args.end_date
        )

        logger.info(f"Starting data processing...")
        logger.info(
            f"Date range: {start_date.date()} to {end_date.date()} ({days_count + 1} days)"
        )
        logger.info(f"Data type: {args.type}")

        # Record processing start time
        start_time = datetime.now()

        # Process data
        success, results = process_data_by_type(args.type, start_date, end_date, logger)

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Generate summary
        summary = generate_summary_report(
            args.type, start_date, end_date, success, results, processing_time
        )

        if args.output_format == "json":
            print(json.dumps(summary, indent=2))
        else:
            print(f"\n{'='*60}")
            print("PROCESSING SUMMARY")
            print(f"{'='*60}")
            print(f"Data Type: {args.type.upper()}")
            print(
                f"Date Range: {start_date.date()} to {end_date.date()} ({days_count + 1} days)"
            )
            print(f"Status: {'SUCCESS' if success else 'ERROR'}")
            print(f"Processing Time: {processing_time:.2f} seconds")
            print(f"\nResults:")
            for result in results:
                print(f"  - {result}")
            print(f"{'='*60}")

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

import argparse
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def setup_logging():
    """Setup logging for Node-RED integration"""
    import logging

    # Create logs directory if it doesn't exist
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "data_processing.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger(__name__)


def validate_date_range(start_date_str, end_date_str):
    """Validate date range parameters"""
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")

        # Check if range is reasonable (max 30 days)
        days_diff = (end_date - start_date).days
        if days_diff > 30:
            raise ValueError("Date range cannot exceed 30 days")

        return start_date, end_date, days_diff

    except ValueError as e:
        if "time data" in str(e):
            raise ValueError("Invalid date format. Use YYYY-MM-DD format")
        raise e


def process_cards_data(start_date, end_date, logger):
    """Process cards data for the specified date range"""
    logger.info(f"Processing cards data from {start_date.date()} to {end_date.date()}")

    try:
        # Import and run cards processing
        from tools.bulk_uploader.bulk_upload_processor import (
            process_cards_for_date_range,
        )

        result = process_cards_for_date_range(start_date, end_date)
        logger.info(f"Cards processing completed successfully: {result}")
        return True, result

    except ImportError:
        # Fallback to calling script directly
        logger.info("Using fallback script execution for cards processing")
        command = f"cd {project_root} && python tools/bulk_uploader/bulk_upload_processor.py --type cards --start-date {start_date.date()} --end-date {end_date.date()}"
        result = os.system(command)

        if result == 0:
            logger.info("Cards processing completed successfully via script")
            return True, "Cards data processed successfully"
        else:
            logger.error(f"Cards processing failed with exit code: {result}")
            return False, f"Cards processing failed with exit code: {result}"

    except Exception as e:
        logger.error(f"Error processing cards data: {str(e)}")
        return False, str(e)


def process_results_data(start_date, end_date, logger):
    """Process results data for the specified date range"""
    logger.info(
        f"Processing results data from {start_date.date()} to {end_date.date()}"
    )

    try:
        # Import and run results processing
        from tools.bulk_uploader.bulk_upload_processor import (
            process_results_for_date_range,
        )

        result = process_results_for_date_range(start_date, end_date)
        logger.info(f"Results processing completed successfully: {result}")
        return True, result

    except ImportError:
        # Fallback to calling script directly
        logger.info("Using fallback script execution for results processing")
        command = f"cd {project_root} && python tools/bulk_uploader/bulk_upload_processor.py --type results --start-date {start_date.date()} --end-date {end_date.date()}"
        result = os.system(command)

        if result == 0:
            logger.info("Results processing completed successfully via script")
            return True, "Results data processed successfully"
        else:
            logger.error(f"Results processing failed with exit code: {result}")
            return False, f"Results processing failed with exit code: {result}"

    except Exception as e:
        logger.error(f"Error processing results data: {str(e)}")
        return False, str(e)


def process_data_by_type(data_type, start_date, end_date, logger):
    """Process data based on type selection"""
    results = []
    overall_success = True

    if data_type in ["cards", "both"]:
        logger.info("Starting cards data processing...")
        success, message = process_cards_data(start_date, end_date, logger)
        results.append(f"Cards: {message}")
        if not success:
            overall_success = False

    if data_type in ["results", "both"]:
        logger.info("Starting results data processing...")
        success, message = process_results_data(start_date, end_date, logger)
        results.append(f"Results: {message}")
        if not success:
            overall_success = False

    return overall_success, results


def generate_summary_report(
    data_type, start_date, end_date, success, results, processing_time
):
    """Generate a summary report of the processing"""
    report = {
        "processing_summary": {
            "data_type": data_type,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days + 1,
            },
            "status": "success" if success else "error",
            "processing_time_seconds": round(processing_time, 2),
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }
    }
    return report


def main():
    """Main processing function"""
    parser = argparse.ArgumentParser(
        description="Process horse racing data with date range and type selection"
    )
    parser.add_argument(
        "--start-date", required=True, help="Start date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--end-date", required=True, help="End date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--type",
        choices=["cards", "results", "both"],
        required=True,
        help="Type of data to process",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format for results",
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging()

    try:
        # Validate inputs
        start_date, end_date, days_count = validate_date_range(
            args.start_date, args.end_date
        )

        logger.info(f"Starting data processing...")
        logger.info(
            f"Date range: {start_date.date()} to {end_date.date()} ({days_count + 1} days)"
        )
        logger.info(f"Data type: {args.type}")

        # Record processing start time
        start_time = datetime.now()

        # Process data
        success, results = process_data_by_type(args.type, start_date, end_date, logger)

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Generate summary
        summary = generate_summary_report(
            args.type, start_date, end_date, success, results, processing_time
        )

        if args.output_format == "json":
            import json

            print(json.dumps(summary, indent=2))
        else:
            print(f"\n{'='*60}")
            print("PROCESSING SUMMARY")
            print(f"{'='*60}")
            print(f"Data Type: {args.type.upper()}")
            print(
                f"Date Range: {start_date.date()} to {end_date.date()} ({days_count + 1} days)"
            )
            print(f"Status: {'SUCCESS' if success else 'ERROR'}")
            print(f"Processing Time: {processing_time:.2f} seconds")
            print(f"\nResults:")
            for result in results:
                print(f"  - {result}")
            print(f"{'='*60}")

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
