import { memo, useMemo, type ReactElement, type JSX } from 'react';

import type { IListingItem } from '@/components/ListingItem/ListingItem';

import {
  TableBody,
  TableCell,
  TableCellWithLink,
  TableRow,
} from '@/components/ui/table';

import ListingItem from '@/components/ListingItem/ListingItem';

import BaseTable from '@/components/Table/BaseTable';

import FilterLink from '@/components/Tabs/FilterLink';

import { generateDiffFilter } from '@/components/Tabs/tabsUtils';
import type { TFilter } from '@/types/general';

export interface ISummaryItem {
  arch: Omit<IListingItem, 'leftIcon'>;
  leftIcon?: IListingItem['leftIcon'];
  onClickKey?: (key: string) => void;
  onClickCompiler?: (compiler: string) => void;
  compilers: string[];
}

export interface ISummaryItemWithFilter extends ISummaryItem {
  diffFilter: TFilter;
}

export interface ISummaryTable {
  summaryHeaders: ReactElement[];
  summaryBody: ISummaryItemWithFilter[] | ISummaryItem[];
  onClickKey?: (key: string) => void;
  onClickCompiler?: (compiler: string) => void;
  diffFilter: Record<string, Record<string, boolean>>;
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
      className="bg-medium-gray rounded-[0rem]!"
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
  diffFilter,
}: ISummaryTable): JSX.Element => {
  const summaryBodyRows = useMemo(
    () =>
      summaryBody?.map(row => (
        <SummaryItem
          onClickKey={onClickKey}
          key={row.arch.text}
          arch={row.arch}
          diffFilter={diffFilter}
          compilers={row.compilers}
          onClickCompiler={onClickCompiler}
        />
      )),
    [summaryBody, onClickKey, diffFilter, onClickCompiler],
  );

  return (
    <DumbSummary summaryHeaders={summaryHeaders}>{summaryBodyRows}</DumbSummary>
  );
};

const SummaryItem = ({
  arch,
  compilers,
  onClickKey,
  leftIcon,
  diffFilter,
}: ISummaryItemWithFilter): JSX.Element => {
  const handleDiffFilter = useMemo(
    () => generateDiffFilter(arch.text, 'archs', diffFilter),
    [arch.text, diffFilter],
  );

  const compilersElement = useMemo(() => {
    return compilers?.map(compiler => (
      <FilterLink
        key={compiler}
        filterSection="compilers"
        filterValue={compiler}
        diffFilter={diffFilter}
      >
        {compiler}
      </FilterLink>
    ));
  }, [compilers, diffFilter]);

  return (
    <TableRow>
      <TableCellWithLink
        linkProps={{
          search: previousParams => ({
            ...previousParams,
            diffFilter: handleDiffFilter,
          }),
          state: s => s,
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

export const MemoizedSummaryItem = memo(SummaryItem);

const MemoizedSummary = memo(Summary);

export default MemoizedSummary;
