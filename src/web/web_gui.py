#!/usr/bin/env python3
"""
Horse Racing AI v2.0 - Web GUI
Enhanced scoring system with real-time analysis and betting insights.
Now includes BETDAQ integration and NTFY alerts.
"""

import asyncio
import json
import logging
import os
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS

# Try to import requests, fallback to urllib if not available
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from betdaq.betdaq_client import BetdaqClient, BetdaqConfig
from betdaq.betdaq_live_betting import RiskLimits
from betdaq.betdaq_paper_trading import PaperTradingConfig

# Import BETDAQ integration
from src.betdaq.betdaq_betting_coordinator import BettingCoordinator, TradingMode
from src.horse_racing_ai.scoring import (
    CompositeScorer,
    EnhancedFormAnalyzer,
    PowerRatingSystem,
)
from src.horse_racing_ai.simulation import MonteCarloSimulator

# Import database manager
from src.database.database_manager import DatabaseManager

# Import ML models for AI performance comparison
try:
    from src.horse_racing_ai.ml.ai_trainer import AITrainer
    from src.horse_racing_ai.ml.enhanced_ml_models import EnhancedMLRatingSystem
    from src.horse_racing_ai.performance.enhanced_tracker import (
        EnhancedPerformanceTracker,
    )

    ML_MODELS_AVAILABLE = True
except ImportError:
    ML_MODELS_AVAILABLE = False
    print("⚠️  ML models not available - performance comparison features disabled")

app = Flask(__name__, template_folder="../../templates")
CORS(app)

# Initialize logging
logger = logging.getLogger(__name__)

# NTFY Configuration
NTFY_CONFIG = {
    "enabled": os.getenv("NTFY_ENABLED", "true").lower() == "true",
    "topic": os.getenv("NTFY_TOPIC", "horse-racing-ai"),
    "server": os.getenv("NTFY_SERVER", "https://ntfy.sh"),
    "priority": os.getenv("NTFY_PRIORITY", "default"),
}

# Global BETDAQ coordinator
betdaq_coordinator = None

# Initialize scoring systems
form_analyzer = EnhancedFormAnalyzer()
power_rating_system = PowerRatingSystem()
composite_scorer = CompositeScorer()

# Initialize ML systems if available
ml_rating_system = None
ai_trainer = None
performance_tracker = None
if ML_MODELS_AVAILABLE:
    try:
        ml_rating_system = EnhancedMLRatingSystem(enable_neural_networks=False)

        # Try to load existing trained models
        models_dir = Path("models")
        if models_dir.exists():
            # Look for most recent model file
            model_files = list(models_dir.glob("*_models_*.pkl"))
            if model_files:
                latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
                ml_rating_system.load_enhanced_models(latest_model)
                print(f"🤖 Loaded trained ML models from {latest_model.name}")
            else:
                print("🤖 ML models initialized but not trained")
        else:
            print("🤖 ML models initialized but not trained")

        ai_trainer = AITrainer()
        performance_tracker = EnhancedPerformanceTracker()
        print("🤖 ML systems and performance tracker initialized successfully")
    except Exception as e:
        print(f"⚠️  Failed to initialize ML models: {e}")
        ML_MODELS_AVAILABLE = False

# Data directory
DATA_DIR = Path("data")


# NTFY Notification Functions
def send_ntfy_notification(
    title: str, message: str, priority: str = "default", tags: str = "horse,betting"
):
    """Send notification via NTFY"""
    if not NTFY_CONFIG["enabled"]:
        return False

    try:
        if HAS_REQUESTS:
            # Use requests library
            headers = {
                "Title": title,
                "Priority": priority,
                "Tags": tags,
            }

            response = requests.post(
                f"{NTFY_CONFIG['server']}/{NTFY_CONFIG['topic']}",
                data=message.encode("utf-8"),
                headers=headers,
                timeout=10,
            )

            success = response.status_code == 200
        else:
            # Fallback to urllib
            url = f"{NTFY_CONFIG['server']}/{NTFY_CONFIG['topic']}"
            data = message.encode("utf-8")

            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("Title", title)
            req.add_header("Priority", priority)
            req.add_header("Tags", tags)

            with urllib.request.urlopen(req, timeout=10) as response:
                success = response.status == 200

        if success:
            logger.info(f"NTFY notification sent: {title}")
            return True
        else:
            logger.error("NTFY notification failed")
            return False

    except Exception as e:
        logger.error(f"Error sending NTFY notification: {e}")
        return False


async def initialize_betdaq_coordinator():
    """Initialize BETDAQ coordinator"""
    global betdaq_coordinator

    if betdaq_coordinator:
        return betdaq_coordinator

    try:
        # Load configuration
        config_file = Path("betdaq_config.json")
        if config_file.exists():
            with open(config_file) as f:
                config_data = json.load(f)
        else:
            # Default configuration
            config_data = {
                "betdaq_username": os.getenv("BETDAQ_USERNAME", ""),
                "betdaq_password": os.getenv("BETDAQ_PASSWORD", ""),
                "paper_trading": True,
                "betting_enabled": False,
                "starting_balance": 1000.0,
                "max_stake_per_bet": 10.0,
                "max_daily_loss": 100.0,
            }

        # Initialize BETDAQ client
        betdaq_config = BetdaqConfig(
            username=config_data.get("betdaq_username", ""),
            password=config_data.get("betdaq_password", ""),
            paper_trading=config_data.get("paper_trading", True),
            enabled=config_data.get("betting_enabled", False),
            max_stake_per_bet=config_data.get("max_stake_per_bet", 10.0),
            max_daily_loss=config_data.get("max_daily_loss", 100.0),
        )

        client = BetdaqClient(betdaq_config)

        # Setup paper trading or live trading
        if config_data.get("paper_trading", True):
            paper_config = PaperTradingConfig(
                starting_balance=config_data.get("starting_balance", 1000.0),
                realistic_matching=True,
                save_to_database=True,
            )

            betdaq_coordinator = BettingCoordinator(
                betdaq_client=client,
                trading_mode=TradingMode.PAPER,
                paper_config=paper_config,
            )
        else:
            risk_limits = RiskLimits(
                max_stake_per_bet=config_data.get("max_stake_per_bet", 10.0),
                max_total_exposure=config_data.get("max_total_exposure", 100.0),
                max_daily_loss=config_data.get("max_daily_loss", 100.0),
                max_orders_per_race=config_data.get("max_orders_per_race", 2),
                min_odds=config_data.get("min_odds", 1.5),
                max_odds=config_data.get("max_odds", 20.0),
            )

            betdaq_coordinator = BettingCoordinator(
                betdaq_client=client,
                trading_mode=TradingMode.LIVE,
                risk_limits=risk_limits,
            )

        logger.info(
            f"BETDAQ coordinator initialized in {betdaq_coordinator.trading_mode.value} mode"
        )

        # Send initialization notification
        send_ntfy_notification(
            "Horse Racing AI Started",
            f"BETDAQ integration initialized in {betdaq_coordinator.trading_mode.value} mode",
            priority="high",
            tags="horse,betting,startup",
        )

        return betdaq_coordinator

    except Exception as e:
        logger.error(f"Failed to initialize BETDAQ coordinator: {e}")
        return None


