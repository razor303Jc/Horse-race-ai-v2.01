#!/usr/bin/env python3
"""
CSV File Database Mapping Validator
Validates which CSV files should go to which database and table
"""

import psycopg2
import pandas as pd
from pathlib import Path

# Database configuration
DB_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "user": "horse_racing",
    "password": "secure_password_123",
}

# Expected file to database/table mapping
FILE_MAPPING = {
    # Cards database (race cards, current race information)
    "cards_horse_racing_db": {
        "horses.csv": "horses",  # Horse information for race cards
        "races.csv": "races",  # Race information for race cards
        "racecard_details.csv": "racecard_details",  # Detailed race card entries
    },
    # Results database (historical results and performance)
    "results_horse_racing_db": {
        # Note: These would typically be result files with different structure
        # "race_results.csv": "race_results",
        # "records.csv": "records"
    },
}


def get_table_schema(database, table):
    """Get table schema from database"""
    try:
        conn = psycopg2.connect(database=database, **DB_CONFIG)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position
        """,
            (table,),
        )

        schema = {}
        for row in cur.fetchall():
            schema[row[0]] = {
                "type": row[1],
                "nullable": row[2] == "YES",
                "default": row[3],
            }

        conn.close()
        return schema
    except Exception as e:
        print(f"Error getting schema for {database}.{table}: {e}")
        return {}


def analyze_csv_file(file_path):
    """Analyze CSV file structure"""
    try:
        df = pd.read_csv(file_path, nrows=5)  # Read first 5 rows for analysis

        return {
            "file_path": str(file_path),
            "columns": list(df.columns),
            "row_count": len(df),
            "sample_data": df.head(2).to_dict("records"),
        }
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return None


def validate_csv_to_table_mapping(csv_file, database, table):
    """Validate if CSV file matches table schema"""
    print(f"\n🔍 Validating: {csv_file} → {database}.{table}")

    # Analyze CSV file
    csv_info = analyze_csv_file(csv_file)
    if not csv_info:
        return False

    # Get table schema
    table_schema = get_table_schema(database, table)
    if not table_schema:
        return False

    print(f"📄 CSV columns ({len(csv_info['columns'])}): {csv_info['columns'][:5]}...")
    print(f"🗃️  DB columns ({len(table_schema)}): {list(table_schema.keys())[:5]}...")

    # Check column compatibility
    csv_columns = set(csv_info["columns"])
    db_columns = set(table_schema.keys())

    # Exact matches
    exact_matches = csv_columns.intersection(db_columns)

    # Missing in CSV (required columns)
    required_columns = {
        col
        for col, schema in table_schema.items()
        if not schema["nullable"] and schema["default"] is None
    }
    missing_required = required_columns - csv_columns

    # Extra in CSV (not in database)
    extra_columns = csv_columns - db_columns

    # Results
    print(f"✅ Exact matches: {len(exact_matches)}/{len(csv_columns)}")
    print(f"⚠️  Extra in CSV: {len(extra_columns)} - {list(extra_columns)[:3]}...")
    print(f"❌ Missing required: {len(missing_required)} - {list(missing_required)}")

    if missing_required:
        print(f"   Missing required columns: {missing_required}")
        return False

    compatibility_score = len(exact_matches) / len(csv_columns) if csv_columns else 0
    print(f"📊 Compatibility: {compatibility_score:.1%}")

    return compatibility_score > 0.7  # 70% compatibility threshold


def scan_processed_directory():
    """Scan the processed directory for CSV files"""
    base_path = Path("/app/data/daily_downloads/processed")
    csv_files = []

    # Find all CSV files, excluding non_target
    for csv_file in base_path.rglob("*.csv"):
        if "non_target" not in str(csv_file):
            csv_files.append(csv_file)

    return sorted(csv_files)


def main():
    """Main validation function"""
    print("🚀 CSV File Database Mapping Validator")
    print("=" * 50)

    # Scan for CSV files
    csv_files = scan_processed_directory()

    if not csv_files:
        print("❌ No CSV files found in processed directory")
        return

    print(f"📋 Found {len(csv_files)} CSV files to validate")

    validation_results = {}

    # Validate each file against expected mappings
    for csv_file in csv_files:
        file_name = csv_file.name
        print(f"\n{'='*60}")
        print(
            f"📄 File: {csv_file.relative_to(Path('/app/data/daily_downloads/processed'))}"
        )

        # Find matching database and table
        matched = False
        for database, file_mappings in FILE_MAPPING.items():
            if file_name in file_mappings:
                table = file_mappings[file_name]
                is_valid = validate_csv_to_table_mapping(csv_file, database, table)

                validation_results[str(csv_file)] = {
                    "database": database,
                    "table": table,
                    "valid": is_valid,
                    "file_name": file_name,
                }
                matched = True
                break

        if not matched:
            print(f"⚠️  No mapping found for {file_name}")
            validation_results[str(csv_file)] = {
                "database": "UNKNOWN",
                "table": "UNKNOWN",
                "valid": False,
                "file_name": file_name,
            }

    # Summary
    print(f"\n{'='*60}")
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)

    total_files = len(validation_results)
    valid_files = sum(1 for r in validation_results.values() if r["valid"])

    print(f"Total files: {total_files}")
    print(f"Valid mappings: {valid_files}")
    print(f"Success rate: {valid_files/total_files*100:.1f}%")

    print("\n📋 DETAILED RESULTS:")
    for file_path, result in validation_results.items():
        status = "✅" if result["valid"] else "❌"
        rel_path = Path(file_path).relative_to(
            Path("/app/data/daily_downloads/processed")
        )
        print(f"{status} {rel_path} → {result['database']}.{result['table']}")

    # Generate upload recommendations
    print(f"\n🚀 UPLOAD RECOMMENDATIONS:")
    for file_path, result in validation_results.items():
        if result["valid"]:
            rel_path = Path(file_path).relative_to(
                Path("/app/data/daily_downloads/processed")
            )
            print(f"✅ READY: {rel_path} → {result['database']}.{result['table']}")

    return validation_results


if __name__ == "__main__":
    main()
