#!/usr/bin/env python3
"""
🏇 Cached Feature Engineering - Phase 1C Integration

Integrates intelligent caching with existing ML feature preparation.
Wraps existing feature engineering functions with caching capabilities.

Author: AI Assistant
Date: August 15, 2025
Part of: Phase 1C - Intelligent Caching System
"""

import pandas as pd
import numpy as np
import psycopg2
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tools.caching.pipeline_cache_manager import (
    PipelineCacheManager,
    cached_feature_engineering,
    cached_database_query
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CachedFeatureEngineering:
    """
    🚀 Enhanced feature engineering with intelligent caching.
    
    Wraps existing feature engineering with Redis-based caching to:
    - Cache expensive database queries
    - Cache computed features by race_id
    - Cache model training data
    - Provide cache analytics and monitoring
    """
    
    def __init__(self, 
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 cache_ttl: int = 3600):
        """Initialize cached feature engineering."""
        
        # Database configuration
        self.db_config = {
            "host": "localhost",
            "port": 5433,
            "database": "horse_racing_db", 
            "user": "horse_racing",
            "password": os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
        }
        
        # Initialize cache manager
        self.cache_manager = PipelineCacheManager(
            redis_host=redis_host,
            redis_port=redis_port,
            default_ttl=cache_ttl
        )
        
        logger.info("🚀 Cached Feature Engineering initialized")
        
    def get_database_connection(self):
        """Get database connection."""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    @cached_database_query
    def get_race_data(self, race_id: str, conn) -> pd.DataFrame:
        """
        Get race data with caching.
        
        Args:
            race_id: Race identifier
            conn: Database connection
            
        Returns:
            DataFrame with race data
        """
        logger.debug(f"🔍 Fetching race data for {race_id}")
        
        query = """
        SELECT 
            r.race_id, r.date, r.course, r.distance, r.race_type,
            r.class, r.surface, r.runners,
            rec.record_id, rec.position, rec.horse, rec.age, 
            rec.weight, rec.jockey, rec.trainer, rec.sp, rec.odds
        FROM races r
        JOIN records rec ON r.race_id = rec.race_id
        WHERE r.race_id = %s
        ORDER BY rec.position
        """
        
        try:
            df = pd.read_sql_query(query, conn, params=(race_id,))
            logger.debug(f"✅ Retrieved {len(df)} records for race {race_id}")
            return df
        except Exception as e:
            logger.error(f"❌ Error fetching race data: {e}")
            return pd.DataFrame()
    
    @cached_database_query  
    def get_horse_historical_performance(self, horse_name: str, conn, 
                                       days_back: int = 365) -> pd.DataFrame:
        """
        Get horse historical performance with caching.
        
        Args:
            horse_name: Horse name
            conn: Database connection
            days_back: Days to look back for history
            
        Returns:
            DataFrame with historical performance
        """
        logger.debug(f"🐎 Fetching performance history for {horse_name}")
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        query = """
        SELECT 
            r.date, r.course, r.distance, r.race_type, r.class,
            rec.position, rec.sp, rec.odds, rec.age, rec.weight
        FROM races r
        JOIN records rec ON r.race_id = rec.race_id
        WHERE rec.horse = %s 
        AND r.date >= %s
        ORDER BY r.date DESC
        LIMIT 50
        """
        
        try:
            df = pd.read_sql_query(
                query, conn, 
                params=(horse_name, cutoff_date.strftime('%Y-%m-%d'))
            )
            logger.debug(f"✅ Retrieved {len(df)} historical races for {horse_name}")
            return df
        except Exception as e:
            logger.error(f"❌ Error fetching horse history: {e}")
            return pd.DataFrame()
    
    @cached_database_query
    def get_jockey_trainer_stats(self, jockey: str, trainer: str, conn,
                               days_back: int = 365) -> Dict[str, float]:
        """
        Get jockey and trainer statistics with caching.
        
        Args:
            jockey: Jockey name
            trainer: Trainer name  
            conn: Database connection
            days_back: Days to look back
            
        Returns:
            Dictionary with jockey/trainer stats
        """
        logger.debug(f"👨‍💼 Fetching stats for jockey: {jockey}, trainer: {trainer}")
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Jockey stats query
        jockey_query = """
        SELECT 
            COUNT(*) as total_races,
            SUM(CASE WHEN rec.position = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN rec.position <= 3 THEN 1 ELSE 0 END) as places
        FROM races r
        JOIN records rec ON r.race_id = rec.race_id
        WHERE rec.jockey = %s 
        AND r.date >= %s
        """
        
        # Trainer stats query
        trainer_query = """
        SELECT 
            COUNT(*) as total_races,
            SUM(CASE WHEN rec.position = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN rec.position <= 3 THEN 1 ELSE 0 END) as places
        FROM races r
        JOIN records rec ON r.race_id = rec.race_id
        WHERE rec.trainer = %s 
        AND r.date >= %s
        """
        
        try:
            # Get jockey stats
            jockey_df = pd.read_sql_query(
                jockey_query, conn,
                params=(jockey, cutoff_date.strftime('%Y-%m-%d'))
            )
            
            # Get trainer stats
            trainer_df = pd.read_sql_query(
                trainer_query, conn,
                params=(trainer, cutoff_date.strftime('%Y-%m-%d'))
            )
            
            # Calculate win rates
            jockey_stats = jockey_df.iloc[0] if len(jockey_df) > 0 else {}
            trainer_stats = trainer_df.iloc[0] if len(trainer_df) > 0 else {}
            
            stats = {
                'jockey_total_races': int(jockey_stats.get('total_races', 0)),
                'jockey_wins': int(jockey_stats.get('wins', 0)),
                'jockey_places': int(jockey_stats.get('places', 0)),
                'jockey_win_rate': (jockey_stats.get('wins', 0) / 
                                  max(jockey_stats.get('total_races', 1), 1)) * 100,
                'jockey_place_rate': (jockey_stats.get('places', 0) / 
                                     max(jockey_stats.get('total_races', 1), 1)) * 100,
                
                'trainer_total_races': int(trainer_stats.get('total_races', 0)),
                'trainer_wins': int(trainer_stats.get('wins', 0)),
                'trainer_places': int(trainer_stats.get('places', 0)),
                'trainer_win_rate': (trainer_stats.get('wins', 0) / 
                                    max(trainer_stats.get('total_races', 1), 1)) * 100,
                'trainer_place_rate': (trainer_stats.get('places', 0) / 
                                      max(trainer_stats.get('total_races', 1), 1)) * 100,
            }
            
            logger.debug(f"✅ Retrieved jockey/trainer stats")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error fetching jockey/trainer stats: {e}")
            return {}
    
    @cached_feature_engineering
    def calculate_horse_form_features(self, horse_name: str, 
                                    historical_data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate horse form features with caching.
        
        Args:
            horse_name: Horse name
            historical_data: Historical performance data
            
        Returns:
            Dictionary with form features
        """
        logger.debug(f"🔢 Calculating form features for {horse_name}")
        
        if historical_data.empty:
            return {
                'avg_position': 10.0,
                'win_rate': 0.0,
                'place_rate': 0.0,
                'recent_form': 0.0,
                'consistency': 0.0,
                'days_since_last_race': 999
            }
        
        try:
            # Sort by date descending
            historical_data = historical_data.sort_values('date', ascending=False)
            
            # Basic stats
            total_races = len(historical_data)
            wins = len(historical_data[historical_data['position'] == 1])
            places = len(historical_data[historical_data['position'] <= 3])
            
            # Recent form (last 5 races)
            recent_races = historical_data.head(5)
            recent_positions = recent_races['position'].tolist()
            recent_form = sum(6 - pos for pos in recent_positions if pos <= 5) / len(recent_positions)
            
            # Consistency (standard deviation of positions)
            position_std = historical_data['position'].std()
            consistency = max(0, 10 - position_std)  # Lower std = higher consistency
            
            # Days since last race
            if not historical_data.empty:
                last_race_date = pd.to_datetime(historical_data.iloc[0]['date'])
                days_since_last = (datetime.now() - last_race_date).days
            else:
                days_since_last = 999
            
            features = {
                'avg_position': float(historical_data['position'].mean()),
                'win_rate': (wins / total_races) * 100 if total_races > 0 else 0.0,
                'place_rate': (places / total_races) * 100 if total_races > 0 else 0.0,
                'recent_form': float(recent_form),
                'consistency': float(consistency),
                'days_since_last_race': int(days_since_last)
            }
            
            logger.debug(f"✅ Calculated form features for {horse_name}")
            return features
            
        except Exception as e:
            logger.error(f"❌ Error calculating form features: {e}")
            return {}
    
    @cached_feature_engineering
    def calculate_race_features(self, race_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate race-level features with caching.
        
        Args:
            race_data: Race data DataFrame
            
        Returns:
            Dictionary with race features
        """
        logger.debug("🏁 Calculating race features")
        
        if race_data.empty:
            return {}
        
        try:
            # Extract race metadata
            race_info = race_data.iloc[0]
            
            # Parse distance (assume it's in furlongs or meters)
            distance_str = str(race_info.get('distance', '0'))
            try:
                # Extract numeric distance
                distance_numeric = float(''.join(filter(str.isdigit, distance_str)))
                if distance_numeric == 0:
                    distance_numeric = 1609  # Default 1 mile in meters
            except:
                distance_numeric = 1609
            
            # Field size
            field_size = len(race_data)
            
            # Class level (try to extract numeric class)
            class_str = str(race_info.get('class', '0'))
            try:
                class_level = int(''.join(filter(str.isdigit, class_str)))
                if class_level == 0:
                    class_level = 3  # Default class
            except:
                class_level = 3
            
            # Surface encoding
            surface = str(race_info.get('surface', 'turf')).lower()
            surface_turf = 1.0 if 'turf' in surface else 0.0
            surface_dirt = 1.0 if 'dirt' in surface or 'sand' in surface else 0.0
            
            # Race type encoding
            race_type = str(race_info.get('race_type', 'flat')).lower()
            race_type_flat = 1.0 if 'flat' in race_type else 0.0
            race_type_hurdle = 1.0 if 'hurdle' in race_type else 0.0
            race_type_chase = 1.0 if 'chase' in race_type else 0.0
            
            features = {
                'distance_numeric': distance_numeric,
                'field_size': field_size,
                'class_level': class_level,
                'surface_turf': surface_turf,
                'surface_dirt': surface_dirt,
                'race_type_flat': race_type_flat,
                'race_type_hurdle': race_type_hurdle,
                'race_type_chase': race_type_chase,
                'race_id': str(race_info.get('race_id', '')),
                'course': str(race_info.get('course', '')),
                'date': str(race_info.get('date', ''))
            }
            
            logger.debug("✅ Calculated race features")
            return features
            
        except Exception as e:
            logger.error(f"❌ Error calculating race features: {e}")
            return {}
    
    def create_ml_features_for_race(self, race_id: str) -> pd.DataFrame:
        """
        Create complete ML feature set for a race with intelligent caching.
        
        Args:
            race_id: Race identifier
            
        Returns:
            DataFrame with features for all horses in the race
        """
        logger.info(f"🎯 Creating ML features for race {race_id}")
        start_time = time.time()
        
        try:
            with self.get_database_connection() as conn:
                # Get race data (cached)
                race_data = self.get_race_data(race_id, conn)
                
                if race_data.empty:
                    logger.error(f"❌ No data found for race {race_id}")
                    return pd.DataFrame()
                
                # Calculate race-level features (cached)
                race_features = self.calculate_race_features(race_data)
                
                # Process each horse
                ml_features = []
                
                for _, horse_record in race_data.iterrows():
                    horse_name = horse_record['horse']
                    jockey = horse_record['jockey']
                    trainer = horse_record['trainer']
                    
                    # Get horse historical data (cached)
                    horse_history = self.get_horse_historical_performance(
                        horse_name, conn
                    )
                    
                    # Calculate horse form features (cached)
                    form_features = self.calculate_horse_form_features(
                        horse_name, horse_history
                    )
                    
                    # Get jockey/trainer stats (cached)
                    jt_stats = self.get_jockey_trainer_stats(
                        jockey, trainer, conn
                    )
                    
                    # Combine all features
                    horse_features = {
                        'race_id': race_id,
                        'horse_name': horse_name,
                        'position': horse_record['position'],
                        'age': horse_record['age'],
                        'jockey': jockey,
                        'trainer': trainer,
                        **race_features,
                        **form_features,
                        **jt_stats
                    }
                    
                    ml_features.append(horse_features)
                
                # Create DataFrame
                features_df = pd.DataFrame(ml_features)
                
                execution_time = time.time() - start_time
                logger.info(f"✅ Created ML features for {len(features_df)} horses in {execution_time:.2f}s")
                
                return features_df
                
        except Exception as e:
            logger.error(f"❌ Error creating ML features: {e}")
            return pd.DataFrame()
    
    def get_cache_analytics(self) -> Dict[str, Any]:
        """Get cache performance analytics."""
        cache_info = self.cache_manager.get_cache_info()
        
        analytics = {
            'cache_performance': {
                'hit_rate_percent': cache_info.get('hit_rate_percent', 0),
                'total_requests': cache_info.get('total_requests', 0),
                'time_saved_ms': cache_info.get('time_saved_ms', 0),
            },
            'cache_status': cache_info.get('connection_status', 'unknown'),
            'redis_info': {
                'version': cache_info.get('redis_version', 'unknown'),
                'memory_mb': cache_info.get('used_memory_mb', 0),
                'clients': cache_info.get('connected_clients', 0)
            }
        }
        
        return analytics
    
    def clear_cache(self, cache_type: Optional[str] = None) -> bool:
        """Clear cache data."""
        if cache_type:
            deleted = self.cache_manager.invalidate_pattern(cache_type, "*")
            logger.info(f"🗑️  Cleared {deleted} entries from {cache_type} cache")
        else:
            success = self.cache_manager.clear_all_cache()
            logger.info("🗑️  Cleared all cache data")
            return success
        
        return deleted > 0


# Example usage and testing
if __name__ == "__main__":
    print("🏇 Cached Feature Engineering - Testing Mode")
    print("=" * 60)
    
    # Initialize cached feature engineering
    cached_fe = CachedFeatureEngineering()
    
    # Test with a sample race
    print("\n🧪 Testing cached feature engineering...")
    
    # This would need a real race_id from your database
    sample_race_id = "R123456"  
    
    print(f"🎯 Creating features for race: {sample_race_id}")
    
    # First run (cache miss expected)
    start_time = time.time()
    features_df = cached_fe.create_ml_features_for_race(sample_race_id)
    first_run_time = time.time() - start_time
    
    print(f"⏱️  First run: {first_run_time:.2f}s (cache miss)")
    print(f"📊 Features created: {len(features_df)} horses")
    
    if not features_df.empty:
        # Second run (cache hit expected)
        start_time = time.time()
        features_df_cached = cached_fe.create_ml_features_for_race(sample_race_id)
        second_run_time = time.time() - start_time
        
        print(f"⏱️  Second run: {second_run_time:.2f}s (cache hit)")
        
        speedup = first_run_time / second_run_time if second_run_time > 0 else 0
        print(f"🚀 Speedup: {speedup:.1f}x faster")
    
    # Display cache analytics
    print("\n📊 Cache Analytics:")
    analytics = cached_fe.get_cache_analytics()
    
    print(f"  • Hit Rate: {analytics['cache_performance']['hit_rate_percent']:.1f}%")
    print(f"  • Total Requests: {analytics['cache_performance']['total_requests']}")
    print(f"  • Time Saved: {analytics['cache_performance']['time_saved_ms']:.1f}ms")
    print(f"  • Cache Status: {analytics['cache_status']}")
    print(f"  • Redis Version: {analytics['redis_info']['version']}")
    
    print("\n🎉 Cached feature engineering testing complete!")
