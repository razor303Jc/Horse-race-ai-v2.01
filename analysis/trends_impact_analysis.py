#!/usr/bin/env python3
"""
Race Trends Impact Analysis
Compares ML performance with and without race trends data to demonstrate the value of trends analysis.
"""

import os
import sys
import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import warnings

warnings.filterwarnings("ignore")

# Add project path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")

from race_trends_ml_integration import RaceTrendsMLIntegration
from advanced_ml_integration_system import AdvancedMLIntegrationSystem

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TrendsImpactAnalysis:
    """
    Analyzes the impact of race trends on ML performance by comparing:
    1. Pure ML models (existing advanced system)
    2. ML + Trends integration (enhanced system)
    """

    def __init__(self):
        # Initialize both systems
        self.pure_ml_system = AdvancedMLIntegrationSystem()
        self.trends_ml_system = RaceTrendsMLIntegration()

        logger.info("🔬 Trends Impact Analysis System initialized")

    def run_comparative_analysis(self, num_samples: int = 6000):
        """Run comprehensive comparison of ML vs ML+Trends"""
        logger.info("🚀 RACE TRENDS IMPACT ANALYSIS")
        logger.info("=" * 70)

        # Test 1: Pure ML System
        logger.info("\n📊 Testing Pure ML System...")
        pure_ml_results = self._test_pure_ml_system(num_samples)

        # Test 2: ML + Trends System
        logger.info("\n📈 Testing ML + Trends System...")
        trends_ml_results = self._test_trends_ml_system(num_samples)

        # Compare results
        logger.info("\n🔍 Analyzing Performance Impact...")
        impact_analysis = self._analyze_impact(pure_ml_results, trends_ml_results)

        # Display comprehensive comparison
        self._display_comprehensive_comparison(
            pure_ml_results, trends_ml_results, impact_analysis
        )

        logger.info("\n🎉 TRENDS IMPACT ANALYSIS COMPLETE!")

        return {
            "pure_ml": pure_ml_results,
            "trends_ml": trends_ml_results,
            "impact": impact_analysis,
        }

    def _test_pure_ml_system(self, num_samples: int) -> Dict[str, Any]:
        """Test pure ML system performance"""
        logger.info(f"🧠 Training pure ML models ({num_samples} samples)...")

        # Create standard dataset
        X, y = self.pure_ml_system.create_advanced_dataset(num_samples)

        # Train models
        results = self.pure_ml_system.train_advanced_models(X, y)

        # Test on sample race
        sample_race = self._create_test_race()
        enhanced_race_data = self._prepare_race_data_for_pure_ml(sample_race)
        predictions = self.pure_ml_system.predict_race(enhanced_race_data)

        return {
            "training_results": results,
            "race_predictions": predictions,
            "feature_count": X.shape[1],
            "dataset_size": num_samples,
        }

    def _test_trends_ml_system(self, num_samples: int) -> Dict[str, Any]:
        """Test ML + trends system performance"""
        logger.info(f"📈 Training ML + trends models ({num_samples} samples)...")

        # Create enhanced dataset with trends
        X_enhanced, y = self.trends_ml_system.create_enhanced_dataset(num_samples)

        # Train models
        results = self.trends_ml_system.train_enhanced_models(X_enhanced, y)

        # Test on sample race with trends analysis
        sample_race = self._create_test_race()
        race_trends, enhanced_predictions = (
            self.trends_ml_system.analyze_race_with_trends(sample_race)
        )

        return {
            "training_results": results,
            "race_trends": race_trends,
            "enhanced_predictions": enhanced_predictions,
            "feature_count": X_enhanced.shape[1],
            "dataset_size": num_samples,
        }

    def _analyze_impact(
        self, pure_ml: Dict[str, Any], trends_ml: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze the impact of adding trends data"""
        impact = {}

        # Performance improvements
        pure_best = max(
            pure_ml["training_results"]["model_results"].values(),
            key=lambda x: x["cv_auc"],
        )
        trends_best = max(
            trends_ml["training_results"]["model_results"].values(),
            key=lambda x: x["cv_auc"],
        )

        impact["auc_improvement"] = trends_best["cv_auc"] - pure_best["cv_auc"]
        impact["auc_improvement_pct"] = (
            impact["auc_improvement"] / pure_best["cv_auc"]
        ) * 100

        # Feature analysis
        impact["feature_increase"] = (
            trends_ml["feature_count"] - pure_ml["feature_count"]
        )
        impact["feature_increase_pct"] = (
            impact["feature_increase"] / pure_ml["feature_count"]
        ) * 100

        # Trends-specific features performance
        trends_features = []
        if "feature_importance" in trends_ml["training_results"]:
            for feature, importance in trends_ml["training_results"][
                "feature_importance"
            ].items():
                if "trend" in feature.lower():
                    trends_features.append((feature, importance))

        impact["trends_features"] = sorted(
            trends_features, key=lambda x: x[1], reverse=True
        )
        impact["trends_importance_total"] = sum(imp for _, imp in trends_features)

        # Prediction quality analysis
        impact["prediction_analysis"] = self._analyze_prediction_quality(
            pure_ml["race_predictions"], trends_ml["enhanced_predictions"]
        )

        return impact

    def _analyze_prediction_quality(
        self, pure_predictions, enhanced_predictions
    ) -> Dict[str, Any]:
        """Analyze prediction quality differences"""
        analysis = {}

        # Compare top picks confidence
        pure_top = pure_predictions[0] if pure_predictions else None
        enhanced_top = enhanced_predictions[0] if enhanced_predictions else None

        if pure_top and enhanced_top:
            analysis["top_pick_confidence_change"] = (
                enhanced_top.confidence_rating
                - getattr(pure_top, "composite_prediction", 0.5)
            )

            analysis["top_pick_prob_change"] = (
                enhanced_top.combined_win_probability - pure_top.win_probability
            )

        # Analyze spread of predictions
        pure_probs = [p.win_probability for p in pure_predictions[:5]]
        enhanced_probs = [p.combined_win_probability for p in enhanced_predictions[:5]]

        analysis["pure_prediction_spread"] = max(pure_probs) - min(pure_probs)
        analysis["enhanced_prediction_spread"] = max(enhanced_probs) - min(
            enhanced_probs
        )
        analysis["spread_change"] = (
            analysis["enhanced_prediction_spread"] - analysis["pure_prediction_spread"]
        )

        return analysis

    def _create_test_race(self) -> Dict[str, Any]:
        """Create consistent test race for comparison"""
        return {
            "race_name": "Trends Impact Test Race",
            "race_type": "handicap",
            "distance": "1m2f",
            "course": "Newmarket",
            "surface": "turf",
            "prize_money": 40000,
            "num_runners": 12,
        }

    def _prepare_race_data_for_pure_ml(self, race_data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare race data for pure ML system"""
        horses_data = []

        for i in range(12):
            horse_data = {
                "horse_name": f"TestHorse_{i+1}",
                "odds_decimal": 2.0 + (i * 2.0),
                "draw": i + 1,
                "weight_lbs": 130 - i,
                "jockey_skill": 90 - (i * 2),
                "trainer_skill": 88 - (i * 2),
                "age": np.random.choice([3, 4, 5, 6]),
                "days_since_last_run": np.random.choice([14, 21, 28]),
                "course_wins": np.random.choice([0, 1, 2]),
                "distance_wins": np.random.choice([0, 1, 2, 3]),
            }
            horses_data.append(horse_data)

        race_df = pd.DataFrame(horses_data)

        # Add required ML features
        race_df["power_rating"] = 85 - (race_df.index * 1.5)
        race_df["speed_rating"] = 88 - (race_df.index * 1.8)
        race_df["form_composite"] = 0.85 - (race_df.index * 0.04)
        race_df["pace_rating"] = 82 - (race_df.index * 1.2)
        race_df["class_rating"] = 90 - (race_df.index * 2)
        race_df["consistency_index"] = 0.8 - (race_df.index * 0.03)
        race_df["course_and_distance_wins"] = race_df["course_wins"] // 2
        race_df["track_condition_encoded"] = 2
        race_df["class_level"] = range(1, 13)
        race_df["distance_meters"] = 1600

        return race_df

    def _display_comprehensive_comparison(
        self, pure_ml: Dict[str, Any], trends_ml: Dict[str, Any], impact: Dict[str, Any]
    ):
        """Display comprehensive comparison results"""

        print("\n" + "=" * 80)
        print("🔬 COMPREHENSIVE TRENDS IMPACT ANALYSIS")
        print("=" * 80)

        # Performance comparison
        print(f"\n📊 PERFORMANCE COMPARISON")
        print("-" * 40)

        print(f"\n🧠 Pure ML System:")
        pure_results = pure_ml["training_results"]["model_results"]
        for name, result in pure_results.items():
            print(f"   {name}: {result['cv_auc']:.4f} ± {result['cv_std']:.4f}")

        print(f"\n📈 ML + Trends System:")
        trends_results = trends_ml["training_results"]["model_results"]
        for name, result in trends_results.items():
            print(f"   {name}: {result['cv_auc']:.4f} ± {result['cv_std']:.4f}")

        # Impact analysis
        print(f"\n🎯 IMPACT ANALYSIS")
        print("-" * 40)
        print(
            f"📈 AUC Improvement: +{impact['auc_improvement']:.4f} ({impact['auc_improvement_pct']:+.2f}%)"
        )
        print(
            f"🔢 Feature Count: {pure_ml['feature_count']} → {trends_ml['feature_count']} (+{impact['feature_increase']})"
        )
        print(f"📊 Feature Increase: +{impact['feature_increase_pct']:.1f}%")

        # Trends features analysis
        if impact["trends_features"]:
            print(f"\n📈 TRENDS FEATURES PERFORMANCE")
            print("-" * 40)
            print(
                f"🎯 Total Trends Importance: {impact['trends_importance_total']:.4f}"
            )
            print(f"🔍 Top Trends Features:")
            for feature, importance in impact["trends_features"][:5]:
                print(f"   • {feature}: {importance:.4f}")

        # Prediction quality comparison
        pred_analysis = impact["prediction_analysis"]
        if pred_analysis:
            print(f"\n🎯 PREDICTION QUALITY ANALYSIS")
            print("-" * 40)
            if "top_pick_prob_change" in pred_analysis:
                print(
                    f"🏆 Top Pick Probability Change: {pred_analysis['top_pick_prob_change']:+.1%}"
                )
            if "top_pick_confidence_change" in pred_analysis:
                print(
                    f"💫 Top Pick Confidence Change: {pred_analysis['top_pick_confidence_change']:+.1%}"
                )
            if "spread_change" in pred_analysis:
                print(
                    f"📊 Prediction Spread Change: {pred_analysis['spread_change']:+.1%}"
                )

        # Race-specific analysis
        if "race_trends" in trends_ml:
            race_trends = trends_ml["race_trends"]
            print(f"\n🏁 RACE-SPECIFIC TRENDS ANALYSIS")
            print("-" * 40)
            print(f"🎯 Overall Edge Score: {race_trends.overall_edge_score:.1%}")
            print(f"📊 Patterns Found: {race_trends.total_patterns_found}")

            if race_trends.age_trends:
                print(f"🎂 Age Trends: {len(race_trends.age_trends)} patterns")
            if race_trends.weight_trends:
                print(f"⚖️ Weight Trends: {len(race_trends.weight_trends)} patterns")
            if race_trends.draw_trends:
                print(f"🎯 Draw Trends: {len(race_trends.draw_trends)} patterns")
            if race_trends.form_trends:
                print(f"📊 Form Trends: {len(race_trends.form_trends)} patterns")

        # Sample predictions comparison
        print(f"\n🏆 SAMPLE PREDICTIONS COMPARISON")
        print("-" * 40)

        print(f"\n🧠 Pure ML Top 3:")
        for i, pred in enumerate(pure_ml["race_predictions"][:3], 1):
            print(f"   {i}. {pred.horse_name}: {pred.win_probability:.1%} win prob")

        print(f"\n📈 ML + Trends Top 3:")
        for i, pred in enumerate(trends_ml["enhanced_predictions"][:3], 1):
            print(
                f"   {i}. {pred.horse_name}: {pred.combined_win_probability:.1%} win prob "
                f"(ML: {pred.ml_win_probability:.1%}, Trends: {pred.trend_score:.1%})"
            )

        # Value assessment
        print(f"\n💰 VALUE ASSESSMENT")
        print("-" * 40)

        if impact["auc_improvement"] > 0:
            print(f"✅ POSITIVE IMPACT: Trends data improves ML performance")
            print(f"🎯 Recommendation: Use ML + Trends integration for better accuracy")
        else:
            print(
                f"⚠️ NEUTRAL/NEGATIVE IMPACT: Trends data doesn't significantly improve ML"
            )
            print(f"🎯 Recommendation: Evaluate trends quality or feature engineering")

        feature_efficiency = (
            impact["trends_importance_total"] / impact["feature_increase"]
            if impact["feature_increase"] > 0
            else 0
        )
        print(
            f"📊 Feature Efficiency: {feature_efficiency:.4f} (importance per new feature)"
        )

        if feature_efficiency > 0.01:
            print(
                f"✅ EFFICIENT: Trends features provide good importance per feature added"
            )
        else:
            print(f"⚠️ INEFFICIENT: Trends features add limited value per feature")

    def run_detailed_trends_analysis(self):
        """Run detailed analysis of specific trends patterns"""
        logger.info("\n🔍 DETAILED TRENDS PATTERN ANALYSIS")
        logger.info("=" * 60)

        # Create sample race with known patterns
        sample_race = {
            "race_name": "Pattern Analysis Race",
            "race_type": "handicap",
            "distance": "1m",
            "course": "Ascot",
            "surface": "turf",
        }

        # Generate historical data with strong patterns
        historical_data = self._generate_pattern_rich_historical_data()

        # Analyze with trends system
        race_trends, predictions = self.trends_ml_system.analyze_race_with_trends(
            sample_race, historical_data
        )

        self._display_detailed_trends_patterns(race_trends, predictions)

    def _generate_pattern_rich_historical_data(self) -> List[Dict[str, Any]]:
        """Generate historical data with clear patterns for analysis"""
        historical_races = []

        # Create 15 races with strong age pattern (4-5 year olds win)
        for i in range(15):
            race = {
                "race_id": f"pattern_race_{i+1}",
                "race_name": f"Pattern Race {i+1}",
                "race_type": "handicap",
                "distance": "1m",
                "course": "Ascot",
                "surface": "turf",
                "race_date": (datetime.now() - timedelta(days=15 + i * 14)).isoformat(),
                "participants": [],
            }

            # Add participants with winner having clear pattern
            for j in range(10):
                is_winner = j == 0

                participant = {
                    "horse_name": f"Horse_{i}_{j}",
                    "age": (
                        4 if is_winner else np.random.choice([3, 6, 7, 8])
                    ),  # Winners are age 4
                    "weight": (
                        120 if is_winner else np.random.normal(128, 5)
                    ),  # Winners carry light weight
                    "draw": (
                        np.random.randint(8, 12)
                        if is_winner
                        else np.random.randint(1, 7)
                    ),  # Winners from high draws
                    "odds": 3.0 + (j * 0.5),
                    "finish_position": j + 1,
                    "days_since_last_run": (
                        21 if is_winner else np.random.choice([7, 14, 35, 42])
                    ),
                    "last_run_result": "loss",  # No winner won last time
                    "course_wins": (
                        1 if (is_winner and i < 8) else 0
                    ),  # 8/15 winners had course form
                    "course_runs": 1 if is_winner else np.random.choice([0, 1]),
                    "distance_wins": (
                        1 if (is_winner and i < 12) else 0
                    ),  # 12/15 had distance form
                    "distance_runs": 2 if is_winner else np.random.choice([0, 1, 2]),
                }
                race["participants"].append(participant)

            historical_races.append(race)

        return historical_races

    def _display_detailed_trends_patterns(self, race_trends, predictions):
        """Display detailed analysis of trends patterns"""

        print(f"\n🎯 DETAILED TRENDS PATTERN ANALYSIS")
        print("-" * 50)

        print(f"\n📊 Race: {race_trends.race_name}")
        print(f"🎯 Overall Edge Score: {race_trends.overall_edge_score:.1%}")
        print(f"📈 Total Patterns: {race_trends.total_patterns_found}")

        # Display all trend categories
        trend_categories = [
            ("🎂 Age Trends", race_trends.age_trends),
            ("⚖️ Weight Trends", race_trends.weight_trends),
            ("🎯 Draw Trends", race_trends.draw_trends),
            ("📊 Form Trends", race_trends.form_trends),
            ("💰 Price Trends", race_trends.price_trends),
            ("🏁 Course Form", race_trends.course_form_trends),
            ("📏 Distance Form", race_trends.distance_form_trends),
        ]

        for category_name, trends in trend_categories:
            if trends:
                print(f"\n{category_name}:")
                for trend in trends:
                    confidence_stars = "⭐" * min(5, int(trend.confidence * 5))
                    print(
                        f"   {confidence_stars} {trend.pattern} ({trend.confidence:.1%} confidence)"
                    )

        print(f"\n🏆 PATTERN-BASED PREDICTIONS")
        print("-" * 30)

        for i, pred in enumerate(predictions[:5], 1):
            print(f"\n{i}. {pred.horse_name}")
            print(f"   📈 Trends Score: {pred.trend_score:.1%}")
            print(f"   🎯 Combined Probability: {pred.combined_win_probability:.1%}")
            print(f"   🏅 Tier: {pred.prediction_tier}")

            if pred.matching_patterns:
                print(f"   ✅ Matches: {', '.join(pred.matching_patterns[:2])}")


def main():
    """Run comprehensive trends impact analysis"""
    analyzer = TrendsImpactAnalysis()

    # Run comparative analysis
    results = analyzer.run_comparative_analysis(num_samples=5000)

    # Run detailed patterns analysis
    analyzer.run_detailed_trends_analysis()


if __name__ == "__main__":
    main()
