#!/usr/bin/env python3
"""
🔄 Pipeline Recovery Strategies - Phase 2A Error Recovery

Specialized recovery mechanisms for different types of pipeline failures:
- Database connection recovery with connection pooling
- Network failure recovery with circuit breakers
- ML training failure recovery with model fallbacks
- File system recovery with alternative paths
- External API recovery with service degradation

Author: AI Assistant
Date: August 15, 2025
Part of: Phase 2A - Enhanced Error Handling & Recovery
"""

import logging
import os
import pickle
import shutil
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import psycopg2
import psycopg2.pool
import redis
import requests

logger = logging.getLogger(__name__)


@dataclass
class RecoveryResult:
    """Result of a recovery attempt."""

    success: bool
    method_used: str
    fallback_data: Any = None
    recovery_time_seconds: float = 0.0
    notes: str = ""


class DatabaseRecoveryManager:
    """Handles database connection failures and recovery."""

    def __init__(
        self, primary_config: Dict[str, Any], backup_config: Dict[str, Any] = None
    ):
        self.primary_config = primary_config
        self.backup_config = backup_config
        self.connection_pool = None
        self.backup_pool = None
        self.last_health_check = None
        self.health_check_interval = 30  # seconds

    def create_connection_pool(
        self, config: Dict[str, Any], pool_size: int = 5
    ) -> psycopg2.pool.ThreadedConnectionPool:
        """Create a connection pool with the given configuration."""
        return psycopg2.pool.ThreadedConnectionPool(
            1,
            pool_size,
            host=config["host"],
            port=config["port"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
        )

    def health_check(self) -> bool:
        """Check if primary database is healthy."""
        if (
            self.last_health_check
            and datetime.now() - self.last_health_check
            < timedelta(seconds=self.health_check_interval)
        ):
            return self.connection_pool is not None

        try:
            if not self.connection_pool:
                self.connection_pool = self.create_connection_pool(self.primary_config)

            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            self.connection_pool.putconn(conn)

            self.last_health_check = datetime.now()
            return True

        except Exception as e:
            logger.warning(f"⚠️ Primary database health check failed: {e}")
            if self.connection_pool:
                self.connection_pool.closeall()
                self.connection_pool = None
            return False

    def get_connection(self) -> RecoveryResult:
        """Get a database connection with automatic failover."""
        start_time = time.time()

        # Try primary database
        if self.health_check():
            try:
                conn = self.connection_pool.getconn()
                return RecoveryResult(
                    success=True,
                    method_used="primary_database",
                    fallback_data=conn,
                    recovery_time_seconds=time.time() - start_time,
                    notes="Connected to primary database",
                )
            except Exception as e:
                logger.error(f"❌ Failed to get connection from primary pool: {e}")

        # Try backup database if configured
        if self.backup_config:
            try:
                if not self.backup_pool:
                    logger.info("🔄 Attempting backup database connection...")
                    self.backup_pool = self.create_connection_pool(self.backup_config)

                conn = self.backup_pool.getconn()
                return RecoveryResult(
                    success=True,
                    method_used="backup_database",
                    fallback_data=conn,
                    recovery_time_seconds=time.time() - start_time,
                    notes="Connected to backup database",
                )
            except Exception as e:
                logger.error(f"❌ Backup database also failed: {e}")

        return RecoveryResult(
            success=False,
            method_used="none",
            recovery_time_seconds=time.time() - start_time,
            notes="All database connections failed",
        )

    def return_connection(self, conn, is_backup: bool = False):
        """Return a connection to the appropriate pool."""
        try:
            if is_backup and self.backup_pool:
                self.backup_pool.putconn(conn)
            elif self.connection_pool:
                self.connection_pool.putconn(conn)
        except Exception as e:
            logger.error(f"❌ Error returning connection to pool: {e}")


class NetworkRecoveryManager:
    """Handles network failures with circuit breaker pattern."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.circuit_open = False

    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is open."""
        if not self.circuit_open:
            return False

        # Check if recovery timeout has passed
        if (
            self.last_failure_time
            and datetime.now() - self.last_failure_time
            > timedelta(seconds=self.recovery_timeout)
        ):
            logger.info("🔄 Circuit breaker recovery timeout reached, attempting reset")
            self.circuit_open = False
            self.failure_count = 0
            return False

        return True

    def record_success(self):
        """Record a successful operation."""
        self.failure_count = 0
        self.circuit_open = False
        self.last_failure_time = None

    def record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.circuit_open = True
            logger.warning(
                f"🚨 Circuit breaker opened after {self.failure_count} failures"
            )

    def make_request(self, url: str, **kwargs) -> RecoveryResult:
        """Make HTTP request with circuit breaker protection."""
        start_time = time.time()

        if self.is_circuit_open():
            return RecoveryResult(
                success=False,
                method_used="circuit_breaker_open",
                recovery_time_seconds=time.time() - start_time,
                notes=f"Circuit breaker open, {self.failure_count} consecutive failures",
            )

        try:
            response = requests.get(url, timeout=30, **kwargs)
            response.raise_for_status()

            self.record_success()
            return RecoveryResult(
                success=True,
                method_used="http_request",
                fallback_data=response,
                recovery_time_seconds=time.time() - start_time,
                notes=f"HTTP {response.status_code} success",
            )

        except Exception as e:
            self.record_failure()
            return RecoveryResult(
                success=False,
                method_used="http_request_failed",
                recovery_time_seconds=time.time() - start_time,
                notes=f"HTTP request failed: {str(e)}",
            )


class MLTrainingRecoveryManager:
    """Handles ML training failures with model fallbacks."""

    def __init__(self, fallback_models_dir: str = "models/fallback"):
        self.fallback_models_dir = Path(fallback_models_dir)
        self.fallback_models_dir.mkdir(parents=True, exist_ok=True)
        self.model_cache = {}

    def save_fallback_model(
        self, model: Any, model_name: str, metadata: Dict[str, Any] = None
    ):
        """Save a trained model as a fallback option."""
        try:
            model_path = self.fallback_models_dir / f"{model_name}.pkl"
            metadata_path = self.fallback_models_dir / f"{model_name}_metadata.json"

            # Save model
            with open(model_path, "wb") as f:
                pickle.dump(model, f)

            # Save metadata
            metadata = metadata or {}
            metadata.update(
                {
                    "saved_at": datetime.now().isoformat(),
                    "model_name": model_name,
                    "file_size": model_path.stat().st_size,
                }
            )

            import json

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"💾 Saved fallback model: {model_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save fallback model {model_name}: {e}")
            return False

    def load_fallback_model(self, model_name: str) -> RecoveryResult:
        """Load a fallback model when training fails."""
        start_time = time.time()

        try:
            # Check cache first
            if model_name in self.model_cache:
                return RecoveryResult(
                    success=True,
                    method_used="cached_fallback_model",
                    fallback_data=self.model_cache[model_name],
                    recovery_time_seconds=time.time() - start_time,
                    notes=f"Loaded {model_name} from cache",
                )

            # Load from disk
            model_path = self.fallback_models_dir / f"{model_name}.pkl"
            metadata_path = self.fallback_models_dir / f"{model_name}_metadata.json"

            if not model_path.exists():
                return RecoveryResult(
                    success=False,
                    method_used="fallback_model_not_found",
                    recovery_time_seconds=time.time() - start_time,
                    notes=f"Fallback model {model_name} not found",
                )

            with open(model_path, "rb") as f:
                model = pickle.load(f)

            # Load metadata if available
            metadata = {}
            if metadata_path.exists():
                import json

                with open(metadata_path, "r") as f:
                    metadata = json.load(f)

            # Cache the model
            self.model_cache[model_name] = model

            return RecoveryResult(
                success=True,
                method_used="disk_fallback_model",
                fallback_data=model,
                recovery_time_seconds=time.time() - start_time,
                notes=f"Loaded {model_name} from disk, saved {metadata.get('saved_at', 'unknown')}",
            )

        except Exception as e:
            return RecoveryResult(
                success=False,
                method_used="fallback_model_load_failed",
                recovery_time_seconds=time.time() - start_time,
                notes=f"Failed to load fallback model: {str(e)}",
            )

    def create_simple_model(
        self, model_type: str = "linear_regression"
    ) -> RecoveryResult:
        """Create a simple fallback model when all else fails."""
        start_time = time.time()

        try:
            if model_type == "linear_regression":
                from sklearn.linear_model import LinearRegression

                model = LinearRegression()
            elif model_type == "random_forest":
                from sklearn.ensemble import RandomForestClassifier

                model = RandomForestClassifier(n_estimators=10, random_state=42)
            elif model_type == "logistic_regression":
                from sklearn.linear_model import LogisticRegression

                model = LogisticRegression(random_state=42)
            else:
                # Default to linear regression
                from sklearn.linear_model import LinearRegression

                model = LinearRegression()

            return RecoveryResult(
                success=True,
                method_used="simple_model_creation",
                fallback_data=model,
                recovery_time_seconds=time.time() - start_time,
                notes=f"Created simple {model_type} model as fallback",
            )

        except Exception as e:
            return RecoveryResult(
                success=False,
                method_used="simple_model_creation_failed",
                recovery_time_seconds=time.time() - start_time,
                notes=f"Failed to create simple model: {str(e)}",
            )


