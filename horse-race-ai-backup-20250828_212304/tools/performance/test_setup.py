#!/usr/bin/env python3
"""
Race Results Integration Test Setup

Creates sample AI predictions and race results data for testing
the performance tracking system.
"""

import logging
import sys
import os
import subprocess
from datetime import datetime, date, timedelta
from typing import List, Dict

# Add project root to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.04")


class TestDataGenerator:
    """Generate test data for race results integration"""

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

    def execute_query(self, database: str, query: str) -> bool:
        """Execute SQL query using docker exec"""
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

            if result.returncode != 0:
                self.logger.error(f"Query failed: {result.stderr}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return False

    def create_sample_ai_predictions(self) -> bool:
        """Create sample AI predictions for testing"""

        try:
            # First create the ai_predictions table if it doesn't exist
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

            if not self.execute_query("advanced_racing_metrics_db", create_table_query):
                return False

            # Sample AI predictions data
            predictions = [
                # Race 1 - High confidence predictions
                (101, 1001, "Thunder Strike", "2025-08-20", 1, 0.85, 0.75, 0.90),
                (101, 1002, "Lightning Bolt", "2025-08-20", 2, 0.72, 0.45, 0.80),
                (101, 1003, "Storm Rider", "2025-08-20", 3, 0.68, 0.35, 0.75),
                # Race 2 - Medium confidence predictions
                (102, 2001, "Wind Walker", "2025-08-21", 1, 0.62, 0.55, 0.70),
                (102, 2002, "Sky Runner", "2025-08-21", 2, 0.58, 0.40, 0.65),
                (102, 2003, "Cloud Chaser", "2025-08-21", 3, 0.54, 0.30, 0.60),
                # Race 3 - Low confidence predictions
                (103, 3001, "Fire Flash", "2025-08-22", 1, 0.45, 0.35, 0.55),
                (103, 3002, "Flame Runner", "2025-08-22", 2, 0.42, 0.30, 0.50),
                (103, 3003, "Blaze Spirit", "2025-08-22", 3, 0.38, 0.25, 0.45),
                # Race 4 - Mixed confidence
                (104, 4001, "Ocean Wave", "2025-08-23", 1, 0.78, 0.65, 0.85),
                (104, 4002, "River Flow", "2025-08-23", 2, 0.51, 0.35, 0.60),
                (104, 4003, "Mountain Peak", "2025-08-23", 3, 0.46, 0.30, 0.55),
            ]

            # Insert predictions
            for pred in predictions:
                insert_query = f"""
                    INSERT INTO ai_predictions (
                        race_id, horse_id, horse_name, prediction_date,
                        predicted_position, confidence_score,
                        predicted_win_probability, predicted_place_probability
                    ) VALUES (
                        {pred[0]}, {pred[1]}, '{pred[2]}', '{pred[3]}',
                        {pred[4]}, {pred[5]}, {pred[6]}, {pred[7]}
                    ) ON CONFLICT (race_id, horse_id, prediction_date) DO UPDATE SET
                        predicted_position = EXCLUDED.predicted_position,
                        confidence_score = EXCLUDED.confidence_score,
                        predicted_win_probability = EXCLUDED.predicted_win_probability,
                        predicted_place_probability = EXCLUDED.predicted_place_probability;
                """

                if not self.execute_query("advanced_racing_metrics_db", insert_query):
                    self.logger.error(f"Failed to insert prediction: {pred}")
                    return False

            self.logger.info("Sample AI predictions created successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error creating sample AI predictions: {e}")
            return False

    def create_sample_race_results(self) -> bool:
        """Create sample race results for testing"""

        try:
            # Sample race results - some matching predictions, some surprises
            race_results = [
                # Race 101 - AI mostly correct
                (101, 1001, "Thunder Strike", 1, 3.5, "2025-08-20"),  # Correct
                (101, 1002, "Lightning Bolt", 3, 5.2, "2025-08-20"),  # Wrong pos
                (101, 1003, "Storm Rider", 2, 4.8, "2025-08-20"),  # Wrong pos
                (101, 1004, "Wild Wind", 4, 8.5, "2025-08-20"),  # Not predicted
                # Race 102 - AI partially correct
                (102, 2001, "Wind Walker", 2, 4.2, "2025-08-21"),  # Wrong pos
                (102, 2002, "Sky Runner", 1, 6.8, "2025-08-21"),  # Wrong pos
                (102, 2003, "Cloud Chaser", 3, 7.2, "2025-08-21"),  # Correct
                (102, 2004, "Fast Track", 4, 12.0, "2025-08-21"),  # Not predicted
                # Race 103 - AI struggles
                (103, 3001, "Fire Flash", 4, 9.5, "2025-08-22"),  # Wrong pos
                (103, 3002, "Flame Runner", 3, 11.2, "2025-08-22"),  # Wrong pos
                (103, 3003, "Blaze Spirit", 2, 8.8, "2025-08-22"),  # Wrong pos
                (103, 3004, "Speed Demon", 1, 15.5, "2025-08-22"),  # Surprise winner
                # Race 104 - AI performs well
                (104, 4001, "Ocean Wave", 1, 2.8, "2025-08-23"),  # Correct
                (104, 4002, "River Flow", 2, 6.5, "2025-08-23"),  # Correct
                (104, 4003, "Mountain Peak", 4, 9.2, "2025-08-23"),  # Wrong pos
                (104, 4004, "Valley Runner", 3, 12.8, "2025-08-23"),  # Not predicted
            ]

            # Insert race results
            for result in race_results:
                # Insert into races table first
                race_insert = f"""
                    INSERT INTO races (race_id, date, course, race_name)
                    VALUES ({result[0]}, '{result[5]}', 'Test Track',
                           'Test Race {result[0]}')
                    ON CONFLICT (race_id) DO NOTHING;
                """

                if not self.execute_query("results_horse_racing_db", race_insert):
                    self.logger.warning(
                        f"Could not insert race {result[0]} - may already exist"
                    )

                # Insert into records table (let ID auto-increment)
                record_insert = f"""
                    INSERT INTO records (race_id, horse_id, name, place, sp)
                    VALUES ({result[0]}, {result[1]}, '{result[2]}',
                           {result[3]}, {result[4]});
                """

                if not self.execute_query("results_horse_racing_db", record_insert):
                    # Try to update if already exists
                    update_query = f"""
                        UPDATE records SET place = {result[3]}, sp = {result[4]}
                        WHERE race_id = {result[0]} AND horse_id = {result[1]};
                    """
                    if not self.execute_query("results_horse_racing_db", update_query):
                        self.logger.error(
                            f"Failed to insert/update race result: {result}"
                        )
                        return False

            self.logger.info("Sample race results created successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error creating sample race results: {e}")
            return False

    def verify_test_data(self) -> bool:
        """Verify test data was created successfully"""

        try:
            # Check AI predictions
            pred_check = self.execute_query(
                "advanced_racing_metrics_db", "SELECT COUNT(*) FROM ai_predictions;"
            )

            # Check race results
            results_check = self.execute_query(
                "results_horse_racing_db",
                "SELECT COUNT(*) FROM records WHERE race_id IN (101, 102, 103, 104);",
            )

            if pred_check and results_check:
                self.logger.info("Test data verification successful")
                return True
            else:
                self.logger.error("Test data verification failed")
                return False

        except Exception as e:
            self.logger.error(f"Error verifying test data: {e}")
            return False

    def setup_test_environment(self) -> bool:
        """Set up complete test environment"""

        try:
            self.logger.info("Setting up test environment...")

            # Create sample AI predictions
            if not self.create_sample_ai_predictions():
                self.logger.error("Failed to create AI predictions")
                return False

            # Create sample race results
            if not self.create_sample_race_results():
                self.logger.error("Failed to create race results")
                return False

            # Verify test data
            if not self.verify_test_data():
                self.logger.error("Test data verification failed")
                return False

            self.logger.info("Test environment setup completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error setting up test environment: {e}")
            return False


def main():
    """Main function for test setup"""

    print("🏇 Race Results Integration Test Setup")
    print("=" * 50)

    try:
        # Initialize test data generator
        generator = TestDataGenerator()

        # Setup test environment
        setup_success = generator.setup_test_environment()

        if setup_success:
            print("\n✅ Test environment setup successful!")
            print("📊 Sample AI predictions created")
            print("🏁 Sample race results created")
            print("🧪 Ready for performance tracking tests")
            return 0
        else:
            print("\n❌ Test environment setup failed")
            return 1

    except Exception as e:
        print(f"❌ Critical error in test setup: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
