import type {
  ColumnDef,
  ExpandedState,
  PaginationState,
  SortingState,
} from '@tanstack/react-table';
import {
  flexRender,
  getCoreRowModel,
  getExpandedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';

import { Fragment, useCallback, useMemo, useState } from 'react';

import { FormattedMessage, useIntl } from 'react-intl';

import DebounceInput from '@/components/DebounceInput/DebounceInput';
import BaseTable, { TableHead } from '@/components/Table/BaseTable';
import { PaginationInfo } from '@/components/Table/PaginationInfo';
import TableStatusFilter from '@/components/Table/TableStatusFilter';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';
import type { IAccordionItems } from '@/pages/TreeDetails/Tabs/Build/BuildAccordionContent';
import AccordionBuildContent from '@/pages/TreeDetails/Tabs/Build/BuildAccordionContent';
import type {
  AccordionItemBuilds,
  BuildsTableFilter,
} from '@/types/tree/TreeDetails';
import { possibleBuildsTableFilter } from '@/types/tree/TreeDetails';

import { Sheet } from '@/components/Sheet';
import { useBuildStatusCount } from '@/api/TreeDetails';
import { LogSheet } from '@/pages/TreeDetails/Tabs/LogSheet';

export interface IBuildsTable {
  buildItems: AccordionItemBuilds[];
  columns: ColumnDef<AccordionItemBuilds>[];
  onClickShowBuild: IAccordionItems['onClickShowBuild'];
  filter: BuildsTableFilter;
  onClickFilter: (filter: BuildsTableFilter) => void;
}

export function BuildsTable({
  buildItems,
  columns,
  onClickShowBuild,
  filter,
  onClickFilter,
}: IBuildsTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [expanded, setExpanded] = useState<ExpandedState>({});
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  const intl = useIntl();

  const rawData = useMemo((): AccordionItemBuilds[] => {
    return buildItems?.map(row => ({
      ...row,
      config: row.config ?? '-',
      compiler: row.compiler ?? '-',
      buildTime: row.buildTime ? (
        <span>
          {typeof row.buildTime === 'number'
            ? Math.floor(row.buildTime) + ' '
            : row.buildTime}
          <FormattedMessage id="global.seconds" />
        </span>
      ) : (
        '-'
      ),
      date: row.date,
    }));
  }, [buildItems]);

  const data = useMemo((): AccordionItemBuilds[] => {
    return filter === 'all'
      ? rawData
      : rawData?.filter(row => row.status && row.status === filter);
  }, [filter, rawData]);

  const filterCount = useMemo(() => {
    const count = possibleBuildsTableFilter.reduce(
      (acc, currentFilter) => {
        if (rawData)
          acc[currentFilter] = rawData?.reduce(
            (total, row) => (row.status === currentFilter ? total + 1 : total),
            0,
          );
        return acc;
      },
      {} as Record<(typeof possibleBuildsTableFilter)[number], number>,
    );
    count.all = rawData ? rawData.length : 0;

    return count;
  }, [rawData]);

  const filters = useMemo(
    () => [
      {
        label: intl.formatMessage(
          { id: 'global.allCount' },
          { count: filterCount[possibleBuildsTableFilter[2]] },
        ),
        value: possibleBuildsTableFilter[2],
        isSelected: filter === possibleBuildsTableFilter[2],
      },
      {
        label: intl.formatMessage(
          { id: 'global.successCount' },
          { count: filterCount[possibleBuildsTableFilter[1]] },
        ),
        value: possibleBuildsTableFilter[1],
        isSelected: filter === possibleBuildsTableFilter[1],
      },
      {
        label: intl.formatMessage(
          { id: 'global.failedCount' },
          { count: filterCount[possibleBuildsTableFilter[0]] },
        ),
        value: possibleBuildsTableFilter[0],
        isSelected: filter === possibleBuildsTableFilter[0],
      },
      {
        label: intl.formatMessage(
          { id: 'global.inconclusiveCount' },
          { count: filterCount[possibleBuildsTableFilter[3]] },
        ),
        value: possibleBuildsTableFilter[3],
        isSelected: filter === possibleBuildsTableFilter[3],
      },
    ],
    [intl, filterCount, filter],
  );

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: setPagination,
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getRowCanExpand: _ => true,
    getExpandedRowModel: getExpandedRowModel(),
    onExpandedChange: setExpanded,
    state: {
      sorting,
      pagination,
      expanded,
    },
  });

  const onSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) =>
      table.setGlobalFilter(String(e.target.value)),
    [table],
  );

  const groupHeaders = table.getHeaderGroups()[0]?.headers;
  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map(header => {
      return (
        <TableHead key={header.id} className="border-b px-0 font-bold">
          {header.isPlaceholder
            ? null
            : flexRender(header.column.columnDef.header, header.getContext())}
        </TableHead>
      );
    });
    // TODO: remove exhaustive-deps and change memo (all tables)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [groupHeaders, sorting]);

  const modelRows = table.getRowModel().rows;

  const sortedItems = useMemo(
    (): AccordionItemBuilds[] => modelRows.map(row => row.original),
    [modelRows],
  );

  const [currentLog, setLog] = useState<number | null>(null);

  const onOpenChange = useCallback(() => setLog(null), [setLog]);
  const openLogSheet = useCallback((index: number) => setLog(index), [setLog]);

  const tableBody = useMemo((): JSX.Element[] | JSX.Element => {
    {
      return modelRows?.length ? (
        modelRows.map((row, index) => {
          return (
            <Fragment key={row.id}>
              <TableRow
                className="cursor-pointer hover:bg-lightBlue"
                onClick={() => {
                  if (row.getCanExpand()) row.toggleExpanded();
                }}
                data-state={row.getIsExpanded() ? 'open' : 'closed'}
              >
                {row.getVisibleCells().map(cell => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
              {row.getIsExpanded() && (
                <TableRow>
                  <TableCell colSpan={groupHeaders.length} className="p-0">
                    <div className="max-h-[400px] w-full overflow-scroll border-b border-darkGray bg-lightGray p-8">
                      <AccordionBuildContent
                        accordionData={row.original}
                        onClickShowBuild={onClickShowBuild}
                        openLogSheet={() => openLogSheet(index)}
                      />
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </Fragment>
          );
        })
      ) : (
        <TableRow>
          <TableCell colSpan={columns.length} className="h-24 text-center">
            <FormattedMessage id="global.noResults" />
          </TableCell>
        </TableRow>
      );
    }
  }, [
    columns.length,
    groupHeaders.length,
    modelRows,
    onClickShowBuild,
    openLogSheet,
  ]);

  const handlePreviousItem = useCallback(() => {
    setLog(c => {
      if (c !== null && c > 0) return c - 1;

      return c;
    });
  }, [setLog]);

  const handleNextItem = useCallback(() => {
    setLog(c => {
      if (c !== null && c < sortedItems.length - 1) return c + 1;

      return c;
    });
  }, [setLog, sortedItems.length]);

  const { data: dataBuildCount, isLoading } = useBuildStatusCount(
    { buildId: sortedItems[currentLog ?? 0]?.id ?? '' },
    { enabled: !!sortedItems[currentLog ?? 0]?.id },
  );

  const navigationLogsActions = useMemo(
    () => ({
      nextItem: handleNextItem,
      hasNext: currentLog !== null && currentLog < sortedItems.length - 1,
      previousItem: handlePreviousItem,
      hasPrevious: currentLog !== null && currentLog > 0,
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
    <div className="flex flex-col gap-6 pb-4">
      <div className="flex justify-between">
        <TableStatusFilter filters={filters} onClickBuild={onClickFilter} />
        <DebounceInput
          debouncedSideEffect={onSearchChange}
          className="w-50"
          type="text"
          placeholder={intl.formatMessage({ id: 'global.search' })}
        />
      </div>
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableBody}</TableBody>

        <Sheet open={currentLog !== null} onOpenChange={onOpenChange}>
          <LogSheet
            logExcerpt={dataBuildCount?.log_excerpt}
            logUrl={sortedItems[currentLog ?? 0]?.buildLogs}
            navigationLogsActions={navigationLogsActions}
          />
        </Sheet>
      </BaseTable>
      <PaginationInfo
        table={table}
        data={data}
        intlLabel="treeDetails.builds"
      />
    </div>
  );
}
