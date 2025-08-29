#!/usr/bin/env python3
"""
Email and SMS Alert System
==========================

Comprehensive alert system for sending notifications about strategy performance,
opportunities, and system status via email and SMS.

Features:
- Email alerts with HTML templates
- SMS alerts via Twilio
- Alert prioritization and throttling
- Template-based messaging
- Alert history and tracking
- Integration with monitoring system

Author: Horse Racing AI System V2.03
Date: August 2025
"""

import logging
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
from jinja2 import Template
import requests

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    """Alert message structure"""

    alert_id: str
    alert_type: str  # "opportunity", "performance", "risk", "system"
    severity: str  # "info", "warning", "error", "critical"
    title: str
    message: str
    data: Dict[str, Any]
    recipients: List[str]
    channels: List[str]  # "email", "sms", "dashboard"
    created_at: datetime
    sent_at: Optional[datetime] = None
    status: str = "pending"  # "pending", "sent", "failed", "throttled"


@dataclass
class AlertTemplate:
    """Alert template for different message types"""

    template_id: str
    alert_type: str
    severity: str
    subject_template: str
    email_template: str
    sms_template: str


class EmailService:
    """Email service for sending alerts"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        self.use_tls = config.get("use_tls", True)
        self.from_email = config.get("from_email", self.username)

        logger.info("Email service initialized")

    def send_email(
        self, to_emails: List[str], subject: str, html_body: str, text_body: str = None
    ) -> bool:
        """Send email alert"""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = ", ".join(to_emails)

            # Add text version
            if text_body:
                text_part = MIMEText(text_body, "plain")
                msg.attach(text_part)

            # Add HTML version
            html_part = MIMEText(html_body, "html")
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {len(to_emails)} recipients")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False


class SMSService:
    """SMS service using Twilio"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.account_sid = config.get("account_sid", "")
        self.auth_token = config.get("auth_token", "")
        self.from_number = config.get("from_number", "")
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"

        logger.info("SMS service initialized")

    def send_sms(self, to_numbers: List[str], message: str) -> bool:
        """Send SMS alert"""
        try:
            auth = (self.account_sid, self.auth_token)

            success_count = 0
            for number in to_numbers:
                # Format number if needed
                if not number.startswith("+"):
                    number = f"+44{number.lstrip('0')}"  # UK format

                data = {"From": self.from_number, "To": number, "Body": message}

                response = requests.post(
                    f"{self.base_url}/Messages.json", auth=auth, data=data
                )

                if response.status_code == 201:
                    success_count += 1
                else:
                    logger.error(f"SMS failed for {number}: {response.text}")

            logger.info(
                f"SMS sent successfully to {success_count}/{len(to_numbers)} recipients"
            )
            return success_count > 0

        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False


