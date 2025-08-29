#!/usr/bin/env python3
"""
Test script for alternative email providers
Tests Outlook, Yahoo, and other common SMTP providers
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def test_outlook_smtp():
    """Test Outlook/Hotmail SMTP configuration"""

    print("🌐 Testing Outlook/Hotmail SMTP Configuration")
    print("===========================================")

    # You would need to replace these with actual Outlook credentials
    smtp_server = "smtp-mail.outlook.com"
    smtp_port = 587
    username = "your-outlook-email@outlook.com"  # Replace with actual
    password = "your-outlook-password"  # Replace with actual

    print(f"Server: {smtp_server}:{smtp_port}")
    print(f"Username: {username}")
    print("Note: You need to provide actual Outlook credentials")

    return False  # Placeholder - would need real credentials


def create_gmail_fix_instructions():
    """Create instructions for fixing Gmail app password"""

    instructions = """
🔧 IMMEDIATE FIX FOR NODE-RED EMAIL

Problem: Gmail app password 'awmf ulio rtjv qybx' is rejected

STEP 1: Generate New Gmail App Password
=====================================
1. Go to: https://myaccount.google.com/security
2. Sign in with: razoremail31@gmail.com
3. Find "2-Step Verification" section
4. Click "App passwords"
5. Select "Mail" → Generate
6. Copy the NEW 16-character password

STEP 2: Update Node-RED Email Nodes
==================================
Option A - Import Updated Flows:
1. I'll create corrected flows for you
2. Import the new JSON file
3. Deploy

Option B - Manual Update:
1. Open Node-RED (http://localhost:1880)
2. Find email nodes (Gmail SMTP, Gmail SMTP Notifications)
3. Double-click each email node
4. Replace password field with NEW app password
5. Deploy flows

STEP 3: Test Email
=================
1. Use Node-RED "Send Test Email" button
2. Or run: python3 test_email_config.py

ALTERNATIVE: Use Different Email Provider
========================================
If Gmail continues to have issues:

Outlook/Hotmail Settings:
- Server: smtp-mail.outlook.com
- Port: 587
- Security: STARTTLS
- Username: your-email@outlook.com
- Password: your-password

Yahoo Settings:
- Server: smtp.mail.yahoo.com
- Port: 587
- Security: STARTTLS
- Username: your-email@yahoo.com
- Password: app-password (Yahoo also requires app passwords)
"""

    print(instructions)


if __name__ == "__main__":
    create_gmail_fix_instructions()

    print("\n" + "=" * 60)
    print("🎯 IMMEDIATE ACTION REQUIRED:")
    print("1. Generate NEW Gmail app password")
    print("2. Update Node-RED email nodes with new password")
    print("3. Test email functionality")
    print("=" * 60)
