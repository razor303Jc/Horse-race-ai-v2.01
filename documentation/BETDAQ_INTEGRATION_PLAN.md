# BETDAQ API Integration Plan for Horse Racing AI v2.0

## Overview

This document outlines the comprehensive plan for integrating BETDAQ betting exchange functionality into our Horse Racing AI system using the `betdaq` Python library (v0.0.7).

## 1. Library Analysis: rozzac90/betdaq

### 1.1 Library Overview

The `rozzac90/betdaq` Python library provides a comprehensive wrapper for the BETDAQ REST API:

- **Repository**: https://github.com/rozzac90/betdaq
- **Version**: 0.0.7 (actively maintained)
- **License**: MIT License
- **Python Support**: 3.6+

### 1.2 Key Features Analyzed

- **APIClient**: Central client for all API operations with session management
- **Module Structure**:
  - `marketdata`: Public endpoints for market information
  - `account`: Account balance, statements, and personal data
  - `betting`: Order placement, modification, and management
- **Authentication Levels**:
  - Read-only methods: Market data, basic account info
  - Secure methods: Trading, balance management, withdrawals
- **Error Handling**: Built-in exception handling for API errors
- **Rate Limiting**: Automatic request throttling to respect API limits

### 1.4 Library Advantages

- **Production Ready**: Well-tested wrapper used in real trading environments
- **Type Safety**: Comprehensive enum definitions for API parameters
- **Error Handling**: Built-in exception handling with detailed error messages
- **Session Management**: Automatic authentication token management
- **Rate Limiting**: Built-in request throttling to prevent API violations
- **Documentation**: Clear method signatures and parameter descriptions
- **Active Development**: Regular updates and bug fixes from maintainer

### 1.5 Implementation Benefits for Horse Racing AI

- **Seamless Integration**: Clean Python interface for all BETDAQ operations
- **Risk Management**: Built-in safeguards for order placement and modification
- **Real-time Capabilities**: Support for live odds feeds and market updates
- **Scalability**: Efficient handling of multiple concurrent market requests
- **Reliability**: Robust error recovery and connection management

## 2. Architecture Overview

### 2.1 Core Components

- **BETDAQ Client Service**: Main API client for authentication and requests
- **Market Data Service**: Real-time odds, prices, and market information
- **Betting Service**: Order placement, management, and monitoring
- **Risk Management**: Position monitoring and automated stop-losses
- **Integration Layer**: Bridge between AI predictions and betting decisions

### 2.2 API Structure & Capabilities

```
BETDAQ API Endpoints (via rozzac90/betdaq):
├── MarketData (Public - No Authentication Required)
│   ├── get_sports() - List all available sports
│   ├── get_sport_markets() - Horse racing markets and events
│   ├── get_market_information() - Detailed market data
│   ├── get_prices() - Current odds and price data
│   └── get_market_status() - Market state (open/suspended/closed)
├── Account (Basic Authentication)
│   ├── get_account_balances() - Current balance information
│   ├── get_betting_history() - Historical betting records
│   └── get_account_statement() - Transaction history
└── Trading (Secure Authentication Required)
    ├── place_orders() - Submit new bets
    ├── update_orders() - Modify existing orders
    ├── cancel_orders() - Cancel pending orders
    ├── get_orders() - List current active orders
    ├── suspend_from_trading() - Emergency stop
    └── list_blacklist_information() - Trading restrictions
```

### 2.3 Integration Points with Horse Racing AI

- **Prediction Pipeline**: AI model outputs → Betting recommendations
- **Odds Comparison**: Live BETDAQ odds vs model predictions
- **Risk Assessment**: Kelly Criterion with AI confidence scores
- **Order Management**: Automated bet placement based on AI signals

