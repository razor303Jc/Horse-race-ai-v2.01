#!/usr/bin/env python3
"""
🎯 Production AI Selections with Advanced Metrics
================================================

This demonstrates the enhanced AI selections system using the newly integrated
advanced metrics models for real-world horse racing predictions.

Usage:
    python production_ai_selections_demo.py

Features:
- Advanced metrics integration (power ratings, speed figures, pace analysis)
- 14 ML models for win/place/position predictions
- Enhanced ensemble predictions combining multiple model types
- Professional betting recommendations with value analysis

Author: AI Assistant
Date: August 20, 2025
"""

import sys
from pathlib import Path
import pandas as pd
import logging

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


def demonstrate_enhanced_ai_selections():
    """Demonstrate the enhanced AI selections system."""
    print("🎯 Enhanced AI Racing Selections - Production Demo")
    print("=" * 60)

    try:
        # Initialize the enhanced generator
        logger.info("🚀 Initializing Enhanced AI Selections Generator...")
        generator = EnhancedAISelectionsGenerator()

        # Show model status
        if generator.advanced_models:
            print(
                f"✅ Advanced Metrics Models: {len(generator.advanced_models)} loaded"
            )
            print(f"   - Win probability models: 5 algorithms")
            print(f"   - Position prediction models: 5 algorithms")
            print(f"   - Place probability models: 4 algorithms")
            print(f"   - Features: {len(generator.feature_columns)} advanced metrics")
        else:
            print("⚠️ Advanced models not available - using fallback mode")

        if generator.legacy_models:
            print(f"✅ Legacy Models: {len(generator.legacy_models)} loaded")
        else:
            print("ℹ️ No legacy models found (normal for advanced setup)")

        print()

        # Create sample race data (simulating today's races)
        print("📊 Creating sample race data...")
        sample_data = create_sample_race_data()
        print(f"   📍 {sample_data['course'].nunique()} courses")
        print(f"   🏇 {sample_data['race_number'].nunique()} races")
        print(f"   🐎 {len(sample_data)} total runners")
        print()

        # Generate enhanced AI selections
        print("🎯 Generating Enhanced AI Selections...")

        # Feature engineering
        features_df = generator.engineer_features(sample_data.copy())
        print(f"   ⚙️ Engineered {len(features_df.columns)} features")

        # Generate predictions
        predictions_df = generator.generate_predictions(features_df)
        print(f"   🤖 Generated predictions for {len(predictions_df)} runners")

        # Create selections
        selections = generator.generate_selections(predictions_df)
        print(f"   🏆 Created selections for {len(selections)} courses")
        print()

        # Display enhanced selections
        display_enhanced_selections(selections)

        # Generate and save full report
        report = generator.format_selections_report(selections)
        report_file = project_root / "enhanced_ai_selections_demo.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📄 Full report saved: {report_file}")
        print()

        # Show advanced metrics summary
        show_advanced_metrics_summary(predictions_df)

        print("✅ Enhanced AI Selections Demo completed successfully!")

    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise


def create_sample_race_data():
    """Create realistic sample race data."""
    # Realistic UK horse racing data
    races_data = {
        "race_id": ["kempton_1", "kempton_2", "lingfield_1", "lingfield_2"],
        "course": ["Kempton", "Kempton", "Lingfield", "Lingfield"],
        "race_number": [1, 2, 1, 2],
        "race_time": ["14:15", "14:50", "15:25", "16:00"],
        "race_date": ["2025-08-20"] * 4,
        "race_name": [
            "Novice Stakes",
            "Handicap",
            "Maiden Stakes",
            "Conditions Stakes",
        ],
        "distance": [1400, 1600, 1200, 2000],
        "prize": [12000, 15000, 8000, 25000],
    }

    # Sample horses with realistic advanced metrics
    horses_data = []

    # Kempton Race 1 - Competitive novice race
    kempton_r1 = [
        {
            "horse_name": "Royal Prospect",
            "jockey": "W. Buick",
            "trainer": "C. Appleby",
            "odds": 2.5,
            "power_rating": 92,
            "speed_figure": 98,
            "form_score": 85,
        },
        {
            "horse_name": "Desert Storm",
            "jockey": "J. Doyle",
            "trainer": "R. Hannon",
            "odds": 4.0,
            "power_rating": 88,
            "speed_figure": 94,
            "form_score": 82,
        },
        {
            "horse_name": "Midnight Express",
            "jockey": "T. Marquand",
            "trainer": "M. Johnston",
            "odds": 6.5,
            "power_rating": 84,
            "speed_figure": 90,
            "form_score": 78,
        },
        {
            "horse_name": "Swift Arrow",
            "jockey": "S. Levey",
            "trainer": "D. Simcock",
            "odds": 9.0,
            "power_rating": 80,
            "speed_figure": 86,
            "form_score": 75,
        },
        {
            "horse_name": "Thunder Bay",
            "jockey": "H. Bentley",
            "trainer": "J. Gosden",
            "odds": 12.0,
            "power_rating": 76,
            "speed_figure": 82,
            "form_score": 72,
        },
    ]

    # Kempton Race 2 - Handicap
    kempton_r2 = [
        {
            "horse_name": "King of Hearts",
            "jockey": "R. Moore",
            "trainer": "A. Balding",
            "odds": 3.2,
            "power_rating": 86,
            "speed_figure": 92,
            "form_score": 80,
        },
        {
            "horse_name": "Brave Spirit",
            "jockey": "L. Dettori",
            "trainer": "J. Gosden",
            "odds": 5.5,
            "power_rating": 83,
            "speed_figure": 89,
            "form_score": 77,
        },
        {
            "horse_name": "Golden Quest",
            "jockey": "O. Murphy",
            "trainer": "A. Balding",
            "odds": 7.0,
            "power_rating": 81,
            "speed_figure": 87,
            "form_score": 74,
        },
        {
            "horse_name": "Silver Moon",
            "jockey": "C. Lee",
            "trainer": "R. Beckett",
            "odds": 11.0,
            "power_rating": 78,
            "speed_figure": 84,
            "form_score": 71,
        },
        {
            "horse_name": "Storm Warning",
            "jockey": "A. Kirby",
            "trainer": "P. Cole",
            "odds": 16.0,
            "power_rating": 74,
            "speed_figure": 80,
            "form_score": 68,
        },
    ]

    # Add similar data for Lingfield races...
    lingfield_r1 = [
        {
            "horse_name": "First Light",
            "jockey": "J. Spencer",
            "trainer": "M. Bell",
            "odds": 2.8,
            "power_rating": 89,
            "speed_figure": 95,
            "form_score": 83,
        },
        {
            "horse_name": "Dawn Raider",
            "jockey": "G. Baker",
            "trainer": "N. Littmoden",
            "odds": 4.5,
            "power_rating": 85,
            "speed_figure": 91,
            "form_score": 79,
        },
        {
            "horse_name": "Quick Silver",
            "jockey": "K. Shoemark",
            "trainer": "S. Dow",
            "odds": 8.0,
            "power_rating": 82,
            "speed_figure": 88,
            "form_score": 76,
        },
    ]

    lingfield_r2 = [
        {
            "horse_name": "Master Plan",
            "jockey": "R. Havlin",
            "trainer": "J. Gosden",
            "odds": 2.0,
            "power_rating": 94,
            "speed_figure": 100,
            "form_score": 87,
        },
        {
            "horse_name": "Royal Command",
            "jockey": "W. Buick",
            "trainer": "C. Appleby",
            "odds": 3.5,
            "power_rating": 90,
            "speed_figure": 96,
            "form_score": 84,
        },
        {
            "horse_name": "Night Vision",
            "jockey": "T. Marquand",
            "trainer": "M. Johnston",
            "odds": 6.0,
            "power_rating": 87,
            "speed_figure": 93,
            "form_score": 81,
        },
        {
            "horse_name": "Star Performer",
            "jockey": "S. Levey",
            "trainer": "D. Simcock",
            "odds": 10.0,
            "power_rating": 83,
            "speed_figure": 89,
            "form_score": 77,
        },
    ]

    # Combine all race data
    all_races = [kempton_r1, kempton_r2, lingfield_r1, lingfield_r2]

    for race_idx, race_horses in enumerate(all_races):
        race_info = {k: v[race_idx] for k, v in races_data.items()}

        for horse_idx, horse in enumerate(race_horses):
            row = race_info.copy()
            row.update(
                {
                    "horse_name": horse["horse_name"],
                    "jockey": horse["jockey"],
                    "trainer": horse["trainer"],
                    "horse_age": 3 + (horse_idx % 3),  # Ages 3-5
                    "horse_weight_kg": 56 + horse_idx,  # Weights 56-60kg
                    "draw": horse_idx + 1,
                    "win_odds": horse["odds"],
                    "place_odds": horse["odds"] / 2.2,  # Typical place odds ratio
                    "power_rating": horse["power_rating"],
                    "speed_figure": horse["speed_figure"],
                    "pace_rating": horse["speed_figure"] - 2,  # Slightly lower pace
                    "form_score": horse["form_score"],
                    "mc_win_probability": 1.0
                    / horse["odds"]
                    * 0.9,  # Adjusted from odds
                    "mc_place_probability": 1.0 / (horse["odds"] / 2.2) * 0.8,
                    "jockey_win_pct": 0.10
                    + (hash(horse["jockey"]) % 20) / 200,  # 10-20%
                    "trainer_win_pct": 0.12
                    + (hash(horse["trainer"]) % 25) / 200,  # 12-25%
                }
            )
            horses_data.append(row)

    return pd.DataFrame(horses_data)


