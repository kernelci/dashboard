import { defineConfig, devices } from '@playwright/test';
import dotenv from 'dotenv';

dotenv.config();

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: process.env.PLAYWRIGHT_TEST_BASE_URL || 'http://localhost:5173',
    bypassCSP: true,
    launchOptions: {
      args: ['--disable-web-security', '--disable-features=VizDisplayCompositor'],
    },
  },
});
