#!/usr/bin/env python3
"""
Performance Test Configuration - Phase 3 Priority 3
Central configuration for performance testing framework

Author: AI Assistant
Date: August 12, 2025
"""

import os
from pathlib import Path

# Performance Test Configuration
PERFORMANCE_CONFIG = {
    # Test execution settings
    "execution": {
        "default_iterations": 5,
        "timeout_seconds": 30,
        "parallel_workers": 5,
        "retry_attempts": 3,
    },
    # Performance thresholds and baselines
    "thresholds": {
        "startup_time_max": 0.15,  # 150ms maximum startup
        "database_connection_max": 0.1,  # 100ms maximum connection
        "memory_usage_max_mb": 200,  # 200MB maximum memory
        "cpu_usage_max_percent": 80,  # 80% maximum CPU
        "throughput_min_mb_per_sec": 0.5,  # 0.5 MB/s minimum throughput
        "success_rate_min": 0.8,  # 80% minimum success rate
        "memory_efficiency_min": 0.6,  # 60% minimum memory efficiency
    },
    # Load testing parameters
    "load_testing": {
        "small_dataset_races": 100,
        "medium_dataset_races": 500,
        "large_dataset_races": 1000,
        "horses_per_race": 12,
        "concurrent_connections": 10,
        "stress_test_duration": 60,  # seconds
    },
    # Concurrent execution settings
    "concurrency": {
        "max_workers": 8,
        "max_async_concurrency": 10,
        "thread_safety_iterations": 100,
        "race_condition_operations": 50,
    },
    # Resource monitoring settings
    "monitoring": {
        "sampling_interval": 0.1,  # 100ms intervals
        "monitoring_duration": 5.0,  # 5 seconds default
        "memory_leak_cycles": 5,
        "cpu_load_duration": 0.5,  # 500ms CPU intensive tasks
    },
    # Benchmark configuration
    "benchmarks": {
        "startup_iterations": 10,
        "connection_iterations": 15,
        "processing_iterations": 5,
        "concurrent_operations": 20,
        "memory_test_iterations": 3,
    },
}

# Test data configurations
TEST_DATA_CONFIG = {
    "csv_headers": [
        "race_date",
        "course",
        "race_time",
        "race_name",
        "race_class",
        "horse_name",
        "jockey",
        "trainer",
        "weight",
        "odds",
        "position",
        "rating",
    ],
    "sample_courses": [
        "Cheltenham",
        "Aintree",
        "Ascot",
        "Newmarket",
        "York",
        "Goodwood",
        "Epsom",
        "Doncaster",
        "Chester",
        "Bath",
    ],
    "sample_classes": [
        "Class 1",
        "Class 2",
        "Class 3",
        "Class 4",
        "Class 5",
        "Listed",
        "Group 1",
        "Group 2",
        "Group 3",
        "Handicap",
    ],
}

# Performance report templates
REPORT_TEMPLATES = {
    "summary": {
        "title": "Performance Test Summary Report",
        "sections": [
            "Executive Summary",
            "Load Testing Results",
            "Concurrent Execution Analysis",
            "Resource Usage Metrics",
            "Performance Benchmarks",
            "Recommendations",
        ],
    },
    "detailed": {
        "title": "Detailed Performance Analysis Report",
        "sections": [
            "Test Environment",
            "Methodology",
            "Load Testing Deep Dive",
            "Concurrency Analysis",
            "Resource Monitoring",
            "Benchmark Results",
            "Performance Trends",
            "Issue Analysis",
            "Optimization Recommendations",
            "Appendices",
        ],
    },
}

# Environment settings
ENVIRONMENT_CONFIG = {
    "test_database": {
        "host": "localhost",
        "port": 5432,
        "database": "test_performance_db",
        "user": "test_user",
        "password": "test_pass",
        "pool_size": 20,
    },
    "paths": {
        "test_data_dir": Path(__file__).parent / "test_data",
        "reports_dir": Path(__file__).parent / "reports",
        "logs_dir": Path(__file__).parent / "logs",
        "temp_dir": Path(__file__).parent / "temp",
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_rotation": True,
        "max_log_size_mb": 10,
    },
}


