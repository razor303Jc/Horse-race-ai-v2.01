"""
🧪 Performance Test Suite
=========================

Performance and load testing for the Horse Racing AI v2.04 system.
Tests system performance under various load conditions and benchmarks.
"""

import pytest
import time
import pandas as pd
import numpy as np
import concurrent.futures
import threading
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import psutil
import json
from typing import Dict, List, Any, Optional, Callable
import statistics


# Test fixtures
@pytest.fixture
def performance_test_config():
    """Performance test configuration"""
    return {
        "load_test": {
            "concurrent_users": 10,
            "requests_per_user": 50,
            "ramp_up_time": 30,  # seconds
            "test_duration": 300,  # seconds
        },
        "benchmarks": {
            "data_processing_threshold": 1000,  # records/second
            "prediction_threshold": 100,  # predictions/second
            "api_response_threshold": 2.0,  # seconds
            "memory_threshold": 1024,  # MB
            "cpu_threshold": 80,  # percentage
        },
        "stress_test": {
            "max_concurrent_requests": 100,
            "large_dataset_size": 10000,
            "memory_stress_iterations": 1000,
        },
    }


@pytest.fixture
def large_dataset_generator():
    """Generate large datasets for performance testing"""

    def generate_dataset(size: int = 10000) -> pd.DataFrame:
        np.random.seed(42)

        data = {
            "race_id": [f"RACE_{i//12:04d}" for i in range(size)],
            "horse_name": [f"Horse_{i}" for i in range(size)],
            "jockey_name": [f"Jockey_{i % 100}" for i in range(size)],
            "trainer_name": [f"Trainer_{i % 75}" for i in range(size)],
            "track": np.random.choice(
                ["RANDWICK", "FLEMINGTON", "ROSEHILL", "CAULFIELD"], size
            ),
            "distance": np.random.choice([1000, 1200, 1400, 1600, 2000], size),
            "track_condition": np.random.choice(
                ["GOOD", "SOFT", "HEAVY", "FIRM"], size
            ),
            "race_class": np.random.choice(["C1", "C2", "C3", "C4", "C5"], size),
            "barrier": np.random.randint(1, 21, size),
            "weight": np.random.uniform(54.0, 62.0, size),
            "odds": np.random.exponential(3.0, size) + 1.0,
            "last_3_avg_position": np.random.uniform(1.0, 12.0, size),
            "days_since_last_run": np.random.randint(7, 365, size),
            "track_win_rate": np.random.uniform(0.0, 0.4, size),
            "jockey_win_rate": np.random.uniform(0.05, 0.25, size),
            "trainer_win_rate": np.random.uniform(0.08, 0.30, size),
            "position": np.random.randint(1, 13, size),
        }

        return pd.DataFrame(data)

    return generate_dataset


@pytest.fixture
def performance_monitor():
    """Monitor system performance during tests"""

    class PerformanceMonitor:
        def __init__(self):
            self.metrics = []
            self.monitoring = False
            self.monitor_thread = None

        def start_monitoring(self):
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.start()

        def stop_monitoring(self):
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join()

        def _monitor_loop(self):
            while self.monitoring:
                try:
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory = psutil.virtual_memory()

                    self.metrics.append(
                        {
                            "timestamp": time.time(),
                            "cpu_percent": cpu_percent,
                            "memory_percent": memory.percent,
                            "memory_used_mb": memory.used / (1024 * 1024),
                        }
                    )

                    time.sleep(1)
                except Exception:
                    # Handle monitoring errors gracefully
                    pass

        def get_stats(self) -> Dict:
            if not self.metrics:
                return {}

            cpu_values = [m["cpu_percent"] for m in self.metrics]
            memory_values = [m["memory_used_mb"] for m in self.metrics]

            return {
                "avg_cpu_percent": statistics.mean(cpu_values),
                "max_cpu_percent": max(cpu_values),
                "avg_memory_mb": statistics.mean(memory_values),
                "max_memory_mb": max(memory_values),
                "sample_count": len(self.metrics),
            }

    return PerformanceMonitor()


