import type { UseQueryResult } from '@tanstack/react-query';
import { ReactNode } from 'react';

import { FormattedMessage } from 'react-intl';

import { cn } from '@/lib/utils';

import { Skeleton } from '@/components/ui/skeleton';

export type QuerySelectorStatus = UseQueryResult['status'];

type QuerySwitcherProps = {
  status: QuerySelectorStatus;
  children: ReactNode;
  skeletonClassname?: string;
  data?: unknown;
};

const QuerySwitcher = ({
  status,
  children,
  skeletonClassname,
  data,
}: QuerySwitcherProps): JSX.Element => {
  switch (status) {
    case 'pending':
      return (
        <Skeleton
          className={cn('grid h-[400px] place-items-center', skeletonClassname)}
        >
          <FormattedMessage id="global.loading" />
        </Skeleton>
      );
    case 'error':
      return (
        <div>
          <FormattedMessage id="global.error" />
        </div>
      );
  }

  if (!data) {
    return (
      <div>
        <FormattedMessage id="global.noDataAvailable" />
      </div>
    );
  }

  return <>{children}</>;
};

export default QuerySwitcher;
