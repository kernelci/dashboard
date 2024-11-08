import type {
  ColumnDef,
  PaginationState,
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

import { useMemo, useState } from 'react';

import { FormattedMessage } from 'react-intl';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';
import { TableHeader } from '@/components/Table/TableHeader';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';
import type { Trees } from '@/types/hardware/hardwareDetails';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { sanitizeTableValue } from '@/components/Table/tableUtils';
import { PaginationInfo } from '@/components/Table/PaginationInfo';
// import { IndeterminateCheckbox } from '@/components/Checkbox/IndeterminateCheckbox';

interface IHardwareHeader {
  treeItems: Trees[];
}

const columns: ColumnDef<Trees>[] = [
  // {
  //   id: 'select',
  //   header: ({ table }) => (
  //     <IndeterminateCheckbox
  //       {...{
  //         checked: table.getIsAllRowsSelected(),
  //         indeterminate: table.getIsSomeRowsSelected(),
  //         onChange: table.getToggleAllRowsSelectedHandler(),
  //         disabled: true,
  //       }}
  //     />
  //   ),
  //   cell: ({ row }) => (
  //     <IndeterminateCheckbox
  //       {...{
  //         checked: row.getIsSelected(),
  //         disabled: !row.getCanSelect(),
  //         onChange: row.getToggleSelectedHandler(),
  //       }}
  //     />
  //   ),
  // },
  {
    accessorKey: 'treeName',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeTable.tree',
        intlDefaultMessage: 'Tree',
      }),
    cell: ({ row }): JSX.Element => (
      <Tooltip>
        <TooltipTrigger>{row.getValue('treeName')}</TooltipTrigger>
        <TooltipContent>{row.original.gitRepositoryUrl}</TooltipContent>
      </Tooltip>
    ),
  },
  {
    accessorKey: 'gitRepositoryBranch',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeTable.branch',
        intlDefaultMessage: 'Branch',
      }),
  },
  {
    accessorKey: 'gitCommitName',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeTable.commitTag',
        intlDefaultMessage: 'Commit/Tag',
      }),
    cell: ({ row }): JSX.Element => (
      <Tooltip>
        <TooltipTrigger>
          {sanitizeTableValue(row.getValue('gitCommitName'), false)}
        </TooltipTrigger>
        <TooltipContent>{row.original.gitCommitHash}</TooltipContent>
      </Tooltip>
    ),
  },
];

const sanitizeTreeItems = (treeItems: Record<string, string>[]): Trees[] => {
  return treeItems.map(tree => ({
    treeName: tree['tree_name'] ?? '-',
    gitRepositoryBranch: tree['git_repository_branch'] ?? '-',
    gitCommitName: tree['git_commit_name'] ?? '-',
    gitCommitHash: tree['git_commit_hash'],
    gitRepositoryUrl: tree['git_repository_url'] ?? '-',
  }));
};

export function HardwareHeader({ treeItems }: IHardwareHeader): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'treeName', desc: false },
  ]);
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 5,
  });
  // const [rowSelection, setRowSelection] = useState({});

  const data = useMemo(() => {
    return sanitizeTreeItems(treeItems);
  }, [treeItems]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: setPagination,
    getFilteredRowModel: getFilteredRowModel(),
    // enableRowSelection: false,
    // onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      pagination,
      // rowSelection,
    },
  });

  const groupHeaders = table.getHeaderGroups()[0]?.headers;
  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map(header => {
      return (
        <TableHead key={header.id}>
          {header.isPlaceholder
            ? null
            : flexRender(header.column.columnDef.header, header.getContext())}
        </TableHead>
      );
    });
    // TODO: remove exhaustive-deps and change memo  (all tables)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [groupHeaders, sorting /*, rowSelection*/]);

  const modelRows = table.getRowModel().rows;
  const tableRows = useMemo((): JSX.Element[] | JSX.Element => {
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
      <TableRow key="no-results">
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id="global.noResults" />
        </TableCell>
      </TableRow>
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [modelRows /*, rowSelection*/]);

  return (
    <div className="flex flex-col gap-6 pb-4">
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableRows}</TableBody>
      </BaseTable>
      <PaginationInfo table={table} data={data} intlLabel="global.trees" />
    </div>
  );
}
