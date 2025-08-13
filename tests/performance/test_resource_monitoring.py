#!/usr/bin/env python3
"""
Resource Monitoring Testing Suite - Phase 3 Priority 3
Tests system resource usage and monitoring during pipeline operations

Author: AI Assistant
Date: August 12, 2025
"""

import asyncio
import gc
import os

# Add project root to path
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock, patch

import psutil
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from daily_pipeline_orchestrator import DailyPipelineOrchestrator


class ResourceMonitor:
    """System resource monitoring utility."""

    def __init__(self):
        self.process = psutil.Process()
        self.monitoring_active = False
        self.resource_history = []
        self.monitor_thread = None

    def get_current_resources(self) -> Dict:
        """Get current system resource usage."""
        try:
            memory_info = self.process.memory_info()
            return {
                "timestamp": time.time(),
                "cpu_percent": self.process.cpu_percent(),
                "memory_rss_mb": memory_info.rss / 1024 / 1024,
                "memory_vms_mb": memory_info.vms / 1024 / 1024,
                "threads": self.process.num_threads(),
                "open_files": (
                    self.process.num_fds() if hasattr(self.process, "num_fds") else 0
                ),
                "connections": len(self.process.connections()),
                "system_memory_percent": psutil.virtual_memory().percent,
                "system_cpu_percent": psutil.cpu_percent(),
                "disk_io_read_mb": (
                    psutil.disk_io_counters().read_bytes / 1024 / 1024
                    if psutil.disk_io_counters()
                    else 0
                ),
                "disk_io_write_mb": (
                    psutil.disk_io_counters().write_bytes / 1024 / 1024
                    if psutil.disk_io_counters()
                    else 0
                ),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {"error": str(e), "timestamp": time.time()}

    def start_monitoring(self, interval: float = 0.1):
        """Start continuous resource monitoring."""
        self.monitoring_active = True
        self.resource_history = []

        def monitor_loop():
            while self.monitoring_active:
                resources = self.get_current_resources()
                self.resource_history.append(resources)
                time.sleep(interval)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop continuous resource monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

    def get_resource_statistics(self) -> Dict:
        """Calculate statistics from monitored resources."""
        if not self.resource_history:
            return {}

        # Filter out error entries
        valid_history = [r for r in self.resource_history if "error" not in r]

        if not valid_history:
            return {"error": "No valid resource data collected"}

        stats = {}
        metrics = [
            "cpu_percent",
            "memory_rss_mb",
            "memory_vms_mb",
            "threads",
            "open_files",
            "connections",
            "system_memory_percent",
            "system_cpu_percent",
        ]

        for metric in metrics:
            values = [r.get(metric, 0) for r in valid_history if metric in r]
            if values:
                stats[metric] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "samples": len(values),
                }

        stats["monitoring_duration"] = (
            valid_history[-1]["timestamp"] - valid_history[0]["timestamp"]
        )
        stats["total_samples"] = len(valid_history)

        return stats


