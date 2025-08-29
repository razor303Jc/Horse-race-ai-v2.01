# 🏇 Node-RED Setup Wizard - Horse Racing AI

## 🎯 Quick Configuration Guide

This guide will walk you through configuring your Node-RED automation system step by step.

---

## 🗄️ **Step 1: Database Connection Setup**

### PostgreSQL Configuration

1. **Open Node-RED Editor**: http://localhost:1881
2. **Find any PostgreSQL node** in the flows (purple database icons)
3. **Double-click** to configure
4. **Click the pencil icon** next to the database dropdown
5. **Enter these settings**:

```yaml
Connection Details:
  Host: localhost (or your database host)
  Port: 5432
  Database: horse_racing
  Username: horse_racing
  Password: secure_password_123

Advanced Settings:
  SSL: false (unless required)
  Connection timeout: 10000
  Query timeout: 60000
  Max connections: 10
```

### Quick Test Query

Add this test query to verify connection:

```sql
SELECT current_timestamp as test_time,
       version() as postgres_version,
       current_database() as database_name;
```

---

## 📧 **Step 2: Email Alert Configuration**

### Gmail/Google Workspace Setup

1. **Find email nodes** (envelope icons in Alert flows)
2. **Double-click** to configure
3. **Set up SMTP settings**:

```yaml
SMTP Configuration:
  Server: smtp.gmail.com
  Port: 465 (SSL) or 587 (TLS)
  Secure: SSL/TLS
  Username: your-email@gmail.com
  Password: your-app-password (NOT your regular password)

From Field: your-email@gmail.com
To Field: alerts@yourdomain.com
```

### 🔐 **Important: App Password Setup**

For Gmail, you MUST use an App Password:

1. Go to Google Account Settings
2. Security → 2-Step Verification
3. App passwords → Generate new password
4. Use this 16-character password in Node-RED

### Alternative Email Providers

```yaml
# Outlook/Hotmail
Server: smtp-mail.outlook.com
Port: 587
Secure: true

# Yahoo
Server: smtp.mail.yahoo.com
Port: 465 or 587
Secure: true

# Custom SMTP
Server: mail.yourdomain.com
Port: 25, 465, or 587
```

---

## ⚡ **Step 3: Test Flows Deployment**

### 3.1 Deploy All Flows

1. **Click the red "Deploy" button** (top right)
2. **Select "Full deployment"**
3. **Confirm deployment**

### 3.2 Test Individual Components

#### Test Database Connection

1. Go to **📊 Data Pipeline** tab
2. Find **"Database Test"** flow
3. **Click the inject button** (blue square with timestamp)
4. Check **debug tab** (bug icon) for results

#### Test Email Alerts

1. Go to **🚨 Alerts** tab
2. Find **"Test Email Alert"** flow
3. **Click inject button**
4. Check your email for test message

#### Test File Operations

1. Go to **📊 Data Pipeline** tab
2. Find **"File System Test"** flow
3. **Click inject button**
4. Check debug output for file listing

### 3.3 Monitor System Status

- **Check the debug panel** (right sidebar, bug icon)
- **Look for error messages** in red
- **Verify success messages** in green
- **Check container logs**: `docker logs horse_racing_node_red`

---

## 📈 **Step 4: Dashboard Customization**

### 4.1 Access Dashboard

- **URL**: http://localhost:1881/ui
- **Should show basic layout** with placeholder data

### 4.2 Dashboard Components Setup

#### System Status Panel

```javascript
Components to Configure:
- System Health Gauge (0-100%)
- Last Update Timestamp
- Active Process Indicator
- Error Count Badge
- Pipeline Status Light
```

#### AI Predictions Panel

```javascript
Components to Configure:
- Win Rate Chart (line graph)
- Best Bets Table (top 5)
- Confidence Distribution
- ROI Tracking
- Prediction Accuracy
```

#### Data Quality Panel

```javascript
Components to Configure:
- Files Processed Counter
- Validation Results
- CSV Status Indicators
- Import Progress Bar
```

### 4.3 Custom Dashboard Elements

#### Add Real Data Sources

1. **Navigate to 📈 Dashboard tab**
2. **Find dashboard nodes** (colored rectangles)
3. **Configure data sources**:
   - Point to your database tables
   - Set refresh intervals
   - Configure chart types

#### Sample Dashboard Query

```sql
-- Latest prediction accuracy
SELECT
    date_trunc('day', created_at) as date,
    AVG(CASE WHEN actual_result = predicted_result THEN 1.0 ELSE 0.0 END) * 100 as accuracy
FROM predictions
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY date_trunc('day', created_at)
ORDER BY date;
```

---

## ⏰ **Step 5: Schedule Automation Setup**

### 5.1 Configure Cron Schedules

#### Daily Data Collection

1. **Go to 📊 Data Pipeline tab**
2. **Find "Daily Schedule" node** (clock icon)
3. **Double-click to configure**
4. **Set schedule**:

