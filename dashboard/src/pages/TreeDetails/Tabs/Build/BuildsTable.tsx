import {
  ColumnDef,
  ExpandedState,
  flexRender,
  getCoreRowModel,
  getExpandedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  PaginationState,
  SortingState,
  useReactTable,
} from '@tanstack/react-table';

import { Fragment, ReactElement, useCallback, useMemo, useState } from 'react';
import { useNavigate, useSearch } from '@tanstack/react-router';

import { FormattedMessage, useIntl } from 'react-intl';

import { MdCheck, MdClose } from 'react-icons/md';

import {
  AccordionItemBuilds,
  BuildsTableFilter,
  possibleBuildsTableFilter,
} from '@/types/tree/TreeDetails';
import { TableHeader } from '@/components/Table/TableHeader';
import TableStatusFilter from '@/components/Table/TableStatusFilter';
import BaseTable, { TableHead } from '@/components/Table/BaseTable';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';
import { PaginationInfo } from '@/components/Table/PaginationInfo';
import { TooltipDateTime } from '@/components/TooltipDateTime';
import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import { ItemType } from '@/components/ListingItem/ListingItem';
import AccordionBuildContent from '@/pages/TreeDetails/Tabs/Build/BuildAccordionContent';

export interface IBuildsTable {
  buildItems: AccordionItemBuilds[];
}

type BuildStatus = Record<AccordionItemBuilds['status'], ReactElement>;

const buildStatusMap: BuildStatus = {
  valid: <MdCheck className="text-green" />,
  invalid: <MdClose className="text-red" />,
  null: <span>-</span>,
};

const columns: ColumnDef<AccordionItemBuilds>[] = [
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
      return buildStatusMap[row.getValue('status') as keyof BuildStatus];
    },
  },
];

export function BuildsTable({ buildItems }: IBuildsTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [expanded, setExpanded] = useState<ExpandedState>({});
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const { tableFilter } = useSearch({
    from: '/tree/$treeId/',
  });
  const selectedFilter = tableFilter.buildsTable;

  const navigate = useNavigate({ from: '/tree/$treeId' });
  const intl = useIntl();

  const rawData = useMemo((): AccordionItemBuilds[] => {
    return buildItems?.map(row => ({
      ...row,
      config: row.config ?? '-',
      compiler: row.compiler ?? '-',
      buildTime: row.buildTime ? (
        <span>
          {typeof row.buildTime === 'number'
            ? Math.floor(row.buildTime) + ' '
            : row.buildTime}
          <FormattedMessage id="global.seconds" />
        </span>
      ) : (
        '-'
      ),
      date: row.date,
    }));
  }, [buildItems]);

  const data = useMemo((): AccordionItemBuilds[] => {
    return selectedFilter === 'all'
      ? rawData
      : rawData?.filter(row => row.status && row.status === selectedFilter);
  }, [selectedFilter, rawData]);

  const filterCount = useMemo(() => {
    const count = possibleBuildsTableFilter.reduce(
      (acc, filter) => {
        if (rawData)
          acc[filter] = rawData?.reduce(
            (total, row) => (row.status === filter ? total + 1 : total),
            0,
          );
        return acc;
      },
      {} as Record<(typeof possibleBuildsTableFilter)[number], number>,
    );
    count.all = rawData ? rawData.length : 0;

    return count;
  }, [rawData]);

  const onClickFilter = useCallback(
    (filter: BuildsTableFilter) => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              buildsTable: filter,
              bootsTable: previousParams.tableFilter.bootsTable,
              testsTable: previousParams.tableFilter.testsTable,
            },
          };
        },
      });
    },
    [navigate],
  );

  const filters = useMemo(
    () => [
      {
        label: intl.formatMessage(
          { id: 'global.allCount' },
          { count: filterCount[possibleBuildsTableFilter[2]] },
        ),
        value: possibleBuildsTableFilter[2],
        isSelected: selectedFilter === possibleBuildsTableFilter[2],
      },
      {
        label: intl.formatMessage(
          { id: 'global.successCount' },
          { count: filterCount[possibleBuildsTableFilter[1]] },
        ),
        value: possibleBuildsTableFilter[1],
        isSelected: selectedFilter === possibleBuildsTableFilter[1],
      },
      {
        label: intl.formatMessage(
          { id: 'global.failedCount' },
          { count: filterCount[possibleBuildsTableFilter[0]] },
        ),
        value: possibleBuildsTableFilter[0],
        isSelected: selectedFilter === possibleBuildsTableFilter[0],
      },
      {
        label: intl.formatMessage(
          { id: 'global.inconclusiveCount' },
          { count: filterCount[possibleBuildsTableFilter[3]] },
        ),
        value: possibleBuildsTableFilter[3],
        isSelected: selectedFilter === possibleBuildsTableFilter[3],
      },
    ],
    [intl, filterCount, selectedFilter],
  );

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: setPagination,
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getRowCanExpand: _ => true,
    getExpandedRowModel: getExpandedRowModel(),
    onExpandedChange: setExpanded,
    state: {
      sorting,
      pagination,
      expanded,
    },
  });

  const groupHeaders = table.getHeaderGroups()[0]?.headers;
  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map(header => {
      return (
        <TableHead key={header.id} className="border-b px-0 font-bold">
          {header.isPlaceholder
            ? null
            : flexRender(header.column.columnDef.header, header.getContext())}
        </TableHead>
      );
    });
    // TODO: remove exhaustive-deps and change memo (all tables)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [groupHeaders, sorting]);

  const modelRows = table.getRowModel().rows;
  const tableBody = useMemo((): JSX.Element[] | JSX.Element => {
    {
      return modelRows?.length ? (
        modelRows.map(row => {
          return (
            <Fragment key={row.id}>
              <TableRow
                className="cursor-pointer hover:bg-lightBlue"
                onClick={() => {
                  if (row.getCanExpand()) row.toggleExpanded();
                }}
                data-state={row.getIsExpanded() ? 'open' : 'closed'}
              >
                {row.getVisibleCells().map(cell => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
              {row.getIsExpanded() && (
                <TableRow>
                  <TableCell colSpan={6} className="p-0">
                    <div className="max-h-[400px] w-full overflow-scroll border-b border-darkGray bg-lightGray p-8">
                      <AccordionBuildContent accordionData={row.original} />
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </Fragment>
          );
        })
      ) : (
        <TableRow>
          <TableCell colSpan={columns.length} className="h-24 text-center">
            <FormattedMessage id="global.noResults" />
          </TableCell>
        </TableRow>
      );
    }
  }, [modelRows]);

  return (
    <div className="flex flex-col gap-6 pb-4">
      <div className="flex justify-between">
        <TableStatusFilter filters={filters} onClickBuild={onClickFilter} />
        <PaginationInfo
          table={table}
          data={data}
          intlLabel="treeDetails.boots"
        />
      </div>
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableBody}</TableBody>
      </BaseTable>
      <PaginationInfo
        table={table}
        data={data}
        intlLabel="treeDetails.builds"
      />
    </div>
  );
}