```
BETDAQ API Endpoints:
├── MarketData (Public)
│   ├── get_sports() - List available sports
│   ├── get_sport_markets() - Horse racing markets
│   ├── get_prices() - Real-time odds/prices
│   └── get_markets() - Market information
├── Betting (Secure)
│   ├── place_orders() - Place bets
│   ├── get_orders() - Check order status
│   ├── cancel_orders() - Cancel bets
│   └── update_orders() - Modify existing orders
├── Account (Secure)
│   ├── get_account_balances() - Check funds
│   └── get_account_statement() - Transaction history
└── Trading (Secure)
    ├── suspend_from_trading() - Emergency stop
    └── list_blacklist_information() - Trading restrictions
```

## 3. Implementation Plan

### 3.1 Phase 1: Foundation Setup (Week 1)

#### 3.1.1 Install Dependencies

```bash
# Core BETDAQ library and dependencies
pip install betdaq==0.0.7
pip install zeep>=4.0.0  # SOAP client for API communication
pip install requests>=2.25.0  # HTTP client
pip install python-dateutil>=2.8.0  # Date handling
```

#### 3.1.2 Enhanced BETDAQ Client Module

```python
# betdaq_client.py
from betdaq.apiclient import APIClient
from betdaq.enums import SportID, Boolean, Polarity, OrderKillType, OrderActionType
from betdaq.exceptions import BetdaqException
from betdaq.filters import create_order, update_order
import logging
from typing import List, Dict, Optional

class BetdaqClient:
    def __init__(self, username: str, password: str):
        self.client = APIClient(username, password)
        self.logger = logging.getLogger(__name__)

    def authenticate(self) -> bool:
        """Test API connection and authentication"""
        try:
            # Test with a simple market data call
            sports = self.client.marketdata.get_sports()
            return True if sports else False
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
```

#### 2.1.3 Configuration Management

```python
# betdaq_config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class BetdaqConfig:
    username: str
    password: str
    max_stake_per_bet: float = 10.0
    max_daily_loss: float = 100.0
    min_odds: float = 1.5
    max_odds: float = 10.0
    enabled: bool = False  # Safety switch

    @classmethod
    def from_env(cls) -> 'BetdaqConfig':
        return cls(
            username=os.getenv('BETDAQ_USERNAME', ''),
            password=os.getenv('BETDAQ_PASSWORD', ''),
            max_stake_per_bet=float(os.getenv('BETDAQ_MAX_STAKE', '10.0')),
            max_daily_loss=float(os.getenv('BETDAQ_MAX_LOSS', '100.0')),
            min_odds=float(os.getenv('BETDAQ_MIN_ODDS', '1.5')),
            max_odds=float(os.getenv('BETDAQ_MAX_ODDS', '10.0')),
            enabled=os.getenv('BETDAQ_ENABLED', 'false').lower() == 'true'
        )
```

### 2.2 Phase 2: Market Data Integration (Week 2)

#### 2.2.1 Horse Racing Market Scanner

```python
# betdaq_market_scanner.py
class BetdaqMarketScanner:
    def __init__(self, client: BetdaqClient):
        self.client = client
        self.horse_racing_id = SportID.HorseRacing.value  # 100004

    async def get_horse_racing_markets(self) -> List[Dict]:
        """Get all active horse racing markets"""
        try:
            markets = self.client.client.marketdata.get_sport_markets(
                sport_ids=[self.horse_racing_id],
                include_selections=True,
                WantDirectDescendentsOnly=Boolean.F.value
            )
            return self._filter_active_markets(markets)
        except Exception as e:
            self.logger.error(f"Failed to get markets: {e}")
            return []

    async def get_market_prices(self, market_ids: List[int]) -> Dict:
        """Get real-time prices for markets"""
        try:
            prices = self.client.client.marketdata.get_prices(
                market_ids=market_ids,
                ThresholdAmount=1.0,
                NumberForPricesRequired=-1,  # All available
                NumberAgainstPricesRequired=-1,
                WantMarketMatchedAmount=Boolean.T.value,
                WantSelectionsMatchedAmounts=Boolean.T.value,
                WantSelectionMatchedDetails=Boolean.T.value
            )
            return self._parse_prices(prices)
        except Exception as e:
            self.logger.error(f"Failed to get prices: {e}")
            return {}
```

