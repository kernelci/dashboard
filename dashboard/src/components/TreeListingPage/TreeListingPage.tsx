import { useSearch } from '@tanstack/react-router';

import { useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import { zOrigin } from '@/types/tree/Tree';

import { usePagination } from '@/hooks/usePagination';

import { Skeleton } from '@/components/Skeleton';

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

  const { data, error, isLoading } = useTreeTable(origin);

  const listItems: TreeTableBody[] = useMemo(() => {
    if (!data || error) return [];

    return data
      .filter(
        tree =>
          tree.git_commit_hash?.includes(inputFilter) ||
          tree.tree_names.some(name => name.includes(inputFilter)) ||
          tree.git_repository_branch?.includes(inputFilter),
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
      .sort((a, b) =>
        a.commitHash.localeCompare(b.commitHash, undefined, {
          numeric: true,
        }),
      );
  }, [data, error, inputFilter]);

  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(listItems.length, ITEMS_PER_PAGE);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  if (isLoading)
    return (
      <Skeleton>
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );

  return data && data.length > 0 ? (
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
  ) : (
    <div className="grid h-[400px] place-items-center rounded-md bg-slate-100 dark:bg-slate-800">
      <FormattedMessage id="global.noData" />
    </div>
  );
};

const ITEMS_PER_PAGE = 10;

export default TreeListingPage;
