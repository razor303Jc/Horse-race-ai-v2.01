#!/usr/bin/env python3
"""
Process Recovered Racing Data
Import the recovered CSV data from trash into the database
"""

import logging
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "tools" / "data_processing"))

from complete_csv_processor import CompleteCsvProcessor


def setup_logging():
    """Setup comprehensive logging"""
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/recovered_data_processing.log"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


def prepare_recovered_data():
    """Copy recovered data to expected location for processing"""
    logger = logging.getLogger(__name__)

    # Source and destination paths
    recovered_base = (
        project_root / "data" / "recovered_from_trash" / "extracted_results"
    )
    staging_base = project_root / "data" / "staging_recovered"

    # Create staging directory
    staging_base.mkdir(exist_ok=True)
    races_dir = staging_base / "races"
    records_dir = staging_base / "records"
    races_dir.mkdir(exist_ok=True)
    records_dir.mkdir(exist_ok=True)

    # Copy files to staging
    source_files = {
        "races": recovered_base / "races" / "races.csv",
        "records": recovered_base / "records" / "records.csv",
    }

    dest_files = {
        "races": races_dir / "races.csv",
        "records": records_dir / "records.csv",
    }

    copied_files = []
    for table, source in source_files.items():
        if source.exists():
            dest = dest_files[table]
            shutil.copy2(source, dest)
            copied_files.append(str(dest))
            logger.info(f"✅ Copied {table}: {source} -> {dest}")
        else:
            logger.warning(f"⚠️ Missing {table}: {source}")

    return copied_files


def process_recovered_data():
    """Process the recovered racing data"""
    logger = setup_logging()
    logger.info("🔄 Starting recovered data processing...")

    # Prepare data files
    copied_files = prepare_recovered_data()
    if not copied_files:
        logger.error("❌ No data files prepared")
        return False

    # Update mapping config temporarily
    config_file = project_root / "config" / "complete_csv_column_mapping.json"
    import json

    # Load original config
    with open(config_file, "r") as f:
        config = json.load(f)

    # Update paths to point to staging
    staging_base = project_root / "data" / "staging_recovered"
    config["table_mappings"]["races"]["csv_files"] = [
        str(staging_base / "races" / "races.csv")
    ]
    config["table_mappings"]["records"]["csv_files"] = [
        str(staging_base / "records" / "records.csv")
    ]

    # Save temporary config
    temp_config_file = project_root / "config" / "temp_recovered_mapping.json"
    with open(temp_config_file, "w") as f:
        json.dump(config, f, indent=2)

    # Now run the processor
    processor = CompleteCsvProcessor()

    # Update processor to use temp config
    processor.config_file = temp_config_file

    try:
        result = processor.process_all_csv_files()

        if result:
            logger.info("✅ Successfully processed recovered data")
        else:
            logger.error("❌ Failed to process recovered data")

        return result

    except Exception as e:
        logger.error(f"❌ Error processing recovered data: {e}")
        return False

    finally:
        # Cleanup temp files
        if temp_config_file.exists():
            temp_config_file.unlink()
            logger.info("🧹 Cleaned up temporary config")


if __name__ == "__main__":
    success = process_recovered_data()
    if success:
        print("✅ Recovered data processing completed successfully")
        sys.exit(0)
    else:
        print("❌ Recovered data processing failed")
        sys.exit(1)
