import type { ColumnDef, Row, SortingState } from '@tanstack/react-table';
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import type { CSSProperties } from 'react';
import { memo, useMemo, useRef, useState } from 'react';

import type { LinkProps } from '@tanstack/react-router';
import { Link } from '@tanstack/react-router';

import type { TestHistory, TIndividualTest } from '@/types/general';

import { DumbTableHeader, TableHead } from '@/components/Table/BaseTable';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';

type GetRowLink = (testId: TestHistory['id']) => LinkProps;

const TableRowComponent = ({
  row,
  getRowLink,
}: {
  row: Row<TIndividualTest>;
  getRowLink: GetRowLink;
}): JSX.Element => {
  const linkProps: LinkProps = useMemo(() => {
    return getRowLink(row.original.id);
  }, [getRowLink, row.original.id]);

  return (
    <TableRow key={row.id} className="border-b-0 hover:bg-lightBlue">
      {row.getVisibleCells().map(cell => {
        return (
          <TableCell key={cell.id}>
            <Link {...linkProps}>
              {flexRender(cell.column.columnDef.cell, cell.getContext())}
            </Link>
          </TableCell>
        );
      })}
    </TableRow>
  );
};
const TableRowMemoized = memo(TableRowComponent);

const ESTIMATED_ROW_HEIGHT = 60;

interface IIndividualTestsTable {
  columns: ColumnDef<TIndividualTest>[];
  data: TIndividualTest[];
  getRowLink: GetRowLink;
}

export function IndividualTestsTable({
  data,
  columns,
  getRowLink,
}: IIndividualTestsTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    manualPagination: true,
    state: {
      sorting,
    },
  });

  const groupHeaders = table.getHeaderGroups()[0]?.headers;
  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map(header => {
      return (
        <TableHead key={header.id} className="px-2">
          {header.isPlaceholder
            ? null
            : flexRender(header.column.columnDef.header, header.getContext())}
        </TableHead>
      );
    });
    // TODO: remove exhaustive-deps and change memo  (all tables)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [groupHeaders, sorting]);

  const { rows } = useMemo(() => {
    return table.getRowModel();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [table, sorting]);

  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: rows.length,
    estimateSize: () => ESTIMATED_ROW_HEIGHT,
    getScrollElement: () => parentRef.current,
    overscan: 5,
  });
  const virtualItems = virtualizer.getVirtualItems();

  const tableRows = useMemo((): JSX.Element[] => {
    return virtualItems.map(virtualRow => {
      const row = rows[virtualRow.index] as Row<TIndividualTest>;
      return (
        <TableRowMemoized row={row} key={row.id} getRowLink={getRowLink} />
      );
    });
  }, [getRowLink, rows, virtualItems]);

  // if more performance is needed, try using translate as in the example from tanstack virtual instead of padding
  // https://tanstack.com/virtual/latest/docs/framework/react/examples/table
  const [firstRowStyle, lastRowStyle]: [CSSProperties, CSSProperties] =
    useMemo(() => {
      if (virtualItems.length === 0) return [{}, {}];
      return [
        { paddingTop: virtualItems[0].start },
        {
          paddingBottom:
            virtualizer.getTotalSize() -
            virtualItems[virtualItems.length - 1].end,
        },
      ];
    }, [virtualItems, virtualizer]);

  return (
    <div
      ref={parentRef}
      className="max-h-[400px] max-w-full overflow-auto bg-lightGray p-8"
    >
      <div className="rounded-lg border-x border-t border-darkGray bg-white text-sm text-black">
        <div style={firstRowStyle} />
        <table className="w-full">
          <DumbTableHeader>{tableHeaders}</DumbTableHeader>
          <TableBody>{tableRows}</TableBody>
        </table>
        <div style={lastRowStyle} />
      </div>
    </div>
  );
}
