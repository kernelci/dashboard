import type { ColumnDef } from '@tanstack/react-table';

import type { JSX } from 'react';

import type { AccordionItemBuilds } from '@/types/tree/TreeDetails';
import { TableHeader } from '@/components/Table/TableHeader';

import { TooltipDateTime } from '@/components/TooltipDateTime';
import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import { ItemType } from '@/components/ListingItem/ListingItem';

import {
  DETAILS_COLUMN_ID,
  MoreDetailsIcon,
  MoreDetailsTableHeader,
} from '@/components/Table/DetailsColumn';
import { getBuildStatusGroup } from '@/utils/status';
import { UNKNOWN_STRING } from '@/utils/constants/backend';

export const defaultBuildColumns: ColumnDef<AccordionItemBuilds>[] = [
  {
    accessorKey: 'config',
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="global.config"
        tooltipId="build.dummyInfo"
      />
    ),
  },
  {
    accessorKey: 'architecture',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.arch" />
    ),
  },
  {
    accessorKey: 'compiler',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.compiler" />
    ),
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
    accessorKey: 'date',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.date" />
    ),
    cell: ({ row }): JSX.Element => (
      <TooltipDateTime
        dateTime={row.getValue('date')}
        lineBreak={true}
        showLabelTime={true}
        showLabelTZ={true}
      />
    ),
  },
  {
    accessorKey: 'buildErrors',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.buildErrors" />
    ),
    cell: ({ row }): JSX.Element => (
      <ColoredCircle
        className="max-w-6"
        quantity={row.getValue('buildErrors')}
        backgroundClassName={
          (row.getValue('buildErrors') as number) > 0
            ? ItemType.Error
            : ItemType.None
        }
      />
    ),
  },
  {
    accessorKey: 'buildTime',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.buildTime" />
    ),
    cell: ({ row }): JSX.Element => {
      return row.getValue('buildTime');
    },
  },
  {
    accessorKey: 'status',
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="global.status"
        tooltipId="build.statusTooltip"
      />
    ),
    cell: ({ row }): string => {
      return row.getValue('status')
        ? row.getValue('status')!.toString().toUpperCase()
        : 'NULL';
    },
    filterFn: (row, columnId, filterValue) =>
      getBuildStatusGroup(row.getValue(columnId)) === filterValue,
  },
  {
    id: DETAILS_COLUMN_ID,
    header: (): JSX.Element => <MoreDetailsTableHeader />,
    cell: (): JSX.Element => <MoreDetailsIcon />,
    meta: {
      dataTestId: 'details-button',
    },
  },
];
