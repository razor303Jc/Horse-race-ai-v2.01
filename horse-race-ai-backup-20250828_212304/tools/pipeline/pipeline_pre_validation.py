#!/usr/bin/env python3
"""
🔍 Pipeline Pre-Validation Check
================================

Integration script that runs enhanced date validation before pipeline execution.
This ensures data quality and prevents processing of stale or incorrect data.

Usage:
    python tools/pipeline/pipeline_pre_validation.py

Exit codes:
    0 - Validation passed, proceed with pipeline
    1 - Critical issues found, stop pipeline
    2 - Warnings detected, proceed with caution

Author: AI Assistant
Date: August 24, 2025
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PipelinePreValidator:
    """Pre-validation check for pipeline execution"""

    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = project_root / "data" / "daily_downloads"
        self.data_dir = data_dir

        # Import here to avoid circular imports
        from tools.pipeline.enhanced_date_validation import EnhancedDateValidator

        self.validator = EnhancedDateValidator(data_dir)

    def run_pre_validation(self) -> Dict:
        """
        Run comprehensive pre-validation checks before pipeline

        Returns:
            Dict with validation results and pipeline decision
        """
        logger.info("🔍 Starting pipeline pre-validation checks...")

        # Run enhanced date validation
        validation_results = self.validator.validate_all_downloads()

        # Extract key information for pipeline decision
        pipeline_decision = {
            "validation_results": validation_results,
            "proceed": validation_results["pipeline_recommendation"] != "stop",
            "warning": validation_results["pipeline_recommendation"] == "warning",
            "issues_found": len(validation_results["date_issues"]) > 0,
            "race_times_available": len(validation_results["race_times"]) > 0,
            "recommendation": validation_results["pipeline_recommendation"],
            "reason": validation_results.get("recommendation_reason", ""),
        }

        # Log decision
        if pipeline_decision["proceed"]:
            if pipeline_decision["warning"]:
                logger.warning("⚠️ Pipeline can proceed but with warnings")
            else:
                logger.info("✅ Pipeline validation passed - safe to proceed")
        else:
            logger.error("🛑 Pipeline validation failed - do not proceed")

        return pipeline_decision

    def check_for_fresh_data_needed(self) -> Dict:
        """
        Check if fresh data download is needed

        Returns:
            Dict indicating if download is needed and why
        """
        from datetime import datetime, timedelta

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        download_recommendation = {
            "download_needed": False,
            "reason": "",
            "target_dates": [],
            "missing_data_types": [],
        }

        # Check for today's cards data
        cards_today = self._check_data_for_date(today, "cards")
        if not cards_today["found"]:
            download_recommendation["download_needed"] = True
            download_recommendation["target_dates"].append(str(today))
            download_recommendation["missing_data_types"].append("cards")

        # Check for yesterday's results data
        results_yesterday = self._check_data_for_date(yesterday, "results")
        if not results_yesterday["found"]:
            download_recommendation["download_needed"] = True
            download_recommendation["target_dates"].append(str(yesterday))
            download_recommendation["missing_data_types"].append("results")

        if download_recommendation["download_needed"]:
            missing_types = ", ".join(download_recommendation["missing_data_types"])
            missing_dates = ", ".join(download_recommendation["target_dates"])
            download_recommendation["reason"] = (
                f"Missing {missing_types} data for {missing_dates}"
            )
        else:
            download_recommendation["reason"] = "All required data is available"

        return download_recommendation

    def _check_data_for_date(self, target_date, data_type: str) -> Dict:
        """Check if data exists for a specific date and type"""
        date_str = target_date.strftime("%Y-%m-%d")

        # Check processed files
        processed_dir = self.data_dir / "processed" / date_str
        if processed_dir.exists():
            zip_files = list(processed_dir.glob(f"*{data_type}*.zip"))
            if zip_files:
                return {"found": True, "location": "processed", "files": zip_files}

        # Check raw data directories
        if data_type == "cards":
            data_dir = self.data_dir / "cards_data"
        else:
            data_dir = self.data_dir / "results_data"

        if data_dir.exists():
            # Check for CSV files with target date
            csv_files = []
            for csv_path in data_dir.rglob("*.csv"):
                if self._csv_contains_date(csv_path, target_date):
                    csv_files.append(csv_path)

            if csv_files:
                return {"found": True, "location": "raw", "files": csv_files}

        return {"found": False, "location": None, "files": []}

    def _csv_contains_date(self, csv_path: Path, target_date) -> bool:
        """Check if CSV file contains data for target date"""
        try:
            import pandas as pd

            df = pd.read_csv(csv_path)

            date_columns = ["Date", "date", "race_date"]
            target_str = target_date.strftime("%Y-%m-%d")

            for col in date_columns:
                if col in df.columns:
                    if target_str in df[col].astype(str).values:
                        return True

        except Exception:
            pass

        return False

    def generate_user_report(self, validation_results: Dict) -> str:
        """Generate a user-friendly report"""
        report = []
        report.append("=" * 60)
        report.append("🔍 PIPELINE PRE-VALIDATION REPORT")
        report.append("=" * 60)

        decision = validation_results

        report.append(
            f"📅 Validation Date: {decision['validation_results']['today_date']}"
        )
        report.append(
            f"📁 Data Directory: {decision['validation_results']['data_directory']}"
        )

        if decision["issues_found"]:
            report.append("\n⚠️ ISSUES DETECTED:")
            for issue in decision["validation_results"]["date_issues"]:
                report.append(f"   • {issue}")
        else:
            report.append("\n✅ No critical issues detected")

        if decision["race_times_available"]:
            report.append("\n🏁 RACE TIMES FOUND:")
            for date, times in decision["validation_results"]["race_times"].items():
                report.append(f"   📅 {date}:")
                report.append(f"      🌅 First: {times['first_race']}")
                report.append(f"      🌆 Last:  {times['last_race']}")
                report.append(f"      🏇 Races: {times['total_races']}")
        else:
            report.append("\n⚠️ No race times detected in current data")

        # Pipeline recommendation
        recommendation = decision["recommendation"].upper()
        report.append(f"\n🎯 PIPELINE RECOMMENDATION: {recommendation}")
        report.append(f"   Reason: {decision['reason']}")

        if recommendation == "STOP":
            report.append("\n🛑 ACTION REQUIRED:")
            report.append("   1. Check if racing services have updated their data")
            report.append("   2. Re-run the auto-downloader to get fresh data")
            report.append("   3. Verify today's racing schedule exists")
            report.append("   4. Re-run this validation after getting fresh data")

        elif recommendation == "WARNING":
            report.append("\n⚠️ PROCEED WITH CAUTION:")
            report.append("   1. Monitor pipeline results carefully")
            report.append("   2. Verify AI selections match expected races")
            report.append("   3. Consider downloading fresh data if available")

        else:
            report.append("\n🚀 READY TO PROCEED:")
            report.append("   All validations passed - pipeline can run safely")

        report.append("\n" + "=" * 60)

        return "\n".join(report)


def main():
    """Main execution function"""
    logger.info("🚀 Starting pipeline pre-validation...")

    # Initialize validator
    validator = PipelinePreValidator()

    # Run validation
    results = validator.run_pre_validation()

    # Generate and display report
    report = validator.generate_user_report(results)
    print(report)

    # Check if fresh data download is needed
    download_check = validator.check_for_fresh_data_needed()
    if download_check["download_needed"]:
        print("\n📥 DOWNLOAD RECOMMENDATION:")
        print(f"   {download_check['reason']}")
        print("   Consider running auto-downloader before pipeline")

    # Save detailed results
    output_file = (
        project_root / "data" / "daily_downloads" / "pipeline_pre_validation.json"
    )
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    logger.info("📄 Validation results saved: %s", output_file)

    # Return appropriate exit code
    if results["recommendation"] == "stop":
        return 1
    elif results["recommendation"] == "warning":
        return 2
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
