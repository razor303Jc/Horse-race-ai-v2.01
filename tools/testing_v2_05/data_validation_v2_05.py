#!/usr/bin/env python3
"""
Data Validation System v2.05 - Horse Racing AI Testing & Simulation Strategy
Comprehensive data validation, quality checks, and integrity testing
for PostgreSQL entity tables and CSV data

Features:
- CSV data validation and quality assessment
- PostgreSQL schema validation
- Data type and constraint validation
- Referential integrity checking
- Performance validation metrics
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
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
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation strictness levels"""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


@dataclass
class ValidationResult:
    """Result of data validation operation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class DataQualityReport:
    """Comprehensive data quality assessment"""
    file_path: str
    total_rows: int
    total_columns: int
    null_percentage: float
    duplicate_rows: int
    data_types: Dict[str, str]
    column_quality: Dict[str, Dict[str, Any]]
    validation_results: List[ValidationResult]
    performance_metrics: Dict[str, float]


class DataValidationV205:
    """Enhanced data validation system for Testing & Simulation Strategy"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STRICT):
        """Initialize validation system"""
        self.validation_level = validation_level
        self.validation_history = []
        
        # Entity table specifications
        self.entity_specs = {
            "horses": {
                "required_columns": ["Horse_ID", "Name"],
                "unique_columns": ["Horse_ID"],
                "nullable_columns": ["country", "colour", "sex", "owner"],
                "numeric_columns": ["Horse_ID", "Age"],
                "text_columns": ["Name", "Country", "trainer", "owner"]
            },
            "jockeys": {
                "required_columns": ["jockey_ID", "jockey"],
                "unique_columns": ["jockey_ID"],
                "nullable_columns": ["allowance_claimed"],
                "numeric_columns": ["jockey_ID", "races", "wins", "placed"],
                "percentage_columns": ["win_rate", "place_rate"]
            },
            "trainers": {
                "required_columns": ["trainer_ID", "trainer"],
                "unique_columns": ["trainer_ID"],
                "nullable_columns": [],
                "numeric_columns": ["trainer_ID", "runners", "wins", "placed"],
                "percentage_columns": ["win_rate", "place_rate"]
            }
        }
        
        logger.info(f"🔍 Data Validation v2.05 initialized")
        logger.info(f"📊 Validation level: {validation_level.value}")
    
    def validate_csv_file(self, csv_file: str, 
                         entity_type: Optional[str] = None) -> ValidationResult:
        """Validate CSV file structure and data quality"""
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            result = ValidationResult(is_valid=True)
            
            # Basic file validation
            if df.empty:
                result.is_valid = False
                result.errors.append("CSV file is empty")
                return result
            
            # Entity-specific validation
            if entity_type and entity_type in self.entity_specs:
                entity_result = self._validate_entity_data(df, entity_type)
                result.errors.extend(entity_result.errors)
                result.warnings.extend(entity_result.warnings)
                if not entity_result.is_valid:
                    result.is_valid = False
            
            # General data quality checks
            quality_result = self._validate_data_quality(df)
            result.warnings.extend(quality_result.warnings)
            result.metrics.update(quality_result.metrics)
            
            # Performance metrics
            result.metrics.update({
                "file_size_mb": os.path.getsize(csv_file) / (1024 * 1024),
                "processing_time": 0.0,  # To be updated by caller
                "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024)
            })
            
            logger.info(f"✅ CSV validation complete: {csv_file}")
            return result
            
        except Exception as e:
            logger.error(f"❌ CSV validation failed: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[f"CSV validation error: {str(e)}"]
            )
    
    def _validate_entity_data(self, df: pd.DataFrame, 
                             entity_type: str) -> ValidationResult:
        """Validate data against entity specifications"""
        
        spec = self.entity_specs[entity_type]
        result = ValidationResult(is_valid=True)
        
        # Check required columns
        missing_required = set(spec["required_columns"]) - set(df.columns)
        if missing_required:
            result.is_valid = False
            result.errors.append(
                f"Missing required columns: {missing_required}"
            )
        
        # Check unique constraints
        for unique_col in spec["unique_columns"]:
            if unique_col in df.columns:
                duplicates = df[unique_col].duplicated().sum()
                if duplicates > 0:
                    if self.validation_level == ValidationLevel.STRICT:
                        result.is_valid = False
                        result.errors.append(
                            f"Duplicate values in {unique_col}: {duplicates}"
                        )
                    else:
                        result.warnings.append(
                            f"Duplicate values in {unique_col}: {duplicates}"
                        )
        
        # Check data types
        for num_col in spec.get("numeric_columns", []):
            if num_col in df.columns:
                non_numeric = pd.to_numeric(
                    df[num_col], errors='coerce'
                ).isna().sum()
                if non_numeric > 0:
                    result.warnings.append(
                        f"Non-numeric values in {num_col}: {non_numeric}"
                    )
        
        # Check percentage columns
        for pct_col in spec.get("percentage_columns", []):
            if pct_col in df.columns:
                invalid_pct = ((df[pct_col] < 0) | (df[pct_col] > 100)).sum()
                if invalid_pct > 0:
                    result.warnings.append(
                        f"Invalid percentage values in {pct_col}: {invalid_pct}"
                    )
        
        return result
    
    def _validate_data_quality(self, df: pd.DataFrame) -> ValidationResult:
        """Perform general data quality validation"""
        
        result = ValidationResult(is_valid=True)
        
        # Calculate quality metrics
        total_cells = df.size
        null_cells = df.isnull().sum().sum()
        null_percentage = (null_cells / total_cells) * 100
        
        # Null value thresholds
        if null_percentage > 50:
            result.warnings.append(
                f"High null percentage: {null_percentage:.1f}%"
            )
        elif null_percentage > 20:
            result.warnings.append(
                f"Moderate null percentage: {null_percentage:.1f}%"
            )
        
        # Duplicate rows
        duplicate_rows = df.duplicated().sum()
        if duplicate_rows > 0:
            result.warnings.append(f"Duplicate rows found: {duplicate_rows}")
        
        # Data type consistency
        mixed_types = []
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for mixed numeric/text in object columns
                try:
                    numeric_count = pd.to_numeric(
                        df[col], errors='coerce'
                    ).notna().sum()
                    if 0 < numeric_count < len(df[col]):
                        mixed_types.append(col)
                except:
                    pass
        
        if mixed_types:
            result.warnings.append(
                f"Mixed data types in columns: {mixed_types}"
            )
        
        # Store metrics
        result.metrics = {
            "null_percentage": null_percentage,
            "duplicate_rows": duplicate_rows,
            "mixed_type_columns": len(mixed_types),
            "total_rows": len(df),
            "total_columns": len(df.columns)
        }
        
        return result
    
    def validate_postgresql_schema(self, connection_config: Dict[str, str],
                                  entity_type: str) -> ValidationResult:
        """Validate PostgreSQL entity table schema"""
        
        try:
            conn = psycopg2.connect(**connection_config)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            result = ValidationResult(is_valid=True)
            table_name = f"{entity_type}_entity"
            
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s AND table_schema = 'public'
                )
            """, (table_name,))
            
            if not cursor.fetchone()['exists']:
                result.is_valid = False
                result.errors.append(f"Table {table_name} does not exist")
                return result
            
            # Check table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = cursor.fetchall()
            result.metrics["column_count"] = len(columns)
            result.metrics["columns"] = [col['column_name'] for col in columns]
            
            # Check for required columns
            required_cols = ["id", f"{entity_type}_id", f"{entity_type}_name"]
            existing_cols = set(col['column_name'] for col in columns)
            
            missing_required = set(required_cols) - existing_cols
            if missing_required:
                result.warnings.append(
                    f"Missing expected columns: {missing_required}"
                )
            
            # Check indexes
            cursor.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = %s AND schemaname = 'public'
            """, (table_name,))
            
            indexes = cursor.fetchall()
            result.metrics["index_count"] = len(indexes)
            
            conn.close()
            logger.info(f"✅ Schema validation complete: {table_name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Schema validation failed: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Schema validation error: {str(e)}"]
            )
    
    def generate_data_quality_report(self, csv_files: List[str]) -> DataQualityReport:
        """Generate comprehensive data quality report"""
        
        all_results = []
        total_rows = 0
        total_files = len(csv_files)
        
        start_time = datetime.now()
        
        for csv_file in csv_files:
            if not Path(csv_file).exists():
                continue
                
            # Determine entity type from filename
            entity_type = None
            for entity in self.entity_specs.keys():
                if entity in Path(csv_file).name.lower():
                    entity_type = entity
                    break
            
            # Validate file
            validation_result = self.validate_csv_file(csv_file, entity_type)
            all_results.append(validation_result)
            
            # Count rows
            try:
                df = pd.read_csv(csv_file)
                total_rows += len(df)
            except:
                pass
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Aggregate metrics
        aggregate_metrics = {
            "total_files_processed": total_files,
            "total_rows_processed": total_rows,
            "processing_time_seconds": processing_time,
            "validation_success_rate": sum(
                1 for r in all_results if r.is_valid
            ) / max(len(all_results), 1) * 100
        }
        
        # Create summary report
        report = DataQualityReport(
            file_path="multiple_files",
            total_rows=total_rows,
            total_columns=0,  # Would need aggregation logic
            null_percentage=0.0,  # Would need aggregation logic
            duplicate_rows=0,  # Would need aggregation logic
            data_types={},
            column_quality={},
            validation_results=all_results,
            performance_metrics=aggregate_metrics
        )
        
        logger.info(f"📊 Data quality report generated for {total_files} files")
        return report
    
    def validate_referential_integrity(self, connection_config: Dict[str, str],
                                     csv_files: Dict[str, str]) -> ValidationResult:
        """Validate referential integrity between entity tables"""
        
        try:
            conn = psycopg2.connect(**connection_config)
            cursor = conn.cursor()
            
            result = ValidationResult(is_valid=True)
            
            # Check horses -> trainers relationship
            if "horses" in csv_files and "trainers" in csv_files:
                horses_df = pd.read_csv(csv_files["horses"])
                trainers_df = pd.read_csv(csv_files["trainers"])
                
                if "trainer_ID" in horses_df.columns and "trainer_ID" in trainers_df.columns:
                    horse_trainers = set(horses_df["trainer_ID"].dropna())
                    available_trainers = set(trainers_df["trainer_ID"].dropna())
                    
                    missing_trainers = horse_trainers - available_trainers
                    if missing_trainers:
                        result.warnings.append(
                            f"Horses reference missing trainers: {len(missing_trainers)} IDs"
                        )
            
            # Check horses -> jockeys relationship (if in race data)
            # Additional integrity checks would go here
            
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"❌ Referential integrity check failed: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Integrity check error: {str(e)}"]
            )
    
    def export_validation_report(self, report: DataQualityReport, 
                               output_file: str) -> bool:
        """Export validation report to JSON file"""
        
        try:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_rows": report.total_rows,
                    "total_columns": report.total_columns,
                    "null_percentage": report.null_percentage,
                    "duplicate_rows": report.duplicate_rows
                },
                "performance_metrics": report.performance_metrics,
                "validation_results": [
                    {
                        "is_valid": result.is_valid,
                        "error_count": len(result.errors),
                        "warning_count": len(result.warnings),
                        "errors": result.errors,
                        "warnings": result.warnings,
                        "metrics": result.metrics
                    }
                    for result in report.validation_results
                ]
            }
            
            with open(output_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"📝 Validation report exported: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Report export failed: {str(e)}")
            return False


