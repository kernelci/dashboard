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

import { useCallback, useMemo, useState, type JSX } from 'react';
import type { UseQueryResult } from '@tanstack/react-query';

import { FormattedMessage } from 'react-intl';

import { useNavigate, useSearch, type LinkProps } from '@tanstack/react-router';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';

import { formattedBreakLineValue } from '@/locales/messages';

import { TableBody, TableCell, TableRow } from '@/components/ui/table';
import { ConditionalTableCell } from '@/components/Table/ConditionalTableCell';

import { GroupedTestStatusWithLink } from '@/components/Status/Status';
import { TableHeader } from '@/components/Table/TableHeader';
import {
  ItemsPerPageSelector,
  ListingCount,
  PaginationButtons,
  PaginationInfo,
} from '@/components/Table/PaginationInfo';

import type { HardwareItemV2 } from '@/types/hardware';

import { statusCountToRequiredStatusCount, sumStatus } from '@/utils/status';

import { usePaginationState } from '@/hooks/usePaginationState';

import { zPossibleTabValidator } from '@/types/tree/TreeDetails';

import type { ListingTableColumnMeta } from '@/types/table';

import { RedirectFrom, type TFilter } from '@/types/general';

import { MemoizedInputTime } from '@/components/InputTime';
import { REDUCED_TIME_SEARCH } from '@/utils/constants/general';
import { EMPTY_VALUE } from '@/lib/string';
import { Badge } from '@/components/ui/badge';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

// TODO Extract and reuse the table
interface IHardwareTable {
  treeTableRows: HardwareItemV2[];
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
  status?: UseQueryResult['status'];
  queryData?: unknown;
  error?: Error | null;
  isLoading?: boolean;
}

const getLinkProps = (
  row: Row<HardwareItemV2>,
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  tabTarget?: string,
  newDiffFilter?: TFilter,
): LinkProps => {
  return {
    from: '/hardware-new',
    to: '/hardware/$hardwareId',
    params: { hardwareId: row.original.platform },
    search: previousSearch => ({
      ...previousSearch,
      currentPageTab: zPossibleTabValidator.parse(tabTarget),
      startTimestampInSeconds,
      endTimestampInSeconds,
      diffFilter: { ...previousSearch.diffFilter, ...newDiffFilter },
    }),
    state: s => ({
      ...s,
      id: row.original.platform,
      from: RedirectFrom.HardwareNew,
      hardwareStatusCount: {
        builds: statusCountToRequiredStatusCount(
          row.original.build_status_summary,
        ),
        tests: statusCountToRequiredStatusCount(
          row.original.test_status_summary,
        ),
        boots: statusCountToRequiredStatusCount(
          row.original.boot_status_summary,
        ),
      },
    }),
  };
};

