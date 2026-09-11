import { useMemo, type JSX } from 'react';

import type { TreeListingItem } from '@/types/tree/Tree';

import { useTreeListing } from '@/api/tree';

import { Toaster } from '@/components/ui/toaster';

import { matchesRegexOrIncludes } from '@/lib/string';

import { MemoizedKcidevCommandButton } from '@/components/Footer/KcidevCommandButton';
import { createTreeListingCommand } from '@/components/Footer/kcidevCommand';

import type { TreeListingRoutesMap } from '@/utils/constants/treeListing';

import { TreeTable } from './TreeTable';

const TreeListingPage = ({
  inputFilter,
  urlFromMap,
  origin,
  intervalInDays,
}: {
  inputFilter: string;
  urlFromMap: TreeListingRoutesMap;
  origin: string;
  intervalInDays: number;
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
      <MemoizedKcidevCommandButton
        command={createTreeListingCommand({
          origin,
          days: intervalInDays,
          omittedFilters: inputFilter ? ['treeSearch'] : [],
        })}
      />
    ),
    [inputFilter, intervalInDays, origin],
  );

  return (
    <>
      <Toaster />
      <div className="flex flex-col gap-6">
        <div className="flex flex-wrap items-center justify-end gap-2">
          {kcidevComponent}
        </div>
        <TreeTable
          treeTableRows={listItems}
          status={status}
          queryData={data}
          error={error}
          isLoading={isLoading}
          urlFromMap={urlFromMap}
        />
      </div>
    </>
  );
};

export default TreeListingPage;
