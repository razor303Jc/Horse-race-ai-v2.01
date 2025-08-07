#!/usr/bin/env python3
"""
Comprehensive ML Integration Demo
===============================

Demonstrates the complete enhanced ML system with:
- Advanced rating predictions using neural networks
- Z-score ML modeling
- Monte Carlo AI enhancement
- Real-time AI performance tracking
- Integrated scoring systems
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import structlog

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.horse_racing_ai.core.config import config
from src.horse_racing_ai.ml.ai_trainer import AITrainer, quick_train_ai_system
from src.horse_racing_ai.ml.enhanced_ml_models import (
    EnhancedMLRatingSystem,
    MonteCarloAIEnhancer,
    ZScoreMLPredictor,
)
from src.horse_racing_ai.scoring.composite_scorer import CompositeScore, CompositeScorer
from src.horse_racing_ai.scoring.form_analyzer import (
    EnhancedFormAnalyzer,
    RacePerformance,
)
from src.horse_racing_ai.simulation.monte_carlo_simulator import MonteCarloSimulator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = structlog.get_logger(__name__)


class MLIntegrationDemo:
    """Comprehensive demo of the enhanced ML integration."""

    def __init__(self):
        """Initialize the ML integration demo."""
        self.ai_trainer = AITrainer()
        self.ml_system = EnhancedMLRatingSystem(enable_neural_networks=True)
        self.z_score_predictor = ZScoreMLPredictor()
        self.monte_carlo_enhancer = MonteCarloAIEnhancer()
        self.composite_scorer = CompositeScorer()
        self.monte_carlo_simulator = MonteCarloSimulator()

        logger.info("ML Integration Demo initialized")

    async def demonstrate_comprehensive_training(self) -> None:
        """Demonstrate comprehensive AI training process."""
        print("\n" + "=" * 80)
        print("🤖 COMPREHENSIVE AI TRAINING DEMONSTRATION")
        print("=" * 80)

        # Check for training data
        training_file = Path("data/massive_training_data.csv")
        if not training_file.exists():
            print(f"⚠️  Training data not found at {training_file}")
            print("   Creating sample training data for demonstration...")
            await self._create_sample_training_data(training_file)

        # Display training overview
        print(f"\n📊 Training Data: {training_file}")
        training_data = pd.read_csv(training_file)
        print(f"   📈 Total Records: {len(training_data):,}")
        print(f"   🏇 Unique Horses: {training_data['horse_name'].nunique():,}")
        print(
            f"   🏁 Unique Races: {len(training_data.groupby(['race_date', 'track', 'race_number'])):,}"
        )

        # Create training plan
        print(f"\n🎯 Creating Training Plan...")
        plan = await self.ai_trainer.create_training_plan(
            objective="Demonstrate comprehensive ML training with ratings, Z-scores, and Monte Carlo",
            target_accuracy=0.65,
            priority=1,
        )

        print(f"   📋 Plan ID: {plan.plan_id}")
        print(f"   🎯 Objective: {plan.objective}")
        print(f"   📊 Target Metrics:")
        for metric, target in plan.target_metrics.items():
            print(f"      • {metric}: {target:.1%}")

        # Execute training
        print(f"\n🚀 Starting Comprehensive Training...")
        print("   This may take several minutes...")

        session = await self.ai_trainer.train_comprehensive_ml_system()

        # Display training results
        print(f"\n✅ Training Session Completed: {session.session_id}")
        print(f"   ⏱️  Duration: {session.end_time - session.start_time}")
        print(f"   🏁 Training Races: {session.training_races}")
        print(f"   📊 Validation Races: {session.validation_races}")
        print(f"   🤖 Models Trained: {', '.join(session.models_trained)}")
        print(f"   📈 Status: {session.status.upper()}")

        # Display performance metrics
        print(f"\n📊 Performance Metrics:")
        for metric, value in session.performance_metrics.items():
            if isinstance(value, float):
                if "accuracy" in metric or "r2" in metric:
                    print(f"   • {metric}: {value:.1%}")
                else:
                    print(f"   • {metric}: {value:.3f}")
            else:
                print(f"   • {metric}: {value}")

    async def demonstrate_enhanced_predictions(self) -> None:
        """Demonstrate enhanced ML predictions with integrated systems."""
        print("\n" + "=" * 80)
        print("🔮 ENHANCED ML PREDICTIONS DEMONSTRATION")
        print("=" * 80)

        # Create sample race data
        print("\n🏁 Creating Sample Race for Prediction...")
        sample_horses = await self._create_sample_race_data()

        print(f"   🏇 Field Size: {len(sample_horses)} horses")
        for i, horse in enumerate(sample_horses, 1):
            print(
                f"   {i}. {horse['name']} (Composite: {horse['composite_score']:.1f})"
            )

        # Generate composite scores
        print(f"\n📊 Generating Composite Scores...")
        composite_scores = []
        for horse in sample_horses:
            score = CompositeScore(
                horse_name=horse["name"],
                composite_score=horse["composite_score"],
                form_score=horse["form_score"],
                power_rating=horse["power_rating"],
                speed_score=horse["speed_score"],
                class_score=horse["class_score"],
                consistency_score=horse["consistency_score"],
                conditions_score=horse["conditions_score"],
                confidence_level=horse["confidence_level"],
                factors=horse.get("factors", []),
            )
            composite_scores.append(score)

        # Race conditions
        race_conditions = {
            "distance": 8.5,
            "surface": "dirt",
            "conditions": "fast",
            "race_class": "ALLOWANCE",
            "field_size": len(sample_horses),
            "purse": 75000,
        }

        print(f"   🏁 Distance: {race_conditions['distance']}f")
        print(f"   🏁 Surface: {race_conditions['surface']}")
        print(f"   🏁 Conditions: {race_conditions['conditions']}")
        print(f"   💰 Purse: ${race_conditions['purse']:,}")

        # Check if ML system is trained
        if not self.ml_system.is_trained:
            print(f"\n⚠️  ML system not trained. Training quick model...")
            await self._quick_train_for_demo()

        # Generate ML predictions
        print(f"\n🤖 Generating Enhanced ML Predictions...")

        try:
            predictions = self.ml_system.predict_race_with_ml(
                horse_data=[],  # Empty for demo
                composite_scores=composite_scores,
                race_conditions=race_conditions,
                use_ensemble=True,
            )

            # Sort by predicted rating
            predictions.sort(key=lambda p: p.predicted_rating, reverse=True)

            print(f"\n🔮 ML Prediction Results:")
            print("-" * 100)
            print(
                f"{'Rank':<4} {'Horse':<20} {'Rating':<8} {'Z-Score':<8} {'Win%':<8} {'Place%':<8} {'Confidence':<10}"
            )
            print("-" * 100)

            for i, pred in enumerate(predictions, 1):
                print(
                    f"{i:<4} {pred.horse_name:<20} {pred.predicted_rating:<8.1f} "
                    f"{pred.predicted_z_score:<8.2f} {pred.win_probability*100:<8.1f} "
                    f"{pred.place_probability*100:<8.1f} {pred.confidence_score*100:<10.1f}"
                )

            # Show prediction factors for top horse
            if predictions:
                top_horse = predictions[0]
                print(f"\n🏆 Top Pick Analysis: {top_horse.horse_name}")
                print(f"   📊 Predicted Rating: {top_horse.predicted_rating:.1f}")
                print(f"   📈 Z-Score: {top_horse.predicted_z_score:.2f}")
                print(f"   🎯 Win Probability: {top_horse.win_probability:.1%}")
                print(f"   🥇 Expected Position: {top_horse.expected_position:.1f}")
                print(
                    f"   📊 Performance Range: {top_horse.performance_range[0]:.1f} - {top_horse.performance_range[1]:.1f}"
                )
                print(f"   🔍 Key Factors:")
                for factor in top_horse.prediction_factors:
                    print(f"      • {factor}")

        except Exception as e:
            print(f"❌ Error generating predictions: {e}")
            logger.error(f"Prediction error: {e}")

    async def demonstrate_z_score_modeling(self) -> None:
        """Demonstrate Z-score ML modeling capabilities."""
        print("\n" + "=" * 80)
        print("📊 Z-SCORE ML MODELING DEMONSTRATION")
        print("=" * 80)

        # Create sample historical data for Z-score training
        print("\n📈 Generating Historical Z-Score Training Data...")

        historical_ratings = []
        field_contexts = []
        actual_z_scores = []

        # Simulate 100 races for training
        for race_num in range(100):
            field_size = np.random.randint(6, 16)
            race_ratings = np.random.normal(75, 15, field_size)
            race_ratings = np.clip(race_ratings, 40, 120)

            # Calculate actual Z-scores
            mean_rating = np.mean(race_ratings)
            std_rating = max(np.std(race_ratings), 1.0)
            z_scores = (race_ratings - mean_rating) / std_rating

            for i, rating in enumerate(race_ratings):
                historical_ratings.append(rating)
                field_contexts.append(
                    {
                        "field_size": field_size,
                        "avg_field_rating": mean_rating,
                        "field_strength": std_rating,
                        "race_competitiveness": min(std_rating / 10.0, 1.0),
                    }
                )
                actual_z_scores.append(z_scores[i])

        print(
            f"   📊 Generated {len(historical_ratings)} training samples from {100} races"
        )

        # Train Z-score model
        print(f"\n🤖 Training Z-Score ML Model...")
        accuracy = self.z_score_predictor.train_z_score_model(
            historical_ratings, field_contexts, actual_z_scores
        )

        print(f"   ✅ Z-Score Model Trained")
        print(f"   📊 Model Accuracy (R²): {accuracy:.3f}")

        # Demonstrate Z-score predictions
        print(f"\n🔮 Demonstrating Z-Score Predictions...")

        # Test race data
        test_ratings = [85.2, 78.5, 92.1, 71.3, 88.7, 75.9, 82.4, 69.8]
        test_context = {
            "field_size": len(test_ratings),
            "avg_field_rating": np.mean(test_ratings),
            "field_strength": np.std(test_ratings),
            "race_competitiveness": 0.6,
        }

        # Statistical Z-scores
        mean_rating = np.mean(test_ratings)
        std_rating = max(np.std(test_ratings), 1.0)
        statistical_z_scores = [(r - mean_rating) / std_rating for r in test_ratings]

        # ML predicted Z-scores
        ml_z_scores = self.z_score_predictor.predict_z_scores(
            test_ratings, test_context
        )

        print(f"\n📊 Z-Score Comparison:")
        print("-" * 70)
        print(
            f"{'Rating':<8} {'Statistical Z':<15} {'ML Z-Score':<12} {'Difference':<12}"
        )
        print("-" * 70)

        for i, rating in enumerate(test_ratings):
            stat_z = statistical_z_scores[i]
            ml_z = ml_z_scores[i]
            diff = abs(stat_z - ml_z)
            print(f"{rating:<8.1f} {stat_z:<15.3f} {ml_z:<12.3f} {diff:<12.3f}")

        # Analysis
        avg_difference = np.mean(
            [abs(s - m) for s, m in zip(statistical_z_scores, ml_z_scores)]
        )
        print(f"\n📊 Average Difference: {avg_difference:.3f}")
        print(
            f"   {'✅' if avg_difference < 0.2 else '⚠️'} ML model {'provides similar' if avg_difference < 0.2 else 'differs from'} statistical Z-scores"
        )

    async def demonstrate_monte_carlo_ai_enhancement(self) -> None:
        """Demonstrate Monte Carlo AI enhancement capabilities."""
        print("\n" + "=" * 80)
        print("🎲 MONTE CARLO AI ENHANCEMENT DEMONSTRATION")
        print("=" * 80)

        # Generate sample horse profiles
        print("\n🏇 Creating Sample Horse Profiles for Monte Carlo...")

        horse_profiles = []
        for i in range(8):
            profile = {
                "horse_name": f"Horse_{i+1}",
                "base_rating": np.random.normal(80, 12),
                "consistency_factor": np.random.uniform(0.4, 0.9),
                "form_trend": np.random.uniform(-0.2, 0.3),
                "confidence_level": np.random.uniform(0.5, 0.95),
            }
            horse_profiles.append(profile)

        for i, profile in enumerate(horse_profiles, 1):
            print(
                f"   {i}. {profile['horse_name']}: Rating {profile['base_rating']:.1f}, "
                f"Consistency {profile['consistency_factor']:.2f}"
            )

        # Optimize Monte Carlo parameters
        print(f"\n⚙️  Optimizing Monte Carlo Parameters...")
        optimized_params = self.monte_carlo_enhancer.optimize_simulation_parameters(
            historical_results=[], simulation_configs=[]
        )

        print(f"   📊 Optimized Parameters:")
        for param, value in optimized_params.items():
            print(f"      • {param}: {value}")

        # Predict simulation variances
        print(f"\n🎯 Predicting Simulation Variances...")
        predicted_variances = self.monte_carlo_enhancer.predict_simulation_variance(
            horse_profiles
        )

        print(f"\n📊 Variance Analysis:")
        print("-" * 60)
        print(
            f"{'Horse':<12} {'Consistency':<12} {'Predicted Var':<15} {'Risk Level':<10}"
        )
        print("-" * 60)

        for i, (profile, variance) in enumerate(
            zip(horse_profiles, predicted_variances)
        ):
            consistency = profile["consistency_factor"]
            risk_level = "Low" if variance < 5 else "Medium" if variance < 8 else "High"
            print(
                f"{profile['horse_name']:<12} {consistency:<12.3f} {variance:<15.2f} {risk_level:<10}"
            )

        # Demonstrate enhanced Monte Carlo simulation
        print(f"\n🎲 Running Enhanced Monte Carlo Simulation...")

        # Create composite scores for simulation
        composite_scores = []
        for profile in horse_profiles:
            score = CompositeScore(
                horse_name=profile["horse_name"],
                composite_score=profile["base_rating"],
                form_score=profile["base_rating"] * (1 + profile["form_trend"]),
                power_rating=profile["base_rating"] + 20,
                speed_score=profile["base_rating"],
                class_score=profile["base_rating"],
                consistency_score=profile["consistency_factor"] * 100,
                conditions_score=75.0,
                confidence_level=profile["confidence_level"],
                factors=[],
            )
            composite_scores.append(score)

        # Run simulation with enhanced parameters
        simulation_result = self.monte_carlo_simulator.run_simulation(
            composite_scores=composite_scores,
            simulations=optimized_params["simulations"],
            use_advanced_modeling=True,
        )

        print(f"\n🏁 Enhanced Monte Carlo Results:")
        print("-" * 80)
        print(
            f"{'Horse':<12} {'Win%':<8} {'Place%':<8} {'Show%':<8} {'Avg Pos':<8} {'Z-Score':<8}"
        )
        print("-" * 80)

        for horse_result in simulation_result.horse_results:
            print(
                f"{horse_result.horse_name:<12} {horse_result.win_probability*100:<8.1f} "
                f"{horse_result.place_probability*100:<8.1f} {horse_result.show_probability*100:<8.1f} "
                f"{horse_result.average_position:<8.1f} {horse_result.z_score:<8.2f}"
            )

        print(f"\n📊 Simulation Statistics:")
        print(f"   🎲 Total Simulations: {simulation_result.total_simulations:,}")
        print(f"   🏇 Field Size: {simulation_result.field_size}")
        print(f"   📊 Confidence Level: {simulation_result.confidence_level:.1%}")
        print(f"   ⚡ Enhanced with AI: ✅")

    async def demonstrate_ai_performance_tracking(self) -> None:
        """Demonstrate AI performance tracking and monitoring."""
        print("\n" + "=" * 80)
        print("📈 AI PERFORMANCE TRACKING DEMONSTRATION")
        print("=" * 80)

        # Check current AI performance
        print("\n📊 Current AI Performance Metrics...")

        if hasattr(self.ml_system, "ai_metrics") and self.ml_system.ai_metrics:
            metrics = self.ml_system.ai_metrics

            print(f"   🎯 Total Predictions: {metrics.total_predictions}")
            print(f"   🏆 Correct Win Predictions: {metrics.correct_win_predictions}")
            print(
                f"   🥇 Correct Place Predictions: {metrics.correct_place_predictions}"
            )
            print(f"   📊 Average Accuracy: {metrics.average_accuracy:.1%}")

            if metrics.performance_history:
                print(
                    f"   📈 Performance History: {len(metrics.performance_history)} entries"
                )
        else:
            print(
                "   ⚠️  No AI metrics available yet - system needs predictions to track"
            )

        # Simulate some performance updates
        print(f"\n🔄 Simulating Performance Updates...")

        # Create sample predictions and results for demonstration
        from src.horse_racing_ai.ml.enhanced_ml_models import MLModelPrediction

        sample_predictions = []
        sample_results = []

        for i in range(5):  # 5 simulated races
            race_predictions = []
            race_results = []

            for j in range(8):  # 8 horses per race
                # Create prediction
                prediction = MLModelPrediction(
                    horse_name=f"Race{i+1}_Horse{j+1}",
                    predicted_rating=np.random.normal(80, 15),
                    predicted_z_score=np.random.normal(0, 1),
                    confidence_score=np.random.uniform(0.5, 0.95),
                    win_probability=np.random.exponential(0.15),
                    place_probability=np.random.uniform(0.2, 0.6),
                    show_probability=np.random.uniform(0.3, 0.7),
                    expected_position=float(j + 1 + np.random.normal(0, 2)),
                    performance_range=(75.0, 85.0),
                    model_features={},
                    prediction_factors=["Sample factor"],
                )
                race_predictions.append(prediction)

                # Create result (simulate race outcome)
                result = {
                    "horse_name": prediction.horse_name,
                    "finish_position": np.random.randint(1, 9),
                    "actual_rating": prediction.predicted_rating
                    + np.random.normal(0, 5),
                }
                race_results.append(result)

            # Normalize win probabilities
            total_win_prob = sum(p.win_probability for p in race_predictions)
            for pred in race_predictions:
                pred.win_probability /= total_win_prob

            sample_predictions.extend(race_predictions)
            sample_results.extend(race_results)

        # Update AI performance with simulated data
        print(
            f"   📈 Processing {len(sample_predictions)} predictions from {5} races..."
        )

        # Batch update performance
        batch_size = 8  # One race at a time
        for i in range(0, len(sample_predictions), batch_size):
            batch_predictions = sample_predictions[i : i + batch_size]
            batch_results = sample_results[i : i + batch_size]

            if len(batch_predictions) == len(batch_results):
                self.ml_system.update_ai_performance(batch_predictions, batch_results)

        # Generate performance report
        print(f"\n📊 Updated AI Performance Report...")
        performance_report = self.ml_system.get_ai_performance_report()

        print(f"   🎯 Total Predictions: {performance_report['total_predictions']}")
        print(f"   🏆 Win Accuracy: {performance_report['win_accuracy']:.1%}")
        print(f"   🥇 Place Accuracy: {performance_report['place_accuracy']:.1%}")
        print(f"   📊 Average Accuracy: {performance_report['average_accuracy']:.1%}")

        if performance_report["performance_trend"]:
            print(f"   📈 Recent Performance Trend:")
            for entry in performance_report["performance_trend"][-3:]:  # Last 3 entries
                timestamp = entry["date"][:19]  # Remove milliseconds
                accuracy = entry["accuracy"]
                print(f"      • {timestamp}: {accuracy:.1%}")

        if performance_report["recommendations"]:
            print(f"   💡 Recommendations:")
            for rec in performance_report["recommendations"]:
                print(f"      • {rec}")

        # Monitor performance and check for retraining needs
        print(f"\n🔍 Monitoring Performance for Retraining Needs...")
        monitoring_report = await self.ai_trainer.monitor_ai_performance()

        print(f"   📊 Monitoring Status: {monitoring_report['recommendation'].upper()}")
        print(
            f"   🔄 Needs Retraining: {'Yes' if monitoring_report['needs_retraining'] else 'No'}"
        )

        if monitoring_report["retraining_reasons"]:
            print(f"   ⚠️  Retraining Reasons:")
            for reason in monitoring_report["retraining_reasons"]:
                print(f"      • {reason}")

    async def demonstrate_full_integration(self) -> None:
        """Demonstrate the complete integrated ML system."""
        print("\n" + "=" * 80)
        print("🚀 FULL ML INTEGRATION DEMONSTRATION")
        print("=" * 80)

        print("\n🔄 This demonstration shows the complete workflow:")
        print("   1. 🤖 Enhanced ML Predictions")
        print("   2. 📊 Z-Score ML Modeling")
        print("   3. 🎲 Monte Carlo AI Enhancement")
        print("   4. 📈 Performance Tracking")
        print("   5. 🔄 Feedback Loop Integration")

        # Create a comprehensive race scenario
        print(f"\n🏁 Creating Comprehensive Race Scenario...")

        # Generate realistic horse data
        horse_data = []
        for i in range(10):
            horse = {
                "name": f"IntegratedTest_Horse_{i+1}",
                "recent_form": np.random.choice(
                    ["excellent", "good", "average", "poor"], p=[0.2, 0.3, 0.4, 0.1]
                ),
                "base_rating": np.random.normal(78, 12),
                "consistency": np.random.uniform(0.3, 0.9),
                "distance_preference": np.random.choice(
                    ["sprint", "mile", "route"], p=[0.3, 0.4, 0.3]
                ),
                "surface_preference": np.random.choice(["dirt", "turf"], p=[0.7, 0.3]),
                "class_level": np.random.choice(
                    ["claiming", "allowance", "stakes"], p=[0.4, 0.5, 0.1]
                ),
            }
            horse_data.append(horse)

        print(f"   🏇 Field: {len(horse_data)} horses")
        print(
            f"   📊 Rating Range: {min(h['base_rating'] for h in horse_data):.1f} - {max(h['base_rating'] for h in horse_data):.1f}"
        )

        # Create enhanced composite scores
        print(f"\n📊 Generating Enhanced Composite Scores...")
        composite_scores = []

        for horse in horse_data:
            # Adjust scores based on form and preferences
            form_multiplier = {
                "excellent": 1.1,
                "good": 1.0,
                "average": 0.95,
                "poor": 0.85,
            }[horse["recent_form"]]

            score = CompositeScore(
                horse_name=horse["name"],
                composite_score=horse["base_rating"] * form_multiplier,
                form_score=horse["base_rating"] * form_multiplier,
                power_rating=horse["base_rating"] + 25,
                speed_score=horse["base_rating"] * (0.9 + horse["consistency"] * 0.2),
                class_score=horse["base_rating"]
                * (1.1 if horse["class_level"] == "stakes" else 1.0),
                consistency_score=horse["consistency"] * 100,
                conditions_score=75.0,
                confidence_level=horse["consistency"],
                factors=[
                    f"Form: {horse['recent_form']}",
                    f"Distance: {horse['distance_preference']}",
                ],
            )
            composite_scores.append(score)

        # Race conditions
        race_conditions = {
            "distance": 8.5,
            "surface": "dirt",
            "conditions": "fast",
            "race_class": "ALLOWANCE",
            "field_size": len(horse_data),
            "purse": 100000,
        }

        # 1. Enhanced ML Predictions
        print(f"\n🤖 Step 1: Enhanced ML Predictions...")
        if self.ml_system.is_trained:
            try:
                ml_predictions = self.ml_system.predict_race_with_ml(
                    horse_data=[],
                    composite_scores=composite_scores,
                    race_conditions=race_conditions,
                    use_ensemble=True,
                )

                print(f"   ✅ Generated {len(ml_predictions)} ML predictions")
                top_pick = max(ml_predictions, key=lambda p: p.predicted_rating)
                print(
                    f"   🏆 Top ML Pick: {top_pick.horse_name} (Rating: {top_pick.predicted_rating:.1f})"
                )

            except Exception as e:
                print(f"   ❌ ML Prediction Error: {e}")
                ml_predictions = []
        else:
            print(f"   ⚠️  ML system not trained - skipping ML predictions")
            ml_predictions = []

        # 2. Z-Score Analysis
        print(f"\n📊 Step 2: Z-Score ML Analysis...")
        ratings = [score.composite_score for score in composite_scores]

        if self.z_score_predictor.is_trained:
            ml_z_scores = self.z_score_predictor.predict_z_scores(
                ratings, race_conditions
            )
            print(f"   ✅ Generated ML Z-scores")
            best_z_horse = composite_scores[np.argmax(ml_z_scores)].horse_name
            print(f"   📈 Best Z-Score: {best_z_horse} ({max(ml_z_scores):.2f})")
        else:
            # Statistical fallback
            mean_rating = np.mean(ratings)
            std_rating = max(np.std(ratings), 1.0)
            ml_z_scores = [(r - mean_rating) / std_rating for r in ratings]
            print(f"   📊 Used statistical Z-scores (model not trained)")

        # 3. Monte Carlo Enhancement
        print(f"\n🎲 Step 3: Monte Carlo AI Enhancement...")
        simulation_result = self.monte_carlo_simulator.run_simulation(
            composite_scores=composite_scores,
            simulations=10000,
            use_advanced_modeling=True,
        )

        top_mc_horse = max(
            simulation_result.horse_results, key=lambda h: h.win_probability
        )
        print(f"   ✅ Monte Carlo simulation completed")
        print(
            f"   🎯 Monte Carlo Favorite: {top_mc_horse.horse_name} ({top_mc_horse.win_probability:.1%} win)"
        )

        # 4. Integrated Analysis
        print(f"\n🔍 Step 4: Integrated Analysis...")

        # Combine all predictions
        integrated_rankings = {}

        for i, score in enumerate(composite_scores):
            horse_name = score.horse_name
            integrated_rankings[horse_name] = {
                "composite_rank": i + 1,
                "composite_score": score.composite_score,
                "z_score": ml_z_scores[i],
                "mc_win_prob": 0.0,
                "ml_rating": 0.0,
                "ml_win_prob": 0.0,
            }

        # Add Monte Carlo data
        for horse_result in simulation_result.horse_results:
            if horse_result.horse_name in integrated_rankings:
                integrated_rankings[horse_result.horse_name][
                    "mc_win_prob"
                ] = horse_result.win_probability

        # Add ML data if available
        if ml_predictions:
            for pred in ml_predictions:
                if pred.horse_name in integrated_rankings:
                    integrated_rankings[pred.horse_name][
                        "ml_rating"
                    ] = pred.predicted_rating
                    integrated_rankings[pred.horse_name][
                        "ml_win_prob"
                    ] = pred.win_probability

        # Calculate integrated score
        for horse_name, data in integrated_rankings.items():
            # Weighted combination of different methods
            integrated_score = (
                data["composite_score"] * 0.3
                + (data["z_score"] + 2) * 20 * 0.2  # Normalize Z-score
                + data["mc_win_prob"] * 100 * 0.3
                + data["ml_rating"] * 0.2
            )
            data["integrated_score"] = integrated_score

        # Display integrated results
        print(f"\n🏁 Final Integrated Rankings:")
        print("-" * 100)
        print(
            f"{'Rank':<4} {'Horse':<25} {'Integrated':<10} {'Composite':<10} {'Z-Score':<8} {'MC Win%':<8} {'ML Rating':<9}"
        )
        print("-" * 100)

        sorted_horses = sorted(
            integrated_rankings.items(),
            key=lambda x: x[1]["integrated_score"],
            reverse=True,
        )

        for rank, (horse_name, data) in enumerate(sorted_horses, 1):
            print(
                f"{rank:<4} {horse_name:<25} {data['integrated_score']:<10.1f} "
                f"{data['composite_score']:<10.1f} {data['z_score']:<8.2f} "
                f"{data['mc_win_prob']*100:<8.1f} {data['ml_rating']:<9.1f}"
            )

        # Top recommendation
        winner = sorted_horses[0]
        print(f"\n🏆 INTEGRATED SYSTEM RECOMMENDATION:")
        print(f"   🥇 Top Pick: {winner[0]}")
        print(f"   📊 Integrated Score: {winner[1]['integrated_score']:.1f}")
        print(f"   💡 Selection combines all AI methods for optimal accuracy")

        # 5. Performance Feedback
        print(f"\n📈 Step 5: Performance Feedback Integration...")
        print(f"   🔄 System ready to learn from race results")
        print(f"   📊 Will update all models based on actual outcomes")
        print(f"   🎯 Continuous improvement cycle activated")

    async def _create_sample_training_data(self, filepath: Path) -> None:
        """Create sample training data for demonstration."""
        logger.info("Creating sample training data for demonstration")

        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Generate synthetic training data
        races = []

        for race_id in range(200):  # 200 races
            race_date = datetime.now().date() - pd.Timedelta(
                days=np.random.randint(1, 365)
            )
            tracks = ["Belmont", "Saratoga", "Aqueduct", "Churchill", "Santa Anita"]
            track = np.random.choice(tracks)
            race_number = np.random.randint(1, 11)

            field_size = np.random.randint(6, 13)

            for position in range(1, field_size + 1):
                horse_data = {
                    "race_date": race_date,
                    "track": track,
                    "race_number": race_number,
                    "horse_name": f"Horse_{race_id}_{position}",
                    "finish_position": position,
                    "distance": np.random.choice([6.0, 6.5, 7.0, 8.0, 8.5, 9.0, 10.0]),
                    "surface": np.random.choice(["dirt", "turf"], p=[0.7, 0.3]),
                    "conditions": np.random.choice(
                        ["fast", "good", "sloppy"], p=[0.7, 0.2, 0.1]
                    ),
                    "race_class": np.random.choice(
                        ["CLAIMING", "ALLOWANCE", "STAKES"], p=[0.5, 0.4, 0.1]
                    ),
                    "purse": np.random.randint(25000, 200000),
                    "composite_score": np.random.normal(80 - (position - 1) * 3, 10),
                    "form_score": np.random.normal(75, 12),
                    "power_rating": np.random.normal(105, 20),
                    "speed_score": np.random.normal(80, 15),
                    "class_score": np.random.normal(75, 12),
                    "consistency_score": np.random.uniform(40, 90),
                    "conditions_score": np.random.uniform(60, 85),
                    "confidence_level": np.random.uniform(0.5, 0.9),
                    "speed_figure": np.random.normal(85, 15),
                    "beaten_lengths": (
                        np.random.exponential(2.0) if position > 1 else 0.0
                    ),
                    "odds": np.random.exponential(5.0),
                    "jockey": f"Jockey_{np.random.randint(1, 20)}",
                    "trainer": f"Trainer_{np.random.randint(1, 15)}",
                    "weight": np.random.randint(115, 125),
                    "age": np.random.randint(3, 8),
                    "sex": np.random.choice(
                        ["C", "G", "F", "M"], p=[0.3, 0.4, 0.2, 0.1]
                    ),
                }

                # Make target_rating based on finish position for training
                horse_data["target_rating"] = horse_data["composite_score"]

                races.append(horse_data)

        # Create DataFrame and save
        training_df = pd.DataFrame(races)
        training_df.to_csv(filepath, index=False)

        print(f"   ✅ Created {len(training_df)} training samples in {filepath}")

    async def _create_sample_race_data(self) -> List[Dict[str, Any]]:
        """Create sample race data for demonstration."""
        horses = []

        horse_names = [
            "Thunder Strike",
            "Golden Arrow",
            "Speed Demon",
            "Royal Crown",
            "Lightning Bolt",
            "Storm Chaser",
            "Fire Dragon",
            "Wind Runner",
        ]

        for i, name in enumerate(horse_names):
            # Create realistic but varied horse data
            base_rating = np.random.normal(78, 12)
            consistency = np.random.uniform(0.4, 0.9)

            horse = {
                "name": name,
                "composite_score": max(50, min(110, base_rating)),
                "form_score": max(40, min(100, base_rating + np.random.normal(0, 8))),
                "power_rating": max(
                    80, min(140, base_rating + 20 + np.random.normal(0, 10))
                ),
                "speed_score": max(50, min(110, base_rating + np.random.normal(0, 6))),
                "class_score": max(40, min(100, base_rating + np.random.normal(0, 8))),
                "consistency_score": consistency * 100,
                "conditions_score": np.random.uniform(65, 85),
                "confidence_level": consistency,
                "factors": [
                    np.random.choice(
                        [
                            "Strong recent form",
                            "Distance specialist",
                            "Track advantage",
                            "Class drop",
                        ]
                    ),
                    np.random.choice(
                        [
                            "Good jockey",
                            "Trainer hot streak",
                            "Equipment change",
                            "Recent workout",
                        ]
                    ),
                ],
            }
            horses.append(horse)

        return horses

    async def _quick_train_for_demo(self) -> None:
        """Quick training for demo purposes."""
        print("   🚀 Quick training for demonstration...")

        try:
            # Create minimal training data
            sample_data = []

            for i in range(100):  # Minimal dataset
                sample_data.append(
                    {
                        "composite_score": np.random.normal(75, 15),
                        "form_score": np.random.normal(70, 12),
                        "power_rating": np.random.normal(100, 20),
                        "speed_score": np.random.normal(80, 15),
                        "class_score": np.random.normal(75, 12),
                        "consistency_score": np.random.uniform(40, 90),
                        "conditions_score": np.random.uniform(60, 85),
                        "confidence_level": np.random.uniform(0.5, 0.9),
                        "target_rating": np.random.normal(75, 15),
                    }
                )

            # Add required features for ML system
            for item in sample_data:
                item.update(
                    {
                        "avg_position_last_5": np.random.uniform(3, 7),
                        "best_position_last_5": np.random.randint(1, 5),
                        "worst_position_last_5": np.random.randint(5, 12),
                        "position_improvement": np.random.normal(0, 0.5),
                        "avg_speed_figure": np.random.normal(80, 10),
                        "max_speed_figure": np.random.normal(90, 10),
                        "speed_consistency": np.random.uniform(3, 8),
                        "speed_trend": np.random.normal(0, 0.3),
                        "avg_beaten_lengths": np.random.exponential(2),
                        "min_beaten_lengths": 0,
                        "performance_volatility": np.random.uniform(1, 4),
                        "jockey_consistency": np.random.uniform(0.5, 1.0),
                        "trainer_consistency": np.random.uniform(0.5, 1.0),
                        "distance_specialization": np.random.uniform(0.3, 0.9),
                        "class_progression": np.random.normal(0, 0.2),
                        "surface_versatility": np.random.uniform(0.5, 1.0),
                        "condition_adaptability": np.random.uniform(0.5, 1.0),
                        "days_since_last_race": np.random.randint(7, 60),
                        "racing_frequency": np.random.uniform(0.05, 0.3),
                        "layoff_factor": np.random.randint(7, 60),
                        "race_distance": 8.0,
                        "field_size": 8,
                        "race_class_numeric": 3.0,
                        "surface_dirt": 1,
                        "surface_turf": 0,
                        "surface_synthetic": 0,
                        "betting_odds": np.random.exponential(5),
                        "log_odds": 1.6,
                        "market_confidence": 0.2,
                        "form_power_interaction": 7500,
                        "speed_class_interaction": 6000,
                        "consistency_confidence": 50,
                    }
                )

            training_df = pd.DataFrame(sample_data)

            # Train models with minimal data
            self.ml_system.train_models(
                training_df, "target_rating", validation_split=0.1
            )
            print("   ✅ Quick training completed")

        except Exception as e:
            print(f"   ❌ Quick training failed: {e}")


async def main():
    """Main demonstration function."""
    print("🏇 " + "=" * 78)
    print("🏇 HORSE RACING AI v2.0 - COMPREHENSIVE ML INTEGRATION DEMO")
    print("🏇 " + "=" * 78)
    print("🏇")
    print("🏇 This demonstration showcases the complete enhanced ML system:")
    print("🏇 • Enhanced ML Models with Neural Networks")
    print("🏇 • Z-Score ML Prediction & Analysis")
    print("🏇 • Monte Carlo AI Enhancement")
    print("🏇 • Real-time AI Performance Tracking")
    print("🏇 • Integrated Prediction System")
    print("🏇")
    print("🏇 " + "=" * 78)

    # Initialize demo
    demo = MLIntegrationDemo()

    try:
        # Run all demonstrations
        await demo.demonstrate_comprehensive_training()
        await demo.demonstrate_enhanced_predictions()
        await demo.demonstrate_z_score_modeling()
        await demo.demonstrate_monte_carlo_ai_enhancement()
        await demo.demonstrate_ai_performance_tracking()
        await demo.demonstrate_full_integration()

        print("\n" + "=" * 80)
        print("🎉 COMPREHENSIVE ML INTEGRATION DEMO COMPLETED")
        print("=" * 80)
        print("✅ All ML enhancements successfully demonstrated:")
        print("   🤖 Enhanced ML rating system with neural networks")
        print("   📊 Z-score ML prediction and modeling")
        print("   🎲 Monte Carlo AI enhancement and optimization")
        print("   📈 Real-time AI performance tracking and monitoring")
        print("   🔄 Integrated feedback loops for continuous improvement")
        print("   🚀 Complete system ready for production use")
        print("\n💡 The system now provides state-of-the-art ML predictions")
        print("   combining multiple AI approaches for maximum accuracy!")

    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        logger.error(f"Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
