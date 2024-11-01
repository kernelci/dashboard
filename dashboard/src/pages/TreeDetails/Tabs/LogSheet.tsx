import { FormattedMessage } from 'react-intl';

import { GrDocumentDownload } from 'react-icons/gr';

import { memo } from 'react';

import BaseCard from '@/components/Cards/BaseCard';
import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
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
import { truncateBigText } from '@/lib/string';
import { useLogFiles } from '@/api/TreeDetails';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import type { LogFile } from '@/types/tree/TreeDetails';

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

export const LogSheet = ({
  logExcerpt,
  logUrl,
}: LogSheetProps): JSX.Element => {
  const { data: logFilesData, status } = useLogFiles(
    { logUrl: logUrl ?? '' },
    { enabled: !!logUrl },
  );
  return (
    <SheetContent className="flex w-[25rem] flex-col sm:w-full sm:max-w-[44rem]">
      <SheetHeader className="mb-3">
        <SheetTitle className="text-[1.75rem]">
          <FormattedMessage id="logSheet.title" />
        </SheetTitle>
      </SheetHeader>
      <BaseCard className="gap-0" title={<FormattedMessage id="global.logs" />}>
        <div className="px-2 py-3 font-mono text-sm text-[#454545]">
          <FormattedMessage
            id="logSheet.indexOf"
            values={{
              link: (
                <a
                  href={logUrl}
                  className="flex gap-2 transition-all hover:text-blue"
                >
                  <span>{truncateBigText(logUrl)}</span>
                  <GrDocumentDownload className="text-blue" />
                </a>
              ),
            }}
          />
        </div>
        <QuerySwitcher
          data={logFilesData}
          status={status}
          skeletonClassname="h-[3rem]"
          customError={
            <div className="p-4 text-center">
              This log url is not supported in the log viewer yet
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
      </BaseCard>
      <div className="my-4 flex flex-row gap-2">
        <ColoredCircle quantity={3} backgroundClassName="bg-lightRed" />
        <h2>
          <FormattedMessage
            id="logSheet.errorsFound"
            defaultMessage="Errors found on Kernel.log"
          />
        </h2>
      </div>
      <CodeBlock code={logExcerpt ?? FallbackLog} />
      <div className="mt-auto flex justify-end">
        <SheetTrigger>
          <Button className="rounded-3xl bg-[#11B3E6] px-14 font-bold text-white">
            <FormattedMessage id="global.close" defaultMessage="Close" />
          </Button>
        </SheetTrigger>
      </div>
    </SheetContent>
  );
};
