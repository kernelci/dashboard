import type { TNavigationLogActions } from '@/components/Sheet/WrapperSheetContent';
import { WrapperSheetContent } from '@/components/Sheet/WrapperSheetContent';

import { LogViewerCard } from './LogViewerCard';
import { LogExcerpt } from './LogExcerpt';

interface ILogSheet {
  logExcerpt?: string;
  logUrl?: string;
  navigationLogsActions?: TNavigationLogActions;
}

export const LogSheetContent = ({
  logExcerpt,
  logUrl,
  navigationLogsActions,
}: ILogSheet): JSX.Element => {
  return (
    <WrapperSheetContent
      sheetTitle="logSheet.title"
      navigationLogsActions={navigationLogsActions}
    >
      <LogViewerCard
        logUrl={logUrl}
        isLoading={navigationLogsActions?.isLoading}
      />
      <LogExcerpt
        logExcerpt={logExcerpt}
        isLoading={navigationLogsActions?.isLoading}
      />
    </WrapperSheetContent>
  );
};
