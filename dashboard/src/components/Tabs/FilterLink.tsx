import { memo, useMemo, type ReactElement } from 'react';

import type { IListingItem } from '../ListingItem/ListingItem';

import { TableBody, TableCell, TableCellWithLink, TableRow } from '../ui/table';

import ListingItem from '../ListingItem/ListingItem';

import BaseTable from '../Table/BaseTable';

import FilterLink from './FilterLink';
import { useDiffFilterParams } from './tabsUtils';

export interface ISummaryItem {
  arch: Omit<IListingItem, 'leftIcon'>;
  leftIcon?: IListingItem['leftIcon'];
  onClickKey?: (key: string) => void;
  onClickCompiler?: (compiler: string) => void;
  compilers: string[];
}

export interface ISummaryItemWithFilter extends ISummaryItem {
  diffFilter: Record<string, Record<string, boolean>>;
}

export interface ISummaryTable {
  summaryHeaders: ReactElement[];
  summaryBody: ISummaryItemWithFilter[];
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
      className="!rounded-[0rem] bg-mediumGray"
      headers={summaryHeaders}
      body={<TableBody>{children}</TableBody>}
    />
