#!/usr/bin/env python3
"""
Time-Aware ML Training Optimizer
Horse Racing AI v2.04 - Intelligent Training Cycle Management

Manages ML model training with performance optimization, ensemble weighting,
and critical time constraints for race deadlines.

Features:
- Performance analysis after each training cycle
- Dynamic ensemble weight optimization
- Time-constraint management (first race deadline)
- Iterative improvement cycles
- Early stopping when time runs out
- Model performance tracking and comparison
"""

import sys
import os
import time
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import subprocess
import pickle

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TimeAwareMLOptimizer:
    """
    Manages ML training cycles with performance optimization and time constraints.
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else project_root
        self.models_dir = self.base_path / "models"
        self.results_dir = self.base_path / "results"
        self.config_dir = self.base_path / "config"
        
        # Training configuration
        self.training_config = self._load_training_config()
        
        # Performance tracking
        self.performance_history = []
        self.current_cycle = 0
        self.best_performance = None
        self.best_models = {}
        
        # Time management
        self.training_start_time = None
        self.first_race_time = None
        self.time_buffer_minutes = 30  # Safety buffer before first race
        
        # Ensure directories exist
        self.models_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
    
    def _load_training_config(self) -> Dict[str, Any]:
        """Load ML training configuration."""
        config_file = self.config_dir / "ml_training_config.yaml"
        
        # Default configuration
        default_config = {
            "max_training_cycles": 5,
            "min_improvement_threshold": 0.01,
            "ensemble_methods": ["random_forest", "xgboost", "lightgbm", "neural_network"],
            "optimization_metrics": ["accuracy", "precision", "recall", "f1_score", "roc_auc"],
            "hyperparameter_search": True,
            "early_stopping_patience": 2,
            "time_per_cycle_minutes": 45,
            "minimum_training_time_minutes": 120
        }
        
        if config_file.exists():
            try:
                import yaml
                with open(config_file, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Failed to load training config: {e}. Using defaults.")
        
        return default_config
    
    def get_first_race_time(self) -> Optional[datetime]:
        """Get the time of the first race today."""
        try:
            # Check database for today's races
            result = subprocess.run([
                "docker", "exec", "-it", "horse_racing_postgres_clean",
                "psql", "-U", "horse_racing", "-d", "horse_racing_db",
                "-c", "SELECT MIN(race_time) FROM races WHERE race_date = CURRENT_DATE;"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                # Parse the race time from output
                lines = output.split('\n')
                for line in lines:
                    if ':' in line and len(line.strip()) > 0:
                        try:
                            race_time_str = line.strip()
                            # Convert to today's datetime
                            today = datetime.now().date()
                            race_time = datetime.strptime(f"{today} {race_time_str}", "%Y-%m-%d %H:%M:%S")
                            return race_time
                        except ValueError:
                            continue
            
            # Fallback: assume first race at 13:00 if not found
            today = datetime.now().date()
            return datetime.combine(today, datetime.strptime("13:00", "%H:%M").time())
            
        except Exception as e:
            logger.error(f"Failed to get first race time: {e}")
            # Default fallback
            today = datetime.now().date()
            return datetime.combine(today, datetime.strptime("13:00", "%H:%M").time())
    
    def calculate_available_training_time(self) -> int:
        """Calculate available training time in minutes."""
        if not self.first_race_time:
            self.first_race_time = self.get_first_race_time()
        
        now = datetime.now()
        deadline = self.first_race_time - timedelta(minutes=self.time_buffer_minutes)
        
        if deadline <= now:
            logger.warning("Already past training deadline!")
            return 0
        
        available_minutes = int((deadline - now).total_seconds() / 60)
        logger.info(f"Available training time: {available_minutes} minutes until {deadline}")
        
        return available_minutes
    
    def estimate_cycle_duration(self) -> int:
        """Estimate how long one training cycle will take."""
        base_time = self.training_config.get("time_per_cycle_minutes", 45)
        
        # Adjust based on data size and methods
        num_methods = len(self.training_config.get("ensemble_methods", []))
        hyperparameter_search = self.training_config.get("hyperparameter_search", True)
        
        estimated_time = base_time * num_methods
        if hyperparameter_search:
            estimated_time *= 1.5  # Hyperparameter search adds time
        
        return int(estimated_time)
    
    def can_start_new_cycle(self) -> bool:
        """Check if there's enough time to start a new training cycle."""
        available_time = self.calculate_available_training_time()
        estimated_cycle_time = self.estimate_cycle_duration()
        
        logger.info(f"Available: {available_time}min, Estimated cycle: {estimated_cycle_time}min")
        
        return available_time >= estimated_cycle_time
    
    def run_training_cycle(self) -> Dict[str, Any]:
        """Run one complete ML training cycle."""
        cycle_start = time.time()
        logger.info(f"🚀 Starting training cycle {self.current_cycle + 1}")
        
        cycle_results = {
            "cycle": self.current_cycle + 1,
            "start_time": datetime.now(),
            "models": {},
            "ensemble_performance": {},
            "optimizations": {}
        }
        
        try:
            # 1. Train individual models
            for method in self.training_config["ensemble_methods"]:
                logger.info(f"Training {method} model...")
                model_results = self._train_model(method)
                cycle_results["models"][method] = model_results
            
            # 2. Optimize ensemble weights
            logger.info("Optimizing ensemble weights...")
            ensemble_weights = self._optimize_ensemble_weights(cycle_results["models"])
            cycle_results["ensemble_weights"] = ensemble_weights
            
            # 3. Evaluate ensemble performance
            logger.info("Evaluating ensemble performance...")
            ensemble_performance = self._evaluate_ensemble(cycle_results["models"], ensemble_weights)
            cycle_results["ensemble_performance"] = ensemble_performance
            
            # 4. Performance analysis and optimization suggestions
            optimizations = self._analyze_performance_and_suggest_optimizations(cycle_results)
            cycle_results["optimizations"] = optimizations
            
            cycle_results["duration_minutes"] = (time.time() - cycle_start) / 60
            cycle_results["end_time"] = datetime.now()
            
            logger.info(f"✅ Cycle {self.current_cycle + 1} completed in {cycle_results['duration_minutes']:.1f} minutes")
            
        except Exception as e:
            logger.error(f"❌ Training cycle failed: {e}")
            cycle_results["error"] = str(e)
            cycle_results["duration_minutes"] = (time.time() - cycle_start) / 60
        
        return cycle_results
    
    def _train_model(self, method: str) -> Dict[str, Any]:
        """Train a single model using specified method."""
        model_results = {
            "method": method,
            "training_time": 0,
            "performance_metrics": {},
            "hyperparameters": {},
            "model_path": None
        }
        
        try:
            # Run the ML training script for this method
            training_start = time.time()
            
            result = subprocess.run([
                "python", "scripts/train_ml_model.py",
                "--method", method,
                "--cycle", str(self.current_cycle + 1),
                "--optimize-hyperparameters" if self.training_config.get("hyperparameter_search") else "--no-optimize",
                "--output-dir", str(self.models_dir)
            ], cwd=self.base_path, capture_output=True, text=True, timeout=3600)  # 1 hour timeout
            
            model_results["training_time"] = time.time() - training_start
            
            if result.returncode == 0:
                # Parse training results
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if "Performance:" in line:
                        # Extract performance metrics
                        try:
                            metrics_str = line.split("Performance:")[1].strip()
                            metrics = json.loads(metrics_str)
                            model_results["performance_metrics"] = metrics
                        except:
                            pass
                    elif "Model saved:" in line:
                        model_path = line.split("Model saved:")[1].strip()
                        model_results["model_path"] = model_path
                
                logger.info(f"✅ {method} training completed")
            else:
                logger.error(f"❌ {method} training failed: {result.stderr}")
                model_results["error"] = result.stderr
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {method} training timed out")
            model_results["error"] = "Training timeout"
        except Exception as e:
            logger.error(f"❌ {method} training error: {e}")
            model_results["error"] = str(e)
        
        return model_results
    
    def _optimize_ensemble_weights(self, models: Dict[str, Any]) -> Dict[str, float]:
        """Optimize ensemble weights based on individual model performance."""
        weights = {}
        total_score = 0
        
        # Calculate weights based on performance
        for method, model_result in models.items():
            if "performance_metrics" in model_result and model_result["performance_metrics"]:
                # Use F1 score as primary metric, fallback to accuracy
                score = model_result["performance_metrics"].get("f1_score", 
                       model_result["performance_metrics"].get("accuracy", 0))
            else:
                score = 0
            
            weights[method] = max(score, 0.1)  # Minimum weight of 0.1
            total_score += weights[method]
        
        # Normalize weights
        if total_score > 0:
            for method in weights:
                weights[method] = weights[method] / total_score
        else:
            # Equal weights if no valid scores
            equal_weight = 1.0 / len(models)
            weights = {method: equal_weight for method in models.keys()}
        
        logger.info(f"Ensemble weights: {weights}")
        return weights
    
    def _evaluate_ensemble(self, models: Dict[str, Any], weights: Dict[str, float]) -> Dict[str, float]:
        """Evaluate ensemble performance with optimized weights."""
        # This would normally run ensemble prediction on validation set
        # For now, calculate weighted average of individual performances
        
        ensemble_metrics = {}
        metrics_to_aggregate = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
        
        for metric in metrics_to_aggregate:
            weighted_sum = 0
            total_weight = 0
            
            for method, model_result in models.items():
                if ("performance_metrics" in model_result and 
                    metric in model_result["performance_metrics"]):
                    weight = weights.get(method, 0)
                    value = model_result["performance_metrics"][metric]
                    weighted_sum += weight * value
                    total_weight += weight
            
            if total_weight > 0:
                ensemble_metrics[metric] = weighted_sum / total_weight
            else:
                ensemble_metrics[metric] = 0
        
        logger.info(f"Ensemble performance: {ensemble_metrics}")
        return ensemble_metrics
    
    def _analyze_performance_and_suggest_optimizations(self, cycle_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance and suggest optimizations for next cycle."""
        optimizations = {
            "performance_trend": "unknown",
            "suggested_changes": [],
            "model_rankings": {},
            "continue_training": True
        }
        
        current_performance = cycle_results["ensemble_performance"]
        
        # Compare with previous cycles
        if self.performance_history:
            previous_performance = self.performance_history[-1]["ensemble_performance"]
            
            # Calculate improvement
            improvement = {}
            for metric in current_performance:
                if metric in previous_performance:
                    improvement[metric] = current_performance[metric] - previous_performance[metric]
            
            avg_improvement = np.mean(list(improvement.values()))
            
            if avg_improvement > self.training_config.get("min_improvement_threshold", 0.01):
                optimizations["performance_trend"] = "improving"
                optimizations["suggested_changes"].append("Continue current approach")
            elif avg_improvement < -self.training_config.get("min_improvement_threshold", 0.01):
                optimizations["performance_trend"] = "declining"
                optimizations["suggested_changes"].extend([
                    "Reduce learning rate",
                    "Increase regularization",
                    "Try different feature engineering"
                ])
            else:
                optimizations["performance_trend"] = "stable"
                optimizations["suggested_changes"].extend([
                    "Try different hyperparameters",
                    "Add more diverse models to ensemble"
                ])
        
        # Rank models by performance
        model_scores = {}
        for method, model_result in cycle_results["models"].items():
            if "performance_metrics" in model_result:
                score = model_result["performance_metrics"].get("f1_score", 0)
                model_scores[method] = score
        
        optimizations["model_rankings"] = dict(sorted(model_scores.items(), key=lambda x: x[1], reverse=True))
        
        # Check if we should continue training
        if len(self.performance_history) >= self.training_config.get("early_stopping_patience", 2):
            recent_improvements = []
            for i in range(1, min(3, len(self.performance_history) + 1)):
                if i < len(self.performance_history):
                    prev_perf = self.performance_history[-i]["ensemble_performance"].get("f1_score", 0)
                    curr_perf = current_performance.get("f1_score", 0)
                    recent_improvements.append(curr_perf - prev_perf)
            
            if all(imp <= 0 for imp in recent_improvements):
                optimizations["continue_training"] = False
                optimizations["suggested_changes"].append("Early stopping - no improvement detected")
        
        return optimizations
    
    def save_cycle_results(self, cycle_results: Dict[str, Any]):
        """Save cycle results for analysis and tracking."""
        # Update performance history
        self.performance_history.append(cycle_results)
        
        # Update best performance
        current_f1 = cycle_results["ensemble_performance"].get("f1_score", 0)
        if self.best_performance is None or current_f1 > self.best_performance.get("f1_score", 0):
            self.best_performance = cycle_results["ensemble_performance"]
            # Save best models
            for method, model_result in cycle_results["models"].items():
                if "model_path" in model_result:
                    self.best_models[method] = model_result["model_path"]
        
        # Save to file
        results_file = self.results_dir / f"training_cycle_{cycle_results['cycle']}.json"
        with open(results_file, 'w') as f:
            # Convert datetime objects for JSON serialization
            serializable_results = self._make_json_serializable(cycle_results)
            json.dump(serializable_results, f, indent=2)
        
        # Save overall training summary
        summary = {
            "total_cycles": len(self.performance_history),
            "best_performance": self.best_performance,
            "best_models": self.best_models,
            "performance_history": [r["ensemble_performance"] for r in self.performance_history],
            "training_start": self.training_start_time.isoformat() if self.training_start_time else None,
            "first_race_time": self.first_race_time.isoformat() if self.first_race_time else None
        }
        
        summary_file = self.results_dir / "training_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable format."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj
    
    def run_optimization_cycles(self) -> Dict[str, Any]:
        """Run multiple training cycles with optimization until time runs out."""
        self.training_start_time = datetime.now()
        self.first_race_time = self.get_first_race_time()
        
        logger.info(f"""
╭─────────────────────────────────────────╮
│        ML Training Optimization        │
│                                         │
│  🕐 Training Start: {self.training_start_time.strftime('%H:%M:%S')}           │
│  🏁 First Race:     {self.first_race_time.strftime('%H:%M:%S')}           │
│  ⏱️  Available Time: {self.calculate_available_training_time()} minutes        │
│                                         │
│  Starting intelligent training cycles  │
╰─────────────────────────────────────────╯
        """)
        
        final_results = {
            "training_completed": False,
            "cycles_completed": 0,
            "total_training_time": 0,
            "final_performance": {},
            "best_performance": {},
            "time_constrained": False,
            "optimization_summary": {}
        }
        
        try:
            max_cycles = self.training_config.get("max_training_cycles", 5)
            min_training_time = self.training_config.get("minimum_training_time_minutes", 120)
            
            # Check if we have minimum training time
            available_time = self.calculate_available_training_time()
            if available_time < min_training_time:
                logger.warning(f"⚠️  Only {available_time} minutes available, less than minimum {min_training_time} minutes")
                final_results["time_constrained"] = True
            
            # Run training cycles
            while (self.current_cycle < max_cycles and 
                   self.can_start_new_cycle()):
                
                cycle_results = self.run_training_cycle()
                self.save_cycle_results(cycle_results)
                
                self.current_cycle += 1
                final_results["cycles_completed"] = self.current_cycle
                
                # Check if we should continue based on optimization analysis
                if ("optimizations" in cycle_results and 
                    not cycle_results["optimizations"].get("continue_training", True)):
                    logger.info("🛑 Early stopping triggered by optimization analysis")
                    break
                
                # Show progress
                remaining_time = self.calculate_available_training_time()
                logger.info(f"📊 Cycle {self.current_cycle} complete. Time remaining: {remaining_time} minutes")
            
            # Final summary
            if self.performance_history:
                final_results["training_completed"] = True
                final_results["final_performance"] = self.performance_history[-1]["ensemble_performance"]
                final_results["best_performance"] = self.best_performance
                
                total_time = (datetime.now() - self.training_start_time).total_seconds() / 60
                final_results["total_training_time"] = total_time
                
                # Optimization summary
                improvements = []
                for i in range(1, len(self.performance_history)):
                    prev_f1 = self.performance_history[i-1]["ensemble_performance"].get("f1_score", 0)
                    curr_f1 = self.performance_history[i]["ensemble_performance"].get("f1_score", 0)
                    improvements.append(curr_f1 - prev_f1)
                
                final_results["optimization_summary"] = {
                    "total_improvement": improvements[-1] if improvements else 0,
                    "average_cycle_improvement": np.mean(improvements) if improvements else 0,
                    "best_cycle": np.argmax([r["ensemble_performance"].get("f1_score", 0) for r in self.performance_history]) + 1,
                    "training_efficiency": final_results["best_performance"].get("f1_score", 0) / total_time if total_time > 0 else 0
                }
            
            logger.info(f"""
╭─────────────────────────────────────────╮
│         Training Complete! 🎉          │
│                                         │
│  Cycles Completed: {final_results['cycles_completed']}                   │
│  Training Time: {final_results.get('total_training_time', 0):.1f} minutes         │
│  Best F1 Score: {final_results.get('best_performance', {}).get('f1_score', 0):.4f}            │
│  Final F1 Score: {final_results.get('final_performance', {}).get('f1_score', 0):.4f}           │
│                                         │
│  Models ready for race predictions!    │
╰─────────────────────────────────────────╯
            """)
            
        except Exception as e:
            logger.error(f"❌ Training optimization failed: {e}")
            final_results["error"] = str(e)
        
        return final_results


def main():
    """Main function to run ML training optimization."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Time-Aware ML Training Optimizer")
    parser.add_argument("--base-path", default=None, help="Base project path")
    parser.add_argument("--first-race-time", default=None, help="First race time (HH:MM)")
    parser.add_argument("--max-cycles", type=int, default=5, help="Maximum training cycles")
    parser.add_argument("--dry-run", action="store_true", help="Show time calculations only")
    
    args = parser.parse_args()
    
    optimizer = TimeAwareMLOptimizer(base_path=args.base_path)
    
    # Override first race time if provided
    if args.first_race_time:
        try:
            today = datetime.now().date()
            race_time = datetime.strptime(f"{today} {args.first_race_time}", "%Y-%m-%d %H:%M")
            optimizer.first_race_time = race_time
        except ValueError:
            logger.error(f"Invalid race time format: {args.first_race_time}. Use HH:MM")
            return 1
    
    # Override max cycles if provided
    if args.max_cycles:
        optimizer.training_config["max_training_cycles"] = args.max_cycles
    
    if args.dry_run:
        # Show time calculations only
        optimizer.first_race_time = optimizer.get_first_race_time()
        available_time = optimizer.calculate_available_training_time()
        estimated_cycle_time = optimizer.estimate_cycle_duration()
        max_possible_cycles = available_time // estimated_cycle_time
        
        print(f"""
Time Analysis:
- First race time: {optimizer.first_race_time}
- Available training time: {available_time} minutes
- Estimated time per cycle: {estimated_cycle_time} minutes
- Maximum possible cycles: {max_possible_cycles}
- Buffer time: {optimizer.time_buffer_minutes} minutes
        """)
        return 0
    
    # Run optimization cycles
    results = optimizer.run_optimization_cycles()
    
    # Return appropriate exit code
    return 0 if results.get("training_completed", False) else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
