# Node-RED Configuration Guide - Horse Racing AI

## 🚀 Quick Start

### 1. Start Node-RED

```bash
# Run the setup script
./setup_node_red.sh

# Or manually with Docker Compose
docker-compose -f docker-compose.node-red.yml up -d node-red
```

### 2. Access Node-RED

- **Editor**: http://localhost:1881
- **Dashboard**: http://localhost:1881/ui
- **Admin Panel**: http://localhost:1881/admin

### 3. Default Login (if authentication enabled)

- **Username**: admin
- **Password**: horse123

## 📋 Essential Configuration Steps

### Step 1: Database Connection Setup

1. Go to Node-RED editor (http://localhost:1880)
2. Double-click any PostgreSQL node
3. Configure database connection:
   ```
   Host: postgres
   Port: 5432
   Database: horse_racing
   Username: horse_racing
   Password: secure_password_123
   ```

### Step 2: Email Alert Configuration

1. Double-click any email node
2. Configure SMTP settings:
   ```
   Server: smtp.gmail.com
   Port: 465
   Secure: SSL/TLS
   Username: your-email@gmail.com
   Password: your-app-password
   ```

### Step 3: File System Paths

Verify these paths are correct in exec nodes:

```
Workspace: /workspace
Data: /workspace/data
Tools: /workspace/tools
Logs: /workspace/logs
```

## 🔧 Flow Categories

### 1. Data Pipeline Flows (Tab: 📊 Data Pipeline)

#### Daily Schedule Flow

- **Trigger**: Cron schedule (6 AM & 10 PM)
- **Purpose**: Automated data collection
- **Actions**: Download racecards → Clean CSV → Import DB → Generate predictions

#### Manual Trigger Flow

- **Trigger**: HTTP endpoint or dashboard button
- **Purpose**: On-demand pipeline execution
- **Endpoint**: http://localhost:1881/manual-trigger

#### Error Handling Flow

- **Trigger**: Pipeline failures
- **Purpose**: Error logging and alerts
- **Actions**: Log error → Send email → Update dashboard

### 2. Dashboard Flows (Tab: 📈 Dashboard)

#### System Status Dashboard

- **URL**: http://localhost:1881/ui
- **Components**:
  - System health gauge
  - Last update timestamp
  - Pipeline status indicators
  - Error log display

#### AI Predictions Dashboard

- **Components**:
  - Prediction accuracy chart
  - Best bets table
  - Performance metrics
  - ROI tracking

#### Data Quality Dashboard

- **Components**:
  - File processing status
  - Data validation results
  - CSV cleaning reports
  - Database import status

### 3. Alert Flows (Tab: 🚨 Alerts)

#### Critical Alerts

- **Triggers**: Pipeline failures, database errors
- **Actions**: Immediate email + SMS
- **Recipients**: Admin team

#### Warning Alerts

- **Triggers**: Data quality issues, performance drops
- **Actions**: Email notification
- **Frequency**: Batched (max 1 per hour)

#### Success Notifications

- **Triggers**: Pipeline completion, new predictions
- **Actions**: Summary email
- **Frequency**: Daily summary

### 4. API Orchestration (Tab: 🔗 API Orchestration)

#### Data Source APIs

- **Racing data providers**
- **Weather services**
- **Odds comparison APIs**
- **Rate limiting and retry logic**

#### Internal APIs

- **Database queries**
- **Model predictions**
- **Performance analytics**
- **System monitoring**

### 5. Reporting Flows (Tab: 📄 Reporting)

#### Daily Reports

- **Schedule**: 11 PM daily
- **Content**: Performance summary, predictions, system status
- **Format**: HTML email + PDF attachment

#### Weekly Reports

- **Schedule**: Sunday 6 PM
- **Content**: Comprehensive analysis, trends, recommendations
- **Distribution**: Email + web portal

## 🎛️ Dashboard UI Components

### Main Dashboard Groups

#### System Status Group

```javascript
- System Health Gauge (0-100%)
- Pipeline Status Text
- Last Update Timestamp
- Active Process Indicator
- Error Count Badge
```

#### AI Predictions Group

```javascript
- Prediction Accuracy Chart (line chart)
- Best Bets Table (top 5 daily)
- Performance Metrics (win rate, ROI)
- Confidence Distribution (histogram)
```

#### Data Quality Group

```javascript
- Files Processed Counter
- Data Validation Status
- CSV Cleaning Results
- Database Import Progress
```

#### Controls Group

```javascript
- Manual Pipeline Trigger Button
- Emergency Stop Button
- Refresh Data Button
- Export Reports Button
```

## 🔐 Security Configuration

### Authentication Setup

1. Enable admin authentication in settings.js
2. Set strong password hash
3. Configure session timeout
4. Enable HTTPS (production)

### API Security

1. Set up API keys for external services
2. Configure rate limiting
3. Enable request logging
4. Set up CORS policies

### Database Security

1. Use connection pooling
2. Enable SSL connections
3. Limit connection timeouts
4. Monitor query performance

## 📊 Monitoring & Logging

### Log Levels

- **Debug**: Development debugging
- **Info**: General information
- **Warn**: Warning conditions
- **Error**: Error conditions
- **Fatal**: Critical errors

### Log Destinations

- **Console**: Docker logs
- **File**: /data/node-red.log
- **Database**: Error tracking table
- **Email**: Critical error alerts

### Metrics Tracking

- **Flow execution times**
- **Error rates**
- **API response times**
- **Database query performance**
- **System resource usage**

## 🚀 Advanced Features

### Custom Nodes Development

```javascript
// Example: Horse Racing Data Validator Node
module.exports = function (RED) {
  function HorseDataValidator(config) {
    RED.nodes.createNode(this, config);
    var node = this;

    node.on("input", function (msg) {
      // Validate horse racing data
      var isValid = validateData(msg.payload);
      msg.payload.isValid = isValid;
      node.send(msg);
    });
  }
  RED.nodes.registerType("horse-data-validator", HorseDataValidator);
};
```

### Subflow Templates

- **Data Download Subflow**: Reusable download logic
- **Error Handler Subflow**: Standard error processing
- **Dashboard Update Subflow**: UI refresh patterns
- **Email Template Subflow**: Formatted notifications

### Context Storage

```javascript
// Flow-level context
flow.set("lastUpdate", new Date());
var lastUpdate = flow.get("lastUpdate");

// Global context
global.set("systemStatus", "running");
var status = global.get("systemStatus");
```

## 🔧 Troubleshooting

### Common Issues

#### Node-RED Won't Start

```bash
# Check Docker logs
docker logs horse_racing_node_red

# Verify network connectivity
docker network ls | grep horse_racing

# Check port conflicts
netstat -an | grep 1880
```

#### Database Connection Fails

```bash
# Test database connectivity
docker exec horse_racing_node_red ping postgres

# Check database credentials
docker exec -it horse_racing_postgres_clean psql -U horse_racing -d horse_racing
```

#### Email Alerts Not Working

1. Verify SMTP settings
2. Check app passwords (Gmail)
3. Test with simple email node
4. Review email logs

#### Dashboard Not Loading

1. Check if dashboard nodes are installed
2. Verify UI routes are configured
3. Clear browser cache
4. Check for JavaScript errors

### Performance Optimization

#### Flow Optimization

- Use link nodes for complex flows
- Implement proper error handling
- Minimize payload sizes
- Use context storage efficiently

#### Database Optimization

- Use connection pooling
- Implement query timeouts
- Monitor slow queries
- Regular maintenance tasks

#### Resource Management

- Monitor memory usage
- Set appropriate timeouts
- Implement rate limiting
- Use efficient data structures

## 📚 Additional Resources

### Node-RED Documentation

- [Official Documentation](https://nodered.org/docs/)
- [Flow Development Guide](https://nodered.org/docs/developing-flows/)
- [Node Development](https://nodered.org/docs/creating-nodes/)

### Community Resources

- [Node-RED Forum](https://discourse.nodered.org/)
- [GitHub Repository](https://github.com/node-red/node-red)
- [Community Flows](https://flows.nodered.org/)

### Horse Racing Specific

- [Racing APIs Documentation](./api-documentation/)
- [Data Schema Reference](./schema-reference/)
- [ML Model Integration](./ml-integration-guide/)

---

_This configuration guide provides everything needed to set up and manage Node-RED automation for your horse racing AI system. Follow the steps systematically for best results._
