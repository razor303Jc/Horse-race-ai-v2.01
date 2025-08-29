import { Page, expect } from '@playwright/test';

/**
 * Test Utilities and Helper Functions
 * Common functions used across multiple test files
 */

export class TestUtils {
  constructor(private page: Page) {}

  /**
   * Wait for the application to be fully loaded
   */
  async waitForAppReady(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
    
    // Wait for any loading indicators to disappear
    const loadingIndicators = this.page.locator('text=Loading, .loading, .spinner');
    await loadingIndicators.first().waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {
      // Ignore if no loading indicators found
    });
  }

  /**
   * Take a screenshot with a descriptive name
   */
  async takeScreenshot(name: string, fullPage: boolean = false): Promise<void> {
    await this.page.screenshot({ 
      path: `test-results/${name}.png`,
      fullPage 
    });
  }

  /**
   * Check if an element is visible within a timeout
   */
  async isElementVisible(selector: string, timeout: number = 5000): Promise<boolean> {
    try {
      await this.page.locator(selector).waitFor({ state: 'visible', timeout });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Wait for API calls to complete
   */
  async waitForAPIComplete(): Promise<void> {
    // Wait for network to be idle
    await this.page.waitForLoadState('networkidle');
    
    // Additional wait for any delayed API calls
    await this.page.waitForTimeout(1000);
  }

  /**
   * Check for error messages on the page
   */
  async checkForErrors(): Promise<string[]> {
    const errorSelectors = [
      'text=/error/i',
      'text=/failed/i', 
      '.error',
      '[role="alert"]',
      '.MuiAlert-standardError'
    ];
    
    const errors: string[] = [];
    
    for (const selector of errorSelectors) {
      const elements = this.page.locator(selector);
      const count = await elements.count();
      
      for (let i = 0; i < count; i++) {
        const text = await elements.nth(i).textContent();
        if (text && text.trim()) {
          errors.push(text.trim());
        }
      }
    }
    
    return errors;
  }

  /**
   * Navigate to a page and verify it loads
   */
  async navigateAndVerify(path: string, expectedText?: string): Promise<void> {
    await this.page.goto(path);
    await this.waitForAppReady();
    
    if (expectedText) {
      await expect(this.page.locator(`text=${expectedText}`)).toBeVisible();
    }
    
    // Check for any errors
    const errors = await this.checkForErrors();
    if (errors.length > 0) {
      console.warn(`Errors found on page ${path}:`, errors);
    }
  }

  /**
   * Simulate mobile device viewport
   */
  async setMobileViewport(): Promise<void> {
    await this.page.setViewportSize({ width: 375, height: 667 });
  }

  /**
   * Simulate tablet device viewport
   */
  async setTabletViewport(): Promise<void> {
    await this.page.setViewportSize({ width: 768, height: 1024 });
  }

  /**
   * Simulate desktop viewport
   */
  async setDesktopViewport(): Promise<void> {
    await this.page.setViewportSize({ width: 1920, height: 1080 });
  }

  /**
   * Wait for and click an element
   */
  async waitAndClick(selector: string, timeout: number = 10000): Promise<void> {
    const element = this.page.locator(selector);
    await element.waitFor({ state: 'visible', timeout });
    await element.click();
  }

  /**
   * Check if page has loaded without JavaScript errors
   */
  async checkConsoleErrors(): Promise<string[]> {
    const consoleErrors: string[] = [];
    
    this.page.on('pageerror', (error) => {
      consoleErrors.push(error.message);
    });
    
    this.page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    return consoleErrors;
  }

  /**
   * Verify common UI elements are present
   */
  async verifyBasicUIElements(): Promise<void> {
    // Check for main heading
    const headings = this.page.locator('h1, h2, h3, h4');
    await expect(headings.first()).toBeVisible();
    
    // Check for navigation elements
    const navigation = this.page.locator('nav, [role="navigation"], [role="tab"]');
    if (await navigation.count() > 0) {
      await expect(navigation.first()).toBeVisible();
    }
  }

  /**
   * Monitor network requests and responses
   */
  async monitorNetworkRequests(): Promise<{requests: string[], responses: any[]}> {
    const requests: string[] = [];
    const responses: any[] = [];
    
    this.page.on('request', (request) => {
      requests.push(request.url());
    });
    
    this.page.on('response', (response) => {
      responses.push({
        url: response.url(),
        status: response.status(),
        contentType: response.headers()['content-type']
      });
    });
    
    return { requests, responses };
  }

  /**
   * Test form interaction
   */
  async testFormField(selector: string, value: string): Promise<void> {
    const field = this.page.locator(selector);
    await field.fill(value);
    
    // Verify the value was set
    const fieldValue = await field.inputValue();
    expect(fieldValue).toBe(value);
  }

  /**
   * Test button interaction
   */
  async testButton(selector: string): Promise<void> {
    const button = this.page.locator(selector);
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
    await button.click();
  }

  /**
   * Verify accessibility basics
   */
  async checkBasicAccessibility(): Promise<{issues: string[], recommendations: string[]}> {
    const issues: string[] = [];
    const recommendations: string[] = [];
    
    // Check for headings structure
    const h1Count = await this.page.locator('h1').count();
    if (h1Count === 0) {
      issues.push('No H1 heading found');
    } else if (h1Count > 1) {
      issues.push('Multiple H1 headings found');
    }
    
    // Check for images without alt text
    const images = this.page.locator('img');
    const imageCount = await images.count();
    
    for (let i = 0; i < Math.min(imageCount, 10); i++) {
      const img = images.nth(i);
      const alt = await img.getAttribute('alt');
      const role = await img.getAttribute('role');
      
      if (!alt && role !== 'presentation') {
        issues.push(`Image ${i + 1} missing alt text`);
      }
    }
    
    // Check for buttons without labels
    const buttons = this.page.locator('button');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < Math.min(buttonCount, 10); i++) {
      const button = buttons.nth(i);
      const text = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');
      const title = await button.getAttribute('title');
      
      if (!text?.trim() && !ariaLabel && !title) {
        issues.push(`Button ${i + 1} missing accessible label`);
      }
    }
    
    // Recommendations
    if (issues.length === 0) {
      recommendations.push('Basic accessibility checks passed');
    }
    
    return { issues, recommendations };
  }
}

/**
 * API Testing Utilities
 */
export class APITestUtils {
  constructor(private baseURL: string = 'http://localhost:8000') {}

  /**
   * Test if API is responsive
   */
  async isAPIReady(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return response.status === 200;
    } catch {
      return false;
    }
  }

  /**
   * Test API endpoint with retry logic
   */
  async testEndpoint(endpoint: string, retries: number = 3): Promise<{status: number, data?: any, error?: string}> {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(`${this.baseURL}${endpoint}`);
        const data = response.headers.get('content-type')?.includes('application/json') 
          ? await response.json() 
          : await response.text();
        
        return { status: response.status, data };
      } catch (error) {
        if (i === retries - 1) {
          return { status: 0, error: error instanceof Error ? error.message : 'Unknown error' };
        }
        
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    return { status: 0, error: 'Max retries exceeded' };
  }

  /**
   * Test POST request to API
   */
  async testPOST(endpoint: string, data: any): Promise<{status: number, response?: any, error?: string}> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      const responseData = response.headers.get('content-type')?.includes('application/json') 
        ? await response.json() 
        : await response.text();
      
      return { status: response.status, response: responseData };
    } catch (error) {
      return { status: 0, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  }
}
