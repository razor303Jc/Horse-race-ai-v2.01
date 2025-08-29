#!/usr/bin/env python3
"""
Quick test of the analysis system
"""

import sys
import time
import json
sys.path.insert(0, '/home/jc/Documents/Horse-race-ai-v2.03/monitoring')

from script_function_analyzer import ScriptFunctionAnalyzer

def main():
    print("🧪 Testing Script Function Analysis System")
    print("=" * 50)
    
    # Create analyzer
    analyzer = ScriptFunctionAnalyzer()
    
    @analyzer.track_function
    def download_csv_files(location):
        """Simulate downloading CSV files"""
        print(f"📥 Downloading CSV files from {location}")
        time.sleep(0.1)
        return {"files": 3, "status": "success"}
    
    @analyzer.track_function
    def process_race_data(data):
        """Simulate processing race data"""
        print(f"🏇 Processing {data['files']} race files")
        time.sleep(0.05)
        if data['files'] == 0:
            raise ValueError("No files to process")
        return {"races": 47, "horses": 418}
    
    @analyzer.track_function
    def train_models(processed_data):
        """Simulate training ML models"""
        print(f"🤖 Training models with {processed_data['races']} races")
        time.sleep(0.2)
        return {"model_accuracy": 0.85, "models_created": 2}
    
    print("\n🚀 Running simulated pipeline...")
    
    try:
        # Stage 1: Download
        download_result = download_csv_files("/home/jc/Documents/Horse-race-ai-v2.03/data/daily_downloads/manual_download")
        
        # Stage 2: Process
        process_result = process_race_data(download_result)
        
        # Stage 3: Train
        model_result = train_models(process_result)
        
        print("\n✅ Pipeline completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
    
    # Generate report
    print("\n📊 Generating analysis report...")
    report = analyzer.generate_report()
    
    print(f"\nSession ID: {report['session_id']}")
    print(f"Functions tracked: {report['summary']['total_functions_tracked']}")
    print(f"Total function calls: {report['summary']['total_function_calls']}")
    
    print("\n🔍 Function call details:")
    for call in report['function_statistics']:
        status = "✅" if call['success'] else "❌"
        duration = call['duration_ms']
        func_name = call['function_name']
        
        if call['success']:
            print(f"{status} {func_name}: {duration:.2f}ms")
        else:
            error = call.get('error', 'Unknown error')
            print(f"{status} {func_name}: {duration:.2f}ms - ERROR: {error}")
    
    # Save report
    report_file = f"/home/jc/Documents/Horse-race-ai-v2.03/monitoring/analysis_logs/quick_test_report_{report['session_id']}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report saved to: {report_file}")
    
    return report

if __name__ == "__main__":
    main()
