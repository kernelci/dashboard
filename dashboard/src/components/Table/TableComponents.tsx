import type { LinkProps } from '@tanstack/react-router';
import type { Cell, Row } from '@tanstack/react-table';
import { flexRender } from '@tanstack/react-table';
import { memo, useCallback, useMemo, type JSX } from 'react';
import { z } from 'zod';

import { TableCellWithLink, TableRow } from '@/components/ui/table';

import { cn } from '@/lib/utils';

import { DETAILS_COLUMN_ID } from './DetailsColumn';

const ColumnMetaSchema = z.object({
  dataTestId: z.string().optional(),
});

type BaseComponentType = {
  id: string;
};

interface ITableCellComponent<T> {
  cell: Cell<T, unknown>;
  rowIndex: number;
  openLogSheet: (index: number) => void;
  detailsLinkProps: LinkProps;
}

const TableCellComponent = <T,>({
  cell,
  rowIndex,
  openLogSheet,
  detailsLinkProps,
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

  const metaResult = ColumnMetaSchema.safeParse(cell.column.columnDef.meta);
  const dataTestId = metaResult.success
    ? metaResult.data.dataTestId
    : undefined;

  return (
    <TableCellWithLink
      onClick={parsedHandleClick}
      key={cell.id}
      linkProps={parsedLinkProps}
      dataTestId={dataTestId}
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
}

const TableRowComponent = <T extends BaseComponentType>({
  row,
  index,
  currentLog,
  openLogSheet,
  getRowLink,
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
        />
      ))}
    </TableRow>
  );
};
export const TableRowMemoized = memo(
  TableRowComponent,
) as typeof TableRowComponent;
