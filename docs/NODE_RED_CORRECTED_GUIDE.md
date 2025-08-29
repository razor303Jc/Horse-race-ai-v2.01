# 🎯 CORRECTED Node-RED Configuration Guide

## 🔍 **WHAT YOU'LL ACTUALLY SEE IN NODE-RED**

Since there's no "Test Query" node, here's what to look for in your current flows:

---

## **📧 STEP 1: Configure Email First (Easier to Find)**

### **In Node-RED Editor (http://localhost:1881):**

1. **Look for these tabs at the top:**

   ```
   🏇 Main │📊 Data │📈 Dashboard│🚨 Alerts│🔗 API │📄 Reports
   ```

2. **Click "🚨 Alerts" tab**

3. **You should see these email nodes:**

   - **📧 "Error Alert Email"**
   - **📧 "Success Notification"**

4. **Double-click "Error Alert Email"** (or any email node)

5. **You'll see a configuration dialog. Look for:**

   ```
   Server: [dropdown - might say "Add new email-credentials..."]
   ```

6. **Click the pencil icon ✏️** next to the Server dropdown

7. **Enter EXACTLY:**

   ```
   Name: Gmail Alert System
   Service: (leave blank)
   Server: smtp.gmail.com
   Port: 465
   Secure: ☑ (checked)
   TLS: ☑ (checked)
   Username: [YOUR GMAIL ADDRESS]
   Password: awmf ulio rtjv qybx
   ```

8. **Click "Add"** then **"Done"**

---

## **🗄️ STEP 2: Find Database Nodes**

### **Look for ANY of these in the flows:**

1. **In "📊 Data Pipeline" tab, look for:**

   - Any **purple colored nodes**
   - Nodes with **database icons** 🗄️
   - Nodes mentioning **"Import"** or **"Database"**
   - The node **"Import to Database"** (this should exist)

2. **If you see "Import to Database" node:**

   - **Double-click it**
   - **Look for database configuration**
   - **Click pencil icon ✏️** next to database dropdown

3. **Enter database settings:**
   ```
   Name: Horse Racing Database
   Host: localhost
   Port: 5432
   Database: postgres
   Username: horse_racing
   Password: secure_password_123
   SSL: ☐ (unchecked)
   ```

---

## **🔧 STEP 3: Add Test Nodes (Manual)**

### **Since test nodes are missing, let's add them:**

1. **In "📊 Data Pipeline" tab**

2. **From the left palette, drag these nodes:**

   - **Drag "inject"** node (under common)
   - **Drag "postgres"** node (should be available after install)
   - **Drag "debug"** node (under common)

3. **Connect them:** inject → postgres → debug

4. **Configure the postgres node** with the database settings above

5. **Set inject node** to trigger on button click

---

## **🎯 ALTERNATIVE: Import Complete Flow**

### **If you can't find the right nodes, try this:**

1. **In Node-RED, click the hamburger menu** ☰ (top right)
2. **Select "Import"**
3. **Copy and paste this simple test flow:**

```json
[
  {
    "id": "test_inject",
    "type": "inject",
    "name": "Test DB",
    "props": [{ "p": "payload" }],
    "topic": "",
    "payload": "",
    "payloadType": "date",
    "x": 200,
    "y": 200,
    "wires": [["test_postgres"]]
  },
  {
    "id": "test_postgres",
    "type": "postgres",
    "name": "DB Test",
    "query": "SELECT current_timestamp, version()",
    "x": 400,
    "y": 200,
    "wires": [["test_debug"]]
  },
  {
    "id": "test_debug",
    "type": "debug",
    "name": "Results",
    "x": 600,
    "y": 200,
    "wires": []
  }
]
```

4. **Click "Import"**
5. **Configure the postgres node** in the imported flow

---

## **🚨 WHAT TO DO IF NOTHING WORKS:**

### **Let's start over with a fresh approach:**

1. **Tell me exactly what you see when you:**

   - Click "📊 Data Pipeline" tab
   - List all the node names you can see

2. **Or take a screenshot** of the Node-RED interface

3. **I'll guide you based on your actual setup**

---

## **📋 QUICK CHECK:**

**In your Node-RED interface, do you see:**

- [ ] Tabs at the top with emoji icons?
- [ ] An "🚨 Alerts" tab?
- [ ] Email nodes with envelope icons 📧?
- [ ] Any purple or database-looking nodes?
- [ ] A left sidebar with node types?

**Let me know what you actually see, and I'll give you the exact steps for YOUR specific setup!**

---

## **🔍 DEBUGGING STEPS:**

```bash
# Check if Node-RED is properly loaded
curl -s http://localhost:1881/flows | jq '. | length'

# Should return a number > 0

# Check what flows are actually loaded
curl -s http://localhost:1881/flows | jq '.[].name' | head -10
```

**Tell me what output you get from these commands, and I'll help you configure exactly what you have!**