# Performance analysis utilities
class PerformanceAnalyzer:
    """Utility class for performance analysis and reporting."""

    @staticmethod
    def analyze_trend(values: list) -> dict:
        """Analyze performance trend from a series of values."""
        if len(values) < 2:
            return {"trend": "insufficient_data"}

        # Calculate linear trend
        x_values = list(range(len(values)))
        mean_x = sum(x_values) / len(x_values)
        mean_y = sum(values) / len(values)

        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, values))
        denominator = sum((x - mean_x) ** 2 for x in x_values)

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        # Determine trend direction
        if abs(slope) < 0.01:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        return {
            "trend": trend,
            "slope": slope,
            "mean": mean_y,
            "variance": sum((v - mean_y) ** 2 for v in values) / len(values),
        }

    @staticmethod
    def calculate_percentiles(values: list) -> dict:
        """Calculate percentile statistics for performance values."""
        if not values:
            return {}

        sorted_values = sorted(values)
        n = len(sorted_values)

        def percentile(p):
            index = (p / 100) * (n - 1)
            if index.is_integer():
                return sorted_values[int(index)]
            else:
                lower = sorted_values[int(index)]
                upper = sorted_values[int(index) + 1]
                return lower + (upper - lower) * (index - int(index))

        return {
            "p50": percentile(50),
            "p75": percentile(75),
            "p90": percentile(90),
            "p95": percentile(95),
            "p99": percentile(99),
        }

    @staticmethod
    def assess_performance_grade(
        actual_value: float, threshold: float, lower_is_better: bool = True
    ) -> dict:
        """Assess performance grade based on threshold comparison."""
        if lower_is_better:
            ratio = actual_value / threshold if threshold > 0 else float("inf")
            if ratio <= 0.8:
                grade = "A"
            elif ratio <= 1.0:
                grade = "B"
            elif ratio <= 1.5:
                grade = "C"
            elif ratio <= 2.0:
                grade = "D"
            else:
                grade = "F"
        else:
            ratio = actual_value / threshold if threshold > 0 else 0
            if ratio >= 1.2:
                grade = "A"
            elif ratio >= 1.0:
                grade = "B"
            elif ratio >= 0.8:
                grade = "C"
            elif ratio >= 0.6:
                grade = "D"
            else:
                grade = "F"

        return {
            "grade": grade,
            "ratio": ratio,
            "passes_threshold": (ratio <= 1.0 if lower_is_better else ratio >= 1.0),
        }


# Utility functions
def get_performance_config():
    """Get performance configuration with environment overrides."""
    config = PERFORMANCE_CONFIG.copy()

    # Apply environment variable overrides
    if "PERF_TEST_ITERATIONS" in os.environ:
        config["execution"]["default_iterations"] = int(
            os.environ["PERF_TEST_ITERATIONS"]
        )

    if "PERF_TEST_TIMEOUT" in os.environ:
        config["execution"]["timeout_seconds"] = int(os.environ["PERF_TEST_TIMEOUT"])

    if "PERF_TEST_WORKERS" in os.environ:
        config["execution"]["parallel_workers"] = int(os.environ["PERF_TEST_WORKERS"])

    return config


def setup_performance_environment():
    """Setup performance testing environment directories."""
    for path in ENVIRONMENT_CONFIG["paths"].values():
        path.mkdir(parents=True, exist_ok=True)

    print("✅ Performance testing environment setup complete")
    print(f"   📁 Test data: {ENVIRONMENT_CONFIG['paths']['test_data_dir']}")
    print(f"   📊 Reports: {ENVIRONMENT_CONFIG['paths']['reports_dir']}")
    print(f"   📝 Logs: {ENVIRONMENT_CONFIG['paths']['logs_dir']}")
    print(f"   🗂️  Temp: {ENVIRONMENT_CONFIG['paths']['temp_dir']}")


def validate_performance_environment():
    """Validate performance testing environment."""
    issues = []

    # Check required directories
    for name, path in ENVIRONMENT_CONFIG["paths"].items():
        if not path.exists():
            issues.append(f"Missing directory: {name} ({path})")

    # Check system resources
    import psutil

    available_memory_gb = psutil.virtual_memory().available / (1024**3)
    if available_memory_gb < 1.0:
        issues.append(f"Low available memory: {available_memory_gb:.1f}GB")

    cpu_count = psutil.cpu_count()
    if cpu_count < 2:
        issues.append(f"Low CPU count: {cpu_count}")

    # Check Python packages
    required_packages = ["psutil", "pytest", "asyncio"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            issues.append(f"Missing required package: {package}")

    if issues:
        print("❌ Performance environment validation issues:")
        for issue in issues:
            print(f"   ⚠️  {issue}")
        return False
    else:
        print("✅ Performance environment validation passed")
        return True


if __name__ == "__main__":
    print("🔧 Performance Test Configuration")
    print("=" * 50)

    # Setup environment
    setup_performance_environment()

    # Validate environment
    is_valid = validate_performance_environment()

    # Display configuration summary
    config = get_performance_config()
    print(f"\n📋 Configuration Summary:")
    print(f"   🔄 Default iterations: {config['execution']['default_iterations']}")
    print(f"   ⏱️  Timeout: {config['execution']['timeout_seconds']}s")
    print(f"   👥 Workers: {config['execution']['parallel_workers']}")
    print(
        f"   🎯 Success rate threshold: {config['thresholds']['success_rate_min']:.1%}"
    )
    print(f"   💾 Memory threshold: {config['thresholds']['memory_usage_max_mb']}MB")

    if is_valid:
        print("\n🚀 Ready for performance testing!")
    else:
        print("\n❌ Please resolve validation issues before running tests")
