#!/usr/bin/env python3
"""
🔍 Schema Compatibility Checker for CSV Preprocessing
=====================================================

This module provides comprehensive schema validation for CSV files before upload
to prevent database schema mismatches and model training failures.

Key Features:
- Column name validation and mapping suggestions
- Data type compatibility checking
- Required fields validation
- Database schema compatibility verification
- Detailed error reporting with actionable recommendations

Author: AI Assistant
Date: August 24, 2025
TODO ID: 27
"""

import json
import logging
import pandas as pd
import psycopg2
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SchemaCompatibilityChecker:
    """
    Comprehensive schema validation for CSV preprocessing

    Prevents schema mismatches like:
    - Column name variations (draw vs number)
    - Missing required fields
    - Data type incompatibilities
    - Database constraint violations
    """

    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = project_root / "config"
        self.config_path = config_path

        # Load configuration files
        self.column_mappings = self._load_column_mappings()
        self.schema_validation_rules = self._load_schema_validation_rules()
        self.field_type_definitions = self._load_field_type_definitions()

        logger.info("🔍 Schema Compatibility Checker initialized")

    def _load_column_mappings(self) -> Dict:
        """Load column mapping configuration"""
        try:
            mapping_file = self.config_path / "complete_csv_column_mapping.json"
            if mapping_file.exists():
                with open(mapping_file, "r") as f:
                    return json.load(f)
            else:
                logger.warning(f"Column mapping file not found: {mapping_file}")
                return {}
        except Exception as e:
            logger.warning(f"Could not load column mappings: {e}")
            return {}

    def _load_schema_validation_rules(self) -> Dict:
        """Load schema validation rules"""
        try:
            rules_file = self.config_path / "schema_validation_rules.json"
            if rules_file.exists():
                with open(rules_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load schema validation rules: {e}")

        # Default validation rules based on our experience
        return {
            "required_fields_by_table": {
                "races": ["race_id", "date", "course", "race_time"],
                "racecard_details": ["race_id", "horse_number", "horse"],
                "horses": ["horse_id", "name"],
                "records": ["race_id", "horse_number", "position"],
            },
            "field_name_standards": {
                "draw": "number",  # Standardize draw → number
                "race_date": "date",  # Standardize race_date → date
                "horse_name": "horse",  # Standardize horse_name → horse
                "jockey_name": "jockey",  # Standardize jockey_name → jockey
                "trainer_name": "trainer",  # Standardize trainer_name → trainer
            },
            "data_type_requirements": {
                "integer_fields": [
                    "race_id",
                    "horse_id",
                    "course_id",
                    "race_number",
                    "age",
                    "weight",
                ],
                "decimal_fields": ["odds", "odds_decimal", "prize"],
                "string_fields": ["race_time", "course", "horse", "jockey", "trainer"],
                "date_fields": ["date", "race_date"],
            },
        }

    def _load_field_type_definitions(self) -> Dict:
        """Load field type definitions"""
        try:
            types_file = self.config_path / "cards_field_types.json"
            if types_file.exists():
                with open(types_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load field type definitions: {e}")

        return {}

    def validate_csv_schema_compatibility(
        self,
        csv_path: Path,
        target_table: str,
        database_connection: Optional[psycopg2.extensions.connection] = None,
    ) -> Dict:
        """
        Comprehensive CSV schema validation

        Args:
            csv_path: Path to CSV file to validate
            target_table: Target database table name
            database_connection: Optional database connection for schema checking

        Returns:
            Dict with validation results and recommendations
        """
        logger.info(
            f"🔍 Validating schema compatibility for {csv_path} → {target_table}"
        )

        validation_result = {
            "csv_file": str(csv_path),
            "target_table": target_table,
            "validation_passed": False,
            "errors": [],
            "warnings": [],
            "recommendations": [],
            "column_analysis": {},
            "data_type_analysis": {},
            "compatibility_score": 0.0,
        }

        try:
            # Load CSV file
            df = pd.read_csv(csv_path)
            logger.info(
                f"📊 Loaded CSV with {len(df)} rows and {len(df.columns)} columns"
            )

            # 1. Column name validation
            column_validation = self._validate_column_names(
                df.columns.tolist(), target_table
            )
            validation_result["column_analysis"] = column_validation

            # 2. Required fields validation
            required_fields = self._validate_required_fields(
                df.columns.tolist(), target_table
            )
            validation_result["required_fields"] = required_fields

            # 3. Data type validation
            data_type_validation = self._validate_data_types(df, target_table)
            validation_result["data_type_analysis"] = data_type_validation

            # 4. Database schema compatibility (if connection provided)
            if database_connection:
                db_compatibility = self._validate_database_compatibility(
                    df.columns.tolist(), target_table, database_connection
                )
                validation_result["database_compatibility"] = db_compatibility

            # 5. Generate recommendations
            recommendations = self._generate_recommendations(validation_result)
            validation_result["recommendations"] = recommendations

            # 6. Calculate compatibility score
            compatibility_score = self._calculate_compatibility_score(validation_result)
            validation_result["compatibility_score"] = compatibility_score

            # 7. Determine overall validation status
            validation_result["validation_passed"] = (
                len(validation_result["errors"]) == 0 and compatibility_score >= 0.8
            )

            logger.info(
                f"✅ Schema validation completed. Score: {compatibility_score:.2f}"
            )

        except Exception as e:
            logger.error(f"❌ Schema validation failed: {e}")
            validation_result["errors"].append(f"Validation failed: {str(e)}")

        return validation_result

    def _validate_column_names(self, csv_columns: List[str], target_table: str) -> Dict:
        """Validate column names against expected schema"""
        logger.info(f"🔍 Validating column names for table: {target_table}")

        analysis = {
            "csv_columns": csv_columns,
            "mapped_columns": {},
            "unmapped_columns": [],
            "suggested_mappings": {},
            "standardization_needed": [],
        }

        # Get expected columns for target table
        table_mappings = self.column_mappings.get("table_mappings", {})
        target_mapping = table_mappings.get(target_table, {})
        expected_columns = target_mapping.get("column_mapping", {})

        for csv_col in csv_columns:
            # Check if column name needs standardization
            standardized_name = self.schema_validation_rules[
                "field_name_standards"
            ].get(csv_col.lower(), csv_col)

            if standardized_name != csv_col:
                analysis["standardization_needed"].append(
                    {"original": csv_col, "standardized": standardized_name}
                )

            # Try to find mapping
            mapped = False
            for db_col, csv_pattern in expected_columns.items():
                if csv_col.lower() == csv_pattern.lower():
                    analysis["mapped_columns"][csv_col] = db_col
                    mapped = True
                    break

            if not mapped:
                analysis["unmapped_columns"].append(csv_col)
                # Suggest similar column names
                suggestions = self._suggest_column_mapping(
                    csv_col, expected_columns.keys()
                )
                if suggestions:
                    analysis["suggested_mappings"][csv_col] = suggestions

        return analysis

    def _validate_required_fields(
        self, csv_columns: List[str], target_table: str
    ) -> Dict:
        """Validate that required fields are present"""
        logger.info(f"🔍 Validating required fields for table: {target_table}")

        required_fields = self.schema_validation_rules["required_fields_by_table"].get(
            target_table, []
        )

        analysis = {
            "required_fields": required_fields,
            "present_fields": [],
            "missing_fields": [],
            "validation_passed": True,
        }

        csv_columns_lower = [col.lower() for col in csv_columns]

        for required_field in required_fields:
            if required_field.lower() in csv_columns_lower:
                analysis["present_fields"].append(required_field)
            else:
                analysis["missing_fields"].append(required_field)
                analysis["validation_passed"] = False

        return analysis

    def _validate_data_types(self, df: pd.DataFrame, target_table: str) -> Dict:
        """Validate data types against expected schema"""
        logger.info(f"🔍 Validating data types for table: {target_table}")

        analysis = {
            "column_types": {},
            "type_mismatches": [],
            "null_counts": {},
            "validation_passed": True,
        }

        data_type_requirements = self.schema_validation_rules["data_type_requirements"]

        for column in df.columns:
            # Analyze current data type
            dtype = str(df[column].dtype)
            null_count = df[column].isnull().sum()

            analysis["column_types"][column] = dtype
            analysis["null_counts"][column] = null_count

            # Check against requirements
            column_lower = column.lower()

            # Check if should be integer
            if column_lower in [
                f.lower() for f in data_type_requirements["integer_fields"]
            ]:
                if not pd.api.types.is_integer_dtype(
                    df[column]
                ) and not pd.api.types.is_numeric_dtype(df[column]):
                    analysis["type_mismatches"].append(
                        {
                            "column": column,
                            "expected": "integer",
                            "actual": dtype,
                            "severity": "error",
                        }
                    )
                    analysis["validation_passed"] = False

            # Check if should be decimal
            elif column_lower in [
                f.lower() for f in data_type_requirements["decimal_fields"]
            ]:
                if not pd.api.types.is_numeric_dtype(df[column]):
                    analysis["type_mismatches"].append(
                        {
                            "column": column,
                            "expected": "decimal/numeric",
                            "actual": dtype,
                            "severity": "error",
                        }
                    )
                    analysis["validation_passed"] = False

        return analysis

    def _validate_database_compatibility(
        self,
        csv_columns: List[str],
        target_table: str,
        db_connection: psycopg2.extensions.connection,
    ) -> Dict:
        """Validate compatibility with actual database schema"""
        logger.info(f"🔍 Validating database compatibility for table: {target_table}")

        analysis = {
            "table_exists": False,
            "database_columns": [],
            "column_matches": [],
            "column_mismatches": [],
            "validation_passed": True,
        }

        try:
            cursor = db_connection.cursor()

            # Check if table exists
            cursor.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)",
                (target_table,),
            )
            analysis["table_exists"] = cursor.fetchone()[0]

            if analysis["table_exists"]:
                # Get database table columns
                cursor.execute(
                    "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s",
                    (target_table,),
                )
                db_columns = cursor.fetchall()
                analysis["database_columns"] = [
                    {"name": col[0], "type": col[1]} for col in db_columns
                ]

                # Compare columns
                db_column_names = [col[0] for col in db_columns]

                for csv_col in csv_columns:
                    if csv_col.lower() in [
                        db_col.lower() for db_col in db_column_names
                    ]:
                        analysis["column_matches"].append(csv_col)
                    else:
                        analysis["column_mismatches"].append(csv_col)

            cursor.close()

        except Exception as e:
            logger.error(f"❌ Database compatibility check failed: {e}")
            analysis["validation_passed"] = False
            analysis["error"] = str(e)

        return analysis

    def _suggest_column_mapping(
        self, csv_column: str, expected_columns: List[str]
    ) -> List[str]:
        """Suggest similar column names using simple similarity"""
        suggestions = []
        csv_col_lower = csv_column.lower()

        for expected_col in expected_columns:
            expected_lower = expected_col.lower()

            # Simple similarity checks
            if csv_col_lower in expected_lower or expected_lower in csv_col_lower:
                suggestions.append(expected_col)
            elif len(csv_col_lower) > 3 and len(expected_lower) > 3:
                # Check for partial matches
                if any(part in expected_lower for part in csv_col_lower.split("_")):
                    suggestions.append(expected_col)

        return suggestions[:3]  # Return top 3 suggestions

    def _generate_recommendations(self, validation_result: Dict) -> List[Dict]:
        """Generate actionable recommendations based on validation results"""
        recommendations = []

        # Column name standardization recommendations
        column_analysis = validation_result.get("column_analysis", {})
        if column_analysis.get("standardization_needed"):
            recommendations.append(
                {
                    "type": "column_standardization",
                    "priority": "high",
                    "description": "Standardize column names to prevent field mapping issues",
                    "actions": column_analysis["standardization_needed"],
                }
            )

        # Missing required fields recommendations
        required_fields = validation_result.get("required_fields", {})
        if required_fields.get("missing_fields"):
            recommendations.append(
                {
                    "type": "missing_required_fields",
                    "priority": "critical",
                    "description": "Add missing required fields or update field mapping",
                    "missing_fields": required_fields["missing_fields"],
                }
            )

        # Data type recommendations
        data_type_analysis = validation_result.get("data_type_analysis", {})
        if data_type_analysis.get("type_mismatches"):
            recommendations.append(
                {
                    "type": "data_type_conversion",
                    "priority": "high",
                    "description": "Convert data types to match schema requirements",
                    "conversions_needed": data_type_analysis["type_mismatches"],
                }
            )

        # Column mapping recommendations
        if column_analysis.get("suggested_mappings"):
            recommendations.append(
                {
                    "type": "column_mapping",
                    "priority": "medium",
                    "description": "Consider these column mappings",
                    "suggestions": column_analysis["suggested_mappings"],
                }
            )

        return recommendations

    def _calculate_compatibility_score(self, validation_result: Dict) -> float:
        """Calculate overall compatibility score (0-1)"""
        score = 1.0

        # Deduct points for errors
        if validation_result.get("errors"):
            score -= 0.5

        # Deduct points for missing required fields
        required_fields = validation_result.get("required_fields", {})
        if required_fields.get("missing_fields"):
            missing_count = len(required_fields["missing_fields"])
            total_required = len(required_fields.get("required_fields", []))
            if total_required > 0:
                score -= 0.3 * (missing_count / total_required)

        # Deduct points for data type mismatches
        data_type_analysis = validation_result.get("data_type_analysis", {})
        if data_type_analysis.get("type_mismatches"):
            mismatch_count = len(data_type_analysis["type_mismatches"])
            total_columns = len(data_type_analysis.get("column_types", {}))
            if total_columns > 0:
                score -= 0.2 * (mismatch_count / total_columns)

        # Deduct points for unmapped columns
        column_analysis = validation_result.get("column_analysis", {})
        if column_analysis.get("unmapped_columns"):
            unmapped_count = len(column_analysis["unmapped_columns"])
            total_columns = len(column_analysis.get("csv_columns", []))
            if total_columns > 0:
                score -= 0.1 * (unmapped_count / total_columns)

        return max(0.0, score)

    def generate_compatibility_report(self, validation_result: Dict) -> str:
        """Generate human-readable compatibility report"""
        report = []
        report.append("🔍 CSV Schema Compatibility Report")
        report.append("=" * 50)
        report.append(f"File: {validation_result['csv_file']}")
        report.append(f"Target Table: {validation_result['target_table']}")
        report.append(
            f"Compatibility Score: {validation_result['compatibility_score']:.2f}/1.0"
        )
        report.append(
            f"Validation Passed: {'✅ YES' if validation_result['validation_passed'] else '❌ NO'}"
        )
        report.append("")

        # Column Analysis
        column_analysis = validation_result.get("column_analysis", {})
        if column_analysis:
            report.append("📋 Column Analysis:")
            report.append(
                f"  • Total Columns: {len(column_analysis.get('csv_columns', []))}"
            )
            report.append(
                f"  • Mapped Columns: {len(column_analysis.get('mapped_columns', {}))}"
            )
            report.append(
                f"  • Unmapped Columns: {len(column_analysis.get('unmapped_columns', []))}"
            )

            if column_analysis.get("standardization_needed"):
                report.append("  • Standardization Needed:")
                for std in column_analysis["standardization_needed"]:
                    report.append(f"    - {std['original']} → {std['standardized']}")
            report.append("")

        # Required Fields
        required_fields = validation_result.get("required_fields", {})
        if required_fields:
            report.append("📋 Required Fields:")
            report.append(
                f"  • Present: {len(required_fields.get('present_fields', []))}"
            )
            report.append(
                f"  • Missing: {len(required_fields.get('missing_fields', []))}"
            )

            if required_fields.get("missing_fields"):
                report.append("  • Missing Fields:")
                for field in required_fields["missing_fields"]:
                    report.append(f"    - {field}")
            report.append("")

        # Recommendations
        recommendations = validation_result.get("recommendations", [])
        if recommendations:
            report.append("💡 Recommendations:")
            for rec in recommendations:
                priority_icon = (
                    "🔥"
                    if rec["priority"] == "critical"
                    else "⚠️" if rec["priority"] == "high" else "📝"
                )
                report.append(f"  {priority_icon} {rec['description']}")
            report.append("")

        # Errors and Warnings
        if validation_result.get("errors"):
            report.append("❌ Errors:")
            for error in validation_result["errors"]:
                report.append(f"  • {error}")
            report.append("")

        if validation_result.get("warnings"):
            report.append("⚠️ Warnings:")
            for warning in validation_result["warnings"]:
                report.append(f"  • {warning}")
            report.append("")

        return "\n".join(report)


