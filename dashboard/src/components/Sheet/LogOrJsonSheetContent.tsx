import type { LinkProps } from '@tanstack/react-router';

import ReactJsonView from '@microlink/react-json-view';

import type { UseQueryResult } from '@tanstack/react-query';

import type { JSX } from 'react';

import type { TNavigationLogActions } from '@/components/Sheet/WrapperSheetContent';
import { WrapperSheetContent } from '@/components/Sheet/WrapperSheetContent';

import { MemoizedMoreDetailsButton } from '@/components/Button/MoreDetailsButton';

import { LogViewerCard } from '@/components/Log/LogViewerCard';
import { LogExcerpt } from '@/components/Log/LogExcerpt';
import IssueSection from '@/components/Issue/IssueSection';
import type { TIssue } from '@/types/issues';
import type { LogData } from '@/hooks/useLogData';

export type SheetType = 'log' | 'json';

interface ILogSheet {
  type?: SheetType;
  jsonContent?: IJsonContent;
  logData?: LogData;
  navigationLogsActions?: TNavigationLogActions;
  currentLinkProps?: LinkProps;
  issues?: TIssue[];
  hideIssueSection?: boolean;
  status?: UseQueryResult['status'];
  error?: UseQueryResult['error'];
}

export interface IJsonContent {
  src?: object;
  name?: string;
}

export const LogOrJsonSheetContent = ({
  type = 'log',
  jsonContent,
  logData,
  navigationLogsActions,
  currentLinkProps,
  issues,
  hideIssueSection,
  status,
  error,
}: ILogSheet): JSX.Element => {
  return (
    <WrapperSheetContent
      sheetTitle={type === 'log' ? 'logSheet.title' : 'jsonSheet.title'}
      navigationLogsActions={navigationLogsActions}
      detailsButton={
        currentLinkProps && (
          <MemoizedMoreDetailsButton linkProps={currentLinkProps} />
        )
      }
    >
      {type === 'log' ? (
        <div className="flex h-screen flex-col">
          <LogViewerCard
            logData={logData}
            isLoading={navigationLogsActions?.isLoading}
          />
          <LogExcerpt
            logExcerpt={logData?.log_excerpt}
            isLoading={navigationLogsActions?.isLoading}
            variant="default"
          />

          {!hideIssueSection && (
            <IssueSection
              data={issues}
              status={status ?? 'success'}
              error={error?.message}
              variant="warning"
            />
          )}
        </div>
      ) : (
        <ReactJsonView
          src={jsonContent?.src ?? {}}
          style={{ fontSize: 14 }}
          displayDataTypes={false}
          name={jsonContent?.name ?? false}
        />
      )}
    </WrapperSheetContent>
  );
};
