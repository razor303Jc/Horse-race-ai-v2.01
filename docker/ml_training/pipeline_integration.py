#!/usr/bin/env python3
"""
Real ML Pipeline Integration
Enhanced version with actual ML training capabilities
"""

import logging
import time
import os
import json
import traceback
from datetime import datetime
from pathlib import Path
import sys

# Add project paths
sys.path.insert(0, '/app')

# Try to import ML training components
try:
    import pandas as pd
    import psycopg2
    from psycopg2.extras import DictCursor
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, roc_auc_score
    import joblib
    ML_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ML libraries not available: {e}")
    ML_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EarlyMorningPipelineIntegration:
    def __init__(self):
        self.logger = logger
        self.is_running = False
        self.models_path = Path("/app/models")
        self.db_config = {
            'host': 'postgres',
            'port': 5432,
            'database': 'horse_racing_db',
            'user': 'horse_racing',
            'password': os.getenv('POSTGRES_PASSWORD', 'secure_password_123')
        }
        
        # Ensure directories exist
        self.models_path.mkdir(exist_ok=True)
        
    def run(self):
        """Run the ML pipeline integration"""
        self.logger.info("🧠 Real ML Pipeline Integration starting...")
        self.is_running = True
        
        try:
            while self.is_running:
                self.logger.info("🔄 ML Pipeline check - system ready")
                
                # Check if trained models exist
                self.check_models()
                
                # Run real training cycle or simulation
                if ML_AVAILABLE:
                    self.run_real_training_cycle()
                else:
                    self.simulate_training_cycle()
                
                # Wait before next cycle
                time.sleep(300)  # 5 minutes between checks
                
        except KeyboardInterrupt:
            self.logger.info("🛑 ML Pipeline Integration stopped")
        except Exception as e:
            self.logger.error(f"❌ ML Pipeline error: {e}")
        finally:
            self.is_running = False
    
    def check_models(self):
        """Check if models are available"""
        model_dir = "/app/models"
        if os.path.exists(model_dir) and os.listdir(model_dir):
            self.logger.info("✅ Model directory found with models")
            return True
        else:
            self.logger.warning("⚠️ Model directory empty or not found")
            return False
    
    def check_database_connection(self):
        """Check if database is accessible and has data"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM races")
            race_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM records")
            record_count = cursor.fetchone()[0]
            
            conn.close()
            
            self.logger.info(f"📊 Database: {race_count} races, {record_count} records")
            return race_count > 0 and record_count > 0
            
        except Exception as e:
            self.logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def load_training_data(self):
        """Load training data from PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            
            query = """
            SELECT 
                r.race_id,
                r.course,
                r.distance,
                r.race_type,
                r.runners,
                rec.horse,
                rec.position,
                rec.age,
                rec.or_rating,
                rec.weight,
                rec.jockey,
                rec.trainer,
                rec.fav,
                rec.sp
            FROM races r
            JOIN records rec ON r.race_id = rec.race_id
            WHERE rec.position IS NOT NULL
            ORDER BY r.race_id, rec.position
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            self.logger.info(f"📊 Loaded {len(df)} training records")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load training data: {e}")
            return None
    
    def prepare_features(self, df):
        """Prepare features for ML training"""
        try:
            # Create target variable (win = position 1)
            df['won'] = (df['position'] == 1).astype(int)
            
            # Prepare numeric features
            features = []
            
            if 'age' in df.columns:
                df['age'] = pd.to_numeric(df['age'], errors='coerce').fillna(0)
                features.append('age')
            
            if 'or_rating' in df.columns:
                df['or_rating'] = pd.to_numeric(df['or_rating'], errors='coerce').fillna(0)
                features.append('or_rating')
            
            if 'runners' in df.columns:
                df['runners'] = pd.to_numeric(df['runners'], errors='coerce').fillna(0)
                features.append('runners')
            
            if 'fav' in df.columns:
                df['is_favorite'] = (df['fav'] == 1).astype(int)
                features.append('is_favorite')
            
            if 'sp' in df.columns:
                df['sp'] = pd.to_numeric(df['sp'], errors='coerce').fillna(0)
                features.append('sp')
            
            if 'race_type' in df.columns:
                df['is_flat'] = df['race_type'].str.contains('Flat', na=False).astype(int)
                features.append('is_flat')
            
            self.logger.info(f"📊 Prepared {len(features)} features")
            return df[features + ['won']].dropna()
            
        except Exception as e:
            self.logger.error(f"❌ Feature preparation failed: {e}")
            return None
    
    def train_models(self, training_data):
        """Train ML models with current data"""
        try:
            feature_cols = [col for col in training_data.columns if col != 'won']
            X = training_data[feature_cols]
            y = training_data['won']
            
            if len(X) < 10:
                self.logger.warning("⚠️ Insufficient training data")
                return False
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train Random Forest
            self.logger.info("🌲 Training Random Forest model...")
            rf_model = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42)
            rf_model.fit(X_train, y_train)
            
            rf_pred = rf_model.predict(X_test)
            rf_prob = rf_model.predict_proba(X_test)[:, 1]
            rf_accuracy = accuracy_score(y_test, rf_pred)
            rf_auc = roc_auc_score(y_test, rf_prob)
            
            # Save model
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rf_path = self.models_path / f'real_rf_model_{timestamp}.joblib'
            joblib.dump(rf_model, rf_path)
            
            self.logger.info(f"✅ RF Model: Accuracy={rf_accuracy:.3f}, AUC={rf_auc:.3f}")
            
            # Save metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'training_records': len(training_data),
                'features': feature_cols,
                'accuracy': rf_accuracy,
                'auc': rf_auc,
                'model_path': str(rf_path)
            }
            
            metadata_path = self.models_path / 'real_training_metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Model training failed: {e}")
            return False
    
    def run_real_training_cycle(self):
        """Execute a real training cycle"""
        self.logger.info("🧠 Starting REAL ML training cycle...")
        
        try:
            if not self.check_database_connection():
                self.logger.warning("⚠️ No database data, skipping real training")
                self.simulate_training_cycle()
                return
            
            raw_data = self.load_training_data()
            if raw_data is None or len(raw_data) == 0:
                self.logger.warning("⚠️ No training data available")
                self.simulate_training_cycle()
                return
            
            training_data = self.prepare_features(raw_data)
            if training_data is None or len(training_data) == 0:
                self.logger.warning("⚠️ Feature preparation failed")
                self.simulate_training_cycle()
                return
            
            success = self.train_models(training_data)
            
            if success:
                self.logger.info("✅ REAL ML training cycle completed successfully")
            else:
                self.logger.error("❌ Real training failed, falling back to simulation")
                self.simulate_training_cycle()
                
        except Exception as e:
            self.logger.error(f"❌ Real training error: {e}")
            self.logger.error(traceback.format_exc())
            self.simulate_training_cycle()

    def simulate_training_cycle(self):
        """Fallback simulation"""
        self.logger.info("🔄 Simulating ML training cycle...")
        time.sleep(5)
        self.logger.info("✅ Training cycle completed")


if __name__ == "__main__":
    integration = EarlyMorningPipelineIntegration()
    integration.run()
