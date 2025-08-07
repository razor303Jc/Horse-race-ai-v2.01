#!/usr/bin/env python3
"""
Race & Data Quality Analyzer for AI Reward System
Analyzes race quality, data availability, and confidence levels for different race types
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging
from typing import Dict, List, Tuple, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RaceDataQualityAnalyzer:
    """
    Analyzes race quality and data availability to inform the AI reward system.

    Key Features:
    - Race type analysis (2yo Novice, Group 1, Handicaps, etc.)
    - Data quantity assessment (form depth, career stats)
    - Confidence scoring based on available information
    - Market quality evaluation
    - Prediction reliability scoring
    """

    def __init__(self, db_path: str = "ai_strategies_corrected.db"):
        self.db_path = db_path

        # Race quality scoring system
        self.race_quality_scores = {
            "Group 1 Stakes": {
                "base_score": 95,
                "data_reliability": 0.95,
                "market_efficiency": 0.90,
            },
            "Group 2 Stakes": {
                "base_score": 90,
                "data_reliability": 0.92,
                "market_efficiency": 0.88,
            },
            "Group 3 Stakes": {
                "base_score": 85,
                "data_reliability": 0.90,
                "market_efficiency": 0.85,
            },
            "Listed Stakes": {
                "base_score": 80,
                "data_reliability": 0.88,
                "market_efficiency": 0.82,
            },
            "Handicap Stakes": {
                "base_score": 75,
                "data_reliability": 0.85,
                "market_efficiency": 0.80,
            },
            "Maiden Stakes": {
                "base_score": 60,
                "data_reliability": 0.70,
                "market_efficiency": 0.75,
            },
            "Novice Stakes": {
                "base_score": 55,
                "data_reliability": 0.65,
                "market_efficiency": 0.70,
            },
            "Claiming Stakes": {
                "base_score": 50,
                "data_reliability": 0.60,
                "market_efficiency": 0.65,
            },
            "Selling Stakes": {
                "base_score": 45,
                "data_reliability": 0.55,
                "market_efficiency": 0.60,
            },
        }

        # Age-based data quality factors
        self.age_data_factors = {
            2: {"form_depth": 0.3, "career_reliability": 0.2, "experience_factor": 0.1},
            3: {"form_depth": 0.6, "career_reliability": 0.5, "experience_factor": 0.4},
            4: {"form_depth": 0.8, "career_reliability": 0.8, "experience_factor": 0.7},
            5: {
                "form_depth": 0.9,
                "career_reliability": 0.9,
                "experience_factor": 0.85,
            },
            6: {
                "form_depth": 0.95,
                "career_reliability": 0.95,
                "experience_factor": 0.9,
            },
            7: {
                "form_depth": 0.92,
                "career_reliability": 0.92,
                "experience_factor": 0.88,
            },
            8: {
                "form_depth": 0.85,
                "career_reliability": 0.85,
                "experience_factor": 0.8,
            },
            9: {
                "form_depth": 0.75,
                "career_reliability": 0.75,
                "experience_factor": 0.7,
            },
            10: {
                "form_depth": 0.65,
                "career_reliability": 0.65,
                "experience_factor": 0.6,
            },
        }

    def analyze_race_quality(self, race_id: int) -> Dict:
        """Analyze the quality and predictability of a specific race"""

        conn = sqlite3.connect(self.db_path)

        # Get race details
        race_query = """
            SELECT rc.race_type, rc.distance_meters, rc.prize_money, rc.num_runners,
                   rc.track_condition, rc.weather, v.name as venue_name
            FROM race_cards rc
            JOIN venues v ON rc.venue_id = v.venue_id
            WHERE rc.race_id = ?
        """

        race_df = pd.read_sql_query(race_query, conn, params=(race_id,))

        if race_df.empty:
            return {"error": f"Race {race_id} not found"}

        race_data = race_df.iloc[0]
        race_type = race_data["race_type"]

        # Get participant data with comprehensive statistics
        participants_query = """
            SELECT rp.participant_id, rp.odds_decimal, rp.actual_finish_position,
                   h.age, h.rating, h.form_rating, h.career_wins, h.career_runs, h.earnings,
                   j.skill_rating as jockey_skill, j.win_percentage as jockey_win_pct, j.career_wins as jockey_wins,
                   t.skill_rating as trainer_skill, t.win_percentage as trainer_win_pct, t.career_wins as trainer_wins,
                   rp.form_string, rp.days_since_last_run, rp.course_wins, rp.distance_wins
            FROM race_participants rp
            JOIN horses h ON rp.horse_id = h.horse_id
            JOIN jockeys j ON rp.jockey_id = j.jockey_id
            JOIN trainers t ON rp.trainer_id = t.trainer_id
            WHERE rp.race_id = ?
        """

        participants_df = pd.read_sql_query(participants_query, conn, params=(race_id,))
        conn.close()

        # Base race quality from race type
        race_quality_data = self.race_quality_scores.get(
            race_type,
            {"base_score": 50, "data_reliability": 0.5, "market_efficiency": 0.5},
        )

        # Analyze data quality for each participant
        data_quality_scores = []
        age_distribution = []
        career_depth_scores = []
        form_reliability_scores = []

        for _, participant in participants_df.iterrows():
            age = participant["age"]
            career_runs = participant["career_runs"]
            career_wins = participant["career_wins"]
            form_string = participant["form_string"] or ""
            days_since_run = participant["days_since_last_run"]

            age_distribution.append(age)

            # Age-based data quality
            age_factors = self.age_data_factors.get(age, self.age_data_factors[5])

            # Career depth scoring
            career_depth = min(1.0, career_runs / 20)  # Full depth at 20+ runs
            career_depth_scores.append(career_depth)

            # Form reliability based on form string length and recency
            form_length = len(form_string)
            form_reliability = min(
                1.0, form_length / 8
            )  # Full reliability at 8+ form characters

            # Recency factor
            recency_factor = 1.0
            if days_since_run > 100:
                recency_factor = 0.7
            elif days_since_run > 60:
                recency_factor = 0.85
            elif days_since_run > 30:
                recency_factor = 0.95

            form_reliability *= recency_factor
            form_reliability_scores.append(form_reliability)

            # Overall participant data quality
            participant_data_quality = (
                age_factors["form_depth"] * 0.3
                + age_factors["career_reliability"] * 0.3
                + career_depth * 0.25
                + form_reliability * 0.15
            )

            data_quality_scores.append(participant_data_quality)

        # Field quality analysis
        field_size = len(participants_df)
        competitive_balance = self._calculate_competitive_balance(
            participants_df["odds_decimal"].tolist()
        )

        # Market liquidity proxy (based on field size and race quality)
        market_liquidity_factor = (
            min(1.0, field_size / 12) * race_quality_data["market_efficiency"]
        )

        # Overall race quality score
        avg_data_quality = np.mean(data_quality_scores)
        min_data_quality = np.min(data_quality_scores)

        # Special handling for different race types
        race_specific_adjustments = self._get_race_specific_adjustments(
            race_type, age_distribution, participants_df
        )

        # Final quality assessment
        overall_quality = (
            race_quality_data["base_score"] * 0.4
            + avg_data_quality * 100 * 0.3
            + competitive_balance * 100 * 0.2
            + market_liquidity_factor * 100 * 0.1
        ) * race_specific_adjustments["quality_multiplier"]

        # Prediction confidence
        prediction_confidence = (
            race_quality_data["data_reliability"] * 0.4
            + avg_data_quality * 0.3
            + min_data_quality * 0.2  # Weakest link factor
            + race_specific_adjustments["confidence_multiplier"] * 0.1
        )

        return {
            "race_id": race_id,
            "race_type": race_type,
            "venue": race_data["venue_name"],
            "field_size": field_size,
            "overall_quality": round(overall_quality, 2),
            "prediction_confidence": round(prediction_confidence, 3),
            "data_quality": {
                "average": round(avg_data_quality, 3),
                "minimum": round(min_data_quality, 3),
                "individual_scores": [round(score, 3) for score in data_quality_scores],
            },
            "race_characteristics": {
                "competitive_balance": round(competitive_balance, 3),
                "market_efficiency": race_quality_data["market_efficiency"],
                "prize_money": race_data["prize_money"],
                "age_distribution": {
                    "ages": age_distribution,
                    "average_age": round(np.mean(age_distribution), 1),
                    "has_juveniles": 2 in age_distribution,
                    "has_novices": any(
                        runs < 5 for runs in participants_df["career_runs"]
                    ),
                },
            },
            "form_analysis": {
                "average_career_depth": round(np.mean(career_depth_scores), 3),
                "average_form_reliability": round(np.mean(form_reliability_scores), 3),
                "data_gaps": sum(1 for score in data_quality_scores if score < 0.5),
            },
            "race_specific_factors": race_specific_adjustments,
            "recommendations": self._generate_analysis_recommendations(
                overall_quality, prediction_confidence, race_type, age_distribution
            ),
        }

    def _calculate_competitive_balance(self, odds_list: List[float]) -> float:
        """Calculate how competitive/balanced the race is based on odds distribution"""
        if not odds_list:
            return 0.0

        # Convert odds to implied probabilities
        implied_probs = [1 / odds for odds in odds_list]

        # Calculate entropy (higher = more competitive)
        entropy = -sum(p * np.log2(p) for p in implied_probs if p > 0)
        max_entropy = np.log2(len(odds_list))

        # Normalize to 0-1 scale
        competitive_balance = entropy / max_entropy if max_entropy > 0 else 0

        return competitive_balance

    def _get_race_specific_adjustments(
        self, race_type: str, age_distribution: List[int], participants_df: pd.DataFrame
    ) -> Dict:
        """Apply race-type specific adjustments to quality scoring"""

        adjustments = {
            "quality_multiplier": 1.0,
            "confidence_multiplier": 1.0,
            "special_factors": [],
        }

        # 2-year-old races
        if any(age == 2 for age in age_distribution):
            if "Novice" in race_type or "Maiden" in race_type:
                adjustments["quality_multiplier"] = 0.6  # Much lower predictability
                adjustments["confidence_multiplier"] = 0.5
                adjustments["special_factors"].append("juvenile_novice_penalty")
            else:
                adjustments["quality_multiplier"] = 0.8
                adjustments["confidence_multiplier"] = 0.7
                adjustments["special_factors"].append("juvenile_race")

        # Maiden races (horses without wins)
        maiden_count = sum(
            1 for _, row in participants_df.iterrows() if row["career_wins"] == 0
        )
        maiden_percentage = maiden_count / len(participants_df)

        if maiden_percentage > 0.7:  # Mostly maidens
            adjustments["quality_multiplier"] *= 0.7
            adjustments["confidence_multiplier"] *= 0.6
            adjustments["special_factors"].append("high_maiden_percentage")

        # Small field penalty
        if len(participants_df) < 8:
            adjustments["quality_multiplier"] *= 0.9
            adjustments["special_factors"].append("small_field")

        # Large field complexity
        if len(participants_df) > 16:
            adjustments["confidence_multiplier"] *= 0.9
            adjustments["special_factors"].append("large_field_complexity")

        # Inexperienced participants
        low_experience_count = sum(
            1 for _, row in participants_df.iterrows() if row["career_runs"] < 3
        )
        if low_experience_count > len(participants_df) * 0.5:
            adjustments["quality_multiplier"] *= 0.8
            adjustments["confidence_multiplier"] *= 0.7
            adjustments["special_factors"].append("high_inexperience")

        # Class inconsistency (mixed ability levels)
        rating_range = participants_df["rating"].max() - participants_df["rating"].min()
        if rating_range > 30:  # Wide rating spread
            adjustments["confidence_multiplier"] *= 0.9
            adjustments["special_factors"].append("wide_ability_range")

        return adjustments

    def _generate_analysis_recommendations(
        self,
        overall_quality: float,
        prediction_confidence: float,
        race_type: str,
        age_distribution: List[int],
    ) -> List[str]:
        """Generate specific recommendations based on race analysis"""

        recommendations = []

        # Quality-based recommendations
        if overall_quality > 80:
            recommendations.append("HIGH_CONFIDENCE: Excellent race for AI predictions")
        elif overall_quality > 65:
            recommendations.append("MEDIUM_CONFIDENCE: Good predictive potential")
        elif overall_quality > 50:
            recommendations.append("LOW_CONFIDENCE: Limited predictive reliability")
        else:
            recommendations.append("AVOID: Poor predictive conditions")

        # Specific race type recommendations
        if "Novice" in race_type and 2 in age_distribution:
            recommendations.append("CAUTION: 2yo novice race - very limited form data")
            recommendations.append("STRATEGY: Focus on trainer/jockey combinations")
            recommendations.append("STAKES: Reduce stake sizes significantly")

        if "Maiden" in race_type:
            recommendations.append(
                "MAIDEN_RACE: Emphasize breeding, connections, market moves"
            )
            recommendations.append(
                "FORM_WARNING: Traditional form analysis less reliable"
            )

        if "Handicap" in race_type:
            recommendations.append(
                "HANDICAP: Good for AI analysis - form data available"
            )
            recommendations.append(
                "WEIGHT_FACTOR: Include weight adjustments in analysis"
            )

        if prediction_confidence < 0.6:
            recommendations.append("LOW_DATA_QUALITY: Consider smaller stakes")
            recommendations.append("RESEARCH: Seek additional market intelligence")

        return recommendations

    def batch_analyze_races(self, race_ids: List[int] = None) -> Dict:
        """Analyze multiple races and provide summary statistics"""

        conn = sqlite3.connect(self.db_path)

        if race_ids is None:
            # Get all races
            cursor = conn.cursor()
            cursor.execute(
                "SELECT race_id FROM race_cards LIMIT 100"
            )  # Limit for performance
            race_ids = [row[0] for row in cursor.fetchall()]

        conn.close()

        results = []
        for race_id in race_ids:
            try:
                analysis = self.analyze_race_quality(race_id)
                if "error" not in analysis:
                    results.append(analysis)
            except Exception as e:
                logger.warning(f"Failed to analyze race {race_id}: {e}")

        # Summary statistics
        if not results:
            return {"error": "No races successfully analyzed"}

        quality_scores = [r["overall_quality"] for r in results]
        confidence_scores = [r["prediction_confidence"] for r in results]

        race_type_distribution = {}
        for result in results:
            race_type = result["race_type"]
            if race_type not in race_type_distribution:
                race_type_distribution[race_type] = 0
            race_type_distribution[race_type] += 1

        return {
            "total_races_analyzed": len(results),
            "quality_distribution": {
                "excellent": sum(1 for q in quality_scores if q > 80),
                "good": sum(1 for q in quality_scores if 65 <= q <= 80),
                "fair": sum(1 for q in quality_scores if 50 <= q < 65),
                "poor": sum(1 for q in quality_scores if q < 50),
            },
            "average_quality": round(np.mean(quality_scores), 2),
            "average_confidence": round(np.mean(confidence_scores), 3),
            "race_type_distribution": race_type_distribution,
            "detailed_results": results[:10],  # Show first 10 detailed results
        }

    def analyze_ai_performance_by_race_quality(self) -> Dict:
        """Analyze how AI performance varies by race quality"""

        conn = sqlite3.connect(self.db_path)

        # Get AI predictions with race details
        query = """
            SELECT ap.prediction_id, ap.race_id, ap.predicted_probability, ap.confidence_score,
                   ap.actual_result, rc.race_type, h.age, h.career_runs,
                   abs.strategy_type, abs.recommended_stake, abs.recommended_odds
            FROM ai_predictions ap
            JOIN race_cards rc ON ap.race_id = rc.race_id
            JOIN race_participants rp ON ap.participant_id = rp.participant_id
            JOIN horses h ON rp.horse_id = h.horse_id
            LEFT JOIN ai_betting_strategies abs ON ap.prediction_id = abs.prediction_id
            WHERE abs.strategy_type IS NOT NULL
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return {"error": "No AI prediction data found"}

        # Analyze each race and categorize by quality
        race_quality_categories = {
            "high_quality": [],
            "medium_quality": [],
            "low_quality": [],
        }

        performance_by_quality = {
            "high_quality": {"predictions": [], "stakes": [], "returns": []},
            "medium_quality": {"predictions": [], "stakes": [], "returns": []},
            "low_quality": {"predictions": [], "stakes": [], "returns": []},
        }

        unique_races = df["race_id"].unique()

        for race_id in unique_races:
            race_analysis = self.analyze_race_quality(race_id)
            if "error" in race_analysis:
                continue

            quality = race_analysis["overall_quality"]
            race_predictions = df[df["race_id"] == race_id]

            # Categorize race quality
            if quality > 70:
                category = "high_quality"
            elif quality > 50:
                category = "medium_quality"
            else:
                category = "low_quality"

            race_quality_categories[category].append(race_id)

            # Calculate performance metrics for this race
            for _, pred in race_predictions.iterrows():
                stake = pred["recommended_stake"] or 0
                odds = pred["recommended_odds"] or 1
                actual_result = pred["actual_result"]

                # Calculate return
                if actual_result == 1:  # Winner
                    return_amount = stake * (odds - 1)
                else:
                    return_amount = -stake

                performance_by_quality[category]["predictions"].append(
                    pred["prediction_id"]
                )
                performance_by_quality[category]["stakes"].append(stake)
                performance_by_quality[category]["returns"].append(return_amount)

        # Calculate summary statistics
        summary = {}
        for category in performance_by_quality:
            data = performance_by_quality[category]

            if data["stakes"]:
                total_stakes = sum(data["stakes"])
                total_returns = sum(data["returns"])
                profit_loss = total_returns
                roi = (profit_loss / total_stakes * 100) if total_stakes > 0 else 0
                win_rate = (
                    sum(1 for r in data["returns"] if r > 0)
                    / len(data["returns"])
                    * 100
                )

                summary[category] = {
                    "race_count": len(race_quality_categories[category]),
                    "prediction_count": len(data["predictions"]),
                    "total_stakes": round(total_stakes, 2),
                    "profit_loss": round(profit_loss, 2),
                    "roi": round(roi, 2),
                    "win_rate": round(win_rate, 2),
                    "average_stake": (
                        round(total_stakes / len(data["stakes"]), 2)
                        if data["stakes"]
                        else 0
                    ),
                }

        return {
            "performance_by_quality": summary,
            "race_distribution": {
                cat: len(races) for cat, races in race_quality_categories.items()
            },
            "recommendations": self._generate_performance_recommendations(summary),
        }

    def _generate_performance_recommendations(
        self, performance_summary: Dict
    ) -> List[str]:
        """Generate recommendations based on performance analysis"""

        recommendations = []

        # Compare performance across quality levels
        high_roi = performance_summary.get("high_quality", {}).get("roi", 0)
        medium_roi = performance_summary.get("medium_quality", {}).get("roi", 0)
        low_roi = performance_summary.get("low_quality", {}).get("roi", 0)

        if high_roi > medium_roi > low_roi:
            recommendations.append(
                "OPTIMAL: AI performs best on high-quality races as expected"
            )
            recommendations.append("STRATEGY: Increase stakes on high-quality races")
        elif low_roi > high_roi:
            recommendations.append("ANOMALY: AI performing better on low-quality races")
            recommendations.append(
                "INVESTIGATE: May indicate overconfidence on quality races"
            )

        if low_roi < -10:
            recommendations.append("WARNING: Significant losses on low-quality races")
            recommendations.append(
                "ACTION: Implement strict filters for poor-quality races"
            )

        high_winrate = performance_summary.get("high_quality", {}).get("win_rate", 0)
        if high_winrate < 25:
            recommendations.append(
                "ACCURACY: Even high-quality race accuracy needs improvement"
            )
            recommendations.append("TRAINING: Focus on prediction model refinement")

        return recommendations


