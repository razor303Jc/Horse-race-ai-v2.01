#!/usr/bin/env python3
"""
Cyclic ML Training System for Horse Racing AI
Runs multiple training cycles with performance analysis and optimization
"""

import logging
import sys
import os
import time
import json
import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
import warnings
import pickle

warnings.filterwarnings("ignore")

sys.path.append("/app")
from tools.ml_training.standalone_course_mapper import StandaloneCourseMapper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CyclicMLTrainer:
    def __init__(self):
        self.training_history = []
        self.best_models = {}
        self.performance_trends = {
            'auc_scores': [],
            'accuracy_scores': [],
            'cycle_times': []
        }
        self.course_mapper = StandaloneCourseMapper()
        
    def connect_database(self):
        """Establish database connection"""
        return psycopg2.connect(
            host="postgres",
            database="results_horse_racing_db",
            user="horse_racing",
            password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
        )
    
    def load_training_data(self):
        """Load and prepare training data"""
        conn = self.connect_database()
        
        query = '''
        SELECT 
            rec.race_id,
            rec.horse_name,
            rec.jockey,
            rec.trainer,
            rec.position,
            rec.horse_id,
            rec.jockey_id,
            rec.trainer_id,
            CAST(rec.starting_price AS FLOAT) as odds_decimal,
            1.0 / CAST(rec.starting_price AS FLOAT) as implied_probability,
            LN(CAST(rec.starting_price AS FLOAT)) as log_odds,
            10.0 as horse_weight_kg,
            CAST(rec.age AS INT) as horse_age,
            COUNT(*) OVER (PARTITION BY rec.race_id) as field_size,
            ROW_NUMBER() OVER (PARTITION BY rec.race_id ORDER BY CAST(rec.starting_price AS FLOAT)) as odds_rank,
            CASE WHEN ROW_NUMBER() OVER (PARTITION BY rec.race_id ORDER BY CAST(rec.starting_price AS FLOAT)) = 1 THEN 1 ELSE 0 END as is_favorite,
            COALESCE(js.win_rate, 0.0) as jockey_win_pct,
            COALESCE(js.place_rate, 0.0) as jockey_place_pct,
            COALESCE(ts.win_rate, 0.0) as trainer_win_pct,
            COALESCE(ts.place_rate, 0.0) as trainer_place_pct
        FROM records rec
        LEFT JOIN jockeys_stats js ON rec.jockey_id = js.jockey_id
        LEFT JOIN trainers_stats ts ON rec.trainer_id = ts.trainer_id
        WHERE rec.position IS NOT NULL
          AND rec.starting_price IS NOT NULL
          AND CAST(rec.starting_price AS FLOAT) > 0
          AND rec.jockey_id IS NOT NULL
          AND rec.trainer_id IS NOT NULL
        ORDER BY rec.race_id, CAST(rec.starting_price AS FLOAT)
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def engineer_features(self, df, cycle_num=0):
        """Create features with cycle-based variations for optimization"""
        features_df = df.copy()
        
        # Target variable
        features_df["is_winner"] = (features_df["position"] == 1).astype(int)
        
        # Basic performance features
        features_df["jockey_performance"] = features_df["jockey_win_pct"] / 100.0
        features_df["trainer_performance"] = features_df["trainer_win_pct"] / 100.0
        
        # Cycle-based feature weighting optimization
        jockey_weight = 0.6 + (cycle_num % 10) * 0.02  # Vary between 0.6-0.78
        trainer_weight = 1.0 - jockey_weight
        
        features_df["combined_performance"] = (
            features_df["jockey_performance"] * jockey_weight
            + features_df["trainer_performance"] * trainer_weight
        )
        
        # Market features
        features_df["market_position"] = 1.0 / features_df["odds_rank"]
        features_df["field_dominance"] = features_df["field_size"] / features_df["odds_rank"]
        
        # Advanced features (introduced progressively)
        if cycle_num > 10:
            features_df["odds_value"] = features_df["implied_probability"] - (1.0 / features_df["field_size"])
            features_df["favorite_advantage"] = features_df["is_favorite"] * features_df["combined_performance"]
        
        if cycle_num > 25:
            features_df["age_performance"] = features_df["horse_age"] * features_df["combined_performance"]
            features_df["field_competitive"] = features_df["field_size"] * features_df["market_position"]
        
        # Select feature columns based on cycle
        base_features = [
            'odds_decimal', 'implied_probability', 'log_odds',
            'horse_weight_kg', 'horse_age', 'field_size', 'odds_rank',
            'is_favorite', 'jockey_performance', 'trainer_performance',
            'combined_performance', 'market_position', 'field_dominance'
        ]
        
        if cycle_num > 10:
            base_features.extend(['odds_value', 'favorite_advantage'])
        
        if cycle_num > 25:
            base_features.extend(['age_performance', 'field_competitive'])
        
        X = features_df[base_features]
        y = features_df['is_winner']
        
        return X, y, base_features
    
    def train_single_cycle(self, cycle_num, session_num):
        """Run a single training cycle"""
        start_time = time.time()
        
        logger.info(f"🔄 Cycle {cycle_num} - Session {session_num}")
        
        # Load data
        df = self.load_training_data()
        X, y, feature_names = self.engineer_features(df, cycle_num)
        
        # Handle missing values
        X = X.fillna(0)
        
        # Split data with some randomization
        random_state = 42 + cycle_num + session_num
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train models with cycle-optimized parameters
        models = {
            'RandomForest': RandomForestClassifier(
                n_estimators=50 + cycle_num * 2,
                max_depth=5 + (cycle_num // 10),
                random_state=random_state,
                n_jobs=1
            ),
            'GradientBoosting': GradientBoostingClassifier(
                n_estimators=50 + cycle_num * 2,
                learning_rate=0.1 - (cycle_num * 0.001),
                max_depth=3 + (cycle_num // 15),
                random_state=random_state
            ),
            'LogisticRegression': LogisticRegression(
                C=1.0 + (cycle_num * 0.1),
                random_state=random_state,
                max_iter=1000
            )
        }
        
        cycle_results = {}
        
        for name, model in models.items():
            if name == 'LogisticRegression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                y_proba = model.predict_proba(X_test_scaled)[:, 1]
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_proba = model.predict_proba(X_test)[:, 1]
            
            auc = roc_auc_score(y_test, y_proba)
            report = classification_report(y_test, y_pred, output_dict=True)
            
            cycle_results[name] = {
                'auc': auc,
                'accuracy': report['accuracy'],
                'precision': report.get('1', {}).get('precision', 0),
                'recall': report.get('1', {}).get('recall', 0),
                'f1': report.get('1', {}).get('f1-score', 0),
                'model': model,
                'scaler': scaler if name == 'LogisticRegression' else None
            }
        
        # Find best model for this cycle
        best_model_name = max(cycle_results.keys(), key=lambda x: cycle_results[x]['auc'])
        best_auc = cycle_results[best_model_name]['auc']
        
        cycle_time = time.time() - start_time
        
        # Store results
        cycle_data = {
            'cycle': cycle_num,
            'session': session_num,
            'timestamp': datetime.now().isoformat(),
            'best_model': best_model_name,
            'best_auc': best_auc,
            'accuracy': cycle_results[best_model_name]['accuracy'],
            'features_used': len(feature_names),
            'feature_names': feature_names,
            'cycle_time': cycle_time,
            'all_results': {k: {key: val for key, val in v.items() if key != 'model' and key != 'scaler'} 
                           for k, v in cycle_results.items()}
        }
        
        self.training_history.append(cycle_data)
        self.performance_trends['auc_scores'].append(best_auc)
        self.performance_trends['accuracy_scores'].append(cycle_results[best_model_name]['accuracy'])
        self.performance_trends['cycle_times'].append(cycle_time)
        
        # Update best models if performance improved
        if best_model_name not in self.best_models or best_auc > self.best_models[best_model_name]['auc']:
            self.best_models[best_model_name] = {
                'auc': best_auc,
                'cycle': cycle_num,
                'session': session_num,
                'model': cycle_results[best_model_name]['model'],
                'scaler': cycle_results[best_model_name]['scaler'],
                'features': feature_names
            }
        
        logger.info(f"  ✅ Best: {best_model_name} - AUC: {best_auc:.4f}, Accuracy: {cycle_results[best_model_name]['accuracy']:.4f}")
        logger.info(f"  ⏱️ Cycle time: {cycle_time:.2f}s")
        
        return cycle_data
    
    def analyze_performance_trends(self):
        """Analyze performance trends and suggest optimizations"""
        if len(self.performance_trends['auc_scores']) < 5:
            return "Not enough data for trend analysis"
        
        recent_aucs = self.performance_trends['auc_scores'][-5:]
        trend = "improving" if recent_aucs[-1] > recent_aucs[0] else "declining"
        
        avg_auc = np.mean(self.performance_trends['auc_scores'])
        max_auc = np.max(self.performance_trends['auc_scores'])
        avg_time = np.mean(self.performance_trends['cycle_times'])
        
        analysis = {
            'trend': trend,
            'average_auc': avg_auc,
            'max_auc': max_auc,
            'average_cycle_time': avg_time,
            'total_cycles': len(self.performance_trends['auc_scores']),
            'recommendation': self._get_optimization_recommendation(trend, avg_auc, max_auc)
        }
        
        return analysis
    
    def _get_optimization_recommendation(self, trend, avg_auc, max_auc):
        """Get optimization recommendations based on performance"""
        if avg_auc > 0.85:
            return "Excellent performance - maintain current strategy"
        elif trend == "improving" and avg_auc > 0.75:
            return "Good trend - continue with progressive feature expansion"
        elif trend == "declining":
            return "Performance declining - consider feature reduction or parameter adjustment"
        else:
            return "Stable performance - try parameter variation for improvement"
    
    def save_training_session(self, session_name):
        """Save training session results"""
        session_data = {
            'session_name': session_name,
            'timestamp': datetime.now().isoformat(),
            'training_history': self.training_history,
            'performance_trends': self.performance_trends,
            'best_models_summary': {
                name: {k: v for k, v in model.items() if k not in ['model', 'scaler']}
                for name, model in self.best_models.items()
            }
        }
        
        # Log session summary instead of saving files (read-only container)
        logger.info(f"📊 SESSION SUMMARY '{session_name}':")
        logger.info(f"  Total cycles: {len(self.training_history)}")
        logger.info(f"  Best AUC achieved: {max(self.performance_trends['auc_scores']):.4f}")
        logger.info(f"  Average AUC: {np.mean(self.performance_trends['auc_scores']):.4f}")
        logger.info(f"  Best models: {list(self.best_models.keys())}")
        
        logger.info(f"💾 Session '{session_name}' logged successfully")
    
    def run_training_cycles(self, num_cycles, sessions_per_cycle, session_name, wait_time=2):
        """Run multiple training cycles"""
        logger.info(f"🚀 Starting {num_cycles} cycles with {sessions_per_cycle} sessions each")
        logger.info(f"📊 Total training sessions: {num_cycles * sessions_per_cycle}")
        
        total_sessions = 0
        
        for cycle in range(1, num_cycles + 1):
            logger.info(f"🔄 CYCLE {cycle}/{num_cycles}")
            
            cycle_start_time = time.time()
            
            for session in range(1, sessions_per_cycle + 1):
                total_sessions += 1
                
                # Run training cycle
                cycle_data = self.train_single_cycle(cycle, session)
                
                # Short wait between sessions
                if session < sessions_per_cycle:
                    time.sleep(wait_time)
            
            # Analyze trends after each cycle
            if cycle % 5 == 0 or cycle == num_cycles:
                analysis = self.analyze_performance_trends()
                logger.info(f"📈 PERFORMANCE ANALYSIS (Cycle {cycle}):")
                if isinstance(analysis, dict):
                    logger.info(f"  Trend: {analysis['trend']}")
                    logger.info(f"  Average AUC: {analysis['average_auc']:.4f}")
                    logger.info(f"  Max AUC: {analysis['max_auc']:.4f}")
                    logger.info(f"  Avg Cycle Time: {analysis['average_cycle_time']:.2f}s")
                    logger.info(f"  Recommendation: {analysis['recommendation']}")
                
                # Save intermediate results
                self.save_training_session(f"{session_name}_cycle_{cycle}")
            
            cycle_time = time.time() - cycle_start_time
            logger.info(f"✅ Cycle {cycle} completed in {cycle_time:.2f}s")
            logger.info(f"🎯 Progress: {cycle}/{num_cycles} cycles, {total_sessions} total sessions")
            
            # Longer wait between cycles
            if cycle < num_cycles:
                logger.info(f"⏸️ Waiting {wait_time*2}s before next cycle...")
                time.sleep(wait_time * 2)
        
        # Final save
        self.save_training_session(session_name)
        
        # Final summary
        final_analysis = self.analyze_performance_trends()
        logger.info("🏁 TRAINING COMPLETE - FINAL SUMMARY:")
        logger.info(f"  Total sessions: {total_sessions}")
        logger.info(f"  Best overall AUC: {max(self.performance_trends['auc_scores']):.4f}")
        logger.info(f"  Best models: {list(self.best_models.keys())}")
        
        return final_analysis


def main():
    """Main training orchestrator"""
    trainer = CyclicMLTrainer()
    
    # Phase 1: Initial training (5 cycles, 5 sessions each = 25 total)
    logger.info("🎯 PHASE 1: Initial Training (5 cycles × 5 sessions)")
    phase1_analysis = trainer.run_training_cycles(
        num_cycles=5,
        sessions_per_cycle=5,
        session_name="phase1_5x5",
        wait_time=2
    )
    
    # Short break between phases
    logger.info("⏸️ Phase break - 10 seconds...")
    time.sleep(10)
    
    # Phase 2: Extended training (10 cycles, 10 sessions each = 100 total)
    logger.info("🎯 PHASE 2: Extended Training (10 cycles × 10 sessions)")
    phase2_analysis = trainer.run_training_cycles(
        num_cycles=10,
        sessions_per_cycle=10,
        session_name="phase2_10x10",
        wait_time=1
    )
    
    logger.info("🎉 ALL TRAINING PHASES COMPLETED!")
    logger.info("Next step: Run AI selections with best trained models")


if __name__ == "__main__":
    main()
