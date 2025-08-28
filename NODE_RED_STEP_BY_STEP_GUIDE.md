# 🎯 Node-RED Configuration Walkthrough

## 🗄️ **STEP 1: Configure Database Connection**

### Visual Steps:

1. **🌐 Open Node-RED Editor**: http://localhost:1881 (should be open now)

2. **📊 Navigate to Data Pipeline Tab**:

   - Look for tabs at the top
   - Click on "📊 Data Pipeline"

3. **🔍 Find PostgreSQL Node**:

   - Look for a **purple node** labeled "Test Query" or any postgres node
   - It will have a database icon

4. **⚙️ Configure Database**:

   - **Double-click** the purple PostgreSQL node
   - You'll see a configuration dialog
   - **Look for "Database" dropdown** - it might say "Add new postgres-config..."

5. **🛠️ Add Database Configuration**:

   - **Click the pencil icon** ✏️ next to the database dropdown
   - A new window opens titled "Add new postgres-config node"

6. **📝 Enter These EXACT Settings**:

   ```
   Name: Horse Racing DB
   Host: localhost
   Port: 5432
   Database: postgres
   SSL: false (unchecked)
   Username: horse_racing
   Password: secure_password_123
   ```

7. **💾 Save Configuration**:
   - Click **"Add"** (red button)
   - Click **"Done"** in the node configuration
   - You should see the node now shows "Horse Racing DB"

### ✅ **Database Configuration Complete!**

---

## 📧 **STEP 2: Configure Email Alerts**

### Using Your App Password: `awmf ulio rtjv qybx`

1. **🚨 Navigate to Alerts Tab**:

   - Click on "🚨 Alerts" tab at the top

2. **📬 Find Email Node**:

   - Look for nodes with **envelope icons** 📧
   - Find "Send Error Alert" or "Send Test Email"

3. **⚙️ Configure Email Node**:

   - **Double-click** any email node
   - You'll see email configuration dialog

4. **🛠️ Add Email Configuration**:

   - **Click the pencil icon** ✏️ next to "Server" dropdown
   - Select "Add new email-credentials..."

5. **📝 Enter Gmail Settings**:

   ```
   Name: Gmail Alerts
   Service: (leave blank for manual config)
   Server: smtp.gmail.com
   Port: 465
   Secure: ✓ (checked)
   TLS: ✓ (checked)
   Username: jc@yourdomain.com  (your actual Gmail)
   Password: awmf ulio rtjv qybx  (your app password from .env)
   ```

6. **📮 Configure Recipients**:

   ```
   To: your-alerts-email@gmail.com
   From: jc@yourdomain.com
   Subject: Horse Racing AI Alert
   ```

7. **💾 Save Email Configuration**:
   - Click **"Add"** (red button)
   - Click **"Done"** in the node configuration

### ✅ **Email Configuration Complete!**

---

## 🚀 **STEP 3: Deploy & Test Everything**

### 🔄 Deploy Flows:

1. **Click the big red "Deploy" button** (top right corner)
2. **Select "Full Deployment"**
3. **Click "Deploy"**
4. **Wait for "Successfully deployed" message**

### 🧪 Test Database:

1. **Go to "📊 Data Pipeline" tab**
2. **Find "Test Database" inject node** (blue square button)
3. **Click the button** (should show timestamp)
4. **Check debug panel** (right sidebar, bug 🐛 icon)
5. **Look for database results** - should show PostgreSQL version info

### 📧 Test Email:

1. **Go to "🚨 Alerts" tab**
2. **Find "Test Email" inject node** (blue square button)
3. **Click the button**
4. **Check your email** for test message
5. **Check debug panel** for any errors

### 📊 Check Dashboard:

1. **Open new tab**: http://localhost:1881/ui
2. **Should see "Horse Racing AI" dashboard**
3. **Look for system status indicators**

---

## 🎯 **VISUAL TROUBLESHOOTING**

### 🔴 **If Database Test Fails**:

- **Red error in debug panel**?
- **Check database is running**: `docker ps | grep postgres`
- **Verify connection settings** match exactly
- **Try localhost vs postgres as hostname**

### 🔴 **If Email Test Fails**:

- **Check app password** is exactly: `awmf ulio rtjv qybx`
- **Verify Gmail 2FA** is enabled
- **Check SMTP settings** match exactly
- **Look for authentication errors** in debug panel

### 🔴 **If Flows Don't Deploy**:

- **Look for yellow warnings** in flows
- **Check missing nodes** (shown as dashed boxes)
- **Restart container**: `docker restart horse_racing_node_red`

---

## 📋 **Configuration Summary**

### ✅ **Database Connection**:

```yaml
Connection String: postgresql://horse_racing:secure_password_123@localhost:5432/postgres
Host: localhost
Port: 5432
Database: postgres
Username: horse_racing
Password: secure_password_123
SSL: false
```

### ✅ **Email Configuration**:

```yaml
SMTP Server: smtp.gmail.com
Port: 465
Security: SSL/TLS enabled
Username: [your Gmail address]
App Password: awmf ulio rtjv qybx
```

### ✅ **Test Results Expected**:

- **Database Test**: Should return PostgreSQL version and timestamp
- **Email Test**: Should receive email with test message
- **Dashboard**: Should show system status gauges and indicators

---

## 🆘 **Quick Commands If Needed**

```bash
# Check Node-RED status
docker ps -f name=horse_racing_node_red

# Restart Node-RED
docker restart horse_racing_node_red

# Check database
docker ps | grep postgres

# View Node-RED logs
docker logs horse_racing_node_red --tail 20
```

---

## 🎉 **Success Indicators**

### ✅ **You'll Know It's Working When**:

- [ ] Database test shows PostgreSQL version in debug panel
- [ ] Email test sends you an actual email
- [ ] Dashboard loads at http://localhost:1881/ui
- [ ] No red errors in debug panel
- [ ] Deploy button is grayed out (successful deployment)
- [ ] All nodes show green "connected" status

### 🏆 **Final Test**:

- **Click "Manual Pipeline Trigger"** in Data Pipeline tab
- **Should trigger the entire automation sequence**
- **Watch debug panel** for flow progression
- **Check for success/error emails**

---

**🏇 Once these steps are complete, your Node-RED automation will be fully operational and ready to handle your horse racing data pipeline 24/7!**