const getColumns = (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
): ColumnDef<HardwareItemV2>[] => {
  return [
    {
      accessorKey: 'platform',
      header: ({ column }): JSX.Element => (
        <TableHeader column={column} intlKey="global.platform" />
      ),
      meta: {
        tabTarget: 'global.builds',
      },
    },
    {
      accessorKey: 'hardware',
      accessorFn: ({ hardware }): number => {
        return hardware ? hardware.length : 0;
      },
      header: ({ column }): JSX.Element => (
        <TableHeader column={column} intlKey="global.compatibles" />
      ),
      cell: ({ row }): JSX.Element => {
        const hardwares = row.original.hardware;
        if (hardwares === undefined || hardwares === null) {
          return <>{EMPTY_VALUE}</>;
        }

        return (
          <div className="flex max-w-xl flex-wrap gap-2">
            {hardwares.map(hardware => {
              return (
                <Badge
                  key={hardware}
                  variant="outline"
                  className="text-sm font-normal text-nowrap"
                >
                  {hardware}
                </Badge>
              );
            })}
          </div>
        );
      },
      meta: {
        tabTarget: 'global.builds',
      },
    },
    {
      accessorKey: 'build_status_summary',
      accessorFn: ({ build_status_summary: buildCount }): number =>
        buildCount ? sumStatus(buildCount) : 0,
      header: ({ column }): JSX.Element => (
        <TableHeader
          column={column}
          intlKey="globalTable.build"
          tooltipId="build.statusTooltip"
        />
      ),
      cell: ({ column, row }): JSX.Element => {
        const tabTarget = (column.columnDef.meta as ListingTableColumnMeta)
          .tabTarget;
        return row.original.build_status_summary ? (
          <GroupedTestStatusWithLink
            pass={row.original.build_status_summary.PASS}
            skip={row.original.build_status_summary.SKIP}
            fail={row.original.build_status_summary.FAIL}
            miss={row.original.build_status_summary.MISS}
            done={row.original.build_status_summary.DONE}
            error={row.original.build_status_summary.ERROR}
            nullStatus={row.original.build_status_summary.NULL}
            passLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              tabTarget,
              {
                buildStatus: { PASS: true },
              },
            )}
            failLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              tabTarget,
              {
                buildStatus: { FAIL: true },
              },
            )}
            inconclusiveLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              tabTarget,
              {
                buildStatus: {
                  MISS: true,
                  ERROR: true,
                  SKIP: true,
                  DONE: true,
                  NULL: true,
                },
              },
            )}
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
      accessorKey: 'boot_status_summary',
      accessorFn: ({ boot_status_summary: bootStatusCount }): number =>
        bootStatusCount ? sumStatus(bootStatusCount) : 0,
      header: ({ column }): JSX.Element => (
        <TableHeader
          column={column}
          intlKey="globalTable.bootStatus"
          tooltipId="boots.statusTooltip"
        />
      ),
      cell: ({ column, row }): JSX.Element => {
        const tabTarget = (column.columnDef.meta as ListingTableColumnMeta)
          .tabTarget;
        return row.original.boot_status_summary ? (
          <GroupedTestStatusWithLink
            pass={row.original.boot_status_summary.PASS}
            skip={row.original.boot_status_summary.SKIP}
            fail={row.original.boot_status_summary.FAIL}
            miss={row.original.boot_status_summary.MISS}
            done={row.original.boot_status_summary.DONE}
            error={row.original.boot_status_summary.ERROR}
            nullStatus={row.original.boot_status_summary.NULL}
            passLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              tabTarget,
              {
                bootStatus: { PASS: true },
              },
            )}
            failLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              tabTarget,
              {
                bootStatus: { FAIL: true },
              },
            )}
            inconclusiveLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              tabTarget,
              {
                bootStatus: {
                  MISS: true,
                  ERROR: true,
                  SKIP: true,
                  DONE: true,
                  NULL: true,
                },
              },
            )}
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
      accessorKey: 'test_status_summary',
      accessorFn: ({ test_status_summary: testStatusCount }): number =>
        testStatusCount ? sumStatus(testStatusCount) : 0,
      header: ({ column }): JSX.Element => (
        <TableHeader
          column={column}
          intlKey="globalTable.test"
          tooltipId="test.statusTooltip"
        />
      ),
      cell: ({ column, row }): JSX.Element => {
        const tabTarget = (column.columnDef.meta as ListingTableColumnMeta)
          .tabTarget;
        return row.original.test_status_summary ? (
          <GroupedTestStatusWithLink
            pass={row.original.test_status_summary.PASS}
            skip={row.original.test_status_summary.SKIP}
            fail={row.original.test_status_summary.FAIL}
            miss={row.original.test_status_summary.MISS}
            done={row.original.test_status_summary.DONE}
            error={row.original.test_status_summary.ERROR}
            nullStatus={row.original.test_status_summary.NULL}
            passLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              tabTarget,
              {
                testStatus: { PASS: true },
              },
            )}
            failLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              tabTarget,
              {
                testStatus: { FAIL: true },
              },
            )}
            inconclusiveLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              tabTarget,
              {
                testStatus: {
                  MISS: true,
                  ERROR: true,
                  SKIP: true,
                  DONE: true,
                  NULL: true,
                },
              },
            )}
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
};

export function HardwareTable({
  treeTableRows,
  startTimestampInSeconds,
  endTimestampInSeconds,
  status,
  queryData,
  error,
  isLoading,
}: IHardwareTable): JSX.Element {
  const { listingSize } = useSearch({ strict: false });
  const navigate = useNavigate({ from: '/hardware-new' });

  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const { pagination, paginationUpdater } = usePaginationState(
    'hardwareListing',
    listingSize,
  );

  const data = useMemo(() => {
    return treeTableRows;
  }, [treeTableRows]);

  const columns = useMemo(
    () => getColumns(startTimestampInSeconds, endTimestampInSeconds),
    [startTimestampInSeconds, endTimestampInSeconds],
  );

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
              <ConditionalTableCell
                key={cell.id}
                cell={cell}
                linkProps={getLinkProps(
                  row,
                  startTimestampInSeconds,
                  endTimestampInSeconds,
                  tabTarget,
                )}
                linkClassName="w-full inline-block h-full"
              />
            );
          })}
        </TableRow>
      ))
    ) : (
      <TableRow>
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id="hardwareListing.notFound" />
        </TableCell>
      </TableRow>
    );
  }, [
    modelRows,
    columns.length,
    startTimestampInSeconds,
    endTimestampInSeconds,
  ]);

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
            values={formattedBreakLineValue}
          />
        </span>
        <div className="flex justify-end gap-y-2 max-[700px]:flex-wrap">
          <MemoizedInputTime
            navigateFrom="/hardware-new"
            defaultInterval={REDUCED_TIME_SEARCH}
          />
          <ItemsPerPageSelector
            table={table}
            onPaginationChange={navigateWithPageSize}
            className="pl-4"
          />
        </div>
        <div className="flex justify-end gap-y-2 max-[700px]:flex-wrap">
          <ListingCount table={table} intlLabel="global.hardware" />
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
            emptyLabel="hardwareListing.notFound"
          />
        }
      >
        <BaseTable headerComponents={tableHeaders}>
          <TableBody>{tableBody}</TableBody>
        </BaseTable>
      </QuerySwitcher>
      <PaginationInfo
        table={table}
        intlLabel="global.hardware"
        onPaginationChange={navigateWithPageSize}
      />
    </div>
  );
}
