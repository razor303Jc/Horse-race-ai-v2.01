# 🏇 Node-RED Configuration Complete!

## ✅ **SETUP STATUS: READY FOR CONFIGURATION**

Your dedicated Node-RED container for the horse racing AI project is now running with all components pre-configured!

---

## 🌐 **Access Points**

- **🎛️ Node-RED Editor**: http://localhost:1881
- **📊 Dashboard**: http://localhost:1881/ui (after flow deployment)
- **⚙️ Admin**: Available via editor

---

## 🎯 **MANUAL CONFIGURATION REQUIRED**

### 1. 🗄️ **Database Connection Setup**

1. **Open Node-RED Editor**: http://localhost:1881
2. **Navigate to** "📊 Data Pipeline" tab
3. **Double-click any purple PostgreSQL node**
4. **Click pencil icon** next to database dropdown
5. **Enter these exact settings**:

```yaml
Host: localhost
Port: 5432
Database: postgres
Username: horse_racing
Password: secure_password_123
SSL: false
Max connections: 10
Connection timeout: 10000
Query timeout: 60000
```

6. **Click "Add"** then **"Done"**

### 2. 📧 **Email Alert Configuration**

1. **Navigate to** "🚨 Alerts" tab
2. **Double-click any email node** (envelope icon)
3. **Configure SMTP settings**:

```yaml
For Gmail:
Server: smtp.gmail.com
Port: 465
Secure: SSL/TLS
Username: your-email@gmail.com
Password: jegd yxwp vklq tjif (your app password)

Recipients:
To: alerts@yourdomain.com
From: your-email@gmail.com
```

4. **Save configuration**

### 3. ⚡ **Deploy Flows**

1. **Click the red "Deploy" button** (top right)
2. **Select "Full deployment"**
3. **Confirm deployment**

### 4. 🧪 **Test Components**

#### Test Database Connection:

1. Go to "📊 Data Pipeline" tab
2. Click the **"Test Database"** inject button (blue square)
3. Check debug panel for results

#### Test Email Alerts:

1. Go to "🚨 Alerts" tab
2. Click the **"Test Email"** inject button
3. Check your email for test message

### 5. ⏰ **Schedule Configuration**

1. **Navigate to** "📊 Data Pipeline" tab
2. **Double-click the "Daily Data Collection" cron node**
3. **Verify schedule**: `0 6,22 * * *` (6 AM & 10 PM daily)
4. **Adjust timezone** if needed
5. **Enable the schedule**

### 6. 📈 **Dashboard Setup**

1. **Access dashboard**: http://localhost:1881/ui
2. **Customize components** as needed
3. **Add real data sources** by configuring database queries in dashboard nodes

---

## 🔧 **Pre-Configured Features**

### ✅ **Installed & Ready:**

- ✅ Node-RED Dashboard for UI
- ✅ PostgreSQL nodes for database integration
- ✅ Email nodes for alerts
- ✅ Cron scheduling for automation
- ✅ File system operations
- ✅ Date/time handling
- ✅ CSV processing capabilities

### ✅ **Pre-Built Flows:**

- ✅ **Daily Data Collection** - Automated download at 6 AM & 10 PM
- ✅ **CSV Data Cleaning** - Automatic data quality processing
- ✅ **Database Import** - Automated data import pipeline
- ✅ **Error Handling** - Email alerts on failures
- ✅ **Manual Triggers** - On-demand pipeline execution
- ✅ **System Monitoring** - Health checks and status updates
- ✅ **Dashboard Components** - Real-time system status display

### ✅ **Configuration Files Created:**

- ✅ `node-red/database-config.json` - Database connection settings
- ✅ `node-red/schedule-config.json` - Automation schedules
- ✅ `node-red/dashboard-layout.json` - Dashboard configuration

---

## 🚀 **Ready-to-Use Automation Pipeline**

Once configured, your system will automatically:

1. **⏰ 6 AM & 10 PM Daily**: Download race cards
2. **🧹 Auto-Clean**: Process and clean CSV data
3. **💾 Import**: Load data into PostgreSQL database
4. **🤖 Generate**: Create AI predictions
5. **📊 Update**: Refresh dashboard with latest data
6. **📧 Alert**: Send notifications on success/failure
7. **📈 Monitor**: Track system health and performance

---

## 🆘 **Quick Troubleshooting**

### Database Connection Issues:

```bash
# Check if database is needed
docker ps | grep postgres

# Start database if not running
docker-compose -f docker-compose.clean.yml up -d postgres
```

### Email Not Sending:

- Verify Gmail app password (not regular password)
- Enable 2-factor authentication first
- Check SMTP settings match exactly

### Flows Not Loading:

- Click "Deploy" button after making changes
- Check debug panel for errors
- Restart container if needed: `docker restart horse_racing_node_red`

---

## 🎯 **Next Steps**

1. **🌐 Open Editor**: http://localhost:1881
2. **⚙️ Configure database nodes** with the provided settings
3. **📧 Set up email alerts** with your credentials
4. **🚀 Deploy flows** using the Deploy button
5. **🧪 Test components** using the inject buttons
6. **📊 View dashboard**: http://localhost:1881/ui

---

## 📋 **Configuration Checklist**

- [ ] Node-RED editor accessible (http://localhost:1881)
- [ ] Database connection configured in PostgreSQL nodes
- [ ] Email settings configured in email nodes
- [ ] Flows deployed successfully (no errors in debug panel)
- [ ] Database test successful (check debug output)
- [ ] Email test successful (check inbox)
- [ ] Schedule configured and enabled
- [ ] Dashboard accessible (http://localhost:1881/ui)
- [ ] Manual pipeline trigger works
- [ ] System status updates properly

---

**🏇 Your Horse Racing AI automation system is ready to rock! All the hard work is done - just complete the manual configuration steps above and you'll have a fully automated data pipeline running 24/7.**

_Remember: Keep your email app password secure and never commit it to version control!_
