#!/usr/bin/env python3
"""
Upload System v2.05 - Horse Racing AI Testing & Simulation Strategy
Advanced upload system for PostgreSQL entity tables with performance
monitoring, error recovery, and comprehensive data validation

Features:
- High-performance batch uploads to PostgreSQL
- Entity table population with data validation
- Upload progress monitoring and statistics
- Error recovery and retry mechanisms
- Memory-efficient processing for large datasets
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class UploadResult:
    """Result of upload operation"""
    success: bool
    records_uploaded: int = 0
    records_failed: int = 0
    upload_time_seconds: float = 0.0
    error_message: Optional[str] = None
    performance_metrics: Dict[str, float] = None


@dataclass
class UploadConfig:
    """Configuration for upload operations"""
    batch_size: int = 1000
    max_workers: int = 4
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    validate_before_upload: bool = True
    upsert_on_conflict: bool = True
    enable_performance_monitoring: bool = True


class UploadSystemV205:
    """Advanced upload system for PostgreSQL entity tables"""
    
    def __init__(self, connection_config: Optional[Dict[str, str]] = None,
                 upload_config: Optional[UploadConfig] = None):
        """Initialize upload system"""
        self.connection_config = connection_config or self._get_default_config()
        self.config = upload_config or UploadConfig()
        self.upload_history = []
        
        # PostgreSQL connection pool
        self.connection_pool = []
        
        logger.info("📤 Upload System v2.05 initialized")
        logger.info(f"🔧 Batch size: {self.config.batch_size}")
        logger.info(f"🔧 Max workers: {self.config.max_workers}")
    
    def _get_default_config(self) -> Dict[str, str]:
        """Get default PostgreSQL connection configuration"""
        return {
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": os.environ.get("DB_PORT", "5432"),
            "database": os.environ.get("DB_NAME", "results"),
            "user": os.environ.get("DB_USER", "horse_racing"),
            "password": os.environ.get("DB_PASSWORD", "secure_password_123")
        }
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_config)
            conn.autocommit = False
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def upload_entity_data(self, csv_file: str, entity_type: str) -> UploadResult:
        """Upload entity data from CSV file to PostgreSQL table"""
        
        start_time = time.time()
        
        try:
            # Validate inputs
            if not Path(csv_file).exists():
                return UploadResult(
                    success=False,
                    error_message=f"CSV file not found: {csv_file}"
                )
            
            # Get entity configuration
            entity_config = self._get_entity_config(entity_type)
            if not entity_config:
                return UploadResult(
                    success=False,
                    error_message=f"Unknown entity type: {entity_type}"
                )
            
            # Load and validate data
            df = pd.read_csv(csv_file)
            logger.info(f"📊 Loaded {len(df)} records from {csv_file}")
            
            # Transform data for entity table
            transformed_data = self._transform_data(df, entity_config)
            
            # Validate data if required
            if self.config.validate_before_upload:
                validation_errors = self._validate_data(
                    transformed_data, entity_config
                )
                if validation_errors:
                    return UploadResult(
                        success=False,
                        error_message=f"Validation errors: {validation_errors}"
                    )
            
            # Upload data in batches
            total_uploaded = 0
            total_failed = 0
            
            for batch in self._create_batches(
                transformed_data, self.config.batch_size
            ):
                batch_result = self._upload_batch(batch, entity_config)
                total_uploaded += batch_result.records_uploaded
                total_failed += batch_result.records_failed
            
            upload_time = time.time() - start_time
            
            # Create result
            result = UploadResult(
                success=total_failed == 0,
                records_uploaded=total_uploaded,
                records_failed=total_failed,
                upload_time_seconds=upload_time,
                performance_metrics={
                    "records_per_second": total_uploaded / upload_time if upload_time > 0 else 0,
                    "average_batch_time": upload_time / max(1, len(transformed_data) // self.config.batch_size),
                    "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024)
                }
            )
            
            # Record upload history
            self.upload_history.append({
                "timestamp": datetime.now().isoformat(),
                "entity_type": entity_type,
                "csv_file": csv_file,
                "result": result
            })
            
            logger.info(f"✅ Upload completed: {total_uploaded} uploaded, {total_failed} failed")
            return result
            
        except Exception as e:
            upload_time = time.time() - start_time
            logger.error(f"❌ Upload failed: {str(e)}")
            return UploadResult(
                success=False,
                upload_time_seconds=upload_time,
                error_message=str(e)
            )
    
    def _get_entity_config(self, entity_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration for entity type"""
        
        configs = {
            "horses": {
                "table_name": "horses_entity",
                "unique_column": "horse_id",
                "required_columns": ["horse_id", "horse_name"],
                "column_mapping": {
                    "horse_id": {"csv_col": "Horse_ID", "type": "int"},
                    "horse_name": {"csv_col": "Name", "type": "str"},
                    "country": {"csv_col": "Country", "type": "str"},
                    "age": {"csv_col": "Age", "type": "int"},
                    "colour": {"csv_col": "colour", "type": "str"},
                    "sex": {"csv_col": "sex", "type": "str"},
                    "owner": {"csv_col": "owner", "type": "str"},
                    "trainer": {"csv_col": "trainer", "type": "str"},
                    "sire": {"csv_col": "sire", "type": "str"},
                    "dam": {"csv_col": "dam", "type": "str"},
                    "dam_sire": {"csv_col": "dam_sire", "type": "str"}
                }
            },
            "jockeys": {
                "table_name": "jockeys_entity",
                "unique_column": "jockey_id",
                "required_columns": ["jockey_id", "jockey_name"],
                "column_mapping": {
                    "jockey_id": {"csv_col": "jockey_ID", "type": "int"},
                    "jockey_name": {"csv_col": "jockey", "type": "str"},
                    "allowance_claimed": {"csv_col": "allowance_claimed", "type": "bool"},
                    "total_races": {"csv_col": "races", "type": "int"},
                    "total_wins": {"csv_col": "wins", "type": "int"},
                    "win_percentage": {"csv_col": "win_rate", "type": "float"},
                    "total_placed": {"csv_col": "placed", "type": "int"},
                    "place_percentage": {"csv_col": "place_rate", "type": "float"}
                }
            },
            "trainers": {
                "table_name": "trainers_entity",
                "unique_column": "trainer_id",
                "required_columns": ["trainer_id", "trainer_name"],
                "column_mapping": {
                    "trainer_id": {"csv_col": "trainer_ID", "type": "int"},
                    "trainer_name": {"csv_col": "trainer", "type": "str"},
                    "total_runners": {"csv_col": "runners", "type": "int"},
                    "total_wins": {"csv_col": "wins", "type": "int"},
                    "win_percentage": {"csv_col": "win_rate", "type": "float"},
                    "total_placed": {"csv_col": "placed", "type": "int"},
                    "place_percentage": {"csv_col": "place_rate", "type": "float"},
                    "flat_runners": {"csv_col": "flat_runners", "type": "int"},
                    "flat_wins": {"csv_col": "flat_wins", "type": "int"},
                    "flat_win_rate": {"csv_col": "flat_win_rate", "type": "float"},
                    "jumps_runners": {"csv_col": "jumps_runners", "type": "int"},
                    "jumps_wins": {"csv_col": "jumps_wins", "type": "int"},
                    "jumps_win_rate": {"csv_col": "jumps_win_rate", "type": "float"}
                }
            }
        }
        
        return configs.get(entity_type)
    
    def _transform_data(self, df: pd.DataFrame, 
                       entity_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform CSV data to entity table format"""
        
        transformed_records = []
        column_mapping = entity_config["column_mapping"]
        
        for _, row in df.iterrows():
            record = {}
            
            # Map CSV columns to entity columns
            for entity_col, mapping_info in column_mapping.items():
                csv_col = mapping_info["csv_col"]
                data_type = mapping_info["type"]
                
                if csv_col in df.columns:
                    value = row[csv_col]
                    
                    # Convert data type
                    converted_value = self._convert_value(value, data_type)
                    record[entity_col] = converted_value
                else:
                    record[entity_col] = None
            
            # Add metadata
            record["created_at"] = datetime.now()
            record["updated_at"] = datetime.now()
            record["is_active"] = True
            
            transformed_records.append(record)
        
        return transformed_records
    
    def _convert_value(self, value: Any, data_type: str) -> Any:
        """Convert value to specified data type"""
        
        if pd.isna(value) or value is None:
            return None
        
        try:
            if data_type == "int":
                return int(float(value))
            elif data_type == "float":
                return float(value)
            elif data_type == "bool":
                if isinstance(value, str):
                    return value.lower() in ['true', '1', 'yes', 'y']
                return bool(value)
            elif data_type == "str":
                return str(value).strip()[:255]  # Limit length
            else:
                return str(value)
        except (ValueError, TypeError):
            return None
    
    def _validate_data(self, data: List[Dict[str, Any]], 
                      entity_config: Dict[str, Any]) -> List[str]:
        """Validate transformed data"""
        
        errors = []
        required_columns = entity_config["required_columns"]
        unique_column = entity_config["unique_column"]
        
        # Check required fields
        for i, record in enumerate(data):
            for req_col in required_columns:
                if record.get(req_col) is None:
                    errors.append(f"Row {i}: Missing required field {req_col}")
        
        # Check unique constraints
        unique_values = set()
        for i, record in enumerate(data):
            value = record.get(unique_column)
            if value is not None:
                if value in unique_values:
                    errors.append(f"Row {i}: Duplicate {unique_column} value: {value}")
                unique_values.add(value)
        
        return errors
    
    def _create_batches(self, data: List[Dict[str, Any]], 
                       batch_size: int) -> List[List[Dict[str, Any]]]:
        """Create batches from data list"""
        
        batches = []
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batches.append(batch)
        
        return batches
    
    def _upload_batch(self, batch: List[Dict[str, Any]], 
                     entity_config: Dict[str, Any]) -> UploadResult:
        """Upload a single batch to database"""
        
        if not batch:
            return UploadResult(success=True, records_uploaded=0)
        
        table_name = entity_config["table_name"]
        unique_column = entity_config["unique_column"]
        
        attempt = 0
        while attempt < self.config.retry_attempts:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Get column names (excluding auto-increment id)
                    columns = [col for col in batch[0].keys() if col != 'id']
                    
                    # Prepare data tuples
                    data_tuples = []
                    for record in batch:
                        tuple_data = tuple(record.get(col) for col in columns)
                        data_tuples.append(tuple_data)
                    
                    # Generate SQL
                    placeholders = ', '.join(['%s'] * len(columns))
                    
                    if self.config.upsert_on_conflict:
                        # UPSERT SQL
                        update_cols = [
                            col for col in columns 
                            if col not in [unique_column, 'created_at']
                        ]
                        
                        sql = f"""
                            INSERT INTO {table_name} ({', '.join(columns)})
                            VALUES ({placeholders})
                            ON CONFLICT ({unique_column}) DO UPDATE SET
                            {', '.join([f"{col} = EXCLUDED.{col}" for col in update_cols])},
                            updated_at = CURRENT_TIMESTAMP
                        """
                    else:
                        # Simple INSERT
                        sql = f"""
                            INSERT INTO {table_name} ({', '.join(columns)})
                            VALUES ({placeholders})
                        """
                    
                    # Execute batch insert
                    execute_values(
                        cursor, sql, data_tuples,
                        template=f"({placeholders})"
                    )
                    
                    conn.commit()
                    
                    return UploadResult(
                        success=True,
                        records_uploaded=len(batch)
                    )
                    
            except Exception as e:
                attempt += 1
                logger.warning(f"Batch upload attempt {attempt} failed: {str(e)}")
                
                if attempt < self.config.retry_attempts:
                    time.sleep(self.config.retry_delay_seconds)
                else:
                    return UploadResult(
                        success=False,
                        records_failed=len(batch),
                        error_message=str(e)
                    )
    
    def upload_complete_dataset(self, data_date: str) -> Dict[str, UploadResult]:
        """Upload complete dataset for a specific date"""
        
        from .data_processing_v2_05 import DataProcessorV205
        
        # Process data first
        processor = DataProcessorV205(
            connection_config=self.connection_config,
            batch_size=self.config.batch_size
        )
        
        processing_results = processor.process_complete_dataset(data_date)
        
        upload_results = {}
        
        # Upload each entity type
        for entity_type in ["horses", "jockeys", "trainers"]:
            if entity_type in processing_results:
                logger.info(f"📤 Starting upload for {entity_type}...")
                
                # Get processed data from temp files
                temp_file = f"/tmp/{entity_type}_{data_date}_processed.csv"
                
                if Path(temp_file).exists():
                    result = self.upload_entity_data(temp_file, entity_type)
                    upload_results[entity_type] = result
                else:
                    logger.warning(f"Processed file not found: {temp_file}")
        
        return upload_results
    
    def verify_upload_integrity(self, entity_type: str) -> Dict[str, Any]:
        """Verify upload integrity for entity table"""
        
        entity_config = self._get_entity_config(entity_type)
        if not entity_config:
            return {"error": f"Unknown entity type: {entity_type}"}
        
        table_name = entity_config["table_name"]
        unique_column = entity_config["unique_column"]
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                # Basic statistics
                cursor.execute(f"SELECT COUNT(*) as total FROM {table_name}")
                total_records = cursor.fetchone()['total']
                
                # Check for null unique values
                cursor.execute(f"""
                    SELECT COUNT(*) as null_uniques 
                    FROM {table_name} 
                    WHERE {unique_column} IS NULL
                """)
                null_uniques = cursor.fetchone()['null_uniques']
                
                # Check for duplicates
                cursor.execute(f"""
                    SELECT COUNT(*) as duplicates 
                    FROM (
                        SELECT {unique_column}, COUNT(*) 
                        FROM {table_name} 
                        GROUP BY {unique_column} 
                        HAVING COUNT(*) > 1
                    ) t
                """)
                duplicates = cursor.fetchone()['duplicates']
                
                # Check recent uploads
                cursor.execute(f"""
                    SELECT COUNT(*) as recent_uploads 
                    FROM {table_name} 
                    WHERE created_at >= NOW() - INTERVAL '1 hour'
                """)
                recent_uploads = cursor.fetchone()['recent_uploads']
                
                verification_result = {
                    "entity_type": entity_type,
                    "table_name": table_name,
                    "total_records": total_records,
                    "null_unique_values": null_uniques,
                    "duplicate_records": duplicates,
                    "recent_uploads": recent_uploads,
                    "integrity_status": "PASS" if (
                        null_uniques == 0 and duplicates == 0
                    ) else "FAIL"
                }
                
                return verification_result
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_upload_statistics(self) -> Dict[str, Any]:
        """Get comprehensive upload statistics"""
        
        if not self.upload_history:
            return {"message": "No upload history available"}
        
        total_uploads = len(self.upload_history)
        successful_uploads = sum(
            1 for entry in self.upload_history 
            if entry["result"].success
        )
        
        total_records = sum(
            entry["result"].records_uploaded 
            for entry in self.upload_history
        )
        
        total_time = sum(
            entry["result"].upload_time_seconds 
            for entry in self.upload_history
        )
        
        statistics = {
            "total_upload_operations": total_uploads,
            "successful_uploads": successful_uploads,
            "success_rate_percentage": (successful_uploads / total_uploads) * 100,
            "total_records_uploaded": total_records,
            "total_upload_time_seconds": total_time,
            "average_records_per_second": total_records / total_time if total_time > 0 else 0,
            "recent_uploads": self.upload_history[-5:] if self.upload_history else []
        }
        
        return statistics


def main():
    """Main function for testing upload system functionality"""
    
    # Initialize upload system
    uploader = UploadSystemV205(
        upload_config=UploadConfig(
            batch_size=500,
            max_workers=2,
            validate_before_upload=True
        )
    )
    
    print("📤 Upload System v2.05 - Testing & Simulation Strategy")
    print("=" * 60)
    
    # Test with 2025-08-26 dataset
    test_date = "2025-08-26"
    
    try:
        print(f"📊 Uploading complete dataset for {test_date}...")
        results = uploader.upload_complete_dataset(test_date)
        
        print(f"\n✅ Upload completed for {len(results)} entity types")
        
        # Verify upload integrity
        print("\n🔍 Verifying upload integrity...")
        for entity_type in results.keys():
            verification = uploader.verify_upload_integrity(entity_type)
            print(f"📋 {entity_type}: {verification}")
        
        # Get statistics
        stats = uploader.get_upload_statistics()
        print(f"\n📈 Upload Statistics:")
        print(f"🔢 Total records: {stats.get('total_records_uploaded', 0)}")
        print(f"⏱️ Success rate: {stats.get('success_rate_percentage', 0):.1f}%")
        
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
    
    print("\n🎯 Upload System v2.05 testing complete!")


if __name__ == "__main__":
    main()
