import { FormattedMessage } from 'react-intl';

import { MdExpandMore } from 'react-icons/md';

import { useMemo } from 'react';

import { usePagination } from '@/hooks/usePagination';

import TreeTable from '../Table/TreeTable';
import { Button } from '../ui/button';
import { TreeTableBody } from '../../types/tree/Tree';
import { useTreeTable } from '../../api/Tree';
import { TableInfo } from '../Table/TableInfo';

interface ITreeListingPage {
  inputFilter: string;
}

const FilterButton = (): JSX.Element => {
  return (
    <Button
      variant="outline"
      className="w-[128px] rounded-full border-black text-black"
    >
      <div className="flex flex-row items-center gap-1">
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
      return data
        .filter(tree => tree.git_commit_hash?.includes(inputFilter))
        .map(
          (tree): TreeTableBody => ({
            commit: tree.git_commit_hash ?? '',
            patchsetHash: tree.patchset_hash ?? '',
            buildStatus: `${tree.build_status.invalid} / ${tree.build_status.invalid + tree.build_status.valid}`,
            testStatus: `${tree.test_status.fail} / ${tree.test_status.total}`,
            id: tree.git_commit_hash ?? '',
            tree_names: tree.tree_names,
          }),
        )
        .sort((a, b) =>
          a.commit.localeCompare(b.commit, undefined, { numeric: true }),
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

export default TreeListingPage;
