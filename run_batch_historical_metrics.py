#!/usr/bin/env python3
"""
Batch Historical Metrics Generator
Process historical results data in manageable batches
"""

import sys
sys.path.append('/home/jc/Documents/Horse-race-ai-v2.03')

from tools.historical_metrics_generator import HistoricalMetricsGenerator
import json
from datetime import datetime

def run_batch_generation():
    print("🏆 Batch Historical Metrics Generation")
    print("=" * 50)
    
    try:
        generator = HistoricalMetricsGenerator()
        
        # Load all data
        data = generator._load_results_data()
        total_records = len(data['records'])
        print(f"📊 Total records to process: {total_records}")
        
        # Process in batches of 50
        batch_size = 50
        total_metrics = {'power_ratings': [], 'speed_ratings': [], 'form_scores': [], 'monte_carlo': []}
        
        for i in range(0, total_records, batch_size):
            batch_end = min(i + batch_size, total_records)
            batch_data = {
                'races': data['races'],
                'records': data['records'][i:batch_end],
                'horses': data['horses']
            }
            
            print(f"\n🔄 Processing batch {i//batch_size + 1}: records {i+1}-{batch_end}")
            
            # Generate metrics for this batch
            batch_metrics = generator._generate_metrics_from_results(batch_data)
            
            # Accumulate metrics
            for key in total_metrics:
                total_metrics[key].extend(batch_metrics[key])
            
            print(f"   ✅ Generated {len(batch_metrics['power_ratings'])} metrics")
        
        print(f"\n📈 Total Generated:")
        print(f"   Power Ratings: {len(total_metrics['power_ratings'])}")
        print(f"   Speed Ratings: {len(total_metrics['speed_ratings'])}")
        print(f"   Form Scores: {len(total_metrics['form_scores'])}")
        print(f"   Monte Carlo: {len(total_metrics['monte_carlo'])}")
        
        # Save to database
        print("\n💾 Saving to database...")
        db_stats = generator._save_to_database(total_metrics)
        print(f"   Database records inserted: {sum(db_stats.values())}")
        
        # Save JSON files
        print("\n📁 Creating JSON files...")
        file_stats = generator._save_json_files(total_metrics)
        print(f"   Files created: {file_stats['count']}")
        
        print("\n🎉 Batch processing completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            generator.conn.close()
        except:
            pass

if __name__ == "__main__":
    success = run_batch_generation()
    sys.exit(0 if success else 1)