```yaml
Schedule Configuration:
  Name: Daily Data Collection
  Schedule: 0 6,22 * * * (6 AM and 10 PM daily)
  Timezone: UTC (or your local timezone)

Alternative Schedules:
  Every 4 hours: 0 */4 * * *
  Business hours only: 0 9-17 * * 1-5
  Weekend only: 0 10,15 * * 6,7
```

#### Weekly Reporting

```yaml
Schedule: 0 18 * * 0  (6 PM every Sunday)
Purpose: Generate weekly performance reports
```

### 5.2 Configure Schedule Actions

#### Data Download Sequence

```yaml
1. Download race cards → Clean CSV → Validate data
2. Import to database → Generate predictions
3. Update dashboards → Send success notification
4. On failure: Log error → Send alert email
```

#### Custom Schedule Examples

```javascript
// Every 30 minutes during racing hours
0 */30 9-18 * * *

// Twice daily at specific times
0 6,22 * * *

// Weekly maintenance (Sunday 2 AM)
0 2 * * 0

// Monthly reporting (1st of month, 9 AM)
0 9 1 * *
```

---

## 🔧 **Step 6: Advanced Configuration**

### 6.1 Environment Variables

Set these in your Node-RED container:

```bash
docker exec horse_racing_node_red sh -c 'echo "
DATABASE_URL=postgresql://horse_racing:secure_password_123@localhost:5432/horse_racing
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
WORKSPACE_PATH=/workspace
" > /data/.env'
```

### 6.2 Security Settings

```yaml
Authentication:
  Enable: true
  Username: admin
  Password: [set-strong-password]

Session:
  Timeout: 3600 (1 hour)
  Secret: [generate-random-secret]

HTTPS:
  Enable: false (true for production)
  Certificate: /path/to/cert.pem
  Key: /path/to/key.pem
```

### 6.3 Performance Optimization

```yaml
Memory Management:
  Node.js heap: 512MB
  Flow execution timeout: 120s
  Maximum payload size: 10MB

Database Connections:
  Pool size: 10
  Connection timeout: 10s
  Idle timeout: 30s
```

---

## 🚨 **Troubleshooting Common Issues**

### Database Connection Fails

```bash
# Test database connectivity
docker exec horse_racing_node_red ping postgres

# Check database status
docker exec -it [postgres-container] psql -U horse_racing -d horse_racing -c "SELECT 1;"

# Verify network connectivity
docker network inspect horse_racing_network
```

### Email Not Sending

```yaml
Common Issues:
1. Wrong app password (not account password)
2. 2FA not enabled on Google account
3. Incorrect SMTP settings
4. Firewall blocking outbound ports
5. Email provider blocking "less secure apps"

Solutions:
1. Generate new app password
2. Enable 2FA first, then create app password
3. Verify SMTP settings with email provider
4. Check ports 587, 465, 25
5. Use OAuth2 instead of basic auth
```

### Flows Not Running

```yaml
Check These:
1. Deploy button clicked (should be grayed out)
2. No errors in debug panel
3. Inject nodes properly configured
4. Cron schedules in correct format
5. Node dependencies installed

Debug Steps:
1. Check debug panel for errors
2. Use inject nodes to test manually
3. Verify container logs
4. Test individual nodes in isolation
```

### Dashboard Not Loading

```yaml
Possible Causes:
1. Dashboard nodes not deployed
2. UI path incorrect (should be /ui)
3. Browser cache issues
4. Port conflicts

Solutions:
1. Redeploy flows completely
2. Clear browser cache
3. Try incognito/private mode
4. Check container ports mapping
```

---

## 📋 **Final Checklist**

### ✅ Configuration Complete When:

- [ ] Database connection successful (green status)
- [ ] Test email received successfully
- [ ] All flows deployed without errors
- [ ] Dashboard accessible at http://localhost:1881/ui
- [ ] Scheduled flows show "next run" times
- [ ] Debug panel clear of errors
- [ ] Container status shows "healthy"
- [ ] Test data appears in dashboard
- [ ] Alert system responds to test triggers
- [ ] File operations work correctly

### 🎯 **Ready for Production When:**

- [ ] Real database data flowing through
- [ ] Email alerts configured for operations team
- [ ] Dashboard shows live racing data
- [ ] Scheduled automation running smoothly
- [ ] Performance monitoring in place
- [ ] Backup and recovery tested
- [ ] Documentation complete
- [ ] Team trained on system

---

## 🆘 **Getting Help**

### Quick Commands

```bash
# Check container status
docker ps -f name=horse_racing_node_red

# View container logs
docker logs horse_racing_node_red --tail 50

# Restart container
docker restart horse_racing_node_red

# Check installed nodes
docker exec horse_racing_node_red npm list --depth=0
```

### Configuration Files

- **Flows**: `/data/flows.json` (inside container)
- **Settings**: `/data/settings.js` (inside container)
- **Logs**: `/data/node-red.log` (inside container)

---

_Follow this guide step by step and you'll have a fully operational Node-RED automation system for your horse racing AI project! 🏇_
