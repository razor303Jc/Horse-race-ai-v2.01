#!/usr/bin/env python3
"""
Intensive Testing Framework for Enhanced Form Scorer V3.1
=========================================================

This framework provides comprehensive testing capabilities for the Enhanced Form Scorer,
designed for large-scale validation and continuous optimization based on real race data.

Features:
- Scalable testing (50 to 10,000+ races)
- Detailed performance analytics
- Weight optimization recommendations
- Comprehensive reporting with statistics
- Performance tracking across different race types
"""

import asyncio
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import statistics
import json
from pathlib import Path

# Import our enhanced form scorer
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enhanced_form_scorer_v3_1_optimized import EnhancedFormScorerV3, DecimalScores

@dataclass
class TestingConfiguration:
    """Configuration for testing runs"""
    num_races: int = 100
    min_runners: int = 4
    max_runners: int = 20
    include_race_types: List[str] = None
    date_range: Tuple[str, str] = None
    output_file: str = None
    detailed_reporting: bool = True
    
    def __post_init__(self):
        if self.include_race_types is None:
            self.include_race_types = ['Flat', 'National Hunt']
        if self.output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_file = f"intensive_test_results_{timestamp}.json"

@dataclass
class RaceResult:
    """Result data for a single race"""
    race_id: int
    race_date: str
    course: str
    distance: int
    race_type: str
    num_runners: int
    winner_name: str
    winner_position: int
    top_rated_horse: str
    top_rated_position: int
    top_rated_score: float
    winner_score: float
    top_3_horses: List[str]
    winner_in_top_3: bool
    score_distribution: Dict[str, float]

@dataclass
class TestingReport:
    """Comprehensive testing report"""
    config: TestingConfiguration
    start_time: str
    end_time: str
    total_races: int
    total_horses: int
    
    # Performance Metrics
    top_rated_win_rate: float
    winner_in_top_3_rate: float
    average_winner_score: float
    average_top_rated_score: float
    score_accuracy: float
    
    # Distribution Analysis
    score_distribution_stats: Dict[str, float]
    position_accuracy: Dict[int, float]
    race_type_performance: Dict[str, Dict[str, float]]
    
    # Recommendations
    weight_recommendations: Dict[str, float]
    threshold_recommendations: Dict[str, float]
    
    # Detailed Results
    race_results: List[RaceResult]

