#!/usr/bin/env python3
"""
Simple test script for historical metrics generation
"""

import sys
sys.path.append('/home/jc/Documents/Horse-race-ai-v2.03')

from tools.historical_metrics_generator import HistoricalMetricsGenerator

print("🐎 Starting Historical Metrics Generator Test")
print("=" * 50)

try:
    generator = HistoricalMetricsGenerator()
    print("✅ Generator initialized")
    
    # Load data
    data = generator._load_results_data()
    print(f"✅ Data loaded: {len(data['records'])} records")
    
    if len(data['records']) > 0:
        # Test with just first 5 records
        test_data = {
            'races': data['races'],
            'records': data['records'][:5],
            'horses': data['horses']
        }
        
        print("🔧 Generating metrics for 5 test records...")
        metrics = generator._generate_metrics_from_results(test_data)
        
        print(f"✅ Generated:")
        print(f"   Power ratings: {len(metrics['power_ratings'])}")
        print(f"   Speed ratings: {len(metrics['speed_ratings'])}")  
        print(f"   Form scores: {len(metrics['form_scores'])}")
        print(f"   Monte Carlo: {len(metrics['monte_carlo'])}")
        
        print("\n🎉 Test completed successfully!")
    else:
        print("❌ No data to process")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    try:
        generator.conn.close()
    except:
        pass
