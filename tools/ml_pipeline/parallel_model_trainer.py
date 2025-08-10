#!/usr/bin/env python3
"""
🚀 Priority 3A: Parallel Model Training Pipeline

Advanced parallel training system that trains multiple ML models simultaneously.
Builds on Priority 1B ML preprocessing and Priority 2A database optimization.

Features:
- Parallel model training using multiprocessing
- Hyperparameter optimization with Grid/Random Search
- Model ensemble creation and evaluation
- Performance comparison and selection
- Production model deployment preparation
- Advanced cross-validation and metrics

Priority: 3A (High Impact, High Complexity - 4 hours implementation)
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
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import pandas as pd
import psycopg2
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
    VotingClassifier,
    BaggingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
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
    classification_report,
    confusion_matrix
)
from sklearn.preprocessing import StandardScaler
import joblib

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ParallelModelTrainer:
    """
    Priority 3A: Parallel Model Training Pipeline
    
    Advanced training system with:
    - Parallel execution of multiple models
    - Hyperparameter optimization
    - Model ensemble creation
    - Performance monitoring and comparison
    - Production deployment preparation
    """
    
    def __init__(self):
        """Initialize the parallel model training system."""
        self.project_root = Path.cwd()
        self.models_dir = self.project_root / "trained_models" / "parallel_training"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Training components
        self.trained_models = {}
        self.model_performance = {}
        self.hyperparameter_results = {}
        self.ensemble_models = {}
        self.preprocessing_pipeline = None
        
        # Training configuration
        self.cv_folds = 5
        self.test_size = 0.2
        self.random_state = 42
        self.n_jobs = -1  # Use all available cores
        
        logger.info("🚀 Parallel Model Training Pipeline initialized - Priority 3A")
    
    def load_preprocessed_data(self) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Load preprocessed data from Priority 1B ML pipeline."""
        logger.info("📊 Loading preprocessed data from ML pipeline...")
        
        try:
            # Load the production preprocessing pipeline
            pipeline_path = self.project_root / "trained_models" / "ml_preprocessing_pipeline.pkl"
            
            if not pipeline_path.exists():
                raise FileNotFoundError("ML preprocessing pipeline not found. Run Priority 1B first.")
            
            with open(pipeline_path, 'rb') as f:
                self.preprocessing_pipeline = pickle.load(f)
            
            logger.info("✅ Preprocessing pipeline loaded")
            
            # Connect to database and load clean data
            conn = psycopg2.connect(
                host="localhost",
                port=5433,
                database="horse_racing_db",
                user="horse_racing",
                password="secure_password_123"
            )
            
            # Load race results data (optimized with Priority 2A indexes)
            query = """
                SELECT 
                    race_date,
                    course,
                    horse_name,
                    jockey_name,
                    trainer_name,
                    horse_age,
                    draw,
                    win_odds,
                    place_odds,
                    barrier,
                    finished_position,
                    margin,
                    time_seconds,
                    horse_weight_kg,
                    handicap_weight
                FROM race_results 
                WHERE race_date >= '2020-01-01'
                    AND finished_position IS NOT NULL
                    AND win_odds IS NOT NULL
                ORDER BY race_date DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            logger.info(f"✅ Loaded {len(df):,} race records")
            
            # Apply the same feature engineering as Priority 1B
            df_features = self._engineer_features(df)
            
            # Create target variable (winner = position 1)
            y = (df_features['finished_position'] == 1).astype(int)
            
            # Get feature columns (exclude target and identifiers)
            feature_columns = [col for col in df_features.columns 
                             if col not in ['finished_position', 'race_date', 'horse_name']]
            
            X = df_features[feature_columns]
            
            # Apply preprocessing pipeline
            X_processed = self.preprocessing_pipeline['preprocessor'].transform(X)
            
            logger.info(f"✅ Features processed: {X_processed.shape[1]} features, {len(y):,} samples")
            logger.info(f"📊 Win rate: {y.mean():.1%}")
            
            return X_processed, y.values, feature_columns
            
        except Exception as e:
            logger.error(f"❌ Failed to load preprocessed data: {e}")
            raise
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features using the same logic as Priority 1B."""
        logger.info("⚙️ Engineering features...")
        
        df_features = df.copy()
        
        # Convert odds columns to numeric, handling any string values
        df_features['win_odds'] = pd.to_numeric(df_features['win_odds'], errors='coerce')
        df_features['place_odds'] = pd.to_numeric(df_features['place_odds'], errors='coerce')
        
        # Numeric feature engineering with safe division
        place_odds_safe = df_features['place_odds'].fillna(1)
        place_odds_safe = place_odds_safe.replace(0, 1)  # Avoid division by zero
        df_features['odds_ratio'] = df_features['win_odds'] / place_odds_safe
        
        handicap_safe = df_features['handicap_weight'].fillna(1)
        handicap_safe = handicap_safe.replace(0, 1)  # Avoid division by zero
        df_features['weight_ratio'] = df_features['horse_weight_kg'] / handicap_safe
        
        df_features['is_favorite'] = (df_features['win_odds'] <= 3.0).astype(int)
        df_features['high_odds'] = (df_features['win_odds'] >= 10.0).astype(int)
        
        # Age categories
        df_features['age_group'] = pd.cut(df_features['horse_age'], 
                                        bins=[0, 3, 5, 8, 100], 
                                        labels=['Young', 'Prime', 'Mature', 'Veteran'])
        
        # Barrier position categories
        df_features['barrier_position'] = pd.cut(df_features['barrier'], 
                                               bins=[0, 3, 8, 100], 
                                               labels=['Inside', 'Middle', 'Outside'])
        
        # Fill missing values
        numeric_columns = df_features.select_dtypes(include=[np.number]).columns
        df_features[numeric_columns] = df_features[numeric_columns].fillna(df_features[numeric_columns].median())
        
        # Encode categorical variables
        categorical_columns = ['course', 'jockey_name', 'trainer_name', 'age_group', 'barrier_position']
        for col in categorical_columns:
            if col in df_features.columns:
                df_features[col] = pd.Categorical(df_features[col]).codes
        
        return df_features
    
    def get_model_configurations(self) -> Dict[str, Dict]:
        """Get model configurations for parallel training."""
        return {
            'random_forest': {
                'model': RandomForestClassifier(random_state=self.random_state, n_jobs=1),
                'param_grid': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 15, 20, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'class_weight': ['balanced', None]
                },
                'search_type': 'grid'
            },
            'gradient_boosting': {
                'model': GradientBoostingClassifier(random_state=self.random_state),
                'param_grid': {
                    'n_estimators': [100, 200, 300],
                    'learning_rate': [0.05, 0.1, 0.15],
                    'max_depth': [3, 5, 7],
                    'subsample': [0.8, 0.9, 1.0]
                },
                'search_type': 'random'
            },
            'extra_trees': {
                'model': ExtraTreesClassifier(random_state=self.random_state, n_jobs=1),
                'param_grid': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 15, 20],
                    'min_samples_split': [2, 5, 10],
                    'class_weight': ['balanced', None]
                },
                'search_type': 'random'
            },
            'neural_network': {
                'model': MLPClassifier(random_state=self.random_state, max_iter=1000),
                'param_grid': {
                    'hidden_layer_sizes': [(100,), (100, 50), (150, 75), (200, 100)],
                    'alpha': [0.0001, 0.001, 0.01],
                    'learning_rate_init': [0.001, 0.01, 0.1],
                    'activation': ['relu', 'tanh']
                },
                'search_type': 'random'
            },
            'logistic_regression': {
                'model': LogisticRegression(random_state=self.random_state, max_iter=1000),
                'param_grid': {
                    'C': [0.1, 1.0, 10.0, 100.0],
                    'penalty': ['l1', 'l2'],
                    'solver': ['liblinear', 'saga'],
                    'class_weight': ['balanced', None]
                },
                'search_type': 'grid'
            },
            'svm': {
                'model': SVC(random_state=self.random_state, probability=True),
                'param_grid': {
                    'C': [0.1, 1.0, 10.0],
                    'kernel': ['rbf', 'linear'],
                    'gamma': ['scale', 'auto', 0.001, 0.01],
                    'class_weight': ['balanced', None]
                },
                'search_type': 'random'
            },
            'knn': {
                'model': KNeighborsClassifier(n_jobs=1),
                'param_grid': {
                    'n_neighbors': [3, 5, 7, 9, 11],
                    'weights': ['uniform', 'distance'],
                    'algorithm': ['auto', 'ball_tree', 'kd_tree'],
                    'p': [1, 2]
                },
                'search_type': 'grid'
            },
            'bagging': {
                'model': BaggingClassifier(random_state=self.random_state, n_jobs=1),
                'param_grid': {
                    'n_estimators': [50, 100, 200],
                    'max_samples': [0.5, 0.7, 1.0],
                    'max_features': [0.5, 0.7, 1.0],
                    'bootstrap': [True, False]
                },
                'search_type': 'random'
            }
        }
    
    def train_single_model(self, model_config: Tuple[str, Dict, np.ndarray, np.ndarray]) -> Dict:
        """Train a single model with hyperparameter optimization."""
        model_name, config, X_train, y_train = model_config
        
        start_time = time.time()
        logger.info(f"🔧 Training {model_name} with hyperparameter optimization...")
        
        try:
            # Create cross-validation strategy
            cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)
            
            # Choose search method
            if config['search_type'] == 'grid':
                search = GridSearchCV(
                    config['model'],
                    config['param_grid'],
                    cv=cv,
                    scoring='roc_auc',
                    n_jobs=1,  # Single job per model for parallel training
                    verbose=0
                )
            else:  # random search
                search = RandomizedSearchCV(
                    config['model'],
                    config['param_grid'],
                    n_iter=20,  # Limit iterations for faster training
                    cv=cv,
                    scoring='roc_auc',
                    n_jobs=1,
                    random_state=self.random_state,
                    verbose=0
                )
            
            # Fit the search
            search.fit(X_train, y_train)
            best_model = search.best_estimator_
            
            # Calculate training time
            training_time = time.time() - start_time
            
            # Get cross-validation scores for best model
            cv_scores = cross_val_score(best_model, X_train, y_train, cv=cv, scoring='roc_auc')
            
            result = {
                'model_name': model_name,
                'best_model': best_model,
                'best_params': search.best_params_,
                'best_cv_score': search.best_score_,
                'cv_scores': cv_scores,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'training_time': training_time,
                'search_type': config['search_type'],
                'n_params_tested': len(search.cv_results_['params'])
            }
            
            logger.info(f"✅ {model_name}: CV AUC={result['cv_mean']:.4f}±{result['cv_std']:.4f}, Time={training_time:.1f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ {model_name} training failed: {e}")
            return {
                'model_name': model_name,
                'error': str(e),
                'training_time': time.time() - start_time
            }
    
    def train_models_parallel(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> Dict:
        """Train multiple models in parallel with hyperparameter optimization."""
        logger.info("🚀 Starting parallel model training with hyperparameter optimization...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
        )
        
        logger.info(f"📊 Training set: {len(X_train):,} samples")
        logger.info(f"📊 Test set: {len(X_test):,} samples")
        logger.info(f"📊 Features: {X_train.shape[1]}")
        
        # Get model configurations
        model_configs = self.get_model_configurations()
        
        # Prepare arguments for parallel training
        training_args = [
            (name, config, X_train, y_train) 
            for name, config in model_configs.items()
        ]
        
        # Train models in parallel
        training_results = []
        failed_models = []
        
        with ProcessPoolExecutor(max_workers=min(len(model_configs), os.cpu_count())) as executor:
            # Submit all training jobs
            future_to_model = {
                executor.submit(self.train_single_model, args): args[0] 
                for args in training_args
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_model):
                model_name = future_to_model[future]
                try:
                    result = future.result()
                    if 'error' in result:
                        failed_models.append(result)
                    else:
                        training_results.append(result)
                except Exception as e:
                    logger.error(f"❌ Parallel training failed for {model_name}: {e}")
                    failed_models.append({'model_name': model_name, 'error': str(e)})
        
        # Evaluate all trained models on test set
        logger.info("📊 Evaluating trained models on test set...")
        
        final_results = {}
        for result in training_results:
            try:
                model_name = result['model_name']
                best_model = result['best_model']
                
                # Test set evaluation
                y_pred = best_model.predict(X_test)
                y_pred_proba = best_model.predict_proba(X_test)[:, 1]
                
                # Calculate comprehensive metrics
                test_metrics = {
                    'accuracy': accuracy_score(y_test, y_pred),
                    'precision': precision_score(y_test, y_pred, zero_division=0),
                    'recall': recall_score(y_test, y_pred, zero_division=0),
                    'f1_score': f1_score(y_test, y_pred, zero_division=0),
                    'roc_auc': roc_auc_score(y_test, y_pred_proba),
                }
                
                # Store comprehensive results
                final_results[model_name] = {
                    **result,
                    'test_metrics': test_metrics,
                    'feature_names': feature_names
                }
                
                # Store trained model
                self.trained_models[model_name] = best_model
                self.model_performance[model_name] = final_results[model_name]
                
                logger.info(f"📊 {model_name} test results: "
                          f"AUC={test_metrics['roc_auc']:.4f}, "
                          f"Accuracy={test_metrics['accuracy']:.4f}")
                
            except Exception as e:
                logger.error(f"❌ Test evaluation failed for {result['model_name']}: {e}")
                failed_models.append({'model_name': result['model_name'], 'error': str(e)})
        
        # Log summary
        logger.info(f"✅ Successfully trained {len(final_results)} models")
        if failed_models:
            logger.warning(f"⚠️ {len(failed_models)} models failed: {[m['model_name'] for m in failed_models]}")
        
        return {
            'successful_models': final_results,
            'failed_models': failed_models,
            'training_summary': {
                'total_models_attempted': len(model_configs),
                'successful_models': len(final_results),
                'failed_models': len(failed_models),
                'training_data_size': len(X_train),
                'test_data_size': len(X_test),
                'feature_count': X_train.shape[1]
            }
        }
    
    def create_ensemble_models(self, X_train: np.ndarray, y_train: np.ndarray, 
                              X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Create ensemble models from top performing individual models."""
        logger.info("🏆 Creating ensemble models from top performers...")
        
        if len(self.trained_models) < 3:
            logger.warning("⚠️ Need at least 3 models for ensemble creation")
            return {}
        
        # Rank models by cross-validation AUC
        model_rankings = sorted(
            [(name, perf['cv_mean']) for name, perf in self.model_performance.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        logger.info("📊 Model rankings by CV AUC:")
        for i, (name, cv_auc) in enumerate(model_rankings[:5], 1):
            logger.info(f"   {i}. {name}: {cv_auc:.4f}")
        
        ensemble_results = {}
        
        # Create different ensemble configurations
        ensemble_configs = [
            {'name': 'top_3_voting', 'models': model_rankings[:3], 'voting': 'soft'},
            {'name': 'top_5_voting', 'models': model_rankings[:5], 'voting': 'soft'},
            {'name': 'top_3_hard_voting', 'models': model_rankings[:3], 'voting': 'hard'},
            {'name': 'all_models_voting', 'models': model_rankings, 'voting': 'soft'}
        ]
        
        for config in ensemble_configs:
            try:
                if len(config['models']) < 3:
                    continue
                
                ensemble_name = config['name']
                logger.info(f"🔧 Creating {ensemble_name}...")
                
                # Prepare estimators for ensemble
                estimators = [
                    (name, self.trained_models[name]) 
                    for name, _ in config['models']
                ]
                
                # Create voting classifier
                ensemble = VotingClassifier(
                    estimators=estimators,
                    voting=config['voting']
                )
                
                # Train ensemble
                start_time = time.time()
                ensemble.fit(X_train, y_train)
                training_time = time.time() - start_time
                
                # Evaluate ensemble
                y_pred = ensemble.predict(X_test)
                if config['voting'] == 'soft':
                    y_pred_proba = ensemble.predict_proba(X_test)[:, 1]
                else:
                    # For hard voting, use average of individual model probabilities
                    y_pred_proba = np.mean([
                        self.trained_models[name].predict_proba(X_test)[:, 1]
                        for name, _ in config['models']
                    ], axis=0)
                
                # Calculate metrics
                test_metrics = {
                    'accuracy': accuracy_score(y_test, y_pred),
                    'precision': precision_score(y_test, y_pred, zero_division=0),
                    'recall': recall_score(y_test, y_pred, zero_division=0),
                    'f1_score': f1_score(y_test, y_pred, zero_division=0),
                    'roc_auc': roc_auc_score(y_test, y_pred_proba),
                }
                
                # Cross-validation for ensemble
                cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)
                cv_scores = cross_val_score(ensemble, X_train, y_train, cv=cv, scoring='roc_auc')
                
                ensemble_results[ensemble_name] = {
                    'ensemble_model': ensemble,
                    'test_metrics': test_metrics,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
                    'training_time': training_time,
                    'component_models': [name for name, _ in config['models']],
                    'voting_type': config['voting']
                }
                
                # Store ensemble
                self.ensemble_models[ensemble_name] = ensemble
                
                logger.info(f"✅ {ensemble_name}: CV AUC={cv_scores.mean():.4f}±{cv_scores.std():.4f}, "
                          f"Test AUC={test_metrics['roc_auc']:.4f}")
                
            except Exception as e:
                logger.error(f"❌ Failed to create {config['name']}: {e}")
        
        return ensemble_results
    
    def save_training_results(self, training_results: Dict, ensemble_results: Dict):
        """Save all training results, models, and metadata."""
        logger.info("💾 Saving training results and models...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save individual models
        models_subdir = self.models_dir / f"individual_models_{timestamp}"
        models_subdir.mkdir(exist_ok=True)
        
        for model_name, model in self.trained_models.items():
            model_path = models_subdir / f"{model_name}.joblib"
            joblib.dump(model, model_path)
            logger.info(f"💾 Saved {model_name} to {model_path}")
        
        # Save ensemble models
        if ensemble_results:
            ensemble_subdir = self.models_dir / f"ensemble_models_{timestamp}"
            ensemble_subdir.mkdir(exist_ok=True)
            
            for ensemble_name, ensemble_info in ensemble_results.items():
                ensemble_path = ensemble_subdir / f"{ensemble_name}.joblib"
                joblib.dump(ensemble_info['ensemble_model'], ensemble_path)
                logger.info(f"💾 Saved ensemble {ensemble_name} to {ensemble_path}")
        
        # Save preprocessing pipeline
        pipeline_path = self.models_dir / f"preprocessing_pipeline_{timestamp}.joblib"
        joblib.dump(self.preprocessing_pipeline, pipeline_path)
        
        # Save comprehensive metadata
        metadata = {
            'training_timestamp': timestamp,
            'training_results': {
                name: {
                    k: v for k, v in result.items() 
                    if k not in ['best_model', 'cv_scores']  # Exclude non-serializable
                }
                for name, result in training_results['successful_models'].items()
            },
            'ensemble_results': {
                name: {
                    k: v for k, v in result.items()
                    if k not in ['ensemble_model']  # Exclude non-serializable
                }
                for name, result in ensemble_results.items()
            },
            'training_summary': training_results['training_summary'],
            'failed_models': training_results['failed_models'],
            'cv_folds': self.cv_folds,
            'test_size': self.test_size,
            'random_state': self.random_state
        }
        
        metadata_path = self.models_dir / f"training_metadata_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"💾 Saved metadata to {metadata_path}")
        
        return {
            'models_dir': models_subdir,
            'ensemble_dir': ensemble_subdir if ensemble_results else None,
            'metadata_file': metadata_path,
            'pipeline_file': pipeline_path
        }
    
    def print_comprehensive_summary(self, training_results: Dict, ensemble_results: Dict):
        """Print comprehensive summary of training results."""
        print("🚀 Priority 3A: Parallel Model Training Complete")
        print("=" * 70)
        
        # Training summary
        summary = training_results['training_summary']
        print(f"\n📊 Training Summary:")
        print(f"   Models attempted: {summary['total_models_attempted']}")
        print(f"   Successful models: {summary['successful_models']}")
        print(f"   Failed models: {summary['failed_models']}")
        print(f"   Training samples: {summary['training_data_size']:,}")
        print(f"   Test samples: {summary['test_data_size']:,}")
        print(f"   Features: {summary['feature_count']:,}")
        
        # Individual model performance
        if training_results['successful_models']:
            print(f"\n🏆 Individual Model Performance (Top 5):")
            
            # Sort by test AUC
            sorted_models = sorted(
                training_results['successful_models'].items(),
                key=lambda x: x[1]['test_metrics']['roc_auc'],
                reverse=True
            )
            
            for i, (name, result) in enumerate(sorted_models[:5], 1):
                test_metrics = result['test_metrics']
                print(f"   {i}. {name:20}: "
                      f"AUC={test_metrics['roc_auc']:.4f}, "
                      f"Acc={test_metrics['accuracy']:.4f}, "
                      f"CV={result['cv_mean']:.4f}±{result['cv_std']:.4f}")
        
        # Ensemble performance
        if ensemble_results:
            print(f"\n🎭 Ensemble Model Performance:")
            
            sorted_ensembles = sorted(
                ensemble_results.items(),
                key=lambda x: x[1]['test_metrics']['roc_auc'],
                reverse=True
            )
            
            for i, (name, result) in enumerate(sorted_ensembles, 1):
                test_metrics = result['test_metrics']
                print(f"   {i}. {name:20}: "
                      f"AUC={test_metrics['roc_auc']:.4f}, "
                      f"Acc={test_metrics['accuracy']:.4f}, "
                      f"CV={result['cv_mean']:.4f}±{result['cv_std']:.4f}")
        
        # Performance insights
        print(f"\n💡 Performance Insights:")
        
        if training_results['successful_models']:
            best_individual = max(
                training_results['successful_models'].items(),
                key=lambda x: x[1]['test_metrics']['roc_auc']
            )
            print(f"   🥇 Best individual model: {best_individual[0]} "
                  f"(AUC: {best_individual[1]['test_metrics']['roc_auc']:.4f})")
        
        if ensemble_results:
            best_ensemble = max(
                ensemble_results.items(),
                key=lambda x: x[1]['test_metrics']['roc_auc']
            )
            print(f"   🏆 Best ensemble model: {best_ensemble[0]} "
                  f"(AUC: {best_ensemble[1]['test_metrics']['roc_auc']:.4f})")
        
        # Training efficiency
        if training_results['successful_models']:
            total_training_time = sum(
                result['training_time'] 
                for result in training_results['successful_models'].values()
            )
            print(f"   ⏱️ Total training time: {total_training_time:.1f} seconds")
            print(f"   🚀 Parallel efficiency achieved")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Deploy best performing model to production")
        print(f"   2. Set up model monitoring and retraining")
        print(f"   3. Integrate with live data feeds (Phase 2)")
        print(f"   4. A/B test different models in production")
    
    def run_complete_parallel_training(self) -> Dict:
        """Run the complete parallel model training pipeline."""
        logger.info("🚀 Starting Priority 3A: Complete Parallel Model Training...")
        
        start_time = time.time()
        
        try:
            # Load preprocessed data
            X, y, feature_names = self.load_preprocessed_data()
            
            # Split data for ensemble creation
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
            )
            
            # Train models in parallel
            training_results = self.train_models_parallel(X, y, feature_names)
            
            # Create ensemble models
            ensemble_results = self.create_ensemble_models(X_train, y_train, X_test, y_test)
            
            # Save all results
            saved_files = self.save_training_results(training_results, ensemble_results)
            
            # Calculate total execution time
            total_time = time.time() - start_time
            
            # Print comprehensive summary
            self.print_comprehensive_summary(training_results, ensemble_results)
            
            logger.info(f"🎉 Priority 3A: Parallel Model Training completed in {total_time:.1f} seconds")
            
            return {
                'success': True,
                'training_results': training_results,
                'ensemble_results': ensemble_results,
                'saved_files': saved_files,
                'execution_time': total_time,
                'models_trained': len(self.trained_models),
                'ensembles_created': len(self.ensemble_models)
            }
            
        except Exception as e:
            logger.error(f"❌ Parallel training failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time
            }


def main():
    """Run Priority 3A: Parallel Model Training Pipeline."""
    trainer = ParallelModelTrainer()
    results = trainer.run_complete_parallel_training()
    
    if results['success']:
        print(f"\n🎉 Priority 3A: Parallel Model Training Complete!")
        print(f"📊 Models trained: {results['models_trained']}")
        print(f"🎭 Ensembles created: {results['ensembles_created']}")
        print(f"⏱️ Execution time: {results['execution_time']:.1f} seconds")
        print(f"🚀 Ready for production deployment!")
    else:
        print(f"\n❌ Parallel training failed: {results['error']}")


if __name__ == "__main__":
    main()
