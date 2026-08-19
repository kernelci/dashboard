import type {
  CellContext,
  ColumnDef,
  Row,
  RowData,
  SortingFn,
} from '@tanstack/react-table';
import type { JSX, ReactNode } from 'react';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import type { TIndividualTest } from '@/types/general';

import { GroupedTestStatus } from '@/components/Status/Status';

import { TableHeader } from '@/components/Table/TableHeader';

import { ChevronRightAnimate } from '@/components/AnimatedIcons/Chevron';

import TooltipHardware from '@/components/Table/TooltipHardware';
import { TooltipDateTime } from '@/components/TooltipDateTime';

import {
  MoreDetailsTableHeader,
  MoreDetailsIcon,
  DETAILS_COLUMN_ID,
} from '@/components/Table/DetailsColumn';
import { UNKNOWN_STRING } from '@/utils/constants/backend';

import { getDateSortKey } from './groupSummaries';
import type { GroupFieldSummary, UnifiedTestRow } from './types';

const INDENT_WIDTH = 12;
export const PATH_TREE_INDENT = INDENT_WIDTH;
const MUTED_VALUE_CLASS = 'text-gray-500';

export const PathWithPrefixEllipsis = ({
  value,
}: {
  value: string;
}): JSX.Element => (
  <div
    className="w-full min-w-0 overflow-hidden text-ellipsis whitespace-nowrap"
    dir="rtl"
    style={{ textAlign: 'left' }}
  >
    <span dir="ltr" style={{ unicodeBidi: 'embed' }}>
      {value}
    </span>
  </div>
);

export const PathWithTooltip = ({ value }: { value: string }): JSX.Element => (
  <Tooltip>
    <TooltipTrigger asChild>
      <div className="min-w-0 overflow-hidden">
        <PathWithPrefixEllipsis value={value} />
      </div>
    </TooltipTrigger>
    <TooltipContent>{value}</TooltipContent>
  </Tooltip>
);

export type SortDirectionGetter = (columnId: string) => false | 'asc' | 'desc';

const PathCell = ({
  row,
  getValue,
}: CellContext<UnifiedTestRow, unknown>): JSX.Element => {
  const value = (getValue() as string) || '';
  const indent = row.depth * INDENT_WIDTH;
  const isExpandable = row.getCanExpand();
  const isLeaf = row.original.kind === 'leaf';

  return (
    <div
      className="flex w-full min-w-0 items-center"
      style={{ paddingLeft: `${indent}px` }}
    >
      {isExpandable && (
        <span className="mr-2 shrink-0">
          <ChevronRightAnimate
            isExpanded={row.getIsExpanded()}
            animated={false}
          />
        </span>
      )}
      {!isExpandable && row.depth > 0 && <span className="mr-2 w-4 shrink-0" />}
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="min-w-0 flex-1 overflow-hidden">
            {isLeaf ? (
              <PathWithPrefixEllipsis value={value} />
            ) : (
              <div className="overflow-hidden text-ellipsis whitespace-nowrap">
                {value}
              </div>
            )}
          </div>
        </TooltipTrigger>
        <TooltipContent>{value}</TooltipContent>
      </Tooltip>
    </div>
  );
};

const StatusCell = ({
  row,
}: CellContext<UnifiedTestRow, unknown>): JSX.Element | string => {
  if (row.original.kind === 'group') {
    return (
      <GroupedTestStatus
        pass={row.original.pass_tests}
        done={row.original.done_tests}
        miss={row.original.miss_tests}
        fail={row.original.fail_tests}
        skip={row.original.skip_tests}
        error={row.original.error_tests}
        nullStatus={row.original.null_tests}
      />
    );
  }

  return row.original.status ?? '';
};

function formatDateLabel(dateTime: string): string {
  const dateObj = new Date(dateTime);
  if (Number.isNaN(dateObj.getTime())) {
    return '-';
  }
  return `${dateObj.toLocaleDateString()} ${dateObj.toLocaleTimeString()}`;
}

function DateRangeCell({
  min,
  max,
  sortDirection,
}: {
  min: string;
  max: string;
  sortDirection: false | 'asc' | 'desc';
}): JSX.Element {
  const emphasizeMin = sortDirection === 'asc';
  const emphasizeMax = sortDirection === 'desc';

  return (
    <div className={`text-nowrap ${MUTED_VALUE_CLASS}`}>
      <span className={emphasizeMin ? 'text-black' : undefined}>
        {formatDateLabel(min)}
      </span>
      {' – '}
      <span className={emphasizeMax ? 'text-black' : undefined}>
        {formatDateLabel(max)}
      </span>
    </div>
  );
}

