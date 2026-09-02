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
export default defineConfig(({ command }) => {
  if (command === 'build' && !dashboardVersion) {
    throw new Error(
      'VITE_DASHBOARD_VERSION is unset and `git describe` failed. Set it to build.',
    );
  }

  return {
    plugins: [tailwindcss(), tsconfigPaths(), react(), TanStackRouterVite()],
    define: {
      'import.meta.env.VITE_DASHBOARD_VERSION':
        JSON.stringify(dashboardVersion),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@privacy-policy': path.resolve(__dirname, '../PRIVACY.md'),
      },
    },
    server: {
      fs: {
        allow: [path.resolve(__dirname, '..')],
      },
    },
  };
});
