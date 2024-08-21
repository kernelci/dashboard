import { useSearch } from '@tanstack/react-router';

import { useMemo } from 'react';

import { zOrigin } from '@/types/tree/Tree';

import { usePagination } from '@/hooks/usePagination';

import TreeTable from '../Table/TreeTable';
import { TreeTableBody } from '../../types/tree/Tree';
import { useTreeTable } from '../../api/Tree';
import { TableInfo } from '../Table/TableInfo';

interface ITreeListingPage {
  inputFilter: string;
}

const TreeListingPage = ({ inputFilter }: ITreeListingPage): JSX.Element => {
  const { origin: unsafeOrigin } = useSearch({ strict: false });
  const origin = zOrigin.parse(unsafeOrigin);

  const { data, error } = useTreeTable(origin);

  const listItems: TreeTableBody[] = useMemo(() => {
    if (!data || error) {
      return [];
    } else {
      return data
        .filter(
          tree =>
            tree.git_commit_hash?.includes(inputFilter) ||
            tree.tree_names.some(name => name.includes(inputFilter)),
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
            testStatus: `${tree.test_status.fail} / ${tree.test_status.total}`,
            id: tree.git_commit_hash ?? '',
            tree_names: tree.tree_names,
            branch: tree.git_repository_branch ?? '',
            date: tree.start_time ?? '',
            url: tree.git_repository_url ?? '',
          }),
        )
        .sort((a, b) =>
          a.commitHash.localeCompare(b.commitHash, undefined, {
            numeric: true,
          }),
        );
    }
  }, [data, error, inputFilter]);

  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(listItems.length, ITEMS_PER_PAGE);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col items-end gap-4">
        <TableInfo
          startIndex={startIndex + 1}
          endIndex={endIndex}
          totalTrees={listItems.length}
          itemsPerPage={ITEMS_PER_PAGE}
          onClickBack={onClickGoBack}
          onClickForward={onClickGoForward}
        />
      </div>
      <TreeTable treeTableRows={listItems.slice(startIndex, endIndex)} />
      <div className="flex flex-col items-end">
        <TableInfo
          startIndex={startIndex + 1}
          endIndex={endIndex}
          totalTrees={listItems.length}
          itemsPerPage={ITEMS_PER_PAGE}
          onClickBack={onClickGoBack}
          onClickForward={onClickGoForward}
        />
      </div>
    </div>
  );
};

const ITEMS_PER_PAGE = 10;

export default TreeListingPage;
