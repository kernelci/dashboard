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
  onClickKey?: (key: string) => void;
  onClickCompiler?: (compiler: string) => void;
}

export interface ISummaryItem {
  arch: IListingItem;
  onClickKey?: (key: string) => void;
  onClickCompiler?: (compiler: string) => void;
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
  onClickKey,
  onClickCompiler,
}: ISummaryTable): JSX.Element => {
  const summaryBodyRows = useMemo(
    () =>
      summaryBody?.map(row => (
        <SummaryItem
          onClickKey={onClickKey}
          key={row.arch.text}
          arch={row.arch}
          compilers={row.compilers}
          onClickCompiler={onClickCompiler}
        />
      )),
    [onClickKey, summaryBody, onClickCompiler],
  );

  return (
    <DumbSummary summaryHeaders={summaryHeaders}>{summaryBodyRows}</DumbSummary>
  );
};

export const SummaryItem = ({
  arch,
  compilers,
  onClickKey,
  onClickCompiler,
}: ISummaryItem): JSX.Element => {
  const compilersElement = useMemo(() => {
    return compilers?.map(compiler => (
      <button
        key={compiler}
        className="line-clamp-1"
        onClick={() => onClickCompiler?.(compiler)}
      >
        {compiler}
      </button>
    ));
  }, [compilers, onClickCompiler]);

  return (
    <TableRow>
      <TableCell>
        <ListingItem
          errors={arch.errors}
          onClick={onClickKey}
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
