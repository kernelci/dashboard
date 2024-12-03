import type {
  ColumnDef,
  PaginationState,
  RowSelectionState,
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

import { useEffect, useMemo, useState } from 'react';

import { FormattedMessage } from 'react-intl';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';
import { TableHeader } from '@/components/Table/TableHeader';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';
import type { Trees } from '@/types/hardware/hardwareDetails';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { sanitizeTableValue } from '@/components/Table/tableUtils';
import { PaginationInfo } from '@/components/Table/PaginationInfo';
import { IndeterminateCheckbox } from '@/components/Checkbox/IndeterminateCheckbox';
import { useDebounce } from '@/hooks/useDebounce';
import { GroupedTestStatus } from '@/components/Status/Status';

const DEBOUNCE_INTERVAL = 2000;

interface IHardwareHeader {
  treeItems: Trees[];
  selectedIndexes?: number[];
  updateTreeFilters: (selectedIndexes: number[]) => void;
}

const columns: ColumnDef<Trees>[] = [
  {
    id: 'select',
    header: ({ table }) => (
      <IndeterminateCheckbox
        {...{
          checked: table.getIsAllRowsSelected(),
          indeterminate: table.getIsSomeRowsSelected(),
          onChange: table.getToggleAllRowsSelectedHandler(),
          disabled: table.getIsAllRowsSelected(),
        }}
      />
    ),
    cell: ({ row, table }) => (
      <IndeterminateCheckbox
        {...{
          checked: row.getIsSelected(),
          disabled:
            !row.getCanSelect() ||
            (Object.keys(table.getState().rowSelection).length === 1 &&
              row.getIsSelected()),
          onChange: row.getToggleSelectedHandler(),
        }}
      />
    ),
  },
  {
    accessorKey: 'treeName',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.tree" />
    ),
    cell: ({ row }): JSX.Element => (
      <Tooltip>
        <TooltipTrigger>{row.getValue('treeName')}</TooltipTrigger>
        <TooltipContent>{row.original.gitRepositoryUrl}</TooltipContent>
      </Tooltip>
    ),
  },
  {
    accessorKey: 'gitRepositoryBranch',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.branch" />
    ),
  },
  {
    accessorKey: 'headGitCommitName',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.commitTag" />
    ),
    cell: ({ row }): JSX.Element => (
      <Tooltip>
        <TooltipTrigger>
          {sanitizeTableValue(row.getValue('headGitCommitName'), false)}
        </TooltipTrigger>
        <TooltipContent>{row.original.headGitCommitHash}</TooltipContent>
      </Tooltip>
    ),
  },
  {
    accessorKey: 'selectedCommitStatusSummaryBuilds',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.build" />
    ),
    cell: ({ row }): JSX.Element => {
      const statusSummary = row.original.selectedCommitStatusSummary?.builds;
      return (
        <GroupedTestStatus
          fail={statusSummary?.invalid}
          pass={statusSummary?.valid}
          nullStatus={statusSummary?.null}
        />
      );
    },
  },
  {
    accessorKey: 'selectedCommitStatusSummaryBoots',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.bootStatus" />
    ),
    cell: ({ row }): JSX.Element => {
      const statusSummary = row.original.selectedCommitStatusSummary?.boots;
      return (
        <GroupedTestStatus
          fail={statusSummary?.FAIL}
          pass={statusSummary?.PASS}
          done={statusSummary?.DONE}
          error={statusSummary?.ERROR}
          miss={statusSummary?.MISS}
          skip={statusSummary?.SKIP}
        />
      );
    },
  },
  {
    accessorKey: 'selectedCommitStatusSummaryTests',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.test" />
    ),
    cell: ({ row }): JSX.Element => {
      const statusSummary = row.original.selectedCommitStatusSummary?.tests;
      return (
        <GroupedTestStatus
          fail={statusSummary?.FAIL}
          pass={statusSummary?.PASS}
          done={statusSummary?.DONE}
          error={statusSummary?.ERROR}
          miss={statusSummary?.MISS}
          skip={statusSummary?.SKIP}
        />
      );
    },
  },
];

const getInitialRowSelection = (
  selectedIndexes: number[],
  treeItemsLength: number,
): Record<string, boolean> => {
  if (selectedIndexes.length === 0) {
    return Object.fromEntries(
      Array.from({ length: treeItemsLength }, (_, i) => [i.toString(), true]),
    );
  }
  return Object.fromEntries(
    Array.from(selectedIndexes, treeIndex => [treeIndex.toString(), true]),
  );
};

const indexesFromRowSelection = (
  rowSelection: RowSelectionState,
  maxTreeItems: number,
): number[] => {
  const rowSelectionValues = Object.values(rowSelection);
  if (
    rowSelectionValues.length === maxTreeItems ||
    rowSelectionValues.length === 0
  ) {
    return [];
  }
  return Object.keys(rowSelection).map(rowId => parseInt(rowId));
};

export function HardwareHeader({
  treeItems,
  selectedIndexes = [],
  updateTreeFilters,
}: IHardwareHeader): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'treeName', desc: false },
  ]);
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 5,
  });

  const [rowSelection, setRowSelection] = useState(() =>
    getInitialRowSelection(selectedIndexes, treeItems.length),
  );

  const rowSelectionDebounced = useDebounce(rowSelection, DEBOUNCE_INTERVAL);

  useEffect(() => {
    const updatedSelection = indexesFromRowSelection(
      rowSelectionDebounced,
      treeItems.length,
    );
    updateTreeFilters(updatedSelection);
  }, [rowSelectionDebounced, treeItems.length, updateTreeFilters]);

  const table = useReactTable({
    data: treeItems,
    columns,
    getCoreRowModel: getCoreRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: setPagination,
    getFilteredRowModel: getFilteredRowModel(),
    getRowId: originalRow => originalRow.index,
    enableRowSelection: true,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      pagination,
      rowSelection,
    },
  });

  const groupHeaders = table.getHeaderGroups()[0]?.headers;
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
                rowSelection, // needed for the selection icon too
              })}
        </TableHead>
      );
    });
  }, [groupHeaders, sorting, rowSelection]);

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
  }, [modelRows, rowSelection]);

  return (
    <div className="flex flex-col gap-6 pb-4">
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableRows}</TableBody>
      </BaseTable>
      <PaginationInfo table={table} intlLabel="global.trees" />
    </div>
  );
}
