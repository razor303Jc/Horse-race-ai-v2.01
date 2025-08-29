#!/usr/bin/env python3
"""
🎯 Intelligent Column Mapper
============================

Robust solution for handling CSV column name variations and mapping them
to consistent database schema column names.

Features:
- Automatic column name normalization
- Fuzzy matching for similar column names
- Database schema validation
- Multiple fallback strategies
- Comprehensive logging and reporting
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import psycopg2
from fuzzywuzzy import fuzz, process
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
logger = logging.getLogger(__name__)


class IntelligentColumnMapper:
    """Intelligent column mapping with multiple fallback strategies"""

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.table_schemas = {}
        self.column_mapping_rules = {}
        self.load_mapping_rules()
        self.fetch_database_schemas()

    def load_mapping_rules(self):
        """Load column mapping rules and aliases"""
        self.column_mapping_rules = {
            # Standard transformations
            "normalization_rules": [
                # Convert CamelCase to snake_case
                (r"([a-z0-9])([A-Z])", r"\1_\2"),
                # Replace common separators with underscores
                (r"[-\s]+", "_"),
                # Remove special characters except underscores
                (r"[^\w]", ""),
                # Convert to lowercase
                (lambda x: x.lower(), None),
            ],
            # Common column aliases (CSV_name -> database_name)
            "column_aliases": {
                # Race table aliases
                "race_id": ["Race_ID", "RaceID", "raceid", "id"],
                "race_number": ["race_number", "Race_Number", "RaceNumber", "number"],
                "race_time": ["race_time", "Race_Time", "RaceTime", "time"],
                "course_id": ["course_id", "Course_ID", "CourseID", "courseid"],
                "course": ["Course", "course", "COURSE", "track"],
                "race_type": ["Race_type", "RaceType", "race_type", "type"],
                "date": ["Date", "date", "DATE", "race_date"],
                "race_name": ["Race_name", "RaceName", "race_name", "name"],
                "class": ["Class", "class", "CLASS", "race_class"],
                "years": ["Years", "years", "YEARS", "age_range"],
                "distance": ["Distance", "distance", "DISTANCE"],
                "surface": ["Surface", "surface", "SURFACE", "track_surface"],
                "prize": ["Prize", "prize", "PRIZE", "prize_money"],
                "runners_racecard": [
                    "Runners_racecard",
                    "RunnersRacecard",
                    "runners_racecard",
                ],
                "runners": ["Runners", "runners", "RUNNERS", "field_size"],
                "draw": ["Draw", "draw", "DRAW"],
                "ew_racecard": ["EW_racecard", "EWRacecard", "ew_racecard"],
                "ew": ["EW", "ew", "each_way"],
                "places_ew_racecard": ["Places_EW_racecard", "PlacesEWRacecard"],
                "places_ew": ["Places_EW", "PlacesEW", "places_ew"],
                # Horse table aliases
                "horse_id": ["id", "ID", "horse_id", "Horse_ID", "HorseID"],
                "horse_name": ["name", "Name", "NAME", "horse_name", "Horse_Name"],
                "age": ["age", "Age", "AGE"],
                "sex": ["sex", "Sex", "SEX", "gender"],
                "color": ["color", "Color", "COLOR", "colour", "Colour"],
                "sire": ["sire", "Sire", "SIRE"],
                "dam": ["dam", "Dam", "DAM"],
                "owner": ["owner", "Owner", "OWNER"],
                "breeder": ["breeder", "Breeder", "BREEDER"],
                # Stats table aliases (jockeys/trainers)
                "total_races": ["Total_races", "TotalRaces", "total_races", "races"],
                "wins": ["Wins", "wins", "WINS", "victories"],
                "percentage_wins": [
                    "Percentage_wins",
                    "PercentageWins",
                    "win_rate",
                    "win_percentage",
                ],
                "placed": ["placed", "Placed", "PLACED", "placings"],
                "percentage_placed": [
                    "Percentage_placed",
                    "PercentagePlaced",
                    "place_rate",
                ],
            },
            # Data type patterns for validation
            "data_type_patterns": {
                "integer": ["id", "number", "runners", "age", "wins", "placed"],
                "decimal": ["percentage", "rate", "odds"],
                "date": ["date", "created_at", "updated_at"],
                "time": ["time"],
                "varchar": [
                    "name",
                    "course",
                    "type",
                    "class",
                    "surface",
                    "color",
                    "sex",
                ],
            },
        }

    def fetch_database_schemas(self):
        """Fetch database schemas for all tables"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            # Get all table names
            cursor.execute(
                """
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename NOT LIKE 'pg_%'
            """
            )
            tables = [row[0] for row in cursor.fetchall()]

            # Get schema for each table
            for table in tables:
                cursor.execute(
                    f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s 
                    ORDER BY ordinal_position
                """,
                    (table,),
                )

                self.table_schemas[table] = {
                    row[0]: {
                        "type": row[1],
                        "nullable": row[2] == "YES",
                        "default": row[3],
                    }
                    for row in cursor.fetchall()
                }

            conn.close()
            console.print(f"✅ Loaded schemas for {len(self.table_schemas)} tables")

        except Exception as e:
            console.print(f"[red]❌ Failed to fetch database schemas: {e}[/red]")
            self.table_schemas = {}

    def normalize_column_name(self, column_name: str) -> str:
        """Normalize column name using transformation rules"""
        normalized = column_name

        for rule in self.column_mapping_rules["normalization_rules"]:
            if callable(rule[0]):
                normalized = rule[0](normalized)
            else:
                normalized = re.sub(rule[0], rule[1], normalized)

        return normalized.strip("_")

    def find_best_column_match(self, csv_column: str, table_name: str) -> Optional[str]:
        """Find best matching database column for CSV column"""
        if table_name not in self.table_schemas:
            return None

        db_columns = list(self.table_schemas[table_name].keys())

        # Strategy 1: Exact match after normalization
        normalized = self.normalize_column_name(csv_column)
        if normalized in db_columns:
            return normalized

        # Strategy 2: Check aliases
        aliases = self.column_mapping_rules["column_aliases"]
        for db_col, csv_aliases in aliases.items():
            if csv_column in csv_aliases and db_col in db_columns:
                return db_col

        # Strategy 3: Fuzzy matching
        best_match = process.extractOne(
            csv_column.lower(), [col.lower() for col in db_columns], scorer=fuzz.ratio
        )

        if best_match and best_match[1] >= 80:  # 80% similarity threshold
            # Find original case version
            for db_col in db_columns:
                if db_col.lower() == best_match[0]:
                    return db_col

        return None

    def map_csv_to_database(
        self, csv_file: Path, table_name: str
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Map CSV columns to database schema and return processed DataFrame"""

        console.print(
            f"\n🔄 Processing: [bold]{csv_file.name}[/bold] → [cyan]{table_name}[/cyan]"
        )

        # Load CSV
        try:
            df = pd.read_csv(csv_file)
            console.print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            return None, {"error": f"Failed to load CSV: {e}"}

        # Create mapping report
        mapping_report = {
            "csv_file": str(csv_file),
            "table_name": table_name,
            "original_columns": list(df.columns),
            "mapped_columns": {},
            "unmapped_columns": [],
            "missing_required_columns": [],
            "data_transformations": [],
        }

        # Map columns
        mapped_df = pd.DataFrame()
        mapping_table = Table(title=f"Column Mapping: {table_name}")
        mapping_table.add_column("CSV Column", style="green")
        mapping_table.add_column("Database Column", style="cyan")
        mapping_table.add_column("Status", style="yellow")
        mapping_table.add_column("Match Method", style="magenta")

        for csv_col in df.columns:
            db_col = self.find_best_column_match(csv_col, table_name)

            if db_col:
                mapped_df[db_col] = df[csv_col]
                mapping_report["mapped_columns"][csv_col] = db_col

                # Determine match method
                normalized = self.normalize_column_name(csv_col)
                if normalized == db_col:
                    method = "Normalized"
                elif any(
                    csv_col in aliases
                    for aliases in self.column_mapping_rules["column_aliases"].values()
                ):
                    method = "Alias"
                else:
                    method = "Fuzzy"

                mapping_table.add_row(csv_col, db_col, "✅ Mapped", method)
            else:
                mapping_report["unmapped_columns"].append(csv_col)
                mapping_table.add_row(csv_col, "—", "❌ No Match", "—")

        # Check for missing required columns
        if table_name in self.table_schemas:
            required_cols = [
                col
                for col, info in self.table_schemas[table_name].items()
                if not info["nullable"] and info["default"] is None
            ]

            for req_col in required_cols:
                if req_col not in mapped_df.columns:
                    mapping_report["missing_required_columns"].append(req_col)

        console.print(mapping_table)

        # Data type transformations and cleaning
        mapped_df = self.clean_and_transform_data(mapped_df, table_name, mapping_report)

        return mapped_df, mapping_report

    def clean_and_transform_data(
        self, df: pd.DataFrame, table_name: str, report: Dict
    ) -> pd.DataFrame:
        """Clean and transform data based on database schema"""

        if table_name not in self.table_schemas:
            return df

        schema = self.table_schemas[table_name]

        for col_name, col_info in schema.items():
            if col_name not in df.columns:
                continue

            col_type = col_info["type"]

            try:
                if col_type in ["integer", "bigint"]:
                    # Convert to integer, handling NaN
                    df[col_name] = pd.to_numeric(df[col_name], errors="coerce")
                    df[col_name] = df[col_name].fillna(0).astype("Int64")

                elif col_type in ["numeric", "decimal", "real", "double precision"]:
                    # Convert to float
                    df[col_name] = pd.to_numeric(df[col_name], errors="coerce")

                elif col_type in ["character varying", "text", "varchar"]:
                    # Clean string data
                    df[col_name] = df[col_name].astype(str)
                    df[col_name] = df[col_name].str.strip()
                    df[col_name] = df[col_name].replace(["nan", "None", ""], None)

                elif col_type == "date":
                    # Convert to date
                    df[col_name] = pd.to_datetime(df[col_name], errors="coerce").dt.date

                elif col_type == "time without time zone":
                    # Convert to time
                    df[col_name] = pd.to_datetime(df[col_name], errors="coerce").dt.time

                report["data_transformations"].append(
                    {"column": col_name, "type": col_type, "transformation": "success"}
                )

            except Exception as e:
                report["data_transformations"].append(
                    {
                        "column": col_name,
                        "type": col_type,
                        "transformation": f"failed: {e}",
                    }
                )

        return df

    def save_mapping_report(self, report: Dict[str, Any], output_dir: Path):
        """Save detailed mapping report"""
        output_dir.mkdir(exist_ok=True)

        report_file = output_dir / f"mapping_report_{report['table_name']}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        console.print(f"📄 Mapping report saved: {report_file}")


def main():
    """Test the intelligent column mapper"""

    # Database configuration
    db_config = {
        "host": "postgres",
        "port": 5432,
        "database": "cards_horse_racing_db",
        "user": "horse_racing",
        "password": "secure_password_123",
    }

    # Initialize mapper
    mapper = IntelligentColumnMapper(db_config)

    # Test files
    test_files = [
        (Path("/app/data/daily_downloads/mapped_races.csv"), "races"),
        (Path("/app/data/daily_downloads/mapped_horses.csv"), "horses"),
        (Path("/app/data/daily_downloads/mapped_jockeys_stats.csv"), "jockeys_stats"),
        (Path("/app/data/daily_downloads/mapped_trainers_stats.csv"), "trainers_stats"),
        (
            Path("/app/data/daily_downloads/mapped_racecard_details.csv"),
            "racecard_details",
        ),
    ]

    output_dir = Path("/app/data/daily_downloads/processed")
    reports_dir = Path("/app/data/daily_downloads/mapping_reports")

    for csv_file, table_name in test_files:
        if csv_file.exists():
            mapped_df, report = mapper.map_csv_to_database(csv_file, table_name)

            if mapped_df is not None:
                # Save processed CSV
                output_file = output_dir / f"processed_{table_name}.csv"
                output_file.parent.mkdir(exist_ok=True)
                mapped_df.to_csv(output_file, index=False)
                console.print(f"💾 Saved processed file: {output_file}")

                # Save mapping report
                mapper.save_mapping_report(report, reports_dir)
            else:
                console.print(f"[red]❌ Failed to process {csv_file}[/red]")


if __name__ == "__main__":
    main()
