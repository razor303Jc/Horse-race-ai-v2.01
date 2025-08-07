#!/usr/bin/env python3
"""
Production Cyclic ML Training System
Full-scale training with 100 cycles, performance reviews every 10 cycles,
comprehensive monitoring, and integration with race trends analysis.
"""

import os
import sys
import logging
from datetime import datetime

# Add project path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.0")

from simplified_cyclic_training import SimplifiedCyclicTraining

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f"production_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def run_production_training():
    """Run full production training with 100 cycles"""
    logger.info("🚀 PRODUCTION CYCLIC ML TRAINING SYSTEM")
    logger.info("=" * 60)
    logger.info(f"⏰ Training started: {datetime.now()}")

    # Configuration
    CONFIG = {
        "total_cycles": 1000,
        "evaluation_interval": 10,
        "num_horses": 15000,
        "training_days": 1095,  # 3 years
        "start_date": "2022-01-01",
        "db_path": "production_training.db",
    }

    logger.info("🔧 CONFIGURATION:")
    for key, value in CONFIG.items():
        logger.info(f"   {key}: {value}")

    # Initialize training system
    trainer = SimplifiedCyclicTraining(db_path=CONFIG["db_path"])

    # Generate training data if needed
    if not os.path.exists(CONFIG["db_path"]):
        logger.info("📊 Generating production training dataset...")
        logger.info(f"   🐎 Horses: {CONFIG['num_horses']:,}")
        logger.info(f"   📅 Training Period: {CONFIG['training_days']} days")
        logger.info(f"   📍 Start Date: {CONFIG['start_date']}")

        trainer.generate_training_data(
            num_horses=CONFIG["num_horses"],
            num_days=CONFIG["training_days"],
            start_date=CONFIG["start_date"],
        )
        logger.info("✅ Production dataset generated")
    else:
        logger.info(f"📊 Using existing dataset: {CONFIG['db_path']}")

    # Run production training cycles
    logger.info("\n🎯 STARTING PRODUCTION TRAINING CYCLES")
    logger.info("=" * 60)

    start_time = datetime.now()

    try:
        trainer.run_training_cycles(
            total_cycles=CONFIG["total_cycles"],
            evaluation_interval=CONFIG["evaluation_interval"],
        )

        end_time = datetime.now()
        total_duration = end_time - start_time

        logger.info(f"\n🎉 PRODUCTION TRAINING COMPLETED SUCCESSFULLY!")
        logger.info(f"⏱️ Total Duration: {total_duration}")
        logger.info(f"🔄 Cycles Completed: {CONFIG['total_cycles']}")
        logger.info(
            f"📊 Evaluations Performed: {CONFIG['total_cycles'] // CONFIG['evaluation_interval']}"
        )

        # Final summary
        logger.info(f"\n📋 FINAL SUMMARY:")
        logger.info(f"   🏁 Training Completed: {end_time}")
        logger.info(f"   💾 Results: cyclic_training_results.json")
        logger.info(
            f"   📝 Log: production_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

    except KeyboardInterrupt:
        logger.info("\n⚠️ Training interrupted by user")
        logger.info(
            "💾 Partial results may be available in cyclic_training_results.json"
        )

    except Exception as e:
        logger.error(f"\n❌ Training failed with error: {e}")
        logger.error("🔧 Check logs for detailed error information")
        raise


def run_extended_analysis():
    """Run extended analysis after training completion"""
    logger.info("\n🔬 EXTENDED POST-TRAINING ANALYSIS")
    logger.info("=" * 50)

    try:
        import json
        import numpy as np
        import matplotlib.pyplot as plt

        # Load results
        with open("cyclic_training_results.json", "r") as f:
            results = json.load(f)

        cycles = results["cycles"]
        aucs = [c["auc"] for c in cycles]
        accuracies = [c["accuracy"] for c in cycles]

        # Performance analysis
        logger.info("📊 EXTENDED PERFORMANCE ANALYSIS:")
        logger.info(f"   🎯 AUC Range: {min(aucs):.4f} - {max(aucs):.4f}")
        logger.info(
            f"   📊 Accuracy Range: {min(accuracies):.4f} - {max(accuracies):.4f}"
        )

        # Learning phases
        if len(aucs) >= 30:
            early_phase = np.mean(aucs[:30])
            mid_phase = np.mean(aucs[30:70]) if len(aucs) >= 70 else np.mean(aucs[30:])
            late_phase = np.mean(aucs[-30:]) if len(aucs) >= 30 else np.mean(aucs)

            logger.info(f"\n📈 LEARNING PHASES:")
            logger.info(f"   🌅 Early Phase (1-30): {early_phase:.4f}")
            logger.info(f"   ☀️ Mid Phase (31-70): {mid_phase:.4f}")
            logger.info(f"   🌇 Late Phase (71-100): {late_phase:.4f}")

        # Feature consistency analysis
        all_features = {}
        for cycle in cycles:
            for feature, importance in cycle.get("top_features", []):
                if feature not in all_features:
                    all_features[feature] = []
                all_features[feature].append(importance)

        logger.info(f"\n🔍 FEATURE CONSISTENCY ANALYSIS:")
        consistent_features = []
        for feature, importances in all_features.items():
            if len(importances) >= 10:  # Feature appeared in 10+ cycles
                std_dev = np.std(importances)
                mean_importance = np.mean(importances)
                consistency = (
                    1 - (std_dev / mean_importance) if mean_importance > 0 else 0
                )
                consistent_features.append((feature, mean_importance, consistency))

        # Sort by consistency
        consistent_features.sort(key=lambda x: x[2], reverse=True)

        logger.info(f"   🔝 Most Consistent Features:")
        for i, (feature, importance, consistency) in enumerate(
            consistent_features[:5], 1
        ):
            logger.info(
                f"      {i}. {feature}: {importance:.4f} "
                f"(consistency: {consistency:.3f})"
            )

        logger.info("✅ Extended analysis complete")

    except Exception as e:
        logger.warning(f"⚠️ Extended analysis failed: {e}")


def main():
    """Main production training function"""
    try:
        # Run production training
        run_production_training()

        # Run extended analysis
        run_extended_analysis()

    except Exception as e:
        logger.error(f"Production training system failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
