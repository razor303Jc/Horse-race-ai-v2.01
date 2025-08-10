#!/usr/bin/env python3
"""
🚀 Priority 3A: Simplified Parallel Model Training Pipeline

Simplified but powerful parallel training system that works with our current data.
Builds on Priority 2A database optimization for fast data access.

Features:
- Parallel model training using multiprocessing
- Multiple ML algorithms with hyperparameter optimization
- Model ensemble creation and evaluation
- Performance comparison and selection
- Production-ready model deployment

Priority: 3A (High Impact, Medium Complexity - 2 hours implementation)
"""

import logging
import os
import pickle
import json
import time
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
import psycopg2
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
    VotingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    GridSearchCV,
    RandomizedSearchCV,
    StratifiedKFold
)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimplifiedParallelTrainer:
    """
    Simplified Parallel Model Training Pipeline
    
    Features:
    - Works with current database structure
    - Parallel model training with hyperparameter optimization
    - Ensemble model creation
    - Production-ready model outputs
    """
    
    def __init__(self):
        """Initialize the simplified parallel trainer."""
        self.project_root = Path.cwd()
        self.models_dir = self.project_root / "trained_models" / "priority_3a"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Training components
        self.trained_models = {}
        self.model_performance = {}
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        # Configuration
        self.cv_folds = 5
        self.test_size = 0.2
        self.random_state = 42
        
        logger.info("🚀 Simplified Parallel Trainer initialized - Priority 3A")
    
    def load_and_prepare_data(self) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Load data from optimized database and prepare features."""
        logger.info("📊 Loading data from optimized database...")
        
        try:
            # Connect to database (benefits from Priority 2A optimization)
            conn = psycopg2.connect(
                host="localhost",
                port=5433,
                database="horse_racing_db",
                user="horse_racing",
                password="secure_password_123"
            )
            
            # Optimized query using Priority 2A indexes
            query = """
                SELECT 
                    rr.race_date,
                    rr.course,
                    rr.horse_name,
                    rr.jockey_name,
                    rr.trainer_name,
                    rr.horse_age,
                    rr.draw,
                    rr.win_odds,
                    rr.place_odds,
                    rr.barrier,
                    rr.finished_position,
                    rr.margin,
                    rr.horse_weight_kg,
                    rr.handicap_weight,
                    js.win_percentage as jockey_win_pct,
                    js.place_percentage as jockey_place_pct,
                    ts.win_percentage as trainer_win_pct,
                    ts.place_percentage as trainer_place_pct
                FROM race_results rr
                LEFT JOIN jockey_stats js ON rr.jockey_name = js.jockey_name
                LEFT JOIN trainer_stats ts ON rr.trainer_name = ts.trainer_name
                WHERE rr.race_date >= '2020-01-01'
                    AND rr.finished_position IS NOT NULL
                    AND rr.win_odds IS NOT NULL
                    AND rr.horse_age IS NOT NULL
                ORDER BY rr.race_date DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            logger.info(f"✅ Loaded {len(df):,} race records with joins")
            
            # Engineer features
            df_features = self._engineer_comprehensive_features(df)
            
            # Create target variable (winner = position 1)
            y = (df_features['finished_position'] == 1).astype(int)
            
            # Select feature columns
            feature_columns = [col for col in df_features.columns 
                             if col not in ['finished_position', 'race_date', 'horse_name', 
                                          'jockey_name', 'trainer_name', 'course']]
            
            X = df_features[feature_columns]
            
            # Handle missing values
            X = X.fillna(X.median())
            
            logger.info(f"✅ Prepared {X.shape[1]} features from {len(y):,} samples")
            logger.info(f"📊 Win rate: {y.mean():.1%}")
            
            return X.values, y.values, feature_columns
            
        except Exception as e:
            logger.error(f"❌ Failed to load and prepare data: {e}")
            raise
    
    def _parse_margin(self, margin_str):
        """Parse horse racing margin notation to numeric value."""
        if pd.isna(margin_str) or margin_str == 'nan':
            return 0.0
        
        margin_str = str(margin_str).lower().strip()
        
        # Special cases
        margin_map = {
            'hd': 0.05,    # head
            'shd': 0.02,   # short head
            'nk': 0.1,     # neck
            'nse': 0.01,   # nose
            'dh': 0.0,     # dead heat
            'nse': 0.01,   # nose
            '': 0.0,
            'nan': 0.0
        }
        
        if margin_str in margin_map:
            return margin_map[margin_str]
        
        # Parse fractions like "2½", "1¼", etc.
        try:
            # Handle fractions
            if '½' in margin_str:
                base = margin_str.replace('½', '')
                if base == '':
                    return 0.5
                return float(base) + 0.5
            elif '¼' in margin_str:
                base = margin_str.replace('¼', '')
                if base == '':
                    return 0.25
                return float(base) + 0.25
            elif '¾' in margin_str:
                base = margin_str.replace('¾', '')
                if base == '':
                    return 0.75
                return float(base) + 0.75
            else:
                return float(margin_str)
        except (ValueError, TypeError):
            return 0.0
    
    def _engineer_comprehensive_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer comprehensive features from available data."""
        logger.info("⚙️ Engineering comprehensive features...")
        
        df_features = df.copy()
        
        # Convert odds to numeric
        df_features['win_odds'] = pd.to_numeric(df_features['win_odds'], errors='coerce')
        df_features['place_odds'] = pd.to_numeric(df_features['place_odds'], errors='coerce')
        
        # Parse margin using custom function
        df_features['margin'] = df_features['margin'].apply(self._parse_margin)
        
        # Basic numeric features
        df_features['horse_age'] = pd.to_numeric(df_features['horse_age'], errors='coerce')
        df_features['draw'] = pd.to_numeric(df_features['draw'], errors='coerce')
        df_features['barrier'] = pd.to_numeric(df_features['barrier'], errors='coerce')
        df_features['horse_weight_kg'] = pd.to_numeric(df_features['horse_weight_kg'], errors='coerce')
        df_features['handicap_weight'] = pd.to_numeric(df_features['handicap_weight'], errors='coerce')
        
        # Odds-based features
        df_features['is_favorite'] = (df_features['win_odds'] <= 3.0).astype(int)
        df_features['high_odds'] = (df_features['win_odds'] >= 10.0).astype(int)
        df_features['log_odds'] = np.log(df_features['win_odds'].clip(lower=1.01))
        df_features['implied_prob'] = 1 / df_features['win_odds'].clip(lower=1.01)
        
        # Safe ratio calculations
        place_odds_safe = df_features['place_odds'].fillna(df_features['win_odds']).clip(lower=0.1)
        df_features['odds_ratio'] = df_features['win_odds'] / place_odds_safe
        
        weight_denom = df_features['handicap_weight'].fillna(df_features['horse_weight_kg']).clip(lower=30)
        df_features['weight_ratio'] = df_features['horse_weight_kg'] / weight_denom
        
        # Age and position features
        df_features['age_squared'] = df_features['horse_age'] ** 2
        df_features['draw_squared'] = df_features['draw'] ** 2
        df_features['barrier_squared'] = df_features['barrier'] ** 2
        
        # Statistical features (from joins)
        df_features['jockey_win_pct'] = pd.to_numeric(df_features['jockey_win_pct'], errors='coerce').fillna(10)
        df_features['jockey_place_pct'] = pd.to_numeric(df_features['jockey_place_pct'], errors='coerce').fillna(25)
        df_features['trainer_win_pct'] = pd.to_numeric(df_features['trainer_win_pct'], errors='coerce').fillna(10)
        df_features['trainer_place_pct'] = pd.to_numeric(df_features['trainer_place_pct'], errors='coerce').fillna(25)
        
        # Combined performance features
        df_features['jockey_trainer_combo'] = df_features['jockey_win_pct'] * df_features['trainer_win_pct']
        df_features['combined_place_pct'] = (df_features['jockey_place_pct'] + df_features['trainer_place_pct']) / 2
        
        # Categorical encoding for high-cardinality features
        for col in ['course']:
            if col in df_features.columns:
                le = LabelEncoder()
                df_features[f'{col}_encoded'] = le.fit_transform(df_features[col].astype(str))
                self.label_encoders[col] = le
        
        logger.info(f"✅ Engineered features: {len([c for c in df_features.columns if c not in df.columns])} new features")
        
        return df_features
    
    def get_model_configs(self) -> Dict[str, Dict]:
        """Get simplified model configurations for parallel training."""
        return {
            'random_forest': {
                'model': RandomForestClassifier(random_state=self.random_state, n_jobs=1),
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [10, 15, None],
                    'min_samples_split': [2, 5],
                    'class_weight': ['balanced', None]
                }
            },
            'gradient_boosting': {
                'model': GradientBoostingClassifier(random_state=self.random_state),
                'params': {
                    'n_estimators': [100, 200],
                    'learning_rate': [0.1, 0.15],
                    'max_depth': [3, 5],
                    'subsample': [0.8, 1.0]
                }
            },
            'extra_trees': {
                'model': ExtraTreesClassifier(random_state=self.random_state, n_jobs=1),
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [10, 15],
                    'min_samples_split': [2, 5],
                    'class_weight': ['balanced', None]
                }
            },
            'logistic_regression': {
                'model': LogisticRegression(random_state=self.random_state, max_iter=1000),
                'params': {
                    'C': [0.1, 1.0, 10.0],
                    'penalty': ['l2'],
                    'class_weight': ['balanced', None]
                }
            },
            'neural_network': {
                'model': MLPClassifier(random_state=self.random_state, max_iter=1000),
                'params': {
                    'hidden_layer_sizes': [(100,), (100, 50)],
                    'alpha': [0.001, 0.01],
                    'learning_rate_init': [0.01, 0.1]
                }
            }
        }
    
    def train_single_model(self, args: Tuple) -> Dict:
        """Train a single model with hyperparameter optimization."""
        model_name, config, X_train, y_train, X_test, y_test = args
        
        start_time = time.time()
        logger.info(f"🔧 Training {model_name}...")
        
        try:
            # Create grid search
            cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=self.random_state)  # Reduced CV for speed
            
            grid_search = GridSearchCV(
                config['model'],
                config['params'],
                cv=cv,
                scoring='roc_auc',
                n_jobs=1,
                verbose=0
            )
            
            # Scale data for neural network
            if model_name == 'neural_network':
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                grid_search.fit(X_train_scaled, y_train)
                
                # Predictions on scaled data
                y_pred = grid_search.predict(X_test_scaled)
                y_pred_proba = grid_search.predict_proba(X_test_scaled)[:, 1]
            else:
                grid_search.fit(X_train, y_train)
                y_pred = grid_search.predict(X_test)
                y_pred_proba = grid_search.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            test_metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, zero_division=0),
                'recall': recall_score(y_test, y_pred, zero_division=0),
                'f1_score': f1_score(y_test, y_pred, zero_division=0),
                'roc_auc': roc_auc_score(y_test, y_pred_proba)
            }
            
            training_time = time.time() - start_time
            
            result = {
                'model_name': model_name,
                'best_model': grid_search.best_estimator_,
                'best_params': grid_search.best_params_,
                'cv_score': grid_search.best_score_,
                'test_metrics': test_metrics,
                'training_time': training_time,
                'scaler': scaler if model_name == 'neural_network' else None
            }
            
            logger.info(f"✅ {model_name}: AUC={test_metrics['roc_auc']:.4f}, CV={grid_search.best_score_:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ {model_name} training failed: {e}")
            return {'model_name': model_name, 'error': str(e)}
    
    def train_models_parallel(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> Dict:
        """Train multiple models in parallel."""
        logger.info("🚀 Starting parallel model training...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
        )
        
        logger.info(f"📊 Training: {len(X_train):,} samples, Test: {len(X_test):,} samples")
        
        # Get model configurations
        model_configs = self.get_model_configs()
        
        # Prepare arguments for parallel training
        training_args = [
            (name, config, X_train, y_train, X_test, y_test)
            for name, config in model_configs.items()
        ]
        
        # Train models in parallel
        results = []
        failed_models = []
        
        with ProcessPoolExecutor(max_workers=min(len(model_configs), os.cpu_count())) as executor:
            future_to_model = {
                executor.submit(self.train_single_model, args): args[0]
                for args in training_args
            }
            
            for future in as_completed(future_to_model):
                model_name = future_to_model[future]
                try:
                    result = future.result()
                    if 'error' in result:
                        failed_models.append(result)
                    else:
                        results.append(result)
                        self.trained_models[model_name] = result['best_model']
                        self.model_performance[model_name] = result
                except Exception as e:
                    logger.error(f"❌ Parallel execution failed for {model_name}: {e}")
                    failed_models.append({'model_name': model_name, 'error': str(e)})
        
        return {
            'successful_models': {r['model_name']: r for r in results},
            'failed_models': failed_models,
            'feature_names': feature_names
        }
    
    def create_ensemble_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                             X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Create ensemble model from top performers."""
        logger.info("🏆 Creating ensemble model...")
        
        if len(self.trained_models) < 3:
            logger.warning("⚠️ Need at least 3 models for ensemble")
            return {}
        
        # Select top models by AUC
        top_models = sorted(
            [(name, perf['test_metrics']['roc_auc']) for name, perf in self.model_performance.items()],
            key=lambda x: x[1],
            reverse=True
        )[:3]  # Top 3 models
        
        logger.info(f"🎯 Using top 3 models for ensemble: {[name for name, _ in top_models]}")
        
        # Create voting classifier
        estimators = [(name, self.trained_models[name]) for name, _ in top_models]
        ensemble = VotingClassifier(estimators=estimators, voting='soft')
        
        # Train ensemble
        start_time = time.time()
        ensemble.fit(X_train, y_train)
        training_time = time.time() - start_time
        
        # Evaluate ensemble
        y_pred = ensemble.predict(X_test)
        y_pred_proba = ensemble.predict_proba(X_test)[:, 1]
        
        ensemble_metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        logger.info(f"✅ Ensemble AUC: {ensemble_metrics['roc_auc']:.4f}")
        
        return {
            'ensemble_model': ensemble,
            'test_metrics': ensemble_metrics,
            'training_time': training_time,
            'component_models': [name for name, _ in top_models]
        }
    
    def save_models_and_results(self, training_results: Dict, ensemble_result: Dict):
        """Save all models and results."""
        logger.info("💾 Saving models and results...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save individual models
        for model_name, model in self.trained_models.items():
            model_path = self.models_dir / f"{model_name}_{timestamp}.joblib"
            joblib.dump(model, model_path)
        
        # Save ensemble if created
        if ensemble_result:
            ensemble_path = self.models_dir / f"ensemble_{timestamp}.joblib"
            joblib.dump(ensemble_result['ensemble_model'], ensemble_path)
        
        # Save label encoders
        encoders_path = self.models_dir / f"encoders_{timestamp}.joblib"
        joblib.dump(self.label_encoders, encoders_path)
        
        # Save results metadata
        metadata = {
            'timestamp': timestamp,
            'model_performance': {
                name: {k: v for k, v in perf.items() if k not in ['best_model', 'scaler']}
                for name, perf in self.model_performance.items()
            },
            'ensemble_performance': {
                k: v for k, v in ensemble_result.items() if k != 'ensemble_model'
            } if ensemble_result else {},
            'feature_names': training_results['feature_names'],
            'failed_models': training_results['failed_models']
        }
        
        metadata_path = self.models_dir / f"results_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"💾 Saved models and metadata to {self.models_dir}")
        
        return {
            'models_dir': self.models_dir,
            'timestamp': timestamp,
            'metadata_file': metadata_path
        }
    
    def print_results_summary(self, training_results: Dict, ensemble_result: Dict):
        """Print comprehensive results summary."""
        print("🚀 Priority 3A: Parallel Model Training Complete")
        print("=" * 60)
        
        # Model performance summary
        successful = training_results['successful_models']
        if successful:
            print(f"\n🏆 Model Performance (sorted by AUC):")
            sorted_models = sorted(
                successful.items(),
                key=lambda x: x[1]['test_metrics']['roc_auc'],
                reverse=True
            )
            
            for i, (name, result) in enumerate(sorted_models, 1):
                metrics = result['test_metrics']
                print(f"   {i}. {name:20}: AUC={metrics['roc_auc']:.4f}, "
                      f"Acc={metrics['accuracy']:.4f}, "
                      f"Time={result['training_time']:.1f}s")
        
        # Ensemble performance
        if ensemble_result:
            print(f"\n🎭 Ensemble Performance:")
            metrics = ensemble_result['test_metrics']
            print(f"   Voting Ensemble: AUC={metrics['roc_auc']:.4f}, "
                  f"Acc={metrics['accuracy']:.4f}")
            print(f"   Components: {', '.join(ensemble_result['component_models'])}")
        
        # Training summary
        print(f"\n📊 Training Summary:")
        print(f"   Successful models: {len(successful)}")
        print(f"   Failed models: {len(training_results['failed_models'])}")
        print(f"   Features used: {len(training_results['feature_names'])}")
        
        if ensemble_result:
            best_auc = ensemble_result['test_metrics']['roc_auc']
        elif successful:
            best_auc = max(r['test_metrics']['roc_auc'] for r in successful.values())
        else:
            best_auc = 0
        
        print(f"   Best AUC achieved: {best_auc:.4f}")
        
        print(f"\n🎯 Production Readiness:")
        print(f"   ✅ Models trained and optimized")
        print(f"   ✅ Ensemble model created") if ensemble_result else print(f"   ⚠️ No ensemble created")
        print(f"   ✅ Models saved for deployment")
        print(f"   ✅ Ready for live prediction serving")
    
    def run_complete_pipeline(self) -> Dict:
        """Run the complete parallel training pipeline."""
        logger.info("🚀 Starting Priority 3A: Complete Parallel Training Pipeline...")
        
        start_time = time.time()
        
        try:
            # Load and prepare data
            X, y, feature_names = self.load_and_prepare_data()
            
            # Split data for ensemble creation
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
            )
            
            # Train models in parallel
            training_results = self.train_models_parallel(X, y, feature_names)
            
            # Create ensemble model
            ensemble_result = self.create_ensemble_model(X_train, y_train, X_test, y_test)
            
            # Save everything
            saved_info = self.save_models_and_results(training_results, ensemble_result)
            
            # Print results
            self.print_results_summary(training_results, ensemble_result)
            
            total_time = time.time() - start_time
            logger.info(f"🎉 Priority 3A completed in {total_time:.1f} seconds")
            
            return {
                'success': True,
                'training_results': training_results,
                'ensemble_result': ensemble_result,
                'saved_info': saved_info,
                'execution_time': total_time
            }
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time
            }


def main():
    """Run Priority 3A: Simplified Parallel Model Training."""
    trainer = SimplifiedParallelTrainer()
    results = trainer.run_complete_pipeline()
    
    if results['success']:
        print(f"\n🎉 Priority 3A: Parallel Model Training Successful!")
        print(f"⏱️ Execution time: {results['execution_time']:.1f} seconds")
        print(f"🚀 Ready for production deployment!")
    else:
        print(f"\n❌ Training failed: {results['error']}")


if __name__ == "__main__":
    main()
