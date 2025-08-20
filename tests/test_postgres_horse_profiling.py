"""
Comprehensive test for PostgreSQL horse profiling system.
Tests database integration, profiling functionality, and API endpoints.
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.horse_racing_ai.analytics.postgres_horse_profiling import (
    PostgreSQLHorseProfilingSystem,
    HorseFormTrend,
    ConditionProfile,
    HorseProfile,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PostgreSQLHorseProfilingTest:
    """Comprehensive test suite for PostgreSQL horse profiling system."""

    def __init__(self):
        """Initialize test suite."""
        self.profiling_system = None
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": [],
        }

    def log_test_result(self, test_name: str, success: bool, error: str = None):
        """Log test result."""
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed_tests"] += 1
            logger.info("✅ %s - PASSED", test_name)
        else:
            self.test_results["failed_tests"] += 1
            logger.error("❌ %s - FAILED: %s", test_name, error)
            self.test_results["errors"].append(f"{test_name}: {error}")

    def test_database_connection(self):
        """Test PostgreSQL database connection."""
        try:
            # Initialize with Docker database configuration
            self.profiling_system = PostgreSQLHorseProfilingSystem(
                host="localhost",
                port=5434,
                database="horse_racing_db",
                user="horse_racing",
                password="secure_password_123",
            )

            # Test basic connection
            with self.profiling_system.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()[0]
                    logger.info("Connected to PostgreSQL: %s", version)

            # Test SQLAlchemy engine
            engine = self.profiling_system.get_sqlalchemy_engine()
            if engine is None:
                raise Exception("Failed to create SQLAlchemy engine")

            self.log_test_result("Database Connection", True)
            return True

        except Exception as e:
            self.log_test_result("Database Connection", False, str(e))
            return False

    def test_table_creation(self):
        """Test profiling table creation."""
        try:
            self.profiling_system.create_profiling_tables()

            # Verify tables were created
            with self.profiling_system.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name IN (
                            'horse_form_trends',
                            'horse_optimal_conditions'
                        )
                    """
                    )
                    tables = [row[0] for row in cursor.fetchall()]

            expected_tables = ["horse_form_trends", "horse_optimal_conditions"]
            missing_tables = set(expected_tables) - set(tables)

            if missing_tables:
                raise Exception(f"Missing tables: {missing_tables}")

            self.log_test_result("Table Creation", True)
            return True

        except Exception as e:
            self.log_test_result("Table Creation", False, str(e))
            return False

    def test_sample_data_check(self):
        """Check if sample horse data exists in the database."""
        try:
            engine = self.profiling_system.get_sqlalchemy_engine()

            # Check for sample horse data
            with engine.connect() as conn:
                result = conn.execute("SELECT COUNT(*) FROM horses LIMIT 1")
                horse_count = result.fetchone()[0]

                result = conn.execute("SELECT COUNT(*) FROM records LIMIT 1")
                record_count = result.fetchone()[0]

            logger.info("Found %d horses, %d records", horse_count, record_count)

            if horse_count == 0 or record_count == 0:
                logger.warning("No sample data found - skipping data-dependent tests")
                self.log_test_result("Sample Data Check", True, "No data available")
                return False

            self.log_test_result("Sample Data Check", True)
            return True

        except Exception as e:
            self.log_test_result("Sample Data Check", False, str(e))
            return False

    def test_form_trend_classification(self):
        """Test horse form trend classification."""
        try:
            # Get a sample horse ID
            engine = self.profiling_system.get_sqlalchemy_engine()
            with engine.connect() as conn:
                result = conn.execute(
                    """
                    SELECT DISTINCT horse_id 
                    FROM records 
                    LIMIT 1
                """
                )
                sample_horse = result.fetchone()

            if not sample_horse:
                raise Exception("No horses available for testing")

            horse_id = sample_horse[0]

            # Test form trend classification
            form_trend = self.profiling_system.classify_form_trend(horse_id)

            if not isinstance(form_trend, HorseFormTrend):
                raise Exception(f"Invalid form trend type: {type(form_trend)}")

            logger.info("Horse %s form trend: %s", horse_id, form_trend.value)

            self.log_test_result("Form Trend Classification", True)
            return True

        except Exception as e:
            self.log_test_result("Form Trend Classification", False, str(e))
            return False

    def test_condition_profiling(self):
        """Test condition-specific performance profiling."""
        try:
            # Get a sample horse ID
            engine = self.profiling_system.get_sqlalchemy_engine()
            with engine.connect() as conn:
                result = conn.execute(
                    """
                    SELECT DISTINCT horse_id 
                    FROM records 
                    LIMIT 1
                """
                )
                sample_horse = result.fetchone()

            if not sample_horse:
                raise Exception("No horses available for testing")

            horse_id = sample_horse[0]

            # Test each condition type
            condition_types = ["track", "distance", "going", "class"]

            for condition_type in condition_types:
                profiles = self.profiling_system.analyze_condition_profiles(
                    horse_id, condition_type
                )

                logger.info(
                    "Horse %s %s profiles: %d conditions",
                    horse_id,
                    condition_type,
                    len(profiles),
                )

                # Validate profile structure
                for condition_name, profile in profiles.items():
                    if not isinstance(profile, ConditionProfile):
                        raise Exception(
                            f"Invalid profile type for {condition_name}: "
                            f"{type(profile)}"
                        )

            self.log_test_result("Condition Profiling", True)
            return True

        except Exception as e:
            self.log_test_result("Condition Profiling", False, str(e))
            return False

    def test_progressive_horses(self):
        """Test progressive horses identification."""
        try:
            progressive_horses = self.profiling_system.get_progressive_horses(
                min_runs=3
            )

            logger.info("Found %d progressive horses", len(progressive_horses))

            # Validate response structure
            for horse in progressive_horses:
                required_keys = ["horse_id", "horse_name", "form_trend"]
                missing_keys = [key for key in required_keys if key not in horse]

                if missing_keys:
                    raise Exception(f"Missing keys in horse data: {missing_keys}")

            self.log_test_result("Progressive Horses", True)
            return True

        except Exception as e:
            self.log_test_result("Progressive Horses", False, str(e))
            return False

    def test_profile_generation(self):
        """Test complete horse profile generation."""
        try:
            # Get a sample horse ID
            engine = self.profiling_system.get_sqlalchemy_engine()
            with engine.connect() as conn:
                result = conn.execute(
                    """
                    SELECT DISTINCT horse_id 
                    FROM records 
                    LIMIT 1
                """
                )
                sample_horse = result.fetchone()

            if not sample_horse:
                raise Exception("No horses available for testing")

            horse_id = sample_horse[0]

            # Generate profile
            profile = self.profiling_system.generate_horse_profile(horse_id)

            if not profile:
                raise Exception("Failed to generate horse profile")

            if not isinstance(profile, HorseProfile):
                raise Exception(f"Invalid profile type: {type(profile)}")

            # Validate profile attributes
            required_attrs = [
                "horse_id",
                "horse_name",
                "form_trend",
                "trend_confidence",
                "preferred_conditions",
                "performance_metrics",
                "last_updated",
                "confidence_level",
            ]

            for attr in required_attrs:
                if not hasattr(profile, attr):
                    raise Exception(f"Missing profile attribute: {attr}")

            logger.info(
                "Generated profile for %s - Confidence: %.2f",
                profile.horse_name,
                profile.confidence_level,
            )

            self.log_test_result("Profile Generation", True)
            return profile

        except Exception as e:
            self.log_test_result("Profile Generation", False, str(e))
            return None

    def test_profile_persistence(self):
        """Test horse profile saving to database."""
        try:
            # Generate a profile first
            profile = self.test_profile_generation()

            if not profile:
                raise Exception("No profile available for persistence test")

            # Save profile to database
            self.profiling_system.save_horse_profile(profile)

            # Verify the profile was saved
            with self.profiling_system.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT COUNT(*) FROM horse_form_trends WHERE horse_id = %s",
                        (profile.horse_id,),
                    )
                    trend_count = cursor.fetchone()[0]

                    cursor.execute(
                        "SELECT COUNT(*) FROM horse_optimal_conditions WHERE horse_id = %s",
                        (profile.horse_id,),
                    )
                    condition_count = cursor.fetchone()[0]

            if trend_count == 0:
                raise Exception("Form trend data not saved")

            if condition_count == 0:
                raise Exception("Optimal conditions data not saved")

            logger.info("Profile saved successfully for horse %s", profile.horse_id)

            self.log_test_result("Profile Persistence", True)
            return True

        except Exception as e:
            self.log_test_result("Profile Persistence", False, str(e))
            return False

    def run_comprehensive_test(self):
        """Run all tests in sequence."""
        logger.info("🏇 Starting PostgreSQL Horse Profiling System Tests")
        logger.info("=" * 60)

        # Database connection tests
        if not self.test_database_connection():
            logger.error("Database connection failed - stopping tests")
            return self.test_results

        # Table creation tests
        if not self.test_table_creation():
            logger.error("Table creation failed - stopping tests")
            return self.test_results

        # Check for sample data
        has_data = self.test_sample_data_check()

        if has_data:
            # Data-dependent tests
            self.test_form_trend_classification()
            self.test_condition_profiling()
            self.test_progressive_horses()
            self.test_profile_generation()
            self.test_profile_persistence()
        else:
            logger.warning("Skipping data-dependent tests due to lack of sample data")

        # Print final results
        logger.info("=" * 60)
        logger.info("🏁 Test Results Summary")
        logger.info("Total Tests: %d", self.test_results["total_tests"])
        logger.info("Passed: %d", self.test_results["passed_tests"])
        logger.info("Failed: %d", self.test_results["failed_tests"])

        if self.test_results["failed_tests"] > 0:
            logger.info("❌ Errors:")
            for error in self.test_results["errors"]:
                logger.info("  - %s", error)
        else:
            logger.info("✅ All tests passed!")

        success_rate = (
            self.test_results["passed_tests"] / self.test_results["total_tests"] * 100
            if self.test_results["total_tests"] > 0
            else 0
        )
        logger.info("Success Rate: %.1f%%", success_rate)

        return self.test_results


def main():
    """Run the comprehensive test suite."""
    test_suite = PostgreSQLHorseProfilingTest()
    results = test_suite.run_comprehensive_test()

    # Exit with error code if tests failed
    if results["failed_tests"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
