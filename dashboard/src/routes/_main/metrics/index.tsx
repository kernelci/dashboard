import { createFileRoute } from '@tanstack/react-router';

import type { JSX } from 'react';

import { MetricsPage } from '@/pages/Metrics/MetricsPage';

const MetricsComponent = (): JSX.Element => {
  return <MetricsPage />;
};

export const Route = createFileRoute('/_main/metrics/')({
  component: MetricsComponent,
});
