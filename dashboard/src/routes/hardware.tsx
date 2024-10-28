import { createFileRoute } from '@tanstack/react-router';

import { UnderDevelopment } from '@/components/UnderDevelopment';

export const Route = createFileRoute('/hardware')({
  component: () => <UnderDevelopment />,
});