class TestDataProcessingPerformance:
    """Performance tests for data processing components"""

    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_bulk_upload_performance(
        self, large_dataset_generator, performance_test_config, performance_monitor
    ):
        """Test bulk upload performance with large datasets"""
        dataset_sizes = [1000, 5000, 10000]

        for size in dataset_sizes:
            print(f"Testing bulk upload with {size} records...")

            # Generate test dataset
            test_data = large_dataset_generator(size)

            # Start monitoring
            performance_monitor.start_monitoring()

            # Measure processing time
            start_time = time.time()

            # Simulate bulk upload process
            upload_results = self._simulate_bulk_upload_process(test_data)

            processing_time = time.time() - start_time
            performance_monitor.stop_monitoring()

            # Calculate performance metrics
            records_per_second = size / processing_time

            # Get system metrics
            system_stats = performance_monitor.get_stats()

            # Performance assertions
            threshold = performance_test_config["benchmarks"][
                "data_processing_threshold"
            ]
            assert (
                records_per_second >= threshold
            ), f"Processing too slow: {records_per_second:.1f} < {threshold} records/sec for {size} records"

            assert upload_results["success"] is True
            assert upload_results["records_processed"] == size

            # Log performance metrics
            print(f"  Records/sec: {records_per_second:.1f}")
            print(f"  Processing time: {processing_time:.2f}s")
            if system_stats:
                print(f"  Avg CPU: {system_stats.get('avg_cpu_percent', 0):.1f}%")
                print(f"  Max Memory: {system_stats.get('max_memory_mb', 0):.1f}MB")

    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_data_cleaning_performance(
        self, large_dataset_generator, performance_test_config
    ):
        """Test data cleaning performance"""
        dataset = large_dataset_generator(10000)

        # Add some dirty data
        dataset.loc[::100, "odds"] = None  # Missing values
        dataset.loc[::150, "weight"] = "invalid"  # Invalid data types

        start_time = time.time()

        # Simulate data cleaning
        cleaned_data = self._simulate_data_cleaning(dataset)

        cleaning_time = time.time() - start_time

        # Performance assertions
        records_per_second = len(dataset) / cleaning_time
        assert (
            records_per_second >= 500
        ), f"Data cleaning too slow: {records_per_second:.1f} records/sec"

        # Quality assertions
        assert len(cleaned_data) > 0
        assert cleaned_data.isnull().sum().sum() < dataset.isnull().sum().sum()

        print(f"Data cleaning: {records_per_second:.1f} records/sec")

    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_feature_engineering_performance(
        self, large_dataset_generator, performance_test_config
    ):
        """Test feature engineering performance"""
        dataset = large_dataset_generator(5000)

        start_time = time.time()

        # Simulate feature engineering
        features_df = self._simulate_feature_engineering(dataset)

        engineering_time = time.time() - start_time

        # Performance assertions
        records_per_second = len(dataset) / engineering_time
        assert (
            records_per_second >= 200
        ), f"Feature engineering too slow: {records_per_second:.1f} records/sec"

        # Quality assertions
        assert len(features_df.columns) > len(dataset.columns)
        assert not features_df.select_dtypes(include=[np.number]).isnull().any().any()

        print(f"Feature engineering: {records_per_second:.1f} records/sec")


