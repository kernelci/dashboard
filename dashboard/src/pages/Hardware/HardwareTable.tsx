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

import { FormattedMessage } from 'react-intl';

import { useNavigate, useSearch, type LinkProps } from '@tanstack/react-router';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';

import { formattedBreakLineValue } from '@/locales/messages';

import {
  TableBody,
  TableCell,
  TableCellWithLink,
  TableRow,
} from '@/components/ui/table';

import { GroupedTestStatusWithLink } from '@/components/Status/Status';
import { TableHeader } from '@/components/Table/TableHeader';
import { PaginationInfo } from '@/components/Table/PaginationInfo';

import type { HardwareTableItem } from '@/types/hardware';

import { statusCountToRequiredStatusCount, sumStatus } from '@/utils/status';

import { usePaginationState } from '@/hooks/usePaginationState';

import { zPossibleTabValidator } from '@/types/tree/TreeDetails';

import type { ListingTableColumnMeta } from '@/types/table';

import { RedirectFrom, type TFilter } from '@/types/general';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { MemoizedInputTime } from '@/components/InputTime';
import { REDUCED_TIME_SEARCH } from '@/utils/constants/general';

// TODO Extract and reuse the table
interface ITreeTable {
  treeTableRows: HardwareTableItem[];
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
}

const getLinkProps = (
  row: Row<HardwareTableItem>,
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  tabTarget?: string,
  newDiffFilter?: TFilter,
): LinkProps => {
  return {
    from: '/hardware',
    to: '/hardware/$hardwareId',
    params: { hardwareId: row.original.hardware_name },
    search: previousSearch => ({
      ...previousSearch,
      currentPageTab: zPossibleTabValidator.parse(tabTarget),
      startTimestampInSeconds,
      endTimestampInSeconds,
      diffFilter: { ...previousSearch.diffFilter, ...newDiffFilter },
    }),
    state: s => ({
      ...s,
      id: row.original.hardware_name,
      from: RedirectFrom.Hardware,
      hardwareStatusCount: {
        builds: row.original.build_status_summary,
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
): ColumnDef<HardwareTableItem>[] => {
  return [
    {
      accessorKey: 'hardware_name',
      header: ({ column }): JSX.Element => (
        <TableHeader column={column} intlKey="global.name" />
      ),
      meta: {
        tabTarget: 'global.builds',
      },
    },
    {
      accessorKey: 'platform',
      header: ({ column }): JSX.Element => (
        <TableHeader column={column} intlKey="global.platform" />
      ),
      cell: ({ row }): JSX.Element => {
        const platforms = row.original.platform;
        if (Array.isArray(platforms)) {
          return (
            <Tooltip>
              <TooltipTrigger>
                <FormattedMessage id="hardware.multiplePlatforms" />
              </TooltipTrigger>
              <TooltipContent>{platforms.join(', ')}</TooltipContent>
            </Tooltip>
          );
        }
        return <>{platforms}</>;
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
}: ITreeTable): JSX.Element {
  const { listingSize } = useSearch({ strict: false });
  const navigate = useNavigate({ from: '/hardware' });

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
              <TableCellWithLink
                key={cell.id}
                linkClassName="w-full inline-block h-full"
                linkProps={getLinkProps(
                  row,
                  startTimestampInSeconds,
                  endTimestampInSeconds,
                  tabTarget,
                )}
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
      <div className="flex items-center justify-between gap-4">
        <span className="text-dim-gray text-left text-sm">
          <FormattedMessage
            id="global.projectUnderDevelopment"
            values={formattedBreakLineValue}
          />
        </span>
        <div className="flex items-center justify-between gap-10">
          <MemoizedInputTime
            navigateFrom="/hardware"
            defaultInterval={REDUCED_TIME_SEARCH}
          />
          <PaginationInfo
            table={table}
            intlLabel="global.hardwares"
            onPaginationChange={navigateWithPageSize}
          />
        </div>
      </div>
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableBody}</TableBody>
      </BaseTable>
      <PaginationInfo
        table={table}
        intlLabel="global.hardwares"
        onPaginationChange={navigateWithPageSize}
      />
    </div>
  );
}