def main():
    """Main function for testing data validation functionality"""
    
    # Initialize validation system
    validator = DataValidationV205(ValidationLevel.STRICT)
    
    # Test data path
    test_data_path = "/home/jc/Documents/Horse-race-ai-v2.05/data/raw_csv_archives/2025-08-26"
    
    print("🔍 Data Validation v2.05 - Testing & Simulation Strategy")
    print("=" * 60)
    
    # Extract test files
    import zipfile
    cards_zip = f"{test_data_path}/raw_csv_cards_2025-08-26_105906.zip"
    results_zip = f"{test_data_path}/raw_csv_results_2025-08-26_105906.zip"
    
    temp_dir = Path("/tmp/validation_test")
    temp_dir.mkdir(exist_ok=True)
    
    test_files = []
    
    if Path(cards_zip).exists():
        with zipfile.ZipFile(cards_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            test_files.extend([
                str(temp_dir / "horses/horses.csv"),
                str(temp_dir / "races/races.csv")
            ])
    
    if Path(results_zip).exists():
        with zipfile.ZipFile(results_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            test_files.extend([
                str(temp_dir / "jockeys_stats/jockeys_stats.csv"),
                str(temp_dir / "trainers_stats/trainers_stats.csv")
            ])
    
    # Generate validation report
    if test_files:
        existing_files = [f for f in test_files if Path(f).exists()]
        print(f"📊 Testing {len(existing_files)} files...")
        
        report = validator.generate_data_quality_report(existing_files)
        
        # Export report
        report_file = "/tmp/data_validation_report_v2_05.json"
        validator.export_validation_report(report, report_file)
        
        print(f"✅ Validation report generated: {report_file}")
        print(f"📈 Performance: {report.performance_metrics}")
    
    print("\n🎯 Data Validation v2.05 testing complete!")


if __name__ == "__main__":
    main()