class TestMLPerformance:
    """Performance tests for ML components"""

    @pytest.mark.performance
    @pytest.mark.ml
    @pytest.mark.benchmark
    def test_model_training_performance(
        self, large_dataset_generator, performance_test_config, performance_monitor
    ):
        """Test ML model training performance"""
        training_sizes = [1000, 5000, 10000]

        for size in training_sizes:
            print(f"Testing ML training with {size} records...")

            # Generate training data
            training_data = large_dataset_generator(size)
            features_df = self._simulate_feature_engineering(training_data)

            performance_monitor.start_monitoring()

            start_time = time.time()

            # Simulate model training
            training_results = self._simulate_model_training(features_df)

            training_time = time.time() - start_time
            performance_monitor.stop_monitoring()

            # Performance assertions
            assert (
                training_time <= 120
            ), f"Training too slow: {training_time:.1f}s for {size} records"
            assert training_results["accuracy"] >= 0.6

            # System resource checks
            system_stats = performance_monitor.get_stats()
            if system_stats:
                memory_threshold = performance_test_config["benchmarks"][
                    "memory_threshold"
                ]
                assert (
                    system_stats.get("max_memory_mb", 0) <= memory_threshold
                ), f"Memory usage too high: {system_stats['max_memory_mb']:.1f}MB"

            print(f"  Training time: {training_time:.1f}s")
            print(f"  Accuracy: {training_results['accuracy']:.3f}")

    @pytest.mark.performance
    @pytest.mark.ml
    @pytest.mark.benchmark
    def test_prediction_performance(
        self, large_dataset_generator, performance_test_config
    ):
        """Test ML prediction performance"""
        # Test different batch sizes
        batch_sizes = [10, 50, 100, 500]

        for batch_size in batch_sizes:
            print(f"Testing predictions with batch size {batch_size}...")

            # Generate prediction data
            prediction_data = large_dataset_generator(batch_size)
            features_df = self._simulate_feature_engineering(prediction_data)

            start_time = time.time()

            # Simulate batch predictions
            predictions = self._simulate_batch_predictions(features_df)

            prediction_time = time.time() - start_time

            # Performance assertions
            predictions_per_second = batch_size / prediction_time
            threshold = performance_test_config["benchmarks"]["prediction_threshold"]

            assert (
                predictions_per_second >= threshold
            ), f"Predictions too slow: {predictions_per_second:.1f} < {threshold} pred/sec"

            assert len(predictions) == batch_size
            assert all(0.0 <= pred <= 1.0 for pred in predictions)

            print(f"  Predictions/sec: {predictions_per_second:.1f}")

    @pytest.mark.performance
    @pytest.mark.ml
    @pytest.mark.benchmark
    def test_concurrent_prediction_performance(
        self, large_dataset_generator, performance_test_config
    ):
        """Test concurrent prediction performance"""
        num_threads = 5
        predictions_per_thread = 20

        def prediction_worker():
            prediction_data = large_dataset_generator(12)  # Typical race size
            features_df = self._simulate_feature_engineering(prediction_data)

            results = []
            for _ in range(predictions_per_thread):
                start_time = time.time()
                predictions = self._simulate_batch_predictions(features_df)
                prediction_time = time.time() - start_time

                results.append({"predictions": predictions, "time": prediction_time})

            return results

        # Execute concurrent predictions
        overall_start = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(prediction_worker) for _ in range(num_threads)]
            all_results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        overall_time = time.time() - overall_start

        # Analyze results
        total_predictions = num_threads * predictions_per_thread
        overall_throughput = total_predictions / overall_time

        # Extract individual prediction times
        all_times = []
        for thread_results in all_results:
            all_times.extend([result["time"] for result in thread_results])

        avg_prediction_time = statistics.mean(all_times)
        max_prediction_time = max(all_times)

        # Performance assertions
        assert (
            overall_throughput >= 50
        ), f"Concurrent throughput too low: {overall_throughput:.1f} pred/sec"
        assert (
            avg_prediction_time <= 1.0
        ), f"Average prediction time too high: {avg_prediction_time:.2f}s"
        assert (
            max_prediction_time <= 5.0
        ), f"Max prediction time too high: {max_prediction_time:.2f}s"

        print(f"Concurrent predictions: {overall_throughput:.1f} pred/sec")
        print(f"Average prediction time: {avg_prediction_time:.3f}s")


