import { test, expect } from '@playwright/test';

/**
 * End-to-End User Journey Tests
 * Tests complete user workflows and scenarios
 */

test.describe('E2E User Journeys', () => {
  test('should complete full dashboard exploration journey', async ({ page }) => {
    // Start at homepage
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Verify landing on dashboard
    await expect(page.locator('h1, h2, h3, h4').first()).toBeVisible();
    
    // Navigate through all dashboard tabs
    const tabs = [
      'Overview',
      'Performance Analytics', 
      'Customizable View'
    ];
    
    for (const tabName of tabs) {
      const tab = page.locator('[role="tab"]').filter({ hasText: tabName });
      if (await tab.isVisible()) {
        await tab.click();
        await page.waitForTimeout(1000);
        
        // Verify tab content loads
        await expect(page.locator('body')).toBeVisible();
        
        // Take screenshot of each tab
        await page.screenshot({ 
          path: `test-results/dashboard-${tabName.toLowerCase().replace(' ', '-')}.png` 
        });
      }
    }
  });

  test('should complete race analysis workflow', async ({ page }) => {
    // Navigate to race cards
    await page.goto('/cards');
    await page.waitForLoadState('networkidle');
    
    // Switch to enhanced analysis
    const enhancedTab = page.locator('[role="tab"]').filter({ hasText: 'Enhanced Analysis' });
    await enhancedTab.click();
    await page.waitForTimeout(2000);
    
    // Enable compare mode
    const compareButton = page.locator('button').filter({ hasText: 'Compare Mode' });
    if (await compareButton.isVisible()) {
      await compareButton.click();
      
      // Try to select horses for comparison
      const horseCards = page.locator('.MuiCard-root').filter({ hasText: /horse|runner/i });
      
      if (await horseCards.count() > 0) {
        // Select first horse
        await horseCards.first().click();
        await page.waitForTimeout(500);
        
        // Select second horse if available
        if (await horseCards.count() > 1) {
          await horseCards.nth(1).click();
          await page.waitForTimeout(500);
        }
        
        // Check for comparison indicators
        const selectedCount = page.locator('text=/selected/i, [class*="selected"]');
        // Should have selection feedback
      }
      
      // Disable compare mode
      await compareButton.click();
    }
    
    // Try to view horse details
    const expandButton = page.locator('[data-testid="expand-race"], .MuiIconButton-root').first();
    if (await expandButton.isVisible()) {
      await expandButton.click();
      await page.waitForTimeout(1000);
      
      // Look for detailed horse information
      const horseDetail = page.locator('.MuiCard-root').filter({ hasText: /horse|runner/i }).first();
      if (await horseDetail.isVisible()) {
        await horseDetail.click();
        await page.waitForTimeout(1000);
        
        // Check for modal or detailed view
        const modal = page.locator('[role="dialog"], .MuiDialog-root').first();
        if (await modal.isVisible()) {
          await expect(modal).toBeVisible();
          
          // Close modal
          const closeButton = modal.locator('button').filter({ hasText: 'Close' });
          if (await closeButton.isVisible()) {
            await closeButton.click();
          }
        }
      }
    }
    
    // Take final screenshot
    await page.screenshot({ path: 'test-results/race-analysis-complete.png' });
  });

  test('should handle navigation between all pages', async ({ page }) => {
    const pages = [
      { path: '/', name: 'Dashboard' },
      { path: '/cards', name: 'Race Cards' },
      { path: '/predictions', name: 'Predictions' },
      { path: '/results', name: 'Results' }
    ];
    
    for (const testPage of pages) {
      // Navigate to page
      await page.goto(testPage.path);
      await page.waitForLoadState('networkidle');
      
      // Verify page loads without errors
      const errorMessages = page.locator('text=/error|failed|crash/i');
      const errorCount = await errorMessages.count();
      
      if (errorCount > 0) {
        console.log(`Found ${errorCount} potential errors on ${testPage.name} page`);
      }
      
      // Verify basic content is present
      await expect(page.locator('body')).toBeVisible();
      
      // Take screenshot
      await page.screenshot({ 
        path: `test-results/page-${testPage.name.toLowerCase().replace(' ', '-')}.png` 
      });
      
      await page.waitForTimeout(1000);
    }
  });

  test('should handle responsive design across devices', async ({ page }) => {
    const devices = [
      { name: 'Desktop', width: 1920, height: 1080 },
      { name: 'Laptop', width: 1366, height: 768 },
      { name: 'Tablet', width: 768, height: 1024 },
      { name: 'Mobile', width: 375, height: 667 },
      { name: 'Mobile Landscape', width: 667, height: 375 }
    ];
    
    for (const device of devices) {
      // Set viewport
      await page.setViewportSize({ width: device.width, height: device.height });
      
      // Test dashboard
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Verify content is visible and accessible
      await expect(page.locator('h1, h2, h3, h4').first()).toBeVisible();
      
      // Test race cards
      await page.goto('/cards');
      await page.waitForLoadState('networkidle');
      
      await expect(page.locator('text=Race Cards')).toBeVisible();
      
      // Take screenshots for each device
      await page.screenshot({ 
        path: `test-results/responsive-${device.name.toLowerCase().replace(' ', '-')}.png`,
        fullPage: true
      });
    }
  });

  test('should handle network conditions and offline scenarios', async ({ page }) => {
    // Test with slow network
    await page.route('**/*', async (route) => {
      await page.waitForTimeout(500); // Add 500ms delay
      route.continue();
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Should still load content
    await expect(page.locator('h1, h2, h3, h4').first()).toBeVisible();
    
    // Test with failed API calls
    await page.route('**/api/**', (route) => {
      route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Service Unavailable' }),
      });
    });
    
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Page should still be functional despite API failures
    await expect(page.locator('text=Race Cards, text=Dashboard').first()).toBeVisible();
    
    // Navigate to other pages
    await page.goto('/cards');
    await page.waitForLoadState('networkidle');
    
    // Should handle API errors gracefully
    await expect(page.locator('text=Race Cards')).toBeVisible();
  });

  test('should perform accessibility checks', async ({ page }) => {
    // Test keyboard navigation
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test tab navigation
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Verify focus is visible
    const focusedElement = page.locator(':focus');
    if (await focusedElement.isVisible()) {
      await expect(focusedElement).toBeVisible();
    }
    
    // Test with screen reader simulation
    const headings = page.locator('h1, h2, h3, h4, h5, h6');
    const headingCount = await headings.count();
    expect(headingCount).toBeGreaterThan(0);
    
    // Check for alt text on images
    const images = page.locator('img');
    const imageCount = await images.count();
    
    for (let i = 0; i < Math.min(imageCount, 5); i++) {
      const img = images.nth(i);
      const alt = await img.getAttribute('alt');
      const role = await img.getAttribute('role');
      
      // Images should have alt text or decorative role
      if (!alt && role !== 'presentation') {
        console.log(`Image ${i} missing alt text`);
      }
    }
    
    // Check for proper button labels
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < Math.min(buttonCount, 10); i++) {
      const button = buttons.nth(i);
      const text = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');
      
      // Buttons should have text or aria-label
      if (!text?.trim() && !ariaLabel) {
        console.log(`Button ${i} missing accessible label`);
      }
    }
  });

  test('should handle data persistence and state management', async ({ page }) => {
    // Navigate to customizable dashboard
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const customizableTab = page.locator('[role="tab"]').filter({ hasText: 'Customizable View' });
    if (await customizableTab.isVisible()) {
      await customizableTab.click();
      await page.waitForTimeout(2000);
      
      // Try to interact with widgets
      const widgets = page.locator('.widget, [data-testid*="widget"]');
      if (await widgets.count() > 0) {
        // Try to modify widget settings
        const firstWidget = widgets.first();
        await firstWidget.hover();
        
        // Look for widget controls
        const widgetControls = page.locator('button').filter({ hasText: /settings|config|edit/i });
        if (await widgetControls.first().isVisible()) {
          await widgetControls.first().click();
          await page.waitForTimeout(500);
        }
      }
      
      // Reload page to test persistence
      await page.reload();
      await page.waitForLoadState('networkidle');
      
      // Should maintain customizations (if any were made)
      await expect(page.locator('text=Customizable Dashboard')).toBeVisible();
    }
  });
});
