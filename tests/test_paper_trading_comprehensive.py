"""
Comprehensive paper trading test suite for BETDAQ integration.

This module tests the complete paper trading system including:
- High confidence betting scenarios
- Mixed confidence level handling
- Value betting with filters
- Stake calculation systems
- Performance tracking
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import pytest
import pytest_asyncio

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from betdaq.betdaq_betting_coordinator import BettingCoordinator, TradingMode
from betdaq.betdaq_client import (
    BetdaqClient,
    BetdaqConfig,
    BetOrder,
    BettingSide,
    MarketInfo,
)
from betdaq.betdaq_paper_trading import PaperTradingConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def paper_trading_coordinator():
    """Create and configure the paper trading coordinator for testing."""
    # Create client config
    config = BetdaqConfig(
        username="test_user", password="test_pass", paper_trading=True
    )

    # Create client
    client = BetdaqClient(config)

    # Create coordinator in paper trading mode
    coordinator = BettingCoordinator(
        betdaq_client=client,
        trading_mode=TradingMode.PAPER,
        paper_config=PaperTradingConfig(),
    )

    return coordinator


@pytest.mark.asyncio
async def test_high_confidence_bets(paper_trading_coordinator):
    """Test Scenario 1: High confidence, high value bets"""
    coordinator = paper_trading_coordinator
    logger.info("\n📋 Test Scenario 1: High Confidence, High Value Bets")

    # Create test market
    market_info = MarketInfo(
        market_id=200001,
        market_name="Test Race 1 - Win",
        start_time=datetime.now() + timedelta(minutes=30),
        status="active",
    )

    # High confidence, high value predictions
    predictions = [
        {
            "horse_name": "Super Star",
            "selection_id": 3001,
            "confidence": 0.92,
            "predicted_odds": 2.0,
            "current_odds": 3.2,
            "value": 0.28,  # 28% edge
        },
        {
            "horse_name": "Lightning Fast",
            "selection_id": 3002,
            "confidence": 0.88,
            "predicted_odds": 3.0,
            "current_odds": 4.5,
            "value": 0.20,  # 20% edge
        },
    ]

    bets_placed = []
    for prediction in predictions:
        bet = await coordinator.process_ai_prediction(prediction, market_info)
        if bet:
            bets_placed.append(bet)
            logger.info(
                f"✅ Bet placed: {bet.horse_name} @ {bet.matched_odds} "
                f"- Stake: £{bet.stake}"
            )

    # Simulate race results
    logger.info("🏁 Simulating race results...")
    await coordinator.simulate_race_result(200001, winning_selection_id=3001)

    # Get results
    summary = coordinator.get_performance_summary()
    paper_data = summary.get("paper_trading", {})
    account = paper_data.get("account", {})

    # Assertions
    assert len(bets_placed) > 0, "Should place at least one bet"
    assert account.get("balance", 0) != 2000.0, "Balance should have changed"
    logger.info("📊 Scenario 1: ✅ PASSED")


@pytest.mark.asyncio
async def test_mixed_confidence_levels(paper_trading_coordinator):
    """Test Scenario 2: Mixed confidence levels"""
    coordinator = paper_trading_coordinator
    logger.info("\n📋 Test Scenario 2: Mixed Confidence Levels")

    market_info = MarketInfo(
        market_id=200002,
        market_name="Test Race 2 - Win",
        start_time=datetime.now() + timedelta(minutes=45),
        status="active",
    )

    # Mixed confidence predictions
    predictions = [
        {
            "horse_name": "Maybe Winner",
            "selection_id": 4001,
            "confidence": 0.65,  # Below threshold
            "predicted_odds": 3.0,
            "current_odds": 4.0,
            "value": 0.15,
        },
        {
            "horse_name": "Good Chance",
            "selection_id": 4002,
            "confidence": 0.78,  # Above threshold
            "predicted_odds": 2.5,
            "current_odds": 3.0,
            "value": 0.12,
        },
        {
            "horse_name": "Sure Thing",
            "selection_id": 4003,
            "confidence": 0.95,  # Very high
            "predicted_odds": 1.8,
            "current_odds": 2.5,
            "value": 0.25,
        },
    ]

    before_balance = coordinator.paper_engine.account.balance

    bets_placed = []
    for prediction in predictions:
        bet = await coordinator.process_ai_prediction(prediction, market_info)
        if bet:
            bets_placed.append(bet)
            confidence = prediction["confidence"]
            logger.info(
                f"✅ Bet accepted: {bet.horse_name} - " f"Confidence: {confidence:.1%}"
            )
        else:
            horse_name = prediction["horse_name"]
            confidence = prediction["confidence"]
            logger.info(
                f"❌ Bet rejected: {horse_name} - " f"Confidence: {confidence:.1%}"
            )

    # Should only place bets for horses with confidence >= 0.75
    expected_bets = 2  # Good Chance and Sure Thing

    # Simulate Sure Thing winning
    await coordinator.simulate_race_result(200002, winning_selection_id=4003)

    after_balance = coordinator.paper_engine.account.balance

    # Assertions
    assert (
        len(bets_placed) == expected_bets
    ), f"Expected {expected_bets} bets, got {len(bets_placed)}"
    assert after_balance != before_balance, "Balance should have changed"
    logger.info("📊 Scenario 2: ✅ PASSED")


@pytest.mark.asyncio
async def test_value_betting_filters(paper_trading_coordinator):
    """Test Scenario 3: Value betting filters"""
    coordinator = paper_trading_coordinator
    logger.info("\n📋 Test Scenario 3: Value Betting Filters")

    market_info = MarketInfo(
        market_id=200003,
        market_name="Test Race 3 - Win",
        start_time=datetime.now() + timedelta(minutes=60),
        status="active",
    )

    # Test value filtering
    predictions = [
        {
            "horse_name": "No Value",
            "selection_id": 5001,
            "confidence": 0.85,
            "predicted_odds": 4.0,
            "current_odds": 3.8,  # Negative value
            "value": -0.05,
        },
        {
            "horse_name": "Low Value",
            "selection_id": 5002,
            "confidence": 0.82,
            "predicted_odds": 5.0,
            "current_odds": 5.2,  # Small positive value
            "value": 0.03,
        },
        {
            "horse_name": "Good Value",
            "selection_id": 5003,
            "confidence": 0.89,
            "predicted_odds": 3.0,
            "current_odds": 4.0,  # Good value
            "value": 0.15,
        },
    ]

    bets_placed = []
    for prediction in predictions:
        bet = await coordinator.process_ai_prediction(prediction, market_info)
        if bet:
            bets_placed.append(bet)
            logger.info(
                f"✅ Bet accepted: {bet.horse_name} - "
                f"Value: {prediction['value']:.1%}"
            )
        else:
            horse_name = prediction["horse_name"]
            value = prediction["value"]
            logger.info(f"❌ Bet rejected: {horse_name} - " f"Value: {value:.1%}")

    # Should only place bet for Good Value (value >= 0.05)
    expected_bets = 1

    # Assertions
    assert (
        len(bets_placed) == expected_bets
    ), f"Expected {expected_bets} bets, got {len(bets_placed)}"
    logger.info("📊 Scenario 3: ✅ PASSED")


@pytest.mark.asyncio
async def test_stake_calculation(paper_trading_coordinator):
    """Test Scenario 4: Stake calculation (Kelly Criterion)"""
    coordinator = paper_trading_coordinator
    logger.info("\n📋 Test Scenario 4: Stake Calculation")

    market_info = MarketInfo(
        market_id=200004,
        market_name="Test Race 4 - Win",
        start_time=datetime.now() + timedelta(minutes=75),
        status="active",
    )

    # Test different confidence/value combinations
    predictions = [
        {
            "horse_name": "Low Risk",
            "selection_id": 6001,
            "confidence": 0.76,
            "predicted_odds": 4.0,
            "current_odds": 5.0,
            "value": 0.10,
        },
        {
            "horse_name": "Medium Risk",
            "selection_id": 6002,
            "confidence": 0.85,
            "predicted_odds": 3.0,
            "current_odds": 4.0,
            "value": 0.15,
        },
        {
            "horse_name": "High Risk",
            "selection_id": 6003,
            "confidence": 0.95,
            "predicted_odds": 2.0,
            "current_odds": 3.0,
            "value": 0.25,
        },
    ]

    stakes = []
    for prediction in predictions:
        bet = await coordinator.process_ai_prediction(prediction, market_info)
        if bet:
            stakes.append(
                {
                    "horse": bet.horse_name,
                    "confidence": prediction["confidence"],
                    "value": prediction["value"],
                    "stake": bet.stake,
                }
            )
            confidence = prediction["confidence"]
            value = prediction["value"]
            logger.info(
                f"✅ {bet.horse_name}: Confidence {confidence:.1%}, "
                f"Value {value:.1%}, Stake £{bet.stake:.2f}"
            )

    # Higher confidence/value should result in higher stakes
    if len(stakes) >= 2:
        stake_progression_correct = stakes[0]["stake"] < stakes[-1]["stake"]
    else:
        stake_progression_correct = True

    # Assertions
    assert stake_progression_correct, "Stakes should increase with higher risk/value"
    assert len(stakes) >= 2, "Should place multiple bets for comparison"
    logger.info("📊 Scenario 4: ✅ PASSED")


@pytest.mark.asyncio
async def test_performance_tracking(paper_trading_coordinator):
    """Test Scenario 5: Performance tracking and analytics"""
    coordinator = paper_trading_coordinator
    logger.info("\n📋 Test Scenario 5: Performance Tracking")

    # Get comprehensive performance summary
    summary = coordinator.get_performance_summary()

    # Export session data
    export_filename = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    await coordinator.export_session_data(export_filename)

    # Check if key metrics are tracked
    paper_data = summary.get("paper_trading", {})
    account = paper_data.get("account", {})

    metrics_present = all(
        [
            "balance" in account,
            "total_staked" in account,
            "bets_placed" in account,
            "win_rate" in paper_data,
            "roi" in paper_data,
        ]
    )

    # Assertions
    assert metrics_present, "All key metrics should be present"
    assert summary is not None, "Performance summary should exist"
    logger.info("📊 Scenario 5: ✅ PASSED")
    logger.info("Data export: ✅ PASSED")
    logger.info(f"Export file: {export_filename}")