class AlertTemplateManager:
    """Manages alert templates"""

    def __init__(self):
        self.templates = {}
        self._load_default_templates()
        logger.info("Alert template manager initialized")

    def _load_default_templates(self):
        """Load default alert templates"""

        # Opportunity alert template
        self.templates["opportunity"] = AlertTemplate(
            template_id="opportunity",
            alert_type="opportunity",
            severity="info",
            subject_template="🎯 New {{ strategy_type }} Opportunity - {{ horse_name }}",
            email_template="""
<h2>🎯 New {{ strategy_type }} Strategy Opportunity</h2>
<div style="background: #f0f9ff; padding: 15px; border-left: 4px solid #0ea5e9; margin: 10px 0;">
    <h3>{{ horse_name }} @ {{ course }}</h3>
    <p><strong>Race Time:</strong> {{ race_time }}</p>
    <p><strong>Expected ROI:</strong> {{ expected_roi }}%</p>
    <p><strong>Confidence:</strong> {{ confidence }}%</p>
    <p><strong>Recommended Stake:</strong> £{{ stake }}</p>
    <p><strong>Odds:</strong> {{ odds }}</p>
</div>
<p><strong>Market Conditions:</strong></p>
<ul>
    <li>Field Size: {{ field_size }}</li>
    <li>Going: {{ going }}</li>
    <li>Race Class: {{ race_class }}</li>
</ul>
<p><em>Alert generated at {{ timestamp }}</em></p>
            """,
            sms_template="🎯 {{ strategy_type }}: {{ horse_name }} @ {{ course }} - ROI: {{ expected_roi }}%, Stake: £{{ stake }}, Odds: {{ odds }}",
        )

        # Performance alert template
        self.templates["performance"] = AlertTemplate(
            template_id="performance",
            alert_type="performance",
            severity="info",
            subject_template="📈 {{ strategy_type }} Performance Update - {{ roi }}% ROI",
            email_template="""
<h2>📈 Strategy Performance Update</h2>
<div style="background: #f0fdf4; padding: 15px; border-left: 4px solid #22c55e; margin: 10px 0;">
    <h3>{{ strategy_type }} Strategy</h3>
    <div style="display: flex; gap: 20px;">
        <div>
            <p><strong>ROI:</strong> {{ roi }}%</p>
            <p><strong>Strike Rate:</strong> {{ strike_rate }}%</p>
            <p><strong>Total Bets:</strong> {{ total_bets }}</p>
        </div>
        <div>
            <p><strong>Net P&L:</strong> £{{ net_profit }}</p>
            <p><strong>Total Stake:</strong> £{{ total_stake }}</p>
            <p><strong>Win Streak:</strong> {{ win_streak }}</p>
        </div>
    </div>
</div>
<p><strong>Period:</strong> {{ period }}</p>
<p><em>Alert generated at {{ timestamp }}</em></p>
            """,
            sms_template="📈 {{ strategy_type }}: {{ roi }}% ROI, {{ strike_rate }}% SR, £{{ net_profit }} P&L",
        )

        # Risk alert template
        self.templates["risk"] = AlertTemplate(
            template_id="risk",
            alert_type="risk",
            severity="warning",
            subject_template="⚠️ Risk Alert - {{ alert_title }}",
            email_template="""
<h2>⚠️ Risk Management Alert</h2>
<div style="background: #fef3c7; padding: 15px; border-left: 4px solid #f59e0b; margin: 10px 0;">
    <h3>{{ alert_title }}</h3>
    <p>{{ alert_message }}</p>
    <div style="margin: 15px 0;">
        <p><strong>Current Status:</strong></p>
        <ul>
            <li>Daily Stake Used: £{{ daily_stake_used }} / £{{ daily_limit }}</li>
            <li>Current Drawdown: {{ drawdown }}%</li>
            <li>Risk Level: {{ risk_level }}</li>
        </ul>
    </div>
</div>
<p><strong>Recommended Action:</strong> {{ recommended_action }}</p>
<p><em>Alert generated at {{ timestamp }}</em></p>
            """,
            sms_template="⚠️ Risk Alert: {{ alert_title }} - {{ alert_message }}",
        )

        # System alert template
        self.templates["system"] = AlertTemplate(
            template_id="system",
            alert_type="system",
            severity="error",
            subject_template="🚨 System Alert - {{ system_name }}",
            email_template="""
<h2>🚨 System Status Alert</h2>
<div style="background: #fef2f2; padding: 15px; border-left: 4px solid #ef4444; margin: 10px 0;">
    <h3>{{ system_name }}</h3>
    <p><strong>Status:</strong> {{ status }}</p>
    <p><strong>Message:</strong> {{ message }}</p>
    <div style="margin: 15px 0;">
        <p><strong>System Health:</strong></p>
        <ul>
            <li>Monitoring: {{ monitoring_status }}</li>
            <li>Database: {{ database_status }}</li>
            <li>API Connections: {{ api_status }}</li>
        </ul>
    </div>
</div>
<p><strong>Next Steps:</strong> {{ next_steps }}</p>
<p><em>Alert generated at {{ timestamp }}</em></p>
            """,
            sms_template="🚨 System: {{ system_name }} - {{ status }} - {{ message }}",
        )

    def get_template(self, alert_type: str) -> Optional[AlertTemplate]:
        """Get template for alert type"""
        return self.templates.get(alert_type)

    def render_email(self, template: AlertTemplate, data: Dict[str, Any]) -> str:
        """Render email template with data"""
        try:
            template_obj = Template(template.email_template)
            return template_obj.render(**data)
        except Exception as e:
            logger.error(f"Error rendering email template: {e}")
            return f"Alert: {data.get('message', 'No message')}"

    def render_sms(self, template: AlertTemplate, data: Dict[str, Any]) -> str:
        """Render SMS template with data"""
        try:
            template_obj = Template(template.sms_template)
            rendered = template_obj.render(**data)
            # Truncate if too long for SMS
            return rendered[:160] if len(rendered) > 160 else rendered
        except Exception as e:
            logger.error(f"Error rendering SMS template: {e}")
            return f"Alert: {data.get('message', 'No message')}"[:160]

    def render_subject(self, template: AlertTemplate, data: Dict[str, Any]) -> str:
        """Render subject template with data"""
        try:
            template_obj = Template(template.subject_template)
            return template_obj.render(**data)
        except Exception as e:
            logger.error(f"Error rendering subject template: {e}")
            return "Horse Racing AI Alert"


