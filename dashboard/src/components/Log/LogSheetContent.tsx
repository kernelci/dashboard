import type { LinkProps } from '@tanstack/react-router';

import type { TNavigationLogActions } from '@/components/Sheet/WrapperSheetContent';
import { WrapperSheetContent } from '@/components/Sheet/WrapperSheetContent';

import { MemoizedMoreDetailsButton } from '@/components/Button/MoreDetailsButton';

import { LogViewerCard } from './LogViewerCard';
import { LogExcerpt } from './LogExcerpt';

interface ILogSheet {
  logExcerpt?: string;
  logUrl?: string;
  navigationLogsActions?: TNavigationLogActions;
  currentLinkProps?: LinkProps;
}

export const LogSheetContent = ({
  logExcerpt,
  logUrl,
  navigationLogsActions,
  currentLinkProps,
}: ILogSheet): JSX.Element => {
  return (
    <WrapperSheetContent
      sheetTitle="logSheet.title"
      navigationLogsActions={navigationLogsActions}
      detailsButton={
        currentLinkProps && (
          <MemoizedMoreDetailsButton linkProps={currentLinkProps} />
        )
      }
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
