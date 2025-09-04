import type { Cell } from '@tanstack/react-table';
import { flexRender } from '@tanstack/react-table';
import type { LinkProps } from '@tanstack/react-router';
import { Link } from '@tanstack/react-router';
import { memo, useMemo, type JSX } from 'react';

import { TableCell, TableCellWithLink } from '@/components/ui/table';
import CopyButton from '@/components/Button/CopyButton';
import { gitCommitValueSelector } from '@/components/Tooltip/CommitTagTooltip';
import type { TreeTableBody } from '@/types/tree/Tree';
import type { HardwareItem } from '@/types/hardware';

interface ConditionalTableCellProps<T = TreeTableBody | HardwareItem> {
  cell: Cell<T, unknown>;
  linkProps: LinkProps;
  linkClassName?: string;
}

type ColumnType = 'status' | 'git_commit_tags' | 'regular';

const isTreeTableBody = (data: unknown): data is TreeTableBody => {
  return (
    typeof data === 'object' &&
    data !== null &&
    'git_commit_hash' in data &&
    'git_commit_name' in data &&
    'git_commit_tags' in data
  );
};

/**
 * Adaptive table cell component that automatically handles different cell types:
 * - Status columns: Uses TableCell without wrapper link (prevents nested <a> tags)
 * - Git commit tags: Uses TableCell with custom link + copy button
 * - Regular columns: Uses TableCellWithLink for navigation
 */
const ConditionalTableCellComponent = <T = TreeTableBody | HardwareItem,>({
  cell,
  linkProps,
  linkClassName = 'w-full inline-block h-full',
}: ConditionalTableCellProps<T>): JSX.Element => {
  const cellContent = useMemo(() => {
    return flexRender(cell.column.columnDef.cell, cell.getContext());
  }, [cell]);

  const columnType = useMemo((): ColumnType => {
    const statusColumnIds = ['build_status', 'boot_status', 'test_status'];
    const columnId = cell.column.id;
    const columnDefId = cell.column.columnDef.id;

    if (statusColumnIds.some(statusId => columnId.includes(statusId))) {
      return 'status';
    }

    if (columnDefId === 'git_commit_tags') {
      return 'git_commit_tags';
    }

    return 'regular';
  }, [cell.column.id, cell.column.columnDef.id]);

  const gitCommitValue = useMemo(() => {
    if (columnType !== 'git_commit_tags') {
      return null;
    }

    const rowData = cell.row.original;
    if (!isTreeTableBody(rowData)) {
      return null;
    }

    return gitCommitValueSelector({
      commitHash: rowData.git_commit_hash,
      commitName: rowData.git_commit_name,
      commitTags: rowData.git_commit_tags,
    }).content;
  }, [columnType, cell.row.original]);

  switch (columnType) {
    case 'status':
      return (
        <TableCell key={cell.id} className="p-4">
          {cellContent}
        </TableCell>
      );

    case 'git_commit_tags':
      if (gitCommitValue) {
        // The CopyButton is defined outside of the cell column because I couldn't find
        // a way to include it within the cell definition while also using it outside of
        // a Link component. I attempted to modify CommitTagTooltip to wrap the tooltip
        // inside a Link component, but this would require the column cell to be a function
        // that receives LinkProps and returns the CommitTagTooltip component. However,
        // I couldn't figure out how to achieve this using TanStack Table, as
        // `cell.getValue()` would return an array instead of the expected function.
        return (
          <TableCell key={cell.id}>
            <Link className="inline-block" {...linkProps}>
              {cellContent}
            </Link>
            <CopyButton value={gitCommitValue} />
          </TableCell>
        );
      }
      return <TableCell key={cell.id}>{cellContent}</TableCell>;

    case 'regular':
    default:
      return (
        <TableCellWithLink
          key={cell.id}
          linkClassName={linkClassName}
          linkProps={linkProps}
        >
          {cellContent}
        </TableCellWithLink>
      );
  }
};

export const ConditionalTableCell = memo(ConditionalTableCellComponent) as <
  T = TreeTableBody | HardwareItem,
>(
  props: ConditionalTableCellProps<T>,
) => JSX.Element;
