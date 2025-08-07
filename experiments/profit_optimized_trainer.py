#!/usr/bin/env python3
"""
Profit-Optimized ML Trainer - Horse Racing AI v2.0
Specialized ML training focused on reward algorithm optimization and money-making
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import joblib
import os
from typing import Dict, List, Tuple, Optional

# ML imports
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.linear_model import LogisticRegression

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProfitOptimizedMLTrainer:
    """
    ML Trainer optimized for profit generation and reward algorithm integration.

    Features:
    - Profit-weighted training samples
    - Kelly Criterion integration
    - Value betting optimization
    - Risk-adjusted performance metrics
    - Real-time reward feedback
    """

    def __init__(self, db_path: str = "ai_strategies_corrected.db"):
        self.db_path = db_path
        self.models = {}
        self.scalers = {}
        self.performance = {}
        self.profit_metrics = {}

        # Profit optimization parameters
        self.profit_weights = {
            "win_reward": 10,  # High reward for wins
            "place_reward": 3,  # Moderate reward for places
            "value_bonus": 2,  # Bonus for value selections
            "loss_penalty": -5,  # Penalty for losses
            "confidence_factor": 1.5,  # Confidence multiplier
        }

        # Ensure models directory exists
        os.makedirs("models/profit_optimized", exist_ok=True)

    def load_training_data(self) -> pd.DataFrame:
        """Load training data with profit optimization focus"""

        logger.info("📊 Loading profit-optimized training data...")

        conn = sqlite3.connect(self.db_path)

        # Load comprehensive data with profit calculations
        query = """
        SELECT 
            rp.participant_id,
            rp.race_id,
            rp.odds_decimal,
            rp.actual_finish_position,
            rp.draw,
            rp.weight_lbs as weight,
            h.age,
            h.rating,
            h.form_rating,
            h.career_wins,
            h.career_runs,
            j.skill_rating as jockey_skill,
            j.win_percentage as jockey_win_pct,
            t.skill_rating as trainer_skill,
            t.win_percentage as trainer_win_pct,
            rc.distance_meters as distance,
            rc.prize_money as prize,
            rc.num_runners as field_size,
            rc.race_type,
            rc.track_condition,
            v.track_type,
            
            -- Calculate profit metrics
            CASE 
                WHEN rp.actual_finish_position = 1 THEN (rp.odds_decimal - 1) * 10  -- Simulated £10 win bet
                ELSE -10  -- Loss
            END as win_profit,
            
            CASE 
                WHEN rp.actual_finish_position <= 3 THEN (rp.odds_decimal * 0.25 - 1) * 10  -- Simulated place bet
                ELSE -10
            END as place_profit,
            
            -- Value calculation
            (1.0 / rp.odds_decimal) as implied_prob,
            
            -- Create target variables
            CASE WHEN rp.actual_finish_position = 1 THEN 1 ELSE 0 END as won_race,
            CASE WHEN rp.actual_finish_position <= 3 THEN 1 ELSE 0 END as placed_race
            
        FROM race_participants rp
        JOIN horses h ON rp.horse_id = h.horse_id
        JOIN jockeys j ON rp.jockey_id = j.jockey_id
        JOIN trainers t ON rp.trainer_id = t.trainer_id
        JOIN race_cards rc ON rp.race_id = rc.race_id
        JOIN venues v ON rc.venue_id = v.venue_id
        WHERE rp.odds_decimal > 0 
        AND rp.actual_finish_position IS NOT NULL
        LIMIT 50000
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        logger.info(f"📈 Loaded {len(df):,} training records with profit data")
        return df

    def engineer_profit_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features specifically for profit optimization"""

        logger.info("🔧 Engineering profit-optimized features...")

        # Fill missing values
        df = df.fillna(
            {
                "age": 4,
                "weight": 60,
                "draw": 1,
                "rating": 75,
                "form_rating": 75,
                "career_wins": 1,
                "career_runs": 5,
                "jockey_skill": 75,
                "jockey_win_pct": 15,
                "trainer_skill": 75,
                "trainer_win_pct": 15,
                "distance": 1600,
                "prize": 10000,
                "field_size": 10,
            }
        )

        # Convert to numeric
        numeric_cols = [
            "odds_decimal",
            "age",
            "weight",
            "draw",
            "rating",
            "form_rating",
            "distance",
            "prize",
            "field_size",
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # PROFIT-FOCUSED FEATURES

        # 1. Value identification
        df["implied_prob"] = 1 / df["odds_decimal"]
        df["true_prob"] = df.groupby("race_id")["won_race"].transform("mean")
        df["value_edge"] = df["true_prob"] - df["implied_prob"]
        df["is_value_bet"] = (df["value_edge"] > 0.05).astype(int)

        # 2. Kelly Criterion calculation
        df["kelly_fraction"] = np.maximum(
            0, (df["true_prob"] * df["odds_decimal"] - 1) / (df["odds_decimal"] - 1)
        )
        df["optimal_kelly"] = (df["kelly_fraction"].between(0.02, 0.1)).astype(int)

        # 3. Profit potential scores
        df["win_profit_potential"] = df["odds_decimal"] * df["true_prob"]
        df["place_profit_potential"] = (df["odds_decimal"] * 0.25) * (
            df.groupby("race_id")["placed_race"].transform("mean")
        )

        # 4. Risk assessment
        df["odds_rank"] = df.groupby("race_id")["odds_decimal"].rank()
        df["is_favorite"] = (df["odds_rank"] == 1).astype(int)
        df["is_longshot"] = (df["odds_decimal"] > 10).astype(int)
        df["risk_category"] = pd.cut(
            df["odds_decimal"],
            bins=[0, 3, 6, 10, 50, 1000],
            labels=["low", "medium", "high", "very_high", "extreme"],
        )

        # 5. Performance indicators
        df["win_rate"] = df["career_wins"] / np.maximum(df["career_runs"], 1)
        df["class_rating"] = df["rating"] / 100
        df["form_momentum"] = df["form_rating"] / df["rating"]

        # 6. Market efficiency indicators
        df["odds_log"] = np.log(df["odds_decimal"])
        df["market_strength"] = 1 / df["odds_decimal"]
        df["field_competitiveness"] = df.groupby("race_id")["odds_decimal"].transform(
            "std"
        )

        # 7. Distance and track suitability
        df["distance_category"] = pd.cut(
            df["distance"],
            bins=[0, 1400, 1800, 2400, 3200, 10000],
            labels=["sprint", "mile", "middle", "staying", "extreme"],
        )
        df["track_suitability"] = df.groupby(["track_type", "distance_category"])[
            "won_race"
        ].transform("mean")

        # 8. Jockey/Trainer factors
        df["jockey_value"] = df["jockey_skill"] / 100
        df["trainer_value"] = df["trainer_skill"] / 100
        df["team_strength"] = (df["jockey_value"] + df["trainer_value"]) / 2

        # 9. Economic factors
        df["prize_per_runner"] = df["prize"] / df["field_size"]
        df["high_value_race"] = (df["prize"] > df["prize"].quantile(0.75)).astype(int)

        # 10. Interaction features
        df["odds_rating_interaction"] = df["odds_log"] * df["class_rating"]
        df["age_distance_interaction"] = df["age"] * np.log1p(df["distance"])
        df["value_confidence"] = df["value_edge"] * df["form_momentum"]

        # Encode categoricals
        categorical_cols = [
            "race_type",
            "track_condition",
            "track_type",
            "distance_category",
            "risk_category",
        ]

        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].fillna("Unknown")
                le = LabelEncoder()
                df[f"{col}_encoded"] = le.fit_transform(df[col])
                self.scalers[f"{col}_encoder"] = le

        logger.info(f"✅ Feature engineering complete: {df.shape[1]} features")
        return df

    def create_profit_weighted_targets(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create targets weighted by profit potential"""

        logger.info("🎯 Creating profit-weighted targets...")

        # Primary target: Win probability adjusted for value
        df["profit_target"] = df["won_race"] * (1 + df["value_edge"])

        # Secondary targets for multi-objective training
        df["value_target"] = df["is_value_bet"]
        df["kelly_target"] = df["optimal_kelly"]
        df["place_target"] = df["placed_race"]

        # Create sample weights based on profit potential
        df["sample_weight"] = 1.0

        # Increase weight for profitable outcomes
        df.loc[df["won_race"] == 1, "sample_weight"] *= 3.0  # Winners get 3x weight
        df.loc[
            df["is_value_bet"] == 1, "sample_weight"
        ] *= 2.0  # Value bets get 2x weight
        df.loc[
            df["optimal_kelly"] == 1, "sample_weight"
        ] *= 1.5  # Good Kelly sizing gets 1.5x weight

        # Decrease weight for poor value
        df.loc[
            df["value_edge"] < -0.1, "sample_weight"
        ] *= 0.5  # Poor value gets 0.5x weight

        logger.info("✅ Profit-weighted targets created")
        return df

    def prepare_training_data(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, List[str], np.ndarray]:
        """Prepare features and targets for training"""

        logger.info("🎯 Preparing profit-optimized training data...")

        # Select features for training
        feature_columns = [
            # Core odds and value features
            "odds_log",
            "implied_prob",
            "value_edge",
            "kelly_fraction",
            "win_profit_potential",
            "place_profit_potential",
            # Horse characteristics
            "age",
            "rating",
            "form_rating",
            "class_rating",
            "form_momentum",
            "win_rate",
            "career_wins",
            "career_runs",
            # Race features
            "draw",
            "weight",
            "field_size",
            "field_competitiveness",
            "prize_per_runner",
            "high_value_race",
            # Market features
            "odds_rank",
            "is_favorite",
            "is_longshot",
            "market_strength",
            # Team features
            "jockey_skill",
            "trainer_skill",
            "team_strength",
            # Suitability features
            "track_suitability",
            # Interaction features
            "odds_rating_interaction",
            "age_distance_interaction",
            "value_confidence",
            # Encoded categoricals
            "race_type_encoded",
            "track_condition_encoded",
            "track_type_encoded",
            "distance_category_encoded",
            "risk_category_encoded",
        ]

        # Keep only features that exist
        available_features = [col for col in feature_columns if col in df.columns]

        X = df[available_features].fillna(0).values
        y = df["profit_target"].values
        weights = df["sample_weight"].values

        logger.info(
            f"📊 Training data prepared: {X.shape[0]:,} samples, {X.shape[1]} features"
        )
        return X, y, available_features, weights

    def train_profit_models(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: List[str],
        sample_weights: np.ndarray,
    ) -> None:
        """Train models optimized for profit generation"""

        logger.info("🤖 Training profit-optimized ML models...")

        # Split data
        X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
            X,
            y,
            sample_weights,
            test_size=0.2,
            random_state=42,
            stratify=(y > 0.5).astype(int),
        )

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers["feature_scaler"] = scaler

        # Define profit-optimized models
        models = {
            "profit_random_forest": RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
            "profit_gradient_boost": GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=6,
                min_samples_split=5,
                random_state=42,
            ),
            "profit_neural_network": MLPClassifier(
                hidden_layer_sizes=(100, 50),
                activation="relu",
                alpha=0.01,
                learning_rate="adaptive",
                max_iter=1000,
                random_state=42,
            ),
            "profit_logistic": LogisticRegression(
                C=1.0, class_weight="balanced", max_iter=2000, random_state=42
            ),
        }

        # Train each model
        for model_name, model in models.items():
            logger.info(f"🔧 Training {model_name}...")

            try:
                # Convert continuous target to binary for classification
                y_binary = (y > 0.5).astype(int)
                y_train_binary = (y_train > 0.5).astype(int)
                y_test_binary = (y_test > 0.5).astype(int)

                # Use scaled data for neural network and logistic
                if model_name in ["profit_neural_network", "profit_logistic"]:
                    model.fit(X_train_scaled, y_train_binary, sample_weight=w_train)
                    y_pred = model.predict(X_test_scaled)
                    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
                else:
                    model.fit(X_train, y_train_binary, sample_weight=w_train)
                    y_pred = model.predict(X_test)
                    y_pred_proba = model.predict_proba(X_test)[:, 1]

                # Calculate standard metrics
                metrics = {
                    "accuracy": accuracy_score(y_test_binary, y_pred),
                    "precision": precision_score(
                        y_test_binary, y_pred, zero_division=0
                    ),
                    "recall": recall_score(y_test_binary, y_pred, zero_division=0),
                    "f1": f1_score(y_test_binary, y_pred, zero_division=0),
                    "auc": roc_auc_score(y_test_binary, y_pred_proba),
                }

                # Calculate profit-specific metrics
                profit_metrics = self._calculate_profit_metrics(
                    y_test_binary, y_pred, y_pred_proba, X_test, feature_names
                )

                # Store results
                self.models[model_name] = model
                self.performance[model_name] = metrics
                self.profit_metrics[model_name] = profit_metrics

                logger.info(
                    f"✅ {model_name}: AUC={metrics['auc']:.4f}, "
                    f"Profit Score={profit_metrics['profit_score']:.2f}"
                )

            except Exception as e:
                logger.error(f"❌ Failed to train {model_name}: {e}")

    def _calculate_profit_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: np.ndarray,
        X_test: np.ndarray,
        feature_names: List[str],
    ) -> Dict:
        """Calculate profit-specific performance metrics"""

        # Simulate betting performance
        total_bets = len(y_true)
        winners = np.sum((y_true == 1) & (y_pred == 1))
        false_positives = np.sum((y_true == 0) & (y_pred == 1))

        # Simplified profit calculation (assuming average odds of 5.0)
        avg_odds = 5.0
        stake_per_bet = 10.0

        gross_profit = winners * stake_per_bet * (avg_odds - 1)
        gross_loss = false_positives * stake_per_bet
        net_profit = gross_profit - gross_loss

        roi = (net_profit / (total_bets * stake_per_bet)) * 100 if total_bets > 0 else 0

        # Value betting metrics
        high_confidence = np.sum(y_proba > 0.7)
        value_opportunities = np.sum((y_proba > 0.3) & (y_true == 1))

        # Kelly criterion simulation
        kelly_optimal = np.sum((y_proba > 0.25) & (y_proba < 0.75))

        profit_score = (
            (roi / 10)
            + (winners / total_bets * 50)
            + (value_opportunities / total_bets * 25)
        )

        return {
            "net_profit": net_profit,
            "roi": roi,
            "winners": winners,
            "total_bets": total_bets,
            "win_rate": winners / total_bets * 100,
            "high_confidence_bets": high_confidence,
            "value_opportunities": value_opportunities,
            "kelly_optimal_bets": kelly_optimal,
            "profit_score": profit_score,
        }

    def save_models(self):
        """Save trained models and metadata"""

        logger.info("💾 Saving profit-optimized models...")

        try:
            # Save models
            for model_name, model in self.models.items():
                model_path = f"models/profit_optimized/{model_name}.joblib"
                joblib.dump(model, model_path)

            # Save scalers
            scalers_path = f"models/profit_optimized/scalers.joblib"
            joblib.dump(self.scalers, scalers_path)

            # Save performance metrics
            performance_path = f"models/profit_optimized/performance.joblib"
            joblib.dump(
                {
                    "standard_metrics": self.performance,
                    "profit_metrics": self.profit_metrics,
                },
                performance_path,
            )

            # Save training summary
            self._save_training_summary()

            logger.info("✅ Profit-optimized models saved successfully")

        except Exception as e:
            logger.error(f"❌ Failed to save models: {e}")

    def _save_training_summary(self):
        """Save comprehensive training summary"""

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        summary = f"""
🎯 PROFIT-OPTIMIZED ML TRAINING SUMMARY
==========================================
Timestamp: {timestamp}

📊 STANDARD PERFORMANCE:
------------------------
"""

        for model_name, metrics in self.performance.items():
            summary += f"""
🤖 {model_name.upper()}:
   Accuracy:  {metrics['accuracy']:.4f}
   Precision: {metrics['precision']:.4f}
   Recall:    {metrics['recall']:.4f}
   F1 Score:  {metrics['f1']:.4f}
   AUC:       {metrics['auc']:.4f}
"""

        summary += f"""

💰 PROFIT PERFORMANCE:
---------------------
"""

        for model_name, metrics in self.profit_metrics.items():
            summary += f"""
💸 {model_name.upper()}:
   Net Profit:    £{metrics['net_profit']:.2f}
   ROI:           {metrics['roi']:.2f}%
   Win Rate:      {metrics['win_rate']:.1f}%
   Winners:       {metrics['winners']}/{metrics['total_bets']}
   Value Bets:    {metrics['value_opportunities']}
   Profit Score:  {metrics['profit_score']:.2f}
"""

        # Find best model
        best_model = max(
            self.profit_metrics.keys(),
            key=lambda x: self.profit_metrics[x]["profit_score"],
        )

        summary += f"""

🏆 BEST MODEL: {best_model.upper()}
Profit Score: {self.profit_metrics[best_model]['profit_score']:.2f}

💡 RECOMMENDATIONS:
- Focus on {best_model} for live betting
- Target value opportunities: {self.profit_metrics[best_model]['value_opportunities']} identified
- Optimize stake sizing using Kelly Criterion
- Monitor ROI target of 15%+ achieved: {self.profit_metrics[best_model]['roi'] > 15}

==========================================
"""

        with open(f"models/profit_optimized/training_summary.txt", "w") as f:
            f.write(summary)

        print(summary)


def main():
    """Run profit-optimized ML training"""

    print("🎯 PROFIT-OPTIMIZED ML TRAINER")
    print("=" * 50)

    trainer = ProfitOptimizedMLTrainer()

    # Load and prepare data
    df = trainer.load_training_data()
    df = trainer.engineer_profit_features(df)
    df = trainer.create_profit_weighted_targets(df)

    # Prepare training data
    X, y, feature_names, weights = trainer.prepare_training_data(df)

    # Train models
    trainer.train_profit_models(X, y, feature_names, weights)

    # Save results
    trainer.save_models()

    print("\n✅ Profit-optimized training complete!")
    print("💾 Models saved to: models/profit_optimized/")
    print("🎯 Ready for reward algorithm analysis!")


if __name__ == "__main__":
    main()
