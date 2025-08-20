"""
Betting API endpoints for BetDaq integration.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel

from ...services.betdaq_client import get_betdaq_client, BetRequest, BetType
from ...services.betting_engine import (
    get_betting_engine, BettingConfiguration, BettingStrategy, 
    RiskLevel, BettingOpportunity
)
from ...core.config import get_settings

router = APIRouter()
settings = get_settings()


class BettingConfigRequest(BaseModel):
    """Request model for betting configuration."""
    strategy: BettingStrategy
    risk_level: RiskLevel
    max_stake_per_bet: float
    max_total_exposure: float
    max_daily_loss: float
    min_odds: float = 1.5
    max_odds: float = 10.0


class BetPlacementRequest(BaseModel):
    """Request model for placing a bet."""
    market_id: int
    selection_id: int
    bet_type: BetType
    price: float
    stake: float


class MarketResponse(BaseModel):
    """Response model for betting markets."""
    market_id: int
    market_name: str
    event_name: str
    start_time: datetime
    status: str
    total_matched: Optional[float]
    selections: List[dict]


@router.get("/health")
async def betting_health_check():
    """Check BetDaq API connectivity."""
    if not settings.betting_enabled:
        raise HTTPException(status_code=503, detail="Betting is disabled")
    
    try:
        betdaq = await get_betdaq_client()
        healthy = await betdaq.health_check()
        
        return {
            "status": "healthy" if healthy else "unhealthy",
            "betdaq_connected": healthy,
            "betting_enabled": settings.betting_enabled
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/markets", response_model=List[MarketResponse])
async def get_betting_markets():
    """Get available betting markets for horse racing."""
    if not settings.betting_enabled:
        raise HTTPException(status_code=503, detail="Betting is disabled")
    
    try:
        betdaq = await get_betdaq_client()
        markets = await betdaq.get_markets("horse_racing")
        
        return [
            MarketResponse(
                market_id=market.market_id,
                market_name=market.market_name,
                event_name=market.event_name,
                start_time=market.start_time,
                status=market.status.value,
                total_matched=float(market.total_matched) if market.total_matched else None,
                selections=[
                    {
                        "selection_id": sel.selection_id,
                        "selection_name": sel.selection_name,
                        "back_price": float(sel.back_price) if sel.back_price else None,
                        "lay_price": float(sel.lay_price) if sel.lay_price else None,
                        "back_size": float(sel.back_size) if sel.back_size else None,
                        "lay_size": float(sel.lay_size) if sel.lay_size else None,
                    }
                    for sel in market.selections
                ]
            )
            for market in markets
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get markets: {str(e)}")


@router.get("/markets/{market_id}/prices")
async def get_market_prices(market_id: int):
    """Get current prices for a specific market."""
    if not settings.betting_enabled:
        raise HTTPException(status_code=503, detail="Betting is disabled")
    
    try:
        betdaq = await get_betdaq_client()
        market = await betdaq.get_market_prices(market_id)
        
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")
        
        return {
            "market_id": market.market_id,
            "market_name": market.market_name,
            "event_name": market.event_name,
            "start_time": market.start_time,
            "status": market.status.value,
            "in_play": market.in_play,
            "selections": [
                {
                    "selection_id": sel.selection_id,
                    "selection_name": sel.selection_name,
                    "back_price": float(sel.back_price) if sel.back_price else None,
                    "lay_price": float(sel.lay_price) if sel.lay_price else None,
                    "back_size": float(sel.back_size) if sel.back_size else None,
                    "lay_size": float(sel.lay_size) if sel.lay_size else None,
                    "last_traded_price": float(sel.last_traded_price) if sel.last_traded_price else None,
                    "total_matched": float(sel.total_matched) if sel.total_matched else None,
                }
                for sel in market.selections
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get market prices: {str(e)}")


@router.post("/configure")
async def configure_betting_engine(config: BettingConfigRequest):
    """Configure the betting engine with strategy and risk parameters."""
    if not settings.betting_enabled:
        raise HTTPException(status_code=503, detail="Betting is disabled")
    
    try:
        betting_config = BettingConfiguration(
            strategy=config.strategy,
            risk_level=config.risk_level,
            max_stake_per_bet=Decimal(str(config.max_stake_per_bet)),
            max_total_exposure=Decimal(str(config.max_total_exposure)),
            max_daily_loss=Decimal(str(config.max_daily_loss)),
            min_odds=Decimal(str(config.min_odds)),
            max_odds=Decimal(str(config.max_odds))
        )
        
        betting_engine = get_betting_engine(betting_config)
        
        return {
            "status": "configured",
            "strategy": config.strategy.value,
            "risk_level": config.risk_level.value,
            "max_stake_per_bet": config.max_stake_per_bet,
            "max_total_exposure": config.max_total_exposure
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure betting engine: {str(e)}")


@router.post("/session/start")
async def start_betting_session():
    """Start a new betting session."""
    if not settings.betting_enabled:
        raise HTTPException(status_code=503, detail="Betting is disabled")
    
    try:
        betting_engine = get_betting_engine()
        if not betting_engine:
            raise HTTPException(status_code=400, detail="Betting engine not configured")
        
        session_id = await betting_engine.start_session()
        
        return {
            "session_id": session_id,
            "status": "started",
            "start_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@router.post("/session/end")
async def end_betting_session():
    """End the current betting session."""
    if not settings.betting_enabled:
        raise HTTPException(status_code=503, detail="Betting is disabled")
    
    try:
        betting_engine = get_betting_engine()
        if not betting_engine:
            raise HTTPException(status_code=400, detail="Betting engine not configured")
        
        session = await betting_engine.end_session()
        
        if not session:
            raise HTTPException(status_code=400, detail="No active session")
        
        return {
            "session_id": session.session_id,
            "status": "ended",
            "duration_minutes": (session.end_time - session.start_time).total_seconds() / 60,
            "total_stakes": float(session.total_stakes),
            "total_winnings": float(session.total_winnings),
            "net_profit": float(session.net_profit),
            "bets_placed": len(session.bets_placed),
            "success_rate": session.success_rate
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")


@router.get("/opportunities")
async def analyze_betting_opportunities():
    """Analyze current markets for betting opportunities."""
    if not settings.betting_enabled:
        raise HTTPException(status_code=503, detail="Betting is disabled")
    
    try:
        betting_engine = get_betting_engine()
        if not betting_engine:
            raise HTTPException(status_code=400, detail="Betting engine not configured")
        
        opportunities = await betting_engine.analyze_markets()
        
        return {
            "opportunities_found": len(opportunities),
            "opportunities": [
                {
                    "race_id": opp.race_id,
                    "horse_name": opp.horse_name,
                    "market_id": opp.market_id,
                    "selection_id": opp.selection_id,
                    "bet_type": opp.recommended_bet_type.value,
                    "odds": float(opp.recommended_odds),
                    "stake": float(opp.recommended_stake),
                    "confidence_score": opp.confidence_score,
                    "value_percentage": opp.value_percentage,
                    "reasoning": opp.reasoning
                }
                for opp in opportunities[:10]  # Limit to top 10
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze opportunities: {str(e)}")


@router.post("/opportunities/{opportunity_index}/execute")
async def execute_betting_opportunity(opportunity_index: int):
    """Execute a specific betting opportunity."""
    if not settings.betting_enabled:
        raise HTTPException(status_code=503, detail="Betting is disabled")
    
    try:
        betting_engine = get_betting_engine()
        if not betting_engine:
            raise HTTPException(status_code=400, detail="Betting engine not configured")
        
        # Get current opportunities
        opportunities = await betting_engine.analyze_markets()
        
        if opportunity_index >= len(opportunities):
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        opportunity = opportunities[opportunity_index]
        placed_bet = await betting_engine.execute_opportunity(opportunity)
        
        if not placed_bet:
            raise HTTPException(status_code=400, detail="Failed to place bet")
        
        return {
            "bet_id": placed_bet.bet_id,
            "status": "placed",
            "market_id": placed_bet.market_id,
            "selection_id": placed_bet.selection_id,
            "bet_type": placed_bet.bet_type.value,
            "price": float(placed_bet.price),
            "stake": float(placed_bet.stake),
            "matched_stake": float(placed_bet.matched_stake),
            "remaining_stake": float(placed_bet.remaining_stake),
            "placed_time": placed_bet.placed_time
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute opportunity: {str(e)}")


@router.post("/bets/place")
async def place_manual_bet(bet_request: BetPlacementRequest):
    """Place a manual bet."""
    if not settings.betting_enabled:
        raise HTTPException(status_code=503, detail="Betting is disabled")
    
    try:
        betdaq = await get_betdaq_client()
        
        bet = BetRequest(
            market_id=bet_request.market_id,
            selection_id=bet_request.selection_id,
            bet_type=bet_request.bet_type,
            price=Decimal(str(bet_request.price)),
            stake=Decimal(str(bet_request.stake))
        )
        
        placed_bet = await betdaq.place_bet(bet)
        
        if not placed_bet:
            raise HTTPException(status_code=400, detail="Failed to place bet")
        
        return {
            "bet_id": placed_bet.bet_id,
            "status": "placed",
            "market_id": placed_bet.market_id,
            "selection_id": placed_bet.selection_id,
            "bet_type": placed_bet.bet_type.value,
            "price": float(placed_bet.price),
            "stake": float(placed_bet.stake),
            "matched_stake": float(placed_bet.matched_stake),
            "remaining_stake": float(placed_bet.remaining_stake),
            "placed_time": placed_bet.placed_time
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to place bet: {str(e)}")


@router.get("/account/balance")
async def get_account_balance():
    """Get BetDaq account balance."""
    if not settings.betting_enabled:
        raise HTTPException(status_code=503, detail="Betting is disabled")
    
    try:
        betdaq = await get_betdaq_client()
        balance = await betdaq.get_account_balance()
        
        if not balance:
            raise HTTPException(status_code=500, detail="Failed to get balance")
        
        return balance
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get balance: {str(e)}")


@router.get("/bets/history")
async def get_bet_history(days: int = Query(default=7, description="Number of days to look back")):
    """Get betting history."""
    if not settings.betting_enabled:
        raise HTTPException(status_code=503, detail="Betting is disabled")
    
    try:
        betdaq = await get_betdaq_client()
        from_date = datetime.now() - timedelta(days=days)
        
        bets = await betdaq.get_bet_history(from_date)
        
        return {
            "total_bets": len(bets),
            "period_days": days,
            "bets": [
                {
                    "bet_id": bet.bet_id,
                    "market_id": bet.market_id,
                    "selection_id": bet.selection_id,
                    "bet_type": bet.bet_type.value,
                    "price": float(bet.price),
                    "stake": float(bet.stake),
                    "matched_stake": float(bet.matched_stake),
                    "remaining_stake": float(bet.remaining_stake),
                    "status": bet.status.value,
                    "placed_time": bet.placed_time
                }
                for bet in bets
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bet history: {str(e)}")


@router.get("/performance")
async def get_betting_performance():
    """Get betting performance statistics."""
    try:
        betting_engine = get_betting_engine()
        if not betting_engine:
            return {"status": "not_configured", "message": "Betting engine not configured"}
        
        performance = await betting_engine.get_performance_summary()
        
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance: {str(e)}")
