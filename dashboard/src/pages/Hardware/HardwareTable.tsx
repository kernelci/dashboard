import type {
  ColumnDef,
  ColumnFiltersState,
  Row,
  SortingState,
} from '@tanstack/react-table';

import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';

import { memo, useCallback, useMemo, useState } from 'react';

import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';

import { formattedBreakLineValue } from '@/locales/messages';

import {
  TableBody,
  TableCell,
  TableCellWithLink,
  TableRow,
} from '@/components/ui/table';

import { BuildStatus, GroupedTestStatus } from '@/components/Status/Status';
import { TableHeader } from '@/components/Table/TableHeader';
import { PaginationInfo } from '@/components/Table/PaginationInfo';

import type { HardwareTableItem } from '@/types/hardware';

import { sumStatus } from '@/utils/status';

import { usePaginationState } from '@/hooks/usePaginationState';

import { zPossibleTabValidator } from '@/types/tree/TreeDetails';

import type { ListingTableColumnMeta } from '@/types/table';

import { InputTime } from './InputTime';

// TODO Extract and reuse the table

const columns: ColumnDef<HardwareTableItem>[] = [
  {
    accessorKey: 'hardwareName',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.name" />
    ),
    meta: {
      tabTarget: 'global.builds',
    },
  },
  {
    accessorKey: 'buildCount',
    accessorFn: ({ buildCount }): number =>
      buildCount ? sumStatus(buildCount) : 0,
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="globalTable.build"
        tooltipId="build.statusTooltip"
      />
    ),
    cell: ({ row }): JSX.Element => {
      return row.original.buildCount ? (
        <BuildStatus
          valid={row.original.buildCount.valid}
          invalid={row.original.buildCount.invalid}
          unknown={row.original.buildCount.null}
        />
      ) : (
        <FormattedMessage id="global.loading" defaultMessage="Loading..." />
      );
    },
    meta: {
      tabTarget: 'global.builds',
    },
  },
  {
    accessorKey: 'bootStatusCount',
    accessorFn: ({ bootStatusCount }): number =>
      bootStatusCount ? sumStatus(bootStatusCount) : 0,
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="globalTable.bootStatus"
        tooltipId="boots.statusTooltip"
      />
    ),
    cell: ({ row }): JSX.Element => {
      return row.original.bootStatusCount ? (
        <GroupedTestStatus
          pass={row.original.bootStatusCount.PASS}
          skip={row.original.bootStatusCount.SKIP}
          fail={row.original.bootStatusCount.FAIL}
          miss={row.original.bootStatusCount.MISS}
          done={row.original.bootStatusCount.DONE}
          error={row.original.bootStatusCount.ERROR}
          nullStatus={row.original.bootStatusCount.NULL}
        />
      ) : (
        <FormattedMessage id="global.loading" defaultMessage="Loading..." />
      );
    },
    meta: {
      tabTarget: 'global.boots',
    },
  },
  {
    accessorKey: 'testStatusCount',
    accessorFn: ({ testStatusCount }): number =>
      testStatusCount ? sumStatus(testStatusCount) : 0,
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="globalTable.test"
        tooltipId="test.statusTooltip"
      />
    ),
    cell: ({ row }): JSX.Element => {
      return row.original.testStatusCount ? (
        <GroupedTestStatus
          pass={row.original.testStatusCount.PASS}
          skip={row.original.testStatusCount.SKIP}
          fail={row.original.testStatusCount.FAIL}
          miss={row.original.testStatusCount.MISS}
          done={row.original.testStatusCount.DONE}
          error={row.original.testStatusCount.ERROR}
          nullStatus={row.original.testStatusCount.NULL}
        />
      ) : (
        <FormattedMessage id="global.loading" defaultMessage="Loading..." />
      );
    },
    meta: {
      tabTarget: 'global.tests',
    },
  },
];

interface ITreeTable {
  treeTableRows: HardwareTableItem[];
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
}

export function HardwareTable({
  treeTableRows,
  startTimestampInSeconds,
  endTimestampInSeconds,
}: ITreeTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const { pagination, paginationUpdater } =
    usePaginationState('hardwareListing');

  const getLinkProps = useCallback(
    (row: Row<HardwareTableItem>, tabTarget?: string): LinkProps => {
      return {
        from: '/hardware',
        to: '/hardware/$hardwareId',
        params: { hardwareId: row.original.hardwareName },

        search: previousSearch => ({
          ...previousSearch,
          currentPageTab: zPossibleTabValidator.parse(tabTarget),
          startTimestampInSeconds,
          endTimestampInSeconds,
        }),
      };
    },
    [endTimestampInSeconds, startTimestampInSeconds],
  );

  const data = useMemo(() => {
    return treeTableRows;
  }, [treeTableRows]);

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: paginationUpdater,
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters,
      pagination,
    },
  });

  const groupHeaders = table.getHeaderGroups()[0].headers;
  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map(header => {
      return (
        <TableHead key={header.id}>
          {header.isPlaceholder
            ? null
            : // the header must change the icon when sorting changes,
              // but just the column dependency won't trigger the rerender
              // so we pass an unused sorting prop here to force the useMemo dependency
              flexRender(header.column.columnDef.header, {
                ...header.getContext(),
                sorting,
              })}
        </TableHead>
      );
    });
  }, [groupHeaders, sorting]);

  const modelRows = table.getRowModel().rows;
  const tableBody = useMemo((): JSX.Element[] | JSX.Element => {
    return modelRows?.length ? (
      modelRows.map(row => (
        <TableRow key={row.id}>
          {row.getVisibleCells().map(cell => {
            const tabTarget = (
              cell.column.columnDef.meta as ListingTableColumnMeta
            ).tabTarget;
            return (
              <TableCellWithLink
                key={cell.id}
                linkClassName="w-full inline-block h-full"
                linkProps={getLinkProps(row, tabTarget)}
              >
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </TableCellWithLink>
            );
          })}
        </TableRow>
      ))
    ) : (
      <TableRow>
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id="global.noResults" />
        </TableCell>
      </TableRow>
    );
  }, [getLinkProps, modelRows]);

  const MemoizedInputTime = memo(InputTime);

  return (
    <div className="flex flex-col gap-6 pb-4">
      <div className="flex items-center justify-between gap-4">
        <span className="text-left text-sm text-dimGray">
          <FormattedMessage
            id="global.projectUnderDevelopment"
            values={formattedBreakLineValue}
          />
        </span>
        <div className="flex items-center justify-between gap-10">
          <MemoizedInputTime />
          <PaginationInfo table={table} intlLabel="global.hardwares" />
        </div>
      </div>
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableBody}</TableBody>
      </BaseTable>
      <PaginationInfo table={table} intlLabel="global.hardwares" />
    </div>
  );
}