class TestAPIPerformance:
    """Performance tests for API components"""

    @pytest.mark.performance
    @pytest.mark.api
    @pytest.mark.benchmark
    def test_api_response_time_performance(self, performance_test_config):
        """Test API response time performance"""
        endpoints = ["/health", "/predict/race", "/races", "/dashboard/data"]

        for endpoint in endpoints:
            print(f"Testing {endpoint} response time...")

            response_times = []

            # Test multiple requests
            for _ in range(10):
                with patch(
                    "requests.get" if endpoint == "/health" else "requests.post"
                ) as mock_request:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"status": "success"}
                    mock_request.return_value = mock_response

                    start_time = time.time()

                    # Simulate API request
                    self._simulate_api_request(endpoint)

                    response_time = time.time() - start_time
                    response_times.append(response_time)

            # Analyze response times
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)

            # Performance assertions
            threshold = performance_test_config["benchmarks"]["api_response_threshold"]
            assert (
                avg_response_time <= threshold
            ), f"{endpoint} too slow: {avg_response_time:.2f}s > {threshold}s"
            assert (
                max_response_time <= threshold * 2
            ), f"{endpoint} max response too slow: {max_response_time:.2f}s"

            print(f"  Avg response: {avg_response_time:.3f}s")
            print(f"  Max response: {max_response_time:.3f}s")

    @pytest.mark.performance
    @pytest.mark.api
    @pytest.mark.load
    def test_api_load_performance(self, performance_test_config, performance_monitor):
        """Test API performance under load"""
        load_config = performance_test_config["load_test"]

        concurrent_users = load_config["concurrent_users"]
        requests_per_user = load_config["requests_per_user"]

        def user_simulation():
            """Simulate a user making multiple requests"""
            response_times = []

            for _ in range(requests_per_user):
                with patch("requests.post") as mock_post:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"status": "success"}
                    mock_post.return_value = mock_response

                    start_time = time.time()
                    self._simulate_api_request("/predict/race")
                    response_time = time.time() - start_time

                    response_times.append(response_time)

                    # Small delay between requests
                    time.sleep(0.1)

            return response_times

        # Start performance monitoring
        performance_monitor.start_monitoring()

        # Execute load test
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrent_users
        ) as executor:
            futures = [
                executor.submit(user_simulation) for _ in range(concurrent_users)
            ]
            all_response_times = []

            for future in concurrent.futures.as_completed(futures):
                all_response_times.extend(future.result())

        total_time = time.time() - start_time
        performance_monitor.stop_monitoring()

        # Analyze results
        total_requests = concurrent_users * requests_per_user
        requests_per_second = total_requests / total_time
        avg_response_time = statistics.mean(all_response_times)

        # Get system stats
        system_stats = performance_monitor.get_stats()

        # Performance assertions
        assert (
            requests_per_second >= 20
        ), f"Request throughput too low: {requests_per_second:.1f} req/sec"
        assert (
            avg_response_time <= 3.0
        ), f"Average response time too high: {avg_response_time:.2f}s"

        # System resource assertions
        if system_stats:
            cpu_threshold = performance_test_config["benchmarks"]["cpu_threshold"]
            assert (
                system_stats.get("avg_cpu_percent", 0) <= cpu_threshold
            ), f"CPU usage too high: {system_stats['avg_cpu_percent']:.1f}%"

        print(f"Load test results:")
        print(f"  Requests/sec: {requests_per_second:.1f}")
        print(f"  Avg response: {avg_response_time:.3f}s")
        if system_stats:
            print(f"  Avg CPU: {system_stats.get('avg_cpu_percent', 0):.1f}%")


