import { FormattedMessage, useIntl } from 'react-intl';

import { GrDocumentDownload } from 'react-icons/gr';

import { memo, useCallback } from 'react';

import BaseCard from '@/components/Cards/BaseCard';
import CodeBlock from '@/components/Filter/CodeBlock';
import {
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/Sheet';
import { DumbTableHeader, TableHead } from '@/components/Table/BaseTable';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableRow } from '@/components/ui/table';
import { truncateUrl } from '@/lib/string';
import { useLogFiles } from '@/api/treeDetails';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import type { LogFile } from '@/types/tree/TreeDetails';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/Tooltip/Tooltip';

//TODO Localize the fallback string
const FallbackLog = `
 ________________________________
/ Sorry, there is no Log Excerpt \\
\\ available for this build.      /
 --------------------------------
        \\   ^__^
         \\  (oo)\\_______
            (__)\\       )\\/\\
                ||----w |
                ||     ||`;

type LogSheetProps = {
  logExcerpt?: string;
  logUrl?: string;
  navigationLogsActions?: {
    previousItem: () => void;
    nextItem: () => void;
    hasPrevious: boolean;
    hasNext: boolean;
    isLoading: boolean;
  };
};

type LogFilesTableProps = {
  logFiles: LogFile[];
  logUrl: string;
};

const LogLink = ({
  combinedLogUrl,
  children,
}: {
  combinedLogUrl: string;
  children: string;
}): JSX.Element => (
  <a
    href={combinedLogUrl}
    className="border-b border-b-transparent transition-all hover:border-b-blue hover:text-blue"
  >
    {children}
  </a>
);

const LogFilesTable = ({
  logFiles,
  logUrl,
}: LogFilesTableProps): JSX.Element => {
  return (
    <Table containerClassName="rounded-none border-none">
      <DumbTableHeader>
        <TableHead>
          <FormattedMessage id="logSheet.fileName" />
        </TableHead>
        <TableHead>
          <FormattedMessage id="logSheet.fileSize" />
        </TableHead>
        <TableHead>
          <FormattedMessage id="global.date" />
        </TableHead>
      </DumbTableHeader>
      <TableBody>
        {logFiles.map(logFile => {
          const combinedLogUrl = `${logUrl}/${logFile.specific_log_url}`;
          return (
            <TableRow key={logFile.file_name}>
              <TableCell>
                <LogLink combinedLogUrl={combinedLogUrl}>
                  {logFile.file_name}
                </LogLink>
              </TableCell>
              <TableCell>
                <LogLink combinedLogUrl={combinedLogUrl}>
                  {logFile.file_size}
                </LogLink>
              </TableCell>
              <TableCell>
                <LogLink combinedLogUrl={combinedLogUrl}>
                  {logFile.date}
                </LogLink>
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
};

const MemoizedLogFilesTable = memo(LogFilesTable);

const nextItem = (
  navigationLogsActions?: LogSheetProps['navigationLogsActions'],
): void => {
  navigationLogsActions?.nextItem();
};

const previousItem = (
  navigationLogsActions?: LogSheetProps['navigationLogsActions'],
): void => {
  navigationLogsActions?.previousItem();
};

const keyboardMap: {
  [key: string]: (
    navigationLogsActions?: LogSheetProps['navigationLogsActions'],
  ) => void;
} = {
  ArrowRight: nextItem,
  ArrowLeft: previousItem,
  ArrowDown: nextItem,
  ArrowUp: previousItem,
  h: previousItem,
  j: nextItem,
  k: previousItem,
  l: nextItem,
};

export const LogSheet = ({
  logExcerpt,
  logUrl,
  navigationLogsActions,
}: LogSheetProps): JSX.Element => {
  const { data: logFilesData, status } = useLogFiles(
    { logUrl: logUrl ?? '' },
    { enabled: !!logUrl },
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent): void => {
      if (!navigationLogsActions?.isLoading) {
        keyboardMap[e.key]?.(navigationLogsActions);
      }
    },
    [navigationLogsActions],
  );

  const { formatMessage } = useIntl();
  const previousTooltipMsg = `${formatMessage({ id: 'global.arrowRight' })},\
    ${formatMessage({ id: 'global.arrowUp' })}, k, h`;
  const nextTooltipMsg = `${formatMessage({ id: 'global.arrowLeft' })},\
    ${formatMessage({ id: 'global.arrowDown' })}, j, l`;

  return (
    <SheetContent
      className="flex flex-col overflow-auto sm:w-full sm:max-w-[clamp(650px,75vw,1300px)]"
      onKeyDown={handleKeyDown}
    >
      <SheetHeader className="mb-3">
        <SheetTitle className="text-[1.75rem]">
          <FormattedMessage id="logSheet.title" />
        </SheetTitle>
      </SheetHeader>
      <BaseCard
        className="gap-0"
        title={<FormattedMessage id="global.fullLogs" />}
      >
        <div className="px-2 py-3 font-mono text-[#454545]">
          {navigationLogsActions?.isLoading ? (
            <FormattedMessage id="global.loading" />
          ) : (
            <FormattedMessage
              id={logUrl ? 'logSheet.downloadLog' : 'logSheet.noLogFound'}
              values={{
                link: (
                  <a
                    href={logUrl}
                    className="flex gap-2 text-blue transition-all hover:underline"
                  >
                    <span>{truncateUrl(logUrl)}</span>
                    <GrDocumentDownload className="text-blue" />
                  </a>
                ),
              }}
            />
          )}
        </div>
        {logUrl ? (
          <QuerySwitcher
            data={logFilesData}
            status={status}
            skeletonClassname="h-[3rem]"
            customError={
              <div className="p-4 text-center">
                <FormattedMessage id="logSheet.logQueryCustomError" />
              </div>
            }
          >
            <Table containerClassName="rounded-none border-none">
              {logFilesData?.log_files && !!logUrl && (
                <MemoizedLogFilesTable
                  logFiles={logFilesData?.log_files}
                  logUrl={logUrl}
                />
              )}
            </Table>
          </QuerySwitcher>
        ) : (
          <div className="p-9"></div>
        )}
      </BaseCard>

      {navigationLogsActions?.isLoading ? (
        <Skeleton className="grid h-[400px] place-items-center">
          <FormattedMessage id="global.loading" />
        </Skeleton>
      ) : (
        <CodeBlock code={logExcerpt ?? FallbackLog} />
      )}

      <div className="mt-auto flex justify-end">
        {navigationLogsActions && (
          <>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  onClick={navigationLogsActions.previousItem}
                  disabled={!navigationLogsActions.hasPrevious}
                  className="rounded-3xl bg-[#11B3E6] px-14 font-bold text-white"
                >
                  <FormattedMessage
                    id="global.prev"
                    defaultMessage="Previous"
                  />
                </Button>
              </TooltipTrigger>
              <TooltipContent>{previousTooltipMsg}</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  onClick={navigationLogsActions.nextItem}
                  disabled={!navigationLogsActions.hasNext}
                  className="mx-5 rounded-3xl bg-[#11B3E6] px-14 font-bold text-white"
                >
                  <FormattedMessage id="global.next" defaultMessage="Next" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>{nextTooltipMsg}</TooltipContent>
            </Tooltip>
          </>
        )}

        <SheetTrigger asChild>
          <Button className="rounded-3xl bg-[#11B3E6] px-14 font-bold text-white">
            <FormattedMessage id="global.close" defaultMessage="Close" />
          </Button>
        </SheetTrigger>
      </div>
    </SheetContent>
  );
};
