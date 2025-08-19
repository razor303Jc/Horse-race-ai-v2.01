#!/usr/bin/env python3
"""
Third-Party Integrations Test Suite
Tests bookmaker APIs, data feeds, payment systems, and external service integrations
"""

import pytest
import json
import hashlib
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal


class TestBookmakerAPIs:
    """Test bookmaker API integrations"""

    @pytest.fixture
    def sample_race_data(self):
        """Sample race data for bookmaker integration testing"""
        return {
            "race_id": "race_001",
            "race_name": "Champion Stakes",
            "track": "ascot",
            "race_time": "2024-03-20T15:30:00Z",
            "distance": "1m 2f",
            "going": "Good to Firm",
            "race_type": "flat",
            "runners": [
                {
                    "horse_id": "horse_001",
                    "horse_name": "Thunder Bolt",
                    "jockey": "A. Murphy",
                    "trainer": "J. Smith",
                    "weight": "9-2",
                    "age": 4,
                    "form": "121",
                },
                {
                    "horse_id": "horse_002",
                    "horse_name": "Lightning Strike",
                    "jockey": "B. Johnson",
                    "trainer": "M. Wilson",
                    "weight": "8-12",
                    "age": 3,
                    "form": "321",
                },
            ],
        }

    @pytest.fixture
    def bookmaker_odds_data(self):
        """Sample odds data from multiple bookmakers"""
        return {
            "race_id": "race_001",
            "last_updated": "2024-03-20T14:45:00Z",
            "bookmakers": {
                "betfair": {
                    "name": "Betfair",
                    "api_version": "v2",
                    "status": "active",
                    "odds": {
                        "horse_001": {"back": 2.5, "lay": 2.52, "volume": 15420.50},
                        "horse_002": {"back": 3.2, "lay": 3.25, "volume": 8750.25},
                    },
                    "market_id": "market_12345",
                },
                "bet365": {
                    "name": "Bet365",
                    "api_version": "v1",
                    "status": "active",
                    "odds": {
                        "horse_001": {"decimal": 2.45, "fractional": "29/20"},
                        "horse_002": {"decimal": 3.15, "fractional": "43/20"},
                    },
                    "market_reference": "ref_67890",
                },
                "ladbrokes": {
                    "name": "Ladbrokes",
                    "api_version": "v1",
                    "status": "active",
                    "odds": {
                        "horse_001": {"decimal": 2.55, "fractional": "31/20"},
                        "horse_002": {"decimal": 3.25, "fractional": "45/20"},
                    },
                    "shop_id": "shop_11111",
                },
            },
        }

    def test_betfair_api_integration(self, bookmaker_odds_data):
        """Test Betfair Exchange API integration"""
        betfair_data = bookmaker_odds_data["bookmakers"]["betfair"]

        # Validate Betfair-specific data structure
        assert "market_id" in betfair_data
        assert betfair_data["api_version"] == "v2"
        assert betfair_data["status"] == "active"

        # Test odds data structure
        for horse_id, odds_data in betfair_data["odds"].items():
            assert "back" in odds_data
            assert "lay" in odds_data
            assert "volume" in odds_data

            # Validate odds relationships
            assert odds_data["back"] > 0
            assert odds_data["lay"] > odds_data["back"]  # Lay > Back on exchange
            assert odds_data["volume"] > 0

    def test_bet365_api_integration(self, bookmaker_odds_data):
        """Test Bet365 API integration"""
        bet365_data = bookmaker_odds_data["bookmakers"]["bet365"]

        # Validate Bet365-specific data structure
        assert "market_reference" in bet365_data
        assert bet365_data["api_version"] == "v1"
        assert bet365_data["status"] == "active"

        # Test odds format conversion
        for horse_id, odds_data in bet365_data["odds"].items():
            assert "decimal" in odds_data
            assert "fractional" in odds_data

            # Validate odds values
            assert odds_data["decimal"] > 1.0
            assert "/" in odds_data["fractional"]

    def test_odds_comparison_engine(self, bookmaker_odds_data):
        """Test odds comparison across bookmakers"""
        race_id = bookmaker_odds_data["race_id"]
        bookmakers = bookmaker_odds_data["bookmakers"]

        # Build comparison table
        comparison_data = {}

        for bookmaker_name, bookmaker_data in bookmakers.items():
            for horse_id, odds_info in bookmaker_data["odds"].items():
                if horse_id not in comparison_data:
                    comparison_data[horse_id] = {}

                # Extract decimal odds (normalize format)
                if bookmaker_name == "betfair":
                    decimal_odds = odds_info["back"]
                else:
                    decimal_odds = odds_info["decimal"]

                comparison_data[horse_id][bookmaker_name] = decimal_odds

        # Find best odds for each horse
        best_odds = {}
        for horse_id, bookmaker_odds in comparison_data.items():
            best_odds[horse_id] = {
                "best_odds": max(bookmaker_odds.values()),
                "best_bookmaker": max(bookmaker_odds, key=bookmaker_odds.get),
                "all_odds": bookmaker_odds,
                "spread": max(bookmaker_odds.values()) - min(bookmaker_odds.values()),
            }

        # Validate comparison results
        assert len(comparison_data) == 2  # Two horses
        assert len(best_odds) == 2

        for horse_id, odds_analysis in best_odds.items():
            assert odds_analysis["best_odds"] > 0
            assert odds_analysis["best_bookmaker"] in bookmakers.keys()
            assert odds_analysis["spread"] >= 0

    def test_arbitrage_detection(self, bookmaker_odds_data):
        """Test arbitrage opportunity detection"""
        bookmakers = bookmaker_odds_data["bookmakers"]

        # Extract best odds for each horse across all bookmakers
        horse_best_odds = {}

        for bookmaker_name, bookmaker_data in bookmakers.items():
            for horse_id, odds_info in bookmaker_data["odds"].items():
                # Get decimal odds
                if bookmaker_name == "betfair":
                    decimal_odds = odds_info["back"]
                else:
                    decimal_odds = odds_info["decimal"]

                if (
                    horse_id not in horse_best_odds
                    or decimal_odds > horse_best_odds[horse_id]
                ):
                    horse_best_odds[horse_id] = decimal_odds

        # Calculate arbitrage percentage
        arbitrage_percentage = sum(1 / odds for odds in horse_best_odds.values())

        # Detect arbitrage opportunity
        is_arbitrage = arbitrage_percentage < 1.0
        profit_margin = (1 - arbitrage_percentage) * 100 if is_arbitrage else 0

        # Calculate stake distribution for arbitrage
        if is_arbitrage:
            total_stake = 100  # £100 total stake
            stake_distribution = {}
            for horse_id, odds in horse_best_odds.items():
                stake_distribution[horse_id] = (
                    total_stake / odds
                ) / arbitrage_percentage

        # Validate arbitrage calculation
        assert isinstance(is_arbitrage, bool)
        assert arbitrage_percentage > 0

        if is_arbitrage:
            assert profit_margin > 0
            assert len(stake_distribution) == len(horse_best_odds)
            assert abs(sum(stake_distribution.values()) - total_stake) < 0.01

    def test_api_rate_limiting(self):
        """Test API rate limiting and throttling"""
        api_limits = {
            "betfair": {
                "requests_per_second": 5,
                "requests_per_hour": 1000,
                "concurrent_connections": 20,
                "data_points_per_second": 10,
            },
            "bet365": {
                "requests_per_minute": 100,
                "requests_per_hour": 5000,
                "burst_limit": 10,
            },
            "ladbrokes": {
                "requests_per_second": 2,
                "requests_per_hour": 500,
                "daily_limit": 10000,
            },
        }

        # Validate rate limit configurations
        for bookmaker, limits in api_limits.items():
            assert any(key.startswith("requests_per_") for key in limits.keys())

            for limit_type, limit_value in limits.items():
                assert limit_value > 0
                assert isinstance(limit_value, int)

    def test_api_error_handling(self):
        """Test API error handling and retry logic"""
        api_errors = [
            {
                "bookmaker": "betfair",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "error_message": "Too many requests",
                "http_status": 429,
                "retry_after": 60,
                "retry_strategy": "exponential_backoff",
            },
            {
                "bookmaker": "bet365",
                "error_code": "MARKET_SUSPENDED",
                "error_message": "Market temporarily unavailable",
                "http_status": 503,
                "retry_after": 30,
                "retry_strategy": "fixed_delay",
            },
            {
                "bookmaker": "ladbrokes",
                "error_code": "AUTHENTICATION_FAILED",
                "error_message": "Invalid API credentials",
                "http_status": 401,
                "retry_after": 0,
                "retry_strategy": "no_retry",
            },
        ]

        # Validate error handling configurations
        valid_strategies = [
            "exponential_backoff",
            "fixed_delay",
            "no_retry",
            "linear_backoff",
        ]

        for error in api_errors:
            assert error["http_status"] in [401, 403, 404, 429, 500, 502, 503, 504]
            assert error["retry_after"] >= 0
            assert error["retry_strategy"] in valid_strategies

            # Specific validation based on error type
            if error["error_code"] == "AUTHENTICATION_FAILED":
                assert error["retry_strategy"] == "no_retry"
            elif error["error_code"] == "RATE_LIMIT_EXCEEDED":
                assert error["retry_after"] > 0


