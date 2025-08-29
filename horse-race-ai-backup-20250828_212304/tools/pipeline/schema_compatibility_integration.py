#!/usr/bin/env python3
"""
🔗 Schema Compatibility Checker Integration
===========================================

Integration module to incorporate schema validation into existing
CSV processing pipeline workflows.

This demonstrates how to use the Schema Compatibility Checker
before CSV uploads to prevent schema mismatches.

Author: AI Assistant
Date: August 24, 2025
TODO ID: 27 Integration
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.pipeline.schema_compatibility_checker import SchemaCompatibilityChecker

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedCSVProcessor:
    """
    Enhanced CSV processor with integrated schema validation

    Wraps existing CSV processing with schema compatibility checking
    to prevent upload failures and data inconsistencies.
    """

    def __init__(self, config_path: Path = None):
        self.schema_checker = SchemaCompatibilityChecker(config_path)
        logger.info("🔗 Enhanced CSV Processor with schema validation initialized")

    def process_csv_with_validation(
        self,
        csv_path: Path,
        target_table: str,
        fix_schema_issues: bool = True,
        backup_original: bool = True,
    ) -> Dict:
        """
        Process CSV file with comprehensive schema validation and optional fixes

        Args:
            csv_path: Path to CSV file
            target_table: Target database table
            fix_schema_issues: Automatically fix detectable schema issues
            backup_original: Create backup before modifications

        Returns:
            Processing result with validation details and file paths
        """
        logger.info(f"🔄 Processing CSV with validation: {csv_path} → {target_table}")

        result = {
            "original_file": str(csv_path),
            "target_table": target_table,
            "validation_passed": False,
            "processing_successful": False,
            "schema_validation": {},
            "fixes_applied": [],
            "output_file": None,
            "backup_file": None,
            "recommendations": [],
        }

        try:
            # Step 1: Schema validation
            logger.info("🔍 Step 1: Schema compatibility validation")
            validation_result = self.schema_checker.validate_csv_schema_compatibility(
                csv_path, target_table
            )
            result["schema_validation"] = validation_result
            result["validation_passed"] = validation_result["validation_passed"]

            # Step 2: Create backup if requested
            if backup_original:
                backup_path = self._create_backup(csv_path)
                result["backup_file"] = str(backup_path)
                logger.info(f"💾 Created backup: {backup_path}")

            # Step 3: Apply fixes if validation failed but fixable
            if not validation_result["validation_passed"] and fix_schema_issues:
                logger.info("🔧 Step 2: Applying automatic schema fixes")
                fixed_df, fixes_applied = self._apply_schema_fixes(
                    csv_path, validation_result
                )

                if fixes_applied:
                    # Save fixed file
                    output_path = self._generate_output_path(csv_path, "_schema_fixed")
                    fixed_df.to_csv(output_path, index=False)
                    result["output_file"] = str(output_path)
                    result["fixes_applied"] = fixes_applied
                    result["processing_successful"] = True

                    logger.info(f"✅ Schema fixes applied and saved to: {output_path}")

                    # Re-validate fixed file
                    revalidation = (
                        self.schema_checker.validate_csv_schema_compatibility(
                            output_path, target_table
                        )
                    )
                    logger.info(
                        f"🔍 Re-validation score: {revalidation['compatibility_score']:.2f}"
                    )
                    result["schema_validation"]["post_fix_validation"] = revalidation
                else:
                    logger.warning("⚠️ No automatic fixes could be applied")
                    result["output_file"] = str(csv_path)  # Use original file
            else:
                result["output_file"] = str(csv_path)  # Use original file
                result["processing_successful"] = validation_result["validation_passed"]

            # Step 4: Generate recommendations for manual fixes
            if not result["processing_successful"]:
                result["recommendations"] = self._generate_manual_fix_recommendations(
                    validation_result
                )

        except Exception as e:
            logger.error(f"❌ CSV processing failed: {e}")
            result["error"] = str(e)

        return result

    def _create_backup(self, csv_path: Path) -> Path:
        """Create backup of original CSV file"""
        backup_path = csv_path.parent / f"{csv_path.stem}_backup{csv_path.suffix}"
        backup_path.write_bytes(csv_path.read_bytes())
        return backup_path

    def _generate_output_path(self, csv_path: Path, suffix: str) -> Path:
        """Generate output file path with suffix"""
        return csv_path.parent / f"{csv_path.stem}{suffix}{csv_path.suffix}"

    def _apply_schema_fixes(self, csv_path: Path, validation_result: Dict) -> tuple:
        """Apply automatic schema fixes based on validation results"""
        fixes_applied = []

        try:
            df = pd.read_csv(csv_path)
            original_columns = list(df.columns)

            # Fix 1: Column name standardization
            column_analysis = validation_result.get("column_analysis", {})
            standardization_needed = column_analysis.get("standardization_needed", [])

            for std in standardization_needed:
                old_name = std["original"]
                new_name = std["standardized"]

                if old_name in df.columns:
                    df = df.rename(columns={old_name: new_name})
                    fixes_applied.append(
                        {
                            "type": "column_rename",
                            "description": f"Renamed '{old_name}' to '{new_name}'",
                            "old_name": old_name,
                            "new_name": new_name,
                        }
                    )
                    logger.info(f"🔧 Renamed column: {old_name} → {new_name}")

            # Fix 2: Add missing required fields with NULL values (if minimal)
            required_fields = validation_result.get("required_fields", {})
            missing_fields = required_fields.get("missing_fields", [])

            # Only auto-add missing fields if there are 2 or fewer missing
            if len(missing_fields) <= 2:
                for missing_field in missing_fields:
                    if missing_field not in df.columns:
                        df[missing_field] = None  # Add with NULL values
                        fixes_applied.append(
                            {
                                "type": "add_missing_field",
                                "description": f"Added missing field '{missing_field}' with NULL values",
                                "field_name": missing_field,
                            }
                        )
                        logger.info(f"🔧 Added missing field: {missing_field}")

            # Fix 3: Basic data type conversions
            data_type_analysis = validation_result.get("data_type_analysis", {})
            type_mismatches = data_type_analysis.get("type_mismatches", [])

            for mismatch in type_mismatches:
                column = mismatch["column"]
                expected_type = mismatch["expected"]

                if column in df.columns and expected_type in [
                    "integer",
                    "decimal/numeric",
                ]:
                    try:
                        if expected_type == "integer":
                            df[column] = pd.to_numeric(
                                df[column], errors="coerce"
                            ).astype("Int64")
                        else:  # decimal/numeric
                            df[column] = pd.to_numeric(df[column], errors="coerce")

                        fixes_applied.append(
                            {
                                "type": "data_type_conversion",
                                "description": f"Converted '{column}' to {expected_type}",
                                "column": column,
                                "target_type": expected_type,
                            }
                        )
                        logger.info(f"🔧 Converted {column} to {expected_type}")
                    except Exception as e:
                        logger.warning(
                            f"⚠️ Could not convert {column} to {expected_type}: {e}"
                        )

            return df, fixes_applied

        except Exception as e:
            logger.error(f"❌ Schema fix application failed: {e}")
            return pd.read_csv(csv_path), []

    def _generate_manual_fix_recommendations(
        self, validation_result: Dict
    ) -> List[str]:
        """Generate manual fix recommendations for issues that couldn't be auto-fixed"""
        recommendations = []

        # Missing fields that couldn't be auto-added
        required_fields = validation_result.get("required_fields", {})
        missing_fields = required_fields.get("missing_fields", [])

        if len(missing_fields) > 2:
            recommendations.append(
                f"⚠️ Manual Action Required: Add missing required fields: {', '.join(missing_fields)}"
            )

        # Complex column mapping issues
        column_analysis = validation_result.get("column_analysis", {})
        suggested_mappings = column_analysis.get("suggested_mappings", {})

        if suggested_mappings:
            recommendations.append(
                "💡 Consider these column mappings for unmapped fields:"
            )
            for unmapped, suggestions in suggested_mappings.items():
                recommendations.append(f"  - '{unmapped}' → {suggestions}")

        # Data quality issues
        data_type_analysis = validation_result.get("data_type_analysis", {})
        if data_type_analysis.get("type_mismatches"):
            recommendations.append(
                "🔧 Review data types and clean data where automatic conversion failed"
            )

        return recommendations

    def generate_processing_report(self, result: Dict) -> str:
        """Generate comprehensive processing report"""
        report = []
        report.append("🔗 Enhanced CSV Processing Report")
        report.append("=" * 50)
        report.append(f"File: {result['original_file']}")
        report.append(f"Target Table: {result['target_table']}")
        report.append(
            f"Processing Successful: {'✅ YES' if result['processing_successful'] else '❌ NO'}"
        )
        report.append("")

        # Schema validation summary
        validation = result.get("schema_validation", {})
        if validation:
            score = validation.get("compatibility_score", 0)
            report.append(f"Schema Compatibility Score: {score:.2f}/1.0")
            report.append("")

        # Fixes applied
        fixes = result.get("fixes_applied", [])
        if fixes:
            report.append("🔧 Automatic Fixes Applied:")
            for fix in fixes:
                report.append(f"  • {fix['description']}")
            report.append("")

        # Output files
        if result.get("output_file"):
            report.append(f"📄 Output File: {result['output_file']}")
        if result.get("backup_file"):
            report.append(f"💾 Backup File: {result['backup_file']}")

        # Recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            report.append("")
            report.append("💡 Manual Action Recommendations:")
            for rec in recommendations:
                report.append(f"  {rec}")

        return "\n".join(report)


def demo_integration():
    """Demonstrate integration with existing pipeline"""
    print("🔗 Schema Compatibility Checker Integration Demo")
    print("=" * 60)

    # Create sample CSV with issues
    sample_data = {
        "Race_ID": ["R001", "R002"],
        "draw": [1, 2],  # Should be 'number'
        "horse_name": ["Thunder", "Lightning"],  # Should be 'horse'
        "jockey_name": ["J. Smith", "M. Jones"],  # Should be 'jockey'
        "odds_decimal": ["5.0", "3.5"],  # String, should be numeric
    }

    import tempfile

    df = pd.DataFrame(sample_data)
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    df.to_csv(temp_file.name, index=False)

    # Process with enhanced processor
    processor = EnhancedCSVProcessor()
    result = processor.process_csv_with_validation(
        Path(temp_file.name),
        "racecard_details",
        fix_schema_issues=True,
        backup_original=True,
    )

    # Display report
    report = processor.generate_processing_report(result)
    print(report)

    print("\n✅ Integration demo completed!")
    print("This shows how schema validation can be seamlessly integrated")
    print("into existing CSV processing workflows.")


if __name__ == "__main__":
    demo_integration()
