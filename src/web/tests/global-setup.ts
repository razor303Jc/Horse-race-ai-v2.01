import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global setup for Playwright tests...');
  
  // Wait for servers to be ready
  await waitForServer('http://localhost:5003', 30000); // Frontend
  await waitForServer('http://localhost:8000', 30000); // API
  
  console.log('✅ Both servers are ready, starting tests...');
}

async function waitForServer(url: string, timeout: number) {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    try {
      const browser = await chromium.launch();
      const page = await browser.newPage();
      await page.goto(url, { timeout: 5000 });
      await browser.close();
      console.log(`✅ Server at ${url} is ready`);
      return;
    } catch (error) {
      console.log(`⏳ Waiting for server at ${url}...`);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  
  throw new Error(`❌ Server at ${url} not ready after ${timeout}ms`);
}

export default globalSetup;
