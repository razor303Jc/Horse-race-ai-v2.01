#!/usr/bin/env python3
"""
FINAL SCHEMA GUARDIAN - Name Mapping Fix
Focus on the exact issue: Name column mapping for jockeys_stats and trainers_stats
"""
import pandas as pd
import psycopg2
from pathlib import Path
import re


class FinalSchemaGuardian:
    def __init__(self):
        self.database_config = {
            "host": "horse_racing_postgres_clean",
            "port": 5432,
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Null patterns
        self.null_patterns = {"-", "NULL", "null", "None", "none", "", "N/A", "n/a"}

    def determine_name_mapping(self, csv_columns, table_name):
        """Fix the exact name mapping issue"""
        mapping = {}

        for col in csv_columns:
            col_lower = col.lower().strip()

            # Handle the specific "Name" column mapping issue
            if col == "Name":
                if table_name == "jockeys_stats":
                    mapping[col] = "jockey_name"
                elif table_name == "trainers_stats":
                    mapping[col] = "trainer_name"
                elif table_name == "horses":
                    mapping[col] = "horse_name"
                else:
                    mapping[col] = "name"

            # Standard mappings
            elif "id" in col_lower and col_lower != "id":
                mapping[col] = col_lower.replace(" ", "_")
            elif col_lower in ["id"]:
                mapping[col] = "id"
            else:
                # Standard case conversion
                normalized = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\\1_\\2", col)
                normalized = re.sub(r"([a-z\\d])([A-Z])", r"\\1_\\2", normalized)
                mapping[col] = normalized.lower()

        return mapping

    def clean_value(self, value):
        """Basic value cleaning"""
        if pd.isna(value) or str(value).strip() in self.null_patterns:
            return None

        value_str = str(value).strip()

        # Handle percentages
        if value_str.endswith("%"):
            try:
                return float(value_str[:-1])
            except:
                return None

        return value_str if value_str else None

    def upload_table(self, csv_file, table_name):
        """Upload a single table with correct name mapping"""
        print(f"\\n🚀 Processing: {csv_file} → {table_name}")

        # Load CSV
        csv_path = Path("/app/data/daily_downloads") / csv_file
        if not csv_path.exists():
            print(f"❌ File not found: {csv_path}")
            return False

        df = pd.read_csv(csv_path)
        print(f"📋 Loaded: {len(df)} rows, {len(df.columns)} columns")
        print(f"📋 CSV columns: {list(df.columns)}")

        # Generate mapping
        mapping = self.determine_name_mapping(df.columns, table_name)
        print(f"🗺️  Column mapping: {mapping}")

        # Apply mapping
        mapped_df = df.rename(columns=mapping)

        # Clean data
        for col in mapped_df.columns:
            mapped_df[col] = mapped_df[col].apply(self.clean_value)

        # Remove empty rows
        cleaned_df = mapped_df.dropna(how="all")
        print(f"📋 Final data: {len(cleaned_df)} rows")

        # Upload to database
        try:
            conn = psycopg2.connect(**self.database_config)

            columns = list(cleaned_df.columns)
            placeholders = ", ".join(["%s"] * len(columns))
            columns_str = ", ".join(columns)

            insert_query = f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """

            # Convert to tuples
            data_tuples = [
                tuple(None if pd.isna(val) else val for val in row)
                for _, row in cleaned_df.iterrows()
            ]

            # Execute upload
            with conn.cursor() as cur:
                cur.executemany(insert_query, data_tuples)
                conn.commit()

                # Check uploaded count
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                total_count = cur.fetchone()[0]

            conn.close()
            print(f"✅ SUCCESS: {len(data_tuples)} rows uploaded to {table_name}")
            print(f"📊 Total records in {table_name}: {total_count}")
            return True

        except Exception as e:
            print(f"❌ FAILED: {table_name} - {e}")
            return False

    def run_final_test(self):
        """Run the final test focusing on name mapping fix"""
        print("🎯 FINAL SCHEMA GUARDIAN - NAME MAPPING FIX")
        print("=" * 60)

        # Focus on the 2 failing tables
        test_tables = {
            "mapped_jockeys_stats.csv": "jockeys_stats",
            "mapped_trainers_stats.csv": "trainers_stats",
        }

        results = {}
        for csv_file, table_name in test_tables.items():
            results[csv_file] = self.upload_table(csv_file, table_name)

        # Summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        success_rate = (successful / total) * 100

        print(f"\\n🏆 FINAL RESULTS:")
        print(f"   Tables tested: {total}")
        print(f"   Successful uploads: {successful}")
        print(f"   Success rate: {success_rate:.1f}%")

        if success_rate == 100:
            print("🎉 PERFECT SUCCESS! Name mapping issue RESOLVED!")
        else:
            print("⚠️  Still debugging needed")

        return results


def main():
    guardian = FinalSchemaGuardian()
    results = guardian.run_final_test()
    return results


if __name__ == "__main__":
    main()
