#!/usr/bin/env python3
"""
Performance Benchmark Suite - Phase 3 Priority 3
Comprehensive benchmarking and performance validation for the pipeline

Author: AI Assistant
Date: August 12, 2025
"""

import asyncio
import json
import statistics
import time
from pathlib import Path
from typing import Dict, List, Tuple
from unittest.mock import Mock, patch
import pytest

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from daily_pipeline_orchestrator import DailyPipelineOrchestrator


class PerformanceBenchmark:
    """Performance benchmarking framework."""
    
    def __init__(self):
        self.benchmarks = {}
        self.baseline_metrics = {
            'pipeline_startup': 0.1,  # 100ms
            'database_connection': 0.05,  # 50ms
            'data_processing_per_mb': 1.0,  # 1 second per MB
            'memory_efficiency': 0.8,  # 80% efficiency
            'cpu_efficiency': 0.7,  # 70% efficiency
        }
    
    def run_benchmark(self, name: str, func, *args, iterations: int = 5, 
                     **kwargs) -> Dict:
        """Run a performance benchmark with multiple iterations."""
        results = {
            'name': name,
            'iterations': iterations,
            'execution_times': [],
            'results': [],
            'errors': [],
            'timestamp': time.time()
        }
        
        print(f"\n🏆 Running benchmark: {name} ({iterations} iterations)")
        
        for i in range(iterations):
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                
                execution_time = end_time - start_time
                results['execution_times'].append(execution_time)
                results['results'].append(result)
                
                print(f"   ⚡ Iteration {i+1}: {execution_time:.4f}s")
                
            except Exception as e:
                error_info = {'iteration': i, 'error': str(e)}
                results['errors'].append(error_info)
                print(f"   ❌ Iteration {i+1}: Error - {str(e)}")
        
        # Calculate statistics
        if results['execution_times']:
            results['statistics'] = {
                'min': min(results['execution_times']),
                'max': max(results['execution_times']),
                'mean': statistics.mean(results['execution_times']),
                'median': statistics.median(results['execution_times']),
                'stdev': (statistics.stdev(results['execution_times']) 
                         if len(results['execution_times']) > 1 else 0),
                'success_rate': len(results['execution_times']) / iterations
            }
        else:
            results['statistics'] = {'success_rate': 0}
        
        self.benchmarks[name] = results
        return results
    
    def run_async_benchmark(self, name: str, async_func, *args, 
                           iterations: int = 5, **kwargs) -> Dict:
        """Run an async performance benchmark."""
        async def async_wrapper():
            return await async_func(*args, **kwargs)
        
        def sync_wrapper():
            return asyncio.run(async_wrapper())
        
        return self.run_benchmark(name, sync_wrapper, iterations=iterations)
    
    def compare_to_baseline(self, benchmark_name: str, 
                           baseline_key: str) -> Dict:
        """Compare benchmark results to baseline metrics."""
        if benchmark_name not in self.benchmarks:
            return {'error': f'Benchmark {benchmark_name} not found'}
        
        if baseline_key not in self.baseline_metrics:
            return {'error': f'Baseline {baseline_key} not found'}
        
        benchmark = self.benchmarks[benchmark_name]
        baseline = self.baseline_metrics[baseline_key]
        
        if 'statistics' not in benchmark or 'mean' not in benchmark['statistics']:
            return {'error': 'Benchmark statistics not available'}
        
        actual_mean = benchmark['statistics']['mean']
        comparison = {
            'benchmark_mean': actual_mean,
            'baseline': baseline,
            'ratio': actual_mean / baseline if baseline > 0 else float('inf'),
            'improvement': ((baseline - actual_mean) / baseline * 100 
                           if baseline > 0 else 0),
            'passes_baseline': actual_mean <= baseline
        }
        
        return comparison
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive performance report."""
        report = {
            'timestamp': time.time(),
            'total_benchmarks': len(self.benchmarks),
            'benchmarks': {},
            'summary': {
                'total_iterations': 0,
                'total_errors': 0,
                'average_success_rate': 0,
                'baseline_comparisons': {}
            }
        }
        
        total_success_rate = 0
        valid_benchmarks = 0
        
        for name, benchmark in self.benchmarks.items():
            report['benchmarks'][name] = benchmark
            report['summary']['total_iterations'] += benchmark['iterations']
            report['summary']['total_errors'] += len(benchmark['errors'])
            
            if 'statistics' in benchmark and 'success_rate' in benchmark['statistics']:
                total_success_rate += benchmark['statistics']['success_rate']
                valid_benchmarks += 1
        
        if valid_benchmarks > 0:
            report['summary']['average_success_rate'] = total_success_rate / valid_benchmarks
        
        return report


class TestPerformanceBenchmarks:
    """Performance benchmark test suite."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.benchmark = PerformanceBenchmark()
        self.orchestrator = None
    
    def teardown_method(self):
        """Cleanup after each test method."""
        pass
    
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
        
        with patch('daily_pipeline_orchestrator.create_config_manager', 
                  return_value=Mock(return_value=mock_manager_instance)):
            with patch('psycopg2.pool.ThreadedConnectionPool'):
                return DailyPipelineOrchestrator()
    
    def test_orchestrator_startup_benchmark(self):
        """Benchmark orchestrator startup performance."""
        def startup_benchmark():
            orchestrator = self.create_orchestrator()
            return {'status': 'initialized', 'orchestrator_id': id(orchestrator)}
        
        results = self.benchmark.run_benchmark(
            'orchestrator_startup',
            startup_benchmark,
            iterations=10
        )
        
        # Analyze results
        stats = results['statistics']
        print(f"\n📊 Startup Benchmark Results:")
        print(f"   ⚡ Mean time: {stats['mean']:.4f}s")
        print(f"   📉 Min time: {stats['min']:.4f}s")
        print(f"   📈 Max time: {stats['max']:.4f}s")
        print(f"   📊 Std dev: {stats['stdev']:.4f}s")
        print(f"   ✅ Success rate: {stats['success_rate']:.1%}")
        
        # Compare to baseline
        comparison = self.benchmark.compare_to_baseline(
            'orchestrator_startup', 
            'pipeline_startup'
        )
        
        print(f"   🎯 Baseline comparison:")
        print(f"      Target: {comparison['baseline']:.4f}s")
        print(f"      Actual: {comparison['benchmark_mean']:.4f}s")
        print(f"      Ratio: {comparison['ratio']:.2f}x")
        print(f"      Improvement: {comparison['improvement']:+.1f}%")
        
        # Performance assertions
        assert stats['success_rate'] >= 0.9, f"Low success rate: {stats['success_rate']:.1%}"
        assert stats['mean'] < 0.15, f"Average startup too slow: {stats['mean']:.4f}s"
        assert comparison['passes_baseline'], \
            f"Startup time {stats['mean']:.4f}s exceeds baseline {comparison['baseline']:.4f}s"
    
    def test_database_connection_benchmark(self):
        """Benchmark database connection performance."""
        orchestrator = self.create_orchestrator()
        
        def connection_benchmark():
            start_time = time.time()
            conn = asyncio.run(orchestrator.get_db_connection())
            connection_time = time.time() - start_time
            
            return {
                'connection_time': connection_time,
                'connection_status': 'connected' if conn else 'failed'
            }
        
        results = self.benchmark.run_benchmark(
            'database_connection',
            connection_benchmark,
            iterations=15
        )
        
        # Analyze results
        stats = results['statistics']
        print(f"\n🔗 Database Connection Benchmark Results:")
        print(f"   ⚡ Mean time: {stats['mean']:.4f}s")
        print(f"   📉 Min time: {stats['min']:.4f}s")
        print(f"   📈 Max time: {stats['max']:.4f}s")
        print(f"   📊 Std dev: {stats['stdev']:.4f}s")
        print(f"   ✅ Success rate: {stats['success_rate']:.1%}")
        
        # Compare to baseline
        comparison = self.benchmark.compare_to_baseline(
            'database_connection', 
            'database_connection'
        )
        
        print(f"   🎯 Baseline comparison:")
        print(f"      Target: {comparison['baseline']:.4f}s")
        print(f"      Actual: {comparison['benchmark_mean']:.4f}s")
        print(f"      Passes: {'✅' if comparison['passes_baseline'] else '❌'}")
        
        # Performance assertions
        assert stats['success_rate'] >= 0.9, f"Low connection success: {stats['success_rate']:.1%}"
        assert stats['mean'] < 0.1, f"Average connection too slow: {stats['mean']:.4f}s"
        assert stats['max'] < 0.2, f"Maximum connection too slow: {stats['max']:.4f}s"
    
    def test_data_processing_benchmark(self):
        """Benchmark data processing performance."""
        def data_processing_benchmark(data_size_mb=1):
            # Simulate data processing
            data_size_bytes = int(data_size_mb * 1024 * 1024)
            test_data = 'x' * data_size_bytes
            
            start_time = time.time()
            
            # Simulate processing operations
            processed_data = []
            chunk_size = 1024
            for i in range(0, len(test_data), chunk_size):
                chunk = test_data[i:i+chunk_size]
                processed_chunk = chunk.upper()  # Simple transformation
                processed_data.append(len(processed_chunk))
            
            processing_time = time.time() - start_time
            
            return {
                'data_size_mb': data_size_mb,
                'processing_time': processing_time,
                'throughput_mb_per_sec': data_size_mb / processing_time if processing_time > 0 else 0,
                'chunks_processed': len(processed_data)
            }
        
        # Test with different data sizes
        for size_mb in [0.1, 0.5, 1.0]:
            benchmark_name = f'data_processing_{size_mb}mb'
            
            results = self.benchmark.run_benchmark(
                benchmark_name,
                data_processing_benchmark,
                data_size_mb=size_mb,
                iterations=5
            )
            
            # Analyze results
            stats = results['statistics']
            sample_result = results['results'][0] if results['results'] else {}
            
            print(f"\n📊 Data Processing Benchmark ({size_mb}MB):")
            print(f"   ⚡ Mean time: {stats['mean']:.4f}s")
            print(f"   🚀 Throughput: {sample_result.get('throughput_mb_per_sec', 0):.2f} MB/s")
            print(f"   ✅ Success rate: {stats['success_rate']:.1%}")
            
            # Performance assertions for different data sizes
            max_time = size_mb * 2.0  # Allow 2 seconds per MB
            assert stats['mean'] < max_time, \
                f"Processing {size_mb}MB took {stats['mean']:.4f}s (limit: {max_time}s)"
            assert sample_result.get('throughput_mb_per_sec', 0) > 0.5, \
                f"Throughput {sample_result.get('throughput_mb_per_sec', 0):.2f} MB/s too low"
    
    def test_concurrent_operations_benchmark(self):
        """Benchmark concurrent operations performance."""
        orchestrator = self.create_orchestrator()
        
        def concurrent_operations_benchmark(num_operations=10):
            import concurrent.futures
            
            def single_operation(op_id):
                # Simulate mixed operations
                try:
                    conn = asyncio.run(orchestrator.get_db_connection())
                    
                    # Simulate some processing
                    data = [f"item_{i}" for i in range(100)]
                    processed = [item.upper() for item in data]
                    
                    return {
                        'operation_id': op_id,
                        'status': 'success',
                        'items_processed': len(processed)
                    }
                except Exception as e:
                    return {
                        'operation_id': op_id,
                        'status': 'error',
                        'error': str(e)
                    }
            
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(single_operation, i) 
                          for i in range(num_operations)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
            total_time = time.time() - start_time
            
            successful_ops = sum(1 for r in results if r.get('status') == 'success')
            
            return {
                'num_operations': num_operations,
                'total_time': total_time,
                'successful_operations': successful_ops,
                'operations_per_second': num_operations / total_time if total_time > 0 else 0,
                'success_rate': successful_ops / num_operations if num_operations > 0 else 0
            }
        
        results = self.benchmark.run_benchmark(
            'concurrent_operations',
            concurrent_operations_benchmark,
            num_operations=20,
            iterations=3
        )
        
        # Analyze results
        stats = results['statistics']
        sample_result = results['results'][0] if results['results'] else {}
        
        print(f"\n🔄 Concurrent Operations Benchmark:")
        print(f"   ⚡ Mean time: {stats['mean']:.4f}s")
        print(f"   🚀 Operations/sec: {sample_result.get('operations_per_second', 0):.2f}")
        print(f"   ✅ Success rate: {sample_result.get('success_rate', 0):.1%}")
        print(f"   📊 Benchmark success: {stats['success_rate']:.1%}")
        
        # Performance assertions
        assert stats['success_rate'] >= 0.8, f"Low benchmark success: {stats['success_rate']:.1%}"
        assert sample_result.get('operations_per_second', 0) > 5, \
            f"Operations per second {sample_result.get('operations_per_second', 0):.2f} too low"
        assert sample_result.get('success_rate', 0) > 0.8, \
            f"Operation success rate {sample_result.get('success_rate', 0):.1%} too low"
    
    def test_memory_efficiency_benchmark(self):
        """Benchmark memory efficiency during operations."""
        import psutil
        
        def memory_efficiency_benchmark():
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Simulate memory-intensive operations
            data_sets = []
            for i in range(10):
                large_dataset = [f"data_item_{j}_{i}" for j in range(10000)]
                data_sets.append(large_dataset)
            
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Cleanup
            del data_sets
            import gc
            gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            memory_used = peak_memory - initial_memory
            memory_recovered = peak_memory - final_memory
            efficiency = memory_recovered / memory_used if memory_used > 0 else 1.0
            
            return {
                'initial_memory_mb': initial_memory,
                'peak_memory_mb': peak_memory,
                'final_memory_mb': final_memory,
                'memory_used_mb': memory_used,
                'memory_recovered_mb': memory_recovered,
                'efficiency_ratio': efficiency
            }
        
        results = self.benchmark.run_benchmark(
            'memory_efficiency',
            memory_efficiency_benchmark,
            iterations=3
        )
        
        # Analyze results
        stats = results['statistics']
        sample_result = results['results'][0] if results['results'] else {}
        
        print(f"\n💾 Memory Efficiency Benchmark:")
        print(f"   📊 Memory used: {sample_result.get('memory_used_mb', 0):.1f}MB")
        print(f"   🔄 Memory recovered: {sample_result.get('memory_recovered_mb', 0):.1f}MB")
        print(f"   ⚡ Efficiency ratio: {sample_result.get('efficiency_ratio', 0):.2f}")
        print(f"   ✅ Success rate: {stats['success_rate']:.1%}")
        
        # Memory efficiency assertions
        assert stats['success_rate'] >= 0.8, f"Low benchmark success: {stats['success_rate']:.1%}"
        assert sample_result.get('efficiency_ratio', 0) > 0.3, \
            f"Memory efficiency {sample_result.get('efficiency_ratio', 0):.2f} too low"
        assert sample_result.get('memory_used_mb', 0) < 100, \
            f"Memory usage {sample_result.get('memory_used_mb', 0):.1f}MB too high"
    
    def test_generate_performance_report(self):
        """Generate and validate comprehensive performance report."""
        # Ensure we have some benchmarks to report on
        if not self.benchmark.benchmarks:
            # Run a quick benchmark to have data
            def simple_benchmark():
                time.sleep(0.01)
                return {'status': 'completed'}
            
            self.benchmark.run_benchmark('test_benchmark', simple_benchmark, iterations=3)
        
        # Generate report
        report = self.benchmark.generate_report()
        
        print(f"\n📋 Performance Report Generated:")
        print(f"   📊 Total benchmarks: {report['total_benchmarks']}")
        print(f"   🔢 Total iterations: {report['summary']['total_iterations']}")
        print(f"   ❌ Total errors: {report['summary']['total_errors']}")
        print(f"   ✅ Average success rate: {report['summary']['average_success_rate']:.1%}")
        
        # Save report to file for analysis
        report_file = Path(__file__).parent / "performance_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"   💾 Report saved to: {report_file}")
        
        # Report validation assertions
        assert report['total_benchmarks'] > 0, "No benchmarks in report"
        assert report['summary']['average_success_rate'] >= 0.7, \
            f"Overall success rate too low: {report['summary']['average_success_rate']:.1%}"
        assert report_file.exists(), "Performance report file not created"


if __name__ == "__main__":
    # Run performance benchmark tests directly
    pytest.main([__file__, "-v", "--tb=short"])