def main():
    """CLI interface for schema compatibility checking"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Schema Compatibility Checker for CSV Preprocessing"
    )
    parser.add_argument("csv_file", help="Path to CSV file to validate")
    parser.add_argument("target_table", help="Target database table name")
    parser.add_argument("--config-path", help="Path to configuration directory")
    parser.add_argument("--db-host", help="Database host for live schema checking")
    parser.add_argument("--db-port", default="5432", help="Database port")
    parser.add_argument("--db-name", help="Database name")
    parser.add_argument("--db-user", help="Database username")
    parser.add_argument("--db-password", help="Database password")
    parser.add_argument("--output", help="Output file for report")

    args = parser.parse_args()

    # Initialize checker
    config_path = Path(args.config_path) if args.config_path else None
    checker = SchemaCompatibilityChecker(config_path)

    # Establish database connection if credentials provided
    db_connection = None
    if args.db_host and args.db_name and args.db_user:
        try:
            db_connection = psycopg2.connect(
                host=args.db_host,
                port=args.db_port,
                database=args.db_name,
                user=args.db_user,
                password=args.db_password,
            )
            logger.info("📡 Connected to database for live schema checking")
        except Exception as e:
            logger.warning(f"Could not connect to database: {e}")

    # Run validation
    csv_path = Path(args.csv_file)
    validation_result = checker.validate_csv_schema_compatibility(
        csv_path, args.target_table, db_connection
    )

    # Generate report
    report = checker.generate_compatibility_report(validation_result)

    # Output report
    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        logger.info(f"📄 Report saved to {args.output}")
    else:
        print(report)

    # Exit with appropriate code
    exit_code = 0 if validation_result["validation_passed"] else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
