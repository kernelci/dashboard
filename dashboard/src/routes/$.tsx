import { createFileRoute, Link } from '@tanstack/react-router';
import { useIntl } from 'react-intl';
import type { JSX } from 'react';

import { Button } from '@/components/ui/button';

const NotFoundComponent = (): JSX.Element => {
  const { formatMessage } = useIntl();

  return (
    <div className="flex h-screen flex-col items-center justify-center space-y-4">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="text-xl">{formatMessage({ id: 'global.notFound' })}</p>
      <Button asChild>
        <Link to="/tree">{formatMessage({ id: 'global.backToHome' })}</Link>
      </Button>
    </div>
  );
};

export const Route = createFileRoute('/$')({
  component: NotFoundComponent,
});
