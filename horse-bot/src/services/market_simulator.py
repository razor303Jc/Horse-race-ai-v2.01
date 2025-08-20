"""
Market Simulator for Horse Racing Betting Exchange

Simulates realistic betting exchange markets and race data for testing
and development without requiring real API connections.
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
import json
import math

logger = logging.getLogger(__name__)


class MarketState(Enum):
    """Market state enum."""
    PRE_PLAY = "pre_play"
    IN_PLAY = "in_play"
    SUSPENDED = "suspended"
    SETTLED = "settled"
    CANCELLED = "cancelled"


@dataclass
class SimulatedRunner:
    """A simulated runner in a betting market."""
    selection_id: int
    name: str
    back_odds: Decimal
    lay_odds: Decimal
    back_size: Decimal  # Available to back
    lay_size: Decimal   # Available to lay
    last_traded: Optional[Decimal] = None
    total_matched: Decimal = field(default_factory=lambda: Decimal('0'))
    win_probability: float = 0.0
    form_rating: float = 5.0  # 1-10 scale
    recent_form: str = ""
    jockey: str = ""
    trainer: str = ""
    weight: str = ""
    age: int = 4
    
    def update_odds(self, back_movement: float = 0.0, lay_movement: float = 0.0):
        """Update odds with market movement."""
        self.back_odds = max(Decimal('1.01'), self.back_odds * Decimal(str(1 + back_movement)))
        self.lay_odds = max(Decimal('1.02'), self.lay_odds * Decimal(str(1 + lay_movement)))
        
        # Ensure lay odds are always higher than back odds
        if self.lay_odds <= self.back_odds:
            self.lay_odds = self.back_odds + Decimal('0.01')


@dataclass
class SimulatedMarket:
    """A simulated betting market."""
    market_id: str
    event_name: str
    event_id: str
    start_time: datetime
    market_type: str = "WIN"
    state: MarketState = MarketState.PRE_PLAY
    total_matched: Decimal = field(default_factory=lambda: Decimal('0'))
    runners: List[SimulatedRunner] = field(default_factory=list)
    in_play_delay: int = 5  # seconds
    race_distance: str = "1m 2f"
    race_class: str = "Class 3"
    track_condition: str = "Good"
    weather: str = "Fine"
    
    def get_runner_by_id(self, selection_id: int) -> Optional[SimulatedRunner]:
        """Get runner by selection ID."""
        return next((r for r in self.runners if r.selection_id == selection_id), None)
    
    def get_overround(self) -> float:
        """Calculate market overround."""
        total_prob = sum(1 / float(runner.back_odds) for runner in self.runners)
        return (total_prob - 1) * 100


class MarketSimulator:
    """
    Simulates realistic betting exchange markets with dynamic pricing,
    market movements, and race scenarios.
    """
    
    def __init__(self):
        self.markets: Dict[str, SimulatedMarket] = {}
        self.race_results: Dict[str, int] = {}  # market_id -> winning_selection_id
        self.market_counter = 1
        
        # UK racecourses for realistic simulation
        self.tracks = [
            "Newmarket", "Ascot", "Epsom", "Cheltenham", "Aintree",
            "York", "Goodwood", "Doncaster", "Chester", "Bath",
            "Windsor", "Kempton", "Lingfield", "Wolverhampton", "Southwell"
        ]
        
        # Realistic horse names
        self.horse_names = [
            "Thunder Bolt", "Lightning Strike", "Storm Chaser", "Wind Runner",
            "Royal Champion", "Noble Quest", "Golden Arrow", "Silver Bullet",
            "Derby Dream", "Classic Star", "Racing Legend", "Speed Demon",
            "Flying Machine", "Rocket Power", "Fire Storm", "Ice Cold",
            "Diamond Dust", "Ruby Red", "Emerald Green", "Sapphire Blue",
            "Midnight Express", "Dawn Raider", "Sunset Glory", "Morning Star",
            "Celtic Warrior", "Viking Spirit", "Roman Centurion", "Greek Hero",
            "Desert King", "Mountain Peak", "Ocean Wave", "River Dance",
            "Forest Fire", "Prairie Wind", "Canyon Runner", "Valley Storm"
        ]
        
        # Top jockeys for realism
        self.jockeys = [
            "F. Dettori", "R. Moore", "W. Buick", "J. Doyle", "T. Marquand",
            "H. Bentley", "S. De Sousa", "D. Tudhope", "J. Fanning", "A. Kirby",
            "R. Havlin", "J. Spencer", "R. Kingscote", "C. Lee", "G. Lee"
        ]
        
        # Top trainers
        self.trainers = [
            "J. Gosden", "A. O'Brien", "M. Johnston", "W. Haggas", "R. Hannon",
            "M. Appleby", "R. Varian", "C. Appleby", "M. Stoute", "J. Fanshawe"
        ]
    
    async def create_realistic_race_card(self, date: datetime, num_races: int = 5) -> List[SimulatedMarket]:
        """Create a realistic race card for a given date."""
        
        markets = []
        
        for race_num in range(1, num_races + 1):
            market = await self._create_realistic_race(date, race_num)
            markets.append(market)
            self.markets[market.market_id] = market
        
        logger.info(f"Created race card with {len(markets)} races for {date.strftime('%Y-%m-%d')}")
        return markets
    
    async def _create_realistic_race(self, date: datetime, race_num: int) -> SimulatedMarket:
        """Create a realistic individual race."""
        
        track = random.choice(self.tracks)
        race_time = date.replace(
            hour=13 + race_num, 
            minute=random.choice([0, 15, 30, 45]),
            second=0,
            microsecond=0
        )
        
        market_id = f"sim_{date.strftime('%Y%m%d')}_{track}_{race_num:02d}"
        
        market = SimulatedMarket(
            market_id=market_id,
            event_name=f"{track} R{race_num}",
            event_id=f"event_{market_id}",
            start_time=race_time,
            race_distance=random.choice(["5f", "6f", "7f", "1m", "1m 2f", "1m 4f", "2m"]),
            race_class=random.choice(["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6"]),
            track_condition=random.choice(["Firm", "Good", "Good to Soft", "Soft", "Heavy"]),
            weather=random.choice(["Fine", "Overcast", "Light Rain", "Showery"])
        )
        
        # Create runners (6-12 horses per race)
        num_runners = random.randint(6, 12)
        used_names = set()
        
        for i in range(num_runners):
            # Pick unique horse name
            horse_name = random.choice(self.horse_names)
            while horse_name in used_names:
                horse_name = random.choice(self.horse_names)
            used_names.add(horse_name)
            
            # Generate realistic odds based on quality distribution
            # Create a realistic favorite-to-outsider spread
            if i == 0:  # Favorite
                base_odds = random.uniform(1.5, 3.5)
            elif i == 1:  # Second favorite
                base_odds = random.uniform(2.5, 5.0)
            elif i == 2:  # Third favorite
                base_odds = random.uniform(3.0, 7.0)
            else:  # Others
                base_odds = random.uniform(4.0, 25.0)
            
            back_odds = Decimal(str(round(base_odds, 2)))
            lay_odds = back_odds + Decimal('0.02')  # 2 tick spread
            
            # Generate form rating (affects odds)
            form_rating = max(1.0, min(10.0, random.gauss(5.0, 2.0)))
            
            # Adjust odds based on form
            if form_rating > 7.0:
                back_odds *= Decimal('0.8')  # Shorten odds for good form
            elif form_rating < 3.0:
                back_odds *= Decimal('1.3')  # Lengthen odds for poor form
            
            # Generate recent form string
            recent_form = self._generate_recent_form(form_rating)
            
            runner = SimulatedRunner(
                selection_id=i + 1,
                name=horse_name,
                back_odds=back_odds,
                lay_odds=lay_odds,
                back_size=Decimal(str(random.randint(100, 2000))),
                lay_size=Decimal(str(random.randint(100, 2000))),
                win_probability=float(1 / back_odds),
                form_rating=form_rating,
                recent_form=recent_form,
                jockey=random.choice(self.jockeys),
                trainer=random.choice(self.trainers),
                weight=f"{random.randint(8, 10)}-{random.randint(0, 13)}",
                age=random.randint(2, 8)
            )
            
            market.runners.append(runner)
        
        # Normalize probabilities to create realistic overround
        self._normalize_market_probabilities(market)
        
        return market
    
    def _generate_recent_form(self, form_rating: float) -> str:
        """Generate realistic recent form string based on rating."""
        
        form_chars = []
        
        for _ in range(5):  # Last 5 runs
            if form_rating > 7.0:
                # Good horses - more wins and places
                chars = ['1'] * 3 + ['2', '3'] * 2 + ['4', '5', '6']
            elif form_rating > 5.0:
                # Average horses
                chars = ['1'] + ['2', '3'] * 2 + ['4', '5', '6'] * 3 + ['7', '8', '9']
            else:
                # Poor horses
                chars = ['1'] + ['2', '3'] + ['4', '5', '6'] * 2 + ['7', '8', '9'] * 4 + ['0', 'P', 'U']
            
            form_chars.append(random.choice(chars))
        
        return ''.join(form_chars)
    
    def _normalize_market_probabilities(self, market: SimulatedMarket):
        """Normalize market to create realistic overround (104-120%)."""
        
        target_overround = random.uniform(1.04, 1.12)  # 4-12% overround
        
        # Calculate current total probability
        current_total = sum(1 / float(runner.back_odds) for runner in market.runners)
        
        # Adjust odds to achieve target overround
        adjustment_factor = current_total / target_overround
        
        for runner in market.runners:
            adjusted_prob = (1 / float(runner.back_odds)) / adjustment_factor
            new_odds = 1 / adjusted_prob
            runner.back_odds = Decimal(str(round(new_odds, 2)))
            runner.lay_odds = runner.back_odds + Decimal('0.02')
            runner.win_probability = adjusted_prob
    
    async def simulate_market_movements(self, market_id: str, duration_minutes: int = 30):
        """Simulate realistic market movements over time."""
        
        market = self.markets.get(market_id)
        if not market:
            return
        
        logger.info(f"Starting market movement simulation for {market.event_name}")
        
        # Simulate movements every 30 seconds
        intervals = duration_minutes * 2
        
        for i in range(intervals):
            await asyncio.sleep(0.1)  # Speed up for demo (normally 30 seconds)
            
            # Calculate time to race start
            time_to_start = (market.start_time - datetime.now()).total_seconds()
            
            # Increase volatility as race approaches
            volatility = min(0.1, 0.02 + (1800 - time_to_start) / 18000)  # Max 10%
            
            # Random market movements
            for runner in market.runners:
                # Random walk with slight bias toward favorites
                bias = -0.001 if runner.win_probability > 0.2 else 0.001
                movement = random.gauss(bias, volatility * 0.5)
                
                runner.update_odds(movement, movement)
                
                # Simulate some trading volume
                trade_volume = Decimal(str(random.randint(10, 200)))
                runner.total_matched += trade_volume
                market.total_matched += trade_volume
            
            # Occasional bigger movements (news, money moves)
            if random.random() < 0.1:  # 10% chance per interval
                runner = random.choice(market.runners)
                big_movement = random.gauss(0, 0.15)  # Bigger movement
                runner.update_odds(big_movement, big_movement)
                logger.debug(f"Big movement: {runner.name} odds moved significantly")
        
        # Switch to in-play when race starts
        if time_to_start <= 0:
            market.state = MarketState.IN_PLAY
            await self._simulate_in_play_action(market)
    
    async def _simulate_in_play_action(self, market: SimulatedMarket):
        """Simulate in-play market action during race."""
        
        logger.info(f"Race {market.event_name} going in-play")
        
        # Simulate race lasting 2-5 minutes
        race_duration = random.uniform(120, 300)
        intervals = int(race_duration / 5)  # Update every 5 seconds
        
        for i in range(intervals):
            await asyncio.sleep(0.05)  # Speed up for demo
            
            # Dramatic odds movements during race
            for runner in market.runners:
                # More volatile movements in-play
                movement = random.gauss(0, 0.3)
                runner.update_odds(movement, movement)
            
            # Random suspensions (sometimes markets suspend in-play)
            if random.random() < 0.05:
                market.state = MarketState.SUSPENDED
                await asyncio.sleep(0.1)  # Brief suspension
                market.state = MarketState.IN_PLAY
        
        # Race finishes - settle market
        await self._settle_market(market)
    
    async def _settle_market(self, market: SimulatedMarket):
        """Settle market with realistic race result."""
        
        logger.info(f"Settling race {market.event_name}")
        
        # Weight selection by inverse odds (favorites more likely to win)
        weights = []
        for runner in market.runners:
            # Higher form rating and lower odds = higher chance
            weight = (runner.form_rating / 5.0) * (1 / float(runner.back_odds))
            weights.append(weight)
        
        # Select winner based on weighted probabilities
        total_weight = sum(weights)
        rand_val = random.random() * total_weight
        
        cumulative = 0
        winner = market.runners[0]  # Default fallback
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if rand_val <= cumulative:
                winner = market.runners[i]
                break
        
        # Store result and settle market
        self.race_results[market.market_id] = winner.selection_id
        market.state = MarketState.SETTLED
        
        logger.info(f"Race {market.event_name} won by {winner.name} ({winner.back_odds})")
    
    async def get_market_prices(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get current market prices in BetDaq-compatible format."""
        
        market = self.markets.get(market_id)
        if not market:
            return None
        
        selections = []
        for runner in market.runners:
            selections.append({
                "selection_id": runner.selection_id,
                "selection_name": runner.name,
                "back_price": float(runner.back_odds),
                "lay_price": float(runner.lay_odds),
                "back_size": float(runner.back_size),
                "lay_size": float(runner.lay_size),
                "last_traded": float(runner.last_traded) if runner.last_traded else None,
                "total_matched": float(runner.total_matched),
                "win_probability": runner.win_probability
            })
        
        return {
            "market_id": market.market_id,
            "event_name": market.event_name,
            "start_time": market.start_time.isoformat(),
            "state": market.state.value,
            "total_matched": float(market.total_matched),
            "selections": selections,
            "overround": market.get_overround()
        }
    
    async def get_race_data(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get race data in our internal format."""
        
        market = self.markets.get(market_id)
        if not market:
            return None
        
        horses = []
        for runner in market.runners:
            horses.append({
                "name": runner.name,
                "number": runner.selection_id,
                "jockey": runner.jockey,
                "trainer": runner.trainer,
                "weight": runner.weight,
                "age": runner.age,
                "form": runner.recent_form,
                "form_rating": runner.form_rating
            })
        
        return {
            "race_id": market.market_id,
            "track_name": market.event_name.split()[0],
            "race_number": int(market.event_name.split('R')[1]),
            "race_time": market.start_time.strftime("%H:%M"),
            "distance": market.race_distance,
            "race_class": market.race_class,
            "conditions": market.track_condition,
            "weather": market.weather,
            "horses": horses
        }
    
    async def place_simulated_bet(
        self, 
        market_id: str, 
        selection_id: int, 
        bet_type: str, 
        odds: Decimal, 
        stake: Decimal
    ) -> Dict[str, Any]:
        """Simulate placing a bet."""
        
        market = self.markets.get(market_id)
        if not market:
            return {"error": "Market not found"}
        
        runner = market.get_runner_by_id(selection_id)
        if not runner:
            return {"error": "Selection not found"}
        
        # Simple bet matching simulation
        if bet_type.upper() == "BACK":
            if odds <= runner.back_odds * Decimal('1.05'):  # Allow 5% tolerance
                bet_id = f"bet_{market_id}_{selection_id}_{random.randint(1000, 9999)}"
                
                # Simulate partial or full matching
                matched_stake = stake if random.random() > 0.1 else stake * Decimal(str(random.uniform(0.5, 1.0)))
                
                return {
                    "bet_id": bet_id,
                    "market_id": market_id,
                    "selection_id": selection_id,
                    "bet_type": bet_type,
                    "requested_odds": float(odds),
                    "matched_odds": float(runner.back_odds),
                    "requested_stake": float(stake),
                    "matched_stake": float(matched_stake),
                    "status": "MATCHED" if matched_stake == stake else "PARTIALLY_MATCHED",
                    "potential_profit": float((runner.back_odds - 1) * matched_stake),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "Odds not available"}
        
        return {"error": "Bet type not supported in simulation"}
    
    async def get_settled_result(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get settled result for a market."""
        
        if market_id not in self.race_results:
            return None
        
        market = self.markets.get(market_id)
        winning_selection_id = self.race_results[market_id]
        
        if market:
            winner = market.get_runner_by_id(winning_selection_id)
            return {
                "market_id": market_id,
                "winning_selection_id": winning_selection_id,
                "winner_name": winner.name if winner else "Unknown",
                "winning_odds": float(winner.back_odds) if winner else 0.0,
                "settlement_time": datetime.now().isoformat()
            }
        
        return None
    
    async def get_available_markets(self) -> List[Dict[str, Any]]:
        """Get list of all available markets."""
        
        markets = []
        for market in self.markets.values():
            markets.append({
                "market_id": market.market_id,
                "event_name": market.event_name,
                "start_time": market.start_time.isoformat(),
                "state": market.state.value,
                "num_runners": len(market.runners),
                "total_matched": float(market.total_matched)
            })
        
        return markets


# Global simulator instance
_market_simulator: Optional[MarketSimulator] = None


async def get_market_simulator() -> MarketSimulator:
    """Get or create the global market simulator."""
    global _market_simulator
    
    if _market_simulator is None:
        _market_simulator = MarketSimulator()
    
    return _market_simulator


async def create_demo_racing_day() -> Dict[str, Any]:
    """Create a full day of simulated racing for demonstration."""
    
    simulator = await get_market_simulator()
    
    # Create race cards for today
    today = datetime.now().replace(hour=13, minute=0, second=0, microsecond=0)
    
    # Create 3 different tracks
    tracks_schedule = [
        (today, "Newmarket", 4),
        (today + timedelta(hours=2), "Ascot", 3),
        (today + timedelta(hours=4), "York", 3)
    ]
    
    all_markets = []
    for track_time, track_name, num_races in tracks_schedule:
        markets = await simulator.create_realistic_race_card(track_time, num_races)
        all_markets.extend(markets)
    
    # Start market movement simulations for all markets
    tasks = []
    for market in all_markets:
        task = asyncio.create_task(simulator.simulate_market_movements(market.market_id, 60))
        tasks.append(task)
    
    return {
        "status": "Demo racing day created",
        "total_markets": len(all_markets),
        "markets": [
            {
                "market_id": m.market_id,
                "event_name": m.event_name,
                "start_time": m.start_time.isoformat(),
                "num_runners": len(m.runners)
            }
            for m in all_markets
        ],
        "simulation_tasks": len(tasks)
    }
