#!/usr/bin/env python3
"""
Simple Form Analyzer for Pipeline
Analyzes horse form using database data without external AI models
"""

import argparse
import sys
from datetime import datetime, timedelta

import psycopg2


class SimpleFormAnalyzer:
    """Database-based form analyzer for pipeline integration."""
    
    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "port": 5433,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }
    
    def analyze_all(self):
        """Analyze all horses in the database."""
        print("🐎 SIMPLE FORM ANALYZER - PIPELINE INTEGRATION")
        print("=" * 60)
        
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    # Get all horses with recent data
                    cur.execute("""
                        SELECT 
                            horse_name,
                            COUNT(*) as race_count,
                            AVG(finished_position::numeric) as avg_position,
                            MIN(race_date) as first_race,
                            MAX(race_date) as last_race
                        FROM race_results 
                        WHERE horse_name IS NOT NULL 
                        AND race_date >= CURRENT_DATE - INTERVAL '30 days'
                        GROUP BY horse_name
                        ORDER BY race_count DESC, avg_position ASC
                        LIMIT 10
                    """)
                    
                    horses = cur.fetchall()
                    
                    print(f"📊 ANALYZING {len(horses)} HORSES WITH RECENT FORM")
                    print("-" * 60)
                    
                    for i, (name, count, avg_pos, first, last) in enumerate(horses, 1):
                        form_score = self.calculate_form_score(avg_pos, count)
                        print(f"{i:2d}. {name[:25]:<25} | Races: {count:2d} | Avg Pos: {avg_pos:.1f} | Score: {form_score:.1f}")
                    
                    # Get total statistics
                    cur.execute("""
                        SELECT 
                            COUNT(DISTINCT horse_name) as unique_horses,
                            COUNT(*) as total_races,
                            AVG(finished_position::numeric) as avg_all_positions
                        FROM race_results 
                        WHERE horse_name IS NOT NULL 
                        AND race_date >= CURRENT_DATE - INTERVAL '30 days'
                    """)
                    
                    stats = cur.fetchone()
                    unique_horses, total_races, avg_all = stats
                    
                    print("\n📈 FORM ANALYSIS SUMMARY")
                    print("-" * 60)
                    print(f"✅ Unique horses analyzed: {unique_horses}")
                    print(f"✅ Total races processed: {total_races}")
                    print(f"✅ Average finishing position: {avg_all:.2f}")
                    print(f"✅ Form scores generated: {len(horses)}")
                    
                    return True
                    
        except Exception as e:
            print(f"❌ Form analysis failed: {e}")
            return False
    
    def calculate_form_score(self, avg_position, race_count):
        """Calculate a simple form score based on average position and experience."""
        if avg_position is None:
            return 0.0
        
        # Convert to float if it's a Decimal
        avg_pos = float(avg_position)
        
        # Base score: lower average position = higher score
        base_score = max(0, 10 - avg_pos)
        
        # Experience bonus: more races = slight bonus (up to 2 points)
        experience_bonus = min(2.0, race_count * 0.1)
        
        return base_score + experience_bonus


def main():
    parser = argparse.ArgumentParser(description="Simple Form Analyzer")
    parser.add_argument("--analyze-all", action="store_true", help="Analyze all horses")
    
    args = parser.parse_args()
    
    analyzer = SimpleFormAnalyzer()
    
    if args.analyze_all:
        success = analyzer.analyze_all()
        return 0 if success else 1
    else:
        print("Usage: python simple_form_analyzer.py --analyze-all")
        return 1


if __name__ == "__main__":
    sys.exit(main())
