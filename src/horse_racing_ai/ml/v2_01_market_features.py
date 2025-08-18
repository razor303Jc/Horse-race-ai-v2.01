#!/usr/bin/env python3
"""
V2.01 Market-Based Feature Engineering
=====================================

Implements the critical market-based features discovered in v2.01 analysis:
- is_favorite (0.259 importance)
- odds_rank (0.230 importance)
- market_share (0.186 importance)
- field_size (0.070 importance)
- rating_odds_ratio (0.052 importance)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MarketFeatures:
    """Market-based features for a horse in a race."""

    horse_name: str
    odds_decimal: float
    is_favorite: bool
    odds_rank: int
    market_share: float
    odds_percentile: float
    field_size: int
    prize_per_runner: float
    rating_odds_ratio: float
    value_rating: float
    implied_probability: float


@dataclass
class RaceMarketAnalysis:
    """Complete market analysis for a race."""

    race_id: str
    field_size: int
    total_prize: float
    market_features: List[MarketFeatures]
    market_efficiency: float
    overround: float


class V201MarketFeatureEngine:
    """
    Advanced market-based feature engineering based on v2.01 analysis.

    Implements the sophisticated market features that showed highest
    importance in v2.01's feature analysis.
    """

    def __init__(self):
        self.feature_weights = {
            "is_favorite": 0.259,
            "odds_rank": 0.230,
            "market_share": 0.186,
            "field_size": 0.070,
            "rating_odds_ratio": 0.052,
            "odds_percentile": 0.043,
            "prize_per_runner": 0.023,
        }

    def calculate_market_features(
        self,
        race_data: pd.DataFrame,
        odds_column: str = "odds_decimal",
        rating_column: str = "or_rating",
        prize_money: float = 5000,
    ) -> RaceMarketAnalysis:
        """
        Calculate comprehensive market features for a race.

        Args:
            race_data: DataFrame with horse data including odds
            odds_column: Column name containing decimal odds
            rating_column: Column name containing official ratings
            prize_money: Total prize money for the race

        Returns:
            RaceMarketAnalysis with all market features
        """
        if odds_column not in race_data.columns:
            # Simulate odds if not available (for testing)
            race_data = race_data.copy()
            race_data[odds_column] = self._simulate_odds(race_data)

        if rating_column not in race_data.columns:
            # Use a proxy rating if official rating not available
            race_data = race_data.copy()
            race_data[rating_column] = self._estimate_rating(race_data)

        field_size = len(race_data)
        prize_per_runner = prize_money / field_size

        # Calculate odds-based features
        odds_data = race_data[odds_column].values
        ratings_data = race_data[rating_column].values

        # Market efficiency calculation
        implied_probs = 1 / odds_data
        overround = sum(implied_probs)
        market_efficiency = 1 / overround if overround > 0 else 0

        # True probabilities (adjusted for overround)
        true_probabilities = implied_probs / overround

        # Calculate features for each horse
        market_features = []

        for idx, (_, horse) in enumerate(race_data.iterrows()):
            odds = odds_data[idx]
            rating = ratings_data[idx]

            # Core market features
            is_favorite = odds == min(odds_data)
            odds_rank = self._calculate_odds_rank(odds, odds_data)
            market_share = true_probabilities[idx]
            odds_percentile = self._calculate_percentile(
                odds, odds_data, ascending=True
            )

            # Advanced features
            rating_odds_ratio = rating / odds if odds > 0 else 0
            implied_probability = 1 / odds if odds > 0 else 0
            value_rating = self._calculate_value_rating(
                rating, odds, ratings_data, odds_data
            )

            market_feature = MarketFeatures(
                horse_name=horse.get("name", f"Horse_{idx}"),
                odds_decimal=odds,
                is_favorite=is_favorite,
                odds_rank=odds_rank,
                market_share=market_share,
                odds_percentile=odds_percentile,
                field_size=field_size,
                prize_per_runner=prize_per_runner,
                rating_odds_ratio=rating_odds_ratio,
                value_rating=value_rating,
                implied_probability=implied_probability,
            )

            market_features.append(market_feature)

        return RaceMarketAnalysis(
            race_id=(
                race_data.get("race_id", ["UNKNOWN"])[0]
                if "race_id" in race_data.columns
                else "UNKNOWN"
            ),
            field_size=field_size,
            total_prize=prize_money,
            market_features=market_features,
            market_efficiency=market_efficiency,
            overround=overround,
        )

    def _calculate_odds_rank(self, odds: float, all_odds: np.ndarray) -> int:
        """Calculate the rank of odds (1 = favorite, higher = outsider)."""
        return int((all_odds < odds).sum() + 1)

    def _calculate_percentile(
        self, value: float, all_values: np.ndarray, ascending: bool = False
    ) -> float:
        """Calculate percentile rank of a value."""
        if ascending:
            return (all_values <= value).mean()
        else:
            return (all_values >= value).mean()

    def _calculate_value_rating(
        self, rating: float, odds: float, all_ratings: np.ndarray, all_odds: np.ndarray
    ) -> float:
        """
        Calculate value rating based on rating vs odds relationship.

        Positive value indicates horse may be undervalued by market.
        """
        if odds <= 0:
            return 0

        # Expected odds based on rating percentile
        rating_percentile = self._calculate_percentile(
            rating, all_ratings, ascending=False
        )
        expected_odds = 1 / (rating_percentile + 0.01)  # Avoid division by zero

        # Value = (Expected odds - Actual odds) / Expected odds
        value_rating = (
            (expected_odds - odds) / expected_odds if expected_odds > 0 else 0
        )

        return value_rating

    def _simulate_odds(self, race_data: pd.DataFrame) -> np.ndarray:
        """Simulate realistic odds based on horse performance data."""
        # Use win percentage as proxy for ability
        if "Percentage_wins" in race_data.columns:
            win_rates = race_data["Percentage_wins"].fillna(0.1)
        else:
            # Random simulation for testing
            win_rates = np.random.uniform(0.05, 0.4, len(race_data))

        # Convert win rates to implied probabilities
        implied_probs = win_rates / win_rates.sum()

        # Add market margin (overround)
        margin = 1.15  # 15% market margin
        adjusted_probs = implied_probs * margin

        # Convert to decimal odds
        odds = 1 / adjusted_probs

        # Add some randomness and ensure realistic range
        odds = odds * np.random.uniform(0.9, 1.1, len(odds))
        odds = np.clip(odds, 1.5, 50.0)  # Realistic odds range

        return odds

    def _estimate_rating(self, race_data: pd.DataFrame) -> np.ndarray:
        """Estimate official rating based on performance data."""
        if "Percentage_wins" in race_data.columns:
            win_rates = race_data["Percentage_wins"].fillna(0.1)
            # Scale to typical rating range (40-120)
            ratings = 40 + (win_rates * 80)
        else:
            # Random ratings for testing
            ratings = np.random.uniform(50, 100, len(race_data))

        return ratings

    def create_feature_matrix(
        self, market_analysis: RaceMarketAnalysis
    ) -> pd.DataFrame:
        """
        Create feature matrix for ML model training.

        Returns DataFrame with all market-based features.
        """
        features_list = []

        for mf in market_analysis.market_features:
            feature_dict = {
                "horse_name": mf.horse_name,
                "is_favorite": int(mf.is_favorite),
                "odds_rank": mf.odds_rank,
                "market_share": mf.market_share,
                "odds_percentile": mf.odds_percentile,
                "field_size": mf.field_size,
                "prize_per_runner": mf.prize_per_runner,
                "rating_odds_ratio": mf.rating_odds_ratio,
                "value_rating": mf.value_rating,
                "implied_probability": mf.implied_probability,
                "odds_decimal": mf.odds_decimal,
                # Derived features
                "is_outsider": int(mf.odds_decimal > 10.0),
                "is_well_backed": int(mf.market_share > 0.15),
                "value_bet_candidate": int(mf.value_rating > 0.2),
                "market_confidence": 1 / mf.odds_decimal,
                "field_size_normalized": mf.field_size
                / 20.0,  # Normalize to typical field size
            }
            features_list.append(feature_dict)

        return pd.DataFrame(features_list)

    def get_top_value_bets(
        self, market_analysis: RaceMarketAnalysis, min_value: float = 0.1
    ) -> List[MarketFeatures]:
        """
        Identify potential value betting opportunities.

        Args:
            market_analysis: Complete race market analysis
            min_value: Minimum value rating threshold

        Returns:
            List of horses with value betting potential
        """
        value_bets = [
            mf for mf in market_analysis.market_features if mf.value_rating > min_value
        ]

        # Sort by value rating (highest first)
        value_bets.sort(key=lambda x: x.value_rating, reverse=True)

        return value_bets

    def analyze_market_efficiency(
        self, market_analysis: RaceMarketAnalysis
    ) -> Dict[str, float]:
        """
        Analyze market efficiency metrics.

        Returns various market efficiency indicators.
        """
        market_features = market_analysis.market_features

        # Calculate metrics
        favorite_odds = min(mf.odds_decimal for mf in market_features)
        outsider_odds = max(mf.odds_decimal for mf in market_features)

        odds_spread = outsider_odds / favorite_odds
        value_opportunities = sum(1 for mf in market_features if mf.value_rating > 0.1)

        analysis = {
            "market_efficiency": market_analysis.market_efficiency,
            "overround": market_analysis.overround,
            "odds_spread": odds_spread,
            "favorite_odds": favorite_odds,
            "outsider_odds": outsider_odds,
            "value_opportunities": value_opportunities,
            "value_percentage": value_opportunities / len(market_features) * 100,
            "market_competitiveness": 1 / (odds_spread / market_analysis.field_size),
        }

        return analysis

    def export_market_features(
        self, market_analysis: RaceMarketAnalysis, filepath: str
    ) -> str:
        """Export market features to CSV format."""
        feature_matrix = self.create_feature_matrix(market_analysis)
        feature_matrix.to_csv(filepath, index=False)

        logger.info(f"Market features exported to {filepath}")
        return filepath

    def get_feature_importance_weights(self) -> Dict[str, float]:
        """Get feature importance weights from v2.01 analysis."""
        return self.feature_weights.copy()


def demo_market_features():
    """Demonstrate market feature engineering with sample data."""
    print("🎯 V2.01 Market Feature Engineering Demo")
    print("=" * 50)

    # Create sample race data
    sample_data = pd.DataFrame(
        {
            "name": [
                "Thunder Bolt",
                "Lightning Strike",
                "Storm Chaser",
                "Wind Runner",
                "Rain Dancer",
            ],
            "Percentage_wins": [0.25, 0.20, 0.15, 0.18, 0.12],
            "Total_races": [20, 25, 30, 22, 28],
            "age": [5, 4, 6, 5, 7],
        }
    )

    # Initialize market feature engine
    market_engine = V201MarketFeatureEngine()

    # Calculate market features
    market_analysis = market_engine.calculate_market_features(
        sample_data, prize_money=10000
    )

    print(f"\n🏇 Race Analysis:")
    print(f"Field Size: {market_analysis.field_size}")
    print(f"Total Prize: £{market_analysis.total_prize:,.0f}")
    print(f"Market Efficiency: {market_analysis.market_efficiency:.3f}")
    print(f"Overround: {market_analysis.overround:.3f}")

    print(f"\n📊 Market Features:")
    print("-" * 80)
    print(f"{'Horse':<15} {'Odds':<6} {'Fav':<4} {'Rank':<4} {'Share':<7} {'Value':<7}")
    print("-" * 80)

    for mf in market_analysis.market_features:
        print(
            f"{mf.horse_name:<15} {mf.odds_decimal:<6.2f} "
            f"{'Yes' if mf.is_favorite else 'No':<4} {mf.odds_rank:<4} "
            f"{mf.market_share:<7.3f} {mf.value_rating:<7.3f}"
        )

    # Value betting analysis
    value_bets = market_engine.get_top_value_bets(market_analysis, min_value=0.05)

    if value_bets:
        print(f"\n💰 Value Betting Opportunities:")
        for vb in value_bets:
            print(
                f"  {vb.horse_name}: Value={vb.value_rating:.3f}, Odds={vb.odds_decimal:.2f}"
            )
    else:
        print(f"\n💰 No significant value betting opportunities identified")

    # Market efficiency analysis
    efficiency = market_engine.analyze_market_efficiency(market_analysis)
    print(f"\n📈 Market Efficiency Analysis:")
    for key, value in efficiency.items():
        print(f"  {key.replace('_', ' ').title()}: {value:.3f}")


if __name__ == "__main__":
    demo_market_features()
