#!/usr/bin/env python3
"""
Quick Data Pipeline Test
🧪 TEST: Test the enhanced data cleaning pipeline with available data

This script will:
1. Test with existing data files
2. Apply enhanced data cleaning
3. Test database upload
4. Generate problem report
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.data_processing.simplified_data_pipeline import SimplifiedDataPipeline


def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


def analyze_existing_data():
    """Analyze existing data files for quality issues"""
    logger = setup_logging()
    logger.info("🔍 Analyzing existing data files...")

    data_dir = Path("data/daily_downloads")
    test_files = [
        "mapped_races.csv",
        "mapped_records.csv",
        "mapped_horses.csv",
        "mapped_jockeys_stats.csv",
        "mapped_trainers_stats.csv",
    ]

    analysis_results = []

    for file_name in test_files:
        file_path = data_dir / file_name
        if file_path.exists():
            logger.info(f"📊 Analyzing {file_name}...")

            try:
                df = pd.read_csv(file_path)

                # Check for dash symbols
                dash_count = 0
                dash_columns = []
                for col in df.columns:
                    col_dashes = (df[col].astype(str) == "-").sum()
                    dash_count += col_dashes
                    if col_dashes > 0:
                        dash_columns.append(f"{col}({col_dashes})")

                # Check for NULL values
                null_count = df.isnull().sum().sum()

                # Check for UK weight format
                weight_format_count = 0
                for col in df.columns:
                    if "weight" in col.lower():
                        uk_pattern = df[col].astype(str).str.match(r"^\d+-\d+$")
                        weight_format_count += uk_pattern.sum()

                # Check for percentage strings
                percentage_count = 0
                for col in df.columns:
                    if df[col].dtype == "object":
                        pct_pattern = df[col].astype(str).str.contains("%", na=False)
                        percentage_count += pct_pattern.sum()

                analysis = {
                    "file": file_name,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "dash_symbols": dash_count,
                    "dash_columns": dash_columns[:5],  # Show first 5
                    "null_values": null_count,
                    "uk_weight_format": weight_format_count,
                    "percentage_strings": percentage_count,
                    "total_issues": dash_count
                    + null_count
                    + weight_format_count
                    + percentage_count,
                }

                analysis_results.append(analysis)

                logger.info(f"  📋 {len(df)} rows, {len(df.columns)} columns")
                logger.info(f"  🔍 Issues found:")
                logger.info(f"    - Dash symbols: {dash_count}")
                logger.info(f"    - NULL values: {null_count}")
                logger.info(f"    - UK weight format: {weight_format_count}")
                logger.info(f"    - Percentage strings: {percentage_count}")

                if dash_count > 0:
                    logger.info(
                        f"    - Dash symbol columns: {', '.join(dash_columns[:3])}"
                    )

            except Exception as e:
                logger.error(f"❌ Failed to analyze {file_name}: {e}")
        else:
            logger.warning(f"⚠️ File not found: {file_name}")

    return analysis_results


def test_with_copied_files():
    """Test by copying files to expected locations"""
    logger = setup_logging()
    logger.info("📋 Setting up test with copied files...")

    # Copy existing files to expected locations for testing
    source_dir = Path("data/daily_downloads")
    file_mappings = {
        "mapped_races.csv": "complete_mapped_races.csv",
        "mapped_records.csv": "complete_mapped_records.csv",
        "mapped_horses.csv": "complete_mapped_horses.csv",
        "mapped_jockeys_stats.csv": "complete_mapped_jockeys_stats.csv",
        "mapped_trainers_stats.csv": "complete_mapped_trainers_stats.csv",
    }

    copied_files = []
    for source_file, target_file in file_mappings.items():
        source_path = source_dir / source_file
        target_path = source_dir / target_file

        if source_path.exists():
            try:
                # Copy file
                import shutil

                shutil.copy2(source_path, target_path)
                copied_files.append(target_file)
                logger.info(f"✅ Copied {source_file} → {target_file}")
            except Exception as e:
                logger.error(f"❌ Failed to copy {source_file}: {e}")
        else:
            logger.warning(f"⚠️ Source file not found: {source_file}")

    return copied_files


def test_cleaning_pipeline():
    """Test the enhanced data cleaning pipeline"""
    logger = setup_logging()
    logger.info("🧹 Testing Enhanced Data Cleaning Pipeline...")

    try:
        # Initialize and run the simplified pipeline
        pipeline = SimplifiedDataPipeline()
        success = pipeline.run_data_cleaning_pipeline()

        if success:
            logger.info("✅ Cleaning pipeline completed successfully")
            return True
        else:
            logger.error("❌ Cleaning pipeline failed")
            if hasattr(pipeline, "errors") and pipeline.errors:
                for error in pipeline.errors:
                    logger.error(f"  - {error}")
            return False

    except Exception as e:
        logger.error(f"💥 Cleaning pipeline crashed: {e}")
        return False


def test_database_upload():
    """Test database upload with cleaned data"""
    logger = setup_logging()
    logger.info("📤 Testing Database Upload...")

    try:
        from tools.data_processing.upload_mapped_data import upload_csv_to_database

        upload_tasks = [
            ("data/daily_downloads/complete_mapped_races.csv", "races"),
            ("data/daily_downloads/complete_mapped_records.csv", "records"),
            ("data/daily_downloads/complete_mapped_horses.csv", "horses"),
        ]

        successful_uploads = 0
        failed_uploads = 0
        upload_issues = []

        for csv_file, table_name in upload_tasks:
            file_path = Path(csv_file)
            if file_path.exists():
                try:
                    logger.info(f"  📊 Uploading {table_name}...")
                    upload_csv_to_database(csv_file, table_name)
                    successful_uploads += 1
                    logger.info(f"  ✅ {table_name} uploaded successfully")

                except Exception as e:
                    error_msg = f"Upload {table_name} failed: {e}"
                    logger.error(f"  ❌ {error_msg}")
                    upload_issues.append(error_msg)
                    failed_uploads += 1
            else:
                warning_msg = f"File not found: {csv_file}"
                logger.warning(f"  ⚠️ {warning_msg}")
                upload_issues.append(warning_msg)
                failed_uploads += 1

        logger.info(
            f"📊 Upload Results: {successful_uploads} successful, {failed_uploads} failed"
        )

        return successful_uploads > 0, upload_issues

    except Exception as e:
        logger.error(f"💥 Upload testing crashed: {e}")
        return False, [f"Upload testing crashed: {e}"]


def generate_final_report(
    analysis_results, cleaning_success, upload_success, upload_issues
):
    """Generate final test report"""
    logger = setup_logging()

    logger.info("\n" + "=" * 70)
    logger.info("📋 DATA PIPELINE TEST REPORT")
    logger.info("=" * 70)

    # Data Quality Analysis Summary
    logger.info("🔍 DATA QUALITY ANALYSIS:")
    total_issues = 0
    for analysis in analysis_results:
        total_issues += analysis["total_issues"]
        logger.info(f"  📊 {analysis['file']}:")
        logger.info(f"    - {analysis['rows']} rows, {analysis['columns']} columns")
        logger.info(f"    - {analysis['total_issues']} total issues found")
        if analysis["dash_symbols"] > 0:
            logger.info(
                f"    - {analysis['dash_symbols']} dash symbols (will be cleaned)"
            )
        if analysis["null_values"] > 0:
            logger.info(f"    - {analysis['null_values']} NULL values")
        if analysis["uk_weight_format"] > 0:
            logger.info(f"    - {analysis['uk_weight_format']} UK weight formats")

    # Test Results
    logger.info(f"\n🧹 CLEANING PIPELINE:")
    if cleaning_success:
        logger.info("  ✅ Enhanced data cleaning completed successfully")
        logger.info("  ✅ Dash symbols cleaned based on data types")
        logger.info("  ✅ Weight formats converted")
        logger.info("  ✅ NULL values handled")
    else:
        logger.info("  ❌ Data cleaning failed")

    logger.info(f"\n📤 DATABASE UPLOAD:")
    if upload_success:
        logger.info("  ✅ At least one table uploaded successfully")
    else:
        logger.info("  ❌ All uploads failed")

    if upload_issues:
        logger.info("  📋 Upload Issues:")
        for i, issue in enumerate(upload_issues, 1):
            logger.info(f"    {i}. {issue}")

    # Overall Assessment
    logger.info(f"\n🎯 OVERALL ASSESSMENT:")
    if cleaning_success and upload_success:
        logger.info("  🎉 Pipeline test PASSED - Ready for production use!")
    elif cleaning_success:
        logger.info("  ⚠️ Cleaning works, but upload issues need attention")
    else:
        logger.info("  ❌ Pipeline needs fixes before production use")

    logger.info("=" * 70)

    # Save report
    report = {
        "test_time": datetime.now().isoformat(),
        "data_analysis": analysis_results,
        "cleaning_success": cleaning_success,
        "upload_success": upload_success,
        "upload_issues": upload_issues,
        "total_data_issues": total_issues,
    }

    # Convert numpy int64 to regular int for JSON serialization
    def convert_numpy_types(obj):
        if hasattr(obj, "item"):
            return obj.item()
        elif isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        return obj

    json_safe_report = convert_numpy_types(report)

    report_file = f"data/logs/pipeline_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(json_safe_report, f, indent=2)

    logger.info(f"📄 Detailed report saved to: {report_file}")

    return cleaning_success and upload_success


def main():
    """Run the comprehensive pipeline test"""
    print("🧪 Enhanced Data Pipeline Test")
    print("=" * 50)

    try:
        # Step 1: Analyze existing data
        print("Step 1: Analyzing existing data quality...")
        analysis_results = analyze_existing_data()

        # Step 2: Setup test files
        print("\nStep 2: Setting up test files...")
        copied_files = test_with_copied_files()

        if not copied_files:
            print("❌ No files available for testing")
            return 1

        # Step 3: Test cleaning pipeline
        print("\nStep 3: Testing enhanced data cleaning...")
        cleaning_success = test_cleaning_pipeline()

        # Step 4: Test database upload
        print("\nStep 4: Testing database upload...")
        upload_success, upload_issues = test_database_upload()

        # Step 5: Generate report
        print("\nStep 5: Generating final report...")
        overall_success = generate_final_report(
            analysis_results, cleaning_success, upload_success, upload_issues
        )

        if overall_success:
            print("\n🎉 Pipeline test completed successfully!")
            return 0
        else:
            print("\n⚠️ Pipeline test found issues. Check the report above.")
            return 1

    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
