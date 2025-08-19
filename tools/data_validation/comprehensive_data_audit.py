#!/usr/bin/env python3
"""
Comprehensive Data Mapping & Quality Audit
Address TODO: Data Mapping & Cleaning Review 🔥 CRITICAL

This script performs a full audit of:
1. Column mappings vs database schema
2. Data type conversions and validation
3. Data quality issues identification
4. Transformation rule validation
"""

import json
import pandas as pd
import psycopg2
from pathlib import Path
from decimal import Decimal
import re


class DataMappingAuditor:
    """Comprehensive data mapping and quality auditor"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.conn = None
        self.cursor = None
        self.issues = []
        self.recommendations = []

    def connect_to_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                port="5434",
                database="horse_racing_db",
                user="horse_racing",
                password="secure_password_123",
            )
            self.cursor = self.conn.cursor()
            print("✅ Connected to database")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def load_mapping_config(self):
        """Load column mapping configuration"""
        config_file = self.project_root / "config" / "complete_csv_column_mapping.json"
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load mapping config: {e}")
            return None

    def get_database_schema(self, table_name):
        """Get actual database schema for comparison"""
        self.cursor.execute(
            """
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position
        """,
            (table_name,),
        )
        return {
            row[0]: {"type": row[1], "nullable": row[2]}
            for row in self.cursor.fetchall()
        }

    def audit_column_mappings(self):
        """PRIORITY 1: Full audit of column mappings"""
        print("🔍 PRIORITY 1: Auditing Column Mappings...")

        config = self.load_mapping_config()
        if not config:
            return False

        for table_name, table_config in config["table_mappings"].items():
            print(f"\n📊 Auditing table: {table_name}")

            # Get actual database schema
            db_schema = self.get_database_schema(table_name)
            if not db_schema:
                self.issues.append(
                    f"❌ Table '{table_name}' does not exist in database"
                )
                continue

            # Check column mappings
            mapping = table_config.get("column_mapping", {})
            for db_col, csv_col in mapping.items():
                if db_col not in db_schema:
                    self.issues.append(
                        f"❌ {table_name}: Database column '{db_col}' not found"
                    )
                else:
                    print(f"  ✅ {db_col} -> {csv_col}")

            # Check for missing columns
            mapped_cols = set(mapping.keys())
            actual_cols = set(db_schema.keys()) - {
                "id",
                "created_at",
                "updated_at",
            }  # Exclude auto columns
            missing_cols = actual_cols - mapped_cols
            if missing_cols:
                self.issues.append(f"⚠️ {table_name}: Unmapped columns: {missing_cols}")

        return True

    def audit_data_type_conversions(self):
        """PRIORITY 2: Validate all data type conversions"""
        print("\n🔍 PRIORITY 2: Auditing Data Type Conversions...")

        # Check records table data quality
        self.cursor.execute(
            """
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN weight_uk = 0 OR weight_uk IS NULL THEN 1 END) as zero_weight_uk,
                COUNT(CASE WHEN weight = 0 OR weight IS NULL THEN 1 END) as zero_weight,
                COUNT(CASE WHEN sp = 0 OR sp IS NULL THEN 1 END) as zero_sp,
                AVG(weight_uk) as avg_weight_uk,
                AVG(weight) as avg_weight
            FROM records
        """
        )
        stats = self.cursor.fetchone()

        print(f"📊 Records Data Quality:")
        print(f"  - Total records: {stats[0]}")
        print(f"  - Zero/null weight_uk: {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
        print(f"  - Zero/null weight: {stats[2]} ({stats[2]/stats[0]*100:.1f}%)")
        print(f"  - Zero/null SP: {stats[3]} ({stats[3]/stats[0]*100:.1f}%)")
        print(f"  - Avg weight_uk: {stats[4]:.2f}")
        print(f"  - Avg weight: {stats[5]:.2f}")

        # Critical issue: Weight conversion appears wrong
        if stats[4] and stats[5]:
            weight_ratio = float(stats[5]) / float(stats[4]) if stats[4] > 0 else 0
            if weight_ratio > 5:  # Should be close to 14 (stones to pounds conversion)
                self.issues.append(
                    f"🚨 CRITICAL: Weight conversion ratio is {weight_ratio:.1f}, expected ~14 (stones to pounds)"
                )
                self.recommendations.append(
                    "Review weight_uk to weight conversion logic in clean_data.py"
                )

        # Check for obvious data quality issues
        if stats[1] > stats[0] * 0.5:  # More than 50% missing weight_uk
            self.issues.append(
                f"🚨 CRITICAL: {stats[1]/stats[0]*100:.1f}% of records missing weight_uk conversion"
            )

    def audit_transformation_rules(self):
        """PRIORITY 3: Check transformation rules and edge cases"""
        print("\n🔍 PRIORITY 3: Auditing Transformation Rules...")

        # Check for unconverted weight formats in the database
        self.cursor.execute(
            """
            SELECT weight_uk, weight, sp 
            FROM records 
            WHERE weight_uk IS NOT NULL AND weight_uk != 0 
            LIMIT 10
        """
        )
        sample_data = self.cursor.fetchall()

        print("📊 Weight Conversion Samples:")
        for row in sample_data:
            uk_weight, decimal_weight, sp = row
            if uk_weight and decimal_weight:
                ratio = float(decimal_weight) / float(uk_weight)
                expected_ratio = 14  # 1 stone = 14 pounds
                if abs(ratio - expected_ratio) > 2:
                    self.issues.append(
                        f"⚠️ Suspicious weight conversion: UK {uk_weight} -> {decimal_weight} (ratio: {ratio:.1f})"
                    )
                print(
                    f"  - UK: {uk_weight} -> Decimal: {decimal_weight} (ratio: {ratio:.1f})"
                )

        # Check for fractional odds that weren't converted
        self.cursor.execute(
            """
            SELECT sp FROM records 
            WHERE sp IS NOT NULL AND sp != 0 
            AND sp::text LIKE '%/%'
            LIMIT 5
        """
        )
        fractional_odds = self.cursor.fetchall()
        if fractional_odds:
            self.issues.append(
                f"🚨 Found {len(fractional_odds)} records with unconverted fractional odds"
            )
            for odds in fractional_odds:
                print(f"  - Unconverted odds: {odds[0]}")

    def audit_data_integrity(self):
        """PRIORITY 4: Data integrity checks and constraint validation"""
        print("\n🔍 PRIORITY 4: Auditing Data Integrity...")

        # Check for referential integrity
        self.cursor.execute(
            """
            SELECT COUNT(DISTINCT r.race_id) as distinct_race_ids,
                   COUNT(DISTINCT rc.race_id) as races_with_records
            FROM records r
            LEFT JOIN races rc ON r.race_id = rc.race_id
        """
        )
        integrity = self.cursor.fetchone()
        print(f"📊 Referential Integrity:")
        print(f"  - Distinct race_ids in records: {integrity[0]}")
        print(f"  - Races with matching records: {integrity[1] or 0}")

        if integrity[0] != integrity[1]:
            orphaned = integrity[0] - (integrity[1] or 0)
            self.issues.append(
                f"⚠️ Found {orphaned} race_ids in records without matching races"
            )

        # Check for reasonable data ranges
        self.cursor.execute(
            """
            SELECT 
                MIN(age) as min_age, MAX(age) as max_age,
                MIN(weight) as min_weight, MAX(weight) as max_weight,
                MIN(sp) as min_sp, MAX(sp) as max_sp
            FROM records
            WHERE age IS NOT NULL AND weight IS NOT NULL AND sp IS NOT NULL
        """
        )
        ranges = self.cursor.fetchone()

        print(f"📊 Data Ranges:")
        print(f"  - Age: {ranges[0]} to {ranges[1]}")
        print(f"  - Weight: {ranges[2]} to {ranges[3]}")
        print(f"  - SP: {ranges[4]} to {ranges[5]}")

        # Validate ranges
        if ranges[0] and ranges[0] < 2:
            self.issues.append(f"⚠️ Minimum age {ranges[0]} seems too low")
        if ranges[1] and ranges[1] > 20:
            self.issues.append(f"⚠️ Maximum age {ranges[1]} seems too high")
        if ranges[2] and ranges[2] < 40:  # Weight in kg
            self.issues.append(f"⚠️ Minimum weight {ranges[2]}kg seems too low")
        if ranges[3] and ranges[3] > 80:
            self.issues.append(f"⚠️ Maximum weight {ranges[3]}kg seems too high")

    def check_csv_files_exist(self):
        """Check if CSV files referenced in mapping exist"""
        print("\n🔍 Checking CSV File Availability...")

        config = self.load_mapping_config()
        if not config:
            return

        for table_name, table_config in config["table_mappings"].items():
            csv_files = table_config.get("csv_files", [])
            for csv_file in csv_files:
                file_path = self.project_root / csv_file
                if not file_path.exists():
                    self.issues.append(f"❌ CSV file not found: {csv_file}")
                else:
                    print(f"  ✅ Found: {csv_file}")

    def generate_recommendations(self):
        """Generate specific recommendations based on findings"""
        print("\n📋 Generating Recommendations...")

        # Weight conversion fix
        self.recommendations.extend(
            [
                "1. Fix weight conversion in clean_data.py - UK format should convert stones-pounds to decimal kilograms",
                "2. Implement proper fractional odds conversion (e.g., '5/2' -> 3.5)",
                "3. Add data validation tests for each transformation rule",
                "4. Create constraint checks for data ranges (age 2-20, weight 40-80kg, etc.)",
                "5. Implement referential integrity checks between tables",
                "6. Add null value handling documentation for each field type",
            ]
        )

    def run_full_audit(self):
        """Execute complete data mapping audit"""
        print("🚀 Starting Comprehensive Data Mapping Audit...")
        print("=" * 60)

        if not self.connect_to_database():
            return False

        # Execute all audit steps
        self.audit_column_mappings()
        self.audit_data_type_conversions()
        self.audit_transformation_rules()
        self.audit_data_integrity()
        self.check_csv_files_exist()
        self.generate_recommendations()

        # Generate report
        self.generate_audit_report()

        if self.conn:
            self.conn.close()

        return len(self.issues) == 0

    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "=" * 60)
        print("📊 DATA MAPPING AUDIT REPORT")
        print("=" * 60)

        if self.issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. {issue}")
        else:
            print("\n✅ No critical issues found!")

        if self.recommendations:
            print(f"\n📋 RECOMMENDATIONS ({len(self.recommendations)}):")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"{i}. {rec}")

        # Save report to file
        report_file = self.project_root / "reports" / "data_mapping_audit_report.md"
        with open(report_file, "w") as f:
            f.write("# Data Mapping Audit Report\n\n")
            f.write(f"**Generated**: {pd.Timestamp.now()}\n\n")

            if self.issues:
                f.write(f"## 🚨 Critical Issues ({len(self.issues)})\n\n")
                for i, issue in enumerate(self.issues, 1):
                    f.write(f"{i}. {issue}\n")
                f.write("\n")

            if self.recommendations:
                f.write(f"## 📋 Recommendations ({len(self.recommendations)})\n\n")
                for i, rec in enumerate(self.recommendations, 1):
                    f.write(f"{i}. {rec}\n")

        print(f"\n📄 Report saved to: {report_file}")


if __name__ == "__main__":
    auditor = DataMappingAuditor()
    success = auditor.run_full_audit()

    if not success:
        print("\n🚨 AUDIT FAILED - Critical issues require immediate attention!")
        exit(1)
    else:
        print("\n✅ AUDIT COMPLETED - System ready for production!")
