import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient } from '@tanstack/react-query';

import { IntlProvider } from 'react-intl';

import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client';

import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';

import { createRouter, RouterProvider } from '@tanstack/react-router';

import { TooltipProvider } from '@/components/Tooltip';

import { messages } from './locales/messages/index';
import { LOCALES } from './locales/constants';

import { routeTree } from './routeTree.gen';

import './index.css';
import { isDev } from './lib/utils/vite';
import { ToastProvider } from './components/ui/toast';
import type { RedirectFrom } from './types/general';

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace FormatjsIntl {
    interface Message {
      ids: keyof (typeof messages)['en-us'];
    }
  }
}

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }

  interface HistoryState {
    id?: string;
    from?: RedirectFrom;
  }
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // eslint-disable-next-line no-magic-numbers
      staleTime: 1000 * 60 * 5, // 5 minutes,
    },
  },
});

const persister = createSyncStoragePersister({
  storage: isDev ? window.sessionStorage : window.localStorage,
});

const currentMessages = messages[LOCALES.EN_US];

const router = createRouter({ routeTree });

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <PersistQueryClientProvider
      client={queryClient}
      persistOptions={{ persister }}
    >
      <IntlProvider
        messages={currentMessages}
        locale={LOCALES.EN_US}
        defaultLocale={LOCALES.EN_US}
      >
        <ToastProvider>
          <TooltipProvider>
            <RouterProvider router={router} />
          </TooltipProvider>
        </ToastProvider>
      </IntlProvider>
    </PersistQueryClientProvider>
  </React.StrictMode>,
);
