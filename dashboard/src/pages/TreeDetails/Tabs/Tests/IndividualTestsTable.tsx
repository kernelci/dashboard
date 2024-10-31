import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  Row,
  SortingState,
  useReactTable,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import { CSSProperties, memo, useMemo, useRef, useState } from 'react';

import { Link, LinkProps } from '@tanstack/react-router';

import { TIndividualTest } from '@/types/general';

import { TooltipDateTime } from '@/components/TooltipDateTime';

import { ChevronRightAnimate } from '@/components/AnimatedIcons/Chevron';

import { TableHeader } from '@/components/Table/TableHeader';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { sanitizeTableValue } from '@/components/Table/tableUtils';
import { DumbTableHeader, TableHead } from '@/components/Table/BaseTable';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';

const columns: ColumnDef<TIndividualTest>[] = [
  {
    accessorKey: 'path',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'testDetails.path',
        intlDefaultMessage: 'Path',
      }),
    cell: ({ row }): JSX.Element => {
      return (
        <Tooltip>
          <TooltipTrigger>
            <div className="max-w-80 overflow-clip text-ellipsis text-nowrap">
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
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'testDetails.status',
        intlDefaultMessage: 'Status',
      }),
  },
  {
    accessorKey: 'start_time',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'global.date',
        intlDefaultMessage: 'Date',
      }),
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
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'testDetails.duration',
        intlDefaultMessage: 'Duration',
      }),
    cell: ({ row }): string =>
      row.getValue('duration') ? row.getValue('duration') : '-',
  },
  {
    id: 'hardware',
    accessorKey: 'hardware',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeDetails.hardware',
        intlDefaultMessage: 'Hardware',
      }),
    cell: ({ row }): JSX.Element => (
      <div className="text-nowrap">
        <TooltipHardware hardwares={row.getValue('hardware')} />
      </div>
    ),
  },
  {
    id: 'chevron',
    cell: (): JSX.Element => <ChevronRightAnimate />,
  },
];

const TooltipHardware = ({
  hardwares,
}: {
  hardwares: string[] | undefined;
}): JSX.Element => {
  const hardwaresTooltip = useMemo(() => {
    return hardwares
      ? hardwares.map(hardware => (
          <div key={hardware} className="text-center">
            <span>{hardware}</span>
            <br />
          </div>
        ))
      : '-';
  }, [hardwares]);

  return (
    <Tooltip>
      <TooltipTrigger>
        {sanitizeTableValue(hardwares?.[0], false)}
      </TooltipTrigger>
      <TooltipContent>{hardwaresTooltip}</TooltipContent>
    </Tooltip>
  );
};

const TableRowComponent = ({
  row,
}: {
  row: Row<TIndividualTest>;
}): JSX.Element => {
  const linkProps: LinkProps = useMemo(() => {
    return {
      to: '/tree/$treeId/test/$testId',
      params: {
        testId: row.original.id,
      },
      search: s => s,
    };
  }, [row.original.id]);

  return (
    <TableRow key={row.id} className="border-b-0 hover:bg-lightBlue">
      {row.getVisibleCells().map(cell => {
        return (
          <TableCell key={cell.id}>
            <Link {...linkProps}>
              {flexRender(cell.column.columnDef.cell, cell.getContext())}
            </Link>
          </TableCell>
        );
      })}
    </TableRow>
  );
};
const TableRowMemoized = memo(TableRowComponent);

const ESTIMATED_ROW_HEIGHT = 60;

export function IndividualTestsTable({
  data,
}: {
  data: TIndividualTest[];
}): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    manualPagination: true,
    state: {
      sorting,
    },
  });

  const groupHeaders = table.getHeaderGroups()[0]?.headers;
  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map(header => {
      return (
        <TableHead key={header.id} className="px-2">
          {header.isPlaceholder
            ? null
            : flexRender(header.column.columnDef.header, header.getContext())}
        </TableHead>
      );
    });
    // TODO: remove exhaustive-deps and change memo  (all tables)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [groupHeaders, sorting]);

  const { rows } = useMemo(() => {
    return table.getRowModel();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [table, sorting]);

  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: rows.length,
    estimateSize: () => ESTIMATED_ROW_HEIGHT,
    getScrollElement: () => parentRef.current,
    overscan: 5,
  });
  const virtualItems = virtualizer.getVirtualItems();

  const tableRows = useMemo((): JSX.Element[] => {
    return virtualItems.map(virtualRow => {
      const row = rows[virtualRow.index] as Row<TIndividualTest>;
      return <TableRowMemoized row={row} key={row.id} />;
    });
  }, [rows, virtualItems]);

  // if more performance is needed, try using translate as in the example from tanstack virtual instead of padding
  // https://tanstack.com/virtual/latest/docs/framework/react/examples/table
  const [firstRowStyle, lastRowStyle]: [CSSProperties, CSSProperties] =
    useMemo(() => {
      if (virtualItems.length === 0) return [{}, {}];
      return [
        { paddingTop: virtualItems[0].start },
        {
          paddingBottom:
            virtualizer.getTotalSize() -
            virtualItems[virtualItems.length - 1].end,
        },
      ];
    }, [virtualItems, virtualizer]);

  return (
    <div
      ref={parentRef}
      className="max-h-[400px] max-w-full overflow-auto bg-lightGray p-8"
    >
      <div className="rounded-lg border-x border-t border-darkGray bg-white text-sm text-black">
        <div style={firstRowStyle} />
        <table className="w-full">
          <DumbTableHeader>{tableHeaders}</DumbTableHeader>
          <TableBody>{tableRows}</TableBody>
        </table>
        <div style={lastRowStyle} />
      </div>
    </div>
  );
}
