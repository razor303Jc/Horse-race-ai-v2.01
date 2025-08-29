# Respectful Auto Downloader

A responsible, once-daily auto downloader for horse racing data that respects horseracedatabase.com while we await their official API release.

## ⚠️ Important Notice

This is a **temporary solution** until horseracedatabase.com releases their official API. The downloader is designed to be:

- **Respectful**: Follows politeness policies with appropriate delays
- **Scheduled**: Runs once daily at 00:01 and stops when successful
- **Rate-limited**: Maximum 15 requests per minute with 3-second delays
- **Single-threaded**: Only one page request at a time
- **Honest**: Uses appropriate User-Agent and respects robots.txt

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-auto-downloader.txt
playwright install chromium
```

### 2. Test Configuration

```bash
./scripts/manage_auto_downloader.sh test
```

### 3. Install and Start Service

```bash
./scripts/manage_auto_downloader.sh install
./scripts/manage_auto_downloader.sh start
```

### 4. Check Status

```bash
./scripts/manage_auto_downloader.sh status
```

## 📋 Management Commands

| Command     | Description                         |
| ----------- | ----------------------------------- |
| `install`   | Install the auto downloader service |
| `start`     | Start the service                   |
| `stop`      | Stop the service                    |
| `restart`   | Restart the service                 |
| `status`    | Show service status and recent logs |
| `logs`      | Show recent logs                    |
| `manual`    | Run download manually for testing   |
| `test`      | Test configuration and dependencies |
| `uninstall` | Remove the service                  |

## ⏰ Schedule

- **Run Time**: 00:01 daily
- **Behavior**: Runs once and stops when successful
- **Max Runtime**: 60 minutes (configurable)
- **Retry Logic**: 3 attempts with 5-second delays

## 🛡️ Respectful Scraping Policies

### Rate Limiting

- Maximum **15 requests per minute**
- **3-second delay** between page loads
- **5-second delay** before retries
- **Single-threaded** operation only

### Politeness Features

- Honest User-Agent identification
- Respects robots.txt directives
- Appropriate HTTP headers
- Graceful error handling
- Comprehensive logging

### Success Criteria

- Minimum **10 races** downloaded
- Minimum **4 horses** per race
- Valid data structure
- Complete without errors

## 📁 File Structure

```
src/automation/
├── respectful_auto_downloader.py  # Main downloader class
├── daily_scheduler.py             # Daily scheduling service
└── README.md                      # This file

config/
└── respectful_downloader_config.json  # Configuration file

scripts/
├── manage_auto_downloader.sh      # Management script
└── horse-racing-auto-downloader.service  # Systemd service

data/daily_downloads/
├── race_data_*.json              # Downloaded race data
├── *.session.json                # Session metadata
├── last_success.json             # Last successful run
└── last_failure.json             # Last failed run
```

## ⚙️ Configuration

Edit `config/respectful_downloader_config.json`:

```json
{
  "daily_run_time": "00:01",
  "page_delay_seconds": 3.0,
  "requests_per_minute": 15,
  "minimum_races_required": 10,
  "respectful_settings": {
    "max_requests_per_minute": 15,
    "page_load_delay_seconds": 3,
    "single_threaded": true
  }
}
```

## 📊 Monitoring

### Check Service Status

```bash
./scripts/manage_auto_downloader.sh status
```

### View Live Logs

```bash
./scripts/manage_auto_downloader.sh logs
```

### Manual Test Run

```bash
./scripts/manage_auto_downloader.sh manual
```

### Check Downloaded Data

```bash
ls -la data/daily_downloads/
```

## 🔧 Troubleshooting

### Service Won't Start

1. Check dependencies: `./scripts/manage_auto_downloader.sh test`
2. Check permissions on data/logs directories
3. Review logs: `sudo journalctl -u horse-racing-auto-downloader.service`

### Download Failures

1. Check internet connectivity
2. Verify horseracedatabase.com is accessible
3. Review download logs in `data/daily_downloads/`
4. Check if site structure has changed

### Configuration Issues

1. Validate JSON: `python3 -m json.tool config/respectful_downloader_config.json`
2. Check file permissions
3. Verify paths exist

## 🎯 Data Output

### Downloaded Files

- `race_data_YYYYMMDD_HHMMSS.json` - Race data
- `race_data_YYYYMMDD_HHMMSS.session.json` - Session metadata

### Data Structure

```json
{
  "download_date": "2025-08-09T00:01:00",
  "races": [
    {
      "race_number": 1,
      "race_name": "Sample Stakes",
      "track": "Sample Track",
      "race_time": "14:00",
      "distance": "1 mile",
      "horses": []
    }
  ],
  "metadata": {
    "source": "horseracedatabase.com",
    "download_method": "respectful_auto_downloader"
  }
}
```

## 📞 Support

- **Purpose**: Temporary data collection until official API
- **Contact**: Respectful research use only
- **Migration**: Will switch to official API when available

## ⚖️ Legal & Ethical

- Respects website terms of service
- Follows robots.txt directives
- Implements appropriate delays
- Temporary solution only
- Research and analysis purposes
- Will migrate to official API

---

**Note**: This downloader is designed to be a responsible, temporary solution. We look forward to migrating to the official horseracedatabase.com API when it becomes available.
