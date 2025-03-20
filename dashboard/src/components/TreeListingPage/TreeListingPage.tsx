import { useMemo, type JSX } from 'react';

import type {
  TableTestStatus,
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

    // TODO remove tree_names since is a field that should not exist

    return currentData
      .filter(tree => {
        return (
          matchesRegexOrIncludes(tree.git_commit_hash, inputFilter) ||
          matchesRegexOrIncludes(tree.git_repository_branch, inputFilter) ||
          matchesRegexOrIncludes(tree.git_repository_url, inputFilter) ||
          (isCompleteTree(tree)
            ? tree.tree_names?.some(name =>
                matchesRegexOrIncludes(name, inputFilter),
              )
            : matchesRegexOrIncludes(tree.tree_name, inputFilter))
        );
      })
      .map((tree): TreeTableBody => {
        const buildStatus = isCompleteTree(tree)
          ? {
              PASS: tree.build_status.PASS,
              FAIL: tree.build_status.FAIL,
              NULL: tree.build_status.NULL,
              ERROR: tree.build_status.ERROR,
              MISS: tree.build_status.MISS,
              DONE: tree.build_status.DONE,
              SKIP: tree.build_status.SKIP,
            }
          : undefined;

        const testStatus = isCompleteTree(tree)
          ? ({
              error: tree.test_status.error,
              fail: tree.test_status.fail,
              miss: tree.test_status.miss,
              pass: tree.test_status.pass,
              skip: tree.test_status.skip,
              done: tree.test_status.done,
              null: tree.test_status.null,
            } satisfies TableTestStatus)
          : undefined;

        const bootStatus = isCompleteTree(tree)
          ? ({
              done: tree.boot_status.done,
              error: tree.boot_status.error,
              fail: tree.boot_status.fail,
              miss: tree.boot_status.miss,
              pass: tree.boot_status.pass,
              skip: tree.boot_status.skip,
              null: tree.boot_status.null,
            } satisfies TableTestStatus)
          : undefined;

        return {
          commitHash: tree.git_commit_hash ?? '',
          commitName: tree.git_commit_name ?? '',
          commitTag: tree.git_commit_tags,
          patchsetHash: tree.patchset_hash ?? '',
          buildStatus,
          testStatus,
          bootStatus,
          id: tree.git_commit_hash ?? '',
          tree_name: isCompleteTree(tree) ? tree.tree_names[0] : tree.tree_name,
          branch: tree.git_repository_branch ?? '',
          date: tree.start_time ?? '',
          url: tree.git_repository_url ?? '',
        };
      })
      .sort((a, b) => {
        const currentATreeName = a.tree_name ?? '';
        const currentBTreeName = b.tree_name ?? '';
        const treeNameComparison =
          currentATreeName.localeCompare(currentBTreeName);

        if (treeNameComparison !== 0) {
          return treeNameComparison;
        }

        const branchComparison = a.branch.localeCompare(b.branch);
        if (branchComparison !== 0) {
          return branchComparison;
        }

        return new Date(b.date).getTime() - new Date(a.date).getTime();
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
