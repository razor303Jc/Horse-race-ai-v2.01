# 🚨 URGENT: Node-RED Email Fix Required

## Issue Identified

Your Gmail app password `awmf ulio rtjv qybx` is being **rejected by Gmail**.

## Error Details

```
535-5.7.8 Username and Password not accepted
https://support.google.com/mail/?p=BadCredentials
```

## Immediate Solution Required

### Step 1: Generate New Gmail App Password

1. **Visit Gmail Security Settings**

   ```
   https://myaccount.google.com/security
   ```

2. **Sign in with**: `razoremail31@gmail.com`

3. **Navigate to App Passwords**

   - Find "2-Step Verification" section
   - Click "App passwords"
   - Select "Mail" from dropdown
   - Click "Generate"

4. **Copy the New Password**
   - Will be 16 characters in format: `xxxx xxxx xxxx xxxx`
   - **Write this down - you'll need it!**

### Step 2: Update Node-RED

#### Option A: Manual Update (Quick)

1. Open Node-RED: http://localhost:1880
2. Go to the "Email Notifications" tab
3. Double-click the "Gmail SMTP" node
4. Replace the password field with your NEW app password
5. Double-click the "Gmail SMTP Notifications" node
6. Replace the password field with your NEW app password
7. Click "Deploy"

#### Option B: Import Corrected Flows

After you get the new password, tell me what it is and I'll create corrected flows for you.

### Step 3: Test Email

Run the test to verify it works:

```bash
python3 test_email_config.py
```

## Alternative Email Providers

If Gmail continues to have issues, I can help you switch to:

### Outlook/Hotmail

- Server: `smtp-mail.outlook.com`
- Port: `587`
- No app password required (just regular password)

### Yahoo Mail

- Server: `smtp.mail.yahoo.com`
- Port: `587`
- Requires app password (like Gmail)

## Current Status

❌ **Email notifications NOT working**  
✅ All Python scripts working  
✅ Database connections working  
✅ Node-RED flows working (except email)

## What You Need to Do Right Now

1. **Generate new Gmail app password** (5 minutes)
2. **Update Node-RED email nodes** (2 minutes)
3. **Test email functionality** (1 minute)

**OR**

Tell me if you want to switch to a different email provider and I'll create the updated configuration for you.

---

**The good news**: Everything else is working perfectly! This is just an email authentication issue that's easy to fix.
