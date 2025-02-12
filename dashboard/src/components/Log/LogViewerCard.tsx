import { GrDocumentDownload } from 'react-icons/gr';

import { FormattedMessage } from 'react-intl';

import { memo } from 'react';

import { useLogFiles } from '@/api/treeDetails';
import BaseCard from '@/components/Cards/BaseCard';
import { truncateUrl } from '@/lib/string';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { Table, TableBody, TableCell, TableRow } from '@/components/ui/table';
import type { LogFile } from '@/types/tree/TreeDetails';
import { DumbTableHeader, TableHead } from '@/components/Table/BaseTable';

const LogLink = ({
  combinedLogUrl,
  children,
}: {
  combinedLogUrl: string;
  children: string;
}): JSX.Element => (
  <a
    href={combinedLogUrl}
    className="hover:border-b-blue hover:text-blue border-b border-b-transparent transition-all"
  >
    {children}
  </a>
);

type TLogFilesTable = {
  logFiles: LogFile[];
  logUrl: string;
};

const LogFilesTable = ({ logFiles, logUrl }: TLogFilesTable): JSX.Element => {
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

interface ILogViewerCard {
  isLoading?: boolean;
  logUrl?: string;
}

export const LogViewerCard = ({
  isLoading,
  logUrl,
}: ILogViewerCard): JSX.Element => {
  const { data: logFilesData, status } = useLogFiles(
    { logUrl: logUrl ?? '' },
    { enabled: !!logUrl },
  );

  return (
    <BaseCard
      className="gap-0"
      title={<FormattedMessage id="global.fullLogs" />}
    >
      <div className="px-2 py-3 font-mono text-[#454545]">
        {isLoading ? (
          <FormattedMessage id="global.loading" />
        ) : (
          <FormattedMessage
            id={logUrl ? 'logSheet.downloadLog' : 'logSheet.noLogFound'}
            values={{
              link: (
                <a
                  href={logUrl}
                  className="text-blue flex gap-2 transition-all hover:underline"
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
  );
};
