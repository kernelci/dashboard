import type { PropsWithChildren } from 'react';

import { Sheet } from '@/components/Sheet';

import { LogSheet } from './LogSheet';

interface TableWithLogSheetProps {
  currentLog?: number;
  onOpenChange?: () => void;
  logExcerpt?: string;
  logUrl?: string;
  navigationLogsActions?: {
    previousItem: () => void;
    nextItem: () => void;
    hasPrevious: boolean;
    hasNext: boolean;
    isLoading: boolean;
  };
}

const WrapperTable = ({
  children,
  currentLog,
  logExcerpt,
  logUrl,
  navigationLogsActions,
  onOpenChange,
}: PropsWithChildren<TableWithLogSheetProps>): JSX.Element => {
  return (
    <div className="flex flex-col gap-6 pb-4">
      {children}

      <Sheet open={typeof currentLog === 'number'} onOpenChange={onOpenChange}>
        <LogSheet
          logExcerpt={logExcerpt}
          logUrl={logUrl}
          navigationLogsActions={navigationLogsActions}
        />
      </Sheet>
    </div>
  );
};

export default WrapperTable;
