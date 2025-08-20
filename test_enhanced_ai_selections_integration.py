#!/usr/bin/env python3
"""
🧪 Test Enhanced AI Selections Integration
=========================================

Tests the integration of advanced metrics models with the AI selections system.

Features:
- Verifies model loading (both legacy and advanced)
- Tests feature engineering with advanced metrics
- Validates prediction generation
- Demonstrates enhanced selections output

Author: AI Assistant
Date: August 20, 2025
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging
import joblib

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


def create_test_data():
    """Create sample race data for testing."""
    logger.info("📊 Creating test race data...")

    # Sample race data with advanced metrics
    test_data = {
        "race_id": [f"test_race_{i//5 + 1}" for i in range(20)],
        "course": ["Ascot"] * 10 + ["Newmarket"] * 10,
        "race_number": [1, 1, 1, 1, 1, 2, 2, 2, 2, 2] * 2,
        "race_time": [
            "14:30",
            "14:30",
            "14:30",
            "14:30",
            "14:30",
            "15:05",
            "15:05",
            "15:05",
            "15:05",
            "15:05",
        ]
        * 2,
        "race_date": ["2025-08-20"] * 20,
        "race_name": ["Test Stakes"] * 20,
        "distance": [1600] * 20,
        "prize": [50000] * 20,
        "horse_name": [
            "Thunder Strike",
            "Lightning Bolt",
            "Storm Chaser",
            "Wind Runner",
            "Fire Flash",
            "Golden Arrow",
            "Silver Bullet",
            "Bronze Star",
            "Iron Will",
            "Steel Force",
            "Speed Demon",
            "Fast Track",
            "Quick Step",
            "Rapid Fire",
            "Swift Arrow",
            "Night Rider",
            "Day Dreamer",
            "Star Gazer",
            "Moon Walker",
            "Sun Beam",
        ],
        "jockey": [
            "J. Smith",
            "M. Jones",
            "R. Brown",
            "S. Wilson",
            "T. Davis",
            "A. Miller",
            "B. Garcia",
            "C. Rodriguez",
            "D. Martinez",
            "E. Anderson",
            "F. Taylor",
            "G. Thomas",
            "H. Jackson",
            "I. White",
            "J. Harris",
            "K. Martin",
            "L. Thompson",
            "M. Garcia",
            "N. Martinez",
            "O. Robinson",
        ],
        "trainer": [
            "Trainer A",
            "Trainer B",
            "Trainer C",
            "Trainer D",
            "Trainer E",
            "Trainer F",
            "Trainer G",
            "Trainer H",
            "Trainer I",
            "Trainer J",
            "Trainer K",
            "Trainer L",
            "Trainer M",
            "Trainer N",
            "Trainer O",
            "Trainer P",
            "Trainer Q",
            "Trainer R",
            "Trainer S",
            "Trainer T",
        ],
        "horse_age": [3, 4, 5, 3, 4, 5, 3, 4, 6, 5, 3, 4, 5, 6, 4, 3, 5, 4, 6, 3],
        "horse_weight_kg": [
            55,
            57,
            59,
            56,
            58,
            60,
            54,
            57,
            61,
            58,
            56,
            59,
            57,
            60,
            55,
            58,
            59,
            56,
            61,
            57,
        ],
        "draw": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
        "win_odds": [
            3.5,
            5.0,
            8.0,
            12.0,
            15.0,
            2.8,
            4.5,
            7.0,
            10.0,
            20.0,
            4.0,
            6.0,
            9.0,
            13.0,
            18.0,
            3.2,
            5.5,
            8.5,
            11.0,
            25.0,
        ],
        "place_odds": [
            1.8,
            2.2,
            3.0,
            4.0,
            5.0,
            1.6,
            2.0,
            2.8,
            3.5,
            6.0,
            2.0,
            2.5,
            3.2,
            4.2,
            5.5,
            1.9,
            2.3,
            3.1,
            3.8,
            7.0,
        ],
        # Advanced metrics data
        "power_rating": [
            95,
            88,
            82,
            75,
            72,
            98,
            91,
            84,
            78,
            68,
            92,
            86,
            80,
            74,
            70,
            94,
            87,
            81,
            76,
            65,
        ],
        "speed_figure": [
            102,
            94,
            87,
            80,
            77,
            105,
            96,
            89,
            82,
            74,
            99,
            91,
            84,
            78,
            75,
            101,
            93,
            86,
            79,
            71,
        ],
        "pace_rating": [
            98,
            90,
            85,
            78,
            75,
            100,
            93,
            87,
            80,
            72,
            95,
            88,
            82,
            76,
            73,
            97,
            89,
            83,
            77,
            69,
        ],
        "form_score": [
            90,
            85,
            80,
            75,
            70,
            92,
            87,
            82,
            77,
            65,
            88,
            83,
            78,
            73,
            68,
            89,
            84,
            79,
            74,
            62,
        ],
        "mc_win_probability": [
            0.28,
            0.20,
            0.12,
            0.08,
            0.06,
            0.35,
            0.22,
            0.14,
            0.10,
            0.05,
            0.25,
            0.16,
            0.11,
            0.07,
            0.05,
            0.31,
            0.18,
            0.11,
            0.09,
            0.04,
        ],
        "mc_place_probability": [
            0.65,
            0.55,
            0.45,
            0.35,
            0.30,
            0.70,
            0.60,
            0.50,
            0.40,
            0.25,
            0.62,
            0.52,
            0.42,
            0.32,
            0.28,
            0.68,
            0.58,
            0.48,
            0.38,
            0.22,
        ],
        # Stats data
        "jockey_win_pct": [
            0.15,
            0.12,
            0.18,
            0.10,
            0.14,
            0.20,
            0.16,
            0.11,
            0.13,
            0.09,
            0.17,
            0.14,
            0.19,
            0.08,
            0.12,
            0.21,
            0.15,
            0.13,
            0.11,
            0.07,
        ],
        "trainer_win_pct": [
            0.18,
            0.15,
            0.22,
            0.12,
            0.16,
            0.25,
            0.19,
            0.14,
            0.17,
            0.11,
            0.20,
            0.17,
            0.23,
            0.10,
            0.15,
            0.26,
            0.18,
            0.16,
            0.13,
            0.09,
        ],
    }

    df = pd.DataFrame(test_data)
    logger.info(
        f"✅ Created test data: {len(df)} horses in {df['race_number'].nunique()} races"
    )

    return df


def test_model_loading():
    """Test model loading functionality."""
    logger.info("🤖 Testing model loading...")

    try:
        generator = EnhancedAISelectionsGenerator()

        # Check if advanced models loaded
        if generator.advanced_models:
            logger.info(
                f"✅ Advanced models loaded: {list(generator.advanced_models.keys())}"
            )
            logger.info(
                f"✅ Features available: {len(generator.feature_columns)} columns"
            )
        else:
            logger.warning("⚠️ No advanced models loaded - will test legacy mode")

        # Check legacy models
        if generator.legacy_models:
            logger.info(
                f"✅ Legacy models loaded: {list(generator.legacy_models.keys())}"
            )
        else:
            logger.warning("⚠️ No legacy models found")

        return generator

    except Exception as e:
        logger.error(f"❌ Model loading failed: {e}")
        return None


def test_feature_engineering(generator, test_df):
    """Test feature engineering with test data."""
    logger.info("⚙️ Testing feature engineering...")

    try:
        # Test feature engineering
        features_df = generator.engineer_features(test_df.copy())

        logger.info(f"✅ Features engineered: {len(features_df.columns)} total columns")

        # Check for key advanced features
        advanced_features = [
            "power_rating",
            "speed_figure",
            "pace_rating",
            "form_score",
        ]
        for feature in advanced_features:
            if feature in features_df.columns:
                logger.info(
                    f"   ✅ {feature}: range [{features_df[feature].min():.1f}, {features_df[feature].max():.1f}]"
                )

        # Check derived features
        derived_features = ["rating_speed_ratio", "power_form_ratio", "field_strength"]
        for feature in derived_features:
            if feature in features_df.columns:
                logger.info(f"   ✅ {feature}: calculated successfully")

        return features_df

    except Exception as e:
        logger.error(f"❌ Feature engineering failed: {e}")
        return None


def test_prediction_generation(generator, features_df):
    """Test prediction generation."""
    logger.info("🎯 Testing prediction generation...")

    try:
        # Generate predictions
        predictions_df = generator.generate_predictions(features_df.copy())

        # Check for prediction columns
        prediction_cols = [
            col
            for col in predictions_df.columns
            if "probability" in col or "position" in col
        ]
        logger.info(f"✅ Predictions generated: {len(prediction_cols)} columns")

        for col in prediction_cols:
            if col in predictions_df.columns:
                values = predictions_df[col]
                if values.notna().any():
                    logger.info(
                        f"   ✅ {col}: range [{values.min():.3f}, {values.max():.3f}]"
                    )

        # Check for enhanced ensemble
        if "enhanced_win_probability" in predictions_df.columns:
            logger.info("   ✅ Enhanced ensemble predictions created")

        return predictions_df

    except Exception as e:
        logger.error(f"❌ Prediction generation failed: {e}")
        return None


def test_selections_generation(generator, predictions_df):
    """Test AI selections generation."""
    logger.info("🏆 Testing selections generation...")

    try:
        # Generate selections
        selections = generator.generate_selections(predictions_df.copy())

        total_races = sum(len(course_races) for course_races in selections.values())
        total_selections = sum(
            len(race["selections"])
            for course_races in selections.values()
            for race in course_races
        )

        logger.info(
            f"✅ Selections generated: {total_races} races, {total_selections} selections"
        )

        # Show sample selections
        for course, races in selections.items():
            logger.info(f"   📍 {course}: {len(races)} races")

            if races:
                sample_race = races[0]
                logger.info(
                    f"      Race {sample_race['race_number']}: {len(sample_race['selections'])} selections"
                )

                if sample_race["selections"]:
                    top_pick = sample_race["selections"][0]
                    logger.info(
                        f"      Top pick: {top_pick['horse_name']} ({top_pick['enhanced_win_prob']:.1%} win prob)"
                    )

        return selections

    except Exception as e:
        logger.error(f"❌ Selections generation failed: {e}")
        return None


def test_report_generation(generator, selections):
    """Test report generation."""
    logger.info("📄 Testing report generation...")

    try:
        # Generate report
        report = generator.format_selections_report(selections)

        logger.info(f"✅ Report generated: {len(report)} characters")

        # Show sample of report
        lines = report.split("\n")
        logger.info("   📋 Report preview:")
        for i, line in enumerate(lines[:10]):
            logger.info(f"      {line}")

        if len(lines) > 10:
            logger.info(f"      ... and {len(lines) - 10} more lines")

        return report

    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        return None


def run_integration_test():
    """Run complete integration test."""
    logger.info("🧪 Starting Enhanced AI Selections Integration Test")
    logger.info("=" * 60)

    # Test 1: Model loading
    generator = test_model_loading()
    if not generator:
        logger.error("❌ Test failed at model loading")
        return False

    # Test 2: Create test data
    test_df = create_test_data()

    # Test 3: Feature engineering
    features_df = test_feature_engineering(generator, test_df)
    if features_df is None:
        logger.error("❌ Test failed at feature engineering")
        return False

    # Test 4: Prediction generation
    predictions_df = test_prediction_generation(generator, features_df)
    if predictions_df is None:
        logger.error("❌ Test failed at prediction generation")
        return False

    # Test 5: Selections generation
    selections = test_selections_generation(generator, predictions_df)
    if selections is None:
        logger.error("❌ Test failed at selections generation")
        return False

    # Test 6: Report generation
    report = test_report_generation(generator, selections)
    if report is None:
        logger.error("❌ Test failed at report generation")
        return False

    # Save test report
    test_report_file = project_root / "test_enhanced_selections_report.txt"
    with open(test_report_file, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info("=" * 60)
    logger.info("✅ Integration test completed successfully!")
    logger.info(f"📄 Test report saved: {test_report_file}")

    return True


def main():
    """Main function."""
    print("🧪 Enhanced AI Selections Integration Test")
    print("==========================================")

    success = run_integration_test()

    if success:
        print("\n🎉 All tests passed! Enhanced AI selections integration is working.")
    else:
        print("\n❌ Some tests failed. Please check the logs above.")


if __name__ == "__main__":
    main()