function getColumnId<TData extends RowData>(
  column: ColumnDef<TData>,
): string | undefined {
  if (column.id) {
    return column.id;
  }
  if ('accessorKey' in column && typeof column.accessorKey === 'string') {
    return column.accessorKey;
  }
  return undefined;
}

function renderLeafCell(
  column: ColumnDef<TIndividualTest>,
  context: CellContext<UnifiedTestRow, unknown>,
): ReactNode {
  if (typeof column.cell === 'function') {
    return column.cell(
      context as unknown as CellContext<TIndividualTest, unknown>,
    );
  }

  const value = context.getValue();
  if (value === undefined || value === null || value === '') {
    return null;
  }
  return value as ReactNode;
}

function renderUniformGroupCell(
  column: ColumnDef<TIndividualTest>,
  context: CellContext<UnifiedTestRow, unknown>,
  value: unknown,
): ReactNode {
  const columnId = getColumnId(column);
  const leafLikeOriginal = {
    ...context.row.original,
    kind: 'leaf' as const,
  };

  return renderLeafCell(column, {
    ...context,
    getValue: () => value as never,
    row: {
      ...context.row,
      original: leafLikeOriginal,
      // Leaf cells read row.getValue(id); the group row has no leaf field values.
      getValue: (id: string) =>
        id === columnId ? value : context.row.getValue(id),
    } as Row<UnifiedTestRow>,
  });
}

function renderGroupSummaryCell(
  column: ColumnDef<TIndividualTest>,
  context: CellContext<UnifiedTestRow, unknown>,
  summary: GroupFieldSummary | undefined,
  getSortDirection: SortDirectionGetter,
  columnId: string,
): ReactNode {
  if (!summary) {
    return null;
  }

  if (summary.kind === 'mixed') {
    return <span className={MUTED_VALUE_CLASS}>({summary.count})</span>;
  }

  if (summary.kind === 'dateRange') {
    return (
      <DateRangeCell
        min={summary.min}
        max={summary.max}
        sortDirection={getSortDirection(columnId)}
      />
    );
  }

  return renderUniformGroupCell(column, context, summary.value);
}

function parseTime(value: unknown): number | null {
  if (typeof value !== 'string' || value === '') {
    return null;
  }
  const time = new Date(value).getTime();
  return Number.isNaN(time) ? null : time;
}

function compareNullable(
  a: number | string | null,
  b: number | string | null,
): number {
  if (a === null && b === null) {
    return 0;
  }
  if (a === null) {
    return 1;
  }
  if (b === null) {
    return -1;
  }
  if (a < b) {
    return -1;
  }
  if (a > b) {
    return 1;
  }
  return 0;
}

function kindTieBreak(rowA: UnifiedTestRow, rowB: UnifiedTestRow): number {
  if (rowA.kind === rowB.kind) {
    return 0;
  }
  return rowA.kind === 'leaf' ? -1 : 1;
}

function getGroupSortValue(
  summary: GroupFieldSummary | undefined,
): unknown | undefined {
  if (!summary || summary.kind === 'mixed' || summary.kind === 'dateRange') {
    return undefined;
  }
  return summary.value;
}

function canonicalizeSortValue(value: unknown): string | null {
  if (value === undefined || value === null || value === '') {
    return null;
  }
  if (Array.isArray(value)) {
    return JSON.stringify(value);
  }
  return String(value);
}

function createGenericSortingFn(columnId: string): SortingFn<UnifiedTestRow> {
  return (rowA, rowB): number => {
    const a = rowA.original;
    const b = rowB.original;

    const aValue =
      a.kind === 'leaf'
        ? a[columnId as keyof UnifiedTestRow]
        : getGroupSortValue(a.summaries?.[columnId]);
    const bValue =
      b.kind === 'leaf'
        ? b[columnId as keyof UnifiedTestRow]
        : getGroupSortValue(b.summaries?.[columnId]);

    const cmp = compareNullable(
      canonicalizeSortValue(aValue),
      canonicalizeSortValue(bValue),
    );
    return cmp !== 0 ? cmp : kindTieBreak(a, b);
  };
}

function createDateSortingFn(
  getSortDirection: SortDirectionGetter,
): SortingFn<UnifiedTestRow> {
  return (rowA, rowB): number => {
    const a = rowA.original;
    const b = rowB.original;
    // Asc: compare mins; desc: compare maxes (TanStack then negates).
    const newestFirst = getSortDirection('start_time') === 'desc';

    const cmp = compareNullable(
      parseTime(getDateSortKey(a, newestFirst)),
      parseTime(getDateSortKey(b, newestFirst)),
    );
    return cmp !== 0 ? cmp : kindTieBreak(a, b);
  };
}

