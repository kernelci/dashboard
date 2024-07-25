import { FormattedMessage } from 'react-intl';

import { MdExpandMore } from 'react-icons/md';

import { useMemo } from 'react';

import { usePagination } from '@/hooks/usePagination';

import TreeTable from '../Table/TreeTable';
import { Button } from '../ui/button';
import { Tree, TreeTableBody } from '../../types/tree/Tree';
import { useTreeTable } from '../../api/Tree';
import { TableInfo } from '../Table/TableInfo';

interface ITreeListingPage {
  inputFilter: string;
}

const FilterButton = (): JSX.Element => {
  return (
    <Button
      variant="outline"
      className="rounded-full w-[128px] border-black text-black"
    >
      <div className="flex flex-row gap-1 items-center">
        <FormattedMessage id="global.filters" />
        <MdExpandMore />
      </div>
    </Button>
  );
};

const TreeListingPage = ({ inputFilter }: ITreeListingPage): JSX.Element => {
  const { data, error } = useTreeTable();

  const listItems: TreeTableBody[] = useMemo(() => {
    if (!data || error) {
      return [];
    } else {
      return (data as Tree[])
        .filter(
          tree =>
            tree.tree_name?.includes(inputFilter) ||
            tree.git_commit_hash?.includes(inputFilter) ||
            tree.git_commit_name?.includes(inputFilter) ||
            tree.git_repository_branch?.includes(inputFilter),
        )
        .map(tree => {
          const fullHash = tree.git_commit_hash ?? '';
          const commitHash =
            fullHash.substring(0, NUMBER_CHAR_HASH) +
            (fullHash.length > NUMBER_CHAR_HASH ? '...' : '');
          const tagCommit = tree.git_commit_name
            ? `${tree.git_commit_name} - ${commitHash}`
            : commitHash;

          return {
            name: tree.tree_name ?? '',
            branch: tree.git_repository_branch ?? '',
            commit: tagCommit,
            buildStatus: `${tree.build_status.invalid} / ${tree.build_status.invalid + tree.build_status.valid}`,
            testStatus: `${tree.test_status.fail} / ${tree.test_status.total}`,
            id: tree.git_commit_hash ?? '',
          };
        })
        .sort(
          (a, b) =>
            a.name.localeCompare(b.name, undefined, { numeric: true }) ||
            a.branch.localeCompare(b.branch, undefined, { numeric: true }),
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
        <FilterButton />
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
const NUMBER_CHAR_HASH = 12;

export default TreeListingPage;
