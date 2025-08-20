# 🧪 Comprehensive Testing Suite for Horse Racing AI v2.03

This directory contains a complete testing framework for both the frontend (React/TypeScript) and backend (FastAPI/Python) components of the Horse Racing AI application.

## 📋 Test Coverage

### Frontend Tests (Playwright)

- **Dashboard Component Tests** - Navigation, tabs, responsive design
- **Race Cards Tests** - Enhanced analysis, comparison mode, horse details
- **API Integration Tests** - Frontend-backend communication, error handling
- **End-to-End Tests** - Complete user journeys, cross-browser compatibility
- **Performance Tests** - Loading times, network conditions
- **Accessibility Tests** - Keyboard navigation, screen reader compatibility

### Backend Tests (pytest)

- **API Endpoint Tests** - All REST endpoints, validation, responses
- **Performance Tests** - Response times, concurrent requests, load testing
- **Security Tests** - CORS, headers, error handling, rate limiting
- **Data Validation Tests** - Input validation, data integrity
- **Integration Tests** - Database connectivity, ML model serving

## 🚀 Quick Start

### Run All Tests

```bash
# Run complete test suite (frontend + backend)
./run_tests.sh

# Run only backend tests
./run_tests.sh backend

# Run only frontend tests
./run_tests.sh frontend
```

### Frontend Tests Only

```bash
cd src/web

# Run all Playwright tests
npm run test

# Run tests with UI mode
npm run test:ui

# Run tests in headed mode (see browser)
npm run test:headed

# Debug specific test
npm run test:debug

# Generate test code
npm run test:codegen
```

### Backend Tests Only

```bash
# Run comprehensive backend tests
python run_backend_tests.py

# Run specific test categories
python -m pytest tests/test_api_comprehensive.py::TestAPIEndpoints -v
python -m pytest tests/test_api_comprehensive.py::TestPerformanceEndpoints -v
python -m pytest tests/test_api_comprehensive.py::TestSecurity -v
```

## 📊 Test Reports

After running tests, comprehensive reports are generated:

### Frontend Reports

- **HTML Report**: `src/web/playwright-report/index.html`
- **Screenshots**: `src/web/test-results/`
- **Videos**: `src/web/test-results/videos/`

### Backend Reports

- **HTML Report**: `test-results/backend-test-report.html`
- **JSON Data**: `test-results/backend-test-results.json`
- **Performance Metrics**: Included in HTML report

### Combined Report

- **Overview**: `test-results/combined-test-report.html`

## 🔧 Test Configuration

### Playwright Configuration

File: `src/web/playwright.config.ts`

- **Browsers**: Chrome, Firefox, Safari, Mobile Chrome, Mobile Safari
- **Viewport**: Desktop (1920x1080), Mobile (375x667), Tablet (768x1024)
- **Test Timeout**: 30 seconds
- **Expect Timeout**: 10 seconds
- **Retries**: 2 on failure
- **Video**: Record on failure
- **Screenshots**: Capture on failure

### Backend Test Configuration

- **API Base URL**: http://localhost:8000
- **Frontend URL**: http://localhost:5003
- **Timeout**: 30 seconds for server startup
- **Concurrent Tests**: Up to 10 parallel requests
- **Performance Thresholds**: <1 second response time

## 🏗️ Test Structure

```
src/web/tests/
├── dashboard.spec.ts           # Dashboard component tests
├── race-cards.spec.ts          # Race cards functionality tests
├── api-integration.spec.ts     # Frontend-backend integration
├── e2e.spec.ts                 # End-to-end user journeys
├── test-utils.ts               # Shared test utilities
├── global-setup.ts             # Test environment setup
└── global-teardown.ts          # Test cleanup

tests/
├── test_api_comprehensive.py   # Complete backend API tests
├── playwright/                 # Legacy Playwright tests
└── integration/                # Integration test suite

root/
├── run_tests.sh                # Master test runner script
├── run_backend_tests.py        # Backend-specific test runner
└── test-results/               # Generated test reports
```

## 🎯 Test Scenarios

### Critical User Journeys

1. **Dashboard Exploration**

   - Load dashboard → Navigate tabs → View analytics → Verify responsiveness

2. **Race Analysis Workflow**

   - View race cards → Enable comparison → Select horses → View details → Check AI predictions

3. **API Integration**

   - Frontend data loading → API error handling → Real-time updates → Performance validation

4. **Cross-Browser Compatibility**
   - Chrome, Firefox, Safari → Desktop, tablet, mobile → All core features

### Performance Benchmarks

- **Page Load**: <2 seconds
- **API Response**: <200ms for 95% of requests
- **Chart Rendering**: <500ms
- **Mobile Performance**: Smooth 60fps interactions

### Security Validation

- **CORS Headers**: Properly configured
- **Input Validation**: SQL injection prevention
- **Error Handling**: No sensitive data exposure
- **Rate Limiting**: Protection against abuse

## 🔍 Debugging Tests

### Frontend Debugging

```bash
# Debug mode with DevTools
npm run test:debug

# Run specific test file
npx playwright test dashboard.spec.ts --debug

# Generate code from interactions
npm run test:codegen http://localhost:5003
```

### Backend Debugging

```bash
# Verbose output
python -m pytest tests/test_api_comprehensive.py -v -s

# Run specific test
python -m pytest tests/test_api_comprehensive.py::TestAPIEndpoints::test_health_endpoint -v

# Print debug info
python run_backend_tests.py --verbose
```

### Common Issues & Solutions

1. **Server Not Running**

   ```bash
   # Start API server manually
   cd api && python prediction_api.py

   # Start frontend manually
   cd src/web && npm run dev
   ```

2. **Port Conflicts**

   - API Server: http://localhost:8000
   - Frontend: http://localhost:5003
   - Check for processes using these ports

3. **Browser Installation**

   ```bash
   cd src/web
   npx playwright install chromium
   ```

4. **Dependencies Missing**

   ```bash
   # Frontend dependencies
   cd src/web && npm install

   # Backend dependencies
   pip install requests pytest playwright
   ```

## 📈 CI/CD Integration

The test suite is designed for easy integration with CI/CD pipelines:

### GitHub Actions Example

```yaml
- name: Run Frontend Tests
  run: |
    cd src/web
    npm ci
    npx playwright install --with-deps
    npm run test

- name: Run Backend Tests
  run: |
    pip install -r requirements.txt
    python run_backend_tests.py
```

### Test Results Artifacts

- HTML reports for easy viewing
- JSON data for programmatic analysis
- Screenshots and videos for failure investigation
- Performance metrics for monitoring

## 🎨 Test Customization

### Adding New Frontend Tests

1. Create new `.spec.ts` file in `src/web/tests/`
2. Import test utilities: `import { TestUtils } from './test-utils';`
3. Follow existing patterns for page objects and assertions

### Adding New Backend Tests

1. Add test methods to `tests/test_api_comprehensive.py`
2. Use existing test classes or create new ones
3. Follow pytest conventions and naming

### Custom Test Configuration

- Modify `playwright.config.ts` for browser settings
- Update `run_backend_tests.py` for API test parameters
- Adjust timeouts and retries as needed

## 📚 Additional Resources

- [Playwright Documentation](https://playwright.dev/docs/intro)
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [React Testing Best Practices](https://testing-library.com/docs/react-testing-library/intro/)

---

**🎯 Goal**: Ensure 100% reliability and performance of the Horse Racing AI application across all browsers, devices, and scenarios through comprehensive automated testing.