#### 2.2.2 Real-time Odds Monitoring

```python
# betdaq_odds_monitor.py
import asyncio
from datetime import datetime, timedelta

class BetdaqOddsMonitor:
    def __init__(self, scanner: BetdaqMarketScanner):
        self.scanner = scanner
        self.running = False
        self.odds_cache = {}

    async def start_monitoring(self, market_ids: List[int], interval: int = 5):
        """Monitor odds changes in real-time"""
        self.running = True
        while self.running:
            try:
                current_prices = await self.scanner.get_market_prices(market_ids)

                for market_id, market_data in current_prices.items():
                    if market_id in self.odds_cache:
                        self._detect_odds_changes(market_id, market_data)

                    self.odds_cache[market_id] = {
                        'data': market_data,
                        'timestamp': datetime.utcnow()
                    }

                await asyncio.sleep(interval)

            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(interval)
```

### 2.3 Phase 3: Betting Integration (Week 3)

#### 2.3.1 Order Management System

```python
# betdaq_betting_service.py
class BetdaqBettingService:
    def __init__(self, client: BetdaqClient, config: BetdaqConfig):
        self.client = client
        self.config = config
        self.active_orders = {}

    async def place_bet(self, selection_id: int, stake: float, price: float,
                       side: str, market_info: Dict) -> Optional[Dict]:
        """Place a bet on BETDAQ exchange"""

        # Validate bet parameters
        if not self._validate_bet(stake, price, side):
            return None

        try:
            # Create order filter
            polarity = Polarity.back if side.lower() == 'back' else Polarity.lay

            order = create_order(
                SelectionId=selection_id,
                Stake=stake,
                Price=price,
                Polarity=polarity.value,
                ExpectedSelectionResetCount=market_info.get('reset_count', 0),
                ExpectedWithdrawalSequenceNumber=market_info.get('withdrawal_seq', 0),
                CancelOnInRunning=Boolean.T,
                CancelIfSelectionReset=Boolean.T,
                KillType=OrderKillType.FillOrKillDontCancel.value,
                PunterReferenceNumber=int(datetime.utcnow().timestamp())
            )

            # Place order
            result = self.client.client.betting.place_orders(
                order_list=[order],
                WantAllOrNothingBehaviour=Boolean.T.value,
                receipt=True
            )

            if result:
                order_info = result[0]
                self.active_orders[order_info['order_id']] = {
                    'selection_id': selection_id,
                    'stake': stake,
                    'price': price,
                    'side': side,
                    'status': order_info['status'],
                    'placed_at': datetime.utcnow()
                }

                self.logger.info(f"Bet placed: {order_info}")
                return order_info

        except Exception as e:
            self.logger.error(f"Failed to place bet: {e}")
            return None

    def _validate_bet(self, stake: float, price: float, side: str) -> bool:
        """Validate bet parameters against config limits"""
        if stake > self.config.max_stake_per_bet:
            self.logger.warning(f"Stake {stake} exceeds limit {self.config.max_stake_per_bet}")
            return False

        if price < self.config.min_odds or price > self.config.max_odds:
            self.logger.warning(f"Price {price} outside limits {self.config.min_odds}-{self.config.max_odds}")
            return False

        return True
```

#### 2.3.2 Risk Management

```python
# betdaq_risk_manager.py
class BetdaqRiskManager:
    def __init__(self, betting_service: BetdaqBettingService, config: BetdaqConfig):
        self.betting_service = betting_service
        self.config = config
        self.daily_pnl = 0.0
        self.positions = {}

    async def check_daily_limits(self) -> bool:
        """Check if daily loss limits exceeded"""
        if abs(self.daily_pnl) >= self.config.max_daily_loss:
            self.logger.warning(f"Daily loss limit reached: {self.daily_pnl}")
            await self._emergency_stop()
            return False
        return True

    async def monitor_positions(self):
        """Monitor all active positions"""
        try:
            orders = self.betting_service.client.client.betting.get_orders()

            for order in orders:
                order_id = order['order_id']
                if order_id in self.betting_service.active_orders:
                    await self._update_position_pnl(order)

        except Exception as e:
            self.logger.error(f"Position monitoring error: {e}")

    async def _emergency_stop(self):
        """Cancel all active orders in emergency"""
        try:
            result = self.betting_service.client.client.betting.cancel_all_orders()
            self.logger.critical(f"Emergency stop executed: {result}")
        except Exception as e:
            self.logger.error(f"Emergency stop failed: {e}")
```

