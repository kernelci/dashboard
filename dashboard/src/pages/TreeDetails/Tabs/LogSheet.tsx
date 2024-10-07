import { FormattedMessage } from 'react-intl';

import { GrDocumentDownload } from 'react-icons/gr';

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
import { DevOnly } from '@/components/FeatureFlag';
import { truncateBigText } from '@/lib/string';

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

export const LogSheet = ({
  logExcerpt,
  logUrl,
}: LogSheetProps): JSX.Element => {
  return (
    <SheetContent className="flex w-[25rem] flex-col sm:w-full sm:max-w-[44rem]">
      <SheetHeader className="mb-3">
        <SheetTitle className="text-[1.75rem]">Build Logs</SheetTitle>
      </SheetHeader>
      <BaseCard className="gap-0" title={<>Logs</>}>
        <div className="px-2 py-3 font-mono text-sm text-[#454545]">
          <FormattedMessage
            id="logSheet.indexOf"
            values={{
              link: (
                <a href={logUrl} className="flex gap-2">
                  <span>{truncateBigText(logUrl)}</span>
                  <GrDocumentDownload className="text-blue" />
                </a>
              ),
            }}
          />
        </div>
        {/* TODO Replace with actual data */}
        <DevOnly>
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
              {/* TODO: Replace with actual data */}
              <TableRow>
                <TableCell>Placeholder 1</TableCell>
                <TableCell>Placeholder 2</TableCell>
                <TableCell>Placeholder 3</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>test.log</TableCell>
                <TableCell>23mb</TableCell>
                <TableCell>2024-03-1</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>task.log</TableCell>
                <TableCell>27mb</TableCell>
                <TableCell>2024-05-1</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </DevOnly>
      </BaseCard>
      <div className="my-8 flex flex-row gap-2">
        <ColoredCircle quantity={3} backgroundClassName="bg-lightRed" />
        <h2>
          <FormattedMessage
            id="logSheet.errorsFound"
            defaultMessage="Errors found on Kernel.log"
          />
        </h2>
      </div>
      {/*TODO: Replace with actual log data */}
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