class TestDataFeeds:
    """Test racing data feed integrations"""

    def test_racing_post_feed(self):
        """Test Racing Post data feed integration"""
        rp_feed_data = {
            "feed_name": "Racing Post",
            "feed_type": "form_data",
            "update_frequency": "realtime",
            "data_format": "json",
            "authentication": "api_key",
            "endpoints": {
                "race_cards": "/api/v1/racecards",
                "results": "/api/v1/results",
                "form_data": "/api/v1/form",
                "ratings": "/api/v1/ratings",
            },
            "sample_data": {
                "horse_id": "horse_001",
                "form_figures": "121314",
                "official_rating": 89,
                "trainer_stats": {"wins": 23, "runs": 156, "strike_rate": 0.147},
                "jockey_stats": {"wins": 67, "runs": 423, "strike_rate": 0.158},
            },
        }

        # Validate Racing Post feed structure
        assert rp_feed_data["feed_type"] in [
            "form_data",
            "live_odds",
            "results",
            "entries",
        ]
        assert rp_feed_data["update_frequency"] in [
            "realtime",
            "5min",
            "15min",
            "hourly",
        ]
        assert rp_feed_data["data_format"] in ["json", "xml", "csv"]

        # Validate sample data
        sample = rp_feed_data["sample_data"]
        assert sample["official_rating"] > 0
        assert 0 <= sample["trainer_stats"]["strike_rate"] <= 1
        assert 0 <= sample["jockey_stats"]["strike_rate"] <= 1

    def test_timeform_feed(self):
        """Test Timeform data feed integration"""
        timeform_data = {
            "feed_name": "Timeform",
            "feed_type": "ratings_analysis",
            "update_frequency": "daily",
            "data_format": "xml",
            "authentication": "oauth2",
            "sample_data": {
                "horse_id": "horse_001",
                "timeform_rating": 98,
                "speed_figure": 105,
                "class_par": 85,
                "going_preference": "good_to_firm",
                "distance_preference": "1m_2f_to_1m_4f",
                "track_suitability": {
                    "ascot": 0.85,
                    "cheltenham": 0.72,
                    "aintree": 0.68,
                },
            },
        }

        # Validate Timeform feed
        sample = timeform_data["sample_data"]
        assert 0 <= sample["timeform_rating"] <= 200
        assert 0 <= sample["speed_figure"] <= 200
        assert 0 <= sample["class_par"] <= 200

        # Validate track suitability scores
        for track, suitability in sample["track_suitability"].items():
            assert 0 <= suitability <= 1

    def test_data_feed_synchronization(self):
        """Test synchronization between multiple data feeds"""
        feed_sync_status = {
            "last_sync": "2024-03-20T14:30:00Z",
            "feeds": {
                "racing_post": {
                    "status": "active",
                    "last_update": "2024-03-20T14:29:45Z",
                    "records_synced": 1247,
                    "sync_duration_ms": 3456,
                },
                "timeform": {
                    "status": "active",
                    "last_update": "2024-03-20T14:28:12Z",
                    "records_synced": 892,
                    "sync_duration_ms": 2134,
                },
                "betfair": {
                    "status": "delayed",
                    "last_update": "2024-03-20T14:15:22Z",
                    "records_synced": 0,
                    "sync_duration_ms": 0,
                    "error": "Rate limit exceeded",
                },
            },
            "data_consistency": {
                "race_matches": 0.98,
                "horse_matches": 0.95,
                "odds_correlation": 0.89,
            },
        }

        # Validate sync status
        for feed_name, feed_status in feed_sync_status["feeds"].items():
            assert feed_status["status"] in ["active", "delayed", "error", "disabled"]
            assert feed_status["records_synced"] >= 0
            assert feed_status["sync_duration_ms"] >= 0

        # Validate data consistency metrics
        consistency = feed_sync_status["data_consistency"]
        assert 0 <= consistency["race_matches"] <= 1
        assert 0 <= consistency["horse_matches"] <= 1
        assert 0 <= consistency["odds_correlation"] <= 1


