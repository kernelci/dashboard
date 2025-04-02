import { useMemo, type JSX } from 'react';

import type {
  Tree,
  TreeFastPathResponse,
  TreeTableBody,
} from '@/types/tree/Tree';

import { useTreeTable, useTreeTableFast } from '@/api/tree';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import { Toaster } from '@/components/ui/toaster';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import { matchesRegexOrIncludes } from '@/lib/string';

import { TreeTable } from './TreeTable';

interface ITreeListingPage {
  inputFilter: string;
}

function isCompleteTree(
  data: Tree | TreeFastPathResponse[number],
): data is Tree {
  return 'build_status' in data;
}

const TreeListingPage = ({ inputFilter }: ITreeListingPage): JSX.Element => {
  //TODO: Combine these 2 hooks inside a single hook
  const {
    data: fastData,
    status: fastStatus,
    error: fastError,
    isLoading: isFastLoading,
  } = useTreeTableFast();
  const { data, error, isLoading } = useTreeTable({
    enabled: fastStatus === 'success' && !!fastData,
  });

  const listItems: TreeTableBody[] = useMemo(() => {
    if (!fastData || fastStatus === 'error') {
      return [];
    }

    const hasCompleteData = !isLoading && !!data;
    const currentData = hasCompleteData ? data : fastData;

    return currentData
      .filter(tree => {
        return (
          matchesRegexOrIncludes(tree.git_commit_hash, inputFilter) ||
          matchesRegexOrIncludes(tree.git_repository_branch, inputFilter) ||
          matchesRegexOrIncludes(tree.git_repository_url, inputFilter) ||
          matchesRegexOrIncludes(tree.tree_name, inputFilter)
        );
      })
      .map((tree): TreeTableBody => {
        if (!isCompleteTree(tree)) {
          return {
            git_commit_hash: tree.git_commit_hash,
            patchset_hash: tree.patchset_hash,
            tree_name: tree.tree_name,
            git_repository_branch: tree.git_repository_branch,
            start_time: tree.start_time,
            git_repository_url: tree.git_repository_url,
            git_commit_name: tree.git_commit_name,
            git_commit_tags: tree.git_commit_tags ?? [],
          };
        }

        return tree;
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
  }, [data, fastData, inputFilter, isLoading, fastStatus]);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <QuerySwitcher
      status={fastStatus}
      data={fastData}
      customError={
        <MemoizedSectionError
          isLoading={isFastLoading}
          errorMessage={fastError?.message}
          emptyLabel="treeListing.notFound"
        />
      }
    >
      <Toaster />
      <div className="flex flex-col gap-6">
        <TreeTable treeTableRows={listItems} />
      </div>
    </QuerySwitcher>
  );
};

export default TreeListingPage;