class FileSystemRecoveryManager:
    """Handles file system failures with alternative paths and recovery."""

    def __init__(self, primary_dir: str, backup_dirs: List[str] = None):
        self.primary_dir = Path(primary_dir)
        self.backup_dirs = [Path(d) for d in (backup_dirs or [])]
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure all directories exist."""
        for directory in [self.primary_dir] + self.backup_dirs:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"⚠️ Could not create directory {directory}: {e}")

    def save_file(
        self, filename: str, data: Any, use_pickle: bool = True
    ) -> RecoveryResult:
        """Save file with automatic failover to backup locations."""
        start_time = time.time()

        # Try primary location first
        for i, directory in enumerate([self.primary_dir] + self.backup_dirs):
            try:
                file_path = directory / filename

                if use_pickle:
                    with open(file_path, "wb") as f:
                        pickle.dump(data, f)
                else:
                    if isinstance(data, str):
                        with open(file_path, "w") as f:
                            f.write(data)
                    elif isinstance(data, bytes):
                        with open(file_path, "wb") as f:
                            f.write(data)
                    else:
                        # Convert to string representation
                        with open(file_path, "w") as f:
                            f.write(str(data))

                location_type = "primary" if i == 0 else f"backup_{i}"
                return RecoveryResult(
                    success=True,
                    method_used=f"file_save_{location_type}",
                    fallback_data=str(file_path),
                    recovery_time_seconds=time.time() - start_time,
                    notes=f"Saved to {location_type} location: {file_path}",
                )

            except Exception as e:
                logger.warning(f"⚠️ Failed to save to {directory}: {e}")
                continue

        return RecoveryResult(
            success=False,
            method_used="file_save_all_failed",
            recovery_time_seconds=time.time() - start_time,
            notes="Failed to save file to any location",
        )

    def load_file(self, filename: str, use_pickle: bool = True) -> RecoveryResult:
        """Load file with automatic search across all locations."""
        start_time = time.time()

        # Try all locations
        for i, directory in enumerate([self.primary_dir] + self.backup_dirs):
            try:
                file_path = directory / filename

                if not file_path.exists():
                    continue

                if use_pickle:
                    with open(file_path, "rb") as f:
                        data = pickle.load(f)
                else:
                    with open(file_path, "r") as f:
                        data = f.read()

                location_type = "primary" if i == 0 else f"backup_{i}"
                return RecoveryResult(
                    success=True,
                    method_used=f"file_load_{location_type}",
                    fallback_data=data,
                    recovery_time_seconds=time.time() - start_time,
                    notes=f"Loaded from {location_type} location: {file_path}",
                )

            except Exception as e:
                logger.warning(f"⚠️ Failed to load from {directory}: {e}")
                continue

        return RecoveryResult(
            success=False,
            method_used="file_load_all_failed",
            recovery_time_seconds=time.time() - start_time,
            notes=f"File {filename} not found in any location",
        )


class CacheRecoveryManager:
    """Handles cache failures with degraded service."""

    def __init__(self, redis_config: Dict[str, Any] = None):
        self.redis_config = redis_config or {"host": "localhost", "port": 6379, "db": 0}
        self.redis_client = None
        self.memory_cache = {}
        self.max_memory_cache_size = 1000

    def get_cache_client(self) -> RecoveryResult:
        """Get cache client with fallback to memory cache."""
        start_time = time.time()

        # Try Redis first
        try:
            if not self.redis_client:
                self.redis_client = redis.Redis(**self.redis_config)

            # Test connection
            self.redis_client.ping()

            return RecoveryResult(
                success=True,
                method_used="redis_cache",
                fallback_data=self.redis_client,
                recovery_time_seconds=time.time() - start_time,
                notes="Connected to Redis cache",
            )

        except Exception as e:
            logger.warning(f"⚠️ Redis cache unavailable, using memory cache: {e}")
            self.redis_client = None

            return RecoveryResult(
                success=True,
                method_used="memory_cache_fallback",
                fallback_data="memory",
                recovery_time_seconds=time.time() - start_time,
                notes="Using in-memory cache as fallback",
            )

    def get(self, key: str) -> RecoveryResult:
        """Get value from cache with automatic fallback."""
        start_time = time.time()

        cache_result = self.get_cache_client()

        if cache_result.success and cache_result.fallback_data != "memory":
            # Try Redis
            try:
                value = self.redis_client.get(key)
                if value:
                    import pickle

                    data = pickle.loads(value)
                    return RecoveryResult(
                        success=True,
                        method_used="redis_cache_hit",
                        fallback_data=data,
                        recovery_time_seconds=time.time() - start_time,
                        notes="Retrieved from Redis cache",
                    )
            except Exception as e:
                logger.warning(f"⚠️ Redis get failed: {e}")

        # Try memory cache
        if key in self.memory_cache:
            return RecoveryResult(
                success=True,
                method_used="memory_cache_hit",
                fallback_data=self.memory_cache[key],
                recovery_time_seconds=time.time() - start_time,
                notes="Retrieved from memory cache",
            )

        return RecoveryResult(
            success=False,
            method_used="cache_miss",
            recovery_time_seconds=time.time() - start_time,
            notes="Cache miss in both Redis and memory",
        )

    def set(self, key: str, value: Any, ttl: int = 3600) -> RecoveryResult:
        """Set value in cache with automatic fallback."""
        start_time = time.time()

        cache_result = self.get_cache_client()

        if cache_result.success and cache_result.fallback_data != "memory":
            # Try Redis
            try:
                import pickle

                serialized = pickle.dumps(value)
                self.redis_client.setex(key, ttl, serialized)

                # Also store in memory cache as backup
                self._manage_memory_cache(key, value)

                return RecoveryResult(
                    success=True,
                    method_used="redis_cache_set",
                    recovery_time_seconds=time.time() - start_time,
                    notes="Stored in Redis cache",
                )
            except Exception as e:
                logger.warning(f"⚠️ Redis set failed: {e}")

        # Fallback to memory cache
        self._manage_memory_cache(key, value)

        return RecoveryResult(
            success=True,
            method_used="memory_cache_set",
            recovery_time_seconds=time.time() - start_time,
            notes="Stored in memory cache",
        )

    def _manage_memory_cache(self, key: str, value: Any):
        """Manage memory cache size by removing oldest entries."""
        self.memory_cache[key] = value

        # Remove oldest entries if cache is too large
        if len(self.memory_cache) > self.max_memory_cache_size:
            # Remove 10% of oldest entries (simple FIFO)
            items_to_remove = len(self.memory_cache) - int(
                self.max_memory_cache_size * 0.9
            )
            keys_to_remove = list(self.memory_cache.keys())[:items_to_remove]
            for k in keys_to_remove:
                del self.memory_cache[k]


if __name__ == "__main__":
    # Test recovery managers
    print("🔄 Testing Pipeline Recovery Strategies...")

    # Test database recovery
    print("\n📊 Testing Database Recovery...")
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "horse_racing_db",
        "user": "horse_racing",
        "password": "secure_password_123",
    }

    db_recovery = DatabaseRecoveryManager(db_config)
    result = db_recovery.get_connection()
    print(f"Database recovery: {result.success} using {result.method_used}")

    # Test ML training recovery
    print("\n🤖 Testing ML Training Recovery...")
    ml_recovery = MLTrainingRecoveryManager()
    result = ml_recovery.create_simple_model("linear_regression")
    print(f"ML recovery: {result.success} using {result.method_used}")

    # Test file system recovery
    print("\n📁 Testing File System Recovery...")
    fs_recovery = FileSystemRecoveryManager(
        "data/primary", ["data/backup1", "data/backup2"]
    )
    result = fs_recovery.save_file("test.txt", "Hello, recovery!", use_pickle=False)
    print(f"File system recovery: {result.success} using {result.method_used}")

    # Test cache recovery
    print("\n💾 Testing Cache Recovery...")
    cache_recovery = CacheRecoveryManager()
    result = cache_recovery.set("test_key", {"data": "test_value"})
    print(f"Cache recovery: {result.success} using {result.method_used}")

    print("\n🎉 Recovery strategies testing complete!")
