import { ReactElement, useMemo } from 'react';

import BaseTable from '../Table/BaseTable';
import { TableBody, TableCell, TableRow } from '../ui/table';
import ListingItem, { IListingItem } from '../ListingItem/ListingItem';

export interface ISummary extends ISummaryTable {
  title: ReactElement;
  type: 'summary';
}

export interface ISummaryTable {
  summaryHeaders: ReactElement[];
  summaryBody: ISummaryItem[];
}

export interface ISummaryItem {
  arch: IListingItem;
  compilers: string[];
}

interface IDumbSummary {
  children: ReactElement | ReactElement[];
  summaryHeaders: ReactElement[];
}

export const DumbSummary = ({
  children,
  summaryHeaders,
}: IDumbSummary): JSX.Element => {
  return (
    <BaseTable
      className="!rounded-[0rem] bg-mediumGray"
      headers={summaryHeaders}
      body={<TableBody>{children}</TableBody>}
    />
  );
};

const Summary = ({
  summaryHeaders,
  summaryBody,
}: ISummaryTable): JSX.Element => {
  const summaryBodyRows = useMemo(
    () =>
      summaryBody?.map(row => (
        <SummaryItem
          key={row.arch.text}
          arch={row.arch}
          compilers={row.compilers}
        />
      )),
    [summaryBody],
  );

  return (
    <DumbSummary summaryHeaders={summaryHeaders}>
      <TableBody>{summaryBodyRows}</TableBody>
    </DumbSummary>
  );
};

export const SummaryItem = ({ arch, compilers }: ISummaryItem): JSX.Element => {
  const compilersElement = useMemo(
    () =>
      compilers?.map(compiler => (
        <span key={compiler} className="line-clamp-1">
          {compiler}
        </span>
      )),
    [compilers],
  );
  return (
    <TableRow>
      <TableCell>
        <ListingItem
          errors={arch.errors}
          warnings={arch.warnings}
          text={arch.text}
          success={arch.success}
        />
      </TableCell>
      <TableCell>
        <div className="flex flex-col gap-1">{compilersElement}</div>
      </TableCell>
    </TableRow>
  );
};

export default Summary;
