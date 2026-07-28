import type { CellContext, ColumnDef, RowData } from '@tanstack/react-table';
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

import type { UnifiedTestRow } from './types';

const INDENT_WIDTH = 20;

const PathCell = ({
  row,
  getValue,
}: CellContext<UnifiedTestRow, unknown>): JSX.Element => {
  const value = (getValue() as string) || '';
  const indent = row.depth * INDENT_WIDTH;
  const isExpandable = row.getCanExpand();

  return (
    <div className="flex items-center" style={{ paddingLeft: `${indent}px` }}>
      {isExpandable && (
        <span className="mr-2">
          <ChevronRightAnimate
            isExpanded={row.getIsExpanded()}
            animated={false}
          />
        </span>
      )}
      {!isExpandable && row.depth > 0 && <span className="mr-2 w-4" />}
      <Tooltip>
        <TooltipTrigger>
          <div className="max-w-80 overflow-clip text-nowrap text-ellipsis">
            {value}
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

/**
 * Adapts leaf/individual-test column defs for the unified group+leaf table:
 * path/status get group-aware cells; other columns are blank on group rows.
 */
export function adaptColumnsForUnifiedTable(
  leafColumns: ColumnDef<TIndividualTest>[],
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

    const adaptedColumn = {
      id: columnId,
      header: column.header as ColumnDef<UnifiedTestRow>['header'] | undefined,
      cell: (context: CellContext<UnifiedTestRow, unknown>): ReactNode => {
        if (context.row.original.kind === 'group') {
          return null;
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
    cell: ({ row }): JSX.Element => {
      return (
        <Tooltip>
          <TooltipTrigger>
            <div className="max-w-80 overflow-clip text-nowrap text-ellipsis">
              {row.getValue('path')}
            </div>
          </TooltipTrigger>
          <TooltipContent>{row.getValue('path')}</TooltipContent>
        </Tooltip>
      );
    },
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

export const defaultColumns: ColumnDef<UnifiedTestRow>[] =
  adaptColumnsForUnifiedTable(defaultInnerColumns);
