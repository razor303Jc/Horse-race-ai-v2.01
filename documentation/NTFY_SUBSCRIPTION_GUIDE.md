# NTFY Topics for Horse Racing AI

## Overview

The Horse Racing AI system uses NTFY for real-time notifications. Below are the topics you should subscribe to for comprehensive monitoring.

## 📱 Mobile App Setup

### Download NTFY App

- **Android**: [Google Play Store](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
- **iOS**: [App Store](https://apps.apple.com/us/app/ntfy/id1625396347)
- **Web**: Access via `https://ntfy.horse-racing.{YOUR_DOMAIN}`

## 🔔 Topics to Subscribe

### Primary Topic

```
horse-racing-alerts
```

**Purpose**: Main notification channel for all alerts

### System Alerts

```
horse_racing_alerts_system
```

**Purpose**: System health, service status, deployment updates
**Priority**: High
**Examples**:

- Service restarts
- Database connectivity issues
- System maintenance notifications

### Data Collection Alerts

```
horse_racing_alerts_data
```

**Purpose**: Data scraping, collection, and processing updates
**Priority**: Medium
**Examples**:

- Successful race data collection
- Data source connectivity issues
- New race meetings detected

### Analysis Alerts

```
horse_racing_alerts_analysis
```

**Purpose**: AI model predictions, analysis results
**Priority**: Medium
**Examples**:

- New predictions available
- Analysis completion notifications
- Model performance updates

### Betting Opportunities

```
horse_racing_alerts_betting
```

**Purpose**: High-confidence betting opportunities
**Priority**: High
**Examples**:

- Value bet alerts
- High-probability predictions
- Betting recommendations

### Performance Monitoring

```
horse_racing_alerts_performance
```

**Purpose**: System performance and optimization alerts
**Priority**: Low
**Examples**:

- Performance metrics
- Resource usage alerts
- Optimization recommendations

### Security Alerts

```
horse_racing_alerts_security
```

**Purpose**: Security-related notifications
**Priority**: Critical
**Examples**:

- Failed login attempts
- Security policy violations
- Unusual activity detection

## 🛠️ Subscription Commands

### Using NTFY CLI

```bash
# Subscribe to all topics
ntfy subscribe horse-racing-alerts
ntfy subscribe horse_racing_alerts_system
ntfy subscribe horse_racing_alerts_data
ntfy subscribe horse_racing_alerts_analysis
ntfy subscribe horse_racing_alerts_betting
ntfy subscribe horse_racing_alerts_performance
ntfy subscribe horse_racing_alerts_security
```

### Using Web Interface

1. Visit `https://ntfy.horse-racing.{YOUR_DOMAIN}`
2. Click "Subscribe to topic"
3. Enter each topic name
4. Configure notification preferences

### Using Mobile App

1. Open NTFY app
2. Tap "+" to add subscription
3. Enter server URL: `https://ntfy.horse-racing.{YOUR_DOMAIN}`
4. Enter topic name
5. Configure notification settings
6. Repeat for all topics

## 🎯 Recommended Notification Settings

### High Priority Topics

- `horse_racing_alerts_betting` - Immediate notifications
- `horse_racing_alerts_security` - Immediate notifications
- `horse_racing_alerts_system` - Immediate notifications

### Medium Priority Topics

- `horse_racing_alerts_data` - Normal notifications
- `horse_racing_alerts_analysis` - Normal notifications

### Low Priority Topics

- `horse_racing_alerts_performance` - Silent/badge only

## 🔧 Testing Notifications

After subscribing, you can test notifications by running:

```bash
# Test basic notification
curl -d "Test notification from Horse Racing AI" https://ntfy.horse-racing.{YOUR_DOMAIN}/horse-racing-alerts

# Test with priority and emoji
curl -H "Priority: high" -H "Title: 🏇 Test Alert" -d "Testing high-priority notification" https://ntfy.horse-racing.{YOUR_DOMAIN}/horse_racing_alerts_betting
```

## 📊 Notification Examples

### System Alert

```
🔧 System Alert
Service restart completed successfully
Database: Connected ✅
Cache: Active ✅
Scraper: Running ✅
```

### Betting Opportunity

```
💰 High-Value Bet Alert
Race: Kempton 15:30
Horse: Thunder Strike
Predicted Win Probability: 85%
Current Odds: 3.5
Value Rating: ⭐⭐⭐⭐⭐
```

### Data Collection

```
📊 Data Update
Successfully collected 47 race results
Updated horse performance ratings
New predictions available for tomorrow's races
```

## 🛡️ Privacy and Security

- All notifications are sent through your private NTFY instance
- No data is shared with external NTFY services
- Topics are private to your deployment
- Consider using authentication middleware for enhanced security

## 📱 Mobile App Configuration Tips

1. **Notification Sounds**: Set unique sounds for high-priority topics
2. **Do Not Disturb**: Configure quiet hours for low-priority notifications
3. **Badges**: Enable badge counts for unread notifications
4. **Grouping**: Group related topics for better organization