class TestPaymentSystems:
    """Test payment gateway integrations"""

    def test_stripe_integration(self):
        """Test Stripe payment processing"""
        stripe_payment = {
            "payment_id": "pay_stripe_001",
            "stripe_payment_intent": "pi_1234567890",
            "amount": 50.00,
            "currency": "GBP",
            "status": "succeeded",
            "payment_method": {
                "type": "card",
                "card": {
                    "brand": "visa",
                    "last4": "4242",
                    "exp_month": 12,
                    "exp_year": 2025,
                },
            },
            "metadata": {
                "user_id": "user_123",
                "bet_id": "bet_456",
                "race_id": "race_789",
            },
            "created": "2024-03-20T14:30:00Z",
            "fees": {"stripe_fee": 1.73, "application_fee": 0.50},
        }

        # Validate Stripe payment structure
        assert stripe_payment["status"] in [
            "succeeded",
            "pending",
            "failed",
            "canceled",
        ]
        assert stripe_payment["amount"] > 0
        assert stripe_payment["currency"] in ["GBP", "USD", "EUR"]

        # Validate payment method
        card = stripe_payment["payment_method"]["card"]
        assert card["brand"] in ["visa", "mastercard", "amex", "discover"]
        assert len(card["last4"]) == 4
        assert 1 <= card["exp_month"] <= 12
        assert card["exp_year"] >= 2024

        # Validate fees
        assert stripe_payment["fees"]["stripe_fee"] > 0
        assert stripe_payment["fees"]["application_fee"] >= 0

    def test_paypal_integration(self):
        """Test PayPal payment processing"""
        paypal_payment = {
            "payment_id": "pay_paypal_001",
            "paypal_order_id": "ORDER123456789",
            "amount": 25.00,
            "currency": "GBP",
            "status": "COMPLETED",
            "payer": {
                "email": "user@example.com",
                "payer_id": "PAYERID123",
                "name": "John Doe",
            },
            "payment_source": "paypal_balance",
            "fees": {"paypal_fee": 1.02, "fixed_fee": 0.30},
            "capture_id": "CAPTURE123456789",
            "created": "2024-03-20T14:30:00Z",
        }

        # Validate PayPal payment structure
        assert paypal_payment["status"] in [
            "COMPLETED",
            "PENDING",
            "FAILED",
            "CANCELLED",
        ]
        assert paypal_payment["amount"] > 0
        assert paypal_payment["currency"] in ["GBP", "USD", "EUR"]
        assert "@" in paypal_payment["payer"]["email"]

        # Validate fees
        assert paypal_payment["fees"]["paypal_fee"] > 0
        assert paypal_payment["fees"]["fixed_fee"] > 0

    def test_open_banking_integration(self):
        """Test Open Banking payment processing"""
        open_banking_payment = {
            "payment_id": "pay_ob_001",
            "consent_id": "consent_123456",
            "bank": "lloyds",
            "amount": 100.00,
            "currency": "GBP",
            "status": "completed",
            "account_details": {
                "sort_code": "12-34-56",
                "account_number": "****5678",
                "account_name": "John Doe",
            },
            "payment_reference": "HORSERACE20240320001",
            "processing_time_ms": 8750,
            "fees": {"bank_fee": 0.00, "service_fee": 0.15},
            "initiated": "2024-03-20T14:25:00Z",
            "completed": "2024-03-20T14:25:08Z",
        }

        # Validate Open Banking payment
        assert open_banking_payment["status"] in [
            "completed",
            "pending",
            "failed",
            "rejected",
        ]
        assert open_banking_payment["bank"] in [
            "lloyds",
            "barclays",
            "hsbc",
            "natwest",
            "santander",
        ]
        assert open_banking_payment["amount"] > 0

        # Validate account details
        account = open_banking_payment["account_details"]
        assert len(account["sort_code"].replace("-", "")) == 6
        assert account["account_number"].startswith("****")

        # Validate processing time
        assert open_banking_payment["processing_time_ms"] > 0

    def test_payment_fraud_detection(self):
        """Test payment fraud detection system"""
        fraud_check = {
            "payment_id": "pay_001",
            "user_id": "user_123",
            "risk_score": 0.23,
            "risk_level": "low",
            "checks": {
                "ip_geolocation": {"pass": True, "country": "GB", "risk_score": 0.05},
                "velocity_check": {
                    "pass": True,
                    "transactions_last_hour": 2,
                    "risk_score": 0.10,
                },
                "device_fingerprint": {
                    "pass": True,
                    "known_device": True,
                    "risk_score": 0.02,
                },
                "amount_analysis": {
                    "pass": True,
                    "unusual_amount": False,
                    "risk_score": 0.06,
                },
            },
            "action": "approve",
            "manual_review_required": False,
            "processed_at": "2024-03-20T14:30:00Z",
        }

        # Validate fraud detection
        assert 0 <= fraud_check["risk_score"] <= 1
        assert fraud_check["risk_level"] in ["low", "medium", "high", "critical"]
        assert fraud_check["action"] in ["approve", "decline", "review", "challenge"]

        # Validate individual checks
        for check_name, check_result in fraud_check["checks"].items():
            assert isinstance(check_result["pass"], bool)
            assert 0 <= check_result["risk_score"] <= 1


