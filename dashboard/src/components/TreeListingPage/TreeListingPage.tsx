import { useMemo, type JSX } from 'react';

import type { TreeListingItem } from '@/types/tree/Tree';

import { useTreeListing } from '@/api/tree';

import { Toaster } from '@/components/ui/toaster';

import { matchesRegexOrIncludes } from '@/lib/string';

import { MemoizedKcidevFooter } from '@/components/Footer/KcidevFooter';

import type { TreeListingRoutesMap } from '@/utils/constants/treeListing';

import { TreeTable } from './TreeTable';

const TreeListingPage = ({
  inputFilter,
  urlFromMap,
}: {
  inputFilter: string;
  urlFromMap: TreeListingRoutesMap;
}): JSX.Element => {
  const { data, error, status, isLoading } = useTreeListing({
    searchFrom: urlFromMap.search,
  });

  const listItems: TreeListingItem[] = useMemo(() => {
    if (!data) {
      return [];
    }

    return data
      .filter(tree => {
        return (
          matchesRegexOrIncludes(tree.git_commit_hash, inputFilter) ||
          matchesRegexOrIncludes(tree.git_repository_branch, inputFilter) ||
          matchesRegexOrIncludes(tree.git_repository_url, inputFilter) ||
          matchesRegexOrIncludes(tree.tree_name, inputFilter)
        );
      })
      .sort((a, b) => {
        const currentATreeName = a.tree_name ?? '';
        const currentBTreeName = b.tree_name ?? '';
        const treeNameComparison =
          currentATreeName.localeCompare(currentBTreeName);

        if (treeNameComparison !== 0) {
          return treeNameComparison;
        }

        const currentABranch = a.git_repository_branch ?? '';
        const currentBBranch = b.git_repository_branch ?? '';
        const branchComparison = currentABranch.localeCompare(currentBBranch);
        if (branchComparison !== 0) {
          return branchComparison;
        }

        if (a.start_time === undefined || b.start_time === undefined) {
          return 0;
        }
        return (
          new Date(b.start_time).getTime() - new Date(a.start_time).getTime()
        );
      });
  }, [data, inputFilter]);

  const kcidevComponent = useMemo(
    () => (
      <MemoizedKcidevFooter commandGroup="trees" args={{ cmdName: 'trees' }} />
    ),
    [],
  );

  return (
    <>
      <Toaster />
      <div className="flex flex-col gap-6">
        <TreeTable
          treeTableRows={listItems}
          status={status}
          queryData={data}
          error={error}
          isLoading={isLoading}
          urlFromMap={urlFromMap}
        />
      </div>
      {kcidevComponent}
    </>
  );
};

export default TreeListingPage;
