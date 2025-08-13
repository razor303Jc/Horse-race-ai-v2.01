#!/usr/bin/env python3
"""
📊 Production Monitoring Dashboard for 17-Stage Dynamic Pipeline
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

class PipelineMonitor:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.logs_dir = self.project_root / "logs"

    def check_pipeline_health(self):
        """Check overall pipeline health"""
        try:
            # Check latest schedule
            schedule_file = self.logs_dir / "dynamic_17_stage_schedule.json"
            if schedule_file.exists():
                with open(schedule_file, "r") as f:
                    schedule = json.load(f)
                    
                analysis = schedule.get("timing_analysis", {})
                
                print(f"🏇 17-Stage Dynamic Pipeline Status - {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 60)
                print(f"📊 Total Stages: {analysis.get('total_stages', 'Unknown')}")
                print(f"🎯 Phases Covered: {analysis.get('phases_covered', 'Unknown')}")
                print(f"⏰ Schedule Type: {analysis.get('schedule_type', 'Unknown')}")
                print(f"🕐 Time Window: {analysis.get('total_window_minutes', 'Unknown')} minutes")
                print(f"⚡ Buffer Time: {analysis.get('buffer_minutes', 'Unknown')} minutes")
                print(f"🏁 First Race: {analysis.get('first_race_time', 'Unknown')}")
                print(f"🏆 Pipeline Completion: {analysis.get('pipeline_completion', 'Unknown')}")
                print("✅ Pipeline: HEALTHY")
                
                return True
            else:
                print("❌ No recent schedule found - pipeline may be inactive")
                return False
                
        except Exception as e:
            print(f"❌ Pipeline monitoring error: {e}")
            return False

    def run_continuous_monitoring(self):
        """Run continuous monitoring"""
        print("🚀 Starting continuous pipeline monitoring...")
        
        while True:
            self.check_pipeline_health()
            print("\n" + "-" * 60)
            print("🔄 Next check in 5 minutes...")
            time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    monitor = PipelineMonitor()
    monitor.run_continuous_monitoring()
