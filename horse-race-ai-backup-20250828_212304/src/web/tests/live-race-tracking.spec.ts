import { test, expect } from '@playwright/test';
import { TestUtils } from './test-utils';

test.describe('Live Race Tracking', () => {
  let testUtils: TestUtils;

  test.beforeEach(async ({ page }) => {
    testUtils = new TestUtils(page);
    await page.goto('/live-racing');
  });

  test('should display race selection interface', async ({ page }) => {
    // Check for main heading
    await expect(page.locator('h4')).toContainText('Live Race Tracking');
    
    // Check for search and filter controls
    await expect(page.locator('input[placeholder*="Search races"]')).toBeVisible();
    await expect(page.locator('label')).toContainText('Status');
    await expect(page.locator('label')).toContainText('Track');
  });

  test('should filter races by search term', async ({ page }) => {
    // Wait for races to load
    await page.waitForSelector('[data-testid="race-card"]', { timeout: 10000 });
    
    // Search for a specific race
    await page.fill('input[placeholder*="Search races"]', 'Stakes');
    
    // Check that search filters the results
    const raceCards = page.locator('[data-testid="race-card"]');
    await expect(raceCards.first()).toBeVisible();
    
    // Verify search term appears in visible races
    const firstRaceTitle = await raceCards.first().locator('h6').textContent();
    expect(firstRaceTitle?.toLowerCase()).toContain('stakes');
  });

  test('should filter races by status', async ({ page }) => {
    // Wait for races to load
    await page.waitForSelector('[data-testid="race-card"]', { timeout: 10000 });
    
    // Select "Running" status filter
    await page.click('text=Status');
    await page.click('text=Running');
    
    // Check that only running races are shown
    const statusChips = page.locator('.MuiChip-label');
    await expect(statusChips.first()).toContainText('RUNNING');
  });

  test('should open live race tracker when clicking on a race', async ({ page }) => {
    // Wait for races to load
    await page.waitForSelector('[data-testid="race-card"]', { timeout: 10000 });
    
    // Click on the first race's "Watch Live" button
    await page.click('button:has-text("Watch Live"), button:has-text("View Race")');
    
    // Check that dialog opens with race tracker
    await expect(page.locator('text=Live Race Tracking')).toBeVisible();
    await expect(page.locator('text=Close')).toBeVisible();
  });

  test('should display race information in cards', async ({ page }) => {
    // Wait for races to load
    await page.waitForSelector('[data-testid="race-card"]', { timeout: 10000 });
    
    const firstCard = page.locator('[data-testid="race-card"]').first();
    
    // Check for essential race information
    await expect(firstCard.locator('h6')).toBeVisible(); // Race name
    await expect(firstCard.locator('text=Distance')).toBeVisible();
    await expect(firstCard.locator('text=Runners')).toBeVisible();
    await expect(firstCard.locator('text=Going')).toBeVisible();
    await expect(firstCard.locator('text=Grade')).toBeVisible();
  });

  test('should show live indicator for live races', async ({ page }) => {
    // Wait for races to load
    await page.waitForSelector('[data-testid="race-card"]', { timeout: 10000 });
    
    // Look for live races
    const liveRaces = page.locator('[data-testid="race-card"]:has-text("LIVE")');
    
    if (await liveRaces.count() > 0) {
      // Check that live indicator is visible
      await expect(liveRaces.first().locator('text=LIVE')).toBeVisible();
      
      // Check that live races have "Watch Live" button
      await expect(liveRaces.first().locator('button:has-text("Watch Live")')).toBeVisible();
    }
  });

  test('should handle race tracking dialog interactions', async ({ page }) => {
    // Wait for races to load
    await page.waitForSelector('[data-testid="race-card"]', { timeout: 10000 });
    
    // Open race tracker
    await page.click('button:has-text("Watch Live"), button:has-text("View Race")');
    
    // Wait for dialog to open
    await expect(page.locator('text=Live Race Tracking')).toBeVisible();
    
    // Check for race tracker components
    await expect(page.locator('text=Live Positions')).toBeVisible();
    await expect(page.locator('text=Live Commentary')).toBeVisible();
    
    // Close dialog
    await page.click('button:has-text("Close")');
    await expect(page.locator('text=Live Race Tracking')).not.toBeVisible();
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Navigate to live racing page
    await page.goto('/live-racing');
    
    // Check that content is properly displayed on mobile
    await expect(page.locator('h4')).toBeVisible();
    
    // Check that race cards stack vertically on mobile
    const raceCards = page.locator('[data-testid="race-card"]');
    if (await raceCards.count() > 1) {
      const firstCardBox = await raceCards.first().boundingBox();
      const secondCardBox = await raceCards.nth(1).boundingBox();
      
      if (firstCardBox && secondCardBox) {
        // On mobile, cards should stack vertically (second card below first)
        expect(secondCardBox.y).toBeGreaterThan(firstCardBox.y + firstCardBox.height - 50);
      }
    }
  });

  test('should handle no races scenario', async ({ page }) => {
    // Mock empty races response
    await page.route('**/api/races/today', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });
    
    await page.goto('/live-racing');
    
    // Check for empty state message
    await expect(page.locator('text=No races found')).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/races/today', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });
    
    await page.goto('/live-racing');
    
    // Check for error message
    await expect(page.locator('text=Failed to load races')).toBeVisible();
    await expect(page.locator('button:has-text("Retry")')).toBeVisible();
  });

  test('should refresh race data periodically', async ({ page }) => {
    let requestCount = 0;
    
    // Count API requests
    await page.route('**/api/races/today', async (route) => {
      requestCount++;
      await route.continue();
    });
    
    await page.goto('/live-racing');
    
    // Wait for initial load
    await page.waitForSelector('[data-testid="race-card"]', { timeout: 10000 });
    const initialCount = requestCount;
    
    // Wait for automatic refresh (should happen every 30 seconds)
    await page.waitForTimeout(35000);
    
    // Check that additional requests were made
    expect(requestCount).toBeGreaterThan(initialCount);
  });

  test.describe('Live Race Tracker Component', () => {
    test.beforeEach(async ({ page }) => {
      // Navigate to race selection and open a race tracker
      await page.goto('/live-racing');
      await page.waitForSelector('[data-testid="race-card"]', { timeout: 10000 });
      await page.click('button:has-text("Watch Live"), button:has-text("View Race")');
      await expect(page.locator('text=Live Race Tracking')).toBeVisible();
    });

    test('should display race header information', async ({ page }) => {
      // Check for race name and details
      await expect(page.locator('h4')).toBeVisible(); // Race name
      await expect(page.locator('text=going')).toBeVisible(); // Track conditions
      
      // Check for start/stop tracking button
      await expect(page.locator('button:has-text("Start Tracking"), button:has-text("Stop Tracking")')).toBeVisible();
    });

    test('should show horse positions list', async ({ page }) => {
      // Check for positions section
      await expect(page.locator('text=Live Positions')).toBeVisible();
      
      // Look for horse entries (might be empty in test mode)
      const horseList = page.locator('[role="list"]');
      await expect(horseList).toBeVisible();
    });

    test('should display live commentary section', async ({ page }) => {
      // Check for commentary section
      await expect(page.locator('text=Live Commentary')).toBeVisible();
      
      // Check for commentary container
      const commentaryContainer = page.locator('text=Live Commentary').locator('..').locator('[role="textbox"], .MuiPaper-root');
      await expect(commentaryContainer).toBeVisible();
    });

    test('should show connection status', async ({ page }) => {
      // Look for connection status indicator
      const connectionStatus = page.locator('text=Live updates connected, text=Connection lost');
      await expect(connectionStatus).toBeVisible();
    });

    test('should handle race tracking toggle', async ({ page }) => {
      // Find tracking button
      const trackingButton = page.locator('button:has-text("Start Tracking"), button:has-text("Stop Tracking")');
      const initialText = await trackingButton.textContent();
      
      // Click to toggle tracking
      await trackingButton.click();
      
      // Wait for button text to change
      await page.waitForTimeout(1000);
      const newText = await trackingButton.textContent();
      
      // Verify button text changed
      expect(newText).not.toBe(initialText);
    });
  });

  test.describe('WebSocket Integration', () => {
    test('should handle WebSocket connection', async ({ page }) => {
      // Mock WebSocket connection
      await page.addInitScript(() => {
        // Mock WebSocket for testing
        (window as any).WebSocket = class MockWebSocket {
          constructor(url: string) {
            setTimeout(() => {
              if (this.onopen) this.onopen({} as Event);
            }, 100);
          }
          
          onopen: ((event: Event) => void) | null = null;
          onmessage: ((event: MessageEvent) => void) | null = null;
          onclose: ((event: CloseEvent) => void) | null = null;
          onerror: ((event: Event) => void) | null = null;
          
          send(data: string) {
            // Mock sending data
          }
          
          close() {
            if (this.onclose) this.onclose({} as CloseEvent);
          }
        };
      });
      
      await page.goto('/live-racing');
      await page.waitForSelector('[data-testid="race-card"]', { timeout: 10000 });
      await page.click('button:has-text("Watch Live"), button:has-text("View Race")');
      
      // Check that WebSocket connection is established
      await expect(page.locator('text=Live updates connected')).toBeVisible({ timeout: 5000 });
    });
  });
});
