import type {
  Cell,
  ColumnDef,
  ExpandedState,
  Header,
  PaginationState,
  Row,
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

import { Fragment, memo, useCallback, useMemo, useState } from 'react';

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

import { useBuildStatusCount } from '@/api/TreeDetails';
import WrapperTable from '@/pages/TreeDetails/Tabs/WrapperTable';
import { cn } from '@/lib/utils';

export interface IBuildsTable {
  buildItems: AccordionItemBuilds[];
  columns: ColumnDef<AccordionItemBuilds>[];
  onClickShowBuild: IAccordionItems['onClickShowBuild'];
  filter: BuildsTableFilter;
  onClickFilter: (filter: BuildsTableFilter) => void;
}

const TableCellComponent = ({
  row,
  cell,
  rowIndex,
  openLogSheet,
}: {
  row: Row<AccordionItemBuilds>;
  cell: Cell<AccordionItemBuilds, unknown>;
  rowIndex: number;
  openLogSheet: (index: number) => void;
}): JSX.Element => {
  const handleClickCell = useCallback(() => {
    if (cell.column.id === 'status') {
      openLogSheet(rowIndex);
    } else if (row.getCanExpand()) {
      row.toggleExpanded();
    }
  }, [cell, row, rowIndex, openLogSheet]);

  return (
    <TableCell key={cell.id} onClick={handleClickCell}>
      {flexRender(cell.column.columnDef.cell, cell.getContext())}
    </TableCell>
  );
};

const AccordionBuildContentComponent = ({
  row,
  rowIndex,
  openLogSheet,
  onClickShowBuild,
}: {
  row: Row<AccordionItemBuilds>;
  rowIndex: number;
  openLogSheet: (index: number) => void;
  onClickShowBuild: IAccordionItems['onClickShowBuild'];
}): JSX.Element => {
  const handleOpenLogSheet = useCallback(
    () => openLogSheet(rowIndex),
    [rowIndex, openLogSheet],
  );

  return (
    <AccordionBuildContent
      accordionData={row.original}
      onClickShowBuild={onClickShowBuild}
      openLogSheet={handleOpenLogSheet}
    />
  );
};

const TableRowComponent = ({
  index,
  row,
  groupHeaders,
  onClickShowBuild,
  openLogSheet,
  currentLog,
  isExpanded,
}: {
  index: number;
  row: Row<AccordionItemBuilds>;
  currentLog?: number;
  openLogSheet: (index: number) => void;
  groupHeaders: Header<AccordionItemBuilds, unknown>[];
  onClickShowBuild: IAccordionItems['onClickShowBuild'];
  isExpanded: boolean;
}): JSX.Element => {
  const className = index === currentLog ? 'bg-lightBlue' : undefined;

  return (
    <Fragment key={row.id}>
      <TableRow
        className={cn('cursor-pointer hover:bg-lightBlue', className)}
        data-state={isExpanded ? 'open' : 'closed'}
      >
        {row.getVisibleCells().map((cell, cellIdx) => (
          <TableCellMemoized
            key={cellIdx}
            cell={cell}
            rowIndex={index}
            row={row}
            openLogSheet={openLogSheet}
          />
        ))}
      </TableRow>
      {isExpanded && (
        <TableRow>
          <TableCell colSpan={groupHeaders.length} className="p-0">
            <div className="max-h-[400px] w-full overflow-scroll border-b border-darkGray bg-lightGray p-8">
              <AccordionBuildContentMemoized
                row={row}
                rowIndex={index}
                onClickShowBuild={onClickShowBuild}
                openLogSheet={openLogSheet}
              />
            </div>
          </TableCell>
        </TableRow>
      )}
    </Fragment>
  );
};

const TableCellMemoized = memo(TableCellComponent);
const AccordionBuildContentMemoized = memo(AccordionBuildContentComponent);
const TableRowMemoized = memo(TableRowComponent);

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

  const [currentLog, setLog] = useState<number | undefined>(undefined);

  const onOpenChange = useCallback(() => setLog(undefined), [setLog]);
  const openLogSheet = useCallback((index: number) => setLog(index), [setLog]);

  const tableBody = useMemo((): JSX.Element[] | JSX.Element => {
    {
      return modelRows?.length ? (
        modelRows.map((row, index) => {
          return (
            <TableRowMemoized
              key={index}
              index={index}
              row={row}
              isExpanded={row.getIsExpanded()}
              groupHeaders={groupHeaders}
              onClickShowBuild={onClickShowBuild}
              openLogSheet={openLogSheet}
              currentLog={currentLog}
            />
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
    modelRows,
    columns.length,
    groupHeaders,
    onClickShowBuild,
    openLogSheet,
    currentLog,
  ]);

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

  const { data: dataBuildCount, isLoading } = useBuildStatusCount(
    { buildId: sortedItems.length > 0 ? sortedItems[currentLog ?? 0]?.id : '' },
    { enabled: sortedItems.length > 0 && !!sortedItems[currentLog ?? 0]?.id },
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
      logExcerpt={dataBuildCount?.log_excerpt}
      logUrl={
        sortedItems.length > 0 ? sortedItems[currentLog ?? 0].buildLogs : ''
      }
      navigationLogsActions={navigationLogsActions}
      onOpenChange={onOpenChange}
    >
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
      </BaseTable>
      <PaginationInfo
        table={table}
        data={data}
        intlLabel="treeDetails.builds"
      />
    </WrapperTable>
  );
}
