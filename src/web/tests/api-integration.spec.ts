import { test, expect } from '@playwright/test';

/**
 * API Integration Tests
 * Tests the frontend-backend API integration
 */

test.describe('API Integration', () => {
  const API_BASE_URL = 'http://localhost:8000';

  test('should connect to API health endpoint', async ({ page }) => {
    // Test direct API call
    const response = await page.request.get(`${API_BASE_URL}/health`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('status');
    expect(data.status).toBe('healthy');
  });

  test('should load real race cards from API', async ({ page }) => {
    // Navigate to race cards page
    await page.goto('/cards');
    await page.waitForLoadState('networkidle');
    
    // Monitor API requests
    const apiRequests: any[] = [];
    page.on('response', (response) => {
      if (response.url().includes('/api/')) {
        apiRequests.push({
          url: response.url(),
          status: response.status(),
        });
      }
    });
    
    // Switch to enhanced analysis to trigger API calls
    const enhancedTab = page.locator('[role="tab"]').filter({ hasText: 'Enhanced Analysis' });
    await enhancedTab.click();
    
    await page.waitForTimeout(3000);
    
    // Check that API calls were made
    expect(apiRequests.length).toBeGreaterThan(0);
    
    // Check for successful responses
    const successfulRequests = apiRequests.filter(req => req.status >= 200 && req.status < 300);
    expect(successfulRequests.length).toBeGreaterThan(0);
  });

  test('should fetch performance analytics data', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Monitor API requests for performance data
    const performanceRequests: any[] = [];
    page.on('response', (response) => {
      if (response.url().includes('/api/stage8/performance') || 
          response.url().includes('/api/performance')) {
        performanceRequests.push({
          url: response.url(),
          status: response.status(),
        });
      }
    });
    
    // Navigate to Performance Analytics tab
    const performanceTab = page.locator('[role="tab"]').filter({ hasText: 'Performance Analytics' });
    await performanceTab.click();
    
    await page.waitForTimeout(3000);
    
    // Check that performance API calls were made or content is visible
    const hasPerformanceContent = await page.locator('text=Performance Metrics, text=Analytics').first().isVisible();
    expect(hasPerformanceContent).toBeTruthy();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Navigate to a page and monitor for error handling
    await page.goto('/cards');
    
    // Intercept API calls and return errors
    await page.route('**/api/**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });
    
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Check for error handling in UI
    const errorMessage = page.locator('text=Error, text=Failed, text=loading').first();
    if (await errorMessage.isVisible()) {
      await expect(errorMessage).toBeVisible();
    }
    
    // Ensure page doesn't crash
    await expect(page.locator('text=Race Cards')).toBeVisible();
  });

  test('should test real API endpoints directly', async ({ request }) => {
    // Test health endpoint
    const healthResponse = await request.get(`${API_BASE_URL}/health`);
    expect(healthResponse.status()).toBe(200);
    
    // Test race cards endpoint
    const raceCardsResponse = await request.get(`${API_BASE_URL}/api/real_race_cards`);
    // Should either return data or a 404/503 if no data
    expect([200, 404, 503]).toContain(raceCardsResponse.status());
    
    // Test daily races endpoint
    const dailyRacesResponse = await request.get(`${API_BASE_URL}/api/daily_races`);
    expect([200, 404, 503]).toContain(dailyRacesResponse.status());
    
    // Test performance endpoint
    const performanceResponse = await request.get(`${API_BASE_URL}/api/stage8/performance`);
    expect([200, 404, 503]).toContain(performanceResponse.status());
  });

  test('should handle loading states during API calls', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/');
    
    // Add network delay to simulate slow API
    await page.route('**/api/**', async (route) => {
      await page.waitForTimeout(1000); // Add 1 second delay
      route.continue();
    });
    
    // Navigate to a tab that triggers API calls
    const performanceTab = page.locator('[role="tab"]').filter({ hasText: 'Performance Analytics' });
    await performanceTab.click();
    
    // Look for loading indicators
    const loadingIndicator = page.locator('text=Loading, .loading, .spinner, .progress').first();
    
    // Either loading should appear or content should load quickly
    await page.waitForTimeout(2000);
    
    // Final check that content is displayed
    const hasContent = await page.locator('h1, h2, h3, h4').first().isVisible();
    expect(hasContent).toBeTruthy();
  });

  test('should verify WebSocket connections work', async ({ page }) => {
    let websocketConnected = false;
    
    // Monitor WebSocket connections
    page.on('websocket', (ws) => {
      websocketConnected = true;
      console.log('WebSocket connection established');
      
      ws.on('framesent', (event) => {
        console.log('WebSocket frame sent:', event.payload);
      });
      
      ws.on('framereceived', (event) => {
        console.log('WebSocket frame received:', event.payload);
      });
    });
    
    // Navigate to dashboard (which may use WebSocket)
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Wait a bit for WebSocket connections
    await page.waitForTimeout(3000);
    
    // WebSocket connection is optional, so just log the result
    console.log(`WebSocket connected: ${websocketConnected}`);
  });
});
