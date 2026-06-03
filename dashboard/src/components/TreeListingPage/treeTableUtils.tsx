import type { ColumnDef } from '@tanstack/react-table';
import type { JSX } from 'react';

import { TooltipDateTime } from '@/components/TooltipDateTime';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { TableHeader } from '@/components/Table/TableHeader';
import { CommitTagTooltip } from '@/components/Tooltip/CommitTagTooltip';
import { sanitizeTableValue } from '@/components/Table/tableUtils';
import type { TreeListingItem } from '@/types/tree/Tree';
import { shouldShowRelativeDate } from '@/lib/date';
import { valueOrEmpty } from '@/lib/string';
import { PinnedTrees } from '@/utils/constants/tables';
import { makeTreeIdentifierKey } from '@/utils/trees';

export const commonTreeTableColumns: ColumnDef<TreeListingItem>[] = [
  {
    accessorKey: 'tree_name',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.tree" />
    ),
    cell: ({ row }): JSX.Element => {
      return (
        <Tooltip>
          <TooltipTrigger>
            {sanitizeTableValue(row.getValue('tree_name') ?? '', false)}
          </TooltipTrigger>
          <TooltipContent>
            <a
              href={row.original.git_repository_url}
              target="_blank"
              rel="noreferrer"
            >
              {sanitizeTableValue(row.original.git_repository_url, false)}
            </a>
          </TooltipContent>
        </Tooltip>
      );
    },
    meta: {
      tabTarget: 'global.builds',
    },
  },
  {
    accessorKey: 'git_repository_branch',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.branch" />
    ),
    cell: ({ row }) => valueOrEmpty(row.getValue('git_repository_branch')),
    meta: {
      tabTarget: 'global.builds',
    },
  },
  {
    id: 'git_commit_tags',
    accessorKey: 'git_commit_tags',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.commitTag" />
    ),
    cell: ({ row }): JSX.Element => (
      <CommitTagTooltip
        commitName={row.original.git_commit_name}
        commitHash={row.original.git_commit_hash}
        commitTags={row.original.git_commit_tags}
      />
    ),
    meta: {
      tabTarget: 'global.builds',
    },
  },
  {
    accessorKey: 'start_time',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.date" />
    ),
    cell: ({ row }): JSX.Element => (
      <TooltipDateTime
        dateTime={row.getValue('start_time')}
        lineBreak={true}
        showRelative={shouldShowRelativeDate(row.getValue('start_time'))}
      />
    ),
    meta: {
      tabTarget: 'global.builds',
    },
  },
];

export const sortTreesWithPinnedFirst = <T extends TreeListingItem>(
  treeTableRows: T[],
): T[] => {
  return treeTableRows.sort((a, b) => {
    const aKey = makeTreeIdentifierKey({
      treeName: valueOrEmpty(a.tree_name),
      gitRepositoryBranch: valueOrEmpty(a.git_repository_branch),
      separator: '/',
    });
    const bKey = makeTreeIdentifierKey({
      treeName: valueOrEmpty(b.tree_name),
      gitRepositoryBranch: valueOrEmpty(b.git_repository_branch),
      separator: '/',
    });

    const aIsPinned = PinnedTrees.some(regex => regex.test(aKey));
    const bIsPinned = PinnedTrees.some(regex => regex.test(bKey));

    if (aIsPinned && !bIsPinned) {
      return -1;
    }
    if (!aIsPinned && bIsPinned) {
      return 1;
    }

    return aKey.localeCompare(bKey);
  });
};
