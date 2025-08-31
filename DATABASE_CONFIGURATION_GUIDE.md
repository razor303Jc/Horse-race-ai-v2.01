# 🗄️ Database Configuration Guide

## Overview

This guide explains the centralized database configuration system that eliminates connection problems and provides consistent database access across all scripts.

## 📁 Configuration Files

### 1. Environment Configuration (`.env`)

```env
# PostgreSQL Database Configuration
POSTGRES_PASSWORD=horse_racing_password
POSTGRES_USER=horse_racing
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Database URLs for Docker containers
CARDS_DATABASE_URL=postgresql://horse_racing:horse_racing_password@postgres:5432/cards_horse_racing_db
RESULTS_DATABASE_URL=postgresql://horse_racing:horse_racing_password@postgres:5432/results_horse_racing_db
ADVANCED_DATABASE_URL=postgresql://horse_racing:horse_racing_password@postgres:5432/advanced_horse_racing_db
```

### 2. Database Configuration Module (`config/database_config.py`)

- Centralized database connection management
- Environment variable integration
- Docker exec command generation
- Connection validation and testing

## 🗃️ Database Structure

### Available Databases:

- **`results_horse_racing_db`** - Results and entity data (horses, jockeys, trainers)
- **`cards_horse_racing_db`** - Race card data (upcoming races)
- **`advanced_horse_racing_db`** - Advanced metrics and ML analytics
- **`postgres`** - Default admin database

### Database Types in Code:

- `"results"` → `results_horse_racing_db`
- `"cards"` → `cards_horse_racing_db`
- `"advanced"` → `advanced_horse_racing_db`
- `"postgres"` → `postgres`

## 🔧 Usage Examples

### 1. Import the Configuration

```python
from config.database_config import db_config, execute_sql_command
```

### 2. Execute SQL Commands

```python
# Simple SQL execution
success = execute_sql_command("results", "SELECT COUNT(*) FROM horses_entity;")

# Custom SQL with docker exec
cmd = db_config.get_docker_exec_command("results", "SELECT * FROM horses_entity LIMIT 5;")
result = subprocess.run(cmd, capture_output=True, text=True)
```

### 3. Get Database URLs

```python
# For SQLAlchemy or other ORM connections
results_url = db_config.get_database_url("results")
# Returns: postgresql://horse_racing:password@postgres:5432/results_horse_racing_db
```

### 4. Validate Connections

```python
# Test if database is accessible
if db_config.validate_connection("results"):
    print("✅ Database connected")
else:
    print("❌ Connection failed")
```

## 🐳 Docker Integration

### Container Names:

- **PostgreSQL**: `horse_racing_postgres_clean`
- **Data Pipeline**: `horse_racing_data_pipeline_clean`
- **ML Trainer**: `horse_racing_ml_trainer_clean`
- **Web App**: `horse_racing_web_app_clean`

### Environment Variables in Docker Compose:

```yaml
environment:
  RESULTS_DATABASE_URL: postgresql://horse_racing:${POSTGRES_PASSWORD:-secure_password_123}@postgres:5432/results_horse_racing_db
  CARDS_DATABASE_URL: postgresql://horse_racing:${POSTGRES_PASSWORD:-secure_password_123}@postgres:5432/cards_horse_racing_db
  ADVANCED_DATABASE_URL: postgresql://horse_racing:${POSTGRES_PASSWORD:-secure_password_123}@postgres:5432/advanced_horse_racing_db
```

## 🔄 Migration from Old Approach

### Before (Hardcoded):

```python
def execute_sql(database, sql_command):
    cmd = [
        "docker", "exec", "horse_racing_postgres_clean",
        "psql", "-U", "horse_racing", "-d", database, "-c", sql_command
    ]
```

### After (Centralized):

```python
from config.database_config import execute_sql_command

def execute_sql(database_type, sql_command):
    return execute_sql_command(database_type, sql_command)
```

## ✅ Scripts Updated

### ✅ **Updated Scripts:**

- `scripts/fixed_entity_loader_v2_05.py` - Entity data loading
- `scripts/test_database_config.py` - Database testing

### 🔄 **Scripts to Update:**

- `tools/manual_pipeline_trigger.py`
- `tools/data_processing/automated_relationships_pipeline.py`
- `tools/automation/daily_performance_tracker.py`
- `docker/ml_training/unified_ml_trainer.py`
- `scripts/run_real_selections.py`

## 🧪 Testing

### Run Database Configuration Test:

```bash
cd /home/jc/Documents/Horse-race-ai-v2.05
python scripts/test_database_config.py
```

### Expected Output:

```
🔧 Testing Database Configuration
==================================================
✅ results: Connected (results_horse_racing_db)
✅ cards: Connected (cards_horse_racing_db)
✅ advanced: Connected (advanced_horse_racing_db)
✅ postgres: Connected (postgres)

🗃️ Testing Entity Tables:
✅ horses_entity: 418 records
✅ jockeys_entity: 6606 records
✅ trainers_entity: 4260 records

🎉 All database connections successful!
```

## 🔒 Security

### Environment Variables:

- Database passwords stored in `.env` file
- Never commit `.env` to version control
- Use `example.env` as template

### Docker Network:

- Internal network communication only
- No external database ports exposed
- Secure container-to-container communication

## 🚀 Benefits

### ✅ **Problem Solved:**

- ❌ No more hardcoded database names
- ❌ No more connection string inconsistencies
- ❌ No more "database does not exist" errors
- ❌ No more Docker exec command duplication

### ✅ **Features Added:**

- ✅ Centralized configuration management
- ✅ Environment variable integration
- ✅ Connection validation and testing
- ✅ Consistent error handling
- ✅ Easy database type switching
- ✅ Future-proof architecture

## 📈 Next Steps

1. **Update remaining Python scripts** to use the new configuration
2. **Add database configuration to Node-RED** automation
3. **Create database backup/restore scripts** using the configuration
4. **Implement connection pooling** for high-performance scenarios
5. **Add database monitoring** and health checks

---

**🎯 Result: Reliable, consistent database connectivity across the entire Horse Racing AI system!**
