"""
Paper Trading Integration Module

Integrates the paper trading system with BetDaq infrastructure
to create a comprehensive testing environment for betting strategies.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
import json

from ..services.paper_trading import (
    PaperTradingEngine, 
    PaperBet, 
    PaperMarket, 
    PaperTradingSession
)
from ..services.enhanced_data_extraction import (
    get_enhanced_today_data,
    EnhancedRaceData,
    EnhancedHorseData
)
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class IntegratedTradingEnvironment:
    """
    Integrated trading environment that combines:
    - Paper trading simulation
    - Enhanced race data
    - BetDaq market integration (for reference pricing)
    - Strategy testing framework
    """
    
    def __init__(self):
        self.paper_engine = PaperTradingEngine()
        self.active_sessions: Dict[str, PaperTradingSession] = {}
        
    async def create_comprehensive_demo_session(self) -> PaperTradingSession:
        """Create a comprehensive demo session with real race data."""
        
        try:
            # Get today's enhanced race data
            logger.info("Fetching enhanced race data for demo session...")
            enhanced_races = await get_enhanced_today_data()
            
            if not enhanced_races:
                logger.warning("No enhanced race data available, creating synthetic demo")
                return await self._create_synthetic_demo_session()
            
            # Create session with real data
            session = await self.paper_engine.create_session(
                session_name=f"Demo_RealData_{datetime.now().strftime('%Y%m%d_%H%M')}",
                initial_balance=Decimal('1000.00'),
                risk_settings={
                    'max_bet_amount': Decimal('50.00'),
                    'max_daily_loss': Decimal('200.00'),
                    'max_exposure_per_race': Decimal('100.00')
                }
            )
            
            # Convert enhanced races to paper markets
            markets_created = 0
            for race in enhanced_races[:5]:  # Limit to first 5 races
                try:
                    market = await self._create_market_from_race(race, session.session_id)
                    if market:
                        markets_created += 1
                except Exception as e:
                    logger.error(f"Failed to create market for race {race.race_id}: {e}")
                    continue
            
            logger.info(f"Created demo session with {markets_created} markets from real race data")
            self.active_sessions[session.session_id] = session
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create comprehensive demo session: {e}")
            return await self._create_synthetic_demo_session()
    
    async def _create_market_from_race(
        self, 
        race: EnhancedRaceData, 
        session_id: str
    ) -> Optional[PaperMarket]:
        """Convert enhanced race data to paper market."""
        
        try:
            # Create market
            market = PaperMarket(
                market_id=f"market_{race.race_id}",
                session_id=session_id,
                event_name=f"{race.track_name} R{race.race_number}",
                market_type="WIN",
                event_time=race.race_date,
                total_matched=Decimal('0.00'),
                runners=[]
            )
            
            # Add runners based on horses
            for i, horse in enumerate(race.horses):
                # Calculate realistic odds based on horse data
                odds = self._calculate_realistic_odds(horse, race, i)
                
                runner = {
                    'selection_id': i + 1,
                    'runner_name': horse.name,
                    'back_odds': odds,
                    'lay_odds': odds + Decimal('0.02'),  # Small spread
                    'available_to_back': Decimal('1000.00'),
                    'available_to_lay': Decimal('1000.00'),
                    'last_price_traded': odds,
                    'total_matched': Decimal('0.00'),
                    'win_probability': float(1 / odds) if odds > 0 else 0.1
                }
                market.runners.append(runner)
            
            # Add market to paper engine
            await self.paper_engine.add_market(market)
            
            logger.debug(f"Created market {market.market_id} with {len(market.runners)} runners")
            return market
            
        except Exception as e:
            logger.error(f"Failed to create market from race: {e}")
            return None
    
    def _calculate_realistic_odds(
        self, 
        horse: EnhancedHorseData, 
        race: EnhancedRaceData, 
        position: int
    ) -> Decimal:
        """Calculate realistic odds based on horse and race data."""
        
        try:
            # Base odds calculation
            base_odds = Decimal('5.0')  # Default moderate odds
            
            # Adjust based on form rating
            if horse.recent_form_rating:
                if horse.recent_form_rating >= 8.0:
                    base_odds = Decimal('2.5')  # Favorite
                elif horse.recent_form_rating >= 6.0:
                    base_odds = Decimal('4.0')  # Good chance
                elif horse.recent_form_rating >= 4.0:
                    base_odds = Decimal('7.0')  # Moderate
                else:
                    base_odds = Decimal('12.0')  # Outsider
            
            # Adjust based on field size
            field_size = len(race.horses)
            if field_size > 12:
                base_odds *= Decimal('1.2')  # Longer odds in big fields
            elif field_size < 8:
                base_odds *= Decimal('0.9')  # Shorter odds in small fields
            
            # Adjust based on distance suitability
            if horse.distance_suitability and horse.distance_suitability > 7.0:
                base_odds *= Decimal('0.8')  # Shorter odds if distance suits
            elif horse.distance_suitability and horse.distance_suitability < 4.0:
                base_odds *= Decimal('1.3')  # Longer odds if distance doesn't suit
            
            # Add some randomness based on position (market forces)
            position_factor = 1 + (position * 0.1)
            base_odds *= Decimal(str(position_factor))
            
            # Ensure odds are in reasonable range
            return max(Decimal('1.1'), min(base_odds, Decimal('50.0')))
            
        except Exception as e:
            logger.error(f"Error calculating odds: {e}")
            return Decimal('5.0')  # Default fallback
    
    async def _create_synthetic_demo_session(self) -> PaperTradingSession:
        """Create synthetic demo session when real data isn't available."""
        
        session = await self.paper_engine.create_session(
            session_name=f"Demo_Synthetic_{datetime.now().strftime('%Y%m%d_%H%M')}",
            initial_balance=Decimal('1000.00'),
            risk_settings={
                'max_bet_amount': Decimal('50.00'),
                'max_daily_loss': Decimal('200.00'),
                'max_exposure_per_race': Decimal('100.00')
            }
        )
        
        # Create synthetic markets
        synthetic_races = [
            {
                'track': 'Newmarket',
                'race_num': 1,
                'horses': ['Thunder Bolt', 'Lightning Strike', 'Storm Chaser', 'Wind Runner']
            },
            {
                'track': 'Ascot', 
                'race_num': 2,
                'horses': ['Royal Champion', 'Noble Quest', 'Golden Arrow', 'Silver Bullet', 'Bronze Medal']
            },
            {
                'track': 'Epsom',
                'race_num': 3, 
                'horses': ['Derby Dream', 'Oaks Winner', 'Classic Star', 'Racing Legend']
            }
        ]
        
        for race_data in synthetic_races:
            market = PaperMarket(
                market_id=f"market_synthetic_{race_data['track']}_{race_data['race_num']}",
                session_id=session.session_id,
                event_name=f"{race_data['track']} R{race_data['race_num']}",
                market_type="WIN",
                event_time=datetime.now() + timedelta(minutes=30),
                total_matched=Decimal('0.00'),
                runners=[]
            )
            
            # Add synthetic runners
            for i, horse_name in enumerate(race_data['horses']):
                base_odds = Decimal(str(2.0 + (i * 1.5)))  # Progressive odds
                
                runner = {
                    'selection_id': i + 1,
                    'runner_name': horse_name,
                    'back_odds': base_odds,
                    'lay_odds': base_odds + Decimal('0.02'),
                    'available_to_back': Decimal('1000.00'),
                    'available_to_lay': Decimal('1000.00'),
                    'last_price_traded': base_odds,
                    'total_matched': Decimal('0.00'),
                    'win_probability': float(1 / base_odds)
                }
                market.runners.append(runner)
            
            await self.paper_engine.add_market(market)
        
        self.active_sessions[session.session_id] = session
        logger.info("Created synthetic demo session with 3 markets")
        
        return session
    
    async def demonstrate_strategy_testing(self, session: PaperTradingSession) -> Dict[str, Any]:
        """Demonstrate strategy testing capabilities."""
        
        try:
            results = {
                'session_id': session.session_id,
                'strategies_tested': [],
                'performance_summary': {}
            }
            
            # Get available markets
            markets = await self.paper_engine.get_session_markets(session.session_id)
            
            if not markets:
                logger.warning("No markets available for strategy testing")
                return results
            
            # Strategy 1: Favorite Backing
            logger.info("Testing Strategy 1: Favorite Backing")
            favorite_bets = await self._test_favorite_backing_strategy(session, markets[:2])
            results['strategies_tested'].append({
                'name': 'Favorite Backing',
                'bets_placed': len(favorite_bets),
                'description': 'Back the favorite in each race'
            })
            
            # Strategy 2: Value Betting
            logger.info("Testing Strategy 2: Value Betting")
            value_bets = await self._test_value_betting_strategy(session, markets[:2])
            results['strategies_tested'].append({
                'name': 'Value Betting',
                'bets_placed': len(value_bets),
                'description': 'Back horses with odds > estimated probability'
            })
            
            # Strategy 3: Lay the Field
            logger.info("Testing Strategy 3: Lay the Field")
            lay_bets = await self._test_lay_field_strategy(session, markets[:1])
            results['strategies_tested'].append({
                'name': 'Lay the Field',
                'bets_placed': len(lay_bets),
                'description': 'Lay multiple selections in same race'
            })
            
            # Get updated session performance
            performance = await self.paper_engine.get_session_performance(session.session_id)
            results['performance_summary'] = {
                'total_bets': performance.total_bets,
                'total_stake': float(performance.total_stake),
                'current_balance': float(performance.current_balance),
                'profit_loss': float(performance.profit_loss),
                'win_rate': performance.win_rate
            }
            
            logger.info(f"Strategy testing complete: {len(results['strategies_tested'])} strategies tested")
            return results
            
        except Exception as e:
            logger.error(f"Error in strategy testing: {e}")
            return {'error': str(e)}
    
    async def _test_favorite_backing_strategy(
        self, 
        session: PaperTradingSession, 
        markets: List[PaperMarket]
    ) -> List[PaperBet]:
        """Test favorite backing strategy."""
        
        bets = []
        
        for market in markets:
            try:
                # Find favorite (lowest odds)
                favorite = min(market.runners, key=lambda r: r['back_odds'])
                
                # Place back bet on favorite
                bet = await self.paper_engine.place_bet(
                    session_id=session.session_id,
                    market_id=market.market_id,
                    selection_id=favorite['selection_id'],
                    bet_type="BACK",
                    odds=favorite['back_odds'],
                    stake=Decimal('10.00')  # Fixed stake
                )
                
                if bet:
                    bets.append(bet)
                    logger.debug(f"Placed favorite bet: {favorite['runner_name']} @ {favorite['back_odds']}")
                
            except Exception as e:
                logger.error(f"Error placing favorite bet: {e}")
                continue
        
        return bets
    
    async def _test_value_betting_strategy(
        self, 
        session: PaperTradingSession, 
        markets: List[PaperMarket]
    ) -> List[PaperBet]:
        """Test value betting strategy."""
        
        bets = []
        
        for market in markets:
            try:
                # Look for value bets (odds > implied probability threshold)
                for runner in market.runners:
                    implied_prob = 1 / float(runner['back_odds'])
                    estimated_prob = runner.get('win_probability', implied_prob)
                    
                    # If our estimated probability is higher than implied, it's value
                    if estimated_prob > implied_prob * 1.2:  # 20% edge required
                        bet = await self.paper_engine.place_bet(
                            session_id=session.session_id,
                            market_id=market.market_id,
                            selection_id=runner['selection_id'],
                            bet_type="BACK",
                            odds=runner['back_odds'],
                            stake=Decimal('8.00')  # Fixed stake
                        )
                        
                        if bet:
                            bets.append(bet)
                            logger.debug(f"Placed value bet: {runner['runner_name']} @ {runner['back_odds']}")
                
            except Exception as e:
                logger.error(f"Error placing value bet: {e}")
                continue
        
        return bets
    
    async def _test_lay_field_strategy(
        self, 
        session: PaperTradingSession, 
        markets: List[PaperMarket]
    ) -> List[PaperBet]:
        """Test lay the field strategy."""
        
        bets = []
        
        for market in markets[:1]:  # Only test on one market
            try:
                # Lay multiple selections (not the favorite)
                runners_to_lay = [r for r in market.runners if r['back_odds'] > Decimal('3.0')][:3]
                
                for runner in runners_to_lay:
                    bet = await self.paper_engine.place_bet(
                        session_id=session.session_id,
                        market_id=market.market_id,
                        selection_id=runner['selection_id'],
                        bet_type="LAY",
                        odds=runner['lay_odds'],
                        stake=Decimal('5.00')  # Smaller stake for lay bets
                    )
                    
                    if bet:
                        bets.append(bet)
                        logger.debug(f"Placed lay bet: {runner['runner_name']} @ {runner['lay_odds']}")
                
            except Exception as e:
                logger.error(f"Error placing lay bet: {e}")
                continue
        
        return bets
    
    async def simulate_race_results(self, session_id: str) -> Dict[str, Any]:
        """Simulate race results and settle markets."""
        
        try:
            markets = await self.paper_engine.get_session_markets(session_id)
            results = {}
            
            for market in markets:
                # Simulate race result (favorite wins 30% of time)
                favorite = min(market.runners, key=lambda r: r['back_odds'])
                
                if len(market.runners) > 0:
                    # Weight selection by inverse of odds (favorites more likely to win)
                    weights = [1 / float(r['back_odds']) for r in market.runners]
                    total_weight = sum(weights)
                    
                    # Simple random selection weighted by odds
                    import random
                    rand_val = random.random() * total_weight
                    cumulative = 0
                    winner = market.runners[0]  # Default fallback
                    
                    for i, weight in enumerate(weights):
                        cumulative += weight
                        if rand_val <= cumulative:
                            winner = market.runners[i]
                            break
                    
                    # Settle market
                    settlement_result = await self.paper_engine.settle_market(
                        market.market_id,
                        winner['selection_id']
                    )
                    
                    results[market.market_id] = {
                        'winner': winner['runner_name'],
                        'winning_odds': float(winner['back_odds']),
                        'settlement': settlement_result
                    }
                    
                    logger.info(f"Market {market.market_id} settled: {winner['runner_name']} wins")
            
            return results
            
        except Exception as e:
            logger.error(f"Error simulating race results: {e}")
            return {'error': str(e)}
    
    async def generate_session_report(self, session_id: str) -> Dict[str, Any]:
        """Generate comprehensive session report."""
        
        try:
            # Get session performance
            performance = await self.paper_engine.get_session_performance(session_id)
            
            # Get all bets
            session = self.active_sessions.get(session_id)
            if not session:
                return {'error': 'Session not found'}
            
            # Compile comprehensive report
            report = {
                'session_info': {
                    'session_id': session_id,
                    'session_name': session.session_name,
                    'created_at': session.created_at.isoformat(),
                    'initial_balance': float(session.initial_balance),
                    'risk_settings': {
                        k: float(v) if isinstance(v, Decimal) else v 
                        for k, v in session.risk_settings.items()
                    }
                },
                'performance': {
                    'current_balance': float(performance.current_balance),
                    'total_stake': float(performance.total_stake),
                    'profit_loss': float(performance.profit_loss),
                    'roi': float(performance.roi),
                    'total_bets': performance.total_bets,
                    'winning_bets': performance.winning_bets,
                    'losing_bets': performance.losing_bets,
                    'win_rate': performance.win_rate,
                    'average_odds': performance.average_odds
                },
                'risk_analysis': {
                    'max_exposure_reached': float(performance.max_exposure),
                    'risk_settings_breached': performance.total_stake > session.risk_settings.get('max_daily_loss', Decimal('1000')),
                    'largest_bet': float(max([bet.stake for bet in session.bets] + [Decimal('0')]))
                },
                'recommendations': []
            }
            
            # Add recommendations based on performance
            if performance.win_rate < 0.3:
                report['recommendations'].append("Consider refining selection criteria - win rate below 30%")
            
            if performance.roi < -0.1:
                report['recommendations'].append("Review staking strategy - negative ROI indicates poor value")
            
            if performance.total_bets < 5:
                report['recommendations'].append("Increase sample size for more reliable performance metrics")
            
            logger.info(f"Generated comprehensive report for session {session_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating session report: {e}")
            return {'error': str(e)}