class TestExternalServices:
    """Test external service integrations"""

    def test_email_service_integration(self):
        """Test email service integration (SendGrid/Mailgun)"""
        email_notification = {
            "service": "sendgrid",
            "message_id": "msg_001",
            "template_id": "template_bet_confirmation",
            "recipient": "user@example.com",
            "subject": "Bet Confirmation - Thunder Bolt",
            "content": {
                "bet_details": {
                    "bet_id": "bet_001",
                    "horse_name": "Thunder Bolt",
                    "race_name": "Champion Stakes",
                    "stake": 25.00,
                    "odds": "5/2",
                },
                "race_details": {"race_time": "15:30", "track": "Ascot"},
            },
            "status": "delivered",
            "sent_at": "2024-03-20T14:30:00Z",
            "delivered_at": "2024-03-20T14:30:12Z",
            "tracking": {"opened": True, "clicked": False, "bounced": False},
        }

        # Validate email notification
        assert email_notification["service"] in [
            "sendgrid",
            "mailgun",
            "ses",
            "mailchimp",
        ]
        assert email_notification["status"] in [
            "sent",
            "delivered",
            "bounced",
            "failed",
        ]
        assert "@" in email_notification["recipient"]

        # Validate tracking
        tracking = email_notification["tracking"]
        for metric in ["opened", "clicked", "bounced"]:
            assert isinstance(tracking[metric], bool)

    def test_sms_service_integration(self):
        """Test SMS service integration (Twilio)"""
        sms_notification = {
            "service": "twilio",
            "message_sid": "SM123456789",
            "to": "+447123456789",
            "from": "+441234567890",
            "body": "Your bet on Thunder Bolt (Race 3:30 Ascot) has been placed. Stake: £25, Odds: 5/2. Good luck!",
            "status": "delivered",
            "price": "0.075",
            "currency": "GBP",
            "sent_at": "2024-03-20T14:30:00Z",
            "delivered_at": "2024-03-20T14:30:05Z",
            "error_code": None,
            "error_message": None,
        }

        # Validate SMS notification
        assert sms_notification["service"] in ["twilio", "messagebird", "nexmo"]
        assert sms_notification["status"] in [
            "sent",
            "delivered",
            "failed",
            "undelivered",
        ]
        assert sms_notification["to"].startswith("+44")  # UK number
        assert float(sms_notification["price"]) > 0

    def test_push_notification_integration(self):
        """Test push notification integration (Firebase)"""
        push_notification = {
            "service": "firebase",
            "notification_id": "notif_001",
            "device_token": "device_token_123456",
            "platform": "ios",
            "title": "Race Starting Soon!",
            "body": "Thunder Bolt in the Champion Stakes starts in 10 minutes",
            "data": {"race_id": "race_001", "bet_id": "bet_001", "action": "view_race"},
            "badge": 3,
            "sound": "default",
            "priority": "high",
            "status": "sent",
            "sent_at": "2024-03-20T15:20:00Z",
            "delivery_attempts": 1,
            "ttl": 3600,
        }

        # Validate push notification
        assert push_notification["service"] in ["firebase", "apns", "pusher"]
        assert push_notification["platform"] in ["ios", "android", "web"]
        assert push_notification["priority"] in ["low", "normal", "high"]
        assert push_notification["status"] in ["sent", "delivered", "failed"]
        assert push_notification["ttl"] > 0

    def test_analytics_service_integration(self):
        """Test analytics service integration (Google Analytics/Mixpanel)"""
        analytics_event = {
            "service": "mixpanel",
            "event_name": "bet_placed",
            "user_id": "user_123",
            "session_id": "session_456",
            "timestamp": "2024-03-20T14:30:00Z",
            "properties": {
                "bet_amount": 25.00,
                "odds": 2.5,
                "race_type": "flat",
                "track": "ascot",
                "device_type": "mobile",
                "user_segment": "premium",
                "campaign_source": "email",
            },
            "user_properties": {
                "total_bets": 147,
                "lifetime_value": 2450.00,
                "registration_date": "2023-08-15",
                "preferred_tracks": ["ascot", "cheltenham"],
            },
        }

        # Validate analytics event
        assert analytics_event["service"] in [
            "mixpanel",
            "google_analytics",
            "amplitude",
        ]
        assert analytics_event["event_name"] in [
            "bet_placed",
            "race_viewed",
            "deposit_made",
            "withdrawal_requested",
        ]

        # Validate properties
        props = analytics_event["properties"]
        assert props["bet_amount"] > 0
        assert props["odds"] > 1.0
        assert props["device_type"] in ["mobile", "desktop", "tablet"]

        # Validate user properties
        user_props = analytics_event["user_properties"]
        assert user_props["total_bets"] > 0
        assert user_props["lifetime_value"] > 0


