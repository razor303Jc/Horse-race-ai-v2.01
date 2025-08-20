#!/usr/bin/env python3
"""
🎯 Real Data AI Selections for August 20, 2025
==============================================

Generates enhanced AI selections using real racing data for today's cards.

Author: AI Assistant
Date: August 20, 2025
"""

import sys
from pathlib import Path
import pandas as pd
import psycopg2
import logging
from datetime import date

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import our enhanced generator
from enhanced_ai_selections_generator import EnhancedAISelectionsGenerator


def check_todays_race_data():
    """Check what race data we have for today."""
    logger.info("🔍 Checking today's race data...")

    # Database connection
    conn = psycopg2.connect(
        host="localhost",
        port="5434",
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )

    try:
        # Check for today's race cards
        query = """
            SELECT 
                course,
                COUNT(DISTINCT race_number) as races,
                COUNT(*) as total_runners,
                MIN(race_time) as first_race,
                MAX(race_time) as last_race
            FROM race_cards rc
            JOIN race_entries re ON rc.race_id = re.race_id  
            WHERE rc.race_date = CURRENT_DATE
            GROUP BY course
            ORDER BY course
        """

        df = pd.read_sql_query(query, conn)

        if len(df) == 0:
            logger.warning("⚠️ No race data found for today")
            return None

        logger.info(f"✅ Found race data for {len(df)} courses:")
        for _, row in df.iterrows():
            logger.info(
                f"   📍 {row['course']}: {row['races']} races, "
                f"{row['total_runners']} runners ({row['first_race']} - {row['last_race']})"
            )

        # Check advanced metrics coverage
        metrics_query = """
            SELECT 
                rc.course,
                COUNT(DISTINCT re.horse_name) as total_horses,
                COUNT(DISTINCT pr.horse_name) as power_rated,
                COUNT(DISTINCT sr.horse_name) as speed_rated,
                COUNT(DISTINCT mc.horse_name) as monte_carlo
            FROM race_cards rc
            JOIN race_entries re ON rc.race_id = re.race_id
            LEFT JOIN horse_power_ratings pr ON re.horse_name = pr.horse_name 
                AND rc.race_date = pr.race_date
            LEFT JOIN horse_speed_ratings sr ON re.horse_name = sr.horse_name 
                AND rc.race_date = sr.race_date
            LEFT JOIN monte_carlo_simulations mc ON re.horse_name = mc.horse_name 
                AND rc.race_date = mc.race_date
            WHERE rc.race_date = CURRENT_DATE
            GROUP BY rc.course
            ORDER BY rc.course
        """

        metrics_df = pd.read_sql_query(metrics_query, conn)

        logger.info("\n📊 Advanced metrics coverage:")
        for _, row in metrics_df.iterrows():
            power_pct = (
                (row["power_rated"] / row["total_horses"]) * 100
                if row["total_horses"] > 0
                else 0
            )
            speed_pct = (
                (row["speed_rated"] / row["total_horses"]) * 100
                if row["total_horses"] > 0
                else 0
            )
            mc_pct = (
                (row["monte_carlo"] / row["total_horses"]) * 100
                if row["total_horses"] > 0
                else 0
            )

            logger.info(
                f"   {row['course']}: Power {power_pct:.0f}%, "
                f"Speed {speed_pct:.0f}%, Monte Carlo {mc_pct:.0f}%"
            )

        return df

    finally:
        conn.close()


def run_real_data_selections():
    """Run enhanced AI selections with real data."""
    logger.info("🚀 Starting Real Data AI Selections for August 20, 2025")
    logger.info("=" * 60)

    try:
        # Check what data we have
        race_overview = check_todays_race_data()

        if race_overview is None:
            logger.error("❌ No race data available for today")
            return

        print("\n" + "=" * 60)
        print("🎯 ENHANCED AI SELECTIONS - REAL DATA")
        print(f"📅 Date: {date.today().strftime('%A, %B %d, %Y')}")
        print("=" * 60)

        # Initialize enhanced generator
        logger.info("🤖 Initializing Enhanced AI Selections Generator...")
        generator = EnhancedAISelectionsGenerator()

        # Show model status
        if generator.advanced_models:
            print(
                f"✅ Advanced Metrics Models: {len(generator.advanced_models)} loaded"
            )
            print(f"   Features: {len(generator.feature_columns)} advanced metrics")
        else:
            print("⚠️ Advanced models not available - using fallback mode")

        print()

        # Load real race data
        logger.info("📊 Loading real race data...")
        races_df = generator.load_race_data()

        if len(races_df) == 0:
            logger.warning("⚠️ No race data loaded")
            return

        print(f"📍 Loaded data from {races_df['course'].nunique()} courses:")
        for course in sorted(races_df["course"].unique()):
            course_data = races_df[races_df["course"] == course]
            races = course_data["race_number"].nunique()
            runners = len(course_data)
            print(f"   🏇 {course}: {races} races, {runners} runners")

        print()

        # Check advanced metrics coverage in loaded data
        advanced_cols = ["power_rating", "speed_figure", "pace_rating", "form_score"]
        coverage = {}
        for col in advanced_cols:
            if col in races_df.columns:
                coverage[col] = races_df[col].notna().sum() / len(races_df) * 100
            else:
                coverage[col] = 0

        print("📊 Advanced Metrics Coverage in Loaded Data:")
        for metric, pct in coverage.items():
            status = "✅" if pct > 50 else "⚠️" if pct > 0 else "❌"
            print(f"   {status} {metric.replace('_', ' ').title()}: {pct:.1f}%")

        print()

        # Generate enhanced AI selections
        logger.info("🎯 Generating Enhanced AI Selections...")

        # Feature engineering
        features_df = generator.engineer_features(races_df)
        logger.info(f"   ⚙️ Engineered {len(features_df.columns)} features")

        # Generate predictions
        predictions_df = generator.generate_predictions(features_df)
        logger.info(f"   🤖 Generated predictions for {len(predictions_df)} runners")

        # Create selections
        selections = generator.generate_selections(predictions_df)
        logger.info(f"   🏆 Created selections for {len(selections)} courses")

        # Generate and display report
        report = generator.format_selections_report(selections)
        print(report)

        # Save report
        report_file = (
            project_root / f"real_ai_selections_{date.today().strftime('%Y%m%d')}.txt"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"📄 Full report saved: {report_file}")

        # Show advanced metrics summary for real data
        show_real_data_summary(predictions_df, races_df)

        print("✅ Real Data AI Selections completed successfully!")

    except Exception as e:
        logger.error(f"❌ Real data selections failed: {e}")
        import traceback

        traceback.print_exc()


