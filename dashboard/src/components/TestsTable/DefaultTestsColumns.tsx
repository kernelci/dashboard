import type { ColumnDef } from '@tanstack/react-table';

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

export const defaultColumns: ColumnDef<TPathTests>[] = [
  {
    accessorKey: 'path_group',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.path" />
    ),
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
  {
    id: 'chevron',
    cell: (): JSX.Element => <ChevronRightAnimate />,
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