def main():
    """Demonstrate the race data quality analyzer"""

    analyzer = RaceDataQualityAnalyzer()

    print("🏇 Race Data Quality Analysis System")
    print("=" * 50)

    # Analyze a sample of races
    batch_analysis = analyzer.batch_analyze_races()

    if "error" not in batch_analysis:
        print(f"\n📊 Batch Analysis Results:")
        print(f"Total races analyzed: {batch_analysis['total_races_analyzed']}")
        print(f"Average quality score: {batch_analysis['average_quality']}/100")
        print(f"Average prediction confidence: {batch_analysis['average_confidence']}")

        print(f"\n🎯 Quality Distribution:")
        for quality, count in batch_analysis["quality_distribution"].items():
            print(f"  {quality.title()}: {count} races")

        print(f"\n🏆 Race Type Distribution:")
        for race_type, count in batch_analysis["race_type_distribution"].items():
            print(f"  {race_type}: {count} races")

    # Analyze AI performance by race quality
    performance_analysis = analyzer.analyze_ai_performance_by_race_quality()

    if "error" not in performance_analysis:
        print(f"\n🤖 AI Performance by Race Quality:")
        for quality, metrics in performance_analysis["performance_by_quality"].items():
            print(f"\n  {quality.replace('_', ' ').title()} Races:")
            print(f"    Races: {metrics['race_count']}")
            print(f"    Predictions: {metrics['prediction_count']}")
            print(f"    ROI: {metrics['roi']}%")
            print(f"    Win Rate: {metrics['win_rate']}%")
            print(f"    P&L: £{metrics['profit_loss']}")

        print(f"\n💡 Recommendations:")
        for rec in performance_analysis["recommendations"]:
            print(f"  • {rec}")


if __name__ == "__main__":
    main()