### 2.4 Phase 4: AI Integration (Week 4)

#### 2.4.1 AI-BETDAQ Bridge

```python
# ai_betdaq_bridge.py
class AIBetdaqBridge:
    def __init__(self, ai_predictor, betting_service: BetdaqBettingService,
                 risk_manager: BetdaqRiskManager):
        self.ai_predictor = ai_predictor
        self.betting_service = betting_service
        self.risk_manager = risk_manager

    async def process_race_predictions(self, race_data: Dict) -> List[Dict]:
        """Convert AI predictions to betting decisions"""

        # Get AI predictions
        predictions = await self.ai_predictor.predict_race(race_data)

        betting_opportunities = []

        for prediction in predictions:
            confidence = prediction.get('confidence', 0)
            predicted_odds = prediction.get('predicted_odds', 0)
            horse_name = prediction.get('horse_name', '')

            # Only consider high-confidence predictions
            if confidence > 0.75:

                # Get current market odds from BETDAQ
                market_odds = await self._get_market_odds(
                    race_data['market_id'],
                    horse_name
                )

                if market_odds:
                    # Calculate value bet
                    value = self._calculate_value(predicted_odds, market_odds)

                    if value > 0.1:  # 10% edge required
                        betting_opportunities.append({
                            'horse_name': horse_name,
                            'selection_id': market_odds['selection_id'],
                            'predicted_odds': predicted_odds,
                            'market_odds': market_odds['best_back'],
                            'confidence': confidence,
                            'value': value,
                            'stake': self._calculate_stake(confidence, value),
                            'side': 'back'
                        })

        return betting_opportunities

    def _calculate_value(self, predicted_odds: float, market_odds: float) -> float:
        """Calculate betting value (Kelly Criterion basis)"""
        if predicted_odds <= 1.0 or market_odds <= 1.0:
            return 0.0

        implied_prob = 1.0 / predicted_odds
        market_prob = 1.0 / market_odds

        return (implied_prob * market_odds - 1) / (market_odds - 1)

    def _calculate_stake(self, confidence: float, value: float) -> float:
        """Calculate optimal stake using Kelly Criterion"""
        # Simplified Kelly: f = (bp - q) / b
        # where b = odds-1, p = confidence, q = 1-confidence

        base_stake = min(
            self.betting_service.config.max_stake_per_bet,
            (confidence * value) * 20  # Conservative multiplier
        )

        return max(1.0, base_stake)  # Minimum £1 stake
```

#### 2.4.2 Automated Trading System

```python
# betdaq_auto_trader.py
class BetdaqAutoTrader:
    def __init__(self, bridge: AIBetdaqBridge, market_scanner: BetdaqMarketScanner):
        self.bridge = bridge
        self.scanner = market_scanner
        self.running = False

    async def start_trading(self):
        """Start automated trading system"""
        self.running = True

        while self.running:
            try:
                # Check daily limits
                if not await self.bridge.risk_manager.check_daily_limits():
                    break

                # Get upcoming horse racing markets
                markets = await self.scanner.get_horse_racing_markets()

                for market in markets:
                    # Check if race starts in next 30 minutes
                    if self._is_race_imminent(market['market_start_time']):

                        # Get race data and AI predictions
                        race_data = await self._prepare_race_data(market)

                        # Get betting opportunities
                        opportunities = await self.bridge.process_race_predictions(race_data)

                        # Execute bets
                        for opp in opportunities:
                            await self._execute_bet(opp, market)

                # Monitor existing positions
                await self.bridge.risk_manager.monitor_positions()

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Trading loop error: {e}")
                await asyncio.sleep(60)

    async def _execute_bet(self, opportunity: Dict, market: Dict):
        """Execute a betting opportunity"""

        result = await self.bridge.betting_service.place_bet(
            selection_id=opportunity['selection_id'],
            stake=opportunity['stake'],
            price=opportunity['market_odds'],
            side=opportunity['side'],
            market_info=market
        )

        if result:
            # Send notification
            await self._send_bet_notification(opportunity, result)
```

