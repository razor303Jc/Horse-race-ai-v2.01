# 🔧 DOCKER DEVELOPMENT WORKFLOW GUIDE

## Using Docker Volumes for Live Development

_Updated: August 25, 2025 - Post Schema Guardian Success_

---

## 🎯 **CURRENT DOCKER DEVELOPMENT SETUP**

### **✅ Docker Volumes Configuration**

Your Docker setup is **perfectly configured** for development with live volume mounting:

```yaml
# Key Volume Mappings from docker-compose.clean.yml:

data-pipeline:
  volumes:
    - ./data:/app/data:rw # Live data access
    - ./tools:/app/tools:ro # Schema Guardian tools
    - ./scripts:/app/scripts:ro # Scripts
    - ./config:/app/config:ro # Configuration
    - ./logs:/app/logs:rw # Live log access
    - ./cache:/app/cache:rw # Cache storage

web-app:
  volumes:
    - ./src:/app/src # Live source code
    - ./templates:/app/templates # Live templates
    - ./api:/app/api # Live API code
    - ./logs:/app/logs:rw # Live logs

ml-trainer:
  volumes:
    - ./models:/app/models:rw # Live model access
    - ./trained_models:/app/trained_models:rw # Model outputs
    - ./tools:/app/tools:ro # ML tools
    - ./src:/app/src:ro # Source code
    - ./data:/app/data:ro # Data access
```

---

## 🚀 **LIVE DEVELOPMENT WORKFLOW**

### **1. Code Changes are LIVE**

When you edit files locally, they're **immediately available** in containers:

- ✅ **Schema Guardian tools** (`./tools/schema_guardian/`) → Live in data-pipeline
- ✅ **Web app source** (`./src/`) → Live in web-app container
- ✅ **API code** (`./api/`) → Live in web-app container
- ✅ **ML models** (`./models/`) → Live in ml-trainer container
- ✅ **Configuration** (`./config/`) → Live in all containers
- ✅ **Test files** (`./tests/`) → Available for live testing

### **2. Running Tests with Docker Volumes**

Since `./tests/` is mounted, you can run tests directly:

```bash
# Run tests inside data-pipeline container (has network access)
docker exec horse_racing_data_pipeline_clean python -m pytest /app/tests/test_schema_guardian_regression.py -v

# Run Schema Guardian tools
docker exec horse_racing_data_pipeline_clean python /app/tools/schema_guardian/ultimate_schema_guardian.py

# Run API tests
docker exec horse_racing_web_app_clean python -m pytest /app/tests/test_api_comprehensive.py -v
```

### **3. Live Development Benefits**

✅ **No Rebuild Required** - Edit code locally, run immediately in container  
✅ **Database Access** - Containers have internal network access to PostgreSQL  
✅ **Schema Guardian Works** - All tools available with proper database connections  
✅ **Live Debugging** - Edit, test, debug without container rebuilds  
✅ **Real Data Testing** - Test with actual 14,825 records in database

---

## 🔬 **ENHANCED TEST FRAMEWORK WORKFLOW**

### **Step 1: Update Test Framework (Live)**

```bash
# Edit tests locally (immediately available in containers)
vim tests/test_schema_guardian_regression.py

# Run updated tests immediately
docker exec horse_racing_data_pipeline_clean python -m pytest /app/tests/test_schema_guardian_regression.py -v
```

### **Step 2: Fix Schema Guardian Issues (Live)**

```bash
# Edit Schema Guardian locally
vim tools/schema_guardian/ultimate_schema_guardian.py

# Test changes immediately
docker exec horse_racing_data_pipeline_clean python /app/tools/schema_guardian/ultimate_schema_guardian.py
```

### **Step 3: Web App Development (Live)**

```bash
# Edit web app code locally
vim src/web_app.py
vim api/prediction_api.py

# Changes are live in web container immediately
# Access via http://localhost:3000
```

---

## 🎯 **IMMEDIATE ACTIONS WITH DOCKER VOLUMES**

