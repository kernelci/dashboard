import type { UseQueryResult } from '@tanstack/react-query';
import { Fragment, type ReactNode, type JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import { cn } from '@/lib/utils';

import { Skeleton } from '@/components/ui/skeleton';
import UnexpectedError from '@/components/UnexpectedError/UnexpectedError';

export type QuerySelectorStatus = UseQueryResult['status'];

type QuerySwitcherProps = {
  status?: QuerySelectorStatus;
  children: ReactNode;
  skeletonClassname?: string;
  data?: unknown;
  customError?: ReactNode;
  customEmptyDataComponent?: JSX.Element;
};

const QuerySwitcher = ({
  status,
  children,
  skeletonClassname,
  data,
  customError,
  customEmptyDataComponent,
}: QuerySwitcherProps): JSX.Element => {
  if (!status) {
    return customEmptyDataComponent ?? <Fragment />;
  }

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
              <UnexpectedError />
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
