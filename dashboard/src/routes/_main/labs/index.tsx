import { createFileRoute } from '@tanstack/react-router';

import type { JSX } from 'react';

import Labs from '@/pages/Labs/Labs';

const LabsComponent = (): JSX.Element => {
  return <Labs urlFromMap={{ search: '/_main/labs', navigate: '/labs' }} />;
};

export const Route = createFileRoute('/_main/labs/')({
  component: LabsComponent,
});
