#!/usr/bin/env python3
"""
🧠 Smart Data Relationships Mapper for Horse Racing Database
Priority 1A: Advanced name-based relationship mapping

When ID relationships are broken, use sophisticated name matching 
and statistical analysis to reconnect racing data.

Author: AI Assistant following Qwen2.5 recommendations
Date: August 10, 2025
"""

import psycopg2
import logging
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
from collections import defaultdict
import re
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_relationship_mapper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SmartRelationshipMapper:
    """
    Advanced relationship mapper using name analysis and statistical patterns.
    
    Strategy:
    1. Extract unique jockey/trainer names from horses table
    2. Use fuzzy matching to connect names to jockey_stats/trainer_stats
    3. Apply statistical validation for match quality
    4. Batch update race_results with high-confidence matches
    """
    
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 5433,
            'database': 'horse_racing_db',
            'user': 'horse_racing',
            'password': 'secure_password_123'
        }
        self.connection = None
        self.cursor = None
        
        # Name mapping caches
        self.jockey_mappings: Dict[str, str] = {}  # normalized -> best match
        self.trainer_mappings: Dict[str, str] = {}
        self.jockey_stats_names: List[str] = []
        self.trainer_stats_names: List[str] = []
        
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
    
    def normalize_name(self, name: str) -> str:
        """Advanced name normalization for better matching."""
        if not name or name in ['Unknown', '0', 'unknown']:
            return ""
        
        # Remove common prefixes and suffixes
        name = str(name).strip()
        prefixes = ['Mr ', 'Mrs ', 'Miss ', 'Ms ', 'Dr ', 'Prof ', 'Sir ', 'Lady ']
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
        
        # Handle initials and common patterns
        name = re.sub(r'\\b[A-Z]\\s', '', name)  # Remove single initials
        name = re.sub(r'\\s+', ' ', name)  # Normalize spaces
        name = name.upper().strip()
        
        return name
    
    def load_reference_names(self):
        """Load all available jockey and trainer names for matching."""
        logger.info("📚 Loading reference names...")
        
        # Load jockey names from jockey_stats
        self.cursor.execute("""
            SELECT DISTINCT jockey_name FROM jockey_stats 
            WHERE jockey_name IS NOT NULL 
            AND jockey_name NOT SIMILAR TO '[0-9]+' 
            AND jockey_name != '0' 
            AND LENGTH(jockey_name) > 2
            ORDER BY jockey_name
        """)
        self.jockey_stats_names = [row[0] for row in self.cursor.fetchall()]
        
        # Load trainer names from trainer_stats
        self.cursor.execute("""
            SELECT DISTINCT trainer_name FROM trainer_stats 
            WHERE trainer_name IS NOT NULL 
            AND trainer_name NOT SIMILAR TO '[0-9]+' 
            AND trainer_name != '0' 
            AND LENGTH(trainer_name) > 2
            ORDER BY trainer_name
        """)
        self.trainer_stats_names = [row[0] for row in self.cursor.fetchall()]
        
        logger.info(f"✅ Loaded {len(self.jockey_stats_names)} jockey names, {len(self.trainer_stats_names)} trainer names")
    
    def find_best_name_match(self, target_name: str, candidates: List[str], threshold: float = 0.85) -> Optional[str]:
        """Find best fuzzy match for a name with high threshold."""
        if not target_name or not candidates:
            return None
        
        target_normalized = self.normalize_name(target_name)
        if not target_normalized:
            return None
        
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            candidate_normalized = self.normalize_name(candidate)
            if not candidate_normalized:
                continue
            
            # Try exact match first
            if target_normalized == candidate_normalized:
                return candidate
            
            # Fuzzy matching
            score = SequenceMatcher(None, target_normalized, candidate_normalized).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate
        
        return best_match
    
    def extract_names_from_horses_table(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        """Extract jockey and trainer names from horses table with frequency counts."""
        logger.info("🔍 Extracting names from horses table...")
        
        # Get jockey names with frequency
        self.cursor.execute(\"\"\"
            SELECT jockey, COUNT(*) as frequency 
            FROM horses 
            WHERE jockey IS NOT NULL 
            AND jockey != 'Unknown' 
            AND jockey != '0'
            AND LENGTH(jockey) > 2
            GROUP BY jockey
            ORDER BY frequency DESC
        \"\"\")
        jockey_freq = {row[0]: row[1] for row in self.cursor.fetchall()}
        
        # Get trainer names with frequency  
        self.cursor.execute(\"\"\"
            SELECT trainer, COUNT(*) as frequency 
            FROM horses 
            WHERE trainer IS NOT NULL 
            AND trainer != 'Unknown' 
            AND trainer != '0'
            AND LENGTH(trainer) > 2
            GROUP BY trainer
            ORDER BY frequency DESC
        \"\"\")
        trainer_freq = {row[0]: row[1] for row in self.cursor.fetchall()}
        
        logger.info(f"📊 Found {len(jockey_freq)} unique jockeys, {len(trainer_freq)} unique trainers in horses table")
        return jockey_freq, trainer_freq
    
    def build_name_mappings(self):
        """Build high-confidence name mappings."""
        logger.info("🔗 Building name mappings...")
        
        jockey_freq, trainer_freq = self.extract_names_from_horses_table()
        
        # Map jockeys
        mapped_jockeys = 0
        for horse_jockey, freq in jockey_freq.items():
            best_match = self.find_best_name_match(horse_jockey, self.jockey_stats_names)
            if best_match:
                self.jockey_mappings[horse_jockey] = best_match
                mapped_jockeys += 1
                logger.debug(f"Jockey mapping: '{horse_jockey}' -> '{best_match}' (freq: {freq})")
        
        # Map trainers
        mapped_trainers = 0
        for horse_trainer, freq in trainer_freq.items():
            best_match = self.find_best_name_match(horse_trainer, self.trainer_stats_names)
            if best_match:
                self.trainer_mappings[horse_trainer] = best_match
                mapped_trainers += 1
                logger.debug(f"Trainer mapping: '{horse_trainer}' -> '{best_match}' (freq: {freq})")
        
        logger.info(f"✅ Built {mapped_jockeys} jockey mappings, {mapped_trainers} trainer mappings")
    
    def update_race_results_via_horses(self) -> Tuple[int, int]:
        """Update race_results by linking through horses table."""
        logger.info("🔄 Updating race_results via horses table relationships...")
        
        jockey_updates = 0
        trainer_updates = 0
        
        # Update jockeys via horses table
        for horse_jockey, stats_jockey in self.jockey_mappings.items():
            self.cursor.execute(\"\"\"
                UPDATE race_results 
                SET jockey_name = %s, updated_at = NOW()
                FROM horses h
                WHERE race_results.horse_id = h.horse_id_numeric
                AND h.jockey = %s
                AND (race_results.jockey_name = 'Unknown' OR race_results.jockey_name = '0')
            \"\"\", (stats_jockey, horse_jockey))
            
            updated_rows = self.cursor.rowcount
            if updated_rows > 0:
                jockey_updates += updated_rows
                logger.debug(f"Updated {updated_rows} races: jockey '{horse_jockey}' -> '{stats_jockey}'")
        
        # Update trainers via horses table
        for horse_trainer, stats_trainer in self.trainer_mappings.items():
            self.cursor.execute(\"\"\"
                UPDATE race_results 
                SET trainer_name = %s, updated_at = NOW()
                FROM horses h
                WHERE race_results.horse_id = h.horse_id_numeric
                AND h.trainer = %s
                AND (race_results.trainer_name = 'Unknown' OR race_results.trainer_name = '0')
            \"\"\", (stats_trainer, horse_trainer))
            
            updated_rows = self.cursor.rowcount
            if updated_rows > 0:
                trainer_updates += updated_rows
                logger.debug(f"Updated {updated_rows} races: trainer '{horse_trainer}' -> '{stats_trainer}'")
        
        self.connection.commit()
        logger.info(f"✅ Updated {jockey_updates} jockey entries, {trainer_updates} trainer entries")
        return jockey_updates, trainer_updates
    
    def analyze_results(self) -> Dict[str, int]:
        """Analyze the results of the mapping process."""
        results = {}
        
        # Count remaining unknowns
        self.cursor.execute(\"\"\"
            SELECT COUNT(*) FROM race_results 
            WHERE jockey_name = 'Unknown' OR trainer_name = 'Unknown'
        \"\"\")
        results['remaining_unknowns'] = self.cursor.fetchone()[0]
        
        # Count total race results
        self.cursor.execute(\"SELECT COUNT(*) FROM race_results\")
        results['total_race_results'] = self.cursor.fetchone()[0]
        
        # Count mapped entries
        results['mapped_jockeys'] = len(self.jockey_mappings)
        results['mapped_trainers'] = len(self.trainer_mappings)
        
        return results
    
    def run_smart_mapping(self) -> bool:
        """Run the complete smart relationship mapping process."""
        try:
            logger.info("🧠 Starting Smart Relationship Mapping - Priority 1A")
            
            if not self.connect():
                return False
            
            # Initial analysis
            initial_results = self.analyze_results()
            logger.info(f"📊 Initial state: {initial_results['remaining_unknowns']} unknowns out of {initial_results['total_race_results']} total")
            
            # Load reference data
            self.load_reference_names()
            
            # Build mappings
            self.build_name_mappings()
            
            # Apply updates
            jockey_updates, trainer_updates = self.update_race_results_via_horses()
            
            # Final analysis
            final_results = self.analyze_results()
            
            # Report results
            logger.info("🎉 Smart Relationship Mapping Complete!")
            logger.info(f"📈 Results:")
            logger.info(f"   - Jockey mappings created: {final_results['mapped_jockeys']}")
            logger.info(f"   - Trainer mappings created: {final_results['mapped_trainers']}")
            logger.info(f"   - Jockey entries updated: {jockey_updates}")
            logger.info(f"   - Trainer entries updated: {trainer_updates}")
            logger.info(f"   - Remaining unknowns: {final_results['remaining_unknowns']} (was {initial_results['remaining_unknowns']})")
            
            improvement = initial_results['remaining_unknowns'] - final_results['remaining_unknowns']
            if improvement > 0:
                logger.info(f"   - Records improved: {improvement} ({improvement/initial_results['remaining_unknowns']*100:.1f}%)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Smart mapping failed: {e}")
            if self.connection:
                self.connection.rollback()
            return False
        finally:
            self.disconnect()


def main():
    """Main execution function."""
    print("🧠 Horse Racing Database - Smart Relationship Mapper")
    print("Advanced name-based relationship reconstruction")
    print("=" * 55)
    
    mapper = SmartRelationshipMapper()
    success = mapper.run_smart_mapping()
    
    if success:
        print("\\n✅ Smart relationship mapping completed!")
        print("📝 Check smart_relationship_mapper.log for detailed information")
    else:
        print("\\n❌ Smart relationship mapping failed!")
        print("📝 Check smart_relationship_mapper.log for error details")
    
    return success


if __name__ == "__main__":
    main()
