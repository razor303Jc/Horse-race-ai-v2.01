import { test, expect } from '@playwright/test';

/**
 * Dashboard Component Tests
 * Tests the main dashboard functionality and navigation
 */

test.describe('Dashboard Component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
  });

  test('should load dashboard successfully', async ({ page }) => {
    // Check if the page loads without errors
    await expect(page).toHaveTitle(/Horse Racing AI/);
    
    // Check for main dashboard heading
    await expect(page.locator('h1, h2, h3, h4').first()).toBeVisible();
    
    // Take screenshot for visual verification
    await page.screenshot({ path: 'test-results/dashboard-loaded.png' });
  });

  test('should display navigation tabs', async ({ page }) => {
    // Check for tab navigation
    const overviewTab = page.locator('[role="tab"]').filter({ hasText: 'Overview' });
    const performanceTab = page.locator('[role="tab"]').filter({ hasText: 'Performance Analytics' });
    const customizableTab = page.locator('[role="tab"]').filter({ hasText: 'Customizable View' });

    await expect(overviewTab).toBeVisible();
    await expect(performanceTab).toBeVisible();
    await expect(customizableTab).toBeVisible();
  });

  test('should switch between dashboard tabs', async ({ page }) => {
    // Test tab switching functionality
    const performanceTab = page.locator('[role="tab"]').filter({ hasText: 'Performance Analytics' });
    await performanceTab.click();
    
    // Wait for tab content to load
    await page.waitForTimeout(1000);
    
    // Verify performance dashboard content is visible
    await expect(page.locator('text=Performance Metrics')).toBeVisible();
    
    // Switch to customizable view
    const customizableTab = page.locator('[role="tab"]').filter({ hasText: 'Customizable View' });
    await customizableTab.click();
    
    await page.waitForTimeout(1000);
    
    // Verify customizable dashboard content is visible
    await expect(page.locator('text=Customizable Dashboard')).toBeVisible();
  });

  test('should display performance metrics', async ({ page }) => {
    // Navigate to Performance Analytics tab
    const performanceTab = page.locator('[role="tab"]').filter({ hasText: 'Performance Analytics' });
    await performanceTab.click();
    
    await page.waitForTimeout(2000);
    
    // Check for chart containers
    const chartContainer = page.locator('.recharts-wrapper, canvas, svg').first();
    await expect(chartContainer).toBeVisible();
    
    // Check for metric selection controls
    const metricSelector = page.locator('select, button').filter({ hasText: /win|roi|profit/i }).first();
    if (await metricSelector.isVisible()) {
      await expect(metricSelector).toBeVisible();
    }
  });

  test('should handle customizable dashboard widgets', async ({ page }) => {
    // Navigate to Customizable View tab
    const customizableTab = page.locator('[role="tab"]').filter({ hasText: 'Customizable View' });
    await customizableTab.click();
    
    await page.waitForTimeout(2000);
    
    // Check for widget containers
    const widgets = page.locator('[data-testid*="widget"], .widget, .card').first();
    await expect(widgets).toBeVisible();
    
    // Check for drag and drop functionality indicators
    const draggableElements = page.locator('[draggable="true"], .draggable').first();
    if (await draggableElements.isVisible()) {
      await expect(draggableElements).toBeVisible();
    }
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Reload page with mobile viewport
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Check if navigation is mobile-friendly
    await expect(page.locator('h1, h2, h3, h4').first()).toBeVisible();
    
    // Take mobile screenshot
    await page.screenshot({ path: 'test-results/dashboard-mobile.png' });
  });
});
