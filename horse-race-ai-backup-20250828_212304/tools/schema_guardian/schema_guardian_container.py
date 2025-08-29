#!/usr/bin/env python3
"""
Schema Guardian - Container Version
Runs inside Docker container for direct database access
"""

import pandas as pd
import psycopg2
from pathlib import Path
import json
import os
from typing import Dict, List


class SchemaGuardianContainer:
    """Schema Guardian optimized for container execution"""

    def __init__(self):
        self.database_config = {
            "host": "postgres",
            "port": 5432,
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Intelligent column mappings
        self.mappings = {
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

    def get_database_schema(self, table_name: str) -> Dict:
        """Get database schema for table"""
        try:
            conn = psycopg2.connect(**self.database_config)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position
                """,
                    (table_name,),
                )

                schema = {}
                for row in cur.fetchall():
                    schema[row[0]] = {"type": row[1], "nullable": row[2] == "YES"}

                conn.close()
                return schema

        except Exception as e:
            print(f"❌ Error getting schema for {table_name}: {e}")
            return {}

    def analyze_csv(self, csv_file: Path) -> Dict:
        """Analyze CSV structure"""
        try:
            df = pd.read_csv(csv_file, nrows=10)
            return {
                "columns": list(df.columns),
                "sample_data": df.head(3).to_dict("records"),
            }
        except Exception as e:
            print(f"❌ Error analyzing {csv_file}: {e}")
            return {}

    def validate_compatibility(self, csv_file: Path, table_name: str):
        """Validate CSV compatibility with database table"""
        print(f"\n🔍 Validating {csv_file.name} → {table_name}")

        # Get structures
        csv_info = self.analyze_csv(csv_file)
        db_schema = self.get_database_schema(table_name)

        if not csv_info or not db_schema:
            print("❌ Failed to analyze structures")
            return False

        csv_columns = csv_info["columns"]
        db_columns = list(db_schema.keys())
        table_mappings = self.mappings.get(table_name, {})

        print(f"📄 CSV columns: {csv_columns}")
        print(f"🗃️  DB columns: {db_columns}")

        # Check compatibility
        issues = []
        fixes = []

        for csv_col in csv_columns:
            if csv_col in db_columns:
                print(f"✅ Direct match: {csv_col}")
            elif csv_col in table_mappings:
                mapped_col = table_mappings[csv_col]
                if mapped_col in db_columns:
                    print(f"🔧 Mapping available: {csv_col} → {mapped_col}")
                    fixes.append(f"Map '{csv_col}' to '{mapped_col}'")
                else:
                    issues.append(
                        f"Mapped column '{mapped_col}' doesn't exist in database"
                    )
            else:
                # Look for case-insensitive match
                matches = [
                    db_col for db_col in db_columns if db_col.lower() == csv_col.lower()
                ]
                if matches:
                    print(f"🔧 Case fix available: {csv_col} → {matches[0]}")
                    fixes.append(f"Fix case: '{csv_col}' → '{matches[0]}'")
                else:
                    issues.append(f"No match for CSV column '{csv_col}'")

        # Show results
        compatible = len(issues) == 0
        auto_fixable = len(issues) == 0 and len(fixes) > 0

        if compatible and not fixes:
            print("✅ FULLY COMPATIBLE - No changes needed")
        elif auto_fixable or not issues:
            print("🔧 AUTO-FIXABLE - Mapping available")
            for fix in fixes:
                print(f"   - {fix}")
        else:
            print("❌ INCOMPATIBLE - Manual fixes required")
            for issue in issues:
                print(f"   - {issue}")

        return compatible or auto_fixable

    def generate_mapping_for_table(
        self, csv_file: Path, table_name: str
    ) -> Dict[str, str]:
        """Generate column mapping for CSV to database table"""
        csv_info = self.analyze_csv(csv_file)
        db_schema = self.get_database_schema(table_name)

        if not csv_info or not db_schema:
            return {}

        mapping = {}
        csv_columns = csv_info["columns"]
        db_columns = list(db_schema.keys())
        table_mappings = self.mappings.get(table_name, {})

        for csv_col in csv_columns:
            if csv_col in table_mappings:
                mapping[csv_col] = table_mappings[csv_col]
            elif csv_col in db_columns:
                mapping[csv_col] = csv_col
            else:
                # Case-insensitive match
                for db_col in db_columns:
                    if csv_col.lower() == db_col.lower():
                        mapping[csv_col] = db_col
                        break

        return mapping

    def diagnose_all_files(self):
        """Diagnose all CSV files in the data directory"""
        print("🛡️ Schema Guardian Container - Full Diagnosis")
        print("=" * 60)

        data_dir = Path("/app/data/daily_downloads")
        file_mappings = {
            "mapped_horses.csv": "horses",
            "mapped_jockeys_stats.csv": "jockeys_stats",
            "mapped_trainers_stats.csv": "trainers_stats",
            "mapped_records.csv": "records",
            "mapped_races.csv": "races",
        }

        results = {}
        total_compatible = 0

        for csv_file_name, table_name in file_mappings.items():
            csv_file = data_dir / csv_file_name
            if csv_file.exists():
                compatible = self.validate_compatibility(csv_file, table_name)
                results[csv_file_name] = {
                    "table": table_name,
                    "compatible": compatible,
                    "mapping": self.generate_mapping_for_table(csv_file, table_name),
                }
                if compatible:
                    total_compatible += 1
            else:
                print(f"⚠️ File not found: {csv_file_name}")

        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   Compatible files: {total_compatible}/{len(file_mappings)}")
        print(f"   Success rate: {(total_compatible/len(file_mappings))*100:.1f}%")

        # Generate mappings for all files
        print(f"\n🔧 GENERATED MAPPINGS:")
        for file_name, result in results.items():
            if result["mapping"]:
                print(f"\n   {file_name} → {result['table']}:")
                for csv_col, db_col in result["mapping"].items():
                    print(f"     '{csv_col}' → '{db_col}'")

        return results


def main():
    """Run complete schema analysis"""
    guardian = SchemaGuardianContainer()
    results = guardian.diagnose_all_files()

    # Save results for reference
    output_file = Path("/app/data/schema_analysis_results.json")
    with open(output_file, "w") as f:
        # Convert results to JSON-serializable format
        json_results = {}
        for file_name, result in results.items():
            json_results[file_name] = {
                "table": result["table"],
                "compatible": result["compatible"],
                "mapping": result["mapping"],
            }
        json.dump(json_results, f, indent=2)

    print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