# Global integrated environment instance
_integrated_environment: Optional[IntegratedTradingEnvironment] = None


async def get_integrated_environment() -> IntegratedTradingEnvironment:
    """Get or create the global integrated trading environment."""
    global _integrated_environment
    
    if _integrated_environment is None:
        _integrated_environment = IntegratedTradingEnvironment()
    
    return _integrated_environment


async def run_full_demo() -> Dict[str, Any]:
    """Run a full demonstration of the integrated trading environment."""
    
    logger.info("🎯 Starting full integrated trading environment demo...")
    
    try:
        # Get environment
        env = await get_integrated_environment()
        
        # Create comprehensive demo session
        session = await env.create_comprehensive_demo_session()
        
        # Demonstrate strategy testing
        strategy_results = await env.demonstrate_strategy_testing(session)
        
        # Simulate race results
        race_results = await env.simulate_race_results(session.session_id)
        
        # Generate final report
        final_report = await env.generate_session_report(session.session_id)
        
        demo_results = {
            'demo_status': 'completed',
            'session_created': session.session_id,
            'strategy_testing': strategy_results,
            'race_simulations': race_results,
            'final_report': final_report,
            'summary': {
                'total_markets': len(race_results),
                'strategies_tested': len(strategy_results.get('strategies_tested', [])),
                'final_balance': final_report.get('performance', {}).get('current_balance', 0),
                'roi': final_report.get('performance', {}).get('roi', 0)
            }
        }
        
        logger.info("🎉 Full demo completed successfully!")
        return demo_results
        
    except Exception as e:
        logger.error(f"Error in full demo: {e}")
        return {'error': str(e), 'demo_status': 'failed'}
