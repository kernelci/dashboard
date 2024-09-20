import { useSearch } from '@tanstack/react-router';

import { useMemo, useState } from 'react';

import { FormattedMessage } from 'react-intl';

import { zOrigin, TreeTableBody } from '@/types/tree/Tree';

import { usePagination } from '@/hooks/usePagination';

import { Skeleton } from '@/components/Skeleton';

import TreeTable from '@/components/Table/TreeTable';

import { useTreeTable } from '@/api/Tree';
import { TableInfo } from '@/components/Table/TableInfo';

import { formattedBreakLineValue } from '@/locales/messages';
import { ItemsPerPageValues } from '@/utils/constants/general';

interface ITreeListingPage {
  inputFilter: string;
}

const TreeListingPage = ({ inputFilter }: ITreeListingPage): JSX.Element => {
  const { origin: unsafeOrigin } = useSearch({ strict: false });
  const origin = zOrigin.parse(unsafeOrigin);
  const [itemsPerPage, setItemsPerPage] = useState(ItemsPerPageValues[0]);

  const { data, error, isLoading } = useTreeTable(origin);

  const listItems: TreeTableBody[] = useMemo(() => {
    if (!data || error) return [];

    return data
      .filter(
        tree =>
          tree.git_commit_hash?.includes(inputFilter) ||
          tree.tree_names.some(name => name.includes(inputFilter)) ||
          tree.git_repository_branch?.includes(inputFilter) ||
          tree.git_repository_url?.includes(inputFilter),
      )
      .map(
        (tree): TreeTableBody => ({
          commitHash: tree.git_commit_hash ?? '',
          commitName: tree.git_commit_name ?? '',
          patchsetHash: tree.patchset_hash ?? '',
          buildStatus: {
            valid: tree.build_status.valid,
            invalid: tree.build_status.invalid,
            null: tree.build_status.null,
          },
          testStatus: {
            done: tree.test_status.done,
            error: tree.test_status.error,
            fail: tree.test_status.fail,
            miss: tree.test_status.miss,
            pass: tree.test_status.pass,
            skip: tree.test_status.skip,
          },
          bootStatus: {
            done: tree.boot_status.done,
            error: tree.boot_status.error,
            fail: tree.boot_status.fail,
            miss: tree.boot_status.miss,
            pass: tree.boot_status.pass,
            skip: tree.boot_status.skip,
          },
          id: tree.git_commit_hash ?? '',
          tree_names: tree.tree_names,
          branch: tree.git_repository_branch ?? '',
          date: tree.start_time ?? '',
          url: tree.git_repository_url ?? '',
        }),
      )
      .sort((a, b) => {
        const currentATreeName = a.tree_names[0] ?? '';
        const currentBTreeName = b.tree_names[0] ?? '';
        const treeNameComparison =
          currentATreeName.localeCompare(currentBTreeName);

        if (treeNameComparison !== 0) return treeNameComparison;

        const branchComparison = a.branch.localeCompare(b.branch);
        if (branchComparison !== 0) return branchComparison;

        return new Date(b.date).getTime() - new Date(a.date).getTime();
      });
  }, [data, error, inputFilter]);

  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(listItems.length, itemsPerPage);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  if (isLoading)
    return (
      <Skeleton>
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );

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

  return data && data.length > 0 ? (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-4">
        <span className="text-left text-sm text-dimGray">
          <FormattedMessage
            id="global.projectUnderDevelopment"
            values={formattedBreakLineValue}
          />
        </span>
        {tableInfoElement}
      </div>
      <TreeTable treeTableRows={listItems.slice(startIndex, endIndex)} />
      <div className="flex flex-col items-end">{tableInfoElement}</div>
    </div>
  ) : (
    <div className="grid h-[400px] place-items-center rounded-md bg-slate-100 dark:bg-slate-800">
      <FormattedMessage id="global.noData" />
    </div>
  );
};

export default TreeListingPage;