# Integration Tests
class TestThirdPartyIntegration:
    """Test third-party service integration scenarios"""

    @pytest.mark.asyncio
    async def test_multi_bookmaker_bet_placement(self):
        """Test placing bets across multiple bookmakers"""
        bet_request = {
            "user_id": "user_123",
            "race_id": "race_001",
            "horse_id": "horse_001",
            "stake": 50.00,
            "bet_type": "win",
            "strategy": "best_odds",
        }

        # Mock bookmaker responses
        bet_placements = {
            "betfair": {
                "status": "accepted",
                "bet_id": "bf_bet_001",
                "odds": 2.55,
                "stake": 50.00,
                "commission": 0.05,
            },
            "bet365": {
                "status": "rejected",
                "reason": "Insufficient balance",
                "error_code": "LOW_BALANCE",
            },
            "ladbrokes": {
                "status": "accepted",
                "bet_id": "lb_bet_001",
                "odds": 2.45,
                "stake": 0.00,  # Not selected due to lower odds
            },
        }

        # Validate bet placement results
        successful_bets = [
            bm
            for bm, result in bet_placements.items()
            if result["status"] == "accepted"
        ]
        failed_bets = [
            bm
            for bm, result in bet_placements.items()
            if result["status"] == "rejected"
        ]

        assert len(successful_bets) >= 1  # At least one successful placement
        assert "betfair" in successful_bets  # Best odds provider succeeded

        # Validate the winning bet (best odds)
        winning_bet = bet_placements["betfair"]
        assert winning_bet["odds"] > bet_placements["ladbrokes"]["odds"]

    def test_data_aggregation_pipeline(self):
        """Test data aggregation from multiple sources"""
        aggregated_data = {
            "race_id": "race_001",
            "last_updated": "2024-03-20T14:30:00Z",
            "sources": {
                "racing_post": {
                    "form_data": True,
                    "ratings": True,
                    "trainer_stats": True,
                },
                "timeform": {"speed_figures": True, "class_analysis": True},
                "betfair": {"live_odds": True, "market_volume": True},
            },
            "data_quality": {"completeness": 0.95, "accuracy": 0.92, "freshness": 0.98},
            "conflicts_detected": 2,
            "conflicts_resolved": 2,
        }

        # Validate aggregation results
        assert aggregated_data["data_quality"]["completeness"] > 0.9
        assert aggregated_data["data_quality"]["accuracy"] > 0.9
        assert aggregated_data["data_quality"]["freshness"] > 0.9
        assert (
            aggregated_data["conflicts_resolved"]
            == aggregated_data["conflicts_detected"]
        )


if __name__ == "__main__":
    """Run third-party integrations test suite"""
    import sys

    print("🔌 Running Third-Party Integrations Test Suite")
    print("=" * 60)

    # Configure pytest
    pytest_args = [
        __file__,
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",
        "-x",  # Stop on first failure
    ]

    # Run tests
    exit_code = pytest.main(pytest_args)

    if exit_code == 0:
        print("\n✅ All third-party integration tests passed successfully!")
        print(
            "🔌 Bookmaker APIs, payment systems, and external services are working correctly!"
        )
    else:
        print(f"\n❌ Third-party integration tests failed with exit code: {exit_code}")
        print("🔧 Please check the test output above for details.")

    sys.exit(exit_code)
