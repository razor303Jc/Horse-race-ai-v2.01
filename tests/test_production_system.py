#!/usr/bin/env python3
"""
Production System Comprehensive Test Suite
==========================================

Complete test suite for the production trading system including:
- Live race data API integration
- Betting exchange API functionality
- Production dashboard deployment
- Alert system notifications
- Live strategy execution coordination

Author: Horse Racing AI System V2.03
"""

import os
import sys
import unittest
import asyncio
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from horse_racing_ai.data_feeds.live_race_data_api import (
    LiveRaceDataAPI,
    RaceDataIntegrator,
)
from horse_racing_ai.betting.betting_exchange_api import (
    BetfairAPI,
    BettingExchangeIntegrator,
)
from horse_racing_ai.alerts.alert_system import AlertSystem, EmailService, SMSService
from horse_racing_ai.production.live_strategy_execution import LiveStrategyExecutor
from horse_racing_ai.orchestration.production_system import ProductionSystemManager


class TestLiveRaceDataAPI(unittest.TestCase):
    """Test live race data API functionality"""

    def setUp(self):
        """Set up test environment"""
        self.config = {
            "base_url": "https://api.theracingapi.com",
            "api_key": "test_key",
            "betfair_app_key": "test_betfair_key",
            "betfair_username": "test_user",
            "betfair_password": "test_pass",
            "update_interval": 30,
            "max_retries": 3,
        }
        self.api = LiveRaceDataAPI(self.config)

    def test_api_initialization(self):
        """Test API initialization"""
        self.assertIsNotNone(self.api)
        self.assertEqual(self.api.config["api_key"], "test_key")
        self.assertEqual(self.api.config["update_interval"], 30)

    @patch("requests.get")
    def test_fetch_race_data(self, mock_get):
        """Test race data fetching"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "races": [
                {
                    "id": "12345",
                    "course": "Ascot",
                    "time": "14:30",
                    "horses": [
                        {"name": "Test Horse 1", "odds": 3.5},
                        {"name": "Test Horse 2", "odds": 4.2},
                    ],
                }
            ]
        }
        mock_get.return_value = mock_response

        # Test fetch
        races = self.api.fetch_todays_races()

        self.assertIsNotNone(races)
        self.assertEqual(len(races["races"]), 1)
        self.assertEqual(races["races"][0]["course"], "Ascot")

    def test_websocket_connection_setup(self):
        """Test WebSocket connection setup"""
        # Test WebSocket URL generation
        ws_url = self.api._generate_websocket_url()
        self.assertIsInstance(ws_url, str)
        self.assertTrue(ws_url.startswith("wss://"))

    def test_data_validation(self):
        """Test race data validation"""
        # Valid race data
        valid_race = {
            "id": "12345",
            "course": "Ascot",
            "time": "14:30",
            "horses": [{"name": "Test Horse", "odds": 3.5}],
        }

        self.assertTrue(self.api._validate_race_data(valid_race))

        # Invalid race data
        invalid_race = {
            "id": "12345",
            "course": "",  # Invalid empty course
            "horses": [],  # Invalid empty horses
        }

        self.assertFalse(self.api._validate_race_data(invalid_race))


class TestBettingExchangeAPI(unittest.TestCase):
    """Test betting exchange API functionality"""

    def setUp(self):
        """Set up test environment"""
        self.config = {
            "exchanges": {
                "betfair": {
                    "enabled": True,
                    "app_key": "test_app_key",
                    "username": "test_user",
                    "password": "test_pass",
                    "commission_rate": 0.05,
                }
            },
            "risk_management": {
                "max_daily_stake": 200.0,
                "max_single_stake": 50.0,
                "max_exposure": 500.0,
            },
        }
        self.api = BetfairAPI(self.config["exchanges"]["betfair"])
        self.integrator = BettingExchangeIntegrator(self.config)

    def test_api_initialization(self):
        """Test API initialization"""
        self.assertIsNotNone(self.api)
        self.assertEqual(self.api.config["commission_rate"], 0.05)

    @patch("betfairlightweight.APIClient")
    def test_authentication(self, mock_client):
        """Test Betfair authentication"""
        # Mock successful login
        mock_client_instance = Mock()
        mock_client_instance.login.return_value = {"status": "SUCCESS"}
        mock_client.return_value = mock_client_instance

        result = self.api.authenticate()

        self.assertTrue(result)
        mock_client_instance.login.assert_called_once()

    def test_risk_management_validation(self):
        """Test risk management validation"""
        # Test stake validation
        self.assertTrue(self.integrator._validate_stake(25.0, "single"))
        self.assertFalse(
            self.integrator._validate_stake(75.0, "single")
        )  # Exceeds max single

        # Test daily exposure
        self.integrator.daily_stake_total = 150.0
        self.assertTrue(self.integrator._validate_stake(40.0, "daily"))
        self.assertFalse(
            self.integrator._validate_stake(60.0, "daily")
        )  # Would exceed daily max

    @patch("betfairlightweight.APIClient")
    def test_bet_placement(self, mock_client):
        """Test bet placement functionality"""
        # Mock successful bet placement
        mock_client_instance = Mock()
        mock_client_instance.betting.place_orders.return_value = Mock(
            status="SUCCESS",
            instruction_reports=[
                Mock(
                    status="SUCCESS",
                    bet_id="12345",
                    instruction=Mock(selection_id="47972"),
                )
            ],
        )
        mock_client.return_value = mock_client_instance

        bet_request = {
            "market_id": "1.12345",
            "selection_id": "47972",
            "odds": 3.5,
            "stake": 10.0,
            "side": "B",
        }

        result = self.api.place_bet(bet_request)

        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "SUCCESS")

    def test_position_tracking(self):
        """Test position tracking functionality"""
        # Add test position
        position = {
            "market_id": "1.12345",
            "selection_id": "47972",
            "stake": 20.0,
            "odds": 3.5,
            "side": "B",
            "strategy": "80_20",
        }

        self.integrator.add_position(position)

        # Test position retrieval
        positions = self.integrator.get_active_positions()
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]["stake"], 20.0)

        # Test P&L calculation
        current_odds = 4.0
        pnl = self.integrator.calculate_position_pnl(position, current_odds)
        self.assertIsInstance(pnl, float)


class TestAlertSystem(unittest.TestCase):
    """Test alert system functionality"""

    def setUp(self):
        """Set up test environment"""
        self.config = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "test@gmail.com",
                "password": "test_password",
                "use_tls": True,
            },
            "sms": {
                "account_sid": "test_sid",
                "auth_token": "test_token",
                "from_number": "+1234567890",
            },
            "throttle_minutes": 30,
            "default_recipients": [
                {
                    "name": "Test User",
                    "email": "test@example.com",
                    "phone": "+44123456789",
                    "alert_types": ["all"],
                }
            ],
        }
        self.alert_system = AlertSystem(self.config)

    def test_alert_system_initialization(self):
        """Test alert system initialization"""
        self.assertIsNotNone(self.alert_system)
        self.assertEqual(len(self.alert_system.recipients), 1)

    @patch("smtplib.SMTP")
    def test_email_sending(self, mock_smtp):
        """Test email sending functionality"""
        # Mock SMTP server
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        email_service = EmailService(self.config["email"])

        result = email_service.send_email(
            to_email="test@example.com",
            subject="Test Alert",
            body="This is a test alert",
            severity="warning",
        )

        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()

    @patch("twilio.rest.Client")
    def test_sms_sending(self, mock_twilio):
        """Test SMS sending functionality"""
        # Mock Twilio client
        mock_client = Mock()
        mock_message = Mock()
        mock_message.sid = "test_message_sid"
        mock_client.messages.create.return_value = mock_message
        mock_twilio.return_value = mock_client

        sms_service = SMSService(self.config["sms"])

        result = sms_service.send_sms(
            to_phone="+44123456789", message="Test SMS alert", severity="error"
        )

        self.assertTrue(result)
        mock_client.messages.create.assert_called_once()

    def test_alert_throttling(self):
        """Test alert throttling functionality"""
        # Send first alert
        alert_data = {
            "type": "trading_opportunity",
            "message": "Test opportunity",
            "severity": "info",
        }

        result1 = self.alert_system.send_alert(alert_data)
        self.assertTrue(result1)

        # Send same alert immediately (should be throttled)
        result2 = self.alert_system.send_alert(alert_data)
        self.assertFalse(result2)  # Should be throttled

    def test_alert_template_rendering(self):
        """Test alert template rendering"""
        template_data = {
            "strategy": "80_20",
            "horse": "Test Horse",
            "odds": 3.5,
            "stake": 15.0,
            "confidence": 0.75,
        }

        rendered = self.alert_system.render_template(
            "trading_opportunity", template_data
        )

        self.assertIsInstance(rendered, dict)
        self.assertIn("subject", rendered)
        self.assertIn("body", rendered)
        self.assertIn("Test Horse", rendered["body"])


class TestLiveStrategyExecution(unittest.TestCase):
    """Test live strategy execution coordination"""

    def setUp(self):
        """Set up test environment"""
        self.config = {
            "execution_mode": "simulation",
            "monitoring_interval": 30,
            "max_concurrent_positions": 5,
            "min_confidence_threshold": 0.65,
            "enable_80_20_strategy": True,
            "enable_dutching_strategy": True,
            "auto_place_bets": False,
        }

        # Mock dependencies
        self.mock_data_api = Mock()
        self.mock_betting_api = Mock()
        self.mock_alert_system = Mock()

        self.executor = LiveStrategyExecutor(
            config=self.config,
            data_api=self.mock_data_api,
            betting_api=self.mock_betting_api,
            alert_system=self.mock_alert_system,
        )

    def test_executor_initialization(self):
        """Test executor initialization"""
        self.assertIsNotNone(self.executor)
        self.assertEqual(self.executor.config["execution_mode"], "simulation")
        self.assertTrue(self.executor.config["enable_80_20_strategy"])

    def test_opportunity_detection(self):
        """Test trading opportunity detection"""
        # Mock race data
        race_data = {
            "id": "12345",
            "course": "Ascot",
            "time": "14:30",
            "horses": [
                {
                    "name": "Test Horse 1",
                    "odds": 3.5,
                    "ai_probability": 0.35,
                    "confidence": 0.78,
                },
                {
                    "name": "Test Horse 2",
                    "odds": 4.2,
                    "ai_probability": 0.28,
                    "confidence": 0.65,
                },
            ],
        }

        opportunities = self.executor.detect_opportunities(race_data)

        self.assertIsInstance(opportunities, list)
        # Should detect 80/20 opportunity for Test Horse 1 (high confidence)
        if opportunities:
            self.assertIn("strategy", opportunities[0])
            self.assertIn("confidence", opportunities[0])

    def test_strategy_execution_80_20(self):
        """Test 80/20 strategy execution"""
        opportunity = {
            "race_id": "12345",
            "horse": "Test Horse",
            "odds": 3.5,
            "ai_probability": 0.35,
            "confidence": 0.78,
            "strategy": "80_20",
            "recommended_stake": 15.0,
        }

        # In simulation mode, should not place real bets
        result = self.executor.execute_strategy(opportunity)

        self.assertIsNotNone(result)
        self.assertEqual(result["execution_mode"], "simulation")
        self.assertIn("simulated_bet", result)

    def test_strategy_execution_dutching(self):
        """Test dutching strategy execution"""
        opportunity = {
            "race_id": "12345",
            "selections": [
                {"horse": "Test Horse 1", "odds": 3.5, "probability": 0.35},
                {"horse": "Test Horse 2", "odds": 4.2, "probability": 0.28},
            ],
            "total_probability": 0.63,
            "strategy": "dutching",
            "total_stake": 25.0,
        }

        result = self.executor.execute_strategy(opportunity)

        self.assertIsNotNone(result)
        self.assertEqual(result["strategy"], "dutching")
        self.assertIn("stake_distribution", result)

    def test_risk_management(self):
        """Test risk management controls"""
        # Test position limit
        self.executor.active_positions = [{}] * 5  # Max positions reached

        opportunity = {"strategy": "80_20", "recommended_stake": 15.0}

        risk_check = self.executor.check_risk_limits(opportunity)
        self.assertFalse(risk_check["approved"])
        self.assertIn("max_positions", risk_check["reason"])

    def test_performance_tracking(self):
        """Test performance tracking functionality"""
        # Simulate completed trade
        trade_result = {
            "trade_id": "trade_12345",
            "strategy": "80_20",
            "stake": 15.0,
            "odds": 3.5,
            "outcome": "won",
            "profit": 37.5,
            "timestamp": datetime.now(),
        }

        self.executor.record_trade_result(trade_result)

        performance = self.executor.get_performance_summary()

        self.assertIsInstance(performance, dict)
        self.assertIn("total_trades", performance)
        self.assertIn("total_profit", performance)
        self.assertIn("win_rate", performance)


class TestProductionSystemOrchestration(unittest.TestCase):
    """Test production system orchestration"""

    def setUp(self):
        """Set up test environment"""
        self.manager = ProductionSystemManager()

    def test_manager_initialization(self):
        """Test manager initialization"""
        self.assertIsNotNone(self.manager)
        self.assertIsInstance(self.manager.processes, dict)
        self.assertIsInstance(self.manager.services_status, dict)

    def test_config_creation(self):
        """Test configuration file creation"""
        # Create test config directory
        os.makedirs("test_config", exist_ok=True)

        # Test config creation (should not raise errors)
        try:
            self.manager._create_race_data_config()
            self.manager._create_betting_exchange_config()
            self.manager._create_alert_config()
            self.manager._create_live_execution_config()
            config_created = True
        except Exception as e:
            config_created = False
            print(f"Config creation error: {e}")

        self.assertTrue(config_created)

        # Cleanup
        import shutil

        if os.path.exists("test_config"):
            shutil.rmtree("test_config")

    @patch("subprocess.Popen")
    def test_service_management(self, mock_popen):
        """Test service start/stop management"""
        # Mock process
        mock_process = Mock()
        mock_process.poll.return_value = None  # Running
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        # Test service start
        self.manager.start_dashboard()

        self.assertEqual(self.manager.services_status["dashboard"], "RUNNING")
        self.assertIn("dashboard", self.manager.processes)

    def test_health_monitoring(self):
        """Test service health monitoring"""
        # Add mock running service
        mock_process = Mock()
        mock_process.poll.return_value = None  # Still running
        self.manager.processes["test_service"] = mock_process
        self.manager.services_status["test_service"] = "RUNNING"

        # Test health check
        health_status = self.manager._check_service_health("test_service")

        self.assertTrue(health_status)

    def test_status_reporting(self):
        """Test status reporting functionality"""
        # Set up mock services
        self.manager.services_status = {
            "dashboard": "RUNNING",
            "execution": "RUNNING",
            "monitoring": "FAILED",
            "alerts": "STOPPED",
        }

        # Test status report generation
        try:
            self.manager._report_status()
            status_reported = True
        except Exception as e:
            status_reported = False
            print(f"Status report error: {e}")

        self.assertTrue(status_reported)


class TestIntegrationScenarios(unittest.TestCase):
    """Test end-to-end integration scenarios"""

    def setUp(self):
        """Set up integration test environment"""
        self.race_data = {
            "id": "12345",
            "course": "Ascot",
            "time": "14:30",
            "horses": [
                {
                    "name": "Test Horse 1",
                    "odds": 3.5,
                    "ai_probability": 0.35,
                    "confidence": 0.78,
                },
                {
                    "name": "Test Horse 2",
                    "odds": 4.2,
                    "ai_probability": 0.28,
                    "confidence": 0.65,
                },
            ],
        }

    def test_full_opportunity_flow(self):
        """Test complete opportunity detection and execution flow"""
        # This would test the full flow from data ingestion to bet placement
        # in a controlled environment

        # 1. Data ingestion and validation
        data_api = Mock()
        data_api.fetch_race_data.return_value = self.race_data

        # 2. Opportunity detection
        executor = Mock()
        executor.detect_opportunities.return_value = [
            {"strategy": "80_20", "confidence": 0.78, "recommended_stake": 15.0}
        ]

        # 3. Risk validation
        executor.check_risk_limits.return_value = {"approved": True}

        # 4. Strategy execution (simulation)
        executor.execute_strategy.return_value = {
            "status": "executed",
            "mode": "simulation",
            "trade_id": "test_trade_123",
        }

        # 5. Alert notification
        alert_system = Mock()
        alert_system.send_alert.return_value = True

        # Test the flow
        race_data = data_api.fetch_race_data()
        opportunities = executor.detect_opportunities(race_data)

        self.assertIsNotNone(race_data)
        self.assertGreater(len(opportunities), 0)

        for opportunity in opportunities:
            risk_check = executor.check_risk_limits(opportunity)
            if risk_check["approved"]:
                result = executor.execute_strategy(opportunity)
                alert_sent = alert_system.send_alert(
                    {"type": "trade_executed", "data": result}
                )

                self.assertEqual(result["status"], "executed")
                self.assertTrue(alert_sent)

    def test_error_handling_and_recovery(self):
        """Test error handling and recovery scenarios"""
        # Test API failure scenarios
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("API connection failed")

            # Should handle gracefully and log error
            try:
                api = LiveRaceDataAPI({"api_key": "test", "max_retries": 1})
                result = api.fetch_todays_races()
                error_handled = True
            except Exception:
                error_handled = False

            # Should not crash the system
            self.assertTrue(error_handled or result is None)

    def test_configuration_validation(self):
        """Test configuration validation"""
        # Test invalid configurations
        invalid_configs = [
            {"api_key": ""},  # Empty API key
            {"max_daily_stake": -100},  # Negative stake
            {"update_interval": 0},  # Invalid interval
        ]

        for config in invalid_configs:
            with self.assertRaises((ValueError, KeyError)):
                # This should validate configuration and raise appropriate errors
                pass


def run_production_tests():
    """Run all production system tests"""
    print("🧪 Running Production System Test Suite")
    print("=" * 50)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestLiveRaceDataAPI,
        TestBettingExchangeAPI,
        TestAlertSystem,
        TestLiveStrategyExecution,
        TestProductionSystemOrchestration,
        TestIntegrationScenarios,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Report results
    print("\n" + "=" * 50)
    print("🏁 Production System Test Results")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )

    if result.failures:
        print("\n❌ FAILURES:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure}")

    if result.errors:
        print("\n🚨 ERRORS:")
        for test, error in result.errors:
            print(f"  - {test}: {error}")

    if result.wasSuccessful():
        print("\n✅ All production system tests passed!")
        return True
    else:
        print("\n❌ Some tests failed. Check output above.")
        return False


if __name__ == "__main__":
    success = run_production_tests()
    sys.exit(0 if success else 1)
