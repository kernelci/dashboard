import type { LinkProps } from '@tanstack/react-router';
import type { Cell, Row } from '@tanstack/react-table';
import { flexRender } from '@tanstack/react-table';
import { memo, useCallback, useMemo, type JSX } from 'react';

import { TableCellWithLink, TableRow } from '@/components/ui/table';

import { cn } from '@/lib/utils';

import { columnWidthStyle } from '@/utils/columnLayout';

import { DETAILS_COLUMN_ID } from './DetailsColumn';

type BaseComponentType = {
  id: string;
};

interface ITableCellComponent<T> {
  cell: Cell<T, unknown>;
  rowIndex: number;
  openLogSheet: (index: number) => void;
  detailsLinkProps: LinkProps;
  columnWidths?: Record<string, number>;
}

const TableCellComponent = <T,>({
  cell,
  rowIndex,
  openLogSheet,
  detailsLinkProps,
  columnWidths,
}: ITableCellComponent<T>): JSX.Element => {
  const handleClick = useCallback(() => {
    openLogSheet(rowIndex);
  }, [rowIndex, openLogSheet]);

  const parsedHandleClick =
    cell.column.id === DETAILS_COLUMN_ID ? undefined : handleClick;

  const parsedLinkProps: LinkProps =
    cell.column.id === DETAILS_COLUMN_ID
      ? detailsLinkProps
      : { search: s => s, state: s => s };

  return (
    <TableCellWithLink
      onClick={parsedHandleClick}
      key={cell.id}
      className="overflow-hidden"
      style={columnWidthStyle(columnWidths?.[cell.column.id])}
      linkProps={parsedLinkProps}
    >
      {flexRender(cell.column.columnDef.cell, cell.getContext())}
    </TableCellWithLink>
  );
};
export const TableCellMemoized = memo(
  TableCellComponent,
) as typeof TableCellComponent;

interface ITableRowComponent<T extends BaseComponentType> {
  row: Row<T>;
  index: number;
  currentLog?: number;
  openLogSheet: (index: number) => void;
  getRowLink: (detailsId: string) => LinkProps;
  columnWidths?: Record<string, number>;
}

const TableRowComponent = <T extends BaseComponentType>({
  row,
  index,
  currentLog,
  openLogSheet,
  getRowLink,
  columnWidths,
}: ITableRowComponent<T>): JSX.Element => {
  const className = index === currentLog ? 'bg-sky-200' : undefined;

  const linkProps = useMemo(() => {
    return getRowLink(row.original.id);
  }, [getRowLink, row.original.id]);

  return (
    <TableRow
      className={cn('hover:bg-light-blue cursor-pointer', className)}
      key={row.id}
    >
      {row.getVisibleCells().map((cell, cellIdx) => (
        <TableCellMemoized<T>
          key={cellIdx}
          cell={cell}
          rowIndex={index}
          openLogSheet={openLogSheet}
          detailsLinkProps={linkProps}
          columnWidths={columnWidths}
        />
      ))}
    </TableRow>
  );
};
export const TableRowMemoized = memo(
  TableRowComponent,
) as typeof TableRowComponent;