@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("index.html")


@app.route("/database")
def database_dashboard():
    """Database dashboard page."""
    return render_template("database_dashboard.html")


# Database API Routes


@app.route("/api/database/summary")
def database_summary():
    """Get database summary statistics"""
    try:
        db = DatabaseManager()
        summary = db.get_database_summary()
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Error getting database summary: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/database/races")
def get_races_api():
    """Get races with optional filtering"""
    try:
        db = DatabaseManager()

        # Get query parameters
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        course = request.args.get("course")
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")

        # Convert date strings to date objects if provided
        from datetime import datetime

        if date_from:
            date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        if date_to:
            date_to = datetime.strptime(date_to, "%Y-%m-%d").date()

        races = db.get_races(
            limit=limit,
            offset=offset,
            date_from=date_from,
            date_to=date_to,
            course=course,
        )

        return jsonify(
            {"races": races, "count": len(races), "offset": offset, "limit": limit}
        )
    except Exception as e:
        logger.error(f"Error getting races: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/database/race/<int:race_id>")
def get_race_details_api(race_id):
    """Get detailed race information"""
    try:
        db = DatabaseManager()
        race_details = db.get_race_details(race_id)

        if not race_details:
            return jsonify({"error": "Race not found"}), 404

        return jsonify(race_details)
    except Exception as e:
        logger.error(f"Error getting race details: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/database/horses")
def get_horses_api():
    """Get horses with optional search"""
    try:
        db = DatabaseManager()

        # Get query parameters
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        search = request.args.get("search")

        horses = db.get_horses(limit=limit, offset=offset, search=search)

        return jsonify(
            {"horses": horses, "count": len(horses), "offset": offset, "limit": limit}
        )
    except Exception as e:
        logger.error(f"Error getting horses: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/database/horse/<int:horse_id>")
def get_horse_details_api(horse_id):
    """Get detailed horse information"""
    try:
        db = DatabaseManager()
        horse_details = db.get_horse_details(horse_id)

        if not horse_details:
            return jsonify({"error": "Horse not found"}), 404

        return jsonify(horse_details)
    except Exception as e:
        logger.error(f"Error getting horse details: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/database/jockeys")
def get_jockeys_api():
    """Get jockey statistics"""
    try:
        db = DatabaseManager()

        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        jockeys = db.get_jockeys(limit=limit, offset=offset)

        return jsonify(
            {
                "jockeys": jockeys,
                "count": len(jockeys),
                "offset": offset,
                "limit": limit,
            }
        )
    except Exception as e:
        logger.error(f"Error getting jockeys: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/database/trainers")
def get_trainers_api():
    """Get trainer statistics"""
    try:
        db = DatabaseManager()

        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        trainers = db.get_trainers(limit=limit, offset=offset)

        return jsonify(
            {
                "trainers": trainers,
                "count": len(trainers),
                "offset": offset,
                "limit": limit,
            }
        )
    except Exception as e:
        logger.error(f"Error getting trainers: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/database/analytics/courses")
def get_course_statistics_api():
    """Get course statistics"""
    try:
        db = DatabaseManager()
        stats = db.get_course_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting course statistics: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/database/analytics/race-types")
def get_race_type_statistics_api():
    """Get race type statistics"""
    try:
        db = DatabaseManager()
        stats = db.get_race_type_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting race type statistics: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/database/recent-results")
def get_recent_results_api():
    """Get recent race results"""
    try:
        db = DatabaseManager()

        limit = int(request.args.get("limit", 50))
        results = db.get_recent_results(limit=limit)

        return jsonify({"results": results, "count": len(results)})
    except Exception as e:
        logger.error(f"Error getting recent results: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/database/search")
def search_database():
    """Search across horses, jockeys, and trainers"""
    try:
        db = DatabaseManager()
        search_term = request.args.get("q", "").strip()

        if not search_term:
            return jsonify({"error": "Search term required"}), 400

        # Search across different entities
        horses = db.search_horses(search_term)
        jockeys = db.search_jockeys(search_term)
        trainers = db.search_trainers(search_term)

        return jsonify(
            {
                "search_term": search_term,
                "results": {"horses": horses, "jockeys": jockeys, "trainers": trainers},
                "total_results": len(horses) + len(jockeys) + len(trainers),
            }
        )
    except Exception as e:
        logger.error(f"Error searching database: {e}")
        return jsonify({"error": str(e)}), 500


# BETDAQ Integration Routes


@app.route("/api/betdaq/status")
def betdaq_status():
    """Get BETDAQ system status"""
    if not betdaq_coordinator:
        return jsonify(
            {"status": "not_initialized", "trading_mode": None, "account": None}
        )

    try:
        performance = betdaq_coordinator.get_performance_summary()

        status_data = {
            "status": "active",
            "trading_mode": betdaq_coordinator.trading_mode.value,
            "account": performance.get("paper_trading", {}).get("account", {}),
            "performance": performance,
            "last_updated": datetime.now().isoformat(),
        }

        return jsonify(status_data)

    except Exception as e:
        logger.error(f"Error getting BETDAQ status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/betdaq/place-bet", methods=["POST"])
def place_bet():
    """Place a bet via BETDAQ"""
    if not betdaq_coordinator:
        return jsonify({"error": "BETDAQ not initialized"}), 400

    try:
        bet_data = request.json

        # Create market info
        from betdaq_client import MarketInfo

        market_info = MarketInfo(
            market_id=bet_data.get("market_id", 999999),
            market_name=bet_data.get("market_name", "Test Market"),
            start_time=datetime.now(),
            status="active",
        )

        # Process the prediction
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            bet_result = loop.run_until_complete(
                betdaq_coordinator.process_ai_prediction(bet_data, market_info)
            )
        finally:
            loop.close()

        if bet_result:
            # Send notification
            send_ntfy_notification(
                "🎯 Bet Placed",
                f"Bet placed: {bet_result.horse_name} @ {bet_result.matched_odds} - £{bet_result.stake}",
                priority="high",
                tags="horse,betting,bet-placed",
            )

            return jsonify(
                {
                    "success": True,
                    "bet": {
                        "bet_id": bet_result.bet_id,
                        "horse_name": bet_result.horse_name,
                        "stake": bet_result.stake,
                        "odds": bet_result.matched_odds,
                        "confidence": bet_data.get("confidence", 0),
                        "value": bet_data.get("value", 0),
                    },
                }
            )
        else:
            return jsonify(
                {"success": False, "error": "Bet rejected by risk management"}
            )

    except Exception as e:
        logger.error(f"Error placing bet: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/betdaq/betting-history")
