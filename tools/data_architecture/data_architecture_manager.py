#!/usr/bin/env python3
"""
Data Architecture Enhancement System - V2.03
============================================

Advanced data architecture improvements including:
- Data versioning and history tracking
- Data quality monitoring and alerts
- Automated backup and recovery system
- Data encryption for sensitive information
- Data retention policies and cleanup

This enhances the V2.03 data infrastructure with enterprise-grade capabilities.
"""

import asyncio
import json
import logging
import os
import shutil
import sqlite3
import subprocess
import hashlib
import gzip
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import psycopg2
import pandas as pd

logger = logging.getLogger(__name__)


class DataArchitectureManager:
    """
    Comprehensive data architecture management system.
    
    Provides enterprise-grade data management capabilities including:
    - Version control and history tracking
    - Quality monitoring and alerting
    - Automated backup and recovery
    - Data encryption and security
    - Retention policies and cleanup
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the data architecture manager."""
        self.config_path = config_path or "config/data_architecture_config.json"
        self.logger = logging.getLogger(__name__)
        
        self.config = self._load_config()
        
        # Initialize paths and directories
        self.data_root = Path(self.config.get('data_root', 'data'))
        self.backup_root = Path(self.config.get('backup_root', 'data/backups'))
        self.versioning_root = Path(self.config.get('versioning_root', 'data/versions'))
        self.monitoring_root = Path(self.config.get('monitoring_root', 'data/monitoring'))
        
        # Create necessary directories
        for path in [self.data_root, self.backup_root, self.versioning_root, self.monitoring_root]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self.encryption_enabled = self.config.get('encryption', {}).get('enabled', True)
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key) if self.encryption_enabled else None
        
        # Database connections
        self.db_config = self.config.get('database', {})
        
        # Monitoring settings
        self.monitoring_enabled = self.config.get('monitoring', {}).get('enabled', True)
        self.quality_thresholds = self.config.get('quality_thresholds', {})
        
        # Backup settings
        self.backup_schedule = self.config.get('backup', {}).get('schedule', 'daily')
        self.backup_retention_days = self.config.get('backup', {}).get('retention_days', 30)
        
        # Versioning settings
        self.versioning_enabled = self.config.get('versioning', {}).get('enabled', True)
        self.max_versions = self.config.get('versioning', {}).get('max_versions', 10)
        
        # Retention settings
        self.retention_policies = self.config.get('retention_policies', {})
        
        self.logger.info("Data Architecture Manager initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                self.logger.info(f"Loaded data architecture config from {self.config_path}")
                return config
            else:
                config = self._get_default_config()
                self._save_config(config)
                return config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration."""
        return {
            "data_root": "data",
            "backup_root": "data/backups",
            "versioning_root": "data/versions",
            "monitoring_root": "data/monitoring",
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "horse_racing_db",
                "user": "horse_racing",
                "password": "secure_password_123"
            },
            "encryption": {
                "enabled": True,
                "key_file": "data/.encryption_key",
                "sensitive_patterns": ["password", "api_key", "token", "secret"]
            },
            "backup": {
                "enabled": True,
                "schedule": "daily",
                "retention_days": 30,
                "compression": True,
                "include_database": True,
                "include_files": True
            },
            "versioning": {
                "enabled": True,
                "max_versions": 10,
                "track_changes": True,
                "version_metadata": True
            },
            "monitoring": {
                "enabled": True,
                "check_interval_minutes": 60,
                "alert_thresholds": {
                    "data_quality_score": 0.8,
                    "missing_data_percentage": 0.05,
                    "duplicate_records": 100,
                    "storage_usage_percentage": 0.85
                }
            },
            "quality_thresholds": {
                "completeness": 0.95,
                "accuracy": 0.98,
                "consistency": 0.90,
                "timeliness": 0.85
            },
            "retention_policies": {
                "raw_data": {"days": 365, "action": "archive"},
                "processed_data": {"days": 180, "action": "compress"},
                "logs": {"days": 90, "action": "delete"},
                "temp_files": {"days": 7, "action": "delete"},
                "backups": {"days": 30, "action": "delete"}
            }
        }
    
    def _save_config(self, config: Dict) -> None:
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info(f"Saved data architecture config to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get existing encryption key or create new one."""
        try:
            key_file = self.config.get('encryption', {}).get('key_file', 'data/.encryption_key')
            
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    key = f.read()
                self.logger.info("Loaded existing encryption key")
                return key
            else:
                # Generate new key
                key = Fernet.generate_key()
                
                # Save key securely
                os.makedirs(os.path.dirname(key_file), exist_ok=True)
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                # Set restrictive permissions
                os.chmod(key_file, 0o600)
                
                self.logger.info("Generated new encryption key")
                return key
                
        except Exception as e:
            self.logger.error(f"Error with encryption key: {e}")
            return Fernet.generate_key()  # Fallback to new key
    
    async def run_data_architecture_improvements(self) -> Dict[str, Any]:
        """
        Run comprehensive data architecture improvements.
        
        Returns:
            Results of all data architecture operations
        """
        start_time = datetime.now()
        
        try:
            self.logger.info("Starting Data Architecture Improvements")
            
            results = {
                'timestamp': start_time.isoformat(),
                'operations_completed': [],
                'operations_failed': [],
                'monitoring_results': {},
                'backup_results': {},
                'versioning_results': {},
                'encryption_results': {},
                'cleanup_results': {},
                'quality_assessment': {}
            }
            
            # 1. Data Quality Monitoring and Assessment
            if self.monitoring_enabled:
                quality_results = await self._run_data_quality_monitoring()
                results['quality_assessment'] = quality_results
                results['operations_completed'].append('data_quality_monitoring')
            
            # 2. Data Versioning and History
            if self.versioning_enabled:
                versioning_results = await self._run_data_versioning()
                results['versioning_results'] = versioning_results
                results['operations_completed'].append('data_versioning')
            
            # 3. Automated Backup System
            backup_results = await self._run_automated_backup()
            results['backup_results'] = backup_results
            results['operations_completed'].append('automated_backup')
            
            # 4. Data Encryption
            if self.encryption_enabled:
                encryption_results = await self._run_data_encryption()
                results['encryption_results'] = encryption_results
                results['operations_completed'].append('data_encryption')
            
            # 5. Data Retention and Cleanup
            cleanup_results = await self._run_retention_cleanup()
            results['cleanup_results'] = cleanup_results
            results['operations_completed'].append('retention_cleanup')
            
            # 6. System Health Check
            health_results = await self._run_system_health_check()
            results['monitoring_results'] = health_results
            results['operations_completed'].append('system_health_check')
            
            # Calculate total processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            results['processing_time_seconds'] = processing_time
            
            self.logger.info(
                f"Data Architecture Improvements completed in {processing_time:.2f}s - "
                f"{len(results['operations_completed'])} operations successful"
            )
            
            return results
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Error in data architecture improvements: {e}")
            
            return {
                'timestamp': start_time.isoformat(),
                'error': str(e),
                'processing_time_seconds': processing_time,
                'operations_completed': results.get('operations_completed', []),
                'operations_failed': results.get('operations_failed', [])
            }
    
    async def _run_data_quality_monitoring(self) -> Dict[str, Any]:
        """Run comprehensive data quality monitoring."""
        try:
            self.logger.info("Running data quality monitoring")
            
            monitoring_results = {
                'timestamp': datetime.now().isoformat(),
                'database_health': {},
                'file_system_health': {},
                'quality_scores': {},
                'alerts_generated': [],
                'recommendations': []
            }
            
            # Database quality checks
            if self.db_config:
                db_health = await self._check_database_health()
                monitoring_results['database_health'] = db_health
                
                # Generate alerts if thresholds exceeded
                alerts = self._generate_quality_alerts(db_health)
                monitoring_results['alerts_generated'].extend(alerts)
            
            # File system quality checks
            fs_health = await self._check_filesystem_health()
            monitoring_results['file_system_health'] = fs_health
            
            # Calculate overall quality scores
            quality_scores = self._calculate_quality_scores(
                monitoring_results['database_health'],
                monitoring_results['file_system_health']
            )
            monitoring_results['quality_scores'] = quality_scores
            
            # Generate recommendations
            recommendations = self._generate_quality_recommendations(monitoring_results)
            monitoring_results['recommendations'] = recommendations
            
            # Save monitoring results
            await self._save_monitoring_results(monitoring_results)
            
            return monitoring_results
            
        except Exception as e:
            self.logger.error(f"Error in data quality monitoring: {e}")
            return {'error': str(e)}
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health and quality metrics."""
        try:
            health_metrics = {
                'connection_status': 'unknown',
                'table_stats': {},
                'data_quality_metrics': {},
                'performance_metrics': {}
            }
            
            # Test database connection
            try:
                conn = psycopg2.connect(**self.db_config)
                cursor = conn.cursor()
                
                health_metrics['connection_status'] = 'healthy'
                
                # Get table statistics
                cursor.execute("""
                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes,
                        n_live_tup as live_tuples,
                        n_dead_tup as dead_tuples
                    FROM pg_stat_user_tables
                    ORDER BY n_live_tup DESC;
                """)
                
                table_stats = {}
                for row in cursor.fetchall():
                    schema, table, inserts, updates, deletes, live, dead = row
                    table_stats[f"{schema}.{table}"] = {
                        'inserts': inserts,
                        'updates': updates,
                        'deletes': deletes,
                        'live_tuples': live,
                        'dead_tuples': dead,
                        'health_score': live / (live + dead) if (live + dead) > 0 else 1.0
                    }
                
                health_metrics['table_stats'] = table_stats
                
                # Data quality checks on key tables
                quality_metrics = {}
                
                # Check records table if exists
                try:
                    cursor.execute("SELECT COUNT(*) FROM records WHERE horse_name IS NULL OR horse_name = ''")
                    null_horses = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM records")
                    total_records = cursor.fetchone()[0]
                    
                    quality_metrics['horse_name_completeness'] = 1.0 - (null_horses / total_records) if total_records > 0 else 0
                    
                except Exception:
                    pass  # Table might not exist
                
                health_metrics['data_quality_metrics'] = quality_metrics
                
                cursor.close()
                conn.close()
                
            except Exception as e:
                health_metrics['connection_status'] = f'failed: {e}'
                self.logger.error(f"Database connection failed: {e}")
            
            return health_metrics
            
        except Exception as e:
            self.logger.error(f"Error checking database health: {e}")
            return {'error': str(e)}
    
    async def _check_filesystem_health(self) -> Dict[str, Any]:
        """Check file system health and metrics."""
        try:
            fs_health = {
                'disk_usage': {},
                'file_counts': {},
                'data_integrity': {},
                'storage_efficiency': {}
            }
            
            # Check disk usage
            for path in [self.data_root, self.backup_root, self.versioning_root]:
                if path.exists():
                    total, used, free = shutil.disk_usage(path)
                    fs_health['disk_usage'][str(path)] = {
                        'total_gb': round(total / (1024**3), 2),
                        'used_gb': round(used / (1024**3), 2),
                        'free_gb': round(free / (1024**3), 2),
                        'usage_percentage': round(used / total * 100, 2)
                    }
            
            # Count files in each directory
            for path in [self.data_root, self.backup_root, self.versioning_root]:
                if path.exists():
                    file_count = sum(1 for _ in path.rglob('*') if _.is_file())
                    fs_health['file_counts'][str(path)] = file_count
            
            # Check data integrity (sample file checksums)
            integrity_checks = await self._check_data_integrity()
            fs_health['data_integrity'] = integrity_checks
            
            return fs_health
            
        except Exception as e:
            self.logger.error(f"Error checking filesystem health: {e}")
            return {'error': str(e)}
    
    async def _check_data_integrity(self) -> Dict[str, Any]:
        """Check data integrity using checksums."""
        try:
            integrity_results = {
                'files_checked': 0,
                'files_corrupted': 0,
                'checksum_mismatches': [],
                'integrity_score': 1.0
            }
            
            checksum_file = self.monitoring_root / 'file_checksums.json'
            stored_checksums = {}
            
            # Load existing checksums
            if checksum_file.exists():
                try:
                    with open(checksum_file, 'r') as f:
                        stored_checksums = json.load(f)
                except Exception:
                    pass
            
            current_checksums = {}
            
            # Check key data files
            data_files = list(self.data_root.rglob('*.csv')) + list(self.data_root.rglob('*.json'))
            
            for file_path in data_files[:20]:  # Limit to first 20 files for performance
                if file_path.is_file():
                    try:
                        # Calculate current checksum
                        current_checksum = self._calculate_file_checksum(file_path)
                        current_checksums[str(file_path)] = current_checksum
                        
                        integrity_results['files_checked'] += 1
                        
                        # Compare with stored checksum
                        stored_checksum = stored_checksums.get(str(file_path))
                        if stored_checksum and stored_checksum != current_checksum:
                            integrity_results['files_corrupted'] += 1
                            integrity_results['checksum_mismatches'].append(str(file_path))
                        
                    except Exception as e:
                        self.logger.warning(f"Error checking file {file_path}: {e}")
            
            # Update stored checksums
            with open(checksum_file, 'w') as f:
                json.dump(current_checksums, f, indent=2)
            
            # Calculate integrity score
            if integrity_results['files_checked'] > 0:
                integrity_results['integrity_score'] = 1.0 - (
                    integrity_results['files_corrupted'] / integrity_results['files_checked']
                )
            
            return integrity_results
            
        except Exception as e:
            self.logger.error(f"Error checking data integrity: {e}")
            return {'error': str(e)}
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _generate_quality_alerts(self, health_data: Dict) -> List[Dict]:
        """Generate quality alerts based on health data."""
        alerts = []
        
        try:
            # Database health alerts
            if health_data.get('connection_status') != 'healthy':
                alerts.append({
                    'type': 'database_connection',
                    'severity': 'high',
                    'message': f"Database connection failed: {health_data.get('connection_status')}",
                    'timestamp': datetime.now().isoformat(),
                    'recommendation': 'Check database server status and connection parameters'
                })
            
            # Data quality alerts
            quality_metrics = health_data.get('data_quality_metrics', {})
            for metric, value in quality_metrics.items():
                threshold = self.quality_thresholds.get(metric.split('_')[-1], 0.9)
                if value < threshold:
                    alerts.append({
                        'type': 'data_quality',
                        'severity': 'medium',
                        'message': f"{metric} below threshold: {value:.2f} < {threshold}",
                        'timestamp': datetime.now().isoformat(),
                        'recommendation': f'Investigate and clean {metric} issues'
                    })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error generating quality alerts: {e}")
            return []
    
    def _calculate_quality_scores(self, db_health: Dict, fs_health: Dict) -> Dict[str, float]:
        """Calculate overall quality scores."""
        try:
            scores = {
                'database_health': 0.0,
                'filesystem_health': 0.0,
                'overall_health': 0.0
            }
            
            # Database health score
            if db_health.get('connection_status') == 'healthy':
                db_score = 0.5  # Base score for healthy connection
                
                # Add quality metrics
                quality_metrics = db_health.get('data_quality_metrics', {})
                if quality_metrics:
                    avg_quality = sum(quality_metrics.values()) / len(quality_metrics)
                    db_score += 0.5 * avg_quality
                else:
                    db_score += 0.3  # Partial score if no quality metrics
                
                scores['database_health'] = min(1.0, db_score)
            
            # Filesystem health score
            fs_score = 0.0
            
            # Disk usage component
            disk_usage = fs_health.get('disk_usage', {})
            if disk_usage:
                avg_usage = sum(d.get('usage_percentage', 0) for d in disk_usage.values()) / len(disk_usage)
                fs_score += 0.5 * (1.0 - min(avg_usage / 100, 1.0))  # Lower usage = higher score
            
            # Data integrity component
            integrity = fs_health.get('data_integrity', {})
            integrity_score = integrity.get('integrity_score', 1.0)
            fs_score += 0.5 * integrity_score
            
            scores['filesystem_health'] = fs_score
            
            # Overall health score
            scores['overall_health'] = (scores['database_health'] + scores['filesystem_health']) / 2
            
            return scores
            
        except Exception as e:
            self.logger.error(f"Error calculating quality scores: {e}")
            return {'error': str(e)}
    
    def _generate_quality_recommendations(self, monitoring_results: Dict) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        try:
            quality_scores = monitoring_results.get('quality_scores', {})
            
            # Database recommendations
            db_score = quality_scores.get('database_health', 0)
            if db_score < 0.8:
                recommendations.append("Consider database maintenance: VACUUM, ANALYZE, and index optimization")
            
            # Filesystem recommendations
            fs_score = quality_scores.get('filesystem_health', 0)
            if fs_score < 0.8:
                recommendations.append("Review disk usage and consider data archival or cleanup")
            
            # Specific recommendations based on alerts
            alerts = monitoring_results.get('alerts_generated', [])
            if len(alerts) > 5:
                recommendations.append("High number of alerts detected - review system configuration")
            
            # Data integrity recommendations
            integrity = monitoring_results.get('file_system_health', {}).get('data_integrity', {})
            if integrity.get('files_corrupted', 0) > 0:
                recommendations.append("Data corruption detected - run full integrity check and restore from backup")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def _save_monitoring_results(self, results: Dict) -> None:
        """Save monitoring results to file."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            results_file = self.monitoring_root / f'monitoring_results_{timestamp}.json'
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Also save as latest
            latest_file = self.monitoring_root / 'latest_monitoring_results.json'
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.logger.info(f"Saved monitoring results to {results_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving monitoring results: {e}")
    
    async def _run_data_versioning(self) -> Dict[str, Any]:
        """Run data versioning and history tracking."""
        try:
            self.logger.info("Running data versioning")
            
            versioning_results = {
                'timestamp': datetime.now().isoformat(),
                'files_versioned': 0,
                'databases_versioned': 0,
                'versions_created': [],
                'old_versions_cleaned': 0,
                'storage_used_mb': 0
            }
            
            # Version key data files
            csv_files = list(self.data_root.rglob('*.csv'))
            json_files = list(self.data_root.rglob('*.json'))
            data_files = csv_files + json_files
            
            for file_path in data_files:
                versioning_path = str(self.versioning_root)
                is_outside_versioning = not str(file_path).startswith(versioning_path)
                if file_path.is_file() and is_outside_versioning:
                    try:
                        version_info = await self._create_file_version(file_path)
                        if version_info:
                            versioning_results['files_versioned'] += 1
                            versioning_results['versions_created'].append(version_info)
                            storage_mb = version_info.get('size_mb', 0)
                            versioning_results['storage_used_mb'] += storage_mb
                    except Exception as e:
                        self.logger.warning(f"Error versioning file {file_path}: {e}")
            
            # Version database if configured
            if self.db_config:
                db_version_info = await self._create_database_version()
                if db_version_info:
                    versioning_results['databases_versioned'] += 1
                    versioning_results['versions_created'].append(db_version_info)
                    versioning_results['storage_used_mb'] += db_version_info.get('size_mb', 0)
            
            # Clean up old versions
            cleaned_count = await self._cleanup_old_versions()
            versioning_results['old_versions_cleaned'] = cleaned_count
            
            return versioning_results
            
        except Exception as e:
            self.logger.error(f"Error in data versioning: {e}")
            return {'error': str(e)}
    
    async def _create_file_version(self, file_path: Path) -> Optional[Dict]:
        """Create a version of a data file."""
        try:
            # Generate version info
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_hash = self._calculate_file_checksum(file_path)
            
            # Create version directory
            relative_path = file_path.relative_to(self.data_root)
            version_dir = self.versioning_root / relative_path.parent
            version_dir.mkdir(parents=True, exist_ok=True)
            
            # Create versioned filename
            version_filename = f"{file_path.stem}_{timestamp}_{file_hash[:8]}{file_path.suffix}"
            version_path = version_dir / version_filename
            
            # Check if this version already exists (same hash)
            existing_versions = list(version_dir.glob(f"{file_path.stem}_*{file_path.suffix}"))
            for existing in existing_versions:
                if file_hash[:8] in existing.name:
                    # Same content, skip versioning
                    return None
            
            # Copy file to version directory
            shutil.copy2(file_path, version_path)
            
            # Create metadata
            metadata = {
                'original_path': str(file_path),
                'version_path': str(version_path),
                'timestamp': timestamp,
                'file_hash': file_hash,
                'file_size': file_path.stat().st_size,
                'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2),
                'creation_time': datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                'modification_time': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
            # Save metadata
            metadata_path = version_path.with_suffix('.metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error creating file version for {file_path}: {e}")
            return None
    
    async def _create_database_version(self) -> Optional[Dict]:
        """Create a version of the database."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create database backup directory
            db_version_dir = self.versioning_root / 'database'
            db_version_dir.mkdir(parents=True, exist_ok=True)
            
            # Create database dump
            dump_filename = f"db_version_{timestamp}.sql"
            dump_path = db_version_dir / dump_filename
            
            # Use pg_dump to create database version
            dump_command = [
                'pg_dump',
                '-h', self.db_config.get('host', 'localhost'),
                '-p', str(self.db_config.get('port', 5432)),
                '-U', self.db_config.get('user', 'postgres'),
                '-d', self.db_config.get('database', 'horse_racing'),
                '-f', str(dump_path),
                '--verbose'
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config.get('password', '')
            
            result = subprocess.run(dump_command, capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                # Compress the dump
                compressed_path = dump_path.with_suffix('.sql.gz')
                with open(dump_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed version
                dump_path.unlink()
                
                # Create metadata
                metadata = {
                    'type': 'database_version',
                    'version_path': str(compressed_path),
                    'timestamp': timestamp,
                    'database': self.db_config.get('database'),
                    'host': self.db_config.get('host'),
                    'file_size': compressed_path.stat().st_size,
                    'size_mb': round(compressed_path.stat().st_size / (1024 * 1024), 2),
                    'dump_success': True
                }
                
                # Save metadata
                metadata_path = compressed_path.with_suffix('.metadata.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                return metadata
            else:
                self.logger.error(f"Database dump failed: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating database version: {e}")
            return None
    
    async def _cleanup_old_versions(self) -> int:
        """Clean up old versions beyond the retention limit."""
        try:
            cleaned_count = 0
            
            # Clean up file versions
            for version_dir in self.versioning_root.rglob('*'):
                if version_dir.is_dir() and version_dir != self.versioning_root:
                    # Get all version files in this directory
                    version_files = []
                    for file_path in version_dir.iterdir():
                        if file_path.is_file() and not file_path.name.endswith('.metadata.json'):
                            try:
                                # Extract timestamp from filename
                                parts = file_path.stem.split('_')
                                if len(parts) >= 2:
                                    timestamp_str = parts[-2]  # Assuming format: name_timestamp_hash
                                    file_time = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                                    version_files.append((file_path, file_time))
                            except Exception:
                                pass  # Skip files with unexpected format
                    
                    # Sort by timestamp (newest first)
                    version_files.sort(key=lambda x: x[1], reverse=True)
                    
                    # Remove old versions beyond max_versions
                    if len(version_files) > self.max_versions:
                        for file_path, _ in version_files[self.max_versions:]:
                            try:
                                file_path.unlink()
                                # Also remove metadata file
                                metadata_path = file_path.with_suffix('.metadata.json')
                                if metadata_path.exists():
                                    metadata_path.unlink()
                                cleaned_count += 1
                            except Exception as e:
                                self.logger.warning(f"Error removing old version {file_path}: {e}")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old versions: {e}")
            return 0
    
    async def _run_automated_backup(self) -> Dict[str, Any]:
        """Run automated backup system."""
        try:
            self.logger.info("Running automated backup")
            
            backup_results = {
                'timestamp': datetime.now().isoformat(),
                'backup_type': 'full',
                'files_backed_up': 0,
                'databases_backed_up': 0,
                'backup_size_mb': 0,
                'backup_path': '',
                'compression_ratio': 0.0,
                'backup_success': False
            }
            
            # Create backup directory with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = self.backup_root / f'backup_{timestamp}'
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_results['backup_path'] = str(backup_dir)
            
            # Backup data files
            if self.config.get('backup', {}).get('include_files', True):
                files_backup_result = await self._backup_data_files(backup_dir)
                backup_results['files_backed_up'] = files_backup_result.get('files_count', 0)
                backup_results['backup_size_mb'] += files_backup_result.get('size_mb', 0)
            
            # Backup database
            if self.config.get('backup', {}).get('include_database', True) and self.db_config:
                db_backup_result = await self._backup_database(backup_dir)
                if db_backup_result.get('success'):
                    backup_results['databases_backed_up'] = 1
                    backup_results['backup_size_mb'] += db_backup_result.get('size_mb', 0)
            
            # Create backup archive if compression enabled
            if self.config.get('backup', {}).get('compression', True):
                archive_result = await self._create_backup_archive(backup_dir)
                if archive_result.get('success'):
                    backup_results['compression_ratio'] = archive_result.get('compression_ratio', 0)
                    backup_results['backup_size_mb'] = archive_result.get('compressed_size_mb', 0)
            
            # Create backup manifest
            manifest = await self._create_backup_manifest(backup_dir, backup_results)
            
            # Clean up old backups
            cleaned_backups = await self._cleanup_old_backups()
            backup_results['old_backups_cleaned'] = cleaned_backups
            
            backup_results['backup_success'] = True
            
            return backup_results
            
        except Exception as e:
            self.logger.error(f"Error in automated backup: {e}")
            return {'error': str(e), 'backup_success': False}
    
    async def _backup_data_files(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup data files to backup directory."""
        try:
            files_backup_dir = backup_dir / 'data_files'
            files_backup_dir.mkdir(parents=True, exist_ok=True)
            
            files_count = 0
            total_size = 0
            
            # Copy important data files
            important_paths = [
                self.data_root / 'daily_downloads',
                self.data_root / 'preprocessed',
                self.data_root / 'monte_carlo_results',
                self.data_root / 'speed_analysis'
            ]
            
            for source_path in important_paths:
                if source_path.exists():
                    dest_path = files_backup_dir / source_path.name
                    
                    if source_path.is_dir():
                        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                        # Count files and size
                        for file_path in dest_path.rglob('*'):
                            if file_path.is_file():
                                files_count += 1
                                total_size += file_path.stat().st_size
                    else:
                        shutil.copy2(source_path, dest_path)
                        files_count += 1
                        total_size += dest_path.stat().st_size
            
            return {
                'files_count': files_count,
                'size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            self.logger.error(f"Error backing up data files: {e}")
            return {'files_count': 0, 'size_mb': 0}
    
    async def _backup_database(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup database to backup directory."""
        try:
            db_backup_dir = backup_dir / 'database'
            db_backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create database dump
            dump_filename = 'database_backup.sql'
            dump_path = db_backup_dir / dump_filename
            
            # Use pg_dump
            dump_command = [
                'pg_dump',
                '-h', self.db_config.get('host', 'localhost'),
                '-p', str(self.db_config.get('port', 5432)),
                '-U', self.db_config.get('user', 'postgres'),
                '-d', self.db_config.get('database', 'horse_racing'),
                '-f', str(dump_path),
                '--verbose'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config.get('password', '')
            
            result = subprocess.run(dump_command, capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                # Compress the dump
                compressed_path = dump_path.with_suffix('.sql.gz')
                with open(dump_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                dump_path.unlink()  # Remove uncompressed version
                
                return {
                    'success': True,
                    'size_mb': round(compressed_path.stat().st_size / (1024 * 1024), 2)
                }
            else:
                self.logger.error(f"Database backup failed: {result.stderr}")
                return {'success': False, 'size_mb': 0}
                
        except Exception as e:
            self.logger.error(f"Error backing up database: {e}")
            return {'success': False, 'size_mb': 0}
    
    async def _create_backup_archive(self, backup_dir: Path) -> Dict[str, Any]:
        """Create compressed archive of backup directory."""
        try:
            archive_path = backup_dir.with_suffix('.tar.gz')
            
            # Calculate original size
            original_size = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
            
            # Create tar.gz archive
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(backup_dir, arcname=backup_dir.name)
            
            # Calculate compressed size
            compressed_size = archive_path.stat().st_size
            
            # Remove original backup directory
            shutil.rmtree(backup_dir)
            
            compression_ratio = (original_size - compressed_size) / original_size if original_size > 0 else 0
            
            return {
                'success': True,
                'compressed_size_mb': round(compressed_size / (1024 * 1024), 2),
                'compression_ratio': round(compression_ratio, 3)
            }
            
        except Exception as e:
            self.logger.error(f"Error creating backup archive: {e}")
            return {'success': False}
    
    async def _create_backup_manifest(self, backup_dir: Path, backup_results: Dict) -> Dict:
        """Create backup manifest with metadata."""
        try:
            manifest = {
                'backup_timestamp': datetime.now().isoformat(),
                'backup_type': 'automated_full',
                'backup_results': backup_results,
                'system_info': {
                    'hostname': os.uname().nodename,
                    'python_version': os.sys.version,
                    'backup_tool_version': '1.0.0'
                },
                'verification': {
                    'checksum': '',
                    'file_count': 0
                }
            }
            
            # Calculate backup checksum and file count
            if backup_dir.exists():
                all_files = list(backup_dir.rglob('*'))
                manifest['verification']['file_count'] = len([f for f in all_files if f.is_file()])
                
                # Simple manifest checksum (sum of file sizes)
                total_size = sum(f.stat().st_size for f in all_files if f.is_file())
                manifest['verification']['checksum'] = str(total_size)
            
            # Save manifest
            manifest_path = backup_dir / 'backup_manifest.json'
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            return manifest
            
        except Exception as e:
            self.logger.error(f"Error creating backup manifest: {e}")
            return {}
    
    async def _cleanup_old_backups(self) -> int:
        """Clean up old backups beyond retention period."""
        try:
            cleaned_count = 0
            cutoff_date = datetime.now() - timedelta(days=self.backup_retention_days)
            
            # Find old backup files/directories
            for backup_item in self.backup_root.iterdir():
                try:
                    # Extract timestamp from backup name
                    if backup_item.name.startswith('backup_'):
                        timestamp_str = backup_item.name.replace('backup_', '').replace('.tar.gz', '')
                        backup_time = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        
                        if backup_time < cutoff_date:
                            if backup_item.is_dir():
                                shutil.rmtree(backup_item)
                            else:
                                backup_item.unlink()
                            cleaned_count += 1
                            
                except Exception as e:
                    self.logger.warning(f"Error processing backup item {backup_item}: {e}")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {e}")
            return 0
    
    async def _run_data_encryption(self) -> Dict[str, Any]:
        """Run data encryption for sensitive information."""
        try:
            self.logger.info("Running data encryption")
            
            encryption_results = {
                'timestamp': datetime.now().isoformat(),
                'files_encrypted': 0,
                'files_decrypted': 0,
                'sensitive_data_found': 0,
                'encryption_status': 'completed',
                'encrypted_files': []
            }
            
            if not self.encryption_enabled:
                encryption_results['encryption_status'] = 'disabled'
                return encryption_results
            
            # Find and encrypt sensitive files
            sensitive_patterns = self.config.get('encryption', {}).get('sensitive_patterns', [])
            
            for file_path in self.data_root.rglob('*'):
                if file_path.is_file() and not file_path.name.endswith('.encrypted'):
                    try:
                        # Check if file contains sensitive data
                        if self._contains_sensitive_data(file_path, sensitive_patterns):
                            encryption_info = await self._encrypt_file(file_path)
                            if encryption_info:
                                encryption_results['files_encrypted'] += 1
                                encryption_results['encrypted_files'].append(encryption_info)
                                encryption_results['sensitive_data_found'] += 1
                    except Exception as e:
                        self.logger.warning(f"Error processing file {file_path}: {e}")
            
            # Verify encryption status
            verification_results = await self._verify_encryption()
            encryption_results.update(verification_results)
            
            return encryption_results
            
        except Exception as e:
            self.logger.error(f"Error in data encryption: {e}")
            return {'error': str(e), 'encryption_status': 'failed'}
    
    def _contains_sensitive_data(self, file_path: Path, sensitive_patterns: List[str]) -> bool:
        """Check if file contains sensitive data patterns."""
        try:
            # Skip binary files
            if file_path.suffix.lower() in ['.jpg', '.png', '.pdf', '.zip', '.gz']:
                return False
            
            # Read file content (sample first 10KB to avoid memory issues)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10240).lower()  # Read first 10KB
            
            # Check for sensitive patterns
            for pattern in sensitive_patterns:
                if pattern.lower() in content:
                    return True
            
            # Check for common sensitive data patterns
            sensitive_indicators = [
                'password', 'secret', 'api_key', 'token', 'credential',
                'private_key', 'access_key', 'session_id'
            ]
            
            for indicator in sensitive_indicators:
                if indicator in content:
                    return True
            
            return False
            
        except Exception:
            return False  # If we can't read the file, assume it's not sensitive
    
    async def _encrypt_file(self, file_path: Path) -> Optional[Dict]:
        """Encrypt a sensitive file."""
        try:
            # Read original file
            with open(file_path, 'rb') as f:
                original_data = f.read()
            
            # Encrypt data
            encrypted_data = self.cipher.encrypt(original_data)
            
            # Create encrypted file path
            encrypted_path = file_path.with_suffix(file_path.suffix + '.encrypted')
            
            # Write encrypted data
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Create encryption metadata
            metadata = {
                'original_path': str(file_path),
                'encrypted_path': str(encrypted_path),
                'encryption_timestamp': datetime.now().isoformat(),
                'original_size': len(original_data),
                'encrypted_size': len(encrypted_data),
                'encryption_method': 'Fernet'
            }
            
            # Save metadata
            metadata_path = encrypted_path.with_suffix('.metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Securely delete original file (overwrite then delete)
            self._secure_delete_file(file_path)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error encrypting file {file_path}: {e}")
            return None
    
    def _secure_delete_file(self, file_path: Path) -> None:
        """Securely delete a file by overwriting it."""
        try:
            if file_path.exists():
                file_size = file_path.stat().st_size
                
                # Overwrite with random data
                with open(file_path, 'r+b') as f:
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
                
                # Delete the file
                file_path.unlink()
                
        except Exception as e:
            self.logger.warning(f"Error securely deleting file {file_path}: {e}")
            # Fallback to regular deletion
            try:
                file_path.unlink()
            except Exception:
                pass
    
    async def _verify_encryption(self) -> Dict[str, Any]:
        """Verify encryption status of files."""
        try:
            verification_results = {
                'encrypted_files_found': 0,
                'decryptable_files': 0,
                'corrupted_files': 0,
                'verification_errors': []
            }
            
            # Find all encrypted files
            encrypted_files = list(self.data_root.rglob('*.encrypted'))
            verification_results['encrypted_files_found'] = len(encrypted_files)
            
            # Test decryption on sample files (first 5)
            for encrypted_file in encrypted_files[:5]:
                try:
                    with open(encrypted_file, 'rb') as f:
                        encrypted_data = f.read()
                    
                    # Try to decrypt
                    decrypted_data = self.cipher.decrypt(encrypted_data)
                    
                    if decrypted_data:
                        verification_results['decryptable_files'] += 1
                    
                except Exception as e:
                    verification_results['corrupted_files'] += 1
                    verification_results['verification_errors'].append(
                        f"Cannot decrypt {encrypted_file}: {str(e)}"
                    )
            
            return verification_results
            
        except Exception as e:
            self.logger.error(f"Error verifying encryption: {e}")
            return {'error': str(e)}
    
    async def _run_retention_cleanup(self) -> Dict[str, Any]:
        """Run data retention policies and cleanup."""
        try:
            self.logger.info("Running retention cleanup")
            
            cleanup_results = {
                'timestamp': datetime.now().isoformat(),
                'policies_applied': [],
                'files_processed': 0,
                'files_deleted': 0,
                'files_archived': 0,
                'files_compressed': 0,
                'space_freed_mb': 0,
                'cleanup_errors': []
            }
            
            # Apply each retention policy
            for policy_name, policy_config in self.retention_policies.items():
                try:
                    policy_results = await self._apply_retention_policy(policy_name, policy_config)
                    cleanup_results['policies_applied'].append({
                        'policy': policy_name,
                        'results': policy_results
                    })
                    
                    # Aggregate results
                    cleanup_results['files_processed'] += policy_results.get('files_processed', 0)
                    cleanup_results['files_deleted'] += policy_results.get('files_deleted', 0)
                    cleanup_results['files_archived'] += policy_results.get('files_archived', 0)
                    cleanup_results['files_compressed'] += policy_results.get('files_compressed', 0)
                    cleanup_results['space_freed_mb'] += policy_results.get('space_freed_mb', 0)
                    
                except Exception as e:
                    error_msg = f"Error applying policy {policy_name}: {e}"
                    cleanup_results['cleanup_errors'].append(error_msg)
                    self.logger.error(error_msg)
            
            return cleanup_results
            
        except Exception as e:
            self.logger.error(f"Error in retention cleanup: {e}")
            return {'error': str(e)}
    
    async def _apply_retention_policy(self, policy_name: str, policy_config: Dict) -> Dict[str, Any]:
        """Apply a specific retention policy."""
        try:
            results = {
                'policy_name': policy_name,
                'files_processed': 0,
                'files_deleted': 0,
                'files_archived': 0,
                'files_compressed': 0,
                'space_freed_mb': 0
            }
            
            days = policy_config.get('days', 30)
            action = policy_config.get('action', 'delete')
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Determine target paths based on policy name
            target_paths = self._get_policy_target_paths(policy_name)
            
            for target_path in target_paths:
                if target_path.exists():
                    # Find files older than cutoff date
                    for file_path in target_path.rglob('*'):
                        if file_path.is_file():
                            try:
                                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                                
                                if file_mtime < cutoff_date:
                                    file_size = file_path.stat().st_size
                                    space_freed = file_size / (1024 * 1024)  # MB
                                    
                                    results['files_processed'] += 1
                                    
                                    if action == 'delete':
                                        file_path.unlink()
                                        results['files_deleted'] += 1
                                        results['space_freed_mb'] += space_freed
                                        
                                    elif action == 'archive':
                                        await self._archive_file(file_path)
                                        results['files_archived'] += 1
                                        results['space_freed_mb'] += space_freed * 0.3  # Assume 70% compression
                                        
                                    elif action == 'compress':
                                        await self._compress_file(file_path)
                                        results['files_compressed'] += 1
                                        results['space_freed_mb'] += space_freed * 0.5  # Assume 50% compression
                                
                            except Exception as e:
                                self.logger.warning(f"Error processing file {file_path}: {e}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error applying retention policy {policy_name}: {e}")
            return {'error': str(e)}
    
    def _get_policy_target_paths(self, policy_name: str) -> List[Path]:
        """Get target paths for a retention policy."""
        path_mapping = {
            'raw_data': [self.data_root / 'daily_downloads'],
            'processed_data': [self.data_root / 'preprocessed'],
            'logs': [Path('logs')],
            'temp_files': [Path('temp'), Path('/tmp')],
            'backups': [self.backup_root]
        }
        
        return path_mapping.get(policy_name, [self.data_root])
    
    async def _archive_file(self, file_path: Path) -> None:
        """Archive a file to long-term storage."""
        try:
            # Create archive directory
            archive_dir = self.data_root / 'archives' / file_path.parent.name
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Create compressed archive
            archive_path = archive_dir / f"{file_path.stem}_{datetime.now().strftime('%Y%m%d')}.gz"
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(archive_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file
            file_path.unlink()
            
        except Exception as e:
            self.logger.error(f"Error archiving file {file_path}: {e}")
    
    async def _compress_file(self, file_path: Path) -> None:
        """Compress a file in place."""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file
            file_path.unlink()
            
        except Exception as e:
            self.logger.error(f"Error compressing file {file_path}: {e}")
    
    async def _run_system_health_check(self) -> Dict[str, Any]:
        """Run comprehensive system health check."""
        try:
            self.logger.info("Running system health check")
            
            health_results = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'healthy',
                'component_health': {},
                'performance_metrics': {},
                'recommendations': [],
                'critical_issues': []
            }
            
            # Check data architecture components
            components = [
                'data_versioning',
                'backup_system',
                'encryption',
                'retention_policies',
                'monitoring_system'
            ]
            
            for component in components:
                component_health = await self._check_component_health(component)
                health_results['component_health'][component] = component_health
                
                if component_health.get('status') == 'critical':
                    health_results['critical_issues'].append(component)
            
            # Calculate overall status
            if health_results['critical_issues']:
                health_results['overall_status'] = 'critical'
            elif any(c.get('status') == 'warning' for c in health_results['component_health'].values()):
                health_results['overall_status'] = 'warning'
            
            # Performance metrics
            performance_metrics = await self._collect_performance_metrics()
            health_results['performance_metrics'] = performance_metrics
            
            # Generate recommendations
            recommendations = self._generate_system_recommendations(health_results)
            health_results['recommendations'] = recommendations
            
            return health_results
            
        except Exception as e:
            self.logger.error(f"Error in system health check: {e}")
            return {'error': str(e), 'overall_status': 'unknown'}
    
    async def _check_component_health(self, component: str) -> Dict[str, Any]:
        """Check health of a specific component."""
        try:
            health = {
                'component': component,
                'status': 'healthy',
                'last_run': 'unknown',
                'issues': [],
                'metrics': {}
            }
            
            if component == 'data_versioning':
                # Check if versioning directory exists and has recent versions
                if self.versioning_root.exists():
                    version_files = list(self.versioning_root.rglob('*'))
                    health['metrics']['version_files'] = len(version_files)
                    
                    if len(version_files) == 0:
                        health['status'] = 'warning'
                        health['issues'].append('No version files found')
                else:
                    health['status'] = 'critical'
                    health['issues'].append('Versioning directory not found')
            
            elif component == 'backup_system':
                # Check if backup directory exists and has recent backups
                if self.backup_root.exists():
                    backup_files = list(self.backup_root.glob('backup_*'))
                    health['metrics']['backup_files'] = len(backup_files)
                    
                    if backup_files:
                        # Check if latest backup is recent
                        latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
                        last_backup_time = datetime.fromtimestamp(latest_backup.stat().st_mtime)
                        hours_since_backup = (datetime.now() - last_backup_time).total_seconds() / 3600
                        
                        health['last_run'] = last_backup_time.isoformat()
                        health['metrics']['hours_since_last_backup'] = round(hours_since_backup, 1)
                        
                        if hours_since_backup > 48:  # More than 2 days
                            health['status'] = 'warning'
                            health['issues'].append('No recent backups found')
                    else:
                        health['status'] = 'critical'
                        health['issues'].append('No backups found')
                else:
                    health['status'] = 'critical'
                    health['issues'].append('Backup directory not found')
            
            elif component == 'encryption':
                # Check encryption key and encrypted files
                if self.encryption_enabled:
                    encrypted_files = list(self.data_root.rglob('*.encrypted'))
                    health['metrics']['encrypted_files'] = len(encrypted_files)
                    
                    if not self.encryption_key:
                        health['status'] = 'critical'
                        health['issues'].append('Encryption key not available')
                else:
                    health['status'] = 'disabled'
            
            elif component == 'retention_policies':
                # Check if retention policies are configured
                if self.retention_policies:
                    health['metrics']['policies_configured'] = len(self.retention_policies)
                else:
                    health['status'] = 'warning'
                    health['issues'].append('No retention policies configured')
            
            elif component == 'monitoring_system':
                # Check if monitoring results exist
                if self.monitoring_root.exists():
                    monitoring_files = list(self.monitoring_root.glob('monitoring_results_*'))
                    health['metrics']['monitoring_files'] = len(monitoring_files)
                    
                    if monitoring_files:
                        latest_monitoring = max(monitoring_files, key=lambda x: x.stat().st_mtime)
                        last_monitoring_time = datetime.fromtimestamp(latest_monitoring.stat().st_mtime)
                        health['last_run'] = last_monitoring_time.isoformat()
                    else:
                        health['status'] = 'warning'
                        health['issues'].append('No monitoring results found')
                else:
                    health['status'] = 'critical'
                    health['issues'].append('Monitoring directory not found')
            
            return health
            
        except Exception as e:
            return {
                'component': component,
                'status': 'error',
                'error': str(e)
            }
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics."""
        try:
            metrics = {}
            
            # Disk usage metrics
            for path in [self.data_root, self.backup_root, self.versioning_root]:
                if path.exists():
                    total, used, free = shutil.disk_usage(path)
                    metrics[f'{path.name}_disk_usage'] = {
                        'total_gb': round(total / (1024**3), 2),
                        'used_gb': round(used / (1024**3), 2),
                        'free_gb': round(free / (1024**3), 2),
                        'usage_percentage': round(used / total * 100, 2)
                    }
            
            # File count metrics
            metrics['file_counts'] = {
                'data_files': len(list(self.data_root.rglob('*'))),
                'backup_files': len(list(self.backup_root.rglob('*'))) if self.backup_root.exists() else 0,
                'version_files': len(list(self.versioning_root.rglob('*'))) if self.versioning_root.exists() else 0
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting performance metrics: {e}")
            return {'error': str(e)}
    
    def _generate_system_recommendations(self, health_results: Dict) -> List[str]:
        """Generate system improvement recommendations."""
        recommendations = []
        
        try:
            # Check critical issues
            if health_results.get('critical_issues'):
                recommendations.append(
                    f"Address critical issues in: {', '.join(health_results['critical_issues'])}"
                )
            
            # Check disk usage
            performance_metrics = health_results.get('performance_metrics', {})
            for disk_metric, values in performance_metrics.items():
                if 'disk_usage' in disk_metric and isinstance(values, dict):
                    usage_pct = values.get('usage_percentage', 0)
                    if usage_pct > 85:
                        recommendations.append(
                            f"High disk usage ({usage_pct}%) on {disk_metric.replace('_disk_usage', '')} - consider cleanup"
                        )
            
            # Check backup frequency
            component_health = health_results.get('component_health', {})
            backup_health = component_health.get('backup_system', {})
            hours_since_backup = backup_health.get('metrics', {}).get('hours_since_last_backup', 0)
            if hours_since_backup > 24:
                recommendations.append("Consider increasing backup frequency")
            
            # Check versioning
            versioning_health = component_health.get('data_versioning', {})
            version_files = versioning_health.get('metrics', {}).get('version_files', 0)
            if version_files > 1000:
                recommendations.append("Large number of version files - review retention policy")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating system recommendations: {e}")
            return []


# Async main function for standalone execution
async def main():
    """Main function for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Architecture Manager')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--operation', choices=['full', 'monitoring', 'backup', 'versioning', 'encryption', 'cleanup'], 
                        default='full', help='Operation to perform')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize manager
    manager = DataArchitectureManager(config_path=args.config)
    
    try:
        if args.operation == 'full':
            results = await manager.run_data_architecture_improvements()
        elif args.operation == 'monitoring':
            results = await manager._run_data_quality_monitoring()
        elif args.operation == 'backup':
            results = await manager._run_automated_backup()
        elif args.operation == 'versioning':
            results = await manager._run_data_versioning()
        elif args.operation == 'encryption':
            results = await manager._run_data_encryption()
        elif args.operation == 'cleanup':
            results = await manager._run_retention_cleanup()
        
        print(json.dumps(results, indent=2))
        
    except Exception as e:
        logger.error(f"Error in data architecture operation: {e}")
        print(json.dumps({'error': str(e)}, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
