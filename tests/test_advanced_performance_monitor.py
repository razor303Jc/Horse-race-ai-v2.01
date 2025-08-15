#!/usr/bin/env python3
"""
Test script for Advanced Performance Monitor
"""

import time
from datetime import datetime

from tools.monitoring.advanced_performance_monitor import AdvancedPerformanceMonitor


def test_performance_monitor():
    """Test the advanced performance monitor functionality."""
    print("🧪 Testing Advanced Performance Monitor...")

    # Create monitor instance
    monitor = AdvancedPerformanceMonitor(monitoring_interval=10)

    # Test 1: Collect system metrics
    print("\n1. Testing system metrics collection...")
    snapshot = monitor.collect_system_metrics()
    print(f"   ✅ CPU: {snapshot.cpu_percent:.1f}%")
    print(f"   ✅ Memory: {snapshot.memory_percent:.1f}% ({snapshot.memory_mb:.0f} MB)")
    print(f"   ✅ Disk Free: {snapshot.disk_free_gb:.1f} GB")
    print(f"   ✅ Processes: {snapshot.process_count}")

    # Test 2: Simulate pipeline metrics
    print("\n2. Testing pipeline metrics collection...")

    # Simulate some pipeline stages
    stages = ["data_download", "data_cleaning", "feature_engineering", "model_training"]

    for i, stage in enumerate(stages):
        processing_time = 2.5 + (i * 0.5)  # Increasing processing time
        records_processed = 1000 - (i * 100)  # Decreasing throughput
        errors = i  # Increasing errors

        metric = monitor.collect_pipeline_metrics(
            stage=stage,
            processing_time=processing_time,
            records_processed=records_processed,
            errors=errors,
        )

        print(
            f"   ✅ {stage}: {processing_time:.1f}s, "
            f"{metric.throughput:.1f} rec/s, {errors} errors"
        )

        time.sleep(0.5)  # Small delay between stages

    # Test 3: Check alerting system
    print("\n3. Testing alerting system...")

    # Create a snapshot that should trigger alerts (high CPU)
    from tools.monitoring.advanced_performance_monitor import ResourceSnapshot

    high_cpu_snapshot = ResourceSnapshot(
        timestamp=datetime.now(),
        cpu_percent=95.0,  # Should trigger critical alert
        memory_percent=60.0,
        memory_mb=4096,
        disk_free_gb=50.0,
        process_count=200,
    )

    alerts = monitor.alert_manager.check_resource_alerts(high_cpu_snapshot)
    for alert in alerts:
        print(f"   🚨 ALERT: {alert.severity} - {alert.message}")
        print(f"      Action: {alert.recommended_action}")

    if not alerts:
        print("   ✅ No alerts generated (thresholds not exceeded)")

    # Test 4: Performance trend analysis
    print("\n4. Testing performance trend analysis...")

    if monitor.stage_timings:
        for stage in list(monitor.stage_timings.keys())[:2]:  # Analyze first 2 stages
            analysis = monitor.analyze_performance_trends(stage, lookback_hours=1)
            if "error" not in analysis:
                print(f"   ✅ {stage} analysis:")
                print(f"      - Metrics: {analysis['metric_count']}")
                print(f"      - Avg time: {analysis['processing_time']['mean']:.2f}s")
                print(
                    f"      - Avg throughput: {analysis['throughput']['mean']:.1f} rec/s"
                )
            else:
                print(f"   ⚠️ {stage}: {analysis['error']}")

    # Test 5: Generate performance report
    print("\n5. Testing performance report generation...")
    report = monitor.generate_performance_report()
    print("   ✅ Report generated:")
    print("   " + "\n   ".join(report.split("\n")[:15]))  # Show first 15 lines

    print(f"\n🎉 Performance Monitor Test Complete!")
    print(f"   • Metrics collected: {len(monitor.metrics_history)}")
    print(f"   • Resource snapshots: {len(monitor.resource_history)}")
    print(f"   • Stages monitored: {len(monitor.stage_timings)}")
    print(f"   • Alerts generated: {len(monitor.alert_manager.alert_history)}")


if __name__ == "__main__":
    test_performance_monitor()
