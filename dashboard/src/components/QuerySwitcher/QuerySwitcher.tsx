import type { UseQueryResult } from '@tanstack/react-query';
import type { ReactNode } from 'react';

import { FormattedMessage } from 'react-intl';

import { cn } from '@/lib/utils';

import { Skeleton } from '@/components/ui/skeleton';

export type QuerySelectorStatus = UseQueryResult['status'];

type QuerySwitcherProps = {
  status: QuerySelectorStatus;
  children: ReactNode;
  skeletonClassname?: string;
  data?: unknown;
  customError?: ReactNode;
};

const QuerySwitcher = ({
  status,
  children,
  skeletonClassname,
  data,
  customError,
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
        <>
          {customError ? (
            customError
          ) : (
            <div>
              <FormattedMessage id="global.error" />
            </div>
          )}
        </>
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
