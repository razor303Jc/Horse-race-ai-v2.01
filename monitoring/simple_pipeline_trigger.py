#!/usr/bin/env python3
"""
Simple Pipeline Trigger - Connects file watcher to actual pipeline execution
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Add monitoring to path
sys.path.insert(0, '/home/jc/Documents/Horse-race-ai-v2.03/monitoring')
from script_function_analyzer import ScriptFunctionAnalyzer

class SimplePipelineTrigger:
    """Simple pipeline trigger with analysis"""
    
    def __init__(self):
        self.base_dir = "/home/jc/Documents/Horse-race-ai-v2.03"
        self.analyzer = ScriptFunctionAnalyzer()
        
    def check_data_readiness(self):
        """Check if data is ready for processing"""
        print("🔍 Checking data readiness...")
        
        # Check cards data
        cards_dir = Path(self.base_dir) / "data/daily_downloads/cards_data"
        cards_ready = False
        if cards_dir.exists():
            races = list((cards_dir / "races").glob("*.csv")) if (cards_dir / "races").exists() else []
            horses = list((cards_dir / "horses").glob("*.csv")) if (cards_dir / "horses").exists() else []
            cards_ready = len(races) > 0 and len(horses) > 0
            print(f"�� Cards data: {len(races)} race files, {len(horses)} horse files")
        
        # Check results data  
        results_dir = Path(self.base_dir) / "data/daily_downloads/results_data"
        results_ready = False
        if results_dir.exists():
            records = list((results_dir / "records").glob("*.csv")) if (results_dir / "records").exists() else []
            results_ready = len(records) > 0
            print(f"📁 Results data: {len(records)} record files")
        
        ready = cards_ready and results_ready
        print(f"✅ Data ready for pipeline: {ready}")
        return ready
    
    def run_database_upload(self):
        """Run the database upload script"""
        print("🔄 Running database upload...")
        
        upload_script = os.path.join(self.base_dir, "tools/database/complete_upload.py")
        
        if not os.path.exists(upload_script):
            print(f"❌ Upload script not found: {upload_script}")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, upload_script],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("✅ Database upload completed successfully")
                return True
            else:
                print(f"❌ Database upload failed (exit {result.returncode})")
                if result.stderr:
                    print(f"Error: {result.stderr[-200:]}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Database upload timed out")
            return False
        except Exception as e:
            print(f"💥 Database upload error: {e}")
            return False
    
    def run_complete_pipeline(self):
        """Run the complete pipeline"""
        print("🎯 Starting Complete Pipeline Execution")
        print("=" * 50)
        
        start_time = datetime.now()
        
        # Check data readiness
        if not self.check_data_readiness():
            print("❌ Pipeline aborted: Data not ready")
            return False
        
        # Stage 2: Database upload
        print("\n🚀 Stage 2: Database Upload")
        upload_success = self.run_database_upload()
        
        if upload_success:
            print("\n✅ Pipeline completed successfully!")
            duration = (datetime.now() - start_time).total_seconds()
            print(f"⏱️ Total duration: {duration:.2f} seconds")
            
            # Generate analysis report
            report = self.analyzer.generate_report()
            print(f"📊 Analysis: {report['summary']['total_function_calls']} function calls tracked")
            
            return True
        else:
            print("\n❌ Pipeline failed at database upload stage")
            return False

def main():
    """Main function"""
    trigger = SimplePipelineTrigger()
    success = trigger.run_complete_pipeline()
    return success

if __name__ == "__main__":
    main()