class AlertDatabase:
    """Database for storing alert history"""

    def __init__(self, db_path: str = "data/alert_history.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
        logger.info(f"Alert database initialized: {db_path}")

    def _init_database(self):
        """Initialize alert database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id TEXT PRIMARY KEY,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    data TEXT,
                    recipients TEXT,
                    channels TEXT,
                    created_at TEXT NOT NULL,
                    sent_at TEXT,
                    status TEXT NOT NULL
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS alert_recipients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    alert_types TEXT,
                    enabled INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()

    def save_alert(self, alert: Alert):
        """Save alert to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO alerts 
                (alert_id, alert_type, severity, title, message, data, 
                 recipients, channels, created_at, sent_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    alert.alert_id,
                    alert.alert_type,
                    alert.severity,
                    alert.title,
                    alert.message,
                    json.dumps(alert.data),
                    json.dumps(alert.recipients),
                    json.dumps(alert.channels),
                    alert.created_at.isoformat(),
                    alert.sent_at.isoformat() if alert.sent_at else None,
                    alert.status,
                ),
            )

            conn.commit()

    def get_recent_alerts(self, hours: int = 24, limit: int = 50) -> List[Alert]:
        """Get recent alerts"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            since_time = (datetime.now() - timedelta(hours=hours)).isoformat()

            cursor.execute(
                """
                SELECT * FROM alerts 
                WHERE created_at >= ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """,
                (since_time, limit),
            )

            alerts = []
            for row in cursor.fetchall():
                alert = Alert(
                    alert_id=row[0],
                    alert_type=row[1],
                    severity=row[2],
                    title=row[3],
                    message=row[4],
                    data=json.loads(row[5]) if row[5] else {},
                    recipients=json.loads(row[6]) if row[6] else [],
                    channels=json.loads(row[7]) if row[7] else [],
                    created_at=datetime.fromisoformat(row[8]),
                    sent_at=datetime.fromisoformat(row[9]) if row[9] else None,
                    status=row[10],
                )
                alerts.append(alert)

            return alerts

    def add_recipient(
        self,
        name: str,
        email: str = None,
        phone: str = None,
        alert_types: List[str] = None,
    ):
        """Add alert recipient"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO alert_recipients (name, email, phone, alert_types)
                VALUES (?, ?, ?, ?)
            """,
                (name, email, phone, json.dumps(alert_types or ["all"])),
            )

            conn.commit()

    def get_recipients(self, alert_type: str = None) -> List[Dict[str, Any]]:
        """Get recipients for alert type"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM alert_recipients WHERE enabled = 1")

            recipients = []
            for row in cursor.fetchall():
                alert_types = json.loads(row[4]) if row[4] else []

                # Check if recipient should receive this alert type
                if (
                    alert_type
                    and "all" not in alert_types
                    and alert_type not in alert_types
                ):
                    continue

                recipient = {
                    "name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "alert_types": alert_types,
                }
                recipients.append(recipient)

            return recipients


