import { useMemo, useState } from 'react';

import { FormattedMessage } from 'react-intl';

import { Tree, TreeFastPathResponse, TreeTableBody } from '@/types/tree/Tree';

import { usePagination } from '@/hooks/usePagination';

import TreeTable from '@/components/Table/TreeTable';

import { useTreeTable, useTreeTableFast } from '@/api/Tree';
import { TableInfo } from '@/components/Table/TableInfo';

import { formattedBreakLineValue } from '@/locales/messages';
import { ItemsPerPageValues } from '@/utils/constants/general';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import { NewTreeTable } from '../NewTables/NewTreeTable';

interface ITreeListingPage {
  inputFilter: string;
}

function isCompleteTree(
  data: Tree | TreeFastPathResponse[number],
): data is Tree {
  return 'build_status' in data;
}

const TreeListingPage = ({ inputFilter }: ITreeListingPage): JSX.Element => {
  const [itemsPerPage, setItemsPerPage] = useState(ItemsPerPageValues[0]);

  //TODO: Combine these 2 hooks inside a single hook
  const { data: fastData, status: fastStatus } = useTreeTableFast();
  const { data, error, isLoading } = useTreeTable({
    enabled: fastStatus === 'success' && !!fastData,
  });

  const listItems: TreeTableBody[] = useMemo(() => {
    if (!fastData || fastStatus == 'error') return [];

    const hasCompleteData = !isLoading && !!data;
    const currentData = hasCompleteData ? data : fastData;

    // TODO remove tree_names since is a filed that should not exist

    return currentData
      .filter(tree => {
        return (
          tree.git_commit_hash?.includes(inputFilter) ||
          tree.git_repository_branch?.includes(inputFilter) ||
          tree.git_repository_url?.includes(inputFilter) ||
          (isCompleteTree(tree)
            ? tree.tree_names?.some(name => name.includes(inputFilter))
            : tree.tree_name?.includes(inputFilter))
        );
      })
      .map((tree): TreeTableBody => {
        const buildStatus = isCompleteTree(tree)
          ? {
              valid: tree.build_status.valid,
              invalid: tree.build_status.invalid,
              null: tree.build_status.null,
            }
          : undefined;

        const testStatus = isCompleteTree(tree)
          ? {
              done: tree.test_status.done,
              error: tree.test_status.error,
              fail: tree.test_status.fail,
              miss: tree.test_status.miss,
              pass: tree.test_status.pass,
              skip: tree.test_status.skip,
            }
          : undefined;

        const bootStatus = isCompleteTree(tree)
          ? {
              done: tree.boot_status.done,
              error: tree.boot_status.error,
              fail: tree.boot_status.fail,
              miss: tree.boot_status.miss,
              pass: tree.boot_status.pass,
              skip: tree.boot_status.skip,
            }
          : undefined;

        return {
          commitHash: tree.git_commit_hash ?? '',
          commitName: tree.git_commit_name ?? '',
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

        if (treeNameComparison !== 0) return treeNameComparison;

        const branchComparison = a.branch.localeCompare(b.branch);
        if (branchComparison !== 0) return branchComparison;

        return new Date(b.date).getTime() - new Date(a.date).getTime();
      });
  }, [data, fastData, inputFilter, isLoading, fastStatus]);

  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(listItems.length, itemsPerPage);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  const tableInfoElement = (
    <TableInfo
      itemName="global.tree"
      startIndex={startIndex + 1}
      endIndex={endIndex}
      totalTrees={listItems.length}
      itemsPerPageValues={ItemsPerPageValues}
      itemsPerPageSelected={itemsPerPage}
      onChangeItemsPerPage={setItemsPerPage}
      onClickBack={onClickGoBack}
      onClickForward={onClickGoForward}
    />
  );

  return (
    <QuerySwitcher status={fastStatus} data={fastData}>
      {/* <div className="flex flex-col gap-6"> */}
      {/* <span className="text-left text-sm text-dimGray">
          <FormattedMessage
            id="global.projectUnderDevelopment"
            values={formattedBreakLineValue}
          />
        </span> */}
      {/* <div className="flex items-center justify-between gap-4">
          {tableInfoElement}
        </div>
        <TreeTable treeTableRows={listItems.slice(startIndex, endIndex)} />
        <div className="flex flex-col items-end">{tableInfoElement}</div> */}
      {/* </div> */}
      <NewTreeTable treeTableRows={listItems} />
    </QuerySwitcher>
  );
};

export default TreeListingPage;
