import type { PropsWithChildren } from 'react';

import type { HistoryState, LinkProps } from '@tanstack/react-router';

import type { UseQueryResult } from '@tanstack/react-query';

import { Sheet } from '@/components/Sheet';

import { LogOrJsonSheetContent } from '@/components/Sheet/LogOrJsonSheetContent';
import type { TNavigationLogActions } from '@/components/Sheet/WrapperSheetContent';
import type { TIssue } from '@/types/general';

interface TableWithLogSheetProps {
  currentLog?: number;
  onOpenChange?: () => void;
  logExcerpt?: string;
  logUrl?: string;
  navigationLogsActions?: TNavigationLogActions;
  currentLinkProps: LinkProps;
  issues?: TIssue[];
  status?: UseQueryResult['status'];
  error?: UseQueryResult['error'];
  previousSearch?: LinkProps['search'];
  historyState?: HistoryState;
}

const WrapperTableWithLogSheet = ({
  children,
  currentLog,
  logExcerpt,
  logUrl,
  navigationLogsActions,
  onOpenChange,
  currentLinkProps,
  issues,
  previousSearch,
  status,
  error,
  historyState,
}: PropsWithChildren<TableWithLogSheetProps>): JSX.Element => {
  return (
    <div className="flex flex-col gap-6 pb-4">
      {children}

      <Sheet open={typeof currentLog === 'number'} onOpenChange={onOpenChange}>
        <LogOrJsonSheetContent
          logExcerpt={logExcerpt}
          logUrl={logUrl}
          navigationLogsActions={navigationLogsActions}
          currentLinkProps={currentLinkProps}
          issues={issues}
          status={status}
          previousSearch={previousSearch}
          historyState={historyState}
          error={error}
        />
      </Sheet>
    </div>
  );
};

export default WrapperTableWithLogSheet;
