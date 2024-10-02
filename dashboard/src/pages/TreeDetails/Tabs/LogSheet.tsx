import { FormattedMessage } from 'react-intl';

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

const PlaceholderLog = `
_______________
< This is a log >
 ---------------
       \\ ^__^
          (oo)_______
          (__)       )/
             ||----w |
             ||     ||`;

export const LogSheet = (): JSX.Element => {
  return (
    <SheetContent className="w-[25rem] sm:w-full sm:max-w-[44rem]">
      <SheetHeader className="mb-3">
        <SheetTitle className="text-[1.75rem]">Build Logs</SheetTitle>
      </SheetHeader>
      <BaseCard className="gap-0" title={<>Logs</>}>
        <div className="px-2 py-3 font-mono text-sm text-[#454545]">
          {/* TODO Replace with actual data */}
          Index of
          /stable-rc/linux-5.10.y/v5.10.215-32-gd3c603576d90b/mips/32r2el_defconfig/gcc-10/logs/
        </div>
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
      <CodeBlock code={PlaceholderLog} />

      <div className="mt-5 flex justify-end">
        <SheetTrigger>
          <Button className="rounded-3xl bg-[#11B3E6] px-14 font-bold text-white">
            <FormattedMessage id="global.close" defaultMessage="Close" />
          </Button>
        </SheetTrigger>
      </div>
    </SheetContent>
  );
};
