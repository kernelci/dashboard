import type { CellContext, ColumnDef } from '@tanstack/react-table';

import type { JSX } from 'react';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import type { TIndividualTest, TPathTests } from '@/types/general';

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

const PathCell = ({ row, getValue }: CellContext<TPathTests, unknown>): JSX.Element => {
  const value = getValue() as string;
  const depth = row.depth;
  const indent = depth * 20;

  const hasSubGroups =
    row.original.sub_groups !== undefined && row.original.sub_groups.length > 0;
  const hasIndividualTests = row.original.individual_tests.length > 0;
  const isExpandable = hasSubGroups || hasIndividualTests;

  return (
    <div
      className="flex items-center"
      style={{ paddingLeft: `${indent}px` }}
    >
      {isExpandable && (
        <span className="mr-2">
          <ChevronRightAnimate
            isExpanded={row.getIsExpanded()}
            animated={false}
          />
        </span>
      )}
      <span>{value}</span>
    </div>
  );
};

export const defaultColumns: ColumnDef<TPathTests>[] = [
  {
    accessorKey: 'path_group',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.path" />
    ),
    cell: PathCell,
  },
  {
    accessorKey: 'pass_tests',
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="global.status"
        tooltipId="boots.statusTooltip"
      />
    ),
    cell: ({ row }): JSX.Element => {
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
    },
  },
];

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
