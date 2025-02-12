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
import { useCallback, useMemo, useRef, useState } from 'react';

import type { LinkProps } from '@tanstack/react-router';

import type { TestHistory, TIndividualTest } from '@/types/general';

import { DumbTableHeader, TableHead } from '@/components/Table/BaseTable';
import { TableBody } from '@/components/ui/table';

import { useTestDetails, useTestIssues } from '@/api/testDetails';
import WrapperTableWithLogSheet from '@/pages/TreeDetails/Tabs/WrapperTableWithLogSheet';

import { TableRowMemoized } from '@/components/Table/TableComponents';

const ESTIMATED_ROW_HEIGHT = 60;

interface IIndividualTestsTable {
  columns: ColumnDef<TIndividualTest>[];
  data: TIndividualTest[];
  getRowLink: (testId: TestHistory['id']) => LinkProps;
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

  const modelRows = table.getRowModel().rows;
  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: modelRows.length,
    estimateSize: () => ESTIMATED_ROW_HEIGHT,
    getScrollElement: () => parentRef.current,
    overscan: 5,
  });
  const virtualItems = virtualizer.getVirtualItems();

  const originalItems = useMemo(
    (): TIndividualTest[] => modelRows.map(row => row.original),
    [modelRows],
  );

  const [currentLog, setLog] = useState<number | undefined>(undefined);

  const onOpenChange = useCallback(() => setLog(undefined), [setLog]);
  const openLogSheet = useCallback((index: number) => setLog(index), [setLog]);

  const tableRows = useMemo((): JSX.Element[] => {
    return virtualItems.map((virtualRow, idx) => {
      const row = modelRows[virtualRow.index] as Row<TIndividualTest>;
      return (
        <TableRowMemoized<TIndividualTest>
          key={row.id}
          index={idx}
          row={row}
          openLogSheet={openLogSheet}
          currentLog={currentLog}
          getRowLink={getRowLink}
        />
      );
    });
  }, [virtualItems, modelRows, openLogSheet, getRowLink, currentLog]);

  // if more performance is needed, try using translate as in the example from tanstack virtual instead of padding
  // https://tanstack.com/virtual/latest/docs/framework/react/examples/table
  const [firstRowStyle, lastRowStyle]: [CSSProperties, CSSProperties] =
    useMemo(() => {
      if (virtualItems.length === 0) {
        return [{}, {}];
      }
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
      if (typeof previousLog === 'number' && previousLog > 0) {
        return previousLog - 1;
      }

      return previousLog;
    });
  }, [setLog]);

  const handleNextItem = useCallback(() => {
    setLog(previousLog => {
      if (
        typeof previousLog === 'number' &&
        previousLog < originalItems.length - 1
      ) {
        return previousLog + 1;
      }

      return previousLog;
    });
  }, [setLog, originalItems.length]);

  const { data: dataTest, isLoading } = useTestDetails(
    originalItems.length > 0 ? originalItems[currentLog ?? 0].id : '',
  );

  const navigationLogsActions = useMemo(
    () => ({
      nextItem: handleNextItem,
      hasNext:
        typeof currentLog === 'number' && currentLog < originalItems.length - 1,
      previousItem: handlePreviousItem,
      hasPrevious: !!currentLog,
      isLoading,
    }),
    [
      currentLog,
      isLoading,
      originalItems.length,
      handleNextItem,
      handlePreviousItem,
    ],
  );

  const currentLinkProps = useMemo(() => {
    return getRowLink(dataTest?.id ?? '');
  }, [dataTest?.id, getRowLink]);

  const {
    data: issues,
    status,
    error,
  } = useTestIssues(
    currentLog !== undefined ? originalItems[currentLog]?.id : '',
  );

  return (
    <WrapperTableWithLogSheet
      currentLog={currentLog}
      logExcerpt={dataTest?.log_excerpt}
      logUrl={dataTest?.log_url}
      navigationLogsActions={navigationLogsActions}
      onOpenChange={onOpenChange}
      currentLinkProps={currentLinkProps}
      issues={issues}
      status={status}
      error={error}
      wrapperClassName="pb-0"
    >
      <div
        ref={parentRef}
        className="bg-light-gray max-h-[400px] max-w-full overflow-auto p-8"
      >
        <div className="border-dark-gray rounded-lg border-x border-t bg-white text-sm text-black">
          <div style={firstRowStyle} />
          <table className="w-full">
            <DumbTableHeader>{tableHeaders}</DumbTableHeader>
            <TableBody>{tableRows}</TableBody>
          </table>
          <div style={lastRowStyle} />
        </div>
      </div>
    </WrapperTableWithLogSheet>
  );
}
