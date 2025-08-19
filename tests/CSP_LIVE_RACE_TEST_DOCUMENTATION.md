# CSP Configuration and Live Race Tracking Test Suite

## Overview

This test suite comprehensively validates the Content Security Policy (CSP) configuration and live race tracking features implemented in Horse Racing AI v2.03.

## Test Structure

### 1. Playwright End-to-End Tests

#### CSP Configuration Tests (`test_csp_configuration.py`)

- **CSP Meta Tag Validation**: Ensures CSP meta tag exists and has proper content
- **Development Mode Compatibility**: Validates CSP allows necessary permissions for Vite HMR
- **JavaScript Execution**: Tests that JavaScript executes without CSP violations
- **Vite HMR Compatibility**: Ensures Hot Module Replacement works with CSP
- **WebSocket Permissions**: Validates WebSocket connections are allowed
- **Security Directives**: Tests all required CSP directives are present
- **Production vs Development**: Documents CSP differences between environments

#### Live Race Tracking Tests (`test_live_race_tracking.py`)

- **Component Loading**: Tests LiveRaceTracker and RaceSelection components load
- **WebSocket Functionality**: Validates WebSocket connection capabilities
- **API Service Integration**: Tests useApiService hook functionality
- **Real-time Updates**: Simulates and tests live race update mechanisms
- **Error Handling**: Tests WebSocket error handling and reconnection logic
- **Performance Monitoring**: Validates integration with performance metrics
- **Responsive Design**: Tests race tracking across different viewport sizes
- **Accessibility**: Validates accessibility features for race tracking components

### 2. Unit Tests

#### CSP Utility Tests (`test_csp_live_race_units.py`)

- **File Existence**: Validates all CSP utility files exist
- **Configuration Logic**: Tests development vs production CSP logic
- **Documentation**: Ensures CSP configuration documentation exists
- **TypeScript Integration**: Validates TypeScript compilation and typing
- **Vite Configuration**: Tests Vite config for CSP compatibility
- **HTML Structure**: Validates index.html CSP meta tag implementation

### 3. Test Execution

#### Comprehensive Test Runner (`run_csp_live_race_tests.py`)

- Executes all test suites in sequence
- Generates detailed JSON reports for each suite
- Creates comprehensive summary report
- Provides success rate analysis
- Saves execution logs and screenshots

## Running the Tests

### Prerequisites

```bash
# Ensure the application is running
cd /home/jc/Documents/Horse-race-ai-v2.03
# Start the application on localhost:5002
```

### Execute All Tests

```bash
# Run comprehensive test suite
python tests/run_csp_live_race_tests.py

# Run individual test suites
pytest tests/playwright/test_csp_configuration.py -v
pytest tests/playwright/test_live_race_tracking.py -v
pytest tests/unit/test_csp_live_race_units.py -v
```

### Generate Reports

Tests automatically generate reports in:

- `tests/playwright/reports/csp_configuration_report.json`
- `tests/playwright/reports/live_race_tracking_report.json`
- `tests/playwright/reports/comprehensive_test_summary.json`

## Test Coverage

### CSP Configuration Coverage

✅ **Meta Tag Implementation**

- CSP meta tag exists in index.html
- Correct http-equiv attribute
- Proper content directive formatting

✅ **Development Environment**

- Allows 'unsafe-eval' for Vite HMR
- Permits 'unsafe-inline' for development styles
- Supports data: and blob: URIs
- WebSocket connections allowed

✅ **Security Directives**

- default-src properly configured
- script-src includes necessary permissions
- style-src allows required sources
- img-src supports various image sources
- connect-src permits API and WebSocket connections
- font-src configured for web fonts

✅ **Vite Integration**

- No CSP violations during JavaScript execution
- Hot Module Replacement compatibility
- Inline sourcemaps work with CSP
- Dynamic script loading permitted in development

### Live Race Tracking Coverage

✅ **Component Architecture**

- LiveRaceTracker component structure
- RaceSelection component functionality
- Integration with main dashboard
- Responsive design across viewports

✅ **WebSocket Implementation**

- WebSocket connection establishment
- Real-time message handling
- Error handling and reconnection logic
- Connection state management

✅ **API Integration**

- useApiService hook functionality
- REST API endpoint integration
- Data fetching and state management
- Error boundary implementation

✅ **User Experience**

- Loading states and indicators
- Error handling and user feedback
- Accessibility features
- Performance optimization

## Key Test Scenarios

### 1. CSP Violation Prevention

- Tests ensure no CSP violations occur during normal operation
- Validates development mode permissions don't break functionality
- Confirms production readiness with stricter CSP policies

### 2. WebSocket Connectivity

- Tests WebSocket connection establishment
- Validates message handling and data flow
- Ensures error recovery and reconnection mechanisms

### 3. Real-time Updates

- Simulates live race data updates
- Tests UI responsiveness to data changes
- Validates state management during updates

### 4. Cross-browser Compatibility

- Tests across different viewport sizes
- Validates responsive design principles
- Ensures accessibility standards compliance

## Expected Outcomes

### Success Criteria

- **CSP Tests**: All tests pass with 0 CSP violations
- **Live Race Tests**: Components load and function correctly
- **Unit Tests**: All utility functions and configurations validated
- **Integration Tests**: Seamless interaction between components

### Performance Benchmarks

- Test execution time: < 60 seconds for full suite
- No memory leaks during WebSocket operations
- Responsive UI updates within 100ms of data changes
- CSP evaluation overhead: < 5ms per page load

## Troubleshooting

### Common Issues

1. **CSP Violations in Development**

   - Check Vite configuration for inline sourcemaps
   - Verify meta tag includes 'unsafe-eval' in development

2. **WebSocket Connection Failures**

   - Ensure WebSocket server is running
   - Check CSP allows ws: or wss: connections
   - Verify firewall and network connectivity

3. **Component Loading Issues**
   - Check React component import paths
   - Verify TypeScript compilation success
   - Ensure all dependencies are installed

### Debug Mode

```bash
# Run tests with debug output
pytest tests/playwright/test_csp_configuration.py -v -s --tb=long

# Generate detailed browser logs
pytest tests/playwright/test_live_race_tracking.py --headed --slowmo=1000
```

## Maintenance

### Regular Maintenance Tasks

- Update CSP policies when adding new external resources
- Review WebSocket connection stability metrics
- Monitor test execution performance
- Update test scenarios for new features

### CSP Policy Updates

When updating CSP policies:

1. Test in development environment first
2. Validate no functionality is broken
3. Update production deployment documentation
4. Run full test suite to ensure compatibility

### Component Updates

When modifying live race tracking components:

1. Update corresponding test cases
2. Verify WebSocket integration still works
3. Test responsive design changes
4. Validate accessibility requirements

## Reporting Issues

### Test Failures

- Include full test output and error messages
- Provide browser console logs if applicable
- Document steps to reproduce the issue
- Include environment information (browser, OS, etc.)

### Performance Issues

- Include timing information from test reports
- Document specific scenarios where performance degrades
- Provide network and system resource usage data
- Include before/after comparisons when possible

---

_This test suite ensures the robust implementation of CSP security measures and live race tracking functionality in Horse Racing AI v2.03._