/**
 * Adapts leaf/individual-test column defs for the unified group+leaf table:
 * path/status get group-aware cells; other columns use group summaries.
 */
export function adaptColumnsForUnifiedTable(
  leafColumns: ColumnDef<TIndividualTest>[],
  getSortDirection: SortDirectionGetter = () => false,
): ColumnDef<UnifiedTestRow>[] {
  return leafColumns.map((column): ColumnDef<UnifiedTestRow> => {
    const columnId = getColumnId(column);

    if (columnId === 'path') {
      return {
        id: 'path',
        accessorKey: 'path',
        header: column.header as
          | ColumnDef<UnifiedTestRow>['header']
          | undefined,
        cell: PathCell,
        sortingFn: createGenericSortingFn('path'),
      };
    }

    if (columnId === 'status') {
      return {
        id: 'status',
        accessorKey: 'status',
        header: column.header as
          | ColumnDef<UnifiedTestRow>['header']
          | undefined,
        cell: StatusCell,
      };
    }

    if (columnId === DETAILS_COLUMN_ID) {
      return {
        id: DETAILS_COLUMN_ID,
        header: column.header as
          | ColumnDef<UnifiedTestRow>['header']
          | undefined,
        cell: (context: CellContext<UnifiedTestRow, unknown>): ReactNode => {
          if (context.row.original.kind === 'group') {
            return null;
          }
          return renderLeafCell(column, context);
        },
        enableSorting: false,
      };
    }

    const isDateColumn = columnId === 'start_time';

    const adaptedColumn = {
      id: columnId,
      header: column.header as ColumnDef<UnifiedTestRow>['header'] | undefined,
      sortUndefined: 'last' as const,
      sortingFn: isDateColumn
        ? createDateSortingFn(getSortDirection)
        : createGenericSortingFn(columnId ?? ''),
      cell: (context: CellContext<UnifiedTestRow, unknown>): ReactNode => {
        if (context.row.original.kind === 'group') {
          return renderGroupSummaryCell(
            column,
            context,
            columnId ? context.row.original.summaries?.[columnId] : undefined,
            getSortDirection,
            columnId ?? '',
          );
        }
        return renderLeafCell(column, context);
      },
    } as ColumnDef<UnifiedTestRow>;

    if ('accessorKey' in column && typeof column.accessorKey === 'string') {
      return {
        ...adaptedColumn,
        accessorKey: column.accessorKey,
      } as ColumnDef<UnifiedTestRow>;
    }

    if ('accessorFn' in column && typeof column.accessorFn === 'function') {
      const leafAccessorFn = column.accessorFn;
      return {
        ...adaptedColumn,
        accessorFn: (row: UnifiedTestRow): unknown =>
          leafAccessorFn(row as unknown as TIndividualTest, 0),
      } as ColumnDef<UnifiedTestRow>;
    }

    return adaptedColumn;
  });
}

export const defaultInnerColumns: ColumnDef<TIndividualTest>[] = [
  {
    accessorKey: 'path',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.path" />
    ),
    cell: ({ row }): JSX.Element => (
      <PathWithTooltip value={String(row.getValue('path') ?? '')} />
    ),
  },
  {
    accessorKey: 'status',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.status" />
    ),
  },
  {
    accessorKey: 'start_time',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.date" />
    ),
    cell: ({ row }): JSX.Element => (
      <div className="text-nowrap">
        <TooltipDateTime
          dateTime={row.getValue('start_time')}
          showLabelTime={true}
        />
      </div>
    ),
  },
  {
    accessorKey: 'duration',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.duration" />
    ),
    cell: ({ row }): string =>
      row.getValue('duration') ? row.getValue('duration') : '-',
  },
  {
    id: 'lab',
    accessorKey: 'lab',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.lab" />
    ),
    cell: ({ row }): string => {
      return row.getValue('lab') || UNKNOWN_STRING;
    },
  },
  {
    id: 'hardware',
    accessorKey: 'hardware',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.hardware" />
    ),
    cell: ({ row }): JSX.Element => (
      <div className="text-nowrap">
        <TooltipHardware hardwares={row.getValue('hardware')} />
      </div>
    ),
  },
  {
    id: DETAILS_COLUMN_ID,
    header: (): JSX.Element => <MoreDetailsTableHeader />,
    cell: (): JSX.Element => <MoreDetailsIcon />,
  },
];
