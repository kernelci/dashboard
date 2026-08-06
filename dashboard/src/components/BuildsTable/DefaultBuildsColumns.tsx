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
    meta: {
      headerIntlKey: 'global.config',
      isRowHeader: true,
      minWidth: 140,
      maxWidth: 320,
    },
  },
  {
    accessorKey: 'architecture',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.arch" />
    ),
    meta: {
      headerIntlKey: 'global.arch',
      minWidth: 90,
      maxWidth: 160,
    },
  },
  {
    accessorKey: 'compiler',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.compiler" />
    ),
    meta: {
      headerIntlKey: 'global.compiler',
      minWidth: 100,
      maxWidth: 200,
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
    meta: {
      headerIntlKey: 'global.date',
      minWidth: 140,
      maxWidth: 220,
    },
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
    meta: {
      headerIntlKey: 'global.buildErrors',
      minWidth: 100,
      maxWidth: 160,
    },
  },
  {
    accessorKey: 'buildTime',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.buildTime" />
    ),
    cell: ({ row }): JSX.Element => {
      return row.getValue('buildTime');
    },
    meta: {
      headerIntlKey: 'global.buildTime',
      minWidth: 100,
      maxWidth: 160,
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
    meta: {
      headerIntlKey: 'global.status',
      minWidth: 100,
      maxWidth: 160,
    },
  },
  {
    id: DETAILS_COLUMN_ID,
    header: (): JSX.Element => <MoreDetailsTableHeader />,
    cell: (): JSX.Element => <MoreDetailsIcon />,
    enableResizing: false,
    meta: {
      minWidth: 64,
      maxWidth: 96,
    },
  },
];
