import type { LinkProps } from '@tanstack/react-router';

import ReactJsonView from '@microlink/react-json-view';

import type { UseQueryResult } from '@tanstack/react-query';

import { type JSX } from 'react';

import type { TNavigationLogActions } from '@/components/Sheet/WrapperSheetContent';
import { WrapperSheetContent } from '@/components/Sheet/WrapperSheetContent';

import { MemoizedMoreDetailsButton } from '@/components/Button/MoreDetailsButton';

import { LogViewerCard } from '@/components/Log/LogViewerCard';
import { LogExcerpt } from '@/components/Log/LogExcerpt';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import IssueSection from '@/components/Issue/IssueSection';
import type { TIssue } from '@/types/issues';
import type { LogData } from '@/hooks/useLogData';
import { LOG_EXCERPT_ALLOWED_DOMAINS } from '@/utils/constants/log_excerpt_allowed_domain';
import { useLogViewer } from '@/api/logViewer';

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
  const mocked_link =
    'https://files-staging.kernelci.org/logexcerpt/f0cec57a87733305dacda1348784379f5f7980a3fd2906f47eaf34d2fb918ebf/logexcerpt.txt.gz';

  const url = new URL(mocked_link);
  const isAllowedDomain = LOG_EXCERPT_ALLOWED_DOMAINS.includes(url.hostname);

  const { data: logExcerptData, status: logExcerptStatus } = isAllowedDomain
    ? useLogViewer(mocked_link)
    : { data: { content: mocked_link }, status: 'success' as 'success' };

  console.log('parsed_info', { logExcerptData, logExcerptStatus });

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
