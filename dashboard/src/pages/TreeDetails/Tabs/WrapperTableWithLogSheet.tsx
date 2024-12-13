import type { PropsWithChildren } from 'react';

import { Sheet } from '@/components/Sheet';

import { LogSheetContent } from '@/components/Log/LogSheetContent';
import type { TNavigationLogActions } from '@/components/Sheet/WrapperSheetContent';

interface TableWithLogSheetProps {
  currentLog?: number;
  onOpenChange?: () => void;
  logExcerpt?: string;
  logUrl?: string;
  navigationLogsActions?: TNavigationLogActions;
}

const WrapperTableWithLogSheet = ({
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
        <LogSheetContent
          logExcerpt={logExcerpt}
          logUrl={logUrl}
          navigationLogsActions={navigationLogsActions}
        />
      </Sheet>
    </div>
  );
};

export default WrapperTableWithLogSheet;
