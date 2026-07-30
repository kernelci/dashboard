import type {
  ColumnDef,
  ExpandedState,
  Row,
  SortingState,
} from '@tanstack/react-table';
import {
  flexRender,
  getCoreRowModel,
  getExpandedRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type JSX,
} from 'react';

import { FormattedMessage, useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';

import type { PossibleTableFilters } from '@/types/tree/TreeDetails';
import { possibleTableFilters } from '@/types/tree/TreeDetails';

import type { TestHistory, TIndividualTest } from '@/types/general';

import { TableBody, TableCell, TableRow } from '@/components/ui/table';

import {
  DumbBaseTable,
  DumbTableHeader,
  TableHead,
} from '@/components/Table/BaseTable';

import type { TableKeys } from '@/utils/constants/tables';

import { TableTopFilters } from '@/components/Table/TableTopFilters';

import type { TStatusFilters } from '@/components/Table/TableStatusFilter';

import type { TableGroupingMode } from '@/components/Table/TableGroupingControls';

import { TableRowMemoized } from '@/components/Table/TableComponents';

import { useTestIssues } from '@/api/testDetails';
import { useLogData } from '@/hooks/useLogData';
import WrapperTableWithLogSheet from '@/pages/TreeDetails/Tabs/WrapperTableWithLogSheet';

import {
  adaptColumnsForUnifiedTable,
  defaultInnerColumns,
} from './DefaultTestsColumns';
import { buildTestsTree } from './buildTestsTree';
import {
  pruneTree,
  computeGlobalCounts,
  matchByStatus,
  matchByPathSubstring,
  matchTestByPathSubstring,
} from './filterTestsTree';
import { collapseSingleChildChains } from './collapseTestsTree';
import {
  buildUnifiedTestsTree,
  flattenTestsToLeafRows,
} from './buildUnifiedTestsTree';
import type { UnifiedTestRow } from './types';

const ESTIMATED_ROW_HEIGHT = 60;
const VIRTUALIZER_OVERSCAN = 5;

export interface ITestsTable {
  tableKey: TableKeys;
  testHistory?: TestHistory[];
  onClickFilter: (filter: PossibleTableFilters) => void;
  filter: PossibleTableFilters;
  innerColumns?: ColumnDef<TIndividualTest>[];
  getRowLink: (testId: TestHistory['id']) => LinkProps;
  updatePathFilter?: (pathFilter: string) => void;
  currentPathFilter?: string;
}

export function TestsTable({
  testHistory,
  onClickFilter,
  filter,
  innerColumns = defaultInnerColumns,
  getRowLink,
  updatePathFilter,
  currentPathFilter,
}: ITestsTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [expanded, setExpanded] = useState<ExpandedState>({});
  const [groupingMode, setGroupingMode] =
    useState<TableGroupingMode>('grouped');
  const pathFilter = currentPathFilter?.trim();

  const intl = useIntl();

  const sortingRef = useRef(sorting);
  sortingRef.current = sorting;

  const getSortDirection = useCallback((columnId: string) => {
    const entry = sortingRef.current.find(item => item.id === columnId);
    if (!entry) {
      return false as const;
    }
    return entry.desc ? ('desc' as const) : ('asc' as const);
  }, []);

  const columns = useMemo(
    () => adaptColumnsForUnifiedTable(innerColumns, getSortDirection),
    [getSortDirection, innerColumns],
  );

  const rawTree = useMemo(() => buildTestsTree(testHistory), [testHistory]);

  const pathFilteredTree = useMemo(() => {
    if (!pathFilter) {
      return rawTree;
    }
    return pruneTree(rawTree, {
      matchTest: matchTestByPathSubstring(pathFilter),
      matchNodePath: matchByPathSubstring(pathFilter),
    });
  }, [rawTree, pathFilter]);

  const globalStatusGroup = useMemo(
    () => computeGlobalCounts(pathFilteredTree),
    [pathFilteredTree],
  );

  const filteredTree = useMemo(() => {
    const filtered =
      filter === 'all'
        ? pathFilteredTree
        : pruneTree(pathFilteredTree, { matchTest: matchByStatus(filter) });
    return collapseSingleChildChains(filtered);
  }, [pathFilteredTree, filter]);

  const groupedData = useMemo(
    () => buildUnifiedTestsTree(filteredTree),
    [filteredTree],
  );
  const flatData = useMemo(
    () => flattenTestsToLeafRows(filteredTree),
    [filteredTree],
  );
  const data = groupingMode === 'ungrouped' ? flatData : groupedData;

  useEffect(() => {
    setExpanded({});
  }, [groupingMode, filteredTree]);

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getSubRows: row => row.subRows,
    getRowCanExpand: row =>
      row.original.kind === 'group' && (row.original.subRows?.length ?? 0) > 0,
    getExpandedRowModel: getExpandedRowModel(),
    onExpandedChange: setExpanded,
    getRowId: row => row.id,
    state: {
      sorting,
      expanded,
    },
  });

  const filterCount: Record<PossibleTableFilters, number> = useMemo(
    () => ({
      all: globalStatusGroup.total_tests,
      success: globalStatusGroup.pass_tests,
      failed: globalStatusGroup.fail_tests,
      inconclusive:
        globalStatusGroup.total_tests -
        globalStatusGroup.pass_tests -
        globalStatusGroup.fail_tests,
    }),
    [globalStatusGroup],
  );

  const filters: TStatusFilters[] = useMemo(
    () => [
      {
        label: intl.formatMessage(
          { id: 'global.allCount' },
          { count: filterCount[possibleTableFilters[0]] },
        ),
        value: possibleTableFilters[0],
        isSelected: filter === possibleTableFilters[0],
      },
      {
        label: intl.formatMessage(
          { id: 'global.successCount' },
          { count: filterCount[possibleTableFilters[1]] },
        ),
        value: possibleTableFilters[1],
        isSelected: filter === possibleTableFilters[1],
      },
      {
        label: intl.formatMessage(
          { id: 'global.failedCount' },
          { count: filterCount[possibleTableFilters[2]] },
        ),
        value: possibleTableFilters[2],
        isSelected: filter === possibleTableFilters[2],
      },
      {
        label: intl.formatMessage(
          { id: 'global.inconclusiveCount' },
          { count: filterCount[possibleTableFilters[3]] },
        ),
        value: possibleTableFilters[3],
        isSelected: filter === possibleTableFilters[3],
      },
    ],
    [filterCount, intl, filter],
  );

  const onSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const trimmedPathFilter = e.target.value.trim();
      if (updatePathFilter) {
        updatePathFilter(trimmedPathFilter);
      }
    },
    [updatePathFilter],
  );

  const onExpandAll = useCallback(() => {
    table.toggleAllRowsExpanded(true);
  }, [table]);

  const onCollapseAll = useCallback(() => {
    table.toggleAllRowsExpanded(false);
  }, [table]);

  const onGroupingModeChange = useCallback((mode: TableGroupingMode) => {
    setGroupingMode(mode);
  }, []);

  const groupingControls = useMemo(
    () => ({
      mode: groupingMode,
      onModeChange: onGroupingModeChange,
      onExpandAll,
      onCollapseAll,
    }),
    [groupingMode, onCollapseAll, onExpandAll, onGroupingModeChange],
  );

  const groupHeaders = table.getHeaderGroups()[0]?.headers;
  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map(header => {
      const headerComponent = header.isPlaceholder
        ? null
        : flexRender(header.column.columnDef.header, {
            ...header.getContext(),
            sorting,
          });
      return (
        <TableHead key={header.id} className="border-b px-2 font-bold">
          {headerComponent}
        </TableHead>
      );
    });
  }, [groupHeaders, sorting]);

  const modelRows = table.getRowModel().rows;

  const { leafRows, leafIndexById } = useMemo(() => {
    const leaves: Row<UnifiedTestRow>[] = [];
    const indexById = new Map<string, number>();

    for (const row of modelRows) {
      if (row.original.kind === 'leaf') {
        indexById.set(row.original.id, leaves.length);
        leaves.push(row);
      }
    }

    return { leafRows: leaves, leafIndexById: indexById };
  }, [modelRows]);

  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: modelRows.length,
    estimateSize: () => ESTIMATED_ROW_HEIGHT,
    getScrollElement: () => parentRef.current,
    overscan: VIRTUALIZER_OVERSCAN,
  });
  const virtualItems = virtualizer.getVirtualItems();

  // Prefer spacer <tr>s over outer padding so sticky headers stay correct.
  // https://tanstack.com/virtual/latest/docs/framework/react/examples/table
  const [paddingTop, paddingBottom] = useMemo((): [number, number] => {
    if (virtualItems.length === 0) {
      return [0, 0];
    }
    return [
      virtualItems[0].start,
      virtualizer.getTotalSize() - virtualItems[virtualItems.length - 1].end,
    ];
  }, [virtualItems, virtualizer]);

  const spacerCellStyle = useMemo(
    (): CSSProperties => ({
      padding: 0,
      border: 0,
    }),
    [],
  );

  const [currentLogId, setLog] = useState<string | undefined>(undefined);

  const currentLog = useMemo(() => {
    if (currentLogId === undefined) {
      return undefined;
    }
    return leafIndexById.get(currentLogId);
  }, [leafIndexById, currentLogId]);

  const activeLogId = currentLog !== undefined ? currentLogId ?? '' : '';

  const onOpenChange = useCallback(() => setLog(undefined), []);
  const openLogSheet = useCallback(
    (index: number) => setLog(leafRows[index]?.original.id),
    [leafRows],
  );

  useEffect(() => {
    if (currentLogId !== undefined && !leafIndexById.has(currentLogId)) {
      setLog(undefined);
    }
  }, [currentLogId, leafIndexById]);

  const handlePreviousItem = useCallback(() => {
    if (currentLog !== undefined && currentLog > 0) {
      setLog(leafRows[currentLog - 1]?.original.id);
    }
  }, [currentLog, leafRows]);

  const handleNextItem = useCallback(() => {
    if (currentLog !== undefined && currentLog < leafRows.length - 1) {
      setLog(leafRows[currentLog + 1]?.original.id);
    }
  }, [currentLog, leafRows]);

  const { data: logData, isLoading } = useLogData(activeLogId, 'test');

  const navigationLogsActions = useMemo(
    () => ({
      nextItem: handleNextItem,
      hasNext:
        typeof currentLog === 'number' && currentLog < leafRows.length - 1,
      previousItem: handlePreviousItem,
      hasPrevious: !!currentLog,
      isLoading,
    }),
    [
      currentLog,
      isLoading,
      leafRows.length,
      handleNextItem,
      handlePreviousItem,
    ],
  );

  const currentLinkProps = useMemo(() => {
    return getRowLink(logData?.id ?? '');
  }, [logData?.id, getRowLink]);

  const { data: issues, status, error } = useTestIssues(activeLogId);

  const tableRows = useMemo((): JSX.Element[] | JSX.Element => {
    if (!modelRows.length) {
      return (
        <TableRow>
          <TableCell colSpan={columns.length} className="h-24 text-center">
            <FormattedMessage id="global.noResults" />
          </TableCell>
        </TableRow>
      );
    }

    const rows: JSX.Element[] = [];

    if (paddingTop > 0) {
      rows.push(
        <tr key="virtual-padding-top" aria-hidden>
          <td
            colSpan={columns.length}
            style={{ ...spacerCellStyle, height: paddingTop }}
          />
        </tr>,
      );
    }

    for (const virtualRow of virtualItems) {
      const row = modelRows[virtualRow.index];
      if (!row) {
        continue;
      }

      if (row.original.kind === 'group') {
        rows.push(
          <TableRow
            key={row.id}
            className="group hover:bg-light-blue cursor-pointer"
            onClick={() => {
              if (row.getCanExpand()) {
                row.toggleExpanded();
              }
            }}
            data-state={row.getIsExpanded() ? 'open' : 'closed'}
            data-depth={row.depth}
          >
            {row.getVisibleCells().map(cell => (
              <TableCell key={cell.id}>
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </TableCell>
            ))}
          </TableRow>,
        );
        continue;
      }

      rows.push(
        <TableRowMemoized<UnifiedTestRow>
          key={row.id}
          index={leafIndexById.get(row.original.id) ?? -1}
          row={row}
          openLogSheet={openLogSheet}
          currentLog={currentLog}
          getRowLink={getRowLink}
        />,
      );
    }

    if (paddingBottom > 0) {
      rows.push(
        <tr key="virtual-padding-bottom" aria-hidden>
          <td
            colSpan={columns.length}
            style={{ ...spacerCellStyle, height: paddingBottom }}
          />
        </tr>,
      );
    }

    return rows;
  }, [
    columns.length,
    currentLog,
    getRowLink,
    leafIndexById,
    modelRows,
    openLogSheet,
    paddingBottom,
    paddingTop,
    spacerCellStyle,
    virtualItems,
  ]);

  return (
    <WrapperTableWithLogSheet
      currentLog={currentLog}
      logData={logData}
      navigationLogsActions={navigationLogsActions}
      onOpenChange={onOpenChange}
      currentLinkProps={currentLinkProps}
      issues={issues}
      status={status}
      error={error}
    >
      <TableTopFilters
        key="testsTableSearch"
        filters={filters}
        onClickFilter={onClickFilter}
        onSearchChange={onSearchChange}
        currentPathFilter={currentPathFilter}
        groupingControls={groupingControls}
      />
      <div ref={parentRef} className="max-h-150 overflow-auto">
        <DumbBaseTable containerClassName="overflow-visible h-full bg-white">
          <DumbTableHeader className="sticky top-0 z-10">
            {tableHeaders}
          </DumbTableHeader>
          <TableBody>{tableRows}</TableBody>
        </DumbBaseTable>
      </div>
    </WrapperTableWithLogSheet>
  );
}
