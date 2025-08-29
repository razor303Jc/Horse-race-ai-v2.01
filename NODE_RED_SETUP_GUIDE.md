# 🏇 Node-RED Horse Racing AI Automation Setup Guide

## 🚀 IMMEDIATE IMPLEMENTATION STEPS

### **STEP 1: Import the Automation Flows**

1. **Open Node-RED Editor**: http://localhost:1881
2. **Import Flows**:
   - Click the hamburger menu (☰) in top-right
   - Select "Import"
   - Choose "select a file to import"
   - Select: `horse_racing_automation_flows.json`
   - Click "Import"

### **STEP 2: Configure Database Connections**

The flows include pre-configured database connections:

#### **Database Configuration Nodes**:

- ✅ **Cards Database**: `cards_horse_racing_db`
- ✅ **Results Database**: `results_horse_racing_db`
- ✅ **Advanced Metrics**: `advanced_racing_metrics_db`

**Connection Details** (already configured):

```
Host: host.docker.internal
Port: 5432
User: horse_racing
Password: secure_password_123
```

### **STEP 3: Configure Email Notifications**

#### **Gmail SMTP Configuration** (pre-configured):

```
Service: Gmail
Host: smtp.gmail.com
Port: 465
Security: SSL/TLS
Username: your-email@gmail.com
App Password: awmf ulio rtjv qybx
```

**⚠️ IMPORTANT**: Update the email address in the flows:

- Replace `your-email@gmail.com` with your actual email address
- The app password is already configured from your .env file

### **STEP 4: Test Each Workflow**

#### **A. Database Connection Tests**

Navigate to the "💾 Database Operations" tab:

1. Click "Test Cards DB" button
2. Click "Test Results DB" button
3. Check debug output for successful connections

#### **B. Email Notification Test**

Navigate to the "📧 Email Notifications" tab:

1. Update email address in "Prepare Email" function node
2. Click "Send Test Email" button
3. Check your email for test message

#### **C. Scheduled Tasks**

Navigate to the "⏰ Scheduled Tasks" tab:

- Daily data check scheduled for 6:00 AM
- Automatically sends daily reports
- Modify cron schedule as needed

#### **D. System Monitoring**

Navigate to the "📊 System Monitoring" tab:

- Health checks run every 5 minutes
- System status displayed on dashboard
- Real-time monitoring active

### **STEP 5: Access Your Dashboard**

**Dashboard URL**: http://localhost:1881/ui

#### **Dashboard Features**:

- 🏠 **Main Dashboard**: System status and controls
- 💾 **Database Tab**: Database operations interface
- 🤖 **Automation Tab**: Automation controls

### **STEP 6: Customize Your Workflows**

#### **Available Workflow Templates**:

1. **🏇 Race Data Processor**:

   - Processes incoming race data
   - Updates database records
   - Triggers notifications

2. **📧 Smart Email Alerts**:

   - Conditional email notifications
   - Race result alerts
   - System status updates

3. **⏰ Automated Scheduling**:

   - Daily data processing
   - Weekly reports
   - Monthly analytics

4. **📊 Real-time Monitoring**:
   - System health checks
   - Database connection monitoring
   - Performance tracking

## 🎯 **READY-TO-USE AUTOMATION FEATURES**

### **✅ Database Operations**

- Automated race data imports
- Real-time result processing
- Data validation and cleanup
- Performance analytics

### **✅ Email Notifications**

- Race start/finish alerts
- System health notifications
- Daily/weekly reports
- Error and exception alerts

### **✅ Scheduled Tasks**

- Daily data synchronization
- Automated backups
- Report generation
- System maintenance

### **✅ Dashboard Monitoring**

- Live system status
- Database health indicators
- Processing activity lights
- Performance metrics

## 🔧 **CUSTOMIZATION OPTIONS**

### **Modify Email Settings**:

```javascript
// In the "Prepare Email" function node:
msg.to = "your-actual-email@gmail.com";
msg.subject = "🏇 Custom Subject";
msg.payload = "Your custom message content";
```

### **Adjust Scheduling**:

```
// Cron expressions for different schedules:
"0 6 * * *"     // Daily at 6:00 AM
"0 */2 * * *"   // Every 2 hours
"0 0 * * 0"     // Weekly on Sunday
"0 0 1 * *"     // Monthly on 1st
```

### **Database Query Customization**:

```sql
-- Example race data queries:
SELECT * FROM races WHERE race_date = CURRENT_DATE;
SELECT COUNT(*) FROM horses WHERE status = 'active';
SELECT * FROM results WHERE result_date >= NOW() - INTERVAL '24 hours';
```

## 🎪 **ADVANCED FEATURES TO ADD**

### **1. AI Model Integration**:

- Connect to ML training service
- Automated prediction workflows
- Model performance monitoring

### **2. Real-time Data Feeds**:

- Live race data ingestion
- Real-time odds monitoring
- Live result processing

### **3. Advanced Analytics**:

- Performance trend analysis
- Predictive modeling
- Risk assessment

### **4. Multi-channel Notifications**:

- SMS alerts
- Slack integration
- Discord notifications
- Mobile push notifications

## 🚦 **NEXT ACTIONS**

1. **Import flows** → Node-RED Editor
2. **Test database connections** → Verify all 3 databases
3. **Send test email** → Confirm Gmail integration
4. **Customize email address** → Update with your email
5. **Explore dashboard** → http://localhost:1881/ui
6. **Schedule your first automation** → Daily report setup

**Your Horse Racing AI automation platform is ready for production use!** 🏆
