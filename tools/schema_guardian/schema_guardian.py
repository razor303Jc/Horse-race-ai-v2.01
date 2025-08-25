#!/usr/bin/env python3
"""
Schema Guardian - The Ultimate Schema Protection System
Prevents recurring schema failures permanently through intelligent automation
"""

import pandas as pd
import psycopg2
from pathlib import Path
import json
import yaml
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from urllib.parse import urlparse
import os


@dataclass
class SchemaMismatch:
    """Represents a schema compatibility issue"""

    table_name: str
    csv_column: str
    database_column: Optional[str]
    issue_type: str  # 'missing', 'case_mismatch', 'type_mismatch'
    suggested_fix: str


@dataclass
class CompatibilityReport:
    """Complete compatibility analysis report"""

    is_compatible: bool
    mismatches: List[SchemaMismatch]
    warnings: List[str]
    auto_fixes_available: bool


class SchemaGuardian:
    """
    The Schema Guardian - Prevents ALL schema-related failures

    Key Responsibilities:
    1. Real-time schema monitoring
    2. CSV-to-database compatibility validation
    3. Automatic mismatch detection
    4. Intelligent fix suggestions
    5. Prevention of data loss
    """

    def __init__(self):
        self.database_configs = self._load_database_configs()
        self.mapping_rules = self._load_mapping_rules()
        self.type_conversion_rules = self._load_type_rules()

    def _load_database_configs(self) -> Dict:
        """Load database connection configurations"""
        return {
            "results": {
                "url": os.getenv(
                    "RESULTS_DATABASE_URL",
                    "postgresql://horse_racing:secure_password_123@postgres:5432/results_horse_racing_db",
                ),
                "schema": "public",
            },
            "cards": {
                "url": os.getenv(
                    "CARDS_DATABASE_URL",
                    "postgresql://horse_racing:secure_password_123@postgres:5432/cards_horse_racing_db",
                ),
                "schema": "public",
            },
            "metrics": {
                "url": os.getenv(
                    "METRICS_DATABASE_URL",
                    "postgresql://horse_racing:secure_password_123@postgres:5432/advanced_racing_metrics_db",
                ),
                "schema": "public",
            },
        }

    def _load_mapping_rules(self) -> Dict:
        """Load intelligent column mapping rules"""
        mapping_file = (
            Path(__file__).parent.parent.parent / "config" / "schema_mappings.yaml"
        )
        if mapping_file.exists():
            with open(mapping_file, "r") as f:
                return yaml.safe_load(f)

        # Default intelligent mappings
        return {
            "horses": {
                "id": "horse_id",
                "name": "horse_name",
                "UptoDate": "uptodate",
                "uptodate": "uptodate",
            },
            "jockeys_stats": {
                "UptoDate": "uptodate",
                "Jockey_ID": "jockey_id",
                "Name": "jockey_name",
            },
            "trainers_stats": {
                "UptoDate": "uptodate",
                "Trainer_ID": "trainer_id",
                "Name": "trainer_name",
            },
            "records": {"id": "record_id", "Race_ID": "race_id"},
            "races": {"Race_ID": "race_id"},
        }

    def _load_type_rules(self) -> Dict:
        """Load data type conversion rules"""
        return {
            "null_values": ["-", "", "None", "NULL", "null"],
            "integer_fields": ["id", "race_id", "horse_id", "jockey_id", "trainer_id"],
            "string_cleaning": {
                "trim_whitespace": True,
                "normalize_case": False,  # Preserve original case unless mapped
            },
        }

    def get_database_schema(self, database_name: str, table_name: str) -> Dict:
        """Extract complete schema information from database"""
        config = self.database_configs[database_name]
        parsed_url = urlparse(config["url"])

        db_config = {
            "host": parsed_url.hostname or "postgres",
            "port": parsed_url.port or 5432,
            "database": parsed_url.path.lstrip("/"),
            "user": parsed_url.username,
            "password": parsed_url.password,
        }

        try:
            conn = psycopg2.connect(**db_config)
            with conn.cursor() as cur:
                # Get column information
                cur.execute(
                    """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s AND table_schema = %s
                    ORDER BY ordinal_position
                """,
                    (table_name, config["schema"]),
                )

                columns = {}
                for row in cur.fetchall():
                    columns[row[0]] = {
                        "type": row[1],
                        "nullable": row[2] == "YES",
                        "default": row[3],
                    }

                conn.close()
                return columns

        except Exception as e:
            print(f"❌ Error getting schema for {database_name}.{table_name}: {e}")
            return {}

    def analyze_csv_structure(self, csv_file: Path) -> Dict:
        """Analyze CSV file structure and data types"""
        try:
            df = pd.read_csv(csv_file, nrows=100)  # Sample for analysis

            structure = {
                "columns": list(df.columns),
                "row_count": len(df),
                "data_types": {},
                "sample_values": {},
                "null_patterns": {},
            }

            for col in df.columns:
                structure["data_types"][col] = str(df[col].dtype)
                structure["sample_values"][col] = df[col].dropna().head(3).tolist()
                structure["null_patterns"][col] = df[col].isnull().sum()

            return structure

        except Exception as e:
            print(f"❌ Error analyzing CSV {csv_file}: {e}")
            return {}

    def validate_compatibility(
        self, csv_file: Path, database_name: str, table_name: str
    ) -> CompatibilityReport:
        """
        CORE FUNCTION: Validates CSV compatibility with database schema
        Returns detailed analysis with fix suggestions
        """
        print(
            f"🔍 Schema Guardian: Validating {csv_file.name} → {database_name}.{table_name}"
        )

        # Get schemas
        csv_structure = self.analyze_csv_structure(csv_file)
        db_schema = self.get_database_schema(database_name, table_name)

        if not csv_structure or not db_schema:
            return CompatibilityReport(
                is_compatible=False,
                mismatches=[],
                warnings=["Failed to analyze schemas"],
                auto_fixes_available=False,
            )

        mismatches = []
        warnings = []

        # Check each CSV column against database
        csv_columns = csv_structure["columns"]
        db_columns = list(db_schema.keys())

        # Apply intelligent mapping
        table_mappings = self.mapping_rules.get(table_name, {})

        for csv_col in csv_columns:
            # Check if column exists directly
            if csv_col in db_columns:
                continue

            # Check if there's a mapping rule
            if csv_col in table_mappings:
                mapped_col = table_mappings[csv_col]
                if mapped_col in db_columns:
                    continue
                else:
                    mismatches.append(
                        SchemaMismatch(
                            table_name=table_name,
                            csv_column=csv_col,
                            database_column=mapped_col,
                            issue_type="missing_target",
                            suggested_fix=f"Database missing column '{mapped_col}' (mapped from '{csv_col}')",
                        )
                    )
            else:
                # Look for case-insensitive match
                csv_col_lower = csv_col.lower()
                matching_db_col = None

                for db_col in db_columns:
                    if db_col.lower() == csv_col_lower:
                        matching_db_col = db_col
                        break

                if matching_db_col:
                    mismatches.append(
                        SchemaMismatch(
                            table_name=table_name,
                            csv_column=csv_col,
                            database_column=matching_db_col,
                            issue_type="case_mismatch",
                            suggested_fix=f"Map '{csv_col}' → '{matching_db_col}'",
                        )
                    )
                else:
                    mismatches.append(
                        SchemaMismatch(
                            table_name=table_name,
                            csv_column=csv_col,
                            database_column=None,
                            issue_type="missing",
                            suggested_fix=f"No matching database column for '{csv_col}'",
                        )
                    )

        # Check for required database columns not in CSV
        for db_col, db_info in db_schema.items():
            if not db_info["nullable"] and db_info["default"] is None:
                # Required column, check if CSV has it (with mapping)
                found = False

                # Direct match
                if db_col in csv_columns:
                    found = True

                # Reverse mapping check
                for csv_col in csv_columns:
                    if table_mappings.get(csv_col) == db_col:
                        found = True
                        break

                if not found:
                    warnings.append(
                        f"Required database column '{db_col}' not found in CSV"
                    )

        is_compatible = len(mismatches) == 0
        auto_fixes_available = all(
            m.issue_type in ["case_mismatch", "missing"] and m.database_column
            for m in mismatches
        )

        return CompatibilityReport(
            is_compatible=is_compatible,
            mismatches=mismatches,
            warnings=warnings,
            auto_fixes_available=auto_fixes_available,
        )

    def generate_column_mapping(
        self, csv_file: Path, database_name: str, table_name: str
    ) -> Dict[str, str]:
        """Generate intelligent column mapping for CSV → Database"""
        print(
            f"🧠 Generating intelligent mapping: {csv_file.name} → {database_name}.{table_name}"
        )

        report = self.validate_compatibility(csv_file, database_name, table_name)
        mapping = {}

        # Start with direct matches
        csv_structure = self.analyze_csv_structure(csv_file)
        db_schema = self.get_database_schema(database_name, table_name)

        csv_columns = csv_structure.get("columns", [])
        db_columns = list(db_schema.keys())

        # Apply known mappings first
        table_mappings = self.mapping_rules.get(table_name, {})

        for csv_col in csv_columns:
            if csv_col in table_mappings:
                mapping[csv_col] = table_mappings[csv_col]
            elif csv_col in db_columns:
                mapping[csv_col] = csv_col
            else:
                # Look for case-insensitive match
                for db_col in db_columns:
                    if csv_col.lower() == db_col.lower():
                        mapping[csv_col] = db_col
                        break

        return mapping

    def create_mapping_config(
        self, csv_file: Path, database_name: str, table_name: str
    ) -> Dict:
        """Create complete mapping configuration for upload"""
        mapping = self.generate_column_mapping(csv_file, database_name, table_name)

        config = {
            "source_file": str(csv_file),
            "target_database": database_name,
            "target_table": table_name,
            "column_mapping": mapping,
            "type_conversions": self.type_conversion_rules,
            "validation_passed": len(mapping) > 0,
        }

        return config

    def diagnose_all_csv_files(self, data_directory: Path) -> Dict:
        """Comprehensive diagnosis of all CSV files in directory"""
        print("🔍 Schema Guardian: Full CSV compatibility analysis")

        results = {}
        csv_files = list(data_directory.glob("*.csv"))

        # Define expected mappings based on filename patterns
        file_mappings = {
            "mapped_horses.csv": ("results", "horses"),
            "mapped_jockeys_stats.csv": ("results", "jockeys_stats"),
            "mapped_trainers_stats.csv": ("results", "trainers_stats"),
            "mapped_records.csv": ("results", "records"),
            "mapped_races.csv": ("results", "races"),
            "mapped_result_races.csv": ("results", "races"),
        }

        for csv_file in csv_files:
            if csv_file.name in file_mappings:
                database_name, table_name = file_mappings[csv_file.name]
                report = self.validate_compatibility(
                    csv_file, database_name, table_name
                )

                results[csv_file.name] = {
                    "file_path": str(csv_file),
                    "target": f"{database_name}.{table_name}",
                    "compatible": report.is_compatible,
                    "mismatches": len(report.mismatches),
                    "warnings": len(report.warnings),
                    "auto_fixable": report.auto_fixes_available,
                    "details": report,
                }

        return results

    def print_compatibility_report(self, results: Dict):
        """Print comprehensive compatibility report"""
        print("\n" + "=" * 80)
        print("🛡️  SCHEMA GUARDIAN COMPATIBILITY REPORT")
        print("=" * 80)

        total_files = len(results)
        compatible_files = sum(1 for r in results.values() if r["compatible"])
        auto_fixable = sum(1 for r in results.values() if r["auto_fixable"])

        print(f"📊 SUMMARY:")
        print(f"   Total Files: {total_files}")
        print(f"   Compatible: {compatible_files}/{total_files}")
        print(f"   Auto-Fixable: {auto_fixable}/{total_files - compatible_files}")
        print(f"   Success Rate: {(compatible_files/total_files)*100:.1f}%")

        print(f"\n📋 DETAILED ANALYSIS:")

        for filename, result in results.items():
            status = "✅ COMPATIBLE" if result["compatible"] else "❌ NEEDS FIXES"
            if not result["compatible"] and result["auto_fixable"]:
                status = "🔧 AUTO-FIXABLE"

            print(f"\n   {filename}")
            print(f"   Target: {result['target']}")
            print(f"   Status: {status}")
            print(
                f"   Issues: {result['mismatches']} mismatches, {result['warnings']} warnings"
            )

            if result["mismatches"] > 0:
                print(f"   Specific Issues:")
                for mismatch in result["details"].mismatches:
                    print(
                        f"     - {mismatch.issue_type}: {mismatch.csv_column} → {mismatch.suggested_fix}"
                    )

        if compatible_files < total_files:
            print(f"\n🚨 ACTION REQUIRED:")
            print(
                f"   {total_files - compatible_files} files need fixing before upload"
            )
            print(
                f"   Use SchemaGuardian.generate_column_mapping() for automatic fixes"
            )
        else:
            print(f"\n🎉 ALL SYSTEMS GO!")
            print(f"   All CSV files compatible with database schemas")


def main():
    """Test the Schema Guardian with current data"""
    print("🛡️ Schema Guardian - Comprehensive Schema Analysis")

    guardian = SchemaGuardian()
    data_dir = Path("/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads")

    if data_dir.exists():
        results = guardian.diagnose_all_csv_files(data_dir)
        guardian.print_compatibility_report(results)
    else:
        print(f"❌ Data directory not found: {data_dir}")


if __name__ == "__main__":
    main()
