#!/usr/bin/env python3
"""
Critical CSV Data Quality Analyzer
Comprehensive analysis of all CSV files for data integrity issues
"""

import os
import pandas as pd
import numpy as np
import logging
import json
import re
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Tuple
import warnings

warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CSVDataQualityAnalyzer:
    """Critical CSV data quality analyzer for racing data"""

    def __init__(self):
        self.workspace_path = Path("/home/jc/Documents/Horse-race-ai-v2.04")
        self.analysis_results = {}
        self.critical_issues = []
        self.warning_issues = []

    def find_csv_files(self, target_dates: List[str] = None) -> Dict[str, List[str]]:
        """Find all CSV files, focusing on target dates"""
        logger.info("🔍 Scanning for CSV files...")

        if target_dates is None:
            target_dates = ["2025-08-27", "2025-08-22", "2025-08-23"]

        csv_files = {"target_date_files": [], "other_files": [], "all_files": []}

        # Search patterns
        search_paths = [
            self.workspace_path / "temp_extract",
            self.workspace_path / "temp_card_processing",
            self.workspace_path / "data" / "daily_downloads",
            self.workspace_path / "tools" / "temp_card_processing",
        ]

        for search_path in search_paths:
            if search_path.exists():
                for csv_file in search_path.rglob("*.csv"):
                    csv_files["all_files"].append(str(csv_file))

                    # Check if file relates to target dates
                    file_str = str(csv_file)
                    is_target_file = any(
                        target_date in file_str for target_date in target_dates
                    )

                    if is_target_file:
                        csv_files["target_date_files"].append(str(csv_file))
                    else:
                        csv_files["other_files"].append(str(csv_file))

        logger.info(f"📊 Found {len(csv_files['all_files'])} total CSV files")
        logger.info(f"🎯 Found {len(csv_files['target_date_files'])} target date files")

        return csv_files

    def analyze_cell_content(self, value: Any) -> Dict[str, Any]:
        """Analyze individual cell content for issues"""
        issues = {
            "has_percent_symbol": False,
            "has_dash": False,
            "is_null": False,
            "is_blank": False,
            "has_special_chars": False,
            "numeric_issues": [],
            "date_issues": [],
            "text_issues": [],
            "raw_value": value,
        }

        # Handle different value types
        if pd.isna(value) or value is None:
            issues["is_null"] = True
            return issues

        # Convert to string for analysis
        str_value = str(value).strip()

        if str_value == "" or str_value.lower() in ["", "none", "null", "nan"]:
            issues["is_blank"] = True
            return issues

        # Check for problematic characters
        if "%" in str_value:
            issues["has_percent_symbol"] = True

        if "-" in str_value and str_value != "-":
            issues["has_dash"] = True

        # Check for special characters that might cause issues
        special_chars = [
            "#",
            "$",
            "@",
            "&",
            "*",
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
            "|",
            "\\",
            "/",
            "?",
            "<",
            ">",
            "~",
            "`",
        ]
        if any(char in str_value for char in special_chars):
            issues["has_special_chars"] = True

        # Check if it looks like a date
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
            r"\d{2}-\d{2}-\d{4}",  # MM-DD-YYYY
            r"\d{1,2}:\d{2}",  # HH:MM
        ]

        for pattern in date_patterns:
            if re.search(pattern, str_value):
                try:
                    # Try to parse various date formats
                    test_formats = [
                        "%Y-%m-%d",
                        "%m/%d/%Y",
                        "%m-%d-%Y",
                        "%H:%M",
                        "%Y-%m-%d %H:%M:%S",
                    ]
                    parsed = False
                    for fmt in test_formats:
                        try:
                            datetime.strptime(str_value, fmt)
                            parsed = True
                            break
                        except:
                            continue
                    if not parsed:
                        issues["date_issues"].append(
                            f"Invalid date format: {str_value}"
                        )
                except:
                    issues["date_issues"].append(f"Unparseable date: {str_value}")

        # Check if it looks numeric but has issues
        if re.search(r"[\d.]", str_value):
            try:
                float(str_value)
            except ValueError:
                if not any(char.isalpha() for char in str_value):
                    issues["numeric_issues"].append(
                        f"Numeric-looking but not parseable: {str_value}"
                    )

        return issues

    def analyze_column_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data types and consistency within columns"""
        column_analysis = {}

        for col in df.columns:
            column_data = {
                "dtype": str(df[col].dtype),
                "null_count": df[col].isnull().sum(),
                "unique_count": df[col].nunique(),
                "sample_values": df[col].dropna().head(5).tolist(),
                "data_type_consistency": True,
                "issues": [],
            }

            # Check for mixed data types
            non_null_values = df[col].dropna()
            if len(non_null_values) > 0:
                # Check if all values are consistent type
                value_types = [type(val).__name__ for val in non_null_values]
                unique_types = set(value_types)

                if len(unique_types) > 1:
                    column_data["data_type_consistency"] = False
                    column_data["issues"].append(
                        f"Mixed data types found: {unique_types}"
                    )

                # Check for problematic values
                for idx, value in non_null_values.head(100).items():
                    cell_issues = self.analyze_cell_content(value)

                    if cell_issues["has_percent_symbol"]:
                        column_data["issues"].append("Contains % symbols")
                        break
                    if cell_issues["has_dash"] and col.lower() not in [
                        "name",
                        "course",
                        "description",
                    ]:
                        column_data["issues"].append("Contains dash characters")
                        break
                    if cell_issues["has_special_chars"]:
                        column_data["issues"].append("Contains special characters")
                        break
                    if cell_issues["numeric_issues"]:
                        column_data["issues"].extend(cell_issues["numeric_issues"])
                        break
                    if cell_issues["date_issues"]:
                        column_data["issues"].extend(cell_issues["date_issues"])
                        break

            column_analysis[col] = column_data

        return column_analysis

    def analyze_csv_file(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive analysis of a single CSV file"""
        logger.info(f"📋 Analyzing: {os.path.basename(file_path)}")

        analysis = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": 0,
            "readable": False,
            "row_count": 0,
            "column_count": 0,
            "columns": [],
            "column_analysis": {},
            "header_issues": [],
            "critical_issues": [],
            "warning_issues": [],
            "data_sample": [],
            "encoding_issues": False,
            "analysis_timestamp": datetime.now().isoformat(),
        }

        try:
            # File size
            analysis["file_size"] = os.path.getsize(file_path)

            # Try to read with different encodings
            encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
            df = None

            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    analysis["readable"] = True
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    analysis["critical_issues"].append(
                        f"Read error with {encoding}: {str(e)}"
                    )

            if df is None:
                analysis["critical_issues"].append("Cannot read file with any encoding")
                return analysis

            # Basic info
            analysis["row_count"] = len(df)
            analysis["column_count"] = len(df.columns)
            analysis["columns"] = df.columns.tolist()

            # Header analysis
            for col in df.columns:
                if pd.isna(col) or str(col).strip() == "":
                    analysis["header_issues"].append("Empty or null column name found")
                if str(col).startswith("Unnamed:"):
                    analysis["header_issues"].append(f"Unnamed column found: {col}")
                if "%" in str(col):
                    analysis["header_issues"].append(f"Column name contains %: {col}")
                if any(char in str(col) for char in ["#", "$", "@"]):
                    analysis["header_issues"].append(
                        f"Column name contains special chars: {col}"
                    )

            # Column-level analysis
            analysis["column_analysis"] = self.analyze_column_data_types(df)

            # Sample data for inspection
            if len(df) > 0:
                sample_size = min(3, len(df))
                analysis["data_sample"] = df.head(sample_size).to_dict("records")

            # Critical issues detection
            for col, col_data in analysis["column_analysis"].items():
                if col_data["null_count"] == len(df):
                    analysis["critical_issues"].append(
                        f"Column '{col}' is completely empty"
                    )

                if col_data["null_count"] > len(df) * 0.5:
                    analysis["warning_issues"].append(
                        f"Column '{col}' has >50% null values ({col_data['null_count']}/{len(df)})"
                    )

                if col_data["issues"]:
                    for issue in col_data["issues"]:
                        if any(
                            keyword in issue.lower()
                            for keyword in ["%", "special char", "mixed data"]
                        ):
                            analysis["critical_issues"].append(
                                f"Column '{col}': {issue}"
                            )
                        else:
                            analysis["warning_issues"].append(
                                f"Column '{col}': {issue}"
                            )

            # Check for completely empty rows
            empty_rows = df.isnull().all(axis=1).sum()
            if empty_rows > 0:
                analysis["warning_issues"].append(
                    f"Found {empty_rows} completely empty rows"
                )

            # Check for duplicate headers
            duplicate_headers = [
                col for col in df.columns if df.columns.tolist().count(col) > 1
            ]
            if duplicate_headers:
                analysis["critical_issues"].append(
                    f"Duplicate column names: {duplicate_headers}"
                )

        except Exception as e:
            analysis["critical_issues"].append(f"Analysis failed: {str(e)}")
            logger.error(f"❌ Failed to analyze {file_path}: {e}")

        return analysis

    def generate_comprehensive_report(self, file_analyses: List[Dict]) -> str:
        """Generate comprehensive data quality report"""

        total_files = len(file_analyses)
        critical_files = sum(
            1 for analysis in file_analyses if analysis["critical_issues"]
        )
        warning_files = sum(
            1 for analysis in file_analyses if analysis["warning_issues"]
        )

        report = f"""
# CRITICAL CSV DATA QUALITY ANALYSIS REPORT
## Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🚨 EXECUTIVE SUMMARY
- **Total Files Analyzed**: {total_files}
- **Files with Critical Issues**: {critical_files}
- **Files with Warnings**: {warning_files}
- **Clean Files**: {total_files - critical_files}

## 🔴 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION

"""

        critical_count = 0
        for analysis in file_analyses:
            if analysis["critical_issues"]:
                critical_count += 1
                report += f"""
### {critical_count}. {analysis['file_name']}
**Path**: `{analysis['file_path']}`
**Size**: {analysis['file_size']:,} bytes | **Rows**: {analysis['row_count']:,} | **Columns**: {analysis['column_count']}

**CRITICAL ISSUES:**
"""
                for issue in analysis["critical_issues"]:
                    report += f"- ❌ {issue}\n"

                if analysis["header_issues"]:
                    report += "\n**HEADER ISSUES:**\n"
                    for issue in analysis["header_issues"]:
                        report += f"- ⚠️ {issue}\n"

        report += f"""

## ⚠️ WARNING ISSUES NEEDING ATTENTION

"""

        warning_count = 0
        for analysis in file_analyses:
            if analysis["warning_issues"] and not analysis["critical_issues"]:
                warning_count += 1
                report += f"""
### {warning_count}. {analysis['file_name']}
**Path**: `{analysis['file_path']}`
**Rows**: {analysis['row_count']:,} | **Columns**: {analysis['column_count']}

**WARNING ISSUES:**
"""
                for issue in analysis["warning_issues"]:
                    report += f"- ⚠️ {issue}\n"

        # Detailed column analysis for critical files
        report += f"""

## 📊 DETAILED COLUMN ANALYSIS

"""

        for analysis in file_analyses:
            if analysis["critical_issues"]:
                report += f"""
### {analysis['file_name']} - Column Details
**Columns**: {', '.join(analysis['columns'])}

"""
                for col, col_data in analysis["column_analysis"].items():
                    if col_data["issues"]:
                        report += f"""
**{col}**:
- Data Type: {col_data['dtype']}
- Null Count: {col_data['null_count']}/{analysis['row_count']} ({(col_data['null_count']/max(analysis['row_count'], 1)*100):.1f}%)
- Unique Values: {col_data['unique_count']}
- Issues: {', '.join(col_data['issues'])}
- Sample Values: {col_data['sample_values']}
"""

        # Sample data for critical files
        report += f"""

## 🔍 SAMPLE DATA FROM PROBLEMATIC FILES

"""

        for analysis in file_analyses:
            if analysis["critical_issues"] and analysis["data_sample"]:
                report += f"""
### {analysis['file_name']} - Sample Rows
"""
                for i, row in enumerate(analysis["data_sample"][:2], 1):
                    report += f"\n**Row {i}**: {row}\n"

        # Recommendations
        report += f"""

## 💡 RECOMMENDATIONS FOR IMMEDIATE ACTION

### Critical Actions Required:
1. **Data Cleaning**: Remove or fix % symbols, special characters, and invalid formats
2. **Null Value Handling**: Address columns with excessive null values
3. **Header Standardization**: Fix unnamed columns and problematic column names
4. **Encoding Verification**: Ensure consistent UTF-8 encoding across all files
5. **Data Type Consistency**: Standardize data types within columns

### Specific Fixes Needed:
- Remove percentage symbols (%) from numeric data
- Standardize dash (-) usage in text fields
- Clean special characters from data fields
- Validate date formats and fix inconsistencies
- Handle null/blank values appropriately

### Prevention Measures:
- Implement data validation at source
- Add automated data quality checks to pipeline
- Standardize CSV export formats
- Regular data quality monitoring

## ⚡ IMPACT ASSESSMENT
**HIGH RISK**: Files with critical issues will cause pipeline failures
**MEDIUM RISK**: Warning issues may cause data inconsistencies
**ACTION REQUIRED**: Address critical issues before running any data processing

---
*This analysis is critical for system reliability. Address all critical issues immediately.*
"""

        return report

    def run_full_analysis(self, target_dates: List[str] = None) -> str:
        """Run complete CSV analysis and generate report"""
        logger.info("🚀 Starting critical CSV data quality analysis...")

        # Find CSV files
        csv_files = self.find_csv_files(target_dates)

        # Focus on target date files first, then others
        priority_files = csv_files["target_date_files"][
            :10
        ]  # Limit to prevent overload
        other_files = csv_files["other_files"][:5]  # Sample of other files

        all_analyses = []

        # Analyze priority files first
        logger.info(f"🎯 Analyzing {len(priority_files)} priority files...")
        for file_path in priority_files:
            analysis = self.analyze_csv_file(file_path)
            all_analyses.append(analysis)

            # Track critical issues
            if analysis["critical_issues"]:
                self.critical_issues.extend(analysis["critical_issues"])

        # Analyze sample of other files
        logger.info(f"📂 Analyzing {len(other_files)} additional files...")
        for file_path in other_files:
            analysis = self.analyze_csv_file(file_path)
            all_analyses.append(analysis)

        # Generate comprehensive report
        report = self.generate_comprehensive_report(all_analyses)

        # Save report
        report_path = (
            self.workspace_path
            / f"CSV_DATA_QUALITY_CRITICAL_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"📄 Critical analysis report saved to: {report_path}")

        # Print summary
        critical_files = sum(
            1 for analysis in all_analyses if analysis["critical_issues"]
        )
        logger.info(
            f"🚨 SUMMARY: {critical_files}/{len(all_analyses)} files have CRITICAL issues"
        )

        return str(report_path)


def main():
    analyzer = CSVDataQualityAnalyzer()

    # Target dates for analysis
    target_dates = ["2025-08-27", "2025-08-22", "2025-08-23"]

    report_path = analyzer.run_full_analysis(target_dates)
    print(f"\n🎯 CRITICAL ANALYSIS COMPLETE")
    print(f"📄 Report saved to: {report_path}")
    print(f"🚨 Review immediately to prevent system failures!")

    return report_path


if __name__ == "__main__":
    main()
