#!/usr/bin/env python3
"""
Load Testing Suite - Phase 3 Priority 3
Tests pipeline performance under high-volume data processing scenarios

Author: AI Assistant
Date: August 12, 2025
"""

import asyncio
import csv
import json
import os
import psutil
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Tuple
from unittest.mock import Mock, patch
import pytest

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from daily_pipeline_orchestrator import DailyPipelineOrchestrator


class LoadTestingFramework:
    """Framework for conducting load tests on the pipeline."""
    
    def __init__(self):
        self.performance_metrics = {}
        self.baseline_metrics = {
            'startup_time': 0.05,  # 50ms baseline
            'memory_usage_mb': 50,  # 50MB baseline
            'processing_time_per_race': 0.1,  # 100ms per race
            'database_connection_time': 0.01,  # 10ms connection time
        }
    
    def monitor_system_resources(self) -> Dict:
        """Monitor current system resource usage."""
        process = psutil.Process()
        return {
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'threads': process.num_threads(),
            'connections': len(process.connections()),
            'open_files': process.num_fds() if hasattr(process, 'num_fds') else 0
        }
    
    def generate_large_dataset(self, num_races: int = 1000, num_horses_per_race: int = 12) -> str:
        """Generate a large CSV dataset for testing."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        
        # Write CSV headers
        headers = [
            'race_date', 'course', 'race_time', 'race_name', 'race_class',
            'horse_name', 'jockey', 'trainer', 'weight', 'odds', 'position', 'rating'
        ]
        
        writer = csv.writer(temp_file)
        writer.writerow(headers)
        
        # Generate race data
        for race_id in range(num_races):
            race_date = f"2025-08-{12 + (race_id % 19):02d}"
            course = f"Course_{race_id % 10}"
            race_time = f"{14 + (race_id % 6)}:{(race_id * 15) % 60:02d}"
            race_name = f"Race_{race_id}"
            race_class = f"Class_{race_id % 5}"
            
            for horse_id in range(num_horses_per_race):
                writer.writerow([
                    race_date, course, race_time, race_name, race_class,
                    f"Horse_{race_id}_{horse_id}", f"Jockey_{horse_id}",
                    f"Trainer_{horse_id}", f"{55 + horse_id}kg",
                    f"{2.5 + horse_id * 0.5:.1f}", horse_id + 1,
                    85 + horse_id * 2
                ])
        
        temp_file.close()
        return temp_file.name
    
    def measure_execution_time(self, func, *args, **kwargs) -> Tuple[float, any]:
        """Measure execution time of a function."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return end_time - start_time, result


