import type { PropsWithChildren, JSX } from 'react';

import type { LinkProps } from '@tanstack/react-router';

import type { UseQueryResult } from '@tanstack/react-query';

import { Sheet } from '@/components/Sheet';

import { LogOrJsonSheetContent } from '@/components/Sheet/LogOrJsonSheetContent';
import type { TNavigationLogActions } from '@/components/Sheet/WrapperSheetContent';
import { cn } from '@/lib/utils';
import type { TIssue } from '@/types/issues';
import type { LogData } from '@/hooks/useLogData';

interface TableWithLogSheetProps {
  currentLog?: number;
  onOpenChange?: () => void;
  logData: LogData;
  navigationLogsActions?: TNavigationLogActions;
  currentLinkProps: LinkProps;
  issues?: TIssue[];
  status?: UseQueryResult['status'];
  error?: UseQueryResult['error'];
  wrapperClassName?: string;
}

const WrapperTableWithLogSheet = ({
  children,
  currentLog,
  logData,
  navigationLogsActions,
  onOpenChange,
  currentLinkProps,
  issues,
  status,
  error,
  wrapperClassName,
}: PropsWithChildren<TableWithLogSheetProps>): JSX.Element => {
  return (
    <div className={cn('flex flex-col gap-6 pb-4', wrapperClassName)}>
      {children}

      <Sheet open={typeof currentLog === 'number'} onOpenChange={onOpenChange}>
        <LogOrJsonSheetContent
          logData={logData}
          navigationLogsActions={navigationLogsActions}
          currentLinkProps={currentLinkProps}
          issues={issues}
          status={status}
          error={error}
        />
      </Sheet>
    </div>
  );
};

export default WrapperTableWithLogSheet;