class IntensiveTestingFramework:
    """
    Comprehensive testing framework for the Enhanced Form Scorer V3.1
    """
    
    def __init__(self, db_path: str = "horse_racing.db"):
        self.db_path = db_path
        self.scorer = EnhancedFormScorerV3()
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the testing framework"""
        logger = logging.getLogger("IntensiveTesting")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total races
            cursor.execute("SELECT COUNT(*) FROM races")
            total_races = cursor.fetchone()[0]
            
            # Date range
            cursor.execute("SELECT MIN(race_date), MAX(race_date) FROM races")
            min_date, max_date = cursor.fetchone()
            
            # Race types
            cursor.execute("""
                SELECT race_type, COUNT(*) 
                FROM races 
                GROUP BY race_type 
                ORDER BY COUNT(*) DESC
            """)
            race_types = dict(cursor.fetchall())
            
            # Average runners per race
            cursor.execute("""
                SELECT AVG(runner_count) 
                FROM (
                    SELECT COUNT(*) as runner_count 
                    FROM race_results 
                    GROUP BY race_id
                )
            """)
            avg_runners = cursor.fetchone()[0]
            
        return {
            "total_races": total_races,
            "date_range": (min_date, max_date),
            "race_types": race_types,
            "average_runners_per_race": round(avg_runners, 1)
        }
    
    def select_test_races(self, config: TestingConfiguration) -> List[int]:
        """Select races for testing based on configuration"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build query conditions
            conditions = []
            params = []
            
            # Race type filter
            if config.include_race_types:
                placeholders = ','.join('?' for _ in config.include_race_types)
                conditions.append(f"r.race_type IN ({placeholders})")
                params.extend(config.include_race_types)
            
            # Date range filter
            if config.date_range:
                conditions.append("r.race_date BETWEEN ? AND ?")
                params.extend(config.date_range)
            
            # Runner count filter
            conditions.append("""
                r.race_id IN (
                    SELECT race_id 
                    FROM race_results 
                    GROUP BY race_id 
                    HAVING COUNT(*) BETWEEN ? AND ?
                )
            """)
            params.extend([config.min_runners, config.max_runners])
            
            # Build final query
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT r.race_id
                FROM races r
                WHERE {where_clause}
                ORDER BY RANDOM()
                LIMIT ?
            """
            params.append(config.num_races)
            
            cursor.execute(query, params)
            race_ids = [row[0] for row in cursor.fetchall()]
            
        self.logger.info(f"Selected {len(race_ids)} races for testing")
        return race_ids
    
    async def analyze_race(self, race_id: int) -> Optional[RaceResult]:
        """Analyze a single race and return results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get race info
                cursor.execute("""
                    SELECT race_date, course, distance, race_type
                    FROM races
                    WHERE race_id = ?
                """, (race_id,))
                
                race_info = cursor.fetchone()
                if not race_info:
                    return None
                
                race_date, course, distance, race_type = race_info
                
                # Get race results with positions
                cursor.execute("""
                    SELECT horse_name, finishing_position
                    FROM race_results
                    WHERE race_id = ?
                    ORDER BY finishing_position
                """, (race_id,))
                
                results = cursor.fetchall()
                if not results:
                    return None
                
                # Find winner
                winner_name = results[0][0]
                
                # Score all horses
                horse_scores = {}
                for horse_name, position in results:
                    try:
                        scores = await self.scorer.calculate_decimal_scores(horse_name, race_date)
                        if scores and scores.total_form_score > 0:
                            horse_scores[horse_name] = scores.total_form_score
                    except Exception as e:
                        self.logger.debug(f"Error scoring {horse_name}: {e}")
                        continue
                
                if not horse_scores:
                    return None
                
                # Find top-rated horse
                top_rated_horse = max(horse_scores.keys(), key=lambda h: horse_scores[h])
                top_rated_score = horse_scores[top_rated_horse]
                
                # Find positions
                horse_positions = {name: pos for name, pos in results}
                top_rated_position = horse_positions.get(top_rated_horse, 999)
                winner_position = horse_positions.get(winner_name, 999)
                winner_score = horse_scores.get(winner_name, 0.0)
                
                # Top 3 analysis
                top_3_horses = [name for name, pos in results[:3]]
                winner_in_top_3 = winner_name in top_3_horses
                
                return RaceResult(
                    race_id=race_id,
                    race_date=race_date,
                    course=course,
                    distance=distance,
                    race_type=race_type,
                    num_runners=len(results),
                    winner_name=winner_name,
                    winner_position=winner_position,
                    top_rated_horse=top_rated_horse,
                    top_rated_position=top_rated_position,
                    top_rated_score=top_rated_score,
                    winner_score=winner_score,
                    top_3_horses=top_3_horses,
                    winner_in_top_3=winner_in_top_3,
                    score_distribution=horse_scores
                )
                
        except Exception as e:
            self.logger.error(f"Error analyzing race {race_id}: {e}")
            return None
    
    async def run_intensive_test(self, config: TestingConfiguration) -> TestingReport:
        """Run intensive testing with the given configuration"""
        start_time = datetime.now()
        self.logger.info(f"Starting intensive test with {config.num_races} races")
        
        # Select races
        race_ids = self.select_test_races(config)
        
        # Analyze races
        race_results = []
        for i, race_id in enumerate(race_ids, 1):
            if i % 10 == 0:
                self.logger.info(f"Processed {i}/{len(race_ids)} races")
            
            result = await self.analyze_race(race_id)
            if result:
                race_results.append(result)
        
        end_time = datetime.now()
        
        # Calculate metrics
        valid_results = [r for r in race_results if r.top_rated_score > 0]
        
        if not valid_results:
            raise ValueError("No valid race results found")
        
        # Basic performance metrics
        top_rated_wins = sum(1 for r in valid_results if r.top_rated_position == 1)
        top_rated_win_rate = top_rated_wins / len(valid_results)
        
        winners_in_top_3 = sum(1 for r in valid_results if r.winner_in_top_3)
        winner_in_top_3_rate = winners_in_top_3 / len(valid_results)
        
        average_winner_score = statistics.mean([r.winner_score for r in valid_results if r.winner_score > 0])
        average_top_rated_score = statistics.mean([r.top_rated_score for r in valid_results])
        
        # Score accuracy (how often higher scores correspond to better positions)
        score_accuracy = self._calculate_score_accuracy(valid_results)
        
        # Distribution analysis
        all_scores = []
        for result in valid_results:
            all_scores.extend(result.score_distribution.values())
        
        score_distribution_stats = {
            "mean": statistics.mean(all_scores),
            "median": statistics.median(all_scores),
            "std_dev": statistics.stdev(all_scores) if len(all_scores) > 1 else 0,
            "min": min(all_scores),
            "max": max(all_scores)
        }
        
        # Position accuracy
        position_accuracy = self._calculate_position_accuracy(valid_results)
        
        # Race type performance
        race_type_performance = self._analyze_race_type_performance(valid_results)
        
        # Generate recommendations
        weight_recommendations = self._generate_weight_recommendations(valid_results)
        threshold_recommendations = self._generate_threshold_recommendations(valid_results)
        
        total_horses = sum(len(r.score_distribution) for r in valid_results)
        
        report = TestingReport(
            config=config,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            total_races=len(valid_results),
            total_horses=total_horses,
            top_rated_win_rate=top_rated_win_rate,
            winner_in_top_3_rate=winner_in_top_3_rate,
            average_winner_score=average_winner_score,
            average_top_rated_score=average_top_rated_score,
            score_accuracy=score_accuracy,
            score_distribution_stats=score_distribution_stats,
            position_accuracy=position_accuracy,
            race_type_performance=race_type_performance,
            weight_recommendations=weight_recommendations,
            threshold_recommendations=threshold_recommendations,
            race_results=valid_results if config.detailed_reporting else []
        )
        
        # Save report
        self._save_report(report, config.output_file)
        
        return report
    
    def _calculate_score_accuracy(self, results: List[RaceResult]) -> float:
        """Calculate how well scores predict positions"""
        accurate_predictions = 0
        total_comparisons = 0
        
        for result in results:
            horses_by_score = sorted(
                result.score_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Get actual positions
            horse_positions = {}
            for i, (horse, _) in enumerate(horses_by_score, 1):
                if horse == result.winner_name:
                    horse_positions[horse] = result.winner_position
                elif horse == result.top_rated_horse:
                    horse_positions[horse] = result.top_rated_position
                # For other horses, we'd need to fetch their positions
            
            # Compare predictions with actual results (simplified)
            if result.top_rated_horse in horse_positions:
                predicted_position = 1  # Top-rated should finish 1st
                actual_position = horse_positions[result.top_rated_horse]
                
                if actual_position <= 3:  # Top 3 is considered accurate
                    accurate_predictions += 1
                total_comparisons += 1
        
        return accurate_predictions / total_comparisons if total_comparisons > 0 else 0
    
    def _calculate_position_accuracy(self, results: List[RaceResult]) -> Dict[int, float]:
        """Calculate accuracy by finishing position"""
        position_data = {}
        
        for result in results:
            pos = result.top_rated_position
            if pos not in position_data:
                position_data[pos] = []
            position_data[pos].append(result.top_rated_score)
        
        # Calculate average scores by position
        position_accuracy = {}
        for pos, scores in position_data.items():
            if pos <= 10:  # Focus on top 10 positions
                position_accuracy[pos] = statistics.mean(scores)
        
        return position_accuracy
    
    def _analyze_race_type_performance(self, results: List[RaceResult]) -> Dict[str, Dict[str, float]]:
        """Analyze performance by race type"""
        race_type_data = {}
        
        for result in results:
            race_type = result.race_type
            if race_type not in race_type_data:
                race_type_data[race_type] = {
                    'win_rate': [],
                    'top_3_rate': [],
                    'avg_score': []
                }
            
            race_type_data[race_type]['win_rate'].append(1 if result.top_rated_position == 1 else 0)
            race_type_data[race_type]['top_3_rate'].append(1 if result.top_rated_position <= 3 else 0)
            race_type_data[race_type]['avg_score'].append(result.top_rated_score)
        
        # Calculate averages
        performance = {}
        for race_type, data in race_type_data.items():
            performance[race_type] = {
                'win_rate': statistics.mean(data['win_rate']),
                'top_3_rate': statistics.mean(data['top_3_rate']),
                'average_score': statistics.mean(data['avg_score']),
                'race_count': len(data['win_rate'])
            }
        
        return performance
    
    def _generate_weight_recommendations(self, results: List[RaceResult]) -> Dict[str, float]:
        """Generate weight optimization recommendations"""
        # This is a simplified version - in practice, you'd run more sophisticated analysis
        
        current_performance = {
            'win_rate': sum(1 for r in results if r.top_rated_position == 1) / len(results),
            'top_3_rate': sum(1 for r in results if r.top_rated_position <= 3) / len(results)
        }
        
        # If performance is below targets, suggest adjustments
        recommendations = {}
        
        if current_performance['win_rate'] < 0.12:  # Below 12% win rate
            recommendations['dslr_weight'] = 0.32  # Increase DSLR
            recommendations['strike_rate_weight'] = 0.38  # Decrease strike rate
            recommendations['form_weight'] = 0.30  # Maintain form
        elif current_performance['top_3_rate'] < 0.35:  # Below 35% top 3 rate
            recommendations['dslr_weight'] = 0.28  # Slight decrease DSLR
            recommendations['strike_rate_weight'] = 0.42  # Increase strike rate
            recommendations['form_weight'] = 0.30  # Maintain form
        else:
            # Current weights are performing well
            recommendations['dslr_weight'] = 0.30
            recommendations['strike_rate_weight'] = 0.40
            recommendations['form_weight'] = 0.30
        
        return recommendations
    
    def _generate_threshold_recommendations(self, results: List[RaceResult]) -> Dict[str, float]:
        """Generate threshold optimization recommendations"""
        all_scores = []
        winning_scores = []
        
        for result in results:
            all_scores.extend(result.score_distribution.values())
            if result.winner_score > 0:
                winning_scores.append(result.winner_score)
        
        if not all_scores or not winning_scores:
            return {}
        
        # Calculate percentiles for category thresholds
        all_scores.sort()
        winning_scores.sort()
        
        return {
            'avoid_threshold': all_scores[int(len(all_scores) * 0.25)],  # 25th percentile
            'hold_threshold': all_scores[int(len(all_scores) * 0.50)],   # 50th percentile
            'back_threshold': all_scores[int(len(all_scores) * 0.75)],   # 75th percentile
            'strong_back_threshold': all_scores[int(len(all_scores) * 0.90)],  # 90th percentile
            'winner_median_score': statistics.median(winning_scores)
        }
    
    def _save_report(self, report: TestingReport, filename: str):
        """Save the testing report to a JSON file"""
        report_dict = asdict(report)
        
        with open(filename, 'w') as f:
            json.dump(report_dict, f, indent=2, default=str)
        
        self.logger.info(f"Report saved to {filename}")
    
    def print_summary(self, report: TestingReport):
        """Print a summary of the testing report"""
        print(f"\n{'='*60}")
        print(f"INTENSIVE TESTING REPORT - Enhanced Form Scorer V3.1")
        print(f"{'='*60}")
        print(f"📅 Test Period: {report.start_time} to {report.end_time}")
        print(f"🏇 Races Analyzed: {report.total_races}")
        print(f"🐎 Horses Scored: {report.total_horses}")
        print(f"⚡ Avg Horses/Race: {report.total_horses / report.total_races:.1f}")
        
        print(f"\n🎯 PERFORMANCE METRICS:")
        print(f"   Top-Rated Win Rate: {report.top_rated_win_rate:.1%}")
        print(f"   Winner in Top 3: {report.winner_in_top_3_rate:.1%}")
        print(f"   Score Accuracy: {report.score_accuracy:.1%}")
        print(f"   Avg Winner Score: {report.average_winner_score:.3f}")
        print(f"   Avg Top-Rated Score: {report.average_top_rated_score:.3f}")
        
        print(f"\n📊 SCORE DISTRIBUTION:")
        stats = report.score_distribution_stats
        print(f"   Mean: {stats['mean']:.3f}")
        print(f"   Median: {stats['median']:.3f}")
        print(f"   Std Dev: {stats['std_dev']:.3f}")
        print(f"   Range: {stats['min']:.3f} - {stats['max']:.3f}")
        
        print(f"\n🏁 RACE TYPE PERFORMANCE:")
        for race_type, perf in report.race_type_performance.items():
            print(f"   {race_type}:")
            print(f"     Win Rate: {perf['win_rate']:.1%}")
            print(f"     Top 3 Rate: {perf['top_3_rate']:.1%}")
            print(f"     Avg Score: {perf['average_score']:.3f}")
            print(f"     Race Count: {perf['race_count']}")
        
        print(f"\n🔧 WEIGHT RECOMMENDATIONS:")
        weights = report.weight_recommendations
        print(f"   DSLR Weight: {weights.get('dslr_weight', 0.30):.1%}")
        print(f"   Strike Rate Weight: {weights.get('strike_rate_weight', 0.40):.1%}")
        print(f"   Form Weight: {weights.get('form_weight', 0.30):.1%}")
        
        print(f"\n🎚️  THRESHOLD RECOMMENDATIONS:")
        thresholds = report.threshold_recommendations
        for name, value in thresholds.items():
            print(f"   {name.replace('_', ' ').title()}: {value:.3f}")
        
        print(f"\n💾 Report saved to: {report.config.output_file}")
        print(f"{'='*60}\n")

# Example usage functions
async def run_quick_test():
    """Run a quick 100-race test"""
    framework = IntensiveTestingFramework()
    
    config = TestingConfiguration(
        num_races=100,
        detailed_reporting=True
    )
    
    print("🚀 Running quick 100-race test...")
    report = await framework.run_intensive_test(config)
    framework.print_summary(report)
    return report

async def run_medium_test():
    """Run a medium 500-race test"""
    framework = IntensiveTestingFramework()
    
    config = TestingConfiguration(
        num_races=500,
        detailed_reporting=False  # Don't store individual race results for large tests
    )
    
    print("🚀 Running medium 500-race test...")
    report = await framework.run_intensive_test(config)
    framework.print_summary(report)
    return report

async def run_large_test():
    """Run a large 2000-race test"""
    framework = IntensiveTestingFramework()
    
    config = TestingConfiguration(
        num_races=2000,
        detailed_reporting=False
    )
    
    print("🚀 Running large 2000-race test...")
    report = await framework.run_intensive_test(config)
    framework.print_summary(report)
    return report

if __name__ == "__main__":
    # Show database stats first
    framework = IntensiveTestingFramework()
    print("📊 Database Statistics:")
    stats = framework.get_database_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n🎯 Available test types:")
    print("1. Quick test (100 races)")
    print("2. Medium test (500 races)")  
    print("3. Large test (2000 races)")
    print("4. Custom test")
    
    choice = input("\nSelect test type (1-4): ").strip()
    
    if choice == "1":
        asyncio.run(run_quick_test())
    elif choice == "2":
        asyncio.run(run_medium_test())
    elif choice == "3":
        asyncio.run(run_large_test())
    elif choice == "4":
        num_races = int(input("Number of races: "))
        config = TestingConfiguration(num_races=num_races)
        asyncio.run(framework.run_intensive_test(config))
    else:
        print("Invalid choice. Running quick test...")
        asyncio.run(run_quick_test())
