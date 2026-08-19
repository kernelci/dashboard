import path from 'path';
import { execSync } from 'node:child_process';

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';
import tailwindcss from '@tailwindcss/vite';

import { TanStackRouterVite } from '@tanstack/router-plugin/vite';

const dashboardVersion =
  process.env.VITE_DASHBOARD_VERSION ||
  ((): string => {
    try {
      return execSync('git describe --tags --always --dirty').toString().trim();
    } catch {
      return '';
    }
  })();

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [tailwindcss(), tsconfigPaths(), react(), TanStackRouterVite()],
  define: {
    'import.meta.env.VITE_DASHBOARD_VERSION': JSON.stringify(dashboardVersion),
    'import.meta.env.VITE_CACHE_BUSTER': JSON.stringify(
      dashboardVersion || `build-${Date.now()}`,
    ),
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
