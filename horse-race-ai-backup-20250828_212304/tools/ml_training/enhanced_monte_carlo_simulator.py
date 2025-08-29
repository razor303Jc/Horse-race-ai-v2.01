#!/usr/bin/env python3
"""
Enhanced Monte Carlo Simulator with Database Integration
========================================================

Monte Carlo simulation system that generates race outcome probabilities
and saves simulation results to the advanced_racing_metrics_db database.

Created: August 24, 2025
"""

import os
import sys
import logging
import uuid
import json
import psycopg2
import psycopg2.extras
import numpy as np
import random
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any

# Add the project root to the path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)


class EnhancedMonteCarloSimulator:
    """Enhanced Monte Carlo simulator with database integration"""

    def __init__(self):
        """Initialize the simulator"""
        self.setup_logging()
        self.db_config = {
            "host": "postgres",
            "database": "advanced_racing_metrics_db",
            "user": "horse_racing",
            "password": "secure_password_123",
            "port": 5432,
        }
        self.cards_db_config = {
            "host": "postgres",
            "database": "cards_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
            "port": 5432,
        }

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
        self.logger = logging.getLogger(__name__)

    def get_database_connection(self, use_cards_db=False):
        """Get database connection"""
        try:
            config = self.cards_db_config if use_cards_db else self.db_config
            conn = psycopg2.connect(**config)
            conn.autocommit = True
            return conn
        except Exception as e:
            self.logger.error(f"❌ Database connection failed: {e}")
            raise

    def get_horse_analysis_data(self, target_date: str = None) -> List[Dict]:
        """Get power ratings and speed/pace data for Monte Carlo simulation"""
        if target_date is None:
            target_date = date.today().strftime('%Y-%m-%d')
            
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Get combined analysis data
            query = """
                SELECT
                    pr.horse_id,
                    pr.horse_name,
                    pr.race_id,
                    pr.final_power_rating,
                    pr.rating_confidence,
                    sp.speed_rating,
                    sp.pace_rating,
                    sp.pace_style,
                    sp.finishing_speed_index,
                    sp.pace_versatility_score
                FROM horse_power_ratings pr
                JOIN horse_speed_pace_ratings sp
                    ON pr.horse_id = sp.horse_id AND pr.race_id = sp.race_id
                WHERE pr.calculation_date = %s
                    AND sp.calculation_date = %s
                ORDER BY pr.race_id, pr.final_power_rating DESC
            """
            
            cursor.execute(query, (target_date, target_date))
            results = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get analysis data: {e}")
            return []

    def calculate_race_probability(self, horse_data: Dict) -> float:
        """Calculate win probability for a horse based on ratings"""
        
        # Get ratings
        power_rating = float(horse_data.get('final_power_rating', 100))
        speed_rating = float(horse_data.get('speed_rating', 75))
        pace_rating = float(horse_data.get('pace_rating', 75))
        finishing_speed = float(horse_data.get('finishing_speed_index', 75))
        confidence = float(horse_data.get('rating_confidence', 0.75))
        versatility = float(horse_data.get('pace_versatility_score', 0.75))
        
        # Combine ratings with weights
        combined_rating = (
            power_rating * 0.4 +      # Power rating is most important
            speed_rating * 0.25 +     # Speed is crucial
            pace_rating * 0.20 +      # Pace management
            finishing_speed * 0.15    # Finishing ability
        )
        
        # Apply confidence and versatility modifiers
        adjusted_rating = combined_rating * confidence * (0.8 + 0.4 * versatility)
        
        return adjusted_rating

    def normalize_probabilities(self, probabilities: List[float]) -> List[float]:
        """Normalize probabilities to sum to 1.0"""
        total = sum(probabilities)
        if total <= 0:
            # Equal probabilities if all are zero
            return [1.0 / len(probabilities)] * len(probabilities)
        
        return [p / total for p in probabilities]

    def run_single_simulation(self, race_horses: List[Dict]) -> Dict:
        """Run a single Monte Carlo simulation for a race"""
        
        # Calculate base probabilities
        probabilities = []
        for horse in race_horses:
            prob = self.calculate_race_probability(horse)
            probabilities.append(prob)
        
        # Normalize probabilities
        normalized_probs = self.normalize_probabilities(probabilities)
        
        # Add random variation to simulate race uncertainty
        random_factors = [random.gauss(1.0, 0.15) for _ in race_horses]
        
        # Apply random factors
        varied_probs = [p * f for p, f in zip(normalized_probs, random_factors)]
        final_probs = self.normalize_probabilities(varied_probs)
        
        # Select winner based on probabilities
        winner_index = np.random.choice(len(race_horses), p=final_probs)
        
        # Create simulation result
        simulation_result = {
            'winner_horse_id': race_horses[winner_index]['horse_id'],
            'winner_horse_name': race_horses[winner_index]['horse_name'],
            'winner_probability': final_probs[winner_index],
            'all_probabilities': final_probs,
            'horse_positions': list(range(len(race_horses)))
        }
        
        return simulation_result

    def run_monte_carlo_simulation(self, race_horses: List[Dict], 
                                 num_simulations: int = 10000) -> Dict:
        """Run Monte Carlo simulation for a race"""
        
        if not race_horses:
            return {'error': 'No horses provided'}
        
        # Track wins for each horse
        horse_wins = {horse['horse_id']: 0 for horse in race_horses}
        horse_names = {horse['horse_id']: horse['horse_name'] for horse in race_horses}
        
        # Run simulations
        simulation_results = []
        
        for i in range(num_simulations):
            result = self.run_single_simulation(race_horses)
            simulation_results.append(result)
            
            # Count win
            winner_id = result['winner_horse_id']
            horse_wins[winner_id] += 1
        
        # Calculate final probabilities
        win_probabilities = {}
        for horse_id, wins in horse_wins.items():
            win_probabilities[horse_id] = {
                'horse_name': horse_names[horse_id],
                'win_probability': wins / num_simulations,
                'wins': wins
            }
        
        # Sort by win probability
        sorted_horses = sorted(
            win_probabilities.items(), 
            key=lambda x: x[1]['win_probability'], 
            reverse=True
        )
        
        return {
            'race_id': race_horses[0]['race_id'],
            'num_simulations': num_simulations,
            'win_probabilities': win_probabilities,
            'sorted_horses': sorted_horses,
            'horse_data': race_horses,  # Include original horse data
            'simulation_metadata': {
                'total_horses': len(race_horses),
                'average_rating': np.mean([
                    h['final_power_rating'] for h in race_horses
                ]),
                'rating_std': np.std([
                    h['final_power_rating'] for h in race_horses
                ])
            }
        }

    def save_monte_carlo_results(self, simulation_results: Dict) -> bool:
        """Save Monte Carlo simulation results to database"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()
            
            race_id = simulation_results['race_id']
            num_simulations = simulation_results['num_simulations']
            
            # Generate a session ID for this race simulation
            session_id = str(uuid.uuid4())
            
            # Calculate simulation metadata
            metadata = simulation_results['simulation_metadata']
            baseline_variance = float(metadata['rating_std'])
            
            # Save individual horse results
            for horse_id, prob_data in simulation_results['win_probabilities'].items():
                horse_name = prob_data['horse_name']
                win_prob = prob_data['win_probability']
                
                # Calculate additional probabilities and statistics
                place_prob = min(0.95, win_prob * 2.5)  # Rough place probability
                show_prob = min(0.98, win_prob * 3.0)   # Rough show probability
                
                # Calculate average finish position (1-4 for typical field)
                field_size = len(simulation_results['win_probabilities'])
                avg_position = 1 + (1 - win_prob) * (field_size - 1)
                
                # Calculate confidence intervals
                ci_lower = max(0.01, win_prob - 0.15)
                ci_upper = min(0.99, win_prob + 0.15)
                
                # Simulation reliability based on number of runs
                reliability = min(0.95, num_simulations / 10000.0)
                
                insert_sql = """
                    INSERT INTO monte_carlo_simulations (
                        simulation_session_id, race_id, horse_id, horse_name,
                        simulation_date, simulations_run, baseline_variance,
                        mean_rating, win_probability, place_probability,
                        show_probability, average_position, performance_ci_lower,
                        performance_ci_upper, simulation_reliability
                    ) VALUES (
                        %s, %s, %s, %s, CURRENT_DATE, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                """
                
                # Get horse rating from original data
                horse_rating = 100.0  # Default fallback
                for horse_data in simulation_results.get('horse_data', []):
                    if horse_data.get('horse_id') == horse_id:
                        power_rating = horse_data.get('final_power_rating', 100.0)
                        horse_rating = float(power_rating)
                        break
                
                cursor.execute(insert_sql, (
                    session_id, race_id, horse_id, horse_name,
                    num_simulations, float(baseline_variance), float(horse_rating),
                    float(win_prob), float(place_prob), float(show_prob), 
                    float(avg_position), float(ci_lower), float(ci_upper), 
                    float(reliability)
                ))
            
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save Monte Carlo results: {e}")
            return False

    def process_all_races(self, target_date: str = None,
                          num_simulations: int = 10000) -> Dict:
        """Process Monte Carlo simulations for all races"""
        date_str = target_date or 'today'
        self.logger.info(f"🎲 Starting Monte Carlo simulation for {date_str}")
        
        # Get analysis data
        analysis_data = self.get_horse_analysis_data(target_date)
        
        if not analysis_data:
            self.logger.warning("⚠️ No analysis data found")
            return {'success': False, 'message': 'No analysis data found'}
        
        # Group by race
        races = {}
        for horse_data in analysis_data:
            race_id = horse_data['race_id']
            if race_id not in races:
                races[race_id] = []
            races[race_id].append(horse_data)
        
        total_races = len(races)
        successful_simulations = 0
        
        simulation_summaries = []
        
        for race_id, race_horses in races.items():
            try:
                self.logger.info(f"🏁 Running simulation for race {race_id} "
                               f"({len(race_horses)} horses)")
                
                # Run Monte Carlo simulation
                simulation_result = self.run_monte_carlo_simulation(
                    race_horses, num_simulations
                )
                
                # Save results
                if self.save_monte_carlo_results(simulation_result):
                    successful_simulations += 1
                    
                    # Log top 3 horses
                    top_3 = simulation_result['sorted_horses'][:3]
                    self.logger.info(f"✅ Race {race_id} simulation complete:")
                    for i, (horse_id, data) in enumerate(top_3, 1):
                        prob_pct = data['win_probability'] * 100
                        self.logger.info(f"   {i}. {data['horse_name']}: {prob_pct:.1f}%")
                    
                    simulation_summaries.append({
                        'race_id': race_id,
                        'top_horse': top_3[0][1]['horse_name'],
                        'top_probability': top_3[0][1]['win_probability'],
                        'horses_count': len(race_horses)
                    })
                else:
                    self.logger.error(f"❌ Failed to save simulation for race {race_id}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error simulating race {race_id}: {e}")
        
        success_rate = (successful_simulations / total_races * 100) if total_races > 0 else 0
        
        result = {
            'success': True,
            'total_races': total_races,
            'successful_simulations': successful_simulations,
            'success_rate': success_rate,
            'num_simulations': num_simulations,
            'simulation_summaries': simulation_summaries
        }
        
        self.logger.info(f"🎯 Monte Carlo simulation complete:")
        self.logger.info(f"   🏁 Total races: {total_races}")
        self.logger.info(f"   ✅ Successful simulations: {successful_simulations}")
        self.logger.info(f"   📈 Success rate: {success_rate:.1f}%")
        self.logger.info(f"   🎲 Simulations per race: {num_simulations:,}")
        
        return result

    def get_simulation_summary(self, race_id: int = None) -> List[Dict]:
        """Get Monte Carlo simulation summary"""
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            if race_id:
                query = """
                    SELECT race_id, horse_name, win_probability, place_probability,
                           show_probability, average_position, simulation_reliability,
                           simulations_run, created_at
                    FROM monte_carlo_simulations
                    WHERE race_id = %s
                    ORDER BY win_probability DESC
                """
                cursor.execute(query, (race_id,))
            else:
                # Get top horses from each race
                query = """
                    SELECT DISTINCT ON (race_id) 
                           race_id, horse_name, win_probability, place_probability,
                           show_probability, simulations_run, created_at
                    FROM monte_carlo_simulations
                    WHERE simulation_date = CURRENT_DATE
                    ORDER BY race_id, win_probability DESC
                """
                cursor.execute(query)
            
            results = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get simulation summary: {e}")
            return []


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Monte Carlo Simulator')
    parser.add_argument('--date', type=str, help='Target date (YYYY-MM-DD)', 
                       default=date.today().strftime('%Y-%m-%d'))
    parser.add_argument('--race-id', type=int, help='Specific race ID to simulate')
    parser.add_argument('--simulations', type=int, default=10000,
                       help='Number of simulations per race (default: 10000)')
    parser.add_argument('--summary', action='store_true', 
                       help='Show simulation summary')
    
    args = parser.parse_args()
    
    simulator = EnhancedMonteCarloSimulator()
    
    if args.summary:
        print("\\n🎲 MONTE CARLO SIMULATION SUMMARY")
        print("=" * 50)
        simulations = simulator.get_simulation_summary(args.race_id)
        
        if args.race_id:
            # Show all horses for specific race
            print(f"🏁 Race {args.race_id} Results:")
            for i, sim in enumerate(simulations, 1):
                prob_pct = sim['win_probability'] * 100
                place_pct = sim['place_probability'] * 100
                print(f"{i}. {sim['horse_name']}")
                print(f"   � Win: {prob_pct:.1f}%")
                print(f"   🥈 Place: {place_pct:.1f}%")
                print(f"   📊 Avg Position: {sim['average_position']:.1f}")
                print(f"   🎲 Simulations: {sim['simulations_run']:,}")
                print()
        else:
            # Show top horse from each race
            print("🏆 Top Predictions by Race:")
            for sim in simulations:
                prob_pct = sim['win_probability'] * 100
                print(f"Race {sim['race_id']}: {sim['horse_name']} ({prob_pct:.1f}%)")
                print(f"   🎲 Simulations: {sim['simulations_run']:,}")
                print(f"   📅 Run: {sim['created_at']}")
                print()
    else:
        result = simulator.process_all_races(args.date, args.simulations)
        
        if result['success']:
            print("\\n✅ MONTE CARLO SIMULATION COMPLETE!")
            print(f"🏁 Processed {result['total_races']} races")
            print(f"✅ Completed {result['successful_simulations']} simulations")
            print(f"📈 Success rate: {result['success_rate']:.1f}%")
            print(f"🎲 {result['num_simulations']:,} simulations per race")
            
            if result['simulation_summaries']:
                print("\\n🏆 TOP RACE PREDICTIONS:")
                for summary in result['simulation_summaries'][:5]:
                    prob_pct = summary['top_probability'] * 100
                    print(f"   Race {summary['race_id']}: "
                          f"{summary['top_horse']} ({prob_pct:.1f}%)")
        else:
            print(f"❌ {result['message']}")


if __name__ == "__main__":
    main()
