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

export type SheetType = 'log' | 'json';

interface ILogSheet {
  type?: SheetType;
  jsonContent?: IJsonContent;
  logExcerpt?: string;
  logUrl?: string;
  navigationLogsActions?: TNavigationLogActions;
  currentLinkProps?: LinkProps;
  issues?: TIssue[];
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
  logExcerpt,
  logUrl,
  navigationLogsActions,
  currentLinkProps,
  issues,
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
        <>
          <LogViewerCard
            logUrl={logUrl}
            isLoading={navigationLogsActions?.isLoading}
          />
          <LogExcerpt
            logExcerpt={logExcerpt}
            isLoading={navigationLogsActions?.isLoading}
          />
          <IssueSection
            data={issues}
            status={status ?? 'success'}
            error={error?.message}
            variant="warning"
          />
        </>
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
