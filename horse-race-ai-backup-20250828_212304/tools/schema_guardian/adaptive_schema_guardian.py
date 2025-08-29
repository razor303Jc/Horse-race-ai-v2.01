#!/usr/bin/env python3
"""
Adaptive Schema Guardian - Handles Dynamic CSV Changes & Case Issues
Automatically maintains schema consistency regardless of CSV format changes
"""

import pandas as pd
import psycopg2
from pathlib import Path
import json
import os
from typing import Dict, List, Tuple
import re
from difflib import SequenceMatcher


class AdaptiveSchemaGuardian:
    """
    Adaptive Schema Guardian - Intelligent CSV-to-Database Mapping

    Features:
    1. Automatic case-insensitive column matching
    2. Dynamic CSV structure adaptation
    3. Intelligent column name similarity matching
    4. Consistent database schema maintenance
    5. Automatic mapping generation and updates
    """

    def __init__(self):
        self.database_config = {
            "host": "postgres",
            "port": 5432,
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Core database schema - what we ALWAYS maintain
        self.core_schemas = {
            "horses": [
                "horse_id",
                "horse_name",
                "age",
                "sex",
                "color",
                "sire",
                "dam",
                "owner",
                "breeder",
                "created_at",
            ],
            "jockeys_stats": [
                "jockey_id",
                "jockey_name",
                "wins",
                "runs",
                "win_rate",
                "place_rate",
                "created_at",
            ],
            "trainers_stats": [
                "trainer_id",
                "trainer_name",
                "wins",
                "runs",
                "win_rate",
                "place_rate",
                "created_at",
            ],
            "records": [
                "id",
                "race_id",
                "horse_number",
                "place",
                "draw",
                "horse_id",
                "country",
                "name",
                "age",
                "weight_uk",
                "weight",
                "jockey_id",
                "jockey",
                "trainer_id",
                "trainer",
                "sp",
                "created_at",
            ],
            "races": [
                "race_id",
                "race_number",
                "race_time",
                "course_id",
                "course",
                "race_type",
                "date",
                "race_name",
                "class",
                "distance",
                "surface",
                "created_at",
            ],
        }

        # Intelligent mapping patterns - handles ANY case variation
        self.mapping_patterns = {
            # ID patterns
            r"^(id|ID|Id)$": "id",
            r"^(race_id|Race_ID|RACE_ID|raceid|RaceID)$": "race_id",
            r"^(horse_id|Horse_ID|HORSE_ID|horseid|HorseID)$": "horse_id",
            r"^(jockey_id|Jockey_ID|JOCKEY_ID|jockeyid|JockeyID)$": "jockey_id",
            r"^(trainer_id|Trainer_ID|TRAINER_ID|trainerid|TrainerID)$": "trainer_id",
            # Name patterns
            r"^(name|Name|NAME|horse_name|Horse_Name|HORSE_NAME)$": "horse_name",
            r"^(jockey_name|Jockey_Name|JOCKEY_NAME|jockey|Jockey|JOCKEY)$": "jockey_name",
            r"^(trainer_name|Trainer_Name|TRAINER_NAME|trainer|Trainer|TRAINER)$": "trainer_name",
            # Date/Update patterns
            r"^(uptodate|UptoDate|UPTODATE|up_to_date|Up_To_Date)$": "uptodate",
            r"^(date|Date|DATE)$": "date",
            # Common field patterns
            r"^(age|Age|AGE)$": "age",
            r"^(sex|Sex|SEX|gender|Gender|GENDER)$": "sex",
            r"^(color|Color|COLOR|colour|Colour|COLOUR)$": "color",
            r"^(wins|Wins|WINS)$": "wins",
            r"^(runs|Runs|RUNS|total_races|Total_Races)$": "runs",
            r"^(place|Place|PLACE|position|Position|POSITION)$": "place",
            r"^(course|Course|COURSE)$": "course",
            r"^(distance|Distance|DISTANCE)$": "distance",
            r"^(surface|Surface|SURFACE)$": "surface",
            r"^(sp|SP|starting_price|Starting_Price)$": "sp",
        }

    def normalize_column_name(self, column_name: str) -> str:
        """
        Normalize any column name to standard database format
        Handles any case variation or naming convention
        """
        # Remove extra whitespace
        column_name = column_name.strip()

        # Check against mapping patterns
        for pattern, normalized in self.mapping_patterns.items():
            if re.match(pattern, column_name):
                return normalized

        # If no pattern match, convert to lowercase with underscores
        # Handle camelCase, PascalCase, snake_case, etc.
        normalized = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", column_name)
        normalized = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", normalized)
        normalized = normalized.lower()
        normalized = re.sub(r"[^a-z0-9_]", "_", normalized)
        normalized = re.sub(r"_+", "_", normalized)
        normalized = normalized.strip("_")

        return normalized

    def find_similar_columns(
        self, csv_column: str, db_columns: List[str], threshold: float = 0.6
    ) -> List[Tuple[str, float]]:
        """
        Find database columns similar to CSV column using fuzzy matching
        Returns list of (column_name, similarity_score) tuples
        """
        similarities = []
        csv_normalized = self.normalize_column_name(csv_column)

        for db_col in db_columns:
            # Direct normalized match
            if csv_normalized == db_col:
                similarities.append((db_col, 1.0))
                continue

            # Fuzzy string matching
            similarity = SequenceMatcher(None, csv_normalized, db_col).ratio()
            if similarity >= threshold:
                similarities.append((db_col, similarity))

        # Sort by similarity score (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities

    def get_database_schema(self, table_name: str) -> Dict:
        """Get current database schema"""
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

    def generate_adaptive_mapping(
        self, csv_file: Path, table_name: str
    ) -> Dict[str, str]:
        """
        Generate adaptive column mapping that handles ANY CSV format changes
        """
        print(f"🧠 Generating adaptive mapping for {csv_file.name} → {table_name}")

        # Read CSV structure
        try:
            df = pd.read_csv(csv_file, nrows=5)
            csv_columns = list(df.columns)
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
            return {}

        # Get database schema
        db_schema = self.get_database_schema(table_name)
        db_columns = list(db_schema.keys())

        if not db_columns:
            print(f"❌ No database schema found for {table_name}")
            return {}

        print(
            f"📄 CSV columns ({len(csv_columns)}): {csv_columns[:10]}{'...' if len(csv_columns) > 10 else ''}"
        )
        print(f"🗃️  DB columns ({len(db_columns)}): {db_columns}")

        mapping = {}
        unmapped_csv = []
        unmapped_db = []

        # Phase 1: Exact normalized matches
        for csv_col in csv_columns:
            normalized = self.normalize_column_name(csv_col)
            if normalized in db_columns:
                mapping[csv_col] = normalized
                print(f"✅ Exact match: '{csv_col}' → '{normalized}'")
            else:
                unmapped_csv.append(csv_col)

        # Phase 2: Fuzzy matching for unmapped columns
        mapped_db_cols = set(mapping.values())
        available_db_cols = [col for col in db_columns if col not in mapped_db_cols]

        for csv_col in unmapped_csv[:]:  # Use slice to modify list during iteration
            similar_cols = self.find_similar_columns(
                csv_col, available_db_cols, threshold=0.7
            )

            if similar_cols:
                best_match, score = similar_cols[0]
                mapping[csv_col] = best_match
                available_db_cols.remove(best_match)
                unmapped_csv.remove(csv_col)
                print(
                    f"🔧 Fuzzy match: '{csv_col}' → '{best_match}' (score: {score:.2f})"
                )

        # Phase 3: Report unmapped columns
        if unmapped_csv:
            print(
                f"⚠️  Unmapped CSV columns ({len(unmapped_csv)}): {unmapped_csv[:5]}{'...' if len(unmapped_csv) > 5 else ''}"
            )

        unmapped_db = [
            col
            for col in db_columns
            if col not in mapping.values() and col != "created_at"
        ]
        if unmapped_db:
            print(f"⚠️  Unmapped DB columns ({len(unmapped_db)}): {unmapped_db}")

        return mapping

    def clean_data_for_upload(
        self, df: pd.DataFrame, mapping: Dict[str, str], table_name: str
    ) -> pd.DataFrame:
        """
        Clean and prepare data for database upload
        """
        print(f"🧹 Cleaning data for {table_name}")

        # Apply column mapping
        mapped_df = df.rename(columns=mapping)

        # Keep only columns that exist in database
        db_schema = self.get_database_schema(table_name)
        db_columns = list(db_schema.keys())

        # Filter to only mapped columns that exist in database
        available_cols = [col for col in mapped_df.columns if col in db_columns]
        cleaned_df = mapped_df[available_cols].copy()

        print(f"📊 Data shape: {df.shape} → {cleaned_df.shape}")
        print(f"📋 Final columns: {list(cleaned_df.columns)}")

        # Clean data values
        for col in cleaned_df.columns:
            # Handle null values
            cleaned_df[col] = cleaned_df[col].replace(
                ["-", "", "None", "NULL", "null"], pd.NA
            )

            # Clean whitespace for string columns
            if cleaned_df[col].dtype == "object":
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
                cleaned_df[col] = cleaned_df[col].replace("nan", pd.NA)

        return cleaned_df

    def upload_with_adaptive_mapping(self, csv_file: Path, table_name: str) -> bool:
        """
        Upload CSV with automatic adaptive mapping
        """
        print(f"\n🚀 Adaptive upload: {csv_file.name} → {table_name}")

        # Generate mapping
        mapping = self.generate_adaptive_mapping(csv_file, table_name)
        if not mapping:
            print("❌ Could not generate mapping")
            return False

        # Read and clean data
        try:
            df = pd.read_csv(csv_file)
            cleaned_df = self.clean_data_for_upload(df, mapping, table_name)

            if len(cleaned_df) == 0:
                print("⚠️  No data to upload after cleaning")
                return False

            # Upload to database
            conn = psycopg2.connect(**self.database_config)

            # Prepare data for bulk insert
            columns = list(cleaned_df.columns)
            placeholders = ", ".join(["%s"] * len(columns))
            columns_str = ", ".join(columns)

            insert_query = f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """

            # Convert DataFrame to list of tuples
            data_tuples = [tuple(row) for row in cleaned_df.to_numpy()]

            with conn.cursor() as cur:
                cur.executemany(insert_query, data_tuples)
                conn.commit()

                # Get final count
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                total_count = cur.fetchone()[0]

            conn.close()

            print(f"✅ Upload successful!")
            print(f"   Processed: {len(df)} rows")
            print(f"   Uploaded: {len(cleaned_df)} rows")
            print(f"   Total in DB: {total_count} rows")

            return True

        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False

    def process_all_csv_files(self, data_directory: Path = None) -> Dict:
        """
        Process all CSV files with adaptive mapping
        """
        if data_directory is None:
            data_directory = Path("/app/data/daily_downloads")

        print("🛡️  Adaptive Schema Guardian - Processing All CSV Files")
        print("=" * 70)

        # Define file-to-table mappings
        file_mappings = {
            "mapped_horses.csv": "horses",
            "mapped_jockeys_stats.csv": "jockeys_stats",
            "mapped_trainers_stats.csv": "trainers_stats",
            "mapped_records.csv": "records",
            "mapped_races.csv": "races",
        }

        results = {}
        successful_uploads = 0

        for csv_filename, table_name in file_mappings.items():
            csv_file = data_directory / csv_filename

            if not csv_file.exists():
                print(f"⚠️  File not found: {csv_filename}")
                results[csv_filename] = {"status": "not_found", "success": False}
                continue

            success = self.upload_with_adaptive_mapping(csv_file, table_name)
            results[csv_filename] = {
                "status": "success" if success else "failed",
                "success": success,
                "table": table_name,
            }

            if success:
                successful_uploads += 1

        # Summary
        total_files = len(file_mappings)
        success_rate = (successful_uploads / total_files) * 100

        print(f"\n📊 FINAL SUMMARY:")
        print(f"   Total files: {total_files}")
        print(f"   Successful: {successful_uploads}")
        print(f"   Success rate: {success_rate:.1f}%")

        if success_rate == 100:
            print("🎉 ALL CSV FILES UPLOADED SUCCESSFULLY!")
            print("🛡️  Schema consistency maintained automatically")
        else:
            print("⚠️  Some files need attention")

        return results


def main():
    """Run adaptive schema guardian"""
    guardian = AdaptiveSchemaGuardian()
    results = guardian.process_all_csv_files()

    # Save results
    output_file = Path("/app/data/adaptive_upload_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
