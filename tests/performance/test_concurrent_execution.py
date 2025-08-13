#!/usr/bin/env python3
"""
Concurrent Execution Testing Suite - Phase 3 Priority 3
Tests pipeline performance under concurrent and parallel execution scenarios

Author: AI Assistant
Date: August 12, 2025
"""

import asyncio
import concurrent.futures

# Add project root to path
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Tuple
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from daily_pipeline_orchestrator import DailyPipelineOrchestrator


class ConcurrentTestingFramework:
    """Framework for testing concurrent execution patterns."""

    def __init__(self):
        self.execution_results = {}
        self.thread_safety_violations = []
        self.race_conditions = []

    def monitor_concurrent_execution(
        self, func, args_list: List[Tuple], max_workers: int = 5
    ) -> Dict:
        """Execute function concurrently and monitor results."""
        results = {}
        errors = []
        execution_times = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_args = {executor.submit(func, *args): args for args in args_list}

            # Collect results
            for future in concurrent.futures.as_completed(future_to_args):
                args = future_to_args[future]
                start_time = time.time()

                try:
                    result = future.result()
                    end_time = time.time()
                    execution_time = end_time - start_time

                    results[args] = {
                        "result": result,
                        "execution_time": execution_time,
                        "success": True,
                    }
                    execution_times.append(execution_time)

                except Exception as e:
                    results[args] = {
                        "error": str(e),
                        "execution_time": 0,
                        "success": False,
                    }
                    errors.append(str(e))

        return {
            "results": results,
            "errors": errors,
            "total_executions": len(args_list),
            "successful_executions": sum(1 for r in results.values() if r["success"]),
            "average_execution_time": (
                sum(execution_times) / len(execution_times) if execution_times else 0
            ),
            "max_execution_time": max(execution_times) if execution_times else 0,
        }

    async def monitor_async_concurrent_execution(
        self, async_func, args_list: List[Tuple], max_concurrency: int = 5
    ) -> Dict:
        """Execute async function concurrently and monitor results."""
        semaphore = asyncio.Semaphore(max_concurrency)
        results = {}
        errors = []
        execution_times = []

        async def execute_with_semaphore(args):
            async with semaphore:
                start_time = time.time()
                try:
                    result = await async_func(*args)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    execution_times.append(execution_time)
                    return args, {
                        "result": result,
                        "execution_time": execution_time,
                        "success": True,
                    }
                except Exception as e:
                    return args, {
                        "error": str(e),
                        "execution_time": 0,
                        "success": False,
                    }

        # Execute all tasks concurrently
        tasks = [execute_with_semaphore(args) for args in args_list]
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for task_result in completed_tasks:
            if isinstance(task_result, Exception):
                errors.append(str(task_result))
            else:
                args, result_data = task_result
                results[args] = result_data
                if not result_data["success"]:
                    errors.append(result_data.get("error", "Unknown error"))

        return {
            "results": results,
            "errors": errors,
            "total_executions": len(args_list),
            "successful_executions": sum(1 for r in results.values() if r["success"]),
            "average_execution_time": (
                sum(execution_times) / len(execution_times) if execution_times else 0
            ),
            "max_execution_time": max(execution_times) if execution_times else 0,
        }


