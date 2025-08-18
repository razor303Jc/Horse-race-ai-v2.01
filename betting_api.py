#!/usr/bin/env python3
"""
💰 Stage 8 Betting API Integration

FastAPI endpoints for the React betting dashboard, integrating with
the Stage 8 betting integration system.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Setup logging
logger = logging.getLogger(__name__)

# Create betting router
betting_router = APIRouter(prefix="/api/betting", tags=["betting"])


# Data models
class BettingRecommendation(BaseModel):
    horse_name: str
    selection_id: int
    market_id: int
    confidence: float
    predicted_odds: float
    current_odds: float
    value: float
    stake_recommendation: float
    recommended_action: str


class PaperBet(BaseModel):
    bet_id: str
    horse_name: str
    stake: float
    odds: float
    status: str
    pnl: float
    timestamp: str


class BettingPerformance(BaseModel):
    account_balance: float
    daily_pnl: float
    win_rate: float
    roi: float
    total_bets: int
    active_bets: int
    winning_bets: int


class PlaceBetRequest(BaseModel):
    horse_name: str
    stake: float
    odds: float
    confidence: float


# Helper functions
def load_stage8_data() -> Dict:
    """Load Stage 8 integration data"""
    try:
        models_dir = Path("/app/models")
        summary_path = models_dir / "stage8_integration_summary.json"

        if summary_path.exists():
            with open(summary_path, "r") as f:
                return json.load(f)
        else:
            # Return default data if file doesn't exist
            return {
                "paper_trading_performance": {
                    "account_balance": 1000.0,
                    "daily_pnl": 0.0,
                    "win_rate": 0.0,
                    "roi": 0.0,
                    "total_bets": 0,
                    "active_bets": 0,
                    "winning_bets": 0,
                },
                "betting_configuration": {"mode": "paper_trading", "enabled": True},
            }
    except Exception as e:
        logger.error(f"Failed to load Stage 8 data: {e}")
        return {}


def save_stage8_data(data: Dict) -> bool:
    """Save Stage 8 integration data"""
    try:
        models_dir = Path("/app/models")
        models_dir.mkdir(exist_ok=True)
        summary_path = models_dir / "stage8_integration_summary.json"

        with open(summary_path, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save Stage 8 data: {e}")
        return False


# API Endpoints


@betting_router.get("/recommendations", response_model=List[BettingRecommendation])
async def get_betting_recommendations():
    """Get current betting recommendations from Stage 8"""
    try:
        # Generate sample recommendations - in production, this would come from Stage 8
        recommendations = [
            BettingRecommendation(
                horse_name="Thunder Strike",
                selection_id=12345,
                market_id=67890,
                confidence=0.85,
                predicted_odds=3.0,
                current_odds=3.5,
                value=0.12,
                stake_recommendation=8.5,
                recommended_action="BACK",
            ),
            BettingRecommendation(
                horse_name="Lightning Bolt",
                selection_id=12346,
                market_id=67891,
                confidence=0.78,
                predicted_odds=3.8,
                current_odds=4.2,
                value=0.08,
                stake_recommendation=6.2,
                recommended_action="BACK",
            ),
            BettingRecommendation(
                horse_name="Storm Chaser",
                selection_id=12347,
                market_id=67892,
                confidence=0.72,
                predicted_odds=4.8,
                current_odds=5.1,
                value=0.04,
                stake_recommendation=4.1,
                recommended_action="SKIP",
            ),
        ]

        # Filter out SKIP recommendations
        active_recommendations = [
            r for r in recommendations if r.recommended_action != "SKIP"
        ]

        return active_recommendations

    except Exception as e:
        logger.error(f"Failed to get betting recommendations: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to load betting recommendations"
        )


@betting_router.get("/performance", response_model=BettingPerformance)
async def get_betting_performance():
    """Get current betting performance metrics"""
    try:
        stage8_data = load_stage8_data()
        perf_data = stage8_data.get("paper_trading_performance", {})

        return BettingPerformance(
            account_balance=perf_data.get("account_balance", 1000.0),
            daily_pnl=perf_data.get("daily_pnl", 0.0),
            win_rate=perf_data.get("win_rate", 0.0),
            roi=perf_data.get("roi", 0.0),
            total_bets=perf_data.get("total_bets", 0),
            active_bets=perf_data.get("active_bets", 0),
            winning_bets=perf_data.get("winning_bets", 0),
        )

    except Exception as e:
        logger.error(f"Failed to get betting performance: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to load betting performance"
        )


@betting_router.get("/active-bets", response_model=List[PaperBet])
async def get_active_bets():
    """Get current active bets"""
    try:
        # In production, this would load from Stage 8 betting system
        active_bets = [
            PaperBet(
                bet_id="bet_001",
                horse_name="Thunder Strike",
                stake=8.5,
                odds=3.5,
                status="active",
                pnl=0.0,
                timestamp=datetime.now().isoformat(),
            )
        ]

        return active_bets

    except Exception as e:
        logger.error(f"Failed to get active bets: {e}")
        raise HTTPException(status_code=500, detail="Failed to load active bets")


@betting_router.post("/place-bet")
async def place_bet(bet_request: PlaceBetRequest):
    """Place a paper trading bet"""
    try:
        # Load current Stage 8 data
        stage8_data = load_stage8_data()
        perf_data = stage8_data.get("paper_trading_performance", {})

        # Check if betting is enabled
        config = stage8_data.get("betting_configuration", {})
        if not config.get("enabled", False):
            raise HTTPException(status_code=400, detail="Betting is currently disabled")

        # Check account balance
        current_balance = perf_data.get("account_balance", 1000.0)
        if bet_request.stake > current_balance:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        # Create new bet
        bet_id = f"bet_{int(datetime.now().timestamp())}"
        new_bet = {
            "bet_id": bet_id,
            "horse_name": bet_request.horse_name,
            "stake": bet_request.stake,
            "odds": bet_request.odds,
            "confidence": bet_request.confidence,
            "status": "placed",
            "pnl": 0.0,
            "timestamp": datetime.now().isoformat(),
        }

        # Update performance data
        updated_perf = {
            **perf_data,
            "account_balance": current_balance - bet_request.stake,
            "total_bets": perf_data.get("total_bets", 0) + 1,
            "active_bets": perf_data.get("active_bets", 0) + 1,
        }

        # Save updated data
        stage8_data["paper_trading_performance"] = updated_perf
        save_stage8_data(stage8_data)

        logger.info(
            f"Paper bet placed: {bet_id} - {bet_request.horse_name} - £{bet_request.stake}"
        )

        return {
            "success": True,
            "bet_id": bet_id,
            "message": f"Paper bet placed on {bet_request.horse_name}",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to place bet: {e}")
        raise HTTPException(status_code=500, detail="Failed to place bet")


@betting_router.get("/config")
async def get_betting_config():
    """Get current betting configuration"""
    try:
        stage8_data = load_stage8_data()
        config = stage8_data.get("betting_configuration", {})

        return {
            "enabled": config.get("enabled", False),
            "mode": config.get("mode", "paper_trading"),
            "max_stake_per_bet": config.get("max_stake_per_bet", 10.0),
            "max_daily_loss": config.get("max_daily_loss", 50.0),
            "min_confidence": config.get("min_confidence", 0.75),
            "risk_management": config.get("risk_management", "enabled"),
        }

    except Exception as e:
        logger.error(f"Failed to get betting config: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to load betting configuration"
        )


@betting_router.post("/emergency-stop")
async def emergency_stop():
    """Trigger emergency stop for all betting"""
    try:
        stage8_data = load_stage8_data()
        config = stage8_data.get("betting_configuration", {})
        config["enabled"] = False
        config["emergency_stop"] = True

        stage8_data["betting_configuration"] = config
        save_stage8_data(stage8_data)

        logger.warning("Emergency stop activated - all betting disabled")

        return {
            "success": True,
            "message": "Emergency stop activated - all betting disabled",
        }

    except Exception as e:
        logger.error(f"Failed to activate emergency stop: {e}")
        raise HTTPException(status_code=500, detail="Failed to activate emergency stop")


@betting_router.get("/status")
async def get_betting_status():
    """Get overall betting system status"""
    try:
        stage8_data = load_stage8_data()

        return {
            "stage8_operational": True,
            "paper_trading_active": True,
            "betting_enabled": stage8_data.get("betting_configuration", {}).get(
                "enabled", False
            ),
            "emergency_stop": stage8_data.get("betting_configuration", {}).get(
                "emergency_stop", False
            ),
            "last_updated": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get betting status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get betting status")
