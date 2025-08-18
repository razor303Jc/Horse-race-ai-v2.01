#!/usr/bin/env python3
"""
🏇 Pre-Race Pipeline for Live Betting
====================================

Comprehensive pre-race analysis pipeline for:
1. Race-day data preparation
2. Real-time prediction generation
3. Live betting opportunity identification
4. Paper trading signal generation

Leverages existing ML models and feature systems for betting insights.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/pre_race_pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class PreRacePipeline:
    """Pre-race analysis pipeline for live betting and paper trading"""

    def __init__(self):
        # Database configuration
        self.db_config = {
            "host": "horse_racing_postgres_clean",
            "port": 5432,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Output directories
        self.output_dir = Path("/app/data/live_betting")
        self.predictions_dir = self.output_dir / "predictions"
        self.signals_dir = self.output_dir / "signals"

        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.predictions_dir.mkdir(parents=True, exist_ok=True)
        self.signals_dir.mkdir(parents=True, exist_ok=True)

        # Betting parameters
        self.min_confidence = 0.65  # Minimum prediction confidence
        self.value_threshold = 1.20  # Minimum odds value ratio
        self.max_risk_per_race = 0.05  # Max 5% of bankroll per race

        logger.info("🏇 Pre-Race Pipeline initialized")

    def get_db_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return None

    def get_todays_races(self) -> List[Dict]:
        """Get today's race data"""
        logger.info("📅 Fetching today's race data...")

        conn = self.get_db_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get today's races
            today = datetime.now().strftime("%Y-%m-%d")

            query = """
            SELECT DISTINCT
                r.id,
                r.name as race_name,
                r.start_time,
                r.course,
                r.distance,
                r.conditions,
                r.prize_money,
                COUNT(h.id) as runner_count
            FROM races r
            LEFT JOIN horses h ON r.id = h.race_id
            WHERE DATE(r.start_time) = %s
            AND r.start_time > NOW()
            GROUP BY r.id, r.name, r.start_time, r.course, r.distance, r.conditions, r.prize_money
            ORDER BY r.start_time
            """

            cursor.execute(query, (today,))
            races = cursor.fetchall()

            logger.info(f"📊 Found {len(races)} races today")
            return [dict(race) for race in races]

        except Exception as e:
            logger.error(f"❌ Error fetching races: {e}")
            return []
        finally:
            conn.close()

    def get_race_horses(self, race_id: str) -> List[Dict]:
        """Get horses for a specific race with historical data"""
        conn = self.get_db_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
            SELECT 
                h.id,
                h.name as horse_name,
                h.number,
                h.age,
                h.weight,
                h.jockey,
                h.trainer,
                h.odds,
                h.form,
                h.last_ran,
                h.distance_from_ideal,
                h.going_preference,
                h.class_rating,
                
                -- Recent performance metrics
                COALESCE(AVG(CASE WHEN pr.finishing_position <= 3 THEN 1.0 ELSE 0.0 END), 0) as win_place_rate,
                COALESCE(AVG(pr.finishing_position), 10) as avg_position,
                COUNT(pr.id) as race_count_last_year,
                
                -- Best recent finish
                MIN(pr.finishing_position) as best_recent_position
                
            FROM horses h
            LEFT JOIN performance_records pr ON h.id = pr.horse_id 
                AND pr.date >= NOW() - INTERVAL '365 days'
            WHERE h.race_id = %s
            GROUP BY h.id, h.name, h.number, h.age, h.weight, h.jockey, h.trainer, 
                     h.odds, h.form, h.last_ran, h.distance_from_ideal, 
                     h.going_preference, h.class_rating
            ORDER BY h.number
            """

            cursor.execute(query, (race_id,))
            horses = cursor.fetchall()

            return [dict(horse) for horse in horses]

        except Exception as e:
            logger.error(f"❌ Error fetching horses for race {race_id}: {e}")
            return []
        finally:
            conn.close()

    def calculate_form_score(self, horse: Dict) -> float:
        """Calculate form score using existing ML logic"""
        try:
            # Base score from recent performance
            form_score = 0.5

            # Win/place rate factor (max +0.3)
            win_rate = horse.get("win_place_rate", 0)
            form_score += min(win_rate * 0.3, 0.3)

            # Average position factor (max +0.2)
            avg_pos = horse.get("avg_position", 10)
            if avg_pos <= 3:
                form_score += 0.2
            elif avg_pos <= 5:
                form_score += 0.1
            elif avg_pos <= 8:
                form_score += 0.05

            # Recent activity factor
            race_count = horse.get("race_count_last_year", 0)
            if race_count >= 5:
                form_score += 0.1
            elif race_count >= 3:
                form_score += 0.05

            # Best recent finish bonus
            best_pos = horse.get("best_recent_position", 99)
            if best_pos == 1:
                form_score += 0.15
            elif best_pos <= 2:
                form_score += 0.1
            elif best_pos <= 3:
                form_score += 0.05

            return min(form_score, 1.0)

        except Exception as e:
            logger.error(f"❌ Error calculating form score: {e}")
            return 0.5

    def calculate_power_rating(self, horse: Dict, race: Dict) -> float:
        """Calculate power rating based on class, conditions, distance"""
        try:
            power_rating = 0.5

            # Class rating factor
            class_rating = horse.get("class_rating", 0)
            if class_rating > 80:
                power_rating += 0.2
            elif class_rating > 60:
                power_rating += 0.1
            elif class_rating > 40:
                power_rating += 0.05

            # Distance suitability
            distance_diff = abs(horse.get("distance_from_ideal", 0))
            if distance_diff <= 200:  # meters
                power_rating += 0.15
            elif distance_diff <= 400:
                power_rating += 0.1
            elif distance_diff <= 800:
                power_rating += 0.05

            # Going/conditions preference
            going_pref = horse.get("going_preference", "unknown")
            race_conditions = race.get("conditions", "").lower()
            if going_pref.lower() in race_conditions:
                power_rating += 0.1

            # Weight factor
            weight = horse.get("weight", 60)
            if weight <= 56:
                power_rating += 0.1
            elif weight >= 62:
                power_rating -= 0.05

            return min(power_rating, 1.0)

        except Exception as e:
            logger.error(f"❌ Error calculating power rating: {e}")
            return 0.5

    def calculate_speed_rating(self, horse: Dict) -> float:
        """Calculate speed rating from recent performance"""
        try:
            # Base speed from average position
            avg_pos = horse.get("avg_position", 10)
            if avg_pos <= 2:
                speed_rating = 0.9
            elif avg_pos <= 4:
                speed_rating = 0.75
            elif avg_pos <= 6:
                speed_rating = 0.6
            elif avg_pos <= 8:
                speed_rating = 0.45
            else:
                speed_rating = 0.3

            # Adjust for consistency
            race_count = horse.get("race_count_last_year", 0)
            if race_count >= 5:
                speed_rating += 0.05

            # Recent activity bonus
            last_ran = horse.get("last_ran")
            if last_ran:
                # Assuming recent activity is better (would need date parsing)
                speed_rating += 0.02

            return min(speed_rating, 1.0)

        except Exception as e:
            logger.error(f"❌ Error calculating speed rating: {e}")
            return 0.5

    def run_monte_carlo_simulation(
        self, horses: List[Dict], num_simulations: int = 1000
    ) -> Dict:
        """Run Monte Carlo simulation for race outcome probabilities"""
        logger.info(f"🎲 Running Monte Carlo simulation ({num_simulations} runs)...")

        try:
            # Prepare horse ratings
            horse_ratings = []
            for horse in horses:
                form = horse.get("form_score", 0.5)
                power = horse.get("power_rating", 0.5)
                speed = horse.get("speed_rating", 0.5)

                # Combined rating with random variation
                base_rating = (form * 0.4) + (power * 0.3) + (speed * 0.3)
                horse_ratings.append(
                    {
                        "id": horse["id"],
                        "name": horse["horse_name"],
                        "number": horse["number"],
                        "base_rating": base_rating,
                        "wins": 0,
                        "places": 0,
                        "shows": 0,
                    }
                )

            # Run simulations
            for _ in range(num_simulations):
                # Add random variation to each horse's performance
                sim_ratings = []
                for horse_rating in horse_ratings:
                    # Random variation ±20%
                    variation = np.random.normal(0, 0.2)
                    sim_rating = max(0.1, horse_rating["base_rating"] + variation)
                    sim_ratings.append(
                        {"index": len(sim_ratings), "rating": sim_rating}
                    )

                # Sort by performance (highest rating wins)
                sim_ratings.sort(key=lambda x: x["rating"], reverse=True)

                # Award positions
                for pos, result in enumerate(sim_ratings[:3]):
                    idx = result["index"]
                    if pos == 0:  # Win
                        horse_ratings[idx]["wins"] += 1
                        horse_ratings[idx]["places"] += 1
                        horse_ratings[idx]["shows"] += 1
                    elif pos == 1:  # Place
                        horse_ratings[idx]["places"] += 1
                        horse_ratings[idx]["shows"] += 1
                    elif pos == 2:  # Show
                        horse_ratings[idx]["shows"] += 1

            # Calculate probabilities
            for horse_rating in horse_ratings:
                horse_rating["win_probability"] = horse_rating["wins"] / num_simulations
                horse_rating["place_probability"] = (
                    horse_rating["places"] / num_simulations
                )
                horse_rating["show_probability"] = (
                    horse_rating["shows"] / num_simulations
                )

            # Sort by win probability
            horse_ratings.sort(key=lambda x: x["win_probability"], reverse=True)

            return {
                "simulations": num_simulations,
                "results": horse_ratings,
                "top_3": horse_ratings[:3],
            }

        except Exception as e:
            logger.error(f"❌ Monte Carlo simulation error: {e}")
            return {"simulations": 0, "results": [], "top_3": []}

    def analyze_race(self, race: Dict) -> Dict:
        """Complete race analysis with predictions and betting signals"""
        logger.info(f"🔍 Analyzing race: {race['race_name']} at {race['course']}")

        # Get horses for this race
        horses = self.get_race_horses(race["id"])
        if not horses:
            logger.warning(f"⚠️ No horses found for race {race['id']}")
            return {}

        # Calculate ratings for each horse
        for horse in horses:
            horse["form_score"] = self.calculate_form_score(horse)
            horse["power_rating"] = self.calculate_power_rating(horse, race)
            horse["speed_rating"] = self.calculate_speed_rating(horse)

            # Combined ML score
            horse["ml_score"] = (
                horse["form_score"] * 0.4
                + horse["power_rating"] * 0.3
                + horse["speed_rating"] * 0.3
            )

        # Run Monte Carlo simulation
        monte_carlo = self.run_monte_carlo_simulation(horses)

        # Generate betting signals
        betting_signals = self.generate_betting_signals(horses, monte_carlo)

        analysis = {
            "race_info": race,
            "horses": horses,
            "monte_carlo": monte_carlo,
            "betting_signals": betting_signals,
            "analysis_time": datetime.now().isoformat(),
            "confidence_level": self.calculate_analysis_confidence(horses, monte_carlo),
        }

        return analysis

    def generate_betting_signals(
        self, horses: List[Dict], monte_carlo: Dict
    ) -> List[Dict]:
        """Generate betting signals based on value and confidence"""
        signals = []

        for i, horse in enumerate(horses):
            # Get Monte Carlo probabilities
            mc_horse = next(
                (h for h in monte_carlo["results"] if h["id"] == horse["id"]), None
            )
            if not mc_horse:
                continue

            # Calculate implied probability from odds
            odds = horse.get("odds", 10.0)
            if odds <= 1:
                continue

            implied_prob = 1 / odds
            win_prob = mc_horse["win_probability"]
            place_prob = mc_horse["place_probability"]

            # Value calculation
            win_value = win_prob / implied_prob if implied_prob > 0 else 0
            place_value = (
                place_prob / (implied_prob * 0.5) if implied_prob > 0 else 0
            )  # Approximate place odds

            # Generate signals
            if win_value > self.value_threshold and win_prob > self.min_confidence:
                signals.append(
                    {
                        "horse_id": horse["id"],
                        "horse_name": horse["horse_name"],
                        "number": horse["number"],
                        "bet_type": "WIN",
                        "confidence": win_prob,
                        "value_ratio": win_value,
                        "recommended_stake": min(
                            win_prob * 0.1, self.max_risk_per_race
                        ),
                        "odds": odds,
                        "reasoning": f"High value win bet - {win_prob:.1%} chance at {odds:.1f}/1",
                    }
                )

            if (
                place_value > 1.15 and place_prob > 0.4
            ):  # Lower threshold for place bets
                signals.append(
                    {
                        "horse_id": horse["id"],
                        "horse_name": horse["horse_name"],
                        "number": horse["number"],
                        "bet_type": "PLACE",
                        "confidence": place_prob,
                        "value_ratio": place_value,
                        "recommended_stake": min(
                            place_prob * 0.05, self.max_risk_per_race * 0.5
                        ),
                        "odds": odds / 2,  # Approximate place odds
                        "reasoning": f"Solid place chance - {place_prob:.1%} probability",
                    }
                )

        # Sort by value ratio
        signals.sort(key=lambda x: x["value_ratio"], reverse=True)
        return signals

    def calculate_analysis_confidence(
        self, horses: List[Dict], monte_carlo: Dict
    ) -> float:
        """Calculate overall confidence in the analysis"""
        try:
            # Factors affecting confidence
            num_horses = len(horses)
            data_quality = (
                sum(1 for h in horses if h.get("race_count_last_year", 0) >= 3)
                / num_horses
            )

            # Monte Carlo spread (less spread = more confidence)
            if monte_carlo["results"]:
                win_probs = [h["win_probability"] for h in monte_carlo["results"]]
                prob_spread = max(win_probs) - min(win_probs)
                spread_factor = min(prob_spread, 0.5) / 0.5  # Normalize
            else:
                spread_factor = 0.5

            # Overall confidence
            confidence = (data_quality * 0.6) + ((1 - spread_factor) * 0.4)
            return min(confidence, 1.0)

        except Exception as e:
            logger.error(f"❌ Error calculating confidence: {e}")
            return 0.5

    def save_analysis(self, analysis: Dict, race_id: str):
        """Save analysis results to files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save full analysis
            analysis_file = self.predictions_dir / f"race_{race_id}_{timestamp}.json"
            with open(analysis_file, "w") as f:
                json.dump(analysis, f, indent=2, default=str)

            # Save betting signals separately
            if analysis.get("betting_signals"):
                signals_file = self.signals_dir / f"signals_{race_id}_{timestamp}.json"
                with open(signals_file, "w") as f:
                    json.dump(analysis["betting_signals"], f, indent=2, default=str)

            logger.info(f"💾 Analysis saved for race {race_id}")

        except Exception as e:
            logger.error(f"❌ Error saving analysis: {e}")

    def run_pre_race_analysis(self):
        """Run complete pre-race analysis for today's races"""
        logger.info("🚀 Starting Pre-Race Analysis Pipeline")

        races = self.get_todays_races()
        if not races:
            logger.info("📭 No races found for today")
            return

        total_signals = 0
        high_value_bets = []

        for race in races:
            logger.info(f"🏇 Processing: {race['race_name']} ({race['start_time']})")

            analysis = self.analyze_race(race)
            if analysis:
                # Save analysis
                self.save_analysis(analysis, race["id"])

                # Count signals
                signals = analysis.get("betting_signals", [])
                total_signals += len(signals)

                # Collect high-value bets
                for signal in signals:
                    if signal["value_ratio"] > 1.5:
                        high_value_bets.append(
                            {
                                "race": race["race_name"],
                                "start_time": race["start_time"],
                                **signal,
                            }
                        )

        # Summary report
        logger.info("=" * 60)
        logger.info("📊 PRE-RACE ANALYSIS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"🏇 Races analyzed: {len(races)}")
        logger.info(f"🎯 Total betting signals: {total_signals}")
        logger.info(f"💎 High-value opportunities: {len(high_value_bets)}")

        if high_value_bets:
            logger.info("\n🔥 TOP VALUE BETS:")
            for bet in high_value_bets[:5]:  # Top 5
                logger.info(f"   {bet['race']} - #{bet['number']} {bet['horse_name']}")
                logger.info(
                    f"   {bet['bet_type']} @ {bet['odds']:.1f}/1 (Value: {bet['value_ratio']:.2f})"
                )
                logger.info(
                    f"   Confidence: {bet['confidence']:.1%} | Stake: {bet['recommended_stake']:.1%}"
                )
                logger.info("")

        logger.info("✅ Pre-race analysis complete")

    def monitor_live_races(self):
        """Monitor races starting soon for last-minute analysis"""
        logger.info("👀 Starting live race monitoring...")

        while True:
            try:
                # Get races starting in next 30 minutes
                conn = self.get_db_connection()
                if conn:
                    cursor = conn.cursor(cursor_factory=RealDictCursor)

                    query = """
                    SELECT id, name, start_time, course
                    FROM races
                    WHERE start_time BETWEEN NOW() AND NOW() + INTERVAL '30 minutes'
                    AND start_time > NOW()
                    ORDER BY start_time
                    """

                    cursor.execute(query)
                    upcoming_races = cursor.fetchall()
                    conn.close()

                    for race in upcoming_races:
                        logger.info(
                            f"⏰ Upcoming: {race['name']} at {race['start_time']}"
                        )
                        # Could trigger last-minute analysis here

                time.sleep(300)  # Check every 5 minutes

            except KeyboardInterrupt:
                logger.info("🛑 Live monitoring stopped")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                time.sleep(60)


def main():
    """Main execution function"""
    pipeline = PreRacePipeline()

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        pipeline.monitor_live_races()
    else:
        pipeline.run_pre_race_analysis()


if __name__ == "__main__":
    main()
