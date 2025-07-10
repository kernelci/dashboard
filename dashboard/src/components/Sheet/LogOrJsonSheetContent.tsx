import type { LinkProps } from '@tanstack/react-router';

import ReactJsonView from '@microlink/react-json-view';

import type { UseQueryResult } from '@tanstack/react-query';

import type { JSX } from 'react';

import type { TNavigationLogActions } from '@/components/Sheet/WrapperSheetContent';
import { WrapperSheetContent } from '@/components/Sheet/WrapperSheetContent';

import { MemoizedMoreDetailsButton } from '@/components/Button/MoreDetailsButton';

import { LogViewerCard } from '@/components/Log/LogViewerCard';
import { LogExcerpt } from '@/components/Log/LogExcerpt';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import IssueSection from '@/components/Issue/IssueSection';
import type { TIssue } from '@/types/issues';
import type { LogData } from '@/hooks/useLogData';
import { useLogExcerpt } from '@/api/logViewer';

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
  const logExcerpt = logData?.log_excerpt;
  const { data: logExcerptData, status: logExcerptStatus } =
    useLogExcerpt(logExcerpt);

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
          <QuerySwitcher data={logExcerptData} status={logExcerptStatus}>
            <LogExcerpt
              logExcerpt={logExcerptData?.content}
              isLoading={navigationLogsActions?.isLoading}
              variant="default"
            />
          </QuerySwitcher>

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
