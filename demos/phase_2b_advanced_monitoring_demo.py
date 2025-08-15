#!/usr/bin/env python3
"""
Phase 2B: Advanced Performance Monitoring - Integration Demo
===========================================================

Demonstrates the complete Phase 2B implementation:
- Advanced performance metrics collection
- Resource usage monitoring
- Intelligent alerting system
- Performance trend analysis
- Real-time monitoring display
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from tools.monitoring.advanced_performance_monitor import (
    AdvancedPerformanceMonitor, ResourceSnapshot
)


def demonstrate_phase_2b_features():
    """Comprehensive demonstration of Phase 2B features."""
    print("🚀 Phase 2B: Advanced Performance Monitoring - DEMO")
    print("=" * 60)
    
    # Initialize monitor
    monitor = AdvancedPerformanceMonitor(monitoring_interval=5)
    
    print("✅ Advanced Performance Monitor initialized")
    print(f"   📂 Log directory: {monitor.project_root}/logs/monitoring")
    print(f"   ⏱️ Monitoring interval: {monitor.monitoring_interval} seconds")
    print(f"   🎯 Alert thresholds: CPU>{monitor.alert_manager.thresholds['cpu_critical']}%")
    
    # Feature 1: System Resource Monitoring
    print("\n🖥️ FEATURE 1: System Resource Monitoring")
    print("-" * 40)
    
    snapshot = monitor.collect_system_metrics()
    print(f"   CPU Usage:     {snapshot.cpu_percent:5.1f}%")
    print(f"   Memory Usage:  {snapshot.memory_percent:5.1f}% ({snapshot.memory_mb:,.0f} MB)")
    print(f"   Disk Free:     {snapshot.disk_free_gb:5.1f} GB")
    print(f"   Processes:     {snapshot.process_count}")
    print(f"   Timestamp:     {snapshot.timestamp.strftime('%H:%M:%S')}")
    
    # Feature 2: Pipeline Stage Performance Tracking
    print("\n📊 FEATURE 2: Pipeline Stage Performance Tracking")
    print("-" * 50)
    
    # Simulate realistic pipeline stages with different performance characteristics
    pipeline_stages = [
        {"name": "data_download", "time": 15.2, "records": 5000, "errors": 0},
        {"name": "data_validation", "time": 8.5, "records": 5000, "errors": 12},
        {"name": "data_cleaning", "time": 22.1, "records": 4988, "errors": 3},
        {"name": "feature_engineering", "time": 45.8, "records": 4985, "errors": 0},
        {"name": "model_training", "time": 120.3, "records": 4985, "errors": 1},
        {"name": "prediction_generation", "time": 18.7, "records": 4984, "errors": 0}
    ]
    
    for stage_info in pipeline_stages:
        metric = monitor.collect_pipeline_metrics(
            stage=stage_info["name"],
            processing_time=stage_info["time"],
            records_processed=stage_info["records"],
            errors=stage_info["errors"]
        )
        
        print(f"   {stage_info['name']:20} | "
              f"{stage_info['time']:6.1f}s | "
              f"{metric.throughput:6.1f} rec/s | "
              f"{stage_info['errors']:2d} errors")
        
        time.sleep(0.2)  # Small delay to simulate real processing
    
    # Feature 3: Intelligent Alerting System
    print("\n🚨 FEATURE 3: Intelligent Alerting System")
    print("-" * 40)
    
    # Test with normal metrics first
    normal_alerts = monitor.alert_manager.check_resource_alerts(snapshot)
    if normal_alerts:
        for alert in normal_alerts:
            print(f"   ALERT: {alert.severity} - {alert.message}")
    else:
        print("   ✅ No alerts for current system state (normal operation)")
    
    # Simulate high resource usage to trigger alerts
    print("\n   🧪 Testing alert thresholds with simulated high usage:")
    
    high_usage_snapshot = ResourceSnapshot(
        timestamp=datetime.now(),
        cpu_percent=95.5,  # Above critical threshold
        memory_percent=96.2,  # Above critical threshold
        memory_mb=8192,
        disk_free_gb=2.1,  # Low disk space
        process_count=450
    )
    
    test_alerts = monitor.alert_manager.check_resource_alerts(high_usage_snapshot)
    for alert in test_alerts:
        print(f"   🚨 {alert.severity}: {alert.message}")
        print(f"      💡 Recommended Action: {alert.recommended_action}")
    
    # Feature 4: Performance Trend Analysis
    print("\n📈 FEATURE 4: Performance Trend Analysis")
    print("-" * 40)
    
    # Simulate additional metrics to have enough data for trends
    for i in range(5):
        for stage_info in pipeline_stages[:3]:  # Just first 3 stages for trend demo
            # Add some variation to simulate real performance changes
            time_variation = stage_info["time"] * (0.9 + (i * 0.05))
            
            monitor.collect_pipeline_metrics(
                stage=stage_info["name"],
                processing_time=time_variation,
                records_processed=stage_info["records"],
                errors=stage_info["errors"]
            )
    
    # Analyze trends for each stage
    for stage_name in ["data_download", "data_validation", "data_cleaning"]:
        analysis = monitor.analyze_performance_trends(stage_name, lookback_hours=1)
        
        if 'error' not in analysis:
            print(f"\n   📊 {stage_name.upper()} ANALYSIS:")
            print(f"      Metrics Collected: {analysis['metric_count']}")
            print(f"      Avg Processing Time: {analysis['processing_time']['mean']:.2f}s")
            print(f"      Time Range: {analysis['processing_time']['min']:.2f}s - {analysis['processing_time']['max']:.2f}s")
            print(f"      Avg Throughput: {analysis['throughput']['mean']:.1f} records/sec")
    
    # Feature 5: Performance Baseline Detection
    print("\n🎯 FEATURE 5: Performance Baseline Detection")
    print("-" * 40)
    
    print("   Baseline Performance (Best Performance Recorded):")
    for stage, baseline in monitor.stage_baselines.items():
        print(f"      {stage:20} | {baseline.processing_time:6.2f}s | {baseline.throughput:6.1f} rec/s")
    
    # Feature 6: Performance Report Generation
    print("\n📄 FEATURE 6: Performance Report Generation")
    print("-" * 40)
    
    report = monitor.generate_performance_report()
    print("   📋 Generated comprehensive performance report:")
    
    # Show key sections of the report
    report_lines = report.split('\n')
    for line in report_lines[:20]:  # Show first 20 lines
        print(f"      {line}")
    
    if len(report_lines) > 20:
        print(f"      ... ({len(report_lines) - 20} more lines)")
    
    # Feature 7: Monitoring Statistics Summary
    print("\n📊 FEATURE 7: Monitoring Statistics Summary")
    print("-" * 40)
    
    print(f"   Total Metrics Collected:     {len(monitor.metrics_history)}")
    print(f"   Resource Snapshots:          {len(monitor.resource_history)}")
    print(f"   Pipeline Stages Monitored:   {len(monitor.stage_timings)}")
    print(f"   Performance Baselines Set:   {len(monitor.stage_baselines)}")
    print(f"   Total Alerts Generated:      {len(monitor.alert_manager.alert_history)}")
    print(f"   Alert Types in Cooldown:     {len(monitor.alert_manager.alert_cooldown)}")
    
    # Phase 2B Completion Summary
    print("\n" + "=" * 60)
    print("🎉 PHASE 2B: ADVANCED PERFORMANCE MONITORING - COMPLETE")
    print("=" * 60)
    
    features_completed = [
        "✅ Real-time system resource monitoring (CPU, Memory, Disk)",
        "✅ Pipeline stage-level performance tracking",
        "✅ Intelligent alerting with configurable thresholds",
        "✅ Performance degradation detection (20% threshold)",
        "✅ Performance trend analysis and statistics",
        "✅ Automatic baseline detection and comparison",
        "✅ Comprehensive performance reporting",
        "✅ Alert cooldown and deduplication system",
        "✅ Resource utilization alerts (CPU >90%, Memory >95%)",
        "✅ Historical performance data retention"
    ]
    
    for feature in features_completed:
        print(f"   {feature}")
    
    print(f"\n🚀 ACHIEVEMENTS:")
    print(f"   • {len(monitor.metrics_history)} performance metrics collected")
    print(f"   • {len(monitor.stage_timings)} pipeline stages monitored")
    print(f"   • {len(monitor.alert_manager.alert_history)} intelligent alerts generated")
    print(f"   • Performance monitoring system ready for production use")
    
    print("\n🎯 NEXT STEPS:")
    print("   → Phase 2C: Data Quality Validation (4-5 hours)")
    print("   → Integration with existing pipeline systems")
    print("   → Dashboard deployment for real-time monitoring")


def demo_live_monitoring():
    """Brief demo of live monitoring display."""
    print("\n" + "=" * 60)
    print("🔴 BONUS: Live Monitoring Display Demo (5 seconds)")
    print("=" * 60)
    print("Press Ctrl+C to stop...")
    
    monitor = AdvancedPerformanceMonitor(monitoring_interval=1)
    
    # Add some sample data
    monitor.collect_pipeline_metrics("demo_stage", 5.2, 1000, 0)
    
    try:
        from rich.live import Live
        
        with Live(monitor.create_monitoring_display(), refresh_per_second=1) as live:
            for i in range(5):  # Run for 5 seconds
                snapshot = monitor.collect_system_metrics()
                monitor.resource_history.append(snapshot)
                live.update(monitor.create_monitoring_display())
                time.sleep(1)
                
        print("\n✅ Live monitoring display demo complete!")
        
    except ImportError:
        print("⚠️ Rich library not available for live display demo")
    except Exception as e:
        print(f"⚠️ Live display demo error: {e}")


if __name__ == "__main__":
    demonstrate_phase_2b_features()
    
    # Optional live demo
    try:
        demo_live_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n⚠️ Live demo error: {e}")
    
    print("\n🏁 Phase 2B Advanced Performance Monitoring Demo Complete!")
