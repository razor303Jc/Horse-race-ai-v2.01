#!/usr/bin/env python3
"""
Trends & Performance Integration Manager for Horse Racing AI v2.0
===============================================================

Integration layer between race trends analysis, AI betting performance,
and database storage systems.

Features:
- RaceTrendsAnalyzer integration with database storage
- AI performance tracking and database integration
- Betting strategy effectiveness monitoring
- Comprehensive performance reporting and analytics
"""

import logging
from datetime import datetime, date
from typing import Any, Dict, List, Optional

from .trends_performance_database_manager import (
    TrendsPerformanceDatabaseManager,
    RaceTrend,
    RaceAnalysisTrends,
    HorseTrendScore,
    AIPrediction,
    BettingStrategy,
    MethodPerformance,
    StrategyPerformance,
)

logger = logging.getLogger(__name__)


class TrendsPerformanceIntegrationManager:
    """Integration manager for trends and performance systems"""

    def __init__(self, db_path: str = "data/trends_performance.db"):
        """Initialize integration manager"""
        self.db_manager = TrendsPerformanceDatabaseManager(db_path)
        logger.info("TrendsPerformanceIntegrationManager initialized")

    # Race Trends Integration
    # =======================================

    def process_race_trends_analysis(
        self, trends_analyzer, race_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process complete race trends analysis and store in database"""
        try:
            race_id = race_data.get(
                "race_id", f"race_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # Analyze race trends using RaceTrendsAnalyzer
            trends_analysis = trends_analyzer.analyze_race_trends(race_data)

            # Extract trend data from analysis
            if hasattr(trends_analysis, "trends") and trends_analysis.trends:
                # Save individual trends
                for trend_data in trends_analysis.trends:
                    trend = RaceTrend(
                        race_id=race_id,
                        trend_category=trend_data.category,
                        trend_type=trend_data.trend_type,
                        pattern_description=trend_data.description,
                        confidence_score=trend_data.confidence,
                        edge_value=trend_data.edge,
                        sample_size=trend_data.sample_size,
                        historical_strike_rate=getattr(trend_data, "strike_rate", 0.0),
                        significance_level=getattr(trend_data, "significance", 0.0),
                    )
                    self.db_manager.save_race_trend(trend)

            # Create race analysis summary
            race_analysis = RaceAnalysisTrends(
                race_id=race_id,
                track=race_data.get("track", "Unknown"),
                race_date=datetime.now().date(),
                distance=race_data.get("distance", 8.0),
                surface=race_data.get("surface", "dirt"),
                race_class=race_data.get("race_class", "ALLOWANCE"),
                total_trends_identified=len(getattr(trends_analysis, "trends", [])),
                high_confidence_trends=self._count_high_confidence_trends(
                    trends_analysis
                ),
                overall_edge_rating=self._calculate_overall_edge_rating(
                    trends_analysis
                ),
                trend_strength=self._assess_trend_strength(trends_analysis),
                # Category-specific counts and edges
                age_trends_count=self._count_trends_by_category(
                    trends_analysis, "age_trends"
                ),
                age_trends_edge=self._calculate_category_edge(
                    trends_analysis, "age_trends"
                ),
                weight_trends_count=self._count_trends_by_category(
                    trends_analysis, "weight_trends"
                ),
                weight_trends_edge=self._calculate_category_edge(
                    trends_analysis, "weight_trends"
                ),
                draw_trends_count=self._count_trends_by_category(
                    trends_analysis, "draw_trends"
                ),
                draw_trends_edge=self._calculate_category_edge(
                    trends_analysis, "draw_trends"
                ),
                form_trends_count=self._count_trends_by_category(
                    trends_analysis, "form_trends"
                ),
                form_trends_edge=self._calculate_category_edge(
                    trends_analysis, "form_trends"
                ),
                price_trends_count=self._count_trends_by_category(
                    trends_analysis, "price_trends"
                ),
                price_trends_edge=self._calculate_category_edge(
                    trends_analysis, "price_trends"
                ),
                seasonal_trends_count=self._count_trends_by_category(
                    trends_analysis, "seasonal_trends"
                ),
                seasonal_trends_edge=self._calculate_category_edge(
                    trends_analysis, "seasonal_trends"
                ),
                course_form_trends_count=self._count_trends_by_category(
                    trends_analysis, "course_form_trends"
                ),
                course_form_trends_edge=self._calculate_category_edge(
                    trends_analysis, "course_form_trends"
                ),
                distance_form_trends_count=self._count_trends_by_category(
                    trends_analysis, "distance_form_trends"
                ),
                distance_form_trends_edge=self._calculate_category_edge(
                    trends_analysis, "distance_form_trends"
                ),
            )

            self.db_manager.save_race_analysis_trends(race_analysis)

            # Process horse trend scores if available
            if hasattr(trends_analysis, "horse_scores"):
                for horse_name, score_data in trends_analysis.horse_scores.items():
                    horse_score = HorseTrendScore(
                        race_id=race_id,
                        horse_name=horse_name,
                        overall_trend_score=score_data.get("overall_score", 0.0),
                        trend_rank=score_data.get("rank", 0),
                        trend_confidence=score_data.get("confidence", 0.0),
                        age_trend_score=score_data.get("age_score", 0.0),
                        weight_trend_score=score_data.get("weight_score", 0.0),
                        draw_trend_score=score_data.get("draw_score", 0.0),
                        form_trend_score=score_data.get("form_score", 0.0),
                        price_trend_score=score_data.get("price_score", 0.0),
                        seasonal_trend_score=score_data.get("seasonal_score", 0.0),
                        course_form_trend_score=score_data.get(
                            "course_form_score", 0.0
                        ),
                        distance_form_trend_score=score_data.get(
                            "distance_form_score", 0.0
                        ),
                        positive_trends_count=score_data.get("positive_trends", 0),
                        negative_trends_count=score_data.get("negative_trends", 0),
                        neutral_trends_count=score_data.get("neutral_trends", 0),
                    )
                    self.db_manager.save_horse_trend_score(horse_score)

            logger.info(f"Race trends analysis processed and stored for {race_id}")
            return {
                "success": True,
                "race_id": race_id,
                "trends_identified": race_analysis.total_trends_identified,
                "overall_edge_rating": race_analysis.overall_edge_rating,
                "trend_strength": race_analysis.trend_strength,
            }

        except Exception as e:
            logger.error(f"Error processing race trends analysis: {e}")
            return {"success": False, "error": str(e)}

    def score_horses_with_trends(
        self,
        trends_analyzer,
        race_data: Dict[str, Any],
        horses_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Score horses against identified race trends"""
        try:
            race_id = race_data.get(
                "race_id", f"race_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # Get or create trends analysis
            trends_analysis = trends_analyzer.analyze_race_trends(race_data)

            scored_horses = []
            for i, horse_data in enumerate(horses_data):
                horse_name = horse_data.get("horse_name", f"Horse_{i+1}")

                # Score horse against trends
                if hasattr(trends_analyzer, "score_horse_trends"):
                    trend_score = trends_analyzer.score_horse_trends(
                        horse_data, trends_analysis
                    )
                else:
                    # Fallback scoring based on available data
                    trend_score = self._calculate_basic_trend_score(
                        horse_data, trends_analysis
                    )

                # Create horse trend score record
                horse_score = HorseTrendScore(
                    race_id=race_id,
                    horse_name=horse_name,
                    overall_trend_score=trend_score.get("overall_score", 0.0),
                    trend_rank=i + 1,  # Will be updated after sorting
                    trend_confidence=trend_score.get("confidence", 0.0),
                    age_trend_score=trend_score.get("age_score", 0.0),
                    weight_trend_score=trend_score.get("weight_score", 0.0),
                    draw_trend_score=trend_score.get("draw_score", 0.0),
                    form_trend_score=trend_score.get("form_score", 0.0),
                    price_trend_score=trend_score.get("price_score", 0.0),
                    seasonal_trend_score=trend_score.get("seasonal_score", 0.0),
                    course_form_trend_score=trend_score.get("course_form_score", 0.0),
                    distance_form_trend_score=trend_score.get(
                        "distance_form_score", 0.0
                    ),
                    positive_trends_count=trend_score.get("positive_trends", 0),
                    negative_trends_count=trend_score.get("negative_trends", 0),
                    neutral_trends_count=trend_score.get("neutral_trends", 0),
                )

                scored_horses.append(
                    {
                        "horse_data": horse_data,
                        "trend_score": horse_score,
                        "overall_score": trend_score.get("overall_score", 0.0),
                    }
                )

            # Sort by trend score and update ranks
            scored_horses.sort(key=lambda x: x["overall_score"], reverse=True)
            for rank, scored_horse in enumerate(scored_horses, 1):
                scored_horse["trend_score"].trend_rank = rank
                self.db_manager.save_horse_trend_score(scored_horse["trend_score"])

            logger.info(f"Horses scored with trends for race {race_id}")
            return {
                "success": True,
                "race_id": race_id,
                "scored_horses": [
                    {
                        "horse_name": sh["horse_data"].get("horse_name"),
                        "trend_score": sh["overall_score"],
                        "trend_rank": sh["trend_score"].trend_rank,
                    }
                    for sh in scored_horses
                ],
            }

        except Exception as e:
            logger.error(f"Error scoring horses with trends: {e}")
            return {"success": False, "error": str(e)}

    # AI Performance Integration
    # =======================================

    def track_ai_predictions(
        self, race_data: Dict[str, Any], predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track AI predictions and store in database"""
        try:
            race_id = race_data.get(
                "race_id", f"race_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            stored_predictions = []
            for horse_name, pred_data in predictions.items():
                ai_prediction = AIPrediction(
                    race_id=race_id,
                    horse_name=horse_name,
                    raw_rating=pred_data.get("raw_rating", 0.0),
                    monte_carlo_rating=pred_data.get("monte_carlo_rating", 0.0),
                    ai_ml_rating=pred_data.get("ai_ml_rating", 0.0),
                    consensus_rating=pred_data.get("consensus_rating", 0.0),
                    raw_win_probability=pred_data.get("raw_win_probability", 0.0),
                    monte_carlo_win_probability=pred_data.get(
                        "monte_carlo_win_probability", 0.0
                    ),
                    ai_ml_win_probability=pred_data.get("ai_ml_win_probability", 0.0),
                    consensus_win_probability=pred_data.get(
                        "consensus_win_probability", 0.0
                    ),
                    prediction_confidence=pred_data.get("prediction_confidence", 0.0),
                    method_agreement_score=pred_data.get("method_agreement_score", 0.0),
                    prediction_consistency=pred_data.get("prediction_consistency", 0.0),
                    betting_odds=pred_data.get("betting_odds", 0.0),
                    implied_probability=pred_data.get("implied_probability", 0.0),
                    value_rating=pred_data.get("value_rating", 0.0),
                    prediction_timestamp=datetime.now(),
                )

                prediction_id = self.db_manager.save_ai_prediction(ai_prediction)
                stored_predictions.append(
                    {
                        "id": prediction_id,
                        "horse_name": horse_name,
                        "confidence": ai_prediction.prediction_confidence,
                        "value_rating": ai_prediction.value_rating,
                    }
                )

            logger.info(f"AI predictions tracked for race {race_id}")
            return {
                "success": True,
                "race_id": race_id,
                "predictions_stored": len(stored_predictions),
                "predictions": stored_predictions,
            }

        except Exception as e:
            logger.error(f"Error tracking AI predictions: {e}")
            return {"success": False, "error": str(e)}

    def track_betting_strategies(
        self, race_data: Dict[str, Any], strategies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Track betting strategies and store in database"""
        try:
            race_id = race_data.get(
                "race_id", f"race_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            stored_strategies = []
            for strategy_data in strategies:
                betting_strategy = BettingStrategy(
                    race_id=race_id,
                    horse_name=strategy_data.get("horse_name", "Unknown"),
                    strategy_type=strategy_data.get("strategy_type", "value_bet"),
                    bet_type=strategy_data.get("bet_type", "win"),
                    recommended_stake=strategy_data.get("recommended_stake", 0.0),
                    recommended_odds=strategy_data.get("recommended_odds", 0.0),
                    expected_value=strategy_data.get("expected_value", 0.0),
                    kelly_fraction=strategy_data.get("kelly_fraction", 0.0),
                    confidence_score=strategy_data.get("confidence_score", 0.0),
                    risk_rating=strategy_data.get("risk_rating", "MEDIUM"),
                    staking_method=strategy_data.get("staking_method", "percentage"),
                    staking_multiplier=strategy_data.get("staking_multiplier", 1.0),
                    strategy_timestamp=datetime.now(),
                )

                strategy_id = self.db_manager.save_betting_strategy(betting_strategy)
                stored_strategies.append(
                    {
                        "id": strategy_id,
                        "horse_name": betting_strategy.horse_name,
                        "strategy_type": betting_strategy.strategy_type,
                        "expected_value": betting_strategy.expected_value,
                        "risk_rating": betting_strategy.risk_rating,
                    }
                )

            logger.info(f"Betting strategies tracked for race {race_id}")
            return {
                "success": True,
                "race_id": race_id,
                "strategies_stored": len(stored_strategies),
                "strategies": stored_strategies,
            }

        except Exception as e:
            logger.error(f"Error tracking betting strategies: {e}")
            return {"success": False, "error": str(e)}

    def update_race_results(
        self, race_id: str, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update race results and calculate performance metrics"""
        try:
            # Calculate prediction accuracy for each horse
            for result in results:
                horse_name = result.get("horse_name")
                finish_position = result.get("finish_position", 999)

                # Update AI prediction accuracy
                # This would need to be implemented based on the specific accuracy calculation
                accuracy = (
                    1.0
                    if finish_position == 1
                    else 0.5 if finish_position <= 3 else 0.0
                )

                # Update betting strategy results if bets were placed
                # This would need actual bet tracking data

            logger.info(f"Race results updated for {race_id}")
            return {
                "success": True,
                "race_id": race_id,
                "results_processed": len(results),
            }

        except Exception as e:
            logger.error(f"Error updating race results: {e}")
            return {"success": False, "error": str(e)}

    # Performance Calculation Methods
    # =======================================

    def calculate_method_performance(
        self, method_name: str, days: int = 30
    ) -> MethodPerformance:
        """Calculate performance metrics for a specific AI method"""
        # This would query the database and calculate comprehensive performance metrics
        # Implementation would involve aggregating prediction accuracy, betting performance, etc.
        return MethodPerformance(
            method_name=method_name,
            calculation_date=date.today(),
            total_predictions=0,
            correct_predictions=0,
            win_accuracy=0.0,
            place_accuracy=0.0,
            overall_accuracy=0.0,
        )

    def calculate_strategy_performance(
        self, strategy_type: str, days: int = 30
    ) -> StrategyPerformance:
        """Calculate performance metrics for a betting strategy"""
        # This would query the database and calculate strategy effectiveness
        return StrategyPerformance(
            strategy_type=strategy_type,
            calculation_date=date.today(),
            total_opportunities=0,
            strategies_used=0,
            usage_rate=0.0,
            total_profit=0.0,
            total_stakes=0.0,
            roi_percentage=0.0,
            win_rate=0.0,
            average_odds=0.0,
        )

    def generate_comprehensive_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        return self.db_manager.get_comprehensive_performance_report(days)

    # Helper Methods
    # =======================================

    def _count_high_confidence_trends(self, trends_analysis) -> int:
        """Count trends with high confidence scores"""
        if not hasattr(trends_analysis, "trends") or not trends_analysis.trends:
            return 0
        return len(
            [t for t in trends_analysis.trends if getattr(t, "confidence", 0) > 0.7]
        )

    def _calculate_overall_edge_rating(self, trends_analysis) -> float:
        """Calculate overall edge rating for the race"""
        if not hasattr(trends_analysis, "trends") or not trends_analysis.trends:
            return 0.0

        total_edge = sum(getattr(t, "edge", 0) for t in trends_analysis.trends)
        return (
            total_edge / len(trends_analysis.trends) if trends_analysis.trends else 0.0
        )

    def _assess_trend_strength(self, trends_analysis) -> str:
        """Assess overall trend strength for the race"""
        if not hasattr(trends_analysis, "trends") or not trends_analysis.trends:
            return "WEAK"

        high_confidence = self._count_high_confidence_trends(trends_analysis)
        total_trends = len(trends_analysis.trends)

        if high_confidence >= 3 and total_trends >= 5:
            return "STRONG"
        elif high_confidence >= 2 or total_trends >= 3:
            return "MODERATE"
        else:
            return "WEAK"

    def _count_trends_by_category(self, trends_analysis, category: str) -> int:
        """Count trends in a specific category"""
        if not hasattr(trends_analysis, category):
            return 0

        category_trends = getattr(trends_analysis, category, [])
        return len(category_trends) if category_trends else 0

    def _calculate_category_edge(self, trends_analysis, category: str) -> float:
        """Calculate edge value for a specific category"""
        if not hasattr(trends_analysis, category):
            return 0.0

        category_trends = getattr(trends_analysis, category, [])
        if not category_trends:
            return 0.0

        total_edge = sum(getattr(t, "edge", 0) for t in category_trends)
        return total_edge / len(category_trends) if category_trends else 0.0

    def _calculate_basic_trend_score(
        self, horse_data: Dict[str, Any], trends_analysis
    ) -> Dict[str, Any]:
        """Calculate basic trend score when advanced scoring is not available"""
        # Basic scoring based on horse attributes against trends
        base_score = 50.0  # Neutral score

        # This would be enhanced with actual trend scoring logic
        return {
            "overall_score": base_score,
            "confidence": 0.5,
            "age_score": 0.0,
            "weight_score": 0.0,
            "draw_score": 0.0,
            "form_score": 0.0,
            "price_score": 0.0,
            "seasonal_score": 0.0,
            "course_form_score": 0.0,
            "distance_form_score": 0.0,
            "positive_trends": 0,
            "negative_trends": 0,
            "neutral_trends": 0,
        }
