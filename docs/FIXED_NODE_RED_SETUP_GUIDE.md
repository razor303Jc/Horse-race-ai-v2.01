# 🏇 Fixed Node-RED Automation Setup Guide

## ❌ Issue Resolved: Missing Node Types

The original flows had incorrect node type names. Here are the corrected types:

- ✅ **Database Config**: `postgresdb` (not `postgres-config`)
- ✅ **Database Query**: `postgres` (not `PostgreSql`)
- ✅ **Email**: `email` (not `e-mail` or `e-mail-config`)

## 🚀 Import Corrected Flows

### Step 1: Import the Fixed Flow File

1. Open Node-RED editor: http://localhost:1881
2. Click the hamburger menu (☰) → Import
3. **Use this corrected file**: `horse_racing_flows_corrected.json`
4. Click "Import"

### Step 2: Configure Database Credentials

After importing, you need to set up the database credentials:

1. Go to any database query node (Cards, Results, or Metrics)
2. Double-click to edit
3. Click the pencil icon next to the database configuration
4. Enter credentials:
   - **Username**: `horse_racing`
   - **Password**: `secure_password_123`
   - **Host**: `host.docker.internal`
   - **Port**: `5432`
   - **Database**:
     - Cards: `cards_horse_racing_db`
     - Results: `results_horse_racing_db`
     - Metrics: `advanced_racing_metrics_db`

### Step 3: Update Email Address

1. Find the "Format Email" function node
2. Edit the line: `msg.to = 'your-email@example.com';`
3. Replace with your actual email address

### Step 4: Deploy and Test

1. Click the red "Deploy" button
2. Test database connections using the inject nodes
3. Send a test email
4. Check the debug panel for results

## 📋 Available Flows

### Database Operations Tab

- **Test Cards DB**: Test connection to cards database
- **Test Results DB**: Test connection to results database
- **Test Metrics DB**: Test connection to metrics database

### Email Notifications Tab

- **Send Test Email**: Send a test email notification

### Scheduled Tasks Tab

- **Daily AI Processing**: Scheduled for 6 AM daily
- **Evening Reports**: Scheduled for 8 PM daily

### System Monitoring Tab

- **Dashboard**: Simple status display
- **Test Buttons**: Manual testing controls

## 🔧 Troubleshooting

### If Database Connections Fail:

1. Verify PostgreSQL is running: `docker ps`
2. Check database credentials match exactly
3. Ensure `host.docker.internal` resolves from within Node-RED container

### If Email Fails:

1. Verify Gmail credentials are correct
2. Update the recipient email address
3. Check Gmail app password is valid

### If Scheduling Doesn't Work:

1. Check cron expressions are valid
2. Deploy the flows after making changes
3. Monitor debug output for schedule events

## ✅ Ready for Production

Once imported and configured:

- All database connections will be functional
- Email notifications will work with Gmail SMTP
- Scheduling will run automated tasks
- Dashboard provides system monitoring

**The corrected flows are now compatible with your installed Node-RED packages!**
