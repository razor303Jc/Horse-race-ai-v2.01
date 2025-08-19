#!/usr/bin/env python3
"""
Simple test to run real ML training with current database
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'docker' / 'ml_training'))

from real_ml_training_pipeline import RealMLTrainingPipeline

def test_real_training():
    """Test real training with current setup"""
    print("🧪 Testing Real ML Training Pipeline...")
    
    # Create pipeline with local paths for testing
    pipeline = RealMLTrainingPipeline()
    
    # Override paths for testing outside Docker
    pipeline.models_path = project_root / 'models'
    pipeline.trained_models_path = project_root / 'trained_models'
    pipeline.models_path.mkdir(exist_ok=True)
    pipeline.trained_models_path.mkdir(exist_ok=True)
    
    # Override database config for external connection
    pipeline.db_config = {
        'host': 'localhost',
        'port': 5434,  # External port
        'database': 'horse_racing_db',
        'user': 'horse_racing',
        'password': 'secure_password_123'
    }
    
    print("📊 Testing database connection...")
    if pipeline.check_database_connection():
        print("✅ Database connection successful")
        
        print("📥 Loading training data...")
        data = pipeline.load_training_data()
        
        if data is not None and len(data) > 0:
            print(f"✅ Loaded {len(data)} training records")
            
            print("🔧 Preparing features...")
            features = pipeline.prepare_features(data)
            
            if features is not None and len(features) > 0:
                print(f"✅ Prepared {len(features)} feature rows")
                print(f"📊 Features: {list(features.columns)}")
                
                print("🧠 Running real training cycle...")
                success = pipeline.run_real_training_cycle()
                
                if success:
                    print("🎯 REAL TRAINING SUCCESSFUL!")
                    return True
                else:
                    print("❌ Training failed")
                    return False
            else:
                print("❌ Feature preparation failed")
                return False
        else:
            print("❌ No training data available")
            return False
    else:
        print("❌ Database connection failed")
        return False

if __name__ == '__main__':
    test_real_training()
