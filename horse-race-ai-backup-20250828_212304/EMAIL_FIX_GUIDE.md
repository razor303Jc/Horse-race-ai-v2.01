# 🚨 Node-RED Email Fix Guide

## Problem Identified

Your Gmail app password `awmf ulio rtjv qybx` is being rejected by Gmail.

## Solution Steps

### 1. Generate New Gmail App Password

1. **Go to Gmail Account Settings**

   - Visit: https://myaccount.google.com/
   - Sign in with `razoremail31@gmail.com`

2. **Navigate to Security**

   - Click "Security" in the left sidebar
   - Scroll to "How you sign in to Google"

3. **Enable 2-Step Verification** (if not already enabled)

   - Click "2-Step Verification"
   - Follow the setup process

4. **Generate App Password**
   - Go back to Security settings
   - Click "2-Step Verification"
   - Scroll down and click "App passwords"
   - Select "Mail" from the dropdown
   - Click "Generate"
   - **Copy the new 16-character password** (format: xxxx xxxx xxxx xxxx)

### 2. Update Node-RED Configuration

After getting the new app password, update your Node-RED flows:

1. **Import the corrected flows** (I'll create this for you)
2. **Or manually edit email nodes**:
   - Double-click each email node
   - Update the "Password" field with the new app password
   - Deploy the flows

### 3. Test Email Functionality

Use the test script to verify:

```bash
python3 test_email_config.py
```

## Alternative: Use Different Email Provider

If Gmail continues to have issues, you can use:

- **Outlook/Hotmail**: smtp-mail.outlook.com:587
- **Yahoo**: smtp.mail.yahoo.com:587
- **Custom SMTP**: Your own email provider

## Quick Fix Commands

1. **Generate new Gmail app password** (manual step)
2. **Run this to update flows** (I'll create updated flows)
3. **Test with**: `python3 test_email_config.py`

---

## Current Status

❌ Gmail app password rejected  
❌ Node-RED email notifications not working  
✅ All other Python integrations working  
✅ Database connections working  
✅ Scripts execution working

## Next Actions Required

1. Get new Gmail app password
2. Update Node-RED email nodes
3. Test email functionality
4. Deploy corrected flows