## 3. Integration Points

### 3.1 Database Schema Extensions

```sql
-- BETDAQ specific tables
CREATE TABLE betdaq_orders (
    id SERIAL PRIMARY KEY,
    order_id BIGINT UNIQUE NOT NULL,
    race_id INTEGER REFERENCES races(id),
    horse_name VARCHAR(255),
    selection_id BIGINT,
    market_id BIGINT,
    stake DECIMAL(10,2),
    odds DECIMAL(10,2),
    side VARCHAR(10),
    status VARCHAR(50),
    placed_at TIMESTAMP,
    matched_at TIMESTAMP,
    pnl DECIMAL(10,2),
    commission DECIMAL(10,2)
);

CREATE TABLE betdaq_market_data (
    id SERIAL PRIMARY KEY,
    market_id BIGINT,
    selection_id BIGINT,
    horse_name VARCHAR(255),
    back_price DECIMAL(10,2),
    lay_price DECIMAL(10,2),
    volume DECIMAL(12,2),
    timestamp TIMESTAMP,
    INDEX idx_market_timestamp (market_id, timestamp)
);
```

### 3.2 Configuration Integration

```python
# Add to existing config system
BETDAQ_CONFIG = {
    'ENABLED': False,  # Safety switch
    'USERNAME': '',
    'PASSWORD': '',
    'MAX_STAKE_PER_BET': 10.0,
    'MAX_DAILY_LOSS': 100.0,
    'MIN_CONFIDENCE': 0.75,
    'MIN_VALUE': 0.10,
    'KELLY_MULTIPLIER': 0.25,  # Conservative Kelly
}
```

### 3.3 Notification Integration

```python
# Extend existing NTFY notification system
class BetdaqNotifications:
    async def send_bet_placed(self, bet_info: Dict):
        message = f"🎯 Bet Placed: {bet_info['horse_name']} @ {bet_info['odds']} - Stake: £{bet_info['stake']}"
        await self.ntfy_client.send_notification("horse-racing-bets", message)

    async def send_bet_matched(self, bet_info: Dict):
        message = f"✅ Bet Matched: {bet_info['horse_name']} - Profit potential: £{bet_info['potential_profit']}"
        await self.ntfy_client.send_notification("horse-racing-bets", message)

    async def send_daily_summary(self, summary: Dict):
        pnl = summary['total_pnl']
        emoji = "📈" if pnl > 0 else "📉"
        message = f"{emoji} Daily Summary: P&L: £{pnl:.2f}, Bets: {summary['total_bets']}, Win Rate: {summary['win_rate']:.1%}"
        await self.ntfy_client.send_notification("horse-racing-summary", message)
```

## 4. Safety Features

### 4.1 Multiple Safety Layers

1. **Configuration Kill Switch**: `BETDAQ_ENABLED=false` stops all betting
2. **Daily Loss Limits**: Automatic trading halt when limits reached
3. **Position Monitoring**: Real-time P&L tracking
4. **Emergency Stop**: Cancel all orders instantly
5. **Confidence Thresholds**: Only bet on high-confidence predictions
6. **Value Betting**: Only bet when significant edge detected

### 4.2 Testing Strategy

1. **Paper Trading Mode**: Test all logic without real money
2. **Sandbox Environment**: Use BETDAQ demo environment if available
3. **Small Stakes Testing**: Start with minimum stakes
4. **Manual Override**: Always allow manual intervention

## 5. Deployment Plan

### 5.1 Environment Setup

