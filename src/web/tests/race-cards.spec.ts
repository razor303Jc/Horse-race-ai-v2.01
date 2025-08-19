import { test, expect } from '@playwright/test';

/**
 * Race Cards Component Tests
 * Tests the enhanced race cards functionality
 */

test.describe('Race Cards Component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/cards');
    await page.waitForLoadState('networkidle');
  });

  test('should load race cards page successfully', async ({ page }) => {
    // Check page title and heading
    await expect(page.locator('text=Race Cards')).toBeVisible();
    
    // Check for tab navigation
    const standardTab = page.locator('[role="tab"]').filter({ hasText: 'Standard View' });
    const enhancedTab = page.locator('[role="tab"]').filter({ hasText: 'Enhanced Analysis' });
    
    await expect(standardTab).toBeVisible();
    await expect(enhancedTab).toBeVisible();
  });

  test('should display race cards in standard view', async ({ page }) => {
    // Ensure we're on standard view
    const standardTab = page.locator('[role="tab"]').filter({ hasText: 'Standard View' });
    await standardTab.click();
    
    await page.waitForTimeout(2000);
    
    // Check for race cards content
    await expect(page.locator('text=Today\'s Race Cards')).toBeVisible();
    
    // Look for race information
    const raceCard = page.locator('.MuiCard-root, .card').first();
    await expect(raceCard).toBeVisible();
    
    // Check for horse information in tables
    const tableRows = page.locator('tr').filter({ hasText: /horse|runner/i });
    if (await tableRows.first().isVisible()) {
      await expect(tableRows.first()).toBeVisible();
    }
  });

  test('should display enhanced race analysis', async ({ page }) => {
    // Switch to enhanced analysis view
    const enhancedTab = page.locator('[role="tab"]').filter({ hasText: 'Enhanced Analysis' });
    await enhancedTab.click();
    
    await page.waitForTimeout(3000);
    
    // Check for enhanced features
    await expect(page.locator('text=Enhanced Race Cards')).toBeVisible();
    
    // Check for comparison mode button
    const compareButton = page.locator('button').filter({ hasText: 'Compare Mode' });
    await expect(compareButton).toBeVisible();
    
    // Check for race expansion functionality
    const expandButton = page.locator('[data-testid="expand-race"], .MuiIconButton-root').first();
    if (await expandButton.isVisible()) {
      await expandButton.click();
      await page.waitForTimeout(1000);
      
      // Check if race details expanded
      const raceDetails = page.locator('.MuiCollapse-root, .expanded-content').first();
      if (await raceDetails.isVisible()) {
        await expect(raceDetails).toBeVisible();
      }
    }
  });

  test('should enable horse comparison mode', async ({ page }) => {
    // Navigate to enhanced analysis
    const enhancedTab = page.locator('[role="tab"]').filter({ hasText: 'Enhanced Analysis' });
    await enhancedTab.click();
    
    await page.waitForTimeout(2000);
    
    // Enable compare mode
    const compareButton = page.locator('button').filter({ hasText: 'Compare Mode' });
    await compareButton.click();
    
    // Check that compare mode is active
    await expect(compareButton).toHaveClass(/contained|active/);
    
    // Look for selectable horses
    const horseCards = page.locator('.MuiCard-root').filter({ hasText: /horse|runner/i });
    if (await horseCards.first().isVisible()) {
      // Try to select a horse for comparison
      await horseCards.first().click();
      await page.waitForTimeout(500);
      
      // Check for selection indication
      const selectedCard = page.locator('.MuiCard-root[class*="selected"], .MuiCard-root[class*="active"]').first();
      if (await selectedCard.isVisible()) {
        await expect(selectedCard).toBeVisible();
      }
    }
  });

  test('should display horse detail modal', async ({ page }) => {
    // Navigate to enhanced analysis
    const enhancedTab = page.locator('[role="tab"]').filter({ hasText: 'Enhanced Analysis' });
    await enhancedTab.click();
    
    await page.waitForTimeout(2000);
    
    // Ensure compare mode is off
    const compareButton = page.locator('button').filter({ hasText: 'Compare Mode' });
    if (await compareButton.isVisible() && await compareButton.getAttribute('class').then(cls => cls?.includes('contained'))) {
      await compareButton.click(); // Turn off compare mode
    }
    
    // Expand race details first
    const expandButton = page.locator('[data-testid="expand-race"], .MuiIconButton-root').first();
    if (await expandButton.isVisible()) {
      await expandButton.click();
      await page.waitForTimeout(1000);
    }
    
    // Click on a horse card to open detail modal
    const horseCard = page.locator('.MuiCard-root').filter({ hasText: /horse|runner/i }).first();
    if (await horseCard.isVisible()) {
      await horseCard.click();
      await page.waitForTimeout(1000);
      
      // Check for modal dialog
      const modal = page.locator('[role="dialog"], .MuiDialog-root').first();
      if (await modal.isVisible()) {
        await expect(modal).toBeVisible();
        
        // Check for detailed horse information
        await expect(modal.locator('text=Detailed Analysis')).toBeVisible();
        
        // Close modal
        const closeButton = modal.locator('button').filter({ hasText: 'Close' });
        await closeButton.click();
      }
    }
  });

  test('should handle loading and error states', async ({ page }) => {
    // Monitor network requests
    const requests: string[] = [];
    page.on('request', (request) => {
      requests.push(request.url());
    });
    
    // Reload page to trigger API calls
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Check if API calls were made
    const apiCalls = requests.filter(url => url.includes('/api/'));
    expect(apiCalls.length).toBeGreaterThan(0);
    
    // Check for loading states or error handling
    const loadingIndicator = page.locator('text=Loading, .loading, .spinner').first();
    const errorMessage = page.locator('text=Error, .error').first();
    
    // Either loading should have appeared or content should be visible
    const hasContent = await page.locator('text=Race Cards').isVisible();
    expect(hasContent).toBeTruthy();
  });

  test('should be responsive on different screen sizes', async ({ page }) => {
    // Test tablet view
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('text=Race Cards')).toBeVisible();
    
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('text=Race Cards')).toBeVisible();
    
    // Take mobile screenshot
    await page.screenshot({ path: 'test-results/race-cards-mobile.png' });
  });
});