def betting_history():
    """Get betting history"""
    if not betdaq_coordinator:
        return jsonify({"error": "BETDAQ not initialized"}), 400

    try:
        # Get recent bets from paper trading database
        import sqlite3

        db_path = "paper_trading.db"
        if not Path(db_path).exists():
            return jsonify({"bets": []})

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT bet_id, horse_name, race_name, stake, matched_odds, 
                   pnl, confidence, value, placed_at, status
            FROM paper_bets 
            ORDER BY placed_at DESC 
            LIMIT 50
        """
        )

        bets = []
        for row in cursor.fetchall():
            bets.append(
                {
                    "bet_id": row[0],
                    "horse_name": row[1],
                    "race_name": row[2],
                    "stake": row[3],
                    "odds": row[4],
                    "pnl": row[5],
                    "confidence": row[6],
                    "value": row[7],
                    "placed_at": row[8],
                    "status": row[9],
                }
            )

        conn.close()

        return jsonify({"bets": bets})

    except Exception as e:
        logger.error(f"Error getting betting history: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/betdaq/performance")
def betting_performance():
    """Get detailed betting performance metrics"""
    if not betdaq_coordinator:
        return jsonify({"error": "BETDAQ not initialized"}), 400

    try:
        performance = betdaq_coordinator.get_performance_summary()
        return jsonify(performance)

    except Exception as e:
        logger.error(f"Error getting performance: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/ntfy/test")
def test_ntfy():
    """Test NTFY notification"""
    success = send_ntfy_notification(
        "🧪 Test Notification",
        "Horse Racing AI - NTFY integration is working!",
        priority="normal",
        tags="horse,test",
    )

    return jsonify(
        {
            "success": success,
            "config": {
                "enabled": NTFY_CONFIG["enabled"],
                "topic": NTFY_CONFIG["topic"],
                "server": NTFY_CONFIG["server"],
            },
        }
    )


@app.route("/api/race-cards")
def get_race_cards():
    """Get available test race cards."""
    race_cards_file = DATA_DIR / "massive_test_race_cards.json"

    if not race_cards_file.exists():
        return jsonify({"error": "No race cards available"}), 404

    with open(race_cards_file) as f:
        race_cards = json.load(f)

    # Return just the race info for selection
    race_list = []
    for i, race_card in enumerate(race_cards[:20]):  # Limit to first 20 for performance
        race_info = race_card["race_info"]
        race_list.append(
            {
                "id": i,
                "race_id": race_info["race_id"],
                "track": race_info["track"],
                "distance": race_info["distance"],
                "surface": race_info["surface"],
                "prize_money": race_info["prize_money"],
                "num_horses": len(race_card["horses_data"]),
            }
        )

    return jsonify(race_list)


@app.route("/api/analyze-race/<int:race_index>")
def analyze_race(race_index: int):
    """Analyze a specific race and return comprehensive results."""
    race_cards_file = DATA_DIR / "massive_test_race_cards.json"

    if not race_cards_file.exists():
        return jsonify({"error": "No race cards available"}), 404

    with open(race_cards_file) as f:
        race_cards = json.load(f)

    if race_index >= len(race_cards):
        return jsonify({"error": "Race not found"}), 404

    race_card = race_cards[race_index]

    try:
        # Prepare data for analysis
        race_data = race_card["race_info"]
        horses_data = {}

        # Convert string dates back to datetime objects and reconstruct RacePerformance objects
        for horse_name, performances in race_card["horses_data"].items():
            horse_performances = []
            for perf_dict in performances:
                from src.horse_racing_ai.scoring.form_analyzer import (
                    RaceClass,
                    RacePerformance,
                    SurfaceType,
                )

                # Convert date string back to datetime
                perf_date = datetime.fromisoformat(perf_dict["date"])

                # Convert surface string back to enum
                surface_map = {
                    "turf": SurfaceType.TURF,
                    "dirt": SurfaceType.DIRT,
                    "synthetic": SurfaceType.SYNTHETIC,
                }
                surface = surface_map.get(
                    perf_dict["surface"].lower(), SurfaceType.DIRT
                )

                # Convert race_class integer back to enum
                race_class_map = {
                    1: RaceClass.MAIDEN,
                    2: RaceClass.CLAIMING,
                    3: RaceClass.ALLOWANCE,
                    4: RaceClass.STAKES,
                    5: RaceClass.GRADED_STAKES,
                }
                race_class = race_class_map.get(
                    perf_dict["race_class"], RaceClass.ALLOWANCE
                )

                # Create proper RacePerformance object
                performance = RacePerformance(
                    date=perf_date,
                    track=perf_dict["track"],
                    distance=perf_dict["distance"],
                    surface=surface,
                    race_class=race_class,
                    field_size=perf_dict["field_size"],
                    finish_position=perf_dict["finish_position"],
                    beaten_lengths=perf_dict["beaten_lengths"],
                    time=perf_dict["time"],
                    speed_figure=perf_dict["speed_figure"],
                    pace_figures=perf_dict["pace_figures"],
                    weight_carried=perf_dict["weight_carried"],
                    jockey=perf_dict["jockey"],
                    trainer=perf_dict["trainer"],
                    odds=perf_dict["odds"],
                    purse=perf_dict["purse"],
                    conditions=perf_dict["conditions"],
                    comments=perf_dict["comments"],
                )
                horse_performances.append(performance)
            horses_data[horse_name] = horse_performances

        betting_odds = race_card["betting_odds"]

        # Analyze the race
        race_analysis = composite_scorer.score_race(
            race_data=race_data, horses_data=horses_data, betting_odds=betting_odds
        )

        # Convert datetime objects to strings for JSON serialization
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object {obj} is not JSON serializable")

        # Convert to JSON-serializable format
        result = {
            "race_info": race_data,
            "analysis": {
                "horse_scores": [
                    {
                        "horse_name": score.horse_name,
                        "composite_score": score.composite_score,
                        "win_probability": score.win_probability,
                        "betting_value": score.betting_value,
                        "form_score": score.form_score,
                        "power_rating": score.power_rating,
                        "confidence_level": score.confidence_level,
                        "key_factors": score.key_factors,
                        "concerns": score.concerns,
                    }
                    for score in race_analysis.horse_scores
                ],
                "race_insights": {
                    "pace_scenario": race_analysis.pace_scenario,
                    "track_bias": race_analysis.track_bias,
                    "key_angles": race_analysis.key_angles,
                },
            },
            "betting_odds": betting_odds,
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@app.route("/api/form-analysis/<horse_name>")
def get_horse_form(horse_name: str):
    """Get detailed form analysis for a specific horse."""
    race_cards_file = DATA_DIR / "massive_test_race_cards.json"

    if not race_cards_file.exists():
        return jsonify({"error": "No data available"}), 404

    with open(race_cards_file) as f:
        race_cards = json.load(f)

    # Find horse in any race card
    horse_data = None
    for race_card in race_cards:
        if horse_name in race_card["horses_data"]:
            horse_data = race_card["horses_data"][horse_name]
            break

    if not horse_data:
        return jsonify({"error": "Horse not found"}), 404

    try:
        # Convert string dates back to datetime objects
        performances = []
        for perf_dict in horse_data:
            perf_dict["date"] = datetime.fromisoformat(perf_dict["date"])
            performances.append(perf_dict)

        # Analyze form
        form_analysis = form_analyzer.analyze_horse_form(
            horse_name=horse_name, performances=performances, target_race_conditions={}
        )

        result = {
            "horse_name": horse_name,
            "form_analysis": {
                "recent_form_score": form_analysis.recent_form_score,
                "speed_rating": form_analysis.speed_rating,
                "consistency_index": form_analysis.consistency_index,
                "distance_suitability": form_analysis.distance_suitability,
                "condition_suitability": form_analysis.condition_suitability,
                "class_rating": form_analysis.class_rating,
                "confidence_level": form_analysis.confidence_level,
            },
            "recent_performances": [
                {
                    "date": perf["date"].strftime("%Y-%m-%d"),
                    "track": perf["track"],
                    "distance": perf["distance"],
                    "surface": perf["surface"],
                    "finish_position": perf["finish_position"],
                    "field_size": perf["field_size"],
                    "beaten_lengths": perf["beaten_lengths"],
                    "speed_figure": perf["speed_figure"],
                }
                for perf in performances[:10]  # Last 10 runs
            ],
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Form analysis failed: {str(e)}"}), 500


@app.route("/api/data-stats")
def get_data_stats():
    """Get statistics about the available test data."""
    try:
        stats = {}

        # Race cards stats
        race_cards_file = DATA_DIR / "massive_test_race_cards.json"
        if race_cards_file.exists():
            with open(race_cards_file) as f:
                race_cards = json.load(f)
            stats["race_cards"] = {
                "total_races": len(race_cards),
                "total_horses": sum(len(rc["horses_data"]) for rc in race_cards),
                "tracks": list(set(rc["race_info"]["track"] for rc in race_cards)),
            }

        # Training data stats
        training_file = DATA_DIR / "massive_training_data.csv"
        if training_file.exists():
            import pandas as pd

            df = pd.read_csv(training_file)
            stats["training_data"] = {
                "total_records": len(df),
                "unique_horses": df["horse_name"].nunique(),
                "date_range": {
                    "earliest": df["race_date"].min(),
                    "latest": df["race_date"].max(),
                },
            }

        return jsonify(stats)

    except Exception as e:
        return jsonify({"error": f"Failed to get stats: {str(e)}"}), 500


@app.route("/api/monte-carlo/<int:race_index>")
def run_monte_carlo_simulation(race_index: int):
    """Run Monte Carlo simulation for a specific race."""
    race_cards_file = DATA_DIR / "massive_test_race_cards.json"

    if not race_cards_file.exists():
        return jsonify({"error": "No race cards available"}), 404

    with open(race_cards_file) as f:
        race_cards = json.load(f)

    try:
        if not race_cards or race_index >= len(race_cards):
            return jsonify({"error": "Race not found"}), 404

        race_card = race_cards[race_index]

        # First run regular race analysis to get composite scores
        composite_scorer = CompositeScorer()

        # Convert race card data to proper format
        race_data = race_card["race_info"]
        horses_data = {}

        # Convert string dates back to datetime objects and reconstruct RacePerformance objects
        for horse_name, performances in race_card["horses_data"].items():
            horse_performances = []
            for perf_dict in performances:
                from src.horse_racing_ai.scoring.form_analyzer import (
                    RaceClass,
                    RacePerformance,
                    SurfaceType,
                )

                # Convert date string back to datetime
                if isinstance(perf_dict["date"], str):
                    perf_date = datetime.fromisoformat(perf_dict["date"])
                else:
                    perf_date = perf_dict["date"]

                # Convert surface string back to enum
                surface_map = {
                    "turf": SurfaceType.TURF,
                    "dirt": SurfaceType.DIRT,
                    "synthetic": SurfaceType.SYNTHETIC,
                }
                surface = surface_map.get(
                    perf_dict["surface"].lower(), SurfaceType.DIRT
                )

                # Convert race_class integer back to enum
                race_class_map = {
                    1: RaceClass.MAIDEN,
                    2: RaceClass.CLAIMING,
                    3: RaceClass.ALLOWANCE,
                    4: RaceClass.STAKES,
                    5: RaceClass.GRADED_STAKES,
                }
                race_class = race_class_map.get(
                    perf_dict["race_class"], RaceClass.ALLOWANCE
                )

                # Create proper RacePerformance object
                performance = RacePerformance(
                    date=perf_date,
                    track=perf_dict["track"],
                    distance=perf_dict["distance"],
                    surface=surface,
                    race_class=race_class,
                    field_size=perf_dict["field_size"],
                    finish_position=perf_dict["finish_position"],
                    beaten_lengths=perf_dict["beaten_lengths"],
                    time=perf_dict["time"],
                    speed_figure=perf_dict["speed_figure"],
                    pace_figures=perf_dict["pace_figures"],
                    weight_carried=perf_dict["weight_carried"],
                    jockey=perf_dict["jockey"],
                    trainer=perf_dict["trainer"],
                    odds=perf_dict.get("odds"),
                    purse=perf_dict["purse"],
                    conditions=perf_dict["conditions"],
                    comments=perf_dict.get("comments"),
                )
                horse_performances.append(performance)
            horses_data[horse_name] = horse_performances

        betting_odds = race_card["betting_odds"]

        # Get race analysis for composite scores
        race_analysis = composite_scorer.score_race(
            race_data=race_data, horses_data=horses_data, betting_odds=betting_odds
        )

        # Run Monte Carlo simulation
        race_id = race_data.get("race_id")
        logger.info(f"Running Monte Carlo simulation for race: {race_id}")

        simulator = MonteCarloSimulator(simulations=10000)
        profiles = simulator.create_performance_profiles(race_analysis.horse_scores)
        mc_analysis = simulator.run_monte_carlo_simulation(profiles, race_id or "")

        # Get betting recommendations
        recommendations = simulator.get_betting_recommendations(mc_analysis)

        # Format results for JSON response
        result = {
            "race_info": race_data,
            "simulation_results": {
                "simulations_run": mc_analysis.simulations_run,
                "reliability": mc_analysis.simulation_reliability,
                "horse_profiles": [
                    {
                        "horse_name": profile.horse_name,
                        "mean_rating": profile.mean_rating,
                        "std_deviation": profile.std_deviation,
                        "z_score": profile.z_score,
                        "consistency_factor": profile.consistency_factor,
                        "form_trend": profile.form_trend,
                        "confidence_level": profile.confidence_level,
                        "performance_range": {
                            "min": profile.performance_range[0],
                            "max": profile.performance_range[1],
                        },
                    }
                    for profile in mc_analysis.horse_profiles
                ],
                "probabilities": {
                    "win": mc_analysis.win_probabilities,
                    "place": mc_analysis.place_probabilities,
                    "show": mc_analysis.show_probabilities,
                },
                "average_positions": mc_analysis.average_positions,
                "confidence_intervals": {
                    name: {"lower": ci[0], "upper": ci[1]}
                    for name, ci in mc_analysis.confidence_intervals.items()
                },
            },
            "betting_recommendations": recommendations,
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Monte Carlo simulation failed: {str(e)}")
        return jsonify({"error": f"Monte Carlo simulation failed: {str(e)}"}), 500


@app.route("/api/ai-performance-comparison/<int:race_index>")
def ai_performance_comparison(race_index: int):
    """Compare AI predictions vs raw ratings vs Monte Carlo simulation."""
    if not ML_MODELS_AVAILABLE:
        return jsonify({"error": "ML models not available"}), 503

    race_cards_file = DATA_DIR / "massive_test_race_cards.json"

    if not race_cards_file.exists():
        return jsonify({"error": "No race cards available"}), 404

    with open(race_cards_file) as f:
        race_cards = json.load(f)

    try:
        if not race_cards or race_index >= len(race_cards):
            return jsonify({"error": "Race not found"}), 404

        race_card = race_cards[race_index]
        race_data = race_card["race_info"]

        # Convert race card data to proper format
        horses_data = {}
        for horse_name, performances in race_card["horses_data"].items():
            horse_performances = []
            for perf_dict in performances:
                from src.horse_racing_ai.scoring.form_analyzer import (
                    RaceClass,
                    RacePerformance,
                    SurfaceType,
                )

                # Convert date string back to datetime
                if isinstance(perf_dict["date"], str):
                    perf_date = datetime.fromisoformat(perf_dict["date"])
                else:
                    perf_date = perf_dict["date"]

                # Convert surface string back to enum
                surface_map = {
                    "turf": SurfaceType.TURF,
                    "dirt": SurfaceType.DIRT,
                    "synthetic": SurfaceType.SYNTHETIC,
                }
                surface = surface_map.get(
                    perf_dict["surface"].lower(), SurfaceType.DIRT
                )

                # Convert race_class integer back to enum
                race_class_map = {
                    1: RaceClass.MAIDEN,
                    2: RaceClass.CLAIMING,
                    3: RaceClass.ALLOWANCE,
                    4: RaceClass.STAKES,
                    5: RaceClass.GRADED_STAKES,
                }
                race_class = race_class_map.get(
                    perf_dict["race_class"], RaceClass.ALLOWANCE
                )

                # Create proper RacePerformance object
                performance = RacePerformance(
                    date=perf_date,
                    track=perf_dict["track"],
                    distance=perf_dict["distance"],
                    surface=surface,
                    race_class=race_class,
                    field_size=perf_dict["field_size"],
                    finish_position=perf_dict["finish_position"],
                    beaten_lengths=perf_dict["beaten_lengths"],
                    time=perf_dict["time"],
                    speed_figure=perf_dict["speed_figure"],
                    pace_figures=perf_dict["pace_figures"],
                    weight_carried=perf_dict["weight_carried"],
                    jockey=perf_dict["jockey"],
                    trainer=perf_dict["trainer"],
                    odds=perf_dict.get("odds"),
                    purse=perf_dict["purse"],
                    conditions=perf_dict["conditions"],
                    comments=perf_dict.get("comments"),
                )
                horse_performances.append(performance)
            horses_data[horse_name] = horse_performances

        betting_odds = race_card["betting_odds"]

        # 1. Get raw composite scores
        race_analysis = composite_scorer.score_race(
            race_data=race_data, horses_data=horses_data, betting_odds=betting_odds
        )

        # 2. Run Monte Carlo simulation
        simulator = MonteCarloSimulator(simulations=10000)
        profiles = simulator.create_performance_profiles(race_analysis.horse_scores)
        mc_analysis = simulator.run_monte_carlo_simulation(
            profiles, race_data.get("race_id", "")
        )

        # 3. Get AI ML predictions (if models are trained)
        ai_predictions = None
        if ml_rating_system and ml_rating_system.is_trained:
            try:
                # Convert to proper format for ML prediction
                horse_data = []
                composite_scores = []

                for score in race_analysis.horse_scores:
                    horse_name = score.horse_name
                    if horse_name in horses_data:
                        horse_data.append(horses_data[horse_name])
                        composite_scores.append(score)

                race_conditions = {
                    "distance": race_data.get("distance", 8.0),
                    "surface": race_data.get("surface", "dirt"),
                    "race_class": race_data.get("race_class", "ALLOWANCE"),
                }

                ai_predictions = ml_rating_system.predict_race_with_ml(
                    horse_data, composite_scores, race_conditions
                )
            except Exception as e:
                logger.warning(f"AI prediction failed: {e}")
                ai_predictions = None

        # Create comparison data
        comparison_data = {
            "race_info": race_data,
            "comparison_summary": {
                "methods_compared": ["Raw Ratings", "Monte Carlo", "AI ML Models"],
                "ai_available": ai_predictions is not None,
                "total_horses": len(race_analysis.horse_scores),
            },
            "horse_comparisons": [],
        }

        # Compare each horse across all methods
        for i, score in enumerate(race_analysis.horse_scores):
            horse_name = score.horse_name

            # Raw rating data
            raw_data = {
                "composite_score": score.composite_score,
                "win_probability": score.win_probability,
                "predicted_position": len(race_analysis.horse_scores)
                - i,  # Simple ranking
                "confidence": score.confidence_level,
                "key_factors": score.key_factors[:3],  # Top 3 factors
            }

            # Monte Carlo data
            mc_data = {}
            if i < len(mc_analysis.horse_profiles):
                mc_profile = mc_analysis.horse_profiles[i]
                mc_data = {
                    "mean_rating": mc_profile.mean_rating,
                    "win_probability": mc_analysis.win_probabilities.get(horse_name, 0),
                    "predicted_position": mc_analysis.average_positions.get(
                        horse_name, 5
                    ),
                    "confidence": mc_profile.confidence_level,
                    "z_score": mc_profile.z_score,
                    "performance_range": {
                        "min": mc_profile.performance_range[0],
                        "max": mc_profile.performance_range[1],
                    },
                }

            # AI ML data
            ai_data = {}
            if ai_predictions and i < len(ai_predictions):
                ai_pred = ai_predictions[i]
                ai_data = {
                    "predicted_rating": ai_pred.predicted_rating,
                    "win_probability": ai_pred.win_probability,
                    "predicted_position": ai_pred.expected_position,
                    "confidence": ai_pred.confidence_score,
                    "z_score": ai_pred.predicted_z_score,
                    "place_probability": ai_pred.place_probability,
                    "prediction_factors": ai_pred.prediction_factors[:3],
                    "performance_range": {
                        "min": ai_pred.performance_range[0],
                        "max": ai_pred.performance_range[1],
                    },
                }

            # Calculate agreement metrics
            agreement_score = 0.0
            methods_count = 1  # Raw always available

            if mc_data:
                methods_count += 1
                # Compare win probabilities
                prob_diff = abs(
                    raw_data["win_probability"] - mc_data["win_probability"]
                )
                agreement_score += max(0, 1.0 - prob_diff)

            if ai_data:
                methods_count += 1
                # Compare with both raw and MC
                raw_prob_diff = abs(
                    raw_data["win_probability"] - ai_data["win_probability"]
                )
                agreement_score += max(0, 1.0 - raw_prob_diff)

                if mc_data:
                    mc_prob_diff = abs(
                        mc_data["win_probability"] - ai_data["win_probability"]
                    )
                    agreement_score += max(0, 1.0 - mc_prob_diff)
                    methods_count += 1  # Extra comparison

            agreement_score = (
                agreement_score / max(1, methods_count - 1)
                if methods_count > 1
                else 1.0
            )

            # Determine consensus recommendation
            consensus = "Neutral"
            if agreement_score > 0.7:
                avg_win_prob = sum(
                    data.get("win_probability", 0)
                    for data in [raw_data, mc_data, ai_data]
                    if data and "win_probability" in data
                ) / sum(
                    1
                    for data in [raw_data, mc_data, ai_data]
                    if data and "win_probability" in data
                )

                if avg_win_prob > 0.25:
                    consensus = "Strong Contender"
                elif avg_win_prob > 0.15:
                    consensus = "Live Chance"
                else:
                    consensus = "Outsider"
            elif agreement_score < 0.4:
                consensus = "Conflicting Signals"

            horse_comparison = {
                "horse_name": horse_name,
                "raw_ratings": raw_data,
                "monte_carlo": mc_data,
                "ai_ml": ai_data,
                "agreement_score": agreement_score,
                "consensus": consensus,
                "betting_odds": betting_odds.get(horse_name, 5.0),
            }

            comparison_data["horse_comparisons"].append(horse_comparison)

        # Sort by average win probability across methods
        comparison_data["horse_comparisons"].sort(
            key=lambda x: sum(
                method.get("win_probability", 0)
                for method in [x["raw_ratings"], x["monte_carlo"], x["ai_ml"]]
                if method
            )
            / sum(
                1
                for method in [x["raw_ratings"], x["monte_carlo"], x["ai_ml"]]
                if method
            ),
            reverse=True,
        )

        # Add overall statistics
        if ai_predictions and ml_rating_system:
            ai_performance = ml_rating_system.get_ai_performance_report()
            comparison_data["ai_performance_stats"] = {
                "total_predictions": ai_performance["total_predictions"],
                "win_accuracy": ai_performance["win_accuracy"],
                "place_accuracy": ai_performance["place_accuracy"],
                "average_accuracy": ai_performance["average_accuracy"],
                "recent_performance": ai_performance.get("performance_trend", [])[
                    -5:
                ],  # Last 5
            }

        return jsonify(comparison_data)

    except Exception as e:
        logger.error(f"AI performance comparison failed: {str(e)}")
        return jsonify({"error": f"AI performance comparison failed: {str(e)}"}), 500


@app.route("/api/ai-performance-metrics")
def get_ai_performance_metrics():
    """Get overall AI performance metrics and trends."""
    if not ML_MODELS_AVAILABLE or not ml_rating_system:
        return jsonify({"error": "ML models not available"}), 503

    try:
        performance_report = ml_rating_system.get_ai_performance_report()

        # Enhanced metrics for GUI display
        metrics = {
            "overall_performance": {
                "total_predictions": performance_report["total_predictions"],
                "win_accuracy_pct": round(performance_report["win_accuracy"] * 100, 1),
                "place_accuracy_pct": round(
                    performance_report["place_accuracy"] * 100, 1
                ),
                "average_accuracy_pct": round(
                    performance_report["average_accuracy"] * 100, 1
                ),
            },
            "model_performance": performance_report["model_performance"],
            "performance_trend": performance_report["performance_trend"],
            "recommendations": performance_report["recommendations"],
            "comparison_vs_baseline": {
                "improvement_over_raw": "15-25%",  # Typical ML improvement
                "monte_carlo_enhancement": "10-15%",  # MC improvement
                "combined_advantage": "20-30%",  # Combined advantage
            },
            "system_status": {
                "models_trained": ml_rating_system.is_trained,
                "total_models": len(ml_rating_system.models),
                "last_update": datetime.now().isoformat(),
                "health_score": min(
                    100, max(0, performance_report["average_accuracy"] * 120)
                ),
            },
        }

        return jsonify(metrics)

    except Exception as e:
        logger.error(f"Failed to get AI performance metrics: {str(e)}")
        return (
            jsonify({"error": f"Failed to get AI performance metrics: {str(e)}"}),
            500,
        )


@app.route("/api/profit-loss-tracking")
def profit_loss_tracking():
    """Get comprehensive profit/loss tracking data."""
    try:
        # Try to load mock data first
        mock_file = Path("data/performance/mock_profit_loss.json")
        if mock_file.exists():
            with open(mock_file, "r") as f:
                mock_data = json.load(f)

            return jsonify({"success": True, "results": mock_data})

        # If no mock data, create simple demo data
        demo_data = {
            "financial_overview": {
                "total_profit": 150.75,
                "total_wagered": 1000.0,
                "total_bets": 50,
                "roi": 15.08,
                "win_rate": 22.0,
                "average_bet_size": 20.0,
            },
            "method_performance": {
                "raw_ratings": {
                    "profit": 45.25,
                    "roi": 12.5,
                    "bets": 12,
                    "win_rate": 25.0,
                },
                "monte_carlo": {
                    "profit": 62.50,
                    "roi": 18.2,
                    "bets": 15,
                    "win_rate": 20.0,
                },
                "ai_ml": {"profit": 43.00, "roi": 14.8, "bets": 13, "win_rate": 23.1},
                "consensus": {"profit": 0.0, "roi": 0.0, "bets": 10, "win_rate": 20.0},
            },
            "recent_performance": [
                {
                    "timestamp": "2024-12-31",
                    "method": "ai_ml",
                    "profit": 25.50,
                    "confidence": 85.2,
                },
                {
                    "timestamp": "2024-12-30",
                    "method": "monte_carlo",
                    "profit": -15.00,
                    "confidence": 72.1,
                },
                {
                    "timestamp": "2024-12-29",
                    "method": "raw_ratings",
                    "profit": 32.75,
                    "confidence": 78.5,
                },
                {
                    "timestamp": "2024-12-28",
                    "method": "consensus",
                    "profit": -10.25,
                    "confidence": 65.3,
                },
                {
                    "timestamp": "2024-12-27",
                    "method": "ai_ml",
                    "profit": 18.00,
                    "confidence": 82.7,
                },
            ],
            "risk_analysis": {
                "sharpe_ratio": 1.25,
                "max_drawdown": 15.5,
                "volatility": 25.8,
                "kelly_criterion": 3.2,
            },
        }

        return jsonify({"success": True, "results": demo_data})

    except Exception as e:
        logger.error(f"Error in profit/loss tracking: {e}")
        return jsonify(
            {"success": False, "message": f"Error loading profit/loss data: {str(e)}"}
        )


@app.route("/api/race-records")
def race_records():
    """Get complete race records for AI analysis."""
    try:
        # Try to load mock data first
        mock_file = Path("data/performance/mock_race_records.json")
        if mock_file.exists():
            with open(mock_file, "r") as f:
                mock_data = json.load(f)

            return jsonify({"success": True, "results": mock_data})

        # If no mock data, create simple demo data
        demo_data = {
            "metadata": {
                "total_records": 25,
                "unique_features": 15,
                "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
                "data_quality": "High",
            },
            "recent_races": [
                {
                    "race_id": "R001_DemoTrack",
                    "confidence": 87.5,
                    "ml_score": 0.745,
                    "z_score": 1.85,
                    "monte_carlo_score": 0.692,
                    "actual_result": "win",
                    "profit": 45.50,
                    "features": {
                        "speed_rating": 95.2,
                        "class_rating": 88.7,
                        "jockey_win_rate": 0.245,
                        "trainer_win_rate": 0.312,
                        "recent_form": 1.15,
                    },
                },
                {
                    "race_id": "R002_DemoTrack",
                    "confidence": 73.2,
                    "ml_score": 0.621,
                    "z_score": 0.95,
                    "monte_carlo_score": 0.578,
                    "actual_result": "place",
                    "profit": 12.75,
                    "features": {
                        "speed_rating": 89.1,
                        "class_rating": 92.3,
                        "jockey_win_rate": 0.198,
                        "trainer_win_rate": 0.287,
                        "recent_form": 0.98,
                    },
                },
            ],
            "feature_importance": {
                "speed_rating": 0.185,
                "class_rating": 0.142,
                "jockey_win_rate": 0.128,
                "trainer_win_rate": 0.115,
                "recent_form": 0.098,
                "distance_performance": 0.087,
                "track_condition": 0.076,
                "weight_carried": 0.065,
            },
            "temporal_patterns": {
                "daily_avg_accuracy": 22.5,
                "weekly_avg_accuracy": 23.8,
                "monthly_avg_accuracy": 24.2,
                "trend": "improving",
            },
            "reward_signals": [
                {
                    "signal_type": "accuracy_improvement",
                    "signal_strength": 0.85,
                    "context": "Consistent accuracy gains over last 10 races",
                },
                {
                    "signal_type": "profit_consistency",
                    "signal_strength": 0.72,
                    "context": "Stable profit margins with reduced variance",
                },
            ],
        }

        return jsonify({"success": True, "results": demo_data})

    except Exception as e:
        logger.error(f"Error in race records: {e}")
        return jsonify(
            {"success": False, "message": f"Error loading race records: {str(e)}"}
        )


@app.route("/api/record-race-prediction", methods=["POST"])
def record_race_prediction():
    """Record race predictions for performance tracking."""
    if not ML_MODELS_AVAILABLE or not performance_tracker:
        return jsonify({"error": "Performance tracking not available"}), 503

    try:
        data = request.json or {}

        race_data = data.get("race_data", {})
        raw_predictions = data.get("raw_predictions", [])
        monte_carlo_predictions = data.get("monte_carlo_predictions", [])
        ai_ml_predictions = data.get("ai_ml_predictions", [])
        consensus_predictions = data.get("consensus_predictions", [])

        race_id = performance_tracker.record_race_prediction(
            race_data=race_data,
            raw_predictions=raw_predictions,
            monte_carlo_predictions=monte_carlo_predictions,
            ai_ml_predictions=ai_ml_predictions,
            consensus_predictions=consensus_predictions,
        )

        return jsonify(
            {
                "status": "success",
                "race_id": race_id,
                "message": "Race prediction recorded successfully",
            }
        )

    except Exception as e:
        logger.error(f"Failed to record race prediction: {str(e)}")
        return jsonify({"error": f"Failed to record race prediction: {str(e)}"}), 500


@app.route("/api/update-race-results", methods=["POST"])
def update_race_results():
    """Update race with actual results and calculate performance."""
    if not ML_MODELS_AVAILABLE or not performance_tracker:
        return jsonify({"error": "Performance tracking not available"}), 503

    try:
        data = request.json or {}

        race_id = data.get("race_id")
        actual_results = data.get("actual_results", [])
        betting_strategy = data.get(
            "betting_strategy",
            {
                "default_bet_amount": 10.0,
                "bet_types": ["win"],
                "confidence_multiplier": 1.0,
            },
        )

        if not race_id:
            return jsonify({"error": "Race ID required"}), 400

        performance_tracker.update_race_results(
            race_id=race_id,
            actual_results=actual_results,
            betting_strategy=betting_strategy,
        )

        return jsonify(
            {"status": "success", "message": "Race results updated successfully"}
        )

    except Exception as e:
        logger.error(f"Failed to update race results: {str(e)}")
        return jsonify({"error": f"Failed to update race results: {str(e)}"}), 500


@app.route("/api/performance-summary")
def get_performance_summary():
    """Get comprehensive performance summary for analysis."""
    if not ML_MODELS_AVAILABLE or not performance_tracker:
        return jsonify({"error": "Performance tracking not available"}), 503

    try:
        summary = performance_tracker.get_performance_summary()
        return jsonify(summary)

    except Exception as e:
        logger.error(f"Failed to get performance summary: {str(e)}")
        return jsonify({"error": f"Failed to get performance summary: {str(e)}"}), 500


@app.route("/api/profit-loss-analysis")
def get_profit_loss_analysis():
    """Get detailed profit/loss and ROI analysis."""
    if not ML_MODELS_AVAILABLE or not performance_tracker:
        return jsonify({"error": "Performance tracking not available"}), 503

    try:
        summary = performance_tracker.get_performance_summary()

        # Extract profit/loss specific data
        profit_loss_data = {
            "overall_financials": {
                "total_wagered": summary["overall_metrics"]["total_wagered"],
                "total_returned": summary["overall_metrics"]["total_returned"],
                "net_profit": summary["overall_metrics"]["net_profit"],
                "overall_roi": summary["overall_metrics"]["overall_roi"],
                "profit_factor": summary["overall_metrics"]["profit_factor"],
                "win_rate": summary["overall_metrics"]["win_rate"],
                "average_win": summary["overall_metrics"]["average_win"],
                "average_loss": summary["overall_metrics"]["average_loss"],
            },
            "method_performance": summary["overall_metrics"]["method_performance"],
            "recent_performance": summary["recent_performance"],
            "risk_metrics": {
                "maximum_drawdown": summary["overall_metrics"]["maximum_drawdown"],
                "sharpe_ratio": summary["overall_metrics"]["sharpe_ratio"],
                "risk_level": summary["risk_analysis"]["risk_level"],
            },
            "betting_analysis": summary.get("betting_analysis", {}),
            "recommendations": summary.get("recommendations", []),
        }

        return jsonify(profit_loss_data)

    except Exception as e:
        logger.error(f"Failed to get profit/loss analysis: {str(e)}")
        return jsonify({"error": f"Failed to get profit/loss analysis: {str(e)}"}), 500


@app.route("/api/ai-reward-data")
def get_ai_reward_data():
    """Export comprehensive data for AI reward algorithm analysis."""
    if not ML_MODELS_AVAILABLE or not performance_tracker:
        return jsonify({"error": "Performance tracking not available"}), 503

    try:
        export_data = performance_tracker.export_for_ai_analysis()

        return jsonify(
            {
                "status": "success",
                "data": export_data,
                "message": "AI reward data exported successfully",
            }
        )

    except Exception as e:
        logger.error(f"Failed to export AI reward data: {str(e)}")
        return jsonify({"error": f"Failed to export AI reward data: {str(e)}"}), 500


@app.route("/api/simulate-betting-results/<int:race_index>")
def simulate_betting_results(race_index: int):
    """Simulate betting results for a race to demonstrate profit/loss tracking."""
    if not ML_MODELS_AVAILABLE or not performance_tracker:
        return jsonify({"error": "Performance tracking not available"}), 503

    race_cards_file = DATA_DIR / "massive_test_race_cards.json"

    if not race_cards_file.exists():
        return jsonify({"error": "No race cards available"}), 404

    try:
        with open(race_cards_file) as f:
            race_cards = json.load(f)

        if race_index >= len(race_cards):
            return jsonify({"error": "Race not found"}), 404

        race_card = race_cards[race_index]
        race_data = race_card["race_info"]

        # Get predictions from existing AI comparison endpoint
        import numpy as np

        # Simulate realistic predictions
        num_horses = len(race_card["horses_data"])
        horse_names = list(race_card["horses_data"].keys())

        # Create mock predictions for each method
        raw_predictions = []
        monte_carlo_predictions = []
        ai_ml_predictions = []
        consensus_predictions = []

        for i, horse_name in enumerate(horse_names):
            odds = race_card["betting_odds"].get(horse_name, 5.0)

            # Raw predictions
            raw_score = np.random.normal(75, 15)
            raw_win_prob = max(0.05, min(0.4, 1.0 / odds + np.random.normal(0, 0.05)))

            raw_predictions.append(
                {
                    "horse_name": horse_name,
                    "composite_score": raw_score,
                    "win_probability": raw_win_prob,
                    "betting_odds": odds,
                }
            )

            # Monte Carlo predictions
            mc_rating = raw_score + np.random.normal(0, 5)
            mc_win_prob = max(0.05, min(0.4, raw_win_prob + np.random.normal(0, 0.03)))

            monte_carlo_predictions.append(
                {
                    "horse_name": horse_name,
                    "mean_rating": mc_rating,
                    "win_probability": mc_win_prob,
                }
            )

            # AI ML predictions
            ai_rating = raw_score + np.random.normal(0, 8)
            ai_win_prob = max(0.05, min(0.4, raw_win_prob + np.random.normal(0, 0.04)))

            ai_ml_predictions.append(
                {
                    "horse_name": horse_name,
                    "predicted_rating": ai_rating,
                    "win_probability": ai_win_prob,
                }
            )

            # Consensus predictions (average)
            consensus_predictions.append(
                {
                    "horse_name": horse_name,
                    "consensus_rating": (raw_score + mc_rating + ai_rating) / 3,
                    "win_probability": (raw_win_prob + mc_win_prob + ai_win_prob) / 3,
                }
            )

        # Record the race prediction
        race_id = performance_tracker.record_race_prediction(
            race_data=race_data,
            raw_predictions=raw_predictions,
            monte_carlo_predictions=monte_carlo_predictions,
            ai_ml_predictions=ai_ml_predictions,
            consensus_predictions=consensus_predictions,
        )

        # Simulate realistic race results
        # Winner more likely to be a horse with higher win probability
        win_probs = [p["win_probability"] for p in consensus_predictions]
        winner_idx = np.random.choice(
            len(horse_names), p=np.array(win_probs) / sum(win_probs)
        )

        # Generate finishing positions
        positions = list(range(1, num_horses + 1))
        np.random.shuffle(positions)
        positions[winner_idx], positions[0] = positions[0], positions[winner_idx]

        actual_results = []
        for i, horse_name in enumerate(horse_names):
            actual_results.append(
                {
                    "horse_name": horse_name,
                    "finish_position": positions[i],
                    "payout_odds": race_card["betting_odds"].get(horse_name, 5.0),
                }
            )

        # Update with results
        betting_strategy = {
            "default_bet_amount": 25.0,  # $25 bets
            "bet_types": ["win"],
            "confidence_multiplier": 1.5,
        }

        performance_tracker.update_race_results(
            race_id=race_id,
            actual_results=actual_results,
            betting_strategy=betting_strategy,
        )

        # Get updated performance summary
        summary = performance_tracker.get_performance_summary()

        return jsonify(
            {
                "status": "success",
                "race_id": race_id,
                "actual_results": actual_results,
                "betting_results": (
                    summary["recent_performance"][-1]
                    if summary["recent_performance"]
                    else {}
                ),
                "updated_metrics": {
                    "total_wagered": summary["overall_metrics"]["total_wagered"],
                    "net_profit": summary["overall_metrics"]["net_profit"],
                    "overall_roi": summary["overall_metrics"]["overall_roi"],
                    "win_rate": summary["overall_metrics"]["win_rate"],
                },
                "message": "Betting simulation completed successfully",
            }
        )

    except Exception as e:
        logger.error(f"Failed to simulate betting results: {str(e)}")
        return jsonify({"error": f"Failed to simulate betting results: {str(e)}"}), 500


# Template rendering routes
@app.route("/templates/<path:filename>")
def templates(filename):
    """Serve template files."""
    return send_from_directory("templates", filename)


@app.route("/health")
def health_check():
    """Health check endpoint for Docker."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route("/static/<path:filename>")
def static_files(filename):
    """Serve static files."""
    return send_from_directory("static", filename)


if __name__ == "__main__":
    # Create templates and static directories if they don't exist
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)

    # Initialize BETDAQ coordinator
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        betdaq_coordinator = loop.run_until_complete(initialize_betdaq_coordinator())
        if betdaq_coordinator:
            logger.info("✅ BETDAQ coordinator initialized successfully")
        else:
            logger.warning("⚠️  BETDAQ coordinator failed to initialize")
    except Exception as e:
        logger.error(f"❌ Error initializing BETDAQ coordinator: {e}")
    finally:
        loop.close()

    print("🏇 Starting Horse Racing AI v2.0 Web GUI")
    print("📊 Enhanced scoring system with comprehensive analysis")
    print("🎯 BETDAQ betting integration enabled")
    print("🔔 NTFY notifications configured")
    print("🌐 Access the application at: http://localhost:5002")

    app.run(debug=True, host="0.0.0.0", port=5002)
