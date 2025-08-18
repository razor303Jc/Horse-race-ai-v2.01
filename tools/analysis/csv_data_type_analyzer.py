#!/usr/bin/env python3
"""
CSV Data Type Analyzer
Comprehensive analysis of CSV files to understand data types, patterns, and data quality
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVDataTypeAnalyzer:
    def __init__(self):
        self.base_path = Path("/home/jc/Documents/Horse-race-ai-v2.02")
        self.results = {}

    def infer_data_types(self, series: pd.Series) -> Dict[str, Any]:
        """Infer detailed data types for a pandas series"""
        analysis = {
            "column_name": series.name,
            "total_rows": len(series),
            "non_null_count": series.count(),
            "null_count": series.isnull().sum(),
            "null_percentage": (series.isnull().sum() / len(series)) * 100,
            "pandas_dtype": str(series.dtype),
            "unique_values": series.nunique(),
            "sample_values": list(series.dropna().head(10).astype(str)),
        }

        # Remove nulls for analysis
        clean_series = series.dropna()

        if len(clean_series) == 0:
            analysis["inferred_type"] = "empty"
            return analysis

        # Check if it's numeric
        try:
            pd.to_numeric(clean_series)
            analysis["inferred_type"] = "numeric"
            analysis["is_integer"] = all(clean_series.astype(str).str.match(r"^-?\d+$"))
            analysis["is_decimal"] = any(clean_series.astype(str).str.contains("."))
            analysis["min_value"] = clean_series.min()
            analysis["max_value"] = clean_series.max()
            if analysis["is_integer"]:
                analysis["numeric_subtype"] = "integer"
            else:
                analysis["numeric_subtype"] = "float"
        except:
            analysis["inferred_type"] = "text"

            # Check for specific patterns
            str_series = clean_series.astype(str)

            # Date patterns
            date_patterns = [
                r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
                r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
                r"\d{1,2}-\w{3}-\d{4}",  # DD-MMM-YYYY
            ]

            # Time patterns
            time_patterns = [
                r"\d{1,2}:\d{2}",  # HH:MM
                r"\d{1,2}:\d{2}:\d{2}",  # HH:MM:SS
            ]

            # Currency patterns
            currency_patterns = [
                r"£[\d,]+",  # £1,000
                r"\$[\d,]+",  # $1,000
                r"[\d,]+\.\d{2}",  # 1,000.00
            ]

            # Distance/measurement patterns
            distance_patterns = [
                r"\d+[mfy]",  # 1m, 1f, 1y
                r"\d+f \d+y",  # 1f 2y
                r"\d+m \d+f",  # 1m 2f
            ]

            # Check patterns
            if any(str_series.str.match(pattern).any() for pattern in date_patterns):
                analysis["text_subtype"] = "date"
            elif any(str_series.str.match(pattern).any() for pattern in time_patterns):
                analysis["text_subtype"] = "time"
            elif any(
                str_series.str.match(pattern).any() for pattern in currency_patterns
            ):
                analysis["text_subtype"] = "currency"
            elif any(
                str_series.str.match(pattern).any() for pattern in distance_patterns
            ):
                analysis["text_subtype"] = "distance"
            elif (
                str_series.str.len().max() <= 10
                and analysis["unique_values"] < len(clean_series) * 0.1
            ):
                analysis["text_subtype"] = "categorical"
            else:
                analysis["text_subtype"] = "general_text"

            # Additional text analysis
            analysis["max_length"] = str_series.str.len().max()
            analysis["min_length"] = str_series.str.len().min()
            analysis["avg_length"] = str_series.str.len().mean()

        return analysis

    def analyze_csv_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single CSV file"""
        logger.info(f"📊 Analyzing: {file_path}")

        try:
            # Read CSV with minimal parsing to preserve raw data
            df = pd.read_csv(file_path, dtype=str, keep_default_na=False)

            analysis = {
                "file_path": str(file_path),
                "file_size_mb": file_path.stat().st_size / (1024 * 1024),
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": list(df.columns),
                "column_analysis": {},
            }

            # Analyze each column
            for col in df.columns:
                # Convert empty strings to NaN for proper null analysis
                series = df[col].replace("", np.nan)
                analysis["column_analysis"][col] = self.infer_data_types(series)

            return analysis

        except Exception as e:
            logger.error(f"❌ Error analyzing {file_path}: {e}")
            return {"error": str(e), "file_path": str(file_path)}

    def find_csv_files(self) -> List[Path]:
        """Find all CSV files in the project"""
        csv_files = []

        # Check daily downloads
        downloads_dir = self.base_path / "data" / "daily_downloads"
        if downloads_dir.exists():
            csv_files.extend(downloads_dir.rglob("*.csv"))

        # Check test data
        test_dir = self.base_path / "tests" / "mock_data"
        if test_dir.exists():
            csv_files.extend(test_dir.rglob("*.csv"))

        return sorted(csv_files)

    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of all analyses"""
        summary = {
            "total_files_analyzed": len(self.results),
            "files_with_errors": len(
                [r for r in self.results.values() if "error" in r]
            ),
            "column_type_distribution": {},
            "common_issues": [],
            "recommendations": [],
        }

        # Collect all column types
        type_counts = {}
        for file_analysis in self.results.values():
            if "column_analysis" in file_analysis:
                for col_name, col_analysis in file_analysis["column_analysis"].items():
                    col_type = col_analysis.get("inferred_type", "unknown")
                    subtype = col_analysis.get(
                        "text_subtype", col_analysis.get("numeric_subtype", "")
                    )
                    full_type = f"{col_type}_{subtype}" if subtype else col_type
                    type_counts[full_type] = type_counts.get(full_type, 0) + 1

        summary["column_type_distribution"] = type_counts

        # Find common issues
        high_null_columns = []
        mixed_type_columns = []

        for file_analysis in self.results.values():
            if "column_analysis" in file_analysis:
                for col_name, col_analysis in file_analysis["column_analysis"].items():
                    if col_analysis.get("null_percentage", 0) > 50:
                        high_null_columns.append(
                            (
                                file_analysis["file_path"],
                                col_name,
                                col_analysis["null_percentage"],
                            )
                        )

        if high_null_columns:
            summary["common_issues"].append(
                f"High null percentages found in {len(high_null_columns)} columns"
            )

        return summary

    def run_analysis(self) -> None:
        """Run complete analysis"""
        logger.info("🚀 Starting CSV Data Type Analysis")

        csv_files = self.find_csv_files()
        logger.info(f"📁 Found {len(csv_files)} CSV files")

        for csv_file in csv_files:
            self.results[str(csv_file)] = self.analyze_csv_file(csv_file)

        # Generate summary
        summary = self.generate_summary()

        # Save results
        output_path = (
            self.base_path / "tools" / "analysis" / "csv_analysis_results.json"
        )
        output_path.parent.mkdir(exist_ok=True, parents=True)

        with open(output_path, "w") as f:
            json.dump(
                {"summary": summary, "detailed_results": self.results},
                f,
                indent=2,
                default=str,
            )

        logger.info(f"💾 Results saved to: {output_path}")

        # Print summary
        self.print_summary(summary)

    def print_summary(self, summary: Dict[str, Any]) -> None:
        """Print analysis summary"""
        print("\n" + "=" * 70)
        print("📊 CSV DATA TYPE ANALYSIS SUMMARY")
        print("=" * 70)

        print(f"📁 Total files analyzed: {summary['total_files_analyzed']}")
        print(f"❌ Files with errors: {summary['files_with_errors']}")

        print(f"\n🔍 COLUMN TYPE DISTRIBUTION:")
        for col_type, count in sorted(
            summary["column_type_distribution"].items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            print(f"   {col_type}: {count} columns")

        if summary["common_issues"]:
            print(f"\n⚠️  COMMON ISSUES:")
            for issue in summary["common_issues"]:
                print(f"   • {issue}")

        print("\n" + "=" * 70)


def main():
    analyzer = CSVDataTypeAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
