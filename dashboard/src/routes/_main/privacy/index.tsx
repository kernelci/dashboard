import { createFileRoute } from '@tanstack/react-router';

import type { JSX } from 'react';

import { PrivacyPage } from '@/pages/Privacy/PrivacyPage';

const PrivacyComponent = (): JSX.Element => {
  return <PrivacyPage />;
};

export const Route = createFileRoute('/_main/privacy/')({
  component: PrivacyComponent,
});
