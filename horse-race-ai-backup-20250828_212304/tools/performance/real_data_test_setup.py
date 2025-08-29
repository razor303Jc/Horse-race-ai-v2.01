#!/usr/bin/env python3
"""
Real Data Test Setup for Race Results Integration

Creates realistic AI predictions using actual race data from the database
for comprehensive performance tracking testing.
"""

import logging
import sys
import os
import subprocess
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple

# Add project root to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.04")


class RealDataTestGenerator:
    """Generate realistic test data using actual race results"""

    def __init__(self):
        self.container_name = "horse_racing_postgres_clean"
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

    def setup_logging(self):
        """Configure logging"""
        log_dir = "/home/jc/Documents/Horse-race-ai-v2.04/logs"
        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )

    def execute_query(self, database: str, query: str) -> List[List[str]]:
        """Execute SQL query and return results"""
        try:
            cmd = [
                "docker",
                "exec",
                self.container_name,
                "psql",
                "-U",
                "horse_racing",
                "-d",
                database,
                "-t",
                "-A",
                "-F",
                "|",
                "-c",
                query,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                self.logger.error(f"Query failed: {result.stderr}")
                return []

            # Parse the results
            lines = result.stdout.strip().split("\n")
            if not lines or lines == [""]:
                return []

            data = []
            for line in lines:
                if line and "|" in line:
                    values = line.split("|")
                    data.append(values)

            return data

        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return []

    def execute_command(self, database: str, query: str) -> bool:
        """Execute SQL command (INSERT/UPDATE/CREATE)"""
        try:
            cmd = [
                "docker",
                "exec",
                self.container_name,
                "psql",
                "-U",
                "horse_racing",
                "-d",
                database,
                "-c",
                query,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            return result.returncode == 0

        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return False

    def get_recent_races(self, days_back: int = 7) -> List[Dict]:
        """Get recent races with complete results"""

        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)

        query = f"""
            SELECT DISTINCT r.race_id, races.date, COUNT(*) as horse_count
            FROM records r
            JOIN races ON r.race_id = races.race_id
            WHERE races.date >= '{start_date}'
                AND races.date <= '{end_date}'
                AND r.place IS NOT NULL
                AND r.sp IS NOT NULL
            GROUP BY r.race_id, races.date
            HAVING COUNT(*) >= 5
            ORDER BY races.date DESC, r.race_id
            LIMIT 10;
        """

        raw_data = self.execute_query("results_horse_racing_db", query)

        races = []
        for row in raw_data:
            if len(row) >= 3:
                races.append(
                    {"race_id": int(row[0]), "date": row[1], "horse_count": int(row[2])}
                )

        return races

    def get_race_horses(self, race_id: int) -> List[Dict]:
        """Get all horses from a specific race"""

        query = f"""
            SELECT race_id, horse_id, name, place, sp
            FROM records
            WHERE race_id = {race_id}
                AND place IS NOT NULL
                AND sp IS NOT NULL
            ORDER BY place;
        """

        raw_data = self.execute_query("results_horse_racing_db", query)

        horses = []
        for row in raw_data:
            if len(row) >= 5:
                horses.append(
                    {
                        "race_id": int(row[0]),
                        "horse_id": int(row[1]),
                        "name": row[2].strip(),
                        "actual_position": int(row[3]),
                        "starting_price": float(row[4]),
                    }
                )

        return horses

    def generate_realistic_predictions(
        self, horses: List[Dict], race_date: str
    ) -> List[Dict]:
        """Generate realistic AI predictions for a race"""

        predictions = []

        for i, horse in enumerate(horses[:8]):  # Top 8 horses
            # Create varying prediction accuracy based on actual results
            actual_pos = horse["actual_position"]

            # Simulate AI prediction with some accuracy patterns
            if actual_pos == 1:  # Winner
                # AI should have good chance of predicting winner
                predicted_pos = random.choices(
                    [1, 2, 3, 4], weights=[0.6, 0.2, 0.15, 0.05]
                )[0]
                confidence = random.uniform(0.65, 0.90)
                win_prob = random.uniform(0.50, 0.80)
            elif actual_pos <= 3:  # Place finishers
                # AI should place these reasonably well
                predicted_pos = random.choices(
                    [1, 2, 3, 4, 5], weights=[0.2, 0.3, 0.3, 0.15, 0.05]
                )[0]
                confidence = random.uniform(0.45, 0.75)
                win_prob = random.uniform(0.30, 0.60)
            else:  # Lower finishers
                # AI might struggle with these
                predicted_pos = random.choices(
                    [1, 2, 3, 4, 5, 6, 7, 8],
                    weights=[0.1, 0.1, 0.15, 0.2, 0.2, 0.15, 0.05, 0.05],
                )[0]
                confidence = random.uniform(0.25, 0.55)
                win_prob = random.uniform(0.10, 0.40)

            # Calculate place probability
            place_prob = min(win_prob + random.uniform(0.15, 0.35), 0.95)

            prediction = {
                "race_id": horse["race_id"],
                "horse_id": horse["horse_id"],
                "horse_name": horse["name"],
                "prediction_date": race_date,
                "predicted_position": predicted_pos,
                "confidence_score": round(confidence, 3),
                "predicted_win_probability": round(win_prob, 3),
                "predicted_place_probability": round(place_prob, 3),
            }

            predictions.append(prediction)

        return predictions

    def create_ai_predictions_table(self) -> bool:
        """Create AI predictions table if it doesn't exist"""

        create_table_query = """
            CREATE TABLE IF NOT EXISTS ai_predictions (
                id SERIAL PRIMARY KEY,
                race_id BIGINT NOT NULL,
                horse_id BIGINT NOT NULL,
                horse_name VARCHAR(255) NOT NULL,
                prediction_date DATE DEFAULT CURRENT_DATE,
                predicted_position INTEGER,
                confidence_score REAL,
                predicted_win_probability REAL,
                predicted_place_probability REAL,
                prediction_algorithm VARCHAR(50) DEFAULT 'AI_SYSTEM_v2.04',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_ai_prediction
                    UNIQUE (race_id, horse_id, prediction_date)
            );
        """

        return self.execute_command("advanced_racing_metrics_db", create_table_query)

    def save_predictions(self, predictions: List[Dict]) -> bool:
        """Save AI predictions to database"""

        try:
            for pred in predictions:
                insert_query = f"""
                    INSERT INTO ai_predictions (
                        race_id, horse_id, horse_name, prediction_date,
                        predicted_position, confidence_score,
                        predicted_win_probability, predicted_place_probability
                    ) VALUES (
                        {pred['race_id']}, {pred['horse_id']}, '{pred['horse_name']}', 
                        '{pred['prediction_date']}', {pred['predicted_position']}, 
                        {pred['confidence_score']}, {pred['predicted_win_probability']}, 
                        {pred['predicted_place_probability']}
                    ) ON CONFLICT (race_id, horse_id, prediction_date) DO UPDATE SET
                        predicted_position = EXCLUDED.predicted_position,
                        confidence_score = EXCLUDED.confidence_score,
                        predicted_win_probability = EXCLUDED.predicted_win_probability,
                        predicted_place_probability = EXCLUDED.predicted_place_probability;
                """

                if not self.execute_command("advanced_racing_metrics_db", insert_query):
                    self.logger.error(
                        f"Failed to save prediction for {pred['horse_name']}"
                    )
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error saving predictions: {e}")
            return False

    def setup_realistic_test_data(self) -> bool:
        """Set up realistic test data using actual race results"""

        try:
            self.logger.info("Setting up realistic test data...")

            # Create AI predictions table
            if not self.create_ai_predictions_table():
                self.logger.error("Failed to create AI predictions table")
                return False

            # Get recent races
            races = self.get_recent_races(days_back=7)

            if not races:
                self.logger.error("No recent races found")
                return False

            self.logger.info(f"Found {len(races)} recent races")

            total_predictions = 0

            # Generate predictions for each race
            for race in races:
                race_id = race["race_id"]
                race_date = race["date"]

                self.logger.info(f"Processing race {race_id} from {race_date}")

                # Get horses in this race
                horses = self.get_race_horses(race_id)

                if len(horses) < 5:
                    self.logger.warning(
                        f"Race {race_id} has only {len(horses)} horses, skipping"
                    )
                    continue

                # Generate realistic predictions
                predictions = self.generate_realistic_predictions(horses, race_date)

                # Save predictions
                if self.save_predictions(predictions):
                    total_predictions += len(predictions)
                    self.logger.info(
                        f"Saved {len(predictions)} predictions for race {race_id}"
                    )
                else:
                    self.logger.error(f"Failed to save predictions for race {race_id}")

            self.logger.info(
                f"Realistic test data setup completed: {total_predictions} predictions created"
            )
            return total_predictions > 0

        except Exception as e:
            self.logger.error(f"Error setting up realistic test data: {e}")
            return False

    def verify_test_data(self) -> Tuple[int, int]:
        """Verify test data and return counts"""

        try:
            # Count AI predictions
            pred_query = "SELECT COUNT(*) FROM ai_predictions;"
            pred_result = self.execute_query("advanced_racing_metrics_db", pred_query)
            prediction_count = (
                int(pred_result[0][0]) if pred_result and pred_result[0] else 0
            )

            # Count matching race results
            results_query = """
                SELECT COUNT(DISTINCT r.race_id) 
                FROM records r 
                JOIN ai_predictions ap ON r.race_id = ap.race_id 
                WHERE r.place IS NOT NULL;
            """
            results_result = self.execute_query(
                "results_horse_racing_db", results_query
            )
            races_count = (
                int(results_result[0][0]) if results_result and results_result[0] else 0
            )

            return prediction_count, races_count

        except Exception as e:
            self.logger.error(f"Error verifying test data: {e}")
            return 0, 0


def main():
    """Main function for realistic test setup"""

    print("🏇 Realistic Race Results Integration Test Setup")
    print("=" * 55)

    try:
        # Initialize test data generator
        generator = RealDataTestGenerator()

        # Setup realistic test environment
        setup_success = generator.setup_realistic_test_data()

        if setup_success:
            # Verify the data
            pred_count, race_count = generator.verify_test_data()

            print(f"\n✅ Realistic test environment setup successful!")
            print(f"📊 AI predictions created: {pred_count}")
            print(f"🏁 Races with results: {race_count}")
            print(f"🧪 Ready for performance tracking analysis")
            print("\nNow run: python tools/performance/race_results_tracker.py")
            return 0
        else:
            print("\n❌ Realistic test environment setup failed")
            return 1

    except Exception as e:
        print(f"❌ Critical error in realistic test setup: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
