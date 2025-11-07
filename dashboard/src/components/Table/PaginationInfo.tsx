import type { Table } from '@tanstack/react-table';

import { FormattedMessage } from 'react-intl';

import { MdArrowBackIos, MdArrowForwardIos } from 'react-icons/md';

import { useCallback, useMemo, type JSX } from 'react';

import type { MessagesKey } from '@/locales/messages';

import { Button } from '@/components/ui/button';

import {
  Select,
  SelectItem,
  SelectContent,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import { cn } from '@/lib/utils';
import { ItemsPerPageValues } from '@/utils/constants/general';

interface IPaginationInfo<T> {
  table: Table<T>;
  intlLabel: MessagesKey;
  onPaginationChange?: (pageSize: number) => void;
}

export function PaginationInfo<T>({
  table,
  intlLabel,
  onPaginationChange,
}: IPaginationInfo<T>): JSX.Element {
  return (
    <div className="flex flex-row flex-wrap justify-end gap-4 text-sm">
      <ItemsPerPageSelector
        table={table}
        onPaginationChange={onPaginationChange}
      />
      <div className="flex flex-wrap justify-end gap-4">
        <ListingCount table={table} intlLabel={intlLabel} />
        <PaginationButtons table={table} />
      </div>
    </div>
  );
}

export const ItemsPerPageSelector = <T,>({
  values = ItemsPerPageValues,
  table,
  onPaginationChange,
  className,
}: {
  values?: number[];
  table: Table<T>;
  onPaginationChange?: (pageSize: number) => void;
  className?: string;
}): JSX.Element => {
  const selected = table.getState().pagination.pageSize;

  const onValueChange = useCallback(
    (value: number) => {
      if (onPaginationChange) {
        onPaginationChange(value);
      }

      table.setPageSize(value);
    },
    [onPaginationChange, table],
  );

  const onChangeHandle = useCallback(
    (v: string) => onValueChange(parseInt(v)),
    [onValueChange],
  );

  const selectItems = useMemo(
    () =>
      values.map(v => (
        <SelectItem key={v} value={v.toString()}>
          {v}
        </SelectItem>
      )),
    [values],
  );

  return (
    <div
      className={cn(
        'flex flex-row items-center gap-2 text-sm whitespace-nowrap',
        className,
      )}
    >
      <FormattedMessage id="table.itemsPerPage" />
      <Select value={selected.toString()} onValueChange={onChangeHandle}>
        <SelectTrigger className="w-16">
          <SelectValue placeholder="" />
        </SelectTrigger>
        <SelectContent>{selectItems}</SelectContent>
      </Select>
    </div>
  );
};

export const ListingCount = <T,>({
  table,
  intlLabel,
  className,
}: {
  table: Table<T>;
  intlLabel: MessagesKey;
  className?: string;
}): JSX.Element => {
  const filteredRowModel = table.getFilteredRowModel();
  const countData = useMemo(
    () => filteredRowModel.rows.length,
    [filteredRowModel],
  );

  const pagination = table.getState().pagination;
  const pageIndex = pagination.pageIndex;
  const pageSize = pagination.pageSize;
  const startIndex = countData > 0 ? pageIndex * pageSize + 1 : 0;
  const endIndex = Math.min((pageIndex + 1) * pageSize, countData);

  return (
    <div className={cn('flex flex-row items-center gap-2 text-sm', className)}>
      <FormattedMessage id="table.showing" />
      <span className="font-bold whitespace-nowrap">
        {startIndex} - {endIndex}
      </span>
      <FormattedMessage id="table.of" />
      <span className="font-bold">{countData}</span>
      <FormattedMessage id={intlLabel} defaultMessage="Trees" />
    </div>
  );
};

export const PaginationButtons = <T,>({
  table,
  buttonsClassName = 'text-blue font-bold',
  className,
}: {
  table: Table<T>;
  buttonsClassName?: string;
  className?: string;
}): JSX.Element => {
  return (
    <div className={cn('flex flex-row items-center gap-2', className)}>
      <Button
        variant="outline"
        onClick={table.previousPage}
        disabled={!table.getCanPreviousPage()}
      >
        <MdArrowBackIos className={buttonsClassName} />
      </Button>
      <Button
        variant="outline"
        onClick={table.nextPage}
        disabled={!table.getCanNextPage()}
      >
        <MdArrowForwardIos className={buttonsClassName} />
      </Button>
    </div>
  );
};
