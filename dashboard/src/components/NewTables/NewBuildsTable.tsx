import {
  ColumnDef,
  ColumnFiltersState,
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

import { Fragment, useCallback, useMemo, useState } from 'react';
import { useNavigate, useSearch } from '@tanstack/react-router';

import { FormattedMessage, useIntl } from 'react-intl';

import {
  AccordionItemBuilds,
  BuildsTableFilter,
  possibleBuildsTableFilter,
} from '@/types/tree/TreeDetails';

import BaseTable, { TableHead } from '../Table/BaseTable';
import { TableBody, TableCell, TableRow } from '../ui/table';

import TableStatusFilter from '../Table/TableStatusFilter';

import { TooltipDateTime } from '../TooltipDateTime';

import ColoredCircle from '../ColoredCircle/ColoredCircle';

import { ItemType } from '../ListingItem/ListingItem';

import { NewTableHeader } from './NewTableHeader';
import { PaginationInfo } from './PaginationInfo';

export interface IBuildsTable {
  buildItems: AccordionItemBuilds[];
}

const columns: ColumnDef<AccordionItemBuilds>[] = [
  {
    accessorKey: 'config',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeDetails.config',
        intlDefaultMessage: 'Config',
      }),
  },
  {
    accessorKey: 'compiler',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeDetails.compiler',
        intlDefaultMessage: 'Compiler',
      }),
  },
  {
    accessorKey: 'date',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
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
      NewTableHeader({
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
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeDetails.buildTime',
        intlDefaultMessage: 'Build Time',
      }),
  },
  {
    accessorKey: 'status',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeDetails.status',
        intlDefaultMessage: 'Status',
        tooltipId: 'buildTab.statusTooltip',
      }),
    cell: ({ row }): JSX.Element => {
      if (row.getValue('status') === 'valid') {
        return <FormattedMessage id="global.pass" defaultMessage={'Pass'} />;
      } else if (row.getValue('status') === 'invalid') {
        return (
          <FormattedMessage id="global.invalid" defaultMessage={'Invalid'} />
        );
      } else if (row.getValue('status') === 'null') {
        return <span>-</span>;
      }
      return (
        <FormattedMessage id="global.unknown" defaultMessage={'Unknown'} />
      );
    },
  },
];

export function NewBuildsTable({ buildItems }: IBuildsTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [expanded, setExpanded] = useState<ExpandedState>({});
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const { tableFilter: filterBy } = useSearch({
    from: '/tree/$treeId/',
  });
  const {
    tableFilter: { buildsTable: selectedFilter },
  } = useSearch({ from: '/tree/$treeId/' });

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

  const data: AccordionItemBuilds[] =
    filterBy.buildsTable === 'all'
      ? rawData
      : rawData?.filter(
          row => row.status && row.status === filterBy.buildsTable,
        );

  const onClickFilter = useCallback(
    (type: BuildsTableFilter) => {
      console.log('clicked on ' + type);
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              buildsTable: type,
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
    (): { label: string; value: BuildsTableFilter; isSelected: boolean }[] => [
      {
        label: intl.formatMessage({ id: 'global.all' }),
        value: possibleBuildsTableFilter[2],
        isSelected: selectedFilter === possibleBuildsTableFilter[2],
      },
      {
        label: intl.formatMessage({ id: 'global.successful' }),
        value: possibleBuildsTableFilter[1],
        isSelected: selectedFilter === possibleBuildsTableFilter[1],
      },
      {
        label: intl.formatMessage({ id: 'global.failed' }),
        value: possibleBuildsTableFilter[0],
        isSelected: selectedFilter === possibleBuildsTableFilter[0],
      },
      {
        label: intl.formatMessage({ id: 'global.inconclusive' }),
        value: possibleBuildsTableFilter[3],
        isSelected: selectedFilter === possibleBuildsTableFilter[3],
      },
    ],
    [intl, selectedFilter],
  );

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
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
      columnFilters,
      pagination,
      expanded,
    },
  });

  return (
    <div className="flex flex-col gap-6 pb-4">
      <TableStatusFilter
        filters={filters}
        onClickBuild={(filter: BuildsTableFilter) => onClickFilter(filter)}
      />
      <BaseTable
        headers={[]}
        headerComponents={table.getHeaderGroups()[0].headers.map(header => {
          return (
            <TableHead key={header.id} className="border-b px-0 font-bold">
              {header.isPlaceholder
                ? null
                : flexRender(
                    header.column.columnDef.header,
                    header.getContext(),
                  )}
            </TableHead>
          );
        })}
      >
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map(row => (
              <Fragment key={row.id}>
                <TableRow
                  className="cursor-pointer hover:bg-lightBlue"
                  onClick={() => {
                    if (row.getCanExpand()) row.toggleExpanded();
                  }}
                >
                  {row.getVisibleCells().map(cell => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
                {row.getIsExpanded() && (
                  <TableRow>
                    <TableCell colSpan={6} className="p-0">
                      <p>beep</p>
                    </TableCell>
                  </TableRow>
                )}
              </Fragment>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                <FormattedMessage id="global.noResults" />
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </BaseTable>
      <PaginationInfo
        table={table}
        pagination={pagination}
        data={data}
        label="builds"
      />
    </div>
  );
}