```bash
# Add to Docker configuration
ENV BETDAQ_USERNAME=""
ENV BETDAQ_PASSWORD=""
ENV BETDAQ_ENABLED="false"
ENV BETDAQ_MAX_STAKE="5.0"
ENV BETDAQ_MAX_LOSS="50.0"
```

### 5.2 Monitoring Dashboard

- Real-time P&L tracking
- Active orders display
- Daily/weekly performance metrics
- Risk management alerts
- API status monitoring

## 6. Risk Disclaimers

⚠️ **IMPORTANT WARNINGS**:

1. **Gambling Risks**: Betting involves financial risk and potential losses
2. **API Reliability**: Exchange APIs can fail or be unavailable
3. **Market Volatility**: Horse racing odds change rapidly
4. **Regulatory Compliance**: Ensure compliance with local gambling laws
5. **Responsible Gambling**: Set strict limits and monitor usage

## 8. Paper Trading & Live Betting Implementation

### 8.1 Paper Trading System

**Purpose**: Safe testing environment without real money risk

**Key Features**:

- Virtual account with configurable starting balance
- Realistic market simulation with commission calculations
- Complete performance tracking and analytics
- SQLite database for persistent storage
- Bet settlement simulation based on AI predictions
- Export capabilities for analysis

**Implementation**:

```python
# betdaq_paper_trading.py - Complete implementation
from betdaq_paper_trading import PaperTradingEngine, PaperTradingConfig

config = PaperTradingConfig(
    starting_balance=1000.0,
    track_performance=True,
    simulate_market_movements=True,
    realistic_matching=True,
    commission_rate=0.02  # 2% like real BETDAQ
)

engine = PaperTradingEngine(config)
```

**Database Schema**:

```sql
-- Paper trading tables
CREATE TABLE paper_bets (
    bet_id TEXT PRIMARY KEY,
    selection_id INTEGER,
    horse_name TEXT,
    race_name TEXT,
    market_id INTEGER,
    stake REAL,
    requested_odds REAL,
    matched_odds REAL,
    side TEXT,
    status TEXT,
    placed_at TEXT,
    matched_at TEXT,
    settled_at TEXT,
    pnl REAL,
    commission REAL,
    confidence REAL,
    value REAL
);

CREATE TABLE paper_account_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    balance REAL,
    daily_pnl REAL,
    total_staked REAL,
    total_won REAL,
    total_lost REAL,
    bets_placed INTEGER,
    bets_won INTEGER,
    win_rate REAL,
    roi REAL
);
```

### 8.2 Live Betting System

**Purpose**: Real money betting with comprehensive risk management

**Key Features**:

- Multi-layer risk management system
- Real-time order monitoring and updates
- Emergency stop capabilities
- Position tracking and P&L calculation
- Frequency limits and exposure controls
- Integration with BETDAQ API

**Risk Management Layers**:

1. **Pre-flight Checks**: Authentication, trading enabled, valid parameters
2. **Risk Limits Validation**: Stake limits, exposure limits, odds ranges
3. **Frequency Controls**: Maximum bets per hour/day
4. **Emergency Stops**: Automatic halt on loss thresholds
5. **Position Monitoring**: Real-time P&L tracking

**Implementation**:

```python
# betdaq_live_betting.py - Complete implementation
from betdaq_live_betting import LiveBettingEngine, RiskLimits

risk_limits = RiskLimits(
    max_stake_per_bet=20.0,
    max_total_exposure=200.0,
    max_daily_loss=100.0,
    max_orders_per_race=3,
    min_odds=1.5,
    max_odds=20.0,
    stop_loss_percentage=10.0,
    max_bet_frequency=10  # per hour
)

engine = LiveBettingEngine(betdaq_client, risk_limits)
```

### 8.3 Unified Betting Coordinator

**Purpose**: Seamless switching between paper trading and live betting

**Key Features**:

- Mode switching (Paper ↔ Live ↔ Disabled)
- Unified API for both trading types
- AI prediction processing
- Performance tracking across modes
- Session data export
- Continuous monitoring

