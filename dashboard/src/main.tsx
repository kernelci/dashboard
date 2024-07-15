import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { IntlProvider } from 'react-intl';

import { flatten } from 'flat';

import { messages } from './locales/messages/index';
import { LOCALES } from './locales/constants';

import './index.css';
import Root from './routes/Root/Root';
import Trees from './routes/Trees/Trees';

const queryClient = new QueryClient();

const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      {
        path: '/',
        element: <Trees />,
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <IntlProvider messages={flatten(messages[LOCALES.EN_US])} locale="en">
        <RouterProvider router={router} />
      </IntlProvider>
    </QueryClientProvider>
  </React.StrictMode>,
);
