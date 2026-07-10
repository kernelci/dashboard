import type {
  ColumnDef,
  ColumnFiltersState,
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

import { useCallback, useMemo, useState, type JSX } from 'react';
import type { UseQueryResult } from '@tanstack/react-query';

import { FormattedMessage } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';
import { GroupedTestStatus } from '@/components/Status/Status';
import { TableHeader } from '@/components/Table/TableHeader';
import {
  ItemsPerPageSelector,
  ListingCount,
  PaginationButtons,
  PaginationInfo,
} from '@/components/Table/PaginationInfo';

import type { LabListingItem } from '@/types/lab';
import type { ShortStatusCount } from '@/types/general';

import { sumStatus } from '@/utils/status';

import { usePaginationState } from '@/hooks/usePaginationState';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import type { LabsListingRoutesMap } from '@/utils/constants/labsListing';

const statusCell = (summary: ShortStatusCount): JSX.Element => (
  <GroupedTestStatus
    preCalculatedGroupedStatus={{
      successCount: summary.PASS,
      failedCount: summary.FAIL,
      inconclusiveCount: summary.INCONCLUSIVE,
    }}
  />
);

const columns: ColumnDef<LabListingItem>[] = [
  {
    accessorKey: 'lab_name',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.lab" />
    ),
  },
  {
    accessorKey: 'build_status_summary',
    accessorFn: ({ build_status_summary: buildCount }): number =>
      sumStatus(buildCount),
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="globalTable.build"
        tooltipId="build.statusTooltip"
      />
    ),
    cell: ({ row }): JSX.Element =>
      statusCell(row.original.build_status_summary),
  },
  {
    accessorKey: 'boot_status_summary',
    accessorFn: ({ boot_status_summary: bootCount }): number =>
      sumStatus(bootCount),
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="globalTable.bootStatus"
        tooltipId="boots.statusTooltip"
      />
    ),
    cell: ({ row }): JSX.Element =>
      statusCell(row.original.boot_status_summary),
  },
  {
    accessorKey: 'test_status_summary',
    accessorFn: ({ test_status_summary: testCount }): number =>
      sumStatus(testCount),
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="globalTable.test"
        tooltipId="test.statusTooltip"
      />
    ),
    cell: ({ row }): JSX.Element =>
      statusCell(row.original.test_status_summary),
  },
];

export function LabsTable({
  labTableRows,
  status,
  queryData,
  error,
  isLoading,
  urlFromMap,
}: {
  labTableRows: LabListingItem[];
  status?: UseQueryResult['status'];
  queryData?: unknown;
  error?: Error | null;
  isLoading?: boolean;
  urlFromMap: LabsListingRoutesMap;
}): JSX.Element {
  const { listingSize } = useSearch({ from: urlFromMap.search });
  const navigate = useNavigate({ from: urlFromMap.navigate });

  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const { pagination, paginationUpdater } = usePaginationState(
    'labsListing',
    listingSize,
  );

  const table = useReactTable({
    data: labTableRows,
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
    return groupHeaders.map(header => (
      <TableHead key={header.id}>
        {header.isPlaceholder
          ? null
          : flexRender(header.column.columnDef.header, {
              ...header.getContext(),
              sorting,
            })}
      </TableHead>
    ));
  }, [groupHeaders, sorting]);

  const modelRows = table.getRowModel().rows;
  const tableBody = useMemo((): JSX.Element[] | JSX.Element => {
    return modelRows?.length ? (
      modelRows.map(row => (
        <TableRow key={row.id}>
          {row.getVisibleCells().map(cell => (
            <TableCell key={cell.id}>
              {flexRender(cell.column.columnDef.cell, cell.getContext())}
            </TableCell>
          ))}
        </TableRow>
      ))
    ) : (
      <TableRow>
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id="labsListing.notFound" />
        </TableCell>
      </TableRow>
    );
  }, [modelRows]);

  const navigateWithPageSize = useCallback(
    (pageSize: number) => {
      navigate({
        search: prev => ({ ...prev, listingSize: pageSize }),
        state: s => s,
      });
    },
    [navigate],
  );

  return (
    <div className="flex flex-col gap-6 pb-4">
      <div className="flex flex-wrap items-center justify-end gap-4">
        <span className="text-dim-gray flex-1 justify-start text-left text-sm">
          <FormattedMessage
            id="global.projectUnderDevelopment"
            values={{ br: <br /> }}
          />
        </span>
        <div className="flex justify-end gap-y-2 max-[700px]:flex-wrap">
          <ItemsPerPageSelector
            table={table}
            onPaginationChange={navigateWithPageSize}
            className="pl-4"
          />
        </div>
        <div className="flex justify-end gap-y-2 max-[700px]:flex-wrap">
          <ListingCount table={table} intlLabel="global.labs" />
          <PaginationButtons table={table} className="pl-4" />
        </div>
      </div>
      <QuerySwitcher
        status={status}
        data={queryData}
        error={error}
        customError={
          <MemoizedSectionError
            isLoading={isLoading}
            errorMessage={error?.message}
            emptyLabel="labsListing.notFound"
          />
        }
      >
        <BaseTable headerComponents={tableHeaders}>
          <TableBody>{tableBody}</TableBody>
        </BaseTable>
      </QuerySwitcher>
      <PaginationInfo
        table={table}
        intlLabel="global.labs"
        onPaginationChange={navigateWithPageSize}
      />
    </div>
  );
}