def show_real_data_summary(predictions_df, races_df):
    """Show summary of real data analysis."""
    print("\n" + "=" * 60)
    print("📈 REAL DATA ANALYSIS SUMMARY")
    print("=" * 60)

    # Prediction quality
    if "enhanced_win_probability" in predictions_df.columns:
        win_probs = predictions_df["enhanced_win_probability"]
        print(f"🎯 Win Probabilities: {win_probs.min():.1%} - {win_probs.max():.1%}")
        print(f"   Average: {win_probs.mean():.1%}")

        # Show distribution
        high_prob = (win_probs > 0.3).sum()
        medium_prob = ((win_probs > 0.15) & (win_probs <= 0.3)).sum()
        low_prob = (win_probs <= 0.15).sum()

        print(f"   High confidence (>30%): {high_prob} horses")
        print(f"   Medium confidence (15-30%): {medium_prob} horses")
        print(f"   Low confidence (<15%): {low_prob} horses")

    # Advanced metrics quality
    if "power_rating" in predictions_df.columns:
        power_ratings = predictions_df["power_rating"].dropna()
        if len(power_ratings) > 0:
            print(
                f"\n🔋 Power Ratings: {power_ratings.min():.1f} - {power_ratings.max():.1f}"
            )
            print(f"   Average: {power_ratings.mean():.1f}")

    if "speed_figure" in predictions_df.columns:
        speed_figures = predictions_df["speed_figure"].dropna()
        if len(speed_figures) > 0:
            print(
                f"⚡ Speed Figures: {speed_figures.min():.1f} - {speed_figures.max():.1f}"
            )
            print(f"   Average: {speed_figures.mean():.1f}")

    # Value opportunities
    if (
        "enhanced_win_probability" in predictions_df.columns
        and "win_odds" in predictions_df.columns
    ):
        # Calculate value bets
        predictions_df["implied_prob"] = 1.0 / predictions_df["win_odds"]
        predictions_df["value"] = (
            predictions_df["enhanced_win_probability"] - predictions_df["implied_prob"]
        )

        strong_value = (predictions_df["value"] > 0.1).sum()
        value_bets = (predictions_df["value"] > 0.05).sum()

        print(f"\n💰 Value Betting Opportunities:")
        print(f"   Strong value bets (>10% edge): {strong_value}")
        print(f"   Value bets (>5% edge): {value_bets}")

        if strong_value > 0:
            print("\n🎯 Top Value Opportunities:")
            top_value = predictions_df.nlargest(3, "value")[
                [
                    "horse_name",
                    "course",
                    "race_number",
                    "win_odds",
                    "enhanced_win_probability",
                    "value",
                ]
            ]
            for _, horse in top_value.iterrows():
                print(
                    f"   {horse['horse_name']} ({horse['course']} R{horse['race_number']}): "
                    f"{horse['win_odds']}/1 odds vs {horse['enhanced_win_probability']:.1%} prob "
                    f"= {horse['value']:.1%} edge"
                )

    # Model performance indicators
    if "prediction_confidence" in predictions_df.columns:
        confidence = predictions_df["prediction_confidence"]
        print(f"\n🎯 Model Confidence: {confidence.min():.1%} - {confidence.max():.1%}")
        print(f"   Average confidence: {confidence.mean():.1%}")

    print()


def main():
    """Main function."""
    print("🎯 Real Data AI Selections for August 20, 2025")
    print("==============================================")
    print()

    run_real_data_selections()


if __name__ == "__main__":
    main()
