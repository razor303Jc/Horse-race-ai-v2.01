# Production System Deployment Guide

## 🚀 Complete Production Setup Instructions

Your Horse Racing AI system is now ready for live deployment! This guide walks you through the complete setup process.

## 📋 Production Components

✅ **1. Live Race Data API** - Real-time race data feeds  
✅ **2. Betting Exchange API** - Automated bet placement via Betfair  
✅ **3. Web Dashboard** - Production deployment with SSL  
✅ **4. Email/SMS Alerts** - Comprehensive notification system  
✅ **5. Live Strategy Execution** - Automated strategy coordination

## 🔧 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r api/requirements.txt
pip install -r docker/requirements-integrated.txt

# Additional production packages
pip install gunicorn nginx twilio betfairlightweight websockets
```

### 2. Create Configuration

```bash
# Create all config files
python production_system.py create-config
```

### 3. Configure API Keys

Edit the following config files with your credentials:

#### `config/race_data_api_config.json`

```json
{
  "api_key": "YOUR_RACING_API_KEY_HERE",
  "betfair_app_key": "YOUR_BETFAIR_APP_KEY",
  "betfair_username": "YOUR_BETFAIR_USERNAME",
  "betfair_password": "YOUR_BETFAIR_PASSWORD"
}
```

#### `config/betting_exchange_config.json`

```json
{
  "exchanges": {
    "betfair": {
      "app_key": "YOUR_BETFAIR_APP_KEY",
      "username": "YOUR_BETFAIR_USERNAME",
      "password": "YOUR_BETFAIR_PASSWORD"
    }
  }
}
```

#### `config/alert_config.json`

```json
{
  "email": {
    "username": "your-email@gmail.com",
    "password": "your-gmail-app-password"
  },
  "sms": {
    "account_sid": "YOUR_TWILIO_ACCOUNT_SID",
    "auth_token": "YOUR_TWILIO_AUTH_TOKEN",
    "from_number": "+1234567890"
  }
}
```

### 4. Start Production System

```bash
# Start all services
python production_system.py start

# Or start individual services
python production_system.py start --service dashboard
python production_system.py start --service execution
```

## 🔑 API Key Setup

### Racing Data API

1. Visit [The Racing API](https://www.theracingapi.com/)
2. Sign up for an account
3. Get your API key from dashboard
4. Add to `config/race_data_api_config.json`

### Betfair API

1. Create [Betfair account](https://developer.betfair.com/)
2. Apply for API access
3. Generate application key
4. Add credentials to `config/betting_exchange_config.json`

### Twilio SMS (Optional)

1. Sign up at [Twilio](https://www.twilio.com/)
2. Get Account SID and Auth Token
3. Buy a phone number
4. Add to `config/alert_config.json`

### Gmail SMTP (Optional)

1. Enable 2-factor authentication on Gmail
2. Generate app-specific password
3. Add to `config/alert_config.json`

## 🌐 Dashboard Access

Once started, access your dashboard at:

- **Local**: http://localhost:5000
- **Production**: https://yourdomain.com (after SSL setup)

## 📊 Dashboard Features

- **Live Race Data**: Real-time odds and market updates
- **Strategy Performance**: 80/20 and dutching results
- **Betting Positions**: Active bets and P&L
- **Risk Management**: Exposure and balance monitoring
- **Alert System**: Live notifications and history

## ⚠️ Safety Features

### Risk Management

- Maximum daily stake limits
- Stop-loss protection
- Balance monitoring
- Position size limits
- Manual approval mode

### Simulation Mode

The system starts in **simulation mode** by default:

- No real money at risk
- All strategies tested with paper trading
- Full functionality without actual betting

## 🔧 System Commands

```bash
# Check system status
python production_system.py status

# Stop all services
python production_system.py stop

# Monitor services
python production_system.py monitor

# Create fresh configs
python production_system.py create-config
```

## 📁 File Structure

```
Horse-race-ai-v2.03/
├── production_system.py          # Main launcher
├── live_race_data_api.py         # Live data feeds
├── betting_exchange_api.py       # Betting automation
├── production_dashboard.py       # Web deployment
├── alert_system.py              # Notifications
├── live_strategy_execution.py    # Strategy coordination
├── config/                      # Configuration files
│   ├── race_data_api_config.json
│   ├── betting_exchange_config.json
│   ├── alert_config.json
│   └── live_execution_config.json
└── logs/                        # System logs
```

## 🔒 Security Setup

### SSL Certificate (Production)

```bash
# Install certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com

# Configure in production_dashboard.py
```

### Firewall Configuration

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5000  # Development only
```

## 📈 Strategy Configuration

### 80/20 Strategy

- **Max Odds**: 10.0
- **Min Odds**: 2.0
- **Default Stake**: £15
- **Target ROI**: 107.7%

### Dutching Strategy

- **Max Selections**: 4
- **Min Total Probability**: 70%
- **Default Stake**: £25
- **Target ROI**: 93.11%

## 🔄 Going Live

### 1. Test in Simulation

```bash
# Ensure simulation mode in config/live_execution_config.json
{
  "execution_mode": "simulation",
  "auto_place_bets": false,
  "require_manual_approval": true
}
```

### 2. Enable Live Trading

```bash
# Edit config/live_execution_config.json
{
  "execution_mode": "live",
  "auto_place_bets": true,
  "require_manual_approval": false
}
```

### 3. Start with Small Stakes

```bash
# Conservative settings for first week
{
  "max_daily_stake": 50.0,
  "max_single_stake": 10.0,
  "max_exposure": 100.0
}
```

## 📞 Support & Monitoring

### System Health Checks

- **Dashboard**: Monitor at http://localhost:5000
- **Logs**: Check `logs/production_system.log`
- **Performance**: View strategy results in dashboard
- **Alerts**: Email/SMS notifications for issues

### Common Issues

#### Service Won't Start

```bash
# Check logs
tail -f logs/production_system.log

# Restart specific service
python production_system.py stop
python production_system.py start --service dashboard
```

#### API Connection Issues

```bash
# Verify API keys in config files
# Check network connectivity
# Review Betfair API status
```

#### Performance Issues

```bash
# Monitor system resources
# Check database performance
# Review strategy parameters
```

## 🎯 Next Steps

1. **Configure API Keys** - Add all your credentials
2. **Test in Simulation** - Run strategies without real money
3. **Monitor Performance** - Watch dashboard for 1-2 days
4. **Enable Alerts** - Test email/SMS notifications
5. **Go Live** - Switch to live mode with small stakes
6. **Scale Up** - Increase stakes as confidence grows

## 📊 Performance Targets

- **80/20 Strategy**: +0.69% ROI (validated on real data)
- **Dutching Strategy**: -2.18% ROI (needs optimization)
- **Combined System**: Target +5-10% monthly returns
- **Risk Management**: Maximum 2% daily drawdown

## 🚨 Emergency Procedures

### Stop All Trading

```bash
python production_system.py stop
```

### Emergency Contact

- Check dashboard alerts
- Review email notifications
- Monitor balance in Betfair account
- Contact support if needed

---

## 🎉 Congratulations!

Your complete production trading system is ready! Start in simulation mode, monitor performance, and gradually transition to live trading as you gain confidence.

**Remember**: Always trade responsibly and within your means. Past performance does not guarantee future results.