### **1. Fix Test Framework (3-4 hours) - LIVE DEVELOPMENT**

**Task:** Run comprehensive test audit using Docker network access

```bash
# Install missing dependencies in container
docker exec horse_racing_data_pipeline_clean pip install coverage

# Run comprehensive test suite with network access
docker exec horse_racing_data_pipeline_clean python /app/tests/run_comprehensive_tests.py

# Fix failing tests by editing locally, testing immediately
```

**Benefits of Docker Volume Approach:**

- ✅ Edit tests locally in your preferred editor
- ✅ Run tests immediately with database access
- ✅ No container rebuilds required
- ✅ Live debugging and iteration

### **2. Fix Web Application (2-4 hours) - LIVE DEVELOPMENT**

**Task:** Fix web app deployment using live volumes

```bash
# Check current web app status
docker ps | grep web

# Edit web app configuration locally
vim src/web_app.py        # Changes immediately available
vim api/prediction_api.py  # Changes immediately available

# Test immediately
curl http://localhost:3000/health
```

### **3. Schema Guardian Enhancement - LIVE DEVELOPMENT**

**Task:** Add regression tests using live volumes

```bash
# Edit Schema Guardian locally
vim tools/schema_guardian/ultimate_schema_guardian.py

# Test immediately with database access
docker exec horse_racing_data_pipeline_clean python /app/tools/schema_guardian/ultimate_schema_guardian.py

# Add tests locally
vim tests/test_schema_guardian_regression.py

# Run immediately
docker exec horse_racing_data_pipeline_clean python -m pytest /app/tests/test_schema_guardian_regression.py -v
```

---

## 💡 **DEVELOPMENT BEST PRACTICES WITH DOCKER VOLUMES**

### **Live Development Cycle:**

1. **Edit Locally** → Use your preferred IDE/editor
2. **Test in Container** → Immediate access to database/network
3. **Debug Live** → Add logs, test immediately
4. **Iterate Fast** → No rebuild delays

### **Database Development:**

```bash
# Schema changes available immediately
vim database/schemas/create_tables.sql

# Test database connections
docker exec horse_racing_data_pipeline_clean python -c "
import psycopg2
conn = psycopg2.connect(
    host='horse_racing_postgres_clean',
    port=5432,
    database='results_horse_racing_db',
    user='horse_racing',
    password='secure_password_123'
)
print('✅ Database connected successfully')
conn.close()
"
```

### **ML Model Development:**

```bash
# Edit ML code locally
vim src/ai_selections.py
vim models/ensemble_predictor.py

# Models and trained_models are live-mounted
# Changes immediately available for testing
```

---

## 🎉 **WHY THIS SETUP IS PERFECT FOR DEVELOPMENT**

### **✅ Current Advantages:**

1. **Live Code Changes** - No container rebuilds
2. **Database Network Access** - Tests work with real data
3. **14,825 Records Available** - Test with real dataset
4. **Schema Guardian Ready** - All tools immediately available
5. **Multi-Service Testing** - Web, API, ML, Pipeline all connected

### **✅ Immediate Benefits:**

- **Fix Test Framework** → Edit locally, run with database access
- **Fix Web App** → Edit locally, test immediately on port 3000
- **Enhance Schema Guardian** → Edit tools, test with real data immediately
- **ML Development** → Train models, test predictions immediately

---

## 🚀 **NEXT ACTION: START LIVE DEVELOPMENT**

**RECOMMENDED:** Start with test framework audit using Docker volumes:

```bash
# Check current test framework status
docker exec horse_racing_data_pipeline_clean python -m pytest /app/tests/ --collect-only | head -20

# Run Schema Guardian tests with database access
docker exec horse_racing_data_pipeline_clean python -m pytest /app/tests/test_schema_guardian_regression.py -v

# Fix issues by editing locally, testing immediately
```

This workflow leverages your excellent Docker volume setup for rapid, live development with full database and network access.

---

_This development workflow enables rapid iteration while maintaining the benefits of containerized database and network access._
