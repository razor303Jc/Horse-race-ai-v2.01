#!/usr/bin/env python3
"""
Web App Racing Analysis Integration
==================================
Simple interface for web app to request racing analysis reports.
"""

import json
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path


class WebAppRacingInterface:
    """Interface for web app to interact with racing analysis."""

    def __init__(self, reports_dir="reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)

    def request_analysis(self, target_date="today", format_type="json"):
        """Request racing analysis for a specific date."""
        try:
            # Run background analyzer
            cmd = [
                "python3",
                "background_racing_analyzer.py",
                "--date",
                target_date,
                "--output",
                str(self.reports_dir),
                "--background",
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=1800
            )  # 30 min timeout

            if result.returncode == 0:
                return self._get_latest_report(target_date, format_type)
            else:
                return {"error": f"Analysis failed: {result.stderr}"}

        except subprocess.TimeoutExpired:
            return {"error": "Analysis timed out after 30 minutes"}
        except Exception as e:
            return {"error": f"Failed to run analysis: {e}"}

    def _get_latest_report(self, target_date, format_type):
        """Get the latest report for a date."""
        try:
            if target_date == "today":
                date_str = date.today().strftime("%Y-%m-%d")
            else:
                date_str = target_date

            if format_type == "json":
                pattern = f"racing_data_{date_str}_*.json"
                files = list(self.reports_dir.glob(pattern))
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    with open(latest_file) as f:
                        return json.load(f)

            elif format_type == "html":
                pattern = f"racing_report_{date_str}_*.html"
                files = list(self.reports_dir.glob(pattern))
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    with open(latest_file) as f:
                        return {"html_content": f.read(), "file_path": str(latest_file)}

            return {"error": "No report found for the specified date"}

        except Exception as e:
            return {"error": f"Failed to read report: {e}"}

    def get_available_reports(self):
        """Get list of available reports."""
        try:
            json_files = list(self.reports_dir.glob("racing_data_*.json"))
            html_files = list(self.reports_dir.glob("racing_report_*.html"))

            reports = []
            for file in json_files:
                try:
                    parts = file.stem.split("_")
                    if len(parts) >= 4:
                        date_part = parts[2]
                        time_part = parts[3]
                        reports.append(
                            {
                                "date": date_part,
                                "time": time_part,
                                "json_file": str(file),
                                "html_file": str(file)
                                .replace("racing_data_", "racing_report_")
                                .replace(".json", ".html"),
                            }
                        )
                except:
                    continue

            return {"reports": reports}

        except Exception as e:
            return {"error": f"Failed to list reports: {e}"}


def main():
    """Command line interface for web app integration."""
    import argparse

    parser = argparse.ArgumentParser(description="Web App Racing Interface")
    parser.add_argument("action", choices=["analyze", "get_report", "list_reports"])
    parser.add_argument("--date", default="today", help="Target date")
    parser.add_argument(
        "--format", choices=["json", "html"], default="json", help="Output format"
    )
    parser.add_argument("--reports-dir", default="reports", help="Reports directory")

    args = parser.parse_args()

    interface = WebAppRacingInterface(args.reports_dir)

    if args.action == "analyze":
        print("🔄 Starting racing analysis...")
        result = interface.request_analysis(args.date, args.format)
        print(json.dumps(result, indent=2))

    elif args.action == "get_report":
        result = interface._get_latest_report(args.date, args.format)
        print(json.dumps(result, indent=2))

    elif args.action == "list_reports":
        result = interface.get_available_reports()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