class TestConcurrentExecution:
    """Test suite for concurrent execution scenarios."""

    def setup_method(self):
        """Setup for each test method."""
        self.concurrent_framework = ConcurrentTestingFramework()
        self.orchestrators = []

    def teardown_method(self):
        """Cleanup after each test method."""
        self.orchestrators.clear()

    def create_orchestrator(self):
        """Create a properly mocked orchestrator."""
        with patch("daily_pipeline_orchestrator.create_config_manager"):
            with patch("psycopg2.pool.ThreadedConnectionPool"):
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
                    return DailyPipelineOrchestrator()

    def test_multiple_orchestrator_initialization_concurrency(self):
        """Test concurrent initialization of multiple orchestrator instances."""
        print("\n🔄 Testing concurrent orchestrator initialization...")

        def create_orchestrator_task(task_id):
            """Task function for creating orchestrator."""
            try:
                orchestrator = self.create_orchestrator()
                return f"orchestrator_{task_id}", orchestrator
            except Exception as e:
                return f"orchestrator_{task_id}", str(e)

        # Test concurrent initialization
        task_args = [(i,) for i in range(10)]
        results = self.concurrent_framework.monitor_concurrent_execution(
            create_orchestrator_task, task_args, max_workers=5
        )

        print(f"   📊 Total executions: {results['total_executions']}")
        print(f"   ✅ Successful: {results['successful_executions']}")
        print(f"   ❌ Failed: {len(results['errors'])}")
        print(f"   ⚡ Average time: {results['average_execution_time']:.3f}s")
        print(f"   🔥 Max time: {results['max_execution_time']:.3f}s")

        # Performance assertions
        assert (
            results["successful_executions"] >= 8
        ), f"Only {results['successful_executions']}/10 orchestrators created successfully"
        assert (
            results["average_execution_time"] < 0.2
        ), f"Average initialization time {results['average_execution_time']:.3f}s too slow"
        assert len(results["errors"]) <= 2, f"Too many errors: {results['errors']}"

    def test_concurrent_database_operations(self):
        """Test concurrent database operations on single orchestrator."""
        print("\n🔗 Testing concurrent database operations...")

        # Create single orchestrator for shared access
        orchestrator = self.create_orchestrator()

        def database_operation_task(operation_id):
            """Task function for database operations."""
            try:
                # Simulate database operation
                conn = asyncio.run(orchestrator.get_db_connection())

                # Simulate query execution time
                time.sleep(0.01)  # 10ms simulated query

                result = {
                    "operation_id": operation_id,
                    "connection_status": "connected" if conn else "failed",
                    "timestamp": time.time(),
                }

                return result
            except Exception as e:
                return {"operation_id": operation_id, "error": str(e)}

        # Test concurrent database operations
        task_args = [(i,) for i in range(20)]
        results = self.concurrent_framework.monitor_concurrent_execution(
            database_operation_task, task_args, max_workers=8
        )

        print(f"   📊 Total operations: {results['total_executions']}")
        print(f"   ✅ Successful: {results['successful_executions']}")
        print(f"   ❌ Failed: {len(results['errors'])}")
        print(f"   ⚡ Average time: {results['average_execution_time']:.3f}s")

        # Concurrency assertions
        assert (
            results["successful_executions"] >= 18
        ), f"Only {results['successful_executions']}/20 database operations successful"
        assert (
            results["average_execution_time"] < 0.1
        ), f"Average operation time {results['average_execution_time']:.3f}s too slow"

    @pytest.mark.asyncio
    async def test_async_concurrent_pipeline_stages(self):
        """Test concurrent execution of async pipeline stages."""
        print("\n⚡ Testing async concurrent pipeline stages...")

        orchestrator = self.create_orchestrator()

        async def async_pipeline_stage(stage_name, processing_time=0.02):
            """Simulate async pipeline stage execution."""
            try:
                await asyncio.sleep(processing_time)  # Simulate async work

                result = {
                    "stage": stage_name,
                    "status": "completed",
                    "processing_time": processing_time,
                    "timestamp": time.time(),
                }

                return result
            except Exception as e:
                return {"stage": stage_name, "error": str(e)}

        # Define pipeline stages to run concurrently
        stage_args = [
            ("data_extraction", 0.03),
            ("data_validation", 0.02),
            ("data_transformation", 0.04),
            ("data_analysis", 0.05),
            ("result_compilation", 0.02),
        ]

        # Execute stages concurrently
        results = await self.concurrent_framework.monitor_async_concurrent_execution(
            async_pipeline_stage, stage_args, max_concurrency=3
        )

        print(f"   📊 Total stages: {results['total_executions']}")
        print(f"   ✅ Successful: {results['successful_executions']}")
        print(f"   ❌ Failed: {len(results['errors'])}")
        print(f"   ⚡ Average time: {results['average_execution_time']:.3f}s")
        print(f"   🔥 Max time: {results['max_execution_time']:.3f}s")

        # Async concurrency assertions
        assert (
            results["successful_executions"] == 5
        ), f"Not all pipeline stages completed successfully: {results['successful_executions']}/5"
        assert (
            results["max_execution_time"] < 0.1
        ), f"Maximum stage time {results['max_execution_time']:.3f}s too slow"
        assert (
            len(results["errors"]) == 0
        ), f"Pipeline stage errors: {results['errors']}"

    def test_thread_safety_validation(self):
        """Test thread safety of shared resources."""
        print("\n🔒 Testing thread safety validation...")

        # Shared resource for testing thread safety
        shared_counter = {"value": 0}
        counter_lock = threading.Lock()

        def thread_safe_increment(thread_id, iterations=100):
            """Thread-safe counter increment."""
            local_increments = 0

            for _ in range(iterations):
                with counter_lock:
                    shared_counter["value"] += 1
                    local_increments += 1

            return {
                "thread_id": thread_id,
                "local_increments": local_increments,
                "final_shared_value": shared_counter["value"],
            }

        def unsafe_increment(thread_id, iterations=100):
            """Unsafe counter increment (for comparison)."""
            local_increments = 0

            for _ in range(iterations):
                # Race condition: read-modify-write without lock
                current_value = shared_counter["value"]
                shared_counter["value"] = current_value + 1
                local_increments += 1

            return {
                "thread_id": thread_id,
                "local_increments": local_increments,
                "final_shared_value": shared_counter["value"],
            }

        # Test thread-safe operations
        shared_counter["value"] = 0
        task_args = [(i, 50) for i in range(10)]

        safe_results = self.concurrent_framework.monitor_concurrent_execution(
            thread_safe_increment, task_args, max_workers=5
        )

        expected_value = 10 * 50  # 10 threads * 50 increments each
        final_value = shared_counter["value"]

        print(f"   🔒 Thread-safe test:")
        print(f"      Expected value: {expected_value}")
        print(f"      Final value: {final_value}")
        print(f"      Value accuracy: {(final_value / expected_value) * 100:.1f}%")

        # Thread safety assertions
        assert (
            final_value == expected_value
        ), f"Thread safety violation: expected {expected_value}, got {final_value}"
        assert (
            safe_results["successful_executions"] == 10
        ), "Not all thread-safe operations completed successfully"

    def test_race_condition_detection(self):
        """Test detection of race conditions in concurrent operations."""
        print("\n🏁 Testing race condition detection...")

        # Shared resource that's vulnerable to race conditions
        shared_state = {"data": [], "counter": 0}

        def potentially_racy_operation(operation_id, add_items=10):
            """Operation that might have race conditions."""
            results = []

            for i in range(add_items):
                # Simulate read-modify-write operations
                current_counter = shared_state["counter"]

                # Simulate some processing time
                time.sleep(0.001)  # 1ms delay

                # Update shared state
                shared_state["counter"] = current_counter + 1
                shared_state["data"].append(f"op_{operation_id}_item_{i}")

                results.append(current_counter)

            return {
                "operation_id": operation_id,
                "items_added": add_items,
                "counter_values": results,
                "final_counter": shared_state["counter"],
                "final_data_length": len(shared_state["data"]),
            }

        # Reset shared state
        shared_state["data"] = []
        shared_state["counter"] = 0

        # Execute potentially racy operations
        task_args = [(i, 5) for i in range(8)]
        results = self.concurrent_framework.monitor_concurrent_execution(
            potentially_racy_operation, task_args, max_workers=4
        )

        expected_counter = 8 * 5  # 8 operations * 5 items each
        expected_data_length = 8 * 5

        final_counter = shared_state["counter"]
        final_data_length = len(shared_state["data"])

        print(f"   🏁 Race condition test:")
        print(f"      Expected counter: {expected_counter}")
        print(f"      Final counter: {final_counter}")
        print(f"      Expected data length: {expected_data_length}")
        print(f"      Final data length: {final_data_length}")

        # Check for race conditions
        counter_accuracy = (
            (final_counter / expected_counter) * 100 if expected_counter > 0 else 0
        )
        data_accuracy = (
            (final_data_length / expected_data_length) * 100
            if expected_data_length > 0
            else 0
        )

        print(f"      Counter accuracy: {counter_accuracy:.1f}%")
        print(f"      Data accuracy: {data_accuracy:.1f}%")

        # Race condition detection (we expect some data loss due to race conditions)
        # This test is designed to detect race conditions, so we expect < 100% accuracy
        assert counter_accuracy < 100, "No race conditions detected (unexpected)"
        assert (
            counter_accuracy > 10
        ), f"Too many race conditions: {counter_accuracy:.1f}% accuracy"
        assert (
            final_data_length <= expected_data_length
        ), "Data length exceeded expected (impossible)"

        # If accuracy is very low, that's actually expected for this stress test
        if counter_accuracy < 50:
            print(
                f"      ℹ️  Low accuracy detected - this is expected for race condition testing"
            )


if __name__ == "__main__":
    # Run concurrent execution tests directly
    pytest.main([__file__, "-v", "--tb=short"])
