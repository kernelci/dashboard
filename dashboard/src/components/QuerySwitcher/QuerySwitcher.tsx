import type { UseQueryResult } from '@tanstack/react-query';
import { Fragment, type ReactNode, type JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import { HttpStatusCode } from 'axios';

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
  error?: Error | null;
};

const QuerySwitcher = ({
  status,
  children,
  skeletonClassname,
  data,
  customError,
  customEmptyDataComponent,
  error,
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
    case 'error': {
      let errorStatusCode: number | undefined;
      const errorMessage = error?.message;
      if (errorMessage) {
        const splittedError = errorMessage.split(':');
        if (splittedError.length > 1) {
          errorStatusCode = parseInt(splittedError[0]);
        }
      }

      if (errorStatusCode === HttpStatusCode.Ok) {
        return <>{children}</>;
      }

      return (
        <>
          {customError ?? (
            <div>
              <UnexpectedError />
            </div>
          )}
        </>
      );
    }
  }

  if (!data) {
    return (
      <div className="text-weak-gray flex flex-col items-center py-6 text-2xl font-semibold">
        <FormattedMessage id="global.noDataAvailable" />
      </div>
    );
  }

  return <>{children}</>;
};

export default QuerySwitcher;
