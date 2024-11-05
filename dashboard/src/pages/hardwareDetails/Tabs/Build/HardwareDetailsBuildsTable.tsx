import type { ColumnDef } from '@tanstack/react-table';

import { MdCheck, MdClose } from 'react-icons/md';

import { BuildsTable } from '@/components/BuildsTable/BuildsTable';
import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import { ItemType } from '@/components/ListingItem/ListingItem';
import { TableHeader } from '@/components/Table/TableHeader';
import { TooltipDateTime } from '@/components/TooltipDateTime';

import type { AccordionItemBuilds } from '@/types/tree/TreeDetails';

export interface THardwareDetailsBuildsTable {
  buildItems: AccordionItemBuilds[];
}

const buildStatusMap = {
  valid: <MdCheck className="text-green" />,
  invalid: <MdClose className="text-red" />,
  null: <span>-</span>,
};

// TODO: put i18n in global.
const columns: ColumnDef<AccordionItemBuilds>[] = [
  {
    accessorKey: 'treeBranch',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'hardwareDetails.treeBranch',
        intlDefaultMessage: 'Tree / Branch',
      }),
  },
  {
    accessorKey: 'config',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeDetails.config',
        intlDefaultMessage: 'Config',
      }),
  },
  {
    accessorKey: 'compiler',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeDetails.compiler',
        intlDefaultMessage: 'Compiler',
      }),
  },
  {
    accessorKey: 'date',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeDetails.date',
        intlDefaultMessage: 'Date',
      }),
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
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeDetails.buildErrors',
        intlDefaultMessage: 'Build Errors',
      }),
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
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeDetails.buildTime',
        intlDefaultMessage: 'Build Time',
      }),
    cell: ({ row }): JSX.Element => {
      return row.getValue('buildTime');
    },
  },
  {
    accessorKey: 'status',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeDetails.status',
        intlDefaultMessage: 'Status',
        tooltipId: 'buildTab.statusTooltip',
      }),
    cell: ({ row }): JSX.Element => {
      return buildStatusMap[
        row.getValue('status') as keyof typeof buildStatusMap
      ];
    },
  },
];

export function HardwareDetailsBuildsTable({
  buildItems,
}: THardwareDetailsBuildsTable): JSX.Element {
  return <BuildsTable buildItems={buildItems} columns={columns} />;
}