def display_enhanced_selections(selections):
    """Display enhanced selections in a formatted way."""
    print("🏆 ENHANCED AI SELECTIONS")
    print("=" * 50)

    for course, races in selections.items():
        print(f"\n🏇 {course.upper()}")
        print("-" * 30)

        for race in races:
            print(f"\nRace {race['race_number']} - {race['race_time']}")
            print(f"Field: {race['field_size']} runners")

            for i, selection in enumerate(race["selections"], 1):
                # Enhanced display with advanced metrics
                print(
                    f"  {i}. {selection['horse_name']} ({selection['jockey']}) - {selection['win_odds']}/1"
                )
                print(
                    f"     Win: {selection['enhanced_win_prob']:.1%} | "
                    f"Place: {selection['enhanced_place_prob']:.1%} | "
                    f"Pos: {selection['predicted_position']:.1f}"
                )

                if selection["power_rating"] != "N/A":
                    print(
                        f"     Power: {selection['power_rating']:.0f} | "
                        f"Speed: {selection['speed_figure']:.0f} | "
                        f"Form: {selection['form_score']:.0f}"
                    )

                print(f"     {selection['betting_recommendation']}")
                print()


def show_advanced_metrics_summary(predictions_df):
    """Show summary of advanced metrics performance."""
    print("📊 ADVANCED METRICS SUMMARY")
    print("=" * 40)

    if "advanced_win_probability" in predictions_df.columns:
        win_probs = predictions_df["advanced_win_probability"]
        print(f"Win Probabilities: {win_probs.min():.1%} - {win_probs.max():.1%}")
        print(f"Average Win Prob: {win_probs.mean():.1%}")

    if "advanced_predicted_position" in predictions_df.columns:
        positions = predictions_df["advanced_predicted_position"]
        print(f"Predicted Positions: {positions.min():.1f} - {positions.max():.1f}")

    if "prediction_confidence" in predictions_df.columns:
        confidence = predictions_df["prediction_confidence"]
        print(f"Model Confidence: {confidence.min():.1%} - {confidence.max():.1%}")

    # Show top performers by power rating
    if "power_rating" in predictions_df.columns:
        top_rated = predictions_df.nlargest(3, "power_rating")[
            ["horse_name", "course", "power_rating", "enhanced_win_probability"]
        ]
        print("\n🔝 Top Power Rated Horses:")
        for _, horse in top_rated.iterrows():
            print(
                f"   {horse['horse_name']} ({horse['course']}): "
                f"Power {horse['power_rating']:.0f}, Win {horse.get('enhanced_win_probability', 0):.1%}"
            )

    print()


def main():
    """Main function."""
    print("🎯 Enhanced AI Racing Selections - Production Demo")
    print("================================================")
    print()

    demonstrate_enhanced_ai_selections()


if __name__ == "__main__":
    main()
