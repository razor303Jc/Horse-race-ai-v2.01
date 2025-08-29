#!/usr/bin/env python3
"""
Race Trends ML Integration System
Combines race trends analysis with advanced ML models for enhanced prediction accuracy.
Integrates trends data with form scoring, power ratings, speed analysis, pace analysis, and Monte Carlo simulation.
"""

import os
import sys
import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import warnings

warnings.filterwarnings("ignore")

# Add project path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")

# Import existing advanced ML system
from advanced_ml_integration_system import AdvancedMLIntegrationSystem

# Import race trends analyzer
try:
    from src.horse_racing_ai.analysis.race_trends_analyzer import (
        RaceTrendsAnalyzer,
        RaceTrend,
        RaceAnalysisTrends,
        HorseTrendScore,
    )
except ImportError:
    # Create simplified versions if not available
    @dataclass
    class RaceTrend:
        trend_type: str
        pattern: str
        percentage: float
        sample_size: int
        confidence: float
        edge_value: float
        last_updated: str

    @dataclass
    class RaceAnalysisTrends:
        race_name: str
        race_type: str
        distance: str
        course: str
        surface: str
        age_trends: List[RaceTrend]
        weight_trends: List[RaceTrend]
        draw_trends: List[RaceTrend]
        form_trends: List[RaceTrend]
        price_trends: List[RaceTrend]
        seasonal_trends: List[RaceTrend]
        course_form_trends: List[RaceTrend]
        distance_form_trends: List[RaceTrend]
        overall_edge_score: float
        total_patterns_found: int
        analysis_date: str

    @dataclass
    class HorseTrendScore:
        horse_name: str
        trend_scores: Dict[str, float]
        overall_trend_score: float
        matching_patterns: List[str]
        edge_factors: List[str]
        confidence: float
        recommendation: str

    class RaceTrendsAnalyzer:
        def __init__(self):
            self.min_sample_size = 10
            self.confidence_threshold = 0.7
            self.edge_threshold = 0.15

        def analyze_race_trends(
            self, race_data: Dict[str, Any], historical_races: List[Dict[str, Any]]
        ) -> RaceAnalysisTrends:
            # Simplified implementation for demo
            return self._create_demo_trends(race_data)

        def score_horse_trends(
            self, horse_data: Dict[str, Any], race_trends: RaceAnalysisTrends
        ) -> HorseTrendScore:
            # Simplified scoring
            return self._create_demo_horse_score(horse_data)

        def _create_demo_trends(self, race_data: Dict[str, Any]) -> RaceAnalysisTrends:
            """Create demonstration trends"""
            age_trends = [
                RaceTrend(
                    "age",
                    "10/12 winners aged 4-5 years",
                    83.3,
                    12,
                    0.9,
                    0.65,
                    datetime.now().isoformat(),
                )
            ]
            weight_trends = [
                RaceTrend(
                    "weight",
                    "8/12 winners carried 9st 2lbs or less",
                    66.7,
                    12,
                    0.85,
                    0.5,
                    datetime.now().isoformat(),
                )
            ]
            draw_trends = [
                RaceTrend(
                    "draw",
                    "7/10 winners from high draws",
                    70.0,
                    10,
                    0.8,
                    0.4,
                    datetime.now().isoformat(),
                )
            ]
            form_trends = [
                RaceTrend(
                    "form",
                    "0/12 winners won last time",
                    0.0,
                    12,
                    0.95,
                    0.7,
                    datetime.now().isoformat(),
                )
            ]

            return RaceAnalysisTrends(
                race_name=race_data.get("race_name", "Demo Race"),
                race_type="handicap",
                distance="1m2f",
                course="Goodwood",
                surface="turf",
                age_trends=age_trends,
                weight_trends=weight_trends,
                draw_trends=draw_trends,
                form_trends=form_trends,
                price_trends=[],
                seasonal_trends=[],
                course_form_trends=[],
                distance_form_trends=[],
                overall_edge_score=0.65,
                total_patterns_found=4,
                analysis_date=datetime.now().isoformat(),
            )

        def _create_demo_horse_score(
            self, horse_data: Dict[str, Any]
        ) -> HorseTrendScore:
            """Create demonstration horse trend score"""
            trend_scores = {
                "age": np.random.uniform(0.3, 0.9),
                "weight": np.random.uniform(0.2, 0.8),
                "draw": np.random.uniform(0.1, 0.7),
                "form": np.random.uniform(0.4, 0.9),
            }

            overall_score = np.mean(list(trend_scores.values()))

            return HorseTrendScore(
                horse_name=horse_data.get("horse_name", "Unknown"),
                trend_scores=trend_scores,
                overall_trend_score=overall_score,
                matching_patterns=["age: 4-5 years", "form: non-winner last time"],
                edge_factors=["Age pattern", "Form pattern"],
                confidence=min(0.95, overall_score + 0.2),
                recommendation=(
                    "STRONG"
                    if overall_score > 0.7
                    else "MODERATE" if overall_score > 0.5 else "WEAK"
                ),
            )


# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class EnhancedPrediction:
    """Enhanced prediction combining ML models with race trends analysis"""

    horse_name: str
    ml_win_probability: float
    ml_place_probability: float
    trend_score: float
    trend_confidence: float
    trend_recommendation: str
    combined_win_probability: float
    combined_place_probability: float
    trends_edge_value: float
    composite_score: float
    prediction_tier: str
    matching_patterns: List[str]
    edge_factors: List[str]
    betting_value: float
    confidence_rating: float


class RaceTrendsMLIntegration:
    """
    Advanced integration system combining:
    1. Optimized ML Models (Random Forest, XGBoost, Neural Networks)
    2. Advanced Form Analysis
    3. Power Rating Systems
    4. Speed & Pace Analysis
    5. Monte Carlo Simulation
    6. Race Trends Analysis (NEW!)
    """

    def __init__(self):
        # Initialize ML system
        self.ml_system = AdvancedMLIntegrationSystem()

        # Initialize trends analyzer
        self.trends_analyzer = RaceTrendsAnalyzer()

        # Weighting factors for combination
        self.ml_weight = 0.65  # ML model weight
        self.trends_weight = 0.35  # Trends analysis weight

        logger.info("🎯 Race Trends ML Integration System initialized")
        logger.info(f"   📊 ML Weight: {self.ml_weight:.1%}")
        logger.info(f"   📈 Trends Weight: {self.trends_weight:.1%}")

    def train_enhanced_models(self, X: pd.DataFrame, y: np.ndarray) -> Dict[str, Any]:
        """Train ML models with enhanced feature set including trends data"""
        logger.info("🚀 Training enhanced ML models with trends integration...")

        # Add simulated trends features to training data
        X_enhanced = self._add_trends_features(X)

        # Train ML models
        results = self.ml_system.train_advanced_models(X_enhanced, y)

        logger.info("✅ Enhanced ML models trained successfully")
        return results

    def analyze_race_with_trends(
        self,
        race_data: Dict[str, Any],
        historical_races: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[RaceAnalysisTrends, List[EnhancedPrediction]]:
        """
        Complete race analysis combining ML predictions with trends analysis
        """
        logger.info("🔍 Analyzing race with trends integration...")

        # Generate historical data if not provided
        if historical_races is None:
            historical_races = self._generate_historical_data()

        # Analyze race trends
        race_trends = self.trends_analyzer.analyze_race_trends(
            race_data, historical_races
        )

        # Get enhanced race data for ML
        enhanced_race_data = self._prepare_race_data_for_ml(race_data)

        # Get ML predictions
        ml_predictions = self.ml_system.predict_race(enhanced_race_data)

        # Combine ML with trends analysis
        enhanced_predictions = []

        for i, ml_pred in enumerate(ml_predictions):
            # Get horse data for trends analysis
            horse_data = enhanced_race_data.iloc[i].to_dict()
            horse_data["horse_name"] = ml_pred.horse_name

            # Score horse against trends
            trend_score = self.trends_analyzer.score_horse_trends(
                horse_data, race_trends
            )

            # Combine ML and trends
            enhanced_pred = self._combine_ml_and_trends(
                ml_pred, trend_score, race_trends
            )
            enhanced_predictions.append(enhanced_pred)

        # Sort by combined score
        enhanced_predictions.sort(
            key=lambda x: x.combined_win_probability, reverse=True
        )

        logger.info(
            f"✅ Race analysis complete - {len(enhanced_predictions)} horses analyzed"
        )

        return race_trends, enhanced_predictions

    def _add_trends_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Add simulated trends features to training data"""
        X_enhanced = X.copy()

        # Simulate trends-based features
        n_samples = len(X)

        # Age trend compliance (based on age)
        if "age" in X.columns:
            X_enhanced["age_trend_compliance"] = np.where(
                X["age"].between(4, 5), 0.9, 0.3
            ) + np.random.normal(0, 0.1, n_samples)
        else:
            X_enhanced["age_trend_compliance"] = np.random.uniform(0.2, 0.9, n_samples)

        # Weight trend compliance (based on weight)
        if "weight_lbs" in X.columns:
            X_enhanced["weight_trend_compliance"] = np.where(
                X["weight_lbs"] <= 130, 0.8, 0.4
            ) + np.random.normal(0, 0.15, n_samples)
        else:
            X_enhanced["weight_trend_compliance"] = np.random.uniform(
                0.3, 0.8, n_samples
            )

        # Draw trend compliance (based on draw)
        if "draw" in X.columns:
            X_enhanced["draw_trend_compliance"] = np.where(
                X["draw"] >= 10, 0.7, 0.4
            ) + np.random.normal(0, 0.12, n_samples)
        else:
            X_enhanced["draw_trend_compliance"] = np.random.uniform(0.2, 0.7, n_samples)

        # Form trend compliance (inverse of recent wins)
        X_enhanced["form_trend_compliance"] = np.random.beta(
            2, 3, n_samples
        )  # Favor non-winners

        # Overall trends score
        X_enhanced["trends_composite_score"] = (
            X_enhanced["age_trend_compliance"] * 0.3
            + X_enhanced["weight_trend_compliance"] * 0.25
            + X_enhanced["draw_trend_compliance"] * 0.2
            + X_enhanced["form_trend_compliance"] * 0.25
        )

        # Trends confidence
        X_enhanced["trends_confidence"] = np.random.beta(
            5, 2, n_samples
        )  # Mostly high confidence

        # Trends edge value
        X_enhanced["trends_edge_value"] = np.random.beta(
            2, 5, n_samples
        )  # Mostly small edges

        logger.info(
            f"📊 Added {X_enhanced.shape[1] - X.shape[1]} trends features to dataset"
        )

        return X_enhanced

    def _prepare_race_data_for_ml(self, race_data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare race data for ML prediction with trends features"""
        # Create sample race data (12 horses)
        horses_data = []

        for i in range(12):
            horse_data = {
                "horse_name": f"Horse_{i+1}",
                "odds_decimal": 2.5 + (i * 2.5),
                "draw": i + 1,
                "weight_lbs": 132 - i,
                "jockey_skill": 92 - (i * 3),
                "trainer_skill": 90 - (i * 2.5),
                "age": np.random.choice([3, 4, 5, 6], p=[0.2, 0.4, 0.3, 0.1]),
                "days_since_last_run": np.random.choice(
                    [14, 21, 28, 35], p=[0.3, 0.4, 0.2, 0.1]
                ),
                "course_wins": np.random.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1]),
                "distance_wins": np.random.choice(
                    [0, 1, 2, 3, 4], p=[0.3, 0.3, 0.2, 0.15, 0.05]
                ),
            }
            horses_data.append(horse_data)

        race_df = pd.DataFrame(horses_data)

        # Add existing ML features
        race_df = self._add_ml_features(race_df)

        # Add trends features
        race_df = self._add_trends_features_to_race(race_df)

        return race_df

    def _add_ml_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add ML features similar to existing system"""
        df_enhanced = df.copy()

        # Add power ratings
        df_enhanced["power_rating"] = 90 - (df_enhanced.index * 2)
        df_enhanced["speed_rating"] = 88 - (df_enhanced.index * 1.8)
        df_enhanced["form_composite"] = 0.9 - (df_enhanced.index * 0.05)
        df_enhanced["pace_rating"] = 85 - (df_enhanced.index * 1.5)
        df_enhanced["class_rating"] = 92 - (df_enhanced.index * 2.2)
        df_enhanced["consistency_index"] = 0.85 - (df_enhanced.index * 0.04)

        # Add derived features
        df_enhanced["course_and_distance_wins"] = df_enhanced["course_wins"] // 2
        df_enhanced["track_condition_encoded"] = 2  # Good track
        df_enhanced["class_level"] = range(1, len(df_enhanced) + 1)
        df_enhanced["distance_meters"] = 1600  # 1 mile

        return df_enhanced

    def _add_trends_features_to_race(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add trends features to race data"""
        # Age trend compliance
        df["age_trend_compliance"] = np.where(
            df["age"].between(4, 5), 0.9, 0.3
        ) + np.random.normal(0, 0.05, len(df))

        # Weight trend compliance
        df["weight_trend_compliance"] = np.where(
            df["weight_lbs"] <= 130, 0.8, 0.4
        ) + np.random.normal(0, 0.1, len(df))

        # Draw trend compliance
        df["draw_trend_compliance"] = np.where(
            df["draw"] >= 10, 0.7, 0.4
        ) + np.random.normal(0, 0.08, len(df))

        # Form trend compliance (non-winners favored)
        df["form_trend_compliance"] = np.random.beta(2, 3, len(df))

        # Overall trends score
        df["trends_composite_score"] = (
            df["age_trend_compliance"] * 0.3
            + df["weight_trend_compliance"] * 0.25
            + df["draw_trend_compliance"] * 0.2
            + df["form_trend_compliance"] * 0.25
        )

        # Trends confidence and edge
        df["trends_confidence"] = np.random.beta(5, 2, len(df))
        df["trends_edge_value"] = np.random.beta(2, 5, len(df))

        return df

    def _combine_ml_and_trends(
        self,
        ml_prediction,
        trend_score: HorseTrendScore,
        race_trends: RaceAnalysisTrends,
    ) -> EnhancedPrediction:
        """Combine ML prediction with trends analysis"""

        # Weighted combination of probabilities
        combined_win_prob = (
            ml_prediction.win_probability * self.ml_weight
            + trend_score.overall_trend_score * self.trends_weight
        )

        combined_place_prob = (
            ml_prediction.place_probability * self.ml_weight
            + min(0.9, trend_score.overall_trend_score * 1.5) * self.trends_weight
        )

        # Calculate betting value
        implied_prob = (
            1 / getattr(ml_prediction, "odds", 5.0)
            if hasattr(ml_prediction, "odds")
            else 0.2
        )
        betting_value = max(0, combined_win_prob - implied_prob)

        # Calculate composite score
        composite_score = (
            combined_win_prob * 0.4
            + trend_score.overall_trend_score * 0.3
            + trend_score.confidence * 0.2
            + (
                race_trends.overall_edge_score
                if race_trends.overall_edge_score > 0
                else 0.1
            )
            * 0.1
        )

        # Determine prediction tier
        if composite_score >= 0.75 and trend_score.confidence >= 0.8:
            tier = "Elite Contender"
        elif composite_score >= 0.65 and trend_score.confidence >= 0.7:
            tier = "Strong Contender"
        elif composite_score >= 0.5 and trend_score.confidence >= 0.5:
            tier = "Live Chance"
        else:
            tier = "Outsider"

        # Confidence rating
        confidence_rating = (
            trend_score.confidence * 0.4
            + min(1.0, ml_prediction.win_probability * 2) * 0.3
            + (race_trends.overall_edge_score * 2) * 0.3
        )

        return EnhancedPrediction(
            horse_name=ml_prediction.horse_name,
            ml_win_probability=ml_prediction.win_probability,
            ml_place_probability=ml_prediction.place_probability,
            trend_score=trend_score.overall_trend_score,
            trend_confidence=trend_score.confidence,
            trend_recommendation=trend_score.recommendation,
            combined_win_probability=combined_win_prob,
            combined_place_probability=combined_place_prob,
            trends_edge_value=race_trends.overall_edge_score,
            composite_score=composite_score,
            prediction_tier=tier,
            matching_patterns=trend_score.matching_patterns,
            edge_factors=trend_score.edge_factors,
            betting_value=betting_value,
            confidence_rating=confidence_rating,
        )

    def _generate_historical_data(self) -> List[Dict[str, Any]]:
        """Generate historical race data for trends analysis"""
        historical_races = []

        for i in range(20):  # 20 historical races
            race = {
                "race_id": f"race_{i+1}",
                "race_name": f"Historical Race {i+1}",
                "race_type": "handicap",
                "distance": "1m2f",
                "course": "Goodwood",
                "surface": "turf",
                "race_date": (datetime.now() - timedelta(days=30 + i * 7)).isoformat(),
                "participants": [],
            }

            # Add participants with winner
            for j in range(12):
                participant = {
                    "horse_name": f"Horse_{i}_{j}",
                    "age": np.random.choice(
                        [3, 4, 5, 6, 7], p=[0.15, 0.35, 0.3, 0.15, 0.05]
                    ),
                    "weight": np.random.normal(125, 8),
                    "draw": j + 1,
                    "odds": 2.0 + (j * 1.5),
                    "finish_position": j + 1,
                    "days_since_last_run": np.random.choice([14, 21, 28, 35]),
                    "last_run_result": (
                        "loss"
                        if j > 0
                        else np.random.choice(["win", "loss"], p=[0.1, 0.9])
                    ),
                    "course_wins": np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1]),
                    "course_runs": np.random.choice(
                        [1, 2, 3, 4], p=[0.4, 0.3, 0.2, 0.1]
                    ),
                    "distance_wins": np.random.choice([0, 1, 2], p=[0.5, 0.4, 0.1]),
                    "distance_runs": np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2]),
                }
                race["participants"].append(participant)

            historical_races.append(race)

        return historical_races

    def create_enhanced_dataset(
        self, num_samples: int = 8000
    ) -> Tuple[pd.DataFrame, np.ndarray]:
        """Create enhanced dataset with trends features"""
        logger.info(
            f"📊 Creating enhanced dataset with trends features ({num_samples} samples)..."
        )

        # Create base dataset
        X, y = self.ml_system.create_advanced_dataset(num_samples)

        # Add trends features
        X_enhanced = self._add_trends_features(X)

        logger.info(
            f"✅ Enhanced dataset created: {X_enhanced.shape[1]} features including trends data"
        )

        return X_enhanced, y

    def run_comprehensive_demo(self):
        """Run comprehensive demonstration of trends + ML integration"""
        logger.info("🚀 RACE TRENDS + ML INTEGRATION COMPREHENSIVE DEMO")
        logger.info("=" * 80)

        # Create enhanced dataset with trends
        logger.info("📊 Creating enhanced training dataset with trends features...")
        X_enhanced, y = self.create_enhanced_dataset(8000)

        # Train enhanced models
        logger.info("🧠 Training enhanced ML models with trends integration...")
        results = self.train_enhanced_models(X_enhanced, y)

        # Create sample race
        sample_race = {
            "race_name": "Goodwood Handicap",
            "race_type": "handicap",
            "distance": "1m2f",
            "course": "Goodwood",
            "surface": "turf",
            "prize_money": 50000,
            "num_runners": 12,
        }

        # Analyze race with trends
        logger.info("🔍 Analyzing sample race with trends integration...")
        race_trends, enhanced_predictions = self.analyze_race_with_trends(sample_race)

        # Display results
        self._display_trends_analysis(race_trends)
        self._display_enhanced_predictions(enhanced_predictions)
        self._display_performance_summary(results)

        logger.info("🎉 COMPREHENSIVE TRENDS + ML DEMO COMPLETE!")

    def _display_trends_analysis(self, race_trends: RaceAnalysisTrends):
        """Display race trends analysis"""
        print("\n" + "=" * 80)
        print("📈 RACE TRENDS ANALYSIS")
        print("=" * 80)

        print(f"\n🏁 Race: {race_trends.race_name}")
        print(f"📊 Overall Edge Score: {race_trends.overall_edge_score:.1%}")
        print(f"🎯 Total Patterns Found: {race_trends.total_patterns_found}")

        print(f"\n🔍 Identified Trends:")

        if race_trends.age_trends:
            print(f"\n🎂 Age Trends:")
            for trend in race_trends.age_trends:
                print(f"   • {trend.pattern} (confidence: {trend.confidence:.1%})")

        if race_trends.weight_trends:
            print(f"\n⚖️ Weight Trends:")
            for trend in race_trends.weight_trends:
                print(f"   • {trend.pattern} (confidence: {trend.confidence:.1%})")

        if race_trends.draw_trends:
            print(f"\n🎯 Draw Trends:")
            for trend in race_trends.draw_trends:
                print(f"   • {trend.pattern} (confidence: {trend.confidence:.1%})")

        if race_trends.form_trends:
            print(f"\n📊 Form Trends:")
            for trend in race_trends.form_trends:
                print(f"   • {trend.pattern} (confidence: {trend.confidence:.1%})")

    def _display_enhanced_predictions(self, predictions: List[EnhancedPrediction]):
        """Display enhanced predictions"""
        print("\n" + "=" * 80)
        print("🎯 ENHANCED PREDICTIONS (ML + TRENDS)")
        print("=" * 80)

        print(f"\n🏆 Top Enhanced Predictions:")

        for i, pred in enumerate(predictions[:8], 1):
            print(f"\n{i}. {pred.horse_name}")
            print(f"   🤖 ML Win Prob: {pred.ml_win_probability:.1%}")
            print(f"   📈 Trends Score: {pred.trend_score:.1%}")
            print(f"   🎯 Combined Win Prob: {pred.combined_win_probability:.1%}")
            print(f"   🏅 Prediction Tier: {pred.prediction_tier}")
            print(f"   💰 Betting Value: {pred.betting_value:.1%}")
            print(f"   📊 Confidence: {pred.confidence_rating:.1%}")

            if pred.matching_patterns:
                print(
                    f"   ✅ Matching Patterns: {', '.join(pred.matching_patterns[:2])}"
                )

            if pred.edge_factors:
                print(f"   🎪 Edge Factors: {', '.join(pred.edge_factors[:2])}")

    def _display_performance_summary(self, results: Dict[str, Any]):
        """Display ML performance summary"""
        print("\n" + "=" * 80)
        print("📊 ENHANCED ML PERFORMANCE (WITH TRENDS)")
        print("=" * 80)

        print(f"\n🏆 Model Performance (AUC Scores):")
        for name, result in results["model_results"].items():
            print(f"   {name}: {result['cv_auc']:.4f} ± {result['cv_std']:.4f}")

        print(f"\n🎯 Best Model: {results['best_model']}")

        if results["feature_importance"]:
            print(f"\n🔍 Top Features (Including Trends):")
            top_features = sorted(
                results["feature_importance"].items(), key=lambda x: x[1], reverse=True
            )[:10]

            for feature, importance in top_features:
                if "trend" in feature.lower():
                    print(f"   📈 {feature}: {importance:.4f} (TRENDS)")
                else:
                    print(f"   • {feature}: {importance:.4f}")


def main():
    """Run the comprehensive race trends + ML integration demo"""
    integration_system = RaceTrendsMLIntegration()
    integration_system.run_comprehensive_demo()


if __name__ == "__main__":
    main()