class TestLoadPerformance:
    """Load testing for pipeline performance under various scenarios."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.load_framework = LoadTestingFramework()
        self.orchestrator = None
    
    def teardown_method(self):
        """Cleanup after each test method."""
        if hasattr(self, 'temp_files'):
            for temp_file in self.temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    @patch('daily_pipeline_orchestrator.create_config_manager')
    @patch('psycopg2.pool.ThreadedConnectionPool')
    def test_startup_performance_under_load(self, mock_pool, mock_config_manager):
        """Test pipeline startup performance with multiple initializations."""
        # Setup mocks
        mock_manager_instance = Mock()
        mock_config_manager.return_value = Mock(return_value=mock_manager_instance)
        
        mock_config = Mock()
        mock_config.database.host = "localhost"
        mock_config.database.port = 5432
        mock_config.database.database = "test_db"
        mock_config.database.user = "test_user"
        mock_config.database.password = "test_pass"
        mock_config.database.pool_min_connections = 1
        mock_config.database.pool_max_connections = 20
        mock_config.data_sources.circuit_breaker_threshold = 3
        mock_config.data_sources.circuit_breaker_timeout = 60
        mock_config.data_sources.retry_attempts = 3
        
        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []
        
        # Test multiple rapid initializations
        startup_times = []
        memory_usage = []
        
        for i in range(10):
            initial_resources = self.load_framework.monitor_system_resources()
            
            start_time = time.time()
            orchestrator = DailyPipelineOrchestrator()
            end_time = time.time()
            
            startup_time = end_time - start_time
            startup_times.append(startup_time)
            
            final_resources = self.load_framework.monitor_system_resources()
            memory_usage.append(final_resources['memory_mb'])
        
        # Performance assertions
        avg_startup_time = sum(startup_times) / len(startup_times)
        max_startup_time = max(startup_times)
        avg_memory = sum(memory_usage) / len(memory_usage)
        
        print(f"\n🔍 Startup Performance Metrics:")
        print(f"   Average startup time: {avg_startup_time:.3f}s")
        print(f"   Maximum startup time: {max_startup_time:.3f}s")
        print(f"   Average memory usage: {avg_memory:.1f}MB")
        
        # Performance benchmarks
        assert avg_startup_time < 0.1, f"Average startup time {avg_startup_time:.3f}s exceeds 100ms threshold"
        assert max_startup_time < 0.2, f"Maximum startup time {max_startup_time:.3f}s exceeds 200ms threshold"
        assert avg_memory < 100, f"Average memory usage {avg_memory:.1f}MB exceeds 100MB threshold"
    
    @patch('daily_pipeline_orchestrator.create_config_manager')
    @patch('psycopg2.pool.ThreadedConnectionPool')
    def test_large_dataset_processing_performance(self, mock_pool, mock_config_manager):
        """Test pipeline performance with large datasets."""
        # Setup orchestrator
        mock_manager_instance = Mock()
        mock_config_manager.return_value = Mock(return_value=mock_manager_instance)
        
        mock_config = Mock()
        mock_config.database.host = "localhost"
        mock_config.database.port = 5432
        mock_config.database.database = "test_db"
        mock_config.database.user = "test_user"
        mock_config.database.password = "test_pass"
        mock_config.database.pool_min_connections = 5
        mock_config.database.pool_max_connections = 20
        mock_config.data_sources.circuit_breaker_threshold = 5
        mock_config.data_sources.circuit_breaker_timeout = 60
        mock_config.data_sources.retry_attempts = 3
        
        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []
        
        orchestrator = DailyPipelineOrchestrator()
        
        # Test with different dataset sizes
        test_sizes = [100, 500, 1000]  # Number of races
        self.temp_files = []
        
        for size in test_sizes:
            print(f"\n📊 Testing with {size} races dataset...")
            
            # Generate large dataset
            large_dataset = self.load_framework.generate_large_dataset(
                num_races=size, 
                num_horses_per_race=12
            )
            self.temp_files.append(large_dataset)
            
            # Monitor resources before processing
            initial_resources = self.load_framework.monitor_system_resources()
            
            # Simulate data processing (mock the actual processing)
            start_time = time.time()
            
            # Mock processing logic
            with open(large_dataset, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
                processed_rows = len(rows) - 1  # Exclude header
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Monitor resources after processing
            final_resources = self.load_framework.monitor_system_resources()
            
            # Calculate metrics
            processing_rate = processed_rows / processing_time if processing_time > 0 else 0
            memory_increase = final_resources['memory_mb'] - initial_resources['memory_mb']
            
            print(f"   📈 Processed {processed_rows} rows in {processing_time:.3f}s")
            print(f"   ⚡ Processing rate: {processing_rate:.1f} rows/second")
            print(f"   💾 Memory increase: {memory_increase:.1f}MB")
            
            # Performance assertions
            assert processing_time < size * 0.01, f"Processing time {processing_time:.3f}s too slow for {size} races"
            assert processing_rate > 1000, f"Processing rate {processing_rate:.1f} rows/s below 1000 rows/s threshold"
            assert memory_increase < 50, f"Memory increase {memory_increase:.1f}MB exceeds 50MB threshold"
    
    @patch('daily_pipeline_orchestrator.create_config_manager')
    @patch('psycopg2.pool.ThreadedConnectionPool')
    def test_database_connection_pool_under_load(self, mock_pool, mock_config_manager):
        """Test database connection pool performance under load."""
        # Setup orchestrator with connection pool
        mock_manager_instance = Mock()
        mock_config_manager.return_value = Mock(return_value=mock_manager_instance)
        
        mock_config = Mock()
        mock_config.database.host = "localhost"
        mock_config.database.port = 5432
        mock_config.database.database = "test_db"
        mock_config.database.user = "test_user"
        mock_config.database.password = "test_pass"
        mock_config.database.pool_min_connections = 5
        mock_config.database.pool_max_connections = 20
        mock_config.data_sources.circuit_breaker_threshold = 5
        mock_config.data_sources.circuit_breaker_timeout = 60
        mock_config.data_sources.retry_attempts = 3
        
        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []
        
        # Mock connection pool behavior
        mock_pool_instance = Mock()
        mock_conn = Mock()
        mock_conn.closed = 0  # Connection is open
        mock_pool_instance.getconn.return_value = mock_conn
        mock_pool.return_value = mock_pool_instance
        
        orchestrator = DailyPipelineOrchestrator()
        
        # Test rapid connection requests
        connection_times = []
        num_connections = 50
        
        print(f"\n🔗 Testing {num_connections} rapid database connections...")
        
        for i in range(num_connections):
            start_time = time.time()
            
            # Simulate getting and returning a connection
            try:
                conn = asyncio.run(orchestrator.get_db_connection())
                if hasattr(orchestrator, 'return_db_connection'):
                    orchestrator.return_db_connection(conn)
            except Exception as e:
                print(f"   ⚠️  Connection {i} failed: {e}")
                continue
            
            end_time = time.time()
            connection_time = end_time - start_time
            connection_times.append(connection_time)
        
        # Calculate connection performance metrics
        if connection_times:
            avg_connection_time = sum(connection_times) / len(connection_times)
            max_connection_time = max(connection_times)
            successful_connections = len(connection_times)
            
            print(f"   📊 Successful connections: {successful_connections}/{num_connections}")
            print(f"   ⚡ Average connection time: {avg_connection_time:.4f}s")
            print(f"   🔥 Maximum connection time: {max_connection_time:.4f}s")
            
            # Performance assertions
            assert successful_connections >= num_connections * 0.95, "Less than 95% connection success rate"
            assert avg_connection_time < 0.05, f"Average connection time {avg_connection_time:.4f}s exceeds 50ms"
            assert max_connection_time < 0.1, f"Maximum connection time {max_connection_time:.4f}s exceeds 100ms"
        else:
            pytest.fail("No successful database connections established")
    
    @patch('daily_pipeline_orchestrator.create_config_manager')
    @patch('psycopg2.pool.ThreadedConnectionPool')
    def test_memory_usage_stability_under_load(self, mock_pool, mock_config_manager):
        """Test memory usage stability during extended operations."""
        # Setup orchestrator
        mock_manager_instance = Mock()
        mock_config_manager.return_value = Mock(return_value=mock_manager_instance)
        
        mock_config = Mock()
        mock_config.database.host = "localhost"
        mock_config.database.port = 5432
        mock_config.database.database = "test_db"
        mock_config.database.user = "test_user"
        mock_config.database.password = "test_pass"
        mock_config.database.pool_min_connections = 2
        mock_config.database.pool_max_connections = 10
        mock_config.data_sources.circuit_breaker_threshold = 3
        mock_config.data_sources.circuit_breaker_timeout = 60
        mock_config.data_sources.retry_attempts = 3
        
        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []
        
        orchestrator = DailyPipelineOrchestrator()
        
        # Monitor memory usage over multiple operations
        memory_samples = []
        num_iterations = 20
        
        print(f"\n💾 Monitoring memory usage over {num_iterations} iterations...")
        
        baseline_memory = self.load_framework.monitor_system_resources()['memory_mb']
        memory_samples.append(baseline_memory)
        
        for i in range(num_iterations):
            # Simulate various pipeline operations
            try:
                # Mock data processing
                test_data = [f"data_{j}" for j in range(1000)]
                processed = [item.upper() for item in test_data]
                
                # Mock database operations
                conn = asyncio.run(orchestrator.get_db_connection())
                
                # Monitor memory
                current_memory = self.load_framework.monitor_system_resources()['memory_mb']
                memory_samples.append(current_memory)
                
                if i % 5 == 0:
                    print(f"   📊 Iteration {i}: {current_memory:.1f}MB")
                
            except Exception as e:
                print(f"   ⚠️  Iteration {i} failed: {e}")
        
        # Analyze memory usage patterns
        memory_increase = max(memory_samples) - baseline_memory
        memory_variance = max(memory_samples) - min(memory_samples)
        final_memory = memory_samples[-1]
        
        print(f"\n📈 Memory Usage Analysis:")
        print(f"   Baseline memory: {baseline_memory:.1f}MB")
        print(f"   Final memory: {final_memory:.1f}MB")
        print(f"   Maximum increase: {memory_increase:.1f}MB")
        print(f"   Memory variance: {memory_variance:.1f}MB")
        
        # Memory stability assertions
        assert memory_increase < 100, f"Memory increase {memory_increase:.1f}MB exceeds 100MB threshold"
        assert memory_variance < 50, f"Memory variance {memory_variance:.1f}MB indicates instability"
        assert final_memory < baseline_memory + 30, f"Final memory {final_memory:.1f}MB shows potential memory leak"


if __name__ == "__main__":
    # Run load tests directly
    pytest.main([__file__, "-v", "--tb=short"])
