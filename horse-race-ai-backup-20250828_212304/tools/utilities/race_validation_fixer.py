#!/usr/bin/env python3
"""
Race Card Upload Validation and Fix Script
==========================================

This script addresses the race overlap validation issue by:
1. Detecting when race cards contain only yesterday's data (complete overlap)
2. Validating whether new races exist for today
3. Preventing duplicate database uploads
4. Providing clear diagnostic information

Key Issues Addressed:
- Race ID overlap between results and cards data
- Database upload failures due to duplicate race IDs
- Validation logic improvements for edge cases
"""

import logging
import os
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
import psycopg2

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RaceCardValidationFixer:
    """Fixes race card validation and upload issues"""

    def __init__(self):
        self.data_dir = project_root / "data" / "daily_downloads"
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def analyze_race_overlap_issue(self) -> Dict:
        """Analyze the current race overlap situation"""
        results = {
            "analysis_time": datetime.now().isoformat(),
            "issue_detected": False,
            "overlap_type": None,
            "recommendations": [],
            "race_data": {},
        }

        try:
            # Check data directories
            results_path = self.data_dir / "results_data"
            cards_path = self.data_dir / "cards_data"

            if not results_path.exists() or not cards_path.exists():
                results["issue_detected"] = True
                results["overlap_type"] = "missing_data"
                results["recommendations"].append(
                    "Missing data directories - run auto-downloader"
                )
                return results

            # Extract race information
            results_races = self._get_race_info(results_path / "races" / "races.csv")
            cards_races = self._get_race_info(cards_path / "races" / "races.csv")

            results["race_data"]["results"] = results_races
            results["race_data"]["cards"] = cards_races

            # Analyze overlap
            if not results_races["race_ids"] or not cards_races["race_ids"]:
                results["issue_detected"] = True
                results["overlap_type"] = "no_race_data"
                results["recommendations"].append(
                    "No race data found - check downloader"
                )
                return results

            # Check for complete overlap
            overlap_ids = results_races["race_ids"].intersection(
                cards_races["race_ids"]
            )
            overlap_percentage = len(overlap_ids) / max(
                len(results_races["race_ids"]), len(cards_races["race_ids"])
            )

            if overlap_percentage >= 0.9:
                results["issue_detected"] = True
                results["overlap_type"] = "complete_overlap"
                results["recommendations"].extend(
                    [
                        "Complete race overlap detected - same races in both datasets",
                        "This indicates no new races scheduled for today",
                        "Database upload should be skipped to avoid duplicates",
                        "Validation logic should handle this scenario gracefully",
                    ]
                )

                # Check if this is legitimate (weekend/holiday)
                today = datetime.now().date()
                if today.weekday() >= 5:  # Saturday or Sunday
                    results["recommendations"].append(
                        "Weekend detected - reduced racing schedule is normal"
                    )

            elif overlap_percentage > 0.3:
                results["issue_detected"] = True
                results["overlap_type"] = "partial_overlap"
                results["recommendations"].extend(
                    [
                        f"Partial race overlap detected ({overlap_percentage:.1%})",
                        "This may indicate data synchronization issues",
                        "Check auto-downloader timing and race schedule updates",
                    ]
                )

            # Check database status
            db_status = self._check_database_race_status(overlap_ids)
            results["race_data"]["database"] = db_status

            if db_status["races_in_db"] and overlap_ids:
                results["recommendations"].append(
                    "WARNING: Overlapping races already exist in database"
                )
                results["recommendations"].append(
                    "Database upload will fail due to primary key conflicts"
                )

        except Exception as e:
            logger.error(f"Error analyzing race overlap: {e}")
            results["issue_detected"] = True
            results["overlap_type"] = "analysis_error"
            results["recommendations"].append(f"Analysis failed: {str(e)}")

        return results

    def _get_race_info(self, csv_path: Path) -> Dict:
        """Extract race information from CSV"""
        info = {
            "file_exists": csv_path.exists(),
            "race_ids": set(),
            "dates": set(),
            "race_count": 0,
            "date_range": None,
        }

        if not csv_path.exists():
            return info

        try:
            df = pd.read_csv(csv_path)

            if "Race_ID" in df.columns:
                info["race_ids"] = set(df["Race_ID"].dropna().astype(int))
                info["race_count"] = len(info["race_ids"])

            if "Date" in df.columns:
                dates = pd.to_datetime(df["Date"], errors="coerce").dt.date
                info["dates"] = set(dates.dropna())
                if info["dates"]:
                    info["date_range"] = f"{min(info['dates'])} to {max(info['dates'])}"

        except Exception as e:
            logger.error(f"Error reading {csv_path}: {e}")

        return info

    def _check_database_race_status(self, race_ids: Set[int]) -> Dict:
        """Check if races already exist in database"""
        status = {
            "connection_ok": False,
            "races_in_db": False,
            "existing_race_count": 0,
            "existing_race_ids": [],
        }

        if not race_ids:
            return status

        try:
            with psycopg2.connect(**self.db_config) as conn:
                status["connection_ok"] = True

                with conn.cursor() as cur:
                    # Check for existing races
                    race_ids_list = list(race_ids)
                    cur.execute(
                        "SELECT race_id FROM races WHERE race_id = ANY(%s)",
                        (race_ids_list,),
                    )
                    existing_races = cur.fetchall()

                    if existing_races:
                        status["races_in_db"] = True
                        status["existing_race_ids"] = [r[0] for r in existing_races]
                        status["existing_race_count"] = len(existing_races)

        except Exception as e:
            logger.error(f"Database check failed: {e}")

        return status

    def fix_validation_logic(self) -> bool:
        """Fix the validation logic to handle race overlaps properly"""
        validator_path = (
            project_root / "tools" / "data_processing" / "data_validator.py"
        )

        if not validator_path.exists():
            logger.error(f"Validator not found: {validator_path}")
            return False

        try:
            # Read current validator
            with open(validator_path, "r") as f:
                content = f.read()

            # Check if already fixed
            if "RACE_OVERLAP_FIX_APPLIED" in content:
                logger.info("Validation fix already applied")
                return True

            # Apply fixes
            fixed_content = self._apply_validation_fixes(content)

            # Write back
            with open(validator_path, "w") as f:
                f.write(fixed_content)

            logger.info("Validation logic fixes applied successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to fix validation logic: {e}")
            return False

    def _apply_validation_fixes(self, content: str) -> str:
        """Apply specific fixes to validation logic"""

        # Fix 1: Improve overlap detection logic
        overlap_fix = """
        # RACE_OVERLAP_FIX_APPLIED - Enhanced overlap detection
        if overlapping_ids:
            overlap_percentage = len(overlapping_ids) / max(
                len(results_race_ids), len(cards_race_ids), 1
            )
            
            # Complete overlap - check if legitimate
            if overlap_percentage >= 0.95 and len(overlapping_ids) >= 10:
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                
                # Check if this is weekend/holiday scenario
                is_weekend = today.weekday() >= 5
                all_cards_yesterday = all(d == yesterday for d in cards_dates)
                
                if is_weekend or all_cards_yesterday:
                    logger.info(
                        f"✅ Complete overlap scenario detected: "
                        f"{len(overlapping_ids)} races, weekend={is_weekend}, "
                        f"cards_from_yesterday={all_cards_yesterday}"
                    )
                    self.validation_results["warnings"].append(
                        f"No new races today - using yesterday's data: {len(overlapping_ids)} races"
                    )
                    # Set flag to skip database upload
                    self.validation_results["summary"]["skip_database_upload"] = True
                else:
                    self.validation_results["errors"].append(
                        f"Unexpected complete race overlap: {len(overlapping_ids)} races"
                    )
            else:
                # Partial overlap - always problematic
                self.validation_results["errors"].append(
                    f"Race ID overlap detected ({overlap_percentage:.1%}): {sorted(list(overlapping_ids)[:10])}"
                )
        """

        # Replace the original overlap detection
        original_pattern = r"if overlapping_ids:.*?overlapping_ids\s*\)"
        import re

        content = re.sub(
            original_pattern, overlap_fix.strip(), content, flags=re.DOTALL
        )

        return content

    def create_smart_upload_script(self) -> Path:
        """Create a smart upload script that handles overlaps"""
        script_path = (
            project_root / "tools" / "data_processing" / "smart_race_uploader.py"
        )

        script_content = '''#!/usr/bin/env python3
"""
Smart Race Card Uploader
========================

Handles race card uploads with overlap detection and duplicate prevention.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, date
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}

class SmartRaceUploader:
    """Smart uploader that prevents duplicate race uploads"""
    
    def __init__(self):
        self.data_dir = project_root / "data" / "daily_downloads"
        self.logger = logging.getLogger(__name__)
    
    def upload_race_cards(self, force: bool = False) -> Dict:
        """Upload race cards with overlap checking"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "races_processed": 0,
            "duplicates_skipped": 0,
            "errors": []
        }
        
        try:
            # Check for data
            cards_path = self.data_dir / "cards_data" / "races" / "races.csv"
            if not cards_path.exists():
                result["status"] = "failed"
                result["errors"].append("No race card data found")
                return result
            
            # Load race data
            df = pd.read_csv(cards_path)
            if df.empty:
                result["status"] = "failed"
                result["errors"].append("Empty race card data")
                return result
            
            # Check for existing races in database
            with psycopg2.connect(**DB_CONFIG) as conn:
                existing_races = self._get_existing_race_ids(conn, df['Race_ID'].tolist())
                
                if existing_races and not force:
                    result["status"] = "skipped"
                    result["duplicates_skipped"] = len(existing_races)
                    result["errors"].append(
                        f"Found {len(existing_races)} existing races - use --force to override"
                    )
                    return result
                
                # Filter out duplicates
                if existing_races:
                    original_count = len(df)
                    df = df[~df['Race_ID'].isin(existing_races)]
                    result["duplicates_skipped"] = original_count - len(df)
                
                if df.empty:
                    result["status"] = "completed"
                    result["errors"].append("All races already exist in database")
                    return result
                
                # Upload new races
                uploaded = self._upload_races(conn, df)
                result["races_processed"] = uploaded
                result["status"] = "completed"
                
        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(str(e))
            self.logger.error(f"Upload failed: {e}")
        
        return result
    
    def _get_existing_race_ids(self, conn, race_ids: List[int]) -> List[int]:
        """Get list of race IDs that already exist in database"""
        with conn.cursor() as cur:
            cur.execute(
                "SELECT race_id FROM races WHERE race_id = ANY(%s)",
                (race_ids,)
            )
            return [row[0] for row in cur.fetchall()]
    
    def _upload_races(self, conn, df: pd.DataFrame) -> int:
        """Upload race data to database"""
        with conn.cursor() as cur:
            # Convert DataFrame to tuples for upload
            race_data = [
                (
                    row['Race_ID'],
                    row.get('race_number'),
                    row.get('race_time'),
                    row.get('course_id'),
                    row.get('Course'),
                    row.get('Race_type'),
                    row.get('Date'),
                    row.get('Race_name'),
                    row.get('Class'),
                    row.get('Years'),
                    row.get('Distance'),
                    row.get('Surface'),
                    row.get('Prize'),
                    row.get('Runners_racecard'),
                    row.get('Runners'),
                    row.get('Draw'),
                    row.get('EW_racecard'),
                    row.get('EW'),
                    row.get('Places_EW_racecard'),
                    row.get('Places_EW')
                )
                for _, row in df.iterrows()
            ]
            
            # Insert races
            execute_values(
                cur,
                """
                INSERT INTO races (
                    race_id, race_number, race_time, course_id, course, race_type,
                    date, race_name, class, years, distance, surface, prize,
                    runners_racecard, runners, draw, ew_racecard, ew,
                    places_ew_racecard, places_ew
                ) VALUES %s
                ON CONFLICT (race_id) DO NOTHING
                """,
                race_data
            )
            
            conn.commit()
            return len(race_data)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart race card uploader")
    parser.add_argument("--force", action="store_true", help="Force upload even if duplicates exist")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    uploader = SmartRaceUploader()
    result = uploader.upload_race_cards(force=args.force)
    
    print(f"Upload Status: {result['status']}")
    print(f"Races Processed: {result['races_processed']}")
    print(f"Duplicates Skipped: {result['duplicates_skipped']}")
    
    if result['errors']:
        print("Errors:")
        for error in result['errors']:
            print(f"  - {error}")
    
    return 0 if result['status'] in ['completed', 'skipped'] else 1

if __name__ == "__main__":
    sys.exit(main())
'''

        with open(script_path, "w") as f:
            f.write(script_content)

        # Make executable
        script_path.chmod(0o755)

        logger.info(f"Smart uploader created: {script_path}")
        return script_path

    def run_diagnostic_report(self) -> None:
        """Generate comprehensive diagnostic report"""
        print("\n" + "=" * 60)
        print("🔍 RACE CARD VALIDATION DIAGNOSTIC REPORT")
        print("=" * 60)

        # Analyze current situation
        analysis = self.analyze_race_overlap_issue()

        print(f"Analysis Time: {analysis['analysis_time']}")
        print(f"Issue Detected: {'❌ YES' if analysis['issue_detected'] else '✅ NO'}")

        if analysis["issue_detected"]:
            print(f"Issue Type: {analysis['overlap_type'].upper()}")

        # Print race data summary
        if "race_data" in analysis:
            rd = analysis["race_data"]
            if "results" in rd and "cards" in rd:
                print(f"\n📊 RACE DATA SUMMARY:")
                print(
                    f"  Results: {rd['results']['race_count']} races, IDs {min(rd['results']['race_ids']) if rd['results']['race_ids'] else 'N/A'}-{max(rd['results']['race_ids']) if rd['results']['race_ids'] else 'N/A'}"
                )
                print(
                    f"  Cards:   {rd['cards']['race_count']} races, IDs {min(rd['cards']['race_ids']) if rd['cards']['race_ids'] else 'N/A'}-{max(rd['cards']['race_ids']) if rd['cards']['race_ids'] else 'N/A'}"
                )

                if rd["results"]["race_ids"] and rd["cards"]["race_ids"]:
                    overlap = rd["results"]["race_ids"].intersection(
                        rd["cards"]["race_ids"]
                    )
                    print(
                        f"  Overlap: {len(overlap)} races ({len(overlap)/max(len(rd['results']['race_ids']), len(rd['cards']['race_ids'])):.1%})"
                    )

                print(
                    f"  Dates:   Results={rd['results']['date_range']}, Cards={rd['cards']['date_range']}"
                )

            if "database" in rd:
                db = rd["database"]
                print(f"\n🗄️ DATABASE STATUS:")
                print(
                    f"  Connection: {'✅ OK' if db['connection_ok'] else '❌ FAILED'}"
                )
                print(f"  Existing Races: {db['existing_race_count']}")
                if db["existing_race_ids"]:
                    print(
                        f"  Existing IDs: {db['existing_race_ids'][:5]}{'...' if len(db['existing_race_ids']) > 5 else ''}"
                    )

        # Print recommendations
        if analysis["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(analysis["recommendations"], 1):
                print(f"  {i}. {rec}")

        print("\n" + "=" * 60)


def main():
    """Main diagnostic and fix function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Race card validation diagnostic and fix tool"
    )
    parser.add_argument(
        "--fix-validator", action="store_true", help="Fix validation logic"
    )
    parser.add_argument(
        "--create-uploader", action="store_true", help="Create smart uploader"
    )
    parser.add_argument(
        "--report-only", action="store_true", help="Only generate diagnostic report"
    )

    args = parser.parse_args()

    fixer = RaceCardValidationFixer()

    # Always run diagnostic report
    fixer.run_diagnostic_report()

    if not args.report_only:
        if args.fix_validator:
            success = fixer.fix_validation_logic()
            print(f"\n🔧 Validation fix: {'✅ SUCCESS' if success else '❌ FAILED'}")

        if args.create_uploader:
            script_path = fixer.create_smart_upload_script()
            print(f"\n📝 Smart uploader created: {script_path}")

        if not args.fix_validator and not args.create_uploader:
            # Default action: fix everything
            print(f"\n🔧 Applying all fixes...")

            validator_fixed = fixer.fix_validation_logic()
            uploader_created = fixer.create_smart_upload_script()

            print(f"Validation fix: {'✅ SUCCESS' if validator_fixed else '❌ FAILED'}")
            print(
                f"Smart uploader: {'✅ CREATED' if uploader_created else '❌ FAILED'}"
            )


if __name__ == "__main__":
    main()
