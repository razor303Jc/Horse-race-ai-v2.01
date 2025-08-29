# Auto-Downloader Schedule Manager CLI

## Overview

The Schedule Manager CLI tool allows you to easily manage the auto-downloader's scheduled start time across all configuration files and Docker containers.

## Installation

The tool is located at: `tools/cli/schedule_manager.py`

## Usage

### Check Current Schedule Status

```bash
python tools/cli/schedule_manager.py status
```

### Update Schedule Time

```bash
# Update schedule and restart container
python tools/cli/schedule_manager.py set 04:00

# Update schedule without restarting container
python tools/cli/schedule_manager.py set 06:30 --no-restart
```

### Restart Container

```bash
python tools/cli/schedule_manager.py restart
```

## Features

- **Automatic Discovery**: Finds all configuration files and Python files with schedule settings
- **Consistency Check**: Shows if all files have the same schedule time
- **Batch Update**: Updates all files at once
- **Container Management**: Can restart the Docker container automatically
- **Validation**: Validates time format (HH:MM)

## Files Updated

The tool automatically updates schedule times in:

### JSON Configuration Files

- `config/config/daily_pipeline_config*.json`
- `config/daily_pipeline_config*.json`

### Python Files

- `tools/utilities/run_docker_auto_downloader.py`
- `docker/automation/run_docker_auto_downloader.py`
- `daily_pipeline_orchestrator.py`

## Examples

### View current schedule across all files:

```bash
python tools/cli/schedule_manager.py status
```

Output:

```
🕒 Auto-Downloader Schedule Status
========================================

⏰ Schedule: 04:00
   📄 daily_pipeline_config.json
   📄 run_docker_auto_downloader.py
   📄 daily_pipeline_orchestrator.py

✅ Consistent schedule: 04:00

🐳 Container: ✅ Running
```

### Update to morning schedule:

```bash
python tools/cli/schedule_manager.py set 06:00
```

### Update for midnight processing:

```bash
python tools/cli/schedule_manager.py set 00:00
```

## Notes

- Time format must be HH:MM (24-hour format)
- The tool requires Docker to be running for container operations
- Changes take effect immediately after container restart
- All configuration files are updated simultaneously to maintain consistency

## Troubleshooting

### Container not found

If the tool reports the container is not running, use:

```bash
python tools/cli/schedule_manager.py restart
```

### Permission issues

Make sure the script is executable:

```bash
chmod +x tools/cli/schedule_manager.py
```

### Inconsistent schedules

If the status shows multiple different schedule times, run:

```bash
python tools/cli/schedule_manager.py set [desired-time]
```

This will synchronize all files to the same schedule time.