class AlertManager:
    """Main alert management system"""

    def __init__(self, config_path: str = "config/alert_config.json"):
        self.config = self._load_config(config_path)

        # Initialize services
        self.email_service = EmailService(self.config.get("email", {}))
        self.sms_service = SMSService(self.config.get("sms", {}))
        self.template_manager = AlertTemplateManager()
        self.database = AlertDatabase()

        # Alert throttling
        self.throttle_cache = {}
        self.throttle_minutes = self.config.get("throttle_minutes", 30)

        logger.info("Alert manager initialized")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load alert configuration"""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "use_tls": True,
                },
                "sms": {"account_sid": "", "auth_token": "", "from_number": ""},
                "throttle_minutes": 30,
                "severity_levels": {
                    "info": ["email"],
                    "warning": ["email", "sms"],
                    "error": ["email", "sms"],
                    "critical": ["email", "sms"],
                },
            }

    def send_alert(
        self,
        alert_type: str,
        severity: str,
        title: str,
        data: Dict[str, Any],
        channels: List[str] = None,
    ) -> bool:
        """Send an alert"""
        try:
            # Create alert ID
            alert_id = f"{alert_type}_{int(datetime.now().timestamp())}"

            # Check throttling
            if self._is_throttled(alert_type, severity):
                logger.info(f"Alert throttled: {alert_type} {severity}")
                return False

            # Get recipients
            recipients = self.database.get_recipients(alert_type)
            if not recipients:
                logger.warning(f"No recipients found for alert type: {alert_type}")
                return False

            # Determine channels based on severity
            if not channels:
                channels = self.config.get("severity_levels", {}).get(
                    severity, ["email"]
                )

            # Add timestamp to data
            data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create alert object
            alert = Alert(
                alert_id=alert_id,
                alert_type=alert_type,
                severity=severity,
                title=title,
                message=data.get("message", ""),
                data=data,
                recipients=[r["email"] for r in recipients if r["email"]],
                channels=channels,
                created_at=datetime.now(),
            )

            # Save to database
            self.database.save_alert(alert)

            # Send alert
            success = self._send_alert_channels(alert, recipients)

            # Update alert status
            alert.status = "sent" if success else "failed"
            alert.sent_at = datetime.now() if success else None
            self.database.save_alert(alert)

            # Update throttle cache
            self._update_throttle_cache(alert_type, severity)

            return success

        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            return False

    def _send_alert_channels(
        self, alert: Alert, recipients: List[Dict[str, Any]]
    ) -> bool:
        """Send alert through specified channels"""
        success = True

        # Get template
        template = self.template_manager.get_template(alert.alert_type)
        if not template:
            logger.error(f"No template found for alert type: {alert.alert_type}")
            return False

        # Send email
        if "email" in alert.channels:
            email_recipients = [r["email"] for r in recipients if r["email"]]
            if email_recipients:
                subject = self.template_manager.render_subject(template, alert.data)
                html_body = self.template_manager.render_email(template, alert.data)

                if not self.email_service.send_email(
                    email_recipients, subject, html_body
                ):
                    success = False

        # Send SMS
        if "sms" in alert.channels:
            sms_recipients = [r["phone"] for r in recipients if r["phone"]]
            if sms_recipients:
                sms_message = self.template_manager.render_sms(template, alert.data)

                if not self.sms_service.send_sms(sms_recipients, sms_message):
                    success = False

        return success

    def _is_throttled(self, alert_type: str, severity: str) -> bool:
        """Check if alert type is throttled"""
        key = f"{alert_type}_{severity}"

        if key in self.throttle_cache:
            last_sent = self.throttle_cache[key]
            if datetime.now() - last_sent < timedelta(minutes=self.throttle_minutes):
                return True

        return False

    def _update_throttle_cache(self, alert_type: str, severity: str):
        """Update throttle cache"""
        key = f"{alert_type}_{severity}"
        self.throttle_cache[key] = datetime.now()

    def send_opportunity_alert(
        self,
        strategy_type: str,
        horse_name: str,
        course: str,
        race_time: str,
        expected_roi: float,
        confidence: float,
        stake: float,
        odds: float,
        **kwargs,
    ):
        """Send opportunity alert"""
        data = {
            "strategy_type": strategy_type,
            "horse_name": horse_name,
            "course": course,
            "race_time": race_time,
            "expected_roi": expected_roi,
            "confidence": confidence,
            "stake": stake,
            "odds": odds,
            **kwargs,
        }

        return self.send_alert(
            alert_type="opportunity",
            severity="info",
            title=f"New {strategy_type} Opportunity - {horse_name}",
            data=data,
        )

    def send_performance_alert(
        self,
        strategy_type: str,
        roi: float,
        strike_rate: float,
        total_bets: int,
        net_profit: float,
        **kwargs,
    ):
        """Send performance alert"""
        data = {
            "strategy_type": strategy_type,
            "roi": roi,
            "strike_rate": strike_rate,
            "total_bets": total_bets,
            "net_profit": net_profit,
            **kwargs,
        }

        severity = "warning" if roi < -10 else "info"

        return self.send_alert(
            alert_type="performance",
            severity=severity,
            title=f"{strategy_type} Performance Update",
            data=data,
        )

    def send_risk_alert(
        self,
        alert_title: str,
        alert_message: str,
        daily_stake_used: float,
        daily_limit: float,
        drawdown: float,
        risk_level: str,
        **kwargs,
    ):
        """Send risk alert"""
        data = {
            "alert_title": alert_title,
            "alert_message": alert_message,
            "daily_stake_used": daily_stake_used,
            "daily_limit": daily_limit,
            "drawdown": drawdown,
            "risk_level": risk_level,
            **kwargs,
        }

        severity = "critical" if risk_level == "HIGH" else "warning"

        return self.send_alert(
            alert_type="risk",
            severity=severity,
            title=f"Risk Alert - {alert_title}",
            data=data,
        )

    def send_system_alert(self, system_name: str, status: str, message: str, **kwargs):
        """Send system alert"""
        data = {
            "system_name": system_name,
            "status": status,
            "message": message,
            **kwargs,
        }

        severity = "critical" if status == "ERROR" else "warning"

        return self.send_alert(
            alert_type="system",
            severity=severity,
            title=f"System Alert - {system_name}",
            data=data,
        )


# Configuration file creation
def create_alert_config():
    """Create alert system configuration"""
    config = {
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "your-email@gmail.com",
            "password": "your-app-password",
            "use_tls": True,
            "from_email": "Horse Racing AI <your-email@gmail.com>",
        },
        "sms": {
            "account_sid": "YOUR_TWILIO_ACCOUNT_SID",
            "auth_token": "YOUR_TWILIO_AUTH_TOKEN",
            "from_number": "+1234567890",
        },
        "throttle_minutes": 30,
        "severity_levels": {
            "info": ["email"],
            "warning": ["email"],
            "error": ["email", "sms"],
            "critical": ["email", "sms"],
        },
        "default_recipients": [
            {
                "name": "Primary Trader",
                "email": "trader@yourdomain.com",
                "phone": "+44123456789",
                "alert_types": ["all"],
            }
        ],
    }

    config_path = "config/alert_config.json"
    os.makedirs("config", exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    logger.info(f"Created alert config: {config_path}")
    return config_path


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)

    # Create config if not exists
    create_alert_config()

    # Initialize alert manager
    alert_manager = AlertManager()

    # Add a demo recipient
    alert_manager.database.add_recipient(
        name="Demo User",
        email="demo@example.com",
        phone="+44123456789",
        alert_types=["opportunity", "performance", "risk"],
    )

    # Send test alerts
    print("Sending test opportunity alert...")
    alert_manager.send_opportunity_alert(
        strategy_type="80/20",
        horse_name="Thunder Strike",
        course="Kempton",
        race_time="14:30",
        expected_roi=12.5,
        confidence=75.0,
        stake=15.0,
        odds=4.5,
        field_size=12,
        going="GOOD",
    )

    print("Sending test performance alert...")
    alert_manager.send_performance_alert(
        strategy_type="Dutching",
        roi=8.3,
        strike_rate=65.0,
        total_bets=25,
        net_profit=45.50,
        period="Last 7 days",
    )

    print("Alert system demo complete!")
