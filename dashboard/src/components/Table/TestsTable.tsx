import { useSearch } from '@tanstack/react-router';

import { TableInfo } from '@/components/Table/TableInfo';
import { usePagination } from '@/hooks/usePagination';

import { useTreeTest } from '@/api/TreeDetails';

import Accordion from '../Accordion/Accordion';

const ITEMS_PER_PAGE = 10;

export interface ITestsTable {
  treeId: string;
}

const TestsTable = ({ treeId }: ITestsTable): JSX.Element => {
  const { testPath, treeInfo, origin } = useSearch({ from: '/tree/$treeId/' });
  const { data } = useTreeTest(
    treeId,
    testPath,
    treeInfo.gitBranch ?? '',
    treeInfo.gitUrl ?? '',
    origin,
  );
  const data_len = data?.length || 0;
  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(data_len, ITEMS_PER_PAGE);

  const tableInfoElement = (
    <div className="flex flex-col items-end">
      <TableInfo
        startIndex={startIndex + 1}
        endIndex={endIndex}
        totalTrees={data_len}
        itemsPerPage={ITEMS_PER_PAGE}
        onClickBack={onClickGoBack}
        onClickForward={onClickGoForward}
      />
    </div>
  );

  return (
    <div className="flex flex-col gap-6">
      {tableInfoElement}
      <Accordion type="test" items={data ?? []} />
      {tableInfoElement}
    </div>
  );
};

export default TestsTable;
