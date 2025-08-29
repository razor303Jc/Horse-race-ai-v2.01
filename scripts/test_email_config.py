#!/usr/bin/env python3
"""
Gmail SMTP Test Script for Node-RED Email Configuration
Tests the exact same settings used in Node-RED flows
"""

import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def test_gmail_smtp():
    """Test Gmail SMTP configuration used in Node-RED"""

    # Node-RED email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    username = "razoremail31@gmail.com"
    app_password = "awmf ulio rtjv qybx"

    print("🏇 Horse Racing AI - Gmail SMTP Test")
    print("===================================")
    print(f"📧 Testing email configuration...")
    print(f"Server: {smtp_server}:{smtp_port}")
    print(f"Username: {username}")
    print(f"App Password: {'*' * (len(app_password) - 4) + app_password[-4:]}")
    print()

    try:
        # Create SMTP connection
        print("🔗 Connecting to Gmail SMTP server...")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)

        # Enable debug output
        server.set_debuglevel(1)

        print("✅ SSL connection established")

        # Login
        print("🔐 Attempting login...")
        server.login(username, app_password)
        print("✅ Login successful!")

        # Create test message
        test_recipient = "razoremail31@gmail.com"  # Send to self for testing

        msg = MIMEMultipart()
        msg["From"] = username
        msg["To"] = test_recipient
        msg["Subject"] = (
            f"🏇 Horse Racing AI - SMTP Test {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        body = f"""
🏇 Horse Racing AI System - Email Test

✅ SMTP Configuration Test Successful!

Test Details:
- Server: {smtp_server}:{smtp_port}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- From: {username}
- To: {test_recipient}

This confirms that your Node-RED email configuration is working correctly.

🤖 Horse Racing AI Automation System
        """

        msg.attach(MIMEText(body, "plain"))

        # Send email
        print("📤 Sending test email...")
        text = msg.as_string()
        server.sendmail(username, test_recipient, text)
        print("✅ Test email sent successfully!")

        # Close connection
        server.quit()
        print("🔚 Connection closed")

        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print("\n🔧 Possible Solutions:")
        print("1. Check if 2-Factor Authentication is enabled on Gmail")
        print("2. Generate a new App Password:")
        print("   - Go to Google Account settings")
        print("   - Security → 2-Step Verification → App passwords")
        print("   - Generate new password for 'Mail'")
        print("3. Verify the app password is copied correctly")
        return False

    except smtplib.SMTPConnectError as e:
        print(f"❌ Connection Error: {e}")
        print("\n🔧 Possible Solutions:")
        print("1. Check internet connection")
        print("2. Verify firewall settings allow SMTP (port 465)")
        print("3. Try using port 587 with STARTTLS instead")
        return False

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False


def test_alternative_config():
    """Test alternative SMTP configuration (port 587 with STARTTLS)"""

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    username = "razoremail31@gmail.com"
    app_password = "awmf ulio rtjv qybx"

    print("\n🔄 Testing Alternative Configuration (Port 587 + STARTTLS)")
    print("=========================================================")

    try:
        # Create SMTP connection
        print("🔗 Connecting to Gmail SMTP server (port 587)...")
        server = smtplib.SMTP(smtp_server, smtp_port)

        # Start TLS
        print("🔐 Starting TLS...")
        server.starttls()
        print("✅ TLS connection established")

        # Login
        print("🔐 Attempting login...")
        server.login(username, app_password)
        print("✅ Alternative configuration works!")

        server.quit()
        return True

    except Exception as e:
        print(f"❌ Alternative configuration failed: {e}")
        return False


if __name__ == "__main__":
    print("Starting Gmail SMTP configuration test...\n")

    # Test primary configuration (same as Node-RED)
    primary_success = test_gmail_smtp()

    if not primary_success:
        # Test alternative configuration
        alternative_success = test_alternative_config()

        if alternative_success:
            print("\n💡 Recommendation: Update Node-RED to use port 587 with STARTTLS")
            print("   Change email node settings:")
            print("   - Port: 587")
            print("   - Secure: false")
            print("   - TLS: true")

    print(f"\n{'='*50}")
    if primary_success:
        print("🎉 SUCCESS: Your Node-RED email configuration is working!")
        print("The issue may be elsewhere in your Node-RED flow.")
    else:
        print("❌ FAILED: Email configuration needs to be fixed.")
        print("Follow the solutions provided above.")
    print(f"{'='*50}")