class TestResourceMonitoring:
    """Test suite for resource monitoring and usage validation."""

    def setup_method(self):
        """Setup for each test method."""
        self.resource_monitor = ResourceMonitor()
        self.orchestrator = None

    def teardown_method(self):
        """Cleanup after each test method."""
        if self.resource_monitor.monitoring_active:
            self.resource_monitor.stop_monitoring()

        # Force garbage collection
        gc.collect()

    def create_orchestrator(self):
        """Create a properly mocked orchestrator."""
        mock_manager_instance = Mock()

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

        with patch(
            "daily_pipeline_orchestrator.create_config_manager",
            return_value=Mock(return_value=mock_manager_instance),
        ):
            with patch("psycopg2.pool.ThreadedConnectionPool"):
                return DailyPipelineOrchestrator()

    def test_baseline_resource_usage(self):
        """Test baseline resource usage without any operations."""
        print("\n📊 Testing baseline resource usage...")

        # Start monitoring
        self.resource_monitor.start_monitoring(interval=0.05)

        # Let it monitor baseline for a short period
        time.sleep(0.5)

        # Stop monitoring
        self.resource_monitor.stop_monitoring()

        # Analyze baseline resources
        stats = self.resource_monitor.get_resource_statistics()

        print(
            f"   💾 Memory (RSS): {stats['memory_rss_mb']['avg']:.1f}MB "
            f"(min: {stats['memory_rss_mb']['min']:.1f}, "
            f"max: {stats['memory_rss_mb']['max']:.1f})"
        )
        print(
            f"   🔄 CPU: {stats['cpu_percent']['avg']:.1f}% "
            f"(min: {stats['cpu_percent']['min']:.1f}, "
            f"max: {stats['cpu_percent']['max']:.1f})"
        )
        print(
            f"   🧵 Threads: {stats['threads']['avg']:.1f} "
            f"(min: {stats['threads']['min']}, "
            f"max: {stats['threads']['max']})"
        )
        print(f"   📁 Open files: {stats['open_files']['avg']:.1f}")
        print(f"   ⏱️  Monitoring duration: {stats['monitoring_duration']:.2f}s")

        # Baseline assertions
        assert (
            stats["memory_rss_mb"]["avg"] < 200
        ), f"Baseline memory usage {stats['memory_rss_mb']['avg']:.1f}MB too high"
        assert (
            stats["cpu_percent"]["max"] < 50
        ), f"Baseline CPU usage {stats['cpu_percent']['max']:.1f}% too high"
        assert (
            stats["threads"]["max"] < 20
        ), f"Baseline thread count {stats['threads']['max']} too high"

    def test_orchestrator_initialization_resource_impact(self):
        """Test resource impact of orchestrator initialization."""
        print("\n🚀 Testing orchestrator initialization resource impact...")

        # Get baseline resources
        baseline = self.resource_monitor.get_current_resources()

        # Start monitoring
        self.resource_monitor.start_monitoring(interval=0.02)

        # Create orchestrator
        orchestrator = self.create_orchestrator()

        # Let monitoring capture initialization impact
        time.sleep(0.3)

        # Stop monitoring
        self.resource_monitor.stop_monitoring()

        # Analyze resource impact
        stats = self.resource_monitor.get_resource_statistics()
        final_resources = self.resource_monitor.get_current_resources()

        memory_increase = final_resources["memory_rss_mb"] - baseline["memory_rss_mb"]

        print(f"   📈 Memory increase: {memory_increase:.1f}MB")
        print(f"   🔄 Max CPU during init: {stats['cpu_percent']['max']:.1f}%")
        print(
            f"   🧵 Thread increase: "
            f"{final_resources['threads'] - baseline['threads']}"
        )
        print(
            f"   📁 Open files increase: "
            f"{final_resources['open_files'] - baseline['open_files']}"
        )

        # Initialization impact assertions
        assert (
            memory_increase < 50
        ), f"Orchestrator initialization increased memory by {memory_increase:.1f}MB"
        assert (
            stats["cpu_percent"]["max"] < 150
        ), f"CPU usage during initialization {stats['cpu_percent']['max']:.1f}% too high"
        assert (
            final_resources["threads"] - baseline["threads"] < 10
        ), "Too many threads created during initialization"

    def test_database_connection_resource_usage(self):
        """Test resource usage during database connection operations."""
        print("\n🔗 Testing database connection resource usage...")

        orchestrator = self.create_orchestrator()

        # Start monitoring
        self.resource_monitor.start_monitoring(interval=0.02)

        # Perform multiple database connection operations
        connections = []
        for i in range(10):
            try:
                conn = asyncio.run(orchestrator.get_db_connection())
                connections.append(conn)
                time.sleep(0.01)  # Small delay between connections
            except Exception as e:
                print(f"   ⚠️  Connection {i} failed: {e}")

        # Let monitoring capture connection impact
        time.sleep(0.2)

        # Stop monitoring
        self.resource_monitor.stop_monitoring()

        # Analyze resource usage
        stats = self.resource_monitor.get_resource_statistics()

        print(f"   🔗 Connections established: {len(connections)}")
        print(
            f"   💾 Memory usage range: "
            f"{stats['memory_rss_mb']['min']:.1f}-{stats['memory_rss_mb']['max']:.1f}MB"
        )
        print(
            f"   🔄 CPU usage range: "
            f"{stats['cpu_percent']['min']:.1f}-{stats['cpu_percent']['max']:.1f}%"
        )
        print(f"   📊 Active connections: {stats['connections']['max']}")

        # Database connection resource assertions
        memory_variance = stats["memory_rss_mb"]["max"] - stats["memory_rss_mb"]["min"]
        assert (
            memory_variance < 30
        ), f"Memory variance during connections {memory_variance:.1f}MB too high"

        # Note: Mocked connections won't show up in network connection monitoring
        # This is expected behavior in testing environment
        assert (
            len(connections) >= 8
        ), f"Expected at least 8 connections, got {len(connections)}"

    def test_memory_leak_detection(self):
        """Test for memory leaks during repeated operations."""
        print("\n🔍 Testing memory leak detection...")

        orchestrator = self.create_orchestrator()

        # Start monitoring
        self.resource_monitor.start_monitoring(interval=0.05)

        # Perform repeated operations that might cause memory leaks
        for cycle in range(5):
            print(f"   🔄 Memory cycle {cycle + 1}/5...")

            # Create and destroy multiple objects
            test_objects = []
            for i in range(100):
                test_data = {
                    "id": i,
                    "data": [f"item_{j}" for j in range(50)],
                    "timestamp": time.time(),
                }
                test_objects.append(test_data)

            # Simulate database operations
            for i in range(5):
                try:
                    conn = asyncio.run(orchestrator.get_db_connection())
                except Exception:
                    pass

            # Clear objects and force garbage collection
            del test_objects
            gc.collect()

            time.sleep(0.1)  # Allow monitoring to capture changes

        # Stop monitoring
        self.resource_monitor.stop_monitoring()

        # Analyze memory patterns
        stats = self.resource_monitor.get_resource_statistics()
        memory_samples = [
            r["memory_rss_mb"]
            for r in self.resource_monitor.resource_history
            if "memory_rss_mb" in r
        ]

        # Calculate memory trend
        if len(memory_samples) >= 10:
            first_half_avg = sum(memory_samples[: len(memory_samples) // 2]) / (
                len(memory_samples) // 2
            )
            second_half_avg = sum(memory_samples[len(memory_samples) // 2 :]) / (
                len(memory_samples) - len(memory_samples) // 2
            )
            memory_trend = second_half_avg - first_half_avg
        else:
            memory_trend = 0

        print(f"   📊 Memory samples: {len(memory_samples)}")
        print(
            f"   💾 Memory range: "
            f"{stats['memory_rss_mb']['min']:.1f}-{stats['memory_rss_mb']['max']:.1f}MB"
        )
        print(f"   📈 Memory trend: {memory_trend:+.1f}MB")
        print(
            f"   🗑️  Memory variance: "
            f"{stats['memory_rss_mb']['max'] - stats['memory_rss_mb']['min']:.1f}MB"
        )

        # Memory leak detection assertions
        assert (
            memory_trend < 10
        ), f"Potential memory leak detected: {memory_trend:.1f}MB increase trend"
        memory_variance = stats["memory_rss_mb"]["max"] - stats["memory_rss_mb"]["min"]
        assert (
            memory_variance < 50
        ), f"Memory variance {memory_variance:.1f}MB indicates instability"

    def test_cpu_usage_under_load(self):
        """Test CPU usage patterns under computational load."""
        print("\n⚡ Testing CPU usage under computational load...")

        orchestrator = self.create_orchestrator()

        # Start monitoring
        self.resource_monitor.start_monitoring(interval=0.02)

        # Generate computational load
        def cpu_intensive_task(duration=0.5):
            """CPU-intensive task for testing."""
            end_time = time.time() + duration
            result = 0

            while time.time() < end_time:
                # Mathematical operations
                for i in range(1000):
                    result += i**2
                    result = result % 1000000

            return result

        # Run CPU-intensive tasks
        print("   🔥 Running CPU-intensive workload...")
        for i in range(3):
            result = cpu_intensive_task(0.3)
            time.sleep(0.1)  # Brief pause between tasks

        # Stop monitoring
        self.resource_monitor.stop_monitoring()

        # Analyze CPU usage
        stats = self.resource_monitor.get_resource_statistics()

        print(
            f"   ⚡ CPU usage range: "
            f"{stats['cpu_percent']['min']:.1f}-{stats['cpu_percent']['max']:.1f}%"
        )
        print(f"   📊 Average CPU: {stats['cpu_percent']['avg']:.1f}%")
        print(f"   🖥️  System CPU max: {stats['system_cpu_percent']['max']:.1f}%")

        # CPU usage assertions
        assert (
            stats["cpu_percent"]["max"] > 10
        ), "CPU-intensive tasks didn't register significant CPU usage"
        assert (
            stats["cpu_percent"]["max"] < 200
        ), f"CPU usage {stats['cpu_percent']['max']:.1f}% too high (possible runaway process)"
        assert (
            stats["cpu_percent"]["avg"] < stats["cpu_percent"]["max"]
        ), "CPU usage should vary during the test"

    def test_file_handle_management(self):
        """Test file handle usage and proper cleanup."""
        print("\n📁 Testing file handle management...")

        orchestrator = self.create_orchestrator()

        # Get baseline file handle count
        baseline = self.resource_monitor.get_current_resources()
        baseline_files = baseline.get("open_files", 0)

        # Start monitoring
        self.resource_monitor.start_monitoring(interval=0.05)

        # Simulate file operations
        temp_files = []
        try:
            for i in range(20):
                # Create temporary files
                import tempfile

                temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
                temp_file.write(f"Test data {i}\n")
                temp_file.close()
                temp_files.append(temp_file.name)

                # Brief pause to allow monitoring
                time.sleep(0.02)

        finally:
            # Cleanup temporary files
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except FileNotFoundError:
                    pass

        # Stop monitoring
        self.resource_monitor.stop_monitoring()

        # Check final file handle count
        final_resources = self.resource_monitor.get_current_resources()
        final_files = final_resources.get("open_files", 0)

        # Analyze file handle usage
        stats = self.resource_monitor.get_resource_statistics()

        print(f"   📁 Baseline files: {baseline_files}")
        print(f"   📁 Peak files: {stats['open_files']['max']}")
        print(f"   📁 Final files: {final_files}")
        print(f"   📁 File handle increase: {final_files - baseline_files}")

        # File handle management assertions
        file_increase = final_files - baseline_files
        assert (
            file_increase < 10
        ), f"File handle leak detected: {file_increase} handles not cleaned up"
        assert (
            stats["open_files"]["max"] - baseline_files <= 25
        ), f"Too many files open simultaneously: {stats['open_files']['max']}"


if __name__ == "__main__":
    # Run resource monitoring tests directly
    pytest.main([__file__, "-v", "--tb=short"])
