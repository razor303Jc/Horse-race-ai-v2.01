#!/usr/bin/env python3
"""
Data Mapping System v2.05 - Horse Racing AI Testing & Simulation Strategy
Comprehensive column mappings, schema validation, and data type handling
for PostgreSQL entity tables

Features:
- PostgreSQL entity table mappings (horses, jockeys, trainers entities)
- CSV-to-Entity field mappings with validation
- Data type conversion and validation
- Schema compatibility checking
- Performance-optimized field mappings
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json
import re
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FieldType(Enum):
    """Supported PostgreSQL field types for entity tables"""

    SERIAL = "SERIAL"
    INTEGER = "INTEGER"
    BIGINT = "BIGINT"
    VARCHAR = "VARCHAR"
    TEXT = "TEXT"
    DECIMAL = "DECIMAL"
    BOOLEAN = "BOOLEAN"
    TIMESTAMP = "TIMESTAMP"
    DATE = "DATE"


@dataclass
class FieldMapping:
    """Represents a field mapping from CSV to PostgreSQL entity table"""

    csv_column: str
    entity_column: str
    field_type: FieldType
    max_length: Optional[int] = None
    nullable: bool = True
    default_value: Optional[Any] = None
    validation_rules: List[str] = field(default_factory=list)
    transformation_func: Optional[str] = None


@dataclass
class EntityTableSchema:
    """Represents the complete schema for an entity table"""

    table_name: str
    primary_key: str
    unique_constraints: List[str] = field(default_factory=list)
    indexes: List[str] = field(default_factory=list)
    field_mappings: Dict[str, FieldMapping] = field(default_factory=dict)


class DataMappingV205:
    """Enhanced data mapping system for PostgreSQL entity tables"""

    def __init__(self, connection_config: Optional[Dict] = None):
        """Initialize data mapping system"""
        self.connection_config = (
            connection_config or self._get_default_connection_config()
        )
        self.entity_schemas = self._initialize_entity_schemas()
        self.validation_errors = []

        logger.info("🗺️ Data Mapping v2.05 initialized")
        logger.info(f"📊 Entity schemas loaded: {list(self.entity_schemas.keys())}")

    def _get_default_connection_config(self) -> Dict[str, str]:
        """Get default PostgreSQL connection configuration"""
        return {
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": os.environ.get("DB_PORT", "5432"),
            "database": os.environ.get("DB_NAME", "results"),
            "user": os.environ.get("DB_USER", "horse_racing"),
            "password": os.environ.get("DB_PASSWORD", "secure_password_123"),
        }

    def _initialize_entity_schemas(self) -> Dict[str, EntityTableSchema]:
        """Initialize entity table schemas with field mappings"""

        # Horses Entity Schema
        horses_schema = EntityTableSchema(
            table_name="horses_entity",
            primary_key="id",
            unique_constraints=["horse_id"],
            indexes=["horse_name", "trainer", "owner", "country"],
            field_mappings={
                "horse_id": FieldMapping(
                    "Horse_ID", "horse_id", FieldType.INTEGER, nullable=False
                ),
                "horse_name": FieldMapping(
                    "Name",
                    "horse_name",
                    FieldType.VARCHAR,
                    max_length=200,
                    nullable=False,
                ),
                "country": FieldMapping(
                    "Country", "country", FieldType.VARCHAR, max_length=3
                ),
                "age": FieldMapping(
                    "Age", "age", FieldType.INTEGER, validation_rules=["range:2,15"]
                ),
                "colour": FieldMapping(
                    "colour", "colour", FieldType.VARCHAR, max_length=50
                ),
                "sex": FieldMapping("sex", "sex", FieldType.VARCHAR, max_length=10),
                "owner": FieldMapping("owner", "owner", FieldType.TEXT),
                "trainer": FieldMapping(
                    "trainer", "trainer", FieldType.VARCHAR, max_length=200
                ),
                "sire": FieldMapping("sire", "sire", FieldType.VARCHAR, max_length=200),
                "dam": FieldMapping("dam", "dam", FieldType.VARCHAR, max_length=200),
                "dam_sire": FieldMapping(
                    "dam_sire", "dam_sire", FieldType.VARCHAR, max_length=200
                ),
            },
        )

        # Jockeys Entity Schema
        jockeys_schema = EntityTableSchema(
            table_name="jockeys_entity",
            primary_key="id",
            unique_constraints=["jockey_id"],
            indexes=["jockey_name", "win_percentage", "total_races"],
            field_mappings={
                "jockey_id": FieldMapping(
                    "jockey_ID", "jockey_id", FieldType.INTEGER, nullable=False
                ),
                "jockey_name": FieldMapping(
                    "jockey",
                    "jockey_name",
                    FieldType.VARCHAR,
                    max_length=200,
                    nullable=False,
                ),
                "allowance_claimed": FieldMapping(
                    "allowance_claimed",
                    "allowance_claimed",
                    FieldType.BOOLEAN,
                    default_value=False,
                ),
                "total_races": FieldMapping(
                    "races",
                    "total_races",
                    FieldType.INTEGER,
                    validation_rules=["min:0"],
                ),
                "total_wins": FieldMapping(
                    "wins", "total_wins", FieldType.INTEGER, validation_rules=["min:0"]
                ),
                "win_percentage": FieldMapping(
                    "win_rate",
                    "win_percentage",
                    FieldType.DECIMAL,
                    validation_rules=["range:0,100"],
                ),
                "total_placed": FieldMapping(
                    "placed",
                    "total_placed",
                    FieldType.INTEGER,
                    validation_rules=["min:0"],
                ),
                "place_percentage": FieldMapping(
                    "place_rate",
                    "place_percentage",
                    FieldType.DECIMAL,
                    validation_rules=["range:0,100"],
                ),
            },
        )

        # Trainers Entity Schema
        trainers_schema = EntityTableSchema(
            table_name="trainers_entity",
            primary_key="id",
            unique_constraints=["trainer_id"],
            indexes=[
                "trainer_name",
                "win_percentage",
                "flat_win_rate",
                "jumps_win_rate",
            ],
            field_mappings={
                "trainer_id": FieldMapping(
                    "trainer_ID", "trainer_id", FieldType.INTEGER, nullable=False
                ),
                "trainer_name": FieldMapping(
                    "trainer",
                    "trainer_name",
                    FieldType.VARCHAR,
                    max_length=200,
                    nullable=False,
                ),
                "total_runners": FieldMapping(
                    "runners",
                    "total_runners",
                    FieldType.INTEGER,
                    validation_rules=["min:0"],
                ),
                "total_wins": FieldMapping(
                    "wins", "total_wins", FieldType.INTEGER, validation_rules=["min:0"]
                ),
                "win_percentage": FieldMapping(
                    "win_rate",
                    "win_percentage",
                    FieldType.DECIMAL,
                    validation_rules=["range:0,100"],
                ),
                "total_placed": FieldMapping(
                    "placed",
                    "total_placed",
                    FieldType.INTEGER,
                    validation_rules=["min:0"],
                ),
                "place_percentage": FieldMapping(
                    "place_rate",
                    "place_percentage",
                    FieldType.DECIMAL,
                    validation_rules=["range:0,100"],
                ),
                "flat_runners": FieldMapping(
                    "flat_runners",
                    "flat_runners",
                    FieldType.INTEGER,
                    validation_rules=["min:0"],
                ),
                "flat_wins": FieldMapping(
                    "flat_wins",
                    "flat_wins",
                    FieldType.INTEGER,
                    validation_rules=["min:0"],
                ),
                "flat_win_rate": FieldMapping(
                    "flat_win_rate",
                    "flat_win_rate",
                    FieldType.DECIMAL,
                    validation_rules=["range:0,100"],
                ),
                "jumps_runners": FieldMapping(
                    "jumps_runners",
                    "jumps_runners",
                    FieldType.INTEGER,
                    validation_rules=["min:0"],
                ),
                "jumps_wins": FieldMapping(
                    "jumps_wins",
                    "jumps_wins",
                    FieldType.INTEGER,
                    validation_rules=["min:0"],
                ),
                "jumps_win_rate": FieldMapping(
                    "jumps_win_rate",
                    "jumps_win_rate",
                    FieldType.DECIMAL,
                    validation_rules=["range:0,100"],
                ),
            },
        )

        return {
            "horses": horses_schema,
            "jockeys": jockeys_schema,
            "trainers": trainers_schema,
        }

    def get_entity_mapping(self, entity_type: str) -> Optional[EntityTableSchema]:
        """Get entity table schema and mappings"""
        return self.entity_schemas.get(entity_type)

    def validate_csv_columns(
        self, csv_file: str, entity_type: str
    ) -> Tuple[bool, List[str]]:
        """Validate CSV file has required columns for entity mapping"""
        try:
            df = pd.read_csv(csv_file, nrows=1)  # Read just header
            csv_columns = set(df.columns)

            schema = self.entity_schemas.get(entity_type)
            if not schema:
                return False, [f"Unknown entity type: {entity_type}"]

            required_columns = set()
            optional_columns = set()
            errors = []

            for field_mapping in schema.field_mappings.values():
                if not field_mapping.nullable and field_mapping.default_value is None:
                    required_columns.add(field_mapping.csv_column)
                else:
                    optional_columns.add(field_mapping.csv_column)

            # Check required columns
            missing_required = required_columns - csv_columns
            if missing_required:
                errors.append(f"Missing required columns: {missing_required}")

            # Check available optional columns
            available_optional = optional_columns & csv_columns
            logger.info(f"✅ Available optional columns: {available_optional}")

            return len(errors) == 0, errors

        except Exception as e:
            return False, [f"Error reading CSV file: {str(e)}"]

    def map_csv_to_entity(self, csv_row: pd.Series, entity_type: str) -> Dict[str, Any]:
        """Map a CSV row to entity table columns with data type conversion"""
        schema = self.entity_schemas.get(entity_type)
        if not schema:
            raise ValueError(f"Unknown entity type: {entity_type}")

        mapped_row = {}

        for entity_col, field_mapping in schema.field_mappings.items():
            csv_col = field_mapping.csv_column

            # Get value from CSV
            if csv_col in csv_row.index and pd.notna(csv_row[csv_col]):
                raw_value = csv_row[csv_col]

                # Convert data type
                try:
                    converted_value = self._convert_data_type(raw_value, field_mapping)

                    # Validate value
                    if self._validate_field_value(converted_value, field_mapping):
                        mapped_row[entity_col] = converted_value
                    else:
                        logger.warning(
                            f"Validation failed for {entity_col}: {converted_value}"
                        )
                        mapped_row[entity_col] = field_mapping.default_value

                except Exception as e:
                    logger.warning(f"Conversion failed for {entity_col}: {str(e)}")
                    mapped_row[entity_col] = field_mapping.default_value
            else:
                # Use default value
                mapped_row[entity_col] = field_mapping.default_value

        return mapped_row

    def _convert_data_type(self, value: Any, field_mapping: FieldMapping) -> Any:
        """Convert value to appropriate data type"""
        if pd.isna(value) or value is None:
            return None

        try:
            if field_mapping.field_type == FieldType.INTEGER:
                return int(float(value))  # Handle string floats like "123.0"

            elif field_mapping.field_type == FieldType.BIGINT:
                return int(float(value))

            elif field_mapping.field_type in [FieldType.VARCHAR, FieldType.TEXT]:
                str_value = str(value).strip()
                if field_mapping.max_length:
                    str_value = str_value[: field_mapping.max_length]
                return str_value

            elif field_mapping.field_type == FieldType.DECIMAL:
                return float(value)

            elif field_mapping.field_type == FieldType.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ["true", "1", "yes", "y"]
                return bool(value)

            elif field_mapping.field_type == FieldType.TIMESTAMP:
                if isinstance(value, str):
                    return pd.to_datetime(value)
                return value

            elif field_mapping.field_type == FieldType.DATE:
                if isinstance(value, str):
                    return pd.to_datetime(value).date()
                return value

            else:
                return value

        except Exception as e:
            logger.warning(
                f"Data type conversion failed: {value} -> {field_mapping.field_type}: {str(e)}"
            )
            return None

    def _validate_field_value(self, value: Any, field_mapping: FieldMapping) -> bool:
        """Validate field value against validation rules"""
        if value is None:
            return field_mapping.nullable

        for rule in field_mapping.validation_rules:
            if not self._apply_validation_rule(value, rule):
                return False

        return True

    def _apply_validation_rule(self, value: Any, rule: str) -> bool:
        """Apply a validation rule to a value"""
        try:
            if rule.startswith("range:"):
                min_val, max_val = map(float, rule[6:].split(","))
                return min_val <= float(value) <= max_val

            elif rule.startswith("min:"):
                min_val = float(rule[4:])
                return float(value) >= min_val

            elif rule.startswith("max:"):
                max_val = float(rule[4:])
                return float(value) <= max_val

            elif rule == "positive":
                return float(value) > 0

            elif rule == "non_negative":
                return float(value) >= 0

            else:
                logger.warning(f"Unknown validation rule: {rule}")
                return True

        except Exception as e:
            logger.warning(f"Validation rule error: {rule} for value {value}: {str(e)}")
            return False

    def generate_insert_sql(
        self, entity_type: str, mapped_data: List[Dict[str, Any]]
    ) -> Tuple[str, List[Tuple]]:
        """Generate PostgreSQL INSERT SQL for entity table"""
        schema = self.entity_schemas.get(entity_type)
        if not schema:
            raise ValueError(f"Unknown entity type: {entity_type}")

        if not mapped_data:
            return "", []

        # Get columns (excluding auto-increment primary key)
        columns = [col for col in mapped_data[0].keys() if col != "id"]

        # Generate SQL
        placeholders = ", ".join(["%s"] * len(columns))
        sql = f"""
            INSERT INTO {schema.table_name} ({", ".join(columns)})
            VALUES ({placeholders})
            ON CONFLICT ({schema.unique_constraints[0]}) DO UPDATE SET
            {", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col not in schema.unique_constraints])},
            updated_at = CURRENT_TIMESTAMP
        """

        # Generate data tuples
        data_tuples = []
        for row in mapped_data:
            tuple_data = tuple(row.get(col) for col in columns)
            data_tuples.append(tuple_data)

        return sql.strip(), data_tuples

    def validate_entity_data_integrity(
        self, entity_type: str, mapped_data: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str]]:
        """Validate data integrity for entity records"""
        schema = self.entity_schemas.get(entity_type)
        if not schema:
            return False, [f"Unknown entity type: {entity_type}"]

        errors = []

        # Check for duplicate unique constraint values
        unique_values = set()
        for i, row in enumerate(mapped_data):
            for constraint_col in schema.unique_constraints:
                value = row.get(constraint_col)
                if value is not None:
                    if value in unique_values:
                        errors.append(
                            f"Duplicate {constraint_col} value at row {i}: {value}"
                        )
                    unique_values.add(value)

        # Check required fields
        for i, row in enumerate(mapped_data):
            for col, field_mapping in schema.field_mappings.items():
                if not field_mapping.nullable and col in row and row[col] is None:
                    errors.append(f"Required field {col} is null at row {i}")

        return len(errors) == 0, errors

    def get_entity_statistics(self, csv_file: str, entity_type: str) -> Dict[str, Any]:
        """Get statistics about CSV data for entity mapping"""
        try:
            df = pd.read_csv(csv_file)
            schema = self.entity_schemas.get(entity_type)

            stats = {
                "total_rows": len(df),
                "entity_type": entity_type,
                "table_name": schema.table_name if schema else "unknown",
                "column_stats": {},
                "data_quality": {},
            }

            if schema:
                for entity_col, field_mapping in schema.field_mappings.items():
                    csv_col = field_mapping.csv_column

                    if csv_col in df.columns:
                        col_data = df[csv_col]
                        stats["column_stats"][entity_col] = {
                            "csv_column": csv_col,
                            "total_values": len(col_data),
                            "non_null_values": col_data.notna().sum(),
                            "null_percentage": (col_data.isna().sum() / len(col_data))
                            * 100,
                            "unique_values": col_data.nunique(),
                            "data_type": str(col_data.dtype),
                        }

                        # Additional stats for numeric columns
                        if pd.api.types.is_numeric_dtype(col_data):
                            stats["column_stats"][entity_col].update(
                                {
                                    "min_value": col_data.min(),
                                    "max_value": col_data.max(),
                                    "mean_value": col_data.mean(),
                                }
                            )

            return stats

        except Exception as e:
            logger.error(f"Error generating entity statistics: {str(e)}")
            return {"error": str(e)}


def main():
    """Main function for testing data mapping functionality"""

    # Initialize data mapping system
    mapper = DataMappingV205()

    # Test with sample data path (adjust as needed)
    test_data_path = (
        "/home/jc/Documents/Horse-race-ai-v2.05/data/raw_csv_archives/2025-08-26"
    )

    print("🗺️ Data Mapping v2.05 - Entity Table Testing")
    print("=" * 60)

    # Test horses mapping
    horses_file = f"{test_data_path}/horses.csv"
    if Path(horses_file).exists():
        print(f"\n📊 Testing horses entity mapping...")
        valid, errors = mapper.validate_csv_columns(horses_file, "horses")

        if valid:
            print("✅ Horses CSV validation passed")
            stats = mapper.get_entity_statistics(horses_file, "horses")
            print(f"📈 Horses statistics: {stats['total_rows']} rows")
        else:
            print(f"❌ Horses CSV validation failed: {errors}")

    # Test jockeys mapping
    jockeys_file = f"{test_data_path}/jockeys_stats.csv"
    if Path(jockeys_file).exists():
        print(f"\n🏇 Testing jockeys entity mapping...")
        valid, errors = mapper.validate_csv_columns(jockeys_file, "jockeys")

        if valid:
            print("✅ Jockeys CSV validation passed")
            stats = mapper.get_entity_statistics(jockeys_file, "jockeys")
            print(f"📈 Jockeys statistics: {stats['total_rows']} rows")
        else:
            print(f"❌ Jockeys CSV validation failed: {errors}")

    print("\n🎯 Data Mapping v2.05 testing complete!")


if __name__ == "__main__":
    main()