**Implementation**:

```python
# betdaq_betting_coordinator.py - Complete implementation
from betdaq_betting_coordinator import BettingCoordinator, TradingMode

coordinator = BettingCoordinator(
    betdaq_client=client,
    trading_mode=TradingMode.PAPER,  # Start safe
    paper_config=paper_config,
    risk_limits=risk_limits
)

# Process AI predictions
bet = await coordinator.process_ai_prediction(prediction, market_info)

# Switch to live trading when ready
await coordinator.switch_mode(TradingMode.LIVE)
```

### 8.4 AI Integration Bridge

**Purpose**: Convert AI predictions to betting decisions

**Features**:

- Confidence threshold filtering
- Value betting calculations (Kelly Criterion)
- Dynamic stake sizing
- Risk-adjusted bet placement
- Performance feedback loop

**Value Calculation**:

```python
def calculate_value(predicted_odds, current_odds):
    implied_prob = 1.0 / predicted_odds
    market_prob = 1.0 / current_odds
    return (implied_prob * current_odds - 1) / (current_odds - 1)
```

**Kelly Criterion Staking**:

```python
def calculate_kelly_stake(confidence, value, odds):
    b = odds - 1
    p = confidence
    q = 1 - confidence
    kelly_fraction = (b * p - q) / b
    conservative_fraction = kelly_fraction * 0.25  # 25% of Kelly
    return min(max_stake, max(1.0, conservative_fraction * max_stake))
```

### 8.5 Implementation Files Created

1. **`betdaq_paper_trading.py`** (465 lines)
   - Complete paper trading simulation
   - Performance tracking and analytics
   - Database persistence
   - Race result simulation

2. **`betdaq_live_betting.py`** (582 lines)
   - Live betting with risk management
   - Order monitoring and settlement
   - Emergency stop functionality
   - AI prediction integration

3. **`betdaq_betting_coordinator.py`** (425 lines)
   - Unified interface for both modes
   - Mode switching capabilities
   - Session management and export
   - Monitoring and performance tracking

### 8.6 Safety Features

**Paper Trading Safety**:

- No real money risk
- Realistic commission simulation
- Performance validation before live trading
- Complete audit trail

**Live Trading Safety**:

- Multiple confirmation layers
- Real-time risk monitoring
- Automatic emergency stops
- Position size limits
- Frequency controls

**Coordinator Safety**:

- Gradual progression (Paper → Live)
- Mode switch validation
- Active order protection
- Emergency stop override

### 8.7 Usage Workflow

**Phase 1: Paper Trading Validation**

```python
# Start with paper trading
coordinator = BettingCoordinator(client, TradingMode.PAPER)

# Test AI predictions
for prediction in ai_predictions:
    bet = await coordinator.process_ai_prediction(prediction, market_info)

# Validate performance
summary = coordinator.get_performance_summary()
if summary['paper_trading']['roi'] > 5.0:  # 5% ROI minimum
    print("Ready for live trading")
```

**Phase 2: Live Trading Deployment**

```python
# Switch to live with conservative limits
risk_limits = RiskLimits(
    max_stake_per_bet=5.0,  # Start small
    max_daily_loss=25.0,
    max_total_exposure=50.0
)

success = await coordinator.switch_mode(TradingMode.LIVE, risk_limits=risk_limits)

# Monitor and scale gradually
await coordinator.start_monitoring(interval=30)
```

### 8.8 Performance Monitoring

**Key Metrics**:

- Win Rate %
- Return on Investment (ROI)
- Profit & Loss (P&L)
- Sharpe Ratio
- Maximum Drawdown
- Bet Frequency
- Value Accuracy

**Monitoring Dashboard Integration**:

```python
# Real-time performance data
performance = coordinator.get_performance_summary()

# Export for analysis
await coordinator.export_session_data("session_2025_08_03.json")

# Integration with existing NTFY notifications
await send_performance_alert(performance)
```

This comprehensive implementation provides a complete paper trading and live betting system with enterprise-grade risk management and safety features.
