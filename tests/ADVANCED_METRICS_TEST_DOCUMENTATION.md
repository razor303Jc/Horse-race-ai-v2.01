# Advanced Metrics Test Framework Documentation

## 🧪 Test Suite Overview

This comprehensive test framework validates the advanced metrics calculation system across multiple dimensions:

### Test Categories

1. **Unit Tests** (`tests/unit/test_advanced_metrics.py`)

   - Individual calculation logic testing
   - Data validation and error handling
   - Algorithm correctness verification

2. **Integration Tests** (`tests/integration/test_advanced_metrics_integration.py`)

   - Docker container integration
   - Database connectivity and operations
   - End-to-end pipeline testing
   - Node-RED integration scenarios

3. **Performance Tests** (`tests/performance/test_advanced_metrics_performance.py`)
   - Execution time benchmarks
   - Memory usage optimization
   - Scalability testing
   - Stress testing under load

## 🚀 Running Tests

### Quick Test Run

```bash
# Run all advanced metrics tests
python tests/run_advanced_metrics_tests.py

# Run specific test categories
pytest tests/unit/test_advanced_metrics.py -v
pytest tests/integration/test_advanced_metrics_integration.py -v
pytest tests/performance/test_advanced_metrics_performance.py -v
```

### Prerequisites

- Docker containers running: `horse_racing_postgres_clean`, `horse_racing_data_pipeline_clean`
- Database connectivity to both `results_horse_racing_db` and `ai_horse_racing_db`
- Sample data in results database
- Python packages: `pytest`, `docker`, `psycopg2`, `pandas`, `numpy`, `psutil`

## 📊 Test Coverage

### Unit Tests Coverage

- ✅ Speed ratings calculation logic
- ✅ Power ratings calculation logic
- ✅ Monte Carlo simulation algorithms
- ✅ Data validation and error handling
- ✅ Position-based metric calculations
- ✅ Calculation consistency across runs

### Integration Tests Coverage

- ✅ Docker container connectivity
- ✅ Database schema validation
- ✅ Complete pipeline execution
- ✅ Data quality verification
- ✅ Horse/race relationship integrity
- ✅ Node-RED exec node compatibility
- ✅ Error handling and timeout scenarios

### Performance Tests Coverage

- ✅ Large dataset processing (1000+ records)
- ✅ Memory efficiency validation
- ✅ Scalability across different data sizes
- ✅ Real Docker execution benchmarks
- ✅ Repeated execution stability
- ✅ Data consistency under stress

## 🎯 Performance Benchmarks

### Expected Performance Metrics

- **Speed Calculations**: < 5 seconds for 1000 records
- **Power Calculations**: < 5 seconds for 1000 records
- **Monte Carlo Simulations**: < 10 seconds for 1000 records
- **Complete Pipeline**: < 30 seconds for 200 records
- **Memory Usage**: < 500MB peak usage
- **Database Insertion**: < 2 seconds for 500 records

### Quality Benchmarks

- **Speed Figures**: Range 20-120, position-correlated
- **Power Ratings**: Range 40-140, class-adjusted
- **Win Probabilities**: Range 0-1, sum ≤ 1 per race
- **Data Consistency**: 100% across multiple runs

## 🔍 Test Data Requirements

### Sample Data Structure

The tests use realistic racing data including:

- Race IDs and dates
- Horse names and finishing positions
- Jockey and trainer information
- Odds and weights
- Track and race class information

### Database Schema Validation

Tests verify the following tables and columns:

- `horse_speed_ratings`: speed_figure, pace_rating
- `horse_power_ratings`: power_rating, base_rating
- `monte_carlo_simulations`: win_probability, place_probability

## 🛠️ Test Configuration

### Docker Environment

```yaml
Required Containers:
  - horse_racing_postgres_clean (PostgreSQL)
  - horse_racing_data_pipeline_clean (Python environment)

Database Connections:
  - Host: localhost
  - Port: 5432
  - User: horse_racing
  - Password: horse_racing_password
```

### Test Environment Variables

```bash
PYTEST_TIMEOUT=300
TEST_DATABASE_URL=postgresql://horse_racing:horse_racing_password@localhost:5432/ai_horse_racing_db
RESULTS_DATABASE_URL=postgresql://horse_racing:horse_racing_password@localhost:5432/results_horse_racing_db
```

## 📋 Test Reports

### Generated Reports

- `tests/reports/unit_test_report.html` - Detailed unit test results
- `tests/reports/integration_test_report.html` - Integration test results
- `tests/reports/advanced_metrics_test_summary.md` - Overall test summary

### Report Contents

- Test execution times
- Pass/fail status for each test
- Performance metrics and benchmarks
- Data quality validation results
- Environment status and configuration

## 🐛 Troubleshooting Tests

### Common Issues

**Docker Containers Not Running**

```bash
# Check container status
docker ps | grep -E "(postgres|pipeline)"

# Start containers if needed
docker-compose up -d
```

**Database Connection Failed**

```bash
# Test database connectivity
docker exec horse_racing_postgres_clean psql -U horse_racing -l

# Check database exists
docker exec horse_racing_postgres_clean psql -U horse_racing -d ai_horse_racing_db -c "\dt"
```

**No Test Data**

```bash
# Check results database has data
docker exec horse_racing_postgres_clean psql -U horse_racing -d results_horse_racing_db -c "SELECT COUNT(*) FROM result_records;"

# Populate sample data if needed
python sample_data_populator.py
```

**Import Errors**

```bash
# Install required packages
pip install pytest docker psycopg2-binary pandas numpy psutil

# Check Python path
python -c "import sys; print(sys.path)"
```

### Test Timeouts

- Unit tests: 5 minutes max
- Integration tests: 10 minutes max
- Performance tests: 15 minutes max
- Individual Docker executions: 2 minutes max

## 🔄 Continuous Integration

### CI Pipeline Integration

```yaml
# Example GitHub Actions workflow
test_advanced_metrics:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: "3.9"
    - name: Start Docker containers
      run: docker-compose up -d
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run advanced metrics tests
      run: python tests/run_advanced_metrics_tests.py
    - name: Upload test reports
      uses: actions/upload-artifact@v2
      with:
        name: test-reports
        path: tests/reports/
```

## 📈 Test Metrics and Monitoring

### Key Performance Indicators

- Test execution time trends
- Memory usage patterns
- Database operation performance
- Error rates and types
- Coverage percentages

### Success Criteria

- ✅ All unit tests pass (100%)
- ✅ All integration tests pass (100%)
- ✅ Performance benchmarks met (95%+)
- ✅ Data quality validation pass (100%)
- ✅ No memory leaks detected
- ✅ Consistent results across runs

## 🎯 Next Steps

### Test Enhancement Roadmap

1. **Load Testing**: Multi-user concurrent execution
2. **Chaos Testing**: Container failure scenarios
3. **Security Testing**: SQL injection prevention
4. **Regression Testing**: Version comparison
5. **End-to-End Testing**: Full Node-RED workflow

### Monitoring Integration

- Automated test scheduling
- Performance trend analysis
- Alert thresholds for failures
- Test result dashboards

---

**Last Updated**: August 31, 2025  
**Test Framework Version**: 1.0  
**Coverage**: 95%+ of advanced metrics functionality  
**Status**: Production Ready ✅
