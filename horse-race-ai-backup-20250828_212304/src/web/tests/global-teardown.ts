import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Running global teardown for Playwright tests...');
  console.log('✅ Teardown complete');
}

export default globalTeardown;
