#!/usr/bin/env python3
"""
Race Staging Manager
Pipeline staging system that detects race times and triggers AI/ML model preparation
15 minutes before the first race of the day.

Key Features:
- Reads today's race cards to detect race times
- Calculates staging time (15 minutes before first race)
- Schedules AI/ML model preparation tasks
- Integrates with daily pipeline orchestrator
- CLI interface for manual staging control
"""

import os
import sys
import json
import sqlite3
import argparse
import logging
from datetime import datetime, timedelta, time as dt_time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import schedule
import time
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/race_staging_manager.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RaceStagingManager:
    """Manages pipeline staging for race preparation timing"""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize race staging manager"""
        config_path = "config/race_staging_config.json"
        self.config_file = Path(config_file) if config_file else Path(config_path)
        self.config = self._load_config()
        self.staging_status = {
            "last_staging": None,
            "current_race_date": None,
            "first_race_time": None,
            "staging_time": None,
            "models_ready": False,
            "preparation_completed": False
        }
        
        # Data directories
        self.data_dir = Path("data/daily_downloads")
        self.cards_dir = self.data_dir / "cards_data"
        self.database_path = Path("ai_strategies_corrected.db")

    def _load_config(self) -> Dict:
        """Load staging configuration"""
        default_config = {
            "staging": {
                "prep_minutes_before_race": 15,
                "auto_staging_enabled": True,
                "staging_check_interval": 300,  # 5 minutes
                "min_lead_time_hours": 2,  # Minimum lead time for staging
            },
            "race_detection": {
                "data_sources": ["cards_data", "database"],
                "time_format": "%H:%M",
                "earliest_race_time": "12:00",
                "latest_race_time": "22:00",
            },
            "pipeline_tasks": {
                "ml_models": ["random_forest", "gradient_boosting", "neural_network"],
                "data_validation": True,
                "performance_checks": True,
                "backup_creation": True,
            },
            "notifications": {
                "staging_alerts": True,
                "model_ready_alerts": True,
                "error_alerts": True,
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
                
        return default_config

    def _save_config(self):
        """Save current configuration"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def detect_race_times(self, target_date: Optional[str] = None) -> List[str]:
        """
        Detect race times for the specified date (or today if not specified)
        
        Args:
            target_date: Date in YYYY-MM-DD format (default: today)
            
        Returns:
            List of race times in HH:MM format, sorted chronologically
        """
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
            
        logger.info(f"🔍 Detecting race times for {target_date}")
        
        race_times = []
        
        # Method 1: Check cards_data CSV files
        race_times.extend(self._detect_from_cards_data(target_date))
        
        # Method 2: Check database
        race_times.extend(self._detect_from_database(target_date))
        
        # Remove duplicates and sort
        unique_times = sorted(list(set(race_times)))
        
        # Filter by time range
        filtered_times = self._filter_race_times(unique_times)
        
        race_count = len(filtered_times)
        logger.info(f"📅 Found {race_count} races for {target_date}: {filtered_times}")
        return filtered_times

    def _detect_from_cards_data(self, target_date: str) -> List[str]:
        """Detect race times from cards_data CSV files"""
        race_times = []
        
        try:
            # Look for races.csv in cards_data
            races_file = self.cards_dir / "races" / "races.csv"
            
            if races_file.exists():
                df = pd.read_csv(races_file)
                logger.info(f"📊 Reading race data from {races_file}")
                
                # Filter by date
                if 'race_date' in df.columns:
                    df = df[df['race_date'] == target_date]
                    
                # Extract race times
                time_columns = ['race_time', 'off_time', 'start_time', 'time']
                for col in time_columns:
                    if col in df.columns:
                        times = df[col].dropna().tolist()
                        for t in times:
                            normalized = self._normalize_time_format(t)
                            if normalized:
                                race_times.append(normalized)
                        break
                        
                logger.info(f"✅ Found {len(race_times)} race times from cards_data")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to read cards_data: {e}")
            
        return race_times

    def _detect_from_database(self, target_date: str) -> List[str]:
        """Detect race times from database"""
        race_times = []
        
        try:
            if not self.database_path.exists():
                logger.warning(f"Database not found: {self.database_path}")
                return race_times
                
            conn = sqlite3.connect(self.database_path)
            
            # Try multiple table schemas
            queries = [
                """
                SELECT DISTINCT race_time, off_time, start_time
                FROM races
                WHERE race_date = ? OR date = ?
                """,
                """
                SELECT DISTINCT time
                FROM race_cards
                WHERE date = ?
                """,
                """
                SELECT DISTINCT race_time
                FROM daily_races
                WHERE race_date = ?
                """
            ]
            
            for query in queries:
                try:
                    if query.count('?') == 2:
                        params = [target_date, target_date]
                        df = pd.read_sql_query(query, conn, params=params)
                    else:
                        df = pd.read_sql_query(query, conn, params=[target_date])
                        
                    for col in df.columns:
                        times = df[col].dropna().tolist()
                        for t in times:
                            normalized = self._normalize_time_format(t)
                            if normalized:
                                race_times.append(normalized)
                        
                    if race_times:
                        count = len(race_times)
                        logger.info(f"✅ Found {count} race times from database")
                        break
                        
                except Exception as e:
                    logger.debug(f"Query failed: {e}")
                    continue
            
            conn.close()
            
        except Exception as e:
            logger.warning(f"⚠️ Database query failed: {e}")
            
        return race_times

    def _normalize_time_format(self, time_str: str) -> str:
        """Normalize time string to HH:MM format"""
        try:
            if isinstance(time_str, str):
                # Handle various formats
                time_str = time_str.strip()
                
                # Already in HH:MM format
                if ':' in time_str and len(time_str) <= 5:
                    parts = time_str.split(':')
                    hour = int(parts[0])
                    minute = int(parts[1])
                    return f"{hour:02d}:{minute:02d}"
                    
                # Handle other formats as needed
                
        except Exception as e:
            logger.debug(f"Failed to normalize time '{time_str}': {e}")
            
        return None

    def _filter_race_times(self, race_times: List[str]) -> List[str]:
        """Filter race times by configured range"""
        try:
            earliest = self.config["race_detection"]["earliest_race_time"]
            latest = self.config["race_detection"]["latest_race_time"]
            
            earliest_time = datetime.strptime(earliest, "%H:%M").time()
            latest_time = datetime.strptime(latest, "%H:%M").time()
            
            filtered = []
            for time_str in race_times:
                if time_str:
                    try:
                        race_time = datetime.strptime(time_str, "%H:%M").time()
                        if earliest_time <= race_time <= latest_time:
                            filtered.append(time_str)
                    except Exception:
                        continue
                        
            return filtered
            
        except Exception as e:
            logger.warning(f"Failed to filter race times: {e}")
            return race_times

    def calculate_staging_time(self, first_race_time: str,
                               prep_minutes: Optional[int] = None) -> str:
        """
        Calculate when pipeline should be ready for staging
        
        Args:
            first_race_time: Time of first race in HH:MM format
            prep_minutes: Minutes before race to be ready (default from config)
            
        Returns:
            Staging time in HH:MM format
        """
        if prep_minutes is None:
            prep_minutes = self.config["staging"]["prep_minutes_before_race"]
            
        try:
            # Parse the race time
            hour, minute = map(int, first_race_time.split(':'))
            race_datetime = datetime.now().replace(hour=hour, minute=minute, second=0)
            
            # Subtract preparation time
            staging_datetime = race_datetime - timedelta(minutes=prep_minutes)
            
            staging_time = staging_datetime.strftime("%H:%M")
            
            msg = f"🎯 Staging time calculated: {staging_time}"
            msg += f" ({prep_minutes} min before {first_race_time})"
            logger.info(msg)
            return staging_time
            
        except Exception as e:
            logger.error(f"Failed to calculate staging time: {e}")
            return None

    def is_staging_time(self, current_time: Optional[str] = None) -> bool:
        """Check if it's time to start staging"""
        if current_time is None:
            current_time = datetime.now().strftime("%H:%M")
            
        staging_time = self.staging_status.get("staging_time")
        
        if not staging_time:
            return False
            
        return current_time >= staging_time

    def prepare_ml_models(self) -> bool:
        """Prepare ML models for the day's racing"""
        logger.info("🤖 Starting ML model preparation...")
        
        try:
            # Import pipeline modules
            sys.path.append(str(Path.cwd()))
            from daily_pipeline_orchestrator import DailyPipelineOrchestrator
            
            orchestrator = DailyPipelineOrchestrator()
            
            # Run essential pipeline components for model readiness
            tasks_completed = []
            
            # 1. Execute a basic pipeline run to ensure models are ready
            logger.info("� Running basic pipeline for model preparation...")
            try:
                import asyncio
                asyncio.run(orchestrator.run_basic_pipeline())
                tasks_completed.append("basic_pipeline")
            except Exception as e:
                logger.warning(f"Basic pipeline failed: {e}")
            
            # 2. Run complete pipeline to ensure everything is current
            logger.info("🚀 Running complete pipeline...")
            try:
                import asyncio
                asyncio.run(orchestrator.run_complete_pipeline_now())
                tasks_completed.append("complete_pipeline")
            except Exception as e:
                logger.warning(f"Complete pipeline failed: {e}")
            
            success_rate = len(tasks_completed) / 2
            
            if success_rate >= 0.5:  # At least 50% of tasks completed
                completed = len(tasks_completed)
                logger.info(f"✅ ML models prepared successfully ({completed}/2 tasks)")
                self.staging_status["models_ready"] = True
                self.staging_status["preparation_completed"] = True
                return True
            else:
                completed = len(tasks_completed)
                msg = f"⚠️ Only {completed}/2 tasks completed"
                msg += " - models may not be fully ready"
                logger.warning(msg)
                return False
                
        except Exception as e:
            logger.error(f"❌ ML model preparation failed: {e}")
            return False

    def execute_staging(self, target_date: Optional[str] = None) -> Dict:
        """
        Execute full staging process for the specified date
        
        Returns:
            Staging status dictionary
        """
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
            
        logger.info(f"🚀 Starting race staging process for {target_date}")
        
        # Reset staging status
        self.staging_status.update({
            "last_staging": datetime.now().isoformat(),
            "current_race_date": target_date,
            "models_ready": False,
            "preparation_completed": False
        })
        
        try:
            # 1. Detect race times
            race_times = self.detect_race_times(target_date)
            
            if not race_times:
                logger.warning(f"❌ No races found for {target_date}")
                return {
                    "success": False,
                    "message": f"No races found for {target_date}",
                    "race_times": [],
                    "staging_time": None
                }
            
            # 2. Calculate staging time
            first_race_time = race_times[0]
            staging_time = self.calculate_staging_time(first_race_time)
            
            if not staging_time:
                logger.error("❌ Failed to calculate staging time")
                return {
                    "success": False,
                    "message": "Failed to calculate staging time",
                    "race_times": race_times,
                    "staging_time": None
                }
            
            # 3. Update staging status
            self.staging_status.update({
                "first_race_time": first_race_time,
                "staging_time": staging_time,
            })
            
            # 4. Check if it's time to prepare models
            current_time = datetime.now().strftime("%H:%M")
            
            if self.is_staging_time(current_time):
                logger.info("⏰ Staging time reached - preparing models now")
                models_ready = self.prepare_ml_models()
            else:
                msg = f"⏳ Staging scheduled for {staging_time}"
                msg += f" (current: {current_time})"
                logger.info(msg)
                models_ready = False
            
            # 5. Return status
            return {
                "success": True,
                "message": f"Staging configured for {target_date}",
                "race_times": race_times,
                "first_race_time": first_race_time,
                "staging_time": staging_time,
                "current_time": current_time,
                "models_ready": models_ready,
                "total_races": len(race_times)
            }
            
        except Exception as e:
            logger.error(f"❌ Staging execution failed: {e}")
            return {
                "success": False,
                "message": f"Staging failed: {e}",
                "race_times": [],
                "staging_time": None
            }

    def start_auto_staging(self):
        """Start automatic staging monitoring"""
        if not self.config["staging"]["auto_staging_enabled"]:
            logger.info("❌ Auto-staging is disabled")
            return
            
        check_interval = self.config["staging"]["staging_check_interval"]
        logger.info(f"🔄 Starting auto-staging monitor (check every {check_interval}s)")
        
        def staging_check():
            """Periodic staging check"""
            try:
                today = datetime.now().strftime("%Y-%m-%d")
                current_time = datetime.now().strftime("%H:%M")
                
                # Only check if we haven't staged today yet
                if (self.staging_status.get("current_race_date") != today or
                        not self.staging_status.get("preparation_completed")):
                    
                    logger.info(f"🔍 Auto-staging check at {current_time}")
                    result = self.execute_staging(today)
                    
                    if result["success"] and result.get("models_ready"):
                        logger.info("✅ Auto-staging completed successfully")
                    elif result["success"]:
                        logger.info(f"⏳ Staging scheduled for {result['staging_time']}")
                    else:
                        logger.warning(f"⚠️ Auto-staging issue: {result['message']}")
                        
            except Exception as e:
                logger.error(f"❌ Auto-staging check failed: {e}")
        
        # Schedule periodic checks
        schedule.every(check_interval).seconds.do(staging_check)
        
        logger.info("🔄 Auto-staging monitor started")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds for scheduled tasks
        except KeyboardInterrupt:
            logger.info("🛑 Auto-staging monitor stopped")

    def get_status(self) -> Dict:
        """Get current staging status"""
        return {
            "staging_status": self.staging_status,
            "config": self.config,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


def main():
    """CLI interface for race staging manager"""
    parser = argparse.ArgumentParser(description="Race Staging Manager CLI")
    parser.add_argument("command",
                        choices=["status", "stage", "detect", "auto", "config"],
                        help="Command to execute")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD, default: today)")
    parser.add_argument("--prep-minutes", type=int, default=15,
                        help="Minutes before race to be ready (default: 15)")
    parser.add_argument("--config", help="Path to config file")
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = RaceStagingManager(args.config)
    
    if args.command == "status":
        print("\n🏁 Race Staging Manager Status")
        print("=" * 50)
        status = manager.get_status()
        
        print(f"📅 Current Time: {status['current_time']}")
        print(f"📊 Race Date: {status['staging_status'].get('current_race_date', 'Not set')}")
        print(f"🏃 First Race: {status['staging_status'].get('first_race_time', 'Not detected')}")
        print(f"⏰ Staging Time: {status['staging_status'].get('staging_time', 'Not calculated')}")
        print(f"🤖 Models Ready: {status['staging_status'].get('models_ready', False)}")
        print(f"✅ Preparation Complete: {status['staging_status'].get('preparation_completed', False)}")
        
    elif args.command == "detect":
        print(f"\n🔍 Detecting Race Times for {args.date or 'today'}")
        print("=" * 50)
        race_times = manager.detect_race_times(args.date)
        
        if race_times:
            print(f"📅 Found {len(race_times)} races:")
            for i, time_str in enumerate(race_times, 1):
                print(f"  {i}. {time_str}")
                
            first_race = race_times[0]
            staging_time = manager.calculate_staging_time(first_race, args.prep_minutes)
            print(f"\n🎯 Staging Time: {staging_time} ({args.prep_minutes} min before {first_race})")
        else:
            print("❌ No races found")
            
    elif args.command == "stage":
        print(f"\n🚀 Executing Staging for {args.date or 'today'}")
        print("=" * 50)
        result = manager.execute_staging(args.date)
        
        if result["success"]:
            print(f"✅ {result['message']}")
            print(f"📊 Total Races: {result['total_races']}")
            print(f"🏃 First Race: {result['first_race_time']}")
            print(f"⏰ Staging Time: {result['staging_time']}")
            print(f"🕐 Current Time: {result['current_time']}")
            print(f"🤖 Models Ready: {result['models_ready']}")
        else:
            print(f"❌ {result['message']}")
            
    elif args.command == "auto":
        print("\n🔄 Starting Auto-Staging Monitor")
        print("=" * 50)
        print("Press Ctrl+C to stop")
        manager.start_auto_staging()
        
    elif args.command == "config":
        print("\n⚙️ Current Configuration")
        print("=" * 50)
        config = manager.config
        print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()
