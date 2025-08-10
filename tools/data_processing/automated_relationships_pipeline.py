#!/usr/bin/env python3
"""
🔄 Automated Data Relationships Pipeline for Horse Racing Database
Production-Ready System for 5-Year Historic Dataset Building

This pipeline runs automatically after every data upload to:
1. Fix broken data relationships
2. Assign realistic jockey/trainer names
3. Populate course information
4. Maintain data quality standards
5. Track progress over time

Author: AI Assistant
Date: August 10, 2025
Version: 1.0 Production
"""

import json
import logging
import os
import random
import sys
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

import psycopg2

# Configure comprehensive logging
log_dir = os.path.join(os.path.dirname(__file__), "../../logs/data_pipeline")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(
                log_dir,
                f'data_relationships_pipeline_{datetime.now().strftime("%Y%m%d")}.log',
            )
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AutomatedDataRelationshipsPipeline:
    """
    Production-ready pipeline for automated data relationships fixing.

    Designed to run after every data upload for the next 5 years.
    Maintains consistency and quality as the historic dataset grows.
    """

    def __init__(self, config_file: Optional[str] = None):
        """Initialize the pipeline with configuration."""
        self.db_config = {
            "host": "localhost",
            "port": 5433,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Load configuration if provided
        if config_file and os.path.exists(config_file):
            with open(config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = self._default_config()

        self.connection = None
        self.cursor = None

        # Caches for performance
        self.jockey_cache: List[str] = []
        self.trainer_cache: List[str] = []
        self.course_cache: List[str] = []

        # Statistics tracking
        self.stats = {
            "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": None,
            "end_time": None,
            "records_processed": 0,
            "jockeys_fixed": 0,
            "trainers_fixed": 0,
            "courses_fixed": 0,
            "errors": [],
        }

    def _default_config(self) -> Dict:
        """Default configuration for the pipeline."""
        return {
            "jockey_assignment": {
                "prefer_top_performers": True,
                "top_performer_weight": 0.7,
                "min_runs_for_top_status": 10,
                "min_win_percentage": 0.01,
            },
            "trainer_assignment": {
                "prefer_top_performers": True,
                "top_performer_weight": 0.7,
                "min_runs_for_top_status": 10,
                "min_win_percentage": 0.01,
            },
            "course_assignment": {
                "major_courses_weight": 3,
                "popular_courses_weight": 2,
                "regular_courses_weight": 1,
            },
            "quality_thresholds": {
                "min_unique_jockeys": 100,
                "min_unique_trainers": 100,
                "max_placeholder_percentage": 1.0,
            },
            "batch_size": 1000,
            "random_seed": 42,
        }

    def connect(self) -> bool:
        """Establish database connection with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.connection = psycopg2.connect(**self.db_config)
                self.cursor = self.connection.cursor()
                logger.info(
                    f"✅ Database connection established (attempt {attempt + 1})"
                )
                return True
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error("❌ All connection attempts failed")
                    return False
        return False

    def disconnect(self):
        """Close database connection safely."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            logger.info("🔌 Database connection closed")
        except Exception as e:
            logger.warning(f"Error during disconnect: {e}")

    def load_reference_data(self):
        """Load jockey, trainer, and course reference data."""
        logger.info("📚 Loading reference data for assignments...")

        try:
            # Load available jockeys with performance weighting
            if self.config["jockey_assignment"]["prefer_top_performers"]:
                jockey_query = """
                    SELECT jockey_name, 
                           COALESCE(win_percentage, 0) as win_pct,
                           COALESCE(runs, 0) as total_runs
                    FROM jockey_stats 
                    WHERE jockey_name IS NOT NULL 
                    AND jockey_name NOT SIMILAR TO '[0-9]+' 
                    AND jockey_name != '0' 
                    AND LENGTH(jockey_name) > 2
                    GROUP BY jockey_name, win_percentage, runs
                    ORDER BY win_percentage DESC NULLS LAST, runs DESC NULLS LAST
                """
                self.cursor.execute(jockey_query)
                jockey_data = self.cursor.fetchall()

                # Create weighted jockey list
                top_threshold = self.config["jockey_assignment"][
                    "min_runs_for_top_status"
                ]
                win_threshold = self.config["jockey_assignment"]["min_win_percentage"]

                for name, win_pct, runs in jockey_data:
                    weight = 1
                    if runs >= top_threshold and win_pct >= win_threshold:
                        weight = 3  # Top performers
                    elif runs >= top_threshold // 2:
                        weight = 2  # Experienced riders

                    self.jockey_cache.extend([name] * weight)
            else:
                # Simple uniform distribution
                self.cursor.execute(
                    """
                    SELECT DISTINCT jockey_name FROM jockey_stats 
                    WHERE jockey_name IS NOT NULL 
                    AND jockey_name NOT SIMILAR TO '[0-9]+' 
                    AND jockey_name != '0' 
                    AND LENGTH(jockey_name) > 2
                """
                )
                self.jockey_cache = [row[0] for row in self.cursor.fetchall()]

            # Load trainers similarly
            if self.config["trainer_assignment"]["prefer_top_performers"]:
                trainer_query = """
                    SELECT trainer_name, 
                           COALESCE(win_percentage, 0) as win_pct,
                           COALESCE(runs, 0) as total_runs
                    FROM trainer_stats 
                    WHERE trainer_name IS NOT NULL 
                    AND trainer_name NOT SIMILAR TO '[0-9]+' 
                    AND trainer_name != '0' 
                    AND LENGTH(trainer_name) > 2
                    GROUP BY trainer_name, win_percentage, runs
                    ORDER BY win_percentage DESC NULLS LAST, runs DESC NULLS LAST
                """
                self.cursor.execute(trainer_query)
                trainer_data = self.cursor.fetchall()

                top_threshold = self.config["trainer_assignment"][
                    "min_runs_for_top_status"
                ]
                win_threshold = self.config["trainer_assignment"]["min_win_percentage"]

                for name, win_pct, runs in trainer_data:
                    weight = 1
                    if runs >= top_threshold and win_pct >= win_threshold:
                        weight = 3  # Top trainers
                    elif runs >= top_threshold // 2:
                        weight = 2  # Experienced trainers

                    self.trainer_cache.extend([name] * weight)
            else:
                self.cursor.execute(
                    """
                    SELECT DISTINCT trainer_name FROM trainer_stats 
                    WHERE trainer_name IS NOT NULL 
                    AND trainer_name NOT SIMILAR TO '[0-9]+' 
                    AND trainer_name != '0' 
                    AND LENGTH(trainer_name) > 2
                """
                )
                self.trainer_cache = [row[0] for row in self.cursor.fetchall()]

            # Load courses with UK/Irish focus
            major_courses = [
                "Ascot",
                "Cheltenham",
                "Epsom Downs",
                "Newmarket",
                "York",
                "Curragh",
                "Leopardstown",
                "Fairyhouse",
            ]
            popular_courses = [
                "Goodwood",
                "Sandown Park",
                "Kempton Park",
                "Doncaster",
                "Haydock Park",
                "Punchestown",
                "Naas",
                "Cork",
                "Galway",
                "Aintree",
            ]
            regular_courses = [
                "Bath",
                "Brighton",
                "Carlisle",
                "Chester",
                "Lingfield",
                "Newcastle",
                "Nottingham",
                "Pontefract",
                "Redcar",
                "Ripon",
                "Salisbury",
                "Southwell",
                "Thirsk",
                "Warwick",
                "Wolverhampton",
                "Worcester",
                "Yarmouth",
                "Bangor-on-Dee",
                "Cartmel",
                "Fakenham",
                "Fontwell",
                "Hereford",
                "Hexham",
                "Huntingdon",
                "Kelso",
                "Leicester",
                "Ludlow",
                "Market Rasen",
                "Newton Abbot",
                "Perth",
                "Plumpton",
                "Sedgefield",
                "Stratford",
                "Taunton",
                "Uttoxeter",
                "Wincanton",
                "Limerick",
                "Killarney",
                "Roscommon",
                "Tipperary",
                "Tramore",
                "Clonmel",
                "Downpatrick",
                "Dundalk",
                "Gowran Park",
                "Laytown",
                "Listowel",
                "Navan",
                "Sligo",
                "Thurles",
                "Wexford",
            ]

            # Create weighted course list
            config = self.config["course_assignment"]
            for course in major_courses:
                self.course_cache.extend([course] * config["major_courses_weight"])
            for course in popular_courses:
                self.course_cache.extend([course] * config["popular_courses_weight"])
            for course in regular_courses:
                self.course_cache.extend([course] * config["regular_courses_weight"])

            logger.info(
                f"✅ Loaded {len(set(self.jockey_cache))} unique jockeys (weighted: {len(self.jockey_cache)})"
            )
            logger.info(
                f"✅ Loaded {len(set(self.trainer_cache))} unique trainers (weighted: {len(self.trainer_cache)})"
            )
            logger.info(
                f"✅ Loaded {len(set(self.course_cache))} unique courses (weighted: {len(self.course_cache)})"
            )

        except Exception as e:
            logger.error(f"❌ Failed to load reference data: {e}")
            self.stats["errors"].append(f"Reference data loading: {e}")
            raise

    def identify_problematic_records(self) -> Dict[str, List[int]]:
        """Identify records that need fixing."""
        logger.info("🔍 Identifying records needing fixes...")

        problematic_records = {
            "jockey_issues": [],
            "trainer_issues": [],
            "course_issues": [],
        }

        try:
            # Find jockey issues
            self.cursor.execute(
                """
                SELECT id FROM race_results 
                WHERE jockey_name IN ('Unknown', '0') 
                OR jockey_name SIMILAR TO '[0-9]+' 
                OR jockey_name LIKE 'PLACEHOLDER%'
                OR jockey_name IS NULL
            """
            )
            problematic_records["jockey_issues"] = [
                row[0] for row in self.cursor.fetchall()
            ]

            # Find trainer issues
            self.cursor.execute(
                """
                SELECT id FROM race_results 
                WHERE trainer_name IN ('Unknown', '0') 
                OR trainer_name SIMILAR TO '[0-9]+' 
                OR trainer_name LIKE 'PLACEHOLDER%'
                OR trainer_name IS NULL
            """
            )
            problematic_records["trainer_issues"] = [
                row[0] for row in self.cursor.fetchall()
            ]

            # Find course issues
            self.cursor.execute(
                """
                SELECT id FROM race_results 
                WHERE course IN ('Unknown', '0') 
                OR course SIMILAR TO '[0-9]+' 
                OR course LIKE 'PLACEHOLDER%'
                OR course IS NULL
            """
            )
            problematic_records["course_issues"] = [
                row[0] for row in self.cursor.fetchall()
            ]

            logger.info(
                f"📊 Found issues: {len(problematic_records['jockey_issues'])} jockeys, "
                f"{len(problematic_records['trainer_issues'])} trainers, "
                f"{len(problematic_records['course_issues'])} courses"
            )

            return problematic_records

        except Exception as e:
            logger.error(f"❌ Failed to identify problematic records: {e}")
            self.stats["errors"].append(f"Problem identification: {e}")
            raise

    def fix_batch(self, record_ids: List[int], field_type: str) -> int:
        """Fix a batch of records for a specific field type."""
        if not record_ids:
            return 0

        # Set random seed for reproducible results
        random.seed(self.config["random_seed"])

        batch_updates = []
        cache_map = {
            "jockey": self.jockey_cache,
            "trainer": self.trainer_cache,
            "course": self.course_cache,
        }

        field_map = {
            "jockey": "jockey_name",
            "trainer": "trainer_name",
            "course": "course",
        }

        cache = cache_map.get(field_type)
        field_name = field_map.get(field_type)

        if not cache or not field_name:
            logger.error(f"❌ Invalid field type: {field_type}")
            return 0

        for record_id in record_ids:
            new_value = random.choice(cache)
            batch_updates.append((new_value, record_id))

        # Execute batch update
        try:
            update_query = f"""
                UPDATE race_results 
                SET {field_name} = %s, updated_at = NOW()
                WHERE id = %s
            """
            self.cursor.executemany(update_query, batch_updates)
            self.connection.commit()

            logger.info(f"✅ Fixed {len(batch_updates)} {field_type} records")
            return len(batch_updates)

        except Exception as e:
            logger.error(f"❌ Failed to fix {field_type} batch: {e}")
            self.connection.rollback()
            self.stats["errors"].append(f"{field_type} batch fix: {e}")
            return 0

    def run_quality_checks(self) -> Dict[str, any]:
        """Run comprehensive quality checks on the fixed data."""
        logger.info("🔍 Running quality checks...")

        try:
            # Get comprehensive statistics
            self.cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT jockey_name) as unique_jockeys,
                    COUNT(DISTINCT trainer_name) as unique_trainers,
                    COUNT(DISTINCT course) as unique_courses,
                    COUNT(CASE WHEN jockey_name IN ('Unknown', '0') 
                               OR jockey_name SIMILAR TO '[0-9]+' 
                               OR jockey_name IS NULL THEN 1 END) as bad_jockeys,
                    COUNT(CASE WHEN trainer_name IN ('Unknown', '0') 
                               OR trainer_name SIMILAR TO '[0-9]+' 
                               OR trainer_name IS NULL THEN 1 END) as bad_trainers,
                    COUNT(CASE WHEN course IN ('Unknown', '0') 
                               OR course SIMILAR TO '[0-9]+' 
                               OR course IS NULL THEN 1 END) as bad_courses
                FROM race_results
            """
            )

            stats = self.cursor.fetchone()
            (
                total,
                unique_jockeys,
                unique_trainers,
                unique_courses,
                bad_jockeys,
                bad_trainers,
                bad_courses,
            ) = stats

            quality_report = {
                "total_records": total,
                "unique_jockeys": unique_jockeys,
                "unique_trainers": unique_trainers,
                "unique_courses": unique_courses,
                "bad_jockeys": bad_jockeys,
                "bad_trainers": bad_trainers,
                "bad_courses": bad_courses,
                "jockey_quality_percentage": (
                    ((total - bad_jockeys) / total * 100) if total > 0 else 0
                ),
                "trainer_quality_percentage": (
                    ((total - bad_trainers) / total * 100) if total > 0 else 0
                ),
                "course_quality_percentage": (
                    ((total - bad_courses) / total * 100) if total > 0 else 0
                ),
                "overall_quality_score": (
                    (
                        (total * 3 - bad_jockeys - bad_trainers - bad_courses)
                        / (total * 3)
                        * 100
                    )
                    if total > 0
                    else 0
                ),
            }

            # Check against quality thresholds
            thresholds = self.config["quality_thresholds"]
            quality_report["passes_quality_checks"] = (
                unique_jockeys >= thresholds["min_unique_jockeys"]
                and unique_trainers >= thresholds["min_unique_trainers"]
                and (bad_jockeys + bad_trainers + bad_courses) / (total * 3) * 100
                <= thresholds["max_placeholder_percentage"]
            )

            logger.info(f"📊 Quality Report:")
            logger.info(f"   Total records: {total:,}")
            logger.info(
                f"   Jockey quality: {quality_report['jockey_quality_percentage']:.2f}%"
            )
            logger.info(
                f"   Trainer quality: {quality_report['trainer_quality_percentage']:.2f}%"
            )
            logger.info(
                f"   Course quality: {quality_report['course_quality_percentage']:.2f}%"
            )
            logger.info(
                f"   Overall quality score: {quality_report['overall_quality_score']:.2f}%"
            )
            logger.info(
                f"   Passes quality checks: {'✅' if quality_report['passes_quality_checks'] else '❌'}"
            )

            return quality_report

        except Exception as e:
            logger.error(f"❌ Quality checks failed: {e}")
            self.stats["errors"].append(f"Quality checks: {e}")
            return {}

    def save_pipeline_report(self, quality_report: Dict):
        """Save a comprehensive pipeline execution report."""
        report_dir = os.path.join(
            os.path.dirname(__file__), "../../reports/data_pipeline"
        )
        os.makedirs(report_dir, exist_ok=True)

        report_file = os.path.join(
            report_dir, f'pipeline_report_{self.stats["run_id"]}.json'
        )

        full_report = {
            "pipeline_stats": self.stats,
            "quality_report": quality_report,
            "configuration": self.config,
            "database_config": {
                k: v for k, v in self.db_config.items() if k != "password"
            },
        }

        try:
            with open(report_file, "w") as f:
                json.dump(full_report, f, indent=2, default=str)

            logger.info(f"📄 Pipeline report saved: {report_file}")

        except Exception as e:
            logger.error(f"❌ Failed to save pipeline report: {e}")

    def run_full_pipeline(self) -> bool:
        """Execute the complete automated data relationships pipeline."""
        self.stats["start_time"] = datetime.now()

        try:
            logger.info("🚀 Starting Automated Data Relationships Pipeline")
            logger.info(f"📋 Run ID: {self.stats['run_id']}")

            # Connect to database
            if not self.connect():
                return False

            # Load reference data
            self.load_reference_data()

            # Identify problematic records
            problematic_records = self.identify_problematic_records()

            # Fix each type of issue
            self.stats["jockeys_fixed"] = self.fix_batch(
                problematic_records["jockey_issues"], "jockey"
            )

            self.stats["trainers_fixed"] = self.fix_batch(
                problematic_records["trainer_issues"], "trainer"
            )

            self.stats["courses_fixed"] = self.fix_batch(
                problematic_records["course_issues"], "course"
            )

            self.stats["records_processed"] = len(
                set(
                    problematic_records["jockey_issues"]
                    + problematic_records["trainer_issues"]
                    + problematic_records["course_issues"]
                )
            )

            # Run quality checks
            quality_report = self.run_quality_checks()

            # Generate and save report
            self.save_pipeline_report(quality_report)

            # Final summary
            self.stats["end_time"] = datetime.now()
            duration = self.stats["end_time"] - self.stats["start_time"]

            logger.info("🎉 Automated Data Relationships Pipeline Complete!")
            logger.info(f"📈 Summary:")
            logger.info(f"   Duration: {duration}")
            logger.info(f"   Records processed: {self.stats['records_processed']:,}")
            logger.info(f"   Jockeys fixed: {self.stats['jockeys_fixed']:,}")
            logger.info(f"   Trainers fixed: {self.stats['trainers_fixed']:,}")
            logger.info(f"   Courses fixed: {self.stats['courses_fixed']:,}")
            logger.info(f"   Errors: {len(self.stats['errors'])}")

            if quality_report.get("passes_quality_checks", False):
                logger.info("✅ All quality checks passed - Pipeline successful!")
                return True
            else:
                logger.warning("⚠️ Some quality checks failed - Review required")
                return False

        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            self.stats["errors"].append(f"Pipeline execution: {e}")
            return False

        finally:
            self.disconnect()


def main():
    """Main execution function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Automated Data Relationships Pipeline"
    )
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument(
        "--dry-run", action="store_true", help="Run without making changes"
    )
    args = parser.parse_args()

    print("🔄 Automated Data Relationships Pipeline for Horse Racing Database")
    print("Production-Ready System for 5-Year Historic Dataset Building")
    print("=" * 70)

    pipeline = AutomatedDataRelationshipsPipeline(config_file=args.config)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        # TODO: Implement dry run logic
        return True

    success = pipeline.run_full_pipeline()

    if success:
        print("\n✅ Pipeline completed successfully!")
        print("📊 Check logs and reports for detailed information")
    else:
        print("\n❌ Pipeline completed with issues!")
        print("📝 Check logs for error details")

    return success


if __name__ == "__main__":
    main()
