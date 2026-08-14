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

    return data.filter(tree => {
      return (
        matchesRegexOrIncludes(tree.git_commit_hash, inputFilter) ||
        matchesRegexOrIncludes(tree.git_repository_branch, inputFilter) ||
        matchesRegexOrIncludes(tree.git_repository_url, inputFilter) ||
        matchesRegexOrIncludes(tree.tree_name, inputFilter)
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
