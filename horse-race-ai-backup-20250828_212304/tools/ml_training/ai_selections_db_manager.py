#!/usr/bin/env python3
"""
AI Selections Database Manager
==============================

Purpose: Save AI-generated horse racing predictions to the database
Author: Horse Racing AI System
Created: 2025-08-23

This script provides functionality to:
1. Save AI predictions to the ai_selections table
2. Generate race summaries with top selections
3. Track model performance
4. Validate and manage prediction data

Usage:
    python ai_selections_db_manager.py [options]
"""

import os
import sys
import json
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import pickle
import numpy as np

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)


class AISelectionsDBManager:
    """Manages AI selections in the database"""

    def __init__(self):
        """Initialize database connection"""
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "database": "cards_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Setup logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            self.logger.info("✅ Connected to database successfully")
            return True
        except Exception as e:
            self.logger.error(f"❌ Database connection failed: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.logger.info("🔌 Database connection closed")

    def get_race_details(
        self, race_date: str, course: str = None, race_number: int = None
    ) -> List[Dict]:
        """Get race and horse details for AI selection"""
        try:
            query = """
            SELECT 
                r.race_id,
                r.race_number,
                r.race_time,
                r.course,
                r.date,
                r.race_name,
                r.distance,
                r.class,
                r.runners,
                rd.detail_id,
                rd.horse_name,
                rd.jockey,
                rd.trainer,
                rd.number,
                rd.odds,
                rd.weight,
                rd.age,
                rd.form
            FROM races r
            JOIN racecard_details rd ON r.race_id = rd.race_id
            WHERE r.date = %s
            """

            params = [race_date]

            if course:
                query += " AND LOWER(r.course) = LOWER(%s)"
                params.append(course)

            if race_number:
                query += " AND r.race_number = %s"
                params.append(race_number)

            query += " ORDER BY r.race_number, rd.number"

            self.cursor.execute(query, params)
            results = self.cursor.fetchall()

            self.logger.info(
                f"📊 Retrieved {len(results)} horse entries for {race_date}"
            )
            return [dict(row) for row in results]

        except Exception as e:
            self.logger.error(f"❌ Error retrieving race details: {e}")
            return []

    def save_ai_selection(self, selection_data: Dict) -> Optional[int]:
        """Save a single AI selection to the database"""
        try:
            insert_query = """
            INSERT INTO ai_selections (
                race_id, detail_id, horse_name, win_probability, place_probability,
                confidence_score, model_name, model_version, auc_score,
                ai_selection_type, recommended_stake, expected_value,
                race_date, course, race_number, features_used, prediction_factors
            ) VALUES (
                %(race_id)s, %(detail_id)s, %(horse_name)s, %(win_probability)s, %(place_probability)s,
                %(confidence_score)s, %(model_name)s, %(model_version)s, %(auc_score)s,
                %(ai_selection_type)s, %(recommended_stake)s, %(expected_value)s,
                %(race_date)s, %(course)s, %(race_number)s, %(features_used)s, %(prediction_factors)s
            ) RETURNING selection_id
            """

            self.cursor.execute(insert_query, selection_data)
            selection_id = self.cursor.fetchone()["selection_id"]
            self.conn.commit()

            self.logger.info(
                f"✅ Saved AI selection for {selection_data['horse_name']} (ID: {selection_id})"
            )
            return selection_id

        except Exception as e:
            self.logger.error(f"❌ Error saving AI selection: {e}")
            self.conn.rollback()
            return None

    def save_race_summary(self, race_id: int, summary_data: Dict) -> Optional[int]:
        """Save race summary with top AI selections"""
        try:
            insert_query = """
            INSERT INTO ai_race_summary (
                race_id, top_win_selection, top_win_probability,
                top_place_selection, top_place_probability,
                race_competitiveness, prediction_certainty, total_horses_analyzed,
                avg_model_auc, model_consensus, betting_strategy, risk_assessment,
                race_date, course, race_number
            ) VALUES (
                %(race_id)s, %(top_win_selection)s, %(top_win_probability)s,
                %(top_place_selection)s, %(top_place_probability)s,
                %(race_competitiveness)s, %(prediction_certainty)s, %(total_horses_analyzed)s,
                %(avg_model_auc)s, %(model_consensus)s, %(betting_strategy)s, %(risk_assessment)s,
                %(race_date)s, %(course)s, %(race_number)s
            ) RETURNING summary_id
            """

            self.cursor.execute(insert_query, summary_data)
            summary_id = self.cursor.fetchone()["summary_id"]
            self.conn.commit()

            self.logger.info(
                f"✅ Saved race summary for Race {summary_data['race_number']} (ID: {summary_id})"
            )
            return summary_id

        except Exception as e:
            self.logger.error(f"❌ Error saving race summary: {e}")
            self.conn.rollback()
            return None

    def update_model_performance(self, model_data: Dict) -> bool:
        """Update or insert model performance data"""
        try:
            upsert_query = """
            INSERT INTO ai_model_performance (
                model_name, model_version, training_date, training_sessions,
                best_auc, avg_auc, accuracy, training_records, validation_records,
                is_active, deployment_date, performance_notes
            ) VALUES (
                %(model_name)s, %(model_version)s, %(training_date)s, %(training_sessions)s,
                %(best_auc)s, %(avg_auc)s, %(accuracy)s, %(training_records)s, %(validation_records)s,
                %(is_active)s, %(deployment_date)s, %(performance_notes)s
            )
            ON CONFLICT (model_name, model_version) DO UPDATE SET
                training_sessions = EXCLUDED.training_sessions,
                best_auc = EXCLUDED.best_auc,
                avg_auc = EXCLUDED.avg_auc,
                accuracy = EXCLUDED.accuracy,
                training_records = EXCLUDED.training_records,
                validation_records = EXCLUDED.validation_records,
                is_active = EXCLUDED.is_active,
                performance_notes = EXCLUDED.performance_notes
            """

            self.cursor.execute(upsert_query, model_data)
            self.conn.commit()

            self.logger.info(
                f"✅ Updated model performance for {model_data['model_name']} v{model_data['model_version']}"
            )
            return True

        except Exception as e:
            self.logger.error(f"❌ Error updating model performance: {e}")
            self.conn.rollback()
            return False

    def generate_ai_selections_from_model(
        self, race_date: str, model_path: str, model_name: str, model_version: str
    ) -> List[Dict]:
        """Generate AI selections using trained model"""
        try:
            # Load the trained model
            with open(model_path, "rb") as f:
                model_data = pickle.load(f)
                model = model_data["model"]
                feature_columns = model_data["feature_columns"]
                scaler = model_data.get("scaler")

            # Get race data for the specified date
            race_details = self.get_race_details(race_date)
            if not race_details:
                self.logger.warning(f"⚠️ No race data found for {race_date}")
                return []

            selections = []

            # Group by race
            races = {}
            for detail in race_details:
                race_id = detail["race_id"]
                if race_id not in races:
                    races[race_id] = []
                races[race_id].append(detail)

            for race_id, horses in races.items():
                race_info = horses[0]  # Get race info from first horse

                self.logger.info(
                    f"🏇 Generating predictions for Race {race_info['race_number']} at {race_info['course']}"
                )

                for horse in horses:
                    try:
                        # Prepare features for prediction
                        features = self._prepare_features(horse, feature_columns)
                        if features is None:
                            continue

                        # Scale features if scaler is available
                        if scaler:
                            features_scaled = scaler.transform([features])
                        else:
                            features_scaled = [features]

                        # Get prediction
                        if hasattr(model, "predict_proba"):
                            # For classification models
                            proba = model.predict_proba(features_scaled)[0]
                            win_probability = (
                                float(proba[1]) if len(proba) > 1 else float(proba[0])
                            )
                        else:
                            # For regression models
                            prediction = model.predict(features_scaled)[0]
                            win_probability = float(min(max(prediction, 0), 1))

                        # Calculate additional metrics
                        place_probability = min(
                            win_probability * 3, 1.0
                        )  # Rough estimation
                        confidence_score = win_probability

                        # Determine selection type
                        if win_probability > 0.3:
                            selection_type = "win"
                            recommended_stake = 5.0
                        elif win_probability > 0.2:
                            selection_type = "each_way"
                            recommended_stake = 3.0
                        elif win_probability > 0.1:
                            selection_type = "place"
                            recommended_stake = 2.0
                        else:
                            selection_type = "watch"
                            recommended_stake = 0.0

                        # Calculate expected value (basic calculation)
                        odds = float(horse["odds"]) if horse["odds"] else 3.0
                        expected_value = (win_probability * odds) - 1.0

                        selection = {
                            "race_id": race_id,
                            "detail_id": horse["detail_id"],
                            "horse_name": horse["horse_name"],
                            "win_probability": Decimal(str(round(win_probability, 4))),
                            "place_probability": Decimal(
                                str(round(place_probability, 4))
                            ),
                            "confidence_score": Decimal(
                                str(round(confidence_score, 4))
                            ),
                            "model_name": model_name,
                            "model_version": model_version,
                            "auc_score": Decimal("0.8664"),  # From our training
                            "ai_selection_type": selection_type,
                            "recommended_stake": Decimal(str(recommended_stake)),
                            "expected_value": Decimal(str(round(expected_value, 4))),
                            "race_date": race_date,
                            "course": horse["course"],
                            "race_number": horse["race_number"],
                            "features_used": json.dumps(feature_columns),
                            "prediction_factors": json.dumps(
                                {
                                    "form": horse["form"],
                                    "odds": horse["odds"],
                                    "weight": horse["weight"],
                                    "jockey": horse["jockey"],
                                    "trainer": horse["trainer"],
                                }
                            ),
                        }

                        selections.append(selection)

                    except Exception as e:
                        self.logger.error(
                            f"❌ Error generating prediction for {horse['horse_name']}: {e}"
                        )
                        continue

            self.logger.info(
                f"🎯 Generated {len(selections)} AI selections for {race_date}"
            )
            return selections

        except Exception as e:
            self.logger.error(f"❌ Error generating AI selections: {e}")
            return []

    def _prepare_features(
        self, horse_data: Dict, feature_columns: List[str]
    ) -> Optional[List[float]]:
        """Prepare feature vector for model prediction"""
        try:
            features = []

            # Basic feature mapping (adjust based on your model's features)
            feature_map = {
                "odds": float(horse_data["odds"]) if horse_data["odds"] else 5.0,
                "age": float(horse_data["age"]) if horse_data["age"] else 5.0,
                "number": float(horse_data["number"]) if horse_data["number"] else 1.0,
                "weight_cleaned": self._parse_weight(horse_data["weight"]),
                "form_score": self._calculate_form_score(horse_data["form"]),
                "runners": float(horse_data.get("runners", 10)),
            }

            # Build feature vector based on model's expected features
            for feature in feature_columns:
                if feature in feature_map:
                    features.append(feature_map[feature])
                else:
                    # Default value for missing features
                    features.append(0.0)

            return features

        except Exception as e:
            self.logger.error(f"❌ Error preparing features: {e}")
            return None

    def _parse_weight(self, weight_str: str) -> float:
        """Parse weight string to numeric value"""
        if not weight_str:
            return 9.0  # Default weight

        try:
            # Handle formats like "9-7", "9.7", "9st 7lb"
            weight_str = str(weight_str).replace("-", ".")
            if "st" in weight_str:
                # Handle "9st 7lb" format
                parts = weight_str.split("st")
                stones = float(parts[0])
                pounds = 0
                if len(parts) > 1 and "lb" in parts[1]:
                    pounds = float(parts[1].replace("lb", "").strip())
                return stones + (pounds / 14)
            else:
                return float(weight_str)
        except:
            return 9.0

    def _calculate_form_score(self, form_str: str) -> float:
        """Calculate form score from form string"""
        if not form_str:
            return 0.5

        try:
            score = 0.0
            count = 0

            for char in str(form_str)[:6]:  # Last 6 runs
                if char.isdigit():
                    position = int(char)
                    if position == 1:
                        score += 1.0
                    elif position == 2:
                        score += 0.8
                    elif position == 3:
                        score += 0.6
                    elif position <= 5:
                        score += 0.4
                    else:
                        score += 0.1
                    count += 1

            return score / count if count > 0 else 0.5

        except:
            return 0.5

    def process_and_save_selections(
        self,
        race_date: str,
        model_path: str,
        model_name: str = "GradientBoosting",
        model_version: str = "v2025.08.23",
    ) -> bool:
        """Complete process to generate and save AI selections"""
        try:
            if not self.connect():
                return False

            # Generate AI selections
            selections = self.generate_ai_selections_from_model(
                race_date, model_path, model_name, model_version
            )

            if not selections:
                self.logger.warning(f"⚠️ No selections generated for {race_date}")
                return False

            # Save selections to database
            saved_count = 0
            for selection in selections:
                if self.save_ai_selection(selection):
                    saved_count += 1

            # Generate and save race summaries
            races = {}
            for selection in selections:
                race_id = selection["race_id"]
                if race_id not in races:
                    races[race_id] = []
                races[race_id].append(selection)

            for race_id, race_selections in races.items():
                summary = self._generate_race_summary(race_id, race_selections)
                self.save_race_summary(race_id, summary)

            self.logger.info(
                f"🎉 Successfully saved {saved_count} AI selections and {len(races)} race summaries"
            )
            return True

        except Exception as e:
            self.logger.error(f"❌ Error processing AI selections: {e}")
            return False
        finally:
            self.disconnect()

    def _generate_race_summary(self, race_id: int, selections: List[Dict]) -> Dict:
        """Generate race summary from selections"""
        # Sort by win probability
        sorted_selections = sorted(
            selections, key=lambda x: x["win_probability"], reverse=True
        )

        top_win = sorted_selections[0]

        # Find top place selection (could be different from win)
        place_sorted = sorted(
            selections, key=lambda x: x["place_probability"], reverse=True
        )
        top_place = place_sorted[0]

        # Calculate competitiveness (how close are the top selections)
        probabilities = [float(s["win_probability"]) for s in selections]
        competitiveness = 1.0 - (max(probabilities) - np.mean(probabilities))

        # Calculate prediction certainty
        certainty = max(probabilities)

        # Determine risk assessment
        if certainty > 0.4:
            risk = "low"
        elif certainty > 0.25:
            risk = "medium"
        else:
            risk = "high"

        # Generate betting strategy
        if max(probabilities) > 0.3:
            strategy = f"Strong win selection on {top_win['horse_name']}"
        elif len([p for p in probabilities if p > 0.2]) > 1:
            strategy = "Multiple strong contenders - consider each-way betting"
        else:
            strategy = "Competitive race - small stakes or avoid"

        return {
            "race_id": race_id,
            "top_win_selection": top_win["horse_name"],
            "top_win_probability": top_win["win_probability"],
            "top_place_selection": top_place["horse_name"],
            "top_place_probability": top_place["place_probability"],
            "race_competitiveness": Decimal(str(round(competitiveness, 4))),
            "prediction_certainty": Decimal(str(round(certainty, 4))),
            "total_horses_analyzed": len(selections),
            "avg_model_auc": Decimal("0.8664"),
            "model_consensus": "High" if certainty > 0.3 else "Medium",
            "betting_strategy": strategy,
            "risk_assessment": risk,
            "race_date": top_win["race_date"],
            "course": top_win["course"],
            "race_number": top_win["race_number"],
        }


def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Selections Database Manager")
    parser.add_argument("--date", required=True, help="Race date (YYYY-MM-DD)")
    parser.add_argument(
        "--model-path", required=True, help="Path to trained model file"
    )
    parser.add_argument("--model-name", default="GradientBoosting", help="Model name")
    parser.add_argument("--model-version", default="v2025.08.23", help="Model version")

    args = parser.parse_args()

    manager = AISelectionsDBManager()
    success = manager.process_and_save_selections(
        args.date, args.model_path, args.model_name, args.model_version
    )

    if success:
        print(f"✅ AI selections saved successfully for {args.date}")
    else:
        print(f"❌ Failed to process AI selections for {args.date}")
        sys.exit(1)


if __name__ == "__main__":
    main()
