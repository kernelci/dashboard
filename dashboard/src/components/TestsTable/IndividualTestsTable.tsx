import type { Cell, ColumnDef, Row, SortingState } from '@tanstack/react-table';
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import type { CSSProperties } from 'react';
import { memo, useCallback, useMemo, useRef, useState } from 'react';

import type { LinkProps } from '@tanstack/react-router';

import type { TestHistory, TIndividualTest } from '@/types/general';

import { DumbTableHeader, TableHead } from '@/components/Table/BaseTable';
import { TableBody, TableCellWithLink, TableRow } from '@/components/ui/table';

import { useTestDetails } from '@/api/testDetails';
import WrapperTable from '@/pages/TreeDetails/Tabs/WrapperTable';
import { cn } from '@/lib/utils';

type GetRowLink = (testId: TestHistory['id']) => LinkProps;

const TableCellComponent = ({
  cell,
  rowIndex,
  linkProps,
  openLogSheet,
}: {
  cell: Cell<TIndividualTest, unknown>;
  rowIndex: number;
  linkProps: LinkProps;
  openLogSheet: (index: number) => void;
}): JSX.Element => {
  const handleClick = useCallback(() => {
    openLogSheet(rowIndex);
  }, [rowIndex, openLogSheet]);

  const parsedHandleClick =
    cell.column.id === 'status' ? handleClick : undefined;
  const parsedLinkProps: LinkProps =
    cell.column.id === 'status' ? { search: s => s } : linkProps;

  return (
    <TableCellWithLink
      onClick={parsedHandleClick}
      key={cell.id}
      linkProps={parsedLinkProps}
    >
      {flexRender(cell.column.columnDef.cell, cell.getContext())}
    </TableCellWithLink>
  );
};

const TableCellMemoized = memo(TableCellComponent);

const TableRowComponent = ({
  row,
  getRowLink,
  index,
  openLogSheet,
  currentLog,
}: {
  row: Row<TIndividualTest>;
  index: number;
  getRowLink: GetRowLink;
  currentLog?: number;
  openLogSheet: (index: number) => void;
}): JSX.Element => {
  const className = index === currentLog ? 'bg-sky-200' : undefined;

  const linkProps: LinkProps = useMemo(() => {
    return getRowLink(row.original.id);
  }, [getRowLink, row.original.id]);

  return (
    <TableRow
      key={row.id}
      className={cn('cursor-pointer border-b-0 hover:bg-lightBlue', className)}
    >
      {row.getVisibleCells().map((cell, idx) => (
        <TableCellMemoized
          key={idx}
          cell={cell}
          linkProps={linkProps}
          openLogSheet={openLogSheet}
          rowIndex={index}
        />
      ))}
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
            : // the header must change the icon when sorting changes,
              // but just the column dependency won't trigger the rerender
              // so we pass an unused sorting prop here to force the useMemo dependency
              flexRender(header.column.columnDef.header, {
                ...header.getContext(),
                sorting,
              })}
        </TableHead>
      );
    });
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

  const sortedItems = useMemo(
    (): TIndividualTest[] => rows.map(row => row.original),
    [rows],
  );

  const [currentLog, setLog] = useState<number | undefined>(undefined);

  const onOpenChange = useCallback(() => setLog(undefined), [setLog]);
  const openLogSheet = useCallback((index: number) => setLog(index), [setLog]);

  const tableRows = useMemo((): JSX.Element[] => {
    return virtualItems.map((virtualRow, idx) => {
      const row = rows[virtualRow.index] as Row<TIndividualTest>;

      return (
        <TableRowMemoized
          openLogSheet={openLogSheet}
          getRowLink={getRowLink}
          row={row}
          index={idx}
          key={row.id}
          currentLog={currentLog}
        />
      );
    });
  }, [virtualItems, rows, openLogSheet, getRowLink, currentLog]);

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

  const handlePreviousItem = useCallback(() => {
    setLog(previousLog => {
      if (typeof previousLog === 'number' && previousLog > 0)
        return previousLog - 1;

      return previousLog;
    });
  }, [setLog]);

  const handleNextItem = useCallback(() => {
    setLog(previousLog => {
      if (
        typeof previousLog === 'number' &&
        previousLog < sortedItems.length - 1
      )
        return previousLog + 1;

      return previousLog;
    });
  }, [setLog, sortedItems.length]);

  const { data: dataTest, isLoading } = useTestDetails(
    sortedItems.length > 0 ? sortedItems[currentLog ?? 0].id : '',
  );

  const navigationLogsActions = useMemo(
    () => ({
      nextItem: handleNextItem,
      hasNext:
        typeof currentLog === 'number' && currentLog < sortedItems.length - 1,
      previousItem: handlePreviousItem,
      hasPrevious: !!currentLog,
      isLoading,
    }),
    [
      currentLog,
      isLoading,
      sortedItems.length,
      handleNextItem,
      handlePreviousItem,
    ],
  );

  return (
    <WrapperTable
      currentLog={currentLog}
      logExcerpt={dataTest?.log_excerpt}
      logUrl={dataTest?.log_url}
      navigationLogsActions={navigationLogsActions}
      onOpenChange={onOpenChange}
    >
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
    </WrapperTable>
  );
}
