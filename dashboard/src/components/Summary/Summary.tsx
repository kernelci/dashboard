import { ReactElement, useMemo } from 'react';

import { useDiffFilterParams } from '@/pages/TreeDetails/treeDetailsUtils';

import FilterLink from '@/pages/TreeDetails/TreeDetailsFilterLink';

import BaseTable from '../Table/BaseTable';
import { TableBody, TableCell, TableCellWithLink, TableRow } from '../ui/table';
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
  arch: Omit<IListingItem, 'leftIcon'>;
  leftIcon?: IListingItem['leftIcon'];
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
  leftIcon,
}: ISummaryItem): JSX.Element => {
  const diffFilter = useDiffFilterParams(arch.text, 'archs');

  const compilersElement = useMemo(() => {
    return compilers?.map(compiler => (
      <FilterLink
        key={compiler}
        filterSection="compilers"
        filterValue={compiler}
      >
        {compiler}
      </FilterLink>
    ));
  }, [compilers]);

  return (
    <TableRow>
      <TableCellWithLink
        linkProps={{
          search: previousParams => ({
            ...previousParams,
            diffFilter,
          }),
        }}
      >
        <ListingItem
          onClick={onClickKey}
          warnings={arch.warnings}
          text={arch.text}
          leftIcon={leftIcon}
          success={arch.success}
          unknown={arch.unknown}
          errors={arch.errors}
        />
      </TableCellWithLink>
      <TableCell>
        <div className="flex flex-col gap-1">{compilersElement}</div>
      </TableCell>
    </TableRow>
  );
};

export default Summary;
