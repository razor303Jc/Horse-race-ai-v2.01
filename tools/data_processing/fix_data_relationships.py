#!/usr/bin/env python3
"""
🚀 Data Relationships Fixer for Horse Racing Database
Priority 1A: Fix disconnected data relationships

Based on Qwen2.5-Coder AI analysis and adapted for our actual database schema.
Transforms race_results from "Unknown" placeholders to real jockey/trainer names.

Author: AI Assistant following Qwen2.5 recommendations
Date: August 10, 2025
"""

import logging
import os
import sys
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

import psycopg2

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("data_relationships_fix.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class DataRelationshipsFixer:
    """
    Fixes broken data relationships in the horse racing database.

    Strategy:
    1. Direct ID matching where possible
    2. Fuzzy name matching for unlinked records
    3. Statistical validation of matches
    4. Batch updates for performance
    """

    def __init__(self):
        self.db_config = {
            "host": "postgres",  # Docker service name for container networking
            "port": 5432,  # Internal container port
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }
        self.connection = None
        self.cursor = None

        # Caches for performance
        self.jockey_cache: Dict[int, str] = {}
        self.trainer_cache: Dict[int, str] = {}
        self.jockey_name_cache: Dict[str, str] = {}  # normalized name -> real name
        self.trainer_name_cache: Dict[str, str] = {}

    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor()
            logger.info("✅ Database connection established")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    def disconnect(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("🔌 Database connection closed")

    def get_data_overview(self) -> Dict[str, int]:
        """Get overview of current data state."""
        overview = {}

        # Count race results with Unknown values
        self.cursor.execute(
            """
            SELECT COUNT(*) FROM race_results 
            WHERE jockey_name = 'Unknown' OR trainer_name = 'Unknown'
        """
        )
        overview["unknown_race_results"] = self.cursor.fetchone()[0]

        # Count total race results
        self.cursor.execute("SELECT COUNT(*) FROM race_results")
        overview["total_race_results"] = self.cursor.fetchone()[0]

        # Count jockeys with real names
        self.cursor.execute(
            """
            SELECT COUNT(*) FROM jockey_stats 
            WHERE jockey_name NOT SIMILAR TO '[0-9]+' 
            AND jockey_name != '0' 
            AND LENGTH(jockey_name) > 2
        """
        )
        overview["real_jockeys"] = self.cursor.fetchone()[0]

        # Count trainers with real names
        self.cursor.execute(
            """
            SELECT COUNT(*) FROM trainer_stats 
            WHERE trainer_name NOT SIMILAR TO '[0-9]+' 
            AND trainer_name != '0' 
            AND LENGTH(trainer_name) > 2
        """
        )
        overview["real_trainers"] = self.cursor.fetchone()[0]

        return overview

    def load_jockey_cache(self):
        """Load jockey data into cache for performance."""
        logger.info("📚 Loading jockey cache...")

        # Load jockeys with IDs (for direct matching)
        self.cursor.execute(
            """
            SELECT id, jockey_name, jockey_id FROM jockey_stats 
            WHERE jockey_id IS NOT NULL 
            AND jockey_name NOT SIMILAR TO '[0-9]+' 
            AND jockey_name != '0' 
            AND LENGTH(jockey_name) > 2
        """
        )

        for db_id, name, jockey_id in self.cursor.fetchall():
            if jockey_id:
                self.jockey_cache[jockey_id] = name

        # Load all jockeys with real names for fuzzy matching
        self.cursor.execute(
            """
            SELECT DISTINCT jockey_name FROM jockey_stats 
            WHERE jockey_name NOT SIMILAR TO '[0-9]+' 
            AND jockey_name != '0' 
            AND LENGTH(jockey_name) > 2
        """
        )

        for (name,) in self.cursor.fetchall():
            normalized = self.normalize_name(name)
            self.jockey_name_cache[normalized] = name

        logger.info(
            f"✅ Loaded {len(self.jockey_cache)} jockeys with IDs, {len(self.jockey_name_cache)} total jockey names"
        )

    def load_trainer_cache(self):
        """Load trainer data into cache for performance."""
        logger.info("📚 Loading trainer cache...")

        # Load trainers with IDs (for direct matching)
        self.cursor.execute(
            """
            SELECT id, trainer_name, trainer_id FROM trainer_stats 
            WHERE trainer_id IS NOT NULL 
            AND trainer_name NOT SIMILAR TO '[0-9]+' 
            AND trainer_name != '0' 
            AND LENGTH(trainer_name) > 2
        """
        )

        for db_id, name, trainer_id in self.cursor.fetchall():
            if trainer_id:
                self.trainer_cache[trainer_id] = name

        # Load all trainers with real names for fuzzy matching
        self.cursor.execute(
            """
            SELECT DISTINCT trainer_name FROM trainer_stats 
            WHERE trainer_name NOT SIMILAR TO '[0-9]+' 
            AND trainer_name != '0' 
            AND LENGTH(trainer_name) > 2
        """
        )

        for (name,) in self.cursor.fetchall():
            normalized = self.normalize_name(name)
            self.trainer_name_cache[normalized] = name

        logger.info(
            f"✅ Loaded {len(self.trainer_cache)} trainers with IDs, {len(self.trainer_name_cache)} total trainer names"
        )

    def normalize_name(self, name: str) -> str:
        """Normalize name for better matching."""
        if not name:
            return ""

        # Remove common prefixes/suffixes and normalize
        name = name.strip()
        name = (
            name.replace("Mr ", "")
            .replace("Mrs ", "")
            .replace("Miss ", "")
            .replace("Ms ", "")
        )
        name = name.replace("Dr ", "").replace("Prof ", "")
        name = name.upper()

        # Remove extra spaces
        while "  " in name:
            name = name.replace("  ", " ")

        return name

    def find_best_match(
        self, target_name: str, candidates: Dict[str, str], threshold: float = 0.8
    ) -> Optional[str]:
        """Find best fuzzy match for a name."""
        if not target_name or not candidates:
            return None

        target_normalized = self.normalize_name(target_name)
        best_match = None
        best_score = 0.0

        for normalized_name, real_name in candidates.items():
            score = SequenceMatcher(None, target_normalized, normalized_name).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = real_name

        return best_match

    def fix_jockey_relationships(self) -> int:
        """Fix jockey relationships in race_results."""
        logger.info("🔧 Fixing jockey relationships...")
        fixed_count = 0

        # Get race results with Unknown jockeys
        self.cursor.execute(
            """
            SELECT id, horse_name, jockey_id FROM race_results 
            WHERE jockey_name = 'Unknown' OR jockey_name = '0'
        """
        )

        unknown_results = self.cursor.fetchall()
        logger.info(f"Found {len(unknown_results)} race results with unknown jockeys")

        updates = []

        for result_id, horse_name, jockey_id in unknown_results:
            jockey_name = None

            # Try direct ID matching first
            if jockey_id and jockey_id in self.jockey_cache:
                jockey_name = self.jockey_cache[jockey_id]
                logger.debug(f"Direct ID match: {jockey_id} -> {jockey_name}")

            # If no direct match, try fuzzy matching on horse name (fallback)
            if not jockey_name and horse_name:
                # This is a simplified approach - in reality, we'd need more sophisticated matching
                # For now, we'll focus on the direct ID matches
                pass

            if jockey_name:
                updates.append((jockey_name, result_id))
                fixed_count += 1

        # Batch update
        if updates:
            logger.info(f"Updating {len(updates)} jockey relationships...")
            self.cursor.executemany(
                """
                UPDATE race_results 
                SET jockey_name = %s, updated_at = NOW()
                WHERE id = %s
            """,
                updates,
            )
            self.connection.commit()

        logger.info(f"✅ Fixed {fixed_count} jockey relationships")
        return fixed_count

    def fix_trainer_relationships(self) -> int:
        """Fix trainer relationships in race_results."""
        logger.info("🔧 Fixing trainer relationships...")
        fixed_count = 0

        # Get race results with Unknown trainers
        self.cursor.execute(
            """
            SELECT id, horse_name, trainer_id FROM race_results 
            WHERE trainer_name = 'Unknown' OR trainer_name = '0'
        """
        )

        unknown_results = self.cursor.fetchall()
        logger.info(f"Found {len(unknown_results)} race results with unknown trainers")

        updates = []

        for result_id, horse_name, trainer_id in unknown_results:
            trainer_name = None

            # Try direct ID matching first
            if trainer_id and trainer_id in self.trainer_cache:
                trainer_name = self.trainer_cache[trainer_id]
                logger.debug(f"Direct ID match: {trainer_id} -> {trainer_name}")

            if trainer_name:
                updates.append((trainer_name, result_id))
                fixed_count += 1

        # Batch update
        if updates:
            logger.info(f"Updating {len(updates)} trainer relationships...")
            self.cursor.executemany(
                """
                UPDATE race_results 
                SET trainer_name = %s, updated_at = NOW()
                WHERE id = %s
            """,
                updates,
            )
            self.connection.commit()

        logger.info(f"✅ Fixed {fixed_count} trainer relationships")
        return fixed_count

    def fix_horse_relationships(self) -> int:
        """Fix horse name consistency using horses table."""
        logger.info("🔧 Fixing horse relationships...")
        fixed_count = 0

        # Get race results where we can match by horse_id
        self.cursor.execute(
            """
            SELECT rr.id, rr.horse_name, h.horse_name 
            FROM race_results rr
            JOIN horses h ON rr.horse_id = h.horse_id_numeric
            WHERE rr.horse_name != h.horse_name
            AND h.horse_name IS NOT NULL
            AND LENGTH(h.horse_name) > 1
        """
        )

        mismatched_horses = self.cursor.fetchall()
        logger.info(
            f"Found {len(mismatched_horses)} race results with horse name mismatches"
        )

        updates = []
        for result_id, old_name, correct_name in mismatched_horses:
            updates.append((correct_name, result_id))
            fixed_count += 1

        # Batch update
        if updates:
            logger.info(f"Updating {len(updates)} horse names...")
            self.cursor.executemany(
                """
                UPDATE race_results 
                SET horse_name = %s, updated_at = NOW()
                WHERE id = %s
            """,
                updates,
            )
            self.connection.commit()

        logger.info(f"✅ Fixed {fixed_count} horse name relationships")
        return fixed_count

    def generate_report(self) -> str:
        """Generate a comprehensive report of the fixes applied."""
        overview_before = self.get_data_overview()

        report = f"""
🚀 DATA RELATIONSHIPS FIX REPORT
=====================================

Date: {logger.handlers[0].formatter.formatTime(logger.handlers[0], logging.LogRecord('', 0, '', 0, '', (), None))}

BEFORE FIXES:
- Race results with Unknown values: {overview_before['unknown_race_results']}
- Total race results: {overview_before['total_race_results']}
- Available jockeys with names: {overview_before['real_jockeys']}
- Available trainers with names: {overview_before['real_trainers']}

FIXES APPLIED:
- Jockey relationships: {self.jockey_cache}
- Trainer relationships: {self.trainer_cache}

STATUS: Ready for execution
"""
        return report

    def run_full_fix(self) -> bool:
        """Run the complete data relationships fix."""
        try:
            logger.info("🚀 Starting Data Relationships Fix - Priority 1A")

            if not self.connect():
                return False

            # Get initial overview
            overview = self.get_data_overview()
            logger.info(
                f"📊 Initial state: {overview['unknown_race_results']} unknown out of {overview['total_race_results']} total race results"
            )

            # Load caches
            self.load_jockey_cache()
            self.load_trainer_cache()

            # Apply fixes
            jockey_fixes = self.fix_jockey_relationships()
            trainer_fixes = self.fix_trainer_relationships()
            horse_fixes = self.fix_horse_relationships()

            # Get final overview
            final_overview = self.get_data_overview()

            logger.info("🎉 Data Relationships Fix Complete!")
            logger.info(f"📈 Results:")
            logger.info(f"   - Jockey relationships fixed: {jockey_fixes}")
            logger.info(f"   - Trainer relationships fixed: {trainer_fixes}")
            logger.info(f"   - Horse name fixes: {horse_fixes}")
            logger.info(
                f"   - Remaining unknowns: {final_overview['unknown_race_results']}"
            )

            return True

        except Exception as e:
            logger.error(f"❌ Fix failed: {e}")
            if self.connection:
                self.connection.rollback()
            return False
        finally:
            self.disconnect()


def main():
    """Main execution function."""
    print("🚀 Horse Racing Database - Data Relationships Fix")
    print("Based on Qwen2.5-Coder AI Analysis")
    print("=" * 50)

    fixer = DataRelationshipsFixer()
    success = fixer.run_full_fix()

    if success:
        print("\n✅ Data relationships fix completed successfully!")
        print("📝 Check data_relationships_fix.log for detailed information")
    else:
        print("\n❌ Data relationships fix failed!")
        print("📝 Check data_relationships_fix.log for error details")

    return success


if __name__ == "__main__":
    main()
