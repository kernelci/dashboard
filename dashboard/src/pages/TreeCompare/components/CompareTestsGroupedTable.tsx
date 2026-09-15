import {
  flexRender,
  getCoreRowModel,
  getExpandedRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type ExpandedState,
  type SortingState,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';

import {
  useCallback,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type JSX,
} from 'react';

import { FormattedMessage } from 'react-intl';

import type { TestHistory, TIndividualTest } from '@/types/general';
import type {
  CompareItemStatus,
  CompareRowChange,
  CompareStatusCounts,
  CompareTestFailureRow,
} from '@/types/tree/TreeCompare';

import {
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { TableHeader as SortableTableHeader } from '@/components/Table/TableHeader';

import { buildTestsTree } from '@/components/TestsTable/buildTestsTree';
import { buildUnifiedTestsTree } from '@/components/TestsTable/buildUnifiedTestsTree';
import { collapseSingleChildChains } from '@/components/TestsTable/collapseTestsTree';
import { adaptColumnsForUnifiedTable } from '@/components/TestsTable/DefaultTestsColumns';
import type { UnifiedTestRow } from '@/components/TestsTable/types';
import { GroupedTestStatus } from '@/components/Status/Status';

import { cn } from '@/lib/utils';

import {
  CompareChangeBadge,
  CompareStatusChip,
  isFailureHighlight,
} from './CompareChangeDisplay';
import { CompareTableSearch, rowMatchesSearch } from './compareTableShared';

const ESTIMATED_ROW_HEIGHT = 56;
const VIRTUALIZER_OVERSCAN = 10;
const VIRTUAL_TABLE_MAX_HEIGHT = 480;
const TESTS_COLGROUP = (
  <colgroup>
    <col className="w-[30%]" />
    <col className="w-[14%]" />
    <col className="w-[12%]" />
    <col className="w-[12%]" />
    <col className="w-[12%]" />
    <col className="w-[4%]" />
    <col className="w-[12%]" />
    <col className="w-[14%]" />
  </colgroup>
);

const EMPTY_COMPARE_COUNTS: CompareStatusCounts = {
  pass: 0,
  fail: 0,
  inconclusive: 0,
};

function bucketCompareItemStatus(
  status: CompareItemStatus,
): keyof CompareStatusCounts {
  if (status === 'PASS') {
    return 'pass';
  }
  if (status === 'FAIL') {
    return 'fail';
  }
  return 'inconclusive';
}

type GroupSideCounts = {
  sideA: CompareStatusCounts;
  sideB: CompareStatusCounts;
};

/** Group rows show per-side status counts, which path summaries cannot express. */
function collectGroupSideCounts(
  rows: UnifiedTestRow[],
  into: Map<string, GroupSideCounts>,
): GroupSideCounts {
  const totals: GroupSideCounts = {
    sideA: { ...EMPTY_COMPARE_COUNTS },
    sideB: { ...EMPTY_COMPARE_COUNTS },
  };

  for (const row of rows) {
    if (row.kind === 'leaf') {
      for (const side of ['sideA', 'sideB'] as const) {
        const status = row[side] as CompareItemStatus | undefined;
        if (status) {
          totals[side][bucketCompareItemStatus(status)] += 1;
        }
      }
      continue;
    }

    const subTotals = collectGroupSideCounts(row.subRows ?? [], into);
    into.set(row.id, subTotals);
    for (const side of ['sideA', 'sideB'] as const) {
      for (const bucket of ['pass', 'fail', 'inconclusive'] as const) {
        totals[side][bucket] += subTotals[side][bucket];
      }
    }
  }

  return totals;
}

const compareLeafColumns: ColumnDef<TIndividualTest>[] = [
  {
    accessorKey: 'path',
    header: ({ column }): JSX.Element => (
      <SortableTableHeader column={column} intlKey="global.path" />
    ),
  },
  {
    id: 'config',
    accessorKey: 'config',
    header: ({ column }): JSX.Element => (
      <SortableTableHeader column={column} intlKey="global.config" />
    ),
    cell: ({ getValue }): string => String(getValue() ?? ''),
  },
  {
    id: 'arch',
    accessorKey: 'arch',
    header: ({ column }): JSX.Element => (
      <SortableTableHeader column={column} intlKey="global.architecture" />
    ),
    cell: ({ getValue }): string => String(getValue() ?? ''),
  },
  {
    id: 'platform',
    accessorKey: 'platform',
    header: ({ column }): JSX.Element => (
      <SortableTableHeader column={column} intlKey="global.hardware" />
    ),
    cell: ({ getValue }): string => String(getValue() ?? ''),
  },
];

/** Rendered after the side columns, so it is adapted separately. */
const changeColumn: ColumnDef<TIndividualTest> = {
  id: 'change',
  accessorKey: 'change',
  header: ({ column }): JSX.Element => (
    <div className="flex justify-center">
      <SortableTableHeader
        column={column}
        intlKey="treeCompare.failures.change"
      />
    </div>
  ),
  cell: ({ getValue }): JSX.Element | null => {
    const change = getValue() as CompareRowChange | undefined;
    if (!change) {
      return null;
    }
    return (
      <div className="flex justify-center">
        <CompareChangeBadge change={change} />
      </div>
    );
  },
};

function createCompareSideColumns(
  groupSideCounts: Map<string, GroupSideCounts>,
): ColumnDef<UnifiedTestRow>[] {
  const groupedSideStatus = (counts: CompareStatusCounts): JSX.Element => (
    <GroupedTestStatus
      preCalculatedGroupedStatus={{
        successCount: counts.pass,
        failedCount: counts.fail,
        inconclusiveCount: counts.inconclusive,
      }}
    />
  );

  const sideStatus = (
    row: UnifiedTestRow,
    side: 'sideA' | 'sideB',
  ): CompareItemStatus | undefined =>
    row.kind === 'leaf'
      ? (row[side] as CompareItemStatus | undefined)
      : undefined;

  const sortBySide = (
    side: 'sideA' | 'sideB',
  ): ColumnDef<UnifiedTestRow>['sortingFn'] => {
    return (rowA, rowB) =>
      String(sideStatus(rowA.original, side) ?? '').localeCompare(
        String(sideStatus(rowB.original, side) ?? ''),
      );
  };

  return [
    {
      id: 'sideA',
      accessorFn: (row): CompareItemStatus | undefined =>
        sideStatus(row, 'sideA'),
      header: ({ column }): JSX.Element => (
        <div className="flex justify-center">
          <SortableTableHeader column={column} intlKey="treeCompare.sideA" />
        </div>
      ),
      cell: ({ row }): JSX.Element | null => {
        if (row.original.kind === 'group') {
          const counts = groupSideCounts.get(row.original.id)?.sideA;
          if (!counts) {
            return null;
          }
          return (
            <div className="flex justify-center">
              {groupedSideStatus(counts)}
            </div>
          );
        }
        const sideA = sideStatus(row.original, 'sideA');
        if (!sideA) {
          return null;
        }
        return (
          <div className="flex justify-center">
            <CompareStatusChip status={sideA} />
          </div>
        );
      },
      sortingFn: sortBySide('sideA'),
    },
    {
      id: 'sideArrow',
      header: (): null => null,
      cell: (): JSX.Element => (
        <span className="text-dim-gray block text-center">→</span>
      ),
      enableSorting: false,
    },
    {
      id: 'sideB',
      accessorFn: (row): CompareItemStatus | undefined =>
        sideStatus(row, 'sideB'),
      header: ({ column }): JSX.Element => (
        <div className="flex justify-center">
          <SortableTableHeader column={column} intlKey="treeCompare.sideB" />
        </div>
      ),
      cell: ({ row }): JSX.Element | null => {
        if (row.original.kind === 'group') {
          const counts = groupSideCounts.get(row.original.id)?.sideB;
          if (!counts) {
            return null;
          }
          return (
            <div className="flex justify-center">
              {groupedSideStatus(counts)}
            </div>
          );
        }
        const sideB = sideStatus(row.original, 'sideB');
        if (!sideB) {
          return null;
        }
        return (
          <div className="flex justify-center">
            <CompareStatusChip status={sideB} />
          </div>
        );
      },
      sortingFn: sortBySide('sideB'),
    },
  ];
}

function compareRowToHistory(row: CompareTestFailureRow): TestHistory {
  return {
    id: row.id,
    path: row.path,
    status: 'NULL' as const,
    config: row.config,
    arch: row.arch,
    platform: row.hardware,
    sideA: row.sideA,
    sideB: row.sideB,
    change: row.change,
  };
}

export function CompareTestsGroupedTable({
  rows,
}: {
  rows: CompareTestFailureRow[];
}): JSX.Element {
  const [search, setSearch] = useState('');
  const [expanded, setExpanded] = useState<ExpandedState>({});
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'path', desc: false },
  ]);

  const onSearchChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setSearch(event.target.value);
    },
    [],
  );

  const filteredRows = useMemo(
    () =>
      rows.filter(row =>
        rowMatchesSearch(
          [
            row.path,
            row.config,
            row.arch,
            row.hardware,
            row.sideA,
            row.sideB,
            row.change,
          ],
          search,
        ),
      ),
    [rows, search],
  );

  const data = useMemo(() => {
    const tree = buildTestsTree(filteredRows.map(compareRowToHistory));
    return buildUnifiedTestsTree(collapseSingleChildChains(tree));
  }, [filteredRows]);

  const groupSideCounts = useMemo(() => {
    const byGroupId = new Map<string, GroupSideCounts>();
    collectGroupSideCounts(data, byGroupId);
    return byGroupId;
  }, [data]);

  const columns = useMemo(
    () => [
      ...adaptColumnsForUnifiedTable(compareLeafColumns),
      ...createCompareSideColumns(groupSideCounts),
      ...adaptColumnsForUnifiedTable([changeColumn]),
    ],
    [groupSideCounts],
  );

  const table = useReactTable({
    data,
    columns,
    enableSortingRemoval: false,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getSubRows: row => row.subRows,
    getRowCanExpand: row =>
      row.original.kind === 'group' && (row.original.subRows?.length ?? 0) > 0,
    getExpandedRowModel: getExpandedRowModel(),
    onExpandedChange: setExpanded,
    getRowId: row => row.id,
    state: { expanded, sorting },
  });

  const modelRows = table.getRowModel().rows;
  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: modelRows.length,
    estimateSize: () => ESTIMATED_ROW_HEIGHT,
    getScrollElement: () => parentRef.current,
    overscan: VIRTUALIZER_OVERSCAN,
  });
  const virtualItems = virtualizer.getVirtualItems();

  const paddingTop = virtualItems.length > 0 ? virtualItems[0].start : 0;
  const paddingBottom =
    virtualItems.length > 0
      ? virtualizer.getTotalSize() - virtualItems[virtualItems.length - 1].end
      : 0;

  const spacerCellStyle: CSSProperties = { padding: 0, border: 0 };
  const colCount = columns.length;

  const groupHeaders = table.getHeaderGroups()[0]?.headers ?? [];

  return (
    <div>
      <CompareTableSearch onSearchChange={onSearchChange} />
      <div
        ref={parentRef}
        className="overflow-auto rounded-lg border border-gray-200 bg-white"
        style={{ height: VIRTUAL_TABLE_MAX_HEIGHT }}
      >
        <table className="w-full table-fixed border-separate border-spacing-0 text-sm">
          {TESTS_COLGROUP}
          <TableHeader className="bg-light-gray sticky top-0 z-10 [&_tr]:border-b [&_tr]:border-gray-200">
            <TableRow className="bg-light-gray hover:bg-light-gray">
              {groupHeaders.map(header => (
                <TableHead
                  key={header.id}
                  className="bg-light-gray font-semibold"
                >
                  {header.isPlaceholder
                    ? null
                    : flexRender(header.column.columnDef.header, {
                        ...header.getContext(),
                        sorting,
                      })}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {modelRows.length === 0 ? (
              <TableRow>
                <TableCell colSpan={colCount} className="h-24 text-center">
                  <FormattedMessage id="global.noResults" />
                </TableCell>
              </TableRow>
            ) : (
              <>
                {paddingTop > 0 && (
                  <tr aria-hidden>
                    <td
                      colSpan={colCount}
                      style={{ ...spacerCellStyle, height: paddingTop }}
                    />
                  </tr>
                )}
                {virtualItems.map(virtualRow => {
                  const row = modelRows[virtualRow.index];
                  if (!row) {
                    return null;
                  }
                  const highlight =
                    row.original.kind === 'leaf' &&
                    isFailureHighlight(row.original.change as CompareRowChange);

                  if (row.original.kind === 'group') {
                    return (
                      <TableRow
                        key={row.id}
                        className="group hover:bg-light-blue cursor-pointer"
                        onClick={() => {
                          if (row.getCanExpand()) {
                            row.toggleExpanded();
                          }
                        }}
                      >
                        {row.getVisibleCells().map(cell => (
                          <TableCell key={cell.id} className="max-w-0 p-4">
                            {flexRender(
                              cell.column.columnDef.cell,
                              cell.getContext(),
                            )}
                          </TableCell>
                        ))}
                      </TableRow>
                    );
                  }

                  return (
                    <TableRow
                      key={row.id}
                      className={cn(highlight && 'bg-red-50')}
                    >
                      {row.getVisibleCells().map(cell => (
                        <TableCell key={cell.id} className="max-w-0 p-4">
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext(),
                          )}
                        </TableCell>
                      ))}
                    </TableRow>
                  );
                })}
                {paddingBottom > 0 && (
                  <tr aria-hidden>
                    <td
                      colSpan={colCount}
                      style={{ ...spacerCellStyle, height: paddingBottom }}
                    />
                  </tr>
                )}
              </>
            )}
          </TableBody>
        </table>
      </div>
    </div>
  );
}