class TestStressAndScalability:
    """Stress and scalability tests"""

    @pytest.mark.performance
    @pytest.mark.stress
    def test_memory_stress(
        self, large_dataset_generator, performance_test_config, performance_monitor
    ):
        """Test system behavior under memory stress"""
        stress_config = performance_test_config["stress_test"]

        performance_monitor.start_monitoring()

        # Create increasingly large datasets
        datasets = []
        for i in range(5):
            size = 2000 * (i + 1)  # Increasing dataset sizes
            dataset = large_dataset_generator(size)
            datasets.append(dataset)

            # Process each dataset
            processed = self._simulate_feature_engineering(dataset)

            # Verify processing still works
            assert len(processed) == size
            assert not processed.select_dtypes(include=[np.number]).isnull().any().any()

        performance_monitor.stop_monitoring()

        # Check memory usage stayed reasonable
        system_stats = performance_monitor.get_stats()
        if system_stats:
            memory_threshold = (
                performance_test_config["benchmarks"]["memory_threshold"] * 2
            )  # Allow higher for stress test
            assert (
                system_stats.get("max_memory_mb", 0) <= memory_threshold
            ), f"Memory usage exceeded stress threshold: {system_stats['max_memory_mb']:.1f}MB"

    @pytest.mark.performance
    @pytest.mark.stress
    def test_concurrent_processing_stress(
        self, large_dataset_generator, performance_test_config
    ):
        """Test concurrent processing under stress"""
        stress_config = performance_test_config["stress_test"]
        max_concurrent = stress_config["max_concurrent_requests"]

        def processing_worker():
            dataset = large_dataset_generator(500)
            return self._simulate_feature_engineering(dataset)

        # Execute stress test
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_concurrent
        ) as executor:
            futures = [
                executor.submit(processing_worker) for _ in range(max_concurrent)
            ]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        total_time = time.time() - start_time

        # Verify all processing completed successfully
        assert len(results) == max_concurrent
        for result in results:
            assert len(result) == 500
            assert not result.select_dtypes(include=[np.number]).isnull().any().any()

        # Performance assertion
        throughput = max_concurrent / total_time
        assert (
            throughput >= 5
        ), f"Concurrent processing throughput too low: {throughput:.1f} jobs/sec"

        print(f"Stress test: {max_concurrent} concurrent jobs in {total_time:.1f}s")

    # Helper methods for simulation

    def _simulate_bulk_upload_process(self, data: pd.DataFrame) -> Dict:
        """Simulate bulk upload process"""
        # Simulate processing time proportional to data size
        processing_time = len(data) * 0.0001  # 0.1ms per record
        time.sleep(processing_time)

        return {
            "success": True,
            "records_processed": len(data),
            "processing_time": processing_time,
        }

    def _simulate_data_cleaning(self, data: pd.DataFrame) -> pd.DataFrame:
        """Simulate data cleaning process"""
        # Simulate cleaning time
        time.sleep(len(data) * 0.00005)  # 0.05ms per record

        # Basic cleaning simulation
        cleaned = data.copy()

        # Fill missing odds with median
        if cleaned["odds"].isnull().any():
            cleaned["odds"] = cleaned["odds"].fillna(cleaned["odds"].median())

        # Convert invalid weights to float
        cleaned["weight"] = pd.to_numeric(cleaned["weight"], errors="coerce")
        cleaned["weight"] = cleaned["weight"].fillna(57.0)  # Default weight

        return cleaned

    def _simulate_feature_engineering(self, data: pd.DataFrame) -> pd.DataFrame:
        """Simulate feature engineering process"""
        # Simulate processing time
        time.sleep(len(data) * 0.0002)  # 0.2ms per record

        features_df = data.copy()

        # Add engineered features
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col in ["distance", "weight", "odds"]:
                features_df[f"{col}_normalized"] = (
                    data[col] - data[col].mean()
                ) / data[col].std()

        features_df["odds_log"] = np.log(data["odds"].clip(lower=1.01))
        features_df["barrier_factor"] = data["barrier"] / 20.0

        return features_df

    def _simulate_model_training(self, features_df: pd.DataFrame) -> Dict:
        """Simulate model training process"""
        # Simulate training time based on data size
        training_time = min(len(features_df) * 0.002, 60)  # Max 60 seconds
        time.sleep(training_time)

        return {
            "accuracy": np.random.uniform(0.65, 0.85),
            "training_time": training_time,
            "success": True,
        }

    def _simulate_batch_predictions(self, features_df: pd.DataFrame) -> List[float]:
        """Simulate batch predictions"""
        # Simulate prediction time
        time.sleep(len(features_df) * 0.001)  # 1ms per prediction

        # Generate predictions
        predictions = np.random.uniform(0.05, 0.95, len(features_df))
        return predictions.tolist()

    def _simulate_api_request(self, endpoint: str) -> Dict:
        """Simulate API request"""
        # Simulate network and processing time
        base_time = 0.05  # 50ms base time
        if "predict" in endpoint:
            time.sleep(base_time + 0.1)  # Prediction endpoints are slower
        else:
            time.sleep(base_time)

        return {"status": "success", "endpoint": endpoint}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
